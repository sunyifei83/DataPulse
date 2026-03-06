<a id="top"></a>

# 数据脉搏（DataPulse）

[🔙 返回主 README](./README.md) | [🇺🇸 English version](./README_EN.md) | [⬆️ 回到顶部](#top)

## 数据脉搏（DataPulse）核心目标

建立统一的跨平台情报入口：对 URL 做采集、解析、置信评分、去重归档并输出结构化结果，服务于 MCP、Skill、Agent、Bot 等编排场景。

## 真实实现能力

- 路由与采集器：`twitter/x`, `reddit`, `youtube`, `bilibili`, `telegram`, `wechat`, `xiaohongshu`, `rss`, `arxiv`, `hackernews`, `trending`, `generic web`, `jina`
- 平台采集策略：
  - Twitter：FxTwitter 主链路 + Nitter 兜底
  - Reddit：公开 `.json` API
  - YouTube：优先字幕，其次可选 Whisper（`GROQ_API_KEY`）
  - Bilibili：官方 API + 交互数据（播放/点赞/投币/收藏/弹幕/转发）
  - Telegram：Telethon（`TG_API_ID`/`TG_API_HASH`），支持 `DATAPULSE_TG_*` 可配置限制
  - WeChat / 小红书：Jina 兜底 + 重试，支持 Playwright 会话回退，XHS 自动提取互动指标（赞/评论/收藏/分享），Session TTL 缓存
  - RSS：多条目 Feed 解析（最多 5 条），自动识别 feed 类型
  - arXiv：Atom API 解析论文元数据（标题/作者/摘要/分类/PDF 链接）
  - Hacker News：Firebase API 动态抓取，engagement 自动标记
  - Trending：trends24.in 全球 400+ 地区 X/Twitter 热搜趋势抓取，30+ 地区别名（us/uk/jp 等），小时级快照，Tweet 量级解析
  - 通用网页：Trafilatura / BeautifulSoup，失败再尝试 Firecrawl（`FIRECRAWL_API_KEY`）或 Jina Reader
  - Jina 增强读取：CSS 选择器定向抓取、等待元素加载、Cookie 透传、代理、AI 图片描述、缓存控制
  - Web 搜索：默认通过多源网关（`search-provider=auto`）路由 Jina/Tavily，支持平台限定搜索（`--platform`）、`--search-provider`、`--search-mode`、深度/新闻/时间窗参数（`--search-deep --search-news --search-time-range --search-freshness`）
  - 产出：
  - 结构化 JSON（`DataPulseItem`）
  - 可选 Markdown 记忆输出（`datapulse-inbox.md` 或自定义路径）
- 多维评分：四维度加权（置信度/来源权威/跨源互证/时效性），输出 0-100 综合分 + 0.01~0.99 置信分
- Digest 构建：自动生成包含 primary/secondary 故事的摘要信封，支持指纹去重与多样性选择
- 任务化（首版 Watch Mission）：
  - 支持保存搜索任务、列出任务、手动执行、禁用任务
  - CLI / Reader / MCP 共用同一套任务对象与运行记录模型
- 处置化（首版 Triage Queue）：
  - 支持 `new / triaged / verified / duplicate / ignored / escalated` 状态流
  - 支持 review note、状态变更记录、`duplicate_of` 归并标记
  - 支持 CLI / Reader / MCP / Console 共用同一套 triage 语义
  - 支持重复项解释（duplicate explain），给出候选条目、相似信号和建议保留主条目
- 证据化（首版 Story Workspace）：
  - 支持 story 聚类、主次证据、时间线、冲突提示、实体聚合
  - 支持 `--story-build / --story-list / --story-show / --story-export`
  - 支持 Reader / MCP 共用同一套 story 语义
- 告警与调度（首版）：
  - 支持 threshold alert rule、到期任务轮询、daemon 单实例锁
  - 支持关键词 / 标签 / 域名 / source_type / 时效过滤
  - 支持 JSON / Markdown / Webhook / 飞书 / Telegram 五类告警分发
  - 支持命名 route 配置与 `--alert-route-list`
  - 支持 `watch_status` 读取 daemon 心跳、指标与最近错误
  - 支持 JSON + HTML 静态状态页输出
- 浏览器控制台（G0）：
  - 提供 `datapulse-console` 本地浏览器控制台
  - 汇总 watch / triage / alert / route / status 五块首版工作台能力
- 稳定性：
  - 统一失败处理，异常窄化（精确捕获 `RequestException`/`TimeoutError` 等）
  - `retry_with_backoff` 重试装饰器 + `CircuitBreaker` 熔断器
  - 429 感知退避：`RateLimitError` 自动遵循 Retry-After 头部，`CircuitBreaker` 对限速加权触发
  - 内存级 TTL 缓存（线程安全，无外部依赖）
  - 批量并发解析，自动 URL 去重
  - 去重 + 时效裁剪（默认 500 条 / 30 天）
  - 入库指纹去重：相似内容（≥50 字符）自动去重，避免重复入库
- 自诊断：
  - `datapulse --doctor`：采集器分级健康检查（tier 0/1/2），展示状态、可用性与设置提示
  - 三级采集器分级：tier 0（零配置）、tier 1（网络/免费）、tier 2（需配置）
  - 路由失败时自动附带 setup_hint，指导用户修复
  - `datapulse --troubleshoot`：输出可执行修复清单（支持 `--troubleshoot <collector>` 定向）
  - `datapulse --check-update`：检查 GitHub 最新版本
  - `datapulse --version`：展示当前版本
  - `datapulse --self-update`：检测并执行线上升级（无更新则提示）
- 可观测性：
  - 结构化日志（`DATAPULSE_LOG_LEVEL` 环境变量控制级别）
- 轻量实体增强（EdgeQuake 蒸馏）：
  - `--entities` 启用 URL 级实体抽取（`fast`/`llm`）
  - `--entity-query` / `--entity-graph` / `--entity-stats` 支持实体存储与查询
  - 评分链路可通过 `DATAPULSE_ENTITY_CORROBORATION_WEIGHT` 引入实体跨源互证加分（默认 `0`）
- 测试基建：
  - 616 个测试，覆盖 41 个测试模块
  - GitHub Actions CI（Python 3.10 / 3.11 / 3.12 矩阵）

## 安装

```bash
pip install -e .
pip install -e ".[all]"   # 启用全部可选能力
```

可选安装组：

- `.[console]`、`.[trafilatura]`、`.[youtube]`、`.[telegram]`、`.[browser]`、`.[mcp]`、`.[notebooklm]`  
  说明：`.[mcp]` 为原生 MCP 能力；未安装时，`python -m datapulse.mcp_server` 自动切到本地 fallback。

## 开发环境

```bash
pip install -e ".[dev]"
pip install pre-commit && pre-commit install
```

## 许可证

本仓库采用 **DataPulse Non-Commercial License v1.0**（不可商用许可证）。
仅支持非商用场景（教学、科研、个人学习、内部 PoC）免费使用；商业使用需联系作者获取商业授权。

完整条款请查看仓库根目录 `LICENSE`。

## 使用流程

### 1. CLI 侧

```bash
# 解析单条
datapulse https://x.com/xxxx/status/123

# 批量解析
datapulse --batch https://x.com/... https://www.reddit.com/... --min-confidence 0.45

# 列出内存
datapulse --list --limit 10 --min-confidence 0.30

# 登录态采集
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

# Watch Mission
datapulse --watch-create --watch-name "AI Radar" --watch-query "OpenAI agents" --watch-platform twitter
datapulse --watch-list
datapulse --watch-run ai-radar
datapulse --watch-disable ai-radar

# 按调度执行到期任务
datapulse --watch-create --watch-name "Infra Radar" --watch-query "LLM inference infra" --watch-schedule @hourly
datapulse --watch-run-due

# 配置 threshold alert rule 并查看告警
datapulse --watch-create --watch-name "Launch Radar" --watch-query "OpenAI launch" --watch-alert-min-score 70 --watch-alert-channel markdown
datapulse --alert-list

# richer alert rule + 命名 route
datapulse --watch-create --watch-name "Launch Ops" --watch-query "OpenAI launch" --watch-alert-route ops-webhook --watch-alert-keyword launch --watch-alert-domain openai.com
datapulse --alert-route-list

# daemon 单轮执行
datapulse --watch-daemon --watch-daemon-once

# 查看 daemon 心跳与指标
datapulse --watch-status

# Triage Queue
datapulse --triage-list
datapulse --triage-explain item-123
datapulse --triage-update item-123 --triage-state verified --triage-note-text "confirmed by analyst"
datapulse --triage-note item-123 --triage-note-text "need follow-up"
datapulse --triage-stats

# Story Workspace
datapulse --story-build
datapulse --story-list
datapulse --story-show story-openai-launch
datapulse --story-export story-openai-launch --story-format markdown

# 启动浏览器控制台（G0）
datapulse-console --port 8765

# 采集器健康自检
datapulse --doctor
datapulse --troubleshoot
datapulse --troubleshoot wechat

# 版本与更新
datapulse --version
datapulse --check-update
datapulse --self-update

# 定向抓取
datapulse https://example.com --target-selector ".article-body" --no-cache

# 实体增强
datapulse https://x.com/xxxx/status/123 --entities --entity-mode fast
datapulse --entity-query OPENAI --entity-type CONCEPT
datapulse --entity-graph OPENAI
datapulse --entity-stats
```

### 0. 最小可用启动

仅需先满足：

- Python 3.10+
- `pip install -e .` 可执行

先执行：

```bash
pip install -e .
datapulse --config-check
datapulse --doctor
```

后续建议：

- 若 `--config-check` 显示搜索密钥缺失，仅按需配置（至少一个即可）：
  - `export JINA_API_KEY=<your_jina_api_key>`（增强抓取/搜索能力）
  - `export TAVILY_API_KEY=<your_tavily_api_key>`（增强搜索覆盖与回退）
- 若 `--doctor` 提示 tier2 依赖不足，按输出的 `建议执行` 逐步修复。

### 0.1 场景化命令速查

A. 单条解析:
  - `datapulse https://x.com/xxxx/status/123`
B. 批量解析:
  - `datapulse --batch https://x.com/... https://www.reddit.com/...`
  - 短参数：`datapulse -b https://x.com/... https://www.reddit.com/...`
C. 搜索:
  - `datapulse --search "LLM inference optimization"`
  - 短参数：`datapulse -s "LLM inference optimization"`
D. 热搜:
  - `datapulse --trending us --trending-limit 10`
  - 短参数：`datapulse -T us --trending-limit 10`
E. 实体:
  - `datapulse https://x.com/xxxx/status/123 --entities --entity-mode fast`
F. Watch:
  - `datapulse --watch-create --watch-name "AI Radar" --watch-query "OpenAI agents"`
  - `datapulse --watch-run ai-radar`
G. Watch 调度:
  - `datapulse --watch-run-due`
H. Alert:
  - `datapulse --alert-list`
  - `datapulse --alert-route-list`
I. Daemon:
  - `datapulse --watch-daemon --watch-daemon-once`
J. Triage:
  - `datapulse --triage-list`
  - `datapulse --triage-explain <item_id>`
  - `datapulse --triage-update <item_id> --triage-state verified`
K. Story Workspace:
  - `datapulse --story-build`
  - `datapulse --story-list`
  - `datapulse --story-show <story_id>`
L. GUI 控制台:
  - `datapulse-console --port 8765`
M. 诊断:
  - `datapulse --config-check`
  - `datapulse --doctor`
  - `datapulse --troubleshoot`
  - `datapulse --troubleshoot wechat`
  - `datapulse --skill-contract`
  - `datapulse --check-update`
  - `datapulse --self-update`
  - 短参数：`datapulse -k`、`datapulse -d`

已提供的短参数：
- `-b/--batch`、`-s/--search`、`-S/--site`、`-l/--list`、`-T/--trending`、`-i/--login`、`-d/--doctor`、`-k/--config-check`；诊断扩展命令：`--troubleshoot`、`--skill-contract`、`--check-update`、`--self-update`、`--version`

### 2. Smoke 测试

```bash
# 仅展示必须配置的变量
datapulse-smoke --list

# 按平台执行
datapulse-smoke --platforms xhs wechat --require-all

# 执行全部配置场景
datapulse-smoke --min-confidence 0.45
```

支持变量：

- `DATAPULSE_SMOKE_TWITTER_URL`
- `DATAPULSE_SMOKE_REDDIT_URL`
- `DATAPULSE_SMOKE_YOUTUBE_URL`
- `DATAPULSE_SMOKE_BILIBILI_URL`
- `DATAPULSE_SMOKE_TELEGRAM_URL`
- `DATAPULSE_SMOKE_RSS_URL`
- `DATAPULSE_SMOKE_WECHAT_URL`
- `DATAPULSE_SMOKE_XHS_URL`

XHS/通用 Browser 回退时的低噪行为可选配置：

- `DATAPULSE_BROWSER_HUMAN_LIKE=1`（开启拟人化抓取行为；默认 0）
- `DATAPULSE_BROWSER_MIN_INTERVAL_SECONDS`（全局最小请求间隔，默认 2.2）
- `DATAPULSE_BROWSER_INTERVAL_JITTER_SECONDS`（请求抖动，默认 1.5）
- `DATAPULSE_BROWSER_PRE_NAV_WAIT_MS_MIN` / `DATAPULSE_BROWSER_PRE_NAV_WAIT_MS_MAX`（导航前随机停顿）
- `DATAPULSE_BROWSER_POST_NAV_WAIT_MS_MIN` / `DATAPULSE_BROWSER_POST_NAV_WAIT_MS_MAX`（导航后沉降等待）
- `DATAPULSE_BROWSER_SCROLL_STEPS_MIN` / `DATAPULSE_BROWSER_SCROLL_STEPS_MAX`（拟人滚动步数）
- `DATAPULSE_BROWSER_SCROLL_WAIT_MS_MIN` / `DATAPULSE_BROWSER_SCROLL_WAIT_MS_MAX`（滚动间隔）
- `DATAPULSE_BROWSER_RANDOMIZE_VIEWPORT=1`（随机 viewport，默认 1）
- `DATAPULSE_BROWSER_USER_AGENT`（自定义 UA）
- `DATAPULSE_BROWSER_LOCALE`（默认 `zh-CN`）
- `DATAPULSE_BROWSER_TIMEZONE`（默认 `Asia/Shanghai`）
- `DATAPULSE_BROWSER_DISABLE_WEBDRIVER=1`（开启 `navigator.webdriver=false` 注入）

建议 XHS 执行顺序：

1) `uv run python3 -m datapulse.cli --login xhs`
2) `DATAPULSE_BROWSER_HUMAN_LIKE=1 uv run python3 -m datapulse.tools.smoke --platforms xhs --min-confidence 0.0`

### 2.1 XHS 复核评分（高可读 + 机读）——B 方案优先

新增自动化复核脚本：`scripts/run_xhs_quality_report.sh`

- 默认执行 `provider=multi` + `mode=multi`（Tavily + Jina 的多源融合路径）
- 默认输出目标：`query=openclaw`
- 输出文件：`artifacts/xhs_quality_<RUN_ID>/xhs_quality_report.json` 与 `xhs_quality_report.md`

快速执行：

```bash
chmod +x scripts/run_xhs_quality_report.sh
bash scripts/run_xhs_quality_report.sh
```

自定义执行（按你的场景）：

```bash
export DATAPULSE_XHS_QUERY="openclaw 记忆"
export DATAPULSE_XHS_LIMIT=10
export DATAPULSE_XHS_MIN_CONFIDENCE=0.0
export DATAPULSE_XHS_PREFER_ENGAGEMENT=1
export JINA_API_KEY=<your-jina-key>
export TAVILY_API_KEY=<your-tavily-key>
bash scripts/run_xhs_quality_report.sh
```

机读/人读并存：
- JSON：`xhs_quality_report.json`（推荐 CI 与自动化回传）
- Markdown：`xhs_quality_report.md`（人类审阅）

分层规则（脚本内置）：
- 高置信：`confidence >= 0.80 且 score >= 70`
- 中置信：`confidence >= 0.65 且 score >= 50`
- 低置信：其余

阈值可通过环境变量调参与追溯。

## MCP / Skill / Agent

- MCP 服务端（`.[mcp]` 可选）：

```bash
python -m datapulse.mcp_server
python -m datapulse.mcp_server --list-tools
python -m datapulse.mcp_server --call health
```

45 个可用工具：

**采集与读取：**
- `read_url(url, min_confidence)` — 解析单条 URL
- `read_batch(urls, min_confidence)` — 批量解析 URL
- `read_url_advanced(url, target_selector, wait_for_selector, no_cache, with_alt, min_confidence)` — CSS 定向抓取
- `search_web(query, sites, platform, limit, fetch_content, min_confidence, provider='auto', mode='single', deep=False, news=False, time_range=None, freshness=None, extract_entities=False, entity_mode='fast', store_entities=True, entity_api_key=None, entity_model='gpt-4o-mini', entity_api_base='https://api.openai.com/v1')` — Web 搜索
- `trending(location, top_n, store)` — X/Twitter 热搜趋势

**内存与状态：**
- `query_inbox(limit, min_confidence)` — 查询收件箱
- `mark_processed(item_id, processed)` — 标记已处理
- `query_unprocessed(limit, min_confidence)` — 查询未处理条目

**处置层（Triage Queue）：**
- `triage_list(limit=20, min_confidence=0.0, states=None, include_closed=False)` — 列出处置队列
- `triage_explain(item_id, limit=5)` — 解释重复项候选和建议主条目
- `triage_update(item_id, state, note='', actor='mcp', duplicate_of='')` — 更新处置状态
- `triage_note(item_id, note, author='mcp')` — 追加处置备注
- `triage_stats(min_confidence=0.0)` — 查看队列统计

**证据层（Story Workspace）：**
- `story_build(profile='default', source_ids=None, max_stories=10, evidence_limit=6, min_confidence=0.0, since=None)` — 构建并持久化 story 聚类快照
- `story_list(limit=20, min_items=1)` — 列出已持久化的 story
- `story_show(identifier)` — 查看单个 story
- `story_export(identifier, output_format='json')` — 导出 story（`json` / `markdown`）

**任务化（Watch Mission）：**
- `create_watch(name, query, platforms=None, sites=None, schedule='manual', min_confidence=0.0, top_n=5)` — 创建任务
- `list_watches(include_disabled=False)` — 列出任务
- `run_watch(identifier)` — 手动执行任务
- `disable_watch(identifier)` — 禁用任务
- `run_due_watches(limit=0)` — 执行当前全部到期任务
- `list_alerts(limit=20, mission_id='')` — 列出告警事件
- `list_alert_routes()` — 列出已配置的命名告警路由
- `watch_status()` — 查看 daemon 心跳、指标与最近错误

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
- `emit_digest_package(profile='default', source_ids=None, top_n=3, secondary_n=7, min_confidence=0.0, since=None, output_format='json')` — 导出 office-ready 摘要包（`json`/`markdown`）

**诊断与工具：**
- `doctor()` — 采集器分级健康自检
- `detect_platform(url)` — 平台检测
- `health()` — 健康检查
- `extract_entities(url, mode='fast', store_entities=True, ...)` — 单 URL 实体抽取（`fast`/`llm`）
- `query_entities(entity_type='', name='', min_sources=1, limit=50)` — 实体查询
- `entity_graph(entity_name, limit=50)` — 实体关联图
- `entity_stats()` — 实体统计

- Skill 接口（适配 OpenClaw 等）：

```python
from datapulse_skill import run
run("请处理这些链接：https://x.com/... 和 https://www.reddit.com/...")
```

- Agent 接口：

```python
from datapulse.agent import DataPulseAgent

agent = DataPulseAgent(min_confidence=0.25)
result = await agent.handle("https://x.com/... and https://www.reddit.com/...")
```

## 配置项

- `INBOX_FILE`
- `DATAPULSE_MEMORY_DIR`
- `DATAPULSE_KEEP_DAYS`（默认 30）
- `DATAPULSE_MAX_INBOX`（默认 500）
- `OUTPUT_DIR`
- `DATAPULSE_MARKDOWN_PATH`
- `OBSIDIAN_VAULT`
- `DATAPULSE_SESSION_DIR`（默认 `~/.datapulse/sessions`）
- `DATAPULSE_WATCHLIST_PATH`（watch mission 存储文件）
- `DATAPULSE_ALERTS_PATH`（告警 JSON 存储文件）
- `DATAPULSE_ALERTS_MARKDOWN_PATH`（告警 Markdown 输出文件）
- `DATAPULSE_ALERT_ROUTING_PATH`（命名告警路由配置文件）
- `DATAPULSE_ALERT_WEBHOOK_URL`（默认 webhook 告警地址）
- `DATAPULSE_FEISHU_WEBHOOK_URL`（默认飞书 webhook 地址）
- `DATAPULSE_TELEGRAM_BOT_TOKEN`（Telegram 告警 bot token）
- `DATAPULSE_TELEGRAM_CHAT_ID`（Telegram 告警 chat id）
- `DATAPULSE_WATCH_DAEMON_LOCK`（daemon 锁文件）
- `DATAPULSE_WATCH_STATUS_PATH`（daemon JSON 状态文件）
- `DATAPULSE_WATCH_STATUS_HTML`（daemon HTML 状态页）
- `DATAPULSE_STORIES_PATH`（story workspace 存储文件）
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
- `DATAPULSE_MIN_CONFIDENCE`
- `DATAPULSE_ENTITY_STORE`（实体存储文件，默认 `entity_store.json`）
- `DATAPULSE_ENTITY_CORROBORATION_WEIGHT`（实体跨源互证加权）
- `DATAPULSE_SESSION_TTL_HOURS`（默认 12 — session 缓存 TTL 小时数）
- `JINA_API_KEY`（Jina 增强读取 + Web 搜索 API Key）
- `TAVILY_API_KEY`（Tavily 搜索 API Key）
- `DATAPULSE_XHS_QUERY`（默认 `openclaw`）
- `DATAPULSE_XHS_LIMIT`（默认 `8`）
- `DATAPULSE_XHS_MIN_CONFIDENCE`（默认 `0.0`）
- `DATAPULSE_XHS_SELECT`（默认 `1`）
- `DATAPULSE_XHS_PREFER_ENGAGEMENT`（默认 `1`）
- `DATAPULSE_XHS_NO_CONTENT_PRINT`（默认 `1`）
- `DATAPULSE_XHS_TIMEOUT_SECONDS`（默认 `120`）
- `DATAPULSE_XHS_HIGH_CONFIDENCE`（默认 `0.80`）
- `DATAPULSE_XHS_MEDIUM_CONFIDENCE`（默认 `0.65`）
- `DATAPULSE_XHS_HIGH_SCORE`（默认 `70`）
- `DATAPULSE_XHS_MEDIUM_SCORE`（默认 `50`）

## 开发与入库约束

- 蓝图计划内的变更按逻辑单元提交入库，不长期停留在本地脏工作区。
- 提交推送后默认触发 GitHub Actions，当前闸门为 `ruff check datapulse/`、`mypy datapulse/`、`pytest tests/`。
- `G0` 浏览器控制台额外通过 `datapulse-console --help` 做入口烟测，确保 console 依赖和脚本包装在 CI 可安装。

## 测试与功能使用建议

1. 先跑 CLI 单条 -> 再跑批量 -> 再跑 `--list` 与 `--clear` 的生命周期操作。
2. 针对关键平台先执行 `datapulse-smoke --platforms ...` 做回归。
3. 为 MCP/Skill/Agent 统一消费 `DataPulseItem.to_dict()` 的 JSON 字段，减少跨组件格式不一致。
4. 敏感凭据通过外部秘钥渠道注入，不写入仓库。
5. 仓内常规操作工作流（功能迭代→编译跟测→高 HA 交付→入库→推送→CI 全绿→问题闭环）见 [docs/inhouse_workflow.md](docs/inhouse_workflow.md)。

## 安全边界

- URL 验证会拒绝本地/内网/非公网解析目标，降低 SSRF 风险。
- `read_batch` 默认跳过单条失败；如需“全量成功”策略，可在调用层收敛。

## 说明

- 仓库文档不包含本地测试环境或模型端点明文信息。
- 敏感配置通过私有运行时注入，不落库。

## OpenClaw 对接说明

- 工具合约模板：`docs/contracts/openclaw_datapulse_tool_contract.json`
- 快速验证脚本：`scripts/datapulse_local_smoke.sh`、`scripts/run_openclaw_remote_smoke_local.sh`
- 发布清单：`docs/release_checklist.md`

### OpenClaw 调试环境与应用环境凭据管理建议

- 调试环境（本地/测试验证）：
  - 真实 `VPS_*`、`MACMINI_*`、`TG_API_*`、`JINA_API_KEY` 等写入 `.env.openclaw.local`，仅用于本机复现与调试。
  - `.env.openclaw.local` 不入库，`scripts/run_openclaw_remote_smoke_local.sh` 可从 `.env.openclaw.example` 引导自动持久化。
- 应用环境（发布/CI/共享主机）：
  - 不在仓库中放入明文凭据；使用部署侧安全渠道注入（如 GitHub Secrets、系统变量、vault、secret mount）。
  - 部署进程侧应优先注入与覆盖，脚本通过环境变量读取后生效。
- 公共红线：
  - `.env.openclaw.example` 仅保留占位符，禁止提交真实账号密码、口令与密钥。
  - 提交前执行 `bash scripts/security_guardrails.sh`，将敏感写入行为变更视为阻塞问题。

### 实操对照表（调试环境 vs 应用环境）

| 目标 | 凭据来源 | 存放位置 | 入库策略 | 运行优先级 |
| --- | --- | --- | --- | --- |
| 本地调试/复现 | 现场手工变量 | `.env.openclaw.local`（本机） | `.gitignore` 保护，不入库 | 高于 `.env.openclaw.example` |
| 共享测试/CI/CD | Secret 管理服务/OS Env | 运行时环境注入 | 不写入仓库历史 | 高于本地调试文件 |
| 模板发布 | 脱敏模板 | `.env.openclaw.example` | 可入库，保持占位符 | 低于运行时 |

建议配合 [docs/search_gateway_config.md](docs/search_gateway_config.md) 与 [docs/test_facts.md](docs/test_facts.md) 执行统一约束。

```bash
chmod +x scripts/datapulse_local_smoke.sh scripts/run_openclaw_remote_smoke_local.sh
# 首次执行会自动持久化；如需手工覆盖可先 cp .env.openclaw.example .env.openclaw.local 后编辑
export URL_1="https://x.com/xxxx/status/123"
export URL_BATCH="https://x.com/... https://www.reddit.com/..."
bash scripts/datapulse_local_smoke.sh
# 远端执行（需先配置 VPS/M4）
bash scripts/run_openclaw_remote_smoke_local.sh
```

## 发布与版本绑定

- 发布资产构建：
  - `python -m build --sdist --wheel .`
  - 生成的 `dist/*.whl` 与 `dist/*.tar.gz` 作为发布附件
- 版本发布方式：
  - `./scripts/release_publish.sh --tag vX.Y.Z`
  - `scripts/release_publish.sh` 会自动从 `RELEASE_NOTES.md` 中提取对应 `## Release: DataPulse vX.Y.Z` 片段作为发布说明，并默认剥离 `Full Changelog` 字段，避免发布页噪音
  - 推送 tag 后由 `.github/workflows/release.yml` 自动上传 GitHub Release 资产

[⬆️ 回到顶部](#top) | [🔙 返回主 README](./README.md) | [🇺🇸 English version](./README_EN.md)
