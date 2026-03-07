# DataPulse Loop Adapter Design Draft

Status: draft only, not wired into runtime

Created: 2026-03-07

## Non-Impact Rules

- This folder is additive only.
- No existing script, workflow, CLI entrypoint, or release gate reads these files.
- The JSON files in this folder are draft/example contracts, not active truth sources.
- The future active paths remain recommendations until a later activation change lands.

## Goal

Define a safe bootstrap path for bringing an EquityGuardian-style loop to DataPulse without copying project-specific logic and without blocking the current repository workflow.

## Operating Model Upgrade

The target is not "a loop that never stops."

The target is a loop that:

1. continues blueprint progression without human handoff when the environment is healthy
2. stops on machine-decidable blockers when the environment is abnormal
3. exposes both continuation and stop conditions in machine-readable contracts

That distinction is what separates an auxiliary script from a trusted delivery pipeline.

## Current Repository Facts

- The repository already has a linear delivery workflow covering local verification, remote HA verification, doc refresh, commit, push, CI, and issue capture.
- There is already one machine-readable execution-plan precedent in the repo, but it is feature-specific rather than repo-level loop truth.
- Remote HA evidence can already be normalized into machine-readable emergency gate output.
- Current release automation is split between a local publish script and a tag-driven GitHub release workflow.
- The current repository state is not ready for direct auto-promotion because the workspace was observed dirty during this assessment and several verification scripts are still report-oriented rather than strict gate commands.

## Why The Accumulated Facts Matter

The facts collected so far are not just implementation details. They explain why the current loop draft is still bootstrap infrastructure instead of a trusted pipeline.

- `datapulse_local_smoke.sh` and `datapulse_remote_openclaw_smoke.sh` were originally report-oriented, so L1 had to add strict wrappers before the loop could treat failures as deterministic blockers.
- `quick_test.sh` was not a declared canonical gate, so its signal could not be promoted directly into trusted stop semantics.
- `ci.yml` ignores `docs/**`, so doc-only loop progress cannot automatically gain CI evidence without a dedicated evidence path.
- the release path is split between local script and tag-triggered workflow, so there is still a human relay boundary in promotion evidence.

These are exactly the kinds of gaps that decide whether a loop can progress autonomously under normal conditions and halt deterministically under abnormal conditions.

## Why Not Copy EquityGuardian Directly

The reusable part is the loop shape, not the project semantics.

Reusable core:

- blueprint plan schema
- loop state schema
- code landing status schema
- next-slice driver
- promotion executor skeleton
- projection sync skeleton

DataPulse-specific adapter logic:

- slice definitions for watch, triage, story, ops, and governance work
- verification command set
- HA acceptance policy
- release evidence policy
- markdown projection targets

## Proposed Contract Set

Recommended future active paths:

1. `docs/governance/datapulse-blueprint-plan.json`
2. `out/project_specific_loop_state.json`
3. `out/code_landing_status.json`

Draft files added in this change:

1. `docs/governance/datapulse-blueprint-plan.draft.json`
2. `docs/governance/project_specific_loop_state.example.json`
3. `docs/governance/code_landing_status.example.json`

Prototype manual exporters added in this change:

1. `scripts/governance/export_datapulse_code_landing_status.py`
2. `scripts/governance/export_datapulse_project_loop_state.py`
3. `scripts/governance/export_datapulse_loop_snapshot.py`

These scripts are not called by any existing workflow and only run when invoked explicitly.

Prototype strict wrappers added in this change:

1. `scripts/governance/run_datapulse_local_smoke_gate.py`
2. `scripts/governance/run_datapulse_remote_smoke_gate.py`

These wrappers do not modify the default smoke scripts. They add an opt-in strict exit layer for future loop consumption.

Draft verification contract added in this change:

1. `docs/governance/datapulse-verification-contract.draft.md`

Draft projection target contract added in this change:

1. `docs/governance/datapulse-projection-targets.draft.md`

Draft decoupling principle contract added in this change:

1. `docs/governance/datapulse-loop-decoupling-principles.draft.md`
2. `docs/governance/datapulse-loop-reusable-capabilities.draft.md`
3. `docs/governance/governance-loop-core-contract.draft.md`
4. `docs/governance/loop-project-adapter-contract.draft.md`
5. `docs/governance/loop-adapter-bundle-contract.draft.md`
6. `docs/governance/governance-loop-adoption-playbook.draft.md`
7. `docs/governance/governance-loop-project-scaffold.draft.md`

L4 draft materials added in this change:

1. `docs/governance/datapulse-evidence-workflow.draft.yml`
2. `docs/governance/datapulse-release-sidecar.example.json`
3. `scripts/governance/export_datapulse_release_sidecar.py`
4. `scripts/governance/export_datapulse_evidence_bundle.py`

Blueprint-first driver materials added in this change:

1. `docs/governance/datapulse-slice-adapter-catalog.draft.json`
2. `scripts/governance/run_datapulse_blueprint_loop_draft.py`
3. `scripts/governance/loop_core_draft.py`
4. `scripts/governance/run_governance_loop_core_draft.py`
5. `scripts/governance/datapulse_loop_adapter_draft.py`
6. `scripts/governance/export_datapulse_loop_adapter_bundle.py`
7. `scripts/governance/run_governance_loop_bundle_draft.py`
8. `scripts/governance/validate_governance_loop_bundle_draft.py`
9. `scripts/governance/init_governance_loop_project_scaffold.py`

Working-copy mode materials added in this change:

1. `docs/governance/datapulse-working-copy-mode.draft.md`
2. `scripts/governance/init_datapulse_blueprint_working_copy.py`
3. `scripts/governance/advance_datapulse_blueprint_working_copy.py`

## Contract Intent

### 1. Blueprint Plan

Purpose:

- Single machine-readable source for loop slices.
- Tracks what is completed, what is next, and what promotion mode is allowed.

Producer:

- Human-maintained at bootstrap stage.

Consumer:

- Future DataPulse loop adapter.

### 2. Project Specific Loop State

Purpose:

- Computed loop truth for the repo at one point in time.
- Answers `current_level`, `next_slice`, `remaining_promotion_gates`, and the machine-readable flow-control semantics for continue vs stop.

Producer:

- Future exporter script.

Consumer:

- Future loop driver and projections.

### 3. Code Landing Status

Purpose:

- Normalized truth for workspace cleanliness, local verification, HA evidence, CI evidence, and release evidence.

Producer:

- Future exporter script that aggregates git, artifact reports, emergency gate output, CI facts, and release facts.

Consumer:

- Loop state exporter and promotion logic.

## Reusable Capability Model Extracted From EquityGuardian

The real reusable unit is not a specific script file. It is a control model with four parts:

1. progress truth
2. stop truth
3. reopen truth
4. evidence round-trip

For DataPulse this means:

- `blueprint_plan` carries progress truth
- `project_specific_loop_state` carries stop and reopen truth
- `code_landing_status` carries evidence truth
- the future active driver must re-export after every promotion-relevant action

This is the level at which reuse should happen. Anything lower becomes project-specific copying. Anything higher becomes strategy without execution semantics.

See also:

- `docs/governance/datapulse-loop-reusable-capabilities.draft.md`
- `docs/governance/governance-loop-core-contract.draft.md`
- `docs/governance/loop-project-adapter-contract.draft.md`
- `docs/governance/loop-adapter-bundle-contract.draft.md`
- `docs/governance/governance-loop-adoption-playbook.draft.md`
- `docs/governance/governance-loop-project-scaffold.draft.md`

## Adapter Interface Recommendation

Recommended adapter surface:

- `load_plan()`
- `collect_code_landing_status()`
- `select_next_slice()`
- `verification_commands_for(slice_id)`
- `promotion_workflow_map()`
- `projection_targets()`

## DataPulse-Specific Gate Map

### Local Verification

Candidate inputs:

- `python3 -m compileall datapulse`
- `ruff check datapulse/`
- `mypy datapulse/`
- `pytest tests/ -q`
- `bash scripts/quick_test.sh`
- `bash scripts/datapulse_local_smoke.sh`
- `bash scripts/datapulse_console_smoke.sh`

Current gap:

- `quick_test.sh` is not a canonical gate command set.
- `datapulse_local_smoke.sh` currently behaves as a report generator and should not be treated as a strict gate until its exit semantics are hardened.

### HA Verification

Candidate inputs:

- `bash scripts/datapulse_remote_openclaw_smoke.sh`
- `bash scripts/emergency_guard.sh`
- `bash scripts/release_readiness.sh`

Current gap:

- `datapulse_remote_openclaw_smoke.sh` records failure state in artifacts, but required-step failure semantics are not yet exposed as a strict process gate contract.

### CI Verification

Candidate inputs:

- GitHub `CI` workflow status

Current gap:

- `docs/**` is ignored by CI, so plan/projection-only updates will not automatically produce CI evidence unless workflow policy changes or a separate evidence workflow is added.

### Release Evidence

Candidate inputs:

- `scripts/release_publish.sh`
- GitHub `Release` workflow

Current gap:

- The release path is currently split between local script behavior and tag-triggered workflow behavior.
- No structured release sidecar bundle exists yet for loop re-ingestion.
- No `workflow_dispatch` evidence workflow exists yet.

## Bootstrap Phases

### L0: Contract Drafts

Outcome:

- Establish draft schemas and a repo-local activation plan with no workflow impact.

### L1: Verification Gate Hardening

Outcome:

- Convert report-oriented commands into gateable commands with reliable exit semantics.

Required changes:

- local smoke exits nonzero when mandatory checks fail
- remote smoke exposes required-step failure as nonzero
- canonical verification command set is explicitly declared

Current bootstrap status:

- local smoke strict wrapper added
- remote smoke strict wrapper added
- quick test strict wrapper added
- canonical command contract drafted
- workflow_dispatch evidence path drafted but not activated
- structured release sidecar contract drafted but not activated

### L2: Code Landing Status Exporter

Outcome:

- Export normalized landing truth to `out/code_landing_status.json`.

### L3: Loop State Exporter

Outcome:

- Export `current_level`, `next_slice`, and `remaining_promotion_gates` to `out/project_specific_loop_state.json`.

### L4: Promotion Evidence Unification

Outcome:

- Add a single evidence path suitable for loop promotion.

Required changes:

- workflow-dispatchable evidence workflow
- structured release evidence bundle
- single authoritative release policy

### L5: Driver Integration

Outcome:

- Run DataPulse through a loop driver in `manual_only` mode first.

Activation rule:

- `auto` promotion remains disabled until L1-L4 are closed.

## Trusted Pipeline Threshold

The loop should not be called a trusted delivery pipeline merely because it can compute `next_slice`.

It crosses that threshold only when:

1. healthy-state continuation no longer requires manual relay
2. abnormal-state blockers are machine-decidable and contract-visible
3. the loop can stop safely without losing progression truth
4. the loop can resume by clearing blockers rather than by re-auditing the repo manually

That is why `blocked` must be treated as a valid operating state, not as evidence that the loop failed.

Expected terminal stop matters just as much as continuation:

- the loop should stop cleanly when `next_slice=no-open-slice` and promotion gates are closed
- that stop should be machine-readable
- specific facts should be able to re-open the loop later without human reinterpretation

## Recommended Next Slice

`L4.1 add_workflow_dispatch_evidence_workflow`

Reason:

- Draft contracts, wrappers, exporters, and projection targets now exist.
- The next step is the first one that would intentionally touch current GitHub workflow behavior.

## Activation Rule

Do not activate these contracts by path rename or script integration until all of the following are true:

- a clean workspace is available for validation
- L1 gate hardening is complete
- L2 and L3 exporters exist
- release evidence path is unified enough to support manual promotion review

## Out of Scope For This Draft

- auto-commit
- auto-push
- automatic release publishing
- Obsidian projection wiring
- changing any current CI or release workflow behavior

## Manual Prototype Commands

Dry-run to stdout:

```bash
python3 scripts/governance/export_datapulse_code_landing_status.py --stdout
python3 scripts/governance/export_datapulse_project_loop_state.py --stdout
python3 scripts/governance/export_datapulse_loop_snapshot.py --stdout
```

Draft file export:

```bash
python3 scripts/governance/export_datapulse_loop_snapshot.py
```

Default draft outputs:

- `out/governance/code_landing_status.draft.json`
- `out/governance/project_specific_loop_state.draft.json`

Strict wrapper evaluation without running smoke again:

```bash
python3 scripts/governance/run_datapulse_local_smoke_gate.py --latest-only --json
python3 scripts/governance/run_datapulse_remote_smoke_gate.py --latest-only --json
```

Strict wrapper execution:

```bash
python3 scripts/governance/run_datapulse_local_smoke_gate.py
python3 scripts/governance/run_datapulse_remote_smoke_gate.py
python3 scripts/governance/run_datapulse_quick_test_gate.py
```

Draft release sidecar export:

```bash
python3 scripts/governance/export_datapulse_release_sidecar.py --stdout
python3 scripts/governance/export_datapulse_evidence_bundle.py --stdout
python3 scripts/governance/run_datapulse_blueprint_loop_draft.py
python3 scripts/governance/init_datapulse_blueprint_working_copy.py --stdout
```
