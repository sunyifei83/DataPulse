---
title: Test Facts
---

<a id="top"></a>

# Test Facts / 测试事实

[🔙 返回主 README](../README.md) | [🔄 中文对照/English](../README_CN.md) | [⬆️ 回到顶部](#top)

## Fact 1: Configuration policy / 配置规范

本仓库不公开本地测试环境和模型端点明文；敏感项仅允许在私有运行时注入。
- Repository policy: no plaintext local test environment/model endpoint values are published in-repo.

## Fact 1.1: Credential management (Debug vs App environment) / 凭据管理实践

- 调试环境：
  - 真实测试凭据优先放入 `.env.openclaw.local`，配合 `scripts/run_openclaw_remote_smoke_local.sh` 本地持久化与 `.gitignore` 防护。
  - 该文件仅用于本机调试链路，不作为应用/CI 凭据来源。
- 应用环境：
  - 生产、CI 与共享服务必须依赖 secret 管理注入（GitHub Secret、vault、环境变量注入层），不通过本地文件提交或共享。
- 运行时参数以启动时环境变量为准，脚本仅作为消费端读取。
- 入库红线：
  - `.env.openclaw.example` 作为脱敏模板；`bash scripts/security_guardrails.sh` 作为入库前阻塞项；`security-guard` workflow 与 `pre-commit` 对齐执行。

## Fact 1.2: 三环境客观资源定义与对接策略（本地 / VPS / Macmini）

- 本地调试环境
  - 资源目标：最短反馈、可读性高、依赖变更可直接验证。
  - 优先检查：CLI/本地 smoke/MCP 列表、Agent 基线调用。
  - 失败策略：出现异常不降级，必须保留错误信息进入问题池。
- VPS 过渡环境
  - 资源目标：验证 `VPS 两跳` 与执行脚本在现实网络中的行为一致性。
  - 优先检查：`ssh -J` 可达性、`MACMINI_DATAPULSE_DIR`、远端 Python 版本、阻断码输出。
  - 失败策略：阻断码归类后必须复测，不得“通过”上报。
- Macmini 应用环境
  - 资源目标：覆盖服务健康状态与业务端到端链路。
  - 优先检查：`/healthz`、`/readyz`、`remote smoke`、MCP/Agent/Skill 联合快检。
  - 失败策略：任何关键路径异常需补齐 RUN_ID 与重放条件，阻塞发布与高可用结论闭环。

### 三环境客观参数（执行2补充）

- VPS 主链路（异地）：`VPS_HOST=137.220.151.57`、`VPS_PORT=6069`、`MACMINI_PORT=2222`、`MACMINI_HOST_CANDIDATES=127.0.0.1,192.168.3.196,192.168.3.195`。
- Macmini 应用（当前）：`192.168.3.196`、`macmini 用户=wangzai-bot`、Runtime `18801`、代理 `127.0.0.1:7897`、API `127.0.0.1:9090`（按本地记录文件）。
- 备份 VPS 参考：`38.244.20.109:20108`，文档标注 IP 被墙，不作为本轮常规两跳主入口。
- 断言：
  - 当前环境处于异地：`REMOTE_DIRECT_SSH=1` 不可用。
  - 对接默认策略是 `VPS 两跳 -> macmini -> Runtime`，本地直连仅作离线回退。

### 三环境凭据治理（高可用）

- 调试：`.env.openclaw.local` 为本机实验持久化目标，禁止入库；适配 `run_openclaw_remote_smoke_local.sh` 自动补齐。
- VPS：`VPS_*` 与 `REMOTE_*` 仅执行期注入，不落共享文件；故障排查优先固定参数版本（`VPS_USER/HOST/PORT`、`MACMINI_HOST`、`REMOTE_PYTHON`）。
- 应用：只走 secret manager / 运行时环境变量；部署端注入优先级高于 `.env.openclaw.local`，模板文件保持脱敏占位符。

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
- 本机与远端凭据请放在 `.env.openclaw.local`，`.env.openclaw.example` 用于脱敏模板；若本地副本缺失，`scripts/run_openclaw_remote_smoke_local.sh` 会自动从当前会话/历史配置持久化填充；并在 `.gitignore` 声明，不入库
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
- 已执行快照（2026-03-04）：
  - 本机：`PASS=10 FAIL=1`（能力边界缺口：`wechat` 解析/DNS 失败、`rss` 目标源 `403/422`；见 RUN_ID `20260304_120313`）
  - 标准化基线：`PASS=11 FAIL=0`（收敛 `PLATFORMS=twitter reddit youtube bilibili telegram xhs`；见 RUN_ID `20260304_120341`）
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

## Fact 3.4b: 远端联测事实（2026-03-04 重新执行）

- 已成功通过两跳隧道连通：`VPS_HOST=137.220.151.57:6069`，`MACMINI_HOST=127.0.0.1`，`MACMINI_PORT=2222`，`MACMINI_HOST_CANDIDATES=127.0.0.1,192.168.3.196,192.168.3.195`。
- 确认 `python3` 缺省解释器为 3.9.6，不满足 `requires-python >=3.10`；当前修复采用显式 `REMOTE_PYTHON=/opt/homebrew/bin/python3.10`、`REMOTE_PYTHON_MIN_VERSION=3.10`。
- `bash scripts/run_openclaw_remote_smoke_local.sh` 本次执行结果：15 步中 14 通过，1 失败（仅 `smoke platforms`）。
- `smoke platforms` 的失败是平台 URL 缺失导致（`Missing smoke URLs`），并非链路阻断码；可通过补齐下列变量重试：
  - `DATAPULSE_SMOKE_REDDIT_URL`
  - `DATAPULSE_SMOKE_YOUTUBE_URL`
  - `DATAPULSE_SMOKE_BILIBILI_URL`
  - `DATAPULSE_SMOKE_TELEGRAM_URL`
  - `DATAPULSE_SMOKE_RSS_URL`
  - `DATAPULSE_SMOKE_WECHAT_URL`
  - `DATAPULSE_SMOKE_XHS_URL`
- 远端存在 `/opt/homebrew/bin/uv (0.10.7)`，可作为评估方案：`REMOTE_USE_UV=1` 与 `REMOTE_UV_PYTHON=3.10`，但当前链路已稳定采用显式 `REMOTE_PYTHON=/opt/homebrew/bin/python3.10`。

## Fact 3.4c: 远端联测事实（2026-03-04 全流程通过）

- `bash scripts/run_openclaw_remote_smoke_local.sh` 二跳复测完成 `RUN_ID=20260304_185014`，15 步均 PASS（`PASS=15`，`FAIL=0`），无新增阻断码，远端报表为 `artifacts/openclaw_datapulse_20260304_185014/remote_report.md`。
- 连通事实：`VPS_HOST=137.220.151.57`，`VPS_PORT=6069`，`MACMINI_HOST=127.0.0.1`，`MACMINI_PORT=2222`，`MACMINI_HOST_CANDIDATES=127.0.0.1,192.168.3.196,192.168.3.195`，`REMOTE_DIRECT_SSH=0`。
- 通过前提：`REMOTE_PYTHON=/opt/homebrew/bin/python3.10`（`REMOTE_AUTOPICK_PYTHON=0`），`REMOTE_BOOTSTRAP_INSTALL=1`，`PLATFORMS` 采用 `twitter reddit bilibili telegram xhs youtube`，并补齐所有 `DATAPULSE_SMOKE_*` URL。
- 结果稳定性说明：核心验收无阻断；运行日志存在外部依赖告警，不影响脚本通过：
  - `telegram` 由于缺少 `TG_API_ID/TG_API_HASH` 有解析降级提示；
  - `xhs` 命中 `Jina Reader 451` 并回退；
  - `youtube` 出现 `youtube-transcript-api` 方法兼容告警与超时重试；
  - `reddit`/`youtube` 个别请求出现连接超时重试后仍有 pass 回退输出。
- 结论：异地两跳链路可作为 Macmini 应用验收前置，建议将平台凭据缺失与跨站超时作为持续观察项，而非当前阻断码项。

## Fact 3.4d: 交付判定升级（HA Gate v1）

- 最新 run `20260304_194700` 与此前 `20260304_185014` 同步按新门禁策略归档为 `YELLOW`：
  - 关键链路 `FAIL=0`；
  - 阻断码为空；
  - 外部告警存在（`Watch`）且可复现地归因为第三方访问抖动/凭据缺失。
- 该结果支持“受限放行”与“持续跟踪”并行：
  - 立即动作：保持两跳链路与版本链路冻结（`REMOTE_PYTHON=3.10` + `PYTHON_MIN=3.10`）；
  - 观察动作：补齐 `TG_API_ID/TG_API_HASH`、记录 Jina 451 与 YouTube 超时趋势；
  - 阻断动作：若未来复测出现 `Blocker` 阶层阻断码则直接回滚放行结论并要求修复。
- 与工程策略联动：
  - 下次复测沿用 `RUN_ID` 必须递增；
  - 以 `[docs/openclaw_datapulse_acceptance_template.md](/Users/sunyifei/DataPulse/docs/openclaw_datapulse_acceptance_template.md)` 的 `0.4 高可用交付 Gate v1` 节为唯一放行依据。

## Fact 3.4e: 执行1 完整对比结果（Python 直连 vs UV）

- 执行对比时间：`2026-03-04`
- 方案 A（Python 直连，默认主路径）
  - 配置：`REMOTE_PYTHON=/opt/homebrew/bin/python3.10`，`REMOTE_AUTOPICK_PYTHON=0`，`REMOTE_BOOTSTRAP_INSTALL=1`。
  - 结果：`RUN_ID=20260304_185014`，`PASS=15`，`FAIL=0`，`remote_report=artifacts/openclaw_datapulse_20260304_185014/remote_report.md`。
  - 说明：未触发 uv 相关阻塞，适合作为默认交付闭环。
- 方案 B（UV）
  - 配置：`REMOTE_USE_UV=1`，`REMOTE_UV_PYTHON=3.10`，`REMOTE_UV_BOOTSTRAP=1`。
  - 结果：`RUN_ID=20260304_193008`，`PASS=16`，`FAIL=0`，`remote_report=artifacts/openclaw_datapulse_20260304_193008/remote_report.md`。
  - 说明：新增 `check uv/bootstrap` 步骤通过；作为恢复/兼容路径可接受，但当前不替代默认主路径。
- 方案 D（最新闭环）：`RUN_ID=20260304_194700`，`PASS=15`，`FAIL=0`，`remote_report=artifacts/openclaw_datapulse_20260304_194700/remote_report.md`。
  - 配置：`VPS_HOST=137.220.151.57`、`VPS_PORT=6069`、`MACMINI_HOST=127.0.0.1`、`MACMINI_PORT=2222`，`REMOTE_PYTHON=/opt/homebrew/bin/python3.10`、`REMOTE_BOOTSTRAP_INSTALL=1`、`REMOTE_AUTOPICK_PYTHON=0`。
  - 评估结论（按高可用）
  - 若追求最小变更与可解释性，默认继续采用方案 A。
  - 若出现解释器或执行链路异常，短时可切换方案 B 复测，两者结果均可归档，仍需保持 `BLOCK/Watch` 分层一致输出。

## Fact 3.6: v0.5.0 能力增量

- **Jina 增强读取**：`JinaAPIClient`（`datapulse/core/jina_client.py`）封装 Reader + Search API，支持 CSS 选择器定向（`X-Target-Selector`）、等待元素（`X-Wait-For-Selector`）、缓存控制（`X-No-Cache`）、AI 图片描述（`X-With-Generated-Alt`）、Cookie 透传、代理。
- **Web 搜索**：`DataPulseReader.search()` 支持多源检索（Jina/Tavily，默认 `provider=auto`），并返回经评分排序的 `DataPulseItem` 列表。CLI `--search` / MCP `search_web`。
- **GenericCollector 回退链增强**：Trafilatura → BS4 → Firecrawl → Jina Reader → fail。
- **新增 MCP 工具**：`search_web`、`read_url_advanced`。
- **新增 CLI 参数**：`--search`、`--site`、`--search-limit`、`--no-fetch`、`--target-selector`、`--no-cache`、`--with-alt`。
- **新增 56 个测试**（`test_jina_client.py` 29 + `test_jina_collector_enhanced.py` 17 + `test_jina_search.py` 10），总计 351+。
- **零新依赖**：全部使用 `requests`（已有）+ 标准库。

## Fact 3.7: v0.5.1 XHS 采集能力增量

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

## Fact 3.9: v0.6.1 可靠性与诊断能力增量

- **采集器健康自检（doctor）**：`BaseCollector` 新增 `tier`（0/1/2）、`setup_hint`、`check()` 方法。13 个采集器全部实现自检，按 tier 0（零配置：rss/arxiv/hackernews）、tier 1（网络/免费：twitter/reddit/bilibili/trending/generic/jina）、tier 2（需配置：youtube/xhs/wechat/telegram）三级分类。
- **Doctor 聚合**：`ParsePipeline.doctor()` 按 tier 分组返回所有采集器健康状态。`DataPulseReader.doctor()` 透传。
- **CLI `--doctor`**：分级表格展示 `[OK]`/`[WARN]`/`[ERR]` 状态图标与 setup_hint。
- **MCP `doctor()` 工具**：返回 JSON 健康报告，MCP 工具总数 24（v0.6.1）→ 28（实体与摘要导出能力补充后）。
- **429 感知退避**：新增 `RateLimitError`（含 `retry_after` 字段），`retry()` 自动遵循 Retry-After 头部（上限 `max_delay`），`respect_retry_after=False` 可选禁用。
- **CircuitBreaker 限速加权**：`rate_limit_weight`（默认 2）使 429 错误以双倍速度填充熔断计数器。
- **入库指纹去重**：`UnifiedInbox.add()` 对 ≥50 字符内容计算指纹，拒绝近似重复。`fingerprint_dedup=False` 逃生口。指纹集 save/reload 持久化。
- **可操作路由错误**：`ParsePipeline.route()` 追踪 `best_match` 采集器，路由失败时附带 `setup_hint` 修复指引。
- **新增 42 个测试**（`test_doctor.py` 25 + `test_retry.py` 10 + `test_storage.py` 7），总计 496 passed，覆盖 25 个测试模块。
- **零新依赖**，零 breaking change。

## Fact 3.10: v0.7.0 实体能力补齐（边界增强）

- **轻量实体蒸馏链路**：`DataPulseReader.extract_entities()` 支持 URL 级实体提取，默认 `mode="fast"`，可切 `llm` 模式；CLI 增加 `--entities`、`--entity-query`、`--entity-graph`、`--entity-stats`。
- **实体持久化能力**：`EntityStore` 增加文件化 JSON 存储（默认 `entity_store.json`），支持 `DATAPULSE_ENTITY_STORE` 覆盖路径；支持 `EntityType`/`Relation` 的查询、实体去重与合并、跨源计数。
- **实体评分加权**：引入 `DATAPULSE_ENTITY_CORROBORATION_WEIGHT`，并在 `scoring` 模块中将跨源实体共现纳入综合评分。
- **MCP 入口补齐**：新增 4 个高价值实体工具 `extract_entities`、`query_entities`、`entity_graph`、`entity_stats`。
- **测试与门禁**：新增实体相关测试覆盖（`test_entities.py`/`test_entity_store.py`/`test_entity_integration.py`），纳入 `tests/` 全量闭环。

## Fact 4: 来源与订阅能力增强

- 已形成统一落地清单：`docs/source_feed_enhancement_plan.md`。
- 对齐重点：源解析与源组、订阅关系、Feed 输出、标记/反馈闭环、安全边界。
- 推荐执行顺序：
  - 先在项目内补齐源列表配置与批量导入流程（P0）。
  - 再补齐 JSON Feed/RSS 输出自检（P1）。
  - 最后补齐 marks/feedback 反馈闭环（P2）。

## Fact 4.1: XHS 复核交付能力（脚本化）

- 已新增 `scripts/xhs_quality_report.py`（一键执行 xhs 候选检索 + 置信/评分输出）。
- 已新增 `scripts/run_xhs_quality_report.sh`（封装输出目录落盘、JSON+Markdown 交付、退出码保留与诊断输出）。
- 脚本执行采用 `provider=multi` + `mode=multi`，输出字段含：
  - `confidence`、`score`、`confidence_factors`、`score_breakdown`
  - `search_sources`、`search_audit`、`search_cross_validation`
  - 可机读报告（JSON）与可审阅报告（Markdown）
- 置信分层规则写死默认值（可环境变量覆盖）：
  - 高置信：`confidence >= 0.80` 且 `score >= 70`
  - 中置信：`confidence >= 0.65` 且 `score >= 50`
  - 低置信：其余

## Fact 3.5: 远端测试环境 HA 可用事实（按官方实践对齐）

### 已确认高置信事实

- 远端入口必须走 VPS 两跳（`ssh -J` / `ProxyJump` 方式）；官方 `ssh_config`/`ssh(1)` 都将该方式定义为“先连跳板后到目标的顺序链路”，适配可写成命令行 `-J` 或配置项 `ProxyJump`。
- 远端需把源码路径作为本机可执行测试上下文（`MACMINI_DATAPULSE_DIR` 指向源码根，含 `pyproject.toml` 与 `datapulse/`）。
- 远端 Python 版本必须满足项目元数据要求（`requires-python` 当前链路要求 `>=3.10`），否则入口导入阶段不应继续。
- 两跳通道与服务可达建议用独立敏感环境变量文件承载（`.env.openclaw.local` / `.env.openclaw` / `.env.local` / `.env.secret`），脚本已支持且不会读取明文入库。
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

## Fact 3.6: 网络拓扑可恢复性补充

- 在当前项目环境中，若本机与内网网段一致时可尝试直连；当前两跳主路基线固定 `127.0.0.1:2222`（第二跳隧道端口映射），并保留 `192.168.3.196`、`192.168.3.195` 作为回退候选。
- 执行策略建议：
  - 首选 `VPS 两跳隧道`，保证与远端正式入网路径一致；
  - 遇到双跳不可达时，改用内网直连做局部验证与修复（仅用于降级排障）。
- 内网直连时可先验证：
  - 远端 Python 版本
  - `curl -fsS http://127.0.0.1:18801/healthz`
  - 远端源码目录与 `import datapulse` 可达性
- 脚本能力补充：`scripts/datapulse_remote_openclaw_smoke.sh` 已支持 `REMOTE_DIRECT_SSH=1` 模式，无需 VPS 跳板即可直连执行同一套预检与阻断闭环。
- 该补充不影响 `两跳`主链路验收顺序，仅用于提高高可用可恢复性（HA 可用率与故障修复时效）。
- 当前可复现连通事实：两跳链路以 `VPS 137.220.151.57:6069` + `127.0.0.1:2222` 为主链路；`MACMINI_HOST=<候选内网IP>` 需结合当前网段确认，`MACMINI_PORT=2222`。
- 远端 uv 闭环增强事实：`REMOTE_UV_BOOTSTRAP=1` 时优先同步本机 `uv` 到 `REMOTE_UV_INSTALL_ROOT`，再 fallback 到远端 `python3 -m pip install --user uv`。
- 当本机 `uv` 与远端平台三元组不一致时（`uname -s`/`uname -m`），会按降级路径执行 pip 安装。
- 新增高可用修复能力：
  - `REMOTE_AUTOPICK_PYTHON=1` 时，会先探测远端可用 Python 并自动选定满足 `REMOTE_PYTHON_MIN_VERSION` 的解释器，优先 `python3.{10,11,12}` 与可执行别名。
  - `MACMINI_DATAPULSE_DIR` 校验时，会尝试候选 `.../DataPulse` 与 `$HOME/.openclaw/workspace/DataPulse`，提升路径偏移场景自愈率。

[⬆️ Back to top / 返回顶部](#top) | [🔙 返回主 README](../README.md) | [🔄 中文对照/English](../README_CN.md)
