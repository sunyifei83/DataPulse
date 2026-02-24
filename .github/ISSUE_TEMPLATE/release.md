---
name: Release checklist
about: Track a release process from code freeze to publication
labels: release
assignees: ''
---

## Release checklist

### 1. 版本准备
- [ ] 更新 `pyproject.toml` 版本
- [ ] 确认 `CHANGELOG.md` 已补齐本次修改
- [ ] 生成/更新 `RELEASE_NOTES.md`
- [ ] 确认文档和许可证信息一致

### 2. 发布验证
- [ ] `python -m build --sdist --wheel .`
- [ ] 运行 `scripts/quick_test.sh`
- [ ] 核对资产文件（`.tar.gz` / `.whl`）可用

### 3. 发布与归档
- [ ] 生成 tag 并推送（`vX.Y.Z`）
- [ ] 创建 Release，附带构建产物与 Release Notes
- [ ] 在仓库同步处补充验收记录

