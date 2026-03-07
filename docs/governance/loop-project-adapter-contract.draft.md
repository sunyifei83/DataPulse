# Loop Project Adapter Contract Draft

Status: draft only, not wired into runtime

Created: 2026-03-07

## Goal

Define the minimum project-side responsibilities needed to plug a repository into the reusable governance loop core.

## Adapter Responsibilities

The project adapter is responsible for exactly these things:

1. load the project blueprint plan
2. collect project landing status
3. load the project slice catalog or workflow map
4. resolve project-specific adapter entries for the current next slice
5. expose project-specific commands, workflows, and evidence paths

The adapter should not re-implement:

- next-slice evaluation
- blocking fact logic
- flow-control classification
- terminal stop semantics
- trust or reuse summaries

Those belong to the core.

## Recommended Surface

- `load_plan()`
- `collect_landing_status()`
- `load_slice_catalog()`
- `resolve_adapter_entry()`
- `build_loop_runtime()`

## DataPulse Draft Landing

The first project adapter draft now lives here:

- `scripts/governance/datapulse_loop_adapter_draft.py`
- `scripts/governance/export_datapulse_loop_adapter_bundle.py`
- `scripts/governance/validate_governance_loop_bundle_draft.py`
- `scripts/governance/verify_datapulse_loop_adoption_draft.py`

It currently wraps:

- DataPulse plan loading
- DataPulse landing-status collection
- DataPulse slice catalog lookup
- core loop-state evaluation and summary generation
- adapter bundle export for core replay

## Why This Matters

This is the line that makes the next repository cheaper:

- keep the core
- replace the adapter

instead of

- copying the whole loop stack
