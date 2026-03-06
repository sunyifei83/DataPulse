# DataPulse Intelligence Hub

跨平台内容采集与事实筛选工具，面向 CLI / MCP / Skill / Agent 工作流。

- 中文文档：[`README_CN.md`](./README_CN.md)
- English docs: [`README_EN.md`](./README_EN.md)
- 许可证：`DataPulse Non-Commercial License v1.0`

## 这是什么

DataPulse 提供一个统一入口，用于：

1. 读取 URL（社媒、论文、RSS、通用网页等）
2. 结构化抽取并评分（置信度 + 综合分）
3. 写入本地 inbox，支持后续查询、摘要、分发

适用场景：

- 热点追踪与信号归档
- Bot/Agent 的“先采集、后推理”前置层
- 多平台内容的标准化落库

## 当前能力（按仓内实现）

| 能力域 | 当前支持 |
| --- | --- |
| 平台采集 | `twitter/x`、`reddit`、`youtube`、`bilibili`、`telegram`、`wechat`、`xhs`、`rss`、`arxiv`、`hackernews`、`generic web` |
| 热点趋势 | `trending`（X/Twitter 趋势页抓取） |
| 搜索 | `Jina` / `Tavily` / `auto` / `multi`，支持 `--platform`、`--site`、时间窗参数 |
| 任务化 | 首版 watch mission：`--watch-create`、`--watch-list`、`--watch-run`、`--watch-run-due`、`--watch-daemon`、`--watch-status` |
| 处置化 | 首版 triage queue：`--triage-list`、`--triage-update`、`--triage-note`、`--triage-stats` |
| 告警分发 | threshold alert rule、关键词/标签/域名/时效过滤、JSON/Markdown/Webhook/Feishu/Telegram sink、`--alert-list`、`--alert-route-list` |
| 运行状态 | daemon 单实例锁、heartbeat JSON/HTML 状态页、MCP `watch_status` |
| 浏览器控制台 | `datapulse-console` 本地 G0 GUI，统一 watch / triage / alert / route / status 工作台 |
| 输出模型 | 统一 `DataPulseItem`（`title/content/url/confidence/score/tags/extra`） |
| 评分排序 | 置信度 + 权威度 + 互证 + 时效性 |
| 实体增强 | `--entities` 抽取，`--entity-query` / `--entity-graph` / `--entity-stats` |
| 摘要与分发 | `build_digest`、JSON/RSS/Atom feed、digest package |
| 生态接入 | CLI、MCP Server、`datapulse_skill`、`DataPulseAgent` |
| 诊断运维 | `--config-check`、`--doctor`、`--troubleshoot`、`--check-update`、`--self-update` |

## 1 分钟上手

### 1) 安装

```bash
# 推荐
uv pip install -e .

# 或
pip install -e .
```

可选能力：

```bash
pip install -e ".[all]"
# 或按需安装：.[console] / .[telegram] / .[browser] / .[mcp] / .[youtube] ...
```

### 2) 环境自检

```bash
datapulse --config-check
datapulse --doctor
```

### 3) 跑第一个任务

```bash
# 读取单条链接
datapulse https://www.reddit.com/r/dataengineering/comments/1rg6fjo/which_data_quality_tool_do_you_use/

# 搜索
datapulse --search "data governance" --search-limit 5

# 趋势
datapulse --trending us --trending-limit 10

# 保存并运行 watch mission
datapulse --watch-create --watch-name "AI Radar" --watch-query "OpenAI agents" --watch-platform twitter
datapulse --watch-run ai-radar

# 按调度执行到期 watch mission
datapulse --watch-create --watch-name "Infra Radar" --watch-query "LLM inference infra" --watch-schedule @hourly
datapulse --watch-run-due

# 配置 threshold alert rule 并查看告警
datapulse --watch-create --watch-name "Launch Radar" --watch-query "OpenAI launch" --watch-alert-min-score 70 --watch-alert-channel markdown
datapulse --alert-list

# richer alert rule + 命名 route
datapulse --watch-create --watch-name "Launch Ops" --watch-query "OpenAI launch" --watch-alert-route ops-webhook --watch-alert-keyword launch --watch-alert-domain openai.com
datapulse --alert-route-list

# 启动 daemon 单轮执行
datapulse --watch-daemon --watch-daemon-once

# 查看 daemon 心跳与指标
datapulse --watch-status

# 查看 triage 队列并确认高价值条目
datapulse --triage-list
datapulse --triage-update item-123 --triage-state verified --triage-note-text "confirmed by analyst"

# 启动浏览器控制台（G0）
datapulse-console --port 8765
```

### 4) 查看落库结果

```bash
datapulse --list --limit 10
```

## 命令速查

| 场景 | 命令 |
| --- | --- |
| 单条解析 | `datapulse <url>` |
| 批量解析 | `datapulse --batch <url1> <url2> ...` |
| 平台限定搜索 | `datapulse --search "关键词" --platform reddit --search-limit 10` |
| 指定 provider | `datapulse --search "关键词" --search-provider tavily` |
| 指定时间窗 | `datapulse --search "关键词" --search-freshness week` |
| 趋势抓取 | `datapulse --trending [us|uk|jp|...] --trending-limit 20` |
| 持续主题跟踪 | `datapulse --watch-create --watch-name "AI Radar" --watch-query "OpenAI agents"` |
| 按调度执行任务 | `datapulse --watch-run-due` |
| 查看告警事件 | `datapulse --alert-list` |
| 查看告警路由 | `datapulse --alert-route-list` |
| daemon 调度轮询 | `datapulse --watch-daemon --watch-daemon-once` |
| daemon 状态快照 | `datapulse --watch-status` |
| triage 队列 | `datapulse --triage-list` |
| triage 状态更新 | `datapulse --triage-update <item_id> --triage-state verified` |
| 浏览器控制台 | `datapulse-console --port 8765` |
| 实体抽取 | `datapulse <url> --entities --entity-mode fast` |
| 查询实体 | `datapulse --entity-query OPENAI --entity-limit 20` |
| 生成摘要 | `datapulse --digest --top-n 3 --secondary-n 7` |
| 导出摘要包 | `datapulse --emit-digest-package --emit-digest-format markdown` |
| 健康检查 | `datapulse --doctor` |
| 故障建议 | `datapulse --troubleshoot` / `datapulse --troubleshoot twitter` |
| smoke 回归 | `datapulse-smoke --list` / `datapulse-smoke --platforms reddit twitter` |

## MCP / Skill / Agent

### MCP Server

```bash
python -m datapulse.mcp_server
python -m datapulse.mcp_server --list-tools
python -m datapulse.mcp_server --call health
```

常用工具：`read_url`、`read_batch`、`search_web`、`create_watch`、`list_watches`、`run_watch`、`run_due_watches`、`triage_list`、`triage_update`、`triage_note`、`triage_stats`、`list_alerts`、`list_alert_routes`、`watch_status`、`trending`、`query_inbox`、`build_digest`、`doctor`。

### Skill 调用

```python
from datapulse_skill import run
run("请处理这些链接: https://x.com/... https://www.reddit.com/...")
```

### Agent 调用

```python
from datapulse.agent import DataPulseAgent

agent = DataPulseAgent(min_confidence=0.25)
result = await agent.handle("https://x.com/... and https://www.reddit.com/...")
```

## 常用环境变量

最常见：

- `JINA_API_KEY`：Jina 搜索/读取增强
- `TAVILY_API_KEY`：Tavily 搜索
- `TG_API_ID` / `TG_API_HASH`：Telegram
- `GROQ_API_KEY`：YouTube 音频转写兜底

运行参数：

- `DATAPULSE_MIN_CONFIDENCE`
- `DATAPULSE_BATCH_CONCURRENCY`
- `DATAPULSE_MEMORY_DIR`
- `DATAPULSE_KEEP_DAYS`
- `DATAPULSE_MAX_INBOX`
- `DATAPULSE_LOG_LEVEL`
- `DATAPULSE_WATCHLIST_PATH`
- `DATAPULSE_ALERTS_PATH`
- `DATAPULSE_ALERTS_MARKDOWN_PATH`
- `DATAPULSE_ALERT_ROUTING_PATH`
- `DATAPULSE_ALERT_WEBHOOK_URL`
- `DATAPULSE_FEISHU_WEBHOOK_URL`
- `DATAPULSE_TELEGRAM_BOT_TOKEN`
- `DATAPULSE_TELEGRAM_CHAT_ID`
- `DATAPULSE_WATCH_DAEMON_LOCK`
- `DATAPULSE_WATCH_STATUS_PATH`
- `DATAPULSE_WATCH_STATUS_HTML`

## 开发与入库

- 蓝图计划内的代码变更应按逻辑单元提交入库，不长期停留在脏工作区。
- 推送到 GitHub 后应触发 Actions，当前默认闸门包括 `ruff check datapulse/`、`mypy datapulse/`、`pytest tests/`。
- GUI/G0 相关变更额外通过 `datapulse-console --help` 入口烟测，确保 console 包装和依赖在 CI 中可安装。

## 安全与边界

- 请勿将密钥提交到仓库（使用运行时环境注入）。
- 本地调试建议使用 `.env.openclaw.local`，保持脱敏模板 `.env.openclaw.example`。
- 提交前可运行：

```bash
bash scripts/security_guardrails.sh
```

## 推荐阅读

- 详细中文说明：[`README_CN.md`](./README_CN.md)
- Detailed English guide: [`README_EN.md`](./README_EN.md)
- 搜索网关配置：[`docs/search_gateway_config.md`](./docs/search_gateway_config.md)
- 验收模板：[`docs/openclaw_datapulse_acceptance_template.md`](./docs/openclaw_datapulse_acceptance_template.md)
- 事实沉淀：[`docs/test_facts.md`](./docs/test_facts.md)
- 发布清单：[`docs/release_checklist.md`](./docs/release_checklist.md)

## License

DataPulse Non-Commercial License v1.0（见根目录 `LICENSE`）。
