# Issue #26/#27 高置信 HA 交付事实（Decisive）

- 交付时间（UTC）：`2026-03-05`
- 关联 Issue：
  - `https://github.com/sunyifei83/DataPulse/issues/26`
  - `https://github.com/sunyifei83/DataPulse/issues/27`
- 交付结论：`HA-DONE / DECISIVE`

## 1. 事实输入（Issue 复核）

- #26：`TwitterCollector.parse()` 可产生 `media_extraction_degraded`，但 `DataPulseReader.read()` 返回的 `confidence_factors` 未保留该降级信号。
- #27：开启 `DATAPULSE_TWITTER_MEDIA_EXTRACT=1` 且缺失 `JINA_API_KEY` 时，媒体增强链路会退化；需要前置校验与可机读错误归因。

## 2. 实现事实（代码）

- `datapulse/reader.py`
  - `_to_item()` 中将 collector 的 `confidence_flags` 与 `compute_confidence()` 的 `reasons` 合并去重。
  - 结果：`media_extraction_degraded` 等关键降级信号不再在 reader 层丢失。

- `datapulse/collectors/twitter.py`
  - `media_extraction` 结构新增：`error_code`、`error_hint`。
  - 新增前置校验：当 `DATAPULSE_TWITTER_MEDIA_EXTRACT=1` 且 `JINA_API_KEY` 缺失时，不发起无效远程调用，输出 `error_code=auth_missing`。
  - 新增错误归因：对 `HTTPError/Timeout/RequestException/JinaBlockedByPolicyError` 分类为可机读错误码（如 `auth_unauthorized`、`network_timeout`、`policy_blocked`）。

## 3. 测试与复现事实

- 新增测试：`tests/test_reader_confidence_flags.py`
  - 覆盖：`_to_item()` 保留 collector 侧 `confidence_flags`。

- 更新测试：`tests/test_twitter_collector.py`
  - 覆盖新增断言：
    - 缺失 `JINA_API_KEY` 时 `auth_missing` 前置降级；
    - `401 Unauthorized` 归因为 `auth_unauthorized`；
    - 新增字段 `error_code/error_hint` 行为。

- 执行结果：
  - `uv run pytest tests/test_twitter_collector.py tests/test_reader_confidence_flags.py -q` → `8 passed`
  - `uv run pytest tests/test_twitter_collector.py tests/test_reader_confidence_flags.py tests/test_integration.py tests/test_confidence.py -q` → `27 passed`
  - `uv run ruff check datapulse/collectors/twitter.py datapulse/reader.py tests/test_twitter_collector.py tests/test_reader_confidence_flags.py` → `All checks passed`

- 实链复现（目标帖文）：
  - 条件：`JINA_API_KEY='' DATAPULSE_TWITTER_MEDIA_EXTRACT=1`
  - 结果：
    - `item.confidence_factors` 包含 `media_extraction_degraded`
    - `item.extra.media_extraction.error_code == auth_missing`

## 4. Decisive 判定

- 判定标准（本次 issue 级）：
  - 事实可复现；
  - 根因已落到代码修复；
  - 回归测试通过；
  - 实链验证与预期一致。
- 结论：`DECISIVE`（#26/#27 问题陈述均被直接覆盖，且可程序化复验）。

## 5. Inescapable 交付与 Assured 部署说明

- Inescapable 交付：
  - 代码、测试、复现实证三者已绑定，任一缺失均无法复验通过。
- Assured 部署（本地能力面）：
  - issue 相关路径已通过自动化测试与真实 URL 复验。
  - 与 issue 无关的外网波动（SSL/超时）保留为环境观察项，不构成本次 issue 修复阻断。
