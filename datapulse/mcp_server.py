"""MCP server wrapper for DataPulse."""

from __future__ import annotations

import asyncio
import json

from datapulse.reader import DataPulseReader


async def _run_read_url(url: str, min_confidence: float = 0.0) -> str:
    reader = DataPulseReader()
    item = await reader.read(url, min_confidence=min_confidence)
    return json.dumps(item.to_dict(), ensure_ascii=False, indent=2)


async def _run_read_batch(urls: list[str], min_confidence: float = 0.0) -> str:
    reader = DataPulseReader()
    items = await reader.read_batch(urls, min_confidence=min_confidence)
    return json.dumps([item.to_dict() for item in items], ensure_ascii=False, indent=2)


if __name__ == "__main__":
    try:
        from mcp.server.fastmcp import FastMCP
    except Exception as exc:
        raise SystemExit(
            "MCP dependency is required. Install with: pip install -e '.[mcp]'\n"
            + str(exc)
        )

    app = FastMCP("datapulse")

    @app.tool()
    async def read_url(url: str, min_confidence: float = 0.0) -> str:  # noqa: ANN001
        return await _run_read_url(url, min_confidence=min_confidence)

    @app.tool()
    async def read_batch(urls: list[str], min_confidence: float = 0.0) -> str:  # noqa: ANN001
        return await _run_read_batch(urls, min_confidence=min_confidence)

    @app.tool()
    async def query_inbox(limit: int = 20, min_confidence: float = 0.0) -> str:  # noqa: ANN001
        reader = DataPulseReader()
        items = reader.list_memory(limit=limit, min_confidence=min_confidence)
        return json.dumps([item.to_dict() for item in items], ensure_ascii=False, indent=2)

    @app.tool()
    async def detect_platform(url: str) -> str:  # noqa: ANN001
        reader = DataPulseReader()
        return reader.detect_platform(url)

    @app.tool()
    async def health() -> str:
        reader = DataPulseReader()
        return json.dumps(
            {
                "ok": True,
                "parsers": reader.router.available_parsers,
                "stored": len(reader.inbox.items),
            },
            ensure_ascii=False,
            indent=2,
        )

    app.run()
