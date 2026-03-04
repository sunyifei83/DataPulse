# 仓库级问题池（Issue Ledger）

> 对齐仓内工作流要求，统一沉淀仓内与联测阶段失败事实。仅记录可复现、可重测、带有复测闭环的项。

## 应急问题闭环模板（执行标准）

- 记录最小信息：
  - 触发时间、阶段、触发分支、提交号、责任人
  - 关键阻断码（如有）、失败命令、现象摘要
  - 证据文件：`remote_report.md` / `remote_test.log` / `local_report.md` / `local_test.log`
  - 变更参数：`VPS_*`、`MACMINI_*`、`REMOTE_*`、`RUN_ID`
- 复测条件（缺一项不予关闭）：
  - 失败复现可重复；
  - 按 [`docs/emergency_mode_runbook.md`](/Users/sunyifei/DataPulse/docs/emergency_mode_runbook.md) 完成至少一轮修复动作；
  - 每次关键参数变更必须新 `RUN_ID`；
  - `remote_report.md` 必须更新且写明阻断码变化；
  - Blocker 消除后才允许状态从 `OPEN` → `DONE`。
- 关闭判定：
  - `DONE`：重复复测 `GREEN`/`YELLOW` 与说明清单一致；
  - `STOP`：出现 `Blocker` 持续未消解时保持 `OPEN` 并同步到发布阻断；
  - `WIP`：缺失关键复测参数（`RUN_ID` 未递增或三件套未归档）不得进入验收结论。
- 复测前提（本仓规则）：
  - 本地底线检查：`bash scripts/datapulse_local_smoke.sh`
  - 远端复测：`bash scripts/datapulse_remote_openclaw_smoke.sh`
  - 归档：`artifacts/openclaw_datapulse_<RUN_ID>/remote_report.md` 与 `artifacts/openclaw_datapulse_<RUN_ID>/remote_test.log`

## WQ-2026-03-04-01（微信公众号 / RSS）

- 触发时间：`2026-03-04 12:07:14Z`
- 阶段：`编译跟测` → `datapulse_local_smoke.sh` 平台回归
- 触发分支：`main`
- 触发提交：`36c8d2d06bca94cb708aa8357cf55384ad57a8bb`
- 责任人：未分配（边界观察）
- 预期修复窗口：未定
- 现象：
  - `wechat`：`No parser produced successful result for https://www.weixin.qq.com/`（日志出现 DNS 解析失败）
  - `rss`：`No parser produced successful result for https://www.reddit.com/.rss`（日志出现 `403` 与 `422`）
- 预期：
  - `PLATFORMS=wechat rss` 下两项均应返回 `[PASS]`，并在 `datapulse-smoke` 结果中落盘。
- 最小复现命令：
  ```bash
  URL_1=https://beewebsystems.com/ \
  URL_BATCH='https://chatprd.ai/ https://beewebsystems.com/ https://uxpilot.ai/' \
  MIN_CONFIDENCE=0.0 \
  DATAPULSE_SMOKE_RSS_URL='https://www.reddit.com/.rss' \
  DATAPULSE_SMOKE_WECHAT_URL='https://www.weixin.qq.com/' \
  PLATFORMS='wechat rss' \
  uv run scripts/datapulse_local_smoke.sh
  ```
- 证据：
  - 报告：`/Users/sunyifei/DataPulse/artifacts/openclaw_datapulse_20260304_120652/local_report.md`
  - 日志：`/Users/sunyifei/DataPulse/artifacts/openclaw_datapulse_20260304_120652/local_test.log`
  - 复现摘要：`PASS=10 FAIL=1`（FAIL 项目 2，脚本聚合计数口径按阶段汇总）
- 处置：
  - 已判定为能力/依赖边界项（非链路回归阻塞）
  - 历史一致性：
    - `RUN_ID 20260304_120313` 同样出现 `wechat`/`rss` 边界
    - `RUN_ID 20260304_120341`（排除 `wechat` 与 `rss`）为主链路 PASS
- 关闭条件：
  - 已完成：可复现可达替代 URL（如 `wechat` / `rss` 公开稳定样例）并在标准验收清单复测通过后标为 `DONE`
- 复测（替代样例）：
  - 命令：
  ```bash
  URL_1=https://example.com/ \
  URL_BATCH='https://www.rssboard.org/rss-specification https://www.gnu.org' \
  DATAPULSE_SMOKE_RSS_URL='https://news.ycombinator.com/rss' \
  DATAPULSE_SMOKE_WECHAT_URL='https://mp.weixin.qq.com/' \
  PLATFORMS='wechat rss' \
  MIN_CONFIDENCE=0.0 \
  uv run scripts/datapulse_local_smoke.sh
  ```
  - 复测结论：`PASS=11 FAIL=0`
  - 复测 `RUN_ID`：`20260304_120853`
  - 报告：`/Users/sunyifei/DataPulse/artifacts/openclaw_datapulse_20260304_120853/local_report.md`
  - 日志：`/Users/sunyifei/DataPulse/artifacts/openclaw_datapulse_20260304_120853/local_test.log`
  - 判定：`wechat` 与 `rss` 平台本身链路可通过；原始 `FAIL` 为样例 URL 可达性波动导致的边界输入问题。
- 当前状态：`DONE`（替代样例复测通过；待在标准验收清单与交付模板持续使用稳定输入继续回归）

## WQ-2026-03-05-01（OpenClaw 历史 open issue 高置信 HA 关单）

- 触发时间：`2026-03-05`
- 阶段：`仓库事实复核` → `issue 关单分流`
- 触发分支：`main`
- 责任人：`@sunyifei83`
- 目标范围：GitHub `open` issue `#18 ~ #24`
- 证据：
  - 关单事实文档：`/Users/sunyifei/DataPulse/docs/openclaw_open_issues_ha_closeout_2026-03-05.md`
  - 实时 issue 清单：`gh issue list --state open`（复核时仅 #18 ~ #24）
  - 同仓复测：`uv run python`（`trending/doctor/read/signature`）
- 处置摘要：
  - `HA-DONE`：`#19 #20 #22 #23`
  - `HA-BOUNDARY`：`#18 #21`
  - `HA-ROADMAP`：`#24`
- 关单动作：
  - 按上述分流统一执行关闭，不再保留该批调研型事实单为 `open`
- 当前状态：`DONE`
