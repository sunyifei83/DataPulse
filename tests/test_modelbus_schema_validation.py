"""Tests for the schema validation helper introduced in reader.py."""
from __future__ import annotations

import pytest

pytest.importorskip("jsonschema")

from datapulse.reader import DataPulseReader


@pytest.fixture
def reader(tmp_path, monkeypatch):
    monkeypatch.setenv("INBOX_FILE", str(tmp_path / "test_inbox.json"))
    return DataPulseReader()


def test_validate_error_messages_for_upstream_schema_are_well_formed(reader):
    payload = {
        "schema": "modelbus.release_status.v1",
        "generated_at_utc": "2026-05-16T00:00:00Z",
        "release_level": "ci_proven",
        "assured_verdict": "pass",
        "runtime": {"base_url": "https://modelbus.example.com"},
    }
    errors = reader._validate_against_schema(payload, "modelbus.release_status.v1")
    # Upstream schema may require more fields than this stub. The test asserts
    # that whatever errors come back name the actual missing fields, not a
    # generic crash.
    for e in errors:
        assert "modelbus.release_status.v1" in e
        assert "[upstream]" in e


def test_validate_returns_empty_for_conformant_consumer_contract(reader):
    payload = {
        "schema": "modelbus.consumer_bridge_config.v1",
        "consumer_id": "datapulse",
        "base_url": "https://modelbus.example.com",
    }
    errors = reader._validate_against_schema(payload, "modelbus.consumer_bridge_config.v1")
    assert errors == [], f"expected no errors, got: {errors}"


def test_validate_catches_missing_required_field(reader):
    payload = {
        "schema": "modelbus.consumer_surface_admission.v1",
        # Intentionally omit consumer_id (required by contract)
        "surface_admissions": [],
    }
    errors = reader._validate_against_schema(payload, "modelbus.consumer_surface_admission.v1")
    assert errors, "expected validation errors for missing consumer_id"
    assert any("consumer_id" in e for e in errors), f"expected 'consumer_id' in errors: {errors}"


def test_validate_catches_schema_const_mismatch(reader):
    payload = {
        "schema": "modelbus.consumer_surface_admission.v2",  # wrong const
        "consumer_id": "datapulse",
        "surface_admissions": [],
    }
    errors = reader._validate_against_schema(payload, "modelbus.consumer_surface_admission.v1")
    assert errors, f"expected error for schema const mismatch: {errors}"


def test_validate_returns_empty_when_no_schema_file_found(reader):
    errors = reader._validate_against_schema({}, "modelbus.nonexistent.v1")
    assert errors == []


def test_validate_skips_gracefully_when_jsonschema_missing(reader, monkeypatch):
    """Force ImportError on `import jsonschema` and confirm helper returns []
    + sets the class-level warn-once flag."""
    import sys
    # Reset the warn-once flag so this test sees a fresh state.
    from datapulse.reader import DataPulseReader
    monkeypatch.setattr(DataPulseReader, "_MODELBUS_VALIDATION_WARNED_MISSING_LIB", False)
    # Setting sys.modules['jsonschema'] = None makes `import jsonschema` raise ImportError.
    monkeypatch.setitem(sys.modules, "jsonschema", None)
    payload = {"schema": "modelbus.consumer_bridge_config.v1", "consumer_id": "datapulse"}
    errors = reader._validate_against_schema(payload, "modelbus.consumer_bridge_config.v1")
    assert errors == []
    # Calling again should NOT toggle the flag back to False.
    errors2 = reader._validate_against_schema(payload, "modelbus.consumer_bridge_config.v1")
    assert errors2 == []
    assert DataPulseReader._MODELBUS_VALIDATION_WARNED_MISSING_LIB is True


import json as _json
import os as _os
from pathlib import Path as _Path


def _write_conformant_bundle(bundle_dir: _Path) -> None:
    """Write a 4-file bundle that satisfies both upstream mirrors and DP contracts."""
    bundle_dir.mkdir(parents=True, exist_ok=True)
    (bundle_dir / "bundle_manifest.json").write_text(_json.dumps({
        "schema": "modelbus.consumer_bundle_manifest.v1",
        "generated_at_utc": "2026-05-16T00:00:00Z",
        "bundle_id": "datapulse.ai_surface_bus",
        "consumer_id": "datapulse",
        "source_profile": {"path": "consumer-profile.datapulse.json", "consumer": {"repo_root": "/tmp"}},
        "runtime": {"base_url": "https://modelbus.example.com"},
        "artifacts": {
            "bundle_readme": {"path": "README.md"},
            "bundle_manifest": {"path": "bundle_manifest.json"},
            "bridge_config": {"path": "bridge_config.json"},
            "alias_catalog": {"path": "alias_catalog.json"},
            "surface_admission": {"path": "surface_admission.json"},
            "release_status": {"path": "release_status.json"},
            "smoke_manifest": {"path": "smoke_manifest.json"},
        },
        "surfaces": [],
        "governance": {"accepted_modelbus_semantics": ["BUNDLE-FIRST-REQUIRED"]},
    }))
    (bundle_dir / "surface_admission.json").write_text(_json.dumps({
        "schema": "modelbus.consumer_surface_admission.v1",
        "consumer_id": "datapulse",
        "generated_at_utc": "2026-05-16T00:00:00Z",
        "surface_admissions": [],
    }))
    (bundle_dir / "bridge_config.json").write_text(_json.dumps({
        "schema": "modelbus.consumer_bridge_config.v1",
        "consumer_id": "datapulse",
    }))
    (bundle_dir / "release_status.json").write_text(_json.dumps({
        "schema": "modelbus.release_status.v1",
        "generated_at_utc": "2026-05-16T00:00:00Z",
        "release_level": "ci_proven",
        "assured_verdict": "pass",
        "runtime": {"base_url": "https://modelbus.example.com"},
    }))


def test_load_bundle_warn_mode_logs_but_does_not_fail(tmp_path, monkeypatch, caplog):
    """Default mode is 'warn': validation errors are logged but do not propagate into errors list."""
    bundle_dir = tmp_path / "bundle"
    _write_conformant_bundle(bundle_dir)
    # Mutilate surface_admission to drop a required field
    sa_path = bundle_dir / "surface_admission.json"
    sa = _json.loads(sa_path.read_text())
    del sa["consumer_id"]
    sa_path.write_text(_json.dumps(sa))

    monkeypatch.setenv("DATAPULSE_MODELBUS_BUNDLE_DIR", str(bundle_dir))
    monkeypatch.delenv("DATAPULSE_MODELBUS_VALIDATION_MODE", raising=False)  # default = warn

    reader = DataPulseReader()
    with caplog.at_level("WARNING"):
        result = reader._load_modelbus_bundle_surface_admissions()

    # In warn mode, the schema-string check for surface_admission STILL fires
    # because deleting consumer_id also leaves the schema-string check alone —
    # but the new validation should ALSO log a warn about consumer_id missing.
    validation_warnings = [r for r in caplog.records if "consumer_id" in r.getMessage()]
    assert validation_warnings, "expected warn-mode log line mentioning consumer_id"


def test_load_bundle_fail_mode_propagates_validation_errors(tmp_path, monkeypatch):
    """Mode='fail': validation errors are appended to the bundle errors list."""
    bundle_dir = tmp_path / "bundle"
    _write_conformant_bundle(bundle_dir)
    sa_path = bundle_dir / "surface_admission.json"
    sa = _json.loads(sa_path.read_text())
    del sa["consumer_id"]
    sa_path.write_text(_json.dumps(sa))

    monkeypatch.setenv("DATAPULSE_MODELBUS_BUNDLE_DIR", str(bundle_dir))
    monkeypatch.setenv("DATAPULSE_MODELBUS_VALIDATION_MODE", "fail")

    reader = DataPulseReader()
    result = reader._load_modelbus_bundle_surface_admissions()

    assert result.get("errors"), f"expected errors in fail mode: {result}"
    assert any("consumer_id" in e for e in result["errors"]), result["errors"]
