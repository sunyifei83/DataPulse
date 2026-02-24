<a id="top"></a>

# 数据脉搏（DataPulse）

[🔙 返回主 README](./README.md) | [🇺🇸 English version](./README_EN.md) | [⬆️ 回到顶部](#top)

## 数据脉搏（DataPulse）核心目标

建立统一的跨平台情报入口：对 URL 做采集、解析、置信评分、去重归档并输出结构化结果，服务于 MCP、Skill、Agent、Bot 等编排场景。

## 真实实现能力

- 路由与采集器：`twitter/x`, `reddit`, `youtube`, `bilibili`, `telegram`, `wechat`, `xiaohongshu`, `rss`, `generic web`
- 平台采集策略：
  - Twitter：FxTwitter 主链路 + Nitter 兜底
  - Reddit：公开 `.json` API
  - YouTube：优先字幕，其次可选 Whisper（`GROQ_API_KEY`）
  - Bilibili：官方 API
  - Telegram：Telethon（需 `TG_API_ID` / `TG_API_HASH`）
  - WeChat / 小红书：Jina 兜底，支持 Playwright 会话回退
  - RSS：读取最新条目
  - 通用网页：Trafilatura / BeautifulSoup，失败再尝试 Firecrawl（`FIRECRAWL_API_KEY`）
- 产出：
  - 结构化 JSON（`DataPulseItem`）
  - 可选 Markdown 记忆输出（`datapulse-inbox.md` 或自定义路径）
- 置信能力：
  - parser 可靠性 + 标题/正文长度/来源/作者/特征因子
  - 分数区间：0.01 ~ 0.99
- 稳定性：
  - 统一失败处理
  - 批量并发解析
  - 去重 + 时效裁剪（默认 500 条 / 30 天）

## 安装

```bash
pip install -e .
pip install -e ".[all]"   # 启用全部可选能力
```

可选安装组：

- `.[trafilatura]`、`.[youtube]`、`.[telegram]`、`.[browser]`、`.[mcp]`、`.[notebooklm]`

## 许可证

本仓库采用 **DataPulse Non-Commercial License v1.0**（不可商用许可证）。
仅支持非商用场景（教学、科研、个人学习、内部 PoC）免费使用；商业使用需联系作者获取商业授权。

完整条款请查看仓库根目录 `LICENSE`。

## 使用流程

### 1. CLI 侧

```bash
# 解析单条
datapulse https://x.com/xxxx/status/123

# 批量解析
datapulse --batch https://x.com/... https://www.reddit.com/... --min-confidence 0.45

# 列出内存
datapulse --list --limit 10 --min-confidence 0.30

# 登录态采集
datapulse --login xhs
datapulse --login wechat

# 清空内存
datapulse --clear
```

### 2. Smoke 测试

```bash
# 仅展示必须配置的变量
datapulse-smoke --list

# 按平台执行
datapulse-smoke --platforms xhs wechat --require-all

# 执行全部配置场景
datapulse-smoke --min-confidence 0.45
```

支持变量：

- `DATAPULSE_SMOKE_TWITTER_URL`
- `DATAPULSE_SMOKE_REDDIT_URL`
- `DATAPULSE_SMOKE_YOUTUBE_URL`
- `DATAPULSE_SMOKE_BILIBILI_URL`
- `DATAPULSE_SMOKE_TELEGRAM_URL`
- `DATAPULSE_SMOKE_RSS_URL`
- `DATAPULSE_SMOKE_WECHAT_URL`
- `DATAPULSE_SMOKE_XHS_URL`

## MCP / Skill / Agent

- MCP 服务端（需 `.[mcp]`）：

```bash
python -m datapulse.mcp_server
```

可用工具：

- `read_url(url, min_confidence=0.0)`
- `read_batch(urls, min_confidence=0.0)`
- `query_inbox(limit=20, min_confidence=0.0)`
- `detect_platform(url)`
- `health()`

- Skill 接口（适配 OpenClaw 等）：

```python
from datapulse_skill import run
run("请处理这些链接：https://x.com/... 和 https://www.reddit.com/...")
```

- Agent 接口：

```python
from datapulse.agent import DataPulseAgent

agent = DataPulseAgent(min_confidence=0.25)
result = await agent.handle("https://x.com/... and https://www.reddit.com/...")
```

## 配置项

- `INBOX_FILE`
- `DATAPULSE_MEMORY_DIR`
- `DATAPULSE_KEEP_DAYS`（默认 30）
- `DATAPULSE_MAX_INBOX`（默认 500）
- `OUTPUT_DIR`
- `DATAPULSE_MARKDOWN_PATH`
- `OBSIDIAN_VAULT`
- `DATAPULSE_SESSION_DIR`（默认 `~/.datapulse/sessions`）
- `TG_API_ID` / `TG_API_HASH`
- `NITTER_INSTANCES`
- `FXTWITTER_API_URL`
- `FIRECRAWL_API_KEY`
- `GROQ_API_KEY`
- `DATAPULSE_SMOKE_*`
- `DATAPULSE_MIN_CONFIDENCE`

## 测试与功能使用建议

1. 先跑 CLI 单条 -> 再跑批量 -> 再跑 `--list` 与 `--clear` 的生命周期操作。
2. 针对关键平台先执行 `datapulse-smoke --platforms ...` 做回归。
3. 为 MCP/Skill/Agent 统一消费 `DataPulseItem.to_dict()` 的 JSON 字段，减少跨组件格式不一致。
4. 敏感凭据通过外部秘钥渠道注入，不写入仓库。

## 安全边界

- URL 验证会拒绝本地/内网/非公网解析目标，降低 SSRF 风险。
- `read_batch` 默认跳过单条失败；如需“全量成功”策略，可在调用层收敛。

## 说明

- 仓库文档不包含本地测试环境或模型端点明文信息。
- 敏感配置通过私有运行时注入，不落库。

## OpenClaw 对接说明

- 工具合约模板：`docs/contracts/openclaw_datapulse_tool_contract.json`
- 快速验证脚本：`scripts/quick_test.sh`

```bash
chmod +x scripts/quick_test.sh
export URL_1="https://x.com/xxxx/status/123"
export URL_BATCH="https://x.com/... https://www.reddit.com/..."
./scripts/quick_test.sh
```

[⬆️ 回到顶部](#top) | [🔙 返回主 README](./README.md) | [🇺🇸 English version](./README_EN.md)
