# 仓内常规操作工作流

> 适用于功能迭代后的变更交付闭环：功能迭代、编译跟测、HA交付、入库、推送、CI 绿化与问题捕获。

## 0. 三环境定义与调试对接策略（本地 / VPS / Macmini）

### 0.1 三环境资源模型（按客观差异设计）

- 本地调试环境（Developer Host）
  - 目标：最小化迭代周期，快速验证仓内功能正确性、契约一致性和异常回归。
  - 资源特征：开发机可控，适合 `python -m` 本地运行；可安装完整开发依赖，便于查看详细 trace。
  - 适用边界：代码单点行为、命令级静态检查、局部异常回放。
- VPS 过渡环境（Jump/Relay）
  - 目标：复现外网到中转链路上的连通与权限约束，验证两跳脚本链路的稳定性。
  - 资源特征：受限网络策略明显，可能无完整浏览器/交互会话，重点在“连通、代理、远端解释器、路径和权限”稳定性。
  - 适用边界：`scripts/datapulse_remote_openclaw_smoke.sh` 全量通道复核，阻断码闭环，`VPS_*`、`REMOTE_*` 参数一致性。
- Macmini 应用环境（Runtime Host）
  - 目标：覆盖生产/发布对齐面，验证 `18801` Runtime 端点和 OpenClaw/Agent 业务链路。
  - 资源特征：目标实例为最终部署姿态；异常与网络退化时必须依赖既有远端回退策略（代理隔离、Python 版本自适应、路径兜底）。
  - 适用边界：服务健康（`/healthz` `/readyz`）+ MCP/Agent/Skill 联动验收（以远端脚本输出为准）。

### 0.2 对接模式映射（MCP / Agent）

- MCP
  - 本地：`python -m datapulse.mcp_server --list-tools`、`--call`、`--stdio` 联通确认。
  - VPS 过渡：通过 `scripts/run_openclaw_remote_smoke_local.sh` 驱动的远端预检链路，验证远端可达性、命令注入与健康探针映射。
  - Macmini 应用：`datapulse` 与 OpenClaw 运行态对齐后，用 `scripts/datapulse_remote_openclaw_smoke.sh` 的 MCP/Agent 快速探针进行闭环确认。
- Agent
  - 本地：`scripts/datapulse_local_smoke.sh` 中 Agent 路径执行 `datapulse.agent.DataPulseAgent` 基础行为（含多 URL/无依赖回退场景）。
  - VPS 过渡：通过脚本 `agent smoke` 步骤复测 `URL_1/URL_BATCH` 对齐，校验会话与异常传播。
  - Macmini 应用：将应用环境变量注入后执行远端 smoke（需明确 `RUN_ID`）并记录阻断码，不得将本地结果替代最终结论。

### 0.3 阶段执行约束（不可遮蔽异常）

- 每个阶段均以明确退出码为准；**禁止**使用 `|| true`、吞错误分支或只抓部分输出而跳过失败。
- 必须记录：
  - 异常类别（如 `PYTHON_VERSION_TOO_LOW`、`PACKAGE_MISSING`、`IMPORT_FAILED`）
  - 失败命令（完整参数）
  - 下一步恢复动作与责任人
- 三环境之间的参数不跨污染：本地 `.env.openclaw.local` 仅用于本机持久化，应用环境以外部注入优先。

### 应急闭环（推荐执行）
- 任一关键阶段失败，按 [`docs/emergency_mode_runbook.md`](/Users/sunyifei/DataPulse/docs/emergency_mode_runbook.md) 的状态机执行：`S0` 到 `S5`，禁止在同一轮叠加参数试错。
- 复测触发必须新 `RUN_ID`，并补齐：
  - `artifacts/openclaw_datapulse_<RUN_ID>/remote_report.md`
  - `artifacts/openclaw_datapulse_<RUN_ID>/remote_test.log`
- Blocker 级别（如 `PYTHON_VERSION_TOO_LOW`、`IMPORT_FAILED`、`SSH_AUTH_FAILED`）直接判定 `STOP`，禁止发布推进。

## 1. 功能迭代

- 在分支完成代码修改前先明确本次改动目标、影响范围与回归点。
- 提交前做局部自检：  
  - `python3 -m compileall datapulse`
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
  - 脚本默认会先做 SSH 连通性预检（含两跳跳转），并在首次阻塞时提前退出以避免长时间挂起。
- 结合输出日志确认阻断码（若有），例如：
  - `PACKAGE_MISSING / IMPORT_FAILED / PYTHON_VERSION_TOO_LOW / BUILD_DEPENDENCY_PROXY_FAIL` 等
- 典型连通性阻断码：
  - `SSH_CONNECTION_REFUSED`（如 `Connection timed out` / `No route to host`）
- 每次执行建议记录：
  - `RUN_ID`（自动生成）
  - 本地/远端报告路径（`artifacts/openclaw_datapulse_<RUN_ID>/*`）

## 4. 文档联动刷新（准确性 / 易读性 / 时效性）

- 在 HA 验收与 PR 提交流程前，先更新本次交付涉及的仓内事实文档：
  - `README.md`、`README_CN.md`、`README_EN.md`
  - 本次验收链路相关 docs（如 `docs/openclaw_datapulse_acceptance_template.md`、`docs/test_facts.md`、`docs/issue_pool.md`）
  - 工具能力契约（如需新增/变更工具）同步更新 `docs/contracts/openclaw_datapulse_tool_contract.json`
- 文档刷新核对清单（最小）：
  - 版本与里程碑（如 `__version__`）
  - MCP 工具数量与清单
  - 搜索、实体、健康检查、远端验收链路
  - 错误码与运行脚本边界输入
- 完成文档更新后，补充一次 PR 说明中的“文档已对齐”条目，并记录更新摘要（变更文件 + 验证依据）。

## 5. 提交变更入库

- 本地确认通过后，执行标准提交流程：
  - `git add`
  - `git commit -m "<type>: <summary>"`
  - 变更内容与验收结果写入 PR 模板对应项（尤其是“发布前检查”）
- 建议 PR 描述同步关键结果：
  - 本机 smoke/quick_test 结果
  - 远端 HA 验收结论
  - 遗留阻断与风险说明

## 6. 推送触发 CI

- 推送到远端分支触发 GitHub Actions：  
  - `.github/workflows/ci.yml`（main/pull_request）自动运行 lint、typecheck、tests。
  - 仅文档/说明文件变更（`*.md`、`docs/**`、`README*`）按当前工作流配置可避免触发 CI；业务代码变更仍走完整 CI。
- CI 全绿为交付前置条件，必须至少确认：
  - `ruff`、`mypy`、`pytest` 全部通过
- 需要重现问题时，先复现最小范围用例，再回到对应阶段补测。

## 7. 捕获问题（闭环）

- CI 失败或联测失败统一进入问题池（`docs/issue_pool.md`），记录以下最小信息：
  - 触发分支、提交号
  - 失败任务与日志片段（CI log / artifacts 报告）
  - 最小复现命令
  - 预期与实际差异
  - 截止时间与责任人
- 修复后重复执行该问题对应阶段，并在 PR/问题记录中补充回归结果（新 RUN_ID）。

## 附：推荐执行顺序

1. 功能迭代 -> 2. 编译跟测 -> 3. 高 HA 交付 -> 4. 文档联动刷新 -> 5. 提交入库 -> 6. 推送触发CI -> 7. CI全绿 -> 8. 捕获问题
