"""Main DataPulse reader API."""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime
from typing import Any

from datapulse.core.confidence import compute_confidence
from datapulse.core.models import DataPulseItem, SourceType
from datapulse.core.router import ParsePipeline
from datapulse.core.source_catalog import SourceCatalog
from datapulse.core.storage import UnifiedInbox, output_record_md, save_markdown
from datapulse.core.utils import inbox_path_from_env, normalize_language

logger = logging.getLogger("datapulse.reader")


class DataPulseReader:
    """End-to-end URL reader used by CLI/MCP/Skill/Agent."""

    def __init__(self, inbox_path: str | None = None):
        self.router = ParsePipeline()
        self.inbox = UnifiedInbox(inbox_path or inbox_path_from_env())
        self.catalog = SourceCatalog()

    async def read(self, url: str, *, min_confidence: float = 0.0) -> DataPulseItem:
        return await asyncio.to_thread(self._read_sync, url, min_confidence)

    def _read_sync(self, url: str, min_confidence: float = 0.0) -> DataPulseItem:
        result, parser = self.router.route(url)
        if not result.success:
            raise RuntimeError(result.error)

        item = self._to_item(result, parser.name)
        if item.confidence < min_confidence:
            raise RuntimeError(f"Confidence too low: {item.confidence:.3f}")

        if self.inbox.add(item):
            self.inbox.save()
        else:
            logger.info("Item already exists in inbox: %s", item.id)

        md_path = save_markdown(item)
        if md_path:
            logger.info("Saved markdown: %s", md_path)
        return item

    async def read_batch(
        self,
        urls: list[str],
        *,
        min_confidence: float = 0.0,
        return_all: bool = True,
    ) -> list[DataPulseItem]:
        # Normalize and deduplicate URLs
        seen: set[str] = set()
        unique_urls: list[str] = []
        for url in urls:
            normalized = url.strip().rstrip("/")
            if normalized and normalized not in seen:
                seen.add(normalized)
                unique_urls.append(url.strip())
        tasks = [self.read(url, min_confidence=min_confidence) for url in unique_urls]
        outputs: list[DataPulseItem] = []
        for item in await asyncio.gather(*tasks, return_exceptions=True):
            if isinstance(item, Exception):
                logger.warning("Batch entry failed: %s", item)
                if return_all:
                    continue
                raise item
            outputs.append(item)

        # Highest confidence first
        outputs.sort(key=lambda it: it.confidence, reverse=True)
        return outputs

    def _to_item(self, parse_result, parser_name: str) -> DataPulseItem:
        source_type = parse_result.source_type or SourceType.GENERIC
        lang = normalize_language(f"{parse_result.title} {parse_result.content}")
        conf_flags: list[str] = list(getattr(parse_result, "confidence_flags", []))
        source_name = parse_result.author or source_type.value
        source_name = source_name or parser_name

        confidence, reasons = compute_confidence(
            parser_name,
            has_title=bool(parse_result.title.strip()),
            content_length=len(parse_result.content or ""),
            has_source=bool(source_name),
            has_author=bool(parse_result.author),
            media_hint=getattr(parse_result, "media_type", "text") or "text",
            extra_flags=conf_flags,
        )

        return DataPulseItem(
            source_type=source_type,
            source_name=source_name,
            title=(parse_result.title or "Untitled").strip()[:300],
            content=parse_result.content or "",
            url=parse_result.url,
            parser=parser_name,
            confidence=confidence,
            confidence_factors=reasons,
            quality_rank=0,
            language=lang,
            tags=list(dict.fromkeys([
                source_type.value,
                parser_name,
                *getattr(parse_result, "tags", []),
            ])),
            extra={
                "raw_excerpt": parse_result.excerpt,
                **getattr(parse_result, "extra", {}),
            },
            score=0,
        )

    def detect_platform(self, url: str) -> str:
        result, parser = self.router.route(url)
        if result.success:
            return parser.name
        return "generic"

    def list_memory(self, limit: int = 20, min_confidence: float = 0.0) -> list[DataPulseItem]:
        return self.inbox.query(limit=limit, min_confidence=min_confidence)

    def resolve_source(self, url: str) -> dict[str, Any]:
        return self.catalog.resolve_source(url)

    def list_sources(self, *, include_inactive: bool = False, public_only: bool = False) -> list[dict[str, Any]]:
        return [s.to_dict() for s in self.catalog.list_sources(include_inactive=include_inactive, public_only=public_only)]

    def list_packs(self, *, public_only: bool = False) -> list[dict[str, Any]]:
        return [p.to_dict() for p in self.catalog.list_packs(public_only=public_only)]

    def list_subscriptions(self, profile: str = "default") -> list[str]:
        return self.catalog.list_subscriptions(profile=profile)

    def subscribe_source(self, source_id: str, *, profile: str = "default") -> bool:
        return self.catalog.subscribe(profile=profile, source_id=source_id)

    def unsubscribe_source(self, source_id: str, *, profile: str = "default") -> bool:
        return self.catalog.unsubscribe(profile=profile, source_id=source_id)

    def install_pack(self, slug: str, *, profile: str = "default") -> int:
        return self.catalog.install_pack(profile, slug=slug)

    def query_feed(
        self,
        *,
        profile: str = "default",
        source_ids: list[str] | None = None,
        limit: int = 20,
        min_confidence: float = 0.0,
        since: str | None = None,
    ) -> list[DataPulseItem]:
        all_items = self.inbox.all_items(min_confidence=min_confidence)
        filtered = self.catalog.filter_by_subscription(
            all_items,
            profile=profile,
            source_ids=source_ids,
        )
        if since:
            since_dt = None
            try:
                since_dt = datetime.fromisoformat(since)
            except Exception:
                since_dt = None
            if since_dt:
                valid: list[DataPulseItem] = []
                for item in filtered:
                    try:
                        ts = datetime.fromisoformat(item.fetched_at)
                    except Exception:
                        valid.append(item)
                        continue
                    if ts >= since_dt:
                        valid.append(item)
                filtered = valid

        ordered = sorted(filtered, key=lambda it: it.fetched_at, reverse=True)
        return ordered[: max(0, limit)]

    def build_json_feed(
        self,
        *,
        profile: str = "default",
        source_ids: list[str] | None = None,
        limit: int = 20,
        min_confidence: float = 0.0,
        since: str | None = None,
    ) -> dict[str, Any]:
        items = self.query_feed(
            profile=profile,
            source_ids=source_ids,
            limit=limit,
            min_confidence=min_confidence,
            since=since,
        )
        base = "https://datapulse.local"
        now = datetime.utcnow().isoformat() + "Z"
        return {
            "version": "https://jsonfeed.org/version/1.1",
            "title": f"DataPulse Feed ({profile})",
            "home_page_url": base,
            "feed_url": f"{base}/feed/{profile}.json",
            "items": [
                {
                    "id": item.id,
                    "title": item.title,
                    "content_text": item.content,
                    "date_published": item.fetched_at,
                    "url": item.url,
                    "source_type": item.source_type.value,
                    "source_name": item.source_name,
                    "author": getattr(item, "author", None),
                }
                for item in items
            ],
            "generated_at": now,
        }

    def build_rss_feed(
        self,
        *,
        profile: str = "default",
        source_ids: list[str] | None = None,
        limit: int = 20,
        min_confidence: float = 0.0,
        since: str | None = None,
    ) -> str:
        items = self.query_feed(
            profile=profile,
            source_ids=source_ids,
            limit=limit,
            min_confidence=min_confidence,
            since=since,
        )
        def _xml_escape(value: str) -> str:
            return (value.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("\"", "&quot;"))

        rows = []
        for item in items:
            pub = item.fetched_at
            try:
                dt = datetime.fromisoformat(pub).strftime("%a, %d %b %Y %H:%M:%S GMT")
            except Exception:
                dt = pub
            rows.append(
                "<item>"
                f"<title>{_xml_escape(item.title)}</title>"
                f"<link>{_xml_escape(item.url)}</link>"
                f"<guid>{_xml_escape(item.id)}</guid>"
                f"<pubDate>{_xml_escape(dt)}</pubDate>"
                f"<description>{_xml_escape(item.content[:1800])}</description>"
                "</item>"
            )

        payload = (
            '<?xml version="1.0" encoding="UTF-8"?>'
            "<rss version=\"2.0\"><channel>"
            "<title>DataPulse Feed</title>"
            "<description>Unified content feed</description>"
            "<link>https://datapulse.local</link>"
            + "".join(rows)
            + "</channel></rss>"
        )
        return payload


def _safe_markdown_document(item: DataPulseItem) -> str:
    return output_record_md(item)
