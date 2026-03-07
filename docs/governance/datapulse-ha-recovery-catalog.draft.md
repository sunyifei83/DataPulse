# DataPulse HA Recovery Catalog Draft

Status: draft only, not wired into runtime

Created: 2026-03-07

## Goal

Define stable, named HA recovery presets so the adapter can refer to preset identities instead of only raw action strings.

## Draft Catalog

The catalog lives here:

- `docs/governance/datapulse-ha-recovery-catalog.draft.json`

## Why This Matters

This is the point where recovery routes stop being ephemeral diagnosis output and become reusable, named contracts.

That lets the adapter answer:

- which preset the current blocker resolves to
- whether the current route exactly matches a known preset
- whether replay is happening against a stable contract or an ad-hoc route
