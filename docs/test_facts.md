---
title: Test Facts
---

<a id="top"></a>

# Test Facts / 测试事实

[🔙 返回主 README](../README.md) | [🔄 中文对照/English](../README_CN.md) | [⬆️ 回到顶部](#top)

## Fact 1: Configuration policy / 配置规范

本仓库不公开本地测试环境和模型端点明文；敏感项仅允许在私有运行时注入。
- Repository policy: no plaintext local test environment/model endpoint values are published in-repo.

## Fact 2: Functionality verification / 功能验证

建议先执行 `datapulse` CLI 单测 → 批量测试 → `datapulse-smoke --list/--platforms` 验证平台适配度。
- Recommended order: CLI single URL checks → batch checks → `datapulse-smoke --list/--platforms`.

## Fact 2.1: 无安装入口兜底

- 本机未执行 `pip install -e .` 时，可直接运行：
  - `python3 -m datapulse.cli <参数>`
  - `python3 -m datapulse.tools.smoke --list`
- 远端脚本已内置 `python3 -m` 调用，默认可在两跳场景下直接执行 smoke。

## Fact 3: OpenClaw 接入验收（Mac Mini M4）

- 已提供本机与远端统一测试脚本：
  - `scripts/datapulse_local_smoke.sh`（本机）
  - `scripts/datapulse_remote_openclaw_smoke.sh`（VPS 两跳隧道到 macmini）
- 已提供验收模板：`docs/openclaw_datapulse_acceptance_template.md`
- 物料与账号指引集中在验收模板：
  - `~/Library/Mobile Documents/iCloud~md~obsidian/Documents/SunYifei/01-项目开发/DataPulse/DataPulse_OpenClaw_接入验收手册.md`
- 远端建议按以下顺序执行（建议保存 LOG）：
  - `bash scripts/datapulse_local_smoke.sh`
  - `bash scripts/datapulse_remote_openclaw_smoke.sh`
  - 本机与远端凭据请放在 `.env.openclaw`（或 `.env.local` / `.env.secret`），并在 `.gitignore` 声明，不入库
  - 建议素材：
    - `URL_1=https://beewebsystems.com/`
    - `URL_BATCH='https://chatprd.ai/ https://beewebsystems.com/ https://uxpilot.ai/'`
    - `DATAPULSE_SMOKE_TWITTER_URL=https://x.com/everestchris6/status/2025995047729254701`
  - 账号与登录：
    - Telegram（私有场景）：`TG_API_ID`、`TG_API_HASH`（来自 `my.telegram.org`）
    - WeChat/XHS：本机运行 `datapulse --login wechat|xhs`
    - Reddit/YouTube/Bilibili/RSS：默认公开链路不需要账号
- 远端执行前先确认模型路由 Runtime 18801 可达：
  - `curl -sS http://127.0.0.1:18801/healthz`
  - `curl -sS http://127.0.0.1:18801/readyz`
  - 统一验收手册（外部 Obsidian 文档）：
  - 主文档：`~/Library/Mobile Documents/iCloud~md~obsidian/Documents/SunYifei/01-项目开发/DataPulse/DataPulse_OpenClaw_接入验收手册.md`
  - 兼容镜像：`~/Library/Mobile Documents/iCloud~md~obsidian/Documents/SunYifei/01-项目开发/openclaw-bot/mac-m4环境/DataPulse_OpenClaw_接入验收手册.md`
- 环境与端点主事实来源：
  - `~/Library/Mobile Documents/iCloud~md~obsidian/Documents/SunYifei/01-项目开发/openclaw-bot/mac-m4环境/基础信息.md`
  - `~/Library/Mobile Documents/iCloud~md~obsidian/Documents/SunYifei/01-项目开发/openclaw-bot/mac-m4环境/模型端点配置.md`
- 已执行快照（2026-02-24）：
  - 本机：`PASS=10 FAIL=1`（缺口：缺少 7 个 `DATAPULSE_SMOKE_*`）
  - 远端：`FAIL`（阻断链路定位到 `ModuleNotFoundError: No module named 'datapulse'`）
  - 远端记录值（高敏信息不入库）：`VPS_HOST=<VPS_HOST>`，`MACMINI_HOST=<MACMINI_HOST>`，`MACMINI_DATAPULSE_DIR=<MACMINI_DATAPULSE_DIR>`
  - 远端 Python（检测值）：`3.9.6`，低于 `requires-python >=3.10`
- 远端高可用预检说明（已加入脚本）：
  - 检查 `MACMINI_DATAPULSE_DIR` 目录存在性（含 `pyproject.toml` 与 `datapulse/`）
  - 检查远端 Python 版本是否 >= 3.10
  - 检查 `python3 -m datapulse.tools.smoke` 入口可达性前的 import 成功性
  - 失败时输出阻断标记（如 `PYTHON_VERSION_TOO_LOW` / `PACKAGE_MISSING` / `IMPORT_FAILED`）

## Fact 3.1: 远端复测关键配置锚点

- 建议校准配置（不入库）：
  - `MACMINI_DATAPULSE_DIR=<remote_workspace>/DataPulse`
  - `REMOTE_PYTHON=python3`（目标机器需满足 3.10+）
  - `REMOTE_BOOTSTRAP_INSTALL=1`（可选，修复 `datapulse` 模块缺失时先执行一次 `pip install -e .`）
  - `REMOTE_HEALTH_URL=http://127.0.0.1:18801`
  - `VPS_HOST=<VPS_HOST>`、`MACMINI_HOST=<MACMINI_HOST>`（当前两跳链路观测值）
- 若环境不可切换，请先确认：
  - SSH 口令/密钥方式可达
  - Runtime `/healthz` 与 `/readyz` 连通

## Fact 3.3: 远端高可用阻断码

- `PYTHON_VERSION_TOO_LOW`：远端解释器低于 `3.10`，请切换到 >=3.10 解释器或使用虚拟环境。
- `DATAPULSE_DIR_NOT_FOUND`：当前 `MACMINI_DATAPULSE_DIR` 不可达或路径错误，请先 `ls` 链接到真实仓库根。
- `PACKAGE_MISSING`：路径存在但未包含 `pyproject.toml` 或 `datapulse/`，请修正为源码根目录。
- `IMPORT_FAILED`：源码可见但 `datapulse` 无法导入，多半是依赖未安装或 `pip` 环境错配，请检查 `REMOTE_BOOTSTRAP_INSTALL` 与 `pip install -e .`。

## Fact 4: 来源与订阅能力增强

- 已形成统一落地清单：`docs/source_feed_enhancement_plan.md`。
- 对齐重点：源解析与源组、订阅关系、Feed 输出、标记/反馈闭环、安全边界。
- 推荐执行顺序：
  - 先在项目内补齐源列表配置与批量导入流程（P0）。
  - 再补齐 JSON Feed/RSS 输出自检（P1）。
  - 最后补齐 marks/feedback 反馈闭环（P2）。

## Fact 3.4: 远端测试环境 HA 可用事实（按官方实践对齐）

### 已确认高置信事实

- 远端入口必须走 VPS 两跳（`ssh -J` / `ProxyJump` 方式）；官方 `ssh_config`/`ssh(1)` 都将该方式定义为“先连跳板后到目标的顺序链路”，适配可写成命令行 `-J` 或配置项 `ProxyJump`。
- 远端需把源码路径作为本机可执行测试上下文（`MACMINI_DATAPULSE_DIR` 指向源码根，含 `pyproject.toml` 与 `datapulse/`）。
- 远端 Python 版本必须满足项目元数据要求（`requires-python` 当前链路要求 `>=3.10`），否则入口导入阶段不应继续。
- 两跳通道与服务可达建议用独立敏感环境变量文件承载（`.env.openclaw` / `.env.local` / `.env.secret`），脚本已支持且不会读取明文入库。
- Runtime 健康检查建议通过 `curl` 指定 `/healthz`、`/readyz` 做层级可观测；已在远端脚本中形成前置阻断点与阻断码。

### 当前阻塞事实与修复动作（高置信）

- 阻塞主因：远端 Python 仍是 `3.9.6`，脚本级阻断码 `PYTHON_VERSION_TOO_LOW`。
  - 修复动作：在远端切换到 3.10+ 解释器（示例 `python3.11`），并将 `REMOTE_PYTHON` 指向对应解释器。
- 阻塞主因二：`ModuleNotFoundError: No module named 'datapulse'`。
  - 修复动作：确认 `MACMINI_DATAPULSE_DIR` 指向 `pyproject.toml` 与 `datapulse/` 同级源码根；必要时执行 `REMOTE_BOOTSTRAP_INSTALL=1` 触发一次 `pip install -e .`。
- 阻塞主因三：SSH 认证与端口参数不匹配（两跳参数变更）。
  - 修复动作：优先改为密钥链路；如继续口令链路，确保 VPS 与跳板 `sshpass` 两段参数一致。

### 官方实践映射（对齐）

- Python 可执行安装：在远端先建立隔离环境（`python3 -m venv`），用该解释器执行 `python3 -m pip install -e .`（官方 Python 文档/Packaging 指南推荐）。
- SSH 两跳隧道：`ssh -J` / `ProxyJump` 是 OpenSSH 标准链路模型；命令链路与配置链路保持一致。
- 可见性与可恢复性：远端脚本已将 `DATAPULSE_DIR_NOT_FOUND` / `PYTHON_VERSION_TOO_LOW` / `PACKAGE_MISSING` / `IMPORT_FAILED` 等阻断码固化，便于自动归档与复测闭环。

[⬆️ Back to top / 返回顶部](#top) | [🔙 返回主 README](../README.md) | [🔄 中文对照/English](../README_CN.md)
