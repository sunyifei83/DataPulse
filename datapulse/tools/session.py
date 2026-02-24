"""Platform session management helpers for authenticated browser fallback."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Dict

from datapulse.core.utils import run_sync, session_path

try:
    from playwright.async_api import async_playwright
except Exception:
    async_playwright = None  # type: ignore[assignment]

logger = logging.getLogger("datapulse.session")


PLATFORM_LOGIN_URLS: Dict[str, str] = {
    "xhs": "https://www.xiaohongshu.com/explore",
    "wechat": "https://mp.weixin.qq.com",
}


def supported_platforms() -> list[str]:
    return sorted(PLATFORM_LOGIN_URLS.keys())


def login_platform(platform: str) -> str:
    """Run a manual login flow and persist Playwright storage state."""
    platform = platform.lower().strip()
    if platform not in PLATFORM_LOGIN_URLS:
        raise ValueError(f"Unsupported platform: {platform}")

    if async_playwright is None:
        raise RuntimeError("Playwright is not installed. Install with: pip install -e '.[browser]'")

    return run_sync(_login(platform))


def _run_instructions(platform: str, state_path: Path) -> str:
    return (
        f"Platform: {platform}\n"
        f"Session saved to: {state_path}\n"
        "1) Complete login in the opened browser window.\n"
        "2) After login is successful, keep the window open and press Ctrl+C in this terminal.\n"
        "3) The session state will be persisted automatically."
    )


async def _login(platform: str) -> str:
    state_path = Path(session_path(platform))
    state_path.parent.mkdir(parents=True, exist_ok=True)
    start_url = PLATFORM_LOGIN_URLS[platform]

    async with async_playwright() as p:  # type: ignore[union-attr]
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        try:
            logger.info("Starting login for %s: %s", platform, start_url)
            await page.goto(start_url, wait_until="domcontentloaded", timeout=60000)
            print(_run_instructions(platform, state_path))
            try:
                while True:
                    if page.is_closed():
                        break
                    await page.wait_for_timeout(1000)
            except KeyboardInterrupt:
                pass
            await context.storage_state(path=str(state_path))
            return str(state_path)
        finally:
            await context.close()
            await browser.close()
