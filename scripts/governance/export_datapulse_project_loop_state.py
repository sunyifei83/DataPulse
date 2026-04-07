#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from datapulse_loop_contracts import (
    DEFAULT_OUT_DIR,
    DEFAULT_PLAN_PATH,
    build_code_landing_status,
    build_project_loop_state,
    load_plan,
    write_json,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Export a draft DataPulse project loop state snapshot. This script is manual-only and not wired into existing workflows."
    )
    parser.add_argument(
        "--plan",
        type=Path,
        default=DEFAULT_PLAN_PATH,
        help="Blueprint plan path. Defaults to the draft plan.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUT_DIR / "project_specific_loop_state.draft.json",
        help="Output path for the draft loop state JSON.",
    )
    parser.add_argument(
        "--release-window-attestation",
        type=Path,
        help="Optional release-window attestation JSON used when rebuilding landing status for the loop state export.",
    )
    parser.add_argument(
        "--stdout",
        action="store_true",
        help="Print JSON to stdout instead of writing the default draft file.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    plan = load_plan(args.plan)
    plan["_source_path"] = str(args.plan.resolve())
    landing_status = build_code_landing_status(
        release_window_attestation_path=args.release_window_attestation.resolve()
        if isinstance(args.release_window_attestation, Path)
        else None
    )
    payload = build_project_loop_state(plan, landing_status)
    if args.stdout:
        print(json.dumps(payload, indent=2, ensure_ascii=True))
        return 0
    write_json(args.output, payload)
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
