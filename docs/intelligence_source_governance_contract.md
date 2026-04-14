# Intelligence Source Governance Contract

## Purpose

This document defines the canonical source-governance contract for DataPulse public-source intelligence intake.

It is the contract of record for `L8.2`. It upgrades source handling from a plain list of usable inputs to a governed directory with stable semantics that other layers can reuse.

## Scope

This contract covers the source-governance tuple for:

- `SourceRecord` entries in `SourceCatalog`
- auto-registered public sources
- `resolve_source()` payloads returned to Reader, CLI, and MCP
- search-gateway provider boundaries
- manual fact intake as a first-class collection mode

This contract does not claim that DataPulse automatically decides whether a collection path is legally compliant. It only defines governance hints and operator-visible boundaries.

## Canonical Governance Tuple

Every governed source should carry five fields:

| Field | Meaning | Current code anchor |
| --- | --- | --- |
| `source_class` | what kind of source this is | `datapulse/core/models.py`, `datapulse/core/source_catalog.py` |
| `collection_mode` | how DataPulse reaches it | `datapulse/core/models.py`, `datapulse/core/source_catalog.py`, `docs/search_gateway_config.md` |
| `authority` | qualitative authority expectation | `datapulse/core/models.py`, `datapulse/core/source_catalog.py` |
| `sensitivity` | operator review expectation | `datapulse/core/models.py`, `datapulse/core/source_catalog.py` |
| `compliance_hints` | non-legal governance hints shown to operators | `datapulse/core/models.py`, `datapulse/core/source_catalog.py`, `docs/search_gateway_config.md` |

The tuple is carried by `SourceGovernance`, then attached to `SourceRecord.governance`.

## Current Repo Anchors

| Surface | Contract role | Repo anchors |
| --- | --- | --- |
| Source registry | durable source-governance record | `datapulse/core/source_catalog.py` |
| Reader / CLI / MCP source inspection | returns normalized source-governance payloads | `datapulse/reader.py`, `datapulse/cli.py`, `datapulse/mcp_server.py` |
| Source scoring | quantitative authority signal | `datapulse/core/source_catalog.py`, `datapulse/core/scoring.py` |
| Search provider gateway | governs provider-side collection boundaries | `datapulse/core/search_gateway.py`, `docs/search_gateway_config.md` |

## Vocabulary

### 1. `source_class`

| Value | Meaning |
| --- | --- |
| `publisher` | publisher-owned or registry-like public source |
| `platform` | hosted public platform or community surface |
| `aggregator` | search or discovery intermediary rather than the underlying content owner |
| `analyst` | operator-supplied manual fact or note intake |
| `generic` | public source not yet classified more precisely |

### 2. `collection_mode`

The following modes are first-class and should remain explicit:

| Value | Meaning |
| --- | --- |
| `public_web` | direct public-web page or feed intake |
| `api` | provider API governed by provider-side terms and credentials |
| `search_gateway` | search-provider mediation such as `SearchGateway` |
| `manual_fact` | manual operator fact or note intake |
| `hybrid` | intentionally mixed intake path |

### 3. `authority`

`authority` is qualitative source posture, not a numeric score:

| Value | Meaning |
| --- | --- |
| `official` | direct authoritative owner or issuer |
| `primary` | strong primary-source signal but not necessarily the issuing authority |
| `secondary` | derivative public source that may still be useful |
| `community` | community or user-generated signal source |
| `unverified` | unknown authority posture |

`authority_weight` remains a quantitative scoring input. It complements `authority`; it does not replace it.

### 4. `sensitivity`

| Value | Meaning |
| --- | --- |
| `public` | normal public-source handling |
| `review_required` | operator review is expected before escalation or automation expansion |
| `elevated` | additional operator caution is expected |

### 5. `compliance_hints`

`compliance_hints` are operator-visible governance reminders. Current canonical hints include:

- `public_content_only`
- `respect_source_terms`
- `respect_rate_limits`
- `api_terms_apply`
- `search_results_require_verification`
- `manual_entry_requires_attribution`
- `operator_review_required`
- `no_automated_legal_determination`

These hints are warnings and boundaries, not machine-issued legal clearances.

## SourceCatalog Mapping

`SourceCatalog` is the canonical registry surface for this contract.

Contract rules:

1. `SourceRecord.governance` is the durable home for the source-governance tuple.
2. `tier` and `authority_weight` remain numeric ranking aids for scoring and routing, while `governance.authority` is the qualitative authority label.
3. `register_auto_source()` must default new public sources into the same governance shape instead of creating ungoverned source entries.
4. `resolve_source()` must return `governance`, `tier`, and `authority_weight` so Reader, CLI, and MCP surfaces can inspect the same source posture.
5. Missing governance fields should default to conservative public-source assumptions rather than implying unrestricted automation.

Default posture in current repo code:

- public web sources default to `collection_mode=public_web`
- API-shaped sources default to `collection_mode=api`
- manual sources default to `collection_mode=manual_fact`
- search gateway remains a separate provider-side mode documented below

## L30.2 Public-APIs Screening Baseline

As of 2026-04-07, the `public-apis` handoff is screened as repo-native seed input only.

Contract consequences:

1. A screened candidate may qualify as a governed feed or context seed without becoming a builtin `SourceCatalog` default.
2. Qualified aggregator and location-context APIs remain `review_required` and must not be reinterpreted as item-level verified evidence on their own.
3. Deferred or rejected candidates stay attributable in repo truth with explicit reasons instead of being silently promoted into runtime admission.

| Candidate | Verdict | Governance posture | Admissible usage | Explicit reason |
| --- | --- | --- | --- | --- |
| `The Guardian Open Platform` | `qualify` | `publisher / api / official / review_required` | governed news feed seed | publisher-owned API with explicit key and commercial-use boundary; suitable once route/watch usage remains terms-reviewed |
| `GNews API` | `qualify` | `aggregator / api / secondary / review_required` | watch/feed seed only | broad multi-source discovery surface is useful for collection breadth, but results remain aggregator output that still requires downstream verification |
| `Geoapify Geocoding API` | `qualify` | `generic / api / secondary / review_required` | location-context seed only | key-based geocoding API is suitable for place normalization and context enrichment, not for item-evidence truth |
| `OpenCage Geocoding API` | `qualify` | `generic / api / secondary / review_required` | location-context seed only | open-data geocoder is governance-compatible for operator-visible place context, with attribution and rate-limit review preserved |
| `NewsAPI` | `defer` | `aggregator / api / secondary / review_required` | none until differentiated need is proven | overlaps the same aggregator lane already covered by `GNews`; keep deferred until source-diversity need or plan-specific terms review justifies dual admission |
| `Associated Press API` | `defer` | `publisher / api / official / review_required` | none until licensed intake path exists | authoritative publisher feed is attractive, but licensed API access and content-rights review should be explicit before repo-native seed admission |
| `MarketAux` | `defer` | `aggregator / api / secondary / review_required` | none in current slice | entity-tagged finance aggregation is more aligned with market-reference specialization than the current generic DataPulse feed wave |
| `LocationIQ` | `defer` | `generic / api / secondary / review_required` | none until redundancy need is proven | geocoding fit exists, but it duplicates the `Geoapify/OpenCage` context lane without adding a new governance advantage for this slice |
| `OpenWeatherMap` | `defer` | `generic / api / secondary / review_required` | weather context only, not admitted now | weather enrichment can help later story context, but it does not solve the current feed/news seed gap |
| `stormglass.io` | `reject_current_slice` | `generic / api / secondary / review_required` | not in `L30.2` scope | marine-weather specialization and commercial-use boundary pull beyond the current repo-native intelligence feed/context need |

These verdicts intentionally do not create a new public DataPulse surface. They only define which `public-apis` candidates are governance-compatible handoff seeds for later explicit admission work.

## L31.2 Tradingview-Style Technical-Signal Seed Screening

As of 2026-04-14, the `tradingview-mcp` donor handoff is screened for DataPulse only as watchlist-seed or operator-context input.

Contract consequences:

1. Qualified donor inputs stay additive to `watch_seed_only` or operator-visible market context; they do not become builtin `SourceCatalog` defaults in this slice.
2. No donor input in this wave may be treated as item-level verified evidence, investor advice, execution truth, or a new public trading surface.
3. Any sentiment-derived or robustness-derived import remains attributable, review-required, and secondary even when it is useful for watch formation or triage context.

| Donor input | Verdict | Governance posture | Admissible usage | Explicit reason |
| --- | --- | --- | --- | --- |
| `technical_regime_sidecar` | `qualify` | `aggregator / hybrid / secondary / review_required` | watchlist seed and operator triage context | derived trend or regime labels can help seed a watch, but they summarize market behavior rather than proving a reportable fact |
| `strategy_robustness_backtest` | `qualify_context_only` | `analyst / manual_fact / secondary / review_required` | operator context seed only | deterministic robustness summaries can help rank whether a signal lane is worth watching, but they remain imported analytic interpretation rather than primary evidence |
| `market_quote_snapshot` | `qualify` | `aggregator / hybrid / secondary / review_required` | watchlist seed and quote context only | point-in-time price, volume, and indicator snapshots can prioritize watch candidates, but they are time-sensitive and insufficient for evidence truth on their own |
| `sentiment_news_contra_sidecar` | `qualify_context_only` | `aggregator / hybrid / secondary / review_required` | operator context seed only | contra sentiment summaries can add cautionary context around a watch or triage decision, but weak-signal news or sentiment blends still require explicit downstream verification |
| `BUY/SELL` summaries, target prices, or entry/exit calls | `reject_current_slice` | `analyst / manual_fact / secondary / review_required` | none | investor-facing recommendation language would cross from governed intake into advice semantics that DataPulse does not own |
| portfolio, execution, or auto-trading triggers | `reject_current_slice` | `analyst / manual_fact / secondary / elevated` | none | execution intent and portfolio automation are outside the existing DataPulse lifecycle and must not be implied by donor screening |
| weak-signal sentiment, Reddit, or RSS donor output asserted as primary evidence truth | `reject_current_slice` | `aggregator / hybrid / secondary / review_required` | none | derivative weak signals may inform review, but they cannot be promoted into primary evidence or machine-trusted truth in this wave |

These verdicts intentionally keep the donor bounded to docs-only screening truth plus future sidecar or wrapper follow-up work. They do not authorize direct runtime admission, scheduled execution, or trading-facing publication.

## SearchGateway Mapping

`SearchGateway` governs provider execution and search-provider mediation. It should use the same source-governance language without pretending that gateway execution fully classifies the underlying destination URL.

Provider-layer mapping:

| Search-gateway layer | Contract value |
| --- | --- |
| `source_class` | `aggregator` |
| `collection_mode` | `search_gateway` |
| `authority` | `secondary` |
| `sensitivity` | `review_required` |
| `compliance_hints` | `search_results_require_verification`, `respect_source_terms`, `operator_review_required`, `no_automated_legal_determination` |

Gateway rules:

1. search-provider results are discovery leads, not verified evidence by themselves
2. provider choice, fallback, and retries belong to gateway governance
3. destination URL classification still belongs to `SourceCatalog.resolve_source()` or explicit operator review
4. gateway audit metadata is provenance about how the result was discovered, not a compliance approval signal

## Manual Fact Intake Mapping

Manual fact intake is first-class but bounded:

| Field | Default value |
| --- | --- |
| `source_class` | `analyst` |
| `collection_mode` | `manual_fact` |
| `authority` | `secondary` unless an operator records stronger provenance separately |
| `sensitivity` | `review_required` |
| `compliance_hints` | `manual_entry_requires_attribution`, `operator_review_required`, `no_automated_legal_determination` |

Manual fact intake is allowed as a source path, but it must remain attributable and operator-reviewed.

## Example Shape

```json
{
  "source_id": "builtin_github",
  "source_type": "github",
  "name": "GitHub Open Source",
  "tier": 1,
  "authority_weight": 0.92,
  "governance": {
    "source_class": "platform",
    "collection_mode": "public_web",
    "authority": "primary",
    "sensitivity": "public",
    "compliance_hints": [
      "public_content_only",
      "respect_source_terms",
      "respect_rate_limits",
      "no_automated_legal_determination"
    ]
  }
}
```

## Invariants

The following invariants should hold for follow-up work:

1. public-web, API, search-gateway, and manual fact intake remain explicit collection modes
2. DataPulse may expose compliance hints, but it must not imply automated legal determination
3. source-governance vocabulary should be shared by SourceCatalog, search-gateway docs, and future triage/story governance work
4. source-governance fields describe boundaries and review posture; they do not silently change evidence truth on their own
