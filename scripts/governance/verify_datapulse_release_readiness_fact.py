#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from export_datapulse_ha_delivery_facts import build_release_readiness_fact


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Verify that an exported DataPulse release_readiness_fact remains aligned with the current readiness observation."
    )
    parser.add_argument(
        "--release-readiness-fact-json",
        type=Path,
        required=True,
        help="Path to a release_readiness_fact.v1 JSON payload.",
    )
    parser.add_argument(
        "--emergency-state",
        type=Path,
        help="Optional persistent emergency_state.json path used during recomputation.",
    )
    return parser.parse_args()


def comparable_payload(payload: dict[str, Any]) -> dict[str, Any]:
    keys = [
        "schema_version",
        "project",
        "source_emergency_state",
        "command",
        "observation",
        "machine_blockers",
    ]
    return {key: payload.get(key) for key in keys}


def main() -> int:
    args = parse_args()
    actual = read_json(args.release_readiness_fact_json)
    expected = build_release_readiness_fact(emergency_state_path=args.emergency_state)

    actual_comp = comparable_payload(actual)
    expected_comp = comparable_payload(expected)
    mismatches = [key for key, value in expected_comp.items() if actual_comp.get(key) != value]

    checks = [
        {
            "name": "release_readiness_fact_schema_version",
            "ok": str(actual.get("schema_version", "")) == "release_readiness_fact.v1",
            "details": ["Release readiness fact schema is correct"]
            if str(actual.get("schema_version", "")) == "release_readiness_fact.v1"
            else [f"unexpected_schema_version:{actual.get('schema_version', '')}"],
        },
        {
            "name": "release_readiness_fact_matches_current_observation",
            "ok": not mismatches,
            "details": ["Release readiness fact matches the current readiness observation"]
            if not mismatches
            else [f"release_readiness_fact_mismatches:{mismatches}"],
        },
    ]

    payload = {
        "valid": all(item["ok"] for item in checks),
        "release_readiness_fact_json": str(args.release_readiness_fact_json),
        "checks": checks,
    }
    print(json.dumps(payload, indent=2, ensure_ascii=True))
    return 0 if payload["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
