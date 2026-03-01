"""Tests for TrendingCollector — no network calls."""

from __future__ import annotations

from unittest.mock import patch

import pytest

from datapulse.collectors.trending import (
    TrendingCollector,
    TrendSnapshot,
    build_trending_url,
    normalize_location,
    parse_volume,
)

# ---------------------------------------------------------------------------
# Embedded HTML fixtures
# ---------------------------------------------------------------------------

SAMPLE_CARD_HTML = """
<html><body>
<div class="trend-card">
  <h3>07:03</h3>
  <time datetime="2026-03-01T07:03:28Z">07:03</time>
  <ol class="trend-card__list">
    <li><a href="/t/AI">#AI</a> <span class="trend-card__count">125K</span></li>
    <li><a href="/t/Python">Python</a> <span class="trend-card__count">45.2K</span></li>
    <li><a href="/t/OpenAI">#OpenAI</a></li>
    <li><a href="/t/DataScience">Data Science</a> <span class="trend-card__count">8,500</span></li>
  </ol>
</div>
<div class="trend-card">
  <h3>06:03</h3>
  <time datetime="2026-03-01T06:03:28Z">06:03</time>
  <ol class="trend-card__list">
    <li><a href="/t/Morning">Morning</a> <span class="trend-card__count">90K</span></li>
    <li><a href="/t/Coffee">Coffee</a></li>
  </ol>
</div>
</body></html>
"""

SAMPLE_COUNTRY_HTML = """
<html><body>
<div class="trend-card">
  <h3>12:00</h3>
  <time datetime="2026-03-01T12:00:00Z">12:00</time>
  <ol class="trend-card__list">
    <li><a href="/t/USATrend">#USATrend</a> <span class="trend-card__count">1.2M</span></li>
    <li><a href="/t/Election">Election</a> <span class="trend-card__count">500K</span></li>
    <li><a href="/t/Weather">Weather</a> <span class="trend-card__count">200K</span></li>
  </ol>
</div>
</body></html>
"""

EMPTY_PAGE_HTML = """
<html><body>
<div class="content">
  <p>No trending data available.</p>
</div>
</body></html>
"""

FALLBACK_HTML = """
<html><body>
<h3>08:00 AM</h3>
<ol>
  <li><a href="/t/FallbackTrend">FallbackTrend</a></li>
  <li><a href="/t/AnotherOne">AnotherOne</a> <span>10K</span></li>
</ol>
</body></html>
"""

NO_VOLUME_HTML = """
<html><body>
<div class="trend-card">
  <h3>15:00</h3>
  <ol class="trend-card__list">
    <li><a href="/t/NoVol1">NoVol1</a></li>
    <li><a href="/t/NoVol2">NoVol2</a></li>
    <li><a href="/t/NoVol3">NoVol3</a></li>
  </ol>
</div>
</body></html>
"""


# ---------------------------------------------------------------------------
# TestCanHandle
# ---------------------------------------------------------------------------

class TestCanHandle:
    def test_trends24_url(self):
        c = TrendingCollector()
        assert c.can_handle("https://trends24.in/") is True

    def test_trends24_with_location(self):
        c = TrendingCollector()
        assert c.can_handle("https://trends24.in/united-states/") is True

    def test_www_subdomain(self):
        c = TrendingCollector()
        assert c.can_handle("https://www.trends24.in/japan/") is True

    def test_negative_twitter(self):
        c = TrendingCollector()
        assert c.can_handle("https://twitter.com/trending") is False

    def test_negative_generic(self):
        c = TrendingCollector()
        assert c.can_handle("https://example.com/trends") is False


# ---------------------------------------------------------------------------
# TestParseVolume
# ---------------------------------------------------------------------------

class TestParseVolume:
    @pytest.mark.parametrize(
        "text, expected_display, expected_raw",
        [
            ("125K", "125K", 125_000),
            ("45.2K", "45.2K", 45_200),
            ("1.2M", "1.2M", 1_200_000),
            ("8,500", "8,500", 8_500),
            ("", "", 0),
            ("   ", "", 0),
            ("10k", "10k", 10_000),
            ("Over 500K tweets", "Over 500K tweets", 500_000),
        ],
    )
    def test_parse_volume(self, text, expected_display, expected_raw):
        display, raw = parse_volume(text)
        assert display == expected_display
        assert raw == expected_raw


# ---------------------------------------------------------------------------
# TestNormalizeLocation
# ---------------------------------------------------------------------------

class TestNormalizeLocation:
    @pytest.mark.parametrize(
        "input_loc, expected",
        [
            ("us", "united-states"),
            ("US", "united-states"),
            ("uk", "united-kingdom"),
            ("jp", "japan"),
            ("worldwide", ""),
            ("global", ""),
            ("  us  ", "united-states"),
            ("my-custom-city", "my-custom-city"),
        ],
    )
    def test_normalize(self, input_loc, expected):
        assert normalize_location(input_loc) == expected

    def test_empty_string(self):
        assert normalize_location("") == ""

    def test_none_like(self):
        assert normalize_location("   ") == ""


# ---------------------------------------------------------------------------
# TestBuildUrl
# ---------------------------------------------------------------------------

class TestBuildUrl:
    def test_worldwide(self):
        assert build_trending_url("") == "https://trends24.in/"
        assert build_trending_url("worldwide") == "https://trends24.in/"

    def test_alias(self):
        assert build_trending_url("us") == "https://trends24.in/united-states/"

    def test_custom_slug(self):
        assert build_trending_url("new-york") == "https://trends24.in/new-york/"


# ---------------------------------------------------------------------------
# TestParse
# ---------------------------------------------------------------------------

class TestParse:
    def _make_collector(self):
        return TrendingCollector()

    def test_country_page(self):
        c = self._make_collector()
        with patch.object(c, "_fetch_page", return_value=SAMPLE_COUNTRY_HTML):
            result = c.parse("https://trends24.in/united-states/")

        assert result.success is True
        assert "United States" in result.title
        assert result.source_type.value == "trending"
        assert result.extra["trend_count"] == 3
        assert result.extra["trends"][0]["name"] == "#USATrend"
        assert result.extra["trends"][0]["volume_raw"] == 1_200_000

    def test_worldwide_page(self):
        c = self._make_collector()
        with patch.object(c, "_fetch_page", return_value=SAMPLE_CARD_HTML):
            result = c.parse("https://trends24.in/")

        assert result.success is True
        assert "Worldwide" in result.title
        assert result.extra["trend_count"] == 4
        assert result.extra["trends"][0]["name"] == "#AI"
        assert result.extra["trends"][0]["volume_raw"] == 125_000
        assert result.extra["trends"][2]["volume"] == ""

    def test_empty_page(self):
        c = self._make_collector()
        with patch.object(c, "_fetch_page", return_value=EMPTY_PAGE_HTML):
            result = c.parse("https://trends24.in/")

        assert result.success is False
        assert "No trending data" in result.error

    def test_confidence_flags_with_volume(self):
        c = self._make_collector()
        with patch.object(c, "_fetch_page", return_value=SAMPLE_CARD_HTML):
            result = c.parse("https://trends24.in/")

        assert "trending_snapshot" in result.confidence_flags
        assert "rich_data" in result.confidence_flags

    def test_no_volume_page(self):
        c = self._make_collector()
        with patch.object(c, "_fetch_page", return_value=NO_VOLUME_HTML):
            result = c.parse("https://trends24.in/")

        assert result.success is True
        assert "trending_snapshot" in result.confidence_flags
        assert "rich_data" not in result.confidence_flags


# ---------------------------------------------------------------------------
# TestFetchSnapshots
# ---------------------------------------------------------------------------

class TestFetchSnapshots:
    def test_multiple_snapshots(self):
        c = TrendingCollector()
        with patch.object(c, "_fetch_page", return_value=SAMPLE_CARD_HTML):
            snapshots = c.fetch_snapshots("", top_n=50)

        assert len(snapshots) == 2
        assert len(snapshots[0].trends) == 4
        assert len(snapshots[1].trends) == 2

    def test_top_n_limiting(self):
        c = TrendingCollector()
        with patch.object(c, "_fetch_page", return_value=SAMPLE_CARD_HTML):
            snapshots = c.fetch_snapshots("", top_n=2)

        assert len(snapshots[0].trends) == 2
        assert snapshots[0].trends[0].name == "#AI"
        assert snapshots[0].trends[1].name == "Python"

    def test_network_error(self):
        c = TrendingCollector()
        import requests as req
        with patch.object(c, "_fetch_page", side_effect=req.RequestException("timeout")):
            with pytest.raises(req.RequestException):
                c.fetch_snapshots("us")


# ---------------------------------------------------------------------------
# TestFallbackParsing
# ---------------------------------------------------------------------------

class TestFallbackParsing:
    def test_structural_h3_ol_fallback(self):
        c = TrendingCollector()
        with patch.object(c, "_fetch_page", return_value=FALLBACK_HTML):
            result = c.parse("https://trends24.in/")

        assert result.success is True
        assert result.extra["trend_count"] == 2
        assert result.extra["trends"][0]["name"] == "FallbackTrend"


# ---------------------------------------------------------------------------
# TestFormatContent
# ---------------------------------------------------------------------------

class TestFormatContent:
    def test_content_format(self):
        c = TrendingCollector()
        with patch.object(c, "_fetch_page", return_value=SAMPLE_CARD_HTML):
            result = c.parse("https://trends24.in/")

        assert "## Trending Topics on X" in result.content
        assert "1. #AI (125K)" in result.content
        assert "3. #OpenAI" in result.content
        assert "Total trending topics: 4" in result.content
