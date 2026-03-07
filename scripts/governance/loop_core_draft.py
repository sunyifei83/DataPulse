#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
from typing import Any


def dedupe(items: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for item in items:
        if not item or item in seen:
            continue
        seen.add(item)
        result.append(item)
    return result


def iter_slices(plan: dict[str, Any]) -> list[tuple[str, dict[str, Any]]]:
    result: list[tuple[str, dict[str, Any]]] = []
    for phase in plan.get("phases", []):
        phase_id = phase.get("id", "")
        for item in phase.get("slices", []):
            result.append((phase_id, item))
    return result


def completed_slice_ids(plan: dict[str, Any]) -> list[str]:
    return [item.get("id", "") for _, item in iter_slices(plan) if item.get("status") == "completed"]


def next_open_slice_entry(plan: dict[str, Any]) -> tuple[str, dict[str, Any] | None]:
    for phase_id, item in iter_slices(plan):
        if item.get("status") not in {"completed", "skipped"}:
            return phase_id, item
    return "", None


def current_level_from_promotion_levels(promotion_levels: dict[str, Any]) -> str:
    repo_landed = bool(promotion_levels.get("repo_landed", {}).get("satisfied"))
    ci_proven = bool(promotion_levels.get("ci_proven", {}).get("satisfied"))
    if ci_proven:
        return "ci_proven"
    if repo_landed:
        return "repo_landed"
    return "manual_only"


def remaining_promotion_gates(landing_status: dict[str, Any], wired: bool) -> list[str]:
    promotion_levels = landing_status.get("promotion_levels", {})
    gates: list[str] = []
    gates.extend(promotion_levels.get("repo_landed", {}).get("reasons", []))
    gates.extend(promotion_levels.get("ci_proven", {}).get("reasons", []))
    if not wired:
        gates.append("draft_not_wired")
    return dedupe(gates)


def next_slice_payload(plan: dict[str, Any]) -> dict[str, Any]:
    phase_id, raw_slice = next_open_slice_entry(plan)
    if raw_slice is None:
        return {
            "id": "no-open-slice",
            "title": "No open slice",
            "category": "complete",
        }
    return {
        "id": raw_slice.get("id", ""),
        "title": raw_slice.get("title", ""),
        "category": raw_slice.get("category", "manual"),
        "phase_id": phase_id,
        "execution_profile": raw_slice.get("execution_profile", "draft_only"),
        "promotion_scope": raw_slice.get("promotion_scope", "none"),
        "closes_gates": raw_slice.get("closes_gates", []),
    }


def blocking_facts_for_next_slice(plan: dict[str, Any], landing_status: dict[str, Any], next_slice: dict[str, Any], wired: bool) -> list[str]:
    if next_slice.get("category") == "complete":
        return []
    gate_groups = landing_status.get("gate_groups", {})
    slice_profiles = plan.get("slice_profiles", {})
    execution_profile = next_slice.get("execution_profile", "draft_only")
    profile = slice_profiles.get(execution_profile, {})
    blockers: list[str] = []
    for group_name in profile.get("blocking_gate_groups", []):
        blockers.extend(gate_groups.get(group_name, []))
    if not wired:
        blockers.append("draft_not_wired")
    return dedupe(blockers)


def flow_control_for_state(
    next_slice: dict[str, Any],
    blocking_facts: list[str],
    remaining_gates: list[str],
    wired: bool,
    promotion_mode: str,
) -> tuple[dict[str, Any], str]:
    auto_continuation_enabled = wired and promotion_mode not in {"manual_only", "disabled"}
    readiness_gaps: list[str] = []
    if not wired:
        readiness_gaps.append("draft_not_wired")
    if not auto_continuation_enabled:
        readiness_gaps.append("manual_handoff_still_required")

    if next_slice.get("category") == "complete":
        stop_reason = "loop_complete" if not remaining_gates else "promotion_gates_open"
        return (
            {
                "status_if_run_now": "stopped",
                "reason_if_run_now": stop_reason,
                "machine_decidable_blockers": True,
                "auto_continuation_enabled": auto_continuation_enabled,
                "readiness_gaps": dedupe(readiness_gaps),
            },
            stop_reason,
        )

    draft_stop_reason = "draft_only_not_wired" if not wired else ""
    if blocking_facts:
        return (
            {
                "status_if_run_now": "blocked",
                "reason_if_run_now": draft_stop_reason or "next_slice_blocked",
                "machine_decidable_blockers": True,
                "auto_continuation_enabled": auto_continuation_enabled,
                "readiness_gaps": dedupe(readiness_gaps),
            },
            draft_stop_reason,
        )
    if auto_continuation_enabled:
        return (
            {
                "status_if_run_now": "ready_for_auto_advance",
                "reason_if_run_now": "environment_healthy",
                "machine_decidable_blockers": True,
                "auto_continuation_enabled": auto_continuation_enabled,
                "readiness_gaps": dedupe(readiness_gaps),
            },
            draft_stop_reason,
        )
    return (
        {
            "status_if_run_now": "ready_waiting_manual_handoff",
            "reason_if_run_now": "manual_promotion_mode",
            "machine_decidable_blockers": True,
            "auto_continuation_enabled": auto_continuation_enabled,
            "readiness_gaps": dedupe(readiness_gaps),
        },
        draft_stop_reason,
    )


def control_contract_for_state(next_slice: dict[str, Any], flow_control: dict[str, Any]) -> dict[str, Any]:
    return {
        "progress_truth": {
            "source": "blueprint_plan_next_open_slice",
            "current_next_slice_id": next_slice.get("id", ""),
        },
        "stop_truth": {
            "source": "blocking_facts_and_flow_control",
            "status_if_run_now": flow_control.get("status_if_run_now", ""),
            "reason_if_run_now": flow_control.get("reason_if_run_now", ""),
            "machine_decidable": True,
            "expected_terminal_stop_on_complete": True,
        },
        "reopen_truth": {
            "machine_decidable": True,
            "triggers": [
                {
                    "id": "plan_new_open_slice",
                    "condition": "blueprint_plan_adds_new_open_slice",
                    "reopens": "next_slice_selection",
                },
                {
                    "id": "workspace_reopened",
                    "condition": "workspace_clean_becomes_false_or_new_repo_change_detected",
                    "reopens": "repo_landed_promotion",
                },
                {
                    "id": "promotion_evidence_regressed",
                    "condition": "ci_or_release_evidence_no_longer_satisfies_current_level",
                    "reopens": "promotion_gates",
                },
            ],
        },
        "driver_cycle": {
            "evidence_round_trip_required": True,
            "steps": [
                "export_state_before_action",
                "execute_slice_or_promotion",
                "collect_evidence",
                "re_export_state",
                "stop_or_continue",
            ],
        },
    }


def build_project_loop_state_core(
    plan: dict[str, Any],
    landing_status: dict[str, Any],
    *,
    source_plan: str,
    generated_at_utc: str,
) -> dict[str, Any]:
    activation = plan.get("activation", {})
    wired = bool(activation.get("wired", False))
    promotion_levels = landing_status.get("promotion_levels", {})
    current_level = current_level_from_promotion_levels(promotion_levels)
    next_slice = next_slice_payload(plan)
    blocking_facts = blocking_facts_for_next_slice(plan, landing_status, next_slice, wired)
    remaining_gates = remaining_promotion_gates(landing_status, wired)
    flow_control, stop_reason = flow_control_for_state(
        next_slice,
        blocking_facts,
        remaining_gates,
        wired,
        activation.get("promotion_mode", "manual_only"),
    )
    workspace = landing_status.get("workspace", {})

    return {
        "schema_version": "project_specific_loop_state.v1",
        "project": plan.get("project", landing_status.get("project", "project")),
        "generated_at_utc": generated_at_utc,
        "state_kind": "draft_export",
        "source_plan": source_plan,
        "wired": wired,
        "current_level": current_level,
        "workspace_clean": bool(workspace.get("clean", False)),
        "completed_slices": completed_slice_ids(plan),
        "next_slice": next_slice,
        "remaining_promotion_gates": remaining_gates,
        "blocking_facts": blocking_facts,
        "pipeline_contract": {
            "objective": "trusted_delivery_pipeline",
            "continuous_when_healthy": True,
            "halts_on_machine_decidable_blockers": True,
            "blocked_state_is_expected": True,
            "resume_when": "machine_blockers_cleared_or_next_slice_changes",
        },
        "control_contract": control_contract_for_state(next_slice, flow_control),
        "flow_control": flow_control,
        "promotion_mode": activation.get("promotion_mode", "manual_only"),
        "stop_reason_if_run_now": stop_reason,
    }


def evaluate_loop_status(loop_state: dict[str, Any], ignored_blocking_facts: list[str] | None = None) -> tuple[str, str, list[str]]:
    ignored = set(ignored_blocking_facts or [])
    raw_blockers = list(loop_state.get("blocking_facts", []))
    effective_blockers = [item for item in raw_blockers if item not in ignored]
    next_slice = loop_state.get("next_slice", {})
    next_category = next_slice.get("category", "")

    if next_category == "complete":
        if loop_state.get("remaining_promotion_gates"):
            return "stopped", "promotion_gates_open", effective_blockers
        return "stopped", "loop_complete", effective_blockers
    if effective_blockers:
        return "blocked", "next_slice_blocked", effective_blockers
    return "ready", "awaiting_manual_slice_execution", effective_blockers


def build_trust_summary(loop_state: dict[str, Any]) -> dict[str, Any]:
    flow_control = dict(loop_state.get("flow_control", {}))
    pipeline_contract = dict(loop_state.get("pipeline_contract", {}))
    auto_continuation_enabled = bool(flow_control.get("auto_continuation_enabled", False))
    machine_decidable_blockers = bool(flow_control.get("machine_decidable_blockers", False))
    readiness_gaps = dedupe(list(flow_control.get("readiness_gaps", [])))
    meets_bar = auto_continuation_enabled and machine_decidable_blockers
    return {
        "target_class": pipeline_contract.get("objective", "trusted_delivery_pipeline"),
        "current_class": "trusted_delivery_pipeline" if meets_bar else "bootstrap_loop",
        "healthy_environment_behavior": "continue_without_human_handoff",
        "abnormal_environment_behavior": "stop_on_machine_decidable_blockers",
        "currently_meets_bar": meets_bar,
        "readiness_gaps": readiness_gaps,
    }


def build_reuse_summary(loop_state: dict[str, Any]) -> dict[str, Any]:
    control_contract = dict(loop_state.get("control_contract", {}))
    flow_control = dict(loop_state.get("flow_control", {}))
    implemented: list[str] = []
    if control_contract.get("progress_truth", {}).get("current_next_slice_id"):
        implemented.append("progress_truth")
    if bool(control_contract.get("stop_truth", {}).get("machine_decidable", False)):
        implemented.append("stop_truth")
    if bool(control_contract.get("reopen_truth", {}).get("machine_decidable", False)):
        implemented.append("reopen_truth")
    if bool(control_contract.get("driver_cycle", {}).get("evidence_round_trip_required", False)):
        implemented.append("evidence_round_trip_contract")

    missing: list[str] = []
    if not bool(flow_control.get("auto_continuation_enabled", False)):
        missing.append("auto_continuation_not_enabled")
    if not bool(loop_state.get("wired", False)):
        missing.append("active_repo_truth_not_wired")

    return {
        "reusable_unit": "progress_truth_plus_stop_truth_plus_reopen_truth_plus_evidence_round_trip",
        "implemented_in_draft": implemented,
        "missing_for_active_reuse": missing,
    }
