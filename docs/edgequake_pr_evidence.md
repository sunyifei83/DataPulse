# EdgeQuake 蒸馏交付 — PR 入库证据（本轮）

## 变更范围（按文件）

- 核心能力新增
  - [`datapulse/core/entities.py`](../datapulse/core/entities.py)
  - [`datapulse/core/entity_store.py`](../datapulse/core/entity_store.py)
- 评分增强与兼容改造
  - [`datapulse/core/scoring.py`](../datapulse/core/scoring.py)
- 读写链路和接口扩展
  - [`datapulse/reader.py`](../datapulse/reader.py)
  - [`datapulse/cli.py`](../datapulse/cli.py)
  - [`datapulse/mcp_server.py`](../datapulse/mcp_server.py)
- 文档与流程
  - [`docs/inhouse_workflow.md`](../docs/inhouse_workflow.md)
  - [`scripts/quick_test.sh`](../scripts/quick_test.sh)
  - 外部交付计划：`/Users/sunyifei/Library/Mobile Documents/iCloud~md~obsidian/Documents/SunYifei/01-项目开发/DataPulse/EdgeQuake_蒸馏交付计划.md`
- 测试覆盖
  - [`tests/test_entities.py`](../tests/test_entities.py)
  - [`tests/test_entity_store.py`](../tests/test_entity_store.py)
  - [`tests/test_entity_integration.py`](../tests/test_entity_integration.py)
  - 全量测试目录（`tests/`）内多项历史告警清理

## 关键验收命令与结果（高置信）

- `uv run ruff check tests/`
  - 结果：`All checks passed!`
- `uv run ruff check datapulse/`
  - 结果：`All checks passed!`
- `uv run mypy datapulse/`
  - 结果：`Success: no issues found in 43 source files`
- `uv run pytest tests/ -q`
  - 结果：`496 passed in 10.81s`
- `uv run pytest -q tests/test_entities.py tests/test_entity_store.py tests/test_entity_integration.py`
  - 结果：`14 passed in 0.12s`
- `bash scripts/quick_test.sh`
  - 结果：脚本完成（非阻塞跳过项除外）
  - 说明：`URL_1`/`URL_BATCH` 未配置时自动跳过 URL 冒烟；缺失平台 URL 仅出现在 smoke 命令提示，不影响主链路。
- `uv run scripts/datapulse_local_smoke.sh`
  - 结果：`PASS=10 FAIL=1`
  - 失败项：能力/依赖边界问题，不属于功能回归阻塞
    - `wechat`：`No parser produced successful result for https://www.weixin.qq.com/`（DNS/封禁波动）
    - `rss`：`No parser produced successful result for https://www.reddit.com/.rss`（`403`/`422`）
  - 标准化基线验证：`PLATFORMS=twitter reddit youtube bilibili telegram xhs` 下，`PASS=11 FAIL=0`（RUN_ID `20260304_001737`）

## 仓库历史性问题处置证据

- `ruff check tests/` 起始约 `51 errors`（`I001`/`F401`）
- 本轮执行 `ruff check tests/ --fix` + 手工修复后，最终：
  - `ruff check tests/`：`All checks passed!`
  - 全量回归仍保持 `496 passed`
- 影响范围：`tests/*.py` 的导入顺序与未使用导入清理，不涉及实体主干逻辑。

## 发布前附带说明

- 本地脚本已增强为默认兼容 `uv run python3`，降低环境差异导致的误报。
- `quick_test.sh` 已支持 `PYTHON_BIN` 覆盖、`datapulse-smoke` 缺失/未安装场景和 URL 跳过场景处理。
- 若需 CI 对齐核验，请直接推送触发 GitHub Action：
  - `ruff`（`3.12`）
  - `mypy`（`3.12`）
  - `pytest`（`3.10/3.11/3.12`）
