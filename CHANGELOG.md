# Changelog

## [0.6.1] - 2026-03-01

### Added — Features
- **Collector Health Self-Check (doctor)**: `BaseCollector` gains `tier`, `setup_hint`, and `check()` method. All 13 collectors implement health self-checks grouped into three tiers: tier 0 (zero-config: rss, arxiv, hackernews), tier 1 (network/free: twitter, reddit, bilibili, trending, generic, jina), tier 2 (needs setup: youtube, xhs, wechat, telegram).
- **Doctor Aggregation**: `ParsePipeline.doctor()` iterates all parsers, calls `check()`, groups results by tier. `DataPulseReader.doctor()` pass-through.
- **CLI `--doctor`**: Tiered health check display with `[OK]`/`[WARN]`/`[ERR]` status icons and actionable setup hints.
- **MCP `doctor()` tool**: Returns JSON health report for all collectors.
- **429-Aware Backoff**: New `RateLimitError` exception with `retry_after` field. `retry()` decorator respects Retry-After header (capped at `max_delay`). `respect_retry_after=False` opt-out.
- **CircuitBreaker Rate-Limit Weighting**: `rate_limit_weight` parameter (default 2) causes rate-limit failures to increment the failure counter faster, opening the circuit sooner under sustained 429s.
- **Ingestion Fingerprint Dedup**: `UnifiedInbox.add()` checks content fingerprint (for content ≥50 chars) to reject near-duplicate items at ingestion. `fingerprint_dedup=False` escape hatch. Fingerprints survive save/reload.
- **Actionable Route Errors**: `ParsePipeline.route()` tracks `best_match` collector and includes `setup_hint` in failure messages.

### Added — Testing
- `tests/test_doctor.py` — 25 new tests for tier assignment, check() shape, doctor() aggregation, setup hints.
- `tests/test_retry.py` — 10 new tests for RateLimitError, 429-aware retry, CircuitBreaker rate-limit weighting.
- `tests/test_storage.py` — 7 new tests for fingerprint dedup (reject/allow/short bypass/opt-out/persist/priority).
- Total test count: 481 across 25 modules.

### Changed
- `BaseCollector` gains `tier: int = 2`, `setup_hint: str = ""` class attributes.
- MCP tool count: 23 → 24 (added `doctor()`).

## [0.6.0] - 2026-03-01

### Added — Features
- **Trending Topics Collector**: `TrendingCollector` in `datapulse/collectors/trending.py` — scrapes trends24.in for X/Twitter trending topics across 400+ global locations. Server-side rendered (requests + BeautifulSoup), no Jina dependency (HTTP 451 blocked).
- **HTML Parsing**: `.trend-card` primary strategy with `h3` + `ol/ul` structural fallback. Extracts rank, name, URL, tweet volume per trend.
- **Volume Parsing**: `parse_volume()` handles K/M suffixes, comma-separated numbers (`125K` → 125000, `1.2M` → 1200000).
- **Location Aliases**: 30+ shortcuts mapping to trends24.in URL slugs (us→united-states, uk→united-kingdom, jp→japan, etc.).
- **`TrendItem` / `TrendSnapshot` dataclasses**: Structured representation of individual trends and hourly snapshots.
- **Reader API**: `DataPulseReader.trending(location, top_n, store)` — async method returning structured `{location, snapshot_time, trend_count, trends[]}`. `store=True` persists snapshot to inbox (opt-in).
- **CLI**: `--trending [LOCATION]` (default: worldwide), `--trending-limit N` (default: 20), `--trending-store` (opt-in inbox storage).
- **MCP Tool**: `trending(location, top_n, store)` — get X/Twitter trending topics for any location.
- `SourceType.TRENDING` enum value.
- `is_trending_url()` URL detector + `resolve_platform_hint()` chain integration.
- `BASE_RELIABILITY["trending"] = 0.78` — between hackernews (0.82) and rss (0.74).
- New confidence flags: `trending_snapshot` (+0.02), `rich_data` (+0.02).

### Added — Testing
- `tests/test_trending_collector.py` — 36 offline tests across 8 test classes (TestCanHandle, TestParseVolume, TestNormalizeLocation, TestBuildUrl, TestParse, TestFetchSnapshots, TestFallbackParsing, TestFormatContent).
- Updated `tests/test_models.py` — SourceType enum values updated for `trending`.
- Total test count: 420+ (raised to 481 in v0.6.1).

### Changed
- `ParsePipeline` includes `TrendingCollector()` after HackerNewsCollector, before RssCollector.
- Version bumped to `0.6.0` across `pyproject.toml`, `__init__.py`, `manifest.json`, tool contract.

## [0.5.1] - 2026-03-01

### Added — Features
- **XHS Engagement Extraction**: `_extract_engagement()` in `datapulse/collectors/xhs.py` — regex-based extraction of like/comment/favorite/share counts from XHS content (Chinese + English patterns). Results stored in `extra["engagement"]`.
- **Platform-aware Search**: `DataPulseReader.search()` gains `platform` parameter. `PLATFORM_SEARCH_SITES` maps platform names (xhs/twitter/reddit/hackernews/arxiv/bilibili) to domain lists, auto-injected into Jina search. CLI `--platform`, MCP `search_web` tool updated.
- **XHS Media Referer Injection**: New `datapulse/core/media.py` — `needs_referer()`, `build_referer()`, `build_media_headers()`, `download_media()` for XHS CDN domains requiring Referer headers.
- **Session TTL Cache**: `session_valid()` and `invalidate_session_cache()` in `datapulse/core/utils.py` — 12-hour positive-only TTL cache for session file existence checks, using existing `TTLCache`. Configurable via `DATAPULSE_SESSION_TTL_HOURS`.
- New confidence flag: `engagement_metrics` (+0.03) — offsets Jina proxy penalty for XHS, restoring baseline 0.72.
- CLI: `--platform` argument (choices: xhs, twitter, reddit, hackernews, arxiv, bilibili).

### Added — Testing
- `tests/test_xhs_engagement.py` — 8 tests for engagement extraction (Chinese/English/mixed/comma numbers/parse integration).
- `tests/test_media.py` — 8 tests for media Referer injection (domain matching/headers/download mock).
- Updated `tests/test_confidence.py` — +3 tests for `engagement_metrics` flag.
- Updated `tests/test_jina_search.py` — +5 tests for platform-aware search.
- Updated `tests/test_utils.py` — +5 tests for session TTL cache.

### Changed
- `datapulse/collectors/xhs.py` rewritten: engagement extraction on Jina success path, `session_valid()` replaces raw `Path.exists()`.

## [0.5.0] - 2026-03-01

### Added — Features
- **Jina API Client**: `datapulse/core/jina_client.py` — unified client for Jina Reader (`r.jina.ai`) and Search (`s.jina.ai`) APIs. `JinaReadOptions` supports CSS selector targeting (`X-Target-Selector`), wait-for-element (`X-Wait-For-Selector`), cache bypass, VLM image descriptions, cookie passthrough, proxy, and POST mode for SPA hash routes. `JinaSearchOptions` supports domain restriction and result limits. Independent `CircuitBreaker` instances for read vs search. API key priority: constructor param > `JINA_API_KEY` env var > no key (free tier).
- **Web Search**: `DataPulseReader.search()` — search the web via Jina Search API and return scored `DataPulseItem` list. Supports `fetch_content=True` for full-page pipeline fetch per result, or `False` for snippet-only mode. Batch inbox persistence (single `save()`). Results integrate into existing 4-dimensional scoring (confidence/authority/corroboration/recency). CLI `--search`, MCP `search_web` tool.
- **Advanced URL Reading**: `read_url_advanced` MCP tool and CLI `--target-selector`, `--no-cache`, `--with-alt` flags for CSS-targeted extraction, cache bypass, and AI image descriptions.
- **Generic Collector Jina Fallback**: `_extract_with_jina()` added as final fallback in `GenericCollector` chain: Trafilatura → BS4 → Firecrawl → Jina Reader → fail. Accepts results >= 200 characters.
- `BASE_RELIABILITY["jina_search"] = 0.72` — new search parser baseline.
- New confidence flags: `css_targeted` (+0.03), `image_captioned` (+0.01), `search_result` (+0.04).
- CLI args: `--search QUERY`, `--site DOMAIN` (repeatable), `--search-limit N`, `--no-fetch`, `--target-selector CSS`, `--no-cache`, `--with-alt`.
- MCP tools: `search_web`, `read_url_advanced`.

### Added — Testing
- `tests/test_jina_client.py` — 29 tests for Jina API client (headers, URL construction, search parsing, circuit breakers, API key priority).
- `tests/test_jina_collector_enhanced.py` — 17 tests for enhanced JinaCollector (option passthrough, confidence flags, circuit breaker degradation).
- `tests/test_jina_search.py` — 10 tests for search flow (fetch_content paths, batch save, sites, limit, min_confidence filter).

### Changed
- `JinaCollector` rewritten to use `JinaAPIClient` with full options support. Reliability bumped 0.64 → 0.72.
- `BASE_RELIABILITY["jina"]` bumped from 0.64 to 0.72.
- Version bumped to `0.5.0` across `pyproject.toml`, `__init__.py`, `manifest.json`, tool contract.

## [0.4.0] - 2026-02-28

### Added — Features
- **Source Authority Tiers**: `SourceRecord` gains `tier` (1=top, 2=standard, 3=niche) and `authority_weight` (0.0-1.0) fields. `SourceCatalog.build_authority_map()` builds name/domain → weight mapping.
- **arXiv Collector**: `ArxivCollector` parses `arxiv.org/abs/`, `arxiv.org/pdf/`, `arxiv:XXXX.XXXXX` via Atom API. Extracts title, authors, abstract, categories, PDF link.
- **HackerNews Collector**: `HackerNewsCollector` parses `news.ycombinator.com` items via Firebase API. Dynamic confidence flags for engagement (`hn_score>=100`, `descendants>=50`).
- **Atom 1.0 Feed**: `build_atom_feed()` outputs Atom 1.0 XML with `<feed xmlns="http://www.w3.org/2005/Atom">`. CLI `--query-atom`, MCP `build_atom_feed` tool.
- **Multi-dimensional Scoring Engine**: `datapulse/core/scoring.py` with 4 dimensions (confidence 0.25, authority 0.30, corroboration 0.25, recency 0.20). `rank_items()` scores, sorts, and annotates items with `score` (0-100), `quality_rank`, and `extra["score_breakdown"]`.
- **Content Fingerprinting**: `content_fingerprint()` for same-topic detection via n-gram shingling.
- **Digest Builder**: `build_digest()` produces curated digests with primary/secondary stories, fingerprint dedup, diverse source selection, provenance metadata. CLI `--digest --top-n --secondary-n`, MCP `build_digest` tool.
- `SourceType.ARXIV` and `SourceType.HACKERNEWS` enum values.
- `is_arxiv_url()`, `is_hackernews_url()` platform detectors.
- `BASE_RELIABILITY["arxiv"] = 0.88`, `BASE_RELIABILITY["hackernews"] = 0.82`.
- Catalog version support expanded to `{1, 2}`.

### Added — Testing
- `tests/test_arxiv_collector.py` — 13 tests for ArxivCollector (can_handle, extract_id, parse_atom_response, author truncation, categories, extra fields).
- `tests/test_hackernews_collector.py` — 11 tests for HackerNewsCollector (can_handle, extract_id, build_result, engagement flags, dead/deleted items).
- `tests/test_scoring.py` — 17 tests for scoring engine (recency, authority, corroboration, composite, rank_items).
- `tests/test_digest.py` — 12 tests for digest builder (structure, counts, diversity, dedup, empty inbox, since/confidence filters).
- Updated `test_source_catalog.py` — 10 new tests for tier/weight fields, build_authority_map, v1 compat, clamping.
- Updated `test_reader.py` — 7 new tests for Atom feed (well-formed XML, namespace, entries, escaping, limit, URN IDs).
- Updated `test_utils.py` — 7 new tests for is_arxiv_url, is_hackernews_url, content_fingerprint, platform hints.
- Updated `test_models.py` — SourceType enum values updated.

### Changed
- Version bumped to `0.4.0` across `pyproject.toml`, `__init__.py`, `manifest.json`, tool contract.
- `ParsePipeline` includes ArxivCollector and HackerNewsCollector (before RssCollector).

## [0.3.0] - 2026-02-28

### Added — Code Quality
- mypy type-checking CI job in `.github/workflows/ci.yml`.
- mypy configuration in `pyproject.toml` (permissive mode, `ignore_missing_imports=true`).
- `types-requests` and `types-beautifulsoup4` added to dev dependencies.
- Pre-commit development setup instructions in `README.md`, `README_CN.md`, `README_EN.md`.

### Added — Features
- `DATAPULSE_BATCH_CONCURRENCY` env var for rate-limiting `read_batch` via `asyncio.Semaphore` (default 5).
- YouTube chapter parsing: `_parse_chapters()` extracts `MM:SS` / `H:MM:SS` timestamps from video descriptions into `extra["chapters"]`.
- Processed state management: `mark_processed()` and `query_unprocessed()` on `UnifiedInbox`, `DataPulseReader`, and as MCP tools.

### Fixed
- JSON Feed `author` field replaced with `authors` array per JSON Feed v1.1 spec (fixes `getattr(item, "author")` bug).
- BeautifulSoup `.get()` return type narrowed with `str()` casts to satisfy mypy.
- Twitter collector `NITTER_INSTANCES` env var parsing fixed to avoid `Optional[str].split()` type error.
- CLI `path` variable renamed to `inbox_path` to avoid type shadow from `login_platform` return.

### Added — Testing
- 15 new tests: batch concurrency, YouTube chapters (5 cases), JSON Feed v1.1 authors, processed state (5 cases), integration pipeline (3 cases).
- `tests/test_integration.py` — end-to-end mock HTTP pipeline test skeleton.
- Total test count: 198.

### Changed
- Version bumped to `0.3.0` across `pyproject.toml`, `__init__.py`, `manifest.json`, tool contract.

## [0.2.0] - 2026-02-28

### Added — Test Infrastructure (Phase 1)
- 183 unit tests across 12 test modules covering models, utils, storage, router, collectors, confidence scoring, retry, reader, and source catalog.
- `tests/conftest.py` with shared fixtures (`sample_item`, `tmp_inbox`, `mock_response`).
- `pytest` + `pytest-asyncio` dev dependencies in `pyproject.toml`.
- `.github/workflows/ci.yml` — GitHub Actions CI running lint + tests on Python 3.10/3.11/3.12.
- `.pre-commit-config.yaml` for local ruff/mypy hooks.

### Added — Resilience (Phase 2)
- `datapulse/core/retry.py` — configurable `retry_with_backoff` decorator and `CircuitBreaker` class.
- `datapulse/core/cache.py` — in-memory TTL cache with thread-safe access.
- Retry integration in `JinaCollector` and RSS collector with exponential backoff.

### Added — Observability (Phase 4)
- `datapulse/core/logging_config.py` — structured logging with `DATAPULSE_LOG_LEVEL` env var support.
- Unified logging across all collectors replacing ad-hoc print statements.

### Changed — Collector Enhancements (Phase 3)
- **RSS**: multi-entry feed parsing (up to `MAX_ENTRIES=25`), returning list of `ParseResult`.
- **Bilibili**: interaction stats (`views`, `likes`, `coins`, `favorites`, `shares`) in `extra` dict.
- **Telegram**: configurable `DATAPULSE_TG_LIMIT` and `DATAPULSE_TG_OFFSET` env vars.
- **Xiaohongshu**: improved title/content extraction with fallback strategies.
- **Jina**: retry-on-failure with backoff; cache integration for repeated URLs.
- Batch URL deduplication in `read_batch`.

### Changed — Core
- Version bumped to `0.2.0`.
- `datapulse/core/storage.py` — improved `prune` with configurable max age; better error handling on corrupt JSON.
- `datapulse/core/utils.py` — new helpers: `validate_external_url` (SSRF protection), `resolve_platform_hint`, `is_platform_url`, `normalize_language`, `content_hash`, `generate_slug`.
- `datapulse/core/source_catalog.py` — `SourceCatalog` with pack-based subscription model, auto-source registration, and domain/pattern matching.
- Import cleanup and ruff lint compliance across all modules.

### Fixed
- Ruff lint: 42 errors resolved (import sorting, unused imports, unused variables).

## [0.1.1] - 2026-02-24

### Added
- 发布流程体系化：新增发布 checklist、发布脚本与 GitHub Actions 自动发布工作流。
- README 与 Release Notes 补充 `dist/*` 资产发布与一键发布说明。
- 新增 PR / Issue 模板，用于版本化提交与发布管理规范化。

### Changed
- 增加 `docs/release_checklist.md` 统一发布验收标准。
- 新增 `scripts/release_publish.sh`，支持 tag 生成/推送与 Release 资产挂接。
- 新增 `.github/workflows/release.yml`，支持 tag 推送触发自动上传构建产物。

## [0.1.0] - 2026-02-24

### Added
- 实现 `DataPulse`（数据脉搏）基础情报中枢：跨平台 URL 采集/解析入口、置信度评分、内存化输出。
- 完整补齐 `README.md`、`README_CN.md`、`README_EN.md` 的功能说明与双语导航结构。
- 补充 OpenClaw 兼容说明与工具调用路径：
  - `docs/contracts/openclaw_datapulse_tool_contract.json`
  - `scripts/quick_test.sh`
- 新增/对齐 `datapulse_skill/manifest.json` 为可用的 Skill 入口定义。
- 提供统一的样例配置 `.env.example` 与测试事实说明 `docs/test_facts.md`。

### Changed
- 许可证变更为不可商用许可：`DataPulse Non-Commercial License v1.0`。
- `pyproject.toml` 中 `license` 字段同步新许可信息。
- 修复 `datapulse_skill/manifest.json` 的 JSON 结构与模式字段问题（可用于上线前校验）。

### Security & Compliance
- 仓库文档移除本地测试环境与模型端点的明文信息，仅保留抽象化环境变量约定。
- README 与测试说明中统一强调本地敏感配置仅在私有运行时注入。

### Notes
- 首次初始化版本，以「功能对齐 + 非商用许可收敛」为主线，未执行完整自动化测试，仅形成可交付结构与文档。
