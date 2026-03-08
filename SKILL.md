---
name: datapulse
description: Cross-platform content collection, web search, trending topics, confidence scoring, and watch/triage workflows for assistant and agent usage.
metadata: {"openclaw":{"requires":{"bins":["python3"]}}}
---

# DataPulse Skill (v0.8.0)

Use this skill when the user needs one or more of the following:

- Read or batch-read URLs across X, Reddit, YouTube, Bilibili, Telegram, WeChat, Xiaohongshu, RSS, arXiv, Hacker News, GitHub, and generic web pages
- Search the web, inspect trending topics, or collect cross-platform signals
- Create watch missions, alert routes, triage queues, or story evidence packs
- Run assistant-ready URL intake through `datapulse_skill.run()`

## Python Entry Point

```python
from datapulse_skill import run

run("请处理这些链接: https://x.com/... https://www.reddit.com/...")
```

## Core Capabilities

- URL ingestion with normalized `DataPulseItem` output
- Confidence scoring and ranking
- Web search and trending discovery
- Watch missions and alert routing
- Triage queue and story workspace workflows

## Environment Notes

- Python `3.10+`
- Optional search enhancement: `JINA_API_KEY`, `TAVILY_API_KEY`
- Optional platform enhancement: `TG_API_ID`, `TG_API_HASH`, `GROQ_API_KEY`
