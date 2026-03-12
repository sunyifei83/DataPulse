# Intelligence Lifecycle Contract

## Purpose

This document defines the canonical DataPulse intelligence lifecycle that now spans recurring mission execution, inbox triage, story assembly, and structured report production.

It is the contract of record for `L6.1` and the report-production anchor of `L14.2`. It must align Reader, CLI, MCP, and browser console work to one progression and one source of truth.

## Scope

This contract covers the shared lifecycle semantics for:

- `WatchMission`
- `MissionRun`
- `DataPulseItem` review and triage state
- `Story` and evidence packaging
- report production objects: `ReportBrief`, `ClaimCard`, `ReportSection`, `CitationBundle`, `Report`, `ExportProfile`
- `AlertEvent` and named-route delivery health as the current delivery surface

This contract currently records the repo-level semantics before full report model/runtime code lands.

## Current Repo Anchors

| Lifecycle step | Canonical object(s) | Repo anchors |
| --- | --- | --- |
| Mission intent | `WatchMission` | `datapulse/core/watchlist.py`, `datapulse/reader.py` |
| Mission execution | `MissionRun` | `datapulse/core/watchlist.py`, `datapulse/core/scheduler.py` |
| Triage queue | `DataPulseItem`, `review_state`, `review_notes`, `review_actions`, `duplicate_of` | `datapulse/core/models.py`, `datapulse/core/triage.py` |
| Story assembly | `Story`, `StoryEvidence`, `StoryTimelineEvent`, `StoryConflict` | `datapulse/core/story.py` |
| Report production (planned layer) | `ReportBrief`, `ClaimCard`, `ReportSection`, `CitationBundle`, `Report`, `ExportProfile` | `docs/intelligence_lifecycle_contract.md`, `docs/gui_intelligence_console_plan.md`, `docs/governance/datapulse-research-os-report-production-blueprint.md` |
| Delivery and ops | `AlertEvent`, named alert routes, route health, ops snapshot | `datapulse/core/alerts.py`, `datapulse/reader.py` |

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
  -> brief / full / source / watch-pack outputs
  -> AlertEvent / route delivery health
```

The lifecycle is additive, not branchless:

- one `WatchMission` can produce many `MissionRun` records
- one `MissionRun` can emit many `DataPulseItem` records
- triage can suppress, verify, or escalate items before and during story assembly
- one `Story` can aggregate items from multiple runs and multiple sources
- one `Story` may be the evidence basis for multiple `ReportBrief` planning units
- one `Report` can be exported through multiple `ExportProfile` shapes
- delivery can consume either mission-level alert facts or report outputs

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

### 6. Delivery and distribution: `AlertEvent` plus route facts

The current repo does not yet expose a standalone delivery object beyond alert events and route-health facts. The effective delivery layer today is:

- `AlertEvent` for mission-triggered threshold outputs
- named alert routes from `AlertRouteStore`
- route delivery health and recent failure summaries from `alert_route_health()` and `ops_snapshot()`
- story export output from `story_export(..., output_format="json"|"markdown")`

Contract rules:

- mission-level delivery emits `AlertEvent` objects; it does not redefine mission or triage state.
- route delivery health is an operational observation of output quality, not a replacement for alert/event truth.
- story export remains the current handoff format until report outputs become authoritative via `ExportProfile`.
- future delivery/subscription work must extend this layer without inventing a second lifecycle separate from mission, triage, and story.

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
| `WatchMission` or `Story` | delivery output | alert evaluation, report export, route dispatch | output remains attributable to mission, rule, story, report, and route facts |

## Cross-Surface Parity

Current lifecycle parity already exists and must remain true:

| Layer | Reader / core surface | CLI / MCP / console surface |
| --- | --- | --- |
| Mission | `create_watch`, `list_watches`, `show_watch`, `list_watch_results`, `run_watch`, `run_due_watches`, `watch_status_snapshot`, `ops_snapshot` | `--watch-*`, `watch_*`, `/api/watches*`, `/api/watch-status`, `/api/overview` |
| Triage | `triage_list`, `triage_explain`, `triage_update`, `triage_note`, `triage_stats` | `--triage-*`, `triage_*`, `/api/triage*` |
| Story | `story_build`, `list_stories`, `show_story`, `story_update`, `story_graph`, `export_story` | `--story-*`, `story_*`, `/api/stories*` |
| Delivery and ops | `list_alerts`, `list_alert_routes`, `alert_route_health`, `ops_snapshot` | `--alert-*`, `--ops-overview`, `alert_route_health`, `ops_overview`, `/api/alert-routes*` |
| Report (planned) | planned `report` readers and stores (L14.5+) | planned `--report-*`, `report_*`, `/api/reports*` |

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

## Implications For Follow-up Slices

- `L6.2` should project this lifecycle contract back into roadmap docs so existing stage naming describes the same chain.
- `L14.2` extends this contract with report-layer nouns, stage mapping, and invariants.
- `L14.3` onward should realize these report-layer objects in core and persistence before deeper UI-specific workflows.
- `L14.6` and later should only project persisted report objects; no browser-only report state.
