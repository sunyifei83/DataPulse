"""Jina fallback collector."""

from __future__ import annotations

import requests
from urllib.parse import urlparse

from datapulse.core.models import SourceType
from datapulse.core.utils import clean_text
from .base import BaseCollector, ParseResult


class JinaCollector(BaseCollector):
    name = "jina"
    source_type = SourceType.GENERIC
    reliability = 0.64

    JINA_BASE = "https://r.jina.ai/"
    TIMEOUT = 30

    def can_handle(self, url: str) -> bool:
        return True

    def parse(self, url: str) -> ParseResult:
        parsed = urlparse(url)
        if not parsed.scheme:
            return ParseResult.failure(url, "Invalid URL: missing scheme")

        try:
            remote = f"{self.JINA_BASE}{url}"
            resp = requests.get(remote, timeout=self.TIMEOUT)
            resp.raise_for_status()
            text = resp.text or ""
            lines = [ln for ln in text.splitlines() if ln.strip()]
            title = ""
            if lines:
                title = lines[0].lstrip("#").strip()
                content = "\n".join(lines[1:]).strip()
            else:
                content = ""

            return ParseResult(
                url=url,
                title=clean_text(title)[:200],
                content=clean_text(content),
                author="",
                excerpt=self._safe_excerpt(content),
                source_type=self.source_type,
                tags=["jina", self.source_type.value],
                confidence_flags=["fallback", "markdown_proxy"],
                extra={"collector": "jina"},
            )
        except Exception as exc:  # noqa: BLE001
            return ParseResult.failure(url, f"JinaCollector failed: {exc}")
