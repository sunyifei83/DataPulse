"""Tests for enhanced Jina collector with JinaAPIClient integration."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from datapulse.collectors.jina import JinaCollector
from datapulse.core.confidence import BASE_RELIABILITY, compute_confidence
from datapulse.core.jina_client import JinaAPIClient, JinaReadOptions, JinaReadResult
from datapulse.core.retry import CircuitBreakerOpen


class TestJinaCollectorEnhanced:
    def test_default_reliability_is_0_72(self):
        c = JinaCollector()
        assert c.reliability == 0.72

    def test_parse_delegates_to_jina_client(self):
        c = JinaCollector()
        fake_result = JinaReadResult(
            url="https://example.com",
            content="# Great Title\n\nSome real content here.",
            status_code=200,
        )
        with patch.object(c._client, "read", return_value=fake_result) as mock_read:
            result = c.parse("https://example.com")
            mock_read.assert_called_once()
            assert result.success
            assert result.title == "Great Title"
            assert "Some real content here." in result.content

    def test_parse_with_target_selector(self):
        c = JinaCollector(target_selector=".article-body")
        fake_result = JinaReadResult(
            url="https://example.com",
            content="# Title\n\nTargeted content.",
            status_code=200,
        )
        with patch.object(c._client, "read", return_value=fake_result) as mock_read:
            result = c.parse("https://example.com")
            mock_read.assert_called_once()
            call_opts = mock_read.call_args[1]["options"]
            assert call_opts.target_selector == ".article-body"
            assert result.success
            assert "css_targeted" in result.confidence_flags

    def test_parse_with_wait_for_selector(self):
        c = JinaCollector(wait_for_selector="#content")
        fake_result = JinaReadResult(
            url="https://example.com",
            content="# Title\n\nLoaded content.",
            status_code=200,
        )
        with patch.object(c._client, "read", return_value=fake_result):
            result = c.parse("https://example.com")
            assert result.success

    def test_parse_with_generated_alt(self):
        c = JinaCollector(with_alt=True)
        fake_result = JinaReadResult(
            url="https://example.com",
            content="# Title\n\nContent with image captions.",
            status_code=200,
        )
        with patch.object(c._client, "read", return_value=fake_result) as mock_read:
            result = c.parse("https://example.com")
            call_opts = mock_read.call_args[1]["options"]
            assert call_opts.with_generated_alt is True
            assert "image_captioned" in result.confidence_flags

    def test_parse_with_no_cache(self):
        c = JinaCollector(no_cache=True)
        fake_result = JinaReadResult(
            url="https://example.com",
            content="# Title\n\nFresh content.",
            status_code=200,
        )
        with patch.object(c._client, "read", return_value=fake_result) as mock_read:
            result = c.parse("https://example.com")
            call_opts = mock_read.call_args[1]["options"]
            assert call_opts.no_cache is True
            assert result.success

    def test_parse_with_cookie(self):
        c = JinaCollector(cookie="session=abc")
        fake_result = JinaReadResult(
            url="https://example.com",
            content="# Title\n\nAuth content.",
            status_code=200,
        )
        with patch.object(c._client, "read", return_value=fake_result) as mock_read:
            result = c.parse("https://example.com")
            call_opts = mock_read.call_args[1]["options"]
            assert call_opts.cookie == "session=abc"

    def test_parse_failure_returns_failure(self):
        c = JinaCollector()
        with patch.object(c._client, "read", side_effect=Exception("network error")):
            result = c.parse("https://example.com")
            assert not result.success
            assert "network error" in result.error

    def test_parse_circuit_breaker_open_returns_failure(self):
        c = JinaCollector()
        with patch.object(c._client, "read", side_effect=CircuitBreakerOpen("open")):
            result = c.parse("https://example.com")
            assert not result.success
            assert "circuit" in result.error.lower() or "open" in result.error.lower()

    def test_parse_invalid_url_returns_failure(self):
        c = JinaCollector()
        result = c.parse("not-a-url")
        assert not result.success
        assert "missing scheme" in result.error.lower()

    def test_confidence_flags_default(self):
        c = JinaCollector()
        fake_result = JinaReadResult(
            url="https://example.com",
            content="# Title\n\nSome content.",
            status_code=200,
        )
        with patch.object(c._client, "read", return_value=fake_result):
            result = c.parse("https://example.com")
            # Default flags when no special options
            assert "markdown_proxy" in result.confidence_flags

    def test_parse_options_combined(self):
        c = JinaCollector(
            target_selector=".main",
            no_cache=True,
            with_alt=True,
            cookie="tok=1",
        )
        fake_result = JinaReadResult(
            url="https://example.com",
            content="# Title\n\nContent.",
            status_code=200,
        )
        with patch.object(c._client, "read", return_value=fake_result) as mock_read:
            result = c.parse("https://example.com")
            call_opts = mock_read.call_args[1]["options"]
            assert call_opts.target_selector == ".main"
            assert call_opts.no_cache is True
            assert call_opts.with_generated_alt is True
            assert call_opts.cookie == "tok=1"
            assert "css_targeted" in result.confidence_flags
            assert "image_captioned" in result.confidence_flags


class TestConfidenceNewFlags:
    def test_jina_search_base_reliability(self):
        assert "jina_search" in BASE_RELIABILITY
        assert BASE_RELIABILITY["jina_search"] == 0.72

    def test_jina_base_reliability_updated(self):
        assert BASE_RELIABILITY["jina"] == 0.72

    def test_css_targeted_flag_boost(self):
        with_flag, reasons = compute_confidence(
            "jina", has_title=True, content_length=1000,
            has_source=True, has_author=False,
            extra_flags=["css_targeted"],
        )
        without_flag, _ = compute_confidence(
            "jina", has_title=True, content_length=1000,
            has_source=True, has_author=False,
        )
        assert with_flag > without_flag
        assert "css_targeted" in reasons

    def test_image_captioned_flag_boost(self):
        with_flag, reasons = compute_confidence(
            "jina", has_title=True, content_length=1000,
            has_source=True, has_author=False,
            extra_flags=["image_captioned"],
        )
        without_flag, _ = compute_confidence(
            "jina", has_title=True, content_length=1000,
            has_source=True, has_author=False,
        )
        assert with_flag > without_flag
        assert "image_captioned" in reasons

    def test_search_result_flag_boost(self):
        with_flag, reasons = compute_confidence(
            "jina_search", has_title=True, content_length=1000,
            has_source=True, has_author=False,
            extra_flags=["search_result"],
        )
        without_flag, _ = compute_confidence(
            "jina_search", has_title=True, content_length=1000,
            has_source=True, has_author=False,
        )
        assert with_flag > without_flag
        assert "search_result" in reasons
