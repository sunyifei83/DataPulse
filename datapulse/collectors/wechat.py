"""WeChat collector with jina fallback and optional browser fallback."""

from __future__ import annotations

from datapulse.core.models import SourceType
from datapulse.core.utils import session_path
from .base import BaseCollector, ParseResult
from .jina import JinaCollector


class WeChatCollector(BaseCollector):
    name = "wechat"
    source_type = SourceType.WECHAT
    reliability = 0.8

    def can_handle(self, url: str) -> bool:
        return "mp.weixin.qq.com" in url.lower()

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
                tags=["wechat", "jina-fallback"],
                confidence_flags=["wechat", "jina"],
                extra=result.extra,
            )

        # optional browser path if installed, omitted if unavailable
        try:
            from .browser import BrowserCollector

            browser = BrowserCollector()
            br = browser.parse(url, storage_state=session_path("wechat"))
            return br
        except Exception:
            return result
