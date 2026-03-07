#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from datapulse_loop_contracts import (
    DEFAULT_OUT_DIR,
    DEFAULT_PLAN_PATH,
    assert_plan_path_mutable,
    build_code_landing_status,
    build_project_loop_state,
    load_plan,
    mark_slice_status,
    prepare_working_copy,
    write_plan,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Advance a mutable DataPulse blueprint working copy by marking a slice status. This script is manual-only and refuses to edit docs/governance plans."
    )
    parser.add_argument(
        "--plan",
        type=Path,
        default=DEFAULT_OUT_DIR / "datapulse-blueprint-plan.working.json",
        help="Working copy plan path. Defaults to out/governance/datapulse-blueprint-plan.working.json.",
    )
    parser.add_argument(
        "--init-from",
        type=Path,
        default=DEFAULT_PLAN_PATH,
        help="Source plan used when --plan does not yet exist.",
    )
    parser.add_argument(
        "--slice-id",
        default="",
        help="Slice id to update. Defaults to the current next slice derived from the working copy.",
    )
    parser.add_argument(
        "--status",
        choices=["completed", "pending", "skipped"],
        default="completed",
        help="Target status to set for the slice.",
    )
    parser.add_argument(
        "--ignore-blocking-fact",
        action="append",
        default=[],
        help="Blocking fact to ignore when auto-selecting the next slice.",
    )
    parser.add_argument(
        "--allow-blocked",
        action="store_true",
        help="Allow mutation even when the current next slice is blocked.",
    )
    parser.add_argument(
        "--stdout",
        action="store_true",
        help="Print the updated plan JSON to stdout instead of writing the working copy file.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.plan.exists():
        assert_plan_path_mutable(args.plan)
        plan = load_plan(args.plan)
        plan["_source_path"] = str(args.plan.resolve())
    else:
        assert_plan_path_mutable(args.plan)
        plan = prepare_working_copy(args.init_from, args.plan)
        plan["_source_path"] = str(args.plan.resolve())

    landing_status = build_code_landing_status()
    loop_state = build_project_loop_state(plan, landing_status)
    blocking_facts = list(loop_state.get("blocking_facts", []))
    effective_blockers = [item for item in blocking_facts if item not in set(args.ignore_blocking_fact)]

    if not args.allow_blocked and effective_blockers:
        payload = {
            "status": "blocked",
            "reason": "working_copy_next_slice_blocked",
            "next_slice": loop_state.get("next_slice", {}),
            "blocking_facts": blocking_facts,
            "effective_blocking_facts": effective_blockers,
            "ignored_blocking_facts": args.ignore_blocking_fact,
        }
        print(json.dumps(payload, indent=2, ensure_ascii=True))
        return 1

    slice_id = args.slice_id or loop_state.get("next_slice", {}).get("id", "")
    if not slice_id or slice_id == "no-open-slice":
        payload = {
            "status": "stopped",
            "reason": "no_open_slice",
            "next_slice": loop_state.get("next_slice", {}),
        }
        print(json.dumps(payload, indent=2, ensure_ascii=True))
        return 0

    updated_item = mark_slice_status(plan, slice_id, args.status)
    plan["_source_path"] = str(args.plan.resolve())

    if args.stdout:
        print(json.dumps(plan, indent=2, ensure_ascii=True))
        return 0

    write_plan(args.plan, plan)
    payload = {
        "status": "advanced",
        "slice": {
            "id": updated_item.get("id", ""),
            "title": updated_item.get("title", ""),
            "status": updated_item.get("status", ""),
        },
        "plan_path": str(args.plan),
        "recommended_next_slice": plan.get("recommended_next_slice", {}),
    }
    print(json.dumps(payload, indent=2, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
