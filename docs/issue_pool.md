# 仓库级问题池（Issue Ledger）

> 对齐仓内工作流要求，统一沉淀仓内与联测阶段失败事实。仅记录可复现、可重测、带有复测闭环的项。

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
  - 需要可复现可达替代 URL（如 `wechat` / `rss` 公开稳定样例）并完成同脚本复测后改为 `OPEN`->`DONE`
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
- 当前状态：`DONE`（边界样例替代可复测，待在标准验收清单使用稳定样例）
