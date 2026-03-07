#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from loop_core_draft import build_project_loop_state_core, dedupe


REPO_ROOT = Path(__file__).resolve().parents[2]
ARTIFACTS_ROOT = REPO_ROOT / "artifacts"
DEFAULT_PLAN_PATH = REPO_ROOT / "docs/governance/datapulse-blueprint-plan.draft.json"
DEFAULT_OUT_DIR = REPO_ROOT / "out/governance"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(read_text(path))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def docs_governance_dir() -> Path:
    return REPO_ROOT / "docs/governance"


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


def repo_workspace_clean() -> tuple[bool, list[str]]:
    status = git_output("status", "--short")
    if not status:
        return True, []
    return False, [line for line in status.splitlines() if line.strip()]


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
        "path": str(path.relative_to(REPO_ROOT)),
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
        "path": str(path.relative_to(REPO_ROOT)),
        "run_id": data.get("运行ID", ""),
        "failed_steps": parse_int(data.get("失败步骤")),
        "log": data.get("日志", ""),
        "block_codes": parse_remote_block_codes(path),
    }


def parse_emergency_state(path: Path | None) -> dict[str, Any] | None:
    if path is None or not path.exists():
        return None
    payload = read_json(path)
    return {
        "path": str(path.relative_to(REPO_ROOT)),
        "run_id": payload.get("run_id", ""),
        "state": payload.get("state", {}),
        "stop": bool(payload.get("stop", False)),
        "conclusion": payload.get("conclusion", ""),
        "first_trigger": payload.get("first_trigger", ""),
        "block_codes": payload.get("block_codes", []),
    }


def ci_docs_only_skip() -> bool:
    ci_path = REPO_ROOT / ".github/workflows/ci.yml"
    if not ci_path.exists():
        return False
    content = read_text(ci_path)
    return "paths-ignore:" in content and '"docs/**"' in content


def workflow_dispatch_available(workflow_path: Path) -> bool:
    if not workflow_path.exists():
        return False
    content = read_text(workflow_path)
    return "workflow_dispatch:" in content


def structured_release_bundle_available() -> bool:
    candidates = [
        REPO_ROOT / "out/ha_latest_release_bundle",
        REPO_ROOT / "out/release_bundle",
    ]
    return any(path.exists() for path in candidates)


def verification_contracts(local_report: dict[str, Any] | None, remote_report: dict[str, Any] | None) -> dict[str, Any]:
    return {
        "compileall": {
            "gateable": True,
            "required_for_loop": True,
            "truth_source": "python3 -m compileall datapulse",
        },
        "quick_test": {
            "gateable": False,
            "gateable_via_wrapper": True,
            "required_for_loop": False,
            "truth_source": "scripts/quick_test.sh",
            "wrapper_command": "python3 scripts/governance/run_datapulse_quick_test_gate.py",
            "reason": "Current semantics are not declared as the canonical strict gate set.",
        },
        "local_smoke": {
            "gateable": False,
            "gateable_via_wrapper": True,
            "required_for_loop": True,
            "truth_source": "artifacts/openclaw_datapulse_<RUN_ID>/local_report.md",
            "wrapper_command": "python3 scripts/governance/run_datapulse_local_smoke_gate.py",
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
            "wrapper_command": "python3 scripts/governance/run_datapulse_remote_smoke_gate.py",
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
    local_report = parse_local_report(latest_artifact_file("local_report.md"))
    remote_report = parse_remote_report(latest_artifact_file("remote_report.md"))
    emergency_state = parse_emergency_state(latest_artifact_file("emergency_state.json"))

    verification = verification_contracts(local_report, remote_report)
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
    ci_proven_reasons: list[str] = []
    if repo_landed_reasons:
        ci_proven_reasons.append("repo_landed_false")
    if ci_docs_only_skip():
        ci_proven_reasons.append("docs_only_changes_skip_ci")
    if not workflow_dispatch_available(release_workflow):
        ci_proven_reasons.append("workflow_dispatch_missing")
    if not structured_release_bundle_available():
        ci_proven_reasons.append("structured_release_bundle_missing")

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
                "docs_only_changes_skip_ci" if ci_docs_only_skip() else "",
            ]
        ),
        "release_governance": dedupe(
            [
                "workflow_dispatch_missing" if not workflow_dispatch_available(release_workflow) else "",
                "structured_release_bundle_missing" if not structured_release_bundle_available() else "",
            ]
        ),
    }

    return {
        "schema_version": "code_landing_status.v1",
        "project": "DataPulse",
        "generated_at_utc": utc_now(),
        "status_kind": "draft_export",
        "wired": False,
        "git": {
            "head": git_output("rev-parse", "HEAD"),
            "branch": git_output("branch", "--show-current"),
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
            "docs_only_changes_skip_ci": ci_docs_only_skip(),
        },
        "release": {
            "mode": "mixed_local_script_and_tag_workflow",
            "workflow_dispatch_available": workflow_dispatch_available(release_workflow),
            "structured_release_bundle": structured_release_bundle_available(),
            "truth_sources": [
                "scripts/release_publish.sh",
                ".github/workflows/release.yml",
            ],
        },
        "gate_groups": gate_groups,
        "promotion_levels": {
            "repo_landed": {
                "satisfied": not repo_landed_reasons,
                "reasons": repo_landed_reasons,
            },
            "ci_proven": {
                "satisfied": not ci_proven_reasons,
                "reasons": ci_proven_reasons,
            },
        },
        "observed_evidence": {
            "latest_local_report": local_report,
            "latest_remote_report": remote_report,
            "latest_emergency_state": emergency_state,
        },
        "evidence_paths": {
            "local_report": "artifacts/openclaw_datapulse_<RUN_ID>/local_report.md",
            "remote_report": "artifacts/openclaw_datapulse_<RUN_ID>/remote_report.md",
            "remote_log": "artifacts/openclaw_datapulse_<RUN_ID>/remote_test.log",
            "emergency_state": "artifacts/openclaw_datapulse_<RUN_ID>/emergency_state.json",
        },
    }

def load_plan(path: Path) -> dict[str, Any]:
    return read_json(path)


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
    return build_project_loop_state_core(
        plan,
        landing_status,
        source_plan=display_path(Path(plan.get("_source_path", DEFAULT_PLAN_PATH))),
        generated_at_utc=utc_now(),
    )
