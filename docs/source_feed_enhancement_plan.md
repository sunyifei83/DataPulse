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
- Web 搜索能力（`s.jina.ai`）：`DataPulseReader.search()` + CLI `--search` + MCP `search_web`。
- Generic Collector Jina 兜底回退链。

### P5：Agent-Reach 蒸馏 ✅ (v0.6.1 完成)
- 采集器健康自检（doctor）：`BaseCollector.check()` + tier/setup_hint，`ParsePipeline.doctor()` 聚合，CLI `--doctor`，MCP `doctor()` 工具。
- 可操作路由错误：`route()` 失败时附带 `setup_hint` 修复指引。
- 429 感知退避：`RateLimitError(retry_after=N)` + `CircuitBreaker.rate_limit_weight=2`。
- 入库指纹去重：`UnifiedInbox.add()` 对 ≥50 字符内容计算指纹拒绝近似重复。
- 平台三级分级体系：tier 0 (零配置) / tier 1 (网络) / tier 2 (需配置)。

## 与现网能力映射

| 目标 | 目前落地状态 | 下一步 |
|---|---|---|
| 来源归类与发现 | ✅ `resolve_source` + domain/pattern matching | ✅ v0.4.0: arXiv/HN 多平台域名扩展 |
| 订阅关系 | ✅ `subscribe/unsubscribe`、`list_subscriptions` | 后续: 增加批量订阅 API |
| 源组复用 | ✅ `install_pack` + `list_packs` | 后续: 导入清单 UI |
| 聚合输出 | ✅ `build_json_feed / build_rss_feed / build_atom_feed` + 测试覆盖 | ✅ v0.4.0: Atom 1.0 + Digest 构建器 |
| 运维安全 | ✅ 健康检查 + SSRF 防护 + 配置化路径 | ✅ v0.3.0: processed 状态管理 |
| 多维评分 | ✅ 四维度加权 + Source Authority Tiers | ✅ v0.4.0 完成 |
| Web 搜索 | ✅ Jina Search API 集成 + CLI/MCP | ✅ v0.5.0 完成 |

## 验收建议（本项目）

- `datapulse --list-sources`、`--list-packs`、`--resolve-source` 基本通过。
- `datapulse --query-feed` 与 `--query-rss` 可生成可读 Feed。
- MCP 包含新增工具：`resolve_source/list_sources/list_packs/query_feed/build_json_feed/build_rss_feed`。
- 远端 OpenClaw 入口可通过 `read_url/read_batch` 与 feed 查询联调。
