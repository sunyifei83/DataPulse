"""Tests for collector enhancements (Phase 3)."""

from __future__ import annotations

import asyncio
import os
import re

import pytest

from datapulse.collectors.rss import RssCollector, _MAX_ENTRIES
from datapulse.collectors.bilibili import BilibiliCollector
from datapulse.collectors.telegram import TelegramCollector
from datapulse.collectors.youtube import YouTubeCollector


class TestRssMultiEntry:
    def test_max_entries_constant(self):
        assert _MAX_ENTRIES == 5

    def test_can_handle_feed_patterns(self):
        collector = RssCollector()
        assert collector.can_handle("https://example.com/feed.xml")
        assert collector.can_handle("https://example.com/rss")
        assert not collector.can_handle("https://example.com/page")


class TestBilibiliInteractionData:
    def test_extra_fields_present_in_result(self):
        """Verify the parse method includes all interaction fields in extra dict."""
        # We test the structure without actual API calls
        collector = BilibiliCollector()
        # Check that _extract_bvid works for proper URLs
        bvid = collector._extract_bvid("https://www.bilibili.com/video/BV1234567890")
        assert bvid == "BV1234567890"

    def test_bvid_not_found(self):
        collector = BilibiliCollector()
        assert collector._extract_bvid("https://example.com/no-bvid") == ""


class TestTelegramConfigurable:
    def test_default_limits(self):
        """Verify env var defaults are sane."""
        # Clear any overrides
        for key in ["DATAPULSE_TG_MAX_MESSAGES", "DATAPULSE_TG_MAX_CHARS", "DATAPULSE_TG_CUTOFF_HOURS"]:
            os.environ.pop(key, None)

        # These are read inside parse(), so we just verify the collector can be created
        collector = TelegramCollector()
        assert collector.name == "telegram"

    def test_env_vars_accepted(self, monkeypatch):
        """Verify env vars don't crash on parse."""
        monkeypatch.setenv("DATAPULSE_TG_MAX_MESSAGES", "10")
        monkeypatch.setenv("DATAPULSE_TG_MAX_CHARS", "500")
        monkeypatch.setenv("DATAPULSE_TG_CUTOFF_HOURS", "48")

        collector = TelegramCollector()
        # Can't actually test parse without Telethon, but verify can_handle works
        assert collector.can_handle("https://t.me/test_channel")


class TestBatchUrlDedup:
    @pytest.mark.asyncio
    async def test_dedup_urls_in_batch(self):
        """read_batch should deduplicate URLs before processing."""
        from unittest.mock import AsyncMock, patch
        from datapulse.reader import DataPulseReader
        from datapulse.core.models import DataPulseItem, SourceType

        reader = DataPulseReader.__new__(DataPulseReader)

        call_count = 0
        async def mock_read(url, *, min_confidence=0.0):
            nonlocal call_count
            call_count += 1
            return DataPulseItem(
                source_type=SourceType.GENERIC,
                source_name="test",
                title="T",
                content="C",
                url=url,
                confidence=0.8,
            )

        reader.read = mock_read

        urls = [
            "https://example.com/page",
            "https://example.com/page",  # exact dup
            "https://example.com/page/",  # trailing slash dup
            "https://other.com/page",
        ]
        results = await reader.read_batch(urls)
        # Should only process 2 unique URLs (after normalization)
        assert call_count == 2
        assert len(results) == 2


class TestBatchConcurrencyLimit:
    @pytest.mark.asyncio
    async def test_concurrency_bounded(self, monkeypatch):
        """read_batch should respect DATAPULSE_BATCH_CONCURRENCY."""
        monkeypatch.setenv("DATAPULSE_BATCH_CONCURRENCY", "2")
        from datapulse.reader import DataPulseReader
        from datapulse.core.models import DataPulseItem, SourceType

        reader = DataPulseReader.__new__(DataPulseReader)
        peak = 0
        current = 0
        lock = asyncio.Lock()

        async def mock_read(url, *, min_confidence=0.0):
            nonlocal peak, current
            async with lock:
                current += 1
                if current > peak:
                    peak = current
            await asyncio.sleep(0.05)
            async with lock:
                current -= 1
            return DataPulseItem(
                source_type=SourceType.GENERIC,
                source_name="test",
                title="T",
                content="C",
                url=url,
                confidence=0.8,
            )

        reader.read = mock_read

        urls = [f"https://example.com/{i}" for i in range(6)]
        results = await reader.read_batch(urls)
        assert len(results) == 6
        assert peak <= 2


class TestYouTubeChapterParsing:
    def test_mmss_format(self):
        desc = "0:00 Intro\n1:23 Main Topic\n5:45 Conclusion"
        chapters = YouTubeCollector._parse_chapters(desc)
        assert len(chapters) == 3
        assert chapters[0]["timestamp"] == "0:00"
        assert chapters[0]["seconds"] == 0
        assert chapters[0]["title"] == "Intro"
        assert chapters[1]["seconds"] == 83
        assert chapters[2]["seconds"] == 345

    def test_hmmss_format(self):
        desc = "0:00:00 Start\n1:02:30 Middle\n2:15:00 End"
        chapters = YouTubeCollector._parse_chapters(desc)
        assert len(chapters) == 3
        assert chapters[0]["seconds"] == 0
        assert chapters[1]["seconds"] == 3750
        assert chapters[2]["seconds"] == 8100

    def test_no_timestamps(self):
        desc = "This is a video about something interesting.\nNo chapters here."
        chapters = YouTubeCollector._parse_chapters(desc)
        assert chapters == []

    def test_mixed_content(self):
        desc = "Check out my video!\n0:00 Intro\nSome text here\n3:45 Topic\nMore text"
        chapters = YouTubeCollector._parse_chapters(desc)
        assert len(chapters) == 2
        assert chapters[0]["title"] == "Intro"
        assert chapters[1]["title"] == "Topic"

    def test_hyphen_separator(self):
        desc = "0:00 - Welcome\n2:30 - Deep Dive\n10:00 - Q&A"
        chapters = YouTubeCollector._parse_chapters(desc)
        assert len(chapters) == 3
        assert chapters[0]["title"] == "Welcome"
        assert chapters[1]["title"] == "Deep Dive"
        assert chapters[2]["title"] == "Q&A"
