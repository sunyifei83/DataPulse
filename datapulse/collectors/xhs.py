"""Xiaohongshu collector with Jina first and optional browser fallback."""

from __future__ import annotations

from pathlib import Path
from datapulse.core.models import SourceType
from datapulse.core.utils import session_path
from .base import BaseCollector, ParseResult
from .jina import JinaCollector


class XiaohongshuCollector(BaseCollector):
    name = "xhs"
    source_type = SourceType.XHS
    reliability = 0.72

    def can_handle(self, url: str) -> bool:
        return any(host in url.lower() for host in ["xiaohongshu.com", "xhslink.com", "xhslink.cn", "xiao"])

    def parse(self, url: str) -> ParseResult:
        jina = JinaCollector()
        result = jina.parse(url)
        if result.success:
            return ParseResult(
                url=url,
                title=result.title,
                content=result.content,
                author=result.author,
                excerpt=result.excerpt,
                source_type=self.source_type,
                tags=["xhs", "jina-fallback"],
                confidence_flags=["xiaohongshu", "jina"],
                extra=result.extra,
            )

        # optional session-based browser retry
        try:
            from .browser import BrowserCollector
            session = Path(session_path("xhs"))
            if session.exists():
                browser = BrowserCollector()
                return browser.parse(url, storage_state=str(session))
        except Exception:
            pass

        return ParseResult.failure(url, "XHS blocked and no fallback session available")
