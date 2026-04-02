# DataPulse Intent-Aware Research Substrate Blueprint

Status: repo-scoped follow-up blueprint, `L29.1` landing completed

Created: 2026-04-02

Updated: 2026-04-02

## Purpose

This document promotes the `last30days` capability review into repository-scoped blueprint truth.

The goal is not to copy `last30days` into DataPulse as a second product, a second runtime, or another collector bundle.

The goal is to define the next narrow slices that let DataPulse add:

- intent-aware research planning
- Chinese-query relevance uplift
- cross-source evidence stitching
- operator-visible coverage-gap signals

under the same Reader-backed lifecycle, report-layer objects, and governed AI overlay that already exist in-repo.

## Current Repo Read

The repository already has the right substrate pieces:

- `datapulse/core/search_gateway.py`
- `datapulse/reader.py`
- `datapulse/core/watchlist.py`
- `datapulse/core/story.py`
- `datapulse/core/report.py`
- `docs/intelligence_lifecycle_contract.md`
- `docs/governance/datapulse-qnaigc-search-provider-blueprint.md`
- `docs/governance/datapulse-research-os-report-production-blueprint.md`
- `docs/governance/datapulse-modelbus-ai-governance-blueprint.md`

Current repo reality:

- `SearchGateway` already centralizes provider routing and normalized `SearchHit` semantics
- the repo already has platform-aware search and a China-oriented QNAIGC candidate lane
- `WatchMission` already carries intent-facing fields such as `query`, `platforms`, `sites`, and `MissionIntent`
- `Story`, `ReportBrief`, `ClaimCard`, `CitationBundle`, `Report`, and `ExportProfile` already exist as the report-production chain
- governed AI surfaces already exist, but `report_draft` remains intentionally fail-closed

That changes the highest-leverage delta.

The next delta is not more providers, more collectors, or another browser-only research flow.

The next delta is an internal research substrate that sits between today's search or mission intake and tomorrow's claim or report assembly:

`query -> query_intent -> source_plan -> research_packet -> evidence stitching -> coverage_gap -> claim/report inputs`

## Canonical Boundary For This Wave

This wave stays additive and internal-first.

Canonical public lifecycle nouns remain:

- `WatchMission`
- `MissionRun`
- `DataPulseItem`
- `Story`
- `ReportBrief`
- `ClaimCard`
- `CitationBundle`
- `Report`
- `ExportProfile`

The internal research-substrate nouns for this wave are:

- `query_intent`
- `source_plan`
- `research_packet`
- repo-local research `evidence_bundle`
- `coverage_gap`

Boundary rules:

1. these nouns are repo-local working or orchestration nouns only unless a later slice admits them explicitly
2. this wave does not publish a new public AI surface
3. this wave does not admit `web_research` as a public surface
4. this wave does not change `report_draft` from fail-closed to admitted
5. substrate outputs must resolve toward `Story`, `ReportBrief`, `ClaimCard`, and `CitationBundle` instead of bypassing them

## High-Value Facts To Promote

### 1. DataPulse is missing intent-aware research planning above `SearchGateway`

Current repo reality:

- provider routing already exists
- Chinese-query provider candidacy already exists
- mission intent already exists

Repo implication:

- the missing seam is not another provider adapter
- the missing seam is `query_intent -> source/provider/depth/freshness planning`
- this seam should live above `SearchGateway` and below final analyst-facing story or report work

### 2. Chinese-query relevance uplift is higher leverage than collector-count growth

The strongest `last30days-cn` value is not platform breadth. It is:

- core-subject extraction
- compound-term detection
- Chinese stopword and synonym handling
- low-signal filtering
- query-specific routing hints

Repo implication:

- the repo should treat Chinese-query handling as a shared research-planning policy
- it should not reduce this wave to one provider-specific heuristic or one collector-specific patch

### 3. Cross-source stitching belongs in evidence and citation prep, not only in search result display

Current repo reality:

- the report layer now has `ClaimCard` and `CitationBundle`
- story assembly already preserves evidence lineage and contradiction markers

Repo implication:

- cross-source linking should become `evidence stitching`
- the target is not a nicer search result list
- the target is better `Story` assembly and stronger claim or citation binding

### 4. Coverage gaps should become operator-visible research quality signals

Current repo reality:

- DataPulse already exposes ops scorecards, delivery health, and factuality-style review signals

Repo implication:

- missing source perspectives and thin evidence windows should become explicit `coverage_gap` outputs
- those signals should appear before claim or delivery work overstates confidence

### 5. AI should consume substrate hints through existing governed surfaces

Current repo reality:

- `mission_suggest`, `claim_draft`, and `delivery_summary` are admitted
- `report_draft` remains intentionally rejected

Repo implication:

- this wave should first enrich the admitted surfaces with better bounded inputs
- it should not use substrate work as a reason to publish a new surface or to skip contract admission work

## What This Wave Must Preserve

All follow-up slices in this wave must preserve the following constraints:

1. `SearchHit` remains the normalized search result contract
2. `WatchMission`, `Story`, and report-layer nouns remain the canonical public lifecycle objects
3. `research_packet` and repo-local research `evidence_bundle` stay internal staging nouns
4. `coverage_gap` must be operator-visible rather than silently folded into hidden scores
5. cross-source stitching must preserve provenance back to persisted item or story identity
6. AI surfaces may consume substrate hints, but they must still return contract-bound suggestion or draft payloads
7. `report_draft` remains fail-closed until an admitted structured contract exists
8. browser work remains a projection over Reader-backed substrate outputs rather than a second research state machine

## What Should Not Be Reopened In This Wave

This wave should not reopen:

- a collector-count expansion wave as the primary target
- direct import of `last30days` provider or collector implementations
- platform-specific scoring tables as the new repo-wide ranking truth
- setup-wizard or cookie-scanning work as the main storyline
- a GUI-only research packet editor
- direct publication of `web_research` or `report_draft`

Those moves would either duplicate existing repo layers or outrun current governance truth.

## Stage Preview

Recommended stage language for this wave:

- `R0`: current baseline `SearchGateway + WatchMission intent + Story/Report objects + governed AI surfaces`
- `R1`: intent-aware research substrate blueprint and boundary freeze
- `R2`: contract freeze for `query_intent`, `source_plan`, `research_packet`, repo-local research `evidence_bundle`, and `coverage_gap`
- `R3`: search or mission runtime planning plus Chinese-query relevance uplift
- `R4`: cross-source evidence stitching and report-layer intake normalization
- `R5`: AI or operator projection plus verification and reopen hardening

## L29 Slice Map

| Slice | Outcome | Why it exists |
| --- | --- | --- |
| `L29.1` | Land this repo-scoped intent-aware research substrate blueprint and fact promotion | Converts the external `last30days` review into repo truth without pretending the wave is already implemented |
| `L29.2` | Freeze the internal research-substrate contract for `query_intent`, `source_plan`, `research_packet`, repo-local research `evidence_bundle`, and `coverage_gap` | Fixes the nouns and boundaries before search, story, report, or AI runtime work starts drifting |
| `L29.3` | Add intent-aware search planning and Chinese-query relevance policy above `SearchGateway` and mission intake | Lands the highest-leverage routing value without reopening provider-count or collector-count debates |
| `L29.4` | Add cross-source evidence stitching and report-layer intake normalization for `Story`, `ClaimCard`, and `CitationBundle` prep | Turns multi-hit search output into citation-ready evidence rather than display-only dedupe |
| `L29.5` | Project `source_plan` and `coverage_gap` through admitted AI surfaces and operator-visible lifecycle views | Delivers product-facing value through `mission_suggest`, `claim_draft`, `delivery_summary`, and Reader-backed views without opening a new public AI surface |
| `L29.6` | Harden verification, parity, and reopen rules for intent-aware routing, evidence stitching, and coverage-gap semantics | Makes this wave machine-checkable and prevents it from silently degrading into ad hoc search heuristics |

## Recommended Ignition Order After This Refresh

Recommended order after this refresh:

1. `L29.2`
2. `L29.3`
3. `L29.4`
4. `L29.5`
5. `L29.6`

This order keeps the next work narrow:

- first freeze the substrate nouns and boundary rules
- then land routing and relevance policy
- then land evidence stitching
- then project the outputs into admitted AI and operator surfaces
- then harden verification and reopen truth

## L29.1 Landing Note

`L29.1` is now landed in repo truth.

What landed:

- this repo-scoped blueprint records `last30days` as an internal research-substrate extraction rather than as a collector or product import
- the repo now has an explicit `L29` wave for intent-aware research planning, evidence stitching, and coverage-gap projection
- the next manual ignition target after this landing is `L29.2`

Acceptance evidence:

- `test -f docs/governance/datapulse-intent-aware-research-substrate-blueprint.md`
- `python3 -m json.tool docs/governance/datapulse-blueprint-plan.draft.json`
- `python3 -m json.tool docs/governance/datapulse-blueprint-plan.json`

## One-Line Direction

DataPulse should absorb the strongest `last30days` capability as an internal research substrate:

`query intent -> source plan -> evidence stitching -> coverage gap`

It should then feed that substrate into existing mission, claim, citation, and delivery layers without opening a new public AI surface or weakening current fail-closed governance.
