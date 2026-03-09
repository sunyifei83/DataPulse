# DataPulse Evidence Backend Contract

## Purpose

This document defines the contract of record for `L10.1`.

It creates one optional backend contract for post-collection evidence enrichment across grounding and factuality work.

The contract fixes invocation boundaries, deterministic fallback behavior, and operator-visible provenance before any `LangExtract`-class or `OpenFactVerification`-class adapter lands.

## Scope

This contract covers:

- optional backend enrichment behind `build_item_grounding(...)` and `build_factuality_gate(...)`
- a shared request/result envelope that future adapters may satisfy through `in_process` or `subprocess_json` transport
- fallback rules that preserve the current deterministic repo behavior when a backend is disabled, unavailable, or invalid
- provenance placement rules that keep backend activity visible to operators without reopening collector architecture

This contract does not cover:

- changing collector routing, `ParsePipeline`, or the native collector bridge contract
- replacing the current heuristic grounding path or deterministic factuality gate
- inventing a parallel claim store, a second story model, or a hidden reviewer workflow
- turning `.github/workflows/governance-loop-auto.yml` into a business executor

## Current Repo Anchors

| Surface | Current fact | Contract consequence |
| --- | --- | --- |
| `datapulse/core/triage.py` | `build_item_grounding(...)` is the stable item-level grounding boundary and currently returns `provided`, `heuristic`, or `empty` | any future grounding backend must sit behind this function and preserve the local fallback path |
| `datapulse/core/triage.py` | `build_item_governance(...)` already stores grounding under the existing governance payload | backend grounding must enrich the current governance object rather than create a parallel claim product |
| `datapulse/core/story.py` | `build_factuality_gate(...)` already emits operator-visible `status / score / reasons / signals / operator_action` | any future factuality backend must preserve this deterministic gate as the canonical delivery boundary |
| `datapulse/core/story.py`, `datapulse/core/alerts.py`, and `datapulse/reader.py` | story export, digest, alert, and reader surfaces already consume grounding and factuality payloads | backend provenance must remain visible through these same surfaces instead of hiding in side channels |
| `docs/governance/datapulse-native-collector-bridge-contract.md` | collection provenance already has its own contract under `extra["collector_provenance"]` | evidence backend provenance must not masquerade as collector provenance |

## Surface Boundary

| Surface | Canonical invocation boundary | Backend role allowed by this contract | Out of scope |
| --- | --- | --- | --- |
| Grounding | `build_item_grounding(item)` after checking for structured provided claims and before returning the deterministic fallback | optional item-level claim and evidence-span extraction | collector changes, cross-item clustering, or story synthesis |
| Factuality | `build_factuality_gate(...)` after evidence rows are selected for a delivery surface | optional advisory backend review of the already computed delivery trust boundary | silent overwrite of deterministic gate fields, collector mutation, or hidden delivery automation |

Boundary note:

- story grounding remains a projection of item-level grounding already present in governance payloads; `L10.1` does not create a separate story-only backend lane

## Activation And Transport

Evidence backend execution stays opt-in.

If no backend is configured, or if a backend dependency is missing, times out, exits non-zero, or returns invalid data, DataPulse must keep running the current deterministic path.

Transport may be either:

- `in_process` for an optional Python dependency or local library wrapper
- `subprocess_json` for a sidecar process that accepts JSON on `stdin` and returns JSON on `stdout`

Both transports must normalize to the same contract below.

Scheduled governance automation stays read-only:

- no backend call defined here may require `.github/workflows/governance-loop-auto.yml` to execute business collection, grounding, or verification work

## Common Invocation Envelope

### Request shape

```json
{
  "schema_version": "evidence_backend_request.v1",
  "surface": "grounding",
  "subject": "item",
  "backend_kind": "langextract_class",
  "input": {
    "item_id": "item-123",
    "title": "Example title",
    "content": "Example body text",
    "source_link": {
      "item_id": "item-123",
      "title": "Example title",
      "url": "https://example.com/story",
      "source_name": "Example Source",
      "source_type": "generic"
    }
  },
  "deterministic": {
    "fallback_mode": "heuristic",
    "claim_count": 1,
    "evidence_span_count": 1
  },
  "metadata": {
    "allow_fallback": true,
    "repo_surface": "triage"
  }
}
```

Required request fields:

| Field | Meaning |
| --- | --- |
| `schema_version` | fixed as `evidence_backend_request.v1` |
| `surface` | `grounding` or `factuality` |
| `subject` | `item`, `story`, `digest`, or another current repo surface |
| `backend_kind` | capability class such as `langextract_class` or `openfactverification_class` |
| `input` | surface-specific payload |
| `deterministic` | the local fallback or deterministic baseline already known to DataPulse |

Optional request fields:

| Field | Meaning |
| --- | --- |
| `metadata` | operator-visible execution hints such as repo surface, allow-fallback posture, or request tags |
| `request_id` | caller-generated correlation id when available |

### Result shape

```json
{
  "schema_version": "evidence_backend_result.v1",
  "ok": true,
  "surface": "grounding",
  "backend_kind": "langextract_class",
  "transport": "subprocess_json",
  "result": {
    "claim_count": 2,
    "evidence_span_count": 2,
    "claims": []
  },
  "provenance": {
    "status": "applied",
    "backend_name": "langextract",
    "backend_version": "0.0.0",
    "request_id": "req-123",
    "latency_ms": 182,
    "used_output": true,
    "warnings": []
  },
  "fallback": {
    "used": false,
    "baseline": "heuristic"
  }
}
```

Failure shape:

```json
{
  "schema_version": "evidence_backend_result.v1",
  "ok": false,
  "surface": "factuality",
  "backend_kind": "openfactverification_class",
  "transport": "in_process",
  "error_code": "backend_unavailable",
  "error": "optional dependency not installed",
  "provenance": {
    "status": "unavailable",
    "backend_name": "openfactverification",
    "warnings": [
      "dependency_missing"
    ]
  },
  "fallback": {
    "used": true,
    "baseline": "deterministic_gate"
  }
}
```

Failure handling rule:

- invalid JSON, schema mismatch, missing required fields, timeout, or empty required output is treated as fallback-eligible backend failure rather than a fatal pipeline error

## Grounding Contract

Grounding remains item-local and source-linked.

The backend may only return claims that can be anchored to the same item's title or content through explicit evidence spans.

### Grounding precedence rules

1. If structured claims are already present, DataPulse keeps the current `provided` result and does not silently replace it with backend output.
2. If structured claims are absent, DataPulse computes the current deterministic fallback first, which remains `heuristic` or `empty`.
3. If the backend is disabled or unavailable, DataPulse returns that deterministic fallback unchanged.
4. If the backend succeeds, it may replace only the deterministic fallback result and must preserve the fallback baseline in provenance.
5. If backend output is empty, malformed, or not anchored to the current item text, DataPulse discards it and returns the deterministic fallback unchanged.

### Grounding output rules

Grounding backend output must normalize to the existing claim schema:

- `claim_id`
- `text`
- `source_link`
- `evidence_spans`

It may add backend metadata, but it must not:

- point evidence spans at another item or another story
- invent a new cross-item claim object model
- bypass the current source-linked evidence requirement

### Grounding provenance placement

When a grounding backend is configured or attempted, its canonical operator-visible provenance belongs at:

- `governance["grounding"]["backend"]`

Recommended shape:

```json
{
  "status": "applied",
  "backend_kind": "langextract_class",
  "backend_name": "langextract",
  "transport": "subprocess_json",
  "request_id": "req-123",
  "latency_ms": 182,
  "fallback_mode": "heuristic",
  "used_output": true,
  "applied_claim_count": 2,
  "warnings": []
}
```

Status vocabulary:

- `applied`
- `skipped`
- `fallback_used`
- `unavailable`
- `invalid`

Future grounding adapters may add a top-level `mode=backend`, but they must also preserve the deterministic baseline as `fallback_mode`.

## Factuality Contract

Factuality stays downstream of evidence selection and remains operator-visible.

The deterministic factuality gate remains the canonical top-level delivery contract in this phase.

### Factuality precedence rules

1. DataPulse always computes the current deterministic factuality gate first.
2. If no evidence rows are selected, the current deterministic `empty` gate remains final and backend review may be skipped.
3. If the backend is disabled, unavailable, or invalid, the deterministic gate is returned unchanged.
4. Backend verdicts are additive and must remain operator-visible under a dedicated backend field.
5. A backend may add stricter review context, but it must not silently relax a deterministic `blocked` or `review_required` gate to `ready`.

### Factuality output rules

Any backend factuality payload must normalize to an advisory review object with:

- a backend-visible review status
- operator-readable reasons or summary text
- backend-generated signals when present

It must not remove or overwrite the current deterministic:

- `status`
- `score`
- `reasons`
- `signals`
- `operator_action`

### Factuality provenance placement

When a factuality backend is configured or attempted, its canonical operator-visible review belongs at:

- `governance["factuality"]["backend_review"]`

Recommended shape:

```json
{
  "status": "applied",
  "backend_kind": "openfactverification_class",
  "backend_name": "openfactverification",
  "transport": "in_process",
  "request_id": "req-456",
  "latency_ms": 241,
  "deterministic_status": "review_required",
  "backend_status": "review_required",
  "used_output": true,
  "warnings": []
}
```

Operator-visible merge rule:

- if a backend emits extra reasons or signals, they should be attached in `backend_review` or mirrored into top-level output only when they stay clearly labeled as backend-derived

## Provenance Rules

Backend provenance must remain separate from collection provenance.

Required field meanings across both surfaces:

| Field | Meaning |
| --- | --- |
| `status` | whether the backend was applied, skipped, or fell back |
| `backend_kind` | the capability class this backend represents |
| `backend_name` | concrete engine or adapter name |
| `transport` | `in_process` or `subprocess_json` |
| `request_id` | trace id when available |
| `latency_ms` | elapsed backend time when available |
| `used_output` | whether backend output affected the final payload |
| `warnings` | non-fatal backend notes that operators may need to see |

Placement rules:

- use `governance["grounding"]["backend"]` for grounding provenance
- use `governance["factuality"]["backend_review"]` for factuality provenance
- do not write evidence backend activity into `extra["collector_provenance"]`
- do not create a second hidden provenance store when the same truth already exists in the surface payload

## Slice Outcome

`L10.1` is complete when these facts remain true:

- the repo defines one contract for optional grounding and factuality backends
- invocation boundaries are fixed at `build_item_grounding(...)` and `build_factuality_gate(...)`
- disabled or failed backends fall back to current deterministic behavior
- backend activity stays operator-visible through explicit grounding and factuality provenance rather than collector provenance
