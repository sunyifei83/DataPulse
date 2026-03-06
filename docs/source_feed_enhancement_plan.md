# 数据源与订阅化增强计划（对标公开方案能力）

## 目标
建立 DataPulse 内部统一来源目录与订阅化输出来承接 OpenClaw 联接场景：稳定识别来源、可控订阅范围、可消费 Feed。

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

### P6：Watch / Mission 任务层 🚧 (v0.7.0 进行中)
- 新增任务对象模型：`WatchMission` / `MissionRun` / `WatchlistStore`。
- 新增轻量调度语义：`@hourly` / `@daily` / `@weekly` / `interval:15m`。
- 新增首版阈值告警：`alert_rules` + 关键词 / 标签 / 域名 / source_type / 时效过滤。
- 新增命名 route：`DATAPULSE_ALERT_ROUTING_PATH` + `list_alert_routes`。
- 新增分发落点：JSON / Markdown / Webhook / 飞书 / Telegram。
- `DataPulseReader` 支持 `create_watch / list_watches / run_watch / disable_watch`。
- `DataPulseReader` 支持 `run_due_watches` 执行当前到期任务。
- `DataPulseReader` 支持 `run_watch_daemon`，带单实例锁。
- `DataPulseReader` 支持 `watch_status_snapshot` 输出 daemon 心跳、指标与最近错误。
- CLI 支持 `--watch-create / --watch-list / --watch-run / --watch-run-due / --watch-daemon / --watch-status / --alert-list / --alert-route-list / --watch-disable`。
- MCP 首版开放：`create_watch / list_watches / run_watch / run_due_watches / list_alerts / list_alert_routes / watch_status / disable_watch`。
- 当前范围为“保存搜索 + 手动执行 + 轻量 due runner + daemon 轮询 + richer alert rule + named routing + 状态页”；自动恢复与更复杂编排留待下一阶段。

### P7：Triage Queue 处置层 🚧 (v0.8.0 进行中)
- 新增 triage 状态模型：`new / triaged / verified / duplicate / ignored / escalated`。
- `DataPulseItem` 新增 `review_state / review_notes / review_actions / duplicate_of`，保持旧 inbox JSON 向后兼容。
- 新增 `core/triage.py`，统一状态校验、备注记录、动作日志、队列统计。
- `DataPulseReader` 支持 `triage_list / triage_update / triage_note / triage_stats`。
- CLI 支持 `--triage-list / --triage-update / --triage-note / --triage-stats`。
- MCP 新增：`triage_list / triage_update / triage_note / triage_stats`。
- Digest 现在默认排除 `duplicate / ignored`，`verified` 状态进入评分链路获得稳定加权。
- `datapulse-console` 已在 G0 壳层中加入 triage queue 面板与状态更新入口。

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
| 处置化 | 🚧 `TriageQueue` 首版（state/note/action + CLI/MCP/Console + digest gate） | 后续: duplicate explain / keyboard workflow / reviewer SLA |

## 验收建议（本项目）

- `datapulse --list-sources`、`--list-packs`、`--resolve-source` 基本通过。
- `datapulse --query-feed` 与 `--query-rss` 可生成可读 Feed。
- `datapulse --watch-create`、`--watch-list`、`--watch-run`、`--watch-disable` 可完成首版任务闭环。
- `datapulse --watch-run-due` 可执行所有到期任务。
- `datapulse --watch-daemon --watch-daemon-once` 可执行单轮 daemon 周期并受锁保护。
- `datapulse --watch-status` 可查看 daemon 心跳、指标与最近错误。
- `datapulse --alert-list` 可查看阈值告警落库结果。
- `datapulse --alert-route-list` 可审计命名路由配置。
- `datapulse --triage-list / --triage-update / --triage-note / --triage-stats` 可完成首版处置闭环。
- MCP 包含新增工具：`resolve_source/list_sources/list_packs/query_feed/build_json_feed/build_rss_feed/create_watch/list_watches/run_watch/run_due_watches/triage_list/triage_update/triage_note/triage_stats/list_alerts/list_alert_routes/watch_status/disable_watch`。
- 远端 OpenClaw 入口可通过 `read_url/read_batch` 与 feed 查询联调。

## 横向蓝图：GUI Intelligence Console

- GUI 已进入合理建设窗口，但不应独立于领域模型先行。
- 推荐顺序：先补 HTTP API 适配层，再做本地单用户浏览器控制台。
- 第一阶段只承接当前 `P6`：watch、alerts、routes、status。
- `G0` 壳层已落地：`FastAPI` + `datapulse-console` + `/api/overview` / `/api/watches` / `/api/alerts` / `/api/alert-routes` / `/api/watch-status` / `/api/triage`。
- GUI 增量应随仓内提交进入 GitHub Actions，至少通过 `ruff` / `mypy` / `pytest` 与 `datapulse-console --help` 烟测。
- 详细方案见 [gui_intelligence_console_plan.md](/Users/sunyifei/DataPulse/docs/gui_intelligence_console_plan.md)。
