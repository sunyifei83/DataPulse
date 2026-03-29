# DataPulse Governance Snapshot Decoupling Contract

Status: draft only, slice `L20.2`

Created: 2026-03-29

## Purpose

Freeze the resolver contract for the `L20` governance snapshot decoupling wave before implementation work begins.

This document does not claim that the new roots are already implemented.

It defines:

1. which root each resolver name owns
2. the precedence order each resolver must follow
3. which artifacts count as tracked runtime truth versus derived same-window evidence

## Resolver Names And Canonical Roots

The repository now reserves three resolver-owned roots:

| Resolver name | Canonical root | Ownership |
| --- | --- | --- |
| `runtime_bundle_root` | `config/modelbus/datapulse/` | Stable tracked runtime bundle truth consumed by `datapulse/reader.py` |
| `governance_snapshot_root` | `artifacts/governance/snapshots/` | Derived loop-state and governance snapshot outputs |
| `evidence_bundle_root` | `artifacts/governance/release_bundle/` | Derived structured release evidence bundle and replay payloads |

These roots are the contract target even if a given directory does not exist yet in the repository.

## Resolution Order

Every runtime, governance, or activation path that participates in this migration must resolve through the same order:

1. explicit CLI argument for the concrete action
2. explicit configured root for that resolver name
3. canonical root from this contract
4. legacy compatibility fallback during migration

Legacy fallback roots remain admissible until `L20.5` retires them:

| Resolver name | Legacy fallback roots |
| --- | --- |
| `runtime_bundle_root` | `out/ha_latest_release_bundle/` |
| `governance_snapshot_root` | `out/governance/` |
| `evidence_bundle_root` | `out/release_bundle/`, `out/ha_latest_release_bundle/` |

`out/ha_latest_release_bundle/` remains dual-readable during migration because current bundle exporters and promotion gates still depend on it, but it is no longer the long-term canonical name for either runtime truth or evidence truth.

## Runtime Truth Versus Derived Evidence

The runtime bundle plane and the evidence plane are different contracts.

### Tracked Runtime Truth

Only low-churn runtime-consumed files belong to `runtime_bundle_root` as source-of-truth artifacts:

- `bundle_manifest.json`
- `surface_admission.json`
- `bridge_config.json`
- `release_status.json` only if its semantics stay stable and non-window-bound

These files may also appear inside a derived evidence bundle as copied evidence, but those copies are not the runtime source of truth.

### Derived Governance Snapshots

The following outputs are same-window governance snapshots and belong to `governance_snapshot_root`, not to tracked runtime truth:

- `activation_intent.draft.json`
- `activation_plan.draft.json`
- `activation_preview.draft.json`
- `auto_continuation_runtime.draft.json`
- `code_landing_status.draft.json`
- `project_specific_loop_state.draft.json`
- `datapulse_release_window_attestation.draft.json`
- `datapulse_surface_runtime_hit_evidence.draft.json`
- `ha_delivery_facts.draft.json`
- `ha_delivery_landing.draft.json`
- `ha_recovery_preset.draft.json`
- `release_readiness_fact.draft.json`
- `release_sidecar.draft.json`
- `slice_execution_brief.draft.json`

### Derived Evidence Bundle

`evidence_bundle_root` owns the structured release evidence directory used for same-window proof, replay, and HA-facing evidence exchange.

Its recognized manifest and payload set may include:

- `structured_release_bundle_manifest.draft.json`
- `adapter_bundle_manifest.draft.json`
- `evidence_bundle_manifest.draft.json`
- `blueprint_plan.snapshot.json`
- `slice_adapter_catalog.snapshot.json`
- copied governance snapshots required for replay or attestation
- copied runtime bundle files required to bind the evidence bundle to a concrete runtime bundle identity

The evidence bundle may contain both runtime-file copies and governance-snapshot copies, but the bundle itself is still derived same-window evidence.

## Required Behavior For Future Implementation Slices

`L20.3` and later slices must preserve these rules:

1. `datapulse/reader.py` resolves `runtime_bundle_root` first and may fall back to `out/ha_latest_release_bundle/` during migration.
2. Governance exporters and loop-state writers resolve `governance_snapshot_root` instead of hardcoding `out/governance/`.
3. Structured release bundle tooling resolves `evidence_bundle_root` instead of treating `out/release_bundle/` or `out/ha_latest_release_bundle/` as the only valid bundle roots.
4. Scheduled governance refresh remains read-only and must not become a business executor.
5. Manual ignition commands stay unchanged; only the underlying root resolution moves.

## Non-Goals

This contract does not:

- create the canonical directories yet
- retire `out/*` fallback paths yet
- change operator-facing ignition commands
- redefine phase or slice semantics

## Exit Statement

`L20.2` is satisfied when repository truth names these resolver-owned roots and freezes that stable runtime bundle files are tracked runtime truth while loop snapshots and structured release bundles remain derived same-window evidence.
