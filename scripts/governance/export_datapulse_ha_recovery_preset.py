#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from datapulse_loop_contracts import DEFAULT_OUT_DIR, utc_now, write_json
from export_datapulse_ha_delivery_facts import build_ha_delivery_facts


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Export a DataPulse HA recovery preset from the current emergency recovery route."
    )
    parser.add_argument(
        "--ha-facts-json",
        type=Path,
        help="Optional ha_delivery_facts.v1 JSON payload. If omitted, the facts are derived from the current repo state.",
    )
    parser.add_argument(
        "--route",
        choices=["selected", "primary", "secondary"],
        default="selected",
        help="Which recovery route to export. Defaults to the currently selected route.",
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
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUT_DIR / "ha_recovery_preset.draft.json",
        help="Output path for the HA recovery preset JSON.",
    )
    parser.add_argument(
        "--stdout",
        action="store_true",
        help="Print JSON to stdout instead of writing the default draft file.",
    )
    parser.add_argument(
        "--shell",
        action="store_true",
        help="Print only the shell command lines for the selected route.",
    )
    return parser.parse_args()


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_ha_facts(args: argparse.Namespace) -> tuple[dict[str, Any], dict[str, Any]]:
    if args.ha_facts_json:
        return read_json(args.ha_facts_json), {
            "source_kind": "provided_json",
            "path": str(args.ha_facts_json),
        }
    return (
        build_ha_delivery_facts(
            probe_release_readiness_flag=args.probe_release_readiness,
            allow_emergency_rehydrate=not args.disable_emergency_rehydration,
        ),
        {
            "source_kind": "derived_current_repo",
            "probe_release_readiness": args.probe_release_readiness,
            "allow_emergency_rehydration": not args.disable_emergency_rehydration,
        },
    )


def resolve_route_name(recovery_route: dict[str, Any], requested_route: str) -> str:
    if requested_route != "selected":
        return requested_route
    selected = str(recovery_route.get("selected_route", ""))
    if selected:
        return selected
    if recovery_route.get("primary_action"):
        return "primary"
    if recovery_route.get("secondary_action"):
        return "secondary"
    return "selected"


def build_recovery_preset(args: argparse.Namespace) -> dict[str, Any]:
    ha_facts, source = load_ha_facts(args)
    recovery_route = dict(ha_facts.get("ha_chain", {}).get("recovery_route", {}))
    route_name = resolve_route_name(recovery_route, args.route)
    route_contract = dict(recovery_route.get(f"{route_name}_execution_contract", {}))
    route_available = bool(route_contract.get("route_available", False))

    payload = {
        "schema_version": "datapulse_ha_recovery_preset.v1",
        "project": "DataPulse",
        "generated_at_utc": utc_now(),
        "wired": False,
        "source_ha_delivery_facts": source,
        "recovery_status": {
            "status": str(recovery_route.get("status", "clear")),
            "first_trigger": str(recovery_route.get("first_trigger", "")),
            "conclusion": str(recovery_route.get("conclusion", "")),
            "selected_route": route_name,
            "route_available": route_available,
            "requires_new_run_id": bool(recovery_route.get("should_new_run_id", False)),
        },
        "catalog_match": recovery_route.get(f"{route_name}_catalog_match", {}),
        "route_contract": route_contract,
        "preset_contract": {
            "preset_kind": str(route_contract.get("route_kind", "empty_recovery_route")),
            "supported_by_existing_remote_smoke_entrypoint": bool(
                route_contract.get("supported_by_existing_remote_smoke_entrypoint", False)
            ),
            "env_assignments": route_contract.get("env_assignments", {}),
            "manual_steps": route_contract.get("manual_steps", []),
            "shell_exports": route_contract.get("shell_exports", []),
            "command_lines": route_contract.get("command_lines", []),
            "entrypoint": route_contract.get("entrypoint", ""),
            "entrypoint_command": route_contract.get("entrypoint_command", ""),
        },
        "blocker_codes": recovery_route.get("blocker_codes", []),
        "recommended_usage": [
            "Prefer catalog-matched presets when catalog_match.matched is true.",
            "Rotate RUN_ID before replay if requires_new_run_id is true.",
            "Use the shell exports and command lines exactly as rendered for the selected route.",
            "Re-run emergency_guard after the remote smoke replay so the recovery fact chain closes.",
        ],
    }
    return payload


def main() -> int:
    args = parse_args()
    payload = build_recovery_preset(args)

    if args.shell:
        command_lines = list(payload.get("preset_contract", {}).get("command_lines", []))
        print("\n".join(command_lines))
        return 0

    if args.stdout:
        print(json.dumps(payload, indent=2, ensure_ascii=True))
        return 0

    write_json(args.output, payload)
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
