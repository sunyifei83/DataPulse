# DataPulse 发布回退指南

> 应急执行优先文档（v1.1）：[`应急模式说明（远端联测）`](/Users/sunyifei/DataPulse/docs/emergency_mode_runbook.md)

## 适用场景
- 新 release 发布后发现功能回归、接口不可用或外部依赖抖动导致服务不稳定
- 合约变更影响 openclaw-bot/下游调用

## 回滚优先级（按低风险到高风险）
1. 熔断/开关降级
   - `export DATAPULSE_SEARCH_PROVIDER_PRECEDENCE=jina,tavily`
   - 移除 `TAVILY_API_KEY`/`JINA_API_KEY`，保留只读路径验证
   - 观察 15 分钟日志与联调验收是否恢复
2. Git 回退（推荐）
   - `git log --oneline -n 20` 找到需回退的提交号
   - `git revert <bad_commit>`
   - `git push origin main`
3. 分支回退（仅在紧急时段）
   - `git push origin +<prev_sha>:main`（需明确批准；会重写主分支）

## 回退前后最少确认
- 回退动作后，先执行：
  - `bash scripts/security_guardrails.sh`
  - `bash scripts/release_readiness.sh`
  - `bash scripts/datapulse_local_smoke.sh`（如有依赖/环境可达）

## 风险记录模板（建议）
- 现象：`datapulse.mcp_server` 某工具异常码
- 影响范围：本地联测、远端联测、OpenClaw 任务链路
- 处理时间：`YYYY-MM-DD HH:MM`
- 处理动作：热修/回退/降级项
