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

- 路由与采集器：`twitter/x`, `reddit`, `youtube`, `bilibili`, `telegram`, `wechat`, `xiaohongshu`, `rss`, `generic web`
- 采集策略：
  - Twitter：FxTwitter + Nitter 兜底
  - Reddit：公开 JSON API
  - YouTube：字幕优先，缺失时可回退到音频转写（`GROQ_API_KEY`）
  - Bilibili：官方 API
  - Telegram：Telethon（需要 `TG_API_ID` / `TG_API_HASH`）
  - WeChat / Xiaohongshu：Jina 兜底，支持 Playwright Session 回退
  - RSS：取 feed 最新条目
  - 通用网页：Trafilatura/BeautifulSoup，失败时可回退 Firecrawl（`FIRECRAWL_API_KEY`）
- 双层输出：
  - 结构化 JSON（统一 `DataPulseItem`）
  - 可选 Markdown 记忆写入（`datapulse-inbox.md` / 自定义路径）
- 分数与置信：基于解析器可靠性、标题/正文长度/来源/作者/标签与特征，最终返回 0.01~0.99 区间
- 稳健性：
  - 统一错误处理
  - 并发批量执行（`read_batch`）
  - 去重与过期裁剪（默认最多 500 条、30 天）

## 安装

```bash
pip install -e .
pip install -e ".[all]"   # 启用全部可选能力
```

可选分组：

- `.[trafilatura]`、`.[youtube]`、`.[telegram]`、`.[browser]`、`.[mcp]`、`.[notebooklm]`

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

- MCP 服务端（需安装 `.[mcp]`）：

```bash
python -m datapulse.mcp_server
```

暴露工具：

- `read_url(url, min_confidence=0.0)`
- `read_batch(urls, min_confidence=0.0)`
- `query_inbox(limit=20, min_confidence=0.0)`
- `detect_platform(url)`
- `health()`

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
- `DATAPULSE_SMOKE_*`
- `DATAPULSE_MIN_CONFIDENCE`

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

- Router and collectors: `twitter/x`, `reddit`, `youtube`, `bilibili`, `telegram`, `wechat`, `xiaohongshu`, `rss`, `generic web`
- Collector strategy:
  - Twitter: FxTwitter primary + Nitter fallback
  - Reddit: public JSON API
  - YouTube: transcript first, optional audio transcription fallback (`GROQ_API_KEY`)
  - Bilibili: official API
  - Telegram: Telethon (`TG_API_ID` / `TG_API_HASH`)
  - WeChat / Xiaohongshu: Jina fallback, optional Playwright session fallback
  - RSS: latest feed item
  - Generic web: Trafilatura / BeautifulSoup, optional Firecrawl fallback (`FIRECRAWL_API_KEY`)
- Output:
  - Structured JSON (`DataPulseItem`)
  - Optional Markdown output (`datapulse-inbox.md` / custom path)
- Scoring:
  - parser reliability + content/title/metadata features, bounded to [0.01, 0.99]
- Resilience:
  - unified parse result handling
  - concurrent batch read (`read_batch`)
  - dedupe and prune by max items / retention days

## Install

```bash
pip install -e .
pip install -e ".[all]"   # enable all optional capabilities
```

Optional groups:

- `.[trafilatura]`, `.[youtube]`, `.[telegram]`, `.[browser]`, `.[mcp]`, `.[notebooklm]`

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

- MCP server (install with `.[mcp]`):

```bash
python -m datapulse.mcp_server
```

Exposed tools:

- `read_url(url, min_confidence=0.0)`
- `read_batch(urls, min_confidence=0.0)`
- `query_inbox(limit=20, min_confidence=0.0)`
- `detect_platform(url)`
- `health()`

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
- `DATAPULSE_SMOKE_*`
- `DATAPULSE_MIN_CONFIDENCE`

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
