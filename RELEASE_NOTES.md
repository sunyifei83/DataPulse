# Release Notes

## Release: DataPulse v0.2.0

发布日期：2026-02-28
构建目标：测试基建 + 韧性增强 + 采集器强化 + 可观测性

### 主要变更

**Phase 1 — 测试基建**
- 新增 183 单元测试，覆盖 models / utils / storage / router / collectors / confidence / retry / reader / source catalog 共 12 个测试文件。
- 新增 `tests/conftest.py`，提供 7 个可复用 fixture。
- GitHub Actions CI：Python 3.10/3.11/3.12 矩阵执行 ruff lint + pytest。
- pre-commit 配置（ruff + mypy hook）。

**Phase 2 — 韧性增强**
- `datapulse/core/retry.py`：`retry_with_backoff` 装饰器 + `CircuitBreaker` 熔断器。
- `datapulse/core/cache.py`：线程安全 TTL 缓存，零外部依赖。
- Bilibili / Jina / RSS 采集器集成重试（2~3 次指数退避）。
- 异常窄化：全局替换 `except Exception` 为精确异常类型。
- Telegram / RSS 新增显式超时（30s / 20s）。

**Phase 3 — 采集器增强**
- RSS：多条目解析（最多 5 条），markdown 分隔输出。
- Bilibili：交互数据（播放/点赞/投币/收藏/弹幕/评论/转发）写入 extra dict。
- Telegram：`DATAPULSE_TG_MAX_MESSAGES` / `DATAPULSE_TG_MAX_CHARS` / `DATAPULSE_TG_CUTOFF_HOURS` 环境变量可配置。
- 小红书：改进标题/内容提取策略，增加 fallback。
- Jina：集成重试 + TTL 缓存。
- `read_batch`：自动 URL 归一化与去重。

**Phase 4 — 可观测性**
- `datapulse/core/logging_config.py`：结构化日志，`DATAPULSE_LOG_LEVEL` 环境变量控制级别。
- 所有采集器统一使用 logger 替代 print。

### 版本一致性
- `pyproject.toml` → 0.2.0
- `datapulse/__init__.py` → 0.2.0
- `datapulse_skill/manifest.json` → 0.2.0
- `docs/contracts/openclaw_datapulse_tool_contract.json` → 0.2.0

### 验收建议
1. `uv run --python 3.11 -- ruff check datapulse/` — 0 errors
2. `uv run --python 3.11 -- python -m pytest tests/ -v` — 183 passed
3. `git tag -l v0.2.0` — tag 存在
4. 所有 15 个 v0.2.0 GitHub Issues 已关闭

---

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

### 发布产物与发布方式（v0.1.0）
- 构建资产：`python -m build --sdist --wheel .`
- 建议附件：
  - `dist/*.whl`
  - `dist/*.tar.gz`
- 发布方式：
  - 标签发布：`./scripts/release_publish.sh --tag v0.1.0`
  - CI 自动发布：`.github/workflows/release.yml`（推送 `v*` 标签触发）
