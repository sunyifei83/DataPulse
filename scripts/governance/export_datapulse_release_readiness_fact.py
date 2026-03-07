#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from datapulse_loop_contracts import write_json
from export_datapulse_ha_delivery_facts import DEFAULT_RELEASE_READINESS_FACT_PATH, build_release_readiness_fact


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Export a persistent DataPulse release_readiness_fact.v1 observation without changing the existing readiness workflow."
    )
    parser.add_argument(
        "--emergency-state",
        type=Path,
        help="Optional persistent emergency_state.json path. Defaults to the latest artifact if omitted.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_RELEASE_READINESS_FACT_PATH,
        help="Output path for the release readiness fact JSON.",
    )
    parser.add_argument(
        "--stdout",
        action="store_true",
        help="Print JSON to stdout instead of writing the default draft file.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = build_release_readiness_fact(emergency_state_path=args.emergency_state)
    if args.stdout:
        print(json.dumps(payload, indent=2, ensure_ascii=True))
        return 0
    write_json(args.output, payload)
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
