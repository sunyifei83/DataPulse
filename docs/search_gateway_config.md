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
- `DATAPULSE_SEARCH_QNAIGC_ENABLED`：候选 provider 启用开关（默认 `0`）
- `DATAPULSE_SEARCH_QNAIGC_LOCALE_PATTERNS`：中文候选触发模式，逗号分隔（默认 `zh,zh-hans,zh-hant,中文`）
- `DATAPULSE_SEARCH_QNAIGC_MAX_RESULTS`：上游 `max_results` 上限（默认 `20`，取值建议 [1,50]）
- `DATAPULSE_SEARCH_QNAIGC_SITE_FILTER_LIMIT`：上游 `site_filter` 上限（默认 `20`）
- `DATAPULSE_SEARCH_QNAIGC_COST_PER_CALL`：每次调用成本约束值（默认 `0.036`）
- `DATAPULSE_SEARCH_QNAIGC_COST_CURRENCY`：成本币种（默认 `CNY`）
- `DATAPULSE_SEARCH_QNAIGC_FAIL_CLOSED_WITHOUT_TOKEN`：无 token 时是否 fail-closed（默认 `1`）

## Token 注入策略（建议）
- `JINA_API_KEY` / `TAVILY_API_KEY` 不应写死到仓库。
- 由部署环境注入，运行时统一通过 `datapulse.core.security.get_secret` 读取。
- 日志/接口返回中的敏感值统一做脱敏处理（`mask_secret`）。

### 三环境调用边界（简化版）

- 本地调试：直接在本机注入最小变量集合进行行为回归；支持快速修正 `DATAPULSE_SEARCH_*`。
- VPS/中转：以 `scripts/run_openclaw_remote_smoke_local.sh` 与 `scripts/datapulse_remote_openclaw_smoke.sh` 为闭环入口，重点校验链路可达性和代理策略隔离。
- 应用环境：统一走运行时 secret，`get_secret` 作为唯一读取入口，避免临时 `.env` 污染共享实例。
- 规则：每次链路失败不掩蔽异常，需带阻断码（`RETRY`、`proxy`、`timeout`）回传。

## 调试环境 / 应用环境凭据分层（最佳实践）

- 调试环境（本地验证）：
  - 使用 `.env.openclaw.local` 持久化本次会话凭据（或本机开发机运行时环境变量），支持快速迭代与复现。
  - 仅本地文件，不参与共享部署；执行 `bash scripts/security_guardrails.sh` 防止误提交。
- 应用环境（CI/CD/生产）：
  - 使用部署侧 secret 管理服务或操作系统环境变量注入，不在仓库路径新增/修改凭据文件。
  - 对接入口统一走启动时变量注入，支持按实例、按工作流、按环境覆盖。
- 统一约束：
  - 模板文件保留占位符（如 `.env.openclaw.example`），不承载任何明文凭据。
  - 敏感变量优先从运行时上下文注入，避免把同一份凭据写到本地与应用文件。

## 来源治理映射

搜索网关属于“provider 侧治理面”，不是底层网页或 API 事实本身的最终分类面。与 [intelligence_source_governance_contract.md](/Users/sunyifei/DataPulse/docs/intelligence_source_governance_contract.md) 对齐时，应采用以下约束：

| 网关层字段 | 合同取值 | 说明 |
| --- | --- | --- |
| `source_class` | `aggregator` | `jina`、`tavily` 这类 provider 是发现中介，不是底层内容权威本身 |
| `collection_mode` | `search_gateway` | 通过统一搜索 provider 执行发现、fallback 与聚合 |
| `authority` | `secondary` | provider 返回的是候选线索，不自动等于高权威证据 |
| `sensitivity` | `review_required` | 搜索结果需要后续归因、核验与人工判断 |
| `compliance_hints` | `search_results_require_verification`、`respect_source_terms`、`operator_review_required`、`no_automated_legal_determination` | 仅提供治理提醒，不做自动法律裁决 |

落地规则：

- `SearchGateway` 负责 provider 选择、重试、熔断和审计元数据，不负责替底层 URL 做最终合规判定。
- provider 返回的 URL 仍应进入 `SourceCatalog.resolve_source()` 或人工审阅，再落到 `public_web` / `api` / `manual_fact` 等最终来源语义。
- 搜索审计字段（如 `provider_chain`、`attempts`、`cross_validation`）属于发现 provenance，不代表“已验证”或“已获合规批准”。

## QNAIGC 候选 Provider 合约边界（L18）

- `qnaigc` 仅作为 `provider=auto` 的候选 provider，不替换现有显式 provider 链路。
- 显式模式保持不变：
  - `provider=jina` -> `["jina"]`
  - `provider=tavily` -> `["tavily", "jina"]`
- 路由约束：
  - `provider=auto` 下可在现有显式链路基础上按 L18.2 的中文查询识别加入候选
  - 中文查询识别器与 token 校验策略属于 runtime 切片 L18.3 的实现边界
- Token 边界：
  - token 名称优先级为 `QNAIGC_TOKEN_A` -> `QNAIGC_TOKEN_B`
  - 两者缺失时不启用 qnaigc 候选路径
- Result 归一化边界：
  - `SearchHit` 仍是唯一共享结果模型
  - `authority_score`、`date`、`request_id` 写入 `SearchHit.extra`

## 验收命令
- `python3 -m datapulse.mcp_server --help`
- `python3 -m datapulse.mcp_server --list-tools`
- `bash scripts/security_guardrails.sh`
