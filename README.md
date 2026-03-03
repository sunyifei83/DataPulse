<a id="top"></a>

# DataPulse (数据脉搏) Intelligence Hub

> 英文名：DataPulse｜中文名：数据脉搏  
> 点击切换到对应语言版本：  
> <a href="./README_CN.md">🇨🇳 中文版</a> | <a href="./README_EN.md">🇺🇸 English version</a>

<details open>
<summary><b>🇨🇳 中文</b></summary>

## 数据脉搏（DataPulse）核心目标

在统一入口下完成跨平台内容采集、结构化抽取、置信度评估与持久化输出，支持后续接入 MCP / Skill / Agent / Bot 的标准化结果流。

## 当前实现能力（按代码实际）

- 路由与采集器：`twitter/x`, `reddit`, `youtube`, `bilibili`, `telegram`, `wechat`, `xiaohongshu`, `rss`, `arxiv`, `hackernews`, `trending`, `generic web`, `jina`
- 采集策略：
  - Twitter：FxTwitter + Nitter 兜底
  - Reddit：公开 JSON API
  - YouTube：字幕优先，缺失时可回退到音频转写（`GROQ_API_KEY`）
  - Bilibili：官方 API + 交互数据（播放/点赞/投币/收藏/弹幕/转发）
  - Telegram：Telethon（`TG_API_ID`/`TG_API_HASH`），支持 `DATAPULSE_TG_*` 可配置限制
  - WeChat / Xiaohongshu：Jina 兜底 + 重试，支持 Playwright Session 回退，XHS 自动提取互动指标（赞/评论/收藏/分享），Session TTL 缓存
  - RSS：多条目 Feed 解析（最多 5 条），自动识别 feed 类型
  - arXiv：Atom API 解析论文元数据（标题/作者/摘要/分类/PDF 链接）
  - Hacker News：Firebase API 动态抓取，engagement 自动标记
  - Trending：trends24.in 全球 400+ 地区 X/Twitter 热搜趋势抓取，支持地区别名（us/uk/jp 等 30+），小时级快照，Tweet 量级解析
  - 通用网页：Trafilatura/BeautifulSoup，失败时可回退 Firecrawl（`FIRECRAWL_API_KEY`）或 Jina Reader
  - Jina 增强读取：CSS 选择器定向抓取、等待元素加载、Cookie 透传、代理、AI 图片描述、缓存控制
  - Web 搜索：通过 Jina Search API (`s.jina.ai`) 搜索全网，自动提取并评分，支持平台限定搜索（`--platform`）
- 双层输出：
  - 结构化 JSON（统一 `DataPulseItem`）
  - 可选 Markdown 记忆写入（`datapulse-inbox.md` / 自定义路径）
- 多维评分：四维度加权（置信度/来源权威/跨源互证/时效性），输出 0-100 综合分 + 0.01~0.99 置信分
- Digest 构建：自动生成包含 primary/secondary 故事的摘要信封，支持指纹去重与多样性选择
- 稳健性：
  - 统一错误处理，异常窄化（精确捕获 `RequestException`/`TimeoutError` 等）
  - `retry_with_backoff` 重试装饰器 + `CircuitBreaker` 熔断器
  - 429 感知退避：`RateLimitError` 自动遵循 Retry-After 头部，`CircuitBreaker` 对限速加权触发
  - 内存级 TTL 缓存（线程安全，无外部依赖）
  - 并发批量执行（`read_batch`），自动 URL 去重
  - 去重与过期裁剪（默认最多 500 条、30 天）
  - 入库指纹去重：相似内容（≥50 字符）自动去重，避免重复入库
- 自诊断：
  - `datapulse --doctor`：采集器分级健康检查（tier 0/1/2），展示状态、可用性与设置提示
  - 三级采集器分级：tier 0（零配置）、tier 1（网络/免费）、tier 2（需配置）
  - 路由失败时自动附带 setup_hint，指导用户修复
- 可观测性：
  - 结构化日志（`DATAPULSE_LOG_LEVEL` 环境变量控制级别）
- 测试基建：
  - 481 单元测试，覆盖 25 个测试模块
  - GitHub Actions CI（Python 3.10 / 3.11 / 3.12 矩阵）

## 安装

```bash
pip install -e .
pip install -e ".[all]"   # 启用全部可选能力
```

可选分组：

- `.[trafilatura]`、`.[youtube]`、`.[telegram]`、`.[browser]`、`.[mcp]`、`.[notebooklm]`  
  注：`.[mcp]` 为原生 MCP 运行支持；若未安装该额外依赖，`python -m datapulse.mcp_server` 会自动退化为内置 stdio fallback（支持 `--list-tools` / `--call`）。

## 开发环境

```bash
pip install -e ".[dev]"
pip install pre-commit && pre-commit install
```

## 许可证

本项目采用「DataPulse Non-Commercial License v1.0」。
仅允许非商业用途（教学、科研、个人研究、内部评估等）内免费使用；商业使用请联系作者获取商业授权。

详细条款请查看仓库根目录 `LICENSE` 文件。

## 快速开始

### 1) CLI 基础用法

```bash
# 解析单条 URL
datapulse https://x.com/xxxx/status/123

# 批量解析（并发）
datapulse --batch https://x.com/... https://www.reddit.com/... --min-confidence 0.45

# 列出内存（按置信降序）
datapulse --list --limit 10 --min-confidence 0.30

# 登录状态采集（用于登录后场景）
datapulse --login xhs
datapulse --login wechat

# 清空内存
datapulse --clear

# Web 搜索
datapulse --search "LLM inference optimization"
datapulse --search "Python 3.13" --site python.org --site peps.python.org
datapulse --search "RAG best practices" --search-limit 10 --min-confidence 0.7

# 平台限定搜索
datapulse --search "护肤" --platform xhs --search-limit 3

# 热搜趋势
datapulse --trending              # 全球热搜
datapulse --trending us           # 美国热搜
datapulse --trending jp --trending-limit 10  # 日本 Top 10
datapulse --trending uk --trending-store     # 英国热搜，存入 inbox

# 采集器健康自检
datapulse --doctor

# 定向抓取
datapulse https://example.com --target-selector ".article-body" --no-cache
```

### 2) Smoke 测试命令

```bash
# 仅列出需要配置的环境变量
datapulse-smoke --list

# 按平台回归
datapulse-smoke --platforms xhs wechat --require-all

# 运行全部场景（可设置置信阈值）
datapulse-smoke --min-confidence 0.45
```

`datapulse-smoke` 的环境变量输入项：

- `DATAPULSE_SMOKE_TWITTER_URL`
- `DATAPULSE_SMOKE_REDDIT_URL`
- `DATAPULSE_SMOKE_YOUTUBE_URL`
- `DATAPULSE_SMOKE_BILIBILI_URL`
- `DATAPULSE_SMOKE_TELEGRAM_URL`
- `DATAPULSE_SMOKE_RSS_URL`
- `DATAPULSE_SMOKE_WECHAT_URL`
- `DATAPULSE_SMOKE_XHS_URL`

## MCP / Skill / Agent 使用

- MCP 服务端（`.[mcp]` 可选，未安装时自动切入内置 fallback）：

```bash
python -m datapulse.mcp_server
python -m datapulse.mcp_server --list-tools
python -m datapulse.mcp_server --call health
```

暴露 24 个工具：

**采集与读取：**
- `read_url(url, min_confidence=0.0)` — 解析单条 URL
- `read_batch(urls, min_confidence=0.0)` — 批量解析 URL
- `read_url_advanced(url, target_selector, wait_for_selector, no_cache, with_alt, min_confidence)` — CSS 定向抓取
- `search_web(query, sites, platform, limit, fetch_content, min_confidence)` — Web 搜索
- `trending(location, top_n, store)` — X/Twitter 热搜趋势

**内存与状态：**
- `query_inbox(limit, min_confidence)` — 查询收件箱
- `mark_processed(item_id, processed)` — 标记已处理
- `query_unprocessed(limit, min_confidence)` — 查询未处理条目

**信源管理：**
- `list_sources(include_inactive, public_only)` — 列出信源目录
- `list_packs(public_only)` — 列出信源包
- `resolve_source(url)` — URL 信源识别
- `list_subscriptions(profile)` — 列出订阅
- `source_subscribe(profile, source_id)` — 订阅信源
- `source_unsubscribe(profile, source_id)` — 取消订阅
- `install_pack(profile, slug)` — 安装信源包

**Feed 与 Digest：**
- `query_feed(profile, source_ids, limit, min_confidence, since)` — 查询 Feed
- `build_json_feed(profile, source_ids, limit, min_confidence, since)` — JSON Feed
- `build_rss_feed(profile, source_ids, limit, min_confidence, since)` — RSS Feed
- `build_atom_feed(profile, source_ids, limit, min_confidence, since)` — Atom 1.0 Feed
- `build_digest(profile, source_ids, top_n, secondary_n, min_confidence, since)` — 精选摘要

**诊断与工具：**
- `doctor()` — 采集器分级健康自检
- `detect_platform(url)` — 平台检测
- `health()` — 健康检查

- Skill 入口（可供 OpenClaw Skill 接入）：

```python
from datapulse_skill import run
run("请处理这些信息: https://x.com/... 或 https://reddit.com/...")
```

- Agent 调用（可被上层 Bot 框架封装）：

```python
from datapulse.agent import DataPulseAgent

agent = DataPulseAgent(min_confidence=0.25)
result = await agent.handle("https://x.com/... and https://www.reddit.com/...")
```

## 配置与环境变量

- `INBOX_FILE`
- `DATAPULSE_MEMORY_DIR`
- `DATAPULSE_KEEP_DAYS`（默认 30）
- `DATAPULSE_MAX_INBOX`（默认 500）
- `OUTPUT_DIR`
- `DATAPULSE_MARKDOWN_PATH`
- `OBSIDIAN_VAULT`
- `DATAPULSE_SESSION_DIR`（默认 `~/.datapulse/sessions`）
- `TG_API_ID` / `TG_API_HASH`
- `NITTER_INSTANCES`
- `FXTWITTER_API_URL`
- `FIRECRAWL_API_KEY`
- `GROQ_API_KEY`
- `DATAPULSE_LOG_LEVEL`（默认 WARNING）
- `DATAPULSE_TG_MAX_MESSAGES`（默认 20）
- `DATAPULSE_TG_MAX_CHARS`（默认 800）
- `DATAPULSE_TG_CUTOFF_HOURS`（默认 24）
- `DATAPULSE_SMOKE_*`
- `DATAPULSE_BATCH_CONCURRENCY`（默认 5）
- `DATAPULSE_MIN_CONFIDENCE`
- `DATAPULSE_SESSION_TTL_HOURS`（默认 12，Session 缓存 TTL 小时数）
- `JINA_API_KEY`（Jina 增强读取 + Web 搜索 API Key）
- `TAVILY_API_KEY`（Tavily 搜索 API Key）

## 使用建议（openclaw-bot 场景）

- MCP 侧建议用 `read_url/read_batch` 产生结构化 JSON，按 `source_type/confidence/tags` 做二次路由。
- Skill 侧建议用 `DataPulseItem` 的 `to_dict()` 结果直接入队，避免复写解析逻辑。
- Agent 侧建议在对话中先抽 URL，再调用 `agent.handle` 做批量批注与限置信。
- 统一记忆路径建议配置独立目录，便于 Bot 多实例共享已采集结果。

## 安全与边界

- 当前实现对 URL 做基础可达性与域名策略校验（拦截内网/本地地址与非公网解析）。
- `read_batch` 默认跳过单条失败，`return_all=False` 可改为遇错即抛。

## 说明

- 仓库文档不包含本地测试环境与模型端点明文信息。
- 敏感配置需放入你的私有运行时环境，通过安全凭证管理方式注入。

## OpenClaw 对接资产（建议）

- 工具契约模板：`docs/contracts/openclaw_datapulse_tool_contract.json`
- 快速验收脚本：`scripts/datapulse_local_smoke.sh`、`scripts/datapulse_remote_openclaw_smoke.sh`
- 发布清单：`docs/release_checklist.md`

```bash
chmod +x scripts/datapulse_local_smoke.sh scripts/datapulse_remote_openclaw_smoke.sh
export URL_1="https://x.com/xxxx/status/123"
export URL_BATCH="https://x.com/... https://www.reddit.com/..."
bash scripts/datapulse_local_smoke.sh
# 远端（需先配置 VPS/M4 连接变量）
bash scripts/datapulse_remote_openclaw_smoke.sh
```

## 发布与版本绑定（Release）

- 发布资产：
  - `python -m build --sdist --wheel .`
  - 附加 `dist/*.whl` 与 `dist/*.tar.gz`
- 自动化：
  - `./scripts/release_publish.sh --tag vX.Y.Z`
  - 推送 tag 后由 `.github/workflows/release.yml` 自动附加资产到 GitHub Release

[🔼 回到顶部](#top) | [🇨🇳 中文详情页](./README_CN.md) | [🇺🇸 English details](./README_EN.md)

</details>

---

<a id="top"></a>

<details>
<summary><b>🇺🇸 English</b></summary>

## Core goal

Build a single intake path for URL content extraction, confidence scoring, and memory output,
with structured results that can feed MCP, Assistant Skill, Agent, or Bot workflows.

## Implemented capabilities

- Router and collectors: `twitter/x`, `reddit`, `youtube`, `bilibili`, `telegram`, `wechat`, `xiaohongshu`, `rss`, `arxiv`, `hackernews`, `trending`, `generic web`, `jina`
- Collector strategy:
  - Twitter: FxTwitter primary + Nitter fallback
  - Reddit: public JSON API
  - YouTube: transcript first, optional audio transcription fallback (`GROQ_API_KEY`)
  - Bilibili: official API + interaction stats (views/likes/coins/favorites/danmaku/shares)
  - Telegram: Telethon (`TG_API_ID`/`TG_API_HASH`), configurable via `DATAPULSE_TG_*` env vars
  - WeChat / Xiaohongshu: Jina fallback with retry, optional Playwright session fallback, XHS auto-extracts engagement metrics (likes/comments/favorites/shares), session TTL cache
  - RSS: multi-entry feed parsing (up to 5 entries), auto feed type detection
  - arXiv: Atom API parsing for paper metadata (title/authors/abstract/categories/PDF link)
  - Hacker News: Firebase API with dynamic engagement flags
  - Trending: trends24.in scraper for X/Twitter trending topics across 400+ global locations, 30+ location aliases (us/uk/jp etc.), hourly snapshots, tweet volume parsing
  - Generic web: Trafilatura / BeautifulSoup, optional Firecrawl fallback (`FIRECRAWL_API_KEY`) or Jina Reader
  - Jina enhanced reading: CSS selector targeting, wait-for-element, cookie passthrough, proxy, AI image descriptions, cache control
  - Web search: search the web via Jina Search API (`s.jina.ai`), auto-extract and score results, platform-scoped search (`--platform`)
- Output:
  - Structured JSON (`DataPulseItem`)
  - Optional Markdown output (`datapulse-inbox.md` / custom path)
- Multi-dimensional scoring: 4-axis weighted (confidence/authority/corroboration/recency), 0-100 composite + [0.01, 0.99] confidence
- Digest builder: curated primary/secondary stories with fingerprint dedup and diversity selection
- Resilience:
  - unified parse result handling with narrowed exceptions
  - `retry_with_backoff` decorator + `CircuitBreaker` for fault tolerance
  - 429-aware backoff: `RateLimitError` respects Retry-After header, `CircuitBreaker` applies weighted rate-limit detection
  - in-memory TTL cache (thread-safe, zero external deps)
  - concurrent batch read (`read_batch`) with auto URL dedup
  - dedupe and prune by max items / retention days
  - ingestion fingerprint dedup: similar content (≥50 chars) auto-deduplicated at inbox level
- Self-diagnostics:
  - `datapulse --doctor`: tiered health check (tier 0/1/2) for all collectors with status icons and setup hints
  - Three-tier collector classification: tier 0 (zero-config), tier 1 (network/free), tier 2 (needs setup)
  - Actionable error messages in route failures with setup hints
- Observability:
  - structured logging (`DATAPULSE_LOG_LEVEL` env var)
- Testing:
  - 481 tests across 25 test modules
  - GitHub Actions CI (Python 3.10/3.11/3.12 matrix)

## Install

```bash
pip install -e .
pip install -e ".[all]"   # enable all optional capabilities
```

Optional groups:

- `.[trafilatura]`, `.[youtube]`, `.[telegram]`, `.[browser]`, `.[mcp]`, `.[notebooklm]`

## Development

```bash
pip install -e ".[dev]"
pip install pre-commit && pre-commit install
```

## License

This project is released under the **DataPulse Non-Commercial License v1.0**.
It is free for non-commercial use (e.g., education, research, personal/POC evaluation).
Commercial usage requires a separate license from the author.

See the root `LICENSE` file for full terms.

## Quick start

### 1) CLI basics

```bash
# read one URL
datapulse https://x.com/xxxx/status/123

# batch read
datapulse --batch https://x.com/... https://www.reddit.com/... --min-confidence 0.45

# list memory in confidence order
datapulse --list --limit 10 --min-confidence 0.30

# store login sessions when needed
datapulse --login xhs
datapulse --login wechat

# clear memory
datapulse --clear

# web search
datapulse --search "LLM inference optimization"
datapulse --search "Python 3.13" --site python.org --site peps.python.org

# trending topics
datapulse --trending              # worldwide
datapulse --trending us           # United States
datapulse --trending jp --trending-limit 10  # Japan top 10
datapulse --trending uk --trending-store     # UK, save to inbox

# collector health check
datapulse --doctor

# targeted extraction
datapulse https://example.com --target-selector ".article-body" --no-cache
```

### 2) Smoke check

```bash
# show required environment keys for smoke tests
datapulse-smoke --list

# run selected platforms
datapulse-smoke --platforms xhs wechat --require-all

# run all configured scenarios
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

## MCP / Skill / Agent

- MCP server (`.[mcp]` optional, fallback to built-in stdio when missing):

```bash
python -m datapulse.mcp_server
python -m datapulse.mcp_server --list-tools
python -m datapulse.mcp_server --call health
```

24 exposed tools:

**Intake & reading:**
- `read_url(url, min_confidence)` — parse a single URL
- `read_batch(urls, min_confidence)` — batch parse URLs
- `read_url_advanced(url, target_selector, wait_for_selector, no_cache, with_alt, min_confidence)` — CSS-targeted extraction
- `search_web(query, sites, platform, limit, fetch_content, min_confidence)` — web search
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

**Diagnostics & utilities:**
- `doctor()` — tiered collector health check
- `detect_platform(url)` — platform detection
- `health()` — health check

- Skill entry (for OpenClaw/assistant adapters):

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

## Config and env vars

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
- `DATAPULSE_BATCH_CONCURRENCY` (default 5)
- `DATAPULSE_MIN_CONFIDENCE`
- `DATAPULSE_SESSION_TTL_HOURS` (default 12 — session cache TTL in hours)
- `JINA_API_KEY` (Jina API key for enhanced reading and web search)
- `TAVILY_API_KEY` (Tavily API key for web search)

## Recommended usage for bot/agent stacks

- MCP: call `read_url/read_batch` and route by `source_type + confidence` before tool selection.
- Skill: use returned summaries or raw `DataPulseItem.to_dict()` directly to avoid re-parsing.
- Agent: extract URLs from text first, then call `DataPulseAgent.handle` for batched processing.
- Keep memory path stable across nodes if your bot runtime needs shared cache.

## Security and boundaries

- URL routing applies public-network checks and blocks obvious local/private targets.
- `read_batch` skips failed entries by default; set strict failure behavior by code as needed.

## OpenClaw integration assets

- Tool contract: `docs/contracts/openclaw_datapulse_tool_contract.json`
- Quick validation scripts: `scripts/datapulse_local_smoke.sh`, `scripts/datapulse_remote_openclaw_smoke.sh`
- Release checklist: `docs/release_checklist.md`

```bash
chmod +x scripts/datapulse_local_smoke.sh scripts/datapulse_remote_openclaw_smoke.sh
export URL_1="https://x.com/xxxx/status/123"
export URL_BATCH="https://x.com/... https://www.reddit.com/..."
bash scripts/datapulse_local_smoke.sh
# remote execution requires VPS tunnel
bash scripts/datapulse_remote_openclaw_smoke.sh
```

## Release and publishing

- Build artifacts:
  - `python -m build --sdist --wheel .`
  - Upload `dist/*.whl` and `dist/*.tar.gz`
- Release automation:
  - `./scripts/release_publish.sh --tag vX.Y.Z`
  - GitHub Actions auto-publishes assets on tag push via `.github/workflows/release.yml`

## Notes

- Repository docs do not include local test environment or model endpoint plaintext.
- Keep sensitive runtime configuration outside repository and inject via private environment management.

[🔼 Back to top](#top) | [🇨🇳 中文详情页](./README_CN.md) | [🇺🇸 English details](./README_EN.md)

</details>
