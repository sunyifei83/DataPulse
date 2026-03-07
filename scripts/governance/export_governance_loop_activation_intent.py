#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from export_governance_loop_activation_plan import load_activation_plan_from_bundle


SURFACE_BINDING_HINTS = {
    "repo_driver_wiring": {
        "binding_kind": "explicit_loop_entrypoint",
        "suggested_binding": "workflow_dispatch_or_repo_local_driver",
        "notes": [
            "Keep activation in an explicit repo-governance entrypoint.",
            "Do not embed project-specific execution semantics into the reusable core.",
        ],
    },
    "repo_auto_continuation_policy": {
        "binding_kind": "auto_continuation_policy",
        "suggested_binding": "scheduler_or_followup_dispatch",
        "notes": [
            "Auto-continuation should react only after machine blockers clear.",
            "Manual relay should remain explicit until the repo-governance cutover is approved.",
        ],
    },
    "repo_workflow_dispatch_entrypoint": {
        "binding_kind": "workflow_dispatch_or_scheduler",
        "suggested_binding": "workflow_dispatch_entrypoint",
        "notes": [
            "Prefer a narrow evidence-entry workflow over a full release or service-governance workflow.",
            "Keep the trigger surface minimal and machine-decidable.",
        ],
    },
    "repo_release_evidence_contract": {
        "binding_kind": "structured_release_evidence",
        "suggested_binding": "release_sidecar_or_bundle",
        "notes": [
            "The loop should re-ingest structured release evidence, not scrape human-oriented release text.",
            "Keep release evidence separate from product-specific governance verdict wording.",
        ],
    },
}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Export a machine-readable governance loop activation intent from an activation plan or bundle."
    )
    parser.add_argument(
        "--bundle-dir",
        type=Path,
        required=True,
        help="Directory containing adapter_bundle_manifest.draft.json and referenced snapshot files.",
    )
    parser.add_argument(
        "--out-path",
        type=Path,
        default=Path("out/governance/activation_intent.draft.json"),
        help="Output path for the activation intent JSON.",
    )
    parser.add_argument(
        "--stdout",
        action="store_true",
        help="Print the activation intent JSON instead of writing it to disk.",
    )
    return parser.parse_args()


def repo_governance_targets(activation_plan: dict[str, Any]) -> list[dict[str, Any]]:
    repo_track = next(
        (track for track in activation_plan.get("activation_tracks", []) if track.get("track_id") == "repo_governance_cutover"),
        {"items": []},
    )
    targets: list[dict[str, Any]] = []
    for item in repo_track.get("items", []):
        surface_id = str(item.get("surface_id", ""))
        hint = SURFACE_BINDING_HINTS.get(
            surface_id,
            {
                "binding_kind": "repo_governance_surface",
                "suggested_binding": "fill_me",
                "notes": ["Fill in the repository-specific cutover binding for this surface."],
            },
        )
        targets.append(
            {
                "surface_id": surface_id,
                "binding_status": "pending_design",
                "binding_kind": hint["binding_kind"],
                "suggested_binding": hint["suggested_binding"],
                "required_for": item.get("required_for", []),
                "from_signals": item.get("from_signals", []),
                "suggested_artifacts": item.get("suggested_artifacts", []),
                "notes": hint["notes"],
            }
        )
    return targets


def build_activation_intent(activation_plan: dict[str, Any]) -> dict[str, Any]:
    adapter_track = next(
        (track for track in activation_plan.get("activation_tracks", []) if track.get("track_id") == "project_adapter_completion"),
        {"items": [], "status": "complete"},
    )
    runtime_track = next(
        (track for track in activation_plan.get("activation_tracks", []) if track.get("track_id") == "runtime_cutover_window"),
        {"items": [], "status": "clear"},
    )
    activation_status = dict(activation_plan.get("activation_status", {}))
    adapter_open = bool(adapter_track.get("items"))
    runtime_open = bool(runtime_track.get("items"))
    ready_for_repo_cutover = bool(activation_status.get("ready_for_active_wiring", False))
    cutover_now_recommended = bool(activation_status.get("cutover_now_recommended", False))

    if adapter_open:
        intent_reason = "project_adapter_prerequisites_open"
    elif runtime_open:
        intent_reason = "runtime_cutover_window_open"
    elif ready_for_repo_cutover:
        intent_reason = "repo_governance_cutover_can_be_planned"
    else:
        intent_reason = "activation_plan_not_ready"

    return {
        "valid": True,
        "schema_version": "governance_loop_activation_intent.v1",
        "generated_at_utc": utc_now(),
        "project": activation_plan.get("project", ""),
        "source_activation_plan": {
            "bundle_dir": activation_plan.get("bundle_dir", ""),
            "manifest_path": activation_plan.get("manifest_path", ""),
        },
        "intent_status": {
            "planning_ready": bool(activation_status.get("planning_ready", False)),
            "ready_for_repo_cutover": ready_for_repo_cutover,
            "cutover_now_recommended": cutover_now_recommended,
            "reason": intent_reason,
        },
        "project_adapter_prerequisites": adapter_track.get("items", []),
        "repo_governance_targets": repo_governance_targets(activation_plan),
        "runtime_cutover_window": {
            "status": runtime_track.get("status", "clear"),
            "facts": runtime_track.get("items", []),
            "handling_rule": "Resolve these for cutover timing, but do not convert them into reusable-core or repo-governance design obligations.",
        },
        "activation_sequence": activation_plan.get("minimal_activation_sequence", []),
        "guardrails": [
            "Keep adapter-owned truth exporters and execution hints outside repo-governance cutover bindings.",
            "Keep runtime blockers visible, but defer them to the cutover window instead of the reusable architecture layer.",
            "Keep repo-governance activation narrow: explicit entrypoints, auto-continuation policy, and structured evidence bindings only.",
        ],
        "non_goals": activation_plan.get("non_goals", []),
    }


def main() -> int:
    args = parse_args()
    activation_plan, exit_code = load_activation_plan_from_bundle(args.bundle_dir)
    if exit_code:
        print(json.dumps(activation_plan, indent=2, ensure_ascii=True))
        return exit_code

    payload = build_activation_intent(activation_plan)
    if args.stdout:
        print(json.dumps(payload, indent=2, ensure_ascii=True))
        return 0

    write_json(args.out_path, payload)
    print(args.out_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
