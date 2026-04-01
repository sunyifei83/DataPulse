from __future__ import annotations

import pytest

from datapulse._runtime import build_python_version_error, ensure_supported_python
from datapulse.surface_capabilities import build_runtime_surface_introspection, build_surface_parity_report, runtime_reopen_rules


def test_build_python_version_error_mentions_minimum_and_uv() -> None:
    message = build_python_version_error((3, 9, 6), executable="/usr/bin/python3")

    assert "Python 3.10+" in message
    assert "3.9.6" in message
    assert "/usr/bin/python3" in message
    assert "`uv run ...`" in message


def test_ensure_supported_python_rejects_older_runtime() -> None:
    with pytest.raises(RuntimeError, match=r"requires Python 3\.10\+"):
        ensure_supported_python((3, 9, 6), executable="/usr/bin/python3")


def test_ensure_supported_python_accepts_supported_runtime() -> None:
    ensure_supported_python((3, 10, 0), executable="/usr/bin/python3.10")


def test_surface_parity_report_is_green_for_landed_catalog() -> None:
    payload = build_surface_parity_report()

    assert payload["ok"] is True
    assert payload["surface_count"] == 5
    assert payload["coverage_by_surface"]["skill"]["documented"] >= 1


def test_surface_parity_report_detects_missing_surface_entries() -> None:
    catalog = {
        "catalog_id": "test-runtime-surfaces",
        "generated_at_utc": "2026-04-01T10:00:00Z",
        "surfaces": [
            {"id": "cli", "title": "CLI", "projection_kind": "argparse"},
            {"id": "mcp", "title": "MCP", "projection_kind": "tool"},
            {"id": "console", "title": "Console", "projection_kind": "http"},
            {"id": "agent", "title": "Agent", "projection_kind": "health_payload"},
            {"id": "skill", "title": "Skill", "projection_kind": "documentation_and_manifest"},
        ],
        "capabilities": [
            {
                "id": "broken_capability",
                "title": "Broken capability",
                "surfaces": {
                    "cli": {"availability": "available", "entrypoints": ["--broken"]},
                    "mcp": {"availability": "available", "entrypoints": ["tool:broken"]},
                    "console": {"availability": "available", "entrypoints": ["GET /api/broken"]},
                    "agent": {"availability": "available", "entrypoints": ["DataPulseAgent.broken()"]},
                },
            }
        ],
    }

    payload = build_surface_parity_report(catalog=catalog)

    assert payload["ok"] is False
    assert payload["findings"][0]["kind"] == "missing_surfaces"
    assert payload["findings"][0]["surfaces"] == ["skill"]


def test_runtime_surface_introspection_includes_reopen_rules() -> None:
    payload = build_runtime_surface_introspection()
    rules = runtime_reopen_rules()

    assert payload["parity"]["ok"] is True
    assert payload["reopen_rules"]["wave_id"] == "L27"
    assert payload["reopen_rules"]["admissible_evidence"] == rules["admissible_evidence"]
