"""Verify every schema file under config/modelbus/schemas/ is a valid Draft-07 JSON Schema."""
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
    # Will raise jsonschema.exceptions.SchemaError if the schema itself is malformed.
    jsonschema.Draft7Validator.check_schema(schema)


def test_at_least_one_schema_in_each_source_dir() -> None:
    upstream = list((SCHEMAS_ROOT / "upstream").glob("*.v1.json"))
    contract = list((SCHEMAS_ROOT / "consumer-contract").glob("*.v1.json"))
    assert upstream, "expected at least one upstream mirror under config/modelbus/schemas/upstream/"
    assert contract, "expected at least one consumer contract under config/modelbus/schemas/consumer-contract/"
