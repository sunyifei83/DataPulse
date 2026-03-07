# DataPulse Structured Release Bundle Draft

Status: draft only, manual and opt-in

Created: 2026-03-07

## Goal

Provide a structured release evidence directory that HA delivery facts can recognize as `structured_release_bundle_available`, without wiring active release workflows.

## Non-Impact Rules

- Export happens only on explicit command.
- Output lives under `out/release_bundle` by default.
- No existing release script, CI workflow, or runtime service path is modified.

## Preferred Export Command

```bash
python3 scripts/governance/export_datapulse_structured_release_bundle.py --probe-ha-readiness
```

## Output Contract

- Directory:
  - `out/release_bundle/`
- Required manifest:
  - `structured_release_bundle_manifest.draft.json`
  - `adapter_bundle_manifest.draft.json`
- Included evidence:
  - `blueprint_plan.snapshot.json`
  - `slice_adapter_catalog.snapshot.json`
  - `code_landing_status.snapshot.json`
  - `evidence_bundle_manifest.draft.json`
  - `ha_delivery_facts.draft.json`
  - `ha_delivery_landing.draft.json`
  - `ha_recovery_preset.draft.json`
  - `release_sidecar.draft.json`
  - `project_specific_loop_state.draft.json`
  - `code_landing_status.draft.json`
  - optionally `release_readiness_fact.draft.json` when `--probe-ha-readiness` is used

## HA Delivery Interaction

- `structured_release_bundle_available()` only becomes true when a recognized manifest exists in `out/release_bundle` or `out/ha_latest_release_bundle`.
- This keeps the `ha_release_structured` gate machine-decidable and avoids false positives from empty directories.
- `.github/workflows/governance-evidence.yml` is the dedicated low-coupling `workflow_dispatch` entrypoint for exporting a bundle in GitHub Actions without changing existing release triggers.
- The same directory is also a valid generic adapter bundle, so governance loop core replay and release evidence export share one artifact root instead of two diverging bundles.
