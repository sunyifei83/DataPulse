# DataPulse Feed Bundle And Digest Delivery Contract

## Purpose

This document is the contract of record for `L19.2` and the prompt/onboarding boundary frozen by `L19.3`.

It freezes the narrow deterministic boundary between today's pack or profile-scoped feed surfaces and future digest rendering or route-backed delivery work. The goal is not to create a second lifecycle. The goal is to make the existing path replayable:

`pack/profile selection -> feed_bundle -> prepare_digest_payload -> render/deliver`

## Scope

This contract defines:

- the replayable `feed_bundle` artifact that sits on top of current `query_feed` and feed export surfaces
- the deterministic `prepare_digest_payload` boundary that sits on top of current `build_digest` and `emit_digest_package`
- the repo-default prompt-pack contract and local override order for digest rendering
- the shared first-run `digest_profile` semantics that CLI, MCP, and console must all compile down to
- the invariants follow-up runtime work must preserve in `Reader`, CLI, MCP, and browser projection layers

## Current Repo Anchors

| Layer | Current anchor | Current role |
| --- | --- | --- |
| feed selection | `query_feed(profile, source_ids, limit, min_confidence, since)` | resolves subscribed or explicit source scope into one ordered item set |
| feed projection | `build_json_feed`, `build_rss_feed`, `build_atom_feed` | projects the selected item set into pull feed formats |
| digest curation | `build_digest(...)` | curates primary and secondary items, stats, factuality, and provenance |
| office-ready package | `emit_digest_package(...)` | derives summary, sources, recommendations, timeline, todos, and includes `digest_payload` |

Current repo truth already has the feed and digest anchors above. The missing contract is the explicit replayable artifact between them and the deterministic route-ready payload that downstream rendering must consume.

## Contract Invariants

The following rules are mandatory for follow-up work:

1. `feed_bundle` is the replayable input between source selection and digest preparation.
2. `prepare_digest_payload` is an additive boundary on top of current `build_digest` and `emit_digest_package`, not a replacement for them.
3. rendering or route dispatch must not re-query network or inbox data once a `prepare_digest_payload` has been produced.
4. pack or profile intent may enter the contract, but concrete bundle membership must always resolve to explicit `source_ids` plus explicit item rows.
5. stats and errors are first-class contract members; missing or degraded conditions must be recorded, not inferred from absent data.
6. the contract must preserve the current lifecycle and delivery nouns: `WatchMission`, `Story`, `Report`, named routes, and `AlertEvent`.

## Replayable `feed_bundle`

### Role

`feed_bundle` is the frozen membership artifact produced after current pack or profile selection has been resolved into concrete feed rows.

It exists so later digest preparation, prompt rendering, browser preview, or route-backed delivery can replay the same source membership without silently re-running `query_feed(...)` against a changed inbox.

### Canonical Shape

```json
{
  "schema_version": "feed_bundle.v1",
  "selection": {
    "profile": "default",
    "pack_id": null,
    "source_ids_requested": [],
    "source_ids_resolved": [],
    "since": null,
    "limit": 500,
    "min_confidence": 0.0
  },
  "window": {
    "since": null,
    "oldest_fetched_at": null,
    "newest_fetched_at": null
  },
  "items": [],
  "stats": {
    "items_selected": 0,
    "sources_selected": 0
  },
  "errors": []
}
```

### Membership Rules

- `selection.profile` keeps the current audience or subscription scope anchor.
- `selection.pack_id` is optional input provenance only; if a pack was used, the bundle must still persist the resolved concrete `source_ids`.
- `selection.source_ids_requested` records the explicit operator request after CLI or MCP parsing.
- `selection.source_ids_resolved` is the canonical replay set that downstream steps must use.
- `window.since` and the oldest or newest fetched timestamps freeze the item window used by the bundle.
- `items` must be the closed membership set in the same deterministic order `query_feed(...)` produced for the bundle run.
- `items` should reuse current repo item truth rather than inventing a second feed row model. Additive bundle-specific context is acceptable, but the underlying content row remains the existing `DataPulseItem`-derived payload.
- `stats` must make bundle size and source breadth operator-visible.
- `errors` must capture membership-affecting degradation such as invalid `since`, missing sources, or partial serialization issues instead of silently dropping them.

### Determinism Rules

- downstream code may filter or rank only against `feed_bundle.items`; it must not re-read inbox state to discover new members
- if a future exporter wants a bundle identifier, it should derive it from bundle content and selection metadata rather than introduce hidden mutable state
- feed exporters may continue projecting live `query_feed(...)` results, but future replay or digest delivery flows should prefer a previously frozen `feed_bundle`

## Deterministic `prepare_digest_payload`

### Role

`prepare_digest_payload` is the deterministic route-ready boundary produced from one frozen `feed_bundle`, explicit digest configuration, and explicit prompt resolution.

Its purpose is to make renderers and delivery surfaces consume one already-prepared input instead of rebuilding digest state ad hoc.

### Canonical Shape

```json
{
  "schema_version": "prepare_digest_payload.v1",
  "content": {
    "feed_bundle": {},
    "digest_payload": {},
    "delivery_package": {}
  },
  "config": {
    "profile": "default",
    "source_ids": [],
    "top_n": 3,
    "secondary_n": 7,
    "min_confidence": 0.0,
    "since": null,
    "max_per_source": 2,
    "output_format": "json",
    "digest_profile": {
      "language": "en",
      "timezone": "UTC",
      "frequency": "@daily",
      "default_delivery_target": {
        "kind": "route",
        "ref": ""
      }
    }
  },
  "prompts": {
    "prompt_pack": "repo_default",
    "repo_default_pack": "digest_delivery_default",
    "render_intent": "digest_delivery",
    "files": [],
    "override_order": [
      "repo_default_pack",
      "local_prompt_overrides",
      "per_run_overrides"
    ],
    "overrides_applied": []
  },
  "stats": {
    "feed_bundle": {},
    "digest": {},
    "delivery_package": {}
  },
  "errors": []
}
```

### Content Rules

- `content.feed_bundle` is the full replayable bundle used for this payload. It is not a soft reference.
- `content.digest_payload` must preserve the current `build_digest(...)` shape as the canonical curated content selection layer.
- `content.delivery_package` must preserve the current office-ready package concepts already emitted by `emit_digest_package(...)`, including `summary`, `sources`, `recommendations`, `timeline`, `todos`, and `factuality`.
- the future runtime implementation may reuse current `emit_digest_package(...)` logic internally, but it must do so over the already-frozen bundle or digest payload rather than by re-querying feed state

### Config Rules

- `config` records every operator-visible choice that changes digest selection or package rendering
- fields that affect curation such as `top_n`, `secondary_n`, `min_confidence`, `since`, and `max_per_source` must be explicit
- `config.source_ids` should reflect the resolved source scope actually used for the payload, not only the user-entered shorthand
- `config.digest_profile` carries the resolved first-run or saved operator defaults for `language`, `timezone`, `frequency`, and `default_delivery_target`
- future renderers may enrich formatting from `config.digest_profile`, but they must not infer locale or cadence from browser-only state or ambient machine settings

### Prompt Rules

- `prompts` is required so the payload boundary carries resolved prompt-pack and override facts instead of relying on implicit environment drift
- `prompts.repo_default_pack` is the repo-shipped baseline for `digest_delivery`; the contract name is `digest_delivery_default`
- override order is fixed and operator-visible: `repo_default_pack -> local_prompt_overrides -> per_run_overrides`
- `local_prompt_overrides` means explicit operator-owned files outside the repo, for example under `~/.datapulse/prompts/...`
- `per_run_overrides` means explicit files or prompt fragments passed for one CLI, MCP, or future console-triggered run; later layers win only for the prompt roles they replace
- `prompts.files` must list the final resolved file set in applied order, and `prompts.overrides_applied` must record every non-default layer that actually changed resolution
- the browser may show readiness and provenance for resolved prompt files, but it must not invent hidden browser-only prompt state or unpublished prompt text paths

### Stats And Error Rules

- `stats.feed_bundle` must summarize membership facts from the frozen bundle
- `stats.digest` must include the curation counters already surfaced by `build_digest(...)`
- `stats.delivery_package` must summarize route-ready facts such as item count, high-confidence count, and factuality status
- `errors` must aggregate deterministic preparation failures or degradations across bundle loading, digest preparation, prompt resolution, and package rendering

## Shared First-Run `digest_profile`

### Role

`digest_profile` is the one shared onboarding record for digest rendering defaults across CLI, MCP, and console.

It exists so the repo has one operator-visible answer for locale, cadence, and default delivery destination instead of scattering those choices across ad hoc flags, browser local storage, or operator memory.

### Canonical Shape

```json
{
  "schema_version": "digest_profile.v1",
  "language": "en",
  "timezone": "UTC",
  "frequency": "@daily",
  "default_delivery_target": {
    "kind": "route",
    "ref": ""
  }
}
```

### Onboarding Rules

- first-run onboarding happens only when no shared `digest_profile` has been persisted and the current run does not already provide all four fields explicitly
- CLI flags, MCP arguments, and future console onboarding are only input surfaces; they must all resolve to the same shared `digest_profile` nouns
- if a shared `digest_profile` already exists, follow-up runs should reuse it as defaults rather than re-opening a separate onboarding flow
- explicit per-run values override the shared profile for that run only; absent fields fall back to the saved profile
- console locale or browser timezone may prefill suggestions, but they do not become repo truth until the shared profile is confirmed

### Delivery Target Rules

- `default_delivery_target` is a delivery reference, not inline transport secrets
- when push delivery is intended, the preferred target is a named route reference with `kind = route`
- direct channel secrets remain route-registry or manual local execution concerns; they are not part of first-run digest onboarding
- an empty `ref` means preview-only or pull-only digest preparation is still allowed until an operator chooses a route

## Anchor Preservation

This contract preserves the existing repo anchors rather than replacing them:

- `build_digest(...)` remains the canonical digest curation step
- `emit_digest_package(...)` remains the canonical office-ready export surface
- a future `prepare_digest_payload(...)` should be an additive helper that composes frozen bundle membership, digest output, package fields, prompt facts, stats, and errors into one route-ready input

Follow-up work must therefore prefer additive APIs such as `build_feed_bundle(...)` or `prepare_digest_payload(...)` over renaming or deleting current feed and digest methods.

## Delivery Implications

When route-backed digest or report delivery expands beyond the current `AlertEvent` lane, the delivery surface must consume `prepare_digest_payload` rather than reconstructing digest content during transport.

That future path must still preserve current delivery truth:

- an attributable event or dispatch record must exist before transport
- named routes remain the durable sink identity
- transport diagnostics remain observational facts rather than replacing digest or bundle truth

## Follow-up Boundary

`L19.4` should implement runtime exporters and Reader or CLI or MCP helpers that follow this contract exactly, including the frozen prompt resolution order and shared `digest_profile` boundary.

`L19.5` and `L19.6` should treat `feed_bundle` and `prepare_digest_payload` as already-frozen nouns, not as UI-local or transport-local shapes.
