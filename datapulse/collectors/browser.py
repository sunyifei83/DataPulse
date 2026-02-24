"""Optional Playwright browser collector used as hard anti-scraping fallback."""

from __future__ import annotations

from pathlib import Path

from datapulse.core.models import SourceType
from datapulse.core.utils import clean_text
from datapulse.core.utils import run_sync
from .base import BaseCollector, ParseResult


class BrowserCollector(BaseCollector):
    name = "browser"
    source_type = SourceType.GENERIC
    reliability = 0.68

    def can_handle(self, url: str) -> bool:
        return True

    def parse(self, url: str, storage_state: str | None = None) -> ParseResult:
        try:
            from playwright.async_api import async_playwright
        except Exception:
            return ParseResult.failure(url, "Playwright is not installed")

        async def _run() -> ParseResult:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                kwargs = {}
                if storage_state and Path(storage_state).exists():
                    kwargs["storage_state"] = storage_state
                context = await browser.new_context(**kwargs)
                page = await context.new_page()
                try:
                    await page.goto(url, wait_until="domcontentloaded", timeout=30000)
                    await page.wait_for_timeout(1200)
                    title = await page.title()
                    content = await page.evaluate(
                        """() => {
                        const el = document.querySelector('article') || document.querySelector('main') || document.querySelector('.content') || document.body;
                        return el ? el.innerText : '';
                    }"""
                    )
                    return ParseResult(
                        url=url,
                        title=(title or "").strip()[:200],
                        content=clean_text(content or ""),
                        author="",
                        source_type=self.source_type,
                        tags=["playwright", "browser"],
                        confidence_flags=["browser-fallback"],
                        extra={"source": "playwright"},
                    )
                finally:
                    await context.close()
                    await browser.close()

        return run_sync(_run())
