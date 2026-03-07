# Loop Adapter Bundle Contract Draft

Status: draft only, not wired into runtime

Created: 2026-03-07

## Goal

Define a file-level handoff contract between a project adapter and the reusable governance loop core.

## Why This Layer Exists

The core and the adapter should not need to import each other directly.

A reusable handoff should be possible through a small bundle that contains:

1. a plan snapshot
2. a landing-status snapshot
3. an optional slice catalog
4. a manifest describing those files

This makes the next repository cheaper because the integration point becomes data, not Python module structure.

## Bundle Layout

Recommended files:

- `adapter_bundle_manifest.draft.json`
- `blueprint_plan.snapshot.json`
- `code_landing_status.snapshot.json`
- `slice_adapter_catalog.snapshot.json`

## Manifest Fields

Required fields:

- `schema_version`
- `project`
- `generated_at_utc`
- `bundle_kind`
- `wired`
- `files.plan`
- `files.landing_status`

Optional fields:

- `files.slice_catalog`
- `adapter_metadata`
- `notes`

## Semantics

### Plan Snapshot

The bundle must contain the exact plan snapshot used for evaluation, not only a pointer to the source path.

### Landing Status Snapshot

The bundle must contain the exact landing-status snapshot used for evaluation.

### Slice Catalog

The slice catalog is optional for core evaluation, but recommended when the caller wants project-specific execution hints.

### Read-Only Reproducibility

The bundle should allow a generic core runner to reproduce:

- `next_slice`
- `blocking_facts`
- `remaining_promotion_gates`
- `ready/blocked/stopped`

without importing the project adapter.

## DataPulse Draft Landing

The first draft bundle exporter and bundle runner live here:

- `scripts/governance/export_datapulse_loop_adapter_bundle.py`
- `scripts/governance/run_governance_loop_bundle_draft.py`
- `scripts/governance/validate_governance_loop_bundle_draft.py`

The bundle validator should confirm:

- manifest shape is valid
- referenced files exist
- the bundle can be replayed through the generic core

## Why This Matters

This is the point where reuse stops being:

- "shared ideas"

and becomes:

- "shared control-plane input/output contract"
