"""Xiaohongshu collector with Jina first and optional browser fallback."""

from __future__ import annotations

import re

from datapulse.core.models import SourceType
from datapulse.core.utils import session_path, session_valid

from .base import BaseCollector, ParseResult
from .jina import JinaCollector

# Patterns for engagement metrics (Chinese + English)
_ENGAGEMENT_PATTERNS: dict[str, re.Pattern[str]] = {
    "like_count": re.compile(r"(\d[\d,]*)\s*(?:likes?|赞|点赞)", re.IGNORECASE),
    "comment_count": re.compile(r"(\d[\d,]*)\s*(?:comments?|评论|留言)", re.IGNORECASE),
    "fav_count": re.compile(r"(\d[\d,]*)\s*(?:favou?rites?|收藏|已收藏)", re.IGNORECASE),
    "share_count": re.compile(r"(\d[\d,]*)\s*(?:shares?|分享|转发)", re.IGNORECASE),
}


def _parse_number(s: str) -> int:
    """Parse a number string with optional commas: '12,345' → 12345."""
    return int(s.replace(",", ""))


def _extract_engagement(content: str) -> dict[str, int]:
    """Extract engagement metrics from content text via regex."""
    metrics: dict[str, int] = {}
    for field_name, pattern in _ENGAGEMENT_PATTERNS.items():
        match = pattern.search(content)
        if match:
            try:
                metrics[field_name] = _parse_number(match.group(1))
            except (ValueError, IndexError):
                continue
    return metrics


class XiaohongshuCollector(BaseCollector):
    name = "xhs"
    source_type = SourceType.XHS
    reliability = 0.72

    def can_handle(self, url: str) -> bool:
        from urllib.parse import urlparse
        hostname = (urlparse(url).hostname or "").lower()
        return hostname in {
            "xiaohongshu.com", "www.xiaohongshu.com",
            "xhslink.com", "xhslink.cn",
        }

    def parse(self, url: str) -> ParseResult:
        jina = JinaCollector()
        result = jina.parse(url)
        if result.success:
            extra = dict(result.extra) if result.extra else {}
            confidence_flags = ["xiaohongshu", "jina"]

            engagement = _extract_engagement(result.content or "")
            if engagement:
                extra["engagement"] = engagement
                confidence_flags.append("engagement_metrics")

            return ParseResult(
                url=url,
                title=result.title,
                content=result.content,
                author=result.author,
                excerpt=result.excerpt,
                source_type=self.source_type,
                tags=["xhs", "jina-fallback"],
                confidence_flags=confidence_flags,
                extra=extra,
            )

        # optional session-based browser retry
        try:
            from .browser import BrowserCollector
            if session_valid("xhs"):
                browser = BrowserCollector()
                return browser.parse(url, storage_state=session_path("xhs"))
        except Exception:
            pass

        return ParseResult.failure(url, "XHS blocked and no fallback session available")
