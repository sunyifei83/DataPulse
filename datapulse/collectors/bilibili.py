"""Bilibili collector via official API."""

from __future__ import annotations

import re
import requests

from datapulse.core.models import SourceType, MediaType
from datapulse.core.utils import clean_text
from .base import BaseCollector, ParseResult


class BilibiliCollector(BaseCollector):
    name = "bilibili"
    source_type = SourceType.BILIBILI
    reliability = 0.84
    api_url = "https://api.bilibili.com/x/web-interface/view"

    def can_handle(self, url: str) -> bool:
        return "bilibili.com" in url.lower() or "b23.tv" in url.lower()

    def parse(self, url: str) -> ParseResult:
        bvid = self._extract_bvid(url)
        if not bvid:
            return ParseResult.failure(url, "Could not detect BV/BVID.")

        resp = requests.get(
            self.api_url,
            params={"bvid": bvid},
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=20,
        )
        resp.raise_for_status()
        payload = resp.json()

        if payload.get("code") != 0:
            return ParseResult.failure(url, payload.get("message", "Bilibili API error"))

        data = payload.get("data", {})
        title = data.get("title", "")
        desc = data.get("desc", "")
        owner = data.get("owner", {})
        stat = data.get("stat", {})

        content = clean_text("\n\n".join([
            f"{title}",
            desc or "",
            f"Author: {owner.get('name', '')}",
            f"Play count: {stat.get('view', 0)}",
        ]))

        return ParseResult(
            url=url,
            title=title,
            author=owner.get("name", ""),
            content=content,
            excerpt=content[:240],
            source_type=self.source_type,
            media_type=MediaType.VIDEO.value,
            tags=["bilibili", "video"],
            confidence_flags=["api"],
            extra={"bvid": bvid, "video_id": bvid},
        )

    @staticmethod
    def _extract_bvid(url: str) -> str:
        m = re.search(r"BV[0-9A-Za-z]{10}", url)
        if m:
            return m.group(0)
        try:
            response = requests.get(url, timeout=8, allow_redirects=True)
            response.raise_for_status()
            redirected = response.url
            m = re.search(r"BV[0-9A-Za-z]{10}", redirected)
            if m:
                return m.group(0)
        except Exception:
            pass
        # short-link handling can be improved via API follow-up; keep as-is
        return ""
