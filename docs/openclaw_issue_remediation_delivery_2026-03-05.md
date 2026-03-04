# OpenClaw 线索问题（#18-#24）落地修复交付事实

- 交付日期：`2026-03-05`
- 修复范围：线索文档提及 `#18 #19 #20 #21 #22 #23 #24`
- 交付类型：实现级修复 + 事实文档入库

## 修复事实清单

1. `#18 trending('china') 404`
- 交付：`reader.trending()` 增加地区失败自动回退 `worldwide`，返回 `requested_location` 与 `fallback_reason`。
- 文件：`datapulse/reader.py`
- 结果：调用方不会因单一区域 404 直接失效，可继续拿到趋势数据。

1. `#19 Jina Search 3s 超时激进`
- 交付：搜索默认超时从 `3s` 提升到 `8s`，且继续支持 `DATAPULSE_SEARCH_TIMEOUT` 环境覆盖。
- 文件：`datapulse/core/config.py`、`datapulse/core/search_gateway.py`
- 结果：主链路时延容忍度提升，减少不必要降级。

1. `#20 doctor() 全部 ✗`
- 交付：`ParsePipeline.doctor()` 回传新增兼容字段 `ok`，并按 `status/available` 推导。
- 文件：`datapulse/core/router.py`
- 结果：旧调用代码使用 `c.get('ok')` 不再出现“全部 ×”假象。

1. `#21 Twitter thin_content`
- 交付：`_read_sync()` 对 Twitter `thin_content` 自动尝试 Jina 内容回填；回填成功后更新 parser/factors/tags。
- 文件：`datapulse/reader.py`
- 结果：提升 Twitter 正文缺失场景的内容恢复率。

1. `#22 YouTube 依赖缺失`
- 交付：`youtube-transcript-api` 进入默认依赖安装集。
- 文件：`pyproject.toml`
- 结果：默认安装即可具备 YouTube 字幕提取能力，降低运行时缺依赖概率。

1. `#23 MEMORY API 偏差`
- 交付：
  - `search()` 增加 `top_n` 兼容别名；
  - `read_batch()` 增加 `store` 兼容参数（保留自动入库语义）；
  - `build_digest()` 支持传入 `items`（兼容 `build_digest(items)` 调用）；
  - 新增 `doctor_async()`、`build_digest_async()`。
- 文件：`datapulse/reader.py`
- 结果：历史调用方式更高兼容，减少 TypeError。

1. `#24 语义层事实核查缺口`
- 交付：
  - 新增轻量语义模块 `datapulse/core/semantic.py`（主张候选提取、立场分类、矛盾提示）；
  - `build_digest()` 新增 `semantic_review` 输出。
- 文件：`datapulse/core/semantic.py`、`datapulse/reader.py`
- 结果：在“采集/排序”之外补齐首版语义层事实视图。

## 入库文件

- 代码修复：
  - `datapulse/reader.py`
  - `datapulse/core/config.py`
  - `datapulse/core/search_gateway.py`
  - `datapulse/core/router.py`
  - `datapulse/core/semantic.py`
  - `pyproject.toml`
- 事实文档：
  - `docs/openclaw_issue_remediation_delivery_2026-03-05.md`

## 说明

- 本次交付聚焦“可落地实现”的最小闭环，不依赖额外基础设施。
- `semantic_review` 为启发式首版，定位为可解释增强层，不替代严格事实判定流程。
