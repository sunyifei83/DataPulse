#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
from typing import Any

from datapulse_loop_contracts import (
    DEFAULT_PLAN_PATH,
    REPO_ROOT,
    build_code_landing_status,
    build_project_loop_state,
    load_plan,
    read_json,
)
from loop_core_draft import build_reuse_summary, build_trust_summary, dedupe, evaluate_loop_status


DEFAULT_CATALOG_PATH = REPO_ROOT / "docs/governance/datapulse-slice-adapter-catalog.draft.json"


def _to_text(value: Any) -> str:
    return str(value).strip() if value is not None else ""


def load_datapulse_catalog(path: Path = DEFAULT_CATALOG_PATH) -> dict[str, Any]:
    return read_json(path)


def find_plan_slice(plan: dict[str, Any], slice_id: str) -> dict[str, Any]:
    target = _to_text(slice_id)
    if not target:
        return {}
    for phase in plan.get("phases", []):
        for item in phase.get("slices", []):
            if _to_text(item.get("id")) == target:
                return dict(item)
    return {}


def default_execute_mode(execution_profile: str, category: str) -> str:
    profile = _to_text(execution_profile).lower()
    category_text = _to_text(category).lower()
    if profile == "draft_only":
        return "manual_edit"
    if profile == "local_wrapper":
        return "manual_local_command"
    if profile == "workflow_change":
        return "manual_edit"
    if profile == "release_policy_change":
        return "manual_analysis"
    if profile == "runtime_validation":
        return "manual_validation"
    if category_text == "promotion":
        return "promotion_managed_by_loop"
    return "manual_edit"


def fallback_candidate_commands(slice_payload: dict[str, Any]) -> list[str]:
    commands = [_to_text(item) for item in slice_payload.get("verification_commands", []) if _to_text(item)]
    if commands:
        return dedupe(commands)

    targets = [
        _to_text(item)
        for item in [*slice_payload.get("artifacts", []), *slice_payload.get("draft_artifacts", [])]
        if _to_text(item)
    ]
    generated: list[str] = []
    for item in targets:
        if item.endswith(".py"):
            generated.append(f"python3 {item} --help")
        elif item.endswith(".sh"):
            generated.append(f"bash -n {item}")
        else:
            generated.append(f"sed -n '1,220p' {item}")
    return dedupe(generated)


def fallback_notes(slice_payload: dict[str, Any], next_slice: dict[str, Any], *, catalog_entry_exists: bool) -> list[str]:
    notes: list[str] = []
    exit_condition = _to_text(slice_payload.get("exit_condition"))
    if exit_condition:
        notes.append(f"exit_condition: {exit_condition}")
    promotion_scope = _to_text(next_slice.get("promotion_scope"))
    if promotion_scope:
        notes.append(f"promotion_scope: {promotion_scope}")
    closes_gates = [item for item in next_slice.get("closes_gates", []) if _to_text(item)]
    if closes_gates:
        notes.append(f"closes_gates: {', '.join(closes_gates)}")
    source_note = dict(slice_payload.get("fact_intake", {}).get("source_note", {}))
    source_note_path = _to_text(source_note.get("path"))
    if source_note_path:
        notes.append(f"source_note: {source_note_path}")
        selected_heading = _to_text(source_note.get("selected_heading"))
        if selected_heading:
            notes.append(f"source_note_heading: {selected_heading}")
    fact_sources = [_to_text(item) for item in slice_payload.get("fact_sources", []) if _to_text(item)]
    for item in fact_sources[:3]:
        notes.append(f"fact_source: {item}")
    if not catalog_entry_exists:
        notes.append("No explicit slice catalog entry exists; this brief is synthesized from the structured blueprint slice.")
    return dedupe(notes)


def build_datapulse_slice_execution_brief(
    plan: dict[str, Any],
    catalog: dict[str, Any],
    next_slice: dict[str, Any],
) -> dict[str, Any]:
    slice_id = _to_text(next_slice.get("id"))
    if not slice_id or slice_id == "no-open-slice":
        return {}

    catalog_entry = dict(catalog.get("slices", {}).get(slice_id, {}))
    plan_slice = find_plan_slice(plan, slice_id)
    summary = _to_text(catalog_entry.get("summary")) or _to_text(plan_slice.get("title")) or _to_text(next_slice.get("title"))
    target_artifacts = dedupe(
        [
            _to_text(item)
            for item in [
                *catalog_entry.get("target_artifacts", []),
                *plan_slice.get("artifacts", []),
                *plan_slice.get("draft_artifacts", []),
            ]
            if _to_text(item)
        ]
    )
    candidate_commands = dedupe(
        [
            _to_text(item)
            for item in [
                *catalog_entry.get("candidate_commands", []),
                *fallback_candidate_commands(plan_slice),
            ]
            if _to_text(item)
        ]
    )
    verification_commands = dedupe(
        [
            _to_text(item)
            for item in plan_slice.get("verification_commands", [])
            if _to_text(item)
        ]
    )
    notes = dedupe(
        [
            _to_text(item)
            for item in [
                *catalog_entry.get("notes", []),
                *fallback_notes(plan_slice, next_slice, catalog_entry_exists=bool(catalog_entry)),
            ]
            if _to_text(item)
        ]
    )

    return {
        "slice_id": slice_id,
        "phase_id": _to_text(next_slice.get("phase_id")),
        "title": _to_text(next_slice.get("title")),
        "category": _to_text(next_slice.get("category")),
        "execution_profile": _to_text(next_slice.get("execution_profile")),
        "adapter_type": _to_text(catalog_entry.get("adapter_type")) or _to_text(next_slice.get("execution_profile")) or "structured_slice",
        "execute_mode": _to_text(catalog_entry.get("execute_mode"))
        or default_execute_mode(next_slice.get("execution_profile", ""), next_slice.get("category", "")),
        "summary": summary,
        "candidate_commands": candidate_commands,
        "verification_commands": verification_commands,
        "target_artifacts": target_artifacts,
        "exit_condition": _to_text(plan_slice.get("exit_condition")),
        "notes": notes,
        "source": {
            "catalog_entry": bool(catalog_entry),
            "plan_slice": bool(plan_slice),
        },
    }


def resolve_datapulse_adapter_entry(catalog: dict[str, Any], slice_id: str) -> dict[str, Any]:
    return dict(catalog.get("slices", {}).get(slice_id, {}))


def build_datapulse_loop_runtime(
    plan_path: Path = DEFAULT_PLAN_PATH,
    catalog_path: Path = DEFAULT_CATALOG_PATH,
    ignore_blocking_facts: list[str] | None = None,
) -> dict[str, Any]:
    ignored = ignore_blocking_facts or []
    plan = load_plan(plan_path)
    plan["_source_path"] = str(plan_path.resolve())
    code_landing_status = build_code_landing_status()
    loop_state = build_project_loop_state(plan, code_landing_status)
    next_slice = dict(loop_state.get("next_slice", {}))
    catalog = load_datapulse_catalog(catalog_path)
    adapter_entry = build_datapulse_slice_execution_brief(plan, catalog, next_slice)
    status, reason, effective_blockers = evaluate_loop_status(loop_state, ignored)

    return {
        "status": status,
        "reason": reason,
        "plan_id": plan.get("plan_id", ""),
        "project": plan.get("project", "DataPulse"),
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
        "slice_execution_brief": adapter_entry,
        "decoupling_summary": {
            "blocking_facts_scope": "current-next-slice-only",
            "remaining_gates_scope": "global-open-gates",
            "service_governance_coupling": "adapter-mediated",
        },
    }
