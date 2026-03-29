#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from datapulse.governance_paths import (
    EVIDENCE_BUNDLE_ROOT,
    GOVERNANCE_SNAPSHOT_ROOT,
    read_root as resolve_governance_read_root,
    write_path as resolve_governance_write_path,
)
from export_governance_loop_activation_intent import build_activation_intent
from export_governance_loop_activation_plan import load_activation_plan_from_bundle


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Export a machine-readable preview of what activation cutover would leave open after applying the current activation intent."
    )
    parser.add_argument(
        "--bundle-dir",
        type=Path,
        default=resolve_governance_read_root(EVIDENCE_BUNDLE_ROOT, repo_root=REPO_ROOT),
        help="Directory containing adapter_bundle_manifest.draft.json and referenced snapshot files.",
    )
    parser.add_argument(
        "--activation-intent-json",
        type=Path,
        help="Optional activation intent JSON. If omitted, the intent is derived from the current bundle.",
    )
    parser.add_argument(
        "--out-path",
        type=Path,
        default=resolve_governance_write_path(
            GOVERNANCE_SNAPSHOT_ROOT,
            "activation_preview.draft.json",
            repo_root=REPO_ROOT,
        ),
        help="Output path for the activation preview JSON.",
    )
    parser.add_argument(
        "--stdout",
        action="store_true",
        help="Print the activation preview JSON instead of writing it to disk.",
    )
    return parser.parse_args()


def activation_preview_status(intent: dict[str, Any]) -> tuple[str, str]:
    adapter_open = bool(intent.get("project_adapter_prerequisites", []))
    repo_open = bool(intent.get("repo_governance_targets", []))
    runtime_open = bool(intent.get("runtime_cutover_window", {}).get("facts", []))
    ready_for_repo_cutover = bool(intent.get("intent_status", {}).get("ready_for_repo_cutover", False))
    cutover_now_recommended = bool(intent.get("intent_status", {}).get("cutover_now_recommended", False))

    if adapter_open:
        return "waiting_project_adapter_prerequisites", "adapter_prerequisites_open"
    if not repo_open:
        return "no_repo_governance_cutover_required", "no_open_repo_targets"
    if runtime_open:
        return "repo_cutover_defined_waiting_runtime_window", "runtime_cutover_window_open"
    if ready_for_repo_cutover and cutover_now_recommended:
        return "repo_cutover_ready", "repo_governance_targets_defined_and_runtime_window_clear"
    if ready_for_repo_cutover:
        return "repo_cutover_defined", "repo_governance_targets_defined"
    return "activation_preview_not_ready", "intent_not_ready"


def build_activation_preview(activation_plan: dict[str, Any], intent: dict[str, Any]) -> dict[str, Any]:
    status, reason = activation_preview_status(intent)
    runtime_facts = list(intent.get("runtime_cutover_window", {}).get("facts", []))
    repo_targets = list(intent.get("repo_governance_targets", []))
    adapter_prereqs = list(intent.get("project_adapter_prerequisites", []))

    return {
        "valid": True,
        "schema_version": "governance_loop_activation_preview.v1",
        "generated_at_utc": utc_now(),
        "project": activation_plan.get("project", ""),
        "source_activation_plan": {
            "bundle_dir": activation_plan.get("bundle_dir", ""),
            "manifest_path": activation_plan.get("manifest_path", ""),
        },
        "source_activation_intent": intent.get("source_activation_plan", {}),
        "preview_status": {
            "status": status,
            "reason": reason,
            "ready_for_repo_cutover": bool(intent.get("intent_status", {}).get("ready_for_repo_cutover", False)),
            "cutover_now_recommended": bool(intent.get("intent_status", {}).get("cutover_now_recommended", False)),
        },
        "preview_assumptions": [
            "All repo-governance targets in the activation intent are implemented exactly as declared.",
            "Project-adapter prerequisites remain unchanged until explicitly closed.",
            "Runtime cutover window facts remain real operating blockers and are not rewritten by activation intent alone.",
        ],
        "projected_post_cutover_state": {
            "remaining_project_adapter_gaps": [item.get("surface_id", "") for item in adapter_prereqs if item.get("surface_id")],
            "remaining_repo_governance_gaps": [],
            "remaining_runtime_blockers": [item.get("fact", "") for item in runtime_facts if item.get("fact")],
            "trusted_pipeline_bar_after_cutover": not adapter_prereqs and not runtime_facts,
        },
        "repo_governance_bindings": repo_targets,
        "project_adapter_prerequisites": adapter_prereqs,
        "runtime_cutover_window": intent.get("runtime_cutover_window", {}),
        "recommended_actions": [
            "Close project-adapter prerequisites before executing repo-governance cutover." if adapter_prereqs else "Project-adapter prerequisites are already clear.",
            "Keep runtime blockers in a separate cutover window and do not promote them into architecture obligations." if runtime_facts else "Runtime cutover window is clear.",
            "Limit repo-governance cutover to the explicit bindings declared in the activation intent.",
        ],
        "non_goals": activation_plan.get("non_goals", []),
    }


def load_intent(args: argparse.Namespace, activation_plan: dict[str, Any]) -> dict[str, Any]:
    if args.activation_intent_json:
        return read_json(args.activation_intent_json)
    return build_activation_intent(activation_plan)


def main() -> int:
    args = parse_args()
    activation_plan, exit_code = load_activation_plan_from_bundle(args.bundle_dir)
    if exit_code:
        print(json.dumps(activation_plan, indent=2, ensure_ascii=True))
        return exit_code

    intent = load_intent(args, activation_plan)
    payload = build_activation_preview(activation_plan, intent)

    if args.stdout:
        print(json.dumps(payload, indent=2, ensure_ascii=True))
        return 0

    write_json(args.out_path, payload)
    print(args.out_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
