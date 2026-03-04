# 仓内常规操作工作流

> 适用于功能迭代后的变更交付闭环：功能迭代、编译跟测、HA交付、入库、推送、CI 绿化与问题捕获。

## 1. 功能迭代

- 在分支完成代码修改前先明确本次改动目标、影响范围与回归点。
- 提交前做局部自检：  
  - `python -m compileall datapulse`
- 变更完成后运行快速静态检查（按开发环境执行）：
  - `pip install -e ".[dev]"`
  - `ruff check datapulse/`
  - `mypy datapulse/`
  - `pytest tests/ -q`

## 2. 编译跟测（本机）

- 运行仓内冒烟与功能回归，确认主链路可用：
  - `bash scripts/quick_test.sh`（通用验证）
  - `bash scripts/datapulse_local_smoke.sh`（CLI/平台覆盖）
  - （必要时）`bash scripts/run_xhs_quality_report.sh` 生成可读+可机读验收结果
- 要求至少通过：
  - CLI 单条与批量解析
  - `datapulse-smoke --list`
  - `datapulse-smoke --platforms ... --require-all`
  - 基础 `query_feed`/`build_json_feed` 路径

## 3. 高可用（HA）交付验证

- 进入接入环境验证前，先确认 `MACMINI_DATAPULSE_DIR`、Python 版本与健康探针可达。
- 运行远端联测（按现网环境）：
  - `bash scripts/datapulse_remote_openclaw_smoke.sh`
- 结合输出日志确认阻断码（若有），例如：
  - `PACKAGE_MISSING / IMPORT_FAILED / PYTHON_VERSION_TOO_LOW / BUILD_DEPENDENCY_PROXY_FAIL` 等
- 每次执行建议记录：
  - `RUN_ID`（自动生成）
  - 本地/远端报告路径（`artifacts/openclaw_datapulse_<RUN_ID>/*`）

## 4. 提交变更入库

- 本地确认通过后，执行标准提交流程：
  - `git add`
  - `git commit -m "<type>: <summary>"`
  - 变更内容与验收结果写入 PR 模板对应项（尤其是“发布前检查”）
- 建议 PR 描述同步关键结果：
  - 本机 smoke/quick_test 结果
  - 远端 HA 验收结论
  - 遗留阻断与风险说明

## 5. 推送触发 CI

- 推送到远端分支触发 GitHub Actions：  
  - `.github/workflows/ci.yml`（main/pull_request）自动运行 lint、typecheck、tests。
- CI 全绿为交付前置条件，必须至少确认：
  - `ruff`、`mypy`、`pytest` 全部通过
- 需要重现问题时，先复现最小范围用例，再回到对应阶段补测。

## 6. 捕获问题（闭环）

- CI 失败或联测失败统一进入问题池（`docs/issue_pool.md`），记录以下最小信息：
  - 触发分支、提交号
  - 失败任务与日志片段（CI log / artifacts 报告）
  - 最小复现命令
  - 预期与实际差异
  - 截止时间与责任人
- 修复后重复执行该问题对应阶段，并在 PR/问题记录中补充回归结果（新 RUN_ID）。

## 附：推荐执行顺序

1. 功能迭代 -> 2. 编译跟测 -> 3. 高 HA 交付 -> 4. 提交入库 -> 5. 推送触发CI -> 6. CI全绿 -> 7. 捕获问题
