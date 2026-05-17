# MB-authoritative schema mirror

This directory contains verbatim copies of JSON Schema documents published by
`sunyifei83/ModelBusProject` at `docs/schemas/`. They are the source of truth
for the payloads DP consumes.

| Schema | MB blob SHA | Pulled |
|---|---|---|
| `modelbus.consumer_bundle_manifest.v1.json` | `56c641142d40b4896c4d10f6e2e538362ee82447` | 2026-05-17 |
| `modelbus.consumer_bridge_config.v1.json` | `00fd50f7f0bc37b1a9c35365af48abe4ed211d81` | 2026-05-17 |
| `modelbus.consumer_surface_admission.v1.json` | `a455f0143f1de850d8850c298de91688d79af0d0` | 2026-05-17 |
| `modelbus.release_status.v1.json` | `78aa95aac295eb20cf907f6c8371583d03008a09` | 2026-05-16 |

The two `consumer_{bridge_config,surface_admission}.v1.json` entries replaced
DP-authored consumer-driven contracts from `../consumer-contract/` after MB
published authoritative documents (issue #9 follow-up, MB commit `9d0a364`,
2026-05-17). See `../consumer-contract/README.md` for the migration record.

The `consumer_bundle_manifest.v1.json` mirror picked up MB's only-add
`source_pin` field in the same MB commit. The field is optional; readers
graceful-ignore when absent (per the schema's own field description).

## Refresh policy

- Weekly `.github/workflows/modelbus-bundle-drift.yml` diffs all four
  mirrors against MB main.
- On non-additive drift, workflow fails. Operator updates the mirror file +
  bumps the SHA in this table in the same PR.
- Do not edit schema content by hand — always re-fetch via `gh api`.

## Re-fetch commands

To refresh a mirror file and verify the upstream SHA:

```bash
# Replace <FILE> with one of the schemas listed above.

# Fetch the schema content:
gh api repos/sunyifei83/ModelBusProject/contents/docs/schemas/<FILE> \
  --jq '.content' | base64 -d > config/modelbus/schemas/upstream/<FILE>

# Print the upstream blob SHA (paste into the table above):
gh api repos/sunyifei83/ModelBusProject/contents/docs/schemas/<FILE> --jq '.sha'
```
