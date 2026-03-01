# DataPulse + OpenClaw 远程接入验收模板（macmini M4）

> 生成时间：`2026-02-24`

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
  - `DATAPULSE_SMOKE_YOUTUBE_URL`
  - `DATAPULSE_SMOKE_BILIBILI_URL`
  - `DATAPULSE_SMOKE_TELEGRAM_URL`
  - `DATAPULSE_SMOKE_RSS_URL`
  - `DATAPULSE_SMOKE_WECHAT_URL`
  - `DATAPULSE_SMOKE_XHS_URL`

### 外部材料来源
- Mac mini 接入环境基线与运维说明见：
  - `~/Library/Mobile Documents/iCloud~md~obsidian/Documents/SunYifei/01-项目开发/openclaw-bot/mac-m4环境/基础信息.md`
- 模型端点与路由映射见：
  - `~/Library/Mobile Documents/iCloud~md~obsidian/Documents/SunYifei/01-项目开发/openclaw-bot/mac-m4环境/模型端点配置.md`

## 3) 物料清单与账号登录指引

### 通用
- `python >= 3.10`、`playwright`（如需登录会话）、`sshpass`（可选）
- 环境变量：`~/.env.openclaw`（或 `.env.local`、`.env.secret`）内填写测试入口与凭据
- `~/.env.openclaw` 与 `.env.local/.env.secret` 已配置在 `.gitignore`，严禁提交明文账号密码、口令、端点密钥
- 可用代理时先确认 `curl -x` 到外网可达
- 兼容方式：未执行 `pip install -e .` 时，可直接运行
  - `python3 -m datapulse.cli <参数>`
  - `python3 -m datapulse.tools.smoke --list`
- 安装成功后推荐使用：
  - `datapulse`
  - `datapulse-smoke`

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
- 建议使用 `~/.env.openclaw` 统一设置：
  - `VPS_USER`
  - `VPS_HOST`
  - `VPS_PASSWORD`（如走 sshpass）
  - `VPS_PORT`（默认 `6069`）
  - `MACMINI_USER`（默认本机 `$USER`；如不同请覆盖）
  - `MACMINI_PASSWORD`（如走 sshpass）
  - `MACMINI_HOST`（默认 `127.0.0.1`；如采用直连按实际内网 IP 配置）
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
  - 若未显式设置，脚本会按 `PLATFORMS` 自动推导：
    - `telegram` -> `telegram`
    - `youtube` -> `youtube`
    - `wechat/xhs` -> `browser`
  - 对应输出：`REMOTE_PIP_EXTRAS_AUTO=telegram,youtube,browser`
  - `REMOTE_PIP_NO_PROXY`（可选，默认 `*`；仅在远端执行命令时注入 `NO_PROXY`/`PIP_NO_PROXY`，不修改系统全局）
  - `REMOTE_DIRECT_SSH`（可选，`0` 默认两跳，`1` 改为内网直连）
- 两跳隧道与直连模式兼容：当 `REMOTE_DIRECT_SSH=1` 时，可不设置 `VPS_USER/VPS_HOST`，脚本仅走 `MACMINI_HOST:MACMINI_PORT`。
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
  sshpass -p "<VPS口令>" ssh -o StrictHostKeyChecking=no -p "${VPS_PORT:-6069}" "$VPS_USER@$VPS_HOST" "sshpass -p '<MacMini口令>' ssh -o StrictHostKeyChecking=no -p ${MACMINI_PORT:-2222} $MACMINI_USER@$MACMINI_HOST 'echo ok'"
```

### 内网直连（补充）
- 如网络条件满足（同网段）可在内网直接 SSH 到 Mac Mini（无需两跳）进行可达性与快速修复验证；当前环境建议先以两跳为主。
- 建议在 `.env.openclaw`/`.env.secret`中补充（脱敏写法）：
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
- 工具链目标：MCP `read_url/read_batch/search_web/read_url_advanced/trending/query_inbox/detect_platform/list_sources/list_packs/query_feed/build_json_feed/build_rss_feed/build_atom_feed/build_digest/health`
- 远端预检（建议在 `bash scripts/datapulse_remote_openclaw_smoke.sh` 前执行）：
  - `MACMINI_DATAPULSE_DIR` 下必须有 `pyproject.toml` 和 `datapulse/`
  - 远端 Python 版本必须 `>=3.10`
  - `python3 -m datapulse.tools.smoke --list` 能够输出场景列表
  - `curl -fsS ${REMOTE_HEALTH_URL}/healthz` 与 `curl -fsS ${REMOTE_HEALTH_URL}/readyz` 通透

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
- [ ] `datapulse --list --limit 5` 返回可读结果
- [ ] `datapulse --batch` 通过
- [ ] `datapulse-smoke --platforms ... --require-all` 通过
- [ ] `datapulse --search "test query" --search-limit 3` 返回搜索结果（需 `JINA_API_KEY`）
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
- [ ] `read_url/read_batch` MCP 工具返回 JSON
- [ ] `search_web` MCP 工具返回搜索结果 JSON
- [ ] `read_url_advanced` MCP 工具定向抓取返回 JSON
- [ ] `trending` MCP 工具返回热搜趋势 JSON
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
