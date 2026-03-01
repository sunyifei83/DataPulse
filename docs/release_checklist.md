# DataPulse 发布流程核对清单

## 目标
用于 vX.Y.Z 发版前后的固定操作，减少手工漏项。

## A. 预发检查
- [ ] 版本号确认（`pyproject.toml`、`datapulse/__init__.py`、`datapulse_skill/manifest.json`、`docs/contracts/openclaw_datapulse_tool_contract.json`）
- [ ] `CHANGELOG.md` 更新
- [ ] `RELEASE_NOTES.md` 更新
- [ ] 许可证、项目名称、文档链接一致（`README*` 与 `LICENSE`）
- [ ] 敏感信息未进入公开文档（包括本地测试环境/端点）

## B. 资产构建
- [ ] `python -m build --sdist --wheel .`
- [ ] 产物目录包含 `.whl` 与 `.tar.gz`

## C. 发布动作
- [ ] 创建/更新 release tag（`vX.Y.Z`）
- [ ] 通过 `scripts/release_publish.sh` 生成 Release（或手动 `gh release create`）
- [ ] 确认 Release 页面挂载 assets 与 Release notes

## D. 回归与归档
- [ ] 运行 smoke/关键场景验证
- [ ] 更新入库说明/里程碑链接（如适用）
- [ ] 记录已知风险与下一步跟进项

