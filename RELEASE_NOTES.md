# Release Notes

## Release: DataPulse v0.1.0 (Initial)

发布日期：2026-02-24  
构建目标：高可用情报中枢 PoC（非商用许可）  

### 主要变更
- 项目名称统一为 **DataPulse / 数据脉搏**。
- 将仓库许可证切换为 **DataPulse Non-Commercial License v1.0**（不可商用）。
- 完成 README 三语系文档的结构性补充：
  - 功能覆盖（路由/采集/输出/置信度）
  - CLI、Smoke、MCP、Skill、Agent 使用说明
  - OpenClaw 适配路径与测试引导
- 新增 `docs/contracts/openclaw_datapulse_tool_contract.json`（OpenClaw 工具契约示例）。
- 新增 `scripts/quick_test.sh`（一键验证脚本）。

### 兼容与集成
- 支持 OpenClaw Bot/Skill/MCP/Agent 侧的接入说明，保留标准化 JSON 输出与 Markdown memory 记录。
- `datapulse_skill/manifest.json` 已修复为合法 JSON，可作为 Skill 触发配置基础文件。

### 合规声明
- 本版本不公开任何本地测试环境与模型端点明文。
- 本版本默认仅用于非商用场景；商业用途需单独授权（参见 `LICENSE` 与 README 许可说明）。

### 验收建议
1. 核对 `LICENSE` 与 `pyproject.toml` 的许可证一致性。
2. 确认三份 README 的文档入口、名称与许可证说明一致。
3. 根据 `scripts/quick_test.sh` 执行本地冒烟验证（必要时可跳过外网依赖场景）。
