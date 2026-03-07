#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from loop_core_draft import (
    build_project_loop_state_core,
    build_reuse_summary,
    build_trust_summary,
    dedupe,
    evaluate_loop_status,
    validate_blueprint_plan_structure,
)


REQUIRED_MANIFEST_FIELDS = [
    "schema_version",
    "project",
    "generated_at_utc",
    "bundle_kind",
    "wired",
    "files",
]

REQUIRED_FILE_KEYS = [
    "plan",
    "landing_status",
]


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_bundle_manifest(bundle_dir: Path) -> tuple[Path, dict[str, Any]]:
    manifest_path = bundle_dir / "adapter_bundle_manifest.draft.json"
    return manifest_path, read_json(manifest_path)


def validate_manifest_shape(manifest: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for key in REQUIRED_MANIFEST_FIELDS:
        if key not in manifest:
            errors.append(f"missing_manifest_field:{key}")
    files = manifest.get("files", {})
    if not isinstance(files, dict):
        errors.append("invalid_manifest_files_object")
        return errors
    for key in REQUIRED_FILE_KEYS:
        if not files.get(key):
            errors.append(f"missing_manifest_files_entry:{key}")
    return errors


def resolve_bundle_files(bundle_dir: Path, manifest: dict[str, Any]) -> tuple[dict[str, Path], list[str]]:
    files = dict(manifest.get("files", {}))
    resolved: dict[str, Path] = {}
    missing: list[str] = []
    keys = REQUIRED_FILE_KEYS + (["slice_catalog"] if files.get("slice_catalog") else [])
    for key in keys:
        rel = str(files.get(key, ""))
        path = bundle_dir / rel
        resolved[key] = path
        if not rel or not path.exists():
            missing.append(key)
    return resolved, missing


def resolve_adapter_entry(catalog: dict[str, Any], slice_id: str) -> dict[str, Any]:
    return dict(catalog.get("slices", {}).get(slice_id, {}))


def build_bundle_runtime_payload(
    bundle_dir: Path,
    ignore_blocking_facts: list[str] | None = None,
) -> tuple[dict[str, Any], list[str], dict[str, str], str]:
    ignored = ignore_blocking_facts or []
    manifest_path, manifest = load_bundle_manifest(bundle_dir)
    errors = validate_manifest_shape(manifest)
    resolved, missing = resolve_bundle_files(bundle_dir, manifest)
    resolved_files = {key: str(value) for key, value in resolved.items()}
    if errors or missing:
        return {}, errors + [f"missing_bundle_file:{item}" for item in missing], resolved_files, str(manifest_path)

    plan = read_json(resolved["plan"])
    plan_errors = validate_blueprint_plan_structure(plan)
    if plan_errors:
        return (
            {},
            [f"invalid_blueprint_plan:{item}" for item in plan_errors],
            resolved_files,
            str(manifest_path),
        )
    landing_status = read_json(resolved["landing_status"])
    loop_state = build_project_loop_state_core(
        plan,
        landing_status,
        source_plan=str(resolved["plan"]),
        generated_at_utc=str(manifest.get("generated_at_utc", "")),
    )
    status, reason, effective_blockers = evaluate_loop_status(loop_state, ignored)
    next_slice = dict(loop_state.get("next_slice", {}))
    adapter_entry = {}
    slice_catalog = resolved.get("slice_catalog")
    if slice_catalog and slice_catalog.exists():
        adapter_entry = resolve_adapter_entry(read_json(slice_catalog), next_slice.get("id", ""))

    payload = {
        "status": status,
        "reason": reason,
        "project": loop_state.get("project", ""),
        "current_level": loop_state.get("current_level", ""),
        "next_slice": next_slice,
        "blocking_facts": loop_state.get("blocking_facts", []),
        "effective_blocking_facts": effective_blockers,
        "ignored_blocking_facts": dedupe(ignored),
        "remaining_promotion_gates": loop_state.get("remaining_promotion_gates", []),
        "pipeline_contract": loop_state.get("pipeline_contract", {}),
        "control_contract": loop_state.get("control_contract", {}),
        "flow_control": loop_state.get("flow_control", {}),
        "trust_summary": build_trust_summary(loop_state),
        "reuse_summary": build_reuse_summary(loop_state),
        "adapter_entry": adapter_entry,
        "bundle_manifest": str(manifest_path),
    }
    return payload, [], resolved_files, str(manifest_path)


def comparable_loop_payload(payload: dict[str, Any]) -> dict[str, Any]:
    keys = [
        "status",
        "reason",
        "project",
        "current_level",
        "next_slice",
        "blocking_facts",
        "effective_blocking_facts",
        "remaining_promotion_gates",
        "pipeline_contract",
        "control_contract",
        "flow_control",
        "trust_summary",
        "reuse_summary",
    ]
    return {key: payload.get(key) for key in keys}


def compare_loop_payloads(expected: dict[str, Any], actual: dict[str, Any]) -> list[str]:
    mismatches: list[str] = []
    expected_comp = comparable_loop_payload(expected)
    actual_comp = comparable_loop_payload(actual)
    for key, expected_value in expected_comp.items():
        if actual_comp.get(key) != expected_value:
            mismatches.append(f"mismatch:{key}")
    return mismatches
