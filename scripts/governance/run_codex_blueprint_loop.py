#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import shlex
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any

from datapulse_loop_adapter import DEFAULT_CATALOG_PATH, build_datapulse_loop_runtime
from datapulse_loop_contracts import (
    DEFAULT_PLAN_PATH,
    REPO_ROOT,
    build_code_landing_status,
    display_path,
    load_plan,
    utc_now,
)
from run_datapulse_auto_continuation import refresh_governance_snapshots, refresh_governance_snapshots_to_targets

DEFAULT_OUTPUT_DIR = REPO_ROOT / "out" / "codex_blueprint_loop"
DEFAULT_BUNDLE_DIR = REPO_ROOT / "out" / "ha_latest_release_bundle"
DEFAULT_UV_CACHE_DIR = Path(tempfile.gettempdir()) / "datapulse-uv-cache"
DEFAULT_PROMOTION_AUTO_REPAIR_REQUEST = DEFAULT_OUTPUT_DIR / "promotion_auto_repair_request.json"
DEFAULT_PROMPT = "自动推进 DataPulse 蓝图"
DEFAULT_MODEL = "gpt-5.4"
DEFAULT_MODEL_REASONING_EFFORT = "xhigh"
DEFAULT_APPROVAL_POLICY = "never"
DEFAULT_PROMOTION_MODE = "manual"
DEFAULT_PRE_PROMOTION_GATE_COMMAND = "uv run python scripts/governance/run_datapulse_quick_test_gate.py"
DEFAULT_SYNC_TRACKED_GOVERNANCE_ON_STOP = True
BLOCKED_EXIT_CODE = 2
PROMOTION_REPO_LANDED = "repo_landed_false"
PROMOTION_HEAD_NOT_PUSHED = "head_not_pushed"
AUTO_CI_RESOLVABLE_GATES = {
    PROMOTION_HEAD_NOT_PUSHED,
    "ci_run_not_proven",
    "ci_run_in_progress",
    "governance_evidence_not_proven",
    "governance_evidence_in_progress",
}
AUTO_CI_HARD_STOP_GATES = {
    "ci_run_failed",
    "governance_evidence_failed",
    "workflow_dispatch_missing",
    "structured_release_bundle_missing",
}
AUTO_REPO_LANDED_REOPEN_BLOCKERS = {"workspace_dirty"}
WORKFLOW_RUN_FIELDS = [
    "databaseId",
    "headSha",
    "headBranch",
    "status",
    "conclusion",
    "event",
    "workflowName",
    "createdAt",
    "updatedAt",
    "url",
]
PYTEST_PASSED_SUMMARY_PATTERN = re.compile(r"\b\d+\s+passed\b")
ENV_ASSIGNMENT_PATTERN = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*=.*$")
PROMOTION_AUTO_REPAIR_ENV_VAR = "DATAPULSE_PROMOTION_AUTO_REPAIR_PATH"
PROMOTION_AUTO_REPAIR_REQUEST_SCHEMA = "datapulse.promotion_auto_repair_request.v1"


def _to_text(value: Any) -> str:
    return str(value).strip() if value is not None else ""


def build_subprocess_env() -> dict[str, str]:
    env = os.environ.copy()
    if sys.platform == "darwin":
        env.setdefault("SYSTEM_VERSION_COMPAT", "1")
    env.setdefault("UV_CACHE_DIR", str(DEFAULT_UV_CACHE_DIR))
    return env


class PromotionExecutionError(RuntimeError):
    def __init__(self, reason: str, detail: str = "", payload: dict[str, Any] | None = None) -> None:
        super().__init__(detail or reason)
        self.reason = _to_text(reason) or "promotion_blocked"
        self.detail = _to_text(detail) or self.reason
        self.payload = dict(payload or {})


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run a local Codex-driven DataPulse blueprint loop that can land the current ready slice and then re-evaluate state."
    )
    parser.add_argument("--codex-bin", default="codex")
    parser.add_argument("--prompt", default=DEFAULT_PROMPT)
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument(
        "--model-reasoning-effort",
        default=DEFAULT_MODEL_REASONING_EFFORT,
        choices=("low", "medium", "high", "xhigh"),
    )
    parser.add_argument(
        "--ask-for-approval",
        default=DEFAULT_APPROVAL_POLICY,
        choices=("untrusted", "on-failure", "on-request", "never"),
    )
    parser.add_argument(
        "--sandbox",
        default="danger-full-access",
        choices=("read-only", "workspace-write", "danger-full-access"),
    )
    parser.add_argument("--dangerously-bypass-approvals-and-sandbox", action="store_true")
    parser.add_argument("--max-rounds", type=int, default=6)
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
        "--bundle-dir",
        type=Path,
        default=DEFAULT_BUNDLE_DIR,
        help="Repository structured evidence bundle directory refreshed when tracked governance snapshots are synced after a terminal stop.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Directory for per-round prompts and Codex last-message outputs. Defaults to out/codex_blueprint_loop.",
    )
    parser.add_argument(
        "--obsidian-source",
        default="",
        help="Optional Obsidian note or directory to expose via --add-dir during Codex execution.",
    )
    parser.add_argument(
        "--continue-through-promotions",
        action="store_true",
        help="Accepted for compatibility. Automatic repo_landed/ci_proven continuation is controlled by --promotion-mode.",
    )
    parser.add_argument(
        "--promotion-mode",
        default=DEFAULT_PROMOTION_MODE,
        choices=("manual", "auto"),
        help="When set to auto, the runner may auto-resolve DataPulse's local repo_landed promotion and then drive the current ci_proven evidence path.",
    )
    parser.add_argument(
        "--push-remote",
        default="origin",
        help="Remote used for auto ci_proven push steps. Defaults to origin.",
    )
    parser.add_argument(
        "--release-tag-label",
        default="",
        help="Accepted for compatibility. The local blueprint loop does not create tags or releases.",
    )
    parser.add_argument(
        "--allow-existing-dirty-worktree",
        action="store_true",
        help="Permit auto-promotion to commit a worktree that was already dirty before this loop run started.",
    )
    parser.add_argument(
        "--poll-interval-seconds",
        type=int,
        default=15,
        help="Polling interval used while waiting for CI or governance evidence runs.",
    )
    parser.add_argument(
        "--ci-timeout-seconds",
        type=int,
        default=900,
        help="Timeout used while waiting for a required CI or governance evidence run.",
    )
    parser.add_argument(
        "--pre-promotion-gate-command",
        default=DEFAULT_PRE_PROMOTION_GATE_COMMAND,
        help="Read-only verification command executed before auto repo_landed promotion. Use an empty string to disable.",
    )
    parser.add_argument(
        "--sync-tracked-governance-on-stop",
        action=argparse.BooleanOptionalAction,
        default=DEFAULT_SYNC_TRACKED_GOVERNANCE_ON_STOP,
        help="Refresh tracked out/governance and release bundle snapshots when the loop reaches a terminal stopped state.",
    )
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--stdout", action="store_true", help="Accepted for compatibility. JSON is always printed.")
    return parser.parse_args()


def build_codex_exec_command(
    *,
    codex_bin: str,
    prompt: str,
    model: str,
    model_reasoning_effort: str,
    ask_for_approval: str,
    sandbox: str,
    dangerous: bool,
    output_last_message: Path,
    obsidian_source: Path | None,
) -> list[str]:
    command = [
        codex_bin,
        "--model",
        model,
        "-c",
        f'model_reasoning_effort="{model_reasoning_effort}"',
        "--ask-for-approval",
        ask_for_approval,
        "--sandbox",
        sandbox,
        "exec",
        "-C",
        str(REPO_ROOT),
        "--output-last-message",
        str(output_last_message),
    ]
    if dangerous:
        command.append("--dangerously-bypass-approvals-and-sandbox")
    if obsidian_source is not None:
        add_dir = obsidian_source if obsidian_source.is_dir() else obsidian_source.parent
        command.extend(["--add-dir", str(add_dir.resolve())])
    command.append(prompt)
    return command


def resolve_obsidian_source(raw_path: str) -> Path | None:
    text = _to_text(raw_path)
    if not text:
        return None
    candidate = Path(text).expanduser().resolve()
    if not candidate.exists():
        return None
    return candidate


def refresh_runtime(
    *,
    plan_path: Path,
    catalog_path: Path,
    bundle_dir: Path,
    tracked_snapshots: bool,
    code_landing_status_output: Path | None = None,
    project_loop_state_output: Path | None = None,
) -> tuple[dict[str, str], dict[str, Any], dict[str, Any]]:
    if tracked_snapshots:
        snapshots = refresh_governance_snapshots(bundle_dir.resolve(), plan_path=plan_path.resolve())
    else:
        if code_landing_status_output is None or project_loop_state_output is None:
            raise ValueError("ephemeral refresh requires explicit code_landing_status_output and project_loop_state_output")
        snapshots = refresh_governance_snapshots_to_targets(
            bundle_dir=bundle_dir.resolve(),
            plan_path=plan_path.resolve(),
            code_landing_status_output=code_landing_status_output.resolve(),
            project_loop_state_output=project_loop_state_output.resolve(),
        )
    runtime = build_datapulse_loop_runtime(plan_path, catalog_path)
    plan = load_plan(plan_path)
    return snapshots, runtime, plan


def git_output(*args: str) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        return ""
    return completed.stdout.strip()


def gh_json(*args: str) -> Any | None:
    completed = subprocess.run(
        ["gh", *args],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
        env=build_subprocess_env(),
    )
    if completed.returncode != 0:
        return None
    content = completed.stdout.strip()
    if not content:
        return None
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        return None


def workspace_status_lines() -> list[str]:
    output = git_output("status", "--short")
    if not output:
        return []
    return [line for line in output.splitlines() if _to_text(line)]


def changed_paths_from_status_lines(status_lines: list[str]) -> list[str]:
    paths: list[str] = []
    for line in status_lines:
        if len(line) < 3:
            continue
        raw_path = line[2:].strip()
        if " -> " in raw_path:
            paths.extend([part.strip() for part in raw_path.split(" -> ") if _to_text(part)])
        elif _to_text(raw_path):
            paths.append(raw_path)
    deduped: list[str] = []
    seen: set[str] = set()
    for item in paths:
        if item in seen:
            continue
        seen.add(item)
        deduped.append(item)
    return deduped


def stage_and_commit_all(commit_message: str, *, dry_run: bool) -> dict[str, Any]:
    status_lines = workspace_status_lines()
    payload: dict[str, Any] = {
        "commit_message": commit_message,
        "changed_paths": changed_paths_from_status_lines(status_lines),
    }
    if dry_run:
        payload["dry_run"] = True
        return payload

    subprocess.run(["git", "add", "-A"], cwd=REPO_ROOT, check=True)
    subprocess.run(["git", "commit", "-m", commit_message], cwd=REPO_ROOT, check=True)
    payload["head"] = git_output("rev-parse", "HEAD")
    return payload


def push_current_branch(remote: str, branch: str, *, dry_run: bool) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "remote": remote,
        "branch": branch,
        "head": git_output("rev-parse", "HEAD"),
    }
    if dry_run:
        payload["dry_run"] = True
        return payload
    subprocess.run(["git", "push", remote, branch], cwd=REPO_ROOT, check=True)
    payload["upstream_head"] = git_output("rev-parse", "@{u}")
    return payload


def dispatch_workflow(workflow: str, branch: str, *, dry_run: bool) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "workflow": workflow,
        "branch": branch,
    }
    if dry_run:
        payload["dry_run"] = True
        return payload
    subprocess.run(
        ["gh", "workflow", "run", workflow, "--ref", branch],
        cwd=REPO_ROOT,
        check=True,
        env=build_subprocess_env(),
    )
    return payload


def list_workflow_runs(workflow: str, *, branch: str) -> list[dict[str, Any]]:
    payload = gh_json("run", "list", "--workflow", workflow, "--branch", branch, "--limit", "20", "--json", ",".join(WORKFLOW_RUN_FIELDS))
    if not isinstance(payload, list):
        return []
    runs: list[dict[str, Any]] = []
    for item in payload:
        if isinstance(item, dict):
            runs.append(item)
    return runs


def normalize_workflow_run(run: dict[str, Any]) -> dict[str, Any]:
    return {
        "database_id": int(run.get("databaseId", 0) or 0),
        "head_sha": _to_text(run.get("headSha")),
        "head_branch": _to_text(run.get("headBranch")),
        "status": _to_text(run.get("status")),
        "conclusion": _to_text(run.get("conclusion")),
        "event": _to_text(run.get("event")),
        "workflow_name": _to_text(run.get("workflowName")),
        "created_at": _to_text(run.get("createdAt")),
        "updated_at": _to_text(run.get("updatedAt")),
        "url": _to_text(run.get("url")),
    }


def wait_for_head_workflow_run(
    workflow: str,
    *,
    branch: str,
    head_sha: str,
    timeout_seconds: int,
    poll_interval_seconds: int,
) -> dict[str, Any]:
    deadline = time.monotonic() + max(timeout_seconds, 1)
    last_seen: dict[str, Any] | None = None
    while time.monotonic() <= deadline:
        matches: list[dict[str, Any]] = []
        for run in list_workflow_runs(workflow, branch=branch):
            normalized = normalize_workflow_run(run)
            if normalized.get("head_sha") != head_sha:
                continue
            if branch and normalized.get("head_branch") != branch:
                continue
            matches.append(normalized)
        if matches:
            matches.sort(
                key=lambda item: (
                    item.get("created_at", ""),
                    int(item.get("database_id", 0) or 0),
                ),
                reverse=True,
            )
            last_seen = matches[0]
            if last_seen.get("status") == "completed":
                if last_seen.get("conclusion") == "success":
                    return last_seen
                raise RuntimeError(
                    f"{workflow} run for {head_sha} concluded {last_seen.get('conclusion') or 'without_success'}: {last_seen.get('url', '')}"
                )
        time.sleep(max(poll_interval_seconds, 1))
    if last_seen:
        raise RuntimeError(
            f"timed out waiting for {workflow} run for {head_sha}; last status={last_seen.get('status')}, conclusion={last_seen.get('conclusion')}"
        )
    raise RuntimeError(f"timed out waiting for {workflow} run for {head_sha}; no matching run observed")


def build_auto_commit_message(slice_execution_brief: dict[str, Any], round_index: int | None) -> str:
    slice_id = _to_text(slice_execution_brief.get("slice_id")) or _to_text(slice_execution_brief.get("id"))
    if slice_id:
        return f"chore(loop): land {slice_id}"
    if round_index is not None:
        return f"chore(loop): land round-{round_index:02d}"
    return "chore(loop): land blueprint changes"


def find_plan_slice(plan: dict[str, Any], slice_id: str) -> dict[str, Any]:
    target = _to_text(slice_id)
    if not target:
        return {}
    for phase in plan.get("phases", []):
        for item in phase.get("slices", []):
            if _to_text(item.get("id")) == target:
                return dict(item)
    return {}


def _minimal_slice_payload(slice_payload: dict[str, Any] | None) -> dict[str, Any]:
    payload = dict(slice_payload or {})
    slice_id = _to_text(payload.get("id")) or _to_text(payload.get("slice_id"))
    if not slice_id:
        return {}
    normalized = {"id": slice_id}
    for key in ("title", "phase_id", "category", "execution_profile", "promotion_scope", "status"):
        value = _to_text(payload.get(key))
        if value:
            normalized[key] = value
    return normalized


def _repo_python_executable() -> str:
    candidates: list[Path] = [
        REPO_ROOT / ".venv" / "bin" / "python",
        REPO_ROOT / ".venv" / "bin" / "python3",
    ]
    if _to_text(sys.executable):
        candidates.append(Path(sys.executable).expanduser())
    if _to_text(sys.prefix):
        candidates.extend(
            [
                Path(sys.prefix).expanduser() / "bin" / "python",
                Path(sys.prefix).expanduser() / "bin" / "python3",
            ]
        )
    seen: set[str] = set()
    for candidate in candidates:
        candidate_text = str(candidate)
        if not candidate_text or candidate_text in seen:
            continue
        seen.add(candidate_text)
        if candidate.exists():
            return candidate_text
    return _to_text(sys.executable) or "python3"


def _parse_shell_style_command(command_text: str) -> tuple[dict[str, str], list[str]]:
    tokens = shlex.split(command_text)
    env_updates: dict[str, str] = {}
    while tokens and ENV_ASSIGNMENT_PATTERN.match(tokens[0]):
        key, value = tokens.pop(0).split("=", 1)
        env_updates[key] = value
    return env_updates, tokens


def _verification_command_argv(command_text: str) -> tuple[dict[str, str], list[str]]:
    env_updates, argv = _parse_shell_style_command(command_text)
    if not argv:
        raise ValueError(f"verification command is empty: {command_text}")
    python_exec = _repo_python_executable()
    if argv[:5] == ["uv", "run", "python", "-m", "pytest"]:
        return env_updates, [python_exec, "-m", "pytest", *argv[5:]]
    if argv[:3] == ["uv", "run", "pytest"]:
        return env_updates, [python_exec, "-m", "pytest", *argv[3:]]
    return env_updates, argv


def _looks_like_pytest_command(argv: list[str]) -> bool:
    if len(argv) >= 3 and argv[1:3] == ["-m", "pytest"]:
        return True
    return Path(argv[0]).name == "pytest" if argv else False


def _should_retry_verification_command(*, argv: list[str], completed: subprocess.CompletedProcess[str]) -> bool:
    if completed.returncode >= 0 or not _looks_like_pytest_command(argv):
        return False
    stdout = _to_text(completed.stdout)
    if not stdout or not PYTEST_PASSED_SUMMARY_PATTERN.search(stdout):
        return False
    lowered = stdout.lower()
    return "failed" not in lowered and "error" not in lowered


def _active_promotion_auto_repair_path() -> Path:
    path_text = _to_text(os.environ.get(PROMOTION_AUTO_REPAIR_ENV_VAR))
    candidate = Path(path_text).expanduser() if path_text else DEFAULT_PROMOTION_AUTO_REPAIR_REQUEST
    return candidate.resolve()


def _read_log_tail(path_text: str, *, limit_chars: int = 4000) -> str:
    text = _to_text(path_text)
    if not text:
        return ""
    path = Path(text).expanduser()
    if not path.exists():
        return ""
    try:
        return path.read_text(encoding="utf-8", errors="replace")[-limit_chars:]
    except OSError:
        return ""


def _failed_verification_result(verification_results: list[dict[str, Any]]) -> dict[str, Any]:
    for result in verification_results:
        if int(result.get("exit_code", 0) or 0) != 0:
            return dict(result)
    return dict(verification_results[-1]) if verification_results else {}


def load_promotion_auto_repair_request() -> dict[str, Any] | None:
    path = _active_promotion_auto_repair_path()
    if not path.exists():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None
    if not isinstance(payload, dict):
        return None
    if _to_text(payload.get("schema_version")) != PROMOTION_AUTO_REPAIR_REQUEST_SCHEMA:
        return None
    payload["path"] = display_path(path)
    return payload


def clear_promotion_auto_repair_request() -> None:
    path = _active_promotion_auto_repair_path()
    os.environ.pop(PROMOTION_AUTO_REPAIR_ENV_VAR, None)
    if path.exists():
        path.unlink()


def _persist_promotion_auto_repair_request(
    *,
    reason: str,
    detail: str,
    round_index: int | None,
    runtime: dict[str, Any],
    slice_execution_brief: dict[str, Any],
    verification_results: list[dict[str, Any]],
    local_verification_commands: list[str],
) -> Path:
    path = _active_promotion_auto_repair_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    failed_result = _failed_verification_result(verification_results)
    failed_stdout_path = _to_text(failed_result.get("stdout_path"))
    failed_stderr_path = _to_text(failed_result.get("stderr_path"))
    payload = {
        "schema_version": PROMOTION_AUTO_REPAIR_REQUEST_SCHEMA,
        "generated_at_utc": utc_now(),
        "reason": _to_text(reason),
        "detail": _to_text(detail),
        "round": round_index,
        "current_level": _to_text(runtime.get("current_level")),
        "remaining_promotion_gates": [
            _to_text(item) for item in runtime.get("remaining_promotion_gates", []) if _to_text(item)
        ],
        "original_next_slice": _minimal_slice_payload(dict(runtime.get("next_slice") or {}))
        or _minimal_slice_payload(slice_execution_brief),
        "local_verification_commands": [
            _to_text(item) for item in local_verification_commands if _to_text(item)
        ]
        or [_to_text(failed_result.get("command"))],
        "failed_command": _to_text(failed_result.get("command")),
        "exit_code": int(failed_result.get("exit_code", 0) or 0),
        "stdout_path": failed_stdout_path,
        "stderr_path": failed_stderr_path,
        "stdout_tail": _read_log_tail(failed_stdout_path),
        "stderr_tail": _read_log_tail(failed_stderr_path),
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.environ[PROMOTION_AUTO_REPAIR_ENV_VAR] = str(path)
    return path


def _refresh_promotion_auto_repair_request(
    *,
    request: dict[str, Any],
    reason: str,
    detail: str,
    verification_results: list[dict[str, Any]],
) -> Path:
    path = _active_promotion_auto_repair_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    failed_result = _failed_verification_result(verification_results)
    failed_stdout_path = _to_text(failed_result.get("stdout_path"))
    failed_stderr_path = _to_text(failed_result.get("stderr_path"))
    payload = dict(request)
    payload.update(
        {
            "schema_version": PROMOTION_AUTO_REPAIR_REQUEST_SCHEMA,
            "generated_at_utc": utc_now(),
            "reason": _to_text(reason),
            "detail": _to_text(detail),
            "failed_command": _to_text(failed_result.get("command")) or _to_text(payload.get("failed_command")),
            "exit_code": int(failed_result.get("exit_code", 0) or 0),
            "stdout_path": failed_stdout_path,
            "stderr_path": failed_stderr_path,
            "stdout_tail": _read_log_tail(failed_stdout_path),
            "stderr_tail": _read_log_tail(failed_stderr_path),
        }
    )
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.environ[PROMOTION_AUTO_REPAIR_ENV_VAR] = str(path)
    return path


def resume_promotion_auto_repair(*, output_dir: Path, dry_run: bool) -> bool:
    request = load_promotion_auto_repair_request()
    if request is None:
        return True
    request_path = _active_promotion_auto_repair_path()
    commands = [
        _to_text(item) for item in request.get("local_verification_commands", []) if _to_text(item)
    ] or [_to_text(request.get("failed_command"))]
    if not any(commands):
        if not dry_run:
            clear_promotion_auto_repair_request()
        print(
            json.dumps(
                {
                    "status": "promotion_auto_repair_cleared",
                    "repair_request_path": display_path(request_path),
                    "failed_command": _to_text(request.get("failed_command")),
                },
                ensure_ascii=False,
            )
        )
        return True
    results, ok = run_verification_commands(
        commands=commands,
        round_dir=output_dir / "promotion-auto-repair-resume",
        dry_run=dry_run,
    )
    print(
        json.dumps(
            {
                "status": "promotion_auto_repair_resume_completed",
                "ok": ok,
                "results": results,
                "repair_request_path": display_path(request_path),
            },
            ensure_ascii=False,
        )
    )
    if not ok:
        refreshed_path = _refresh_promotion_auto_repair_request(
            request=request,
            reason="promotion_auto_repair_resume_failed",
            detail="promotion_auto_repair_resume_failed",
            verification_results=results,
        )
        print(
            json.dumps(
                {
                    "status": "promotion_auto_repair_pending",
                    "repair_request_path": display_path(refreshed_path),
                    "failed_command": _to_text(_failed_verification_result(results).get("command")),
                },
                ensure_ascii=False,
            )
        )
        return False
    if not dry_run:
        clear_promotion_auto_repair_request()
    print(
        json.dumps(
            {
                "status": "promotion_auto_repair_cleared",
                "repair_request_path": display_path(request_path),
                "failed_command": _to_text(request.get("failed_command")),
                "dry_run": bool(dry_run),
            },
            ensure_ascii=False,
        )
    )
    return True


def run_verification_commands(
    *,
    commands: list[str],
    round_dir: Path,
    dry_run: bool,
) -> tuple[list[dict[str, Any]], bool]:
    results: list[dict[str, Any]] = []
    if not commands:
        return results, True
    round_dir.mkdir(parents=True, exist_ok=True)

    for index, command_text in enumerate(commands, start=1):
        stdout_path = round_dir / f"verify-{index:02d}.stdout.log"
        stderr_path = round_dir / f"verify-{index:02d}.stderr.log"
        result: dict[str, Any] = {
            "command": command_text,
            "stdout_path": str(stdout_path),
            "stderr_path": str(stderr_path),
        }
        if dry_run:
            result["exit_code"] = 0
            result["dry_run"] = True
            results.append(result)
            continue

        env = build_subprocess_env()
        env_updates, argv = _verification_command_argv(command_text)
        env.update(env_updates)
        retryable = True
        while True:
            completed = subprocess.run(
                argv,
                cwd=REPO_ROOT,
                check=False,
                env=env,
                capture_output=True,
                text=True,
            )
            if completed.returncode == 0:
                break
            if retryable and _should_retry_verification_command(argv=argv, completed=completed):
                retryable = False
                continue
            break
        stdout_path.write_text(completed.stdout or "", encoding="utf-8")
        stderr_path.write_text(completed.stderr or "", encoding="utf-8")
        result["exit_code"] = int(completed.returncode)
        results.append(result)
        if completed.returncode != 0:
            return results, False
    return results, True


def run_pre_promotion_gate(
    *,
    command_text: str,
    output_dir: Path,
    round_index: int | None,
    dry_run: bool,
) -> tuple[list[dict[str, Any]], bool]:
    if not _to_text(command_text):
        return [], True
    gate_dir = output_dir / (
        "pre-promotion-gate-initial" if round_index is None else f"pre-promotion-gate-round-{round_index:02d}"
    )
    gate_dir.mkdir(parents=True, exist_ok=True)
    return run_verification_commands(
        commands=[command_text],
        round_dir=gate_dir,
        dry_run=dry_run,
    )


def _effective_blocker_set(runtime: dict[str, Any]) -> set[str]:
    return {_to_text(item) for item in runtime.get("effective_blocking_facts", []) if _to_text(item)}


def _is_terminal_promotion_gate_stop(runtime: dict[str, Any]) -> bool:
    return _to_text(runtime.get("status")) == "stopped" and _to_text(runtime.get("reason")) == "promotion_gates_open"


def supports_auto_repo_landed(runtime: dict[str, Any]) -> bool:
    remaining = {_to_text(item) for item in runtime.get("remaining_promotion_gates", []) if _to_text(item)}
    if PROMOTION_REPO_LANDED not in remaining:
        return False
    if _is_terminal_promotion_gate_stop(runtime):
        return True
    if _to_text(runtime.get("status")) != "blocked":
        return False
    if _to_text(runtime.get("reason")) != "next_slice_blocked":
        return False
    blockers = _effective_blocker_set(runtime)
    return blockers == AUTO_REPO_LANDED_REOPEN_BLOCKERS


def supports_auto_ci_proven(runtime: dict[str, Any]) -> bool:
    remaining = {_to_text(item) for item in runtime.get("remaining_promotion_gates", []) if _to_text(item)}
    if PROMOTION_REPO_LANDED in remaining:
        return False
    if remaining & AUTO_CI_HARD_STOP_GATES:
        return False
    if not (remaining & AUTO_CI_RESOLVABLE_GATES):
        return False
    if _is_terminal_promotion_gate_stop(runtime):
        return True
    return _to_text(runtime.get("status")) == "ready" and _to_text(runtime.get("reason")) == "awaiting_manual_slice_execution"


def evaluate_progress(
    *,
    before_runtime: dict[str, Any],
    after_runtime: dict[str, Any],
    before_plan: dict[str, Any],
    after_plan: dict[str, Any],
    before_status_lines: list[str],
    after_status_lines: list[str],
) -> bool:
    before_slice_id = _to_text(dict(before_runtime.get("next_slice") or {}).get("id"))
    after_slice_id = _to_text(dict(after_runtime.get("next_slice") or {}).get("id"))
    if before_slice_id != after_slice_id:
        return True
    if _to_text(before_runtime.get("current_level")) != _to_text(after_runtime.get("current_level")):
        return True
    if list(before_runtime.get("remaining_promotion_gates", [])) != list(after_runtime.get("remaining_promotion_gates", [])):
        return True
    if before_status_lines != after_status_lines:
        return True
    before_slice = find_plan_slice(before_plan, before_slice_id)
    after_slice = find_plan_slice(after_plan, after_slice_id)
    return before_slice != after_slice


def maybe_auto_promote(
    *,
    runtime: dict[str, Any],
    slice_execution_brief: dict[str, Any],
    round_index: int | None,
    output_dir: Path,
    baseline_dirty_paths: list[str],
    promotion_mode: str,
    allow_existing_dirty_worktree: bool,
    plan_path: Path,
    catalog_path: Path,
    bundle_dir: Path,
    tracked_snapshots: bool,
    code_landing_status_output: Path | None,
    project_loop_state_output: Path | None,
    push_remote: str,
    poll_interval_seconds: int,
    ci_timeout_seconds: int,
    pre_promotion_gate_command: str,
    dry_run: bool,
) -> tuple[dict[str, Any], dict[str, str], dict[str, Any], list[dict[str, Any]]]:
    promotions: list[dict[str, Any]] = []
    snapshots: dict[str, str] = {}
    plan = load_plan(plan_path)
    current_runtime = runtime

    if _to_text(promotion_mode).lower() != "auto":
        return current_runtime, snapshots, plan, promotions

    while supports_auto_repo_landed(current_runtime):
        if baseline_dirty_paths and not allow_existing_dirty_worktree:
            raise RuntimeError(
                "auto repo_landed promotion blocked by preexisting dirty worktree; rerun with --allow-existing-dirty-worktree"
            )
        status_lines = workspace_status_lines()
        if not status_lines:
            raise RuntimeError("auto repo_landed promotion selected but workspace has no changes to commit")
        gate_results, gate_ok = run_pre_promotion_gate(
            command_text=pre_promotion_gate_command,
            output_dir=output_dir,
            round_index=round_index,
            dry_run=dry_run,
        )
        if gate_results:
            print(
                json.dumps(
                    {
                        "status": "pre_promotion_gate_completed",
                        "round": round_index,
                        "ok": gate_ok,
                        "results": gate_results,
                    },
                    ensure_ascii=False,
                )
            )
        if not gate_ok:
            request_path = _persist_promotion_auto_repair_request(
                reason="pre_promotion_gate_failed",
                detail="pre_promotion_gate_failed",
                round_index=round_index,
                runtime=current_runtime,
                slice_execution_brief=slice_execution_brief,
                verification_results=gate_results,
                local_verification_commands=[pre_promotion_gate_command],
            )
            payload: dict[str, Any] = {
                "status": "promotion_auto_repair_requested",
                "repair_request_path": display_path(request_path),
                "failed_command": _to_text(_failed_verification_result(gate_results).get("command")),
            }
            if round_index is not None:
                payload["round"] = round_index
            print(json.dumps(payload, ensure_ascii=False))
            raise PromotionExecutionError(
                "pre_promotion_gate_failed",
                "pre_promotion_gate_failed",
                {
                    "repair_request_path": display_path(request_path),
                    "failed_command": _to_text(_failed_verification_result(gate_results).get("command")),
                },
            )

        commit_message = build_auto_commit_message(slice_execution_brief, round_index)
        promotion_payload = {
            "promotion": "repo_landed",
            **stage_and_commit_all(commit_message, dry_run=dry_run),
        }
        promotions.append(promotion_payload)
        print(json.dumps({"status": "promotion_executed", **promotion_payload}, ensure_ascii=False))

        if dry_run:
            break

        snapshots, current_runtime, plan = refresh_runtime(
            plan_path=plan_path,
            catalog_path=catalog_path,
            bundle_dir=bundle_dir,
            tracked_snapshots=tracked_snapshots,
            code_landing_status_output=code_landing_status_output,
            project_loop_state_output=project_loop_state_output,
        )
        baseline_dirty_paths = changed_paths_from_status_lines(workspace_status_lines())

    while supports_auto_ci_proven(current_runtime):
        landing_status = build_code_landing_status()
        git_truth = dict(landing_status.get("git", {}))
        ci_truth = dict(landing_status.get("ci", {}))
        branch = _to_text(git_truth.get("branch"))
        head_sha = _to_text(git_truth.get("head"))
        head_published = bool(git_truth.get("head_published_to_upstream"))
        proof_mode = _to_text(ci_truth.get("proof_mode")) or "push_ci_workflow"
        required_workflow = _to_text(ci_truth.get("required_workflow")) or ("governance-evidence.yml" if proof_mode == "governance_evidence_dispatch" else "CI")

        if not branch or not head_sha:
            raise RuntimeError("auto ci_proven promotion missing current branch/head truth")

        if not head_published:
            push_payload = {
                "promotion": "ci_proven",
                "step": "push_head",
                **push_current_branch(push_remote, branch, dry_run=dry_run),
            }
            promotions.append(push_payload)
            print(json.dumps({"status": "promotion_executed", **push_payload}, ensure_ascii=False))
            if dry_run:
                break
            snapshots, current_runtime, plan = refresh_runtime(
                plan_path=plan_path,
                catalog_path=catalog_path,
                bundle_dir=bundle_dir,
                tracked_snapshots=tracked_snapshots,
                code_landing_status_output=code_landing_status_output,
                project_loop_state_output=project_loop_state_output,
            )
            continue

        workflow_payload: dict[str, Any] = {
            "promotion": "ci_proven",
            "step": "await_required_workflow",
            "proof_mode": proof_mode,
            "workflow": required_workflow,
            "branch": branch,
            "head_sha": head_sha,
        }
        if proof_mode == "governance_evidence_dispatch":
            workflow_payload["dispatch"] = dispatch_workflow(required_workflow, branch, dry_run=dry_run)
        if dry_run:
            promotions.append(workflow_payload)
            print(json.dumps({"status": "promotion_executed", **workflow_payload}, ensure_ascii=False))
            break

        observed_run = wait_for_head_workflow_run(
            required_workflow,
            branch=branch,
            head_sha=head_sha,
            timeout_seconds=ci_timeout_seconds,
            poll_interval_seconds=poll_interval_seconds,
        )
        workflow_payload["observed_run"] = observed_run
        promotions.append(workflow_payload)
        print(json.dumps({"status": "promotion_executed", **workflow_payload}, ensure_ascii=False))

        snapshots, current_runtime, plan = refresh_runtime(
            plan_path=plan_path,
            catalog_path=catalog_path,
            bundle_dir=bundle_dir,
            tracked_snapshots=tracked_snapshots,
            code_landing_status_output=code_landing_status_output,
            project_loop_state_output=project_loop_state_output,
        )

    return current_runtime, snapshots, plan, promotions


def effective_plan_edit_target(plan_path: Path, plan: dict[str, Any]) -> str:
    base_plan = _to_text(plan.get("_base_plan_path"))
    if base_plan:
        return display_path(Path(base_plan))
    return display_path(plan_path.resolve())


def format_list(items: list[str]) -> str:
    cleaned = [_to_text(item) for item in items if _to_text(item)]
    if not cleaned:
        return "- (none)"
    return "\n".join(f"- {item}" for item in cleaned)


def build_codex_prompt_text(
    *,
    prompt: str,
    runtime: dict[str, Any],
    adapter_entry: dict[str, Any],
    plan_edit_target: str,
    promotion_mode: str,
    obsidian_source: Path | None,
) -> str:
    next_slice = dict(runtime.get("next_slice") or {})
    lines = [
        prompt,
        "",
        "当前任务是推进 DataPulse blueprint loop 的当前 next_slice，并在本轮结束后让 loop 重新评估。",
        "",
        "当前 loop 事实：",
        f"- plan_id: {_to_text(runtime.get('plan_id'))}",
        f"- current_level: {_to_text(runtime.get('current_level'))}",
        f"- next_slice: {_to_text(next_slice.get('id'))} / {_to_text(next_slice.get('phase_id'))} / {_to_text(next_slice.get('title'))}",
        f"- execution_profile: {_to_text(next_slice.get('execution_profile'))}",
        f"- current_status: {_to_text(runtime.get('status'))}",
        f"- current_reason: {_to_text(runtime.get('reason'))}",
        f"- promotion_mode: {_to_text(promotion_mode)}",
        "",
        "蓝图与治理约束：",
        f"- blueprint edit target: {plan_edit_target}",
        "- confirmed targets must remain structured as phase + slices + status",
        "- do not introduce Future Track or future_* prose-only planning state",
        "- only land the current next_slice unless the current slice cannot be completed without a tightly-scoped prerequisite",
        "- keep scheduled governance workflow read-only; do not turn .github/workflows/governance-loop-auto.yml into a business executor",
        "- do not hand-edit out/governance or out/*release_bundle snapshots unless a generated exporter requires regeneration",
        "",
        "当前 slice adapter：",
        f"- execute_mode: {_to_text(adapter_entry.get('execute_mode')) or 'unspecified'}",
        f"- adapter_type: {_to_text(adapter_entry.get('adapter_type')) or 'unspecified'}",
        f"- summary: {_to_text(adapter_entry.get('summary')) or 'unspecified'}",
        "- candidate_commands:",
        format_list(list(adapter_entry.get("candidate_commands", []))),
        "- verification_commands:",
        format_list(list(adapter_entry.get("verification_commands", []))),
        "- target_artifacts:",
        format_list(list(adapter_entry.get("target_artifacts", []))),
        "- notes:",
        format_list(list(adapter_entry.get("notes", []))),
        f"- exit_condition: {_to_text(adapter_entry.get('exit_condition')) or 'unspecified'}",
        "",
        "完成标准：",
        f"- the repo should reflect the landing of {_to_text(next_slice.get('id'))}",
        "- update the structured blueprint slice status to match reality",
        "- if the slice lands, re-run or leave enough changes so the governance exporters can reflect the new state",
        "- if the slice cannot land safely, leave the repo in a truthful blocked state rather than faking completion",
    ]
    if obsidian_source is not None:
        lines.extend(
            [
                "",
                f"外部事实补充路径可读取：{obsidian_source}",
                "- if you need external fact wording, read it from the provided Obsidian path and then land only the repo-relevant structured truth.",
            ]
        )
    return "\n".join(lines).strip() + "\n"


def stop_snapshot(runtime: dict[str, Any]) -> dict[str, Any]:
    payload = {
        "status": _to_text(runtime.get("status")) or "stopped",
        "reason": _to_text(runtime.get("reason")) or "loop_stopped",
        "current_level": _to_text(runtime.get("current_level")),
        "next_slice": _to_text(dict(runtime.get("next_slice") or {}).get("id")),
        "blocking_facts": list(runtime.get("effective_blocking_facts", [])),
        "remaining_promotion_gates": list(runtime.get("remaining_promotion_gates", [])),
    }
    return payload


def refresh_tracked_governance_on_stop(
    *,
    runtime: dict[str, Any],
    plan_path: Path,
    bundle_dir: Path,
    enabled: bool,
    dry_run: bool,
) -> dict[str, str]:
    if not enabled or dry_run:
        return {}
    if _to_text(runtime.get("status")) != "stopped":
        return {}
    return refresh_governance_snapshots(bundle_dir.resolve(), plan_path=plan_path.resolve())


def run_round(
    *,
    command: list[str],
    output_dir: Path,
    round_index: int,
    prompt_text: str,
    dry_run: bool,
) -> int:
    round_dir = output_dir / f"round-{round_index:02d}"
    round_dir.mkdir(parents=True, exist_ok=True)
    (round_dir / "prompt.txt").write_text(prompt_text, encoding="utf-8")
    (round_dir / "command.json").write_text(json.dumps(command, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(f"[round {round_index}] {' '.join(command)}")
    if dry_run:
        return 0
    completed = subprocess.run(
        command,
        cwd=REPO_ROOT,
        check=False,
        env=build_subprocess_env(),
    )
    return int(completed.returncode)


def main() -> int:
    args = parse_args()
    obsidian_source = resolve_obsidian_source(args.obsidian_source)

    with tempfile.TemporaryDirectory(prefix="datapulse_codex_loop_") as temp_dir:
        temp_root = Path(temp_dir)
        tracked_snapshots_enabled = False
        code_landing_status_output = temp_root / "governance" / "code_landing_status.draft.json"
        project_loop_state_output = temp_root / "governance" / "project_specific_loop_state.draft.json"
        bundle_dir = temp_root / "bundle"
        tracked_bundle_dir = args.bundle_dir.expanduser().resolve()
        output_dir = args.output_dir.expanduser().resolve()
        output_dir.mkdir(parents=True, exist_ok=True)
        if _to_text(args.promotion_mode).lower() == "auto":
            if not resume_promotion_auto_repair(output_dir=output_dir, dry_run=bool(args.dry_run)):
                return BLOCKED_EXIT_CODE

        baseline_dirty_paths = changed_paths_from_status_lines(workspace_status_lines())
        snapshots, runtime, plan = refresh_runtime(
            plan_path=args.plan,
            catalog_path=args.catalog,
            bundle_dir=bundle_dir,
            tracked_snapshots=tracked_snapshots_enabled,
            code_landing_status_output=code_landing_status_output,
            project_loop_state_output=project_loop_state_output,
        )
        initial_payload = {
            "status": _to_text(runtime.get("status")),
            "reason": _to_text(runtime.get("reason")),
            "current_level": _to_text(runtime.get("current_level")),
            "next_slice": _to_text(dict(runtime.get("next_slice") or {}).get("id")),
            "snapshots_refreshed": snapshots,
        }
        print(json.dumps({"status": "runtime_refreshed", **initial_payload}, ensure_ascii=False))

        try:
            runtime, promotion_snapshots, plan, _ = maybe_auto_promote(
                runtime=runtime,
                slice_execution_brief=dict(runtime.get("slice_execution_brief") or runtime.get("adapter_entry") or {}),
                round_index=None,
                output_dir=output_dir,
                baseline_dirty_paths=baseline_dirty_paths,
                promotion_mode=str(args.promotion_mode),
                allow_existing_dirty_worktree=bool(args.allow_existing_dirty_worktree),
                plan_path=args.plan,
                catalog_path=args.catalog,
                bundle_dir=bundle_dir,
                tracked_snapshots=tracked_snapshots_enabled,
                code_landing_status_output=code_landing_status_output,
                project_loop_state_output=project_loop_state_output,
                push_remote=str(args.push_remote),
                poll_interval_seconds=int(args.poll_interval_seconds),
                ci_timeout_seconds=int(args.ci_timeout_seconds),
                pre_promotion_gate_command=str(args.pre_promotion_gate_command),
                dry_run=bool(args.dry_run),
            )
            if promotion_snapshots:
                snapshots = promotion_snapshots
        except PromotionExecutionError as exc:
            print(
                json.dumps(
                    {
                        "status": "blocked",
                        "reason": "auto_promotion_blocked",
                        "detail": exc.detail,
                        **exc.payload,
                    },
                    ensure_ascii=False,
                )
            )
            return BLOCKED_EXIT_CODE
        except RuntimeError as exc:
            print(json.dumps({"status": "blocked", "reason": "auto_promotion_blocked", "detail": str(exc)}, ensure_ascii=False))
            return BLOCKED_EXIT_CODE

        if _to_text(runtime.get("status")) == "blocked":
            print(json.dumps(stop_snapshot(runtime), ensure_ascii=False))
            return BLOCKED_EXIT_CODE
        if _to_text(runtime.get("status")) == "stopped":
            tracked_snapshots = refresh_tracked_governance_on_stop(
                runtime=runtime,
                plan_path=args.plan,
                bundle_dir=tracked_bundle_dir,
                enabled=bool(args.sync_tracked_governance_on_stop),
                dry_run=bool(args.dry_run),
            )
            if tracked_snapshots:
                print(json.dumps({"status": "tracked_snapshots_refreshed", "snapshots_refreshed": tracked_snapshots}, ensure_ascii=False))
            print(json.dumps(stop_snapshot(runtime), ensure_ascii=False))
            return 0

        for round_index in range(1, max(int(args.max_rounds), 1) + 1):
            runtime = build_datapulse_loop_runtime(args.plan, args.catalog)
            before_runtime = dict(runtime)
            next_slice = dict(runtime.get("next_slice") or {})
            adapter_entry = dict(runtime.get("slice_execution_brief") or runtime.get("adapter_entry") or {})
            plan = load_plan(args.plan)
            before_status_lines = workspace_status_lines()
            before_plan = plan
            prompt_text = build_codex_prompt_text(
                prompt=str(args.prompt),
                runtime=runtime,
                adapter_entry=adapter_entry,
                plan_edit_target=effective_plan_edit_target(args.plan, plan),
                promotion_mode=str(args.promotion_mode),
                obsidian_source=obsidian_source,
            )
            round_dir = output_dir / f"round-{round_index:02d}"
            output_last_message = round_dir / "last_message.txt"
            command = build_codex_exec_command(
                codex_bin=str(args.codex_bin),
                prompt=prompt_text,
                model=str(args.model),
                model_reasoning_effort=str(args.model_reasoning_effort),
                ask_for_approval=str(args.ask_for_approval),
                sandbox=str(args.sandbox),
                dangerous=bool(args.dangerously_bypass_approvals_and_sandbox),
                output_last_message=output_last_message,
                obsidian_source=obsidian_source,
            )
            exit_code = run_round(
                command=command,
                output_dir=output_dir,
                round_index=round_index,
                prompt_text=prompt_text,
                dry_run=bool(args.dry_run),
            )
            if exit_code != 0:
                print(json.dumps({"status": "failed", "round": round_index, "exit_code": exit_code}, ensure_ascii=False))
                return exit_code

            verification_results, verification_ok = run_verification_commands(
                commands=list(adapter_entry.get("verification_commands", [])),
                round_dir=round_dir,
                dry_run=bool(args.dry_run),
            )
            print(
                json.dumps(
                    {
                        "status": "verification_completed",
                        "round": round_index,
                        "ok": verification_ok,
                        "results": verification_results,
                    },
                    ensure_ascii=False,
                )
            )
            if not verification_ok:
                print(
                    json.dumps(
                        {
                            "status": "blocked",
                            "reason": "post_round_verification_failed",
                            "round": round_index,
                            "verification_results": verification_results,
                        },
                        ensure_ascii=False,
                    )
                )
                return BLOCKED_EXIT_CODE

            snapshots, runtime, _ = refresh_runtime(
                plan_path=args.plan,
                catalog_path=args.catalog,
                bundle_dir=bundle_dir,
                tracked_snapshots=tracked_snapshots_enabled,
                code_landing_status_output=code_landing_status_output,
                project_loop_state_output=project_loop_state_output,
            )
            after_plan = load_plan(args.plan)
            after_status_lines = workspace_status_lines()

            if not args.dry_run and not evaluate_progress(
                before_runtime=before_runtime,
                after_runtime=runtime,
                before_plan=before_plan,
                after_plan=after_plan,
                before_status_lines=before_status_lines,
                after_status_lines=after_status_lines,
            ):
                print(
                    json.dumps(
                        {
                            "status": "blocked",
                            "reason": "no_progress_detected",
                            "round": round_index,
                            "next_slice": _to_text(next_slice.get("id")),
                        },
                        ensure_ascii=False,
                    )
                )
                return BLOCKED_EXIT_CODE

            try:
                runtime, promotion_snapshots, _, promotions = maybe_auto_promote(
                    runtime=runtime,
                    slice_execution_brief=adapter_entry,
                    round_index=round_index,
                    output_dir=output_dir,
                    baseline_dirty_paths=baseline_dirty_paths,
                    promotion_mode=str(args.promotion_mode),
                    allow_existing_dirty_worktree=bool(args.allow_existing_dirty_worktree),
                    plan_path=args.plan,
                    catalog_path=args.catalog,
                        bundle_dir=bundle_dir,
                        tracked_snapshots=tracked_snapshots_enabled,
                        code_landing_status_output=code_landing_status_output,
                        project_loop_state_output=project_loop_state_output,
                        push_remote=str(args.push_remote),
                        poll_interval_seconds=int(args.poll_interval_seconds),
                        ci_timeout_seconds=int(args.ci_timeout_seconds),
                        pre_promotion_gate_command=str(args.pre_promotion_gate_command),
                        dry_run=bool(args.dry_run),
                )
                if promotions and promotion_snapshots:
                    snapshots = promotion_snapshots
            except PromotionExecutionError as exc:
                payload = {
                    "status": "blocked",
                    "reason": "auto_promotion_blocked",
                    "round": round_index,
                    "detail": exc.detail,
                    **exc.payload,
                }
                print(json.dumps(payload, ensure_ascii=False))
                return BLOCKED_EXIT_CODE
            except RuntimeError as exc:
                print(
                    json.dumps(
                        {
                            "status": "blocked",
                            "reason": "auto_promotion_blocked",
                            "round": round_index,
                            "detail": str(exc),
                        },
                        ensure_ascii=False,
                    )
                )
                return BLOCKED_EXIT_CODE

            status_text = _to_text(runtime.get("status"))
            progress_payload = {
                "status": "continue",
                "round": round_index,
                "current_level": _to_text(runtime.get("current_level")),
                "next_slice": _to_text(dict(runtime.get("next_slice") or {}).get("id")),
                "runtime_status": status_text,
                "runtime_reason": _to_text(runtime.get("reason")),
                "snapshots_refreshed": snapshots,
            }
            print(json.dumps(progress_payload, ensure_ascii=False))
            baseline_dirty_paths = changed_paths_from_status_lines(workspace_status_lines())

            if status_text == "blocked":
                payload = stop_snapshot(runtime)
                payload["round"] = round_index
                print(json.dumps(payload, ensure_ascii=False))
                return BLOCKED_EXIT_CODE
            if status_text == "stopped":
                tracked_snapshots = refresh_tracked_governance_on_stop(
                    runtime=runtime,
                    plan_path=args.plan,
                    bundle_dir=tracked_bundle_dir,
                    enabled=bool(args.sync_tracked_governance_on_stop),
                    dry_run=bool(args.dry_run),
                )
                if tracked_snapshots:
                    print(
                        json.dumps(
                            {
                                "status": "tracked_snapshots_refreshed",
                                "round": round_index,
                                "snapshots_refreshed": tracked_snapshots,
                            },
                            ensure_ascii=False,
                        )
                    )
                payload = stop_snapshot(runtime)
                payload["round"] = round_index
                print(json.dumps(payload, ensure_ascii=False))
                return 0

            if _to_text(dict(runtime.get("next_slice") or {}).get("id")) == _to_text(next_slice.get("id")) and args.dry_run:
                continue

    print(json.dumps({"status": "max_rounds_reached", "max_rounds": int(args.max_rounds)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
