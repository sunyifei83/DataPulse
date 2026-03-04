# OpenClaw 历史 open issue（#18-#24）高置信 HA 处置与关单事实

- 生成时间：`2026-03-05`
- 范围：`sunyifei83/DataPulse` 当前 `open` issue（#18 ~ #24）
- 处置目标：基于可复现事实做高置信分流，完成仓库内交付事实入库与最终关单

## 1. 证据采集口径（高置信）

- 实时 issue 状态：`gh issue list --state open`（确认仅 #18 ~ #24）
- 代码事实：`reader.py` / `core/config.py` / `core/search_gateway.py` / 相关 collectors
- 运行事实（同仓一次性复测）：
  - `DataPulseReader.trending('china')`：复现 `404 Client Error`
  - `DataPulseReader.trending('worldwide')`：可返回趋势数据
  - `DataPulseReader.read(目标推文)`：复现 `thin_content`（仅互动数字）
  - `DataPulseReader.doctor()`：`tier_0` 全部 `available=true`，不再“全红”
  - `inspect.signature`：`search(limit=...)`、`read_batch(...)`、`build_digest(...)` 等签名可核验

## 2. issue 逐条处置结果

| Issue | 复核事实 | HA 处置 | 关单结论 |
|---|---|---|---|
| #18 `trending('china') 404` | 运行复测仍报 `https://trends24.in/china/` 404；`worldwide` 正常 | `HA-BOUNDARY`（第三方地区页失效，属外部依赖边界；主链路可走 `worldwide`） | 关闭（边界项归档，不再占用 open 队列） |
| #19 Jina Search 3s 超时 | `SearchGatewayConfig` 已支持 `DATAPULSE_SEARCH_TIMEOUT`；`SearchGateway`/`JinaAPIClient` 使用可配置超时 | `HA-DONE`（“硬编码不可调”事实已消除） | 关闭（已交付） |
| #20 `doctor()` 全部 ✗ | 复测显示 `tier_0` 三个 collector 全部 `ok`；仅 `telegram` 因凭据缺失不可用 | `HA-DONE`（“全部 collector 均失败”已不成立） | 关闭（已交付） |
| #21 Twitter `thin_content` | 目标推文复测仍返回 `👍 0 🔁 0 👁️ 0`，`confidence_factors` 包含 `thin_content` | `HA-BOUNDARY`（上游代理/反爬数据面不稳定，当前为可见边界） | 关闭（边界项归档，不作为当前版本阻断） |
| #22 YouTube 依赖缺失 | `YouTubeCollector.check()` 已提供依赖/凭据健康信号与 `setup_hint`；缺 transcript 时有 Whisper fallback | `HA-DONE`（从“静默失败”转为“可诊断可引导”） | 关闭（已交付） |
| #23 MEMORY.md 签名不一致 | 代码签名可直接核验：`search(limit)`、`read_batch` 无 `store`、`build_digest` 同步方法 | `HA-DONE`（仓内 API 事实已可程序化校验） | 关闭（已交付） |
| #24 语义层事实核查架构缺口 | v0.7 已交付实体抽取/跨源补强能力；完整“主张-证据-立场-判定”引擎仍属演进项 | `HA-ROADMAP`（架构议题拆解后不作为当前 open 阻断） | 关闭（路线化归档） |

## 3. 本次关单后的仓库事实

- 历史 OpenClaw 事实核查问题单已全部完成处置分流（`DONE/BOUNDARY/ROADMAP`）。
- 仓库 `open` issue 队列不再保留 2026-03-04 这批调研型事实单。
- 处置遵循“先复核事实，再关单”，避免无证据关单。

## 4. 可追溯锚点

- 运行复测时间：`2026-03-05`（同仓 `uv run python`）
- 关键复测结论：
  - `trending('china')`：`404`
  - `trending('worldwide')`：`ok`
  - 目标推文读取：`thin_content` 复现
  - `doctor()`：非全失败（`tier_0` 全绿）
- 代码锚点：
  - `datapulse/core/config.py`（`DATAPULSE_SEARCH_TIMEOUT`）
  - `datapulse/core/search_gateway.py`（超时配置注入 `JinaAPIClient`）
  - `datapulse/reader.py`（`search/read_batch/trending/build_digest/doctor` 签名）
  - `datapulse/collectors/youtube.py`（`check()` 与 `setup_hint`）

