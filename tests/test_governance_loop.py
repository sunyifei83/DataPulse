from __future__ import annotations

import importlib
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
