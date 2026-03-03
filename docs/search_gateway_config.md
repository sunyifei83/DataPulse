# 搜索网关配置治理（外部能力统一入口）

## 变更目标
- 搜索能力通过单点网关 `datapulse.core.search_gateway.SearchGateway` 执行 provider 选择、重试、熔断、超时与跨源聚合。
- 运行时参数全部来自环境变量，避免硬编码与外部服务耦合。
- 与 MCP/CLI 的搜索入口共享同一套行为。

## 关键配置项
- `DATAPULSE_SEARCH_TIMEOUT`：搜索 HTTP 超时（秒，默认 `3.0`，最小 `1.0`）
- `DATAPULSE_SEARCH_RETRY_ATTEMPTS`：最大重试次数（默认 `2`，范围 `1~10`）
- `DATAPULSE_SEARCH_RETRY_BASE_DELAY`：基础退避（默认 `1.0`）
- `DATAPULSE_SEARCH_RETRY_MAX_DELAY_SECONDS`：退避上限（默认 `4.0`）
- `DATAPULSE_SEARCH_RETRY_BACKOFF`：指数退避因子（默认 `2.0`）
- `DATAPULSE_SEARCH_RETRY_RESPECT_RETRY_AFTER`：是否尊重 `Retry-After`（默认 `1`，`0/false/off` 禁用）
- `DATAPULSE_SEARCH_CB_FAILURE_THRESHOLD`：熔断阈值（默认 `5`）
- `DATAPULSE_SEARCH_CB_RECOVERY_TIMEOUT`：熔断恢复时间（秒，默认 `60`）
- `DATAPULSE_SEARCH_CB_RATE_LIMIT_WEIGHT`：429 折损权重（默认 `2`）
- `DATAPULSE_SEARCH_PROVIDER_PRECEDENCE`：provider 顺序，如 `tavily,jina`

## Token 注入策略（建议）
- `JINA_API_KEY` / `TAVILY_API_KEY` 不应写死到仓库。
- 由部署环境注入，运行时统一通过 `datapulse.core.security.get_secret` 读取。
- 日志/接口返回中的敏感值统一做脱敏处理（`mask_secret`）。

## 验收命令
- `python3 -m datapulse.mcp_server --help`
- `python3 -m datapulse.mcp_server --list-tools`
- `bash scripts/security_guardrails.sh`
