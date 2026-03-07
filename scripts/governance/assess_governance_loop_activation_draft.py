#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from loop_bundle_draft import build_bundle_runtime_payload, load_bundle_manifest, read_json, resolve_bundle_files, validate_manifest_shape
from loop_core_draft import dedupe


SURFACE_DEFINITIONS: dict[str, dict[str, Any]] = {
    "adapter_repo_truth_exporter": {
        "order": 10,
        "layer": "project_adapter",
        "impact_scope": "adapter_only",
        "touches_active_workflows": False,
        "required_for": ["repo_landed", "trusted_delivery_pipeline"],
        "summary": "Export machine-readable repository landing truth from the project adapter.",
        "artifact_tokens": ["adapter_module", "landing_status_path", "plan_path"],
    },
    "adapter_ci_truth_exporter": {
        "order": 20,
        "layer": "project_adapter",
        "impact_scope": "adapter_only",
        "touches_active_workflows": False,
        "required_for": ["ci_proven", "trusted_delivery_pipeline"],
        "summary": "Export machine-readable CI or evidence truth instead of leaving CI promotion opaque.",
        "artifact_tokens": ["adapter_module", "landing_status_path", "plan_path"],
    },
    "adapter_verification_gate_contract": {
        "order": 30,
        "layer": "project_adapter",
        "impact_scope": "adapter_only",
        "touches_active_workflows": False,
        "required_for": ["machine_decidable_blockers", "trusted_delivery_pipeline"],
        "summary": "Promote report-oriented verification into strict gate contracts or explicit wrappers.",
        "artifact_tokens": ["adapter_module", "landing_status_path"],
    },
    "repo_driver_wiring": {
        "order": 40,
        "layer": "repo_governance",
        "impact_scope": "activation_only",
        "touches_active_workflows": True,
        "required_for": ["active_loop", "trusted_delivery_pipeline"],
        "summary": "Wire the reusable loop into an explicit repository entrypoint without embedding project semantics into the core.",
        "artifact_tokens": ["plan_path", "bundle_runner", "repo_activation_path"],
    },
    "repo_auto_continuation_policy": {
        "order": 50,
        "layer": "repo_governance",
        "impact_scope": "activation_only",
        "touches_active_workflows": True,
        "required_for": ["continuous_when_healthy", "trusted_delivery_pipeline"],
        "summary": "Replace manual relay with an explicit auto-continuation policy once machine blockers clear.",
        "artifact_tokens": ["plan_path", "bundle_runner", "repo_activation_path"],
    },
    "repo_workflow_dispatch_entrypoint": {
        "order": 60,
        "layer": "repo_governance",
        "impact_scope": "activation_only",
        "touches_active_workflows": True,
        "required_for": ["workflow_round_trip", "trusted_delivery_pipeline"],
        "summary": "Provide a machine-triggerable repository workflow or scheduler entrypoint for evidence collection or promotion.",
        "artifact_tokens": ["repo_activation_path", "plan_path"],
    },
    "repo_release_evidence_contract": {
        "order": 70,
        "layer": "repo_governance",
        "impact_scope": "activation_only",
        "touches_active_workflows": True,
        "required_for": ["release_round_trip", "trusted_delivery_pipeline"],
        "summary": "Publish structured release evidence that the loop can re-ingest after promotion.",
        "artifact_tokens": ["release_evidence_path", "landing_status_path"],
    },
}

SIGNAL_TO_SURFACE = {
    "repo_truth_not_exported": "adapter_repo_truth_exporter",
    "ci_truth_not_exported": "adapter_ci_truth_exporter",
    "verification_not_fully_gateable": "adapter_verification_gate_contract",
    "draft_not_wired": "repo_driver_wiring",
    "active_repo_truth_not_wired": "repo_driver_wiring",
    "manual_handoff_still_required": "repo_auto_continuation_policy",
    "auto_continuation_not_enabled": "repo_auto_continuation_policy",
    "workflow_dispatch_missing": "repo_workflow_dispatch_entrypoint",
    "structured_release_bundle_missing": "repo_release_evidence_contract",
}

OPERATING_FACTS = {
    "workspace_dirty": {
        "category": "working_copy",
        "summary": "The workspace is dirty, so the loop should stop instead of promoting repo-level truth.",
    },
    "latest_local_smoke_failed": {
        "category": "local_verification",
        "summary": "The latest local smoke evidence is failing and should remain a runtime blocker, not a core coupling point.",
    },
    "latest_remote_smoke_failed": {
        "category": "runtime_governance",
        "summary": "The latest remote or HA evidence is failing and should remain an operational blocker.",
    },
    "emergency_stop": {
        "category": "runtime_safety",
        "summary": "Emergency stop is asserted and should halt progression as a machine-decidable runtime blocker.",
    },
    "docs_only_changes_skip_ci": {
        "category": "policy_constraint",
        "summary": "Current CI policy skips docs-only changes, so promotion truth must treat the absence of CI evidence explicitly.",
    },
    "repo_landed_false": {
        "category": "derived_promotion_gate",
        "summary": "Repository promotion is currently unsatisfied. Treat the more specific machine facts as the real blockers instead of coupling this derived gate into activation design.",
    },
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Assess the activation boundary of a governance loop bundle without wiring it into active workflows."
    )
    parser.add_argument(
        "--bundle-dir",
        type=Path,
        required=True,
        help="Directory containing adapter_bundle_manifest.draft.json and referenced snapshot files.",
    )
    return parser.parse_args()


def signal_sort_key(signal: str) -> tuple[int, str]:
    if signal in SIGNAL_TO_SURFACE:
        surface = SURFACE_DEFINITIONS[SIGNAL_TO_SURFACE[signal]]
        return int(surface.get("order", 999)), signal
    if signal in OPERATING_FACTS:
        return 900, signal
    if looks_like_activation_signal(signal):
        return 800, signal
    return 950, signal


def looks_like_activation_signal(signal: str) -> bool:
    activation_tokens = [
        "not_wired",
        "not_exported",
        "missing",
        "manual_handoff",
        "not_enabled",
    ]
    return any(token in signal for token in activation_tokens)


def artifact_value(token: str, manifest: dict[str, Any], resolved_files: dict[str, str]) -> str:
    adapter_metadata = manifest.get("adapter_metadata", {})
    token_map = {
        "adapter_module": str(adapter_metadata.get("adapter_module", "scripts/governance/<project>_loop_adapter.py")),
        "bundle_runner": str(adapter_metadata.get("core_runner", "scripts/governance/run_governance_loop_bundle_draft.py")),
        "bundle_validator": str(adapter_metadata.get("validator", "scripts/governance/validate_governance_loop_bundle_draft.py")),
        "plan_path": resolved_files.get("plan", ""),
        "landing_status_path": resolved_files.get("landing_status", ""),
        "slice_catalog_path": resolved_files.get("slice_catalog", ""),
        "repo_activation_path": "repository workflow, scheduler, or explicit loop trigger entrypoint",
        "release_evidence_path": "structured release evidence sidecar or bundle",
    }
    return token_map.get(token, token)


def build_surface_entry(
    surface_id: str,
    signals: list[str],
    manifest: dict[str, Any],
    resolved_files: dict[str, str],
) -> dict[str, Any]:
    definition = SURFACE_DEFINITIONS[surface_id]
    return {
        "surface_id": surface_id,
        "layer": definition["layer"],
        "impact_scope": definition["impact_scope"],
        "touches_active_workflows": definition["touches_active_workflows"],
        "required_for": definition["required_for"],
        "summary": definition["summary"],
        "from_signals": sorted(dedupe(signals)),
        "suggested_artifacts": dedupe(
            [artifact_value(token, manifest, resolved_files) for token in definition.get("artifact_tokens", []) if artifact_value(token, manifest, resolved_files)]
        ),
    }


def build_unknown_activation_surface(signal: str, manifest: dict[str, Any], resolved_files: dict[str, str]) -> dict[str, Any]:
    return {
        "surface_id": f"project_specific_activation_surface:{signal}",
        "layer": "project_adapter",
        "impact_scope": "adapter_only",
        "touches_active_workflows": False,
        "required_for": ["project_specific_truth"],
        "summary": "This signal looks like a missing project-specific activation contract and should stay in the adapter layer.",
        "from_signals": [signal],
        "suggested_artifacts": dedupe(
            [
                artifact_value("adapter_module", manifest, resolved_files),
                artifact_value("plan_path", manifest, resolved_files),
                artifact_value("bundle_validator", manifest, resolved_files),
            ]
        ),
    }


def build_operating_fact_entry(signal: str) -> dict[str, Any]:
    definition = OPERATING_FACTS.get(
        signal,
        {
            "category": "machine_blocker",
            "summary": "This is a machine-decidable operating blocker and should not be promoted into reusable-core coupling.",
        },
    )
    return {
        "fact": signal,
        "category": definition["category"],
        "summary": definition["summary"],
    }


def collect_activation_signals(payload: dict[str, Any]) -> list[str]:
    signals: list[str] = []
    signals.extend(payload.get("blocking_facts", []))
    signals.extend(payload.get("remaining_promotion_gates", []))
    signals.extend(payload.get("flow_control", {}).get("readiness_gaps", []))
    signals.extend(payload.get("reuse_summary", {}).get("missing_for_active_reuse", []))
    return sorted(dedupe(signals), key=signal_sort_key)


def build_activation_boundary(
    plan: dict[str, Any],
    manifest: dict[str, Any],
    resolved_files: dict[str, str],
    payload: dict[str, Any],
) -> dict[str, Any]:
    signals = collect_activation_signals(payload)
    surfaces: dict[str, list[str]] = {}
    operating_facts: list[str] = []
    for signal in signals:
        if signal == "repo_landed_false" and "repo_truth_not_exported" in signals:
            surfaces.setdefault("adapter_repo_truth_exporter", []).append(signal)
            continue
        surface_id = SIGNAL_TO_SURFACE.get(signal)
        if surface_id:
            surfaces.setdefault(surface_id, []).append(signal)
            continue
        if signal in OPERATING_FACTS or not looks_like_activation_signal(signal):
            operating_facts.append(signal)
            continue
        surfaces.setdefault(f"project_specific_activation_surface:{signal}", []).append(signal)

    activation_requirements: list[dict[str, Any]] = []
    for surface_id, matched_signals in surfaces.items():
        if surface_id in SURFACE_DEFINITIONS:
            activation_requirements.append(build_surface_entry(surface_id, matched_signals, manifest, resolved_files))
        else:
            activation_requirements.append(build_unknown_activation_surface(matched_signals[0], manifest, resolved_files))
    activation_requirements.sort(key=lambda item: (0 if not str(item["surface_id"]).startswith("project_specific_activation_surface:") else 1, item["surface_id"]))
    activation_requirements.sort(key=lambda item: next((definition["order"] for surface_id, definition in SURFACE_DEFINITIONS.items() if surface_id == item["surface_id"]), 850))

    operating_blockers = [build_operating_fact_entry(signal) for signal in sorted(dedupe(operating_facts))]
    ready_for_active_wiring = not any(item.get("layer") == "project_adapter" for item in activation_requirements)
    activation_sequence = [
        {
            "step": index,
            "surface_id": item["surface_id"],
            "layer": item["layer"],
            "summary": item["summary"],
        }
        for index, item in enumerate(activation_requirements, start=1)
    ]

    return {
        "current_state": {
            "wired": bool(plan.get("activation", {}).get("wired", manifest.get("wired", False))),
            "bundle_wired_flag": bool(manifest.get("wired", False)),
            "promotion_mode": str(plan.get("activation", {}).get("promotion_mode", "manual_only")),
            "status_if_run_now": payload.get("status", ""),
            "reason_if_run_now": payload.get("reason", ""),
            "current_class": payload.get("trust_summary", {}).get("current_class", ""),
            "target_class": payload.get("trust_summary", {}).get("target_class", ""),
            "auto_continuation_enabled": bool(payload.get("flow_control", {}).get("auto_continuation_enabled", False)),
        },
        "activation_requirements": activation_requirements,
        "operating_blockers": operating_blockers,
        "ready_for_active_wiring": ready_for_active_wiring,
        "open_activation_surface_ids": [item["surface_id"] for item in activation_requirements],
        "minimal_activation_sequence": activation_sequence,
        "decoupling_rule": "Keep missing truth exporters and workflow entrypoints in the adapter or repo-governance layer; keep dirty workspaces and failed evidence as runtime blockers.",
    }


def invalid_payload(bundle_dir: Path, errors: list[str], manifest_path: str = "", resolved_files: dict[str, str] | None = None) -> dict[str, Any]:
    return {
        "valid": False,
        "bundle_dir": str(bundle_dir),
        "manifest_path": manifest_path,
        "resolved_files": resolved_files or {},
        "errors": errors,
    }


def main() -> int:
    args = parse_args()
    bundle_dir = args.bundle_dir

    try:
        manifest_path, manifest = load_bundle_manifest(bundle_dir)
    except FileNotFoundError:
        payload = invalid_payload(bundle_dir, ["missing_manifest:adapter_bundle_manifest.draft.json"])
        print(json.dumps(payload, indent=2, ensure_ascii=True))
        return 1

    errors = validate_manifest_shape(manifest)
    resolved, missing_files = resolve_bundle_files(bundle_dir, manifest)
    resolved_files = {key: str(value) for key, value in resolved.items()}
    if errors or missing_files:
        payload = invalid_payload(
            bundle_dir,
            errors + [f"missing_bundle_file:{item}" for item in missing_files],
            str(manifest_path),
            resolved_files,
        )
        print(json.dumps(payload, indent=2, ensure_ascii=True))
        return 1

    runtime_payload, runtime_errors, _, _ = build_bundle_runtime_payload(bundle_dir, [])
    if runtime_errors:
        payload = invalid_payload(bundle_dir, runtime_errors, str(manifest_path), resolved_files)
        print(json.dumps(payload, indent=2, ensure_ascii=True))
        return 1

    plan = read_json(resolved["plan"])
    activation_boundary = build_activation_boundary(plan, manifest, resolved_files, runtime_payload)
    payload = {
        "valid": True,
        "bundle_dir": str(bundle_dir),
        "manifest_path": str(manifest_path),
        "resolved_files": resolved_files,
        "runtime_summary": {
            "status": runtime_payload.get("status", ""),
            "reason": runtime_payload.get("reason", ""),
            "project": runtime_payload.get("project", ""),
            "current_level": runtime_payload.get("current_level", ""),
            "next_slice": runtime_payload.get("next_slice", {}),
            "blocking_facts": runtime_payload.get("blocking_facts", []),
            "remaining_promotion_gates": runtime_payload.get("remaining_promotion_gates", []),
            "trust_summary": runtime_payload.get("trust_summary", {}),
            "reuse_summary": runtime_payload.get("reuse_summary", {}),
        },
        "activation_boundary": activation_boundary,
    }
    print(json.dumps(payload, indent=2, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
