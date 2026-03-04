<a id="top"></a>

# DataPulse (Chinese name: 数据脉搏) Intelligence Hub (English)

[🔙 Back to Main README](./README.md) | [🇨🇳 中文版本](./README_CN.md) | [⬆️ Back to top](#top)

## Core goal

DataPulse provides one shared intake path for URL extraction, confidence scoring, and memory output
for MCP, Skill, Agent, and bot workflows.

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
- Observability:
  - structured logging (`DATAPULSE_LOG_LEVEL` env var)
- Testing:
  - 496 tests across 25 modules
  - GitHub Actions CI (Python 3.10/3.11/3.12 matrix)

## Install

```bash
pip install -e .
pip install -e ".[all]"   # enable all optional capabilities
```

Optional groups:

- `.[trafilatura]`, `.[youtube]`, `.[telegram]`, `.[browser]`, `.[mcp]`, `.[notebooklm]`  
  Note: `.[mcp]` enables native MCP transport; when missing, `python -m datapulse.mcp_server` falls back to an internal stdio-compatible runtime.

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

# collector health check
datapulse --doctor

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
python -m datapulse.mcp_server
python -m datapulse.mcp_server --list-tools
python -m datapulse.mcp_server --call health
```

28 tools available:

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
- `OBSIDIAN_VAULT`
- `DATAPULSE_SESSION_DIR` (default `~/.datapulse/sessions`)
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

## Functional validation guide

1. Run one-off CLI checks, then multi-URL batch checks, then list/clear lifecycle.
2. Run platform smoke tests before promotion (`datapulse-smoke --platforms ...`).
3. For MCP/Skill/Agent orchestration, pass through `DataPulseItem.to_dict()` to keep schema stable.
4. Keep sensitive secrets and model endpoints out of repository history and inject them through your secret management path.

## Safety

- URL checks block local/private/localhost targets by default.
- `read_batch` skips failed single URLs by default; enforce strict mode in caller when needed.

## Notes

- Repository docs do not include local test environment or model endpoint plaintext.
- Keep sensitive runtime configuration outside the repository and load it in private runtime context.

## OpenClaw integration assets

- Tool contract: `docs/contracts/openclaw_datapulse_tool_contract.json`
- Quick validation scripts: `scripts/datapulse_local_smoke.sh`, `scripts/datapulse_remote_openclaw_smoke.sh`
- Release checklist: `docs/release_checklist.md`

```bash
chmod +x scripts/datapulse_local_smoke.sh scripts/datapulse_remote_openclaw_smoke.sh
export URL_1="https://x.com/xxxx/status/123"
export URL_BATCH="https://x.com/... https://www.reddit.com/..."
bash scripts/datapulse_local_smoke.sh
# remote execution requires VPS/M4 tunnel
bash scripts/datapulse_remote_openclaw_smoke.sh
```

## Release & publishing

- Build artifacts:
  - `python -m build --sdist --wheel .`
  - attach `dist/*.whl` and `dist/*.tar.gz`
- Publishing:
  - `./scripts/release_publish.sh --tag vX.Y.Z`
  - On tag push, `.github/workflows/release.yml` auto uploads release assets

[⬆️ Back to top](#top) | [🔙 Back to Main README](./README.md) | [🇨🇳 中文版本](./README_CN.md)
