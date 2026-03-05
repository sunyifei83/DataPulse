# Issue #25 高置信 HA 交付事实（Twitter 媒体图文结构化提取）

- Issue: `https://github.com/sunyifei83/DataPulse/issues/25`
- 交付时间（UTC）：`2026-03-05`
- 交付结论：`HA-DONE`

## 1. 事实输入（来自 issue）

- 目标推文在正文仅保留摘要与媒体 URL，关键信息位于图片中。
- 既有链路缺少结构化媒体提取字段，导致事实链条在入库阶段丢失。
- 约束要求：可选链路、fail-closed、避免把未验证 OCR 文本误判为高置信事实。

## 2. 实现交付（代码事实）

- 文件：`datapulse/collectors/twitter.py`
- 新增能力：
  - `extra.media_extraction` 结构化输出，字段包含：
    - `status`：`not_applicable|ok|skipped|degraded`
    - `items[]`：媒体提取明细（`index/type/url/text/method/confidence`）
    - `method`：提取方法来源（`fxtwitter_metadata` / `jina_generated_alt`）
    - `confidence`：媒体提取均值（与主文置信度分离）
  - 可选增强链路（默认关闭）：
    - `DATAPULSE_TWITTER_MEDIA_EXTRACT=1` 时，对图片 URL 触发 Jina `with_generated_alt` 提取。
    - 支持 `DATAPULSE_TWITTER_MEDIA_TIMEOUT` 与 `DATAPULSE_TWITTER_MEDIA_MAX_ITEMS`。
  - fail-closed：
    - 增强提取异常不伪造内容，`status=degraded` 并记录 `failed` 计数。
  - 入文链路：
    - 当存在提取文本时，追加 `## Media Extracted Signals (Unverified)`，保留“未验证”标注。

## 3. 高置信控制（HA）

- 媒体提取置信度单独存放在 `extra.media_extraction.confidence`，不直接作为主文高置信事实。
- `confidence_flags` 未引入 `image_captioned` 正向加分，避免未验证 OCR 文本抬高全局置信度。
- 降级路径显式化：提取失败时给出 `degraded`，不 silent fail。

## 4. 测试事实（落地执行）

- 新增测试文件：`tests/test_twitter_collector.py`
  - 覆盖：无媒体/元数据提取/可选增强提取/fail-closed 降级/`_parse_fxtwitter` 结构化输出。
- 执行记录：
  - `uv run pytest tests/test_twitter_collector.py tests/test_collectors.py tests/test_confidence.py`
    - 结果：`59 passed`
  - `uv run pytest tests/test_integration.py`
    - 结果：`3 passed`
  - `uv run ruff check datapulse/collectors/twitter.py tests/test_twitter_collector.py`
    - 结果：`All checks passed`

## 5. 关单判定

- Issue #25 的“事实缺口”已由实现与测试闭环覆盖。
- 满足“可选增强 + fail-closed + 可追溯结构化字段”三项约束。
- 建议执行最终关单。
