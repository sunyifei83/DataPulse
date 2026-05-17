"""Verify every schema file under config/modelbus/schemas/ is a valid JSON Schema (Draft-7 / 2019-09 / 2020-12 per $schema)."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
SCHEMAS_ROOT = REPO_ROOT / "config" / "modelbus" / "schemas"


def _all_schema_files() -> list[Path]:
    return sorted(SCHEMAS_ROOT.rglob("*.v1.json"))


@pytest.mark.parametrize("schema_path", _all_schema_files(), ids=lambda p: p.relative_to(REPO_ROOT).as_posix())
def test_schema_file_is_valid_json_schema(schema_path: Path) -> None:
    jsonschema = pytest.importorskip("jsonschema")
    schema = json.loads(schema_path.read_text())
    schema_uri = str(schema.get("$schema") or "")
    if "2020-12" in schema_uri:
        validator_cls = jsonschema.Draft202012Validator
    elif "2019-09" in schema_uri:
        validator_cls = jsonschema.Draft201909Validator
    else:
        validator_cls = jsonschema.Draft7Validator
    # Will raise jsonschema.exceptions.SchemaError if the schema itself is malformed.
    validator_cls.check_schema(schema)


def test_upstream_has_mirror_for_every_dp_consumed_schema() -> None:
    """DP must always have an upstream mirror for every schema name it reads
    from MB. The list is hand-maintained from the 4 _validate_against_schema
    call sites in datapulse/reader.py (the four bundle payloads)."""
    upstream = {p.name for p in (SCHEMAS_ROOT / "upstream").glob("*.v1.json")}
    required = {
        "modelbus.consumer_bundle_manifest.v1.json",
        "modelbus.consumer_bridge_config.v1.json",
        "modelbus.consumer_surface_admission.v1.json",
        "modelbus.release_status.v1.json",
    }
    missing = required - upstream
    assert not missing, f"upstream/ is missing required mirrors: {sorted(missing)}"


def test_consumer_contract_dir_exists_for_future_use() -> None:
    """consumer-contract/ may be empty after MB publishes authoritative
    schemas (as of 2026-05-17 it is). The directory + README stay so the
    schema-discovery fallback path in reader.py keeps working and a new CDC
    stand-in can be dropped in without scaffolding."""
    contract_dir = SCHEMAS_ROOT / "consumer-contract"
    assert contract_dir.is_dir()
    assert (contract_dir / "README.md").is_file()
