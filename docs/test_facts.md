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
- 版本兼容增强：`scripts/datapulse_remote_openclaw_smoke.sh` 已支持 `REMOTE_USE_UV=1` 触发 `uv run --project ... --python ... -- python ...` 执行链路，可用于远端 3.9.x 环境的兼容尝试。
- 环境与端点主事实来源：
  - `~/Library/Mobile Documents/iCloud~md~obsidian/Documents/SunYifei/01-项目开发/openclaw-bot/mac-m4环境/基础信息.md`
  - `~/Library/Mobile Documents/iCloud~md~obsidian/Documents/SunYifei/01-项目开发/openclaw-bot/mac-m4环境/模型端点配置.md`
- 已执行快照（2026-02-24）：
  - 本机：`PASS=10 FAIL=1`（缺口：缺少 7 个 `DATAPULSE_SMOKE_*`）
- 历史快照（修复前）：`FAIL`（阻断链路定位到 `ModuleNotFoundError: No module named 'datapulse'`）
- 历史快照（修复前）：`FAIL`（当前卡点定位到 `pip install -e .` 构建依赖下载失败：`hatchling` 拉取阶段走代理失败，返回 `ProxyError: Cannot connect to proxy`）
  - 远端记录值（高敏信息不入库）：`VPS_HOST=<VPS_HOST>`，`MACMINI_HOST=<MACMINI_HOST>`，`MACMINI_DATAPULSE_DIR=<MACMINI_DATAPULSE_DIR>`
  - 远端 Python（检测值）：已发现 `python3.10` 可用，示例 `/opt/homebrew/bin/python3.10`，但安装链路仍需修复构建依赖代理配置。
- 远端：`PASS`（两跳链路 + 脚本内命令级代理隔离后；`remote_test` 能到达 MCP/Agent/skill 与 OpenClaw 健康检查）
- 远端最近一轮执行残留卡点：`telegram` 平台未装 `Telethon`、`xhs` 在当前会话下无回退会话、`bilibili` 依赖数据不足导致个别内容抓取退化；属于平台能力/依赖与网络策略类非链路阻塞。
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
  - `REMOTE_PIP_EXTRAS=telegram,youtube`（按需补齐平台可选依赖）
  - `REMOTE_HEALTH_URL=http://127.0.0.1:18801`
  - `VPS_HOST=<VPS_HOST>`、`MACMINI_HOST=<MACMINI_HOST>`（当前两跳链路观测值）
- 远端脚本补齐策略（新增）：
  - 当 `REMOTE_PIP_EXTRAS` 为空时，脚本按 `PLATFORMS` 自动推导：`telegram` -> `telegram`、`youtube` -> `youtube`、`wechat/xhs` -> `browser`。
  - 由脚本输出：`REMOTE_PIP_EXTRAS_AUTO=<自动列表>`，可直接复用当前运行链路而无需手工维护。
- 若环境不可切换，请先确认：
  - SSH 口令/密钥方式可达
  - Runtime `/healthz` 与 `/readyz` 连通

## Fact 3.3: 远端高可用阻断码

- `PYTHON_VERSION_TOO_LOW`：远端解释器低于 `3.10`，请切换到 >=3.10 解释器或使用虚拟环境。
- `DATAPULSE_DIR_NOT_FOUND`：当前 `MACMINI_DATAPULSE_DIR` 不可达或路径错误，请先 `ls` 链接到真实仓库根。
- `PACKAGE_MISSING`：路径存在但未包含 `pyproject.toml` 或 `datapulse/`，请修正为源码根目录。
- `IMPORT_FAILED`：源码可见但 `datapulse` 无法导入，多半是依赖未安装或 `pip` 环境错配，请检查 `REMOTE_BOOTSTRAP_INSTALL` 与 `pip install -e .`。
- `REMOTE_PLATFORM_DEPENDENCY_MISSING`（日志提示类）：`datapulse` 某平台 collector 缺少依赖（如 `Telethon`、`youtube-transcript-api`）；建议设置 `REMOTE_PIP_EXTRAS=telegram,youtube` 后复测。
- `BUILD_DEPENDENCY_PROXY_FAIL`：`pip install -e .` 阶段构建依赖（例如 `hatchling`）通过代理访问 `pypi` 失败。  
  修复动作：在远端执行命令前显式清理 `HTTP(S)_PROXY` 与 `ALL_PROXY`，或确认 `127.0.0.1:7897` 端口可用。
- `REMOTE_COMMAND_PROXY_ISOLATED`：代理修复采用“仅注入到远端命令执行上下文”的模式（`NO_PROXY="*"` + 清空 `HTTPS_PROXY/HTTP_PROXY/ALL_PROXY/...`）；不修改 macmini 长期系统代理配置，不影响系统其他进程。

## Fact 3.6: v0.5.0 能力增量

- **Jina 增强读取**：`JinaAPIClient`（`datapulse/core/jina_client.py`）封装 Reader + Search API，支持 CSS 选择器定向（`X-Target-Selector`）、等待元素（`X-Wait-For-Selector`）、缓存控制（`X-No-Cache`）、AI 图片描述（`X-With-Generated-Alt`）、Cookie 透传、代理。
- **Web 搜索**：`DataPulseReader.search()` 通过 Jina Search API（`s.jina.ai`）搜索全网，返回经评分排序的 `DataPulseItem` 列表。CLI `--search` / MCP `search_web`。
- **GenericCollector 回退链增强**：Trafilatura → BS4 → Firecrawl → Jina Reader → fail。
- **新增 MCP 工具**：`search_web`、`read_url_advanced`。
- **新增 CLI 参数**：`--search`、`--site`、`--search-limit`、`--no-fetch`、`--target-selector`、`--no-cache`、`--with-alt`。
- **新增 56 个测试**（`test_jina_client.py` 29 + `test_jina_collector_enhanced.py` 17 + `test_jina_search.py` 10），总计 351+。
- **零新依赖**：全部使用 `requests`（已有）+ 标准库。

## Fact 3.7: v0.5.1 XHS 蒸馏能力增量

- **XHS Engagement 提取**：`_extract_engagement()` 正则匹配中英文互动指标（赞/评论/收藏/分享），写入 `extra["engagement"]`。
- **平台感知搜索**：`search()` 新增 `platform` 参数（xhs/twitter/reddit/hackernews/arxiv/bilibili），自动注入域名限定。CLI `--platform`、MCP `search_web` 工具同步更新。
- **XHS 媒体 Referer 注入**：新建 `datapulse/core/media.py`，检测 xhscdn.com 等域名自动注入 Referer header + 流式下载。
- **Session TTL 缓存**：`session_valid()` 12h 正向缓存，避免频繁文件系统检查。`DATAPULSE_SESSION_TTL_HOURS` 可配置。
- **engagement_metrics 置信度标志**：新增 confidence flag (+0.03)，抵消 Jina proxy 惩罚，XHS 恢复 baseline 0.72。
- **新增 22 个测试**（`test_xhs_engagement.py` 8 + `test_media.py` 8 + confidence 3 + search 5 + utils 5 = 29 用例），总计 373+。
- **零新依赖**：全部使用已有 `requests` + 标准库。

## Fact 3.8: v0.6.0 Trending Topics 能力增量

- **Trending 采集器**：`TrendingCollector`（`datapulse/collectors/trending.py`）基于 requests + BeautifulSoup 采集 trends24.in 全球 X/Twitter 热搜趋势（Jina Reader HTTP 451 不可用）。
- **HTML 解析**：`.trend-card` 主策略 + `h3`/`ol/ul` 结构化回退，提取 rank/name/url/volume。
- **Volume 解析**：`parse_volume()` 处理 K/M 后缀和逗号分隔（`125K`→125000, `1.2M`→1200000）。
- **30+ 地区别名**：us→united-states, uk→united-kingdom, jp→japan 等，支持 400+ 全球地区。
- **Reader API**：`DataPulseReader.trending(location, top_n, store)` 异步方法，`store=True` 可选持久化。
- **新增 CLI 参数**：`--trending [LOCATION]`、`--trending-limit N`、`--trending-store`。
- **新增 MCP 工具**：`trending(location, top_n, store)`。
- **Confidence**：`BASE_RELIABILITY["trending"] = 0.78`，flags：`trending_snapshot` (+0.02)、`rich_data` (+0.02)。
- **新增 36 个测试**（`test_trending_collector.py` 8 类），总计 420+。
- **零新依赖**：全部使用已有 `requests`、`beautifulsoup4`、`lxml`。

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

- 阻塞主因一：`pip install -e .` 构建依赖下载阶段走代理失败（`ProxyError: Cannot connect to proxy`），显示 `hatchling` 无可用版本。
  - 修复动作：在远端执行前确认代理端口与配置，或在远端脚本上下文里临时移除 `HTTP(S)_PROXY/ALL_PROXY`。
- 阻塞主因二：`ModuleNotFoundError: No module named 'datapulse'`（在代理问题修复前常见伴随表现）。
  - 修复动作：确认 `MACMINI_DATAPULSE_DIR` 指向 `pyproject.toml` 与 `datapulse/` 同级源码根；必要时执行 `REMOTE_BOOTSTRAP_INSTALL=1` 触发一次 `pip install -e .`。
- 阻塞主因三：SSH 认证与端口参数不匹配（两跳参数变更）。
  - 修复动作：优先改为密钥链路；如继续口令链路，确保 VPS 与跳板 `sshpass` 两段参数一致。

### 官方实践映射（对齐）

- Python 可执行安装：在远端先建立隔离环境（`python3 -m venv`），用该解释器执行 `python3 -m pip install -e .`（官方 Python 文档/Packaging 指南推荐）。
- SSH 两跳隧道：`ssh -J` / `ProxyJump` 是 OpenSSH 标准链路模型；命令链路与配置链路保持一致。
- 可见性与可恢复性：远端脚本已将 `DATAPULSE_DIR_NOT_FOUND` / `PYTHON_VERSION_TOO_LOW` / `PACKAGE_MISSING` / `IMPORT_FAILED` 等阻断码固化，便于自动归档与复测闭环。

## Fact 3.5: 网络拓扑可恢复性补充

- 在当前项目环境中，若本机与内网网段一致时可尝试直连；当前观测链路下 `192.168.3.196` ICMP 为丢包，故优先使用两跳。
- 执行策略建议：
  - 首选 `VPS 两跳隧道`，保证与远端正式入网路径一致；
  - 遇到双跳不可达时，改用内网直连做局部验证与修复（仅用于降级排障）。
- 内网直连时可先验证：
  - 远端 Python 版本
  - `curl -fsS http://127.0.0.1:18801/healthz`
  - 远端源码目录与 `import datapulse` 可达性
- 脚本能力补充：`scripts/datapulse_remote_openclaw_smoke.sh` 已支持 `REMOTE_DIRECT_SSH=1` 模式，无需 VPS 跳板即可直连执行同一套预检与阻断闭环。
- 该补充不影响 `两跳`主链路验收顺序，仅用于提高高可用可恢复性（HA 可用率与故障修复时效）。
- 当前可复现连通事实：两跳链路可用；`MACMINI_HOST=<内网IP>` 需结合当前网段确认，`MACMINI_PORT=22`。
- 远端 uv 闭环增强事实：`REMOTE_UV_BOOTSTRAP=1` 时优先同步本机 `uv` 到 `REMOTE_UV_INSTALL_ROOT`，再 fallback 到远端 `python3 -m pip install --user uv`。
- 当本机 `uv` 与远端平台三元组不一致时（`uname -s`/`uname -m`），会按降级路径执行 pip 安装。
- 新增高可用修复能力：
  - `REMOTE_AUTOPICK_PYTHON=1` 时，会先探测远端可用 Python 并自动选定满足 `REMOTE_PYTHON_MIN_VERSION` 的解释器，优先 `python3.{10,11,12}` 与可执行别名。
  - `MACMINI_DATAPULSE_DIR` 校验时，会尝试候选 `.../DataPulse` 与 `$HOME/.openclaw/workspace/DataPulse`，提升路径偏移场景自愈率。

[⬆️ Back to top / 返回顶部](#top) | [🔙 返回主 README](../README.md) | [🔄 中文对照/English](../README_CN.md)
