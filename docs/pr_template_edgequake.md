# PR 描述（EdgeQuake 蒸馏交付）

## 标题（示例）
feat: 吸收实体抽取能力并补强评分链路（EdgeQuake 交付）

## 变更摘要
- 新增 `datapulse/core/entities.py` 与 `datapulse/core/entity_store.py`，支持实体抽取、标准化、关系建模与本地持久化。
- 增强评分逻辑（`datapulse/core/scoring.py`）支持实体跨源共识加分，默认行为保持兼容。
- 扩展 `DataPulseReader`、CLI 与 MCP 能力，提供实体查询/图谱/统计能力入口。
- 增加实体能力专项测试：
  - `tests/test_entities.py`
  - `tests/test_entity_store.py`
  - `tests/test_entity_integration.py`
- 列表化并修正仓库级 `ruff tests/` 历史告警（不改变实体核心逻辑）。

## 验证结果（高置信）
- `uv run ruff check tests/`
  - All checks passed!
- `uv run ruff check datapulse/`
  - All checks passed!
- `uv run mypy datapulse/`
  - Success: no issues found in 43 source files
- `uv run pytest tests/ -q`
  - 496 passed in 10.81s
- `uv run pytest -q tests/test_entities.py tests/test_entity_store.py tests/test_entity_integration.py`
  - 14 passed in 0.12s
- `bash scripts/quick_test.sh`
  - 成功完成；仅在未设置 URL 环境变量时跳过 URL 冒烟；缺失 smoke 平台 URL 的提示不阻塞主链路。
- `uv run scripts/datapulse_local_smoke.sh`
  - PASS=10 FAIL=1（FAIL 为平台能力/依赖边界：`wechat`、`rss`；RUN_ID `20260304_001443`）
  - 标准化基线：`PLATFORMS=twitter reddit youtube bilibili telegram xhs`，`PASS=11 FAIL=0`（RUN_ID `20260304_001737`）

## 风险与回滚
- 风险主要集中在 `entity_source_counts`/`entity` 新特性未开启时为默认关闭、主逻辑行为保持兼容。
- 回滚方式：回退该轮提交；CLI/MCP/实体相关命令回退为旧行为。

## 说明
- 依据仓内交付流程与 `EdgeQuake_蒸馏交付计划.md`，当前已形成从功能迭代、门禁复核、HA 脚本复测到问题闭环的证据链。
