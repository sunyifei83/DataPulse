# DataPulse Intelligence Hub

本地优先的公开来源情报采集、处置、证据化、报告交付与治理底座，面向 CLI / MCP / Skill / Agent 工作流。

<p align="center">
  <img src="./docs/assets/datapulse-command-chamber-hero.jpg" alt="DataPulse Command Chamber key visual" width="960">
</p>

<p align="center">
  <strong>DataPulse Command Chamber</strong><br>
  以钢蓝指挥舱、红色约束环和中央证据球为主视觉的本地优先情报操作面。
</p>

- 中文文档：[`README_CN.md`](./README_CN.md)
- English docs: [`README_EN.md`](./README_EN.md)
- 品牌基线：[`docs/brand_identity.md`](./docs/brand_identity.md)
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

## 升维判断与蓝图落地

| 维度 | 当前判断 |
| --- | --- |
| 仓库定位 | DataPulse 已从“多平台解析器集合”演进为本地优先的公开来源情报操作面，主链路是 `collection -> mission -> triage -> story -> report -> delivery -> governance`。 |
| 已形成闭环 | 公开来源采集、搜索、watch/triage/story、alert/route、ops scorecard、browser console、source/lifecycle/delivery governance 已在仓内形成可运行闭环。 |
| 正在收敛 | report objects、normalized delivery subscription、report package/dispatch、governed AI surfaces 已进入 Reader / CLI / MCP 运行面，但仍按治理契约逐层收口，而不是伪装成“全自动研究代理”。 |
| 当前蓝图态 | 当前结构化蓝图已完成至 `L30.3`（其中 `L29` wave 已完成至 `L29.6`）；`recommended_next_slice=no-open-slice`，直到出现新的 blueprint wave 或 admissible reopen evidence。 |
| 明确边界 | 本仓不是付费数据库采购系统、线下访谈系统、ERP/CRM 情报中台，也不对抓取合法性做自动法律判断。 |
| 当前证明面 | canonical roots 为 `artifacts/governance/snapshots/`、`artifacts/governance/release_bundle/` 与 `config/modelbus/datapulse/`；legacy `out/ha_latest_release_bundle/` 仅保留兼容读取，其中 `project_specific_loop_state.draft.json`、`code_landing_status.draft.json`、`release_status.json`、`datapulse-ai-surface-admission.example.json` 分别沉淀 loop/runtime、代码落地、发布状态与 AI surface admission 真相。 |

## 当前能力（按仓内实现）

| 能力域 | 当前支持 |
| --- | --- |
| 平台采集 | `twitter/x`、`reddit`、`youtube`、`bilibili`、`telegram`、`wechat`、`xhs`、`rss`、`arxiv`、`hackernews`、`generic web` |
| 热点趋势 | `trending`（X/Twitter 趋势页抓取） |
| 搜索 | `Jina` / `Tavily` / `auto` / `multi`，支持 `--platform`、`--site`、时间窗参数 |
| 任务化 | 首版 watch mission：`--watch-create`、`--watch-list`、`--watch-alert-set`、`--watch-alert-clear`、`--watch-show`、`--watch-results`、`--watch-run`、`--watch-run-due`、`--watch-daemon`、`--watch-status`，其中 `--watch-show` 已含最近失败重试建议 |
| 处置化 | 首版 triage queue：`--triage-list`、`--triage-explain`、`--triage-update`、`--triage-note`、`--triage-stats` |
| 证据化 | 首版 story workspace：`--story-build`、`--story-list`、`--story-show`、`--story-update`、`--story-graph`、`--story-export` |
| 告警分发 | threshold alert rule、关键词/标签/域名/时效过滤、JSON/Markdown/Webhook/Feishu/Telegram sink、`--alert-list`、`--alert-route-list`、`--alert-route-health` |
| 运行状态 | daemon 单实例锁、heartbeat JSON/HTML 状态页、MCP `watch_status`、CLI `--ops-overview`、任务级 watch health / aggregate success-rate / intelligence governance scorecard |
| 浏览器控制台 | `datapulse-console` 本地 G0/G3 GUI，统一 watch / triage / story / alert / route / status 工作台，`Mission Cockpit` 已具备 result stream、filter chips、timeline strip 和基础 alert rule 编辑，`Triage Queue` 已具备 first-cut keyboard workflow，`Story Workspace` 已具备基础 story editor |
| 报告生产 | `--report-object` + `--report-list/create/update/compose/quality/export`，围绕 `ReportBrief / ClaimCard / ReportSection / Report / ExportProfile` 组织研究产物 |
| 角色化交付 | `--delivery-subscription-*`、`--delivery-package`、`--delivery-dispatch`，支持 `profile / watch_mission / story / report` subject kind 的 normalized delivery subscription |
| 治理式 AI | `--ai-surface-precheck`、`--ai-mission-suggest`、`--ai-triage-assist`、`--ai-claim-draft`、`--ai-report-draft`、`--ai-delivery-summary`；当前 `report_draft` 仍按 admission contract 故意 fail-closed |
| 情报治理 | `MissionIntent`、`SourceGovernance`、生命周期/分发/来源治理契约、`commercial_intelligence_governance_blueprint`、coverage/freshness/alert yield/triage throughput/story conversion scorecard |
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
datapulse --watch-show ai-radar
datapulse --watch-results ai-radar
datapulse --watch-run ai-radar

# 按调度执行到期 watch mission
datapulse --watch-create --watch-name "Infra Radar" --watch-query "LLM inference infra" --watch-schedule @hourly
datapulse --watch-run-due

# 配置 threshold alert rule 并查看告警
datapulse --watch-create --watch-name "Launch Radar" --watch-query "OpenAI launch" --watch-alert-min-score 70 --watch-alert-channel markdown
datapulse --alert-list

# richer alert rule + 命名 route
datapulse --watch-create --watch-name "Launch Ops" --watch-query "OpenAI launch" --watch-alert-route ops-webhook --watch-alert-keyword launch --watch-alert-domain openai.com
datapulse --watch-alert-set launch-ops --watch-alert-route ops-webhook --watch-alert-keyword launch --watch-alert-domain openai.com --watch-alert-min-score 70
datapulse --watch-alert-clear launch-ops
datapulse --alert-route-list
datapulse --alert-route-health

# 启动 daemon 单轮执行
datapulse --watch-daemon --watch-daemon-once

# 查看 daemon 心跳与指标
datapulse --watch-status

# 启动浏览器控制台（仓内直接运行）
bash scripts/datapulse_console.sh --port 8765

# 或使用模块入口
uv run python -m datapulse.console_server --port 8765

# 若已安装 console 入口到 PATH
datapulse-console --port 8765

# 查看 triage 队列并确认高价值条目
datapulse --triage-list
datapulse --triage-explain item-123
datapulse --triage-update item-123 --triage-state verified --triage-note-text "confirmed by analyst"

# 构建并查看 story workspace
datapulse --story-build
datapulse --story-list
datapulse --story-show story-openai-launch
datapulse --story-update story-openai-launch --story-title "OpenAI Launch Watch" --story-status monitoring
datapulse --story-graph story-openai-launch

```

### 4) 启动浏览器控制台

```bash
# 仓内直接运行（推荐，不依赖 PATH）
bash scripts/datapulse_console.sh --port 8765

# 模块入口
uv run python -m datapulse.console_server --port 8765

# 若需要全局命令，先安装 console 依赖
uv pip install -e ".[console]"
datapulse-console --port 8765

# 控制台入口 smoke
bash scripts/datapulse_console_smoke.sh
```

说明：本机 `python3` 可能仍指向 `3.9`。仓内脚本会优先选择 `uv run python` 或 `python3.10+`，并在直接使用过低版本时给出明确报错，而不是在导入阶段抛出隐晦异常。

![DataPulse Console Preview](docs/datapulse_console.png)

参数填写说明见：[docs/datapulse_console_parameter_guide.md](docs/datapulse_console_parameter_guide.md)

### 5) 查看落库结果

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
| 调整任务告警规则 | `datapulse --watch-alert-set <watch_id> --watch-alert-route ops-webhook --watch-alert-keyword launch` |
| 清空任务告警规则 | `datapulse --watch-alert-clear <watch_id>` |
| 查看任务驾驶舱（含失败重试建议） | `datapulse --watch-show ai-radar` |
| 查看任务结果流 | `datapulse --watch-results ai-radar` |
| 按调度执行任务 | `datapulse --watch-run-due` |
| 查看告警事件 | `datapulse --alert-list` |
| 查看告警路由 | `datapulse --alert-route-list` |
| 查看路由健康 | `datapulse --alert-route-health` |
| 查看统一运维总览 | `datapulse --ops-overview` |
| daemon 调度轮询 | `datapulse --watch-daemon --watch-daemon-once` |
| daemon 状态快照 | `datapulse --watch-status` |
| triage 队列 | `datapulse --triage-list` |
| triage 重复项解释 | `datapulse --triage-explain <item_id>` |
| triage 状态更新 | `datapulse --triage-update <item_id> --triage-state verified` |
| story 构建 | `datapulse --story-build` |
| story 查看/编辑/导出 | `datapulse --story-show <story_id>` / `datapulse --story-update <story_id>` / `datapulse --story-export <story_id>` |
| 报告装配 / 质检 / 导出 | `datapulse --report-object report --report-compose <report_id>` / `datapulse --report-quality <report_id>` / `datapulse --report-export <report_id>` |
| 交付订阅 / 派发 | `datapulse --delivery-subscription-list` / `datapulse --delivery-package <subscription_id>` / `datapulse --delivery-dispatch <subscription_id>` |
| AI surface 预检 / 投影 | `datapulse --ai-surface-precheck claim_draft` / `datapulse --ai-mission-suggest <watch_id>` / `datapulse --ai-delivery-summary <alert_id>` |
| 浏览器控制台 | `datapulse-console --port 8765`（含 Story Workspace 证据板与基础 story editor） |
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
uv run python -m datapulse.mcp_server
uv run python -m datapulse.mcp_server --list-tools
uv run python -m datapulse.mcp_server --call health
```

常用工具已覆盖采集、mission、triage、story、report、delivery 与治理式 AI。代表性工具包括：`read_url`、`search_web`、`create_watch`、`watch_show`、`triage_explain`、`story_export`、`compose_report`、`export_report`、`list_delivery_subscriptions`、`dispatch_report_delivery`、`ai_surface_precheck`、`ai_mission_suggest`、`ai_delivery_summary`、`doctor`。

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
- `DATAPULSE_STORIES_PATH`
- `DATAPULSE_REPORTS_PATH`

## 开发与入库

- 蓝图计划内的代码变更应按逻辑单元提交入库，不长期停留在脏工作区。
- 推送到 GitHub 后应触发 Actions，当前默认闸门包括 `ruff check datapulse/`、`mypy datapulse/`、`pytest tests/`。
- GUI/G0 相关变更额外通过 `datapulse-console --help` 入口烟测，确保 console 包装和依赖在 CI 中可安装。
- 当前仓内证明面以 `artifacts/governance/snapshots/`、`artifacts/governance/release_bundle/` 与 `config/modelbus/datapulse/` 为准；`out/ha_latest_release_bundle/` 仅作为兼容读取入口，不应再作为唯一 canonical source。

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
- 生命周期契约：[`docs/intelligence_lifecycle_contract.md`](./docs/intelligence_lifecycle_contract.md)
- 来源治理契约：[`docs/intelligence_source_governance_contract.md`](./docs/intelligence_source_governance_contract.md)
- 分发契约：[`docs/intelligence_delivery_contract.md`](./docs/intelligence_delivery_contract.md)
- 商业情报治理蓝图：[`docs/commercial_intelligence_governance_blueprint.md`](./docs/commercial_intelligence_governance_blueprint.md)
- 当前 canonical 证明根：
  - [`artifacts/governance/snapshots/`](./artifacts/governance/snapshots/)
  - [`artifacts/governance/release_bundle/`](./artifacts/governance/release_bundle/)
  - [`config/modelbus/datapulse/`](./config/modelbus/datapulse/)
- 验收模板：[`docs/openclaw_datapulse_acceptance_template.md`](./docs/openclaw_datapulse_acceptance_template.md)
- 事实沉淀：[`docs/test_facts.md`](./docs/test_facts.md)
- 发布清单：[`docs/release_checklist.md`](./docs/release_checklist.md)

## License

DataPulse Non-Commercial License v1.0（见根目录 `LICENSE`）。
