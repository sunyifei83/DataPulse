# MB-authoritative schema mirror

This directory contains verbatim copies of JSON Schema documents published by
`sunyifei83/ModelBusProject` at `docs/schemas/`. They are the source of truth
for the payloads DP consumes.

| Schema | MB blob SHA | Pulled |
|---|---|---|
| `modelbus.consumer_bundle_manifest.v1.json` | `84dc243485070785b3dc77474966e00ed9f7a5fd` | 2026-05-16 |
| `modelbus.release_status.v1.json` | `78aa95aac295eb20cf907f6c8371583d03008a09` | 2026-05-16 |

## Refresh policy

- Weekly `.github/workflows/modelbus-bundle-drift.yml` diffs these against MB main.
- On non-additive drift, workflow fails. Operator updates the mirror file +
  bumps the SHA in this table in the same PR.
- Do not edit schema content by hand — always re-fetch via `gh api`.

## Re-fetch commands

To refresh a mirror file and verify the upstream SHA:

```bash
# Replace <FILE> with one of: modelbus.consumer_bundle_manifest.v1.json, modelbus.release_status.v1.json

# Fetch the schema content:
gh api repos/sunyifei83/ModelBusProject/contents/docs/schemas/<FILE> \
  --jq '.content' | base64 -d > config/modelbus/schemas/upstream/<FILE>

# Print the upstream blob SHA (paste into the table above):
gh api repos/sunyifei83/ModelBusProject/contents/docs/schemas/<FILE> --jq '.sha'
```
