# DataPulse Intent-Aware Research Substrate Contract

Status: `L29.2` landed repo contract

Created: 2026-04-02

Updated: 2026-04-02

## Purpose

This contract freezes the internal-only research-substrate nouns introduced by the `L29` wave before runtime work expands `SearchGateway`, `Story`, report-layer intake, or governed AI projections.

The contract of record is:

`query -> query_intent -> source_plan -> research_packet -> repo-local research evidence_bundle -> coverage_gap -> Story / ReportBrief / ClaimCard / CitationBundle inputs`

The public lifecycle does not change. `WatchMission`, `MissionRun`, `DataPulseItem`, `Story`, `ReportBrief`, `ClaimCard`, `CitationBundle`, `Report`, and `ExportProfile` remain the canonical DataPulse nouns.

## Frozen Internal Nouns

| Noun | Frozen role | Owner | Never treat as |
| --- | --- | --- | --- |
| `query_intent` | internal interpretation of one analyst query or mission query in normalized research terms | research-planning layer above `SearchGateway` | a public API/CLI noun, a provider contract, or a replacement for `WatchMission.query` |
| `source_plan` | bounded retrieval plan derived from `query_intent` | research-planning layer above `SearchGateway` | a second search result object, a provider credential surface, or final ranking truth |
| `research_packet` | repo-local staging envelope that binds planned research intake to bounded downstream evidence work | internal research orchestration | a published AI surface, a stable cross-surface payload, or a substitute for `Story` / `ReportBrief` |
| repo-local research `evidence_bundle` | staging package attached to a `research_packet` before report-layer normalization | internal evidence-stitching layer | the governance same-window evidence bundle under `artifacts/governance/release_bundle/` |
| `coverage_gap` | explicit record of missing, weak, contradictory, or blocked evidence coverage | internal research-quality layer with operator-visible projection | a hidden score tweak, admission proof, or a reason to bypass review |

## Object Freeze

### `query_intent`

`query_intent` is the internal read of what the user or mission is actually asking for. It may own:

- topic or entity focus
- task or research objective
- locale or language hints, including Chinese-query handling
- freshness, depth, and source-diversity expectations
- exclusions, ambiguity notes, and known open questions

Contract rules:

- it is derived from explicit operator or mission input; it must not overwrite the original query text
- it lives above `SearchGateway` and below final story or report work
- it may shape retrieval planning, but it is not itself a search result or a public lifecycle noun

### `source_plan`

`source_plan` is the bounded retrieval plan derived from `query_intent`. It may own:

- provider or source-family hints
- platform or site focus
- freshness or time-window targets
- retrieval depth and diversification goals
- evidence-stitching expectations needed before story or claim preparation

Contract rules:

- it is advisory planning input above `SearchGateway`; it does not replace `SearchHit`
- it may produce concrete search parameters, but provider routing and normalized result emission stay inside `SearchGateway`
- it must not become a provider-specific credential or alias surface

### `research_packet`

`research_packet` is the repo-local staging envelope that binds one bounded research attempt to downstream report preparation. It may own:

- one `query_intent`
- one bounded `source_plan`
- candidate `SearchHit`, item, story, or report-intake references
- working notes and provenance needed for evidence stitching
- the intended `ReportBrief` or citation-prep scope

Contract rules:

- it stays internal and repo-local
- it resolves toward `Story`, `ReportBrief`, `ClaimCard`, and `CitationBundle`; it does not replace them
- it must not be projected as a stable Reader / CLI / MCP / browser / API noun in this slice

### repo-local research `evidence_bundle`

Repo-local research `evidence_bundle` is the staging evidence package attached to a `research_packet` before report-layer normalization. It may own:

- candidate evidence references
- provenance annotations
- citation notes and quote candidates
- contradiction or corroboration markers
- staging metadata needed to form later `CitationBundle` or `ClaimCard` inputs

Contract rules:

- it is distinct from the governance same-window evidence bundle written under `artifacts/governance/release_bundle/`
- by itself it is not runtime admission evidence, release proof, or governance snapshot truth
- it exists to preserve provenance while evidence is stitched into landed report-layer nouns

### `coverage_gap`

`coverage_gap` is the explicit record of what the current research pass still does not cover well enough. It may own:

- missing source perspectives
- thin or stale evidence windows
- unresolved contradictions
- blocked retrieval paths or unavailable source classes
- confidence-limiting gaps that should be shown before claim or delivery work overstates certainty

Contract rules:

- it must be operator-visible wherever later slices project it; it must not disappear into hidden ranking or confidence math
- it may inform review and AI suggestions, but it cannot clear quality gates by itself
- it is a research-quality signal, not a new public AI surface

## Ownership Boundaries

### Search and Mission Boundary

- `WatchMission.query`, mission scope, and direct analyst queries remain the source truth for collection intent
- `query_intent` and `source_plan` are internal derivatives of that source truth
- `SearchGateway` continues to own provider routing, retries, fallback order, and normalized `SearchHit` emission

### Story and Report Boundary

- `Story` remains the first canonical evidence package visible in the public lifecycle
- internal substrate nouns may feed `Story`, `ReportBrief`, `ClaimCard`, and `CitationBundle`, but they must not bypass those objects
- cross-source stitching must preserve provenance back to persisted items, stories, URLs, and source identities

### Governed AI Boundary

- admitted surfaces may consume bounded substrate hints through existing lifecycle anchors only
- `mission_suggest`, `claim_draft`, and `delivery_summary` may later project `source_plan` or `coverage_gap` semantics without publishing those nouns as new public surfaces
- `report_draft` remains fail-closed, and this contract does not admit `web_research`

## Consumption Rules

| Consumer | Allowed to consume | Must not do |
| --- | --- | --- |
| `SearchGateway` and mission intake | concrete execution hints derived from `query_intent` or `source_plan` | persist or publish those nouns as the shared search contract |
| `Story` assembly | stitched evidence and explicit coverage-gap signals with preserved provenance | replace story identity with a `research_packet` or hide unresolved gaps |
| report-layer intake | normalized evidence inputs that resolve toward `ReportBrief`, `ClaimCard`, and `CitationBundle` | treat repo-local `evidence_bundle` as a public report object |
| Reader / CLI / MCP / browser / API | later operator-visible projections approved by a separate slice | expose `query_intent`, `source_plan`, `research_packet`, repo-local research `evidence_bundle`, or `coverage_gap` as stable public nouns in `L29.2` |
| governance exporters | repo-truth references to this internal boundary | confuse repo-local research `evidence_bundle` with governance release-bundle artifacts |

## Not Published By This Slice

- no new public AI surface
- no `web_research` admission
- no `report_draft` admission change
- no second lifecycle beside the existing Reader-backed lifecycle
- no replacement of `SearchHit` as the normalized search result contract
- no replacement of `Story`, `ReportBrief`, `ClaimCard`, or `CitationBundle` as the landed evidence and report nouns

## Repo Anchors

- `docs/intelligence_lifecycle_contract.md`
- `docs/governance/datapulse-intent-aware-research-substrate-blueprint.md`
- `docs/governance/datapulse-modelbus-repo-prep-blueprint.md`
- `docs/governance/datapulse-modelbus-ai-governance-blueprint.md`
