# Release Notes

## Release: DataPulse v0.5.0

发布日期：2026-03-01
构建目标：Jina 增强读取 + Web 搜索能力集成

### 主要变更

**Phase 1 — Jina API 客户端层**
- 新建 `datapulse/core/jina_client.py`：统一封装 Jina Reader (`r.jina.ai`) 和 Search (`s.jina.ai`) API。
- `JinaReadOptions`：CSS 选择器定向抓取、等待元素加载、Cookie 透传、代理、AI 图片描述、缓存控制、POST 模式（SPA hash 路由）。
- `JinaSearchOptions`：限定搜索域名、最大结果数。
- 独立 `CircuitBreaker` 实例（read 故障不影响 search），read 使用 `@retry(max_attempts=2)`。
- API Key 优先级：构造函数参数 > `JINA_API_KEY` 环境变量 > 无 key（免费层）。

**Phase 2 — JinaCollector 升级**
- `JinaCollector` 重写为使用 `JinaAPIClient`，支持 `target_selector`、`wait_for_selector`、`no_cache`、`with_alt`、`cookie`、`proxy_url`。
- 可靠性从 0.64 提升至 0.72。
- 新增 confidence flags：`css_targeted` (+0.03)、`image_captioned` (+0.01)、`search_result` (+0.04)。
- `BASE_RELIABILITY["jina_search"] = 0.72`（新增搜索解析器基线）。

**Phase 3 — Web 搜索能力**
- `DataPulseReader.search()` 异步方法：通过 Jina Search API 搜索全网，返回经评分排序的 `DataPulseItem` 列表。
- `fetch_content=True` 模式：对每个搜索结果 URL 通过完整 `ParsePipeline` 抓取以获取更高质量内容。
- `fetch_content=False` 模式：直接使用搜索结果的 snippet 构建 item。
- 批量 inbox 持久化（单次 `save()`），通过 `rank_items()` 统一评分。

**Phase 4 — CLI 集成**
- `--search QUERY`：搜索关键词。
- `--site DOMAIN`：限定搜索域（可重复）。
- `--search-limit N`：最大结果数（默认 5）。
- `--no-fetch`：跳过对搜索结果的全量抓取。
- `--target-selector CSS`：CSS 选择器定向抓取。
- `--no-cache`：绕过 Jina 缓存。
- `--with-alt`：启用 AI 图片描述。

**Phase 5 — MCP 集成**
- `search_web` 工具：搜索全网并返回经评分的 LLM 友好结果。
- `read_url_advanced` 工具：CSS 选择器定向读取 + 高级选项。

**Phase 6 — Generic Collector 增强回退**
- 在 GenericCollector 回退链尾部加入 Jina Reader：Trafilatura → BS4 → Firecrawl → Jina Reader → fail。
- 仅接受 >= 200 字符的结果。

### 测试
- 新增 56 个测试（29 + 17 + 10），全部通过。
- 零新依赖，全部使用 `requests`（已有）+ 标准库。

### 版本一致性
- `pyproject.toml` → 0.5.0
- `datapulse/__init__.py` → 0.5.0
- `datapulse_skill/manifest.json` → 0.5.0
- `docs/contracts/openclaw_datapulse_tool_contract.json` → 0.5.0

### 验收建议
1. `python3 -m pytest tests/test_jina_client.py tests/test_jina_collector_enhanced.py tests/test_jina_search.py -v` — 56 passed
2. `python3 -m pytest tests/ -v` — 351 passed（2 个预存 async 测试基础设施问题，非本次变更引入）
3. `git tag -l v0.5.0` — tag 存在

---

## Release: DataPulse v0.4.0

发布日期：2026-02-28
构建目标：多维评分 + 来源权威 + 跨源互证 + Digest 构建器 + Atom feed + arXiv/HN 采集器

### 主要变更

**Phase 1 — 基础扩展**
- **Source Authority Tiers**: `SourceRecord` 新增 `tier`（1=顶级 2=标准 3=小众）和 `authority_weight`（0.0-1.0），`SourceCatalog.build_authority_map()` 构建权威映射。Catalog 版本支持 `{1, 2}`。
- **arXiv Collector**: 解析 `arxiv.org/abs/`、`arxiv.org/pdf/`、`arxiv:XXXX.XXXXX`，通过 Atom API 获取结构化元数据（标题/作者/摘要/分类/PDF链接）。`BASE_RELIABILITY["arxiv"] = 0.88`。
- **HackerNews Collector**: 解析 `news.ycombinator.com` 条目，通过 Firebase API 获取数据。动态 confidence flags：`hn_score>=100` → `high_engagement`、`descendants>=50` → `comments`。`BASE_RELIABILITY["hackernews"] = 0.82`。
- **Atom 1.0 Feed**: `build_atom_feed()` 输出标准 Atom 1.0 XML。CLI `--query-atom`、MCP `build_atom_feed` 工具。

**Phase 2 — 多维评分引擎**
- `datapulse/core/scoring.py`：四维度加权评分（confidence 0.25 / authority 0.30 / corroboration 0.25 / recency 0.20）。
- `content_fingerprint()` 通过 n-gram shingling 实现同主题检测。
- `rank_items()` 统一入口：评分 → 排序 → 设置 `score`（0-100）、`quality_rank`、`extra["score_breakdown"]`。
- 时效性衰减：指数衰减 `2^(-age_h / half_life)`，`DATAPULSE_RECENCY_HALF_LIFE` 环境变量（默认 24h）。

**Phase 3 — Digest 构建器**
- `build_digest()` 产出包含 primary/secondary 故事的摘要信封。
- 指纹去重（同指纹保留最高分）+ 贪心多样性选择（惩罚同源聚集）。
- 输出 stats、provenance 元数据。CLI `--digest --top-n --secondary-n`、MCP `build_digest` 工具。

### 测试
- 新增 ~77 个测试，涵盖 arXiv/HN 采集器、评分引擎、Digest 构建器、Atom feed、source authority。

### 版本一致性
- `pyproject.toml` → 0.4.0
- `datapulse/__init__.py` → 0.4.0
- `datapulse_skill/manifest.json` → 0.4.0
- `docs/contracts/openclaw_datapulse_tool_contract.json` → 0.4.0

---

## Release: DataPulse v0.3.0

发布日期：2026-02-28
构建目标：代码质量门禁 + 功能增强 + 集成测试

### 主要变更

**Phase 1 — 代码质量门禁**
- mypy CI 集成：`pyproject.toml` 添加 `[tool.mypy]` 配置，CI 新增 `typecheck` job。
- 添加 `types-requests`、`types-beautifulsoup4` 到 dev 依赖。
- 修复 6 处 mypy 类型错误（BeautifulSoup `.get()` 返回类型、`NITTER_INSTANCES` 解析、CLI 变量遮蔽等）。
- 三份 README 新增「开发环境」小节（pre-commit 安装说明）。

**Phase 2 — 功能增强**
- `read_batch` 批量限速：`DATAPULSE_BATCH_CONCURRENCY` 环境变量控制并发上限（默认 5），使用 `asyncio.Semaphore`。
- JSON Feed v1.1 合规：`author` 字段替换为 `authors` 数组（修复 `getattr(item, "author")` 潜在 bug）。
- YouTube 章节解析：`_parse_chapters()` 从视频描述中提取 `MM:SS` / `H:MM:SS` 时间戳，写入 `extra["chapters"]`。
- Processed 状态管理：`UnifiedInbox.mark_processed()` / `query_unprocessed()` + `DataPulseReader` 透传 + 2 个 MCP 工具。

**Phase 3 — 基建演进**
- `tests/test_integration.py`：mock HTTP 层端到端集成测试。
- 新增 15 个测试用例，总计 198 个。

### 版本一致性
- `pyproject.toml` → 0.3.0
- `datapulse/__init__.py` → 0.3.0
- `datapulse_skill/manifest.json` → 0.3.0
- `docs/contracts/openclaw_datapulse_tool_contract.json` → 0.3.0

### 验收建议
1. `uv run --python 3.11 -- mypy datapulse/` — 0 errors
2. `uv run --python 3.11 -- ruff check datapulse/` — 0 errors
3. `uv run --python 3.11 -- python -m pytest tests/ -v` — 198 passed
4. `git tag -l v0.3.0` — tag 存在

---

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
