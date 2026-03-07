#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from datapulse_loop_contracts import DEFAULT_OUT_DIR, DEFAULT_PLAN_PATH, prepare_working_copy, write_plan


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create a mutable working copy of the DataPulse draft blueprint plan. This script is manual-only and does not modify docs/governance."
    )
    parser.add_argument(
        "--source-plan",
        type=Path,
        default=DEFAULT_PLAN_PATH,
        help="Source blueprint plan path. Defaults to the draft plan under docs/governance.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUT_DIR / "datapulse-blueprint-plan.working.json",
        help="Output working copy path.",
    )
    parser.add_argument(
        "--stdout",
        action="store_true",
        help="Print the prepared working copy JSON to stdout instead of writing the default file.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    plan = prepare_working_copy(args.source_plan, args.output)
    if args.stdout:
        print(json.dumps(plan, indent=2, ensure_ascii=True))
        return 0
    write_plan(args.output, plan)
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
