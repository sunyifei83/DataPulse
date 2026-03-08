# 数据源与订阅化增强计划（对标公开方案能力）

## 目标
建立 DataPulse 内部统一来源目录与订阅化输出来承接 OpenClaw 联接场景：稳定识别来源、可控订阅范围、可消费 Feed。

## 生命周期投影（L6.2）

- 本文档现在按 [intelligence_lifecycle_contract.md](/Users/sunyifei/DataPulse/docs/intelligence_lifecycle_contract.md) 解释现有路线，而不再把 feed、watch、triage、story 视为互相脱节的能力块。
- 统一链路以 `WatchMission -> MissionRun -> DataPulseItem(review/triage) -> Story/evidence package -> AlertEvent/route delivery/story export` 为准。
- `P6` 负责 mission intent 与 run execution，`P7` 负责 triage state/note/action，`P8` 负责 evidence package；当前 delivery/output 面则由 `AlertEvent`、named routes、`build_json_feed / build_rss_feed / build_atom_feed`、`story_export(...)`、`alert_route_health()`、`ops_snapshot()` 共同构成。
- 当前 feed/digest/story export 都应视为同一 lifecycle 的下游输出，而不是独立于任务、处置、证据之外的第二条产品线。
- 更丰富的订阅、回调、角色化输出 contract 仍属于后续 `L6.3`，本轮只把现有 repo 事实投影回本路线图。

## 里程碑

### P0：来源目录 ✅ (v0.2.0 完成)
- 提供 `DATAPULSE_SOURCE_CATALOG` 驱动的本地源清单。
- 支持 `list_sources / resolve_source / subscribe / unsubscribe / install_pack`。
- 支持来源类型与配置自动映射（含 RSS/网站 URL 识别）。
- 完整测试覆盖（`tests/test_source_catalog.py`，20+ 测试用例）。

### P1：聚合交付 ✅ (v0.2.0 完成)
- 提供 JSON Feed 与 RSS 风格输出（`build_json_feed` / `build_rss_feed`）。
- 在 `Reader` 和 `MCP` 上提供查询/构建入口。
- 在 smoke 脚本中加入源目录与 feed 自检。
- Feed 生成测试覆盖（`tests/test_reader.py`）。

### P2：安全与反馈 ✅ (v0.3.0 完成)
- 补充标记/状态化反馈数据结构（pending / processed）：`mark_processed()` / `query_unprocessed()` on `UnifiedInbox`、`DataPulseReader`、MCP 工具。
- 为关键写操作增加环境变量开关与鉴权策略。

### P3：多维评分与 Digest ✅ (v0.4.0 完成)
- 四维度加权评分引擎（confidence/authority/corroboration/recency）。
- Source Authority Tiers：`SourceRecord` 新增 `tier` 与 `authority_weight`。
- Digest 构建器：primary/secondary 故事、指纹去重、多样性选择。
- arXiv / Hacker News 采集器。
- Atom 1.0 Feed 输出。

### P4：Jina 增强读取与 Web 搜索 ✅ (v0.5.0 完成)
- Jina API 客户端统一封装（Reader + Search）。
- CSS 选择器定向抓取、等待元素、缓存控制、AI 图片描述。
- Web 搜索能力：`DataPulseReader.search()` + CLI `--search` + MCP `search_web`（默认多源网关：Jina/Tavily）。
- Generic Collector Jina 兜底回退链。

### P5：可靠性与诊断增强 ✅ (v0.6.1 完成)
- 采集器健康自检（doctor）：`BaseCollector.check()` + tier/setup_hint，`ParsePipeline.doctor()` 聚合，CLI `--doctor`，MCP `doctor()` 工具。
- 可操作路由错误：`route()` 失败时附带 `setup_hint` 修复指引。
- 429 感知退避：`RateLimitError(retry_after=N)` + `CircuitBreaker.rate_limit_weight=2`。
- 入库指纹去重：`UnifiedInbox.add()` 对 ≥50 字符内容计算指纹拒绝近似重复。
- 平台三级分级体系：tier 0 (零配置) / tier 1 (网络) / tier 2 (需配置)。

### P6：Watch / Mission 任务层 🚧 (v0.8.0 首版闭环，后续增强继续)
- 新增任务对象模型：`WatchMission` / `MissionRun` / `WatchlistStore`。
- 新增轻量调度语义：`@hourly` / `@daily` / `@weekly` / `interval:15m`。
- 新增首版阈值告警：`alert_rules` + 关键词 / 标签 / 域名 / source_type / 时效过滤。
- 新增命名 route：`DATAPULSE_ALERT_ROUTING_PATH` + `list_alert_routes`。
- 新增分发落点：JSON / Markdown / Webhook / 飞书 / Telegram。
- `DataPulseReader` 支持 `create_watch / list_watches / run_watch / disable_watch`。
- `DataPulseReader` 支持 `run_due_watches` 执行当前到期任务。
- `DataPulseReader` 支持 `run_watch_daemon`，带单实例锁。
- `DataPulseReader` 支持 `watch_status_snapshot` 输出 daemon 心跳、指标与最近错误。
- CLI 支持 `--watch-create / --watch-list / --watch-alert-set / --watch-alert-clear / --watch-show / --watch-results / --watch-run / --watch-run-due / --watch-daemon / --watch-status / --alert-list / --alert-route-list / --alert-route-health / --watch-disable`。
- MCP 首版开放：`create_watch / list_watches / watch_show / watch_set_alert_rules / watch_results / run_watch / run_due_watches / list_alerts / list_alert_routes / alert_route_health / watch_status / disable_watch`。
- 当前范围为“保存搜索 + 手动执行 + 轻量 due runner + daemon 轮询 + richer alert rule + named routing + 状态页”；自动恢复与更复杂编排留待下一阶段。

### P7：Triage Queue 处置层 🚧 (v0.8.0 首版闭环，后续增强继续)
- 新增 triage 状态模型：`new / triaged / verified / duplicate / ignored / escalated`。
- `DataPulseItem` 新增 `review_state / review_notes / review_actions / duplicate_of`，保持旧 inbox JSON 向后兼容。
- 新增 `core/triage.py`，统一状态校验、备注记录、动作日志、队列统计，以及重复项解释能力。
- `DataPulseReader` 支持 `triage_list / triage_explain / triage_update / triage_note / triage_stats`。
- CLI 支持 `--triage-list / --triage-explain / --triage-update / --triage-note / --triage-stats`。
- MCP 新增：`triage_list / triage_explain / triage_update / triage_note / triage_stats`。
- Digest 现在默认排除 `duplicate / ignored`，`verified` 状态进入评分链路获得稳定加权。
- `datapulse-console` 已在 G0 壳层中加入 triage queue 面板、状态更新入口和 duplicate explain 视图。
- browser `Triage Queue` 已补入 state filter chips、review note history 与 inline note composer，并直接走 `/api/triage/{id}/state` / `/api/triage/{id}/note` 写回。
- browser `Triage Queue` 已补入 first-cut keyboard workflow：`J/K` 选择、`V/T/E/I` 状态流转、`D` 打开 duplicate explain、`N` 聚焦 note composer。

### P8：Story Workspace 证据层 🚧 (v0.8.0 首版闭环，后续增强继续)
- 新增 `core/story.py`，提供 `Story / StoryEvidence / StoryTimelineEvent / StoryConflict / StoryStore`。
- 新增首版 story 聚合构建器：基于标题/正文/实体/域名/指纹相似度聚类，生成主次证据、时间线、冲突提示与实体聚合。
- `DataPulseReader` 支持 `story_build / list_stories / show_story / export_story`。
- `DataPulseReader` 支持 `story_graph` 生成 story-aware entity graph。
- CLI 新增：`--story-build / --story-list / --story-show / --story-update / --story-graph / --story-export`。
- MCP 新增：`story_build / story_list / story_show / story_update / story_graph / story_export`。
- `datapulse-console` 已补入首版 story workspace：story 列表、证据栈、时间线、冲突标记、entity graph、Markdown 证据包预览，以及可回写 `title / summary / status` 的 story editor。
- 当前范围为“持久化 story snapshot + GUI story board + entity graph + 基础 story editor”；故事合并、证据重排留待下一阶段。

## 截至 2026-03-08 的落地事实

- `P6/G1` 已形成单任务 cockpit 闭环：`watch_show / watch_results / watch_set_alert_rules`，浏览器内可查看 `recent runs / recent results / recent alerts / retry advice`，并可直接替换或清空基础 alert rule。
- `P6/G1` 的浏览器 alert rule editor 已支持多规则编辑，不再只暴露第一条规则。
- `Mission Cockpit` 已具备 `result filter chips + timeline strip`，不再只是结果列表；同一块面板里可筛看最近结果并回放 run/result/alert 时间线。
- `P6/G4` 已具备统一运维快照：`ops_snapshot()`、CLI `--ops-overview`、MCP `ops_overview()`、浏览器状态面板对齐输出 `collector tiers / watch health / aggregate success-rate / route health`。
- `P6/G4` 已进一步补入 drill-down：collector remediation 明细、route mission/rule 计数、最近路由错误摘要已进入同一 ops 面板。
- 浏览器控制台已可独立启动和烟测：`datapulse-console`、`python -m datapulse.console_server`、`scripts/datapulse_console.sh`、`scripts/datapulse_console_smoke.sh`。
- `P7/P8` 的 first cut 已进入同一控制面：triage queue、duplicate explain、story board、entity graph、Markdown story export preview 都已在仓内交付，而非停留在蓝图。
- `P7/G2` 已从基础入口推进到可操作工作台：同屏支持 queue state filter chips、duplicate explain、state transitions、review note history 与 inline note composer。
- `P7/G2` 已进一步补入 first-cut keyboard workflow：`J/K` 选中条目、`V/T/E/I` 快捷处置、`D` 打开重复项解释、`N` 聚焦 note composer。
- `P8/G3` 已不再是只读板：单个 story 现在可在 CLI / MCP / Console 中回写 `title / summary / status`，浏览器内已补入 `story editor`。
- `L8` 治理收口已进入仓内事实：来源治理契约、商业情报治理蓝图、mission intent 语义、governance scorecard 均已在 repo 中落锚，不再只是外部方法论。

## 与现网能力映射

| 目标 | 目前落地状态 | 下一步 |
|---|---|---|
| 来源归类与发现 | ✅ `resolve_source` + domain/pattern matching | ✅ v0.4.0: arXiv/HN 多平台域名扩展 |
| 订阅关系 | ✅ `subscribe/unsubscribe`、`list_subscriptions` | 后续: 增加批量订阅 API |
| 源组复用 | ✅ `install_pack` + `list_packs` | 后续: 导入清单 UI |
| 聚合输出 | ✅ `build_json_feed / build_rss_feed / build_atom_feed` + 测试覆盖 | ✅ v0.4.0: Atom 1.0 + Digest 构建器 |
| 运维安全 | ✅ 健康检查 + SSRF 防护 + 配置化路径 | ✅ v0.3.0: processed 状态管理 |
| 多维评分 | ✅ 四维度加权 + Source Authority Tiers | ✅ v0.4.0 完成 |
| Web 搜索 | ✅ 多源网关（Jina/Tavily）CLI/MCP | ✅ v0.5.0 完成 |
| 任务化 | 🚧 `WatchMission` 首版（CLI/Reader/MCP + due runner + daemon + richer alert sink + status page） | 后续: 自动重跑 / 故障恢复 / 聚合面板 |
| 处置化 | 🚧 `TriageQueue` 首版（state/note/action + duplicate explain + CLI/MCP/Console + digest gate） | 后续: keyboard workflow / reviewer SLA |
| 证据化 | 🚧 `Story Workspace` 首版（story cluster + evidence/timeline/conflict + CLI/MCP + persisted snapshot + console board + entity graph） | 后续: story merge / editor |
| 分发化 | 🚧 当前有效交付层为 `AlertEvent` + named routes + `build_json_feed / build_rss_feed / build_atom_feed` + `story_export` + `alert_route_health / ops_snapshot` | 后续: `L6.3` 明确订阅/回调 contract，统一角色化 feed 与 route-backed 输出 |

## 验收建议（本项目）

- `datapulse --list-sources`、`--list-packs`、`--resolve-source` 基本通过。
- `datapulse --query-feed` 与 `--query-rss` 可生成可读 Feed。
- `datapulse --watch-create`、`--watch-list`、`--watch-run`、`--watch-disable` 可完成首版任务闭环。
- `datapulse --watch-show` 可查看单个任务的近期运行、近期结果流、近期告警，以及最近一次失败原因与重试建议。
- `datapulse --watch-alert-set / --watch-alert-clear` 可替换或清空单个任务的告警规则。
- `datapulse --watch-results` 可单独读取某个任务的持久化结果流。
- `datapulse --watch-run-due` 可执行所有到期任务。
- `datapulse --watch-daemon --watch-daemon-once` 可执行单轮 daemon 周期并受锁保护。
- `datapulse --watch-status` 可查看 daemon 心跳、指标与最近错误。
- `datapulse --alert-list` 可查看阈值告警落库结果。
- `datapulse --alert-route-list` 可审计命名路由配置。
- `datapulse --alert-route-health` 可查看命名路由的投递健康状态。
- `datapulse --triage-list / --triage-explain / --triage-update / --triage-note / --triage-stats` 可完成首版处置闭环。
- `datapulse --story-build / --story-list / --story-show / --story-update / --story-export` 可完成首版证据组织与基础编辑闭环。
- MCP 包含新增工具：`resolve_source/list_sources/list_packs/query_feed/build_json_feed/build_rss_feed/create_watch/list_watches/watch_show/watch_set_alert_rules/watch_results/run_watch/run_due_watches/triage_list/triage_explain/triage_update/triage_note/triage_stats/story_build/story_list/story_show/story_update/story_graph/story_export/list_alerts/list_alert_routes/alert_route_health/watch_status/disable_watch`。
- 远端 OpenClaw 入口可通过 `read_url/read_batch` 与 feed 查询联调。

## 横向蓝图：GUI Intelligence Console

- GUI 已进入合理建设窗口，但不应独立于领域模型先行。
- 推荐顺序：先补 HTTP API 适配层，再做本地单用户浏览器控制台。
- `G0/G1/G2/G3/G4` 应按同一 lifecycle 阅读：`mission -> run -> triage -> story -> delivery`；GUI 负责操作承载，不负责发明第二套对象语义。
- 当前浏览器控制台已承接 `P6 + P7 + P8 first cut`，并补入 `G1/G4` 控制面：watch、mission cockpit、result stream、result filter chips、timeline strip、retry advice、alert rule editor、alerts、routes、route health、watch health、status、triage、story board。
- `G2` 的 browser triage workspace 已从基础入口推进到可操作工作台：同屏支持 queue state filter chips、duplicate explain、state transitions、review note history、inline note composer，以及 first-cut keyboard workflow。
- `G3` 的 browser story workspace 已补入基础 story editor：同屏支持查看 evidence/timeline/graph，并直接回写 story title、summary 与 status。
- `G4` 现已补到任务级 watch health / aggregate success-rate board：后端 `ops_snapshot()`、CLI `--ops-overview`、MCP `ops_overview()` 与浏览器状态面板保持一致。
- `G4` 已继续补入 route delivery timeline：最近投递尝试、投递状态和错误摘要可在同一 ops 面板连续查看。
- `G0/G3` 壳层已落地，且已补入 `mission detail + result stream + result filter chips + timeline strip + alert rule editor` 与 `route health` 首版：`FastAPI` + `datapulse-console` + `/api/overview` / `/api/watches` / `/api/watches/{id}` / `/api/watches/{id}/results` / `/api/watches/{id}/alert-rules` / `/api/alerts` / `/api/alert-routes` / `/api/alert-routes/health` / `/api/watch-status` / `/api/triage` / `/api/triage/{id}/explain` / `/api/stories` / `/api/stories/{id}` / `/api/stories/{id}/graph` / `/api/stories/{id}/export`。
- console 启动入口已补齐：`datapulse-console`、`python -m datapulse.console_server` 与 `scripts/datapulse_console.sh`；仓内附带 `scripts/datapulse_console_smoke.sh` 做入口烟测。
- `P8` backend 与首版 GUI story board 已打通，当前已补入 story-aware entity graph 和基础 story editor；更深的编辑能力后续再补。
- GUI 增量应随仓内提交进入 GitHub Actions，至少通过 `ruff` / `mypy` / `pytest` 与 `datapulse-console --help` 烟测。
- 详细方案见 [gui_intelligence_console_plan.md](/Users/sunyifei/DataPulse/docs/gui_intelligence_console_plan.md)。
