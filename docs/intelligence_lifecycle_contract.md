# Intelligence Lifecycle Contract

## Purpose

This document defines the canonical DataPulse intelligence lifecycle that now spans recurring mission execution, inbox triage, story assembly, structured report production, and the governed AI-assistance overlay attached to those layers.

It is the contract of record for `L6.1`, the report-production anchor of `L14.2`, and the AI surface/switch anchor of `L16.2`. It must align Reader, CLI, MCP, and browser console work to one progression and one source of truth.

## Scope

This contract covers the shared lifecycle semantics for:

- `WatchMission`
- `MissionRun`
- `DataPulseItem` review and triage state
- `Story` and evidence packaging
- report production objects: `ReportBrief`, `ClaimCard`, `ReportSection`, `CitationBundle`, `Report`, `ExportProfile`
- `AlertEvent` and named-route delivery health as the current delivery surface
- `Report` and `ExportProfile` as the authoritative delivery basis for report-layer outputs
- AI assistance surface contracts and `off` / `assist` / `review` switch semantics for watch, triage, report, and delivery work

The repo now ships report-domain persistence plus Reader / CLI / MCP / browser-API runtime surfaces. This contract therefore records the authoritative lifecycle for landed layers and states which AI/runtime paths remain intentionally fail-closed.

## Current Landing Posture

- report-domain objects are repo-backed in `datapulse/core/report.py` and projected through `datapulse/reader.py`, `datapulse/cli.py`, `datapulse/mcp_server.py`, and `datapulse/console_server.py`
- governed AI runtime projections are also repo-backed; current admission truth admits `mission_suggest`, `triage_assist`, `claim_draft`, and `delivery_summary`
- `report_draft` already has Reader / CLI / MCP / console runtime parity, but remains intentionally rejected / fail-closed until an admitted structured contract exists

## Current Repo Anchors

| Lifecycle step | Canonical object(s) | Repo anchors |
| --- | --- | --- |
| Mission intent | `WatchMission` | `datapulse/core/watchlist.py`, `datapulse/reader.py` |
| Mission execution | `MissionRun` | `datapulse/core/watchlist.py`, `datapulse/core/scheduler.py` |
| Triage queue | `DataPulseItem`, `review_state`, `review_notes`, `review_actions`, `duplicate_of` | `datapulse/core/models.py`, `datapulse/core/triage.py` |
| Story assembly | `Story`, `StoryEvidence`, `StoryTimelineEvent`, `StoryConflict` | `datapulse/core/story.py` |
| Report production (landed additive layer) | `ReportBrief`, `ClaimCard`, `ReportSection`, `CitationBundle`, `Report`, `ExportProfile` | `datapulse/core/report.py`, `datapulse/reader.py`, `datapulse/cli.py`, `datapulse/mcp_server.py`, `datapulse/console_server.py`, `docs/governance/datapulse-research-os-report-production-blueprint.md` |
| Delivery and ops | `AlertEvent`, named alert routes, route health, ops snapshot | `datapulse/core/alerts.py`, `datapulse/reader.py` |
| Report-backed delivery | `Report`, `ExportProfile` | `docs/intelligence_delivery_contract.md`, `docs/governance/datapulse-report-delivery-subscription-blueprint.md`, `datapulse/core/report.py` |
| AI assistance overlay (governed runtime layer) | `mission_suggest`, `triage_assist`, `claim_draft`, `report_draft`, `delivery_summary`; `off`, `assist`, `review` | `datapulse/reader.py`, `datapulse/cli.py`, `datapulse/mcp_server.py`, `datapulse/console_server.py`, `docs/governance/datapulse-modelbus-ai-governance-blueprint.md`, `out/ha_latest_release_bundle/datapulse-ai-surface-admission.example.json` |

## Canonical Lifecycle

```text
WatchMission
  -> MissionRun
  -> DataPulseItem queue entries
  -> triage decisions and reviewer notes
  -> Story / evidence package
  -> ReportBrief
  -> ClaimCard
  -> ReportSection
  -> Report
  -> ExportProfile
  -> brief / full / source / watch_pack outputs
  -> delivery subscription mapping by output kind and route observation
```

The lifecycle is additive, not branchless:

- one `WatchMission` can produce many `MissionRun` records
- one `MissionRun` can emit many `DataPulseItem` records
- triage can suppress, verify, or escalate items before and during story assembly
- one `Story` can aggregate items from multiple runs and multiple sources
- one `Story` may be the evidence basis for multiple `ReportBrief` planning units
- one `Report` can be exported through multiple `ExportProfile` shapes
- delivery can consume either mission-level alert facts, profile scope pull outputs, or report outputs

AI assistance is also additive:

- AI surfaces attach to existing lifecycle objects; they do not create a second object chain.
- one lifecycle object may have zero or many AI suggestion or draft payloads over time.
- AI outputs remain subordinate to operator and deterministic authority even when review workflows are enabled.

## Object Contract

### 1. Mission intent: `WatchMission`

`WatchMission` is the durable expression of recurring analyst intent. It owns:

- mission identity: `id`, `name`
- collection scope: `query`, `platforms`, `sites`
- execution policy: `schedule`, `enabled`
- selection thresholds: `min_confidence`, `top_n`
- downstream alert intent: `alert_rules`
- latest execution summary: `last_run_at`, `last_run_count`, `last_run_status`, `last_run_error`
- bounded recent history: `runs`

Contract rules:

- `WatchMission` is the only lifecycle object that represents standing collection intent.
- surfaces must use the same mission identifier across `Reader`, CLI, MCP, and console.
- mutating alert rules belongs to the mission layer, not the delivery layer.

### 2. Mission execution: `MissionRun`

`MissionRun` is the immutable record of one mission execution attempt. It owns:

- `mission_id`
- `status`
- `item_count`
- `trigger`
- `error`
- `started_at`
- `finished_at`
- `id`

Contract rules:

- each run records execution truth even when no useful items are produced.
- failed runs must not fabricate triage, story, or delivery state transitions.
- run history is operational evidence for retry guidance, daemon status, and mission audit.

### 3. Triage queue: `DataPulseItem` review state

Mission output enters the inbox as `DataPulseItem` records, then passes through the triage contract:

- states: `new`, `triaged`, `verified`, `duplicate`, `ignored`, `escalated`
- notes: reviewer commentary attached through `review_notes`
- actions: state transitions attached through `review_actions`
- duplicate linkage: `duplicate_of`

Contract rules:

- triage is the only lifecycle layer allowed to mark an item `duplicate` or `ignored`.
- `verified`, `duplicate`, and `ignored` are terminal review states in current repo semantics.
- `duplicate` and `ignored` items are excluded from digest/story candidate flow.
- `verified` and `escalated` are positive signals that should survive into scoring, story ranking, and analyst review surfaces.

### 4. Story assembly: `Story`

`Story` is the canonical evidence package that turns multiple signals into one explainable unit. Current repo fields include:

- `title`, `summary`, `status`
- `score`, `confidence`
- `item_count`, `source_count`
- `primary_item_id`
- `entities`, `source_names`
- `primary_evidence`, `secondary_evidence`
- `timeline`
- `contradictions`
- `semantic_review`

Contract rules:

- stories aggregate evidence across items, not across ad hoc UI-only state.
- story assembly must preserve provenance back to item IDs, URLs, sources, and review state.
- story edits such as `title / summary / status` refine the package but do not replace underlying evidence lineage.
- entity graph, timeline, contradiction markers, and Markdown export are views over the same story object.

### 5. Report production (additive): `ReportBrief`, `ClaimCard`, `ReportSection`, `CitationBundle`, `Report`, `ExportProfile`

The report layer is additive and starts above `Story` instead of replacing it.

#### `ReportBrief`

- purpose: define report intent, audience, and deliverable scope
- fields: `story_ids`, `title`, `scope`, `constraints`, `owner`, `status`, `created_at`, `updated_at`
- invariants: must reference at least one validated source story and must not mutate mission/triage state

#### `ClaimCard`

- purpose: bounded judgment unit with explicit evidence binding and confidence
- fields: `text`, `confidence`, `evidence_ids`, `state`, `contradictions`, `notes`
- invariants: claims cannot move to finalizable states with unresolved evidence gaps or contradiction flags

#### `ReportSection`

- purpose: ordered section model for report assembly and editorial sequencing
- fields: `title`, `section_type`, `claim_card_ids`, `summary`
- invariants: section order is deterministic and each listed claim id must exist

#### `CitationBundle`

- purpose: reusable citation package for one or more claims/sections
- fields: source ids, URLs, quote spans, evidence notes, confidence annotations
- invariants: each citation maps to persisted source identity from story/item provenance

#### `Report`

- purpose: aggregate of sections and claims into one reusable research artifact
- fields: section graph, provenance summary, quality outputs, lock/version metadata
- invariants: report integrity and outputs remain tied to underlying story and claim provenance

#### `ExportProfile`

- purpose: reusable output selector (`brief`, `full`, `sources`, `watch_pack`)
- fields: profile name, field mapping, rendering policy, delivery metadata
- invariants: changing a profile changes output shape only; it never rewrites underlying story, claim, or report facts

### 6. Delivery and distribution: `Report` plus route-backed event observation

The delivery layer now binds authoritative report output kinds, push triggers, and route observations:

- `Report` + `ExportProfile` define authoritative report outputs (`brief`, `full`, `sources`, `watch_pack`)
- `AlertEvent` for mission-level trigger records and route-aware delivery intents
- named routes from `AlertRouteStore`
- route delivery health and recent failure summaries from `alert_route_health()` and `ops_snapshot()`
- story export output from `story_export(..., output_format="json"|"markdown")`

Contract rules:

- mission-level delivery emits `AlertEvent` objects; it does not redefine mission or triage state.
- route delivery health is an operational observation of output quality, not a replacement for alert/event truth.
- story export remains a legacy handoff format; report outputs are authoritative for report-layer delivery via `ExportProfile`.
- future delivery/subscription work must extend this layer without inventing a second lifecycle separate from mission, triage, and story.

## Governed AI Assistance Overlay

AI assistance is an explicit overlay on the canonical lifecycle objects above. It does not introduce a parallel lifecycle, and it does not grant AI direct final-state authority.

### Surface contract

| Surface | Lifecycle anchor | Allowed AI outputs | Never allowed |
| --- | --- | --- | --- |
| `mission_suggest` | `WatchMission` intent and mission-planning inputs | candidate mission definitions, query/site edits, scope suggestions, run-readiness notes | directly creating or mutating live mission state, enabling schedules, or emitting delivery events |
| `triage_assist` | `DataPulseItem` review queue and reviewer context | explain payloads, candidate review rationales, duplicate hints, evidence-gap flags, operator-visible draft notes | writing final `review_state`, silently overwriting reviewer notes/actions, or bypassing item-level review authority |
| `claim_draft` | `Story`, `ReportBrief`, and `ClaimCard` staging | candidate claims, evidence bindings, contradiction flags, confidence drafts | marking claims final, clearing unresolved evidence gaps without review, or bypassing report quality gates |
| `report_draft` | `ReportSection`, `Report`, and `ExportProfile` staging | section drafts, outline proposals, synthesis rewrites, output-package suggestions | marking a report final/exportable, rewriting provenance lineage, or changing delivery policy as source truth |
| `delivery_summary` | `AlertEvent`, named-route health, report-output audit, and delivery observations | route-health summaries, dispatch explanations, operator-visible delivery digests, candidate incident notes | dispatching routes, acknowledging/suppressing failure truth, or replacing attributable event/attempt records |

Contract rules:

- every AI payload must be attributable to one explicit surface id and one underlying lifecycle object or object set.
- surfaces may emit `suggestion`, `draft`, `explain`, or candidate judgment payloads only.
- surfaces must not write final review, export, or dispatch outcomes directly.
- delivery-facing AI may summarize route and report-output facts, but it may not become a transport executor.

Current admission posture:

- `mission_suggest`, `triage_assist`, `claim_draft`, and `delivery_summary` are currently admitted surfaces
- `report_draft` remains runtime-visible but governance-rejected / fail-closed until a structured contract is admitted

### Switch semantics

The same switch semantics apply across Reader, CLI, MCP, API, and browser projection:

- `off`: no AI assistance call is made; the lifecycle stays fully deterministic/manual.
- `assist`: AI may generate additive suggestions, drafts, and explanations for the declared surface, but final state transitions still require existing deterministic rules or operator action.
- `review`: AI may prefill candidate initial assessments or draft packages for the declared surface, but nothing becomes final until an operator confirms it or a pre-existing deterministic rule independently permits the same outcome.

Switch rules:

- `review` is not autonomous mode; it is still operator-confirmed mode.
- the switch meaning must not drift by tool, route, or UI.
- switching a surface to `assist` or `review` does not widen the allowed output types for that surface.
- manual override, degradation, and failure facts remain visible governance observations rather than hidden prompt behavior.

## Transition Contract

| From | To | Transition source | Required shared truth |
| --- | --- | --- | --- |
| `WatchMission` | `MissionRun` | manual run, due runner, or daemon cycle | stable mission ID and schedule semantics |
| `MissionRun` | `DataPulseItem` queue | collector and reader output persisted into inbox | item provenance tied back to mission/run context when available |
| `DataPulseItem` | triaged item | triage update or note flows | shared review states and note/action schema |
| triaged items | `Story` | story build and persistence | evidence preserves item IDs, review state, timeline, and source lineage |
| `Story` | `ReportBrief` | report planning and scope definition | story references and provenance stay stable |
| `ReportBrief` | `ClaimCard` | claim drafting with evidence assignment | claim and evidence IDs are valid and linked to source story |
| `ClaimCard` | `ReportSection` | editorial sequencing and sectioning | section ordering and claim references are deterministic |
| `ReportSection` | `Report` | report assembly | all section/claim objects are validated against provenance |
| `Report` | `ExportProfile` | export-profile selection | profile output is deterministic for a given report snapshot |
| `WatchMission` or `Report` | report-aware delivery output | alert evaluation, report routing, route dispatch | output remains attributable via explicit `subject_kind`, `output_kind`, subject identity, rule, and route facts |

## Cross-Surface Parity

Current lifecycle parity already exists and must remain true:

| Layer | Reader / core surface | CLI / MCP / console surface |
| --- | --- | --- |
| Mission | `create_watch`, `list_watches`, `show_watch`, `list_watch_results`, `run_watch`, `run_due_watches`, `watch_status_snapshot`, `ops_snapshot` | `--watch-*`, `watch_*`, `/api/watches*`, `/api/watch-status`, `/api/overview` |
| Triage | `triage_list`, `triage_explain`, `triage_update`, `triage_note`, `triage_stats` | `--triage-*`, `triage_*`, `/api/triage*` |
| Story | `story_build`, `list_stories`, `show_story`, `story_update`, `story_graph`, `export_story` | `--story-*`, `story_*`, `/api/stories*` |
| Delivery and ops | `list_alerts`, `list_alert_routes`, `alert_route_health`, `ops_snapshot`, `list_delivery_subscriptions`, `list_delivery_dispatch_records`, `build_report_delivery_package`, `dispatch_report_delivery` | `--alert-*`, `--ops-overview`, `--delivery-*`, `alert_route_health`, `ops_overview`, `list_delivery_subscriptions`, `dispatch_report_delivery`, `/api/alert-routes*`, `/api/delivery-subscriptions*`, `/api/delivery-dispatch-records` |
| Report | `list_report_briefs`, `create_report_brief`, `list_report_sections`, `create_report_section`, `list_reports`, `create_report`, `compose_report`, `assess_report_quality`, `export_report` | `--report-*`, `list_report_*`, `create_report_*`, `compose_report`, `export_report`, `/api/report-briefs*`, `/api/report-sections*`, `/api/reports*` |
| AI assistance | `ai_surface_precheck`, `ai_mission_suggest`, `ai_triage_assist`, `ai_claim_draft`, `ai_report_draft`, `ai_delivery_summary` | `--ai-*`, `ai_*`, `/api/ai/surfaces/*`, `/api/watches/{id}/ai/*`, `/api/triage/{id}/ai/*`, `/api/stories/{id}/ai/*`, `/api/reports/{id}/ai/*`, `/api/alerts/{id}/ai/*` |

Contract rules:

- status enums and identifiers must not drift by surface.
- browser console remains an operating layer over the same reader-backed contract.
- MCP and CLI should expose the same lifecycle nouns, not aliases that invent new domain meanings.

## Lifecycle Invariants

The following invariants should hold for all follow-up work:

1. `WatchMission -> MissionRun -> triage -> Story -> report-layer staging -> export` is the canonical progression.
2. A later layer may summarize an earlier layer, but may not replace its source-of-truth record.
3. Review-state semantics are global repo truth and must not fork by tool or UI.
4. Story objects must remain evidence-preserving, not presentation-only.
5. Report-layer objects must be additive above Story; they cannot redefine mission, triage, or Story semantics.
6. `ExportProfile` selects output shape only; it cannot mutate provenance-rich base objects.
7. Delivery quality facts must stay attached to route or alert observations instead of mutating mission/story/report truth.
8. New roadmap or API work should map back to one lifecycle step in this contract.
9. Report delivery planning must use explicit `subject_kind` + `output_kind` mappings and route-backed observations, not UI-only state.
10. AI assistance is a governed overlay keyed by explicit surface ids; it is not a second lifecycle.
11. `off`, `assist`, and `review` must mean the same thing across Reader, CLI, MCP, API, and browser projection.
12. AI may emit only suggestion/draft/explain or candidate judgment payloads; it must not write final review, export, or route-dispatch state directly.
13. `review` mode still requires operator confirmation for state transitions, report finalization, and delivery actions that matter to repo truth.
14. AI runtime and governance observations may inform operators, but they do not replace lifecycle source truth.

## Implications For Follow-up Slices

- `L6.2` should project this lifecycle contract back into roadmap docs so existing stage naming describes the same chain.
- `L14.2` extends this contract with report-layer nouns, stage mapping, and invariants.
- `L16.2` defines the AI surface ids and `off` / `assist` / `review` semantics in this shared lifecycle contract before bridge or schema slices land.
- `L14.3` onward should realize these report-layer objects in core and persistence before deeper UI-specific workflows.
- `L14.6` and later should only project persisted report objects; no browser-only report state.
