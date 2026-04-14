# DataPulse Manual Acquisition Sidecar Contract

## Purpose

This document defines the contract of record for `L9.10`.

It places `EasySpider`, `Crawlab`, and `f2` class tools into an explicit operator-driven emergency acquisition lane.

The lane exists to preserve their value for brittle, login-gated, or media-heavy collection without promoting them into the core `ParsePipeline` or native bridge contract.

## Scope

This contract covers:

- operator-invoked emergency or exception-path acquisition
- handoff from manual tooling into the existing `WatchMission -> DataPulseItem -> triage -> Story` lifecycle
- required run artifacts and provenance for repo-visible intake
- boundary rules that keep manual tooling out of scheduled governance and core collector routing

This contract does not cover:

- automatic invocation from `ParsePipeline`, `WatchDaemon`, or `.github/workflows/governance-loop-auto.yml`
- vendoring third-party operator tools into the repository
- adding new first-class collector profiles or source types beyond the existing `SourceType.MANUAL`
- storing large raw media bundles or browser-export dumps directly in the git tree

## Current Repo Anchors

| Surface | Current fact | Contract consequence |
| --- | --- | --- |
| `docs/intelligence_lifecycle_contract.md` | the canonical lifecycle is `WatchMission -> MissionRun -> DataPulseItem -> Story/evidence package -> delivery` | manual acquisition must hand off into the existing lifecycle instead of inventing a parallel one |
| `datapulse/core/models.py` | the repo already has `SourceType.MANUAL` and `SourceCollectionMode.MANUAL_FACT` | manual emergency intake should use the existing manual source posture instead of pretending to be a first-class native collector |
| `datapulse/core/source_catalog.py` | manual sources default to `source_class=analyst`, `collection_mode=manual_fact`, and `sensitivity=review_required` | operator-driven acquisition stays explicitly review-bound |
| `datapulse/core/storage.py` | `UnifiedInbox` persists `DataPulseItem` objects, not raw crawler job state | manual tool output must be curated before repo-visible intake |
| `datapulse/core/triage.py` and `datapulse/core/story.py` | triage, story, and delivery already preserve item-level provenance | manual lane handoff must emit provenance that downstream surfaces can keep visible |
| `docs/governance/datapulse-native-collector-bridge-contract.md` | `EasySpider`, `Crawlab`, and `f2` are explicitly out of the native bridge shortlist | this lane remains separate from `DATAPULSE_NATIVE_COLLECTOR_BRIDGE_CMD` and `collector_provenance` |

## Lane Membership

| Tool class | Lane role | Why it stays manual | Expected output posture |
| --- | --- | --- | --- |
| `EasySpider` | rapid page capture for brittle or anti-bot-heavy targets | UI-driven flows are useful in emergencies but too brittle to treat as a core collector dependency | operator-reviewed HTML/JSON/CSV export plus screenshots when needed |
| `Crawlab` | operator-run batch or orchestrated spider execution | it is an orchestration plane, not a DataPulse collector contract | run manifest plus exported job results or bundle references |
| `f2` | download-heavy short-video and media-sidecar capture | media download workflows do not map cleanly onto the current text-first collector chain | metadata export plus canonical URLs and external media refs |

`TrendRadar` remains a watch/feed seed input lane under `L9.9`, not part of this manual acquisition contract.

## Activation Rules

Use the manual acquisition lane only when at least one of the following is true:

1. the canonical URL matters, but the existing collector or native bridge cannot capture it in time because of login, rendering, or anti-bot friction
2. the operator needs a one-off emergency capture before content disappears
3. the required output is media-heavy or download-oriented and would be lossy if forced through the normal collector path
4. an external operator tool can narrow the search or extraction scope faster than building a new collector would

Do not use the manual acquisition lane when:

- the current automated collector path already returns enough content
- the work is routine watch execution that should stay in `WatchDaemon` or normal collector maintenance
- the only rationale is convenience rather than a concrete exception or emergency condition

## Handoff Contract

Manual tools stay out-of-band until an operator curates the result into one of the following handoff modes:

| Handoff mode | When to use it | Repo-visible result |
| --- | --- | --- |
| `url_recollection` | the manual tool discovered or preserved a canonical URL that DataPulse can still recollect | rerun the normal DataPulse collector path on the canonical URL; keep the manual bundle only as supporting provenance |
| `manual_fact_item` | the evidence exists only in the manual export, downloaded media, or login-gated capture | create a curated `DataPulseItem` with `source_type=manual`; this slice defines the contract but does not add a new importer |
| `story_attachment_only` | the raw bundle is too large, sensitive, or operational to turn into an inbox item directly | keep the raw bundle outside git and reference it from analyst notes, triage context, or story export |

Decision rule:

1. prefer `url_recollection` whenever a stable public URL still exists
2. use `manual_fact_item` only when the evidence would otherwise be lost
3. use `story_attachment_only` when the artifact is valuable context but not suitable as a standalone inbox item

## Required Manual Run Artifacts

Every manual acquisition run should preserve a bundle outside the core collector path with at least:

1. a machine-readable run manifest
2. one or more raw export references
3. a short operator curation note that explains what was captured and why

Recommended manifest shape:

```json
{
  "schema_version": "manual_acquisition_capture.v1",
  "lane": "manual_sidecar",
  "tool_class": "easyspider",
  "tool_name": "EasySpider",
  "operator": "analyst@example",
  "executed_at_utc": "2026-03-09T03:57:49Z",
  "trigger_reason": "collector_login_friction",
  "target_urls": [
    "https://mp.weixin.qq.com/s/example"
  ],
  "handoff_mode": "manual_fact_item",
  "session_mode": "operator_browser_state",
  "output_refs": [
    "/secure/manual-captures/2026-03-09/wechat-article.json",
    "/secure/manual-captures/2026-03-09/wechat-article.png"
  ],
  "notes": "Used after native and jina paths were insufficient during an urgent capture window."
}
```

Manifest rules:

- `tool_class`, `operator`, `executed_at_utc`, `trigger_reason`, and `handoff_mode` are required
- `output_refs` may point to local secure paths, object storage IDs, or case-system references, but should not assume the raw bundle lives in git
- if the run consumed login state or cookies, `session_mode` must say so without leaking the secret material itself

## Provenance Contract For Repo-Visible Intake

When a manual run becomes repo-visible truth, it should not reuse `extra["collector_provenance"]`.

Instead, manual intake should use `extra["manual_acquisition_provenance"]` so downstream surfaces can distinguish operator-curated evidence from automated collector output.

Recommended shape:

```json
{
  "lane": "manual_sidecar",
  "tool_class": "f2",
  "tool_name": "f2",
  "operator": "analyst@example",
  "executed_at_utc": "2026-03-09T03:57:49Z",
  "handoff_mode": "manual_fact_item",
  "artifact_ref": "/secure/manual-captures/2026-03-09/video-case-17",
  "canonical_url": "https://www.douyin.com/video/123",
  "platform_hint": "douyin",
  "session_mode": "tool_local_state",
  "trigger_reason": "download_heavy_evidence_capture",
  "review_required": true
}
```

Repo-visible handoff rules:

- use `SourceType.MANUAL` for manual fact items instead of masquerading as `wechat`, `weibo`, `xhs`, or another automated source type
- keep platform hints in tags or `manual_acquisition_provenance.platform_hint`, not as fake collector identity
- set the source-governance posture to the existing manual-fact defaults: `source_class=analyst`, `collection_mode=manual_fact`, `sensitivity=review_required`
- preserve the canonical public URL when one exists, even if the actual capture came from a manual export
- manual acquisition does not auto-upgrade an item to `verified`; triage and story layers still own review-state truth

## Operational Boundaries

The manual acquisition lane is intentionally constrained:

1. it is operator-invoked and manual-only
2. it does not run from scheduled governance workflows
3. it does not become a new default branch in `ParsePipeline`
4. it does not grant legal or compliance clearance; operator review remains mandatory
5. it does not require repo-local storage of large downloaded media or external job-state dumps

For `EasySpider`, `Crawlab`, and `f2`, the repo truth is the handoff contract and provenance vocabulary, not a new always-on executor.

## Local Market Wrapper Boundary

Future tradingview-style tooling belongs in DataPulse only as a local/manual wrapper or sidecar lane.

Examples include quote snapshots, technical-regime screens, deterministic robustness checks, and sentiment-contra helpers. Those tools may inform watchlist seeding, operator triage context, or a manual evidence capture, but they do not become a new public trading surface or an automated business-runtime lane.

Boundary rules:

1. wrapper execution stays local/manual and must not be scheduled from `.github/workflows/governance-loop-auto.yml` or other governance-loop automation
2. repo-visible truth must resolve through existing `url_recollection`, `manual_fact_item`, or `story_attachment_only` handoff modes
3. watchlist or market-context usage must remain additive to existing lifecycle objects rather than inventing a wrapper-owned object chain
4. wrapper output must not publish BUY/SELL conclusions, portfolio logic, execution triggers, or proxy-policy semantics as DataPulse repo truth
5. any wrapper-local artifacts remain supporting context until triage, story, or manual-provenance handoff makes them attributable inside the current lifecycle contract

## Slice Outcome

`L9.10` is complete when these facts remain true:

- `EasySpider`, `Crawlab`, and `f2` are explicitly classified as a manual emergency acquisition lane
- the lane has clear activation rules and handoff modes
- repo-visible manual intake is distinguished from automated collector provenance
- scheduled governance automation remains read-only and does not become a business executor for these tools
