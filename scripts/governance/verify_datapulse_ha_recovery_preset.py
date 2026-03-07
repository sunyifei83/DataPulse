#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from export_datapulse_ha_recovery_preset import build_recovery_preset


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Verify that an exported DataPulse HA recovery preset remains aligned with the current HA recovery route."
    )
    parser.add_argument(
        "--ha-recovery-preset-json",
        type=Path,
        required=True,
        help="Path to a datapulse_ha_recovery_preset.v1 JSON payload.",
    )
    parser.add_argument(
        "--ha-facts-json",
        type=Path,
        help="Optional ha_delivery_facts.v1 JSON payload used during recomputation.",
    )
    parser.add_argument(
        "--route",
        choices=["selected", "primary", "secondary"],
        default="selected",
        help="Which route should be recomputed for verification.",
    )
    parser.add_argument(
        "--probe-release-readiness",
        action="store_true",
        help="Opt in to probing release_readiness when deriving HA facts.",
    )
    parser.add_argument(
        "--disable-emergency-rehydration",
        action="store_true",
        help="Do not derive a temporary emergency_state.json during HA fact derivation.",
    )
    return parser.parse_args()


def comparable_payload(payload: dict[str, Any]) -> dict[str, Any]:
    keys = [
        "schema_version",
        "project",
        "recovery_status",
        "route_contract",
        "preset_contract",
        "blocker_codes",
    ]
    return {key: payload.get(key) for key in keys}


def main() -> int:
    args = parse_args()
    actual = read_json(args.ha_recovery_preset_json)
    expected = build_recovery_preset(args)

    actual_comp = comparable_payload(actual)
    expected_comp = comparable_payload(expected)
    mismatches = [key for key, value in expected_comp.items() if actual_comp.get(key) != value]

    checks = [
        {
            "name": "ha_recovery_preset_schema_version",
            "ok": str(actual.get("schema_version", "")) == "datapulse_ha_recovery_preset.v1",
            "details": ["HA recovery preset schema is correct"]
            if str(actual.get("schema_version", "")) == "datapulse_ha_recovery_preset.v1"
            else [f"unexpected_schema_version:{actual.get('schema_version', '')}"],
        },
        {
            "name": "ha_recovery_preset_matches_current_route",
            "ok": not mismatches,
            "details": ["HA recovery preset matches the current recovery route"]
            if not mismatches
            else [f"ha_recovery_preset_mismatches:{mismatches}"],
        },
    ]

    payload = {
        "valid": all(item["ok"] for item in checks),
        "ha_recovery_preset_json": str(args.ha_recovery_preset_json),
        "checks": checks,
    }
    print(json.dumps(payload, indent=2, ensure_ascii=True))
    return 0 if payload["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
