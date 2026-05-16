# DataPulse consumer-driven contracts

This directory contains JSON Schemas **authored by DataPulse** for ModelBus
payloads that MB has not yet published as authoritative `.json` schema
documents (only emitted as payload `schema:` tags from
`sunyifei83/ModelBusProject:scripts/ci/build_consumer_bundle.py`).

Contracts here encode **only the fields DP reader.py depends on**, with
`additionalProperties: true` so MB is free to add fields without breaking DP.
This is the classic consumer-driven contract pattern (Pact CDC).

## Files

| Schema | DP-consumed at | MB code reference |
|---|---|---|
| `modelbus.consumer_surface_admission.v1.json` | `datapulse/reader.py:1103-1158` | `build_consumer_bundle.py:207` |
| `modelbus.consumer_bridge_config.v1.json` | `datapulse/reader.py:1107-1110, 1179` | `build_consumer_bundle.py:158` |

## Migration to MB-authoritative

When MB publishes `docs/schemas/modelbus.consumer_{surface_admission,bridge_config}.v1.json`:
1. Mirror them into `../upstream/`.
2. Delete the file here.
3. Reader auto-prefers `upstream/` (see `_validate_against_schema`).
