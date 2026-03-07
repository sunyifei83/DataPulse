# DataPulse HA Delivery Facts Draft

Status: draft only, not wired into runtime

Created: 2026-03-07

## Goal

Export a DataPulse-specific fact view for high-HA delivery without mixing project HA semantics into the reusable loop core.

## Scope

This fact view is intentionally project-specific. It tracks:

- latest remote smoke observation
- emergency gate observation
- emergency recovery route
- optional release readiness probe
- structured release evidence availability

It does not decide generic loop control semantics.

## Draft Exporter

The exporter lives here:

- `scripts/governance/export_datapulse_ha_delivery_facts.py`

The verifier lives here:

- `scripts/governance/verify_datapulse_ha_delivery_facts.py`
- `scripts/governance/export_datapulse_ha_delivery_landing.py`

Example:

```bash
python3 scripts/governance/export_datapulse_ha_delivery_facts.py --stdout
python3 scripts/governance/export_datapulse_ha_delivery_facts.py --probe-release-readiness --stdout
```

## Delivery Levels

The draft levels are:

1. `ha_observed`
2. `ha_guarded`
3. `ha_ready`
4. `ha_release_structured`

Interpretation:

- `ha_observed` means the latest remote smoke fact is present and passing.
- `ha_guarded` means the emergency gate fact is also passing.
- `ha_ready` means release readiness has been explicitly observed and passed.
- `ha_release_structured` means the release evidence path is also structured enough for round-trip reuse.

## Recovery Semantics

If the emergency gate blocks, this fact view should also expose:

- `first_trigger`
- `blocker_codes`
- whether a new `run_id` is required
- the machine-readable primary and secondary recovery actions

That makes HA stop facts actionable instead of merely descriptive.

## Non-Impact Rules

- Emergency-state rehydration is temporary and does not write persistent repo artifacts.
- If emergency-state rehydration fails, the exporter should surface a concrete machine fact rather than a generic missing-state placeholder.
- Release-readiness probing is opt-in because it runs the existing readiness script explicitly.
- No active workflow, CI, release path, or default smoke behavior is changed.

## Why This Matters

This gives DataPulse a dedicated HA-delivery truth layer:

- stronger than prose
- narrower than the full loop state
- still decoupled from the reusable control plane

That truth layer now feeds a second DataPulse-specific landing view:

- `datapulse_ha_delivery_landing.v1`
- `datapulse_ha_recovery_preset.v1`

The landing view composes HA facts with activation preview so repo cutover facts and HA runtime blockers remain separate.

The recovery preset operationalizes the currently selected route into a replayable remote-smoke contract.
