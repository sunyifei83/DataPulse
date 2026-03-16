#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from loop_core_draft import (
    build_project_loop_state_core,
    current_level_from_promotion_levels,
    dedupe,
    ensure_valid_blueprint_plan,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
ARTIFACTS_ROOT = REPO_ROOT / "artifacts"
DRAFT_PLAN_PATH = REPO_ROOT / "docs/governance/datapulse-blueprint-plan.draft.json"
ACTIVE_PLAN_PATH = REPO_ROOT / "docs/governance/datapulse-blueprint-plan.json"
DEFAULT_PLAN_PATH = ACTIVE_PLAN_PATH if ACTIVE_PLAN_PATH.exists() else DRAFT_PLAN_PATH
DEFAULT_OUT_DIR = REPO_ROOT / "out/governance"
DEFAULT_QUICK_TEST_GATE_PATH = ARTIFACTS_ROOT / "governance" / "quick_test_gate.draft.json"
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


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(read_text(path))


def deep_merge_dicts(base: dict[str, Any], overlay: dict[str, Any]) -> dict[str, Any]:
    merged = dict(base)
    for key, value in overlay.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = deep_merge_dicts(dict(merged[key]), value)
        else:
            merged[key] = value
    return merged


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def docs_governance_dir() -> Path:
    return REPO_ROOT / "docs/governance"


def resolve_repo_path(raw_path: str, *, relative_to: Path | None = None) -> Path:
    candidate = Path(raw_path)
    if candidate.is_absolute():
        return candidate.resolve()
    repo_candidate = (REPO_ROOT / candidate).resolve()
    if repo_candidate.exists():
        return repo_candidate
    base_dir = relative_to.parent if relative_to is not None else REPO_ROOT
    return (base_dir / candidate).resolve()


def display_path(path: Path) -> str:
    resolved = path.resolve()
    if resolved.is_relative_to(REPO_ROOT):
        return str(resolved.relative_to(REPO_ROOT))
    return str(resolved)


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


IGNORED_WORKSPACE_GATE_PATHS = {
    "out/governance/activation_intent.draft.json",
    "out/governance/activation_plan.draft.json",
    "out/governance/activation_preview.draft.json",
    "out/governance/auto_continuation_runtime.draft.json",
    "out/governance/code_landing_status.draft.json",
    "out/governance/datapulse-ai-surface-admission.example.json",
    "out/governance/datapulse_surface_runtime_hit_evidence.draft.json",
    "out/governance/evidence_bundle_manifest.draft.json",
    "out/governance/ha_delivery_facts.draft.json",
    "out/governance/ha_delivery_landing.draft.json",
    "out/governance/ha_recovery_preset.draft.json",
    "out/governance/project_specific_loop_state.draft.json",
    "out/governance/release_readiness_fact.draft.json",
    "out/governance/release_sidecar.draft.json",
    "out/governance/slice_execution_brief.draft.json",
}

IGNORED_WORKSPACE_GATE_PREFIXES = (
    "out/ha_latest_release_bundle/",
    "out/release_bundle/",
)


def gh_json(*args: str) -> Any | None:
    completed = subprocess.run(
        ["gh", *args],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
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


def repo_workspace_clean() -> tuple[bool, list[str]]:
    status = git_output("status", "--short")
    if not status:
        return True, []
    effective_lines: list[str] = []
    for line in status.splitlines():
        if not line.strip():
            continue
        if len(line) < 3:
            effective_lines.append(line)
            continue
        raw_path = line[2:].strip()
        paths = [part.strip() for part in raw_path.split(" -> ") if part.strip()] if " -> " in raw_path else [raw_path]
        if all(
            path in IGNORED_WORKSPACE_GATE_PATHS or path.startswith(IGNORED_WORKSPACE_GATE_PREFIXES)
            for path in paths
            if path
        ):
            continue
        effective_lines.append(line)
    if not effective_lines:
        return True, []
    return False, effective_lines


def changed_paths_from_status_lines(status_lines: list[str]) -> list[str]:
    paths: list[str] = []
    for line in status_lines:
        if len(line) < 3:
            continue
        raw_path = line[2:].strip()
        if " -> " in raw_path:
            parts = [part.strip() for part in raw_path.split(" -> ") if part.strip()]
            paths.extend(parts)
        elif raw_path:
            paths.append(raw_path)
    return dedupe(paths)


def ci_paths_ignore_configured() -> bool:
    ci_path = REPO_ROOT / ".github/workflows/ci.yml"
    if not ci_path.exists():
        return False
    content = read_text(ci_path)
    required_markers = [
        'paths-ignore:',
        '"*.md"',
        '"README.md"',
        '"README_CN.md"',
        '"README_EN.md"',
        '"docs/**"',
    ]
    return all(marker in content for marker in required_markers)


def is_ci_ignored_docs_path(path: str) -> bool:
    normalized = path.strip().lstrip("./")
    if not normalized:
        return False
    if normalized.startswith("docs/"):
        return True
    if normalized in {"README.md", "README_CN.md", "README_EN.md"}:
        return True
    return "/" not in normalized and normalized.endswith(".md")


def current_change_paths(workspace_clean: bool, dirty_entries: list[str]) -> list[str]:
    if not workspace_clean:
        return changed_paths_from_status_lines(dirty_entries)
    changed = git_output("diff-tree", "--no-commit-id", "--name-only", "-r", "HEAD")
    if not changed:
        return []
    return dedupe([line.strip() for line in changed.splitlines() if line.strip()])


def ci_docs_only_skip_active(workspace_clean: bool, dirty_entries: list[str]) -> tuple[bool, list[str]]:
    if not ci_paths_ignore_configured():
        return False, []
    change_paths = current_change_paths(workspace_clean, dirty_entries)
    if not change_paths:
        return False, []
    docs_only = all(is_ci_ignored_docs_path(path) for path in change_paths)
    return docs_only, change_paths


def latest_artifact_file(filename: str) -> Path | None:
    if not ARTIFACTS_ROOT.exists():
        return None
    candidates = sorted(
        ARTIFACTS_ROOT.glob(f"openclaw_datapulse_*/{filename}"),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )
    return candidates[0] if candidates else None


def parse_report_kv(path: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    for raw_line in read_text(path).splitlines():
        line = raw_line.strip()
        if not line.startswith("- "):
            continue
        if ":" not in line:
            continue
        key, value = line[2:].split(":", 1)
        result[key.strip()] = value.strip()
    return result


def parse_remote_block_codes(path: Path) -> list[str]:
    block_codes: list[str] = []
    in_block_section = False
    for raw_line in read_text(path).splitlines():
        line = raw_line.rstrip()
        stripped = line.strip()
        if stripped == "## 阻断码":
            in_block_section = True
            continue
        if in_block_section and stripped.startswith("## "):
            break
        if not in_block_section or not stripped.startswith("- "):
            continue
        token = stripped[2:].strip()
        if token == "无新增阻断码":
            continue
        block_codes.append(token)
    return block_codes


def parse_int(value: str, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def parse_local_report(path: Path | None) -> dict[str, Any] | None:
    if path is None or not path.exists():
        return None
    data = parse_report_kv(path)
    return {
        "path": display_path(path),
        "run_id": data.get("运行ID", ""),
        "pass_count": parse_int(data.get("PASS")),
        "fail_count": parse_int(data.get("FAIL")),
        "log": data.get("Log", ""),
    }


def parse_remote_report(path: Path | None) -> dict[str, Any] | None:
    if path is None or not path.exists():
        return None
    data = parse_report_kv(path)
    return {
        "path": display_path(path),
        "run_id": data.get("运行ID", ""),
        "failed_steps": parse_int(data.get("失败步骤")),
        "log": data.get("日志", ""),
        "block_codes": parse_remote_block_codes(path),
    }


def parse_quick_test_gate(path: Path | None = None) -> dict[str, Any] | None:
    target = path or DEFAULT_QUICK_TEST_GATE_PATH
    if not target.exists():
        return None
    try:
        payload = read_json(target)
    except (json.JSONDecodeError, OSError):
        return None
    if str(payload.get("schema_version", "")) not in {"", "quick_test_gate.v1"}:
        return None
    git_payload = dict(payload.get("git", {})) if isinstance(payload.get("git", {}), dict) else {}
    return {
        "path": display_path(target),
        "schema_version": str(payload.get("schema_version", "quick_test_gate.v1")),
        "generated_at_utc": str(payload.get("generated_at_utc", "")),
        "ok": bool(payload.get("ok", False)),
        "read_only": bool(payload.get("read_only", True)),
        "git": {
            "head": str(git_payload.get("head", "")),
            "branch": str(git_payload.get("branch", "")),
        },
        "steps": list(payload.get("steps", [])) if isinstance(payload.get("steps", []), list) else [],
    }


def summarize_quick_test_gate(report: dict[str, Any] | None, *, current_head: str) -> dict[str, Any]:
    if not report:
        return {
            "status": "unobserved",
            "current_head_match": False,
        }
    git_payload = dict(report.get("git", {})) if isinstance(report.get("git", {}), dict) else {}
    observed_head = str(git_payload.get("head", "")).strip()
    current_head_match = bool(current_head and observed_head and observed_head == current_head)
    if current_head_match:
        status = "passed" if bool(report.get("ok", False)) else "failed"
    elif observed_head:
        status = "stale_head"
    else:
        status = "observed"
    return {
        "status": status,
        "current_head_match": current_head_match,
    }


def quick_test_gate_headline(verification: dict[str, Any]) -> dict[str, Any]:
    quick_test = dict(verification.get("quick_test", {})) if isinstance(verification.get("quick_test", {}), dict) else {}
    observation = (
        dict(quick_test.get("latest_observation", {})) if isinstance(quick_test.get("latest_observation", {}), dict) else {}
    )
    git_payload = dict(observation.get("git", {})) if isinstance(observation.get("git", {}), dict) else {}
    return {
        "status": str(quick_test.get("latest_observation_status", "unobserved")),
        "observed": bool(observation),
        "current_head_match": bool(quick_test.get("latest_observation_current_head_match", False)),
        "ok": bool(observation.get("ok", False)) if observation else False,
        "generated_at_utc": str(observation.get("generated_at_utc", "")),
        "head": str(git_payload.get("head", "")),
        "branch": str(git_payload.get("branch", "")),
        "path": str(observation.get("path", "")),
    }


def parse_emergency_state(path: Path | None) -> dict[str, Any] | None:
    if path is None or not path.exists():
        return None
    payload = read_json(path)
    return {
        "path": display_path(path),
        "run_id": payload.get("run_id", ""),
        "state": payload.get("state", {}),
        "stop": bool(payload.get("stop", False)),
        "should_new_run_id": bool(payload.get("should_new_run_id", False)),
        "blocker_codes": payload.get("blocker_codes", []),
        "fail_steps": parse_int(payload.get("fail_steps")),
        "conclusion": payload.get("conclusion", ""),
        "first_trigger": payload.get("first_trigger", ""),
        "block_codes": payload.get("block_codes", []),
        "recommendation": payload.get("recommendation", {}),
        "evidence": payload.get("evidence", {}),
    }


def ci_docs_only_skip() -> bool:
    workspace_clean, dirty_entries = repo_workspace_clean()
    active, _ = ci_docs_only_skip_active(workspace_clean, dirty_entries)
    return active


def workflow_dispatch_available(workflow_path: Path) -> bool:
    if not workflow_path.exists():
        return False
    content = read_text(workflow_path)
    return "workflow_dispatch:" in content


def workflow_dispatch_entrypoints() -> list[str]:
    candidates = [
        REPO_ROOT / ".github/workflows/release.yml",
        REPO_ROOT / ".github/workflows/governance-evidence.yml",
    ]
    entrypoints: list[str] = []
    for path in candidates:
        if workflow_dispatch_available(path):
            entrypoints.append(display_path(path))
    return entrypoints


def workflow_push_tag_release_enabled(workflow_path: Path) -> bool:
    if not workflow_path.exists():
        return False
    content = read_text(workflow_path)
    return "push:" in content and "tags:" in content


def git_upstream_ref() -> str:
    return git_output("rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}")


def git_upstream_head() -> str:
    return git_output("rev-parse", "@{u}")


def current_head_published(head_sha: str) -> tuple[bool, str, str]:
    upstream_ref = git_upstream_ref()
    upstream_head = git_upstream_head()
    return bool(head_sha and upstream_head and upstream_head == head_sha), upstream_ref, upstream_head


def list_github_workflow_runs(workflow: str, *, branch: str = "", limit: int = 20) -> list[dict[str, Any]]:
    args = ["run", "list", "--workflow", workflow, "--limit", str(limit), "--json", ",".join(WORKFLOW_RUN_FIELDS)]
    if branch:
        args.extend(["--branch", branch])
    payload = gh_json(*args)
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
        "head_sha": str(run.get("headSha", "")).strip(),
        "head_branch": str(run.get("headBranch", "")).strip(),
        "status": str(run.get("status", "")).strip(),
        "conclusion": str(run.get("conclusion", "")).strip(),
        "event": str(run.get("event", "")).strip(),
        "workflow_name": str(run.get("workflowName", "")).strip(),
        "created_at": str(run.get("createdAt", "")).strip(),
        "updated_at": str(run.get("updatedAt", "")).strip(),
        "url": str(run.get("url", "")).strip(),
    }


def latest_workflow_run_for_head(workflow: str, *, head_sha: str, branch: str) -> dict[str, Any] | None:
    if not head_sha:
        return None
    matches: list[dict[str, Any]] = []
    for run in list_github_workflow_runs(workflow, branch=branch):
        normalized = normalize_workflow_run(run)
        if normalized.get("head_sha") != head_sha:
            continue
        if branch and normalized.get("head_branch") != branch:
            continue
        matches.append(normalized)
    if not matches:
        return None
    matches.sort(
        key=lambda item: (
            item.get("created_at", ""),
            int(item.get("database_id", 0) or 0),
        ),
        reverse=True,
    )
    return matches[0]


def workflow_run_reason(prefix: str, run: dict[str, Any] | None) -> str:
    if run is None:
        return f"{prefix}_not_proven"
    status = str(run.get("status", "")).strip()
    conclusion = str(run.get("conclusion", "")).strip()
    if status and status != "completed":
        return f"{prefix}_in_progress"
    if conclusion != "success":
        return f"{prefix}_failed"
    return ""


def workflow_run_success(run: dict[str, Any] | None) -> bool:
    if run is None:
        return False
    return str(run.get("status", "")).strip() == "completed" and str(run.get("conclusion", "")).strip() == "success"


def structured_release_bundle_available() -> bool:
    candidates = [
        REPO_ROOT / "out/ha_latest_release_bundle",
        REPO_ROOT / "out/release_bundle",
    ]
    manifest_names = [
        "structured_release_bundle_manifest.draft.json",
        "evidence_bundle_manifest.draft.json",
    ]
    for path in candidates:
        if not path.exists() or not path.is_dir():
            continue
        if any((path / name).exists() for name in manifest_names):
            return True
    return False


def verification_contracts(
    local_report: dict[str, Any] | None,
    remote_report: dict[str, Any] | None,
    *,
    quick_test_report: dict[str, Any] | None = None,
    current_head: str = "",
) -> dict[str, Any]:
    quick_test_summary = summarize_quick_test_gate(quick_test_report, current_head=current_head)
    return {
        "compileall": {
            "gateable": True,
            "required_for_loop": True,
            "truth_source": "uv run python -m compileall datapulse",
        },
        "quick_test": {
            "gateable": False,
            "gateable_via_wrapper": True,
            "required_for_loop": False,
            "truth_source": "scripts/quick_test.sh",
            "wrapper_command": "uv run python scripts/governance/run_datapulse_quick_test_gate.py",
            "reason": "Current semantics are not declared as the canonical strict gate set.",
            "latest_observation": quick_test_report,
            "latest_observation_status": quick_test_summary.get("status", "unobserved"),
            "latest_observation_current_head_match": bool(quick_test_summary.get("current_head_match", False)),
        },
        "local_smoke": {
            "gateable": False,
            "gateable_via_wrapper": True,
            "required_for_loop": True,
            "truth_source": "artifacts/openclaw_datapulse_<RUN_ID>/local_report.md",
            "wrapper_command": "uv run python scripts/governance/run_datapulse_local_smoke_gate.py",
            "latest_observation": local_report,
            "reason": "Current script writes PASS/FAIL summary but does not fail the process when fail_count is nonzero.",
        },
        "console_smoke": {
            "gateable": True,
            "required_for_loop": True,
            "truth_source": "scripts/datapulse_console_smoke.sh",
        },
        "remote_smoke": {
            "gateable": False,
            "gateable_via_wrapper": True,
            "required_for_loop": True,
            "truth_source": "artifacts/openclaw_datapulse_<RUN_ID>/remote_report.md",
            "wrapper_command": "uv run python scripts/governance/run_datapulse_remote_smoke_gate.py",
            "latest_observation": remote_report,
            "reason": "Current script records required-step failures in report output but does not expose them as a strict process gate contract.",
        },
        "emergency_gate": {
            "gateable": True,
            "required_for_loop": True,
            "truth_source": "artifacts/openclaw_datapulse_<RUN_ID>/emergency_state.json",
        },
        "release_readiness": {
            "gateable": True,
            "required_for_loop": True,
            "truth_source": "scripts/release_readiness.sh",
        },
    }


def build_code_landing_status() -> dict[str, Any]:
    workspace_clean, dirty_entries = repo_workspace_clean()
    docs_only_skip_active, change_paths = ci_docs_only_skip_active(workspace_clean, dirty_entries)
    head_sha = git_output("rev-parse", "HEAD")
    branch = git_output("branch", "--show-current")
    head_published, upstream_ref, upstream_head = current_head_published(head_sha)
    local_report = parse_local_report(latest_artifact_file("local_report.md"))
    remote_report = parse_remote_report(latest_artifact_file("remote_report.md"))
    quick_test_report = parse_quick_test_gate()
    emergency_state = parse_emergency_state(latest_artifact_file("emergency_state.json"))
    structured_bundle_ready = structured_release_bundle_available()
    ci_head_run = latest_workflow_run_for_head("CI", head_sha=head_sha, branch=branch)
    governance_head_run = latest_workflow_run_for_head("governance-evidence.yml", head_sha=head_sha, branch=branch)

    verification = verification_contracts(
        local_report,
        remote_report,
        quick_test_report=quick_test_report,
        current_head=head_sha,
    )
    verification_gateable = all(
        (item.get("gateable", False) or item.get("gateable_via_wrapper", False))
        for item in verification.values()
        if item.get("required_for_loop", True)
    )

    repo_landed_reasons: list[str] = []
    if not workspace_clean:
        repo_landed_reasons.append("workspace_dirty")
    if not verification_gateable:
        repo_landed_reasons.append("verification_not_fully_gateable")
    if local_report and local_report.get("fail_count", 0) > 0:
        repo_landed_reasons.append("latest_local_smoke_failed")
    if remote_report and remote_report.get("failed_steps", 0) > 0:
        repo_landed_reasons.append("latest_remote_smoke_failed")
    if emergency_state and emergency_state.get("stop"):
        repo_landed_reasons.append("emergency_stop")

    release_workflow = REPO_ROOT / ".github/workflows/release.yml"
    dispatch_entrypoints = workflow_dispatch_entrypoints()
    workflow_dispatch_ready = bool(dispatch_entrypoints)
    tag_push_release_enabled = workflow_push_tag_release_enabled(release_workflow)
    mixed_release_policy = tag_push_release_enabled
    ci_proof_mode = "governance_evidence_dispatch" if docs_only_skip_active else "push_ci_workflow"
    ci_proof_run = governance_head_run if docs_only_skip_active else ci_head_run
    ci_proven_reasons: list[str] = []
    if repo_landed_reasons:
        ci_proven_reasons.append("repo_landed_false")
    if not head_published:
        ci_proven_reasons.append("head_not_pushed")
    if docs_only_skip_active:
        if not workflow_dispatch_ready:
            ci_proven_reasons.append("workflow_dispatch_missing")
        if not structured_bundle_ready:
            ci_proven_reasons.append("structured_release_bundle_missing")
        ci_reason = workflow_run_reason("governance_evidence", governance_head_run)
        if ci_reason:
            ci_proven_reasons.append(ci_reason)
    else:
        ci_reason = workflow_run_reason("ci_run", ci_head_run)
        if ci_reason:
            ci_proven_reasons.append(ci_reason)

    gate_groups = {
        "execution_safety": dedupe(
            [
                "workspace_dirty" if not workspace_clean else "",
            ]
        ),
        "local_verification": dedupe(
            [
                "latest_local_smoke_failed" if local_report and local_report.get("fail_count", 0) > 0 else "",
            ]
        ),
        "runtime_governance": dedupe(
            [
                "latest_remote_smoke_failed" if remote_report and remote_report.get("failed_steps", 0) > 0 else "",
                "emergency_stop" if emergency_state and emergency_state.get("stop") else "",
            ]
        ),
        "ci_policy": dedupe(
            [
                "docs_only_changes_skip_ci" if docs_only_skip_active else "",
                "head_not_pushed" if not head_published else "",
            ]
        ),
        "release_governance": dedupe(
            [
                "workflow_dispatch_missing" if not workflow_dispatch_ready else "",
                "structured_release_bundle_missing" if not structured_bundle_ready else "",
                "mixed_release_policy" if mixed_release_policy else "",
            ]
        ),
    }
    promotion_levels = {
        "repo_landed": {
            "satisfied": not repo_landed_reasons,
            "reasons": repo_landed_reasons,
        },
        "ci_proven": {
            "satisfied": not ci_proven_reasons,
            "reasons": ci_proven_reasons,
        },
    }
    headline_summary = {
        "current_level": current_level_from_promotion_levels(promotion_levels),
        "workspace_clean": workspace_clean,
        "head_published_to_upstream": head_published,
        "repo_landed": bool(promotion_levels["repo_landed"]["satisfied"]),
        "ci_proven": bool(promotion_levels["ci_proven"]["satisfied"]),
        "ci_proof_mode": ci_proof_mode,
        "required_workflow": "governance-evidence.yml" if docs_only_skip_active else "CI",
        "quick_test_gate": quick_test_gate_headline(verification),
    }

    return {
        "schema_version": "code_landing_status.v1",
        "project": "DataPulse",
        "generated_at_utc": utc_now(),
        "status_kind": "draft_export",
        "wired": False,
        "headline_summary": headline_summary,
        "git": {
            "head": head_sha,
            "branch": branch,
            "upstream_ref": upstream_ref,
            "upstream_head": upstream_head,
            "head_published_to_upstream": head_published,
        },
        "workspace": {
            "clean": workspace_clean,
            "dirty_entries": dirty_entries,
            "reason": "" if workspace_clean else "git status reported local modifications.",
        },
        "verification": verification,
        "ci": {
            "workflow_name": "CI",
            "truth_source": ".github/workflows/ci.yml",
            "docs_only_changes_skip_ci": docs_only_skip_active,
            "docs_paths_ignore_configured": ci_paths_ignore_configured(),
            "proof_mode": ci_proof_mode,
            "head_published_to_upstream": head_published,
            "required_workflow": "governance-evidence.yml" if docs_only_skip_active else "CI",
            "required_run": ci_proof_run,
            "latest_head_ci_run": ci_head_run,
            "latest_head_governance_evidence_run": governance_head_run,
            "change_scope": {
                "paths": change_paths,
                "docs_only": docs_only_skip_active,
            },
        },
        "release": {
            "mode": "mixed_local_script_and_tag_workflow" if mixed_release_policy else "script_authoritative_with_manual_workflow_repair",
            "workflow_dispatch_available": workflow_dispatch_ready,
            "workflow_dispatch_entrypoints": dispatch_entrypoints,
            "tag_push_release_enabled": tag_push_release_enabled,
            "structured_release_bundle": structured_bundle_ready,
            "policy_gates": ["mixed_release_policy"] if mixed_release_policy else [],
            "truth_sources": [
                "scripts/release_publish.sh",
                ".github/workflows/release.yml",
                ".github/workflows/governance-evidence.yml",
            ],
        },
        "gate_groups": gate_groups,
        "promotion_levels": promotion_levels,
        "observed_evidence": {
            "latest_quick_test_gate": quick_test_report,
            "latest_local_report": local_report,
            "latest_remote_report": remote_report,
            "latest_emergency_state": emergency_state,
            "latest_head_ci_run": ci_head_run,
            "latest_head_governance_evidence_run": governance_head_run,
        },
        "evidence_paths": {
            "quick_test_gate": display_path(DEFAULT_QUICK_TEST_GATE_PATH),
            "local_report": "artifacts/openclaw_datapulse_<RUN_ID>/local_report.md",
            "remote_report": "artifacts/openclaw_datapulse_<RUN_ID>/remote_report.md",
            "remote_log": "artifacts/openclaw_datapulse_<RUN_ID>/remote_test.log",
            "emergency_state": "artifacts/openclaw_datapulse_<RUN_ID>/emergency_state.json",
        },
    }

def load_plan(path: Path) -> dict[str, Any]:
    plan = read_json(path)
    if str(plan.get("schema_version", "")) != "blueprint_plan_overlay.v1":
        resolved_plan = apply_activation_policy(plan, source_path=path)
        ensure_valid_blueprint_plan(resolved_plan, source=display_path(path.resolve()))
        return resolved_plan

    base_plan_raw = str(plan.get("base_plan", "")).strip()
    if not base_plan_raw:
        raise ValueError(f"Plan overlay missing base_plan: {path}")
    base_path = resolve_repo_path(base_plan_raw, relative_to=path)
    base_plan = load_plan(base_path)

    overlay = {key: value for key, value in plan.items() if key not in {"schema_version", "base_plan"}}
    merged = deep_merge_dicts(base_plan, overlay)
    merged["_overlay_path"] = str(path.resolve())
    merged["_base_plan_path"] = str(base_path.resolve())
    resolved_plan = apply_activation_policy(merged, source_path=path)
    ensure_valid_blueprint_plan(resolved_plan, source=display_path(path.resolve()))
    return resolved_plan


def apply_activation_policy(plan: dict[str, Any], *, source_path: Path) -> dict[str, Any]:
    activation = dict(plan.get("activation", {}))
    policy_ref = activation.get("auto_continuation_policy", {})
    if not isinstance(policy_ref, dict):
        return plan
    raw_path = str(policy_ref.get("path", "")).strip()
    if not raw_path:
        return plan

    policy_path = resolve_repo_path(raw_path, relative_to=source_path)
    policy_payload: dict[str, Any]
    if policy_path.exists():
        policy_payload = read_json(policy_path)
    else:
        policy_payload = {
            "schema_version": "datapulse_auto_continuation_policy.v1",
            "enabled": False,
            "policy_status": "missing",
            "reason": "policy_file_missing",
        }
    policy_payload = dict(policy_payload)
    policy_payload["path"] = display_path(policy_path)
    activation["auto_continuation"] = policy_payload
    plan["activation"] = activation
    return plan


def write_plan(path: Path, plan: dict[str, Any]) -> None:
    write_json(path, plan)

def update_phase_statuses(plan: dict[str, Any]) -> None:
    phase_statuses: dict[str, str] = {}
    overall_status = "completed"
    for phase in plan.get("phases", []):
        slice_statuses = [item.get("status", "pending") for item in phase.get("slices", [])]
        if slice_statuses and all(status in {"completed", "skipped"} for status in slice_statuses):
            phase_status = "completed"
        elif any(status in {"completed", "skipped"} for status in slice_statuses):
            phase_status = "in_progress"
        else:
            phase_status = "pending"
        phase["status"] = phase_status
        phase_statuses[phase.get("id", "")] = phase_status
        if phase_status != "completed":
            overall_status = "in_progress"
    plan["phase_statuses"] = phase_statuses
    plan["status"] = overall_status


def find_slice(plan: dict[str, Any], slice_id: str) -> dict[str, Any] | None:
    for phase in plan.get("phases", []):
        for item in phase.get("slices", []):
            if item.get("id") == slice_id:
                return item
    return None


def next_open_slice(plan: dict[str, Any]) -> dict[str, Any] | None:
    for phase in plan.get("phases", []):
        for item in phase.get("slices", []):
            if item.get("status") not in {"completed", "skipped"}:
                return item
    return None


def refresh_recommended_next_slice(plan: dict[str, Any]) -> None:
    next_slice = next_open_slice(plan)
    if next_slice is None:
        plan["recommended_next_slice"] = {
            "id": "no-open-slice",
            "title": "No open slice",
            "reason": "All current slices are completed in this working copy.",
        }
        return
    plan["recommended_next_slice"] = {
        "id": next_slice.get("id", ""),
        "title": next_slice.get("title", ""),
        "reason": "Derived from the next open slice in the working copy.",
    }


def assert_plan_path_mutable(plan_path: Path) -> None:
    resolved = plan_path.resolve()
    if resolved.is_relative_to(docs_governance_dir()):
        raise ValueError(
            f"Refusing to mutate plan under {docs_governance_dir()}. Use a working copy under out/ or pass a temp path."
        )


def prepare_working_copy(source_path: Path, target_path: Path) -> dict[str, Any]:
    plan = load_plan(source_path)
    plan["_source_path"] = str(source_path.resolve())
    plan["working_copy"] = {
        "enabled": True,
        "source_plan": str(source_path.resolve()),
        "generated_at_utc": utc_now(),
    }
    update_phase_statuses(plan)
    refresh_recommended_next_slice(plan)
    return plan


def mark_slice_status(plan: dict[str, Any], slice_id: str, status: str) -> dict[str, Any]:
    item = find_slice(plan, slice_id)
    if item is None:
        raise ValueError(f"Slice not found: {slice_id}")
    item["status"] = status
    plan["last_updated_utc"] = utc_now()
    progress_log = list(plan.get("progress_log", []))
    progress_log.append(
        {
            "at_utc": utc_now(),
            "slice_id": slice_id,
            "status": status,
        }
    )
    plan["progress_log"] = progress_log
    update_phase_statuses(plan)
    refresh_recommended_next_slice(plan)
    return item

def build_project_loop_state(plan: dict[str, Any], landing_status: dict[str, Any]) -> dict[str, Any]:
    payload = build_project_loop_state_core(
        plan,
        landing_status,
        source_plan=display_path(Path(plan.get("_source_path", DEFAULT_PLAN_PATH))),
        generated_at_utc=utc_now(),
    )
    verification = dict(landing_status.get("verification", {}))
    quick_test = dict(verification.get("quick_test", {})) if isinstance(verification.get("quick_test", {}), dict) else {}
    observation = dict(quick_test.get("latest_observation", {})) if isinstance(quick_test.get("latest_observation", {}), dict) else {}
    git_payload = dict(observation.get("git", {})) if isinstance(observation.get("git", {}), dict) else {}
    payload["local_verification"] = {
        "quick_test_gate": {
            "status": str(quick_test.get("latest_observation_status", "unobserved")),
            "observed": bool(observation),
            "current_head_match": bool(quick_test.get("latest_observation_current_head_match", False)),
            "ok": bool(observation.get("ok", False)) if observation else False,
            "generated_at_utc": str(observation.get("generated_at_utc", "")),
            "head": str(git_payload.get("head", "")),
            "branch": str(git_payload.get("branch", "")),
            "path": str(observation.get("path", "")),
        }
    }
    next_slice = dict(payload.get("next_slice", {})) if isinstance(payload.get("next_slice", {}), dict) else {}
    flow_control = dict(payload.get("flow_control", {})) if isinstance(payload.get("flow_control", {}), dict) else {}
    payload["headline_summary"] = {
        "current_level": str(payload.get("current_level", "")),
        "workspace_clean": bool(payload.get("workspace_clean", False)),
        "next_slice_id": str(next_slice.get("id", "")),
        "next_slice_title": str(next_slice.get("title", "")),
        "status_if_run_now": str(flow_control.get("status_if_run_now", "")),
        "reason_if_run_now": str(flow_control.get("reason_if_run_now", "")),
        "quick_test_gate": dict(payload["local_verification"]["quick_test_gate"]),
    }
    return payload


def build_loop_snapshot_summary(landing_status: dict[str, Any], loop_state: dict[str, Any]) -> dict[str, Any]:
    landing_headline = (
        dict(landing_status.get("headline_summary", {}))
        if isinstance(landing_status.get("headline_summary", {}), dict)
        else {}
    )
    loop_headline = (
        dict(loop_state.get("headline_summary", {})) if isinstance(loop_state.get("headline_summary", {}), dict) else {}
    )
    quick_test_gate = (
        dict(loop_headline.get("quick_test_gate", {}))
        if isinstance(loop_headline.get("quick_test_gate", {}), dict)
        else dict(landing_headline.get("quick_test_gate", {}))
        if isinstance(landing_headline.get("quick_test_gate", {}), dict)
        else {}
    )
    return {
        "current_level": str(loop_headline.get("current_level", landing_headline.get("current_level", ""))),
        "workspace_clean": bool(loop_headline.get("workspace_clean", landing_headline.get("workspace_clean", False))),
        "next_slice_id": str(loop_headline.get("next_slice_id", "")),
        "next_slice_title": str(loop_headline.get("next_slice_title", "")),
        "status_if_run_now": str(loop_headline.get("status_if_run_now", "")),
        "reason_if_run_now": str(loop_headline.get("reason_if_run_now", "")),
        "repo_landed": bool(landing_headline.get("repo_landed", False)),
        "ci_proven": bool(landing_headline.get("ci_proven", False)),
        "quick_test_gate": quick_test_gate,
    }
