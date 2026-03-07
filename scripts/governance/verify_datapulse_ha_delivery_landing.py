#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from datapulse_loop_adapter_draft import DEFAULT_CATALOG_PATH
from datapulse_loop_contracts import DEFAULT_PLAN_PATH
from export_datapulse_ha_delivery_landing import build_ha_delivery_landing


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Verify that exported DataPulse HA delivery landing facts remain aligned with the current activation and HA evidence inputs."
    )
    parser.add_argument(
        "--ha-delivery-landing-json",
        type=Path,
        required=True,
        help="Path to a datapulse_ha_delivery_landing.v1 JSON payload.",
    )
    parser.add_argument(
        "--bundle-dir",
        type=Path,
        help="Optional adapter bundle directory used during recomputation.",
    )
    parser.add_argument(
        "--plan",
        type=Path,
        default=DEFAULT_PLAN_PATH,
        help="Blueprint plan path used when a temporary bundle is derived.",
    )
    parser.add_argument(
        "--catalog",
        type=Path,
        default=DEFAULT_CATALOG_PATH,
        help="Slice adapter catalog path used when a temporary bundle is derived.",
    )
    parser.add_argument(
        "--ha-facts-json",
        type=Path,
        help="Optional ha_delivery_facts.v1 JSON payload used during recomputation.",
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
    normalized_tracks: list[dict[str, Any]] = []
    for track in payload.get("delivery_tracks", []):
        items = list(track.get("items", []))
        if track.get("track_id") == "repo_governance_cutover":
            items = [
                {
                    "surface_id": item.get("surface_id"),
                    "binding_status": item.get("binding_status"),
                    "binding_kind": item.get("binding_kind"),
                    "suggested_binding": item.get("suggested_binding"),
                    "required_for": item.get("required_for"),
                    "from_signals": item.get("from_signals"),
                    "notes": item.get("notes"),
                }
                for item in items
            ]
        normalized_tracks.append(
            {
                "track_id": track.get("track_id"),
                "status": track.get("status"),
                "items": items,
            }
        )

    keys = [
        "schema_version",
        "project",
        "delivery_target",
        "delivery_status",
        "landing_bar",
        "fact_projection",
        "control_contract",
        "recommended_actions",
    ]
    comparable = {key: payload.get(key) for key in keys}
    comparable["delivery_tracks"] = normalized_tracks
    return comparable


def build_expected(args: argparse.Namespace) -> tuple[dict[str, Any], int]:
    expected_args = argparse.Namespace(
        bundle_dir=args.bundle_dir,
        plan=args.plan,
        catalog=args.catalog,
        ha_facts_json=args.ha_facts_json,
        probe_release_readiness=args.probe_release_readiness,
        disable_emergency_rehydration=args.disable_emergency_rehydration,
        output=Path(""),
        stdout=False,
    )
    return build_ha_delivery_landing(expected_args)


def main() -> int:
    args = parse_args()
    actual = read_json(args.ha_delivery_landing_json)
    expected, exit_code = build_expected(args)
    if exit_code:
        print(json.dumps(expected, indent=2, ensure_ascii=True))
        return exit_code

    actual_comp = comparable_payload(actual)
    expected_comp = comparable_payload(expected)
    mismatches = [key for key, value in expected_comp.items() if actual_comp.get(key) != value]

    checks = [
        {
            "name": "ha_delivery_landing_schema_version",
            "ok": str(actual.get("schema_version", "")) == "datapulse_ha_delivery_landing.v1",
            "details": ["HA delivery landing schema is correct"]
            if str(actual.get("schema_version", "")) == "datapulse_ha_delivery_landing.v1"
            else [f"unexpected_schema_version:{actual.get('schema_version', '')}"],
        },
        {
            "name": "ha_delivery_landing_matches_current_inputs",
            "ok": not mismatches,
            "details": ["HA delivery landing matches the current activation and HA inputs"]
            if not mismatches
            else [f"ha_delivery_landing_mismatches:{mismatches}"],
        },
    ]

    payload = {
        "valid": all(item["ok"] for item in checks),
        "ha_delivery_landing_json": str(args.ha_delivery_landing_json),
        "checks": checks,
    }
    print(json.dumps(payload, indent=2, ensure_ascii=True))
    return 0 if payload["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
