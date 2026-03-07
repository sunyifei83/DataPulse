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


def load_datapulse_catalog(path: Path = DEFAULT_CATALOG_PATH) -> dict[str, Any]:
    return read_json(path)


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
    adapter_entry = resolve_datapulse_adapter_entry(catalog, next_slice.get("id", ""))
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
        "decoupling_summary": {
            "blocking_facts_scope": "current-next-slice-only",
            "remaining_gates_scope": "global-open-gates",
            "service_governance_coupling": "adapter-mediated",
        },
    }
