#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from datapulse_loop_contracts import REPO_ROOT, read_json, utc_now, write_json
from export_datapulse_ai_surface_admission_example import build_payload as build_admission_payload

DEFAULT_OUTPUT_DIR = REPO_ROOT / "out/ha_latest_release_bundle"
DEFAULT_SUBSCRIPTIONS_PATH = REPO_ROOT / "docs/governance/datapulse-ai-surface-subscriptions.example.json"
DEFAULT_PROJECT_LOOP_STATE_PATH = REPO_ROOT / "out/governance/project_specific_loop_state.draft.json"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Export a ModelBus consumer bundle that DataPulse can consume through the bundle-first default path."
    )
    parser.add_argument(
        "--subscriptions",
        type=Path,
        default=DEFAULT_SUBSCRIPTIONS_PATH,
        help="Candidate AI surface subscription contract path.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Bundle directory that will receive ModelBus consumer artifacts.",
    )
    parser.add_argument(
        "--admission-output",
        type=Path,
        default=None,
        help="Optional path for the exported admission example. Defaults to <output-dir>/datapulse-ai-surface-admission.example.json.",
    )
    parser.add_argument(
        "--project-loop-state-json",
        type=Path,
        help="Optional project_specific_loop_state.draft.json used to determine release_level for release_status.json.",
    )
    parser.add_argument(
        "--stdout",
        action="store_true",
        help="Print the manifest payload to stdout instead of writing bundle files.",
    )
    return parser.parse_args()


def load_release_level(project_loop_state_path: Path | None = None) -> str:
    loop_state_path = (
        project_loop_state_path.resolve()
        if isinstance(project_loop_state_path, Path)
        else DEFAULT_PROJECT_LOOP_STATE_PATH
    )
    if not loop_state_path.exists():
        return ""
    payload = read_json(loop_state_path)
    return str(payload.get("current_level", "") or "").strip()


def alias_by_surface(subscriptions: dict[str, Any]) -> dict[str, str]:
    aliases: dict[str, str] = {}
    for surface in subscriptions.get("surfaces", []):
        if not isinstance(surface, dict):
            continue
        surface_id = str(surface.get("surface", "") or "").strip()
        if not surface_id:
            continue
        for candidate in surface.get("candidate_subscriptions", []):
            if not isinstance(candidate, dict):
                continue
            alias = str(candidate.get("alias", "") or "").strip()
            if alias:
                aliases[surface_id] = alias
                break
    return aliases


def build_surface_admissions(
    admission_payload: dict[str, Any],
    *,
    fallback_aliases: dict[str, str],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for raw_row in admission_payload.get("surface_admissions", []):
        if not isinstance(raw_row, dict):
            continue
        surface_id = str(raw_row.get("surface", "") or "").strip()
        if not surface_id:
            continue
        requested_alias = str(
            raw_row.get("requested_alias", "")
            or raw_row.get("admitted_alias", "")
            or fallback_aliases.get(surface_id, "")
        ).strip()
        must_expose_runtime_facts = [
            str(item).strip()
            for item in raw_row.get("must_expose_runtime_facts", [])
            if str(item).strip()
        ]
        if "request_id" not in must_expose_runtime_facts:
            must_expose_runtime_facts.append("request_id")
        rows.append(
            {
                "surface_id": surface_id,
                "requested_alias": requested_alias,
                "admission_status": str(raw_row.get("admission_status", "") or "rejected").strip().lower() or "rejected",
                "admitted_alias": str(raw_row.get("admitted_alias", "") or "").strip(),
                "mode_admission": dict(raw_row.get("mode_admission") or {})
                if isinstance(raw_row.get("mode_admission"), dict)
                else {"off": "manual_only", "assist": "rejected", "review": "rejected"},
                "schema_contract": str(raw_row.get("required_schema_contract", "") or "").strip(),
                "manual_fallback": str(
                    raw_row.get("manual_fallback", "manual_or_deterministic_behavior") or "manual_or_deterministic_behavior"
                ).strip(),
                "degraded_result_allowed": bool(raw_row.get("degraded_result_allowed", False)),
                "must_expose_runtime_facts": must_expose_runtime_facts,
                "rejectable_gaps": list(raw_row.get("rejectable_gaps") or []),
            }
        )
    return rows


def build_bridge_config(aliases: dict[str, str]) -> dict[str, Any]:
    return {
        "schema": "modelbus.consumer_bridge_config.v1",
        "generated_at_utc": utc_now(),
        "consumer_id": "datapulse",
        "bundle_id": "datapulse.ai_surface_bus",
        "base_url": "https://modelbus.example.com",
        "request_protocol": "responses",
        "endpoint": "/v1/responses",
        "bus_key_env": "DATAPULSE_MODELBUS_BUS_KEY",
        "tenant_env": "DATAPULSE_MODELBUS_TENANT",
        "tenant_header": "X-ModelBus-Tenant",
        "alias_by_surface": aliases,
    }


def build_release_status(release_level: str) -> dict[str, Any]:
    return {
        "schema": "modelbus.release_status.v1",
        "generated_at_utc": utc_now(),
        "release_level": release_level,
        "assured_verdict": "pass" if release_level else "unknown",
        "runtime": {
            "base_url": "https://modelbus.example.com",
        },
    }


def build_bundle_manifest() -> dict[str, Any]:
    return {
        "schema": "modelbus.consumer_bundle_manifest.v1",
        "generated_at_utc": utc_now(),
        "bundle_id": "datapulse.ai_surface_bus",
        "consumer_id": "datapulse",
        "artifacts": {
            "surface_admission": {"path": "surface_admission.json"},
            "bridge_config": {"path": "bridge_config.json"},
            "release_status": {"path": "release_status.json"},
        },
    }


def main() -> int:
    args = parse_args()
    output_dir = args.output_dir.resolve()
    subscriptions_path = args.subscriptions.resolve()
    subscriptions = read_json(subscriptions_path)
    admission_payload = build_admission_payload(subscriptions, subscriptions_path)
    aliases = alias_by_surface(subscriptions)
    release_level = load_release_level(args.project_loop_state_json)
    admission_output = (
        args.admission_output.resolve()
        if isinstance(args.admission_output, Path)
        else (output_dir / "datapulse-ai-surface-admission.example.json").resolve()
    )
    surface_admission = {
        "schema": "modelbus.consumer_surface_admission.v1",
        "generated_at_utc": utc_now(),
        "consumer_id": "datapulse",
        "release_window": {
            "generated_at_utc": utc_now(),
            "release_level": release_level,
            "assured_verdict": "pass",
            "constitutional_semantics": "BUNDLE-FIRST-REQUIRED",
        },
        "surface_admissions": build_surface_admissions(admission_payload, fallback_aliases=aliases),
    }
    bridge_config = build_bridge_config(aliases)
    release_status = build_release_status(release_level)
    bundle_manifest = build_bundle_manifest()

    if args.stdout:
        print(
            json.dumps(
                {
                    "output_dir": str(output_dir),
                    "bundle_manifest": bundle_manifest,
                    "surface_admission": surface_admission,
                    "bridge_config": bridge_config,
                    "release_status": release_status,
                    "admission_example": admission_payload,
                },
                indent=2,
                ensure_ascii=True,
            )
        )
        return 0

    output_dir.mkdir(parents=True, exist_ok=True)
    write_json(admission_output, admission_payload)
    write_json(output_dir / "bundle_manifest.json", bundle_manifest)
    write_json(output_dir / "surface_admission.json", surface_admission)
    write_json(output_dir / "bridge_config.json", bridge_config)
    write_json(output_dir / "release_status.json", release_status)
    print(output_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
