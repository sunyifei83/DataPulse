# QNAIGC Provider Contract (Repo Draft)

## Scope

This contract defines the non-runtime boundaries for introducing QNAIGC into `SearchGateway` as a narrowly-scoped
candidate provider.

It is intentionally a draft-locked contract: implementation details are described as "reserved for L18.3+".

## In-Scope Facts

- Provider name: `qnaigc`
- API endpoint: `POST https://api.qnaigc.com/v1/search/web`
- Candidate mode: only through `provider="auto"` in `SearchGateway.search(...)`
- Explicit mode behavior:
  - `provider="jina"` should continue as `["jina"]`
  - `provider="tavily"` should continue as `["tavily", "jina"]` if fallback remains required
  - `provider="auto"` may include QNAIGC ahead of current default chain only when the query is classified as Chinese-oriented
- Default runtime precedence target:
  - tavily/jina remain the explicit default chain
  - QNAIGC is an optional auto-only candidate path

## Query Classification

QNAIGC candidate routing is only considered when a query is likely Chinese-centric.

At L18.2, the contract freeze is:

- Chinese-oriented pattern source: at least one Han character in query input
- The exact detection implementation is deferred to runtime slice L18.3
- Locale-sensitive gating must be explicitly observable by configuration

## Token and Runtime Injection Boundary

- Token candidates: `QNAIGC_TOKEN_A`, `QNAIGC_TOKEN_B`
- Resolution order: A first, then B
- Token values must be loaded through existing secret-loading boundary (no repo persistence)
- If no token can be resolved, QNAIGC must not be considered as a candidate and must fail closed for the candidate lane

## Result Normalization

For every QNAIGC result mapped to `SearchHit`:

- keep canonical fields (`title`, `url`, `snippet`, `provider`, `source`, `score`) as the base contract
- keep provider-unique raw fields in `SearchHit.extra`, including:
  - `authority_score`
  - `date`
  - `request_id`

## Cost and Safety Constraints

- Default expected unit cost from external input: `0.036 元 / 次`
- Per-call cost controls must be operator-visible before auto-wider routing is enabled
- `max_results` and `site_filter` should stay within API-specified ceilings:
  - `max_results` <= 50
  - `site_filter` <= 20 entries
- Candidate-lane behavior must remain fail-closed on missing token, provider contract drift, or 429

## Contract Artifacts

- `datapulse/core/config.py` fields for candidate gating and constraints
- `docs/search_gateway_config.md` for operator visibility
- implementation handoff to L18.3 for adapter wiring
