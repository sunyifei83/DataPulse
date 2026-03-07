#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from assess_governance_loop_activation_draft import build_activation_boundary
from loop_bundle_draft import build_bundle_runtime_payload, load_bundle_manifest, read_json, resolve_bundle_files, validate_manifest_shape


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Export a machine-readable governance loop activation plan from an adapter bundle."
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
        default=Path("out/governance/activation_plan.draft.json"),
        help="Output path for the activation plan JSON.",
    )
    parser.add_argument(
        "--stdout",
        action="store_true",
        help="Print the activation plan JSON instead of writing it to disk.",
    )
    return parser.parse_args()


def invalid_plan(bundle_dir: Path, errors: list[str], manifest_path: str = "", resolved_files: dict[str, str] | None = None) -> dict[str, Any]:
    return {
        "valid": False,
        "bundle_dir": str(bundle_dir),
        "manifest_path": manifest_path,
        "resolved_files": resolved_files or {},
        "errors": errors,
    }


def activation_tracks(activation_boundary: dict[str, Any]) -> list[dict[str, Any]]:
    requirements = list(activation_boundary.get("activation_requirements", []))
    adapter = [item for item in requirements if item.get("layer") == "project_adapter"]
    repo = [item for item in requirements if item.get("layer") == "repo_governance"]
    operating = list(activation_boundary.get("operating_blockers", []))
    return [
        {
            "track_id": "project_adapter_completion",
            "layer": "project_adapter",
            "goal": "Close project-specific truth gaps before discussing active wiring.",
            "status": "open" if adapter else "complete",
            "items": adapter,
        },
        {
            "track_id": "repo_governance_cutover",
            "layer": "repo_governance",
            "goal": "Wire explicit repository entrypoints only after adapter-side truth gaps are closed.",
            "status": "open" if repo else "complete",
            "items": repo,
        },
        {
            "track_id": "runtime_cutover_window",
            "layer": "runtime_blockers",
            "goal": "Keep machine-decidable runtime blockers visible without baking them into reusable architecture coupling.",
            "status": "open" if operating else "clear",
            "items": operating,
        },
    ]


def build_plan_payload(
    bundle_dir: Path,
    manifest_path: Path,
    resolved_files: dict[str, str],
    runtime_payload: dict[str, Any],
    activation_boundary: dict[str, Any],
) -> dict[str, Any]:
    current_state = dict(activation_boundary.get("current_state", {}))
    operating_blockers = list(activation_boundary.get("operating_blockers", []))
    ready_for_active_wiring = bool(activation_boundary.get("ready_for_active_wiring", False))
    cutover_now_recommended = ready_for_active_wiring and not operating_blockers
    return {
        "valid": True,
        "schema_version": "governance_loop_activation_plan.v1",
        "generated_at_utc": utc_now(),
        "bundle_dir": str(bundle_dir),
        "manifest_path": str(manifest_path),
        "project": runtime_payload.get("project", ""),
        "target_class": runtime_payload.get("trust_summary", {}).get("target_class", ""),
        "current_class": runtime_payload.get("trust_summary", {}).get("current_class", ""),
        "activation_status": {
            "planning_ready": True,
            "ready_for_active_wiring": ready_for_active_wiring,
            "cutover_now_recommended": cutover_now_recommended,
            "status_if_run_now": current_state.get("status_if_run_now", ""),
            "reason_if_run_now": current_state.get("reason_if_run_now", ""),
            "promotion_mode": current_state.get("promotion_mode", "manual_only"),
        },
        "activation_tracks": activation_tracks(activation_boundary),
        "minimal_activation_sequence": activation_boundary.get("minimal_activation_sequence", []),
        "open_activation_surface_ids": activation_boundary.get("open_activation_surface_ids", []),
        "deferred_operating_blockers": operating_blockers,
        "activation_boundary": activation_boundary,
        "resolved_files": resolved_files,
        "decoupling_contract": {
            "rule": activation_boundary.get("decoupling_rule", ""),
            "core_ownership": "next-slice, blocker, and stop semantics stay in the reusable core",
            "adapter_ownership": "project truth exporters and execution hints stay in the project adapter",
            "repo_governance_ownership": "active wiring, scheduler entrypoints, and release evidence cutover stay in repo governance",
        },
        "recommended_cut_lines": [
            {
                "id": "finish_project_adapter_truth_first",
                "when": "project_adapter track is open",
                "guidance": "Do not start live workflow wiring while adapter-owned truth exporters are still missing.",
            },
            {
                "id": "wire_repo_entrypoints_second",
                "when": "ready_for_active_wiring is true",
                "guidance": "Limit activation changes to explicit repo-governance entrypoints instead of embedding project semantics into the core.",
            },
            {
                "id": "treat_runtime_blockers_as_cutover_window_facts",
                "when": "runtime_cutover_window track is open",
                "guidance": "Resolve runtime blockers for cutover timing, but do not promote them into reusable activation architecture.",
            },
        ],
        "non_goals": [
            "Do not copy project verification commands into the reusable core.",
            "Do not treat a dirty workspace or failing runtime evidence as reusable-core design gaps.",
            "Do not wire active workflows before the activation boundary is explicit.",
        ],
    }


def load_activation_plan_from_bundle(bundle_dir: Path) -> tuple[dict[str, Any], int]:
    try:
        manifest_path, manifest = load_bundle_manifest(bundle_dir)
    except FileNotFoundError:
        payload = invalid_plan(bundle_dir, ["missing_manifest:adapter_bundle_manifest.draft.json"])
        return payload, 1

    errors = validate_manifest_shape(manifest)
    resolved, missing_files = resolve_bundle_files(bundle_dir, manifest)
    resolved_files = {key: str(value) for key, value in resolved.items()}
    if errors or missing_files:
        payload = invalid_plan(
            bundle_dir,
            errors + [f"missing_bundle_file:{item}" for item in missing_files],
            str(manifest_path),
            resolved_files,
        )
        return payload, 1

    runtime_payload, runtime_errors, _, _ = build_bundle_runtime_payload(bundle_dir, [])
    if runtime_errors:
        payload = invalid_plan(bundle_dir, runtime_errors, str(manifest_path), resolved_files)
        return payload, 1

    plan = read_json(resolved["plan"])
    activation_boundary = build_activation_boundary(plan, manifest, resolved_files, runtime_payload)
    payload = build_plan_payload(bundle_dir, manifest_path, resolved_files, runtime_payload, activation_boundary)
    return payload, 0


def main() -> int:
    args = parse_args()
    payload, exit_code = load_activation_plan_from_bundle(args.bundle_dir)

    if args.stdout:
        print(json.dumps(payload, indent=2, ensure_ascii=True))
        return exit_code

    if exit_code:
        print(json.dumps(payload, indent=2, ensure_ascii=True))
        return exit_code

    write_json(args.out_path, payload)
    print(args.out_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
