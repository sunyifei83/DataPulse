# DataPulse Release Readiness Fact Draft

Status: draft only, manual and opt-in

Created: 2026-03-07

## Goal

Turn `bash scripts/release_readiness.sh` from a one-off terminal probe into a persistent machine-readable fact that can be consumed by HA delivery state without wiring it into active workflows.

## Non-Impact Rules

- This fact is exported only when explicitly requested.
- It does not change the default behavior of `scripts/release_readiness.sh`.
- It does not modify CI, release, or existing service governance entrypoints.

## Preferred Export Command

```bash
python3 scripts/governance/export_datapulse_release_readiness_fact.py
```

Optional explicit source:

```bash
python3 scripts/governance/export_datapulse_release_readiness_fact.py \
  --emergency-state artifacts/openclaw_datapulse_<RUN_ID>/emergency_state.json
```

## Contract

- Schema: `release_readiness_fact.v1`
- Truth source:
  - persistent `emergency_state.json`
  - direct execution of `bash scripts/release_readiness.sh --emergency-state <state> --require-emergency-gate`
- Core fields:
  - `source_emergency_state`
  - `command`
  - `observation.status`
  - `observation.gate_passed`
  - `observation.pass_count`
  - `observation.fail_count`
  - `observation.failed_checks`
  - `machine_blockers`

## HA Delivery Interaction

- `export_datapulse_ha_delivery_facts.py` may consume this fact as a stable readiness truth source.
- This lets `ha_ready` depend on a persisted observation rather than a transient one-off probe.
- If no matching fact exists for the current emergency run, HA delivery facts remain `release_readiness_unobserved`.
