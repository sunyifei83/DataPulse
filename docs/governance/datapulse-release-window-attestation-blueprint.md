# DataPulse Release-Window Attestation Blueprint

## Purpose

This document promotes the next follow-up wave after the completed `L16` AI-runtime work into repository-scoped blueprint truth.

The goal is not to reopen bundle adapter design or invent new AI runtime semantics. The goal is to bind the already-landed facts into one same-window attestation artifact that promotion, replay, and manual review can trust.

## Current Repo Read

DataPulse already has the core runtime facts needed for a formal release-window attestation:

- bundle-first admission is the default runtime path
- `delivery_summary` has verified runtime-hit evidence
- `report_draft` has verified fail-closed runtime-hit evidence
- release readiness is already summarized in `release_sidecar.draft.json`
- structured release bundles already carry bundle, runtime-hit, and sidecar artifacts

Current repo anchors:

- `out/governance/datapulse_surface_runtime_hit_evidence.draft.json`
- `out/governance/release_sidecar.draft.json`
- `out/ha_latest_release_bundle/structured_release_bundle_manifest.draft.json`
- `docs/governance/datapulse-structured-release-bundle.draft.md`
- `docs/governance/datapulse-ai-surface-admission-contract.md`
- `scripts/governance/export_datapulse_surface_runtime_hit_evidence.py`
- `scripts/governance/export_datapulse_release_sidecar.py`
- `scripts/governance/export_datapulse_structured_release_bundle.py`

That changes the next highest-leverage delta.

The repository does not need another debate about whether bundle-first consumption is real. The next delta is to make one release window produce one formal attestation that can be replayed, reviewed, and promoted without stitching several files together by hand.

## What This Wave Must Preserve

Invariants for this wave:

1. release-window attestation binds existing facts; it does not reinterpret runtime semantics
2. `report_draft = verified_fail_closed` remains valid required runtime closure, not a disguised successful draft capability
3. local snapshot fallback remains diagnostic context, not the attested primary runtime source
4. same-window identity must be explicit through fields such as `window_id`, `git_head`, `generated_at_utc`, and bundle identity
5. replay entrypoints must stay visible so the attested statement can be attributed and rerun
6. missing bundle, runtime-hit evidence, or sidecar truth must fail closed instead of yielding a "looks ready" summary

## High-Value Facts To Promote

### 1. Runtime closure is no longer the main gap

Current repo reality:

- the `L16` wave already closed the runtime path for bundle-first admission and delivery/report evidence

Repo implication:

- the follow-up wave should center on release-window attestation, not on reopening runtime enablement slices

### 2. Promotion still relies on manually correlating several artifacts

Current repo reality:

- bundle manifests, runtime-hit evidence, sidecar summaries, and replay commands already exist, but they are not yet bound as a single same-window assertion

Repo implication:

- one exporter and one contract should make that binding explicit

### 3. Same-window truth matters more than more summaries

Current repo reality:

- the repo already has multiple readiness summaries

Repo implication:

- the next artifact should emphasize `same_window`, `same_head`, and replayability rather than inventing another independent readiness scorecard

## What Should Not Be Reopened In This Wave

This wave should not reintroduce:

- a second bundle adapter design discussion
- new AI surface semantics
- alternate success semantics for `report_draft`
- provider-routing logic inside DataPulse
- a separate attestation runtime path outside the current bundle and governance exporters

## L17 Slice Map

| Slice | Outcome | Why it exists |
| --- | --- | --- |
| `L17.1` | Land this repo-scoped release-window attestation blueprint and manual ignition map | Converts the current next-step judgment into active repo truth before exporter or gate work reopens |
| `L17.2` | Define the release-window attestation contract and example payload | Makes bundle, runtime-hit, sidecar, replay, and same-window identity machine-readable and fail-closed |
| `L17.3` | Add a single release-window attestation exporter and attach it to the structured bundle | Produces one attributable artifact per window instead of several loosely related files |
| `L17.4` | Harden promotion and replay gates around attestation freshness and same-window consistency | Makes manual promotion and replay read attestation truth first, while preserving fail-closed semantics |

## Manual Ignition Handoff

`L17.2` is the contract-freeze slice for this wave. Once the contract document and companion example payload are present in repo truth, the next manual ignition target should move to `L17.3`.

Recommended order after `L17.2` lands:

1. `L17.3`
2. `L17.4`

This handoff keeps the next work narrow:

- first emit one attestation artifact and attach it to the canonical bundle
- then harden gates and tests around the new attestation artifact

## One-Line Direction

`DataPulse` should treat release-window attestation as the next primary follow-up: bind bundle, runtime-hit, release sidecar, and replay entrypoint into one same-window artifact, and stop spending planning energy on whether bundle-first consumption is already real.
