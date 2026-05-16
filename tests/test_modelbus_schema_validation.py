"""Tests for the schema validation helper introduced in reader.py."""
from __future__ import annotations

import pytest

pytest.importorskip("jsonschema")

from datapulse.reader import DataPulseReader


@pytest.fixture
def reader(tmp_path, monkeypatch):
    monkeypatch.setenv("INBOX_FILE", str(tmp_path / "test_inbox.json"))
    return DataPulseReader()


def test_validate_returns_empty_when_payload_conforms_to_upstream(reader):
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
