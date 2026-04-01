#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ast
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CAPABILITY_CATALOG_PATH = REPO_ROOT / "docs/governance/datapulse-surface-capability-catalog.draft.json"
DEFAULT_BRIDGE_CONFIG_PATH = REPO_ROOT / "config/modelbus/datapulse/bridge_config.json"
DEFAULT_SURFACE_ADMISSION_PATH = REPO_ROOT / "config/modelbus/datapulse/surface_admission.json"
DEFAULT_READER_PATH = REPO_ROOT / "datapulse/reader.py"
DEFAULT_OUTPUT_PATH = REPO_ROOT / "docs/governance/datapulse-internal-ai-surface-registry.draft.json"

_EXPECTED_SURFACES = [
    {
        "surface_id": "ai_surface_precheck",
        "capability_id": "governed_ai_surface_precheck",
        "registry_class": "governance_precheck",
        "subject_kind": "GovernedAISurface",
        "output_kind": "precheck",
        "bridge_bound": False,
    },
    {
        "surface_id": "mission_suggest",
        "capability_id": "governed_ai_mission_suggest",
        "registry_class": "governed_projection",
        "bridge_bound": True,
    },
    {
        "surface_id": "triage_assist",
        "capability_id": "governed_ai_triage_assist",
        "registry_class": "governed_projection",
        "bridge_bound": True,
    },
    {
        "surface_id": "claim_draft",
        "capability_id": "governed_ai_claim_draft",
        "registry_class": "governed_projection",
        "bridge_bound": True,
    },
    {
        "surface_id": "report_draft",
        "capability_id": "governed_ai_report_draft",
        "registry_class": "governed_projection",
        "bridge_bound": True,
    },
    {
        "surface_id": "delivery_summary",
        "capability_id": "governed_ai_delivery_summary",
        "registry_class": "governed_projection",
        "bridge_bound": True,
    },
]


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def display_path(path: Path) -> str:
    resolved = path.resolve()
    if resolved.is_relative_to(REPO_ROOT):
        return str(resolved.relative_to(REPO_ROOT))
    return str(resolved)


def dedupe(values: List[str]) -> List[str]:
    result: List[str] = []
    seen = set()
    for raw in values:
        value = str(raw or "").strip()
        if not value or value in seen:
            continue
        seen.add(value)
        result.append(value)
    return result


def extract_literal_assignments(path: Path, names: List[str]) -> Dict[str, Any]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    wanted = set(names)
    assignments: Dict[str, Any] = {}
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if not isinstance(target, ast.Name) or target.id not in wanted:
                    continue
                assignments[target.id] = ast.literal_eval(node.value)
            continue
        if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name) and node.target.id in wanted:
            assignments[node.target.id] = ast.literal_eval(node.value)
    missing = sorted(wanted - set(assignments))
    if missing:
        raise ValueError(f"Missing literal assignments in {display_path(path)}: {', '.join(missing)}")
    return assignments


def build_capability_index(catalog: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    return {
        str(item.get("id", "")).strip(): item
        for item in catalog.get("capabilities", [])
        if str(item.get("id", "")).strip()
    }


def build_admission_index(admission_payload: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    return {
        str(item.get("surface_id", "")).strip(): item
        for item in admission_payload.get("surface_admissions", [])
        if str(item.get("surface_id", "")).strip()
    }


def bound_tools_from_capability(capability: Dict[str, Any]) -> List[str]:
    mcp = capability.get("surfaces", {}).get("mcp", {})
    entrypoints = mcp.get("entrypoints", []) if isinstance(mcp, dict) else []
    tool_ids = []
    for entrypoint in entrypoints:
        raw = str(entrypoint).strip()
        if raw.startswith("tool:"):
            tool_ids.append(raw.split(":", 1)[1])
    return dedupe(tool_ids)


def projection_layers(capability: Dict[str, Any]) -> List[str]:
    layers = []
    for layer, payload in capability.get("surfaces", {}).items():
        if not isinstance(payload, dict):
            continue
        if str(payload.get("availability", "")).strip() == "available":
            layers.append(str(layer).strip())
    return layers


def build_surface_row(
    spec: Dict[str, Any],
    capability: Dict[str, Any],
    bridge_alias_by_surface: Dict[str, str],
    admission_by_surface: Dict[str, Dict[str, Any]],
    lifecycle_anchors: Dict[str, str],
    output_kinds: Dict[str, str],
) -> Dict[str, Any]:
    surface_id = spec["surface_id"]
    capability_id = spec["capability_id"]
    governed_surface_id = str(capability.get("governed_ai_surface_id", "")).strip()
    if spec.get("bridge_bound", False) and governed_surface_id != surface_id:
        raise ValueError(
            f"Capability {capability_id} expected governed_ai_surface_id={surface_id} but found {governed_surface_id or '<missing>'}"
        )

    admission_row = admission_by_surface.get(surface_id, {})
    bound_aliases: List[str] = []
    if spec.get("bridge_bound", False):
        bound_aliases = dedupe(
            [
                str(bridge_alias_by_surface.get(surface_id, "")).strip(),
                str(admission_row.get("requested_alias", "")).strip(),
                str(admission_row.get("admitted_alias", "")).strip(),
            ]
        )

    subject_kind = str(spec.get("subject_kind", "")).strip() or str(lifecycle_anchors.get(surface_id, "")).strip()
    output_kind = str(spec.get("output_kind", "")).strip() or str(output_kinds.get(surface_id, "")).strip()

    return {
        "surface_id": surface_id,
        "registry_class": spec["registry_class"],
        "owner_seam": str(capability.get("owner_seam", "")).strip(),
        "capability_id": capability_id,
        "governed_ai_surface_id": governed_surface_id,
        "internal_only": True,
        "external_publication_promise": False,
        "customer_runtime_enabled": False,
        "subject_kind": subject_kind,
        "output_kind": output_kind,
        "schema_contract_id": str(admission_row.get("schema_contract", "")).strip(),
        "bound_aliases": bound_aliases,
        "bound_tools": bound_tools_from_capability(capability),
        "projection_layers": projection_layers(capability),
        "projections": capability.get("surfaces", {}),
    }


def build_payload(
    capability_catalog_path: Path,
    bridge_config_path: Path,
    surface_admission_path: Path,
    reader_path: Path,
) -> Dict[str, Any]:
    catalog = read_json(capability_catalog_path)
    bridge_config = read_json(bridge_config_path)
    surface_admission = read_json(surface_admission_path)
    reader_assignments = extract_literal_assignments(
        reader_path,
        ["_AI_SURFACE_LIFECYCLE_ANCHORS", "_AI_SURFACE_OUTPUT_KINDS"],
    )
    capabilities = build_capability_index(catalog)
    admissions = build_admission_index(surface_admission)
    bridge_alias_by_surface = {
        str(key).strip(): str(value).strip()
        for key, value in bridge_config.get("alias_by_surface", {}).items()
        if str(key).strip()
    }

    surfaces = []
    for spec in _EXPECTED_SURFACES:
        capability_id = spec["capability_id"]
        capability = capabilities.get(capability_id)
        if capability is None:
            raise ValueError(f"Capability not found in catalog: {capability_id}")
        surfaces.append(
            build_surface_row(
                spec,
                capability,
                bridge_alias_by_surface,
                admissions,
                reader_assignments["_AI_SURFACE_LIFECYCLE_ANCHORS"],
                reader_assignments["_AI_SURFACE_OUTPUT_KINDS"],
            )
        )

    return {
        "schema_version": "datapulse_internal_ai_surface_registry.v1",
        "registry_id": "datapulse_internal_ai_surfaces",
        "generated_at_utc": utc_now(),
        "state_kind": "draft_export",
        "publication_boundary": {
            "classification": "internal_only",
            "external_publication_promise": False,
            "customer_runtime_enabled": False,
            "notes": [
                "This registry enumerates current repo-native internal AI surfaces only.",
                "Presence in this registry must not be interpreted as an external publication or subscription promise.",
            ],
        },
        "sources": {
            "capability_catalog": display_path(capability_catalog_path),
            "bridge_config": display_path(bridge_config_path),
            "surface_admission": display_path(surface_admission_path),
            "reader_runtime_contract": display_path(reader_path),
        },
        "surface_ids": [row["surface_id"] for row in surfaces],
        "surfaces": surfaces,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Export the repo-native registry of current internal DataPulse AI surfaces."
    )
    parser.add_argument(
        "--capability-catalog",
        type=Path,
        default=DEFAULT_CAPABILITY_CATALOG_PATH,
        help="Capability catalog that declares AI projection entrypoints.",
    )
    parser.add_argument(
        "--bridge-config",
        type=Path,
        default=DEFAULT_BRIDGE_CONFIG_PATH,
        help="Bridge config that binds current internal surface aliases.",
    )
    parser.add_argument(
        "--surface-admission",
        type=Path,
        default=DEFAULT_SURFACE_ADMISSION_PATH,
        help="Surface admission facts used for current contract bindings.",
    )
    parser.add_argument(
        "--reader",
        type=Path,
        default=DEFAULT_READER_PATH,
        help="Reader module used for lifecycle anchor and output-kind literals.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT_PATH,
        help="Output path for the draft registry JSON.",
    )
    parser.add_argument(
        "--stdout",
        action="store_true",
        help="Print JSON to stdout instead of writing the output file.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = build_payload(
        capability_catalog_path=args.capability_catalog,
        bridge_config_path=args.bridge_config,
        surface_admission_path=args.surface_admission,
        reader_path=args.reader,
    )
    if args.stdout:
        print(json.dumps(payload, indent=2, ensure_ascii=True))
        return 0
    write_json(args.output, payload)
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
