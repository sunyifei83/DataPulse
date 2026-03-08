# DataPulse Content Acquisition And Fact Screening Reinforcement Blueprint

## Purpose

This document distills the external Obsidian note `仓内_内容采集与事实筛选工具_Top10检索汇总_2026-03-09.md` into repository-relevant reinforcement facts.

The goal is not to import a generic "Top 10 tools" list into the repo. The goal is to decide which facts justify new blueprint slices for DataPulse.

## Current Repo Read

The current repository already has broad collector coverage and a functioning evidence pipeline:

- `datapulse/core/router.py` already routes across platform collectors plus `generic` and `jina`.
- `datapulse/collectors/wechat.py` is still `jina` first with optional browser fallback.
- `datapulse/collectors/xhs.py` is still `jina` first with optional session-backed browser fallback.
- `datapulse/collectors/generic.py` already stacks `trafilatura`, `BeautifulSoup`, optional `Firecrawl`, and `Jina` fallback.
- `datapulse/core/triage.py` and `datapulse/core/story.py` already carry governance and evidence structures, but they do not yet add explicit claim grounding or a factuality gate.

That means the largest delta is no longer "add another generic crawler." The largest delta is "close native-source gaps and improve evidence trust before delivery."

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

## L9 Slice Map

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

## Manual Ignition Order

Recommended order after this promotion:

1. `L9.2`
2. `L9.3`
3. `L9.4`
4. `L9.5`
5. `L9.6`
6. `L9.7`
7. `L9.8`
8. `L9.9`
9. `L9.10`

This order keeps DataPulse focused on the highest-reach collection gap first, then closes the evidence-trust gap before expanding auxiliary acquisition lanes.
