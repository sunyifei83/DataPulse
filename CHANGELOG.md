# Changelog

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
