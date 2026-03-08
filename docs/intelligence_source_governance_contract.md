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
