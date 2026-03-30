# DataPulse Release-Window Attestation Contract

## Purpose

This document is the contract of record for `L17.2`.

It defines the machine-readable attestation shape that binds one declared release window to:

- bundle identity
- AI runtime-hit evidence
- release sidecar truth
- replay entrypoint binding

The contract is fail-closed. Missing, stale, cross-head, or cross-bundle evidence must produce `attestation_status=blocked` rather than a permissive summary.

The companion machine-readable artifact for this slice is:

- `docs/governance/datapulse-release-window-attestation.example.json`

`L17.3` should emit this shape without changing existing runtime semantics.

## Scope

This contract covers:

- one attestation payload per declared release window
- fields that bind bundle, runtime-hit, sidecar, and replay evidence into one statement
- fail-closed checks for missing evidence and same-window mismatches
- freshness checks for source timestamps and inter-source skew

This contract does not cover:

- new AI surface semantics
- new release readiness scores beyond existing source artifacts
- automatic workflow execution
- recomputing runtime semantics instead of binding existing exported facts

## Source Artifacts To Bind

The attestation must bind the currently exported facts instead of inventing parallel truth:

| Source | Required role in attestation |
| --- | --- |
| `structured_release_bundle_manifest.draft.json` | declares the canonical bundle directory and bundle file set |
| `bundle_manifest.json` | declares the generic consumer bundle identity |
| `datapulse_surface_runtime_hit_evidence.draft.json` | proves runtime-hit closure and names the runtime replay entrypoint |
| `release_sidecar.draft.json` | provides git head, release readiness, and bundle availability truth |
| `validate_governance_loop_bundle_draft.py` | provides the generic core replay entrypoint for the same bundle |
| `run_datapulse_ha_recovery_replay.py` | remains the named manual replay wrapper for remote smoke recovery |

## Canonical Payload

The attestation payload must use:

- `schema_version = datapulse_release_window_attestation.v1`
- `attestation_status = attested | blocked`

Normative top-level shape:

```json
{
  "schema_version": "datapulse_release_window_attestation.v1",
  "project": "DataPulse",
  "generated_at_utc": "<RFC3339 UTC>",
  "window_id": "<stable release-window id>",
  "git_head": "<git sha>",
  "attestation_status": "attested",
  "blocking_reasons": [],
  "same_window": {
    "required": true,
    "same_head_required": true,
    "same_bundle_dir_required": false,
    "same_runtime_bundle_required": true,
    "proven": true,
    "reasons": []
  },
  "freshness": {
    "max_source_age_seconds": 900,
    "max_inter_source_skew_seconds": 300,
    "all_sources_fresh": true,
    "max_observed_skew_seconds": 0,
    "sources": []
  },
  "bundle_identity": {},
  "runtime_hit_evidence": {},
  "release_sidecar_truth": {},
  "replay_binding": {}
}
```

## Required Fields

| Field | Required meaning |
| --- | --- |
| `generated_at_utc` | timestamp when the attestation itself was emitted |
| `window_id` | stable identifier for exactly one declared release window; later review notes and bundle attachments must reuse it verbatim |
| `git_head` | canonical git head for the attested window |
| `attestation_status` | `attested` only when every required check passes; otherwise `blocked` |
| `blocking_reasons` | non-empty when `attestation_status=blocked`; empty when `attestation_status=attested` |
| `same_window` | explicit proof summary that bundle, runtime-hit evidence, sidecar truth, and replay binding all point at the same window |
| `freshness` | explicit source-age and source-skew checks for the bound artifacts |

## Bundle Identity Section

`bundle_identity` must include:

- `bundle_dir`
- `structured_manifest_path`
- `structured_manifest_generated_at_utc`
- `adapter_bundle_manifest_path`
- `bundle_manifest_path`
- `bundle_id`
- `consumer_id`
- `bundle_files`

Required checks:

1. `bundle_dir` is the canonical directory being attested.
2. `structured_manifest_path` and `bundle_manifest_path` must both exist.
3. `bundle_files` must include the runtime-hit evidence file and release sidecar file named by the attestation.
4. The replay entrypoint in `replay_binding.primary_bundle_replay.bundle_dir` must match `bundle_identity.bundle_dir`.

## Runtime-Hit Evidence Section

`runtime_hit_evidence` must include:

- `path`
- `schema_version`
- `generated_at_utc`
- `bundle_default_strategy`
- `runtime_bundle_dir`
- `closure_replay_entrypoint`
- `required_surfaces`
- `release_level_prerequisites`

Each `required_surfaces[]` row must include:

- `surface`
- `expected_evidence_status`
- `observed_evidence_status`
- `release_scope`
- `request_id`
- `served_by_alias`
- `satisfied`

Runtime rules:

1. `bundle_default_strategy` must be `bundle_first`.
2. `runtime_bundle_dir` must equal `bundle_identity.runtime_bundle_source_dir`.
3. `mission_suggest` must be present with `expected_evidence_status=verified` and `observed_evidence_status=verified`.
4. `triage_assist` must be present with `expected_evidence_status=verified` and `observed_evidence_status=verified`.
5. `claim_draft` must be present with `expected_evidence_status=verified` and `observed_evidence_status=verified`.
6. `report_draft` must be present with `expected_evidence_status=verified_fail_closed` and `observed_evidence_status=verified_fail_closed`.
7. `delivery_summary` must be present with `expected_evidence_status=verified` and `observed_evidence_status=verified`.
8. `report_draft` fail-closed evidence is valid required runtime closure and must not be rewritten as a success-only admission state.
9. `closure_replay_entrypoint` is required and must remain visible in the attestation.

## Release Sidecar Truth Section

`release_sidecar_truth` must include:

- `path`
- `schema_version`
- `generated_at_utc`
- `release_tag`
- `git_head`
- `workspace_clean`
- `structured_release_bundle_available`
- `runtime_hit_evidence_available`
- `required_change_prerequisites_met`
- `promotion_discussion_allowed`
- `promotion_readiness_reasons`

Sidecar rules:

1. `release_sidecar_truth.git_head` must equal top-level `git_head`.
2. `structured_release_bundle_available` must be `true`.
3. `runtime_hit_evidence_available` must be `true`.
4. `required_change_prerequisites_met` must be `true`.
5. `promotion_readiness_reasons` must stay empty for `attestation_status=attested`.

## Replay Binding Section

`replay_binding` must include:

- `primary_bundle_replay`
- `runtime_hit_replay`
- `ha_recovery_replay`

`primary_bundle_replay` must include:

- `kind`
- `entrypoint`
- `bundle_dir`
- `expected_result`

`runtime_hit_replay` must include:

- `kind`
- `entrypoint`
- `bundle_dir`
- `expected_result`

`ha_recovery_replay` must include:

- `kind`
- `entrypoint`
- `manual_execute_entrypoint`
- `expected_result`

Replay rules:

1. `primary_bundle_replay.entrypoint` must point at generic core bundle replay for the same `bundle_dir`.
2. `runtime_hit_replay.entrypoint` must point at the runtime-hit exporter for the same `bundle_dir`.
3. `ha_recovery_replay` remains manual-only; the attestation binds its entrypoint for attribution and rerun visibility, not for scheduled execution.

## Freshness Rules

`freshness` must include:

- `max_source_age_seconds`
- `max_inter_source_skew_seconds`
- `all_sources_fresh`
- `max_observed_skew_seconds`
- `sources`

Each `sources[]` row must include:

- `source`
- `path`
- `generated_at_utc`
- `age_seconds`
- `fresh`

Freshness checks are fail-closed:

1. every bound source must expose a parseable UTC `generated_at_utc`
2. no source timestamp may be later than the attestation timestamp
3. every `age_seconds` must be less than or equal to `max_source_age_seconds`
4. `max_observed_skew_seconds` must be less than or equal to `max_inter_source_skew_seconds`
5. `all_sources_fresh` must be `true` for `attestation_status=attested`

Recommended initial policy for `L17.3`:

- `max_source_age_seconds = 900`
- `max_inter_source_skew_seconds = 300`

## Fail-Closed Reasons

The attestation must use machine-readable blocker strings. At minimum, the exporter must be able to emit:

- `missing_bundle_manifest`
- `missing_runtime_hit_evidence`
- `missing_release_sidecar`
- `missing_primary_bundle_replay`
- `missing_runtime_hit_replay`
- `bundle_runtime_dir_mismatch`
- `git_head_mismatch`
- `mission_suggest_not_verified`
- `triage_assist_not_verified`
- `claim_draft_not_verified`
- `delivery_summary_not_verified`
- `report_draft_not_verified_fail_closed`
- `structured_release_bundle_not_available`
- `required_runtime_prerequisites_not_met`
- `source_timestamp_missing`
- `source_timestamp_in_future`
- `source_stale`
- `source_time_skew_exceeded`

## Same-Window Proof

`same_window.proven=true` is allowed only when all of the following are true:

1. top-level `git_head` matches `release_sidecar_truth.git_head`
2. `bundle_identity.runtime_bundle_source_dir` matches `runtime_hit_evidence.runtime_bundle_dir`
3. `bundle_identity.bundle_dir` matches `replay_binding.primary_bundle_replay.bundle_dir`
4. `runtime_hit_evidence.closure_replay_entrypoint` matches `replay_binding.runtime_hit_replay.entrypoint`
5. freshness checks pass for every bound source
6. `blocking_reasons` is empty

Otherwise:

- `same_window.proven` must be `false`
- `attestation_status` must be `blocked`

## Slice Outcome

`L17.2` is complete when the repository contains this contract and the companion example payload, and the active blueprint truth advances the next manual ignition target to `L17.3`.
