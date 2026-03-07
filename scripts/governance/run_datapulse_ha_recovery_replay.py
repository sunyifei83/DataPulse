#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any

from datapulse_loop_adapter_draft import DEFAULT_CATALOG_PATH
from datapulse_loop_contracts import DEFAULT_OUT_DIR, DEFAULT_PLAN_PATH, REPO_ROOT, display_path, parse_emergency_state, write_json
from export_datapulse_ha_delivery_facts import build_ha_delivery_facts
from export_datapulse_ha_delivery_landing import build_ha_delivery_landing
from export_datapulse_ha_recovery_preset import build_recovery_preset


REMOTE_EMERGENCY_RULES = REPO_ROOT / "docs/emergency_rules.json"
ARTIFACT_PREFIX = "openclaw_datapulse_"
REPORT_LINE_RE = re.compile(r"^remote report:\s+(.+)$", re.MULTILINE)
LOG_LINE_RE = re.compile(r"^(?:远端日志|remote log):\s+(.+)$", re.MULTILINE)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Manual-only HA recovery replay wrapper for DataPulse. Defaults to dry-run and only executes on explicit --execute."
    )
    parser.add_argument(
        "--ha-facts-json",
        type=Path,
        help="Optional ha_delivery_facts.v1 JSON payload used to derive the recovery preset.",
    )
    parser.add_argument(
        "--route",
        choices=["selected", "primary", "secondary"],
        default="selected",
        help="Which recovery route to replay. Defaults to the currently selected route.",
    )
    parser.add_argument(
        "--run-id",
        default="",
        help="Explicit RUN_ID for the replay. If omitted, a new RUN_ID is generated when needed.",
    )
    parser.add_argument(
        "--artifacts-dir",
        type=Path,
        default=REPO_ROOT / "artifacts",
        help="Artifact root used by the replay command.",
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Actually execute the recovery replay. Without this flag the wrapper only prints the replay plan.",
    )
    parser.add_argument(
        "--write-governance-snapshots",
        action="store_true",
        help="After execution, refresh draft HA governance snapshots under --governance-out-dir.",
    )
    parser.add_argument(
        "--governance-out-dir",
        type=Path,
        default=DEFAULT_OUT_DIR,
        help="Output directory for refreshed governance snapshots when --write-governance-snapshots is set.",
    )
    parser.add_argument(
        "--plan",
        type=Path,
        default=DEFAULT_PLAN_PATH,
        help="Blueprint plan path used when recomputing the landing view after replay.",
    )
    parser.add_argument(
        "--catalog",
        type=Path,
        default=DEFAULT_CATALOG_PATH,
        help="Slice adapter catalog path used when recomputing the landing view after replay.",
    )
    parser.add_argument(
        "--probe-release-readiness",
        action="store_true",
        help="Opt in to probing release_readiness when refreshing HA facts after replay.",
    )
    parser.add_argument(
        "--disable-emergency-rehydration",
        action="store_true",
        help="Do not derive a temporary emergency_state.json during HA fact derivation.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print machine-readable summary JSON.",
    )
    return parser.parse_args()


def default_run_id() -> str:
    return datetime.utcnow().strftime("%Y%m%d_%H%M%S")


def resolve_output_path(raw: str) -> Path | None:
    value = raw.strip()
    if not value:
        return None
    path = Path(value)
    if path.is_absolute():
        return path.resolve()
    normalized = value[2:] if value.startswith("./") else value
    return (REPO_ROOT / normalized).resolve()


def stdout_tail(text: str) -> list[str]:
    lines = [line for line in text.strip().splitlines() if line.strip()]
    return lines[-20:]


def reported_artifact_path(pattern: re.Pattern[str], stdout: str) -> Path | None:
    match = pattern.search(stdout)
    if not match:
        return None
    return resolve_output_path(match.group(1))


def build_preset_args(args: argparse.Namespace) -> argparse.Namespace:
    return argparse.Namespace(
        ha_facts_json=args.ha_facts_json,
        route=args.route,
        probe_release_readiness=args.probe_release_readiness,
        disable_emergency_rehydration=args.disable_emergency_rehydration,
        output=Path(""),
        stdout=False,
        shell=False,
    )


def build_landing_args(args: argparse.Namespace, *, ha_facts_json: Path | None = None) -> argparse.Namespace:
    return argparse.Namespace(
        bundle_dir=None,
        plan=args.plan,
        catalog=args.catalog,
        ha_facts_json=ha_facts_json,
        probe_release_readiness=args.probe_release_readiness,
        disable_emergency_rehydration=args.disable_emergency_rehydration,
        output=Path(""),
        stdout=False,
    )


def build_replay_context(args: argparse.Namespace, preset: dict[str, Any]) -> dict[str, Any]:
    route_contract = dict(preset.get("route_contract", {}))
    preset_contract = dict(preset.get("preset_contract", {}))
    catalog_match = dict(preset.get("catalog_match", {}))
    recovery_status = dict(preset.get("recovery_status", {}))
    route_available = bool(recovery_status.get("route_available", False))
    supported = bool(preset_contract.get("supported_by_existing_remote_smoke_entrypoint", False))
    run_id = args.run_id.strip() or default_run_id()
    artifacts_dir = args.artifacts_dir.resolve()
    run_dir = artifacts_dir / f"openclaw_datapulse_{run_id}"

    command_lines = list(preset_contract.get("shell_exports", []))
    command_lines.append(f"export OUT_DIR={artifacts_dir}")
    if bool(recovery_status.get("requires_new_run_id", False)) or args.run_id.strip():
        command_lines.append(f"export RUN_ID={run_id}")
    command_lines.append(str(preset_contract.get("entrypoint", "")))

    return {
        "route_available": route_available,
        "supported_by_existing_remote_smoke_entrypoint": supported,
        "selected_route": recovery_status.get("selected_route", ""),
        "catalog_match": catalog_match,
        "requires_new_run_id": bool(recovery_status.get("requires_new_run_id", False)),
        "entrypoint": str(preset_contract.get("entrypoint", "")),
        "env_assignments": dict(preset_contract.get("env_assignments", {})),
        "manual_steps": list(route_contract.get("manual_steps", [])),
        "run_id": run_id,
        "artifacts_dir": artifacts_dir,
        "run_dir": run_dir,
        "report_path": run_dir / "remote_report.md",
        "log_path": run_dir / "remote_test.log",
        "emergency_state_path": run_dir / "emergency_state.json",
        "command_lines": command_lines,
    }


def resolve_actual_replay_context(context: dict[str, Any], completed: subprocess.CompletedProcess[str]) -> dict[str, Any]:
    report_path = reported_artifact_path(REPORT_LINE_RE, completed.stdout) or Path(context["report_path"])
    log_path = reported_artifact_path(LOG_LINE_RE, completed.stdout) or Path(context["log_path"])

    if report_path.exists() and not log_path.exists():
        log_path = report_path.parent / "remote_test.log"
    if log_path.exists() and not report_path.exists():
        report_path = log_path.parent / "remote_report.md"

    run_dir = Path(context["run_dir"])
    if report_path.exists():
        run_dir = report_path.parent
    elif log_path.exists():
        run_dir = log_path.parent

    run_id = str(context["run_id"])
    if run_dir.name.startswith(ARTIFACT_PREFIX):
        run_id = run_dir.name[len(ARTIFACT_PREFIX) :]

    actual = dict(context)
    actual["run_id"] = run_id
    actual["run_dir"] = run_dir
    actual["report_path"] = report_path
    actual["log_path"] = log_path
    actual["emergency_state_path"] = run_dir / "emergency_state.json"
    return actual


def dry_run_payload(args: argparse.Namespace, preset: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    return {
        "ok": True,
        "executed": False,
        "dry_run": True,
        "project": "DataPulse",
        "preset": preset,
        "replay_context": {
            "selected_route": context["selected_route"],
            "catalog_match": context["catalog_match"],
            "route_available": context["route_available"],
            "supported_by_existing_remote_smoke_entrypoint": context["supported_by_existing_remote_smoke_entrypoint"],
            "run_id": context["run_id"],
            "artifacts_dir": str(context["artifacts_dir"]),
            "run_dir": str(context["run_dir"]),
            "report_path": str(context["report_path"]),
            "log_path": str(context["log_path"]),
            "emergency_state_path": str(context["emergency_state_path"]),
            "env_assignments": context["env_assignments"],
            "manual_steps": context["manual_steps"],
            "command_lines": context["command_lines"],
        },
    }


def invalid_payload(reason: str, preset: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    payload = dry_run_payload(argparse.Namespace(), preset, context)
    payload["ok"] = False
    payload["reason"] = reason
    return payload


def run_remote_replay(context: dict[str, Any]) -> tuple[subprocess.CompletedProcess[str], dict[str, str]]:
    env = os.environ.copy()
    for key, value in context["env_assignments"].items():
        env[str(key)] = str(value)
    env["RUN_ID"] = str(context["run_id"])
    env["OUT_DIR"] = str(context["artifacts_dir"])

    completed = subprocess.run(
        ["bash", "scripts/datapulse_remote_openclaw_smoke.sh"],
        cwd=REPO_ROOT,
        env=env,
        check=False,
        capture_output=True,
        text=True,
    )
    return completed, env


def run_emergency_guard(context: dict[str, Any]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            "bash",
            "scripts/emergency_guard.sh",
            "--rules",
            str(REMOTE_EMERGENCY_RULES),
            "--report",
            str(context["report_path"]),
            "--log",
            str(context["log_path"]),
            "--out",
            str(context["emergency_state_path"]),
        ],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )


def refresh_governance_snapshots(args: argparse.Namespace, ha_facts: dict[str, Any], ha_landing: dict[str, Any], preset: dict[str, Any]) -> list[str]:
    out_dir = args.governance_out_dir
    write_json(out_dir / "ha_delivery_facts.draft.json", ha_facts)
    write_json(out_dir / "ha_delivery_landing.draft.json", ha_landing)
    write_json(out_dir / "ha_recovery_preset.draft.json", preset)
    return [
        str((out_dir / "ha_delivery_facts.draft.json").resolve()),
        str((out_dir / "ha_delivery_landing.draft.json").resolve()),
        str((out_dir / "ha_recovery_preset.draft.json").resolve()),
    ]


def build_execute_payload(
    args: argparse.Namespace,
    preset: dict[str, Any],
    context: dict[str, Any],
) -> tuple[dict[str, Any], int]:
    completed, env = run_remote_replay(context)
    actual_context = resolve_actual_replay_context(context, completed)
    report_exists = actual_context["report_path"].exists()
    log_exists = actual_context["log_path"].exists()
    emergency_completed: subprocess.CompletedProcess[str] | None = None
    emergency_state = None

    if report_exists and log_exists:
        emergency_completed = run_emergency_guard(actual_context)
        emergency_state = parse_emergency_state(
            actual_context["emergency_state_path"] if actual_context["emergency_state_path"].exists() else None
        )

    ha_facts = build_ha_delivery_facts(
        probe_release_readiness_flag=args.probe_release_readiness,
        allow_emergency_rehydrate=not args.disable_emergency_rehydration,
    )
    landing_args = build_landing_args(args)
    ha_landing, landing_rc = build_ha_delivery_landing(landing_args)
    replay_preset = build_recovery_preset(build_preset_args(args))

    written_snapshots: list[str] = []
    if args.write_governance_snapshots:
        written_snapshots = refresh_governance_snapshots(args, ha_facts, ha_landing, replay_preset)

    emergency_gate = dict(ha_facts.get("ha_chain", {}).get("emergency_gate", {}))
    replay_cleared = bool(completed.returncode == 0 and emergency_gate.get("gate_passed", False) and landing_rc == 0)
    payload = {
        "ok": replay_cleared,
        "executed": True,
        "dry_run": False,
        "project": "DataPulse",
        "preset": preset,
        "replay_context": {
            "selected_route": actual_context["selected_route"],
            "catalog_match": actual_context["catalog_match"],
            "run_id": actual_context["run_id"],
            "artifacts_dir": str(actual_context["artifacts_dir"]),
            "run_dir": display_path(actual_context["run_dir"]),
            "report_path": display_path(actual_context["report_path"]),
            "log_path": display_path(actual_context["log_path"]),
            "emergency_state_path": display_path(actual_context["emergency_state_path"]),
            "env_assignments": actual_context["env_assignments"],
            "command_lines": actual_context["command_lines"],
            "env_keys": sorted(key for key in env if key in actual_context["env_assignments"] or key in {"RUN_ID", "OUT_DIR"}),
        },
        "remote_smoke": {
            "rc": completed.returncode,
            "stdout_tail": stdout_tail(completed.stdout),
            "stderr_tail": stdout_tail(completed.stderr),
            "report_exists": report_exists,
            "log_exists": log_exists,
        },
        "emergency_guard": {
            "ran": emergency_completed is not None,
            "rc": emergency_completed.returncode if emergency_completed is not None else None,
            "stdout_tail": stdout_tail(emergency_completed.stdout) if emergency_completed is not None else [],
            "stderr_tail": stdout_tail(emergency_completed.stderr) if emergency_completed is not None else [],
            "state": emergency_state,
        },
        "post_replay": {
            "ha_current_level": ha_facts.get("current_level", ""),
            "ha_next_missing_level": ha_facts.get("next_missing_level", ""),
            "emergency_gate_status": emergency_gate.get("status", ""),
            "emergency_first_trigger": emergency_gate.get("first_trigger", ""),
            "landing_status": ha_landing.get("delivery_status", {}).get("status", "") if landing_rc == 0 else "",
            "landing_recovery_status": ha_landing.get("delivery_status", {}).get("recovery_route_status", "") if landing_rc == 0 else "",
            "landing_machine_blockers": ha_landing.get("fact_projection", {}).get("machine_blockers", []) if landing_rc == 0 else [],
        },
        "governance_snapshots_written": written_snapshots,
    }
    return payload, 0 if replay_cleared else 1


def print_payload(payload: dict[str, Any], as_json: bool) -> None:
    if as_json:
        print(json.dumps(payload, indent=2, ensure_ascii=True))
        return

    if payload.get("dry_run", False):
        context = payload.get("replay_context", {})
        print(
            f"[replay] dry-run route={context.get('selected_route', '')} "
            f"run_id={context.get('run_id', '')} supported={context.get('supported_by_existing_remote_smoke_entrypoint', False)}"
        )
        for line in context.get("command_lines", []):
            print(line)
        return

    state = "PASS" if payload.get("ok", False) else "FAIL"
    post = payload.get("post_replay", {})
    print(
        f"[replay] {state} run_id={payload.get('replay_context', {}).get('run_id', '')} "
        f"emergency_gate={post.get('emergency_gate_status', '')} "
        f"landing={post.get('landing_status', '')}"
    )


def main() -> int:
    args = parse_args()
    preset = build_recovery_preset(build_preset_args(args))
    context = build_replay_context(args, preset)

    if not context["route_available"]:
        payload = invalid_payload("recovery_route_unavailable", preset, context)
        print_payload(payload, args.json)
        return 2
    if not context["supported_by_existing_remote_smoke_entrypoint"]:
        payload = invalid_payload("recovery_route_not_supported_by_existing_entrypoint", preset, context)
        print_payload(payload, args.json)
        return 2

    if not args.execute:
        payload = dry_run_payload(args, preset, context)
        print_payload(payload, args.json)
        return 0

    payload, exit_code = build_execute_payload(args, preset, context)
    print_payload(payload, args.json)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
