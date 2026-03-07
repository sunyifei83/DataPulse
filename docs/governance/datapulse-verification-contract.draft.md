# DataPulse Verification Contract Draft

Status: draft only, not wired into runtime

Created: 2026-03-07

## Goal

Declare the preferred strict verification commands that a future DataPulse loop should consume, without changing any existing default workflow behavior.

## Non-Impact Rules

- This document is descriptive only.
- It does not change CI, release, readiness, or current developer workflow behavior.
- Existing commands remain unchanged; wrappers are opt-in only.

## Preferred Strict Commands

### Local Baseline

1. `python3 -m compileall datapulse`
2. `bash scripts/datapulse_console_smoke.sh`
3. `python3 scripts/governance/run_datapulse_local_smoke_gate.py`

Interpretation:

- These commands should be treated as strict local gate candidates for a future loop.
- The wrapper command is preferred over calling `scripts/datapulse_local_smoke.sh` directly because it converts the report summary into a reliable process exit code.

### HA Baseline

1. `python3 scripts/governance/run_datapulse_remote_smoke_gate.py`

Interpretation:

- This wrapper is preferred over calling `scripts/datapulse_remote_openclaw_smoke.sh` directly because it converts `failed_steps` into a reliable gate result.

### Promotion Readiness

1. `bash scripts/emergency_guard.sh --rules docs/emergency_rules.json --report <remote_report> --log <remote_log> --out <emergency_state>`
2. `bash scripts/release_readiness.sh --emergency-state <emergency_state> --require-emergency-gate`

Interpretation:

- These commands remain the preferred readiness gate layer once a remote report exists.

## Commands Explicitly Excluded For Now

### `bash scripts/quick_test.sh`

Reason:

- Current semantics still contain swallowed failures and are not yet suitable as a canonical loop gate.

Status:

- keep available for manual developer convenience
- do not treat as future loop truth until normalized

## Strict Replacement Available

### `python3 scripts/governance/run_datapulse_quick_test_gate.py`

Reason:

- Provides a read-only strict wrapper around the reusable parts of quick verification.
- Avoids `--clear` and other mutable behavior from the original convenience script.

Status:

- safe for manual use
- suitable as an opt-in governance gate
- still optional until the project decides whether it belongs in every slice class

## Commands That Stay Contextual

These commands remain valuable but environment-dependent and should be project-policy-driven rather than hardcoded into the first loop adapter:

- `ruff check datapulse/`
- `mypy datapulse/`
- `pytest tests/ -q`
- `bash scripts/release_publish.sh`

## Activation Rule

Do not treat this contract as active until:

- the repository exposes active blueprint and loop-state truth sources
- exporter scripts are promoted from draft to active paths
- the project explicitly chooses whether `ruff` / `mypy` / `pytest` are mandatory on every slice or only on selected slice classes
