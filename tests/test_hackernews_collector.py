"""Tests for HackerNewsCollector — no network calls."""

from __future__ import annotations

from unittest.mock import patch

import pytest

from datapulse.collectors.hackernews import HackerNewsCollector, extract_hn_id


class TestCanHandle:
    def test_item_url(self):
        c = HackerNewsCollector()
        assert c.can_handle("https://news.ycombinator.com/item?id=12345") is True

    def test_front_page(self):
        c = HackerNewsCollector()
        assert c.can_handle("https://news.ycombinator.com") is True

    def test_negative_generic(self):
        c = HackerNewsCollector()
        assert c.can_handle("https://example.com/page") is False

    def test_negative_reddit(self):
        c = HackerNewsCollector()
        assert c.can_handle("https://reddit.com/r/test") is False


class TestExtractId:
    def test_standard_url(self):
        assert extract_hn_id("https://news.ycombinator.com/item?id=12345") == "12345"

    def test_no_id(self):
        assert extract_hn_id("https://news.ycombinator.com") is None

    def test_multiple_params(self):
        assert extract_hn_id("https://news.ycombinator.com/item?id=99999&foo=bar") == "99999"


class TestBuildResult:
    def _make_collector(self):
        return HackerNewsCollector()

    def test_story_with_link(self):
        c = self._make_collector()
        mock_data = {
            "id": 12345,
            "type": "story",
            "title": "Show HN: My Project",
            "url": "https://myproject.com",
            "by": "testuser",
            "score": 150,
            "descendants": 80,
            "time": 1700000000,
        }
        with patch.object(c, "_fetch_item", return_value=mock_data):
            result = c.parse("https://news.ycombinator.com/item?id=12345")

        assert result.success is True
        assert result.title == "Show HN: My Project"
        assert result.author == "testuser"
        assert result.extra["hn_id"] == "12345"
        assert result.extra["hn_score"] == 150
        assert result.extra["hn_comments"] == 80
        assert result.extra["linked_url"] == "https://myproject.com"

    def test_text_post_no_link(self):
        c = self._make_collector()
        mock_data = {
            "id": 99999,
            "type": "story",
            "title": "Ask HN: What is your stack?",
            "text": "I'm curious about what people use.",
            "by": "asker",
            "score": 30,
            "descendants": 10,
            "time": 1700000000,
        }
        with patch.object(c, "_fetch_item", return_value=mock_data):
            result = c.parse("https://news.ycombinator.com/item?id=99999")

        assert result.success is True
        assert result.extra["linked_url"] == ""
        assert "curious" in result.content

    def test_high_engagement_flag(self):
        c = self._make_collector()
        mock_data = {
            "id": 11111,
            "type": "story",
            "title": "Popular Post",
            "by": "user",
            "score": 500,
            "descendants": 200,
            "time": 1700000000,
        }
        with patch.object(c, "_fetch_item", return_value=mock_data):
            result = c.parse("https://news.ycombinator.com/item?id=11111")

        assert "high_engagement" in result.confidence_flags
        assert "comments" in result.confidence_flags

    def test_low_engagement_no_flags(self):
        c = self._make_collector()
        mock_data = {
            "id": 22222,
            "type": "story",
            "title": "Quiet Post",
            "by": "user",
            "score": 5,
            "descendants": 2,
            "time": 1700000000,
        }
        with patch.object(c, "_fetch_item", return_value=mock_data):
            result = c.parse("https://news.ycombinator.com/item?id=22222")

        assert "high_engagement" not in result.confidence_flags
        assert "comments" not in result.confidence_flags
        assert "hn_api" in result.confidence_flags

    def test_deleted_item(self):
        c = self._make_collector()
        mock_data = {"id": 33333, "deleted": True}
        with patch.object(c, "_fetch_item", return_value=mock_data):
            result = c.parse("https://news.ycombinator.com/item?id=33333")

        assert result.success is False

    def test_dead_item(self):
        c = self._make_collector()
        mock_data = {"id": 44444, "dead": True}
        with patch.object(c, "_fetch_item", return_value=mock_data):
            result = c.parse("https://news.ycombinator.com/item?id=44444")

        assert result.success is False

    def test_no_id_in_url(self):
        c = self._make_collector()
        result = c.parse("https://news.ycombinator.com")
        assert result.success is False
