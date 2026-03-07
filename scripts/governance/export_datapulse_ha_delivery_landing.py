#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path
from typing import Any

from datapulse_loop_adapter_draft import DEFAULT_CATALOG_PATH
from datapulse_loop_contracts import DEFAULT_OUT_DIR, DEFAULT_PLAN_PATH, build_code_landing_status, load_plan, utc_now, write_json
from export_datapulse_ha_delivery_facts import build_ha_delivery_facts
from export_datapulse_loop_adapter_bundle import build_manifest
from export_governance_loop_activation_intent import build_activation_intent
from export_governance_loop_activation_plan import load_activation_plan_from_bundle
from export_governance_loop_activation_preview import build_activation_preview


TARGET_HA_LEVEL = "ha_release_structured"
RELEASE_FACT_TO_SURFACE = {
    "workflow_dispatch_missing": "repo_workflow_dispatch_entrypoint",
    "structured_release_bundle_missing": "repo_release_evidence_contract",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Export a DataPulse-specific landing view that combines activation cutover and HA delivery facts."
    )
    parser.add_argument(
        "--bundle-dir",
        type=Path,
        help="Optional adapter bundle directory. If omitted, a temporary bundle is derived from the current draft plan and catalog.",
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
        help="Optional ha_delivery_facts.v1 JSON payload. If omitted, the facts are derived from the current repo state.",
    )
    parser.add_argument(
        "--probe-release-readiness",
        action="store_true",
        help="Opt in to probing release_readiness when deriving HA delivery facts.",
    )
    parser.add_argument(
        "--disable-emergency-rehydration",
        action="store_true",
        help="Do not derive a temporary emergency_state.json during HA fact derivation.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUT_DIR / "ha_delivery_landing.draft.json",
        help="Output path for the HA delivery landing JSON.",
    )
    parser.add_argument(
        "--stdout",
        action="store_true",
        help="Print JSON to stdout instead of writing the default draft file.",
    )
    return parser.parse_args()


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_temp_bundle(bundle_dir: Path, plan_path: Path, catalog_path: Path) -> None:
    plan = load_plan(plan_path)
    landing_status = build_code_landing_status()
    project = str(plan.get("project", landing_status.get("project", "DataPulse")))
    activation = dict(plan.get("activation", {}))
    auto_policy = activation.get("auto_continuation", {})
    manifest = build_manifest(
        project,
        wired=bool(activation.get("wired", False)),
        auto_policy_included=isinstance(auto_policy, dict) and bool(auto_policy.get("path")),
    )

    write_json(bundle_dir / "blueprint_plan.snapshot.json", plan)
    write_json(bundle_dir / "code_landing_status.snapshot.json", landing_status)
    write_json(bundle_dir / "slice_adapter_catalog.snapshot.json", read_json(catalog_path))
    if isinstance(auto_policy, dict) and auto_policy.get("path"):
        write_json(bundle_dir / "auto_continuation_policy.snapshot.json", dict(auto_policy))
    write_json(bundle_dir / "adapter_bundle_manifest.draft.json", manifest)


def load_activation_stack(bundle_dir: Path) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], int]:
    activation_plan, exit_code = load_activation_plan_from_bundle(bundle_dir)
    if exit_code:
        return activation_plan, {}, {}, exit_code
    intent = build_activation_intent(activation_plan)
    preview = build_activation_preview(activation_plan, intent)
    return activation_plan, intent, preview, 0


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


def runtime_cutover_facts(preview: dict[str, Any]) -> list[dict[str, Any]]:
    return list(preview.get("runtime_cutover_window", {}).get("facts", []))


def runtime_fact_ids(items: list[dict[str, Any]]) -> list[str]:
    return [str(item.get("fact", "")) for item in items if item.get("fact")]


def release_structuring_projection(release_facts: list[str], repo_surface_ids: set[str]) -> list[dict[str, Any]]:
    projected: list[dict[str, Any]] = []
    for fact in release_facts:
        surface_id = RELEASE_FACT_TO_SURFACE.get(fact, "")
        projected.append(
            {
                "fact": fact,
                "surface_id": surface_id,
                "binding_declared": surface_id in repo_surface_ids if surface_id else False,
                "handling_rule": "repo_governance_cutover" if surface_id else "project_specific_release_structuring",
            }
        )
    return projected


def unique_strings(values: list[str]) -> list[str]:
    return sorted({value for value in values if value})


def overall_status(
    *,
    landed_now: bool,
    adapter_prereqs_open: bool,
    repo_targets_open: bool,
    runtime_open: bool,
    ha_runtime_open: bool,
    release_structuring_open: bool,
) -> str:
    if landed_now:
        return "high_ha_delivery_landed"
    if adapter_prereqs_open:
        return "waiting_project_adapter_prerequisites"
    if repo_targets_open and (runtime_open or ha_runtime_open or release_structuring_open):
        return "repo_cutover_defined_waiting_runtime_and_ha_facts"
    if repo_targets_open:
        return "repo_cutover_defined_waiting_wiring"
    if runtime_open or ha_runtime_open or release_structuring_open:
        return "waiting_high_ha_runtime_facts"
    return "high_ha_delivery_progressing"


def reason_codes(
    *,
    preview: dict[str, Any],
    activation_plan: dict[str, Any],
    current_level: str,
    next_missing_level: str,
    repo_targets: list[dict[str, Any]],
    adapter_prereqs: list[dict[str, Any]],
    runtime_facts: list[str],
    ha_runtime_facts: list[str],
    release_structuring_facts: list[str],
    recovery_route: dict[str, Any],
) -> list[str]:
    reasons: list[str] = []
    if adapter_prereqs:
        reasons.append("project_adapter_prerequisites_open")
    if repo_targets:
        reasons.append("repo_governance_cutover_pending")
    if runtime_facts:
        reasons.append("runtime_cutover_window_open")
    if ha_runtime_facts:
        reasons.append("ha_runtime_blockers_open")
    if release_structuring_facts:
        reasons.append("release_structuring_open")
    if recovery_route.get("status") == "required":
        reasons.append("ha_recovery_route_required")
    elif recovery_route.get("status") == "unavailable":
        reasons.append("ha_recovery_route_unavailable")
    if current_level != TARGET_HA_LEVEL:
        reasons.append(f"next_missing_ha_level:{next_missing_level}")
    if activation_plan.get("current_class", "") != activation_plan.get("target_class", ""):
        reasons.append("target_pipeline_class_not_reached")
    preview_reason = str(preview.get("preview_status", {}).get("reason", ""))
    if preview_reason:
        reasons.append(f"activation_preview:{preview_reason}")
    return unique_strings(reasons)


def build_recommended_actions(
    *,
    repo_targets: list[dict[str, Any]],
    runtime_facts: list[str],
    next_missing_level: str,
    ha_runtime_facts: list[str],
    release_structuring_facts: list[str],
    recovery_route: dict[str, Any],
) -> list[str]:
    actions: list[str] = []
    if repo_targets:
        actions.append(
            "Keep repo-governance cutover limited to the declared surfaces: "
            + ", ".join(str(item.get("surface_id", "")) for item in repo_targets if item.get("surface_id"))
        )
    if runtime_facts:
        actions.append(
            "Resolve runtime cutover window facts separately from architecture work: " + ", ".join(runtime_facts)
        )
    if ha_runtime_facts:
        actions.append(
            f"Close HA runtime blockers required for {next_missing_level}: " + ", ".join(ha_runtime_facts)
        )
    if recovery_route.get("status") == "required":
        selected_route = str(recovery_route.get("selected_route", "primary"))
        selected_contract = dict(recovery_route.get(f"{selected_route}_execution_contract", {}))
        primary = str(recovery_route.get("primary_action", ""))
        secondary = str(recovery_route.get("secondary_action", ""))
        trigger = str(recovery_route.get("first_trigger", ""))
        route = primary or secondary or "follow emergency runbook"
        actions.append(f"Execute the emergency recovery route for {trigger or 'the current blocker'}: {route}")
        if selected_contract.get("supported_by_existing_remote_smoke_entrypoint", False):
            actions.append("The selected recovery route is already executable through scripts/datapulse_remote_openclaw_smoke.sh.")
        if secondary:
            actions.append(f"Fallback recovery route remains available: {secondary}")
    if release_structuring_facts:
        actions.append(
            "Treat release-structuring facts as repo-governance evidence bindings, not reusable-core gaps: "
            + ", ".join(release_structuring_facts)
        )
    if not actions:
        actions.append("The current draft facts satisfy the high-HA delivery landing bar.")
    return actions


def invalid_payload(errors: list[str], source_adapter_bundle: dict[str, Any], source_ha_delivery_facts: dict[str, Any]) -> dict[str, Any]:
    return {
        "valid": False,
        "schema_version": "datapulse_ha_delivery_landing.v1",
        "project": "DataPulse",
        "generated_at_utc": utc_now(),
        "wired": False,
        "source_adapter_bundle": source_adapter_bundle,
        "source_ha_delivery_facts": source_ha_delivery_facts,
        "errors": errors,
    }


def build_ha_delivery_landing(args: argparse.Namespace) -> tuple[dict[str, Any], int]:
    ha_facts, ha_source = load_ha_facts(args)

    if args.bundle_dir:
        activation_plan, intent, preview, exit_code = load_activation_stack(args.bundle_dir)
        source_adapter_bundle = {
            "source_kind": "provided_bundle_dir",
            "bundle_dir": str(args.bundle_dir),
            "manifest_path": activation_plan.get("manifest_path", ""),
            "ephemeral": False,
        }
        if exit_code:
            return invalid_payload(list(activation_plan.get("errors", [])), source_adapter_bundle, ha_source), exit_code
    else:
        with tempfile.TemporaryDirectory() as tmp_dir:
            bundle_dir = Path(tmp_dir) / "adapter_bundle"
            bundle_dir.mkdir(parents=True, exist_ok=True)
            write_temp_bundle(bundle_dir, args.plan, args.catalog)
            activation_plan, intent, preview, exit_code = load_activation_stack(bundle_dir)
            source_adapter_bundle = {
                "source_kind": "derived_temp_bundle",
                "bundle_dir": str(bundle_dir),
                "manifest_path": activation_plan.get("manifest_path", ""),
                "ephemeral": True,
            }
            if exit_code:
                return invalid_payload(list(activation_plan.get("errors", [])), source_adapter_bundle, ha_source), exit_code

    repo_targets = list(preview.get("repo_governance_bindings", []))
    repo_surface_ids = {str(item.get("surface_id", "")) for item in repo_targets if item.get("surface_id")}
    adapter_prereqs = list(preview.get("project_adapter_prerequisites", []))
    runtime_items = runtime_cutover_facts(preview)
    runtime_facts = runtime_fact_ids(runtime_items)
    ha_runtime_facts = list(ha_facts.get("fact_groups", {}).get("ha_runtime", []))
    ha_recovery_signals = list(ha_facts.get("fact_groups", {}).get("ha_recovery_signals", []))
    release_facts = list(ha_facts.get("fact_groups", {}).get("release_structuring", []))
    recovery_route = dict(ha_facts.get("ha_chain", {}).get("recovery_route", {}))
    selected_route_name = str(recovery_route.get("selected_route", ""))
    selected_recovery_contract = (
        dict(recovery_route.get(f"{selected_route_name}_execution_contract", {})) if selected_route_name else {}
    )
    release_projection = release_structuring_projection(release_facts, repo_surface_ids)
    all_machine_blockers = unique_strings(runtime_facts + list(ha_facts.get("machine_blockers", [])))
    current_level = str(ha_facts.get("current_level", ""))
    next_missing_level = str(ha_facts.get("next_missing_level", ""))
    target_pipeline_class = str(activation_plan.get("target_class", "trusted_delivery_pipeline"))
    current_pipeline_class = str(activation_plan.get("current_class", ""))
    target_ha_level_reached = current_level == TARGET_HA_LEVEL
    target_pipeline_class_reached = current_pipeline_class == target_pipeline_class
    landed_now = (
        not adapter_prereqs
        and not repo_targets
        and not runtime_facts
        and not ha_runtime_facts
        and not release_facts
        and target_ha_level_reached
        and target_pipeline_class_reached
    )
    ready_for_repo_cutover = bool(intent.get("intent_status", {}).get("ready_for_repo_cutover", False))
    repo_cutover_now_recommended = bool(intent.get("intent_status", {}).get("cutover_now_recommended", False))
    high_ha_cutover_now_recommended = ready_for_repo_cutover and not runtime_facts and not ha_runtime_facts and not release_facts
    next_level_blockers = list(ha_facts.get("delivery_levels", {}).get(next_missing_level, {}).get("reasons", []))
    status = overall_status(
        landed_now=landed_now,
        adapter_prereqs_open=bool(adapter_prereqs),
        repo_targets_open=bool(repo_targets),
        runtime_open=bool(runtime_facts),
        ha_runtime_open=bool(ha_runtime_facts),
        release_structuring_open=bool(release_facts),
    )

    payload = {
        "valid": True,
        "schema_version": "datapulse_ha_delivery_landing.v1",
        "project": str(activation_plan.get("project", "DataPulse")),
        "generated_at_utc": utc_now(),
        "wired": False,
        "source_adapter_bundle": source_adapter_bundle,
        "source_ha_delivery_facts": ha_source,
        "delivery_target": {
            "objective": "high_ha_delivery",
            "target_level": TARGET_HA_LEVEL,
            "target_pipeline_class": target_pipeline_class,
        },
        "delivery_status": {
            "status": status,
            "reason_codes": reason_codes(
                preview=preview,
                activation_plan=activation_plan,
                current_level=current_level,
                next_missing_level=next_missing_level,
                repo_targets=repo_targets,
                adapter_prereqs=adapter_prereqs,
                runtime_facts=runtime_facts,
                ha_runtime_facts=ha_runtime_facts,
                release_structuring_facts=release_facts,
                recovery_route=recovery_route,
            ),
            "preview_status": str(preview.get("preview_status", {}).get("status", "")),
            "preview_reason": str(preview.get("preview_status", {}).get("reason", "")),
            "current_level": current_level,
            "next_missing_level": next_missing_level,
            "next_level_blockers": next_level_blockers,
            "recovery_route_status": str(recovery_route.get("status", "clear")),
            "recovery_trigger": str(recovery_route.get("first_trigger", "")),
            "recovery_requires_new_run_id": bool(recovery_route.get("should_new_run_id", False)),
            "recovery_selected_route": selected_route_name,
            "recovery_entrypoint_supported": bool(
                selected_recovery_contract.get("supported_by_existing_remote_smoke_entrypoint", False)
            ),
            "recovery_primary_action": str(recovery_route.get("primary_action", "")),
            "current_pipeline_class": current_pipeline_class,
            "target_pipeline_class": target_pipeline_class,
            "ready_for_repo_cutover": ready_for_repo_cutover,
            "repo_cutover_now_recommended": repo_cutover_now_recommended,
            "high_ha_cutover_now_recommended": high_ha_cutover_now_recommended,
            "landed_now": landed_now,
        },
        "landing_bar": {
            "project_adapter_clear": not adapter_prereqs,
            "repo_governance_targets_open": bool(repo_targets),
            "runtime_cutover_window_clear": not runtime_facts,
            "ha_runtime_clear": not ha_runtime_facts,
            "release_structuring_clear": not release_facts,
            "target_ha_level_reached": target_ha_level_reached,
            "target_pipeline_class_reached": target_pipeline_class_reached,
            "landed_now": landed_now,
        },
        "delivery_tracks": [
            {
                "track_id": "repo_governance_cutover",
                "status": "open" if repo_targets else "clear",
                "items": repo_targets,
            },
            {
                "track_id": "runtime_cutover_window",
                "status": "open" if runtime_items else "clear",
                "items": runtime_items,
            },
            {
                "track_id": "ha_runtime_stabilization",
                "status": "open" if ha_runtime_facts else "clear",
                "items": [
                    {
                        "fact": fact,
                        "required_for_level": next_missing_level,
                        "source": "ha_delivery_facts",
                    }
                    for fact in ha_runtime_facts
                ],
            },
            {
                "track_id": "ha_recovery_route",
                "status": str(recovery_route.get("status", "clear")),
                "items": []
                if recovery_route.get("status", "clear") == "clear"
                else [
                    {
                        "first_trigger": recovery_route.get("first_trigger", ""),
                        "blocker_codes": recovery_route.get("blocker_codes", []),
                        "should_new_run_id": bool(recovery_route.get("should_new_run_id", False)),
                        "selected_route": selected_route_name,
                        "primary_action": recovery_route.get("primary_action", ""),
                        "secondary_action": recovery_route.get("secondary_action", ""),
                        "remediation_class": recovery_route.get("remediation_class", ""),
                        "entrypoint_supported": bool(
                            selected_recovery_contract.get("supported_by_existing_remote_smoke_entrypoint", False)
                        ),
                        "entrypoint": selected_recovery_contract.get("entrypoint", ""),
                        "env_assignments": selected_recovery_contract.get("env_assignments", {}),
                        "manual_steps": selected_recovery_contract.get("manual_steps", []),
                    }
                ],
            },
            {
                "track_id": "release_structuring",
                "status": "open" if release_projection else "clear",
                "items": release_projection,
            },
        ],
        "fact_projection": {
            "repo_governance_surface_ids": sorted(item for item in repo_surface_ids if item),
            "runtime_cutover_window_facts": runtime_facts,
            "ha_runtime_facts": ha_runtime_facts,
            "ha_recovery_signals": ha_recovery_signals,
            "ha_recovery_env_keys": sorted(selected_recovery_contract.get("env_assignments", {}).keys()),
            "release_structuring_facts": release_facts,
            "release_structuring_projection": release_projection,
            "machine_blockers": all_machine_blockers,
        },
        "control_contract": {
            "machine_decidable": True,
            "project_specific": True,
            "not_part_of_reusable_core": True,
            "continue_conditions": {
                "repo_governance_targets_clear": not repo_targets,
                "runtime_cutover_window_clear": not runtime_facts,
                "ha_runtime_clear": not ha_runtime_facts,
                "release_structuring_clear": not release_facts,
                "target_ha_level_reached": target_ha_level_reached,
                "target_pipeline_class_reached": target_pipeline_class_reached,
            },
            "stop_on_machine_blockers": all_machine_blockers,
            "reopen_truth": {
                "next_missing_level": next_missing_level,
                "repo_governance_surfaces": sorted(item for item in repo_surface_ids if item),
                "runtime_facts": all_machine_blockers,
                "recovery_signals": ha_recovery_signals,
            },
        },
        "recommended_actions": build_recommended_actions(
            repo_targets=repo_targets,
            runtime_facts=runtime_facts,
            next_missing_level=next_missing_level,
            ha_runtime_facts=ha_runtime_facts,
            release_structuring_facts=release_facts,
            recovery_route=recovery_route,
        ),
    }
    return payload, 0


def main() -> int:
    args = parse_args()
    payload, exit_code = build_ha_delivery_landing(args)

    if args.stdout:
        print(json.dumps(payload, indent=2, ensure_ascii=True))
        return exit_code

    if exit_code:
        print(json.dumps(payload, indent=2, ensure_ascii=True))
        return exit_code

    write_json(args.output, payload)
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
