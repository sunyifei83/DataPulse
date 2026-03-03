# DataPulse 发布流程核对清单

## 目标
用于 vX.Y.Z 发版前后的固定操作，减少手工漏项。

## A. 预发检查
- [ ] 运行 `bash scripts/security_guardrails.sh`（禁止明文 token 进入仓库）
- [ ] 运行 `bash scripts/release_readiness.sh`，确认必需文件与环境核对通过
- [ ] 版本号确认（`pyproject.toml`、`datapulse/__init__.py`、`datapulse_skill/manifest.json`、`docs/contracts/openclaw_datapulse_tool_contract.json`）
- [ ] `CHANGELOG.md` 更新
- [ ] `RELEASE_NOTES.md` 更新
- [ ] 许可证、项目名称、文档链接一致（`README*` 与 `LICENSE`）
- [ ] 敏感信息未进入公开文档（包括本地测试环境/端点）
- [ ] `.claude/` 在 `.gitignore` 中声明并保持未入库

## B. 配置与外部能力治理
- [ ] 关键环境变量（含 Token/超时/重试）来源仅通过环境变量与安全文档注入（避免写死）
- [ ] 已执行 `docs/search_gateway_config.md` 中的「搜索配置治理」检查项
- [ ] MCP 入口已通过 `datapulse.mcp_server` 内建 fallback 验证（`python3 -m datapulse.mcp_server --list-tools`）

## C. 资产构建
- [ ] `python -m build --sdist --wheel .`
- [ ] 产物目录包含 `.whl` 与 `.tar.gz`

## D. 发布动作
- [ ] 创建/更新 release tag（`vX.Y.Z`）
- [ ] 通过 `scripts/release_publish.sh` 生成 Release（或手动 `gh release create`）
- [ ] 确认 Release 页面挂载 assets 与 Release notes

## E. 回归与归档
- [ ] 运行 smoke/关键场景验证
- [ ] 更新入库说明/里程碑链接（如适用）
- [ ] 记录已知风险与下一步跟进项

## F. 回退与应急
- [ ] 阅读并确认 [`docs/release_rollback_guide.md`](docs/release_rollback_guide.md)
- [ ] 回退演练脚本输出已归档（`git log` + `git revert`/回滚命令）
