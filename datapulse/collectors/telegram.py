"""Telegram collector using Telethon API (optional dependency)."""

from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone

from datapulse.core.models import SourceType
from datapulse.core.utils import run_sync
from .base import BaseCollector, ParseResult


class TelegramCollector(BaseCollector):
    name = "telegram"
    source_type = SourceType.TELEGRAM
    reliability = 0.78

    def can_handle(self, url: str) -> bool:
        return "t.me" in url.lower()

    def parse(self, url: str) -> ParseResult:
        channel = self._extract_channel(url)
        if not channel:
            return ParseResult.failure(url, "Cannot parse Telegram channel")

        try:
            from telethon import TelegramClient
        except Exception:
            return ParseResult.failure(url, "Telethon not installed. pip install -e '.[telegram]'")

        api_id = os.getenv("TG_API_ID", "").strip()
        api_hash = os.getenv("TG_API_HASH", "").strip()
        if not api_id or not api_hash:
            return ParseResult.failure(url, "Missing TG_API_ID / TG_API_HASH")

        cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
        messages = []
        try:
            async def fetch() -> list[str]:
                from telethon.tl.types import Message

                async with TelegramClient(os.getenv("TG_SESSION_PATH", "./tg_session"), int(api_id), api_hash) as client:
                    entity = await client.get_entity(channel)
                    async for msg in client.iter_messages(entity, limit=20):
                        if not isinstance(msg, Message) or not msg.text:
                            continue
                        if msg.date < cutoff:
                            break
                        messages.append(f"[{msg.date.isoformat()}] {msg.text[:800]}")
                return messages

            content_rows = run_sync(fetch())
            if not content_rows:
                return ParseResult.failure(url, "No recent Telegram messages found")

            content = "\n\n".join(content_rows)
            return ParseResult(
                url=url,
                title=f"Telegram: {channel}",
                content=content,
                author=channel,
                excerpt=content[:260],
                source_type=self.source_type,
                tags=["telegram", "latest-messages"],
                confidence_flags=["telethon"],
                extra={"channel": channel, "count": len(content_rows)},
            )
        except Exception as exc:
            return ParseResult.failure(url, f"Telegram fetch failed: {exc}")

    @staticmethod
    def _extract_channel(url: str) -> str:
        parts = [p for p in url.split("/") if p and not p.startswith("http")]
        if not parts:
            return ""
        return parts[0]
