# Intelligence Delivery Contract

## Purpose

This document defines the canonical DataPulse delivery and subscription contract for route-backed intelligence outputs.

It is the contract of record for `L6.3`. It refines the delivery half of [intelligence_lifecycle_contract.md](/Users/sunyifei/DataPulse/docs/intelligence_lifecycle_contract.md) so `AlertEvent`, named routes, feed subscriptions, story export, and delivery health are treated as one output plane instead of parallel feature islands.

## Scope

This contract covers the current and near-term output semantics for:

- source-profile subscriptions and feed export
- normalized `DeliverySubscription` / `DeliveryDispatchRecord` persistence for report, story, watch, and profile subjects
- watch-level alert rules and triggered `AlertEvent` records
- named delivery routes from `AlertRouteStore`
- report-output handoff via `Report` + `ExportProfile`
- story export as the legacy evidence-package handoff
- route health and ops observations

The repo now persists a normalized delivery-subscription object, but not every lifecycle surface auto-manages one yet. Follow-up work must extend the contract below rather than inventing a second subscription plane beside it.

## Current Repo Anchors

| Delivery step | Canonical object(s) | Repo anchors |
| --- | --- | --- |
| Subscription scope | source catalog profiles, subscribed source IDs | `datapulse/core/source_catalog.py`, `datapulse/reader.py` |
| Normalized delivery subscription | `DeliverySubscription`, `DeliveryDispatchRecord` | `datapulse/core/report.py`, `datapulse/reader.py`, `datapulse/cli.py`, `datapulse/mcp_server.py`, `datapulse/console_server.py` |
| Triggered delivery intent | `WatchMission.alert_rules` | `datapulse/core/watchlist.py`, `datapulse/core/alerts.py`, `datapulse/reader.py` |
| Triggered event record | `AlertEvent` | `datapulse/core/alerts.py` |
| Route registry | `AlertRouteStore`, named route config | `datapulse/core/alerts.py` |
| Pull outputs | `build_json_feed`, `build_rss_feed`, `build_atom_feed` | `datapulse/reader.py`, `datapulse/mcp_server.py`, `datapulse/cli.py` |
| Report package and dispatch | `build_report_delivery_package`, `dispatch_report_delivery` | `datapulse/core/report.py`, `datapulse/reader.py`, `datapulse/cli.py`, `datapulse/mcp_server.py`, `datapulse/console_server.py` |
| Evidence-package export | `export_story(..., output_format="json"|"markdown")` | `datapulse/reader.py`, `datapulse/mcp_server.py`, `datapulse/cli.py` |
| Delivery observations | `list_alert_routes`, `alert_route_health`, `ops_snapshot` | `datapulse/reader.py`, `datapulse/console_server.py` |

## Canonical Output Model

```text
subscription scope or mission/story/report selection
  -> output package selection
  -> optional trigger evaluation
  -> named route dispatch or pull export
  -> delivery observations
```

The contract separates five concerns:

1. subscription scope decides which intelligence a consumer wants
2. output package decides how that intelligence is shaped
3. trigger evaluation decides when a push event should exist
4. route dispatch decides where a push event goes
5. delivery observations report transport quality without mutating source truth

## Object Contract

### 1. Subscription scope

The current repo now has two real subscription primitives:

- source-profile subscriptions in `SourceCatalog`
- normalized delivery subscriptions in `datapulse/core/report.py`

Current anchors:

- `list_subscriptions(profile="default")`
- `subscribe_source(source_id, profile="default")`
- `unsubscribe_source(source_id, profile="default")`
- `query_feed(profile=..., source_ids=...)`
- `list_delivery_subscriptions(...)`
- `create_delivery_subscription(...)`
- `build_report_delivery_package(...)`
- `dispatch_report_delivery(...)`

Contract rules:

- a subscription scope selects content membership; it does not define transport credentials
- `profile` is the stable audience identifier for pull-oriented outputs
- explicit `source_ids` may override a profile at read time, but should not invent a second subscription model
- normalized delivery subscriptions should reference existing mission/story/report/profile truth instead of copying business state
- future watch/story subscription UX should compile down to the same idea: stable subject identity first, transport second

### 2. Triggered delivery intent

Mission-level push delivery is currently expressed through `WatchMission.alert_rules`.

Current rule facts include:

- threshold and filter fields such as `min_score`, `min_confidence`, `domains`, `keyword_any`, `keyword_all`, `exclude_keywords`, `required_tags`, `source_types`, `max_age_minutes`
- direct channel hints via `channels`
- named-route references via `routes`

Contract rules:

- `alert_rules` decide whether a mission result set should emit a delivery event
- route names belong here as destination references, but route configuration itself belongs to the route registry
- the rule layer owns business filters; the route layer owns transport details
- future story-triggered or digest-triggered delivery should reuse this split instead of embedding webhook tokens into story objects

### 3. Triggered event record: `AlertEvent`

`AlertEvent` is the immutable record of one triggered output event. Current fields include:

- `mission_id`, `mission_name`
- `rule_name`
- `channels`
- `item_ids`
- `summary`
- `created_at`
- `delivered_channels`
- `extra`

Contract rules:

- `AlertEvent` is created when trigger conditions are met, even if downstream route delivery later fails
- `delivered_channels` records transport outcomes; it does not redefine whether the event happened
- `extra.rule` and `extra.delivery_errors` are delivery metadata attached to the event record, not replacement truth
- the default persisted sink is always `json`; richer transports extend, rather than replace, the event record

### 4. Route registry: named routes

Named routes are the durable push-delivery sink contract.

Current route facts:

- routes live in `AlertRouteStore`
- each route has a stable `name`
- each route declares one `channel`
- channel-specific config may come from the route payload or environment variables
- list surfaces redact secrets before returning route config

Contract rules:

- route identity must be stable and reusable across missions
- missions and future subscriptions should reference routes by name, not duplicate secrets inline
- route config may carry transport concerns such as `webhook_url`, `headers`, `telegram_bot_token`, or `telegram_chat_id`
- route listing is an audit surface; secret redaction must remain mandatory

### 5. Output packages

The repo currently exposes three output package families:

| Package family | Current shape | Delivery mode |
| --- | --- | --- |
| mission alert | `AlertEvent` plus matched item payloads | push |
| report output | `ExportProfile` selected outputs over `Report` (`brief`, `full`, `sources`, `watch_pack`) | pull and route-backed push |
| feed snapshot | JSON Feed, RSS, Atom built from profile/source subscription scope | pull |
| story evidence package | story JSON or Markdown export | pull |

Contract rules:

- output packages are typed views over lifecycle truth; they are not independent business objects
- feed and report outputs are canonical pull subscription surfaces for profile and report-scoped consumption
- story export is the legacy pull evidence-package handoff
- route-backed push delivery currently operates on `AlertEvent`; future digest, report, or story push delivery must still produce an attributable event record before dispatch

## Route-Backed Delivery Contract

When a push output uses named routes, the contract is:

`triggered output -> named route lookup -> channel dispatch -> delivered_channels / delivery_errors -> route health`

Current dispatchable channels include:

- `markdown`
- `webhook`
- `feishu`
- `telegram`

Contract rules:

- named routes are the preferred push indirection layer for reusable delivery targets
- direct channel configuration is acceptable for local/manual use, but route names are the durable operating contract
- route dispatch failure must be reported as delivery observation, not by deleting or suppressing the `AlertEvent`
- route labels in `delivered_channels` should remain channel-qualified when route-backed, such as `webhook:ops-webhook`

## Delivery Observation Contract

Delivery observation is currently exposed through:

- `alert_route_health(limit=...)`
- `ops_snapshot()`
- watch-level `recent_alerts`, `delivery_stats`, and `timeline_strip`

Current route health states include:

- `healthy`
- `degraded`
- `missing`
- `idle`

Contract rules:

- delivery observations are operational facts about transport quality
- operational status must not overwrite mission truth, triage truth, story truth, or event truth
- `missing` means a referenced route does not resolve to config
- `degraded` means attempts exist with failures
- `healthy` means attempts exist with successful delivery
- `idle` means a route is configured but has no observed attempt

## Normalized Subscription Shape

The repo now persists normalized `DeliverySubscription` and `DeliveryDispatchRecord` objects in `datapulse/core/report.py`. Follow-up work should expand adoption of this shape instead of creating a second subscription model:

| Field | Meaning | Current anchor |
| --- | --- | --- |
| `subscriber_kind` | who is consuming the output | not yet first-class |
| `subject_kind` | `profile`, `watch_mission`, `story`, or `report` | persisted in `DeliverySubscription` |
| `subject_ref` | stable subject identifier | persisted in `DeliverySubscription` |
| `output_kind` | `alert_event`, `feed_json`, `feed_rss`, `feed_atom`, `story_json`, `story_markdown`, `report_brief`, `report_full`, `report_sources`, `report_watch_pack` | persisted in `DeliverySubscription` |
| `delivery_mode` | `pull` or `push` | persisted in `DeliverySubscription` |
| `route_names` | named push targets | persisted in `DeliverySubscription`; route names still resolve through `AlertRouteStore` |
| `cursor_or_since` | incremental read pointer | persisted in `DeliverySubscription` |

Forward-compatibility rules:

- a future first-class subscription object must reference existing mission/story/profile truth instead of copying business fields
- `subject_kind='report'` must bind `subject_ref` to a stable `Report` identifier and map to explicit report output kinds for delivery
- `output_kind` and `delivery_mode` must remain explicit so feed export, story export, and route-backed push are one model
- route-backed story or digest delivery should emit an attributable event/attempt record before transport

## Cross-Surface Parity

Current output parity that should remain true:

| Layer | Reader/core surface | CLI / MCP / console surface |
| --- | --- | --- |
| subscription scope | `list_subscriptions`, `subscribe_source`, `unsubscribe_source`, `query_feed` | CLI feed flags, MCP `build_json_feed / build_rss_feed / build_atom_feed` |
| mission push delivery | `run_watch`, `list_alerts`, `list_alert_routes` | `--watch-run`, `--alert-list`, `--alert-route-list`, MCP alert tools, browser alert panels |
| normalized delivery subscription | `list_delivery_subscriptions`, `create_delivery_subscription`, `build_report_delivery_package`, `dispatch_report_delivery`, `list_delivery_dispatch_records` | `--delivery-*`, MCP delivery tools, `/api/delivery-subscriptions*`, `/api/delivery-dispatch-records` |
| route health | `alert_route_health`, `ops_snapshot` | `--alert-route-health`, `--ops-overview`, MCP `alert_route_health / ops_overview`, browser ops board |
| evidence export | `export_story`, `export_report` | `--story-export`, `--report-export`, MCP `story_export / export_report`, browser export preview and `/api/reports/{id}/export` |

Contract rules:

- the same route names and delivery states must mean the same thing across Reader, CLI, MCP, and console
- pull exports and push events should stay Reader-backed rather than UI-defined
- follow-up API work should expose these nouns directly instead of inventing GUI-only labels like "notification job" or "delivery card" as source truth

## Delivery Invariants

The following invariants should hold for all follow-up work:

1. subscription scope, trigger logic, package shape, route transport, and delivery observation are distinct layers
2. transport failure does not erase delivery intent or event truth
3. named routes are reusable sink identities, not mission-specific aliases
4. feed export and story export are pull subscription surfaces over existing lifecycle truth
5. route health and ops metrics are observational, not authoritative replacements for source objects
6. future watch/story subscription UX must extend this contract instead of creating a second delivery plane

## Implications For Follow-up Work

- role-based digest or briefing outputs should be modeled as additional output kinds, not as a parallel product surface
- story-triggered callbacks should reuse named routes and delivery observations instead of inventing standalone callback status stores
- when first-class watch/story subscriptions land, they should normalize onto `subject_ref + output_kind + delivery_mode + route_names`
- roadmap and GUI work should treat delivery as one route-backed output plane spanning alerts, feeds, story export, and ops facts
