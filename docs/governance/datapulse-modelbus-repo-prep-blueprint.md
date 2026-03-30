# DataPulse ModelBus Repo-Prep Blueprint

## Purpose

This document promotes the `2026-03-30` ModelBus feedback note into DataPulse repository truth.

The goal is repo-local ignition preparation only. The goal is not to declare a fresh full shadow integration window while `ModelBus` and `DataPulse` still disagree on the published public AI surface set.

## External Fact Promoted

The external note says DataPulse can move immediately on repo-internal preparation, but should not treat the current `ModelBus` consumer profile as ready for a full same-window shadow closeout.

The repo-specific reason is concrete:

- on `2026-03-29`, `ModelBus` promoted `web_research` into its default surface set
- as of `2026-03-30`, `DataPulse` still exposes only five governed public AI surfaces through repo runtime truth:
  - `mission_suggest`
  - `triage_assist`
  - `claim_draft`
  - `report_draft`
  - `delivery_summary`
- therefore the next repo move is preparation, not premature publication of a sixth surface

## Repo-Specific Reinterpretation

### 1. Preserve bundle-first through DataPulse resolver-owned roots

The external note used `out/ha_latest_release_bundle` language because that was the shared historical intake surface.

DataPulse should not restore that path as canonical repo truth.

After `L20`, the repo-owned interpretation is:

- explicit override first: `DATAPULSE_MODELBUS_BUNDLE_DIR`
- canonical stable runtime bundle root: `config/modelbus/datapulse/`
- canonical same-window evidence bundle root: `artifacts/governance/release_bundle/`
- legacy `out/ha_latest_release_bundle/` and `out/release_bundle/` remain compatibility fallbacks only

That means "bundle-first" remains correct, but the repo-owned canonical roots stay the resolver-owned roots landed in `L20`.

### 2. The published public AI surface set stays at five

Until CLI, contract, and runtime evidence align in the same window, DataPulse should continue to treat only these five as governed public surfaces:

- `mission_suggest`
- `triage_assist`
- `claim_draft`
- `report_draft`
- `delivery_summary`

`web_research` is not a published DataPulse public surface yet.

### 3. `report_draft=verified_fail_closed` remains required runtime closure

This repo must not weaken `report_draft` just to produce a prettier success summary.

The correct readiness rule remains:

- `mission_suggest`, `triage_assist`, `claim_draft`, and `delivery_summary` verify as admitted governed surfaces
- `report_draft` verifies as `verified_fail_closed`

That is valid required runtime closure, not a disguised success state.

### 4. Repo-local preparation can land now

The repo can and should prepare the following immediately:

- machine-readable runtime-hit evidence for all five public surfaces
- same-window attestation that binds all five public surfaces, while preserving `report_draft=verified_fail_closed`
- provenance visibility for:
  - `served_by_alias`
  - `request_id`
  - `degraded`
  - `fallback_used`
  - `schema_valid`
  - `manual_override_required`

The repo can also keep staging internal working-slice nouns without publishing them as new AI surfaces:

- `research_packet`
- `evidence_bundle`
- `ReportBrief`
- `CitationBundle`

Repo read:

- `ReportBrief` and `CitationBundle` are already first-class repo-backed objects
- `research_packet` is the repo-local staging envelope that binds candidate research intake to one `ReportBrief` scope and one or more `CitationBundle` candidates
- repo-local research `evidence_bundle` is the staging package attached to `research_packet`; it is distinct from the governance same-window evidence bundle rooted at `artifacts/governance/release_bundle/`
- `research_packet` and repo-local research `evidence_bundle` stay internal and non-public; they do not widen the admitted DataPulse AI surface set
- `web_research` remains non-public until CLI surface enumeration, contract language, and runtime evidence align in the same window

### 5. What still must not happen in this wave

Do not use this wave to:

- publish `web_research` as a DataPulse public AI surface
- bind provider-specific aliases or downstream provider API keys directly into DataPulse business modules
- bypass `surface_admission`, `release_status`, or runtime facts to infer AI readiness
- retell `research-analysis-primary` as a final report generator

## Internal Research Working-Slice Boundary

`L21.3` fixes the repo-language boundary for internal research staging:

1. `ReportBrief` and `CitationBundle` remain the landed repo-backed objects that downstream report work, CLI views, and governance contracts may name directly.
2. `research_packet` is a repo-local working-slice object only. It may group candidate research intake, report intent, and citation assembly inputs, but it is not a published public AI surface or stable cross-surface contract noun.
3. repo-local research `evidence_bundle` is also a working-slice object only. It may package staging evidence for a `research_packet`, but it is not the same object as the governance same-window evidence bundle written under `artifacts/governance/release_bundle/`.
4. Internal staging nouns may prepare later work around `ReportBrief` and `CitationBundle`, but they must not be used to imply that `web_research` is already admitted or operator-visible as a DataPulse public surface.

## Post-Fix Same-Window Joint-Debug Entry Gate

Once `ModelBus` closes the current mismatch, the next formal joint-debug window may open only when all of the following are true in the same window:

1. DataPulse CLI surface enumeration, lifecycle/AI-governance contract language, and ModelBus bundle truth agree on the same published public AI surface set for the debug window.
2. If that shared surface set is still five, `web_research` remains non-public and may appear only as internal working-slice language.
3. `research_packet` and repo-local research `evidence_bundle` are described as repo-local staging nouns, while `ReportBrief` and `CitationBundle` remain the landed repo-backed objects they feed.
4. same-window machine-readable evidence exists for `mission_suggest`, `triage_assist`, `claim_draft`, `report_draft`, and `delivery_summary`.
5. `mission_suggest`, `triage_assist`, `claim_draft`, and `delivery_summary` are observed as `verified`.
6. `report_draft` is observed as `verified_fail_closed`.
7. `admission_source=modelbus_bundle` is present and visible provenance includes `served_by_alias`, `request_id`, `degraded`, `fallback_used`, `schema_valid`, and `manual_override_required`.
8. No provider-specific aliases or downstream provider API keys are newly bound into DataPulse business modules as part of debug prep.

Only after that gate is satisfied may the same-window joint-debug window discuss whether `web_research` should move from internal staging language into a published DataPulse surface contract.

## L21 Slice Map

| Slice | Outcome | Why it exists |
| --- | --- | --- |
| `L21.1` | Land this repo-scoped repo-prep blueprint and ignition boundary | Converts the external note into DataPulse-owned blueprint truth instead of keeping it as an off-repo reminder |
| `L21.2` | Expand runtime-hit and same-window attestation closure to all five public AI surfaces | Makes local ignition readiness machine-readable before the next external fix window opens |
| `L21.3` | Stage internal research working-slice boundaries and formal post-fix joint-debug entry criteria | Keeps `research_packet` / `evidence_bundle` internal, preserves the five-surface boundary, and writes the next handoff rules explicitly |

## Manual Ignition Handoff

`L21.1`, `L21.2`, and `L21.3` are landed repo truth.

No further manual ignition target remains open inside `L21`.

The next move is loop re-evaluation against the structured blueprint working copy.
