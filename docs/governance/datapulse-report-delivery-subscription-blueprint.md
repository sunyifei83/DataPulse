# DataPulse Report Delivery And Subscription Blueprint

## Purpose

This document promotes the next repo-relevant wave after report production into repository truth.

The goal is not to reopen report persistence or invent another GUI product. The goal is to define the next narrow blueprint slices that turn authoritative report outputs into one Reader-backed delivery and subscription plane.

## Canonical Contract Snapshot For L15.2

L15.2 establishes these explicit normalized shapes before implementation:

- Delivery subjects: `profile`, `watch_mission`, `story`, `report`
- Delivery outputs: `alert_event`, `feed_json`, `feed_rss`, `feed_atom`, `story_json`, `story_markdown`, `report_brief`, `report_full`, `report_sources`, `report_watch_pack`
- Route binding: `route_names` references named route identities from `AlertRouteStore`
- Cursoring: `cursor_or_since` is used for pull subscriptions and future incremental report package pagination
- Canonical subscription projection: `subject_kind + subject_ref + output_kind + delivery_mode + route_names + cursor_or_since`

## Current Repo Read

The repository now has a lifecycle-complete report-production layer that reaches:

- `WatchMission`
- `MissionRun`
- `DataPulseItem` triage
- `Story` evidence package
- `ReportBrief`
- `ClaimCard`
- `ReportSection`
- `Report`
- `ExportProfile`
- `brief / full / sources / watch_pack` report outputs

Current repo anchors:

- `docs/intelligence_lifecycle_contract.md`
- `docs/intelligence_delivery_contract.md`
- `docs/gui_intelligence_console_plan.md`
- `docs/governance/datapulse-research-os-report-production-blueprint.md`
- `datapulse/core/report.py`
- `datapulse/core/alerts.py`
- `datapulse/reader.py`
- `datapulse/cli.py`
- `datapulse/mcp_server.py`
- `datapulse/console_server.py`
- `datapulse/console_markup.py`

That changes the highest-leverage delta.

The repo no longer needs another report-writing surface first. The next delta is to make report outputs deliverable, subscribable, and auditable through the same route-backed output plane that already covers alerts, feeds, and delivery observations.

## Canonical Follow-up Stage Mapping

The lifecycle extension for this wave should stay additive:

- `Story` remains the evidence package.
- `Report` plus `ExportProfile` remain the authoritative output source above `Story`.
- `DeliverySubscription` should normalize stable audience scope over `profile`, `watch_mission`, `story`, and `report`.
- report-backed push delivery should emit attributable dispatch records before transport.
- named routes remain the reusable sink identity; transport config does not move into report or browser-local state.

Invariants to enforce before implementation work:

1. `Report` and `ExportProfile` remain the source of output truth; delivery layers cannot mutate report provenance.
2. subscription scope, package shape, route transport, and delivery observations stay distinct.
3. future report/story subscriptions must reuse named routes instead of duplicating channel secrets inline.
4. route-backed report delivery must produce attributable event or attempt records before dispatch.
5. no GUI-only delivery or subscription state is allowed before Reader-backed persistence exists.
6. richer briefing or digest outputs must extend output kinds, not create a second product surface.

Stage map for implementation:

- `L15.2`: contract and roadmap alignment for report-authoritative delivery and normalized subscriptions
- `L15.3`: add normalized subscription and dispatch persistence
- `L15.4`: add report-backed package assembly and attributable dispatch records
- `L15.5`: expose delivery-subscription CRUD and dispatch through Reader, CLI, MCP, and API
- `L15.6`: project the same delivery objects into the browser shell
- `L15.7`: harden verification for route-backed report delivery and subscription flows

## High-Value Facts To Promote

### 1. Report outputs are now authoritative enough to become delivery subjects

Current repo reality:

- `story export` is no longer the only structured handoff surface
- `Report` plus `ExportProfile` already define durable output shapes

Repo implication:

- the next wave should treat report outputs as first-class delivery subjects instead of extending story export forever
- route-backed delivery should reference persisted report truth, not ad hoc markdown text blobs

### 2. Delivery follow-up should normalize subscriptions instead of adding feature-specific knobs

Current repo reality:

- source-profile subscriptions already exist
- watch delivery already uses `alert_rules.routes`
- the delivery contract already defines a normalized future shape around `subject_ref + output_kind + delivery_mode + route_names`

Repo implication:

- follow-up work should converge on one persisted subscription model rather than separate watch, story, and report toggles
- `report` should join `profile`, `watch_mission`, and `story` as a normalized subject kind

### 3. Named routes remain the durable transport boundary

Current repo reality:

- route config is already stable, reusable, and redacted in audit surfaces
- delivery health is already modeled as observation instead of source truth

Repo implication:

- do not embed webhook or bot credentials into report objects or browser drafts
- report-backed delivery should resolve through named routes and existing delivery observations

### 4. Briefing and digest outputs belong to the output plane, not to a second product surface

Current repo reality:

- the delivery contract already says role-based digest or briefing outputs should be modeled as additional output kinds

Repo implication:

- future briefing work should extend `output_kind`
- do not introduce a separate "briefing app" or GUI-only scheduler model

## What Should Not Be Promoted As First-Class Slices Now

This wave does not justify immediate blueprint slices for:

- a second frontend or report-publishing product
- multi-user collaboration or approval workflows
- freeform rich-text editing beyond persisted report objects
- route-secret management inside reports
- subscription-specific business copies of report, story, or watch objects

Those moves would either fork the lifecycle or weaken the existing Reader-backed contract.

## Integration Rules For This Phase

All follow-up slices in this phase should obey the same constraints:

1. preserve `Story` as the evidence package and `Report` as the authoritative report output layer
2. extend the delivery contract instead of bypassing it
3. normalize subscriptions around explicit `subject_kind`, `subject_ref`, `output_kind`, `delivery_mode`, `route_names`, and `cursor_or_since`
4. keep named routes as reusable sink identities
5. emit attributable dispatch records before transport for report-backed push delivery
6. project delivery nouns through Reader, CLI, MCP, API, and browser rather than inventing GUI-only state
7. keep slices narrow enough that the loop can stop on machine-decidable progress

## Stage Preview

Recommended stage language for this follow-up wave:

- `D0`: current repo baseline `alerts / feeds / story export / report export / route health`
- `D1`: report-authoritative delivery contract and normalized subscription extension
- `D2`: normalized delivery-subscription persistence
- `D3`: report-backed package assembly and dispatch records
- `D4`: Reader, CLI, MCP, and HTTP projection
- `D5`: browser delivery workspace over persisted objects
- `D6`: route-backed briefing outputs and regression hardening

## L15 Slice Map

| Slice | Outcome | Why it exists |
| --- | --- | --- |
| `L15.1` | Land this repo-scoped report-delivery and subscription blueprint plus ignition map | Converts the next-wave judgment into repo truth before implementation slices reopen |
| `L15.2` | Extend lifecycle and delivery contracts with report-authoritative output kinds and normalized subscription invariants | Fixes how reports, routes, and subscriptions relate before core code starts drifting |
| `L15.3` | Add normalized delivery-subscription core objects and persistence | Makes report/story/watch subscriptions explicit repo objects instead of CLI flags or browser toggles |
| `L15.4` | Add report-backed package assembly and attributable dispatch records | Keeps route-backed report delivery deterministic, auditable, and provenance-preserving |
| `L15.5` | Expose delivery-subscription CRUD and dispatch through Reader, CLI, MCP, and HTTP API | Preserves cross-surface parity and keeps the browser as a projection |
| `L15.6` | Add browser delivery workspace inside the current console shell | Delivers operator value without opening a second delivery product surface |
| `L15.7` | Harden verification for route-backed report delivery, subscription normalization, and delivery audit flows | Protects the new delivery plane before richer briefing expansion lands |

## Recommended Ignition Order After This Refresh

Recommended order after this refresh:

1. `L15.1`
2. `L15.2`
3. `L15.3`
4. `L15.4`
5. `L15.5`
6. `L15.6`
7. `L15.7`

This order keeps DataPulse from jumping straight into browser workflow or digest UX before the contract, persistence, and delivery audit model are explicit.
