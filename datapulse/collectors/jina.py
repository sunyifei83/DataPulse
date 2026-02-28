"""Jina fallback collector."""

from __future__ import annotations

from urllib.parse import urlparse

import requests

from datapulse.core.models import SourceType
from datapulse.core.retry import retry
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
            text = self._fetch(url)
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
        except (requests.RequestException, requests.Timeout, OSError) as exc:
            return ParseResult.failure(url, f"JinaCollector failed: {exc}")
        except ValueError as exc:
            return ParseResult.failure(url, f"JinaCollector parse error: {exc}")

    @retry(max_attempts=2, base_delay=1.0, retryable=(requests.RequestException,))
    def _fetch(self, url: str) -> str:
        remote = f"{self.JINA_BASE}{url}"
        resp = requests.get(remote, timeout=self.TIMEOUT)
        resp.raise_for_status()
        return resp.text or ""
