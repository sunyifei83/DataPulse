"""Tests for collector health check (doctor) capability."""

from __future__ import annotations

import os

import pytest

from datapulse.collectors import (
    ArxivCollector,
    BaseCollector,
    BilibiliCollector,
    GenericCollector,
    HackerNewsCollector,
    JinaCollector,
    RedditCollector,
    RssCollector,
    TelegramCollector,
    TrendingCollector,
    TwitterCollector,
    WeChatCollector,
    XiaohongshuCollector,
    YouTubeCollector,
)
from datapulse.core.router import ParsePipeline


# ── Tier assignment ──────────────────────────────────────────────────────────

TIER_0 = [RssCollector, ArxivCollector, HackerNewsCollector]
TIER_1 = [
    TwitterCollector, RedditCollector, BilibiliCollector,
    TrendingCollector, GenericCollector, JinaCollector,
]
TIER_2 = [YouTubeCollector, XiaohongshuCollector, WeChatCollector, TelegramCollector]

ALL_COLLECTORS = TIER_0 + TIER_1 + TIER_2


@pytest.mark.parametrize("cls", TIER_0, ids=lambda c: c.name)
def test_tier_0_assignment(cls):
    assert cls.tier == 0


@pytest.mark.parametrize("cls", TIER_1, ids=lambda c: c.name)
def test_tier_1_assignment(cls):
    assert cls.tier == 1


@pytest.mark.parametrize("cls", TIER_2, ids=lambda c: c.name)
def test_tier_2_assignment(cls):
    assert cls.tier == 2


# ── check() shape validation ────────────────────────────────────────────────

@pytest.mark.parametrize("cls", ALL_COLLECTORS, ids=lambda c: c.name)
def test_check_returns_valid_shape(cls):
    collector = cls() if cls != JinaCollector else cls()
    result = collector.check()
    assert isinstance(result, dict)
    assert "status" in result
    assert "message" in result
    assert "available" in result
    assert result["status"] in ("ok", "warn", "err")
    assert isinstance(result["message"], str)
    assert isinstance(result["available"], bool)


# ── BaseCollector default check() ────────────────────────────────────────────

def test_base_collector_default_check():
    """BaseCollector.check() returns ok with 'no check implemented' message."""
    # Create a minimal concrete subclass
    class Stub(BaseCollector):
        name = "stub"

        def can_handle(self, url: str) -> bool:
            return False

        def parse(self, url: str):
            pass

    stub = Stub()
    result = stub.check()
    assert result["status"] == "ok"
    assert "no check" in result["message"]
    assert result["available"] is True


# ── Tier-2 collectors have setup_hint ────────────────────────────────────────

@pytest.mark.parametrize("cls", TIER_2, ids=lambda c: c.name)
def test_tier2_has_setup_hint(cls):
    assert cls.setup_hint, f"{cls.name} (tier 2) should have a setup_hint"


# ── Telegram check with/without env vars ─────────────────────────────────────

def test_telegram_check_no_env(monkeypatch):
    monkeypatch.delenv("TG_API_ID", raising=False)
    monkeypatch.delenv("TG_API_HASH", raising=False)
    result = TelegramCollector().check()
    assert result["available"] is False
    assert "not" in result["message"].lower()


def test_telegram_check_with_env_no_telethon(monkeypatch):
    monkeypatch.setenv("TG_API_ID", "12345")
    monkeypatch.setenv("TG_API_HASH", "abcdef")
    # telethon may or may not be installed — either way, check() should not crash
    result = TelegramCollector().check()
    assert isinstance(result["available"], bool)


# ── YouTube check ────────────────────────────────────────────────────────────

def test_youtube_check_no_deps(monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    result = YouTubeCollector().check()
    # Result depends on whether youtube-transcript-api is installed
    assert result["status"] in ("ok", "warn")


# ── Jina check ───────────────────────────────────────────────────────────────

def test_jina_check_no_key(monkeypatch):
    monkeypatch.delenv("JINA_API_KEY", raising=False)
    result = JinaCollector().check()
    assert result["status"] == "warn"
    assert result["available"] is True


def test_jina_check_with_key(monkeypatch):
    monkeypatch.setenv("JINA_API_KEY", "test-key")
    result = JinaCollector().check()
    assert result["status"] == "ok"


# ── Generic check ────────────────────────────────────────────────────────────

def test_generic_check():
    result = GenericCollector().check()
    assert result["available"] is True
    assert "backends" in result["message"] or "trafilatura" in result["message"]


# ── XHS check ────────────────────────────────────────────────────────────────

def test_xhs_check_no_session():
    """Without a real session file, XHS reports Jina-only mode."""
    result = XiaohongshuCollector().check()
    # In test env, no session file exists
    assert result["available"] is True
    assert result["status"] in ("ok", "warn")


# ── doctor() aggregation ────────────────────────────────────────────────────

def test_doctor_returns_all_tiers():
    pipeline = ParsePipeline()
    report = pipeline.doctor()
    assert "tier_0" in report
    assert "tier_1" in report
    assert "tier_2" in report


def test_doctor_total_equals_parsers():
    pipeline = ParsePipeline()
    report = pipeline.doctor()
    total = sum(len(v) for v in report.values())
    assert total == len(pipeline.parsers)


def test_doctor_entry_shape():
    pipeline = ParsePipeline()
    report = pipeline.doctor()
    for tier_key, entries in report.items():
        for entry in entries:
            assert "name" in entry
            assert "status" in entry
            assert "message" in entry
            assert "available" in entry
            assert "setup_hint" in entry


def test_doctor_tier0_all_ok():
    """Tier-0 collectors should always report ok (zero deps)."""
    pipeline = ParsePipeline()
    report = pipeline.doctor()
    for entry in report["tier_0"]:
        assert entry["status"] == "ok", f"{entry['name']} tier-0 should be ok"


def test_doctor_names_unique():
    pipeline = ParsePipeline()
    report = pipeline.doctor()
    names = []
    for entries in report.values():
        for entry in entries:
            names.append(entry["name"])
    assert len(names) == len(set(names)), "Doctor report has duplicate collector names"
