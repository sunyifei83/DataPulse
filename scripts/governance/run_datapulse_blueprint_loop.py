#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from datapulse_loop_adapter import DEFAULT_CATALOG_PATH, build_datapulse_loop_runtime
from datapulse_loop_contracts import DEFAULT_PLAN_PATH, load_plan


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the active manual-mode DataPulse blueprint loop evaluation. This script is read-only and does not execute repository changes."
    )
    parser.add_argument(
        "--plan",
        type=Path,
        default=DEFAULT_PLAN_PATH,
        help="Blueprint plan path. Defaults to the active plan overlay when present.",
    )
    parser.add_argument(
        "--catalog",
        type=Path,
        default=DEFAULT_CATALOG_PATH,
        help="Slice adapter catalog path.",
    )
    parser.add_argument(
        "--ignore-blocking-fact",
        action="append",
        default=[],
        help="Blocking fact to ignore for preview purposes. Can be supplied multiple times.",
    )
    parser.add_argument(
        "--stdout",
        action="store_true",
        help="Accepted for compatibility. Output is JSON by default.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    load_plan(args.plan)
    payload = build_datapulse_loop_runtime(args.plan, args.catalog, args.ignore_blocking_fact)
    print(json.dumps(payload, indent=2, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
