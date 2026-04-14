# DataPulse Native Collector Bridge Contract

## Purpose

This document defines the contract of record for `L9.2`.

It fixes the shortlist order, sidecar invocation boundary, env/session dependencies, `ParseResult` normalization rules, provenance markers, and fallback policy for future Chinese-source integrations.

This slice does not land any native collector implementation by itself. It only defines the contract that later slices must follow.

## Scope

This contract covers:

- sidecar-backed native collectors for Chinese-source acquisition
- the request/response boundary between DataPulse collectors and an external bridge process
- normalization into the existing `ParseResult` dataclass
- operator-visible provenance and fallback semantics
- the target shortlist for `L9.3` through `L9.6`

This contract does not cover:

- vendoring third-party collector repositories into the DataPulse tree
- removing current `jina`, browser, or generic fallbacks
- changing scheduled governance workflows into business executors
- introducing new first-class `SourceType` values outside their own blueprint slices
- treating tradingview-style quote, regime, robustness, or contra tooling as a generic market-runtime extension of `DATAPULSE_NATIVE_COLLECTOR_BRIDGE_CMD`

## Current Repo Anchors

| Surface | Current fact | Contract consequence |
| --- | --- | --- |
| `datapulse/core/router.py` | routing already prefers platform collectors, then falls back across the existing parser stack | native paths must plug in as normal collectors instead of inventing a second router |
| `datapulse/collectors/base.py` | `ParseResult` is the stable collector output shape | every bridge response must normalize into this shape before it reaches Reader, triage, or story layers |
| `datapulse/collectors/wechat.py` | current order is `jina` first, then optional browser fallback | future native WeChat work must preserve this safety net until the native path is proven |
| `datapulse/collectors/xhs.py` | current order is `jina` first, then session-backed browser fallback | future `MediaCrawler`-class work must keep the current XHS fallback chain intact |
| `datapulse/core/utils.py` | `DATAPULSE_SESSION_DIR`, `session_path(...)`, and `session_valid(...)` already define the repo's session boundary | native bridge work must reuse this boundary instead of inventing an unrelated session layout |

## Shortlist Order

The current shortlist order is fixed as:

1. `MediaCrawler`
2. `wechat_spider`
3. `weiboSpider`
4. `GeneralNewsExtractor`

Contract meaning:

| Order | Profile id | Target slice | Contract role |
| --- | --- | --- | --- |
| 1 | `mediacrawler` | `L9.3` | highest-reach sidecar profile for XHS plus broader Chinese-platform collection |
| 2 | `wechat_spider` | `L9.4` | native WeChat article path with explicit fallback to the existing collector chain |
| 3 | `weibo_spider` | `L9.5` | first direct Weibo bridge path for a current router gap |
| 4 | `general_news_extractor` | `L9.6` | Chinese-news正文 extraction backend that shares the same normalization and provenance vocabulary |

`TrendRadar`, `EasySpider`, `Crawlab`, and `f2` stay out of this bridge contract. They belong to later trend-feed or manual-lane slices.

## Activation Boundary

Native bridge execution stays opt-in.

If the bridge command is not configured, or if a profile-specific prerequisite is missing, DataPulse must skip the native path and continue through the current fallback chain.

### Canonical env and session dependencies

| Dependency | Meaning | Contract rule |
| --- | --- | --- |
| `DATAPULSE_NATIVE_COLLECTOR_BRIDGE_CMD` | command used to invoke the bridge sidecar | required to enable any sidecar-backed native profile |
| `DATAPULSE_NATIVE_COLLECTOR_BRIDGE_WORKDIR` | optional working directory for the bridge process | used when the sidecar depends on its own checkout or runtime files |
| `DATAPULSE_NATIVE_COLLECTOR_BRIDGE_TIMEOUT_SECONDS` | default bridge timeout | should default to a finite value such as `45` seconds; collector-specific overrides may go lower but not higher silently |
| `DATAPULSE_NATIVE_COLLECTOR_STATE_DIR` | writable sidecar scratch/state directory | defaults to `~/.datapulse/native_collectors` when unset |
| `DATAPULSE_SESSION_DIR` | shared Playwright session directory already used by current collectors | remains the canonical home for session files passed into the native bridge |

Profile-specific session posture:

| Profile id | Session key | Current posture |
| --- | --- | --- |
| `mediacrawler` | `xhs` when an authenticated XHS path is needed | may run anonymously, but must declare session usage when it consumes stored login state |
| `wechat_spider` | `wechat` | may require the existing WeChat session file; if missing, it should return a soft failure and allow fallback |
| `weibo_spider` | `weibo` | reserved for future use; until a dedicated Weibo login path exists, the bridge must not reuse `wechat` or `xhs` state files |
| `general_news_extractor` | none | no session dependency |

Sidecar-owned cookies, API keys, or repo-specific secrets may exist, but they stay sidecar-local. This contract only guarantees the shared DataPulse env/session boundary above.

## Invocation Contract

Sidecar invocation must stay machine-readable:

1. DataPulse invokes the configured command as a subprocess.
2. The request payload is one JSON document on `stdin`.
3. The sidecar response is one JSON document on `stdout`.
4. Human-readable logs belong on `stderr`.
5. Invalid JSON, a non-zero exit, or a timeout is treated as `bridge_unavailable` and remains fallback-eligible.

### Request shape

```json
{
  "schema_version": "native_collector_bridge_request.v1",
  "profile": "mediacrawler",
  "url": "https://www.xiaohongshu.com/explore/abc123",
  "source_type_hint": "xhs",
  "timeout_seconds": 45,
  "session": {
    "key": "xhs",
    "path": "/Users/example/.datapulse/sessions/xhs.json",
    "required": false
  },
  "metadata": {
    "allow_fallback": true,
    "fallback_chain": [
      "jina",
      "browser"
    ]
  }
}
```

Required request fields:

| Field | Meaning |
| --- | --- |
| `schema_version` | fixed as `native_collector_bridge_request.v1` |
| `profile` | one of the shortlisted profile ids |
| `url` | target URL |
| `source_type_hint` | current collector intent such as `wechat`, `xhs`, or `generic` |
| `timeout_seconds` | execution deadline for the sidecar attempt |

Optional request fields:

| Field | Meaning |
| --- | --- |
| `session` | shared session metadata passed from `session_path(...)` when a profile may use login state |
| `metadata` | operator-visible execution hints such as the planned fallback chain |

## Result Contract

### Success shape

```json
{
  "schema_version": "native_collector_bridge_result.v1",
  "ok": true,
  "profile": "mediacrawler",
  "canonical_url": "https://www.xiaohongshu.com/explore/abc123",
  "source_type": "xhs",
  "title": "Example title",
  "content": "Example body text",
  "author": "Example author",
  "excerpt": "Example body text",
  "tags": [
    "xhs",
    "native-bridge",
    "mediacrawler"
  ],
  "confidence_flags": [
    "native-bridge",
    "session-authenticated"
  ],
  "extra": {
    "engagement": {
      "like_count": 12
    }
  },
  "provenance": {
    "collector_family": "native_sidecar",
    "bridge_profile": "mediacrawler",
    "transport": "subprocess_json",
    "session_key": "xhs",
    "session_mode": "playwright_storage_state",
    "raw_source_type": "xhs",
    "fallback_policy": "xhs_native_then_jina_then_browser"
  }
}
```

### Failure shape

```json
{
  "schema_version": "native_collector_bridge_result.v1",
  "ok": false,
  "profile": "wechat_spider",
  "error_code": "login_required",
  "error": "wechat session missing",
  "retryable": false,
  "provenance": {
    "collector_family": "native_sidecar",
    "bridge_profile": "wechat_spider",
    "transport": "subprocess_json",
    "session_key": "wechat",
    "session_mode": "playwright_storage_state",
    "raw_source_type": "wechat",
    "fallback_policy": "wechat_native_then_jina_then_browser"
  }
}
```

## `ParseResult` Normalization

Bridge responses normalize into `ParseResult` with these rules:

| Bridge field | `ParseResult` target | Rule |
| --- | --- | --- |
| `canonical_url` | `url` | use `canonical_url` when present, otherwise keep the request URL |
| `title` | `title` | trim whitespace; empty string is allowed but not preferred |
| `content` | `content` | must be non-empty for a successful normalized result |
| `author` | `author` | copy through when available |
| `excerpt` | `excerpt` | use sidecar excerpt when present, otherwise let DataPulse generate one from normalized content |
| `source_type` | `source_type` | map to the closest current `SourceType`; if the type is not yet modeled, keep `SourceType.GENERIC` and expose the raw platform in provenance plus tags |
| `tags` | `tags` | must include the platform tag, `native-bridge`, and the bridge profile id |
| `confidence_flags` | `confidence_flags` | must include `native-bridge`; session-backed runs should also add `session-authenticated` |
| `extra` + `provenance` | `extra["collector_provenance"]` plus other `extra` data | provenance is preserved under `extra["collector_provenance"]`; other structured payload remains under `extra` |

Minimum completeness rule:

- a bridge result with `ok=true` but empty or near-empty `content` should be treated as a degraded failure and remain fallback-eligible

Source-type rule before future slices land:

- `weibo` or other not-yet-modeled platform codes must not silently become new first-class router semantics
- until their own slices land, those platform codes stay visible through `tags` and `extra["collector_provenance"]["raw_source_type"]`

## Provenance Markers

All native bridge results must expose a canonical provenance object at `extra["collector_provenance"]`.

Required fields:

| Field | Meaning |
| --- | --- |
| `collector_family` | `native_sidecar` for subprocess bridges, `native_library` for future in-process extractor integrations |
| `bridge_profile` | shortlisted profile id |
| `transport` | `subprocess_json` or `in_process` |
| `session_key` | `wechat`, `xhs`, `weibo`, or empty string |
| `session_mode` | `playwright_storage_state`, `sidecar_cookie_store`, or `none` |
| `raw_source_type` | platform code emitted by the bridge |
| `fallback_policy` | named fallback chain for the collector surface |

Optional fields:

- `sidecar_name`
- `sidecar_version`
- `warnings`
- `rate_limit_window`

The goal is simple: operators must be able to tell whether DataPulse used a native bridge, what profile it used, whether login state was consumed, and what fallback chain remained available.

## Fallback Policy

The fallback policy stays explicit and conservative:

| Surface | Native target | Required fallback behavior |
| --- | --- | --- |
| WeChat | `wechat_spider` | `native -> jina -> browser` |
| XHS and broader `MediaCrawler` lane | `mediacrawler` | `native -> jina -> browser` for current XHS collection; future platform expansion must remain operator-visible |
| Weibo | `weibo_spider` | no first-class collector claim until `L9.5`; failure remains visible and may fall through to later generic handling if a dedicated collector is not yet registered |
| Chinese news正文 | `general_news_extractor` | `native-like extractor -> trafilatura -> BeautifulSoup -> Firecrawl -> Jina` |

Failure-code policy:

| `error_code` | Expected behavior |
| --- | --- |
| `bridge_unavailable` | continue fallback and surface the setup issue in logs or hints |
| `prereq_missing` | continue fallback and surface the missing dependency |
| `login_required` | continue fallback and surface the missing session requirement |
| `rate_limited` | continue fallback unless the caller explicitly chooses to stop |
| `policy_blocked` | continue fallback when an existing safe fallback exists |
| `unsupported_url` | continue fallback |

No native bridge attempt may suppress a currently available fallback path merely because the sidecar is installed.

## Excluded Local Market Wrapper Boundary

Future tradingview-style market tooling is outside this native collector bridge contract.

If DataPulse later uses a local wrapper or sidecar for quote snapshots, technical-regime checks, robustness runs, or sentiment-contra helpers, that path must stay outside the native collector shortlist and outside scheduled governance execution.

Boundary rules:

1. do not reuse `DATAPULSE_NATIVE_COLLECTOR_BRIDGE_CMD` as a generic market-tooling executor
2. keep any such path local/manual and operator-visible rather than promoting it into `.github/workflows/governance-loop-auto.yml` or another scheduled governance runner
3. admit repo-visible outputs only through existing watchlist seed, market-context sidecar, or manual-acquisition handoff semantics
4. do not let wrapper-local output become first-class collector truth, a new public trading surface, or wrapper-owned business truth outside the lifecycle contract

## Invariants For Follow-Up Slices

1. Native collector work stays contract-first and opt-in.
2. `DATAPULSE_SESSION_DIR` remains the shared session boundary.
3. All native outputs must normalize into `ParseResult` and `extra["collector_provenance"]`.
4. Fallback order remains visible to operators and unchanged until a later slice explicitly proves otherwise.
5. `GeneralNewsExtractor` shares the same normalization and provenance vocabulary even if `L9.6` lands as an in-process backend instead of a subprocess sidecar.
