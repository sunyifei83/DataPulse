# DataPulse consumer-driven contracts

This directory **currently holds no contracts.** As of 2026-05-17 all
ModelBus payload schemas DP consumes have been published as authoritative
JSON Schema documents at `sunyifei83/ModelBusProject:docs/schemas/` and are
mirrored into `../upstream/` instead.

## Migration record (2026-05-17)

Two CDC stand-ins originally lived here:

| Schema | Lifespan | Replaced by |
|---|---|---|
| `modelbus.consumer_surface_admission.v1.json` | 2026-05-16 (PR #50) → 2026-05-17 | `../upstream/` mirror of MB blob `a455f014` |
| `modelbus.consumer_bridge_config.v1.json` | 2026-05-16 (PR #50) → 2026-05-17 | `../upstream/` mirror of MB blob `00fd50f7` |

Both were Pact-style CDC stand-ins (`additionalProperties: true`, only the
fields DP reader.py touched were required) shipped in PR #50 because MB had
not yet published authoritative schemas for these two payloads. MB closed
that gap in commit `9d0a364` (issue #9 follow-up); DP migrated to the
authoritative mirrors and deleted the stand-ins.

The MB authoritative schemas are **strict** (`additionalProperties: false`,
many more required fields). DP's existing local bundle in
`config/modelbus/datapulse/` drifts against them and will surface warns
under `MODELBUS_VALIDATION_MODE=warn`. This drift unblocks only after the
fresh bundle from MB lands (DataPulse issue #51).

## Future use

This directory remains in the schema discovery path
(`datapulse/reader.py:_validate_against_schema` falls back to
`consumer-contract/` after `upstream/`). If MB ever introduces a new
payload tag without publishing an authoritative schema, DP can re-author a
CDC stand-in here pending MB catch-up.
