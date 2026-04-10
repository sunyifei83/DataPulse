<a id="top"></a>

# DataPulse (Chinese name: 数据脉搏) Intelligence Hub (English)

[🔙 Back to Main README](./README.md) | [🇨🇳 中文版本](./README_CN.md) | [⬆️ Back to top](#top)

<p align="center">
  <img src="./docs/assets/datapulse-command-chamber-hero.jpg" alt="DataPulse command chamber key visual" width="960">
</p>

<p align="center">
  <strong>DataPulse Command Chamber</strong><br>
  The repository now uses a steel-blue command room, red containment rings, and a central evidence globe as its core brand language.
</p>

Brand baseline: [`docs/brand_identity.md`](./docs/brand_identity.md)

## Core goal

DataPulse provides one shared intake path for URL extraction, confidence scoring, and memory output
for MCP, Skill, Agent, and bot workflows.

## Higher-level view and blueprint landing

| Dimension | Current reading |
| --- | --- |
| Repository posture | DataPulse is no longer just a multi-platform parser set. It is now a local-first public-source intelligence operating surface with the chain `collection -> mission -> triage -> story -> report -> delivery -> governance`. |
| Landed closed loops | Public-source intake, search, watch/triage/story, alert/routes, ops scorecard, browser console, and source/lifecycle/delivery governance are all repo-landed and runnable. |
| In-flight convergence | Report objects, normalized delivery subscriptions, report package/dispatch flows, and governed AI surfaces are now in Reader / CLI / MCP runtime, but still intentionally constrained by governance contracts instead of being marketed as a fully autonomous research agent. |
| Current blueprint state | The structured blueprint is now completed through `L30.3`, with the `L29` wave completed through `L29.6`; `recommended_next_slice=no-open-slice` remains in effect until a new blueprint wave or admissible reopen evidence appears. |
| Explicit boundary | This repo is not a paid-database procurement layer, field-interview system, ERP/CRM intelligence platform, or automated legal-compliance oracle. |
| Current proof surface | The canonical roots are `artifacts/governance/snapshots/`, `artifacts/governance/release_bundle/`, and `config/modelbus/datapulse/`; legacy `out/ha_latest_release_bundle/` remains compatibility-only, while `project_specific_loop_state.draft.json`, `code_landing_status.draft.json`, `release_status.json`, and `datapulse-ai-surface-admission.example.json` hold loop/runtime, code-landing, release, and AI-surface admission truth respectively. |

## Implemented features

- Parser routing: `twitter/x`, `reddit`, `youtube`, `bilibili`, `telegram`, `wechat`, `xiaohongshu`, `rss`, `arxiv`, `hackernews`, `trending`, `generic web`, `jina`
- Platform strategies:
  - Twitter: FxTwitter primary + Nitter fallback
  - Reddit: public `.json` API
  - YouTube: transcript first, optional Whisper fallback (`GROQ_API_KEY`)
  - Bilibili: official API + interaction stats (views/likes/coins/favorites/danmaku/shares)
  - Telegram: Telethon (`TG_API_ID`/`TG_API_HASH`), configurable via `DATAPULSE_TG_*` env vars
  - WeChat / Xiaohongshu: Jina fallback with retry, optional Playwright session fallback, XHS auto-extracts engagement metrics (likes/comments/favorites/shares), session TTL cache
  - RSS: multi-entry feed parsing (up to 5 entries), auto feed type detection
  - arXiv: Atom API for structured paper metadata (title/authors/abstract/categories/PDF link)
  - Hacker News: Firebase API with dynamic engagement flags
  - Trending: trends24.in scraper for X/Twitter trending topics across 400+ global locations, 30+ location aliases (us/uk/jp etc.), hourly snapshots, tweet volume parsing
  - Generic web: Trafilatura / BeautifulSoup, optional Firecrawl fallback (`FIRECRAWL_API_KEY`) or Jina Reader
  - Jina enhanced reading: CSS selector targeting, wait-for-element, cookie passthrough, proxy, AI image descriptions, cache control
  - Web search: multi-source search with default auto provider (Jina/Tavily), supports `--platform`, `--search-provider`, `--search-mode`, deep/news/time-range filters, and score-based output
  - Outputs:
  - structured JSON (`DataPulseItem`)
  - optional Markdown inbox output (`datapulse-inbox.md` / custom path)
- Multi-dimensional scoring: 4 dimensions weighted (confidence 0.25 / authority 0.30 / corroboration 0.25 / recency 0.20), outputs 0-100 composite score + 0.01~0.99 confidence score
- Digest builder: auto-generates digest envelopes with primary/secondary stories, fingerprint dedup, diverse source selection
- Task layer (initial Watch Mission support):
  - save recurring search missions, list them, run them manually, disable them
  - replace or clear one mission's alert rules with `--watch-alert-set / --watch-alert-clear`
  - shared mission/run object model across CLI, Reader, and MCP
- Triage queue (initial support):
  - review states: `new / triaged / verified / duplicate / ignored / escalated`
  - review notes, review actions, and `duplicate_of` linking
  - shared triage semantics across CLI, Reader, MCP, and the browser console
  - duplicate explain workflow with candidate ranking, signals, and suggested primary item
- Story workspace (initial support):
  - story clustering, primary/secondary evidence, timelines, contradiction hints, and entity rollups
  - `--story-build / --story-list / --story-show / --story-update / --story-graph / --story-export`
  - shared story semantics across Reader, MCP, and the browser console
- Structured report and role-aware delivery:
  - `datapulse/core/report.py` now persists `ReportBrief / ClaimCard / ReportSection / CitationBundle / Report / ExportProfile / DeliverySubscription / DeliveryDispatchRecord`
  - CLI / Reader / MCP now expose `--report-*`, `--delivery-*`, and corresponding tool surfaces for report assembly, delivery package generation, dispatch, and audit
- Alerts and scheduling (initial support):
  - threshold alert rules, due-runner polling, daemon single-instance lock
  - keyword / tag / domain / source-type / freshness filters for alert matching
  - JSON / Markdown / Webhook / Feishu / Telegram alert sinks for auto-distribution
  - named route config with `--alert-route-list / --alert-route-health`
  - `--watch-alert-set / --watch-alert-clear` to replace or clear one mission's alert rules in place
  - `--watch-show / --watch-results` for one mission's recent runs, persisted result stream, recent alert outcomes, and latest failure retry guidance
  - `watch_status` for daemon heartbeat, metrics, and last error
  - JSON + HTML static status outputs
- Browser console (G0/G3):
  - local `datapulse-console` browser shell
  - unified watch / mission cockpit / triage / story / alert / route / route health / status operating surface
  - `Mission Cockpit` now includes a persisted result stream for each mission
  - `Mission Cockpit` now includes result filter chips and a timeline strip for one mission's recent events
  - `Mission Cockpit` now includes a first-cut alert rule editor for replacing or clearing the console threshold rule
  - `Triage Queue` now includes a first-cut keyboard workflow: `J/K` move selection, `V/T/E/I` apply state changes, `D` loads duplicate explain, and `N` focuses the note composer
  - the status board now includes collector tier breakdown, a watch health board, and aggregate success-rate signals
  - includes a Story Workspace board with evidence stacks, timeline, contradiction markers, entity graph, Markdown pack preview, and a basic story editor for `title / summary / status`
- Reliability:
  - centralized parse error handling with narrowed exceptions
  - `retry_with_backoff` decorator + `CircuitBreaker` for fault tolerance
  - 429-aware backoff: `RateLimitError` respects Retry-After header, `CircuitBreaker` applies weighted rate-limit detection
  - in-memory TTL cache (thread-safe, zero external deps)
  - concurrent batch reads with auto URL dedup
  - dedupe and prune by max items / retention days
  - ingestion fingerprint dedup: similar content (≥50 chars) auto-deduplicated at inbox level
- Light entity layer (EdgeQuake distillation):
  - `--entities` enables URL-level entity extraction (`fast` / `llm`)
  - `--entity-query` / `--entity-graph` / `--entity-stats` for entity store query and inspection
  - entity corroboration can be tuned by `DATAPULSE_ENTITY_CORROBORATION_WEIGHT` (default `0`)
- Self-diagnostics:
  - `datapulse --doctor`: tiered health check (tier 0/1/2) for all collectors with status icons and setup hints
  - Three-tier collector classification: tier 0 (zero-config), tier 1 (network/free), tier 2 (needs setup)
  - Actionable error messages in route failures with setup hints
  - `datapulse --troubleshoot`: output actionable fix suggestions (optional `--troubleshoot <collector>`)
  - `datapulse --check-update`: check latest GitHub release
  - `datapulse --version`: show current version
  - `datapulse --self-update`: run an update attempt when a newer release exists
- Observability:
  - structured logging (`DATAPULSE_LOG_LEVEL` env var)
- Intelligence governance and ops loop:
  - `SourceGovernance` now gives the source directory a stable `source_class / collection_mode / authority / sensitivity / compliance_hints` tuple
  - `MissionIntent` now gives watch missions explicit `demand_intent / key_questions / freshness / coverage_targets`
  - the repo now includes a [source governance contract](./docs/intelligence_source_governance_contract.md), [lifecycle contract](./docs/intelligence_lifecycle_contract.md), [delivery contract](./docs/intelligence_delivery_contract.md), and [commercial intelligence governance blueprint](./docs/commercial_intelligence_governance_blueprint.md)
  - `ops_snapshot()`, `datapulse --ops-overview`, and the browser console now expose an intelligence governance scorecard for coverage, freshness, alert yield, triage throughput, and story conversion
- Governed AI surfaces:
  - Reader / CLI / MCP / console now project `mission_suggest`, `triage_assist`, `claim_draft`, `report_draft`, and `delivery_summary`
  - current admission truth is intentionally asymmetric: `mission_suggest`, `triage_assist`, `claim_draft`, and `delivery_summary` are admitted, while `report_draft` remains runtime-visible but fail-closed until its structured contract is admitted
- Verification and proof surface:
  - GitHub Actions CI (Python 3.10/3.11/3.12 matrix) and the repo quick gate form the default promotion gate
  - canonical truth now lives under `artifacts/governance/snapshots/`, `artifacts/governance/release_bundle/`, and `config/modelbus/datapulse/`; `out/ha_latest_release_bundle/` remains compatibility-only

## Install

```bash
pip install -e .
pip install -e ".[all]"   # enable all optional capabilities
```

Optional groups:

- `.[console]`, `.[trafilatura]`, `.[youtube]`, `.[telegram]`, `.[browser]`, `.[mcp]`, `.[notebooklm]`  
  Note: `.[mcp]` enables native MCP transport; when missing, `uv run python -m datapulse.mcp_server` falls back to an internal stdio-compatible runtime.

## Development

```bash
pip install -e ".[dev]"
pip install pre-commit && pre-commit install
```

## License

DataPulse uses **DataPulse Non-Commercial License v1.0**.
It is free for non-commercial use only (education, research, personal learning, internal PoC).
Commercial usage requires a separate license from the author.

Please refer to the root `LICENSE` file for the full terms.

## Workflows

### 0) Minimum runnable setup

Only required:

- Python 3.10+ available
- Datapulse install command can run

Run first:

```bash
pip install -e .
datapulse --config-check
datapulse --doctor
```

Note: local `python3` may still resolve to `3.9`. Repo wrappers now prefer `uv run python` or an explicit `python3.10+` interpreter, and direct imports fail fast with a clear version error instead of an opaque runtime exception.

What to do next:

- If `--config-check` marks search keys missing, set only what you need:
  - `export JINA_API_KEY=<your_jina_api_key>` (improves extraction and search)
  - `export TAVILY_API_KEY=<your_tavily_api_key>` (improves search coverage/fallback)
- If `--doctor` marks tier-2 collectors as not ready, follow the printed `Suggested commands`.

### 0.1) Command cheatsheet by scenario

A. Parse one URL:
  - `datapulse https://x.com/xxxx/status/123`
B. Parse a batch:
  - `datapulse --batch https://x.com/... https://www.reddit.com/...`
  - Short form: `datapulse -b https://x.com/... https://www.reddit.com/...`
C. Search web:
  - `datapulse --search "LLM inference optimization"`
  - Short form: `datapulse -s "LLM inference optimization"`
D. Trending:
  - `datapulse --trending us --trending-limit 10`
  - Short form: `datapulse -T us --trending-limit 10`
E. Entity flow:
  - `datapulse https://x.com/xxxx/status/123 --entities --entity-mode fast`
F. Watch mission:
  - `datapulse --watch-create --watch-name "AI Radar" --watch-query "OpenAI agents"`
  - `datapulse --watch-alert-set ai-radar --watch-alert-route ops-webhook --watch-alert-keyword launch`
  - `datapulse --watch-alert-clear ai-radar`
  - `datapulse --watch-show ai-radar`
  - `datapulse --watch-results ai-radar`
  - `datapulse --watch-run ai-radar`
G. Watch scheduler:
  - `datapulse --watch-run-due`
H. Alerts:
  - `datapulse --alert-list`
  - `datapulse --alert-route-list`
  - `datapulse --alert-route-health`
I. Daemon:
  - `datapulse --watch-daemon --watch-daemon-once`
  - `datapulse --ops-overview`
J. Triage queue:
  - `datapulse --triage-list`
  - `datapulse --triage-explain <item_id>`
  - `datapulse --triage-update <item_id> --triage-state verified`
K. Story workspace:
  - `datapulse --story-build`
  - `datapulse --story-list`
  - `datapulse --story-show <story_id>`
  - `datapulse --story-update <story_id>`
  - `datapulse --story-graph <story_id>`
L. Browser console:
  - `datapulse-console --port 8765` (includes the Story Workspace board and basic story editor)
M. Diagnostics:
  - `datapulse --config-check`
  - `datapulse --doctor`
  - `datapulse --troubleshoot`
  - `datapulse --troubleshoot telegram`
  - `datapulse --skill-contract`
  - `datapulse --check-update`
  - `datapulse --self-update`
  - Short form: `datapulse -k` and `datapulse -d`

Short flags introduced in CLI:
- `-b/--batch`, `-s/--search`, `-S/--site`, `-l/--list`, `-T/--trending`, `-i/--login`, `-d/--doctor`, `-k/--config-check`; diagnostic extras: `--troubleshoot`, `--skill-contract`, `--check-update`, `--self-update`, `--version`

### 1) CLI usage

```bash
# read one URL
datapulse https://x.com/xxxx/status/123

# batch read
datapulse --batch https://x.com/... https://www.reddit.com/... --min-confidence 0.45

# list memory
datapulse --list --limit 10 --min-confidence 0.30

# login state capture
datapulse --login xhs
datapulse --login wechat

# clear memory
datapulse --clear

# web search
datapulse --search "LLM inference optimization"
datapulse --search "Python 3.13" --site python.org --site peps.python.org

# platform-scoped search
datapulse --search "skincare" --platform xhs --search-limit 3

# trending topics
datapulse --trending              # worldwide
datapulse --trending us           # United States
datapulse --trending jp --trending-limit 10  # Japan top 10
datapulse --trending uk --trending-store     # UK, save to inbox

# Watch Mission
datapulse --watch-create --watch-name "AI Radar" --watch-query "OpenAI agents" --watch-platform twitter
datapulse --watch-list
datapulse --watch-show ai-radar
datapulse --watch-results ai-radar
datapulse --watch-run ai-radar
datapulse --watch-disable ai-radar

# Run due watch missions from schedule
datapulse --watch-create --watch-name "Infra Radar" --watch-query "LLM inference infra" --watch-schedule @hourly
datapulse --watch-run-due

# Configure one threshold alert rule and inspect alert events
datapulse --watch-create --watch-name "Launch Radar" --watch-query "OpenAI launch" --watch-alert-min-score 70 --watch-alert-channel markdown
datapulse --alert-list

# Richer alert rule + named route
datapulse --watch-create --watch-name "Launch Ops" --watch-query "OpenAI launch" --watch-alert-route ops-webhook --watch-alert-keyword launch --watch-alert-domain openai.com
datapulse --watch-alert-set launch-ops --watch-alert-route ops-webhook --watch-alert-keyword launch --watch-alert-domain openai.com --watch-alert-min-score 70
datapulse --watch-alert-clear launch-ops
datapulse --alert-route-list
datapulse --alert-route-health

# Run daemon for one polling cycle
datapulse --watch-daemon --watch-daemon-once

# Show daemon heartbeat and metrics
datapulse --watch-status
datapulse --ops-overview

# Triage queue
datapulse --triage-list
datapulse --triage-explain item-123
datapulse --triage-update item-123 --triage-state verified --triage-note-text "confirmed by analyst"
datapulse --triage-note item-123 --triage-note-text "needs follow-up"
datapulse --triage-stats

# Story workspace
datapulse --story-build
datapulse --story-list
datapulse --story-show story-openai-launch
datapulse --story-update story-openai-launch --story-title "OpenAI Launch Watch" --story-status monitoring
datapulse --story-graph story-openai-launch
datapulse --story-export story-openai-launch --story-format markdown

# Launch the local browser console from the repo (recommended)
bash scripts/datapulse_console.sh --port 8765

# Or use the module entrypoint
uv run python -m datapulse.console_server --port 8765

# If installed into PATH
datapulse-console --port 8765

# Console entry smoke
bash scripts/datapulse_console_smoke.sh

![DataPulse Console Preview](docs/datapulse_console.png)

Field guide: [docs/datapulse_console_parameter_guide.md](docs/datapulse_console_parameter_guide.md)

# collector health check
datapulse --doctor
datapulse --troubleshoot
datapulse --troubleshoot telegram

# version and updates
datapulse --version
datapulse --check-update
datapulse --self-update

# targeted extraction
datapulse https://example.com --target-selector ".article-body" --no-cache

# entity-aware usage
datapulse https://x.com/xxxx/status/123 --entities --entity-mode fast
datapulse --entity-query OPENAI --entity-type CONCEPT
datapulse --entity-graph OPENAI
datapulse --entity-stats
```

### 2) Smoke checks

```bash
# list required env keys only
datapulse-smoke --list

# run selected platforms
datapulse-smoke --platforms xhs wechat --require-all

# run configured scenarios
datapulse-smoke --min-confidence 0.45
```

Smoke env vars:

- `DATAPULSE_SMOKE_TWITTER_URL`
- `DATAPULSE_SMOKE_REDDIT_URL`
- `DATAPULSE_SMOKE_YOUTUBE_URL`
- `DATAPULSE_SMOKE_BILIBILI_URL`
- `DATAPULSE_SMOKE_TELEGRAM_URL`
- `DATAPULSE_SMOKE_RSS_URL`
- `DATAPULSE_SMOKE_WECHAT_URL`
- `DATAPULSE_SMOKE_XHS_URL`

## MCP / Skill / Agent usage

- MCP server (`.[mcp]` optional, fallback to built-in stdio when missing):

```bash
uv run python -m datapulse.mcp_server
uv run python -m datapulse.mcp_server --list-tools
uv run python -m datapulse.mcp_server --call health
```

MCP coverage spans intake, source management, missions, triage, story, report, delivery, governed AI, and diagnostics:

**Intake & reading:**
- `read_url(url, min_confidence)` — parse a single URL
- `read_batch(urls, min_confidence)` — batch parse URLs
- `read_url_advanced(url, target_selector, wait_for_selector, no_cache, with_alt, min_confidence)` — CSS-targeted extraction
- `search_web(query, sites, platform, limit, fetch_content, min_confidence, provider='auto', mode='single', deep=False, news=False, time_range=None, freshness=None, extract_entities=False, entity_mode='fast', store_entities=True, entity_api_key=None, entity_model='gpt-4o-mini', entity_api_base='https://api.openai.com/v1')` — web search
- `trending(location, top_n, store)` — X/Twitter trending topics

**Memory & state:**
- `query_inbox(limit, min_confidence)` — query inbox
- `mark_processed(item_id, processed)` — mark as processed
- `query_unprocessed(limit, min_confidence)` — query unprocessed items

**Triage queue:**
- `triage_list(limit=20, min_confidence=0.0, states=None, include_closed=False)` — list triage queue items
- `triage_explain(item_id, limit=5)` — explain likely duplicate candidates and suggested primary item
- `triage_update(item_id, state, note='', actor='mcp', duplicate_of='')` — update one triage state
- `triage_note(item_id, note, author='mcp')` — append one review note
- `triage_stats(min_confidence=0.0)` — show queue counts by state

**Story workspace:**
- `story_build(profile='default', source_ids=None, max_stories=10, evidence_limit=6, min_confidence=0.0, since=None)` — build and persist a clustered story snapshot
- `story_list(limit=20, min_items=1)` — list persisted stories
- `story_show(identifier)` — inspect one story
- `story_graph(identifier, entity_limit=12, relation_limit=24)` — inspect the entity graph for one story
- `story_export(identifier, output_format='json')` — export one story as `json` or `markdown`

**Watch Mission:**
- `create_watch(name, query, platforms=None, sites=None, schedule='manual', min_confidence=0.0, top_n=5)` — create a saved recurring mission
- `list_watches(include_disabled=False)` — list missions
- `watch_show(identifier)` — inspect one mission with recent runs and recent alerts
- `watch_set_alert_rules(identifier, alert_rules=None)` — replace one mission's alert rules; pass `[]` to clear them
- `watch_results(identifier, limit=10, min_confidence=0.0)` — inspect the persisted result stream for one mission
- `run_watch(identifier)` — run one mission by id or name
- `disable_watch(identifier)` — disable one mission
- `run_due_watches(limit=0)` — run all currently due missions
- `list_alerts(limit=20, mission_id='')` — list stored alert events
- `list_alert_routes()` — list configured named alert routes
- `alert_route_health(limit=100)` — inspect delivery health for named alert routes
- `watch_status()` — inspect daemon heartbeat, metrics, and last error

**Source management:**
- `list_sources(include_inactive, public_only)` — list source catalog
- `list_packs(public_only)` — list source packs
- `resolve_source(url)` — resolve URL to source
- `list_subscriptions(profile)` — list subscriptions
- `source_subscribe(profile, source_id)` — subscribe to source
- `source_unsubscribe(profile, source_id)` — unsubscribe
- `install_pack(profile, slug)` — install source pack

**Feed & digest:**
- `query_feed(profile, source_ids, limit, min_confidence, since)` — query feed
- `build_json_feed(profile, source_ids, limit, min_confidence, since)` — JSON Feed
- `build_rss_feed(profile, source_ids, limit, min_confidence, since)` — RSS Feed
- `build_atom_feed(profile, source_ids, limit, min_confidence, since)` — Atom 1.0 Feed
- `build_digest(profile, source_ids, top_n, secondary_n, min_confidence, since)` — curated digest
- `emit_digest_package(profile='default', source_ids=None, top_n=3, secondary_n=7, min_confidence=0.0, since=None, output_format='json')` — export office-ready digest package (`json`/`markdown`)

**Report and delivery:**
- `list_report_briefs / create_report_brief / show_report_brief / update_report_brief` — report brief management
- `list_reports / create_report / show_report / update_report / compose_report / assess_report_quality / export_report` — report assembly, quality gates, and export
- `list_delivery_subscriptions / create_delivery_subscription / update_delivery_subscription / delete_delivery_subscription` — normalized delivery subscriptions
- `build_report_delivery_package / dispatch_report_delivery / list_delivery_dispatch_records` — package generation, dispatch, and attributable delivery audit

**Governed AI surfaces:**
- `ai_surface_precheck` — inspect current admission / mode / contract truth for one AI surface
- `ai_mission_suggest / ai_triage_assist / ai_claim_draft / ai_report_draft / ai_delivery_summary` — governed projections for watch, triage, story, report, and delivery work
- `report_draft` remains intentionally fail-closed at governance level even though the runtime surface already exists

**Diagnostics & utilities:**
- `doctor()` — tiered collector health check
- `detect_platform(url)` — platform detection
- `health()` — health check
- `extract_entities(url, mode='fast', store_entities=True, ...)` — extract entities from a single URL (fast or llm mode)
- `query_entities(entity_type='', name='', min_sources=1, limit=50)` — query entities by type/name
- `entity_graph(entity_name, limit=50)` — entity relation graph output
- `entity_stats()` — entity store statistics

- Skill entry:

```python
from datapulse_skill import run
run("Please process: https://x.com/... and https://www.reddit.com/...")
```

- Agent usage:

```python
from datapulse.agent import DataPulseAgent

agent = DataPulseAgent(min_confidence=0.25)
result = await agent.handle("https://x.com/... and https://www.reddit.com/...")
```

## Configuration

- `INBOX_FILE`
- `DATAPULSE_MEMORY_DIR`
- `DATAPULSE_KEEP_DAYS` (default 30)
- `DATAPULSE_MAX_INBOX` (default 500)
- `OUTPUT_DIR`
- `DATAPULSE_MARKDOWN_PATH`
- `DATAPULSE_MARKDOWN_PROJECTION` (`auto`/`disabled`/`obsidian`/`storage`/`hybrid`)
- `OBSIDIAN_VAULT`
- `DATAPULSE_SESSION_DIR` (default `~/.datapulse/sessions`)
- `DATAPULSE_WATCHLIST_PATH` (watch mission storage file)
- `DATAPULSE_ALERTS_PATH` (alert JSON store)
- `DATAPULSE_ALERTS_MARKDOWN_PATH` (alert Markdown sink)
- `DATAPULSE_ALERT_ROUTING_PATH` (named alert route config file)
- `DATAPULSE_ALERT_WEBHOOK_URL` (default webhook alert sink)
- `DATAPULSE_FEISHU_WEBHOOK_URL` (default Feishu webhook)
- `DATAPULSE_TELEGRAM_BOT_TOKEN` (Telegram alert bot token)
- `DATAPULSE_TELEGRAM_CHAT_ID` (Telegram alert chat id)
- `DATAPULSE_WATCH_DAEMON_LOCK` (daemon lock file)
- `DATAPULSE_WATCH_STATUS_PATH` (daemon JSON status file)
- `DATAPULSE_WATCH_STATUS_HTML` (daemon HTML status page)
- `DATAPULSE_STORIES_PATH` (story workspace storage file)
- `DATAPULSE_REPORTS_PATH` (report and delivery storage file)
- `TG_API_ID` / `TG_API_HASH`
- `NITTER_INSTANCES`
- `FXTWITTER_API_URL`
- `FIRECRAWL_API_KEY`
- `GROQ_API_KEY`
- `DATAPULSE_LOG_LEVEL` (default WARNING)
- `DATAPULSE_TG_MAX_MESSAGES` (default 20)
- `DATAPULSE_TG_MAX_CHARS` (default 800)
- `DATAPULSE_TG_CUTOFF_HOURS` (default 24)
- `DATAPULSE_SMOKE_*`
- `DATAPULSE_MIN_CONFIDENCE`
- `DATAPULSE_SESSION_TTL_HOURS` (default 12 — session cache TTL in hours)
- `DATAPULSE_ENTITY_STORE` (entity store file, default `entity_store.json`)
- `DATAPULSE_ENTITY_CORROBORATION_WEIGHT` (entity corroboration weight, default `0`)
- `JINA_API_KEY` (Jina API Key for enhanced reading and web search)
- `TAVILY_API_KEY` (Tavily API Key for web search)

Markdown projection notes:

- Structured inbox JSON remains the system of record.
- Markdown/Obsidian output is a projection layer and runs fail-open.
- `auto` keeps the legacy priority: `DATAPULSE_MARKDOWN_PATH` -> `OBSIDIAN_VAULT` -> `OUTPUT_DIR`.
- `hybrid` mirrors records to both Obsidian and storage targets when configured.

## Functional validation guide

1. Run one-off CLI checks, then multi-URL batch checks, then list/clear lifecycle.
2. Run platform smoke tests before promotion (`datapulse-smoke --platforms ...`).
3. For MCP/Skill/Agent orchestration, pass through `DataPulseItem.to_dict()` to keep schema stable.
4. Keep sensitive secrets and model endpoints out of repository history and inject them through your secret management path.

## Development and CI gate

- Blueprint work should land as repository commits, not remain as long-lived local workspace drift.
- After push, GitHub Actions is the default gate: `ruff check datapulse/`, `mypy datapulse/`, and `pytest tests/`.
- The G0 browser console adds a lightweight smoke check through `datapulse-console --help` so packaging and console dependencies are validated in CI.
- Current code-landing, release-readiness, and AI-admission truth should be read from `artifacts/governance/snapshots/`, `artifacts/governance/release_bundle/`, and `config/modelbus/datapulse/`; `out/ha_latest_release_bundle/` remains a compatibility fallback only.

## Safety

- URL checks block local/private/localhost targets by default.
- `read_batch` skips failed single URLs by default; enforce strict mode in caller when needed.

## Notes

- Repository docs do not include local test environment or model endpoint plaintext.
- Keep sensitive runtime configuration outside the repository and load it in private runtime context.

## OpenClaw integration assets

- Tool contract: `docs/contracts/openclaw_datapulse_tool_contract.json`
- Quick validation scripts: `scripts/datapulse_local_smoke.sh`, `scripts/run_openclaw_remote_smoke_local.sh`
- Release checklist: `docs/release_checklist.md`
- Governance contracts: `docs/intelligence_source_governance_contract.md`, `docs/intelligence_lifecycle_contract.md`, `docs/intelligence_delivery_contract.md`
- Commercial intelligence blueprint: `docs/commercial_intelligence_governance_blueprint.md`

### OpenClaw credential management best practice (debug vs app environment)

- Debug environment (local verification):
  - Keep real `VPS_*`, `MACMINI_*`, `TG_API_*`, `JINA_API_KEY` values in `.env.openclaw.local` only.
  - `.env.openclaw.local` must stay out of version control.
  - `scripts/run_openclaw_remote_smoke_local.sh` bootstraps from `.env.openclaw.example` and writes your actual local run context back locally.
- App environment (CI/CD/shared runtime):
  - Do not persist secrets in repository files.
  - Inject credentials through deployment secret channels (GitHub Secrets, OS env store, vault, mounted secret files).
  - Runtime variables should be provided at process start and take precedence over local test defaults.
- Shared guardrail:
  - `.env.openclaw.example` is a redacted template only.
  - Run `bash scripts/security_guardrails.sh` before release to enforce non-leak checks.

#### Deployment credential matrix (debug vs app)

| Target | Secret source | Storage location | Repo policy | Runtime precedence |
| --- | --- | --- | --- | --- |
| Local debug/repro | Manual environment values | `.env.openclaw.local` (local only) | Git-ignored, not committed | Higher than `.env.openclaw.example` |
| Shared test/CI/CD | Secret manager or OS env | Runtime env injection | Must not be committed | Higher than local debug file |
| Template publishing | Redacted template | `.env.openclaw.example` | Can be committed with placeholders | Lower than runtime |

Keep this aligned with `docs/search_gateway_config.md` and `docs/test_facts.md`.

```bash
chmod +x scripts/datapulse_local_smoke.sh scripts/run_openclaw_remote_smoke_local.sh
# First run auto-persists from existing local/session config.
# For manual override: cp .env.openclaw.example .env.openclaw.local then edit.
export URL_1="https://x.com/xxxx/status/123"
export URL_BATCH="https://x.com/... https://www.reddit.com/..."
bash scripts/datapulse_local_smoke.sh
# remote execution requires VPS/M4 tunnel
bash scripts/run_openclaw_remote_smoke_local.sh
```

## Release & publishing

- Confirm a release Python runtime at `>=3.10` before publishing:
  - explicit override: `export DATAPULSE_RELEASE_PYTHON=python3.10`
  - or verify directly: `uv run --python 3.10 python -V`
- Build artifacts:
  - `bash scripts/release_readiness.sh`
  - `uv run --python 3.10 python -m build --sdist --wheel .`
  - attach `dist/*.whl` and `dist/*.tar.gz`
- Publishing:
  - `./scripts/release_publish.sh --tag vX.Y.Z --dry-run`
  - `./scripts/release_publish.sh --tag vX.Y.Z`
  - `scripts/release_publish.sh` auto-resolves `DATAPULSE_RELEASE_PYTHON`, or falls back to a `uv` build path so the runtime does not need to ship with `pip`
  - `scripts/release_publish.sh` auto-extracts the matching `## Release: DataPulse vX.Y.Z` section from `RELEASE_NOTES.md`, reuses it for both the annotated tag message and GitHub Release notes, and strips `Full Changelog` by default.
  - The repo currently treats `scripts/release_publish.sh` as the authoritative release entrypoint; `.github/workflows/release.yml` is only for manual asset repair on an existing tag/release and is not a tag-push autopublish path

[⬆️ Back to top](#top) | [🔙 Back to Main README](./README.md) | [🇨🇳 中文版本](./README_CN.md)
