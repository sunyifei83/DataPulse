# DataPulse ModelBus Bridge Contract

## Purpose

This document defines the contract of record for `L16.3`.

It fixes the stable bridge between DataPulse AI assistance surfaces and a ModelBus runtime without binding DataPulse business code to provider SDK details, provider credential formats, or provider-specific fallback logic.

## Scope

This contract covers:

- the repo-facing runtime inputs that DataPulse may own for AI assistance calls
- the mapping from DataPulse surface ids to ModelBus alias keys
- the normalized request and result envelope between DataPulse and ModelBus
- secret and configuration boundaries between the DataPulse repo and the ModelBus runtime
- fallback and degradation ownership so route policy stays visible without being reimplemented in DataPulse

This contract does not cover:

- direct provider SDK imports in DataPulse business modules
- copying ModelBus provider routing, token pools, whitelists, or multi-provider orchestration into this repo
- structured AI output schemas, admission facts, or Reader-backed runtime services from `L16.4` through `L16.6`
- turning `.github/workflows/governance-loop-auto.yml` into a business executor

## Current Repo Anchors

| Surface | Current fact | Contract consequence |
| --- | --- | --- |
| `docs/intelligence_lifecycle_contract.md` | DataPulse already defines governed AI surfaces as `mission_suggest`, `triage_assist`, `claim_draft`, `report_draft`, and `delivery_summary` | the bridge must accept stable surface ids rather than provider-specific model names |
| `docs/governance/datapulse-modelbus-ai-governance-blueprint.md` | the AI wave already requires `off / assist / review` semantics and ModelBus-backed routing | the bridge must preserve mode and surface context without widening DataPulse authority |
| `datapulse/reader.py`, CLI, MCP, console projection docs | Reader-backed parity remains the governing rule for future AI runtime work | one bridge contract must serve Reader, CLI, MCP, API, and console projection instead of tool-local wiring |
| `docs/governance/datapulse-evidence-backend-contract.md` | backend boundaries in this repo already preserve deterministic fallback and visible provenance | the ModelBus bridge should behave like another governed backend boundary with explicit fallback facts |
| named route and delivery governance docs | DataPulse already distinguishes reusable route identity from transport configuration | surface-to-alias mapping should be stable config, while provider routing stays inside ModelBus |

## Bridge Boundary

The bridge contract is:

`DataPulse governed AI surface -> ModelBus alias lookup -> ModelBus runtime request -> structured result plus runtime facts`

Boundary rules:

1. DataPulse chooses the business surface, lifecycle object context, and switch mode.
2. DataPulse may provide repo-facing bridge inputs only: `base_url`, `bus_key`, `alias_by_surface`, timeout, and request metadata.
3. ModelBus owns provider selection, provider credentials, route expansion, retries, fallback order, degradation logic, and transport-specific compatibility.
4. DataPulse receives a normalized response plus runtime facts; it does not receive or manage provider SDK objects.
5. If the bridge is disabled, unavailable, or invalid, DataPulse must stay on governed manual or deterministic behavior for the affected surface.

## Canonical Bridge Inputs

DataPulse must normalize bridge configuration to one repo-facing object before any runtime call lands:

```json
{
  "schema_version": "datapulse_modelbus_bridge_config.v1",
  "base_url": "https://modelbus.internal",
  "bus_key": "env:DATAPULSE_MODELBUS_BUS_KEY",
  "alias_by_surface": {
    "mission_suggest": "dp.mission.suggest",
    "triage_assist": "dp.triage.assist",
    "claim_draft": "dp.claim.draft",
    "report_draft": "dp.report.draft",
    "delivery_summary": "dp.delivery.summary"
  },
  "timeout_seconds": 20,
  "fallback_policy": "modelbus_owned",
  "metadata": {
    "caller": "reader",
    "allow_degraded_result": true
  }
}
```

Required fields:

| Field | Meaning |
| --- | --- |
| `schema_version` | fixed as `datapulse_modelbus_bridge_config.v1` |
| `base_url` | the ModelBus runtime endpoint DataPulse calls |
| `bus_key` | the DataPulse-held secret or secret reference used to authenticate to ModelBus |
| `alias_by_surface` | mapping from DataPulse surface id to one stable ModelBus alias key |
| `timeout_seconds` | request timeout DataPulse applies to the bridge call |
| `fallback_policy` | must resolve to `modelbus_owned` for this phase |

Optional fields:

| Field | Meaning |
| --- | --- |
| `metadata` | caller-visible hints such as projection surface or request tags |
| `default_alias` | optional alias for future non-surface-specific requests; current governed surfaces should still resolve explicitly |

Normalization rules:

- DataPulse may source values from env, secret storage, or a future repo config file, but runtime code must consume the normalized shape above.
- `bus_key` may be stored as a secret reference at rest, but the effective call must carry the resolved credential only at runtime.
- `alias_by_surface` must be explicit for every governed AI surface in `L16.2`; missing alias lookup is a fail-closed condition.
- `fallback_policy` is declarative in DataPulse and operational in ModelBus. DataPulse may ask whether degraded results are acceptable, but it does not own the fallback chain.

## Surface-To-Alias Mapping

The stable mapping rule for this phase is:

| DataPulse surface | Alias ownership | Allowed meaning |
| --- | --- | --- |
| `mission_suggest` | DataPulse config chooses alias key | mission-planning suggestion route only |
| `triage_assist` | DataPulse config chooses alias key | triage explanation or candidate-judgment route only |
| `claim_draft` | DataPulse config chooses alias key | claim drafting route only |
| `report_draft` | DataPulse config chooses alias key | report composition route only |
| `delivery_summary` | DataPulse config chooses alias key | delivery explanation and summary route only |

Mapping rules:

1. DataPulse owns which alias key a governed surface calls.
2. ModelBus owns what providers, models, or fallback routes satisfy that alias key.
3. Alias keys are stable governance identifiers, not provider names.
4. Surface ids and alias keys must not drift by Reader, CLI, MCP, API, or browser surface.
5. DataPulse business modules must not inspect alias internals to infer provider family or model brand.

## Secret And Ownership Boundary

### DataPulse-owned inputs

DataPulse may own only the minimum bridge-facing secrets and config needed to make a ModelBus request:

- `base_url`
- `bus_key`
- `alias_by_surface`
- `timeout_seconds`
- caller metadata such as `surface`, `mode`, request id, and object references

DataPulse must not own:

- provider API keys
- provider account topology
- route expansion or provider fallback sequences
- model whitelist internals beyond the chosen alias key
- token-pool, quota, or billing orchestration

### ModelBus-owned runtime concerns

ModelBus owns:

- alias-to-provider or alias-to-route expansion
- provider compatibility rules
- retries, fallback order, and degraded route selection
- provider-specific auth material
- runtime metrics, traces, and audit for downstream execution

Boundary rule:

- DataPulse authenticates to ModelBus; ModelBus authenticates to downstream providers.

## Common Invocation Envelope

### Request shape

```json
{
  "schema_version": "datapulse_modelbus_bridge_request.v1",
  "surface": "triage_assist",
  "mode": "assist",
  "alias": "dp.triage.assist",
  "subject": {
    "kind": "DataPulseItem",
    "id": "item-123"
  },
  "input": {
    "operator_prompt": "Explain likely duplicate risk",
    "payload_ref": "triage:item-123"
  },
  "governance": {
    "allow_final_state_write": false,
    "allow_degraded_result": true,
    "schema_contract": "pending_l16_4"
  },
  "runtime": {
    "request_id": "req-123",
    "timeout_seconds": 20
  }
}
```

Required request fields:

| Field | Meaning |
| --- | --- |
| `schema_version` | fixed as `datapulse_modelbus_bridge_request.v1` |
| `surface` | one governed DataPulse AI surface id |
| `mode` | `off`, `assist`, or `review`; `off` should short-circuit before the bridge call |
| `alias` | resolved alias from `alias_by_surface[surface]` |
| `subject` | canonical lifecycle object reference |
| `input` | surface-specific payload prepared by DataPulse |
| `governance` | DataPulse-owned execution constraints |
| `runtime` | request id and timeout data |

### Result shape

```json
{
  "schema_version": "datapulse_modelbus_bridge_result.v1",
  "ok": true,
  "surface": "triage_assist",
  "mode": "assist",
  "alias": "dp.triage.assist",
  "result": {
    "payload": {},
    "raw_contract": "pending_l16_4"
  },
  "runtime_facts": {
    "status": "applied",
    "degraded": false,
    "fallback_used": false,
    "served_by_alias": "dp.triage.assist",
    "latency_ms": 182,
    "request_id": "req-123"
  }
}
```

Failure shape:

```json
{
  "schema_version": "datapulse_modelbus_bridge_result.v1",
  "ok": false,
  "surface": "report_draft",
  "mode": "assist",
  "alias": "dp.report.draft",
  "error_code": "bridge_unavailable",
  "error": "ModelBus request timed out",
  "runtime_facts": {
    "status": "fallback_used",
    "degraded": true,
    "fallback_used": true,
    "served_by_alias": "dp.report.draft",
    "request_id": "req-456"
  }
}
```

Result rules:

- the bridge result must stay provider-agnostic at the DataPulse boundary
- runtime facts must expose whether degradation or fallback happened, but need not expose provider secrets or provider-specific topology
- invalid JSON, missing required fields, or unknown surface/alias binding is bridge failure, not silent success
- a later `L16.4` contract may replace `raw_contract: pending_l16_4` with concrete schema ids, but it must keep the same bridge envelope

## Fallback And Degradation Ownership

Fallback policy ownership is fixed in this phase:

1. DataPulse decides whether a surface is `off`, `assist`, or `review`.
2. DataPulse decides whether a degraded AI result is admissible for that surface invocation.
3. ModelBus decides provider retry order, route fallback, and degraded serving behavior behind the alias.
4. DataPulse decides how to expose fallback or degradation facts to operators and whether the returned payload may be considered for downstream review.
5. DataPulse must fail closed to manual or deterministic behavior when the bridge result is missing, invalid, or disallowed by governance mode.

This means:

- DataPulse owns business fallback to manual review or deterministic no-op.
- ModelBus owns runtime fallback across providers or routes.
- neither side may hide fallback from operator-visible governance facts.

## Invariants

The following invariants should hold for all follow-up work:

1. DataPulse business code addresses governed AI work by surface id and alias key, not by provider SDK.
2. `bus_key` is the only bridge secret DataPulse needs for this contract; downstream provider secrets stay outside the repo boundary.
3. surface-to-alias mapping is explicit and machine-readable for every governed surface.
4. missing alias config, missing `bus_key`, or bridge schema failure must fail closed.
5. ModelBus runtime fallback must remain visible as returned runtime facts, not hidden prompt behavior.
6. the bridge must be reusable by Reader, CLI, MCP, API, and console projection without changing surface semantics.
7. this contract does not authorize AI to write final triage, report, or dispatch state.

## Implications For Follow-up Slices

- `L16.4` should bind concrete structured output schema ids onto the `result.payload` contract without changing bridge ownership.
- `L16.5` should admit or reject alias-backed capabilities per surface, rather than embedding admission in provider-specific code paths.
- `L16.6` should place Reader-backed AI services behind this bridge instead of talking to providers directly.
- `L16.7` should project the same surface ids, alias-derived runtime facts, and fallback observations across CLI, MCP, API, and console.
