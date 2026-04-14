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

## L9：中文原生采集桥接契约（2026-03-09）

- `L9.2` 已把中文原生采集增强收敛为 contract-first 路线，契约文档固定在 `docs/governance/datapulse-native-collector-bridge-contract.md`。
- 当前 shortlist 顺序固定为 `MediaCrawler -> wechat_spider -> weiboSpider -> GeneralNewsExtractor`；`TrendRadar / EasySpider / Crawlab / f2` 继续留在后续 trend 或 manual lane，不进入当前 bridge contract。
- sidecar 启用边界收敛为 `DATAPULSE_NATIVE_COLLECTOR_BRIDGE_CMD`、`DATAPULSE_NATIVE_COLLECTOR_BRIDGE_WORKDIR`、`DATAPULSE_NATIVE_COLLECTOR_BRIDGE_TIMEOUT_SECONDS`、`DATAPULSE_NATIVE_COLLECTOR_STATE_DIR`，并复用既有 `DATAPULSE_SESSION_DIR` 与 `session_path(...)` 约定。
- 所有 native 返回都必须先归一化到 `ParseResult`，并在 `extra["collector_provenance"]` 中写明 `collector_family / bridge_profile / transport / session_key / raw_source_type / fallback_policy`；在 source type 尚未正式入模前，只能通过 provenance 和 tags 暴露，不得偷渡成新的一级路由语义。
- 回退策略保持窄而真实：`wechat` 走 `native -> jina -> browser`，`xhs / MediaCrawler` 走 `native -> jina -> browser`，`weibo` 现走 `native -> jina`，`GeneralNewsExtractor` 现走 `extractor -> trafilatura -> BeautifulSoup -> Firecrawl -> Jina`。
- 因此 `L9.2` 的完成含义是“桥接契约已定稿”，不是“中文原生采集已落地”；后续实现切片顺序仍为 `L9.3 -> L9.4 -> L9.5 -> L9.6`。
- `L9.3` 现已在仓内落地 `datapulse/collectors/native_bridge.py`：当 `DATAPULSE_NATIVE_COLLECTOR_BRIDGE_CMD` 配置后，DataPulse 会以 subprocess JSON sidecar 方式优先尝试 `mediacrawler` profile，并把成功结果归一化到现有 `ParseResult`。
- `L9.4` 现已在仓内落地 `datapulse/collectors/wechat.py`：`WeChatCollector` 会在 `DATAPULSE_NATIVE_COLLECTOR_BRIDGE_CMD` 已配置且 `wechat` session 已就绪时优先尝试 `wechat_spider` profile，并在成功时保留 `native_sidecar` provenance。
- 当前全局 `native_bridge` 仍只前推 `XHS + Zhihu + Tieba + Douyin + Kuaishou` 这条 `MediaCrawler` lane；`wechat` 与 `weibo` 的 native 入口都保持在各自 collector 内部，避免把 `wechat_spider / weibo_spider` 扩成新的全局一级路由语义。
- `ParsePipeline` 已把 `native_bridge` 作为相关 URL 的优先 collector，但 bridge 不可用、返回 soft failure、或内容不足时，`xhs` 仍保持 `native -> jina -> browser`；`wechat` 现保持 `native -> jina -> browser`，并为 native/Jina/browser 三条路径都写入 `collector_provenance` 以保持执行路径可见。
- `L9.5` 现已在仓内落地 `datapulse/collectors/weibo.py`：Weibo URL 会进入 first-class `WeiboCollector`，优先尝试 `weibo_spider` profile，并在 native 未启用或失败时回退到 Jina，同时把 `source_type=weibo` 与 `collector_provenance` 归一化到稳定输出。
- `L9.6` 现已在仓内落地 `datapulse/collectors/generic.py`：`GenericCollector` 会在 `gne` 可用且正文看起来像中文新闻时优先尝试 `GeneralNewsExtractor` 风格抽取，并把 `bridge_profile / transport / fallback_policy` 归一化到 `extra["collector_provenance"]`；若 backend 不可用、正文过薄或不适配，链路仍回退到 `trafilatura -> BeautifulSoup -> Firecrawl -> Jina`。
- `L9.7` 现已在仓内落地 `datapulse/core/triage.py`、`datapulse/core/story.py` 与 `datapulse/reader.py`：triage 与 story surfaces 现在会投影 source-linked grounded claims 和 evidence spans；当前 grounding mode 已明确区分 `provided / heuristic / empty`，把 claim/evidence 关系带入既有治理面，而不是另起一套 claim store。
- `L9.8` 现已在仓内落地 `datapulse/core/story.py`、`datapulse/core/alerts.py` 与 `datapulse/reader.py`：digest、story export 与 alert escalation 现在都经过 operator-visible factuality gate，输出 `status / score / reasons / signals / operator_action`；当前 gate 仍是 deterministic trust boundary，不依赖外部 verifier backend。
- `L9.9` 现已在仓内落地 `datapulse/core/watchlist.py` 与 `datapulse/reader.py`：`WatchMission` 现在可持久化 `trend_inputs`，并固定标记为 `input_kind=trend_feed`、`usage_mode=watch_seed_only`，明确这些输入只是 mission/feed seed，不是 item-level evidence。
- `DataPulseReader.create_watch_from_trends(...)` 会把现有 `trending()` snapshot 归一化成 trend seed input 后再创建 watch；原有 `create_watch(...)` 也可直接接收结构化 `trend_inputs`，但 watch 的执行路径仍然走既有 query/search/URL collector 链路。
- watch 运行结果与 feed 输出现在会把 trend seed 上下文作为 `watch_seed_inputs / datapulse_context / trend_seed_summary` 暴露出来，并附带边界说明，避免把 trend feed 误读成对 URL collector 的替代。
- `L9.10` 现已在仓内落地 `docs/governance/datapulse-manual-acquisition-sidecar-contract.md`：`EasySpider / Crawlab / f2` 被明确固定在 `manual emergency acquisition lane`，不进入 `ParsePipeline`、`native bridge` shortlist 或 `.github/workflows/governance-loop-auto.yml`。
- `L9.10` 的 handoff 顺序固定为 `url_recollection -> manual_fact_item -> story_attachment_only`：能回到 canonical URL 的优先重新走现有 collector；只有证据会丢失时才允许以 `SourceType.MANUAL` / `collection_mode=manual_fact` 进入 repo-visible truth。
- manual lane 的 provenance 与 automated collector 分离：若手工采集产物进入仓内对象，应该写入 `extra["manual_acquisition_provenance"]`，而不是复用 `extra["collector_provenance"]` 去伪装成 native 或 generic collector。
- manual lane 的最小交接物固定为 `run manifest + raw export refs + operator curation note`；原始导出、下载媒体和外部 job state 应保留在 operator-controlled 路径或外部对象存储中，不直接耦合进 git 仓库。
- 基于同一份外部 Top10 事实，当前已经没有新的 collector/trend/manual-lane open slice 需求；唯一仍然 repo-relevant 的 reopen 方向，是把 `LangExtract / OpenFactVerification` 这类工具收敛成可选 backend contract 和 adapter，而不是继续扩 collector lane。

## L10：可选证据后端强化（2026-03-09）

- `L10` 的目标不是再开新 collector，而是把已经落地的 grounding/factuality surfaces 升级成 backend-ready extension point。
- `L10.1` 现已在仓内落地 `docs/governance/datapulse-evidence-backend-contract.md`：contract 固定 `build_item_grounding(...)` 与 `build_factuality_gate(...)` 两个 backend boundary，要求 opt-in invocation、deterministic fallback 优先、以及 operator-visible provenance。
- grounding backend 的默认边界已固定：若已有 `provided` claims 就不应静默改写；若 backend 不可用、超时、或输出无效，必须回退到当前 `heuristic / empty` 路径。
- factuality backend 的默认边界也已固定：当前 deterministic `status / score / reasons / signals / operator_action` 仍是 canonical delivery contract，backend verdict 只能以 additive 且 operator-visible 的方式进入治理面，不能静默放宽既有 gate。
- `L10.2` 应把 `LangExtract`-class 能力挂到现有 `build_item_grounding(...)` 边界后面，并在 backend 不可用时严格回退到当前 `provided / heuristic / empty` 路径。
- `L10.3` 应把 `OpenFactVerification`-class 能力挂到现有 `build_factuality_gate(...)` 边界后面，并保留当前 `status / score / reasons / signals / operator_action` 的 operator-visible contract。
- 因此下一次点火顺序已前推为 `L10.2 -> L10.3`，而不是重新打开任何已经完成的 `L9` collector slice。

## L19：Feed Bundle 与 Digest Delivery 加固波次（2026-03-29）

- 这轮不是重做来源目录、pack 或 digest。仓内已经有 `list_packs / install_pack / query_feed / build_json_feed / build_atom_feed / build_digest / emit_digest_package`。
- `follow-builders` 对本仓真正有价值的不是采集器更多，而是这条轻闭环：`curated pack/profile -> replayable feed bundle -> deterministic digest payload -> prompt-governed rendering -> route-backed delivery`。
- 当前差距已经收敛为 5 个窄缺口：
  - 缺可回放 `feed_bundle` artifact，无法把 `pack/profile/source_ids/run_window/stats/errors` 固化为后续摘要输入；
  - 缺 `prepare_digest_payload` 风格 contract，当前 `build_digest/emit_digest_package` 还没有形成单一 `content/config/prompts/stats/errors` 边界；
  - 缺 digest prompt pack 与本地 override 顺序；
  - 浏览器虽有 onboarding copy，但 CLI/MCP/GUI 还没有共享 `language/timezone/frequency/default_delivery` 这类 digest profile；
  - Telegram 与 report delivery 仍存在单次发送与 `3900` 字截断路径，缺 chunk、fallback 与显式 diagnostics。
- 这轮必须保持当前 lifecycle 不变：仍然是 `mission -> triage -> story -> report -> delivery`；`feed_bundle` 与 `prepare_digest_payload` 只是补输出与交付中台，不另起第二条产品线。
- `L19.2` 现已在仓内落地 [datapulse-feed-bundle-digest-delivery-contract.md](/Users/sunyifei/DataPulse/docs/governance/datapulse-feed-bundle-digest-delivery-contract.md)：
  - `feed_bundle.v1` 固定 replayable membership 边界为 `selection + window + items + stats + errors`，要求 pack 或 profile 输入最终都解析成 concrete `source_ids` 与 closed item set；
  - `prepare_digest_payload.v1` 固定 route-ready deterministic boundary 为 `content + config + prompts + stats + errors`，其中 `content` 必须保留 `feed_bundle + build_digest` 产物与当前 `emit_digest_package` 的 office-ready package 概念；
  - follow-up runtime 不得在 rendering 或 delivery 阶段重新 query feed 或 network data，`build_digest / emit_digest_package` 继续作为 additive anchors 保留。
- 仓内治理蓝图已把这轮提升为 `L19`：
  - `L19.1` 蓝图与点火图已落仓；
  - `L19.2` contract 已冻结；
  - `L19.3` 为当前 next slice：再冻结 prompt override 与 first-run profile/onboarding；
  - `L19.4` 补 Reader/CLI/MCP 导出与 payload runtime；
  - `L19.5` 补 Telegram chunk/fallback/diagnostics；
  - `L19.6` 再把同一组 noun 投到 GUI。

## L30：public-apis feed/news/location-context 候选筛选（2026-04-07）

- `L30.2` 的完成语义不是“新增一批 DataPulse 已发布来源”，而是把 `public-apis` handoff 里的 feed、news、location-context 候选筛成 repo-native governed seeds。
- 当前仓内 truth 已固定在 [intelligence_source_governance_contract.md](/Users/sunyifei/DataPulse/docs/intelligence_source_governance_contract.md) 的 `L30.2 Public-APIs Screening Baseline`：
  - `qualify`：`The Guardian Open Platform`、`GNews API`、`Geoapify Geocoding API`、`OpenCage Geocoding API`
  - `defer`：`NewsAPI`、`Associated Press API`、`MarketAux`、`LocationIQ`、`OpenWeatherMap`
  - `reject_current_slice`：`stormglass.io`
- 这批条目的共同边界已经固定：
  - 只作为 `watch/feed seed` 或 `location-context seed`
  - 默认仍按 `collection_mode=api`、`sensitivity=review_required` 处理
  - 不能因为进入 repo truth 就被解释成 item-level verified evidence 或 DataPulse 外部已发布 surface
- 这轮不把任何 `public-apis` 候选写进 builtin source defaults；若后续真的要落入 `SourceCatalog` 或 pack，必须由后续 slice 单独做 terms、operator-review、runtime admission 和 evidence boundary 收口。
- `The Guardian Open Platform` 是当前最强的 publisher-owned news seed；`GNews API` 作为 aggregator seed 补 discovery breadth，但不能替代验证。
- `Geoapify/OpenCage` 只解决地点归一化与上下文增强；`OpenWeatherMap` 和 `stormglass.io` 都不应被误写成当前 feed 主线，其中 `stormglass.io` 直接超出本 slice 的 intelligence context 需求。
- `Associated Press API` 与 `MarketAux` 继续保留在可追溯 defer 状态：前者卡在 licensed content / rights review，后者更接近 market-reference specialization，应等待更明确的 downstream need 再决定是否重开。

## L31：tradingview-mcp donor 技术信号 seed screening（2026-04-14）

- `L31.2` 的完成语义不是把 `tradingview-mcp` donor 变成 DataPulse 的新 published source，也不是把技术指标、回测或情绪信号写成 item evidence。
- 当前仓内 truth 已固定在 [intelligence_source_governance_contract.md](/Users/sunyifei/DataPulse/docs/intelligence_source_governance_contract.md) 的 `L31.2 Tradingview-Style Technical-Signal Seed Screening`：
  - `qualify`：`technical_regime_sidecar`、`market_quote_snapshot`
  - `qualify_context_only`：`strategy_robustness_backtest`、`sentiment_news_contra_sidecar`
  - `reject_current_slice`：`BUY/SELL` 结论、target price / entry-exit calls、portfolio / execution / auto-trading triggers、以及任何试图把 weak-signal sentiment / Reddit / RSS donor output 升格成 primary evidence truth 的路径
- 这批 donor 输入的共同边界已经固定：
  - 只能作为 `watchlist seed` 或 operator-visible `market context`
  - 默认仍按 `secondary + review_required` 的导入姿态处理；`strategy_robustness_backtest` 在当前仓里更接近 `manual_fact` 风格的解释性 context
  - 不会因为进入 repo truth 就变成 builtin `SourceCatalog` default、已发布 public surface，或 DataPulse 的 investor-facing judgment
- 当前最适合被 DataPulse 吸收的是 `technical_regime_sidecar + market_quote_snapshot` 这一类 watch formation context；它们帮助决定“值得看什么”，不帮助决定“应该买卖什么”。
- `strategy_robustness_backtest` 与 `sentiment_news_contra_sidecar` 可以保留为后续 `watchlist_market_context_sidecar` slice 的 operator context 素材，但在这一轮不能越界成自动决策或 item-level fact truth。
- 因此 `L31.2` 落地后，后续实现必须复用现有 `trend_inputs` 与 `watch_seed_only` 语义，而不是新开 trading object chain；如果未来真的要接 donor wrapper，也必须在后续 slice 里单独收口 local-only boundary。

## 与现网能力映射

| 目标 | 目前落地状态 | 下一步 |
|---|---|---|
| 来源归类与发现 | ✅ `resolve_source` + domain/pattern matching | ✅ v0.4.0: arXiv/HN 多平台域名扩展 |
| 订阅关系 | ✅ `subscribe/unsubscribe`、`list_subscriptions` | 后续: 增加批量订阅 API |
| 源组复用 | ✅ `install_pack` + `list_packs` | 后续: 导入清单 UI |
| 聚合输出 | ✅ `build_json_feed / build_rss_feed / build_atom_feed` + 测试覆盖 | ✅ v0.4.0: Atom 1.0 + Digest 构建器 |
| 摘要载荷 | 🚧 `build_digest / emit_digest_package` 已落地，且 `L19.2` 已冻结 `feed_bundle.v1 + prepare_digest_payload.v1` contract | 后续: `L19.3` prompt override / first-run profile；`L19.4` runtime export 与 payload emission |
| 运维安全 | ✅ 健康检查 + SSRF 防护 + 配置化路径 | ✅ v0.3.0: processed 状态管理 |
| 多维评分 | ✅ 四维度加权 + Source Authority Tiers | ✅ v0.4.0 完成 |
| Web 搜索 | ✅ 多源网关（Jina/Tavily）CLI/MCP | ✅ v0.5.0 完成 |
| 任务化 | 🚧 `WatchMission` 首版（CLI/Reader/MCP + due runner + daemon + richer alert sink + status page） | 后续: 自动重跑 / 故障恢复 / 聚合面板 |
| 处置化 | 🚧 `TriageQueue` 首版（state/note/action + duplicate explain + CLI/MCP/Console + digest gate） | 后续: keyboard workflow / reviewer SLA |
| 证据化 | 🚧 `Story Workspace` 首版（story cluster + evidence/timeline/conflict + CLI/MCP + persisted snapshot + console board + entity graph） | 后续: story merge / editor |
| 分发化 | 🚧 当前有效交付层为 `AlertEvent` + named routes + `build_json_feed / build_rss_feed / build_atom_feed` + `story_export` + `alert_route_health / ops_snapshot`；后续 digest/report push 需消费冻结后的 `prepare_digest_payload` | 后续: `L6.3` 明确订阅/回调 contract；`L19.5` 补 Telegram chunk/fallback 与 route-backed digest/report diagnostics |

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
- `L19.6` 的 GUI follow-up 应聚焦于 `feed_bundle` 浏览/触发、digest profile onboarding、prompt pack readiness、以及 route-backed digest/report diagnostics；这些都应投影同一 Reader noun，而不是新增 GUI-only digest composer。
- `G0/G3` 壳层已落地，且已补入 `mission detail + result stream + result filter chips + timeline strip + alert rule editor` 与 `route health` 首版：`FastAPI` + `datapulse-console` + `/api/overview` / `/api/watches` / `/api/watches/{id}` / `/api/watches/{id}/results` / `/api/watches/{id}/alert-rules` / `/api/alerts` / `/api/alert-routes` / `/api/alert-routes/health` / `/api/watch-status` / `/api/triage` / `/api/triage/{id}/explain` / `/api/stories` / `/api/stories/{id}` / `/api/stories/{id}/graph` / `/api/stories/{id}/export`。
- console 启动入口已补齐：`datapulse-console`、`python -m datapulse.console_server` 与 `scripts/datapulse_console.sh`；仓内附带 `scripts/datapulse_console_smoke.sh` 做入口烟测。
- `P8` backend 与首版 GUI story board 已打通，当前已补入 story-aware entity graph 和基础 story editor；更深的编辑能力后续再补。
- GUI 增量应随仓内提交进入 GitHub Actions，至少通过 `ruff` / `mypy` / `pytest` 与 `datapulse-console --help` 烟测。
- 详细方案见 [gui_intelligence_console_plan.md](/Users/sunyifei/DataPulse/docs/gui_intelligence_console_plan.md)。
