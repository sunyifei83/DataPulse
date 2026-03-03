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
  - Web 搜索：通过 Jina Search API (`s.jina.ai`) 搜索全网，自动提取并评分，支持平台限定搜索（`--platform`）
- 产出：
  - 结构化 JSON（`DataPulseItem`）
  - 可选 Markdown 记忆输出（`datapulse-inbox.md` 或自定义路径）
- 多维评分：四维度加权（置信度/来源权威/跨源互证/时效性），输出 0-100 综合分 + 0.01~0.99 置信分
- Digest 构建：自动生成包含 primary/secondary 故事的摘要信封，支持指纹去重与多样性选择
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
- 可观测性：
  - 结构化日志（`DATAPULSE_LOG_LEVEL` 环境变量控制级别）
- 测试基建：
  - 481 个测试，覆盖 25 个测试模块
  - GitHub Actions CI（Python 3.10 / 3.11 / 3.12 矩阵）

## 安装

```bash
pip install -e .
pip install -e ".[all]"   # 启用全部可选能力
```

可选安装组：

- `.[trafilatura]`、`.[youtube]`、`.[telegram]`、`.[browser]`、`.[mcp]`、`.[notebooklm]`  
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

# 采集器健康自检
datapulse --doctor

# 定向抓取
datapulse https://example.com --target-selector ".article-body" --no-cache
```

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

## MCP / Skill / Agent

- MCP 服务端（`.[mcp]` 可选）：

```bash
python -m datapulse.mcp_server
python -m datapulse.mcp_server --list-tools
python -m datapulse.mcp_server --call health
```

24 个可用工具：

**采集与读取：**
- `read_url(url, min_confidence)` — 解析单条 URL
- `read_batch(urls, min_confidence)` — 批量解析 URL
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
- `DATAPULSE_SESSION_TTL_HOURS`（默认 12 — session 缓存 TTL 小时数）
- `JINA_API_KEY`（Jina 增强读取 + Web 搜索 API Key）
- `TAVILY_API_KEY`（Tavily 搜索 API Key）

## 测试与功能使用建议

1. 先跑 CLI 单条 -> 再跑批量 -> 再跑 `--list` 与 `--clear` 的生命周期操作。
2. 针对关键平台先执行 `datapulse-smoke --platforms ...` 做回归。
3. 为 MCP/Skill/Agent 统一消费 `DataPulseItem.to_dict()` 的 JSON 字段，减少跨组件格式不一致。
4. 敏感凭据通过外部秘钥渠道注入，不写入仓库。

## 安全边界

- URL 验证会拒绝本地/内网/非公网解析目标，降低 SSRF 风险。
- `read_batch` 默认跳过单条失败；如需“全量成功”策略，可在调用层收敛。

## 说明

- 仓库文档不包含本地测试环境或模型端点明文信息。
- 敏感配置通过私有运行时注入，不落库。

## OpenClaw 对接说明

- 工具合约模板：`docs/contracts/openclaw_datapulse_tool_contract.json`
- 快速验证脚本：`scripts/datapulse_local_smoke.sh`、`scripts/datapulse_remote_openclaw_smoke.sh`
- 发布清单：`docs/release_checklist.md`

```bash
chmod +x scripts/datapulse_local_smoke.sh scripts/datapulse_remote_openclaw_smoke.sh
export URL_1="https://x.com/xxxx/status/123"
export URL_BATCH="https://x.com/... https://www.reddit.com/..."
bash scripts/datapulse_local_smoke.sh
# 远端执行（需先配置 VPS/M4）
bash scripts/datapulse_remote_openclaw_smoke.sh
```

## 发布与版本绑定

- 发布资产构建：
  - `python -m build --sdist --wheel .`
  - 生成的 `dist/*.whl` 与 `dist/*.tar.gz` 作为发布附件
- 版本发布方式：
  - `./scripts/release_publish.sh --tag vX.Y.Z`
  - 推送 tag 后由 `.github/workflows/release.yml` 自动上传 GitHub Release 资产

[⬆️ 回到顶部](#top) | [🔙 返回主 README](./README.md) | [🇺🇸 English version](./README_EN.md)
