# 数据源与订阅化增强计划（对标公开方案能力）

## 目标
建立 DataPulse 内部统一来源目录与订阅化输出来承接 OpenClaw 联接场景：稳定识别来源、可控订阅范围、可消费 Feed。

## 里程碑

### P0：来源目录（已开始）
- 提供 `DATAPULSE_SOURCE_CATALOG` 驱动的本地源清单。
- 支持 `list_sources / resolve_source / subscribe / unsubscribe / install_pack`。
- 支持来源类型与配置自动映射（含 RSS/网站 URL 识别）。

### P1：聚合交付
- 提供 JSON Feed 与 RSS 风格输出。
- 在 `Reader` 和 `MCP` 上提供查询/构建入口。
- 在 smoke 脚本中加入源目录与 feed 自检。

### P2：安全与反馈
- 补充标记/状态化反馈数据结构（pending / processed）。
- 为关键写操作增加环境变量开关与鉴权策略。

## 与现网能力映射

| 目标 | 目前落地状态 | 下一步 |
|---|---|---|
| 来源归类与发现 | `resolve_source`（URL 解析） | 完善多平台域名边界和 pattern 规则 |
| 订阅关系 | `subscribe/unsubscribe`、`list_subscriptions` | 增加批量订阅 API |
| 源组复用 | `install_pack` | 接入 `list_packs` 与导入清单 |
| 聚合输出 | `build_json_feed / build_rss_feed` | 增加 profile 级别摘要模板 |
| 运维安全 | 健康检查 + 配置化路径 | 增加写接口保护与鉴权开关 |

## 验收建议（本项目）

- `datapulse --list-sources`、`--list-packs`、`--resolve-source` 基本通过。
- `datapulse --query-feed` 与 `--query-rss` 可生成可读 Feed。
- MCP 包含新增工具：`resolve_source/list_sources/list_packs/query_feed/build_json_feed/build_rss_feed`。
- 远端 OpenClaw 入口可通过 `read_url/read_batch` 与 feed 查询联调。
