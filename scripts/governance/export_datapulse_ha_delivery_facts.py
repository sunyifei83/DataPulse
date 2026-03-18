#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import shlex
import subprocess
import tempfile
from pathlib import Path
from typing import Any

from datapulse_loop_contracts import (
    DEFAULT_OUT_DIR,
    REPO_ROOT,
    latest_artifact_file,
    parse_emergency_state,
    parse_remote_report,
    utc_now,
    workflow_dispatch_available,
    structured_release_bundle_available,
    write_json,
)


LEVEL_ORDER = [
    "ha_observed",
    "ha_guarded",
    "ha_ready",
    "ha_release_structured",
]

DERIVED_LEVEL_FACTS = {
    "ha_observed_false",
    "ha_guarded_false",
    "ha_ready_false",
}

REMOTE_SMOKE_ENTRYPOINT = "bash scripts/datapulse_remote_openclaw_smoke.sh"
RECOVERY_CATALOG_PATH = REPO_ROOT / "docs/governance/datapulse-ha-recovery-catalog.draft.json"
DEFAULT_RELEASE_READINESS_FACT_PATH = DEFAULT_OUT_DIR / "release_readiness_fact.draft.json"
SUPPORTED_REMOTE_RECOVERY_ENV_KEYS = {
    "MACMINI_DATAPULSE_DIR",
    "MACMINI_HOST",
    "MACMINI_HOST_CANDIDATES",
    "REMOTE_AUTOPICK_PYTHON",
    "REMOTE_BOOTSTRAP_INSTALL",
    "REMOTE_PIP_EXTRAS",
    "REMOTE_PIP_NO_PROXY",
    "REMOTE_PYTHON",
    "REMOTE_PYTHON_MIN_VERSION",
    "REMOTE_UV_BOOTSTRAP",
    "REMOTE_UV_INSTALL_ROOT",
    "REMOTE_UV_LOCAL_BINARY",
    "REMOTE_UV_PYTHON",
    "REMOTE_USE_UV",
    "VPS_HOST",
    "VPS_PORT",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Export DataPulse-specific high-HA delivery facts without wiring them into active workflows."
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUT_DIR / "ha_delivery_facts.draft.json",
        help="Output path for the HA delivery facts JSON.",
    )
    parser.add_argument(
        "--stdout",
        action="store_true",
        help="Print JSON to stdout instead of writing the default draft file.",
    )
    parser.add_argument(
        "--probe-release-readiness",
        action="store_true",
        help="Opt in to executing scripts/release_readiness.sh and capturing its result.",
    )
    parser.add_argument(
        "--disable-emergency-rehydration",
        action="store_true",
        help="Do not derive a temporary emergency_state.json from the latest remote report if the latest artifact is missing or stale.",
    )
    parser.add_argument(
        "--release-readiness-fact-json",
        type=Path,
        help="Optional persisted release_readiness_fact.v1 JSON payload to consume instead of relying on the default out/governance path.",
    )
    return parser.parse_args()


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def repo_relative(path: Path) -> str:
    resolved = path.resolve()
    if resolved.is_relative_to(REPO_ROOT):
        return str(resolved.relative_to(REPO_ROOT))
    return str(resolved)


def resolve_report_path(raw: str) -> Path | None:
    if not raw.strip():
        return None
    path = Path(raw)
    if path.is_absolute():
        return path if path.exists() else None
    normalized = raw[2:] if raw.startswith("./") else raw
    candidate = (REPO_ROOT / normalized).resolve()
    return candidate if candidate.exists() else None


def remote_observation() -> dict[str, Any]:
    report_path = latest_artifact_file("remote_report.md")
    report = parse_remote_report(report_path)
    if not report:
        return {
            "status": "missing",
            "available": False,
            "gate_passed": False,
            "reasons": ["remote_report_missing"],
        }

    log_path = resolve_report_path(str(report.get("log", "")))
    failed_steps = int(report.get("failed_steps", 0))
    gate_passed = failed_steps == 0
    return {
        "status": "passed" if gate_passed else "failed",
        "available": True,
        "gate_passed": gate_passed,
        "run_id": report.get("run_id", ""),
        "failed_steps": failed_steps,
        "block_codes": list(report.get("block_codes", [])),
        "report_path": str(report.get("path", "")),
        "log_path": repo_relative(log_path) if log_path else "",
        "reasons": [] if gate_passed else ["latest_remote_smoke_failed"],
    }


def derive_emergency_state(report_path: Path, log_path: Path) -> dict[str, Any]:
    with tempfile.TemporaryDirectory() as tmp_dir:
        out_path = Path(tmp_dir) / "emergency_state.json"
        completed = subprocess.run(
            [
                "bash",
                "scripts/emergency_guard.sh",
                "--rules",
                "docs/emergency_rules.json",
                "--report",
                str(report_path),
                "--log",
                str(log_path),
                "--out",
                str(out_path),
            ],
            cwd=REPO_ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        payload = parse_emergency_state(out_path if out_path.exists() else None)
        return {
            "returncode": completed.returncode,
            "payload": payload,
            "stdout": completed.stdout,
            "stderr": completed.stderr,
        }


def classify_emergency_derivation_failure(result: dict[str, Any]) -> tuple[str, list[str]]:
    combined = ((result.get("stdout") or "") + "\n" + (result.get("stderr") or "")).lower()
    if "syntaxerror" in combined:
        return "script_syntax_error", ["emergency_guard_syntax_error", "emergency_state_missing"]
    return "derivation_failed", ["emergency_state_derivation_failed", "emergency_state_missing"]


def split_action_steps(raw_action: str) -> list[str]:
    return [item.strip() for item in raw_action.split("+") if item.strip()]


def parse_route_step(step: str) -> tuple[str, str] | None:
    match = re.fullmatch(r"([A-Z][A-Z0-9_]*)=(.+)", step)
    if not match:
        return None
    return match.group(1), match.group(2).strip()


def load_recovery_catalog() -> dict[str, Any]:
    if not RECOVERY_CATALOG_PATH.exists():
        return {
            "schema_version": "datapulse_ha_recovery_catalog.v1",
            "project": "DataPulse",
            "wired": False,
            "presets": [],
        }
    return read_json(RECOVERY_CATALOG_PATH)


def match_recovery_contract(
    contract: dict[str, Any],
    *,
    first_trigger: str,
    requires_new_run_id: bool,
) -> dict[str, Any]:
    catalog = load_recovery_catalog()
    for preset in catalog.get("presets", []):
        if str(preset.get("entrypoint", "")) != str(contract.get("entrypoint", "")):
            continue
        if bool(preset.get("requires_new_run_id", False)) != requires_new_run_id:
            continue
        if dict(preset.get("env_assignments", {})) != dict(contract.get("env_assignments", {})):
            continue
        if list(preset.get("manual_steps", [])) != list(contract.get("manual_steps", [])):
            continue
        recommended = list(preset.get("recommended_signals", []))
        signal_match = not recommended or first_trigger in recommended
        return {
            "matched": True,
            "catalog_schema_version": catalog.get("schema_version", ""),
            "preset_id": str(preset.get("preset_id", "")),
            "title": str(preset.get("title", "")),
            "match_kind": "exact_signal_match" if signal_match else "exact_contract_match_signal_not_listed",
            "recommended_signals": recommended,
            "notes": list(preset.get("notes", [])),
        }

    return {
        "matched": False,
        "catalog_schema_version": catalog.get("schema_version", ""),
        "preset_id": "",
        "title": "",
        "match_kind": "unmatched",
        "recommended_signals": [],
        "notes": [],
    }


def build_execution_contract(raw_action: str, *, requires_new_run_id: bool, route_name: str) -> dict[str, Any]:
    raw_steps = split_action_steps(raw_action)
    env_assignments: dict[str, str] = {}
    manual_steps: list[str] = []
    unsupported_env_keys: list[str] = []

    for step in raw_steps:
        parsed = parse_route_step(step)
        if not parsed:
            manual_steps.append(step)
            continue
        key, value = parsed
        env_assignments[key] = value
        if key not in SUPPORTED_REMOTE_RECOVERY_ENV_KEYS:
            unsupported_env_keys.append(key)

    route_available = bool(raw_steps)
    supported_by_existing_entrypoint = route_available and not unsupported_env_keys and not manual_steps and bool(env_assignments)
    shell_exports = [f"export {key}={shlex.quote(value)}" for key, value in env_assignments.items()]
    command_lines = list(shell_exports)
    if supported_by_existing_entrypoint and requires_new_run_id:
        command_lines.append("export RUN_ID=$(date +%Y%m%d_%H%M%S)")
    if supported_by_existing_entrypoint:
        command_lines.append(REMOTE_SMOKE_ENTRYPOINT)

    if env_assignments and not manual_steps:
        route_kind = "remote_smoke_env_preset"
    elif manual_steps and not env_assignments:
        route_kind = "manual_recovery_step"
    elif env_assignments or manual_steps:
        route_kind = "mixed_recovery_route"
    else:
        route_kind = "empty_recovery_route"

    return {
        "route_name": route_name,
        "route_available": route_available,
        "raw_action": raw_action,
        "route_kind": route_kind,
        "env_assignments": env_assignments,
        "manual_steps": manual_steps,
        "supported_env_keys": sorted(env_assignments.keys()),
        "unsupported_env_keys": sorted(unsupported_env_keys),
        "supported_by_existing_remote_smoke_entrypoint": supported_by_existing_entrypoint,
        "requires_new_run_id": requires_new_run_id,
        "entrypoint": REMOTE_SMOKE_ENTRYPOINT,
        "shell_exports": shell_exports,
        "command_lines": command_lines,
        "entrypoint_command": "\n".join(command_lines),
    }


def emergency_observation(remote: dict[str, Any], allow_rehydrate: bool) -> dict[str, Any]:
    observed_path = latest_artifact_file("emergency_state.json")
    observed = parse_emergency_state(observed_path)
    remote_run_id = str(remote.get("run_id", ""))
    observed_matches_remote = bool(observed and remote_run_id and observed.get("run_id", "") == remote_run_id)

    if observed and (not remote_run_id or observed_matches_remote):
        stop = bool(observed.get("stop", False))
        return {
            "status": "blocked" if stop else "passed",
            "available": True,
            "gate_passed": not stop,
            "source_kind": "artifact_observed",
            "matches_latest_remote": observed_matches_remote or not remote_run_id,
            "run_id": observed.get("run_id", ""),
            "state": observed.get("state", {}),
            "conclusion": observed.get("conclusion", ""),
            "first_trigger": observed.get("first_trigger", ""),
            "block_codes": list(observed.get("block_codes", [])),
            "blocker_codes": list(observed.get("blocker_codes", [])),
            "should_new_run_id": bool(observed.get("should_new_run_id", False)),
            "fail_steps": int(observed.get("fail_steps", 0) or 0),
            "recommendation": dict(observed.get("recommendation", {})),
            "evidence": dict(observed.get("evidence", {})),
            "report_path": str(remote.get("report_path", "")),
            "log_path": str(remote.get("log_path", "")),
            "reasons": [] if not stop else ["emergency_stop"],
        }

    if not allow_rehydrate:
        reasons = ["emergency_state_missing"]
        if observed and remote_run_id and not observed_matches_remote:
            reasons.insert(0, "emergency_state_stale")
        return {
            "status": "missing",
            "available": False,
            "gate_passed": False,
            "source_kind": "missing",
            "matches_latest_remote": False,
            "reasons": reasons,
        }

    if not remote.get("available", False):
        return {
            "status": "missing",
            "available": False,
            "gate_passed": False,
            "source_kind": "missing",
            "matches_latest_remote": False,
            "reasons": ["remote_report_missing", "emergency_state_missing"],
        }

    report_path = REPO_ROOT / str(remote.get("report_path", ""))
    log_path = REPO_ROOT / str(remote.get("log_path", ""))
    if not log_path.exists():
        return {
            "status": "missing",
            "available": False,
            "gate_passed": False,
            "source_kind": "missing",
            "matches_latest_remote": False,
            "reasons": ["remote_log_missing", "emergency_state_missing"],
        }

    derived = derive_emergency_state(report_path, log_path)
    payload = derived.get("payload")
    if not payload:
        failure_kind, reasons = classify_emergency_derivation_failure(derived)
        return {
            "status": "missing",
            "available": False,
            "gate_passed": False,
            "source_kind": "derived_failed",
            "matches_latest_remote": False,
            "failure_kind": failure_kind,
            "derivation_returncode": int(derived.get("returncode", 0)),
            "reasons": reasons,
        }

    stop = bool(payload.get("stop", False))
    return {
        "status": "blocked" if stop else "passed",
        "available": True,
        "gate_passed": not stop,
        "source_kind": "derived_from_latest_remote_report",
        "matches_latest_remote": True,
        "run_id": payload.get("run_id", ""),
        "state": payload.get("state", {}),
        "conclusion": payload.get("conclusion", ""),
        "first_trigger": payload.get("first_trigger", ""),
        "block_codes": list(payload.get("block_codes", [])),
        "blocker_codes": list(payload.get("blocker_codes", [])),
        "should_new_run_id": bool(payload.get("should_new_run_id", False)),
        "fail_steps": int(payload.get("fail_steps", 0) or 0),
        "recommendation": dict(payload.get("recommendation", {})),
        "evidence": dict(payload.get("evidence", {})),
        "report_path": str(remote.get("report_path", "")),
        "log_path": str(remote.get("log_path", "")),
        "reasons": [] if not stop else ["emergency_stop"],
    }


def emergency_recovery_route(emergency: dict[str, Any]) -> dict[str, Any]:
    blocked = emergency.get("status") == "blocked" or not emergency.get("gate_passed", False)
    recommendation = dict(emergency.get("recommendation", {}))
    first_trigger = str(emergency.get("first_trigger", ""))
    blocker_codes = [code for code in emergency.get("blocker_codes", []) if code]
    block_codes = [code for code in emergency.get("block_codes", []) if code]
    state = dict(emergency.get("state", {}))
    route_available = bool(first_trigger or recommendation or blocker_codes or block_codes or state)

    if not blocked:
        status = "clear"
        reasons: list[str] = []
    elif route_available:
        status = "required"
        reasons = ["emergency_stop"]
    else:
        status = "unavailable"
        reasons = ["emergency_recovery_route_unavailable"]

    primary_action = str(recommendation.get("primary_action", ""))
    secondary_action = str(recommendation.get("secondary_action", ""))
    primary_contract = build_execution_contract(
        primary_action,
        requires_new_run_id=bool(emergency.get("should_new_run_id", False)),
        route_name="primary",
    )
    secondary_contract = build_execution_contract(
        secondary_action,
        requires_new_run_id=bool(emergency.get("should_new_run_id", False)),
        route_name="secondary",
    )
    primary_match = match_recovery_contract(
        primary_contract,
        first_trigger=first_trigger,
        requires_new_run_id=bool(emergency.get("should_new_run_id", False)),
    )
    secondary_match = match_recovery_contract(
        secondary_contract,
        first_trigger=first_trigger,
        requires_new_run_id=bool(emergency.get("should_new_run_id", False)),
    )
    selected_route = "primary" if primary_action else ("secondary" if secondary_action else "")
    selected_match = primary_match if selected_route == "primary" else secondary_match

    return {
        "status": status,
        "route_available": route_available,
        "run_id": emergency.get("run_id", ""),
        "state": state,
        "conclusion": emergency.get("conclusion", ""),
        "first_trigger": first_trigger,
        "block_codes": block_codes,
        "blocker_codes": blocker_codes,
        "should_new_run_id": bool(emergency.get("should_new_run_id", False)),
        "fail_steps": int(emergency.get("fail_steps", 0) or 0),
        "primary_action": primary_action,
        "secondary_action": secondary_action,
        "remediation_class": str(recommendation.get("remediation_class", "")),
        "selected_route": selected_route,
        "primary_execution_contract": primary_contract,
        "primary_catalog_match": primary_match,
        "secondary_execution_contract": secondary_contract,
        "secondary_catalog_match": secondary_match,
        "selected_catalog_match": selected_match,
        "reasons": reasons,
    }


def parse_release_readiness_counts(output: str) -> tuple[int, int]:
    match = re.search(r"release readiness:\s*pass=(\d+)\s*fail=(\d+)", output)
    if not match:
        return 0, 0
    return int(match.group(1)), int(match.group(2))


def tail_lines(output: str, *, limit: int = 20) -> list[str]:
    lines = [line for line in output.strip().splitlines() if line.strip()]
    return lines[-limit:]


def parse_check_lines(output: str, prefix: str) -> list[str]:
    return [line.removeprefix(prefix).strip() for line in output.splitlines() if line.startswith(prefix)]


def normalize_release_readiness_check_line(line: str) -> str:
    normalized = str(line or "").strip()
    if normalized.startswith("release python runtime available:"):
        return "release python runtime available: python>=3.10"
    if normalized.startswith("release build path available:"):
        return "release build path available"
    return normalized


def normalize_release_readiness_output_line(line: str) -> str:
    normalized = str(line or "").strip()
    if normalized.startswith("[PASS] "):
        return "[PASS] " + normalize_release_readiness_check_line(normalized.removeprefix("[PASS] "))
    return normalized


def read_release_readiness_fact(path: Path | None) -> dict[str, Any] | None:
    if path is None or not path.exists():
        return None
    payload = read_json(path)
    if str(payload.get("schema_version", "")) != "release_readiness_fact.v1":
        return None
    return payload


def latest_persistent_emergency_state(emergency: dict[str, Any]) -> Path | None:
    if not emergency.get("available", False) or emergency.get("source_kind") != "artifact_observed":
        return None
    state_path = latest_artifact_file("emergency_state.json")
    observed = parse_emergency_state(state_path)
    if not state_path or not observed:
        return None
    emergency_run_id = str(emergency.get("run_id", ""))
    if emergency_run_id and observed.get("run_id", "") != emergency_run_id:
        return None
    return state_path


def build_release_readiness_fact(*, emergency_state_path: Path | None = None) -> dict[str, Any]:
    state_path = emergency_state_path or latest_artifact_file("emergency_state.json")
    state_payload = parse_emergency_state(state_path)

    if state_path is None or not state_path.exists() or not state_payload:
        return {
            "schema_version": "release_readiness_fact.v1",
            "project": "DataPulse",
            "generated_at_utc": utc_now(),
            "fact_kind": "draft_export",
            "wired": False,
            "source_emergency_state": {
                "available": False,
                "path": "",
                "run_id": "",
                "conclusion": "",
                "stop": None,
                "first_trigger": "",
            },
            "command": {
                "entrypoint": "bash scripts/release_readiness.sh",
                "args": ["--emergency-state", "<missing>", "--require-emergency-gate"],
                "require_emergency_gate": True,
            },
            "observation": {
                "status": "unobserved",
                "gate_passed": False,
                "returncode": None,
                "pass_count": 0,
                "fail_count": 0,
                "passed_checks": [],
                "failed_checks": [],
                "stdout_tail": [],
                "stderr_tail": [],
                "reasons": ["release_readiness_unobserved", "emergency_state_unavailable"],
            },
            "machine_blockers": ["release_readiness_unobserved", "emergency_state_unavailable"],
        }

    completed = subprocess.run(
        [
            "bash",
            "scripts/release_readiness.sh",
            "--emergency-state",
            str(state_path),
            "--require-emergency-gate",
        ],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    combined = (completed.stdout or "") + ("\n" if completed.stdout and completed.stderr else "") + (completed.stderr or "")
    pass_count, fail_count = parse_release_readiness_counts(combined)
    passed_checks = [
        normalize_release_readiness_check_line(line)
        for line in parse_check_lines(combined, "[PASS] ")
    ]
    failed_checks = parse_check_lines(combined, "[FAIL] ")
    reasons = [] if completed.returncode == 0 else ["release_readiness_failed"]

    return {
        "schema_version": "release_readiness_fact.v1",
        "project": "DataPulse",
        "generated_at_utc": utc_now(),
        "fact_kind": "draft_export",
        "wired": False,
        "source_emergency_state": {
            "available": True,
            "path": repo_relative(state_path),
            "run_id": str(state_payload.get("run_id", "")),
            "conclusion": str(state_payload.get("conclusion", "")),
            "stop": bool(state_payload.get("stop", False)),
            "first_trigger": str(state_payload.get("first_trigger", "")),
        },
        "command": {
            "entrypoint": "bash scripts/release_readiness.sh",
            "args": ["--emergency-state", repo_relative(state_path), "--require-emergency-gate"],
            "require_emergency_gate": True,
        },
        "observation": {
            "status": "passed" if completed.returncode == 0 else "failed",
            "gate_passed": completed.returncode == 0,
            "returncode": completed.returncode,
            "pass_count": pass_count,
            "fail_count": fail_count,
            "passed_checks": passed_checks,
            "failed_checks": failed_checks,
            "stdout_tail": [
                normalize_release_readiness_output_line(line)
                for line in tail_lines(completed.stdout or "")
            ],
            "stderr_tail": tail_lines(completed.stderr or ""),
            "reasons": reasons,
        },
        "machine_blockers": failed_checks if completed.returncode != 0 else [],
    }


def release_readiness_from_fact(fact: dict[str, Any], *, probe_requested: bool) -> dict[str, Any]:
    observation = dict(fact.get("observation", {}))
    return {
        "probe_requested": probe_requested,
        "source_kind": "persisted_fact" if not probe_requested else "probe_current_repo",
        "source_fact_path": repo_relative(DEFAULT_RELEASE_READINESS_FACT_PATH)
        if not probe_requested
        else "",
        "status": str(observation.get("status", "unobserved")),
        "gate_passed": bool(observation.get("gate_passed", False)),
        "pass_count": int(observation.get("pass_count", 0) or 0),
        "fail_count": int(observation.get("fail_count", 0) or 0),
        "failed_checks": list(observation.get("failed_checks", [])),
        "reasons": list(observation.get("reasons", [])),
    }


def matching_release_readiness_fact(emergency: dict[str, Any], fact_path: Path | None) -> dict[str, Any] | None:
    fact = read_release_readiness_fact(fact_path)
    if not fact:
        return None
    source = dict(fact.get("source_emergency_state", {}))
    if not source.get("available", False):
        return None
    emergency_run_id = str(emergency.get("run_id", ""))
    if emergency_run_id and str(source.get("run_id", "")) != emergency_run_id:
        return None
    if bool(source.get("stop", False)) != (not bool(emergency.get("gate_passed", False))):
        return None
    return fact


def probe_release_readiness(
    emergency: dict[str, Any],
    probe_requested: bool,
    *,
    release_readiness_fact_path: Path | None = None,
) -> dict[str, Any]:
    if not probe_requested:
        persisted = matching_release_readiness_fact(
            emergency,
            release_readiness_fact_path or DEFAULT_RELEASE_READINESS_FACT_PATH,
        )
        if persisted:
            result = release_readiness_from_fact(persisted, probe_requested=False)
            result["source_fact_path"] = repo_relative(release_readiness_fact_path or DEFAULT_RELEASE_READINESS_FACT_PATH)
            return result
        return {
            "probe_requested": False,
            "status": "unobserved",
            "gate_passed": False,
            "pass_count": 0,
            "fail_count": 0,
            "failed_checks": [],
            "reasons": ["release_readiness_unobserved"],
        }

    state_path = latest_persistent_emergency_state(emergency)
    if state_path is None:
        return {
            "probe_requested": True,
            "status": "unobserved",
            "gate_passed": False,
            "pass_count": 0,
            "fail_count": 0,
            "failed_checks": [],
            "reasons": ["release_readiness_requires_persistent_emergency_state", "release_readiness_unobserved"],
        }

    fact = build_release_readiness_fact(emergency_state_path=state_path)
    return release_readiness_from_fact(fact, probe_requested=True)


def build_delivery_levels(
    remote: dict[str, Any],
    emergency: dict[str, Any],
    readiness: dict[str, Any],
    workflow_dispatch_available: bool,
    structured_release_bundle: bool,
) -> dict[str, Any]:
    levels: dict[str, Any] = {}

    observed_reasons = list(remote.get("reasons", []))
    levels["ha_observed"] = {
        "satisfied": bool(remote.get("gate_passed", False)),
        "reasons": observed_reasons,
    }

    guarded_reasons: list[str] = []
    if not levels["ha_observed"]["satisfied"]:
        guarded_reasons.append("ha_observed_false")
        guarded_reasons.extend(observed_reasons)
    elif emergency.get("status") == "missing":
        guarded_reasons.extend(list(emergency.get("reasons", [])) or ["emergency_state_missing"])
    elif not emergency.get("gate_passed", False):
        guarded_reasons.extend(list(emergency.get("reasons", [])) or ["emergency_stop"])
    levels["ha_guarded"] = {
        "satisfied": not guarded_reasons,
        "reasons": guarded_reasons,
    }

    ready_reasons: list[str] = []
    if not levels["ha_guarded"]["satisfied"]:
        ready_reasons.append("ha_guarded_false")
        ready_reasons.extend(levels["ha_guarded"]["reasons"])
    elif readiness.get("status") == "unobserved":
        ready_reasons.extend(list(readiness.get("reasons", [])) or ["release_readiness_unobserved"])
    elif not readiness.get("gate_passed", False):
        ready_reasons.extend(list(readiness.get("reasons", [])) or ["release_readiness_failed"])
    levels["ha_ready"] = {
        "satisfied": not ready_reasons,
        "reasons": ready_reasons,
    }

    structured_reasons: list[str] = []
    if not levels["ha_ready"]["satisfied"]:
        structured_reasons.append("ha_ready_false")
        structured_reasons.extend(levels["ha_ready"]["reasons"])
    if not workflow_dispatch_available:
        structured_reasons.append("workflow_dispatch_missing")
    if not structured_release_bundle:
        structured_reasons.append("structured_release_bundle_missing")
    levels["ha_release_structured"] = {
        "satisfied": not structured_reasons,
        "reasons": structured_reasons,
    }
    return levels


def current_level(levels: dict[str, Any]) -> str:
    level = "ha_unproven"
    for item in LEVEL_ORDER:
        if levels.get(item, {}).get("satisfied", False):
            level = item
    return level


def next_missing_level(levels: dict[str, Any]) -> str:
    for item in LEVEL_ORDER:
        if not levels.get(item, {}).get("satisfied", False):
            return item
    return "ha_release_structured"


def build_ha_delivery_facts(
    *,
    probe_release_readiness_flag: bool,
    allow_emergency_rehydrate: bool,
    release_readiness_fact_path: Path | None = None,
) -> dict[str, Any]:
    remote = remote_observation()
    emergency = emergency_observation(remote, allow_emergency_rehydrate)
    recovery_route = emergency_recovery_route(emergency)
    readiness = probe_release_readiness(
        emergency,
        probe_release_readiness_flag,
        release_readiness_fact_path=release_readiness_fact_path,
    )
    release_workflow = REPO_ROOT / ".github/workflows/release.yml"
    governance_workflow = REPO_ROOT / ".github/workflows/governance-evidence.yml"
    workflow_dispatch = workflow_dispatch_available(release_workflow) or workflow_dispatch_available(governance_workflow)
    dispatch_entrypoints = [
        path
        for path in [
            ".github/workflows/release.yml" if workflow_dispatch_available(release_workflow) else "",
            ".github/workflows/governance-evidence.yml" if workflow_dispatch_available(governance_workflow) else "",
        ]
        if path
    ]
    structured_bundle = structured_release_bundle_available()
    levels = build_delivery_levels(remote, emergency, readiness, workflow_dispatch, structured_bundle)
    facts = sorted(
        {
            reason
            for item in levels.values()
            for reason in item.get("reasons", [])
            if reason and reason not in DERIVED_LEVEL_FACTS
        }
    )

    return {
        "schema_version": "ha_delivery_facts.v1",
        "project": "DataPulse",
        "generated_at_utc": utc_now(),
        "fact_kind": "draft_export",
        "wired": False,
        "current_level": current_level(levels),
        "next_missing_level": next_missing_level(levels),
        "ha_chain": {
            "remote_observation": remote,
            "emergency_gate": emergency,
            "recovery_route": recovery_route,
            "release_readiness": readiness,
            "release_structuring": {
                "workflow_dispatch_available": workflow_dispatch,
                "workflow_dispatch_entrypoints": dispatch_entrypoints,
                "structured_release_bundle_available": structured_bundle,
                "active_release_workflow": dispatch_entrypoints[0] if dispatch_entrypoints else ".github/workflows/release.yml",
            },
        },
        "delivery_levels": levels,
        "open_facts": facts,
        "machine_blockers": facts,
        "fact_groups": {
            "ha_runtime": [
                item
                for item in facts
                if item
                not in {
                    "workflow_dispatch_missing",
                    "structured_release_bundle_missing",
                }
            ],
            "ha_recovery_signals": [
                item
                for item in recovery_route.get("blocker_codes", [])
                if item
            ],
            "release_structuring": [
                item
                for item in facts
                if item in {"workflow_dispatch_missing", "structured_release_bundle_missing"}
            ],
        },
        "delivery_contract": {
            "objective": "high_ha_delivery",
            "machine_decidable": True,
            "project_specific": True,
            "not_part_of_reusable_core": True,
            "recovery_catalog_path": str(RECOVERY_CATALOG_PATH.relative_to(REPO_ROOT)),
            "evidence_chain": [
                "remote_smoke",
                "emergency_gate",
                "release_readiness",
                "structured_release_evidence",
            ],
        },
    }


def main() -> int:
    args = parse_args()
    payload = build_ha_delivery_facts(
        probe_release_readiness_flag=args.probe_release_readiness,
        allow_emergency_rehydrate=not args.disable_emergency_rehydration,
        release_readiness_fact_path=args.release_readiness_fact_json,
    )

    if args.stdout:
        print(json.dumps(payload, indent=2, ensure_ascii=True))
        return 0

    write_json(args.output, payload)
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
