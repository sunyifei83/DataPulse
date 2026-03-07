#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from datapulse_loop_adapter import DEFAULT_CATALOG_PATH, build_datapulse_loop_runtime
from datapulse_loop_contracts import DEFAULT_OUT_DIR, DEFAULT_PLAN_PATH, write_json


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Export the current DataPulse slice execution brief for human or Codex consumption."
    )
    parser.add_argument(
        "--plan",
        type=Path,
        default=DEFAULT_PLAN_PATH,
        help="Blueprint plan path. Defaults to the active plan overlay.",
    )
    parser.add_argument(
        "--catalog",
        type=Path,
        default=DEFAULT_CATALOG_PATH,
        help="Slice adapter catalog path.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUT_DIR / "slice_execution_brief.draft.json",
        help="Output path for the current slice execution brief.",
    )
    parser.add_argument(
        "--stdout",
        action="store_true",
        help="Print JSON to stdout instead of writing the default draft file.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    runtime = build_datapulse_loop_runtime(args.plan, args.catalog)
    payload = {
        "schema_version": "datapulse_slice_execution_brief.v1",
        "project": runtime.get("project", "DataPulse"),
        "status": runtime.get("status", ""),
        "reason": runtime.get("reason", ""),
        "current_level": runtime.get("current_level", ""),
        "next_slice": runtime.get("next_slice", {}),
        "slice_execution_brief": runtime.get("slice_execution_brief", {}),
        "blocking_facts": runtime.get("effective_blocking_facts", []),
        "remaining_promotion_gates": runtime.get("remaining_promotion_gates", []),
    }
    if args.stdout:
        print(json.dumps(payload, indent=2, ensure_ascii=True))
        return 0
    write_json(args.output, payload)
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
