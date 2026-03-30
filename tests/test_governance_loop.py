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


@pytest.fixture(scope="module")
def loop_contracts():
    if str(GOVERNANCE_SCRIPTS_DIR) not in sys.path:
        sys.path.insert(0, str(GOVERNANCE_SCRIPTS_DIR))
    return importlib.import_module("datapulse_loop_contracts")


@pytest.fixture(scope="module")
def governance_paths():
    return importlib.import_module("datapulse.governance_paths")


@pytest.fixture(scope="module")
def evidence_bundle_module():
    if str(GOVERNANCE_SCRIPTS_DIR) not in sys.path:
        sys.path.insert(0, str(GOVERNANCE_SCRIPTS_DIR))
    return importlib.import_module("export_datapulse_evidence_bundle")


@pytest.fixture(scope="module")
def structured_bundle_module():
    if str(GOVERNANCE_SCRIPTS_DIR) not in sys.path:
        sys.path.insert(0, str(GOVERNANCE_SCRIPTS_DIR))
    return importlib.import_module("export_datapulse_structured_release_bundle")


@pytest.fixture(scope="module")
def ha_delivery_facts_module():
    if str(GOVERNANCE_SCRIPTS_DIR) not in sys.path:
        sys.path.insert(0, str(GOVERNANCE_SCRIPTS_DIR))
    return importlib.import_module("export_datapulse_ha_delivery_facts")


@pytest.fixture(scope="module")
def release_window_attestation_module():
    if str(GOVERNANCE_SCRIPTS_DIR) not in sys.path:
        sys.path.insert(0, str(GOVERNANCE_SCRIPTS_DIR))
    return importlib.import_module("export_datapulse_release_window_attestation")


def _stub_release_gate_baseline(loop_contracts, monkeypatch, *, head: str = "abc123", branch: str = "main") -> None:
    monkeypatch.setattr(loop_contracts, "repo_workspace_clean", lambda: (True, []))
    monkeypatch.setattr(loop_contracts, "ci_docs_only_skip_active", lambda workspace_clean, dirty_entries: (False, []))
    monkeypatch.setattr(
        loop_contracts,
        "git_output",
        lambda *args: head
        if args == ("rev-parse", "HEAD")
        else branch
        if args == ("branch", "--show-current")
        else "",
    )
    monkeypatch.setattr(loop_contracts, "current_head_published", lambda head_sha: (True, "origin/main", head_sha))
    monkeypatch.setattr(loop_contracts, "latest_artifact_file", lambda filename: None)
    monkeypatch.setattr(loop_contracts, "parse_quick_test_gate", lambda path=None: None)
    monkeypatch.setattr(loop_contracts, "structured_release_bundle_available", lambda: True)
    monkeypatch.setattr(loop_contracts, "workflow_dispatch_entrypoints", lambda: [".github/workflows/release.yml"])
    monkeypatch.setattr(loop_contracts, "workflow_push_tag_release_enabled", lambda workflow_path: False)
    monkeypatch.setattr(loop_contracts, "ci_paths_ignore_configured", lambda: False)
    monkeypatch.setattr(
        loop_contracts,
        "latest_workflow_run_for_head",
        lambda workflow, *, head_sha, branch: {
            "status": "completed",
            "conclusion": "success",
            "head_sha": head_sha,
            "head_branch": branch,
        },
    )


def test_governance_path_read_prefers_configured_root_before_canonical(governance_paths, tmp_path: Path) -> None:
    configured_root = tmp_path / "configured"
    canonical_root = tmp_path / "artifacts" / "governance" / "snapshots"
    legacy_root = tmp_path / "out" / "governance"
    configured_root.mkdir(parents=True, exist_ok=True)
    canonical_root.mkdir(parents=True, exist_ok=True)
    legacy_root.mkdir(parents=True, exist_ok=True)
    (configured_root / "activation_plan.draft.json").write_text("{}", encoding="utf-8")
    (canonical_root / "activation_plan.draft.json").write_text('{"canonical": true}', encoding="utf-8")
    (legacy_root / "activation_plan.draft.json").write_text('{"legacy": true}', encoding="utf-8")

    path = governance_paths.read_path(
        governance_paths.GOVERNANCE_SNAPSHOT_ROOT,
        "activation_plan.draft.json",
        repo_root=tmp_path,
        environ={"DATAPULSE_GOVERNANCE_SNAPSHOT_ROOT": str(configured_root)},
    )

    assert path == (configured_root / "activation_plan.draft.json").resolve()


def test_governance_path_read_falls_back_to_legacy_when_canonical_missing(governance_paths, tmp_path: Path) -> None:
    legacy_root = tmp_path / "out" / "governance"
    legacy_root.mkdir(parents=True, exist_ok=True)
    legacy_file = legacy_root / "activation_preview.draft.json"
    legacy_file.write_text("{}", encoding="utf-8")

    path = governance_paths.read_path(
        governance_paths.GOVERNANCE_SNAPSHOT_ROOT,
        "activation_preview.draft.json",
        repo_root=tmp_path,
    )

    assert path == legacy_file.resolve()


def test_governance_path_write_targets_canonical_root_not_legacy(governance_paths, tmp_path: Path) -> None:
    path = governance_paths.write_path(
        governance_paths.EVIDENCE_BUNDLE_ROOT,
        "adapter_bundle_manifest.draft.json",
        repo_root=tmp_path,
    )

    assert path == (tmp_path / "artifacts/governance/release_bundle/adapter_bundle_manifest.draft.json").resolve()


def test_refresh_tracked_governance_on_stop_runs_for_terminal_stop(governance_loop, monkeypatch, tmp_path: Path) -> None:
    captured: dict[str, Path] = {}

    def _fake_refresh(bundle_dir: Path, *, plan_path: Path) -> dict[str, str]:
        captured["bundle_dir"] = bundle_dir
        captured["plan_path"] = plan_path
        return {"code_landing_status": "out/governance/code_landing_status.draft.json"}

    monkeypatch.setattr(governance_loop, "refresh_governance_snapshots", _fake_refresh)

    result = governance_loop.refresh_stop_outputs_on_terminal_state(
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

    result = governance_loop.refresh_stop_outputs_on_terminal_state(
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

    dry_run_result = governance_loop.refresh_stop_outputs_on_terminal_state(
        runtime={"status": "stopped"},
        plan_path=tmp_path / "plan.json",
        bundle_dir=tmp_path / "bundle",
        enabled=True,
        dry_run=True,
    )
    ready_result = governance_loop.refresh_stop_outputs_on_terminal_state(
        runtime={"status": "ready"},
        plan_path=tmp_path / "plan.json",
        bundle_dir=tmp_path / "bundle",
        enabled=True,
        dry_run=False,
    )

    assert dry_run_result == {}
    assert ready_result == {}


def test_repo_workspace_clean_ignores_codex_loop_output_prefix(loop_contracts, monkeypatch) -> None:
    monkeypatch.setattr(
        loop_contracts,
        "git_output",
        lambda *args: " M out/codex_blueprint_loop/round-02/command.json\n",
    )

    clean, entries = loop_contracts.repo_workspace_clean()

    assert clean is True
    assert entries == []


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


def test_build_code_landing_status_blocks_missing_release_window_attestation(loop_contracts, monkeypatch, tmp_path: Path) -> None:
    _stub_release_gate_baseline(loop_contracts, monkeypatch)
    monkeypatch.setattr(loop_contracts, "parse_release_window_attestation", lambda path=None: None)
    expected_path = (tmp_path / "artifacts/governance/snapshots/datapulse_release_window_attestation.draft.json").resolve()
    monkeypatch.setattr(loop_contracts, "resolve_governance_read_path", lambda *args, **kwargs: expected_path)

    payload = loop_contracts.build_code_landing_status()

    assert "release_window_attestation_missing" in payload["gate_groups"]["release_governance"]
    assert payload["release"]["primary_same_window_truth"] == str(expected_path)
    assert payload["release"]["release_window_attestation"]["status"] == "missing"
    assert payload["release"]["release_window_attestation"]["runtime_closure_complete"] is False


def test_build_code_landing_status_accepts_verified_fail_closed_attestation(loop_contracts, monkeypatch) -> None:
    _stub_release_gate_baseline(loop_contracts, monkeypatch)
    monkeypatch.setattr(
        loop_contracts,
        "parse_release_window_attestation",
        lambda path=None: {
            "path": "out/governance/datapulse_release_window_attestation.draft.json",
            "schema_version": "datapulse_release_window_attestation.v1",
            "generated_at_utc": "2026-03-17T07:00:00Z",
            "window_id": "dp-release-window-20260317T070000Z-abc123",
            "git_head": "abc123",
            "attestation_status": "attested",
            "blocking_reasons": [],
            "same_window": {"proven": True},
            "freshness": {"all_sources_fresh": True, "sources": []},
            "runtime_hit_evidence": {
                "required_surfaces": [
                    {
                        "surface": "mission_suggest",
                        "observed_evidence_status": "verified",
                    },
                    {
                        "surface": "triage_assist",
                        "observed_evidence_status": "verified",
                    },
                    {
                        "surface": "claim_draft",
                        "observed_evidence_status": "verified",
                    },
                    {
                        "surface": "report_draft",
                        "observed_evidence_status": "verified_fail_closed",
                    },
                    {
                        "surface": "delivery_summary",
                        "observed_evidence_status": "verified",
                    },
                ]
            },
        },
    )

    payload = loop_contracts.build_code_landing_status()

    assert payload["gate_groups"]["release_governance"] == []
    assert payload["release"]["release_window_attestation"]["status"] == "attested"
    assert payload["release"]["release_window_attestation"]["runtime_closure_complete"] is True
    assert payload["release"]["release_window_attestation"]["same_window_proven"] is True


def test_build_code_landing_status_rejects_cross_head_attestation(loop_contracts, monkeypatch) -> None:
    _stub_release_gate_baseline(loop_contracts, monkeypatch, head="current-head")
    monkeypatch.setattr(
        loop_contracts,
        "parse_release_window_attestation",
        lambda path=None: {
            "path": "out/governance/datapulse_release_window_attestation.draft.json",
            "schema_version": "datapulse_release_window_attestation.v1",
            "generated_at_utc": "2026-03-17T07:00:00Z",
            "window_id": "dp-release-window-20260317T070000Z-other-head",
            "git_head": "other-head",
            "attestation_status": "attested",
            "blocking_reasons": [],
            "same_window": {"proven": True},
            "freshness": {"all_sources_fresh": True, "sources": []},
            "runtime_hit_evidence": {
                "required_surfaces": [
                    {
                        "surface": "mission_suggest",
                        "observed_evidence_status": "verified",
                    },
                    {
                        "surface": "triage_assist",
                        "observed_evidence_status": "verified",
                    },
                    {
                        "surface": "claim_draft",
                        "observed_evidence_status": "verified",
                    },
                    {
                        "surface": "report_draft",
                        "observed_evidence_status": "verified_fail_closed",
                    },
                    {
                        "surface": "delivery_summary",
                        "observed_evidence_status": "verified",
                    },
                ]
            },
        },
    )

    payload = loop_contracts.build_code_landing_status()

    assert "release_window_attestation_cross_head" in payload["gate_groups"]["release_governance"]
    assert payload["release"]["release_window_attestation"]["status"] == "cross_head"
    assert payload["release"]["release_window_attestation"]["current_head_match"] is False


def test_build_code_landing_status_rejects_stale_attestation(loop_contracts, monkeypatch) -> None:
    _stub_release_gate_baseline(loop_contracts, monkeypatch)
    monkeypatch.setattr(
        loop_contracts,
        "parse_release_window_attestation",
        lambda path=None: {
            "path": "out/governance/datapulse_release_window_attestation.draft.json",
            "schema_version": "datapulse_release_window_attestation.v1",
            "generated_at_utc": "2026-03-17T06:30:00Z",
            "window_id": "dp-release-window-20260317T063000Z-abc123",
            "git_head": "abc123",
            "attestation_status": "blocked",
            "blocking_reasons": ["source_stale"],
            "same_window": {"proven": False},
            "freshness": {"all_sources_fresh": False, "sources": []},
            "runtime_hit_evidence": {
                "required_surfaces": [
                    {
                        "surface": "mission_suggest",
                        "observed_evidence_status": "verified",
                    },
                    {
                        "surface": "triage_assist",
                        "observed_evidence_status": "verified",
                    },
                    {
                        "surface": "claim_draft",
                        "observed_evidence_status": "verified",
                    },
                    {
                        "surface": "report_draft",
                        "observed_evidence_status": "verified_fail_closed",
                    },
                    {
                        "surface": "delivery_summary",
                        "observed_evidence_status": "verified",
                    },
                ]
            },
        },
    )

    payload = loop_contracts.build_code_landing_status()

    assert "release_window_attestation_stale" in payload["gate_groups"]["release_governance"]
    assert "release_window_attestation_not_attested" in payload["gate_groups"]["release_governance"]


def test_build_code_landing_status_uses_explicit_attestation_path(loop_contracts, monkeypatch, tmp_path: Path) -> None:
    _stub_release_gate_baseline(loop_contracts, monkeypatch)
    captured: dict[str, Path | None] = {"path": None}

    def _fake_parse_release_window_attestation(path=None):
        captured["path"] = path
        return {
            "path": str(path),
            "schema_version": "datapulse_release_window_attestation.v1",
            "generated_at_utc": "2026-03-17T07:00:00Z",
            "window_id": "dp-release-window-20260317T070000Z-abc123",
            "git_head": "abc123",
            "attestation_status": "attested",
            "blocking_reasons": [],
            "same_window": {"proven": True},
            "freshness": {"all_sources_fresh": True, "sources": []},
            "runtime_hit_evidence": {
                "required_surfaces": [
                    {"surface": "mission_suggest", "observed_evidence_status": "verified"},
                    {"surface": "triage_assist", "observed_evidence_status": "verified"},
                    {"surface": "claim_draft", "observed_evidence_status": "verified"},
                    {"surface": "report_draft", "observed_evidence_status": "verified_fail_closed"},
                    {"surface": "delivery_summary", "observed_evidence_status": "verified"},
                ]
            },
        }

    monkeypatch.setattr(loop_contracts, "parse_release_window_attestation", _fake_parse_release_window_attestation)

    attestation_path = tmp_path / "bundle-attestation.json"
    payload = loop_contracts.build_code_landing_status(release_window_attestation_path=attestation_path)

    assert captured["path"] == attestation_path.resolve()
    assert payload["release"]["primary_same_window_truth"] == str(attestation_path.resolve())
    assert payload["evidence_paths"]["release_window_attestation"] == str(attestation_path.resolve())
    assert payload["release"]["truth_sources"][0] == str(attestation_path.resolve())


def test_build_release_readiness_fact_normalizes_environment_specific_runtime_lines(
    ha_delivery_facts_module, monkeypatch, tmp_path: Path
) -> None:
    state_path = tmp_path / "emergency_state.json"
    state_path.write_text("{}", encoding="utf-8")
    monkeypatch.setattr(
        ha_delivery_facts_module,
        "parse_emergency_state",
        lambda path: {
            "run_id": "run-1",
            "conclusion": "GREEN",
            "stop": False,
            "first_trigger": "",
        },
    )
    monkeypatch.setattr(
        ha_delivery_facts_module.subprocess,
        "run",
        lambda *args, **kwargs: ha_delivery_facts_module.subprocess.CompletedProcess(
            args[0],
            0,
            stdout=(
                "[PASS] release python runtime available: uv run --python 3.10 python\n"
                "[PASS] release build path available: uv run --python 3.10 --with build python -m build\n"
                "release readiness: pass=2 fail=0\n"
            ),
            stderr="",
        ),
    )

    payload = ha_delivery_facts_module.build_release_readiness_fact(emergency_state_path=state_path)

    assert payload["observation"]["passed_checks"] == [
        "release python runtime available: python>=3.10",
        "release build path available",
    ]
    assert payload["observation"]["stdout_tail"] == [
        "[PASS] release python runtime available: python>=3.10",
        "[PASS] release build path available",
        "release readiness: pass=2 fail=0",
    ]


def test_evidence_bundle_rebuilds_landing_status_from_generated_attestation(
    evidence_bundle_module, monkeypatch, tmp_path: Path
) -> None:
    out_dir = tmp_path / "bundle"
    captured: dict[str, object] = {}
    commands: list[list[str]] = []

    monkeypatch.setattr(
        evidence_bundle_module,
        "parse_args",
        lambda: evidence_bundle_module.argparse.Namespace(
            plan=tmp_path / "plan.json",
            tag="",
            notes_file=Path("RELEASE_NOTES.md"),
            out_dir=out_dir,
            bundle_dir=out_dir,
            runtime_bundle_dir=tmp_path / "runtime-bundle",
            probe_ha_readiness=False,
            stdout=False,
        ),
    )
    monkeypatch.setattr(evidence_bundle_module, "load_plan", lambda path: {"project": "DataPulse"})
    monkeypatch.setattr(evidence_bundle_module, "detect_tag", lambda tag: "v0.8.0")
    monkeypatch.setattr(evidence_bundle_module, "build_manifest", lambda *args, **kwargs: {"manifest": True})
    monkeypatch.setattr(evidence_bundle_module, "build_project_loop_state", lambda plan, status: {"current_level": "ci_proven"})
    monkeypatch.setattr(evidence_bundle_module, "write_json", lambda path, payload: None)
    monkeypatch.setattr(evidence_bundle_module, "current_python_command", lambda: ["python"])

    def _fake_build_code_landing_status(*, release_window_attestation_path=None):
        captured["attestation_path"] = release_window_attestation_path
        return {"headline_summary": {"current_level": "ci_proven"}}

    monkeypatch.setattr(evidence_bundle_module, "build_code_landing_status", _fake_build_code_landing_status)

    def _fake_run(command, check=True):
        commands.append(list(command))
        return evidence_bundle_module.subprocess.CompletedProcess(command, 0)

    monkeypatch.setattr(evidence_bundle_module.subprocess, "run", _fake_run)

    assert evidence_bundle_module.main() == 0
    assert captured["attestation_path"] == (out_dir / "datapulse_release_window_attestation.draft.json").resolve()
    assert any(
        "--runtime-hit-json" in command
        for command in commands
        if any(str(item).endswith("export_datapulse_release_sidecar.py") for item in command)
    )
    assert any(
        "--bundle-dir" in command and str(tmp_path / "runtime-bundle") in command
        for command in commands
        if any(str(item).endswith("export_datapulse_surface_runtime_hit_evidence.py") for item in command)
    )
    assert any(
        "--bundle-dir" in command and str(out_dir) in command
        for command in commands
        if any(str(item).endswith("export_datapulse_release_window_attestation.py") for item in command)
    )
    assert any(
        "--release-window-attestation" in command
        for command in commands
        if any(str(item).endswith("export_datapulse_ha_delivery_landing.py") for item in command)
    )


def test_structured_bundle_refreshes_adapter_and_modelbus_after_evidence_export(
    structured_bundle_module, monkeypatch, tmp_path: Path
) -> None:
    out_dir = tmp_path / "bundle"
    commands: list[list[str]] = []

    monkeypatch.setattr(
        structured_bundle_module,
        "parse_args",
        lambda: structured_bundle_module.argparse.Namespace(
            plan=tmp_path / "plan.json",
            out_dir=out_dir,
            runtime_bundle_dir=tmp_path / "runtime-bundle",
            tag="",
            notes_file=Path("RELEASE_NOTES.md"),
            probe_ha_readiness=True,
            stdout=False,
        ),
    )
    monkeypatch.setattr(structured_bundle_module, "load_plan", lambda path: {"activation": {}})
    monkeypatch.setattr(
        structured_bundle_module,
        "copy_runtime_bundle_files",
        lambda runtime_bundle_dir, bundle_dir: [
            "bundle_manifest.json",
            "surface_admission.json",
            "bridge_config.json",
            "release_status.json",
        ],
    )
    monkeypatch.setattr(structured_bundle_module, "build_manifest", lambda *args, **kwargs: {"manifest": True})
    monkeypatch.setattr(structured_bundle_module, "write_json", lambda path, payload: None)
    monkeypatch.setattr(structured_bundle_module, "current_python_command", lambda: ["python"])

    def _fake_run(command, cwd=None, check=True):
        commands.append(list(command))
        return structured_bundle_module.subprocess.CompletedProcess(command, 0)

    monkeypatch.setattr(structured_bundle_module.subprocess, "run", _fake_run)

    assert structured_bundle_module.main() == 0
    assert [command[1] for command in commands] == [
        "scripts/governance/export_datapulse_evidence_bundle.py",
        "scripts/governance/export_datapulse_loop_adapter_bundle.py",
    ]
    assert "--runtime-bundle-dir" in commands[0]
    assert "--release-window-attestation" in commands[1]


def test_release_window_attestation_decouples_stable_runtime_bundle_from_same_window_freshness(
    release_window_attestation_module, monkeypatch, tmp_path: Path
) -> None:
    scripts_dir = tmp_path / "scripts" / "governance"
    scripts_dir.mkdir(parents=True, exist_ok=True)
    (scripts_dir / "validate_governance_loop_bundle_draft.py").write_text("print('ok')\n", encoding="utf-8")
    (scripts_dir / "export_datapulse_surface_runtime_hit_evidence.py").write_text("print('ok')\n", encoding="utf-8")
    bundle_dir = tmp_path / "artifacts" / "governance" / "release_bundle"
    bundle_dir.mkdir(parents=True, exist_ok=True)
    runtime_bundle_dir = tmp_path / "config" / "modelbus" / "datapulse"
    runtime_bundle_dir.mkdir(parents=True, exist_ok=True)
    runtime_hit_path = tmp_path / "artifacts" / "governance" / "snapshots" / "datapulse_surface_runtime_hit_evidence.draft.json"
    runtime_hit_path.parent.mkdir(parents=True, exist_ok=True)
    release_sidecar_path = tmp_path / "artifacts" / "governance" / "snapshots" / "release_sidecar.draft.json"
    output_path = tmp_path / "artifacts" / "governance" / "snapshots" / "datapulse_release_window_attestation.draft.json"

    (bundle_dir / "structured_release_bundle_manifest.draft.json").write_text(
        json.dumps(
            {
                "schema_version": "structured_release_bundle_manifest.v1",
                "generated_at_utc": "2026-03-30T04:29:24Z",
                "runtime_bundle": {
                    "source_dir": str(runtime_bundle_dir.resolve()),
                    "files_copied": [
                        "bundle_manifest.json",
                        "surface_admission.json",
                        "bridge_config.json",
                        "release_status.json",
                    ],
                },
                "files": [
                    "datapulse_surface_runtime_hit_evidence.draft.json",
                    "release_sidecar.draft.json",
                ],
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    (bundle_dir / "bundle_manifest.json").write_text(
        json.dumps(
            {
                "schema": "modelbus.consumer_bundle_manifest.v1",
                "generated_at_utc": "2026-03-29T10:04:27Z",
                "bundle_id": "datapulse.ai_surface_bus",
                "consumer_id": "datapulse",
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    (bundle_dir / "adapter_bundle_manifest.draft.json").write_text("{}\n", encoding="utf-8")
    runtime_hit_path.write_text(
        json.dumps(
            {
                "schema_version": "datapulse_surface_runtime_hit_evidence.v1",
                "generated_at_utc": "2026-03-30T04:29:24Z",
                "bundle_default": {
                    "strategy": "bundle_first",
                    "runtime_bundle_dir": "config/modelbus/datapulse",
                },
                "closure": {
                    "replay_entrypoint": "python3 scripts/governance/export_datapulse_surface_runtime_hit_evidence.py --bundle-dir config/modelbus/datapulse",
                    "required_runtime_hit_targets": [
                        {
                            "surface": "mission_suggest",
                            "expected_evidence_status": "verified",
                            "release_scope": "shadow",
                        },
                        {
                            "surface": "triage_assist",
                            "expected_evidence_status": "verified",
                            "release_scope": "shadow",
                        },
                        {
                            "surface": "claim_draft",
                            "expected_evidence_status": "verified",
                            "release_scope": "shadow",
                        },
                        {
                            "surface": "report_draft",
                            "expected_evidence_status": "verified_fail_closed",
                            "release_scope": "required",
                        },
                        {
                            "surface": "delivery_summary",
                            "expected_evidence_status": "verified",
                            "release_scope": "shadow",
                        },
                    ],
                },
                "surfaces": [
                    {
                        "surface": "mission_suggest",
                        "evidence_status": "verified",
                        "request_id": "mission-1",
                        "served_by_alias": "dp.mission.suggest",
                        "contract_id": "datapulse_ai_watch_suggestion.v1",
                        "fail_closed": False,
                    },
                    {
                        "surface": "triage_assist",
                        "evidence_status": "verified",
                        "request_id": "triage-1",
                        "served_by_alias": "dp.triage.assist",
                        "contract_id": "datapulse_ai_triage_explain.v1",
                        "fail_closed": False,
                    },
                    {
                        "surface": "claim_draft",
                        "evidence_status": "verified",
                        "request_id": "claim-1",
                        "served_by_alias": "dp.claim.draft",
                        "contract_id": "datapulse_ai_claim_draft.v1",
                        "fail_closed": False,
                    },
                    {
                        "surface": "report_draft",
                        "evidence_status": "verified_fail_closed",
                        "request_id": "report-1",
                        "served_by_alias": "dp.report.draft",
                        "contract_id": "",
                        "fail_closed": True,
                    },
                    {
                        "surface": "delivery_summary",
                        "evidence_status": "verified",
                        "request_id": "delivery-1",
                        "served_by_alias": "dp.delivery.summary",
                        "contract_id": "datapulse_ai_delivery_summary.v1",
                        "fail_closed": False,
                    },
                ],
                "release_level_prerequisites": {
                    "bundle_first_default_ready": True,
                    "shadow_change_prerequisites_met": True,
                    "required_change_prerequisites_met": True,
                    "promotion_discussion_allowed": True,
                },
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    release_sidecar_path.write_text(
        json.dumps(
            {
                "schema_version": "release_sidecar.v1",
                "generated_at_utc": "2026-03-30T04:29:33Z",
                "release": {"tag": "v0.8.0"},
                "git": {
                    "head": "3b2b5add9073be37d244a586e30ff71bb3abba59",
                    "workspace_clean": True,
                },
                "governed_ai_release_readiness": {
                    "runtime_hit_evidence_available": True,
                    "required_change_prerequisites_met": True,
                    "promotion_discussion_allowed": True,
                },
                "promotion_readiness": {
                    "structured_release_bundle_available": True,
                    "reasons": [],
                },
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(release_window_attestation_module, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(release_window_attestation_module, "utc_now", lambda: "2026-03-30T04:29:40Z")
    monkeypatch.setattr(
        release_window_attestation_module,
        "parse_args",
        lambda: release_window_attestation_module.argparse.Namespace(
            bundle_dir=bundle_dir,
            runtime_hit_json=runtime_hit_path,
            release_sidecar_json=release_sidecar_path,
            output=output_path,
            max_source_age_seconds=900,
            max_inter_source_skew_seconds=300,
            stdout=False,
        ),
    )

    assert release_window_attestation_module.main() == 0
    payload = json.loads(output_path.read_text(encoding="utf-8"))

    assert payload["attestation_status"] == "attested"
    assert payload["blocking_reasons"] == []
    assert payload["same_window"]["same_bundle_dir_required"] is False
    assert payload["same_window"]["same_runtime_bundle_required"] is True
    assert payload["runtime_hit_evidence"]["runtime_bundle_dir"] == str(runtime_bundle_dir.resolve())
    assert payload["bundle_identity"]["runtime_bundle_source_dir"] == str(runtime_bundle_dir.resolve())
    assert {row["source"] for row in payload["freshness"]["sources"]} == {
        "structured_release_bundle_manifest",
        "runtime_hit_evidence",
        "release_sidecar",
    }


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
    monkeypatch.setattr(governance_loop, "workspace_status_lines", lambda: [" M datapulse/reader.py"])

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
