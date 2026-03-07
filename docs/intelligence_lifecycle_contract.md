# Intelligence Lifecycle Contract

## Purpose

This document defines the canonical DataPulse intelligence lifecycle that now spans recurring mission execution, inbox triage, story assembly, and route-backed delivery signals.

It is the contract of record for `L6.1`. It should be used to keep `Reader`, `CLI`, `MCP`, and browser console work aligned to one lifecycle instead of growing parallel feature surfaces.

## Scope

This contract covers the shared lifecycle semantics for:

- `WatchMission`
- `MissionRun`
- `DataPulseItem` review and triage state
- `Story` and evidence packaging
- `AlertEvent` and named-route delivery health as the current delivery surface

This contract does not yet define a richer subscription or callback model. That follow-up belongs to `L6.3`.

## Current Repo Anchors

| Lifecycle step | Canonical object(s) | Repo anchors |
| --- | --- | --- |
| Mission intent | `WatchMission` | `datapulse/core/watchlist.py`, `datapulse/reader.py` |
| Mission execution | `MissionRun` | `datapulse/core/watchlist.py`, `datapulse/core/scheduler.py` |
| Triage queue | `DataPulseItem`, `review_state`, `review_notes`, `review_actions`, `duplicate_of` | `datapulse/core/models.py`, `datapulse/core/triage.py` |
| Story assembly | `Story`, `StoryEvidence`, `StoryTimelineEvent`, `StoryConflict` | `datapulse/core/story.py` |
| Delivery and ops | `AlertEvent`, named alert routes, route health, ops snapshot | `datapulse/core/alerts.py`, `datapulse/reader.py` |

## Canonical Lifecycle

```text
WatchMission
  -> MissionRun
  -> DataPulseItem queue entries
  -> triage decisions and reviewer notes
  -> Story / evidence package
  -> AlertEvent / route delivery health / story export
```

The lifecycle is additive, not branchless:

- one `WatchMission` can produce many `MissionRun` records
- one `MissionRun` can emit many `DataPulseItem` records
- triage can suppress, verify, or escalate items before and during story assembly
- one `Story` can aggregate items from multiple runs and multiple sources
- delivery can consume either mission-level alert facts or story-level export artifacts

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

### 5. Delivery and distribution: `AlertEvent` plus route facts

The current repo does not yet expose a standalone delivery object beyond alert events and route-health facts. The effective delivery layer today is:

- `AlertEvent` for mission-triggered threshold outputs
- named alert routes from `AlertRouteStore`
- route delivery health and recent failure summaries from `alert_route_health()` and `ops_snapshot()`
- story export output from `story_export(..., output_format="json"|"markdown")`

Contract rules:

- mission-level delivery emits `AlertEvent` objects; it does not redefine mission or triage state.
- route delivery health is an operational observation of output quality, not a replacement for alert/event truth.
- story export is the current evidence-package handoff format until a richer subscription contract lands.
- future delivery/subscription work must extend this layer without inventing a second lifecycle separate from mission, triage, and story.

## Transition Contract

| From | To | Transition source | Required shared truth |
| --- | --- | --- | --- |
| `WatchMission` | `MissionRun` | manual run, due runner, or daemon cycle | stable mission ID and schedule semantics |
| `MissionRun` | `DataPulseItem` queue | collector and reader output persisted into inbox | item provenance tied back to mission/run context when available |
| `DataPulseItem` | triaged item | triage update or note flows | shared review states and note/action schema |
| triaged items | `Story` | story build and persistence | evidence preserves item IDs, review state, timeline, and source lineage |
| `WatchMission` or `Story` | delivery output | alert evaluation, story export, route dispatch | output remains attributable to mission, rule, story, and route facts |

## Cross-Surface Parity

Current lifecycle parity already exists and must remain true:

| Layer | Reader / core surface | CLI / MCP / console surface |
| --- | --- | --- |
| Mission | `create_watch`, `list_watches`, `show_watch`, `list_watch_results`, `run_watch`, `run_due_watches`, `watch_status_snapshot`, `ops_snapshot` | `--watch-*`, `watch_*`, `/api/watches*`, `/api/watch-status`, `/api/overview` |
| Triage | `triage_list`, `triage_explain`, `triage_update`, `triage_note`, `triage_stats` | `--triage-*`, `triage_*`, `/api/triage*` |
| Story | `story_build`, `list_stories`, `show_story`, `story_update`, `story_graph`, `export_story` | `--story-*`, `story_*`, `/api/stories*` |
| Delivery and ops | `list_alerts`, `list_alert_routes`, `alert_route_health`, `ops_snapshot` | `--alert-*`, `--ops-overview`, `alert_route_health`, `ops_overview`, `/api/alert-routes*` |

Contract rules:

- status enums and identifiers must not drift by surface.
- browser console remains an operating layer over the same reader-backed contract.
- MCP and CLI should expose the same lifecycle nouns, not aliases that invent new domain meanings.

## Lifecycle Invariants

The following invariants should hold for all follow-up work:

1. `WatchMission -> MissionRun -> triage -> Story -> delivery` is the canonical progression.
2. A later layer may summarize an earlier layer, but may not replace its source-of-truth record.
3. Review-state semantics are global repo truth and must not fork by tool or UI.
4. Story objects must remain evidence-preserving, not presentation-only.
5. Delivery quality facts must stay attached to route or alert observations instead of mutating mission/story truth.
6. New roadmap or API work should map back to one lifecycle step in this contract.

## Implications For Follow-up Slices

- `L6.2` should project this lifecycle contract back into roadmap docs so `P6/P7/P8/P9` and `G0/G1/G2/G3/G4` describe the same chain.
- `L6.3` should refine the delivery half of this contract into explicit subscription, callback, and route-backed output semantics.
- until those slices land, this document is the repo-level truth for how existing mission, triage, story, and delivery features connect.
