#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from loop_core_draft import build_project_loop_state_core, build_reuse_summary, build_trust_summary, dedupe, evaluate_loop_status


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the repo-agnostic governance loop core against a plan JSON and landing-status JSON."
    )
    parser.add_argument("--plan", type=Path, required=True, help="Path to blueprint plan JSON.")
    parser.add_argument("--landing-status", type=Path, required=True, help="Path to landing-status JSON.")
    parser.add_argument("--catalog", type=Path, help="Optional slice adapter catalog JSON.")
    parser.add_argument(
        "--ignore-blocking-fact",
        action="append",
        default=[],
        help="Blocking fact to ignore for preview purposes. Can be supplied multiple times.",
    )
    return parser.parse_args()


def resolve_adapter_entry(catalog: dict[str, Any], slice_id: str) -> dict[str, Any]:
    return dict(catalog.get("slices", {}).get(slice_id, {}))


def main() -> int:
    args = parse_args()
    plan = read_json(args.plan)
    landing_status = read_json(args.landing_status)
    loop_state = build_project_loop_state_core(
        plan,
        landing_status,
        source_plan=str(args.plan),
        generated_at_utc=utc_now(),
    )
    status, reason, effective_blockers = evaluate_loop_status(loop_state, args.ignore_blocking_fact)
    next_slice = dict(loop_state.get("next_slice", {}))
    adapter_entry = {}
    if args.catalog:
        adapter_entry = resolve_adapter_entry(read_json(args.catalog), next_slice.get("id", ""))

    payload = {
        "status": status,
        "reason": reason,
        "project": loop_state.get("project", ""),
        "current_level": loop_state.get("current_level", ""),
        "next_slice": next_slice,
        "blocking_facts": loop_state.get("blocking_facts", []),
        "effective_blocking_facts": effective_blockers,
        "ignored_blocking_facts": dedupe(args.ignore_blocking_fact),
        "remaining_promotion_gates": loop_state.get("remaining_promotion_gates", []),
        "pipeline_contract": loop_state.get("pipeline_contract", {}),
        "control_contract": loop_state.get("control_contract", {}),
        "flow_control": loop_state.get("flow_control", {}),
        "trust_summary": build_trust_summary(loop_state),
        "reuse_summary": build_reuse_summary(loop_state),
        "adapter_entry": adapter_entry,
    }
    print(json.dumps(payload, indent=2, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
