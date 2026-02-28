# Changelog

## [0.2.0] - 2026-02-28

### Added — Test Infrastructure (Phase 1)
- 183 unit tests across 12 test modules covering models, utils, storage, router, collectors, confidence scoring, retry, reader, and source catalog.
- `tests/conftest.py` with shared fixtures (`sample_item`, `tmp_inbox`, `mock_response`).
- `pytest` + `pytest-asyncio` dev dependencies in `pyproject.toml`.
- `.github/workflows/ci.yml` — GitHub Actions CI running lint + tests on Python 3.10/3.11/3.12.
- `.pre-commit-config.yaml` for local ruff/mypy hooks.

### Added — Resilience (Phase 2)
- `datapulse/core/retry.py` — configurable `retry_with_backoff` decorator and `CircuitBreaker` class.
- `datapulse/core/cache.py` — in-memory TTL cache with thread-safe access.
- Retry integration in `JinaCollector` and RSS collector with exponential backoff.

### Added — Observability (Phase 4)
- `datapulse/core/logging_config.py` — structured logging with `DATAPULSE_LOG_LEVEL` env var support.
- Unified logging across all collectors replacing ad-hoc print statements.

### Changed — Collector Enhancements (Phase 3)
- **RSS**: multi-entry feed parsing (up to `MAX_ENTRIES=25`), returning list of `ParseResult`.
- **Bilibili**: interaction stats (`views`, `likes`, `coins`, `favorites`, `shares`) in `extra` dict.
- **Telegram**: configurable `DATAPULSE_TG_LIMIT` and `DATAPULSE_TG_OFFSET` env vars.
- **Xiaohongshu**: improved title/content extraction with fallback strategies.
- **Jina**: retry-on-failure with backoff; cache integration for repeated URLs.
- Batch URL deduplication in `read_batch`.

### Changed — Core
- Version bumped to `0.2.0`.
- `datapulse/core/storage.py` — improved `prune` with configurable max age; better error handling on corrupt JSON.
- `datapulse/core/utils.py` — new helpers: `validate_external_url` (SSRF protection), `resolve_platform_hint`, `is_platform_url`, `normalize_language`, `content_hash`, `generate_slug`.
- `datapulse/core/source_catalog.py` — `SourceCatalog` with pack-based subscription model, auto-source registration, and domain/pattern matching.
- Import cleanup and ruff lint compliance across all modules.

### Fixed
- Ruff lint: 42 errors resolved (import sorting, unused imports, unused variables).

## [0.1.1] - 2026-02-24

### Added
- 发布流程体系化：新增发布 checklist、发布脚本与 GitHub Actions 自动发布工作流。
- README 与 Release Notes 补充 `dist/*` 资产发布与一键发布说明。
- 新增 PR / Issue 模板，用于版本化提交与发布管理规范化。

### Changed
- 增加 `docs/release_checklist.md` 统一发布验收标准。
- 新增 `scripts/release_publish.sh`，支持 tag 生成/推送与 Release 资产挂接。
- 新增 `.github/workflows/release.yml`，支持 tag 推送触发自动上传构建产物。

## [0.1.0] - 2026-02-24

### Added
- 实现 `DataPulse`（数据脉搏）基础情报中枢：跨平台 URL 采集/解析入口、置信度评分、内存化输出。
- 完整补齐 `README.md`、`README_CN.md`、`README_EN.md` 的功能说明与双语导航结构。
- 补充 OpenClaw 兼容说明与工具调用路径：
  - `docs/contracts/openclaw_datapulse_tool_contract.json`
  - `scripts/quick_test.sh`
- 新增/对齐 `datapulse_skill/manifest.json` 为可用的 Skill 入口定义。
- 提供统一的样例配置 `.env.example` 与测试事实说明 `docs/test_facts.md`。

### Changed
- 许可证变更为不可商用许可：`DataPulse Non-Commercial License v1.0`。
- `pyproject.toml` 中 `license` 字段同步新许可信息。
- 修复 `datapulse_skill/manifest.json` 的 JSON 结构与模式字段问题（可用于上线前校验）。

### Security & Compliance
- 仓库文档移除本地测试环境与模型端点的明文信息，仅保留抽象化环境变量约定。
- README 与测试说明中统一强调本地敏感配置仅在私有运行时注入。

### Notes
- 首次初始化版本，以「功能对齐 + 非商用许可收敛」为主线，未执行完整自动化测试，仅形成可交付结构与文档。
