# 应急模式说明（远端联测）v1.1

## 目标（适用场景）
- 远端联测出现阻断、连通失败、解释器兼容异常、依赖缺失、上下文窗口超限（如 `context window exceeded`）时，采用单页闭环处置。
- 约束：不做多分支盲测。每次关键参数变更都必须产出新 `RUN_ID` 并完整复测。

## 0. 事故状态机（固定流程）
按以下状态逐级推进，每轮只执行当前状态定义动作，不跨状态叠加：
- `S0 监控`：收集异常现象、阻断码、失败命令（`remote_test.log` 与 `remote_report.md`）。
- `S1 分型`：归因到下列之一：路径类 / 解释器类 / 依赖类 / 网络类 / 工具链类 / 上下文类。
- `S2 隔离`：暂停新增测试，只允许一次恢复动作并立刻复测。
- `S3 路由`：按下文决策矩阵选择单一恢复路径。
- `S4 恢复执行`：执行固定修复动作，产出新 `RUN_ID` 复测。
- `S5 复核放行`：通过时给出 GREEN/YELLOW；有新 Blocker 或连续失败则 `STOP`。

## 1. 固定起始动作（每次事件必做）
1. 固定本次运行快照：
```bash
export RUN_ID=$(date +%Y%m%d_%H%M%S)
export OUT_DIR=artifacts
```
2. 安全与本机底线检查：
```bash
bash scripts/security_guardrails.sh
bash scripts/datapulse_local_smoke.sh
```
3. 保持变量只改一组：本次只允许一次主路径变更（解释器、VPS、依赖、代理类单选一组）。
4. 执行主命令：
```bash
bash scripts/datapulse_remote_openclaw_smoke.sh
```
5. 若失败，按决策矩阵仅改一条路径后复测；不得重复在同一 `RUN_ID` 下再次叠加参数。

## 2. 决策矩阵（触发信号 → 单一第一动作）
| 触发信号 | 首选动作 | 次选动作 | 回退条件 |
| --- | --- | --- | --- |
| `PYTHON_VERSION_TOO_LOW` / `UV_NOT_FOUND` | `REMOTE_USE_UV=0` + 明确 `REMOTE_PYTHON=/opt/homebrew/bin/python3.10` + `REMOTE_BOOTSTRAP_INSTALL=1` | `REMOTE_USE_UV=1` + `REMOTE_UV_PYTHON=3.10` | 两条路径均失败或出现 Blocker，直接 `STOP` |
| `IMPORT_FAILED` / `PACKAGE_MISSING` / `PYPROJECT_MISSING` | `REMOTE_BOOTSTRAP_INSTALL=1` + 校验 `MACMINI_DATAPULSE_DIR` | 补齐 `REMOTE_PIP_EXTRAS`（按平台）后重测 | 仍失败不改解释器，先记录问题并进入阻断 |
| `BUILD_DEPENDENCY_PROXY_FAIL` | 保持 Python 直连，保持命令级代理隔离（脚本默认） | `REMOTE_PIP_NO_PROXY="*"`，按需 `REMOTE_UV_BOOTSTRAP=1` | 仍失败，提交网络/代理链路工单 |
| `SSH_CONNECTION_REFUSED` / `SSH_AUTH_FAILED` / `SSH_HOST_KEY_UNKNOWN` | 优先调整 `MACMINI_HOST`（按 `MACMINI_HOST_CANDIDATES`） | 切备份 VPS（见第 3 节） | 备份 VPS 仍失败，进入问题池 |
| `context window exceeded` | 停止该轮，构造精简上下文重试 | 仅保留阻断码+关键命令+环境快照再次复测 | 再次超限则按故障隔离人工复核 |

## 3. uv 恢复路径（主备切换）

### 3.1 主恢复：Python 直连（默认）
```bash
export REMOTE_USE_UV=0
export REMOTE_AUTOPICK_PYTHON=1
export REMOTE_PYTHON_MIN_VERSION=3.10
export REMOTE_PYTHON=/opt/homebrew/bin/python3.10
export REMOTE_BOOTSTRAP_INSTALL=1
```

### 3.2 备份恢复：uv 执行链
```bash
export REMOTE_USE_UV=1
export REMOTE_UV_PYTHON=3.10
export REMOTE_AUTOPICK_PYTHON=0
export REMOTE_BOOTSTRAP_INSTALL=1
export REMOTE_UV_BOOTSTRAP=1
export REMOTE_UV_LOCAL_BINARY=$(command -v uv)
export REMOTE_UV_INSTALL_ROOT=~/.local/bin
```
- 当 `REMOTE_DIRECT_SSH=1` 且 `REMOTE_UV_BOOTSTRAP=1`：先尝试同步本机 `uv` 到远端再执行。
- 同步失败自动回退 `python3 -m pip install --user uv`，并继续后续验证。
- uv 仍失败不得立即改 VPS；先回收到 `REMOTE_USE_UV=0` 的 Python 直连路径。

## 4. 备份 VPS 回退规则（网络异常优先）
- 主链路默认：`VPS_HOST=137.220.151.57`、`VPS_PORT=6069`、`MACMINI_HOST_CANDIDATES=127.0.0.1,192.168.3.196,192.168.3.195`、`REMOTE_DIRECT_SSH=0`。
- 备份链路：`VPS_HOST=38.244.20.109`、`VPS_PORT=20108`，仅作为可用性对照，不作常规主入口。
- 切换动作只允许发生一次，且必须新 `RUN_ID`：
```bash
export RUN_ID=$(date +%Y%m%d_%H%M%S)
export VPS_HOST=38.244.20.109
export VPS_PORT=20108
bash scripts/datapulse_remote_openclaw_smoke.sh
```
- 若主链路与备份链路连续失败：`STOP`，进入问题池，不再进行路径堆栈试错。

## 5. 异常关闭（阻断）与复测触发
### 5.1 立即停止（Blocker）
- 阻断码触发：`DATAPULSE_DIR_NOT_FOUND`、`PYPROJECT_MISSING`、`PACKAGE_MISSING`、`PYTHON_VERSION_TOO_LOW`、`IMPORT_FAILED`、`UV_NOT_FOUND`、`SSH_CONNECTION_REFUSED`、`SSH_AUTH_FAILED`、`SSH_HOST_KEY_UNKNOWN`
- `remote compact` 报 `context window exceeded`，先行停止并清理输入再复测。

### 5.2 复测必须新 `RUN_ID` 的情况
- 任何关键参数变更：`VPS_HOST/VPS_PORT`、`MACMINI_HOST`、`REMOTE_USE_UV`、`REMOTE_UV_*`、`REMOTE_PYTHON`、`REMOTE_PIP_EXTRAS`、`REMOTE_PYTHON_MIN_VERSION`。
- 新增或消失阻断码、关键步骤 FAIL、或 Watch 上升为 Blocker。
- 复测命令始终：
```bash
export RUN_ID=$(date +%Y%m%d_%H%M%S)
bash scripts/datapulse_remote_openclaw_smoke.sh
```

## 6. 上下文窗口保护（避免 `context window exceeded` 循环）
- 每次向 `remote compact` 传递的上下文只保留：事件摘要、`RUN_ID`、阻断码、失败命令、差异变量、1~2 份关键日志摘要。
- 禁止传入全量日志、历史无关讨论、连续错误堆栈全集，减少模型输入失控。
- 复测前重复执行 `bash scripts/security_guardrails.sh`。

## 7. 收口输出（每次都要归档）
- `artifacts/openclaw_datapulse_${RUN_ID}/remote_report.md`
- `artifacts/openclaw_datapulse_${RUN_ID}/remote_test.log`
- 复测结论：`RED`（阻断未消）、`YELLOW`（仅 Watch）、`GREEN`（无阻断、无新 Blocker）。
- 触发 `STOP` 时，必须同步问题池与责任人，避免发布推进。

## 8. 一页执行清单（值守可直接粘贴）
```bash
# 0) 事件起点：设置 RUN_ID 与输出目录
RUN_ID=$(date +%Y%m%d_%H%M%S); export OUT_DIR=artifacts

# 1) 安全与本机底线
bash scripts/security_guardrails.sh && bash scripts/datapulse_local_smoke.sh

# 2) 默认执行（主路径）
export REMOTE_USE_UV=0
export REMOTE_AUTOPICK_PYTHON=1
export REMOTE_PYTHON_MIN_VERSION=3.10
export REMOTE_PYTHON=/opt/homebrew/bin/python3.10
export REMOTE_BOOTSTRAP_INSTALL=1
bash scripts/datapulse_remote_openclaw_smoke.sh
code=$?

# 3) 仅失败时，按矩阵改一项参数并复测（需新 RUN_ID）
if [ "$code" -ne 0 ]; then
  export RUN_ID=$(date +%Y%m%d_%H%M%S)
  # 失败含 context window exceeded：停止本轮并重构输入后再执行 remote compact
  # 失败含 SSH/网络问题：先换主机候选，再切备份 VPS，仅一次
fi

bash scripts/datapulse_remote_openclaw_smoke.sh
```

## 9. 机器可读化与状态记录（执行后立即跑）
```bash
RUN_DIR="artifacts/openclaw_datapulse_${RUN_ID}"
bash scripts/emergency_guard.sh \
  --rules docs/emergency_rules.json \
  --report "$RUN_DIR/remote_report.md" \
  --log "$RUN_DIR/remote_test.log" \
  --out "$RUN_DIR/emergency_state.json"
```
- 输出字段要核对：`RUN_ID`、`FIRST_TRIGGER`、`STATE`、`NEW_RUN_ID_REQUIRED`、`STOP`

```bash
# 发布前一键闸口（可接入 release_readiness）
bash scripts/release_readiness.sh \
  --emergency-state "$RUN_DIR/emergency_state.json" \
  --require-emergency-gate
```

## 版本
- `2026-03-04`
- `应急模式说明 v1.2（升维版 + 机器可读）`
