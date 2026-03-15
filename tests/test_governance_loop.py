from __future__ import annotations

import importlib
import json
import sys
from pathlib import Path

import pytest

GOVERNANCE_SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "scripts" / "governance"


@pytest.fixture(scope="module")
def governance_loop():
    if str(GOVERNANCE_SCRIPTS_DIR) not in sys.path:
        sys.path.insert(0, str(GOVERNANCE_SCRIPTS_DIR))
    return importlib.import_module("run_codex_blueprint_loop")


@pytest.fixture(scope="module")
def auto_continuation():
    if str(GOVERNANCE_SCRIPTS_DIR) not in sys.path:
        sys.path.insert(0, str(GOVERNANCE_SCRIPTS_DIR))
    return importlib.import_module("run_datapulse_auto_continuation")


def test_refresh_tracked_governance_on_stop_runs_for_terminal_stop(governance_loop, monkeypatch, tmp_path: Path) -> None:
    captured: dict[str, Path] = {}

    def _fake_refresh(bundle_dir: Path, *, plan_path: Path) -> dict[str, str]:
        captured["bundle_dir"] = bundle_dir
        captured["plan_path"] = plan_path
        return {"code_landing_status": "out/governance/code_landing_status.draft.json"}

    monkeypatch.setattr(governance_loop, "refresh_governance_snapshots", _fake_refresh)

    result = governance_loop.refresh_tracked_governance_on_stop(
        runtime={"status": "stopped"},
        plan_path=tmp_path / "plan.json",
        bundle_dir=tmp_path / "bundle",
        enabled=True,
        dry_run=False,
    )

    assert result == {"code_landing_status": "out/governance/code_landing_status.draft.json"}
    assert captured["plan_path"] == (tmp_path / "plan.json").resolve()
    assert captured["bundle_dir"] == (tmp_path / "bundle").resolve()


def test_refresh_tracked_governance_on_stop_skips_when_disabled(governance_loop, monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(
        governance_loop,
        "refresh_governance_snapshots",
        lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("should not refresh when disabled")),
    )

    result = governance_loop.refresh_tracked_governance_on_stop(
        runtime={"status": "stopped"},
        plan_path=tmp_path / "plan.json",
        bundle_dir=tmp_path / "bundle",
        enabled=False,
        dry_run=False,
    )

    assert result == {}


def test_refresh_tracked_governance_on_stop_skips_for_dry_run_or_non_terminal_state(
    governance_loop, monkeypatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(
        governance_loop,
        "refresh_governance_snapshots",
        lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("should not refresh outside terminal stop")),
    )

    dry_run_result = governance_loop.refresh_tracked_governance_on_stop(
        runtime={"status": "stopped"},
        plan_path=tmp_path / "plan.json",
        bundle_dir=tmp_path / "bundle",
        enabled=True,
        dry_run=True,
    )
    ready_result = governance_loop.refresh_tracked_governance_on_stop(
        runtime={"status": "ready"},
        plan_path=tmp_path / "plan.json",
        bundle_dir=tmp_path / "bundle",
        enabled=True,
        dry_run=False,
    )

    assert dry_run_result == {}
    assert ready_result == {}


def test_run_capture_with_mode_raises_for_required_failure(auto_continuation, monkeypatch) -> None:
    def _fake_run(*args, **kwargs):
        return auto_continuation.subprocess.CompletedProcess(
            args[0],
            1,
            stdout='{"ok": false}\n',
            stderr="required failure\n",
        )

    monkeypatch.setattr(auto_continuation.subprocess, "run", _fake_run)

    with pytest.raises(auto_continuation.subprocess.CalledProcessError):
        auto_continuation.run_capture_with_mode(["python", "scripts/governance/run_datapulse_quick_test_gate.py"])


def test_refresh_governance_snapshots_treats_quick_test_as_best_effort(
    auto_continuation, monkeypatch, tmp_path: Path
) -> None:
    calls: list[tuple[tuple[str, ...], bool]] = []

    def _fake_run_capture(command: list[str], *, required: bool = True) -> str:
        calls.append((tuple(command), required))
        script_name = command[1] if len(command) > 1 else ""
        if script_name == "scripts/governance/run_datapulse_quick_test_gate.py":
            assert required is False
            return '{"ok": false}'
        assert required is True
        return script_name

    monkeypatch.setattr(auto_continuation, "current_python_command", lambda: ["python"])
    monkeypatch.setattr(auto_continuation, "run_capture_with_mode", _fake_run_capture)

    result = auto_continuation.refresh_governance_snapshots_to_targets(
        bundle_dir=tmp_path / "bundle",
        plan_path=tmp_path / "plan.json",
        code_landing_status_output=tmp_path / "code_landing_status.json",
        project_loop_state_output=tmp_path / "project_loop_state.json",
    )

    assert result == {
        "quick_test_gate": '{"ok": false}',
        "code_landing_status": "scripts/governance/export_datapulse_code_landing_status.py",
        "project_loop_state": "scripts/governance/export_datapulse_project_loop_state.py",
        "structured_release_bundle": "scripts/governance/export_datapulse_structured_release_bundle.py",
    }
    assert calls == [
        (("python", "scripts/governance/run_datapulse_quick_test_gate.py"), False),
        (
            (
                "python",
                "scripts/governance/export_datapulse_code_landing_status.py",
                "--output",
                str(tmp_path / "code_landing_status.json"),
            ),
            True,
        ),
        (
            (
                "python",
                "scripts/governance/export_datapulse_project_loop_state.py",
                "--plan",
                str(tmp_path / "plan.json"),
                "--output",
                str(tmp_path / "project_loop_state.json"),
            ),
            True,
        ),
        (
            (
                "python",
                "scripts/governance/export_datapulse_structured_release_bundle.py",
                "--plan",
                str(tmp_path / "plan.json"),
                "--out-dir",
                str(tmp_path / "bundle"),
                "--probe-ha-readiness",
            ),
            True,
        ),
    ]


def test_supports_auto_repo_landed_for_workspace_dirty_reopen(governance_loop) -> None:
    runtime = {
        "status": "blocked",
        "reason": "next_slice_blocked",
        "effective_blocking_facts": ["workspace_dirty"],
        "remaining_promotion_gates": ["workspace_dirty", "repo_landed_false", "head_not_pushed"],
    }

    assert governance_loop.supports_auto_repo_landed(runtime) is True


def test_supports_auto_repo_landed_rejects_non_workspace_blockers(governance_loop) -> None:
    runtime = {
        "status": "blocked",
        "reason": "next_slice_blocked",
        "effective_blocking_facts": ["workspace_dirty", "latest_local_smoke_failed"],
        "remaining_promotion_gates": ["workspace_dirty", "repo_landed_false"],
    }

    assert governance_loop.supports_auto_repo_landed(runtime) is False


def test_supports_auto_ci_proven_for_ready_manual_handoff(governance_loop) -> None:
    runtime = {
        "status": "ready",
        "reason": "awaiting_manual_slice_execution",
        "effective_blocking_facts": [],
        "remaining_promotion_gates": ["head_not_pushed", "ci_run_not_proven"],
    }

    assert governance_loop.supports_auto_ci_proven(runtime) is True


def test_supports_auto_ci_proven_rejects_hard_stop_gates(governance_loop) -> None:
    runtime = {
        "status": "ready",
        "reason": "awaiting_manual_slice_execution",
        "effective_blocking_facts": [],
        "remaining_promotion_gates": ["ci_run_not_proven", "structured_release_bundle_missing"],
    }

    assert governance_loop.supports_auto_ci_proven(runtime) is False


def test_build_subprocess_env_sets_uv_cache_dir(governance_loop, monkeypatch) -> None:
    monkeypatch.delenv("UV_CACHE_DIR", raising=False)

    env = governance_loop.build_subprocess_env()

    assert env["UV_CACHE_DIR"] == str(governance_loop.DEFAULT_UV_CACHE_DIR)


def test_verification_command_argv_normalizes_uv_pytest(governance_loop, monkeypatch, tmp_path: Path) -> None:
    venv_python = tmp_path / ".venv" / "bin" / "python"
    venv_python.parent.mkdir(parents=True, exist_ok=True)
    venv_python.write_text("", encoding="utf-8")
    monkeypatch.setattr(governance_loop, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(governance_loop.sys, "executable", str(tmp_path / "fallback-python"))
    monkeypatch.setattr(governance_loop.sys, "prefix", str(tmp_path / "fallback-prefix"))

    env_updates, argv = governance_loop._verification_command_argv(
        "UV_CACHE_DIR=/tmp/custom uv run pytest tests/test_governance_loop.py -q"
    )

    assert env_updates == {"UV_CACHE_DIR": "/tmp/custom"}
    assert argv == [str(venv_python), "-m", "pytest", "tests/test_governance_loop.py", "-q"]


def test_run_verification_commands_retries_pytest_after_negative_signal(governance_loop, monkeypatch, tmp_path: Path) -> None:
    calls: list[list[str]] = []
    outputs = [
        governance_loop.subprocess.CompletedProcess(
            [str(tmp_path / "python"), "-m", "pytest", "-q"],
            -9,
            stdout="============================= 2 passed in 0.12s =============================\n",
            stderr="",
        ),
        governance_loop.subprocess.CompletedProcess(
            [str(tmp_path / "python"), "-m", "pytest", "-q"],
            0,
            stdout="============================= 2 passed in 0.10s =============================\n",
            stderr="",
        ),
    ]

    monkeypatch.setattr(governance_loop, "_verification_command_argv", lambda command: ({}, [str(tmp_path / "python"), "-m", "pytest", "-q"]))

    def _fake_run(argv, **kwargs):
        calls.append(list(argv))
        return outputs.pop(0)

    monkeypatch.setattr(governance_loop.subprocess, "run", _fake_run)

    results, ok = governance_loop.run_verification_commands(
        commands=["uv run pytest -q"],
        round_dir=tmp_path / "round",
        dry_run=False,
    )

    assert ok is True
    assert len(calls) == 2
    assert results[0]["exit_code"] == 0


def test_persist_and_load_promotion_auto_repair_request(governance_loop, monkeypatch, tmp_path: Path) -> None:
    request_path = tmp_path / "promotion_auto_repair_request.json"
    stdout_path = tmp_path / "gate.stdout.log"
    stderr_path = tmp_path / "gate.stderr.log"
    stdout_path.write_text("gate stdout\n", encoding="utf-8")
    stderr_path.write_text("gate stderr\n", encoding="utf-8")
    monkeypatch.setenv(governance_loop.PROMOTION_AUTO_REPAIR_ENV_VAR, str(request_path))

    persisted_path = governance_loop._persist_promotion_auto_repair_request(
        reason="pre_promotion_gate_failed",
        detail="pre_promotion_gate_failed",
        round_index=3,
        runtime={
            "current_level": "manual_only",
            "remaining_promotion_gates": ["repo_landed_false", "head_not_pushed"],
            "next_slice": {
                "id": "L16.4",
                "title": "Structured contracts",
                "phase_id": "L16",
                "category": "manual",
                "execution_profile": "workflow_change",
            },
        },
        slice_execution_brief={"id": "L16.4"},
        verification_results=[
            {
                "command": "uv run python scripts/governance/run_datapulse_quick_test_gate.py",
                "stdout_path": str(stdout_path),
                "stderr_path": str(stderr_path),
                "exit_code": 1,
            }
        ],
        local_verification_commands=["uv run python scripts/governance/run_datapulse_quick_test_gate.py"],
    )

    assert persisted_path == request_path.resolve()
    payload = governance_loop.load_promotion_auto_repair_request()
    assert payload is not None
    assert payload["schema_version"] == governance_loop.PROMOTION_AUTO_REPAIR_REQUEST_SCHEMA
    assert payload["failed_command"] == "uv run python scripts/governance/run_datapulse_quick_test_gate.py"
    assert payload["round"] == 3
    assert payload["original_next_slice"]["id"] == "L16.4"
    assert "gate stdout" in payload["stdout_tail"]
    assert "gate stderr" in payload["stderr_tail"]

    governance_loop.clear_promotion_auto_repair_request()
    assert request_path.exists() is False


def test_resume_promotion_auto_repair_clears_request_on_success(governance_loop, monkeypatch, tmp_path: Path) -> None:
    request_path = tmp_path / "promotion_auto_repair_request.json"
    monkeypatch.setenv(governance_loop.PROMOTION_AUTO_REPAIR_ENV_VAR, str(request_path))
    request_path.write_text(
        json.dumps(
            {
                "schema_version": governance_loop.PROMOTION_AUTO_REPAIR_REQUEST_SCHEMA,
                "generated_at_utc": "2026-03-15T00:00:00Z",
                "reason": "pre_promotion_gate_failed",
                "detail": "pre_promotion_gate_failed",
                "round": 1,
                "failed_command": "uv run python scripts/governance/run_datapulse_quick_test_gate.py",
                "local_verification_commands": ["uv run python scripts/governance/run_datapulse_quick_test_gate.py"],
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    def _fake_run_verification_commands(*, commands, round_dir, dry_run):
        assert commands == ["uv run python scripts/governance/run_datapulse_quick_test_gate.py"]
        assert round_dir == tmp_path / "out" / "promotion-auto-repair-resume"
        assert dry_run is False
        return ([{"command": commands[0], "stdout_path": "stdout.log", "stderr_path": "stderr.log", "exit_code": 0}], True)

    monkeypatch.setattr(governance_loop, "run_verification_commands", _fake_run_verification_commands)

    ok = governance_loop.resume_promotion_auto_repair(output_dir=tmp_path / "out", dry_run=False)

    assert ok is True
    assert request_path.exists() is False


def test_resume_promotion_auto_repair_keeps_request_on_failure(governance_loop, monkeypatch, tmp_path: Path) -> None:
    request_path = tmp_path / "promotion_auto_repair_request.json"
    stdout_path = tmp_path / "resume.stdout.log"
    stderr_path = tmp_path / "resume.stderr.log"
    stdout_path.write_text("resume stdout\n", encoding="utf-8")
    stderr_path.write_text("resume stderr\n", encoding="utf-8")
    monkeypatch.setenv(governance_loop.PROMOTION_AUTO_REPAIR_ENV_VAR, str(request_path))
    request_path.write_text(
        json.dumps(
            {
                "schema_version": governance_loop.PROMOTION_AUTO_REPAIR_REQUEST_SCHEMA,
                "generated_at_utc": "2026-03-15T00:00:00Z",
                "reason": "pre_promotion_gate_failed",
                "detail": "pre_promotion_gate_failed",
                "round": 1,
                "failed_command": "uv run python scripts/governance/run_datapulse_quick_test_gate.py",
                "local_verification_commands": ["uv run python scripts/governance/run_datapulse_quick_test_gate.py"],
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    def _fake_run_verification_commands(*, commands, round_dir, dry_run):
        assert dry_run is False
        return (
            [
                {
                    "command": commands[0],
                    "stdout_path": str(stdout_path),
                    "stderr_path": str(stderr_path),
                    "exit_code": 1,
                }
            ],
            False,
        )

    monkeypatch.setattr(governance_loop, "run_verification_commands", _fake_run_verification_commands)

    ok = governance_loop.resume_promotion_auto_repair(output_dir=tmp_path / "out", dry_run=False)

    assert ok is False
    payload = json.loads(request_path.read_text(encoding="utf-8"))
    assert payload["reason"] == "promotion_auto_repair_resume_failed"
    assert payload["failed_command"] == "uv run python scripts/governance/run_datapulse_quick_test_gate.py"
    assert "resume stdout" in payload["stdout_tail"]


def test_maybe_auto_promote_persists_repair_request_on_pre_promotion_gate_failure(
    governance_loop, monkeypatch, tmp_path: Path
) -> None:
    request_path = tmp_path / "promotion_auto_repair_request.json"
    monkeypatch.setenv(governance_loop.PROMOTION_AUTO_REPAIR_ENV_VAR, str(request_path))
    stdout_path = tmp_path / "gate.stdout.log"
    stderr_path = tmp_path / "gate.stderr.log"
    stdout_path.write_text("gate stdout\n", encoding="utf-8")
    stderr_path.write_text("gate stderr\n", encoding="utf-8")
    monkeypatch.setattr(governance_loop, "load_plan", lambda path: {})
    monkeypatch.setattr(
        governance_loop,
        "run_pre_promotion_gate",
        lambda **kwargs: (
            [
                {
                    "command": "uv run python scripts/governance/run_datapulse_quick_test_gate.py",
                    "stdout_path": str(stdout_path),
                    "stderr_path": str(stderr_path),
                    "exit_code": 1,
                }
            ],
            False,
        ),
    )

    runtime = {
        "status": "blocked",
        "reason": "next_slice_blocked",
        "effective_blocking_facts": ["workspace_dirty"],
        "remaining_promotion_gates": ["workspace_dirty", "repo_landed_false", "head_not_pushed"],
        "current_level": "manual_only",
        "next_slice": {
            "id": "L16.4",
            "title": "Structured contracts",
            "phase_id": "L16",
            "category": "manual",
            "execution_profile": "workflow_change",
        },
    }

    with pytest.raises(governance_loop.PromotionExecutionError) as exc_info:
        governance_loop.maybe_auto_promote(
            runtime=runtime,
            slice_execution_brief={"id": "L16.4"},
            round_index=1,
            output_dir=tmp_path / "out",
            baseline_dirty_paths=["datapulse/reader.py"],
            promotion_mode="auto",
            allow_existing_dirty_worktree=True,
            plan_path=tmp_path / "plan.json",
            catalog_path=tmp_path / "catalog.json",
            bundle_dir=tmp_path / "bundle",
            tracked_snapshots=False,
            code_landing_status_output=tmp_path / "code_landing_status.json",
            project_loop_state_output=tmp_path / "project_loop_state.json",
            push_remote="origin",
            poll_interval_seconds=1,
            ci_timeout_seconds=1,
            pre_promotion_gate_command="uv run python scripts/governance/run_datapulse_quick_test_gate.py",
            dry_run=False,
        )

    assert exc_info.value.reason == "pre_promotion_gate_failed"
    payload = json.loads(request_path.read_text(encoding="utf-8"))
    assert payload["failed_command"] == "uv run python scripts/governance/run_datapulse_quick_test_gate.py"
    assert payload["original_next_slice"]["id"] == "L16.4"
