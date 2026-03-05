# DataPulse + OpenClaw 远程接入验收模板（macmini M4）

> 生成时间：`2026-03-04`
> 应急入口：[`应急模式说明（远端联测）v1.1`](/Users/sunyifei/DataPulse/docs/emergency_mode_runbook.md)

## 0) 三环境定义与对接策略（先本地再 VPS 再 Macmini）

### 0.1 资源与职责边界

- 本地调试环境（Developer Host）
  - 任务：快速验证本地 CLI/MCP/Agent 行为是否可复现。
  - 资源特征：开发机可安装开发依赖与日志工具，强调可调试性和最短反馈。
- VPS 过渡环境（VPS 两跳/Relay）
  - 任务：验证连通、代理、密钥注入、远端解释器和脚本参数在真实链路中的可达性。
  - 资源特征：受限网络策略明显，可能无完整浏览器/交互会话，重点在最小闭环复用（健康探针 + 阻断码 + smoke）。
- Macmini 应用环境（Runtime Host）
  - 任务：验证部署态功能行为、服务健康、MCP/Agent 可观察输出与阻断恢复能力。
  - 资源特征：作为最终部署面，采用与运行时一致的网络与模型路由；本地输出只能作为先验，不可替代该环境结论。

#### 0.1.1 三环境客观资源对照（异地约束）

- 本地（Debug Host）
  - 任务：快速验证本地 CLI/MCP/Agent 基线行为与参数可读性。
  - 资源特点：可安装调试工具，通常不持有稳定内网直连条件。
  - 验证策略：本机 smoke 先行，失败先本地复现再复测远端。
- VPS 过渡环境（当前主链路）
  - 任务：验证两跳隧道链路、代理、SSH 与阻断码闭环。
  - 资源特点：`VPS_HOST=137.220.151.57:6069`，`MACMINI_HOST_CANDIDATES=127.0.0.1,192.168.3.196,192.168.3.195`，`MACMINI_PORT=2222`（映射端口）。
  - 验证策略：默认 `REMOTE_DIRECT_SSH=0`，保留失败重试与阻断码归档。
- Macmini 应用（Runtime Host）
  - 任务：以 Runtime 与网关实际行为作为最终验收锚点。
  - 资源特点：异地部署，`192.168.3.196` 为历史/回退参考，默认不作为第一优先直连。
  - 验证策略：`/healthz` `/readyz` + 远端 smoke + MCP/Agent 快检。
- 备份 VPS（历史参考，不作为当前主链路）
  - 任务：网络异常时的架构对照与回退参考。
  - 资源特点：`38.244.20.109:20108` 标注为“IP 被墙”，常规链路不建议直接作为验收主路径。
  - 验证策略：仅在网络切换/回退场景用于对照。

### 0.2 MCP / Agent 运行模式选择（按环境）

| 环境 | MCP 模式 | Agent 模式 | 切换触发条件 | 输出要求 |
| --- | --- | --- | --- | --- |
| 本地 | `python3 -m datapulse.mcp_server --list-tools`；必要时 `--call` | 本地 smoke 的 `agent` 步骤 | 本地改动 / 契约变更 | 返回码 `0`，工具清单稳定，字段可解析 |
| VPS 过渡 | `bash scripts/run_openclaw_remote_smoke_local.sh`（两跳为主） | `bash scripts/datapulse_remote_openclaw_smoke.sh` 的 `agent smoke` 步骤 | 本地验证通过后 | 阻断码可读、`REMOTE_*` 参数一致、`RUN_ID` 写入 |
| Macmini 应用 | 以 `18801` Runtime 为最终判定端口进行 smoke | 远端 smoke + 应用链路复核 | VPS 阶段通过后 | `/healthz` `/readyz` + 阻断码闭环均通过 |

### 0.2.1 模式切换策略（按资源差异）

- VPS 过渡：
  - MCP：固定走两跳远端脚本，优先保留 `smoke list`、`smoke platforms` 与 `mcp/agent quick probe`。
  - Agent：通过 `agent smoke` 与 `run script` 的 `RUN_ID` 落盘复现，禁止本地结果替代。
- 本地：
  - MCP：先执行 `python3 -m datapulse.mcp_server --list-tools` 与本机 smoke，作为远端预检。
  - Agent：本机异常必须复现后再进入远端环境复测。
- Macmini：
  - 以 `healthz/readyz`、MCP 工具集合与 `DataPulseAgent.handle` 为最终判定。

### 0.2.2 环境硬约束

- 当前异地链路下，`REMOTE_DIRECT_SSH=1` 不应作为默认路径，固定使用 `REMOTE_DIRECT_SSH=0`。
- Macmini 直连仅作为回退候选：`MACMINI_HOST` 可在本地网段可达时再使用，不作为生产验收默认入口。
- 两跳路径的优先级：`MACMINI_HOST=127.0.0.1`（VPS 本地隧道）优先，随后回退 `192.168.3.196`，再回退 `192.168.3.195`。

### 0.3 异常处理（不可遮蔽）

- 本阶段每步必须保留完整失败输出，禁止 `|| true`、静默降级。
- 任一关键步骤失败，不得跳过并进入下一阶段；必须复现、归档、复测。
- 发生异常时，按 `S0→S5` 状态机执行（见 `docs/emergency_mode_runbook.md`），禁止同一轮叠加多路径变更。
- 阶段顺序硬约束：
  - 本地失败：禁止进入 VPS 阶段；
  - VPS 失败：禁止直接用作应用结论；
  - Macmini 失败：需输出阻断码与复测动作（含 Python/路径/网络检查）。

### 0.4 高可用交付 Gate v1（判定制度）

- 判定状态：
  - `GREEN`：关键链路无阻断码、关键步骤 PASS、观察告警可控。
  - `YELLOW`：关键链路 PASS，出现外部依赖波动告警，无阻断码，可受限放行并建立观察清单。
  - `RED`：出现阻断码、关键步骤 FAIL，或关键闭环未达标（`RUN_ID` 缺失、`healthz/readyz` 失败）。
- 关键步骤（硬约束）：
  - `check datapulse directory exists`
  - `check pyproject`
  - `check datapulse package`
  - `check python version`
  - `check pip toolchain`
  - `import datapulse`
  - `smoke list`
  - `smoke platforms`
  - `healthz/readyz`
  - `mcp/agent quick probe`
- 阻断码分层：
  - `Blocker`：`DATAPULSE_DIR_NOT_FOUND`、`PACKAGE_MISSING`、`PYTHON_VERSION_TOO_LOW`、`PYPROJECT_MISSING`、`IMPORT_FAILED`、`UV_NOT_FOUND`、`SSH_CONNECTION_REFUSED`、`SSH_AUTH_FAILED`。
  - `Watch`：`telegram` 缺 `TG_API_ID/TG_API_HASH`、`xhs` Jina 451、`youtube` 超时/字幕接口兼容提示、临时网络抖动。
- 放行规则：
  - `GREEN` 入库条件：`FAIL=0` 且阻断码为空且 Watch 告警已列清。
  - `YELLOW` 入库条件：`FAIL=0` 且仅 Watch 告警，需附：`观察项`、`责任人`、`下次复测计划`。
  - `RED` 入库条件：`FAIL>0` 或存在 Blocker，必须先消解阻断码后复测。
- 自动要求：
  - 每次执行必须有 `RUN_ID`、`remote_report.md`、`remote_test.log` 三件套。
  - 复测必须新 `RUN_ID`。
  - 任意 `RED` 必须更新 `docs/test_facts.md` 阶段性事实并重放关键步骤。
  - 任意 `Blocker` 级别阻断先按 Runbook 处理后再复测，`Blocker` 不得直接放行。

### 0.4.1 应急执行一致性

- 首选恢复路径：按 `docs/emergency_mode_runbook.md` 的决策矩阵执行。
- 关键参数变更触发复测的前置条件：`RUN_ID` 递增 + 输出三件套存在。
- 本次对齐：
  - `RUN_ID=20260304_185014` 对应 `YELLOW`，关键步骤 PASS=15/15，Blocker=0，Watch=外部依赖告警（telegram/xhs/youtube/reddit）。

## 1) 测试环境
- 机器：Mac Mini M4
- 接入路径：`VPS 两跳隧道`（带宽受限时可降级为 `MACMINI_HOST` 内网直连）
- OpenClaw Runtime：`127.0.0.1:18801`
- 推荐本地命令入口：`python3`
- 测试执行人：
- 测试日期（UTC）：
- RUN_ID：

## 2) 测试素材准备
- `URL_1`：如 `https://beewebsystems.com/`
- `URL_BATCH`：如 `https://chatprd.ai/ https://beewebsystems.com/ https://uxpilot.ai/`
- 平台 Smoke 变量（按需）：
  - `DATAPULSE_SMOKE_TWITTER_URL`
    - 可用示例：`https://x.com/everestchris6/status/2025995047729254701`
  - `DATAPULSE_SMOKE_REDDIT_URL`
    - 缺失会导致 `smoke platforms --require-all` 直接报错（`Missing smoke URLs`）
  - `DATAPULSE_SMOKE_YOUTUBE_URL`
  - `DATAPULSE_SMOKE_BILIBILI_URL`
  - `DATAPULSE_SMOKE_TELEGRAM_URL`
  - `DATAPULSE_SMOKE_RSS_URL`
  - `DATAPULSE_SMOKE_WECHAT_URL`
  - `DATAPULSE_SMOKE_XHS_URL`

### 2.1 远端联测基线事实（2026-03-04）

- 两跳主链路（固定执行）：
  - `VPS_HOST=137.220.151.57`、`VPS_PORT=6069`
  - `MACMINI_HOST=127.0.0.1`
  - `MACMINI_PORT=2222`
  - `MACMINI_HOST_CANDIDATES=127.0.0.1,192.168.3.196,192.168.3.195`
- 当前环境为异地，`REMOTE_DIRECT_SSH=1` 不可用；本阶段以两跳为准（`REMOTE_DIRECT_SSH=0`）
- 远端 `python3` 默认链路为 3.9.6，不满足 `>=3.10`，已固定使用 `REMOTE_PYTHON=/opt/homebrew/bin/python3.10` 完成全流程
- 远端同时存在 uv（`/opt/homebrew/bin/uv 0.10.7`），`REMOTE_USE_UV=1` 可作为后续替代方案，当前保持 Python 直连路径稳定性优先。
- 最新执行（`RUN_ID=20260304_185014`）全量通过：15/15 无失败，`remote_report=artifacts/openclaw_datapulse_20260304_185014/remote_report.md`，无新增阻断码。
- uv 执行回路（执行1）补测 `RUN_ID=20260304_193008` 全量通过：16/16 无失败，`remote_report=artifacts/openclaw_datapulse_20260304_193008/remote_report.md`，无新增阻断码（含 `check uv/bootstrap`）。
- 最新闭环复测（`RUN_ID=20260304_194700`）再次全量通过：15/15 无失败，`remote_report=artifacts/openclaw_datapulse_20260304_194700/remote_report.md`，无新增阻断码（外部告警保留为 Watch）。
- 已补齐的 `DATAPULSE_SMOKE_*` 输入（用于 `smoke platforms --require-all`）：
  - `DATAPULSE_SMOKE_REDDIT_URL=https://www.reddit.com/r/python/comments/1f6m2v9/why_i_use_python/`
  - `DATAPULSE_SMOKE_YOUTUBE_URL=https://www.youtube.com/watch?v=dQw4w9WgXcQ`
  - `DATAPULSE_SMOKE_BILIBILI_URL=https://www.bilibili.com/video/BV1Xx411c7mD`
  - `DATAPULSE_SMOKE_TELEGRAM_URL=https://t.me/s/telegram`
  - `DATAPULSE_SMOKE_RSS_URL=https://www.reddit.com/.rss`
  - `DATAPULSE_SMOKE_WECHAT_URL=https://www.weixin.qq.com/`
  - `DATAPULSE_SMOKE_XHS_URL=https://www.xiaohongshu.com/explore`
- 运行中的非阻断告警（仅观测）：
  - `telegram` 缺 `TG_API_ID/TG_API_HASH` 时走 fallback；
  - `xhs` 遇到 `Jina` 法规限制 451；
  - `youtube` 视频字幕接口与网络时延告警（`timeout`）。

### 2.2 执行1：Python 直连与 uv 路径对比（高可用结论）

- 方案A（当前主路径）：`REMOTE_PYTHON=/opt/homebrew/bin/python3.10`，`REMOTE_AUTOPICK_PYTHON=0`，`REMOTE_BOOTSTRAP_INSTALL=1`。
  - 结果：`RUN_ID=20260304_185014`，15/15 PASS，阻断码为空。
  - 评价：行为最稳、变更面最小，作为默认验收主路径。
- 方案B（uv 备份路径）：`REMOTE_USE_UV=1`，`REMOTE_UV_PYTHON=3.10`，`REMOTE_UV_BOOTSTRAP=1`。
  - 结果：`RUN_ID=20260304_193008`，16/16 PASS，阻断码为空。
  - 评价：可作为恢复路径，关键差异是增加 uv 引导动作；在依赖分发或权限波动时，需明确记录额外耗时与失败窗口。
- 方案C（系统级升级）：本阶段未执行系统级 Python 升级。
  - 评价：在共享或异地 VPS 上不建议优先采用，当前优先保留解释器显式化和 `REMOTE_PYTHON_MIN_VERSION=3.10` 控制。

### 两跳执行命令（异地复核）

- 入口示例（与执行脚本等价）：
```bash
sshpass -p "$VPS_PASSWORD" ssh -o StrictHostKeyChecking=no -o ConnectTimeout=15 -p 6069 "$VPS_USER@$VPS_HOST" \
  "sshpass -p '$MACMINI_PASSWORD' ssh -o StrictHostKeyChecking=no -o ConnectTimeout=15 -p '$MACMINI_PORT' '$MACMINI_USER@$MACMINI_HOST' 'bash -lc \"cd $MACMINI_DATAPULSE_DIR && $REMOTE_PYTHON -m datapulse.tools.smoke --platforms $PLATFORMS --require-all --min-confidence ${MIN_CONFIDENCE}\"'"
```

### 外部材料来源
- Mac mini 接入环境基线与运维说明见：
  - `~/Library/Mobile Documents/iCloud~md~obsidian/Documents/SunYifei/01-项目开发/openclaw-bot/mac-m4环境/基础信息.md`
- 登录与连通策略对齐：
  - `~/Library/Mobile Documents/iCloud~md~obsidian/Documents/SunYifei/01-项目开发/openclaw-bot/旺仔2号和旺仔1号登陆方式.md`
- 模型端点与路由映射见：
  - `~/Library/Mobile Documents/iCloud~md~obsidian/Documents/SunYifei/01-项目开发/openclaw-bot/mac-m4环境/模型端点配置.md`

## 3) 物料清单与账号登录指引

### 通用
- `python >= 3.10`、`playwright`（如需登录会话）、`sshpass`（可选）
- 环境变量：`~/.env.openclaw.local` 内填写真实测试入口与凭据；`.env.openclaw.example` 为脱敏模板（入库）
- `~/.env.openclaw.local` 与 `.env.openclaw.example` 均由 `.gitignore` 约定保护，严禁提交明文账号密码、口令、端点密钥
- 首选执行流程：
```bash
# 首次未建本地文件时，脚本会自动从现有环境/本地配置补齐并持久化到 .env.openclaw.local
# 如需覆盖可先 cp .env.openclaw.example .env.openclaw.local 后编辑
bash scripts/run_openclaw_remote_smoke_local.sh
```
- 可用代理时先确认 `curl -x` 到外网可达
- 兼容方式：未执行 `pip install -e .` 时，可直接运行
  - `python3 -m datapulse.cli <参数>`
  - `python3 -m datapulse.tools.smoke --list`
- 安装成功后推荐使用：
  - `datapulse`
  - `datapulse-smoke`

### 凭据管理最佳实践（本地 / VPS / 应用环境）

- 调试环境（本地复现）：
  - 仅本机 `.env.openclaw.local` 存放测试专用真实值；
  - 使用 `bash scripts/run_openclaw_remote_smoke_local.sh` 自动补齐并持久化；
  - 禁止提交 `.env.openclaw.local` 到仓库。
- VPS 过渡（两跳执行期）：
  - `VPS_*`、`MACMINI_*`、`REMOTE_*` 按会话级参数注入，不入库；
  - 口令/密钥链路参数变更先在非关键链路验证，再应用到生产路径；
- 当前异地环境下不采用 `REMOTE_DIRECT_SSH=1`；保持两跳路径（`REMOTE_DIRECT_SSH=0`）进行验证，按阻断码策略处理失败。
  - 禁止将本地 `.env.openclaw.local` 直接写入共享 CI 配置。
- 应用环境（CI/预发/生产）：
  - 不在仓库目录持久化 `VPS_*`、`MACMINI_*`、`TG_API_*`、`JINA_API_KEY`、`TAVILY_API_KEY`；
  - 通过环境注入或 secret store（如 GitHub Secrets、vault、运行时挂载）注入；
  - 保证部署端注入优先级高于 `.env.openclaw.local`。
- 对齐红线：
  - `.env.openclaw.example` 作为脱敏模板入库；
  - 验证前执行 `bash scripts/security_guardrails.sh`，避免明文凭据误入 commit。

#### 凭据分层对照（验收即用）

| 类型 | 调试环境（本地） | 应用环境（共享/CI） |
| --- | --- | --- |
| SSH 与主机 | `.env.openclaw.local` + `--export` | 环境注入（secret/环境变量） |
| OpenAPI/Search Token | 本地 `.env.openclaw.local` | 环境变量注入，按实例隔离 |
| 模板文件 | `.env.openclaw.example`（占位符） | 仅发布时使用，不改动明文 |

### 三环境补充对照（优先使用）

| 类型 | 调试环境（本地） | VPS 过渡环境 | 应用环境（共享/CI） |
| --- | --- | --- | --- |
| SSH 与主机 | `.env.openclaw.local` + `--export` | `VPS_*` / `MACMINI_*` / `REMOTE_*`（执行期） | 环境变量注入（secret/环境变量） |
| Token 与搜索服务 | 本地 `.env.openclaw.local` | 通过执行链路注入，可由脚本透传到远端 | 部署端注入 |
| 会话与端点 | 本地环境变量 | `MACMINI_HOST/MACMINI_PORT` + `REMOTE_HEALTH_URL` | 部署端配置与 secret store |
| 模板文件 | `.env.openclaw.example`（占位符） | `.env.openclaw.example`（占位符） | 仅发布时使用，不改动明文 |

执行要求：
- `bash scripts/run_openclaw_remote_smoke_local.sh`
- `bash scripts/security_guardrails.sh`

### 平台登录/凭据
- **Telegram**
  - 需要：`TG_API_ID`、`TG_API_HASH`
  - 获取方式：登录 `https://my.telegram.org`，进入 `API development tools` 创建应用获取 `api_id`、`api_hash`
  - 无法注册时可用已有账号凭据：向环境管理员确认是否已配置共享会话。
- **X/Twitter（XHS、微信）**
  - X/Twitter：默认走 FxTwitter / Nitter，不需要账号；可选提供 `NITTER_INSTANCES`
  - 小红书（XHS）：先本机执行 `datapulse --login xhs`
  - 微信公众号：先本机执行 `datapulse --login wechat`
  - 私有源可在平台侧完成账号绑定后导出可公开的 RSS/内容 URL 后再测
- **Reddit / YouTube / Bilibili / RSS**
  - 公开链路无需账号即可进行冒烟测试；建议使用公开帖子或公开视频链接。
- **微信 / 小红书会话说明**
  - 出现二维码/验证码时，按本地浏览器提示完成登录；成功后按 `Ctrl+C` 让会话落盘（便于后续复用）

### 平台登录入口与凭据来源（快速指引）
- Telegram：`https://my.telegram.org`（API development tools）
- WeChat / XHS：本机 `datapulse --login wechat|xhs`
- Reddit/YouTube/Bilibili/RSS：公开内容 URL 即可

### VPS 两跳隧道
- 建议优先使用 `~/.env.openclaw.local` 统一设置（兼容时可使用 `.env.openclaw`）：
  - `VPS_USER`
  - `VPS_HOST`
  - `VPS_PASSWORD`（如走 sshpass）
  - `VPS_PORT`（默认 `6069`）
  - `MACMINI_USER`（默认本机 `$USER`；如不同请覆盖）
  - `MACMINI_PASSWORD`（如走 sshpass）
  - `MACMINI_HOST`（默认 `127.0.0.1`；两跳默认指向 VPS 本地映射端口）
  - `MACMINI_HOST_CANDIDATES`（可选，逗号分隔，脚本会按序尝试，例如 `127.0.0.1,192.168.3.196,192.168.3.195`）
  - `MACMINI_PORT`（默认 `22`；两跳隧道常用 `2222`）
  - `MACMINI_DATAPULSE_DIR`（默认 `\$HOME/.openclaw/workspace/DataPulse`，按实际路径设置）
  - `REMOTE_PYTHON`（可选，默认 `python3`）
  - `REMOTE_BOOTSTRAP_INSTALL`（可选，`0` 关闭，`1` 在导入前执行一次 `pip install -e .`）
  - `REMOTE_INSTALL_CMD`（可选，默认 `$REMOTE_PYTHON -m pip install -e .`）
  - `REMOTE_HEALTH_URL`（可选，默认 `http://127.0.0.1:18801`）
  - `REMOTE_USE_UV`（可选，`1` 让脚本走 uv 解释器封装）
  - `REMOTE_AUTOPICK_PYTHON`（可选，默认 `1`，自动选远端可用且满足版本的 python）
  - `REMOTE_UV_PYTHON`（可选，默认 `3.10`）
  - `REMOTE_UV_BOOTSTRAP`（可选，`1` 在缺失时尝试直连 macmini 同步本机 uv 并启用兜底）
  - `REMOTE_UV_LOCAL_BINARY`（可选，直连同步时优先使用的本机 uv 路径，默认自动探测）
  - `REMOTE_UV_INSTALL_ROOT`（可选，直连同步目标目录，默认 `\$HOME/.local/bin`）
  - `REMOTE_PIP_EXTRAS`（可选，补齐平台依赖；如 `telegram,youtube,browser,all`）
  - `SSH_CONNECT_TIMEOUT`（可选，SSH 连接超时秒数，默认 `8`）
  - `REMOTE_ABORT_ON_CONNECT_FAIL`（可选，默认 `1`，首次连通性失败直接终止并写阻断码）
  - 当前环境注记：异地链路不支持内网直连，建议固定 `REMOTE_DIRECT_SSH=0`，仅两跳测试
  - 若未显式设置，脚本会按 `PLATFORMS` 自动推导：
    - `telegram` -> `telegram`
    - `youtube` -> `youtube`
    - `wechat/xhs` -> `browser`
  - 对应输出：`REMOTE_PIP_EXTRAS_AUTO=telegram,youtube,browser`
  - `REMOTE_PIP_NO_PROXY`（可选，默认 `*`；仅在远端执行命令时注入 `NO_PROXY`/`PIP_NO_PROXY`，不修改系统全局）
  - `REMOTE_DIRECT_SSH`（可选，`0` 默认两跳，`1` 改为内网直连；当前环境禁止启用）
- 两跳隧道与直连模式兼容：当 `REMOTE_DIRECT_SSH=1` 时，可不设置 `VPS_USER/VPS_HOST`，脚本仅走 `MACMINI_HOST:MACMINI_PORT`。当前异地路径不应启用该模式。
- `MACMINI_HOST_CANDIDATES` 用于异地链路回退，按列表顺序尝试候选 IP（例如先 `127.0.0.1`，再 `192.168.3.196`，最后 `192.168.3.195`）。
- 认证方式：
  - 口令认证（sshpass）
    - 需要安装 `sshpass`
    - 示例见下方 `sshpass` 命令
  - 密钥认证（推荐）
    - 本机执行以下任一：
      - `ssh-keygen -t ed25519 -f ~/.ssh/datapulse_test_ed25519`
      - `ssh-copy-id -i ~/.ssh/datapulse_test_ed25519.pub -p "${VPS_PORT:-6069}" "${VPS_USER}@${VPS_HOST}"`
      - `ssh-copy-id -o "ProxyJump=${VPS_USER}@${VPS_HOST}:${VPS_PORT:-6069}" -p "${MACMINI_PORT:-22}" "${MACMINI_USER}@${MACMINI_HOST}"`
- 连通性检查（执行在本机）：
```bash
  ssh -o StrictHostKeyChecking=no -p "${VPS_PORT:-6069}" "$VPS_USER@$VPS_HOST" "echo ok"
  ssh -o StrictHostKeyChecking=no -J "$VPS_USER@$VPS_HOST:${VPS_PORT:-6069}" -p "${MACMINI_PORT:-22}" "$MACMINI_USER@$MACMINI_HOST" "echo ok"
  sshpass -p "<VPS口令>" ssh -o StrictHostKeyChecking=no -o ConnectTimeout=15 -p "${VPS_PORT:-6069}" "$VPS_USER@$VPS_HOST" "sshpass -p '<MacMini口令>' ssh -o StrictHostKeyChecking=no -o ConnectTimeout=15 -p ${MACMINI_PORT:-2222} $MACMINI_USER@$MACMINI_HOST 'echo ok'"
```

### 内网直连（补充）
- 如网络条件满足（同网段）可在内网直接 SSH 到 Mac Mini（无需两跳）进行可达性与快速修复验证；当前环境建议先以两跳为主。
- 建议在 `.env.openclaw.local` 中补充（脱敏写法）：
- `MACMINI_HOST=<内网IP>`
  - `MACMINI_PORT=22`
  - `MACMINI_USER=<同macmini系统用户>`
- 直连连通性快速检查：
```bash
export REMOTE_DIRECT_SSH=1
export MACMINI_HOST=<内网IP>
export MACMINI_PORT=22
export MACMINI_USER=<macmini-user>
export MACMINI_PASSWORD=<macmini-口令>   # 可选，口令访问；无口令可走密钥
bash scripts/datapulse_remote_openclaw_smoke.sh  # 两跳不可用时启用
```

```bash
sshpass -p "<MacMini口令>" ssh -o StrictHostKeyChecking=no -p "${MACMINI_PORT:-22}" "$MACMINI_USER@$MACMINI_HOST" "pwd && python3 --version && curl -fsS http://127.0.0.1:18801/healthz"
```

- 直连验证可直接启用 `REMOTE_UV_BOOTSTRAP=1`，脚本会优先尝试将本机 `uv` 二进制同步到远端，再回退到远端 `python -m pip install --user uv`：
```bash
export REMOTE_DIRECT_SSH=1
export REMOTE_UV_BOOTSTRAP=1
export MACMINI_USER=<macmini-user>
export MACMINI_HOST=<内网IP>
export MACMINI_PASSWORD=<macmini-口令或密钥免密访问>
export REMOTE_PYTHON=python3
export REMOTE_UV_INSTALL_ROOT=~/.local/bin
export REMOTE_UV_LOCAL_BINARY=$(command -v uv)
bash scripts/datapulse_remote_openclaw_smoke.sh
```
- 说明：若 `LOCAL uv` 平台与目标主机不一致（如 x86_64 vs arm64），脚本会自动降级到 `python3 -m pip install --user uv`，保持验证闭环。

- `scripts/datapulse_remote_openclaw_smoke.sh` 的代理修复是“命令级注入”：在每次 `run_remote` 发送的远端命令前临时设置 `HTTPS_PROXY/HTTP_PROXY/ALL_PROXY=空` 且 `NO_PROXY='*'`，不会影响 macmini 上其它长期进程。

- 注意：脚本同时支持两跳与直连模式；当前优先用两跳（直连受制于本机网段）。内网直连主要用于
  - 临时修复/验证
  - 与脚本阻断码结论交叉比对
  - 降低两跳不可用时的初级排障成本
- 脚本还会尝试远端 python 自适应与 `MACMINI_DATAPULSE_DIR` 兜底定位（含 `DataPulse` 子目录），以减少手工设置偏差。

### 远端源码与依赖恢复（高可用）

- 远端阻塞根因若为 `ModuleNotFoundError: No module named 'datapulse'`，可先执行：
```bash
export MACMINI_DATAPULSE_DIR="\$HOME/.openclaw/workspace/DataPulse"
export REMOTE_BOOTSTRAP_INSTALL=1
bash scripts/datapulse_remote_openclaw_smoke.sh
```
- 若出现“远端 python 版本 <3.10”，可改为 uv 路径执行：
```bash
export REMOTE_USE_UV=1
export REMOTE_UV_PYTHON=3.10
export REMOTE_BOOTSTRAP_INSTALL=1
bash scripts/datapulse_remote_openclaw_smoke.sh
```
- 与 `PLATFORMS` 自动推导能力配套，典型一键补齐动作：
```bash
export PLATFORMS="twitter reddit bilibili telegram wechat xhs youtube"
unset REMOTE_PIP_EXTRAS
export REMOTE_BOOTSTRAP_INSTALL=1
bash scripts/datapulse_remote_openclaw_smoke.sh
```
- 若出现 `Telethon not installed` / `youtube-transcript-api` 相关可在安装阶段补齐依赖后复测：
```bash
export REMOTE_PIP_EXTRAS=telegram,youtube
export REMOTE_BOOTSTRAP_INSTALL=1
bash scripts/datapulse_remote_openclaw_smoke.sh
```
- 如需把修复动作记录为快检动作，可先验证：
```bash
sshpass -p "<VPS口令>" ssh -o StrictHostKeyChecking=no -p "${VPS_PORT:-6069}" "${VPS_USER}@${VPS_HOST}" \
  "sshpass -p '<MacMini口令>' ssh -o StrictHostKeyChecking=no -p ${MACMINI_PORT:-2222} ${MACMINI_USER}@${MACMINI_HOST} \
  'test -d \"${MACMINI_DATAPULSE_DIR}\" && test -d \"${MACMINI_DATAPULSE_DIR}/datapulse\" && [ -f \"${MACMINI_DATAPULSE_DIR}/pyproject.toml\" ] && python3 -m pip --version && python3 -m datapulse.tools.smoke --list'"
```
- 远端脚本会输出阻断码（示例）：`PACKAGE_MISSING`、`PYTHON_VERSION_TOO_LOW`、`IMPORT_FAILED`。

### OpenClaw/OpenModel 端点
- Runtime 状态检测：`curl -sS http://127.0.0.1:18801/healthz`
- 就绪检测：`curl -sS http://127.0.0.1:18801/readyz`
- 工具链目标（28 个 MCP 工具）：`read_url` / `read_batch` / `read_url_advanced` / `search_web` / `trending` / `query_inbox` / `mark_processed` / `query_unprocessed` / `list_sources` / `list_packs` / `resolve_source` / `list_subscriptions` / `source_subscribe` / `source_unsubscribe` / `install_pack` / `query_feed` / `build_json_feed` / `build_rss_feed` / `build_atom_feed` / `build_digest` / `emit_digest_package` / `extract_entities` / `query_entities` / `entity_graph` / `entity_stats` / `doctor` / `detect_platform` / `health`
- 远端预检（建议在 `bash scripts/datapulse_remote_openclaw_smoke.sh` 前执行）：
  - `MACMINI_DATAPULSE_DIR` 下必须有 `pyproject.toml` 和 `datapulse/`
  - 远端 Python 版本必须 `>=3.10`
  - `python3 -m datapulse.tools.smoke --list` 能够输出场景列表
  - `curl -fsS ${REMOTE_HEALTH_URL}/healthz` 与 `curl -fsS ${REMOTE_HEALTH_URL}/readyz` 通透

#### MCP 调用示例（可直接复制）

```bash
python3 -m datapulse.mcp_server --stdio << 'PY'
{"jsonrpc":"2.0","id":"01","method":"tools/call","params":{"name":"search_web","arguments":{"query":"openclaw data pipeline","limit":5,"provider":"auto","mode":"single","fetch_content":true}}}
PY
```

```bash
python3 -m datapulse.mcp_server --stdio << 'PY'
{"jsonrpc":"2.0","id":"02","method":"tools/call","params":{"name":"read_url_advanced","arguments":{"url":"https://www.reddit.com/r/MachineLearning/comments/...","target_selector":"article","with_alt":false,"min_confidence":0.0}}}
PY
```

```bash
python3 -m datapulse.mcp_server --stdio << 'PY'
{"jsonrpc":"2.0","id":"02b","method":"tools/call","params":{"name":"search_web","arguments":{"query":"AI 开发工作流","provider":"auto","mode":"multi","limit":3,"extract_entities":true,"entity_mode":"fast","store_entities":true}}}
PY
```

```bash
python3 -m datapulse.mcp_server --stdio << 'PY'
{"jsonrpc":"2.0","id":"03","method":"tools/call","params":{"name":"trending","arguments":{"location":"us","top_n":10,"validate":true,"validate_mode":"strict"}}}
PY
```

```bash
python3 -m datapulse.mcp_server --stdio << 'PY'
{"jsonrpc":"2.0","id":"04","method":"tools/call","params":{"name":"read_url","arguments":{"url":"https://beewebsystems.com/","min_confidence":0.0}}}
PY
```

```bash
python3 -m datapulse.mcp_server --stdio << 'PY'
{"jsonrpc":"2.0","id":"05","method":"tools/call","params":{"name":"read_batch","arguments":{"urls":["https://chatprd.ai/","https://uxpilot.ai/"],"min_confidence":0.0}}}
PY
```

```bash
python3 -m datapulse.mcp_server --stdio << 'PY'
{"jsonrpc":"2.0","id":"06","method":"tools/call","params":{"name":"doctor","arguments":{}}}
PY
```

### 来源与聚合能力核查（可选）
- 对齐目标：建立本地化的源目录、订阅关系与 Feed 订阅输出闭环。
- 参考材料：`docs/source_feed_enhancement_plan.md`

#### 来源能力必测点（建议）
- Source 解析：验证输入 URL 可自动归类为 `type/config`（例如 RSS/Feed/站点 URL）。
- Source 管理：验证公开/私有来源、订阅关系可配置。
- Feed 输出：验证 JSON Feed 与 RSS 风格导出路径（本地约定路径）。
- API 安全：写入口与鉴权边界（关键操作需明确权限位）。

#### 本地能力核查（DataPulse 等价）
- `datapulse --list-sources`：支持 `public_only` / `include_inactive`。
- `datapulse --resolve-source <url>`：返回解析类型和配置信息。
- `datapulse --source-subscribe / --source-unsubscribe`：订阅关系可变更。
- `datapulse --list-packs` 与 `--install-pack`：支持源组导入。
- `datapulse --query-feed`：输出 JSON Feed。
- `datapulse --query-rss`：输出 RSS。

## 4) 本机验收
- 执行脚本：`bash scripts/datapulse_local_smoke.sh`
- [ ] `datapulse-smoke --list` 可执行
- [ ] `bash scripts/run_xhs_quality_report.sh` 生成 `artifacts/xhs_quality_<RUN_ID>/*` 与高可读复核输出
- [ ] `datapulse --list --limit 5` 返回可读结果
- [ ] `datapulse --batch` 通过
- [ ] `datapulse-smoke --platforms ... --require-all` 通过
- [ ] `datapulse --search "test query" --search-limit 3 --search-provider auto` 返回搜索结果（如遇 provider 限制，请配置对应 `JINA_API_KEY` 或 `TAVILY_API_KEY`）
- [ ] `datapulse --trending us --trending-limit 10` 返回热搜趋势
- [ ] `datapulse <url> --target-selector "main"` 定向抓取通过
- [ ] `DataPulseAgent` 返回 JSON 风格 payload（status/count/items）
- [ ] `datapulse_skill.run()` 输出可读摘要

## 5) 远端接入验收
- [ ] VPS 两跳 SSH 成功
- [ ] Runtime 18801：`curl -sS http://127.0.0.1:18801/healthz`
- [ ] `bash scripts/datapulse_remote_openclaw_smoke.sh` 完整通过
  - 运行前先确认 `MACMINI_DATAPULSE_DIR` 指向 macmini 上可访问且含有 `datapulse` 源码目录。
- [ ] 远端 `python3 -m datapulse.tools.smoke --list` 输出正常
- [ ] 18801 健康端检查通过
- [ ] `read_url` / `read_batch` MCP 工具返回 JSON
- [ ] `search_web` MCP 工具返回搜索结果 JSON
- [ ] `read_url_advanced` MCP 工具定向抓取返回 JSON
- [ ] `trending` MCP 工具返回热搜趋势 JSON
- [ ] `query_feed` / `build_json_feed` / `build_rss_feed` / `build_atom_feed` Feed 输出正常
- [ ] `build_digest` 精选摘要返回 JSON
- [ ] `emit_digest_package` 产出 office-ready payload（`json`/`markdown`）正常
- [ ] `doctor` MCP 工具返回采集器健康分组报告
- [ ] `list_sources` / `resolve_source` / `list_subscriptions` 信源管理正常
- [ ] `mark_processed` / `query_unprocessed` 状态管理正常
- [ ] `extract_entities` 返回实体抽取结果，支持 `fast`/`llm`
- [ ] `query_entities` 可按 `entity_type/name` 查询实体
- [ ] `entity_graph` 输出实体关系闭环
- [ ] `entity_stats` 返回实体存储汇总
- [ ] OpenClaw 工具入口可被网关启动并返回结构化结果

## 6) 结果记录

| 项目 | 结果 | 备注 |
|---|---|---|
| 本机 smoke | PASS/FAIL | |
| 远端 smoke | PASS/FAIL | |
| MCP read_url | PASS/FAIL | |
| MCP read_batch | PASS/FAIL | |
| MCP search_web | PASS/FAIL | |
| MCP read_url_advanced | PASS/FAIL | |
| MCP trending | PASS/FAIL | |
| MCP Feed 输出 (json/rss/atom) | PASS/FAIL | |
| MCP build_digest | PASS/FAIL | |
| MCP emit_digest_package | PASS/FAIL | |
| MCP doctor | PASS/FAIL | |
| MCP 信源管理 (sources/subs) | PASS/FAIL | |
| MCP 状态管理 (processed) | PASS/FAIL | |
| MCP 实体工具 (extract/query/graph/stats) | PASS/FAIL | |
| Skill run | PASS/FAIL | |
| Agent handle | PASS/FAIL | |

## 7) 风险与遗留
- 远端测试阻塞主因目前集中在两类：
  - `MACMINI_DATAPULSE_DIR` 未指向源码目录（含 `datapulse/`）
  - 远端 Python 版本低于 `3.10`
- 复测前建议锁定：
  - SSH 通道与端口、Runtime 授权及代理路径
  - 依赖版本与 `pip install -e .` 覆盖范围（至少核心入口）
- 先以 `MACMINI_DATAPULSE_DIR=$HOME/.openclaw/workspace/DataPulse` 做 smoke，若仍失败再回退确认 `MACMINI_USER` 是否有权限访问该路径
- 现有风险闭环：
  - 已在验收脚本输出中加入阻断码，便于自动归档和链路回归定位
