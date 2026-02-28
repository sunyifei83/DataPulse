"""MCP server wrapper for DataPulse."""

from __future__ import annotations

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


async def _run_list_sources(include_inactive: bool = False, public_only: bool = True) -> str:
    reader = DataPulseReader()
    return json.dumps(reader.list_sources(include_inactive=include_inactive, public_only=public_only), ensure_ascii=False, indent=2)


async def _run_list_packs(public_only: bool = True) -> str:
    reader = DataPulseReader()
    return json.dumps(reader.list_packs(public_only=public_only), ensure_ascii=False, indent=2)


async def _run_resolve_source(url: str) -> str:
    reader = DataPulseReader()
    return json.dumps(reader.resolve_source(url), ensure_ascii=False, indent=2)


async def _run_list_subscriptions(profile: str = "default") -> str:
    reader = DataPulseReader()
    return json.dumps(reader.list_subscriptions(profile=profile), ensure_ascii=False, indent=2)


async def _run_query_feed(profile: str = "default", source_ids: list[str] | None = None, limit: int = 20,
                        min_confidence: float = 0.0, since: str | None = None) -> str:
    reader = DataPulseReader()
    items = reader.query_feed(profile=profile, source_ids=source_ids, limit=limit, min_confidence=min_confidence, since=since)
    return json.dumps([item.to_dict() for item in items], ensure_ascii=False, indent=2)


async def _run_build_json_feed(
    profile: str = "default",
    source_ids: list[str] | None = None,
    limit: int = 20,
    min_confidence: float = 0.0,
    since: str | None = None,
) -> str:
    reader = DataPulseReader()
    payload = reader.build_json_feed(profile=profile, source_ids=source_ids, limit=limit, min_confidence=min_confidence, since=since)
    return json.dumps(payload, ensure_ascii=False, indent=2)


async def _run_build_rss_feed(
    profile: str = "default",
    source_ids: list[str] | None = None,
    limit: int = 20,
    min_confidence: float = 0.0,
    since: str | None = None,
) -> str:
    reader = DataPulseReader()
    return reader.build_rss_feed(
        profile=profile,
        source_ids=source_ids,
        limit=limit,
        min_confidence=min_confidence,
        since=since,
    )


async def _run_build_digest(
    profile: str = "default",
    source_ids: list[str] | None = None,
    top_n: int = 3,
    secondary_n: int = 7,
    min_confidence: float = 0.0,
    since: str | None = None,
) -> str:
    reader = DataPulseReader()
    payload = reader.build_digest(
        profile=profile,
        source_ids=source_ids,
        top_n=top_n,
        secondary_n=secondary_n,
        min_confidence=min_confidence,
        since=since,
    )
    return json.dumps(payload, ensure_ascii=False, indent=2)


async def _run_build_atom_feed(
    profile: str = "default",
    source_ids: list[str] | None = None,
    limit: int = 20,
    min_confidence: float = 0.0,
    since: str | None = None,
) -> str:
    reader = DataPulseReader()
    return reader.build_atom_feed(
        profile=profile,
        source_ids=source_ids,
        limit=limit,
        min_confidence=min_confidence,
        since=since,
    )


async def _run_subscribe_source(profile: str, source_id: str) -> str:
    reader = DataPulseReader()
    ok = reader.subscribe_source(source_id, profile=profile)
    return json.dumps({"ok": ok, "source_id": source_id, "profile": profile}, ensure_ascii=False, indent=2)


async def _run_unsubscribe_source(profile: str, source_id: str) -> str:
    reader = DataPulseReader()
    ok = reader.unsubscribe_source(source_id, profile=profile)
    return json.dumps({"ok": ok, "source_id": source_id, "profile": profile}, ensure_ascii=False, indent=2)


async def _run_mark_processed(item_id: str, processed: bool = True) -> str:
    reader = DataPulseReader()
    ok = reader.mark_processed(item_id, processed=processed)
    return json.dumps({"ok": ok}, ensure_ascii=False, indent=2)


async def _run_query_unprocessed(limit: int = 20, min_confidence: float = 0.0) -> str:
    reader = DataPulseReader()
    items = reader.query_unprocessed(limit=limit, min_confidence=min_confidence)
    return json.dumps([item.to_dict() for item in items], ensure_ascii=False, indent=2)


async def _run_install_pack(profile: str, slug: str) -> str:
    reader = DataPulseReader()
    added = reader.install_pack(slug=slug, profile=profile)
    return json.dumps({"ok": added > 0, "added": added, "slug": slug, "profile": profile}, ensure_ascii=False, indent=2)


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
    async def list_sources(include_inactive: bool = False, public_only: bool = True) -> str:  # noqa: ANN001
        return await _run_list_sources(include_inactive=include_inactive, public_only=public_only)

    @app.tool()
    async def list_packs(public_only: bool = True) -> str:  # noqa: ANN001
        return await _run_list_packs(public_only=public_only)

    @app.tool()
    async def resolve_source(url: str) -> str:  # noqa: ANN001
        return await _run_resolve_source(url)

    @app.tool()
    async def list_subscriptions(profile: str = "default") -> str:  # noqa: ANN001
        return await _run_list_subscriptions(profile=profile)

    @app.tool()
    async def source_subscribe(profile: str, source_id: str) -> str:  # noqa: ANN001
        return await _run_subscribe_source(profile=profile, source_id=source_id)

    @app.tool()
    async def source_unsubscribe(profile: str, source_id: str) -> str:  # noqa: ANN001
        return await _run_unsubscribe_source(profile=profile, source_id=source_id)

    @app.tool()
    async def install_pack(profile: str, slug: str) -> str:  # noqa: ANN001
        return await _run_install_pack(profile=profile, slug=slug)

    @app.tool()
    async def query_feed(profile: str = "default", source_ids: list[str] | None = None,
                        limit: int = 20, min_confidence: float = 0.0, since: str | None = None) -> str:  # noqa: ANN001
        return await _run_query_feed(
            profile=profile,
            source_ids=source_ids,
            limit=limit,
            min_confidence=min_confidence,
            since=since,
        )

    @app.tool()
    async def build_json_feed(profile: str = "default", source_ids: list[str] | None = None,
                             limit: int = 20, min_confidence: float = 0.0, since: str | None = None) -> str:  # noqa: ANN001
        return await _run_build_json_feed(
            profile=profile,
            source_ids=source_ids,
            limit=limit,
            min_confidence=min_confidence,
            since=since,
        )

    @app.tool()
    async def build_rss_feed(profile: str = "default", source_ids: list[str] | None = None,
                            limit: int = 20, min_confidence: float = 0.0, since: str | None = None) -> str:  # noqa: ANN001
        return await _run_build_rss_feed(
            profile=profile,
            source_ids=source_ids,
            limit=limit,
            min_confidence=min_confidence,
            since=since,
        )

    @app.tool()
    async def build_atom_feed(profile: str = "default", source_ids: list[str] | None = None,
                              limit: int = 20, min_confidence: float = 0.0, since: str | None = None) -> str:  # noqa: ANN001
        return await _run_build_atom_feed(
            profile=profile,
            source_ids=source_ids,
            limit=limit,
            min_confidence=min_confidence,
            since=since,
        )

    @app.tool()
    async def build_digest(profile: str = "default", source_ids: list[str] | None = None,
                           top_n: int = 3, secondary_n: int = 7, min_confidence: float = 0.0,
                           since: str | None = None) -> str:  # noqa: ANN001
        return await _run_build_digest(
            profile=profile,
            source_ids=source_ids,
            top_n=top_n,
            secondary_n=secondary_n,
            min_confidence=min_confidence,
            since=since,
        )

    @app.tool()
    async def mark_processed(item_id: str, processed: bool = True) -> str:  # noqa: ANN001
        return await _run_mark_processed(item_id, processed=processed)

    @app.tool()
    async def query_unprocessed(limit: int = 20, min_confidence: float = 0.0) -> str:  # noqa: ANN001
        return await _run_query_unprocessed(limit=limit, min_confidence=min_confidence)

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
        import sys
        import time

        import datapulse

        reader = DataPulseReader()
        return json.dumps(
            {
                "ok": True,
                "version": datapulse.__version__,
                "python_version": sys.version.split()[0],
                "uptime_seconds": round(time.monotonic(), 1),
                "parsers": reader.router.available_parsers,
                "stored": len(reader.inbox.items),
            },
            ensure_ascii=False,
            indent=2,
        )

    app.run()
