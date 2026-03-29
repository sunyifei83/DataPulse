# DataPulse Governance Snapshot Decoupling Blueprint

## Purpose

This document defines the root fix for DataPulse governance snapshot churn.

The goal is not to remove governance evidence, weaken release truth, or reopen the completed `L19` wave.

The goal is to separate three different kinds of truth that are currently coupled together under `out/*`:

1. repository blueprint truth
2. runtime-consumed bundle truth
3. same-window governance evidence

That separation is what prevents post-CI closeout refreshes from reopening the repository with a new commit-shaped delta.

## Current Coupling Problem

Current repo reality:

- blueprint and next-slice truth already live in tracked repo documents under `docs/governance/*`
- runtime bundle-first default currently points at `out/ha_latest_release_bundle`
- loop refresh and stop handling currently write tracked snapshots back into `out/governance` and `out/*release_bundle*`
- promotion gates still infer `structured_release_bundle_available` from `out/ha_latest_release_bundle` or `out/release_bundle`

That creates one structural problem:

`out/*` is simultaneously treated as runtime default, governance proof surface, and repository-visible tracked snapshot.

As a result:

- terminal stop refreshes generate tracked diffs even when the repo is already logically complete
- post-push CI closeout can produce a new local delta that is true for the current `HEAD`, but should not become a new `HEAD`
- operator intent becomes ambiguous because "refresh truth" and "create another commit" are no longer clearly separated

## What Must Be Preserved

This migration must preserve the current loop ergonomics:

1. `docs/governance/datapulse-blueprint-plan*.json` remains the canonical blueprint and `next_slice` truth
2. external note intake and blueprint promotion remain valid
3. `bash scripts/governance/ignite_datapulse_codex_loop.sh` remains the operator-facing manual ignition entrypoint
4. scheduled governance refresh stays read-only
5. same-window attestation remains machine-readable, attributable, and fail-closed
6. replayable evidence still exists for manual recovery and audit

## What Must Not Be Reopened

This migration should not reopen:

- phase / slice semantics
- Obsidian-to-blueprint intake flow
- bundle-first runtime semantics for AI surface admission
- release/tag automation scope
- a new parallel governance control plane beside the existing loop

## Target End State

The repository should operate with three clearly separated planes.

### 1. Repo Truth Plane

Tracked and reviewable in `main`.

Owns:

- blueprint plans
- contracts
- slice catalog
- prompt defaults
- stable runtime policy/config

Example locations:

- `docs/governance/*`
- `prompts/*`
- `config/modelbus/datapulse/*`

### 2. Runtime Bundle Plane

Tracked, but intentionally stable and low-churn.

Purpose:

- provide the default runtime bundle-first surface consumed by `datapulse/reader.py`
- carry only the artifacts needed for runtime consumption

Recommended canonical root:

- `config/modelbus/datapulse/`

Target artifact posture:

- `bundle_manifest.json`
- `surface_admission.json`
- `bridge_config.json`
- optionally `release_status.json`, but only if its semantics become stable and non-window-bound

This plane must not require `git_head`, release-window freshness, or timestamp churn in order to stay valid.

### 3. Evidence Plane

Derived, high-churn, and not required to be tracked on `main`.

Purpose:

- prove current same-window promotion truth
- support replay and manual recovery
- feed CI and operator diagnostics

Recommended roots:

- local ignored outputs under `artifacts/governance/`
- CI artifacts / workflow artifacts
- optional dedicated evidence branch if persistent repo-visible history is still required

Expected members:

- `code_landing_status.draft.json`
- `project_specific_loop_state.draft.json`
- `datapulse_release_window_attestation.draft.json`
- `release_sidecar.draft.json`
- `structured_release_bundle_manifest.draft.json`
- `evidence_bundle_manifest.draft.json`
- runtime-hit and HA delivery fact snapshots

## Migration Rule

The migration is successful only when:

- changing same-window evidence no longer requires a new `main` branch commit
- runtime default bundle does not depend on the same files that promotion gates treat as window-bound truth
- manual ignition remains one command

## P0: Compatibility Shell

`P0` is the no-break migration layer.

It does not change operator-facing ignition commands or blueprint intake flow.

### P0.1 Path Resolution Layer

Introduce one resolver layer for governance/evidence paths instead of hardcoded `out/*` defaults.

Required knobs:

- runtime bundle root
- governance snapshot root
- evidence bundle root

Required behavior:

- explicit CLI argument still wins
- configured path comes next
- legacy `out/*` fallback remains available during migration

### P0.2 Dual-Read Compatibility

Update readers, loop scripts, and promotion gates to read through the resolver layer.

Required compatibility:

- runtime bundle load can read the new runtime root first, then fall back to legacy `out/ha_latest_release_bundle`
- attestation and landing exporters can write to alternate roots without changing loop semantics
- activation preview / intent / plan tooling can resolve bundle manifests outside `out/*`

### P0.3 Gate Decoupling

Promotion gates must stop assuming that `out/*` is the only valid evidence root.

Required refactor points:

- `structured_release_bundle_available()`
- release-window attestation lookup
- auto-continuation refresh targets
- Codex loop stop-sync behavior

### P0.4 Ignition Surface Stability

Preserve the existing operator surface:

- `bash scripts/governance/ignite_datapulse_codex_loop.sh`
- `python3 scripts/governance/land_datapulse_blueprint_intake.py ...`

The implementation may move underlying roots, but these commands should not gain new mandatory arguments.

### P0 Acceptance

`P0` is complete when all of the following are true:

1. `run_datapulse_blueprint_loop.py` still resolves the same `next_slice` from the active plan
2. `land_datapulse_blueprint_intake.py` still returns a clean-baseline ignition command
3. the local Codex loop can run with the same wrapper command as today
4. docs-only and non-doc `ci_proven` promotion still work
5. no script requires `out/ha_latest_release_bundle` to be the only admissible bundle root

## P1: Truth Split

`P1` is the actual root fix.

### P1.1 Stable Runtime Bundle Root

Move the default runtime-consumed bundle away from `out/ha_latest_release_bundle`.

Recommended target:

- `config/modelbus/datapulse/`

Required rule:

- runtime bundle files must be stable enough to live in tracked repo truth without forcing same-window refresh churn

### P1.2 Derived Evidence Root

Move window-bound evidence exporters to ignored outputs and CI artifact storage.

Recommended target:

- `artifacts/governance/`

Required rule:

- terminal stop refresh writes derived evidence for local truth, but does not create tracked working-tree churn on `main`

### P1.3 Runtime/Evidence Contract Split

Make runtime bundle and evidence bundle different concepts.

Runtime bundle:

- consumed by `datapulse/reader.py`
- low-churn
- policy/config oriented

Evidence bundle:

- consumed by governance and replay tooling
- high-churn
- includes attestation, loop state, landing status, and same-window proofs

### P1.4 Attestation Binding Shift

Release-window attestation should bind to:

- `git_head`
- workflow run identity
- bundle identity
- artifact path or artifact URL
- optional content hash

It should not require a fresh tracked repo commit just to preserve the attested statement.

### P1 Acceptance

`P1` is complete when all of the following are true:

1. post-push CI closeout does not leave tracked `out/*` deltas in the worktree
2. manual ignition remains a one-command wrapper
3. runtime bundle-first behavior still works in a clean clone
4. same-window attestation remains machine-readable and fail-closed
5. evidence can still be replayed or inspected without relying on a new `main` branch commit

## P2: Legacy Path Retirement

`P2` is optional retirement work after the compatibility layer proves stable.

Retirement steps:

1. remove legacy `out/*` fallback as the default runtime root
2. stop syncing tracked governance snapshots back into repo-visible `out/*`
3. update docs and examples to describe `config/modelbus/datapulse/` as runtime truth and `artifacts/governance/` as derived evidence
4. add `out/governance/`, `out/release_bundle/`, and `out/ha_latest_release_bundle/` to ignore rules if they are no longer intended as tracked repo surfaces

`P2` should happen only after `P0` and `P1` are already proven.

## Impact On Existing Loop And Manual Ignition

This migration should be treated as a compatibility-preserving repo-governance change, not as a new execution wave.

What should stay unchanged for operators:

- the active blueprint still decides `next_slice`
- external fact intake still lands blueprint truth first
- local ignition still begins from the same wrapper command

What changes under the hood:

- bundle and evidence roots become resolved instead of hardcoded
- stop-refresh writes derived truth into the evidence plane rather than reopening tracked repo state
- runtime default no longer depends on the same files that same-window promotion gates continuously rewrite

## Recommended Execution Order

Recommended order:

1. land `P0` path resolution and dual-read compatibility
2. prove that current wrapper commands still work unchanged
3. land `P1` runtime/evidence split
4. verify that post-CI closeout no longer creates tracked churn
5. decide whether `P2` retirement should happen immediately or stay deferred

## One-Line Direction

DataPulse should keep blueprint truth in repo, keep runtime defaults stable and low-churn, move same-window governance evidence into a derived evidence plane, and preserve the current manual ignition interface while removing the commit-shaped churn caused by tracked `out/*` refreshes.
