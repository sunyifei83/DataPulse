"""RSS feed collector."""

from __future__ import annotations

import feedparser
from datapulse.core.models import SourceType
from datapulse.core.utils import clean_text, generate_excerpt
from .base import BaseCollector, ParseResult


class RssCollector(BaseCollector):
    name = "rss"
    source_type = SourceType.RSS
    reliability = 0.74

    def can_handle(self, url: str) -> bool:
        lower = url.lower()
        return lower.endswith(".xml") or "/rss" in lower or "/atom" in lower

    def parse(self, url: str) -> ParseResult:
        feed = feedparser.parse(url)
        if feed.bozo and not feed.entries:
            return ParseResult.failure(url, f"Invalid RSS feed: {feed.bozo_exception}")
        source_title = feed.feed.get("title", url)
        if not feed.entries:
            return ParseResult.failure(url, "RSS feed has no entries")

        first = feed.entries[0]
        title = first.get("title", "")
        summary = first.get("summary", "")
        content = clean_text(summary)
        link = first.get("link", "")

        return ParseResult(
            url=link or url,
            title=f"[{source_title}] {title}",
            content=content or "No content available",
            author=source_title,
            excerpt=generate_excerpt(content),
            source_type=self.source_type,
            tags=["rss", "feed"],
            confidence_flags=["rss-feed", "latest-item"],
            extra={"source_url": url, "published": first.get("published", "")},
        )
