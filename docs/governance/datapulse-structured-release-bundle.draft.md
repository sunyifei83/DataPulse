# DataPulse Structured Release Bundle Draft

Status: draft only, manual and opt-in

Created: 2026-03-07

## Goal

Provide a structured release evidence directory that HA delivery facts can recognize as `structured_release_bundle_available`, without collapsing evidence-bundle truth into the stable runtime bundle contract.

## Non-Impact Rules

- Export happens only on explicit command.
- The canonical resolver name for this artifact class is `evidence_bundle_root`.
- During compatibility, exporters may still default to `out/release_bundle`.
- No existing release script, CI workflow, or runtime service path is modified.

## Resolver Contract

- `evidence_bundle_root` is the long-term bundle root for structured same-window release evidence.
- `runtime_bundle_root` is a separate resolver and should not be inferred from the structured evidence bundle location.
- `governance_snapshot_root` owns draft loop-state and attestation snapshots that may be copied into the evidence bundle when replay requires them.
- Until `L20.3` and `L20.4` land, legacy compatibility roots remain dual-readable:
  - `out/release_bundle`
  - `out/ha_latest_release_bundle`

The migration contract is:

1. explicit CLI bundle path wins
2. configured `evidence_bundle_root` comes next
3. canonical root from the decoupling contract comes next
4. legacy `out/*release_bundle*` roots remain fallback-only during migration

## Preferred Export Command

```bash
python3 scripts/governance/export_datapulse_structured_release_bundle.py --probe-ha-readiness
```

## Output Contract

- Directory:
  - canonical: `artifacts/governance/release_bundle/`
  - compatibility fallback: `out/release_bundle/`
- Required manifest:
  - `structured_release_bundle_manifest.draft.json`
  - `adapter_bundle_manifest.draft.json`
  - copied runtime bundle files when available:
    - `bundle_manifest.json`
    - `surface_admission.json`
    - `bridge_config.json`
    - `release_status.json`
- Included evidence:
  - `blueprint_plan.snapshot.json`
  - `slice_adapter_catalog.snapshot.json`
  - `code_landing_status.snapshot.json`
  - `datapulse-ai-surface-admission.example.json`
  - `datapulse_surface_runtime_hit_evidence.draft.json`
  - `evidence_bundle_manifest.draft.json`
  - `ha_delivery_facts.draft.json`
  - `ha_delivery_landing.draft.json`
  - `ha_recovery_preset.draft.json`
  - `release_sidecar.draft.json`
  - `project_specific_loop_state.draft.json`
  - `code_landing_status.draft.json`
  - optionally `release_readiness_fact.draft.json` when `--probe-ha-readiness` is used

Runtime bundle files included in the evidence directory are copied evidence that bind the bundle to a concrete runtime payload. They are not, by themselves, the canonical tracked runtime truth.

## HA Delivery Interaction

- `structured_release_bundle_available()` should become true when a recognized manifest exists in the resolved `evidence_bundle_root`, with `out/release_bundle` and `out/ha_latest_release_bundle` retained as migration fallbacks.
- `out/ha_latest_release_bundle` remains a compatibility runtime-bundle fallback during migration, not the long-term canonical root for stable runtime truth.
- Local admission snapshots remain diagnostic-only when the bundle-first default path is evaluated; they are no longer a parallel primary runtime source.
- This keeps the `ha_release_structured` gate machine-decidable and avoids false positives from empty directories.
- `.github/workflows/governance-evidence.yml` is the dedicated low-coupling `workflow_dispatch` entrypoint for exporting a bundle in GitHub Actions without changing existing release triggers.
- The same directory is also a valid generic adapter bundle, so governance loop core replay and release evidence export share one derived evidence root instead of two diverging bundles.
