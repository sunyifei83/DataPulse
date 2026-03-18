# DataPulse QNAIGC Search Candidate Provider Blueprint

## Purpose

This document promotes the QNAIGC web-search suggestion into repository-scoped blueprint truth.

The goal is not to replace the current `tavily/jina` chain or to smuggle provider-specific result fields into shared business objects. The goal is to add one narrow China-oriented candidate lane that can improve Chinese-query coverage while preserving `SearchHit` normalization, current fallback semantics, and explicit operator control over cost.

## Current Repo Read

DataPulse already has the right integration seam for this wave:

- `datapulse/core/search_gateway.py`
- `datapulse/core/config.py`
- `datapulse/reader.py`
- `docs/search_gateway_config.md`

Current repo reality:

- the repo already centralizes provider routing through `SearchGateway`
- `SearchHit` is the canonical normalized search result object
- `auto` and `multi` are the existing routing modes
- provider preference is currently `tavily,jina`
- search-provider facts already flow through `extra`, `raw`, and audit metadata instead of mutating higher-level lifecycle objects

That changes the next highest-leverage delta.

The next delta is not "add another search API because it exists." The next delta is to add a narrow candidate provider that is useful exactly where the current chain is weaker: Chinese-language discovery with explicit structured result metadata.

## High-Value Capability To Extract

The QNAIGC web-search API is valuable to DataPulse for four reasons:

1. it exposes a simple REST endpoint for web search with structured JSON results
2. it supports `time_filter` and `site_filter`, which maps cleanly to current gateway inputs
3. result items already include `date` and `authority_score`
4. the response carries a request-level `request_id`, which is useful provenance for troubleshooting and operator review

Repo implication:

- DataPulse should treat QNAIGC as a search-provider candidate with stronger Chinese-query relevance and richer per-result provenance, not as a second lifecycle or a special-case business object model

## Constraints This Wave Must Preserve

Invariants for this wave:

1. `SearchHit` remains the shared result contract
2. provider-specific fields such as `authority_score`, `date`, and `request_id` must stay in `SearchHit.extra`
3. `raw` may retain the provider payload, but downstream code must continue to work against normalized `SearchHit`
4. QNAIGC should first appear only as an `auto` candidate for Chinese-language queries; it should not replace the current default `tavily/jina` chain
5. the repo should preserve existing `jina` and `tavily` explicit modes
6. pricing and usage limits must be operator-visible before runtime activation is considered
7. secrets remain runtime-injected; no token value belongs in repo truth

## Cost And Usage Guardrails

Known external constraints for manual planning:

- provider endpoint: `POST https://api.qnaigc.com/v1/search/web`
- `max_results` default `20`, maximum `50`
- `site_filter` maximum `20`
- structured result metadata includes `date`, `authority_score`, and response-level `request_id`
- operator-provided cost assumption: `0.036 元 / 次`
- the public API page reviewed for this blueprint does not expose a clear machine-readable QPS quota, so rate-limit handling must remain conservative and fail closed on `429`

Repo implication:

- this provider should not be activated as an unrestricted first-hop default
- manual ignition should begin with low-volume Chinese-query smoke tests and explicit budget awareness
- future implementation should expose provider-level timeout, retry, and disable controls through existing gateway config patterns instead of hardcoding a "cheap enough" assumption

## Runtime Credential Boundary

Manual test preparation can reuse locally authorized runtime tokens without creating a new credential file:

- `~/.config/modelbus/modelbus.local.env`
- `QNAIGC_TOKEN_A`
- `QNAIGC_TOKEN_B`

Repo rule:

- implementation may read a runtime-selected QNAIGC token through the existing secret-loading boundary, but the repository must never persist token values, rotated aliases, or account-specific billing assumptions

## What Should Not Be Reopened In This Wave

This wave should not reopen:

- a second search result object beside `SearchHit`
- a default-provider replacement for all queries
- provider-specific branching inside triage, story, report, or delivery code
- hidden locale routing with no operator-visible audit trail
- broad-cost experimentation before manual ignition guardrails exist

## L18 Slice Map

| Slice | Outcome | Why it exists |
| --- | --- | --- |
| `L18.1` | Land this repo-scoped QNAIGC search-provider blueprint and manual ignition map | Converts the suggestion into active repo truth before config or runtime work starts drifting |
| `L18.2` | Define the QNAIGC provider contract, routing rules, and runtime config boundary | Freezes how Chinese-query candidate routing, token lookup, cost guardrails, and `SearchHit.extra` mapping should work before adapter code lands |
| `L18.3` | Add the QNAIGC provider adapter, normalized `SearchHit` mapping, and Chinese-query auto-candidate routing | Lands the narrow runtime value without changing the shared result contract or replacing current explicit providers |
| `L18.4` | Harden verification, diagnostics, and manual ignition guidance for QNAIGC search usage | Makes provider cost, rate-limit behavior, and fallback semantics operator-visible before broader promotion discussion |

## Manual Ignition Handoff

`L18.2` is the contract-freeze slice for this wave. Once the provider contract and config boundary are explicit in repo truth, the next manual ignition target should move to `L18.3`.

Recommended order after this refresh:

1. `L18.2`
2. `L18.3`
3. `L18.4`

This handoff keeps the next work narrow:

- first freeze provider routing, config, and provenance semantics
- then add the adapter and Chinese-query candidate lane
- then harden cost-aware diagnostics, smoke paths, and verification

## One-Line Direction

`DataPulse` should treat QNAIGC web search as a cost-aware Chinese-query candidate provider behind `SearchGateway`: preserve `SearchHit` normalization, store `authority_score/date/request_id` in `extra`, and stage activation through explicit manual ignition rather than replacing the current `tavily/jina` default chain.
