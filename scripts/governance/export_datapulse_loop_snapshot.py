#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from datapulse_loop_contracts import (
    DEFAULT_OUT_DIR,
    DEFAULT_PLAN_PATH,
    build_code_landing_status,
    build_loop_snapshot_summary,
    build_project_loop_state,
    load_plan,
    write_json,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Export both draft governance snapshots for DataPulse. This script is manual-only and not wired into existing workflows."
    )
    parser.add_argument(
        "--plan",
        type=Path,
        default=DEFAULT_PLAN_PATH,
        help="Blueprint plan path. Defaults to the draft plan.",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=DEFAULT_OUT_DIR,
        help="Directory for draft snapshot outputs.",
    )
    parser.add_argument(
        "--stdout",
        action="store_true",
        help="Print a combined JSON payload to stdout instead of writing files.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    plan = load_plan(args.plan)
    plan["_source_path"] = str(args.plan.resolve())
    landing_status = build_code_landing_status()
    loop_state = build_project_loop_state(plan, landing_status)
    summary = build_loop_snapshot_summary(landing_status, loop_state)

    if args.stdout:
        print(
            json.dumps(
                {
                    "summary": summary,
                    "code_landing_status": landing_status,
                    "project_specific_loop_state": loop_state,
                },
                indent=2,
                ensure_ascii=True,
            )
        )
        return 0

    out_dir = args.out_dir
    write_json(out_dir / "code_landing_status.draft.json", landing_status)
    write_json(out_dir / "project_specific_loop_state.draft.json", loop_state)
    print(out_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
