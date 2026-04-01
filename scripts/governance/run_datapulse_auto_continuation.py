#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from datapulse.governance_paths import (
    EVIDENCE_BUNDLE_ROOT,
    GOVERNANCE_SNAPSHOT_ROOT,
    write_path as resolve_governance_write_path,
    write_root as resolve_governance_write_root,
)
from datapulse_loop_adapter import DEFAULT_CATALOG_PATH, build_datapulse_loop_runtime
from datapulse_loop_contracts import DEFAULT_PLAN_PATH, REPO_ROOT, display_path, read_json, write_json

DEFAULT_POLICY_PATH = REPO_ROOT / "docs/governance/datapulse-auto-continuation-policy.json"
DEFAULT_OUTPUT_PATH = resolve_governance_write_path(
    GOVERNANCE_SNAPSHOT_ROOT,
    "auto_continuation_runtime.draft.json",
    repo_root=REPO_ROOT,
)
DEFAULT_BUNDLE_DIR = resolve_governance_write_root(EVIDENCE_BUNDLE_ROOT, repo_root=REPO_ROOT)


def current_python_command() -> list[str]:
    return [sys.executable]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the read-only auto-continuation entrypoint for the DataPulse blueprint loop and refresh resolver-addressed governance/evidence outputs when requested."
    )
    parser.add_argument(
        "--plan",
        type=Path,
        default=DEFAULT_PLAN_PATH,
        help="Blueprint plan path. Defaults to the active plan overlay.",
    )
    parser.add_argument(
        "--catalog",
        type=Path,
        default=DEFAULT_CATALOG_PATH,
        help="Slice adapter catalog path.",
    )
    parser.add_argument(
        "--policy",
        type=Path,
        default=DEFAULT_POLICY_PATH,
        help="Auto-continuation policy path.",
    )
    parser.add_argument(
        "--bundle-dir",
        type=Path,
        default=DEFAULT_BUNDLE_DIR,
        help="Structured evidence bundle directory to refresh when requested. Defaults to the canonical evidence_bundle_root.",
    )
    parser.add_argument(
        "--write-governance-snapshots",
        action="store_true",
        help="Refresh resolver-addressed code landing status, project loop state, and structured evidence bundle before evaluation.",
    )
    parser.add_argument(
        "--out-path",
        type=Path,
        default=DEFAULT_OUTPUT_PATH,
        help="Output path for the auto-continuation runtime JSON.",
    )
    parser.add_argument(
        "--stdout",
        action="store_true",
        help="Print JSON to stdout instead of writing the default draft file.",
    )
    return parser.parse_args()


def run_capture(command: list[str]) -> str:
    return run_capture_with_mode(command)


def run_capture_with_mode(command: list[str], *, required: bool = True) -> str:
    completed = subprocess.run(
        command,
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    stdout = completed.stdout.strip()
    stderr = completed.stderr.strip()
    if required and completed.returncode != 0:
        raise subprocess.CalledProcessError(
            completed.returncode,
            completed.args,
            output=completed.stdout,
            stderr=completed.stderr,
        )
    if stdout:
        return stdout
    return stderr


def refresh_governance_snapshots(bundle_dir: Path, *, plan_path: Path = DEFAULT_PLAN_PATH) -> dict[str, str]:
    return refresh_governance_snapshots_to_targets(
        bundle_dir=bundle_dir,
        plan_path=plan_path,
        code_landing_status_output=resolve_governance_write_path(
            GOVERNANCE_SNAPSHOT_ROOT,
            "code_landing_status.draft.json",
            repo_root=REPO_ROOT,
        ),
        project_loop_state_output=resolve_governance_write_path(
            GOVERNANCE_SNAPSHOT_ROOT,
            "project_specific_loop_state.draft.json",
            repo_root=REPO_ROOT,
        ),
    )


def refresh_governance_snapshots_to_targets(
    *,
    bundle_dir: Path,
    plan_path: Path = DEFAULT_PLAN_PATH,
    code_landing_status_output: Path,
    project_loop_state_output: Path,
) -> dict[str, str]:
    return {
        # quick_test_gate is an observational wrapper, not a required loop refresh gate.
        "quick_test_gate": run_capture_with_mode(
            [
                *current_python_command(),
                "scripts/governance/run_datapulse_quick_test_gate.py",
            ],
            required=False,
        ),
        "internal_ai_surface_runtime_evidence": run_capture(
            [
                *current_python_command(),
                "scripts/governance/export_datapulse_internal_ai_surface_runtime_evidence.py",
            ]
        ),
        "code_landing_status": run_capture(
            [
                *current_python_command(),
                "scripts/governance/export_datapulse_code_landing_status.py",
                "--output",
                str(code_landing_status_output),
            ]
        ),
        "project_loop_state": run_capture(
            [
                *current_python_command(),
                "scripts/governance/export_datapulse_project_loop_state.py",
                "--plan",
                str(plan_path),
                "--output",
                str(project_loop_state_output),
            ]
        ),
        "structured_release_bundle": run_capture(
            [
                *current_python_command(),
                "scripts/governance/export_datapulse_structured_release_bundle.py",
                "--plan",
                str(plan_path),
                "--out-dir",
                str(bundle_dir),
                "--probe-ha-readiness",
            ]
        ),
    }


def load_policy(path: Path) -> dict[str, Any]:
    payload = read_json(path)
    payload = dict(payload)
    payload["path"] = display_path(path)
    return payload


def decision_for_runtime(policy: dict[str, Any], runtime: dict[str, Any]) -> dict[str, Any]:
    policy_enabled = bool(policy.get("enabled", False))
    runtime_auto_enabled = bool(runtime.get("flow_control", {}).get("auto_continuation_enabled", False))
    if not policy_enabled:
        return {
            "policy_state": "disabled",
            "action": "stop",
            "reason": "policy_disabled",
            "machine_decidable": True,
            "blocking_facts": [],
        }
    if not runtime_auto_enabled:
        return {
            "policy_state": "misaligned",
            "action": "stop",
            "reason": "runtime_not_auto_enabled",
            "machine_decidable": True,
            "blocking_facts": list(runtime.get("effective_blocking_facts", [])),
        }
    status = str(runtime.get("status", ""))
    if status == "blocked":
        return {
            "policy_state": "active",
            "action": "stop",
            "reason": "machine_blockers_open",
            "machine_decidable": True,
            "blocking_facts": list(runtime.get("effective_blocking_facts", [])),
        }
    if status == "stopped":
        return {
            "policy_state": "active",
            "action": "stop",
            "reason": str(runtime.get("reason", "loop_stopped")),
            "machine_decidable": True,
            "blocking_facts": list(runtime.get("remaining_promotion_gates", [])),
        }
    return {
        "policy_state": "active",
        "action": "continue",
        "reason": "ready_for_auto_advance",
        "machine_decidable": True,
        "blocking_facts": [],
    }


def companion_slice_execution_entrypoint(policy: dict[str, Any], runtime: dict[str, Any]) -> dict[str, Any]:
    entrypoint = dict(policy.get("companion_entrypoints", {}).get("local_codex_blueprint_loop", {}))
    if not entrypoint:
        return {}
    runtime_status = str(runtime.get("status", ""))
    next_slice = dict(runtime.get("next_slice", {}))
    eligible_now = runtime_status == "ready" and str(next_slice.get("category", "")) != "complete"
    return {
        "enabled": bool(entrypoint.get("enabled", False)),
        "trigger_mode": str(entrypoint.get("trigger_mode", "")),
        "runner": str(entrypoint.get("runner", "")),
        "recommended_command": str(entrypoint.get("recommended_command", "")),
        "side_effect_mode": str(entrypoint.get("side_effect_mode", "")),
        "guardrails": list(entrypoint.get("guardrails", [])),
        "eligible_now": eligible_now,
        "reason_if_not_eligible": "" if eligible_now else runtime_status or "runtime_not_ready",
        "next_slice": dict(runtime.get("next_slice", {})),
        "slice_execution_brief": dict(runtime.get("slice_execution_brief", {})),
    }


def build_payload(
    *,
    policy: dict[str, Any],
    runtime: dict[str, Any],
    bundle_dir: Path,
    snapshots_refreshed: dict[str, str],
) -> dict[str, Any]:
    decision = decision_for_runtime(policy, runtime)
    return {
        "schema_version": "datapulse_auto_continuation_runtime.v1",
        "project": runtime.get("project", "DataPulse"),
        "policy": policy,
        "runtime": runtime,
        "entrypoint": {
            "bundle_dir": display_path(bundle_dir.resolve()),
            "runner": "scripts/governance/run_datapulse_auto_continuation.py",
            "workflow": ".github/workflows/governance-loop-auto.yml",
        },
        "snapshots_refreshed": snapshots_refreshed,
        "decision": decision,
        "companion_slice_execution": companion_slice_execution_entrypoint(policy, runtime),
        "control_plane_contract": {
            "healthy_environment_behavior": "continue_without_human_handoff",
            "abnormal_environment_behavior": "stop_on_machine_decidable_blockers",
            "default_side_effect_mode": "read_only",
        },
    }


def main() -> int:
    args = parse_args()
    snapshots_refreshed: dict[str, str] = {}
    if args.write_governance_snapshots:
        snapshots_refreshed = refresh_governance_snapshots(args.bundle_dir.resolve(), plan_path=args.plan.resolve())

    policy = load_policy(args.policy.resolve())
    runtime = build_datapulse_loop_runtime(args.plan, args.catalog)
    payload = build_payload(
        policy=policy,
        runtime=runtime,
        bundle_dir=args.bundle_dir.resolve(),
        snapshots_refreshed=snapshots_refreshed,
    )

    if args.stdout:
        print(json.dumps(payload, indent=2, ensure_ascii=True))
        return 0

    write_json(args.out_path, payload)
    print(args.out_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
