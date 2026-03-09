# DataPulse Content Acquisition And Fact Screening Reinforcement Blueprint

## Purpose

This document distills the external Obsidian note `仓内_内容采集与事实筛选工具_Top10检索汇总_2026-03-09.md` into repository-relevant reinforcement facts.

The goal is not to import a generic "Top 10 tools" list into the repo. The goal is to decide which facts justify new blueprint slices for DataPulse.

## Current Repo Read

The current repository has now converted the original external note into landed repo truth through `L9.1` to `L9.10`:

- `datapulse/core/router.py` now routes across first-class platform collectors, `native_bridge`, `generic`, and `jina`.
- `datapulse/collectors/wechat.py` now prefers a native `wechat_spider` path when configured, then falls back to `jina -> browser`.
- `datapulse/collectors/xhs.py` now has a `MediaCrawler`-class native bridge path ahead of `jina -> browser`.
- `datapulse/collectors/weibo.py` exists as a first-class collector with `source_type=weibo` and `native -> jina` fallback semantics.
- `datapulse/collectors/generic.py` now has a Chinese-news正文 backend path ahead of `trafilatura -> BeautifulSoup -> Firecrawl -> Jina`.
- `datapulse/core/triage.py`, `datapulse/core/story.py`, `datapulse/core/alerts.py`, and `datapulse/reader.py` now project grounded claims plus a factuality gate into triage, story, digest, export, and alert surfaces.
- `datapulse/core/watchlist.py` and `datapulse/reader.py` now carry `trend_inputs` with an explicit `watch_seed_only` boundary.
- `docs/governance/datapulse-manual-acquisition-sidecar-contract.md` now fixes `EasySpider / Crawlab / f2` in a separate manual emergency lane.

That means the largest delta from the same external note is no longer collector coverage. The largest remaining delta is optional backend operationalization behind the newly landed grounding and factuality surfaces.

## High-Value Facts To Promote

### 1. Generic crawler additions are lower-delta than native Chinese source reinforcement

The external note confirms that tools like `Firecrawl`, `Crawl4AI`, `Scrapy`, and `Crawlee` are strong, but DataPulse already has a usable generic web stack. Replacing or expanding that stack is second-order work compared with source-native coverage gaps.

Repo implication:

- do not open blueprint slices for generic-crawler replacement right now
- keep generic extraction work limited to targeted正文 quality uplift where the current stack is weak

### 2. Native Chinese platform collection is the highest-ROI acquisition uplift

The note's highest-value collector facts are not abstract crawling facts. They are platform-specific:

- `MediaCrawler` covers multiple Chinese platforms in one sidecar-capable package
- `wechat_spider` targets native WeChat article collection
- `weiboSpider` fills a direct current gap

Repo implication:

- prioritize a sidecar-style native collector bridge over deeper generic crawler work
- keep existing `jina` and browser fallbacks as safety nets rather than replacing them first

### 3. WeChat and Weibo are concrete repo gaps; XHS is a quality gap

Current repo reality:

- WeChat exists, but it is fallback-heavy
- Weibo does not have a native collector in the router
- XHS exists, but it remains fallback-heavy and would benefit from a native bridge path rather than more parsing heuristics

Repo implication:

- split native Chinese collection into separate slices instead of treating it as one oversized "China collector" task

### 4. Chinese news正文 extraction is a cheap, high-leverage uplift

The note identifies `GeneralNewsExtractor` as a strong fit for Chinese article extraction. This maps cleanly to the current `generic` collector and does not require a full collector architecture reset.

Repo implication:

- add a targeted正文 extraction slice to the existing generic collector chain
- keep it separate from platform-native collector work

### 5. Grounded claim extraction is the missing bridge between collection and evidence products

The note's strongest fact-screening fit for this repo is `LangExtract`, because it maps directly onto the existing `triage -> story` path.

Repo implication:

- add a slice that projects claim/evidence grounding into triage and story surfaces
- require source-linked provenance instead of free-text summary-only outputs

### 6. A factuality gate belongs before digest, story export, and alert escalation

The cleanest fit for `OpenFactVerification`-class tooling is not inside low-level collection. It belongs at the downstream trust boundary before DataPulse turns collected evidence into outward-facing outputs.

Repo implication:

- add a slice that introduces a factuality gate before digest/story export and alert promotion
- keep factuality outputs operator-visible rather than silently mutating scores

### 7. TrendRadar, EasySpider, Crawlab, and f2 are secondary lanes

These tools are still useful, but they should not displace the first reinforcement lane:

- `TrendRadar` fits watch seeding and trend/feed intake
- `EasySpider` and `Crawlab` fit manual or operator-driven acquisition workflows
- `f2` fits download-heavy or short-video sidecar workflows

Repo implication:

- represent these as later slices or explicit secondary lanes
- do not let them preempt native collector and fact-screening slices

### 8. LangExtract and OpenFactVerification remain repo-relevant only as optional backend adapters now

Current repo reality after `L9`:

- grounded claim projection exists, but `build_item_grounding(...)` currently resolves to `provided`, `heuristic`, or `empty` rather than calling an optional external grounding backend
- the factuality gate exists, but `build_factuality_gate(...)` is still a deterministic scoring boundary rather than a pluggable external verifier

Repo implication:

- no new collector-lane slice is justified from the original note
- a new repo-relevant phase is justified only for optional backend contracts and adapters behind the now-stable grounding and factuality surfaces

## What Should Not Be Promoted As First-Class Slices Now

The external note does not justify immediate blueprint slices for:

- a generic replacement of `generic.py`
- a repository-wide switch from current collectors to `Scrapy` or `Crawl4AI`
- direct adoption of UI-heavy manual tools as core collector dependencies

Those remain reference facts, not immediate blueprint truth.

## Integration Rules For This Phase

All follow-up slices in this phase should obey the same constraints:

1. Prefer sidecar or bridge integration over deep vendoring of third-party repositories.
2. Preserve current `jina` and browser fallbacks until a native path is proven.
3. Emit provenance that makes native collector use, grounded claim extraction, and factuality decisions visible to operators.
4. Keep platform-native collection,正文 extraction, grounded claims, and factuality gating as separate slices so the loop can stop on narrow, machine-decidable work.

## Historical L9 Slice Map

All `L9` slices are now completed in repo truth.

| Slice | Outcome | Why it exists |
| --- | --- | --- |
| `L9.1` | Land this repo-scoped reinforcement blueprint | Converts the external note into repo truth without importing a giant prose blob as one open slice |
| `L9.2` | Define the native Chinese collector bridge contract and shortlist | Creates the contract that later collector slices can implement without architecture drift |
| `L9.3` | Implement a `MediaCrawler`-class sidecar bridge | Highest-reach native-source acquisition uplift across Chinese platforms |
| `L9.4` | Add a first native WeChat collector path | Directly addresses a current fallback-heavy collector |
| `L9.5` | Add a first native Weibo collector path | Fills a current router gap |
| `L9.6` | Add a Chinese news正文 extraction backend | Cheap quality lift for Chinese article pages within the generic chain |
| `L9.7` | Add grounded claim/evidence extraction to triage and story | Turns collected text into source-linked claims instead of summary-only evidence |
| `L9.8` | Add a factuality gate before outward-facing outputs | Raises trust at the delivery boundary |
| `L9.9` | Add trend-feed inputs for watch seeding | Uses TrendRadar-class inputs without confusing trend feeds with URL collectors |
| `L9.10` | Define a manual emergency acquisition lane for operator tools | Captures `EasySpider/Crawlab/f2` value without coupling them into the core collector path |

## Post-L9 Closeout Conclusion

The original external note does not currently justify another open collector, trend, or manual-lane slice.

What it does justify now is narrower follow-up work:

- formalize an optional grounding/factuality backend contract
- plug a `LangExtract`-class backend into the current grounding surface without regressing `provided/heuristic` fallback
- plug an `OpenFactVerification`-class backend into the current factuality gate without hiding the current deterministic operator-visible signals

## L10 Slice Map

| Slice | Outcome | Why it exists |
| --- | --- | --- |
| `L10.1` | Define optional evidence-backend contracts and provenance rules | The repo now has stable grounding/factuality surfaces but no contract for backend-assisted enrichment |
| `L10.2` | Add a `LangExtract`-class grounding adapter | Upgrades grounded claims from heuristic-only fallback to optional backend-assisted extraction |
| `L10.3` | Add an `OpenFactVerification`-class factuality adapter | Upgrades the delivery trust boundary from deterministic-only scoring to optional backend-assisted verification |

## Recommended Ignition Order After This Refresh

Recommended order after this refresh:

1. `L10.1`
2. `L10.2`
3. `L10.3`

This order keeps DataPulse from reopening already-settled collector lanes and instead focuses the next loop on backend-ready evidence enrichment where the repo still has a real delta.
