<a id="top"></a>

# DataPulse (Chinese name: 数据脉搏) Intelligence Hub (English)

[🔙 Back to Main README](./README.md) | [🇨🇳 中文版本](./README_CN.md) | [⬆️ Back to top](#top)

## Core goal

DataPulse provides one shared intake path for URL extraction, confidence scoring, and memory output
for MCP, Skill, Agent, and bot workflows.

## Implemented features

- Parser routing: `twitter/x`, `reddit`, `youtube`, `bilibili`, `telegram`, `wechat`, `xiaohongshu`, `rss`, `generic web`
- Platform strategies:
  - Twitter: FxTwitter primary + Nitter fallback
  - Reddit: public `.json` API
  - YouTube: transcript first, optional Whisper fallback (`GROQ_API_KEY`)
  - Bilibili: official API + interaction stats (views/likes/coins/favorites/danmaku/shares)
  - Telegram: Telethon (`TG_API_ID`/`TG_API_HASH`), configurable via `DATAPULSE_TG_*` env vars
  - WeChat / Xiaohongshu: Jina fallback with retry, optional Playwright session fallback
  - RSS: multi-entry feed parsing (up to 5 entries), auto feed type detection
  - Generic web: Trafilatura / BeautifulSoup, optional Firecrawl fallback (`FIRECRAWL_API_KEY`)
- Outputs:
  - structured JSON (`DataPulseItem`)
  - optional Markdown inbox output (`datapulse-inbox.md` / custom path)
- Confidence pipeline:
  - parser reliability + title/content/source/author/feature flags
  - score bounded to [0.01, 0.99]
- Reliability:
  - centralized parse error handling with narrowed exceptions
  - `retry_with_backoff` decorator + `CircuitBreaker` for fault tolerance
  - in-memory TTL cache (thread-safe, zero external deps)
  - concurrent batch reads with auto URL dedup
  - dedupe and prune by max items / retention days
- Observability:
  - structured logging (`DATAPULSE_LOG_LEVEL` env var)
- Testing:
  - 183 unit tests across 12 modules
  - GitHub Actions CI (Python 3.10/3.11/3.12 matrix)

## Install

```bash
pip install -e .
pip install -e ".[all]"   # enable all optional capabilities
```

Optional groups:

- `.[trafilatura]`, `.[youtube]`, `.[telegram]`, `.[browser]`, `.[mcp]`, `.[notebooklm]`

## License

DataPulse uses **DataPulse Non-Commercial License v1.0**.
It is free for non-commercial use only (education, research, personal learning, internal PoC).
Commercial usage requires a separate license from the author.

Please refer to the root `LICENSE` file for the full terms.

## Workflows

### 1) CLI usage

```bash
# read one URL
datapulse https://x.com/xxxx/status/123

# batch read
datapulse --batch https://x.com/... https://www.reddit.com/... --min-confidence 0.45

# list memory
datapulse --list --limit 10 --min-confidence 0.30

# login state capture
datapulse --login xhs
datapulse --login wechat

# clear memory
datapulse --clear
```

### 2) Smoke checks

```bash
# list required env keys only
datapulse-smoke --list

# run selected platforms
datapulse-smoke --platforms xhs wechat --require-all

# run configured scenarios
datapulse-smoke --min-confidence 0.45
```

Smoke env vars:

- `DATAPULSE_SMOKE_TWITTER_URL`
- `DATAPULSE_SMOKE_REDDIT_URL`
- `DATAPULSE_SMOKE_YOUTUBE_URL`
- `DATAPULSE_SMOKE_BILIBILI_URL`
- `DATAPULSE_SMOKE_TELEGRAM_URL`
- `DATAPULSE_SMOKE_RSS_URL`
- `DATAPULSE_SMOKE_WECHAT_URL`
- `DATAPULSE_SMOKE_XHS_URL`

## MCP / Skill / Agent usage

- MCP server:

```bash
python -m datapulse.mcp_server
```

Tools:

- `read_url(url, min_confidence=0.0)`
- `read_batch(urls, min_confidence=0.0)`
- `query_inbox(limit=20, min_confidence=0.0)`
- `detect_platform(url)`
- `health()`

- Skill entry:

```python
from datapulse_skill import run
run("Please process: https://x.com/... and https://www.reddit.com/...")
```

- Agent usage:

```python
from datapulse.agent import DataPulseAgent

agent = DataPulseAgent(min_confidence=0.25)
result = await agent.handle("https://x.com/... and https://www.reddit.com/...")
```

## Configuration

- `INBOX_FILE`
- `DATAPULSE_MEMORY_DIR`
- `DATAPULSE_KEEP_DAYS` (default 30)
- `DATAPULSE_MAX_INBOX` (default 500)
- `OUTPUT_DIR`
- `DATAPULSE_MARKDOWN_PATH`
- `OBSIDIAN_VAULT`
- `DATAPULSE_SESSION_DIR` (default `~/.datapulse/sessions`)
- `TG_API_ID` / `TG_API_HASH`
- `NITTER_INSTANCES`
- `FXTWITTER_API_URL`
- `FIRECRAWL_API_KEY`
- `GROQ_API_KEY`
- `DATAPULSE_LOG_LEVEL` (default WARNING)
- `DATAPULSE_TG_MAX_MESSAGES` (default 20)
- `DATAPULSE_TG_MAX_CHARS` (default 800)
- `DATAPULSE_TG_CUTOFF_HOURS` (default 24)
- `DATAPULSE_SMOKE_*`
- `DATAPULSE_MIN_CONFIDENCE`

## Functional validation guide

1. Run one-off CLI checks, then multi-URL batch checks, then list/clear lifecycle.
2. Run platform smoke tests before promotion (`datapulse-smoke --platforms ...`).
3. For MCP/Skill/Agent orchestration, pass through `DataPulseItem.to_dict()` to keep schema stable.
4. Keep sensitive secrets and model endpoints out of repository history and inject them through your secret management path.

## Safety

- URL checks block local/private/localhost targets by default.
- `read_batch` skips failed single URLs by default; enforce strict mode in caller when needed.

## Notes

- Repository docs do not include local test environment or model endpoint plaintext.
- Keep sensitive runtime configuration outside the repository and load it in private runtime context.

## OpenClaw integration assets

- Tool contract: `docs/contracts/openclaw_datapulse_tool_contract.json`
- Quick validation scripts: `scripts/datapulse_local_smoke.sh`, `scripts/datapulse_remote_openclaw_smoke.sh`
- Release checklist: `docs/release_checklist.md`

```bash
chmod +x scripts/datapulse_local_smoke.sh scripts/datapulse_remote_openclaw_smoke.sh
export URL_1="https://x.com/xxxx/status/123"
export URL_BATCH="https://x.com/... https://www.reddit.com/..."
bash scripts/datapulse_local_smoke.sh
# remote execution requires VPS/M4 tunnel
bash scripts/datapulse_remote_openclaw_smoke.sh
```

## Release & publishing

- Build artifacts:
  - `python -m build --sdist --wheel .`
  - attach `dist/*.whl` and `dist/*.tar.gz`
- Publishing:
  - `./scripts/release_publish.sh --tag vX.Y.Z`
  - On tag push, `.github/workflows/release.yml` auto uploads release assets

[⬆️ Back to top](#top) | [🔙 Back to Main README](./README.md) | [🇨🇳 中文版本](./README_CN.md)
