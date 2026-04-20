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
def consumer_bundle_module():
    if str(GOVERNANCE_SCRIPTS_DIR) not in sys.path:
        sys.path.insert(0, str(GOVERNANCE_SCRIPTS_DIR))
    return importlib.import_module("export_datapulse_modelbus_consumer_bundle")


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


def test_active_overlay_truth_contract_matches_resolved_plan_and_tracked_loop_snapshot(loop_contracts) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    overlay_path = repo_root / "docs/governance/datapulse-blueprint-plan.json"
    base_path = repo_root / "docs/governance/datapulse-blueprint-plan.draft.json"
    loop_snapshot_path = repo_root / "artifacts/governance/snapshots/project_specific_loop_state.draft.json"

    overlay = json.loads(overlay_path.read_text(encoding="utf-8"))
    truth_contract = dict(overlay.get("truth_contract", {}))
    canonical_phase_truth = dict(truth_contract.get("canonical_phase_truth", {}))
    derived_execution_truth = dict(truth_contract.get("derived_execution_truth", {}))
    resolved_plan = loop_contracts.load_plan(overlay_path)
    resolved_status = resolved_plan.get("status")

    assert overlay.get("base_plan") == "docs/governance/datapulse-blueprint-plan.draft.json"
    assert overlay.get("status") == resolved_status
    assert resolved_status in {"in_progress", "completed"}
    assert truth_contract.get("overlay_role") == "active_entrypoint_and_activation_policy"
    assert truth_contract.get("resolved_plan_semantics") == "deep_merge_overlay_onto_base_plan"
    assert canonical_phase_truth.get("path") == "docs/governance/datapulse-blueprint-plan.draft.json"
    assert derived_execution_truth.get("path") == "artifacts/governance/snapshots/project_specific_loop_state.draft.json"

    expected_completed_slices = [
        item.get("id", "")
        for phase in resolved_plan.get("phases", [])
        for item in phase.get("slices", [])
        if item.get("status") == "completed"
    ]

    assert resolved_plan.get("_base_plan_path") == str(base_path.resolve())
    assert resolved_status == overlay.get("status")
    recommended_next_slice = dict(resolved_plan.get("recommended_next_slice", {}))
    assert recommended_next_slice.get("id")
    assert recommended_next_slice.get("title")

    resolved_plan["_source_path"] = str(overlay_path.resolve())
    landing_status = {
        "project": "DataPulse",
        "workspace": {
            "clean": True,
        },
        "promotion_levels": {
            "repo_landed": {
                "satisfied": True,
                "reasons": [],
            },
            "ci_proven": {
                "satisfied": True,
                "reasons": [],
            },
        },
        "gate_groups": {
            "release_governance": [],
        },
    }

    loop_snapshot = loop_contracts.build_project_loop_state(resolved_plan, landing_status)

    assert loop_snapshot.get("source_plan") == "docs/governance/datapulse-blueprint-plan.json"
    assert loop_snapshot.get("completed_slices") == expected_completed_slices
    assert loop_snapshot.get("next_slice", {}).get("id") == recommended_next_slice.get("id")
    assert loop_snapshot.get("remaining_promotion_gates") == []
    if recommended_next_slice.get("id") == "no-open-slice":
        assert loop_snapshot.get("stop_reason_if_run_now") == "loop_complete"
    else:
        assert loop_snapshot.get("flow_control", {}).get("status_if_run_now") == "ready_waiting_manual_handoff"
        assert loop_snapshot.get("flow_control", {}).get("reason_if_run_now") == "manual_promotion_mode"
        assert loop_snapshot.get("stop_reason_if_run_now") == ""

    if loop_snapshot_path.exists():
        persisted_snapshot = json.loads(loop_snapshot_path.read_text(encoding="utf-8"))
        if persisted_snapshot.get("source_plan") == loop_snapshot.get("source_plan"):
            assert persisted_snapshot.get("completed_slices") == loop_snapshot.get("completed_slices")
            assert persisted_snapshot.get("next_slice", {}).get("id") == loop_snapshot.get("next_slice", {}).get("id")
            assert isinstance(persisted_snapshot.get("remaining_promotion_gates"), list)
            assert persisted_snapshot.get("stop_reason_if_run_now") == loop_snapshot.get("stop_reason_if_run_now")


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


def test_modelbus_consumer_bundle_defaults_admission_output_to_governance_snapshots(
    consumer_bundle_module, monkeypatch, tmp_path: Path
) -> None:
    subscriptions_path = tmp_path / "subscriptions.json"
    subscriptions_path.write_text('{"surfaces": []}', encoding="utf-8")
    output_dir = tmp_path / "config" / "modelbus" / "datapulse"
    admission_output = tmp_path / "artifacts" / "governance" / "snapshots" / "datapulse-ai-surface-admission.example.json"
    captured_paths: list[Path] = []

    monkeypatch.setattr(
        consumer_bundle_module,
        "parse_args",
        lambda: type(
            "Args",
            (),
            {
                "subscriptions": subscriptions_path,
                "output_dir": output_dir,
                "admission_output": None,
                "project_loop_state_json": None,
                "stdout": False,
            },
        )(),
    )
    monkeypatch.setattr(consumer_bundle_module, "DEFAULT_ADMISSION_OUTPUT_PATH", admission_output)
    monkeypatch.setattr(consumer_bundle_module, "read_json", lambda path: {"surfaces": []})
    monkeypatch.setattr(consumer_bundle_module, "build_admission_payload", lambda subscriptions, path: {"surface_admissions": []})
    monkeypatch.setattr(consumer_bundle_module, "load_release_level", lambda path=None: "ci_proven")
    monkeypatch.setattr(consumer_bundle_module, "write_json", lambda path, payload: captured_paths.append(Path(path)))

    rc = consumer_bundle_module.main()

    assert rc == 0
    assert admission_output in captured_paths
    assert output_dir / "datapulse-ai-surface-admission.example.json" not in captured_paths


def test_modelbus_consumer_bundle_skips_rewrite_when_only_generated_at_changes(
    consumer_bundle_module, monkeypatch, tmp_path: Path
) -> None:
    subscriptions = {
        "surfaces": [
            {
                "surface": "mission_suggest",
                "candidate_subscriptions": [{"alias": "dp.mission.suggest"}],
            }
        ]
    }
    output_dir = tmp_path / "config" / "modelbus" / "datapulse"
    admission_output = tmp_path / "artifacts" / "governance" / "snapshots" / "datapulse-ai-surface-admission.example.json"
    subscriptions_path = tmp_path / "subscriptions.json"
    subscriptions_path.write_text(json.dumps(subscriptions), encoding="utf-8")

    def _admission_payload() -> dict[str, object]:
        return {
            "schema_version": "datapulse_ai_surface_admission.v1",
            "generated_at_utc": consumer_bundle_module.utc_now(),
            "surface_admissions": [
                {
                    "surface": "mission_suggest",
                    "required_schema_contract": "datapulse_ai_watch_suggestion.v1",
                    "admission_status": "admitted",
                    "mode_admission": {
                        "off": "manual_only",
                        "assist": "admitted",
                        "review": "admitted",
                    },
                    "requested_alias": "dp.mission.suggest",
                    "admitted_alias": "dp.mission.suggest",
                    "manual_fallback": "manual_review",
                    "degraded_result_allowed": True,
                    "must_expose_runtime_facts": ["served_by_alias"],
                }
            ],
        }

    monkeypatch.setattr(
        consumer_bundle_module,
        "parse_args",
        lambda: type(
            "Args",
            (),
            {
                "subscriptions": subscriptions_path,
                "output_dir": output_dir,
                "admission_output": None,
                "project_loop_state_json": None,
                "stdout": False,
            },
        )(),
    )
    monkeypatch.setattr(consumer_bundle_module, "DEFAULT_ADMISSION_OUTPUT_PATH", admission_output)
    monkeypatch.setattr(consumer_bundle_module, "read_json", lambda path: subscriptions)
    monkeypatch.setattr(consumer_bundle_module, "build_admission_payload", lambda subscriptions, path: _admission_payload())
    monkeypatch.setattr(consumer_bundle_module, "load_release_level", lambda path=None: "ci_proven")

    monkeypatch.setattr(consumer_bundle_module, "utc_now", lambda: "2026-04-02T03:05:09Z")
    aliases = consumer_bundle_module.alias_by_surface(subscriptions)
    consumer_bundle_module.write_json(admission_output, _admission_payload())
    consumer_bundle_module.write_json(output_dir / "bundle_manifest.json", consumer_bundle_module.build_bundle_manifest())
    consumer_bundle_module.write_json(
        output_dir / "surface_admission.json",
        {
            "schema": "modelbus.consumer_surface_admission.v1",
            "generated_at_utc": consumer_bundle_module.utc_now(),
            "consumer_id": "datapulse",
            "release_window": {
                "generated_at_utc": consumer_bundle_module.utc_now(),
                "release_level": "ci_proven",
                "assured_verdict": "pass",
                "constitutional_semantics": "BUNDLE-FIRST-REQUIRED",
            },
            "surface_admissions": consumer_bundle_module.build_surface_admissions(
                _admission_payload(),
                fallback_aliases=aliases,
            ),
        },
    )
    consumer_bundle_module.write_json(output_dir / "bridge_config.json", consumer_bundle_module.build_bridge_config(aliases))
    consumer_bundle_module.write_json(output_dir / "release_status.json", consumer_bundle_module.build_release_status("ci_proven"))

    writes: list[Path] = []
    monkeypatch.setattr(consumer_bundle_module, "utc_now", lambda: "2026-04-02T03:43:17Z")
    monkeypatch.setattr(consumer_bundle_module, "write_json", lambda path, payload: writes.append(Path(path)))

    rc = consumer_bundle_module.main()

    assert rc == 0
    assert writes == []


def test_modelbus_consumer_bundle_rewrites_when_release_level_changes(
    consumer_bundle_module, monkeypatch, tmp_path: Path
) -> None:
    subscriptions = {
        "surfaces": [
            {
                "surface": "mission_suggest",
                "candidate_subscriptions": [{"alias": "dp.mission.suggest"}],
            }
        ]
    }
    output_dir = tmp_path / "config" / "modelbus" / "datapulse"
    admission_output = tmp_path / "artifacts" / "governance" / "snapshots" / "datapulse-ai-surface-admission.example.json"
    subscriptions_path = tmp_path / "subscriptions.json"
    subscriptions_path.write_text(json.dumps(subscriptions), encoding="utf-8")

    def _admission_payload() -> dict[str, object]:
        return {
            "schema_version": "datapulse_ai_surface_admission.v1",
            "generated_at_utc": consumer_bundle_module.utc_now(),
            "surface_admissions": [
                {
                    "surface": "mission_suggest",
                    "required_schema_contract": "datapulse_ai_watch_suggestion.v1",
                    "admission_status": "admitted",
                    "mode_admission": {
                        "off": "manual_only",
                        "assist": "admitted",
                        "review": "admitted",
                    },
                    "requested_alias": "dp.mission.suggest",
                    "admitted_alias": "dp.mission.suggest",
                    "manual_fallback": "manual_review",
                    "degraded_result_allowed": True,
                    "must_expose_runtime_facts": ["served_by_alias"],
                }
            ],
        }

    monkeypatch.setattr(
        consumer_bundle_module,
        "parse_args",
        lambda: type(
            "Args",
            (),
            {
                "subscriptions": subscriptions_path,
                "output_dir": output_dir,
                "admission_output": None,
                "project_loop_state_json": None,
                "stdout": False,
            },
        )(),
    )
    monkeypatch.setattr(consumer_bundle_module, "DEFAULT_ADMISSION_OUTPUT_PATH", admission_output)
    monkeypatch.setattr(consumer_bundle_module, "read_json", lambda path: subscriptions)
    monkeypatch.setattr(consumer_bundle_module, "build_admission_payload", lambda subscriptions, path: _admission_payload())

    monkeypatch.setattr(consumer_bundle_module, "utc_now", lambda: "2026-04-02T03:05:09Z")
    aliases = consumer_bundle_module.alias_by_surface(subscriptions)
    consumer_bundle_module.write_json(admission_output, _admission_payload())
    consumer_bundle_module.write_json(output_dir / "bundle_manifest.json", consumer_bundle_module.build_bundle_manifest())
    consumer_bundle_module.write_json(
        output_dir / "surface_admission.json",
        {
            "schema": "modelbus.consumer_surface_admission.v1",
            "generated_at_utc": consumer_bundle_module.utc_now(),
            "consumer_id": "datapulse",
            "release_window": {
                "generated_at_utc": consumer_bundle_module.utc_now(),
                "release_level": "manual_only",
                "assured_verdict": "pass",
                "constitutional_semantics": "BUNDLE-FIRST-REQUIRED",
            },
            "surface_admissions": consumer_bundle_module.build_surface_admissions(
                _admission_payload(),
                fallback_aliases=aliases,
            ),
        },
    )
    consumer_bundle_module.write_json(output_dir / "bridge_config.json", consumer_bundle_module.build_bridge_config(aliases))
    consumer_bundle_module.write_json(output_dir / "release_status.json", consumer_bundle_module.build_release_status("manual_only"))

    writes: list[Path] = []
    monkeypatch.setattr(consumer_bundle_module, "load_release_level", lambda path=None: "ci_proven")
    monkeypatch.setattr(consumer_bundle_module, "utc_now", lambda: "2026-04-02T03:43:17Z")
    monkeypatch.setattr(consumer_bundle_module, "write_json", lambda path, payload: writes.append(Path(path)))

    rc = consumer_bundle_module.main()

    assert rc == 0
    assert writes == [
        (output_dir / "surface_admission.json").resolve(),
        (output_dir / "release_status.json").resolve(),
    ]


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


def test_repo_workspace_clean_ignores_internal_runtime_evidence_output(loop_contracts, monkeypatch) -> None:
    monkeypatch.setattr(
        loop_contracts,
        "git_output",
        lambda *args: " M out/governance/datapulse_internal_ai_surface_runtime_evidence.draft.json\n",
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
    snapshot_attestation_path = tmp_path / "snapshots" / "datapulse_release_window_attestation.draft.json"

    monkeypatch.setattr(
        auto_continuation,
        "resolve_governance_write_path",
        lambda root, name, repo_root=None: tmp_path / "snapshots" / name,
    )

    def _fake_run_capture(command: list[str], *, required: bool = True) -> str:
        calls.append((tuple(command), required))
        script_name = command[1] if len(command) > 1 else ""
        if script_name == "scripts/governance/run_datapulse_quick_test_gate.py":
            assert required is False
            return '{"ok": false}'
        if script_name == "scripts/governance/export_datapulse_structured_release_bundle.py":
            bundle_attestation_path = tmp_path / "bundle" / "datapulse_release_window_attestation.draft.json"
            bundle_attestation_path.parent.mkdir(parents=True, exist_ok=True)
            bundle_attestation_path.write_text('{"git_head":"abc"}', encoding="utf-8")
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
        "internal_ai_surface_runtime_evidence": "scripts/governance/export_datapulse_internal_ai_surface_runtime_evidence.py",
        "structured_release_bundle": "scripts/governance/export_datapulse_structured_release_bundle.py",
        "code_landing_status": "scripts/governance/export_datapulse_code_landing_status.py",
        "project_loop_state": "scripts/governance/export_datapulse_project_loop_state.py",
    }
    assert snapshot_attestation_path.read_text(encoding="utf-8") == '{"git_head":"abc"}'
    assert calls == [
        (("python", "scripts/governance/run_datapulse_quick_test_gate.py"), False),
        (
            (
                "python",
                "scripts/governance/export_datapulse_internal_ai_surface_runtime_evidence.py",
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
        (
            (
                "python",
                "scripts/governance/export_datapulse_code_landing_status.py",
                "--output",
                str(tmp_path / "code_landing_status.json"),
                "--release-window-attestation",
                str(snapshot_attestation_path),
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
                "--release-window-attestation",
                str(snapshot_attestation_path),
            ),
            True,
        ),
    ]


def test_project_loop_state_export_forwards_release_window_attestation(monkeypatch, tmp_path: Path) -> None:
    if str(GOVERNANCE_SCRIPTS_DIR) not in sys.path:
        sys.path.insert(0, str(GOVERNANCE_SCRIPTS_DIR))
    project_loop_state_module = importlib.import_module("export_datapulse_project_loop_state")

    attestation_path = tmp_path / "datapulse_release_window_attestation.draft.json"
    captured: dict[str, Path | None] = {"attestation_path": None}

    monkeypatch.setattr(
        project_loop_state_module,
        "parse_args",
        lambda: project_loop_state_module.argparse.Namespace(
            plan=tmp_path / "plan.json",
            output=tmp_path / "project_specific_loop_state.draft.json",
            release_window_attestation=attestation_path,
            stdout=False,
        ),
    )
    monkeypatch.setattr(project_loop_state_module, "load_plan", lambda path: {"project": "DataPulse"})

    def _fake_build_code_landing_status(*, release_window_attestation_path=None):
        captured["attestation_path"] = release_window_attestation_path
        return {"headline_summary": {"current_level": "release_governed"}}

    monkeypatch.setattr(project_loop_state_module, "build_code_landing_status", _fake_build_code_landing_status)
    monkeypatch.setattr(project_loop_state_module, "build_project_loop_state", lambda plan, landing_status: {"status": "ok"})
    monkeypatch.setattr(project_loop_state_module, "write_json", lambda path, payload: None)

    assert project_loop_state_module.main() == 0
    assert captured["attestation_path"] == attestation_path.resolve()


def test_parse_args_defaults_to_dirty_worktree_fallback(governance_loop, monkeypatch) -> None:
    monkeypatch.setattr(sys, "argv", ["run_codex_blueprint_loop.py"])

    args = governance_loop.parse_args()

    assert args.allow_existing_dirty_worktree is True
    assert args.dirty_worktree_settle_max_attempts == governance_loop.DEFAULT_DIRTY_WORKTREE_SETTLE_MAX_ATTEMPTS


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


def test_maybe_auto_promote_defers_dirty_worktree_settle_before_fallback(
    governance_loop, monkeypatch, tmp_path: Path
) -> None:
    stdout_path = tmp_path / "gate.stdout.log"
    stderr_path = tmp_path / "gate.stderr.log"
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
    settle_attempts: dict[str, int] = {}

    returned_runtime, _snapshots, _plan, promotions = governance_loop.maybe_auto_promote(
        runtime=runtime,
        slice_execution_brief={"id": "L16.4"},
        round_index=1,
        output_dir=tmp_path / "out",
        baseline_dirty_paths=["datapulse/reader.py"],
        promotion_mode="auto",
        allow_existing_dirty_worktree=True,
        dirty_worktree_settle_attempts=settle_attempts,
        dirty_worktree_settle_max_attempts=3,
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

    carryover = governance_loop.dirty_worktree_carryover_payload(promotions)
    assert returned_runtime == runtime
    assert carryover is not None
    assert carryover["step"] == governance_loop.DIRTY_WORKTREE_SETTLE_DEFERRED_STEP
    assert carryover["settle_attempt"] == 1
    assert governance_loop.supports_dirty_worktree_round_continuation(runtime, promotions) is True
    assert settle_attempts[governance_loop.dirty_worktree_settle_signature(runtime, [" M datapulse/reader.py"])] == 1


def test_maybe_auto_promote_uses_dirty_worktree_fallback_after_retry_budget(
    governance_loop, monkeypatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(governance_loop, "load_plan", lambda path: {})
    monkeypatch.setattr(
        governance_loop,
        "run_pre_promotion_gate",
        lambda **kwargs: (_ for _ in ()).throw(AssertionError("fallback should skip another gate run")),
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
    settle_attempts = {
        governance_loop.dirty_worktree_settle_signature(runtime, [" M datapulse/reader.py"]): 3,
    }

    _runtime, _snapshots, _plan, promotions = governance_loop.maybe_auto_promote(
        runtime=runtime,
        slice_execution_brief={"id": "L16.4"},
        round_index=2,
        output_dir=tmp_path / "out",
        baseline_dirty_paths=["datapulse/reader.py"],
        promotion_mode="auto",
        allow_existing_dirty_worktree=True,
        dirty_worktree_settle_attempts=settle_attempts,
        dirty_worktree_settle_max_attempts=3,
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

    carryover = governance_loop.dirty_worktree_carryover_payload(promotions)
    assert carryover is not None
    assert carryover["step"] == governance_loop.DIRTY_WORKTREE_CARRYOVER_FALLBACK_STEP
    assert carryover["settle_attempt"] == 3


def test_maybe_auto_promote_persists_repair_request_after_dirty_worktree_settle_budget_exhausts_in_strict_mode(
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
            allow_existing_dirty_worktree=False,
            dirty_worktree_settle_attempts={},
            dirty_worktree_settle_max_attempts=1,
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


def test_internal_ai_surface_registry_export_builds_internal_only_registry() -> None:
    if str(GOVERNANCE_SCRIPTS_DIR) not in sys.path:
        sys.path.insert(0, str(GOVERNANCE_SCRIPTS_DIR))
    registry_module = importlib.import_module("export_datapulse_internal_ai_surface_registry")

    payload = registry_module.build_payload(
        registry_module.DEFAULT_CAPABILITY_CATALOG_PATH,
        registry_module.DEFAULT_BRIDGE_CONFIG_PATH,
        registry_module.DEFAULT_SURFACE_ADMISSION_PATH,
        registry_module.DEFAULT_READER_PATH,
    )

    assert payload["schema_version"] == "datapulse_internal_ai_surface_registry.v1"
    assert payload["publication_boundary"]["external_publication_promise"] is False
    assert payload["surface_ids"] == [
        "ai_surface_precheck",
        "mission_suggest",
        "triage_assist",
        "claim_draft",
        "report_draft",
        "delivery_summary",
    ]

    surfaces = {row["surface_id"]: row for row in payload["surfaces"]}
    assert all(row["internal_only"] is True for row in payload["surfaces"])
    assert surfaces["ai_surface_precheck"]["bound_tools"] == ["ai_surface_precheck"]
    assert surfaces["ai_surface_precheck"]["bound_aliases"] == []
    assert surfaces["mission_suggest"]["subject_kind"] == "WatchMission"
    assert surfaces["mission_suggest"]["bound_aliases"] == ["dp.mission.suggest"]
    assert surfaces["report_draft"]["bound_aliases"] == ["dp.report.draft"]
    assert surfaces["report_draft"]["schema_contract_id"] == ""
    assert surfaces["delivery_summary"]["output_kind"] == "summary"


def test_internal_ai_surface_registry_export_main_writes_requested_output(monkeypatch, tmp_path: Path) -> None:
    if str(GOVERNANCE_SCRIPTS_DIR) not in sys.path:
        sys.path.insert(0, str(GOVERNANCE_SCRIPTS_DIR))
    registry_module = importlib.import_module("export_datapulse_internal_ai_surface_registry")
    output_path = tmp_path / "datapulse-internal-ai-surface-registry.draft.json"

    monkeypatch.setattr(registry_module, "utc_now", lambda: "2026-04-01T15:52:00Z")
    monkeypatch.setattr(
        registry_module,
        "parse_args",
        lambda: registry_module.argparse.Namespace(
            capability_catalog=registry_module.DEFAULT_CAPABILITY_CATALOG_PATH,
            bridge_config=registry_module.DEFAULT_BRIDGE_CONFIG_PATH,
            surface_admission=registry_module.DEFAULT_SURFACE_ADMISSION_PATH,
            reader=registry_module.DEFAULT_READER_PATH,
            output=output_path,
            stdout=False,
        ),
    )

    assert registry_module.main() == 0
    payload = json.loads(output_path.read_text(encoding="utf-8"))

    assert payload["generated_at_utc"] == "2026-04-01T15:52:00Z"
    assert payload["surface_ids"][0] == "ai_surface_precheck"
    assert payload["surface_ids"][-1] == "delivery_summary"
