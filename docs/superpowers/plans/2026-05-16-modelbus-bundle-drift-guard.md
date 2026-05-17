# ModelBus Bundle Drift Guard Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make ModelBus bundle schema drift loud (parser-enforced JSON Schema validation) and observable in CI (weekly diff against MB upstream).

**Architecture:** Two-source schema validation in `datapulse/reader.py` — mirror MB-authoritative schemas where published, DP-authored consumer-driven contracts for un-published payloads (Pact CDC pattern). Single-shot operator step re-pulls the conformant bundle from MB. Weekly GitHub Actions workflow diffs DP's mirror against MB's main HEAD via cross-repo PAT.

**Tech Stack:** Python 3.10+, `jsonschema>=4.0` (optional extra `governance`), GitHub Actions, `gh` CLI, no new runtime deps.

**Spec:** `docs/superpowers/specs/2026-05-16-modelbus-bundle-drift-guard-design.md`

---

## Task 1: Create schema directories and populate

**Files:**
- Create: `config/modelbus/schemas/upstream/modelbus.consumer_bundle_manifest.v1.json`
- Create: `config/modelbus/schemas/upstream/modelbus.release_status.v1.json`
- Create: `config/modelbus/schemas/upstream/README.md`
- Create: `config/modelbus/schemas/consumer-contract/modelbus.consumer_surface_admission.v1.json`
- Create: `config/modelbus/schemas/consumer-contract/modelbus.consumer_bridge_config.v1.json`
- Create: `config/modelbus/schemas/consumer-contract/README.md`

- [ ] **Step 1: Create directories**

```bash
mkdir -p config/modelbus/schemas/upstream config/modelbus/schemas/consumer-contract
```

- [ ] **Step 2: Fetch MB-authoritative bundle_manifest schema**

```bash
gh api repos/sunyifei83/ModelBusProject/contents/docs/schemas/modelbus.consumer_bundle_manifest.v1.json --jq '.content' \
  | base64 -d > config/modelbus/schemas/upstream/modelbus.consumer_bundle_manifest.v1.json
```

Verify it parses as JSON:
```bash
python3 -c "import json; json.load(open('config/modelbus/schemas/upstream/modelbus.consumer_bundle_manifest.v1.json'))"
```
Expected: no output (success).

- [ ] **Step 3: Fetch MB-authoritative release_status schema**

```bash
gh api repos/sunyifei83/ModelBusProject/contents/docs/schemas/modelbus.release_status.v1.json --jq '.content' \
  | base64 -d > config/modelbus/schemas/upstream/modelbus.release_status.v1.json
python3 -c "import json; json.load(open('config/modelbus/schemas/upstream/modelbus.release_status.v1.json'))"
```

- [ ] **Step 4: Write upstream README.md**

File `config/modelbus/schemas/upstream/README.md`:

```markdown
# MB-authoritative schema mirror

This directory contains verbatim copies of JSON Schema documents published by
`sunyifei83/ModelBusProject` at `docs/schemas/`. They are the source of truth
for the payloads DP consumes.

| Schema | MB blob SHA | Pulled |
|---|---|---|
| `modelbus.consumer_bundle_manifest.v1.json` | `84dc243485070785b3dc77474966e00ed9f7a5fd` | 2026-05-16 |
| `modelbus.release_status.v1.json` | `78aa95aac295eb20cf907f6c8371583d03008a09` | 2026-05-16 |

## Refresh policy

- Weekly `.github/workflows/modelbus-bundle-drift.yml` diffs these against MB main.
- On non-additive drift, workflow fails. Operator updates the mirror file +
  bumps the SHA in this table in the same PR.
- Do not edit schema content by hand — always re-fetch via `gh api`.
```

- [ ] **Step 5: Author DP consumer contract for surface_admission**

File `config/modelbus/schemas/consumer-contract/modelbus.consumer_surface_admission.v1.json`:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "consumer-contract/modelbus.consumer_surface_admission.v1",
  "title": "DataPulse consumer contract for modelbus.consumer_surface_admission.v1",
  "description": "Authored by DP. Encodes the fields DP reader.py depends on. MB-emitted payloads may include additional fields (additionalProperties:true). Swap to MB-authoritative upstream/ mirror when MB publishes one.",
  "type": "object",
  "required": ["schema", "consumer_id", "surface_admissions"],
  "additionalProperties": true,
  "properties": {
    "schema": {"const": "modelbus.consumer_surface_admission.v1"},
    "consumer_id": {"const": "datapulse"},
    "generated_at_utc": {"type": "string"},
    "surface_admissions": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["surface_id", "admission_status"],
        "additionalProperties": true,
        "properties": {
          "surface_id": {"type": "string", "minLength": 1},
          "requested_alias": {"type": "string"},
          "admitted_alias": {"type": "string"},
          "admission_status": {"type": "string", "enum": ["admitted", "rejected"]},
          "mode_admission": {"type": "object"},
          "schema_contract": {"type": ["string", "null"]},
          "manual_fallback": {"type": "string"},
          "degraded_result_allowed": {"type": "boolean"},
          "must_expose_runtime_facts": {"type": "array"},
          "rejectable_gaps": {"type": "array"}
        }
      }
    },
    "release_window": {
      "type": "object",
      "additionalProperties": true,
      "properties": {
        "constitutional_semantics": {"type": "string"}
      }
    }
  }
}
```

- [ ] **Step 6: Author DP consumer contract for bridge_config**

File `config/modelbus/schemas/consumer-contract/modelbus.consumer_bridge_config.v1.json`:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "consumer-contract/modelbus.consumer_bridge_config.v1",
  "title": "DataPulse consumer contract for modelbus.consumer_bridge_config.v1",
  "description": "Authored by DP. The bridge_config payload is returned verbatim to callers (datapulse/reader.py:1179), so structurally DP only requires schema + consumer_id. Swap to MB-authoritative upstream/ mirror when MB publishes one.",
  "type": "object",
  "required": ["schema", "consumer_id"],
  "additionalProperties": true,
  "properties": {
    "schema": {"const": "modelbus.consumer_bridge_config.v1"},
    "consumer_id": {"const": "datapulse"}
  }
}
```

- [ ] **Step 7: Write consumer-contract README.md**

File `config/modelbus/schemas/consumer-contract/README.md`:

```markdown
# DataPulse consumer-driven contracts

This directory contains JSON Schemas **authored by DataPulse** for ModelBus
payloads that MB has not yet published as authoritative `.json` schema
documents (only emitted as payload `schema:` tags from
`sunyifei83/ModelBusProject:scripts/ci/build_consumer_bundle.py`).

Contracts here encode **only the fields DP reader.py depends on**, with
`additionalProperties: true` so MB is free to add fields without breaking DP.
This is the classic consumer-driven contract pattern (Pact CDC).

## Files

| Schema | DP-consumed at | MB code reference |
|---|---|---|
| `modelbus.consumer_surface_admission.v1.json` | `datapulse/reader.py:1103-1117, 1114-1158` | `build_consumer_bundle.py:207` |
| `modelbus.consumer_bridge_config.v1.json` | `datapulse/reader.py:1107-1110, 1179` | `build_consumer_bundle.py:158` |

## Migration to MB-authoritative

When MB publishes `docs/schemas/modelbus.consumer_{surface_admission,bridge_config}.v1.json`:
1. Mirror them into `../upstream/`.
2. Delete the file here.
3. Reader auto-prefers `upstream/` (see `_validate_against_schema`).
```

- [ ] **Step 8: Commit**

```bash
git add config/modelbus/schemas/
git commit -m "feat(modelbus): add schema mirror + consumer contracts

Mirror MB-authoritative bundle_manifest and release_status schemas at
config/modelbus/schemas/upstream/. Author DP consumer-driven contracts
for surface_admission and bridge_config payloads at
config/modelbus/schemas/consumer-contract/.

Refs spec docs/superpowers/specs/2026-05-16-modelbus-bundle-drift-guard-design.md"
```

---

## Task 2: Walking JSON Schema validity test

**Files:**
- Create: `tests/test_modelbus_schema_well_formed.py`

- [ ] **Step 1: Write the failing test**

File `tests/test_modelbus_schema_well_formed.py`:

```python
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
```

- [ ] **Step 2: Run test to verify it passes**

Run: `pytest tests/test_modelbus_schema_well_formed.py -v`

If `jsonschema` is not installed, parametrized cases will skip (importorskip). That's fine for this task; Task 3 adds the dep.

Expected: `test_at_least_one_schema_in_each_source_dir` PASS (after Task 1 schemas in place); parametrized cases SKIP if jsonschema missing, else PASS.

- [ ] **Step 3: Commit**

```bash
git add tests/test_modelbus_schema_well_formed.py
git commit -m "test(modelbus): assert schema files are well-formed JSON Schema"
```

---

## Task 3: Add jsonschema as optional dep

**Files:**
- Modify: `pyproject.toml:40-60`

- [ ] **Step 1: Add `governance` extra and include in `all`**

Edit `pyproject.toml`. After line 52 (inside the `all = [...]` array, before the closing bracket), add `"jsonschema>=4.0",`. Then after line 59 (the `console = ...` line) add a new line:

```toml
governance = ["jsonschema>=4.0"]
```

Also add `"jsonschema>=4.0"` to the `dev` array on line 60 so `pip install -e .[dev]` pulls it for tests.

Final shape (around lines 40-60):

```toml
[project.optional-dependencies]
all = [
    "trafilatura>=1.12",
    "lxml>=5.1",
    "lxml-html-clean>=0.4",
    "youtube-transcript-api>=0.6.2",
    "telethon>=1.34",
    "playwright>=1.40",
    "mcp[cli]>=1.0",
    "notebooklm-py>=0.3.0",
    "fastapi>=0.115",
    "uvicorn>=0.30",
    "jsonschema>=4.0",
]
trafilatura = ["trafilatura>=1.12", "beautifulsoup4>=4.12"]
youtube = ["youtube-transcript-api>=0.6.2"]
telegram = ["telethon>=1.34"]
browser = ["playwright>=1.40"]
mcp = ["mcp[cli]>=1.0"]
notebooklm = ["notebooklm-py>=0.3.0"]
console = ["fastapi>=0.115", "uvicorn>=0.30"]
governance = ["jsonschema>=4.0"]
dev = ["pytest>=8.0", "pytest-asyncio>=0.23", "ruff>=0.3", "mypy>=1.8", "types-requests>=2.31", "types-beautifulsoup4>=4.12", "fastapi>=0.115", "uvicorn>=0.30", "httpx>=0.27", "jsonschema>=4.0"]
```

- [ ] **Step 2: Install the dep locally for tests**

```bash
pip install -e '.[dev]'
```

Verify:
```bash
python3 -c "import jsonschema; print(jsonschema.__version__)"
```
Expected: prints a version `>=4.0`.

- [ ] **Step 3: Re-run Task 2's tests to confirm parametrized cases now run**

```bash
pytest tests/test_modelbus_schema_well_formed.py -v
```
Expected: all parametrized cases PASS (no skips). Should be 4 parametrized PASSes + the directory presence test = 5 PASS.

- [ ] **Step 4: Commit**

```bash
git add pyproject.toml
git commit -m "build: add jsonschema as optional [governance] extra and dev dep"
```

---

## Task 4: TDD `_validate_against_schema` helper

**Files:**
- Modify: `datapulse/reader.py` (add helper method near other modelbus helpers, ~line 1183)
- Create: `tests/test_modelbus_schema_validation.py`

- [ ] **Step 1: Write the failing test**

File `tests/test_modelbus_schema_validation.py`:

```python
"""Tests for the schema validation helper introduced in reader.py."""
from __future__ import annotations

import pytest

pytest.importorskip("jsonschema")

from datapulse.reader import DataPulseReader


@pytest.fixture
def reader(tmp_path, monkeypatch):
    monkeypatch.setenv("DATAPULSE_DB", str(tmp_path / "test.db"))
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
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/test_modelbus_schema_validation.py -v
```
Expected: all tests FAIL with `AttributeError: 'DataPulseReader' object has no attribute '_validate_against_schema'`.

- [ ] **Step 3: Implement the helper**

Open `datapulse/reader.py`. Find the line `def _load_modelbus_bundle_surface_admissions(self) -> dict[str, Any]:` (around line 1183). Insert a new method **before** it:

```python
    _MODELBUS_SCHEMAS_DIR = Path(__file__).resolve().parent.parent / "config" / "modelbus" / "schemas"
    _MODELBUS_SCHEMA_SOURCES = ("upstream", "consumer-contract")
    _MODELBUS_VALIDATION_WARNED_MISSING_LIB = False

    def _validate_against_schema(self, payload: dict[str, Any], schema_name: str) -> list[str]:
        """Validate `payload` against the named schema, trying upstream/ first then consumer-contract/.

        Returns list of human-readable error messages. Empty list means:
          - payload is valid, OR
          - no schema file found on disk (graceful skip), OR
          - jsonschema library not installed (graceful skip with one-time warn).
        """
        try:
            import jsonschema
        except ImportError:
            if not DataPulseReader._MODELBUS_VALIDATION_WARNED_MISSING_LIB:
                logger.warning(
                    "jsonschema not installed; modelbus schema validation skipped. "
                    "Install via: pip install -e '.[governance]'"
                )
                DataPulseReader._MODELBUS_VALIDATION_WARNED_MISSING_LIB = True
            return []

        for source in self._MODELBUS_SCHEMA_SOURCES:
            schema_path = self._MODELBUS_SCHEMAS_DIR / source / f"{schema_name}.json"
            if not schema_path.exists():
                continue
            try:
                schema = json.loads(schema_path.read_text(encoding="utf-8"))
                validator = jsonschema.Draft7Validator(schema)
            except (json.JSONDecodeError, jsonschema.exceptions.SchemaError) as exc:
                return [f"[{source}] {schema_name} schema unloadable: {exc}"]
            errors: list[str] = []
            for err in validator.iter_errors(payload):
                path = "/".join(str(p) for p in err.absolute_path) or "<root>"
                errors.append(f"[{source}] {schema_name} at {path}: {err.message}")
            return errors
        return []
```

Confirm `Path` and `json` and `logger` are already imported at the top of reader.py (grep first):

```bash
grep -nE '^(from pathlib|^import json|^logger\s*=)' datapulse/reader.py | head
```
If `Path` is missing, add `from pathlib import Path`. If `json` missing, add `import json`. (Both almost certainly already present.)

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/test_modelbus_schema_validation.py -v
```
Expected: 5 PASS.

- [ ] **Step 5: Commit**

```bash
git add datapulse/reader.py tests/test_modelbus_schema_validation.py
git commit -m "feat(reader): add _validate_against_schema helper

Loads schemas from config/modelbus/schemas/{upstream,consumer-contract}/
in that order, runs Draft-07 validation, returns human-readable errors.
Gracefully degrades when jsonschema is not installed."
```

---

## Task 5: TDD wire validation into 4 reader sites (warn-only by default)

**Files:**
- Modify: `datapulse/reader.py:1054-1112` (4 existing schema-string check sites)
- Modify: `tests/test_modelbus_schema_validation.py` (add integration tests)

- [ ] **Step 1: Write failing integration tests**

Append to `tests/test_modelbus_schema_validation.py`:

```python
import json
import os
from pathlib import Path


def _write_conformant_bundle(bundle_dir: Path) -> None:
    """Write a 4-file bundle that satisfies both upstream mirrors and DP contracts."""
    bundle_dir.mkdir(parents=True, exist_ok=True)
    # Stub manifest matching the upstream schema's required fields (minimal).
    (bundle_dir / "bundle_manifest.json").write_text(json.dumps({
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
    (bundle_dir / "surface_admission.json").write_text(json.dumps({
        "schema": "modelbus.consumer_surface_admission.v1",
        "consumer_id": "datapulse",
        "generated_at_utc": "2026-05-16T00:00:00Z",
        "surface_admissions": [],
    }))
    (bundle_dir / "bridge_config.json").write_text(json.dumps({
        "schema": "modelbus.consumer_bridge_config.v1",
        "consumer_id": "datapulse",
    }))
    (bundle_dir / "release_status.json").write_text(json.dumps({
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
    # Mutilate surface_admission to miss required field
    sa_path = bundle_dir / "surface_admission.json"
    sa = json.loads(sa_path.read_text())
    del sa["consumer_id"]
    sa_path.write_text(json.dumps(sa))

    monkeypatch.setenv("DATAPULSE_MODELBUS_BUNDLE_DIR", str(bundle_dir))
    monkeypatch.delenv("DATAPULSE_MODELBUS_VALIDATION_MODE", raising=False)  # default = warn

    reader = DataPulseReader()
    with caplog.at_level("WARNING"):
        result = reader._load_modelbus_bundle_surface_admissions()

    # In warn mode, errors list should NOT contain the validation error
    # (basic schema-string check still passes because we only removed consumer_id).
    validation_warnings = [r for r in caplog.records if "consumer_id" in r.getMessage()]
    assert validation_warnings, "expected warn-mode log line mentioning consumer_id"


def test_load_bundle_fail_mode_propagates_validation_errors(tmp_path, monkeypatch):
    """Mode='fail': validation errors are appended to the bundle errors list."""
    bundle_dir = tmp_path / "bundle"
    _write_conformant_bundle(bundle_dir)
    sa_path = bundle_dir / "surface_admission.json"
    sa = json.loads(sa_path.read_text())
    del sa["consumer_id"]
    sa_path.write_text(json.dumps(sa))

    monkeypatch.setenv("DATAPULSE_MODELBUS_BUNDLE_DIR", str(bundle_dir))
    monkeypatch.setenv("DATAPULSE_MODELBUS_VALIDATION_MODE", "fail")

    reader = DataPulseReader()
    result = reader._load_modelbus_bundle_surface_admissions()

    assert result.get("errors"), f"expected errors in fail mode: {result}"
    assert any("consumer_id" in e for e in result["errors"]), result["errors"]
```

- [ ] **Step 2: Run integration tests to verify they fail**

```bash
pytest tests/test_modelbus_schema_validation.py::test_load_bundle_warn_mode_logs_but_does_not_fail tests/test_modelbus_schema_validation.py::test_load_bundle_fail_mode_propagates_validation_errors -v
```
Expected: both FAIL — warn case: no validation warnings (helper not wired in). Fail case: no validation errors in result.

- [ ] **Step 3: Add validation mode constant and wire into 4 sites**

Open `datapulse/reader.py`. Below the constants you added in Task 4 (`_MODELBUS_SCHEMAS_DIR` etc.), add:

```python
    _MODELBUS_VALIDATION_MODE_ENV = "DATAPULSE_MODELBUS_VALIDATION_MODE"
    _MODELBUS_VALIDATION_MODE_DEFAULT = "warn"
```

Add a small helper near `_validate_against_schema`:

```python
    def _record_modelbus_validation(self, errors: list[str], validation_errors: list[str]) -> None:
        """Route validation errors per current mode. In 'warn' (default), log only.
        In 'fail', append to the bundle errors list."""
        if not validation_errors:
            return
        mode = str(os.getenv(self._MODELBUS_VALIDATION_MODE_ENV, self._MODELBUS_VALIDATION_MODE_DEFAULT)).strip().lower()
        if mode == "fail":
            errors.extend(validation_errors)
        else:
            for msg in validation_errors:
                logger.warning("modelbus schema validation: %s", msg)
```

Confirm `os` is imported at top of reader.py (almost certainly yes; if not, add `import os`).

Now wire into the 4 existing sites in `_load_modelbus_bundle_surface_admissions_from_dir`. Locate the block currently at lines 1054-1112. After each `errors.append(...)` schema-string check (4 sites), call the validator. The cleanest patch is to add validation calls **after** the string checks complete but **before** the `if errors:` early-return.

Find lines around 1112-1117:

```python
        if release_status_payload and str(release_status_payload.get("schema") or "").strip() != "modelbus.release_status.v1":
            errors.append("modelbus release status invalid: schema mismatch")

        rows = surface_admission_payload.get("surface_admissions")
```

Insert **between** the release_status check and the `rows = ...` line (after current line 1112, before current line 1114):

```python

        # Schema-validation pass (per-payload). Mode controlled by env;
        # default 'warn' logs without failing the bundle load.
        self._record_modelbus_validation(errors, self._validate_against_schema(
            bundle_manifest, "modelbus.consumer_bundle_manifest.v1"))
        if surface_admission_payload:
            self._record_modelbus_validation(errors, self._validate_against_schema(
                surface_admission_payload, "modelbus.consumer_surface_admission.v1"))
        if bridge_config_payload:
            self._record_modelbus_validation(errors, self._validate_against_schema(
                bridge_config_payload, "modelbus.consumer_bridge_config.v1"))
        if release_status_payload:
            self._record_modelbus_validation(errors, self._validate_against_schema(
                release_status_payload, "modelbus.release_status.v1"))

```

- [ ] **Step 4: Run integration tests to verify they pass**

```bash
pytest tests/test_modelbus_schema_validation.py -v
```
Expected: all 7 tests PASS.

- [ ] **Step 5: Run the rest of the test suite to confirm no regression**

```bash
pytest tests/test_reader.py -v
```
Expected: existing tests still PASS (DP local snapshot may produce warn-mode log lines, but that's expected).

- [ ] **Step 6: Commit**

```bash
git add datapulse/reader.py tests/test_modelbus_schema_validation.py
git commit -m "feat(reader): wire schema validation into 4 bundle payload sites

Per-payload jsonschema validation runs after existing schema-string
checks. Default mode='warn' (logs only); mode='fail' (via env
DATAPULSE_MODELBUS_VALIDATION_MODE=fail) propagates errors into the
bundle errors list, which the existing fail-closed path picks up.

Rollout: ship in warn mode, run for >=7 days, then flip default to fail
(Task 7)."
```

---

## Task 6: Re-pull conformant bundle from MB (Layer 1, operator step)

This task is **operator-executed** (not pure code) because MB owns bundle production. The plan documents the steps so the engineer can either run them locally (if they have MB checkout) or coordinate with MB owner.

**Files:**
- Modify: `config/modelbus/datapulse/bundle_manifest.json` (replaced)
- Modify: `config/modelbus/datapulse/surface_admission.json` (replaced)
- Modify: `config/modelbus/datapulse/bridge_config.json` (replaced)
- Modify: `config/modelbus/datapulse/release_status.json` (replaced)
- Create: `tests/test_local_bundle_snapshot_conformance.py`

- [ ] **Step 1: Trigger MB bundle generation**

On MB checkout (`~/ModelBusProject`):

```bash
cd ~/ModelBusProject
bash scripts/local/verify_assured_release.sh \
  --out out_tmp_datapulse_drift_fix_20260516/assured_deploy \
  --release-level assured \
  --consumer-bundle-batch-manifest docs/examples/consumer-bundle-batch.release-attachment.json
```

If you do not have MB checkout: open issue #9 comment requesting MB owner produce a fresh bundle and attach the 4 JSON files. Pause here until those land in `~/Downloads/` or similar.

- [ ] **Step 2: Copy bundle files into DP**

```bash
# Adjust source path to match what verify_assured_release.sh produced
cp ~/ModelBusProject/out_tmp_datapulse_drift_fix_20260516/assured_deploy/consumer_bundles/datapulse/bundle_manifest.json \
   ~/DataPulse/config/modelbus/datapulse/bundle_manifest.json

cp ~/ModelBusProject/out_tmp_datapulse_drift_fix_20260516/assured_deploy/consumer_bundles/datapulse/surface_admission.json \
   ~/DataPulse/config/modelbus/datapulse/surface_admission.json

cp ~/ModelBusProject/out_tmp_datapulse_drift_fix_20260516/assured_deploy/consumer_bundles/datapulse/bridge_config.json \
   ~/DataPulse/config/modelbus/datapulse/bridge_config.json

cp ~/ModelBusProject/out_tmp_datapulse_drift_fix_20260516/assured_deploy/consumer_bundles/datapulse/release_status.json \
   ~/DataPulse/config/modelbus/datapulse/release_status.json
```

- [ ] **Step 3: Write a conformance test for the local snapshot**

File `tests/test_local_bundle_snapshot_conformance.py`:

```python
"""Assert the committed local bundle snapshot conforms to MB current schema/contract.

Sentinel test: if this fails, run Layer 1 (re-pull from MB) — see
docs/superpowers/plans/2026-05-16-modelbus-bundle-drift-guard.md Task 6.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

pytest.importorskip("jsonschema")

from datapulse.reader import DataPulseReader

REPO_ROOT = Path(__file__).resolve().parent.parent
SNAPSHOT_DIR = REPO_ROOT / "config" / "modelbus" / "datapulse"


@pytest.fixture
def reader(tmp_path, monkeypatch):
    monkeypatch.setenv("DATAPULSE_DB", str(tmp_path / "test.db"))
    return DataPulseReader()


@pytest.mark.parametrize("filename,schema_name", [
    ("bundle_manifest.json", "modelbus.consumer_bundle_manifest.v1"),
    ("surface_admission.json", "modelbus.consumer_surface_admission.v1"),
    ("bridge_config.json", "modelbus.consumer_bridge_config.v1"),
    ("release_status.json", "modelbus.release_status.v1"),
])
def test_local_snapshot_payload_conforms(reader, filename, schema_name):
    payload = json.loads((SNAPSHOT_DIR / filename).read_text())
    errors = reader._validate_against_schema(payload, schema_name)
    assert not errors, (
        f"Local bundle snapshot {filename} drifted from {schema_name}.\n"
        f"Errors:\n  - " + "\n  - ".join(errors) + "\n\n"
        "Fix: re-run MB bundle generation (Task 6 of bundle-drift-guard plan)."
    )
```

- [ ] **Step 4: Run conformance test**

```bash
pytest tests/test_local_bundle_snapshot_conformance.py -v
```
Expected: 4 PASS (if MB bundle was correctly re-pulled). If still FAIL, the bundle MB produced is itself non-conformant — escalate to MB owner before continuing.

- [ ] **Step 5: Commit**

```bash
git add config/modelbus/datapulse/ tests/test_local_bundle_snapshot_conformance.py
git commit -m "chore(modelbus): refresh local bundle snapshot to current MB v1 spec

Replaces 44-day-stale snapshot (generated_at_utc 2026-04-02) with bundle
produced from MB main HEAD on 2026-05-16. Adds tests/test_local_bundle_
snapshot_conformance.py as sentinel to catch future drift."
```

---

## Task 7: Flip Layer 2 default to fail-closed mode

**Prerequisite (revised 2026-05-17, see design §11.2):**

Tasks 1–6 landed AND `scripts/check_modelbus_admission.sh` exits 0 (default: ≥10 validation events since last warn). The original "≥7 days warn-mode soak" criterion was deprecated as a subjective threshold — replaced by the event-based admission gate implemented in `datapulse/core/validation_counter.py`. This aligns with the project rule "事实锚点优先 — 机械化 / 客观化优先于人工".

To check admission status at any time:

```bash
scripts/check_modelbus_admission.sh                  # default min=10
scripts/check_modelbus_admission.sh --min-validations 5   # tune threshold
uv run python -m datapulse.core.validation_counter state  # dump counter JSON
```

Exit 0 = ready to flip; exit 1 = pending. The script writes a one-line GRANTED/PENDING summary to stderr.

Counter state is persisted to `~/.datapulse/modelbus_validation_counter.json` (override via `DATAPULSE_MODELBUS_VALIDATION_COUNTER_PATH` env var, used by tests).

**Files:**
- Modify: `datapulse/reader.py` (change one constant)
- Modify: `tests/test_modelbus_schema_validation.py` (flip default-mode test)

- [ ] **Step 0: Confirm admission**

```bash
scripts/check_modelbus_admission.sh
echo "exit: $?"
```

Expected: exit 0 with `GRANTED: ...` on stderr. If exit 1 (`PENDING: ...`), do not proceed — investigate any non-zero warn count first.

- [ ] **Step 1: Update test to expect fail-mode as default**

Edit `tests/test_modelbus_schema_validation.py`. Change `test_load_bundle_warn_mode_logs_but_does_not_fail` to require explicit `DATAPULSE_MODELBUS_VALIDATION_MODE=warn` for warn behavior:

Replace the line:
```python
    monkeypatch.delenv("DATAPULSE_MODELBUS_VALIDATION_MODE", raising=False)  # default = warn
```
with:
```python
    monkeypatch.setenv("DATAPULSE_MODELBUS_VALIDATION_MODE", "warn")  # explicit opt-in
```

Add a new test:

```python
def test_load_bundle_default_mode_is_fail(tmp_path, monkeypatch):
    """Post-flip default: validation errors propagate without env var."""
    bundle_dir = tmp_path / "bundle"
    _write_conformant_bundle(bundle_dir)
    sa_path = bundle_dir / "surface_admission.json"
    sa = json.loads(sa_path.read_text())
    del sa["consumer_id"]
    sa_path.write_text(json.dumps(sa))

    monkeypatch.setenv("DATAPULSE_MODELBUS_BUNDLE_DIR", str(bundle_dir))
    monkeypatch.delenv("DATAPULSE_MODELBUS_VALIDATION_MODE", raising=False)

    reader = DataPulseReader()
    result = reader._load_modelbus_bundle_surface_admissions()

    assert result.get("errors"), "expected default mode (fail) to surface errors"
    assert any("consumer_id" in e for e in result["errors"]), result["errors"]
```

- [ ] **Step 2: Run tests to verify the new test fails**

```bash
pytest tests/test_modelbus_schema_validation.py::test_load_bundle_default_mode_is_fail -v
```
Expected: FAIL (default is still warn).

- [ ] **Step 3: Flip the default constant**

In `datapulse/reader.py`, change:

```python
    _MODELBUS_VALIDATION_MODE_DEFAULT = "warn"
```

to:

```python
    _MODELBUS_VALIDATION_MODE_DEFAULT = "fail"
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/test_modelbus_schema_validation.py -v
```
Expected: all PASS (warn test now uses explicit env var; default test passes; original fail test still passes).

- [ ] **Step 5: Commit**

```bash
git add datapulse/reader.py tests/test_modelbus_schema_validation.py
git commit -m "feat(reader): flip modelbus schema validation default to fail-closed

Admission gate (scripts/check_modelbus_admission.sh) returned exit 0:
N consecutive validation events since the most recent warn, satisfying
the event-based soak criterion documented in design §11.2. Validation
errors now propagate into the bundle errors list by default. Opt back
into warn mode via env DATAPULSE_MODELBUS_VALIDATION_MODE=warn."
```

---

## Task 8: Drift CI workflow + PAT setup

**Files:**
- Create: `.github/workflows/modelbus-bundle-drift.yml`

- [ ] **Step 1: Create PAT and add as secret**

In a browser:
1. Visit https://github.com/settings/personal-access-tokens/new
2. Create a fine-grained PAT scoped to `sunyifei83/ModelBusProject` with `Contents: Read` only.
3. Set expiration to 365 days; note expiration date in your calendar.
4. Copy the token value.
5. In DP repo settings → Secrets and variables → Actions → New repository secret. Name: `MB_REPO_READ_TOKEN`, value: the token.

If PAT creation is blocked or you want to defer, the workflow file in Step 2 falls back to a `if: ${{ secrets.MB_REPO_READ_TOKEN != '' }}` guard so the workflow no-ops without the secret rather than failing.

- [ ] **Step 2: Author the workflow**

File `.github/workflows/modelbus-bundle-drift.yml`:

```yaml
name: ModelBus Bundle Drift

on:
  schedule:
    # Weekly Monday 14:00 UTC. Adjust if your team prefers a different cadence.
    - cron: '0 14 * * MON'
  pull_request:
    paths:
      - 'config/modelbus/**'
      - 'datapulse/reader.py'
      - '.github/workflows/modelbus-bundle-drift.yml'
  workflow_dispatch:

permissions:
  contents: read
  issues: write  # for opening drift-detected issues on schedule runs

jobs:
  diff-upstream-schemas:
    runs-on: ubuntu-latest
    if: ${{ secrets.MB_REPO_READ_TOKEN != '' }}
    steps:
      - uses: actions/checkout@v4

      - name: Fetch MB-upstream schemas
        env:
          GH_TOKEN: ${{ secrets.MB_REPO_READ_TOKEN }}
        run: |
          mkdir -p /tmp/mb-upstream
          for schema in modelbus.consumer_bundle_manifest.v1.json modelbus.release_status.v1.json; do
            gh api "repos/sunyifei83/ModelBusProject/contents/docs/schemas/${schema}" \
              --jq '.content' | base64 -d > "/tmp/mb-upstream/${schema}"
          done

      - name: Diff against local mirror
        id: diff
        run: |
          set +e
          status=0
          for schema in modelbus.consumer_bundle_manifest.v1.json modelbus.release_status.v1.json; do
            # Normalize key order via jq -S then diff. Non-empty diff fails the step.
            jq -S . "config/modelbus/schemas/upstream/${schema}" > /tmp/local.json
            jq -S . "/tmp/mb-upstream/${schema}" > /tmp/upstream.json
            if ! diff -u /tmp/local.json /tmp/upstream.json > "/tmp/diff-${schema}.txt"; then
              echo "::warning::Drift detected in ${schema}"
              echo "--- DIFF (${schema}) ---"
              cat "/tmp/diff-${schema}.txt"
              status=1
            fi
          done
          exit $status

      - name: Open drift issue on scheduled run
        if: failure() && github.event_name == 'schedule'
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          gh issue create \
            --title "ModelBus schema drift detected (weekly check)" \
            --body "Weekly drift workflow detected upstream schema changes. See run: ${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}. Update mirrors in \`config/modelbus/schemas/upstream/\` and bump pin SHAs in the README." \
            --label "governance,modelbus"

  bundle-snapshot-age:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Inspect snapshot age
        run: |
          generated=$(jq -r .generated_at_utc config/modelbus/datapulse/bundle_manifest.json)
          ts=$(date -u -d "$generated" +%s)
          now=$(date -u +%s)
          age_days=$(( (now - ts) / 86400 ))
          echo "Bundle generated $generated; age=${age_days}d"
          if [ "$age_days" -gt 90 ]; then
            echo "::error::Bundle snapshot is ${age_days} days old (> 90); fail. Re-run Layer 1 of bundle-drift-guard plan."
            exit 1
          elif [ "$age_days" -gt 60 ]; then
            echo "::warning::Bundle snapshot is ${age_days} days old (> 60); consider refresh."
          fi
```

Note on the `if: ${{ secrets.MB_REPO_READ_TOKEN != '' }}` guard: the `diff-upstream-schemas` job is skipped when the secret is absent. The `bundle-snapshot-age` job always runs (uses only local files).

- [ ] **Step 3: Test the workflow via manual dispatch**

After pushing to a branch:
```bash
gh workflow run modelbus-bundle-drift.yml --ref <your-branch>
gh run watch
```

Expected outcomes:
- If mirror matches MB main: `diff-upstream-schemas` PASS, `bundle-snapshot-age` depends on freshness of Task 6's refresh.
- If you intentionally edit the local mirror to introduce a fake diff: `diff-upstream-schemas` FAIL with diff content in logs.

- [ ] **Step 4: Commit**

```bash
git add .github/workflows/modelbus-bundle-drift.yml
git commit -m "ci: add weekly modelbus bundle drift workflow

Diffs config/modelbus/schemas/upstream/ against MB main via cross-repo
PAT (MB_REPO_READ_TOKEN). Also checks local bundle snapshot age.
Scheduled runs open issues on drift; PR runs gate the merge."
```

---

## Out-of-scope (future plans)

- **Renovate auto-PR for mirror SHA bumps** (Layer 4 in spec §4.4). Defer to a follow-up plan once Layer 3 runs for ≥1 month and we have data on actual diff cadence.
- **`source_pin` field consumption** (spec §9 Q2). Pending MB-side acceptance via issue #9 reply. When MB adds the field, modify `bundle-snapshot-age` job to compute commit-distance instead of date age.
- **Migration plan for MB v2 schema introduction** (spec §9 Q3). Write when MB v2 surfaces; uses Expand-Contract pattern.
