#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_REGISTRY_PATH = REPO_ROOT / "docs/governance/datapulse-internal-ai-surface-registry.draft.json"
DEFAULT_BRIDGE_CONFIG_PATH = REPO_ROOT / "config/modelbus/datapulse/bridge_config.json"
DEFAULT_SURFACE_ADMISSION_PATH = REPO_ROOT / "config/modelbus/datapulse/surface_admission.json"
DEFAULT_OUTPUT_PATH = REPO_ROOT / "out/governance/datapulse_internal_ai_surface_admission.draft.json"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def display_path(path: Path) -> str:
    resolved = path.resolve()
    if resolved.is_relative_to(REPO_ROOT):
        return str(resolved.relative_to(REPO_ROOT))
    return str(resolved)


def dedupe(values: list[str]) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for raw in values:
        value = str(raw or "").strip()
        if not value or value in seen:
            continue
        seen.add(value)
        result.append(value)
    return result


def build_admission_index(payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        str(item.get("surface_id", "")).strip(): item
        for item in payload.get("surface_admissions", [])
        if str(item.get("surface_id", "")).strip()
    }


def blocking_failure_reason(admission_row: dict[str, Any]) -> str:
    for gap in admission_row.get("rejectable_gaps", []):
        if not isinstance(gap, dict):
            continue
        if bool(gap.get("blocking", False)):
            reason = str(gap.get("reason", "")).strip()
            if reason:
                return reason
    return ""


def schema_verdict(surface_row: dict[str, Any], admission_row: dict[str, Any]) -> str:
    surface_id = str(surface_row.get("surface_id", "")).strip()
    schema_contract_id = str(surface_row.get("schema_contract_id", "")).strip() or str(
        admission_row.get("schema_contract", "")
    ).strip()
    if surface_id == "ai_surface_precheck":
        return "not_applicable"
    if schema_contract_id:
        return "schema_bound"
    if surface_id == "report_draft":
        return "missing_contract_fail_closed"
    if str(admission_row.get("admission_status", "")).strip() == "rejected":
        return "missing_schema_contract"
    return "unknown"


def policy_verdict(surface_row: dict[str, Any], admission_row: dict[str, Any]) -> str:
    surface_id = str(surface_row.get("surface_id", "")).strip()
    admission_status = str(admission_row.get("admission_status", "")).strip()
    if surface_id == "ai_surface_precheck":
        return "precheck_only"
    if admission_status == "admitted":
        return "admitted"
    if surface_id == "report_draft":
        return "fail_closed"
    if admission_status == "rejected":
        return "rejected"
    return "unknown"


def build_row(
    surface_row: dict[str, Any],
    bridge_alias_by_surface: dict[str, str],
    admission_by_surface: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    surface_id = str(surface_row.get("surface_id", "")).strip()
    if not surface_id:
        raise ValueError("Registry surface row missing surface_id.")

    admission_row = admission_by_surface.get(surface_id, {})
    schema_contract_id = str(surface_row.get("schema_contract_id", "")).strip() or str(
        admission_row.get("schema_contract", "")
    ).strip()
    bound_aliases = dedupe(
        [
            *[str(item).strip() for item in surface_row.get("bound_aliases", [])],
            str(bridge_alias_by_surface.get(surface_id, "")).strip(),
            str(admission_row.get("requested_alias", "")).strip(),
            str(admission_row.get("admitted_alias", "")).strip(),
        ]
    )
    bound_tools = dedupe([str(item).strip() for item in surface_row.get("bound_tools", [])])
    tool_schema_verdict = schema_verdict(surface_row, admission_row)
    tool_policy_verdict = policy_verdict(surface_row, admission_row)
    failure_reason = blocking_failure_reason(admission_row)

    return {
        "surface_id": surface_id,
        "bound_aliases": bound_aliases,
        "bound_tools": bound_tools,
        "tool_schema_verdict": tool_schema_verdict,
        "tool_policy_verdict": tool_policy_verdict,
        "failure_reason": failure_reason,
        "schema_contract_id": schema_contract_id,
        "requested_alias": str(admission_row.get("requested_alias", "")).strip(),
        "admitted_alias": str(admission_row.get("admitted_alias", "")).strip(),
        "admission_status": str(admission_row.get("admission_status", "")).strip(),
        "manual_fallback": str(admission_row.get("manual_fallback", "")).strip(),
        "fail_closed": tool_policy_verdict == "fail_closed",
    }


def build_payload(
    registry_path: Path,
    bridge_config_path: Path,
    surface_admission_path: Path,
) -> dict[str, Any]:
    registry_payload = read_json(registry_path)
    bridge_config = read_json(bridge_config_path)
    surface_admission = read_json(surface_admission_path)

    surfaces = list(registry_payload.get("surfaces", []))
    admission_by_surface = build_admission_index(surface_admission)
    bridge_alias_by_surface = {
        str(key).strip(): str(value).strip()
        for key, value in bridge_config.get("alias_by_surface", {}).items()
        if str(key).strip()
    }

    rows = [build_row(surface_row, bridge_alias_by_surface, admission_by_surface) for surface_row in surfaces]
    report_draft_row = next((row for row in rows if row["surface_id"] == "report_draft"), None)
    if report_draft_row is None:
        raise ValueError("Registry did not emit report_draft; fail_closed truth would be lost.")
    if report_draft_row["tool_policy_verdict"] != "fail_closed":
        raise ValueError("report_draft must remain explicitly fail_closed in internal admission rows.")

    policy_verdict_counts: dict[str, int] = {}
    schema_verdict_counts: dict[str, int] = {}
    for row in rows:
        policy_verdict = row["tool_policy_verdict"]
        schema_verdict_value = row["tool_schema_verdict"]
        policy_verdict_counts[policy_verdict] = policy_verdict_counts.get(policy_verdict, 0) + 1
        schema_verdict_counts[schema_verdict_value] = schema_verdict_counts.get(schema_verdict_value, 0) + 1

    return {
        "schema_version": "datapulse_internal_ai_surface_admission.v1",
        "admission_id": "datapulse_internal_ai_surface_admission",
        "generated_at_utc": utc_now(),
        "state_kind": "draft_export",
        "sources": {
            "internal_ai_surface_registry": display_path(registry_path),
            "bridge_config": display_path(bridge_config_path),
            "surface_admission": display_path(surface_admission_path),
        },
        "surface_ids": [row["surface_id"] for row in rows],
        "surface_admission_rows": rows,
        "summary": {
            "surface_count": len(rows),
            "policy_verdict_counts": policy_verdict_counts,
            "schema_verdict_counts": schema_verdict_counts,
            "fail_closed_surface_ids": [row["surface_id"] for row in rows if row["fail_closed"]],
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Export minimal admission verdict rows for each DataPulse internal AI surface."
    )
    parser.add_argument(
        "--registry",
        type=Path,
        default=DEFAULT_REGISTRY_PATH,
        help="Path to datapulse-internal-ai-surface-registry.draft.json.",
    )
    parser.add_argument(
        "--bridge-config",
        type=Path,
        default=DEFAULT_BRIDGE_CONFIG_PATH,
        help="Path to the ModelBus bridge config.",
    )
    parser.add_argument(
        "--surface-admission",
        type=Path,
        default=DEFAULT_SURFACE_ADMISSION_PATH,
        help="Path to the admitted surface facts.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT_PATH,
        help="Output path for the internal AI surface admission draft JSON.",
    )
    parser.add_argument(
        "--stdout",
        action="store_true",
        help="Print JSON to stdout instead of writing the output file.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = build_payload(args.registry, args.bridge_config, args.surface_admission)
    if args.stdout:
        print(json.dumps(payload, indent=2, ensure_ascii=True))
        return 0
    write_json(args.output, payload)
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
