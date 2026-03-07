# DataPulse HA Recovery Preset Draft

Status: draft only, not wired into runtime

Created: 2026-03-07

## Goal

Turn the current machine-readable emergency recovery route into a replayable preset for the existing remote smoke entrypoint.

## Position In The Stack

This draft sits below:

- `ha_delivery_facts.v1`
- `datapulse_ha_delivery_landing.v1`

It does not replace those facts. It operationalizes the currently selected recovery route.

## Draft Exporter

The exporter lives here:

- `scripts/governance/export_datapulse_ha_recovery_preset.py`

The verifier lives here:

- `scripts/governance/verify_datapulse_ha_recovery_preset.py`

Example:

```bash
python3 scripts/governance/export_datapulse_ha_recovery_preset.py --stdout
python3 scripts/governance/export_datapulse_ha_recovery_preset.py --shell
```

## What It Exports

The preset should make these facts explicit:

- selected route
- catalog match
- supported env assignments
- manual steps that still require operator judgment
- whether the route is executable through `scripts/datapulse_remote_openclaw_smoke.sh`
- whether replay requires a new `RUN_ID`

## Non-Impact Rules

- The exporter is read-only.
- It does not execute the remote smoke itself.
- It only renders the currently observed recovery route into a reusable preset.

## Why This Matters

This is the first point where high-HA recovery stops being just diagnosis.

It becomes a concrete, machine-readable replay contract for the next remote run.

That replay can then be driven by:

- `scripts/governance/run_datapulse_ha_recovery_replay.py`
