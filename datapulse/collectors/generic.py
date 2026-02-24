"""Generic collector for any web page."""

from __future__ import annotations

import logging
import requests
from bs4 import BeautifulSoup

from datapulse.core.models import SourceType
from datapulse.core.utils import clean_text, validate_external_url, generate_excerpt
from .base import BaseCollector, ParseResult

logger = logging.getLogger("datapulse.parsers.generic")


class GenericCollector(BaseCollector):
    name = "generic"
    source_type = SourceType.GENERIC
    reliability = 0.72
    allowed_content_types = ("text/html", "application/xhtml+xml", "text/plain", "application/xml")
    max_response_bytes = 5_000_000

    def can_handle(self, url: str) -> bool:
        return True

    def parse(self, url: str) -> ParseResult:
        last_error = ""
        try:
            safe, reason = validate_external_url(url)
            if not safe:
                return ParseResult.failure(url, reason)

            html = self._fetch_html(url)
            extracted = ""
            try:
                import trafilatura  # type: ignore[import-not-found]

                extracted = trafilatura.extract(
                    html,
                    url=url,
                    include_comments=False,
                    include_tables=True,
                    include_links=True,
                    output_format="txt",
                    favor_precision=True,
                ) or ""
            except Exception as exc:
                logger.info("GenericCollector trafilatura unavailable for %s: %s", url, exc)

            title, author = self._extract_metadata(html, url)
            if extracted and len(extracted.strip()) > 50:
                content = clean_text(extracted)
                return ParseResult(
                    url=url,
                    title=title,
                    author=author,
                    content=content,
                    excerpt=self._safe_excerpt(content),
                    source_type=self.source_type,
                    tags=["generic", "trafilatura"],
                    confidence_flags=["trafilatura"],
                    extra={"url": url, "collector": "generic"},
                )

            bs_content = self._extract_with_bs(html)
            if bs_content:
                return ParseResult(
                    url=url,
                    title=title,
                    author=author,
                    content=bs_content,
                    excerpt=self._safe_excerpt(bs_content),
                    source_type=self.source_type,
                    tags=["generic", "beautifulsoup"],
                    confidence_flags=["fallback_bs4"],
                    extra={"url": url, "collector": "generic"},
                )
            last_error = "Could not extract meaningful text."
        except Exception as exc:  # noqa: BLE001
            last_error = str(exc)
            logger.warning("GenericCollector failed for %s: %s", url, last_error)

        # Optional firecrawl fallback
        fc_result = self._extract_with_firecrawl(url)
        if fc_result:
            return fc_result

        return ParseResult.failure(url, last_error or "Generic parse failed")

    def _fetch_html(self, url: str) -> str:
        with requests.get(
            url,
            timeout=self.timeout,
            allow_redirects=True,
            stream=True,
            headers={
                "User-Agent": "Mozilla/5.0",
                "Accept": "text/html,application/xhtml+xml;q=0.9,*/*;q=0.8",
            },
        ) as resp:
            resp.raise_for_status()
            safe, reason = validate_external_url(resp.url)
            if not safe:
                raise ValueError(f"Blocked redirect target: {reason}")

            content_type = (resp.headers.get("Content-Type") or "").lower()
            if content_type and not any(ct in content_type for ct in self.allowed_content_types):
                raise ValueError(f"Unsupported content type: {content_type}")

            body = bytearray()
            for chunk in resp.iter_content(chunk_size=8192):
                if not chunk:
                    continue
                body.extend(chunk)
                if len(body) > self.max_response_bytes:
                    raise ValueError(f"Response too large: > {self.max_response_bytes}")
            encoding = resp.encoding or resp.apparent_encoding or "utf-8"
            return body.decode(encoding, errors="replace")

    @staticmethod
    def _extract_metadata(html: str, url: str) -> tuple[str, str]:
        soup = BeautifulSoup(html, "lxml")
        title = ""
        title_tag = soup.find("title")
        if title_tag:
            title = title_tag.get_text(strip=True)
        og_title = soup.find("meta", property="og:title")
        if og_title and og_title.get("content"):
            title = og_title.get("content")
        author = ""
        meta_author = soup.find("meta", attrs={"name": "author"})
        if meta_author:
            author = meta_author.get("content", "")
        return title, author

    @staticmethod
    def _extract_with_bs(html: str) -> str:
        soup = BeautifulSoup(html, "lxml")
        for node in soup.find_all(["script", "style", "header", "footer", "nav", "aside"]):
            node.decompose()

        main = soup.find("article") or soup.find("main") or soup.find("div", attrs={"role": "main"})
        if not main:
            main = soup.body
        if not main:
            return ""
        content = main.get_text("\n", strip=True)
        return clean_text(content)

    def _extract_with_firecrawl(self, url: str) -> ParseResult | None:
        api_key = __import__("os").getenv("FIRECRAWL_API_KEY", "").strip()
        if not api_key:
            return None

        try:
            resp = requests.post(
                "https://api.firecrawl.dev/v1/scrape",
                json={"url": url, "formats": ["markdown"]},
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                timeout=self.timeout * 2,
            )
            resp.raise_for_status()
            payload = resp.json()
            if not payload.get("success"):
                return None
            data = payload.get("data", {})
            markdown = clean_text(data.get("markdown", ""))
            if len(markdown) < 200:
                return None
            return ParseResult(
                url=url,
                title=data.get("metadata", {}).get("title", ""),
                author=data.get("metadata", {}).get("author", ""),
                content=markdown,
                excerpt=generate_excerpt(markdown),
                source_type=self.source_type,
                tags=["generic", "firecrawl"],
                confidence_flags=["firecrawl"],
                extra={"collector": "generic", "firecrawl": True},
            )
        except Exception:
            return None
