# DataPulse HA Delivery Landing Draft

Status: draft only, not wired into runtime

Created: 2026-03-07

## Goal

Compose two truth layers into one DataPulse-specific landing view:

- reusable activation preview from the governance loop core stack
- project-specific HA delivery facts from the DataPulse adapter

The result should answer whether DataPulse is merely planning repo cutover, or actually closing the machine-decidable bar for high-HA delivery.

## Position In The Stack

This draft sits above:

- `governance_loop_activation_plan.v1`
- `governance_loop_activation_intent.v1`
- `governance_loop_activation_preview.v1`
- `ha_delivery_facts.v1`

It remains project-specific on purpose.

The current emergency recovery route can also be exported separately as:

- `datapulse_ha_recovery_preset.v1`

## Draft Exporter

The exporter lives here:

- `scripts/governance/export_datapulse_ha_delivery_landing.py`

The verifier lives here:

- `scripts/governance/verify_datapulse_ha_delivery_landing.py`

Example:

```bash
python3 scripts/governance/export_datapulse_ha_delivery_landing.py --stdout
python3 scripts/governance/export_datapulse_ha_delivery_landing.py \
  --ha-facts-json out/governance/ha_delivery_facts.draft.json \
  --stdout
```

## What It Decides

This landing view keeps five categories separate:

1. repo-governance cutover surfaces
2. runtime cutover window facts
3. HA runtime blockers
4. HA recovery route
5. release-structuring facts

That separation matters because high-HA delivery does not fail for one generic reason.

It can be delayed because:

- repo-governance wiring is still pending
- runtime cutover timing is unsafe
- the HA chain has not reached the next machine-decidable level
- the emergency stop already knows a recovery route that still has not been executed
- release evidence is still human-oriented instead of structured

## Non-Impact Rules

- This draft does not change any active workflow, readiness gate, or release path.
- If no bundle directory is provided, the exporter derives a temporary adapter bundle and discards it.
- HA fact derivation remains read-only unless `--probe-release-readiness` is explicitly requested.
- This landing view is a DataPulse adapter composition layer, not part of the reusable loop core.

## Why This Matters

This is the first draft fact that answers the real delivery question:

- not only whether loop cutover is planned
- not only whether HA evidence exists
- but whether the repository is actually converging on a machine-decidable high-HA delivery bar
