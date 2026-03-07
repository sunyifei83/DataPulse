#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from export_datapulse_ha_delivery_facts import build_ha_delivery_facts


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Verify that exported DataPulse HA delivery facts remain aligned with the current observed evidence chain."
    )
    parser.add_argument(
        "--ha-facts-json",
        type=Path,
        required=True,
        help="Path to a ha_delivery_facts.v1 JSON payload.",
    )
    parser.add_argument(
        "--probe-release-readiness",
        action="store_true",
        help="Recompute using an explicit release_readiness probe.",
    )
    parser.add_argument(
        "--disable-emergency-rehydration",
        action="store_true",
        help="Do not derive a temporary emergency_state.json during recomputation.",
    )
    parser.add_argument(
        "--release-readiness-fact-json",
        type=Path,
        help="Optional persisted release_readiness_fact.v1 JSON payload used during recomputation.",
    )
    return parser.parse_args()


def comparable_payload(payload: dict[str, Any]) -> dict[str, Any]:
    keys = [
        "schema_version",
        "project",
        "current_level",
        "next_missing_level",
        "ha_chain",
        "delivery_levels",
        "open_facts",
        "machine_blockers",
        "fact_groups",
        "delivery_contract",
    ]
    return {key: payload.get(key) for key in keys}


def main() -> int:
    args = parse_args()
    actual = read_json(args.ha_facts_json)
    expected = build_ha_delivery_facts(
        probe_release_readiness_flag=args.probe_release_readiness,
        allow_emergency_rehydrate=not args.disable_emergency_rehydration,
        release_readiness_fact_path=args.release_readiness_fact_json,
    )

    actual_comp = comparable_payload(actual)
    expected_comp = comparable_payload(expected)
    mismatches = [key for key, value in expected_comp.items() if actual_comp.get(key) != value]

    checks = [
        {
            "name": "ha_facts_schema_version",
            "ok": str(actual.get("schema_version", "")) == "ha_delivery_facts.v1",
            "details": ["HA delivery facts schema is correct"]
            if str(actual.get("schema_version", "")) == "ha_delivery_facts.v1"
            else [f"unexpected_schema_version:{actual.get('schema_version', '')}"],
        },
        {
            "name": "ha_facts_match_current_chain",
            "ok": not mismatches,
            "details": ["HA delivery facts match the current observed chain"]
            if not mismatches
            else [f"ha_fact_mismatches:{mismatches}"],
        },
    ]

    payload = {
        "valid": all(item["ok"] for item in checks),
        "ha_facts_json": str(args.ha_facts_json),
        "checks": checks,
    }
    print(json.dumps(payload, indent=2, ensure_ascii=True))
    return 0 if payload["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
