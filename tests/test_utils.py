"""Tests for core utility functions."""

from __future__ import annotations

import pytest

from datapulse.core.utils import (
    extract_urls,
    validate_external_url,
    resolve_platform_hint,
    is_xhs_url,
    is_twitter_url,
    is_reddit_url,
    is_youtube_url,
    is_bilibili_url,
    is_telegram_url,
    is_wechat_url,
    is_arxiv_url,
    is_hackernews_url,
    is_rss_feed,
    clean_text,
    generate_excerpt,
    normalize_language,
    content_hash,
    content_fingerprint,
    get_domain,
    generate_slug,
    session_valid,
    invalidate_session_cache,
    _session_ttl_cache,
)


class TestExtractUrls:
    def test_single_url(self):
        urls = extract_urls("Check out https://example.com for more")
        assert urls == ["https://example.com"]

    def test_multiple_urls(self):
        text = "Visit https://a.com and http://b.com today"
        urls = extract_urls(text)
        assert len(urls) == 2

    def test_dedup(self):
        text = "https://example.com and https://example.com again"
        urls = extract_urls(text)
        assert len(urls) == 1

    def test_strips_trailing_punct(self):
        text = "See https://example.com/page."
        urls = extract_urls(text)
        assert urls[0] == "https://example.com/page"

    def test_no_urls(self):
        assert extract_urls("No links here") == []

    def test_empty_string(self):
        assert extract_urls("") == []

    def test_preserves_order(self):
        text = "First: https://b.com then https://a.com"
        urls = extract_urls(text)
        assert urls == ["https://b.com", "https://a.com"]


class TestValidateExternalUrl:
    def test_valid_public_url(self):
        ok, msg = validate_external_url("https://example.com")
        assert ok is True

    def test_rejects_ftp(self):
        ok, msg = validate_external_url("ftp://example.com")
        assert ok is False

    def test_rejects_localhost(self):
        ok, msg = validate_external_url("http://localhost/admin")
        assert ok is False

    def test_rejects_private_ip(self):
        ok, msg = validate_external_url("http://192.168.1.1/")
        assert ok is False

    def test_rejects_loopback(self):
        ok, msg = validate_external_url("http://127.0.0.1/secret")
        assert ok is False

    def test_rejects_internal_suffix(self):
        ok, msg = validate_external_url("http://myhost.local/")
        assert ok is False

    def test_rejects_empty_host(self):
        ok, msg = validate_external_url("http:///path")
        assert ok is False

    def test_rejects_link_local_ip(self):
        ok, msg = validate_external_url("http://169.254.1.1/")
        assert ok is False


class TestResolvePlatformHint:
    @pytest.mark.parametrize("url,expected", [
        ("https://x.com/user/status/123", "twitter"),
        ("https://twitter.com/user/status/123", "twitter"),
        ("https://www.reddit.com/r/python/comments/abc/test/", "reddit"),
        ("https://youtube.com/watch?v=abc", "youtube"),
        ("https://youtu.be/abc", "youtube"),
        ("https://www.bilibili.com/video/BV1234567890", "bilibili"),
        ("https://t.me/channel", "telegram"),
        ("https://mp.weixin.qq.com/s/abc", "wechat"),
        ("https://www.xiaohongshu.com/explore/123", "xhs"),
        ("https://arxiv.org/abs/2301.00001", "arxiv"),
        ("https://news.ycombinator.com/item?id=12345", "hackernews"),
        ("https://example.com/feed.xml", "rss"),
        ("https://example.com/rss", "rss"),
        ("https://example.com/page", "generic"),
    ])
    def test_platform_hints(self, url, expected):
        assert resolve_platform_hint(url) == expected


class TestIsXhsUrl:
    def test_main_domain(self):
        assert is_xhs_url("https://xiaohongshu.com/explore/123") is True

    def test_www_domain(self):
        assert is_xhs_url("https://www.xiaohongshu.com/explore/123") is True

    def test_short_link(self):
        assert is_xhs_url("https://xhslink.com/abc") is True

    def test_not_xhs(self):
        assert is_xhs_url("https://example.com") is False

    def test_xiao_substring_no_match(self):
        """Regression: 'xiao' substring should NOT match arbitrary URLs."""
        assert is_xhs_url("https://xiaomi.com/phone") is False


class TestIsPlatformUrl:
    def test_twitter_variants(self):
        assert is_twitter_url("https://twitter.com/user") is True
        assert is_twitter_url("https://x.com/user") is True
        assert is_twitter_url("https://mobile.x.com/user") is True

    def test_reddit_variants(self):
        assert is_reddit_url("https://reddit.com/r/test") is True
        assert is_reddit_url("https://old.reddit.com/r/test") is True

    def test_youtube_variants(self):
        assert is_youtube_url("https://youtube.com/watch?v=x") is True
        assert is_youtube_url("https://youtu.be/x") is True

    def test_bilibili(self):
        assert is_bilibili_url("https://www.bilibili.com/video/BV123") is True
        assert is_bilibili_url("https://b23.tv/abc") is True

    def test_telegram(self):
        assert is_telegram_url("https://t.me/channel") is True

    def test_wechat(self):
        assert is_wechat_url("https://mp.weixin.qq.com/s/abc") is True


class TestCleanText:
    def test_collapses_spaces(self):
        assert clean_text("hello   world") == "hello world"

    def test_collapses_newlines(self):
        assert clean_text("a\n\n\n\nb") == "a\n\nb"

    def test_strips(self):
        assert clean_text("  hello  ") == "hello"

    def test_none_safe(self):
        assert clean_text(None) == ""


class TestGenerateExcerpt:
    def test_short_text_unchanged(self):
        text = "Short text"
        assert generate_excerpt(text) == text

    def test_long_text_truncated(self):
        text = "word " * 100
        result = generate_excerpt(text, max_length=50)
        assert len(result) <= 55  # with ellipsis

    def test_empty(self):
        assert generate_excerpt("") == ""


class TestNormalizeLanguage:
    def test_chinese(self):
        assert normalize_language("这是中文测试文本内容") == "zh"

    def test_english(self):
        assert normalize_language("This is English text content") == "en"

    def test_empty(self):
        assert normalize_language("") == "unknown"


class TestContentHash:
    def test_deterministic(self):
        assert content_hash("hello") == content_hash("hello")

    def test_different(self):
        assert content_hash("hello") != content_hash("world")

    def test_empty(self):
        assert content_hash("") == content_hash("")


class TestGetDomain:
    def test_basic(self):
        assert get_domain("https://www.example.com/page") == "example.com"

    def test_subdomain(self):
        assert get_domain("https://blog.example.com") == "example.com"


class TestGenerateSlug:
    def test_basic(self):
        slug = generate_slug("Hello World!")
        assert slug == "hello-world"

    def test_max_length(self):
        slug = generate_slug("a" * 100, max_length=20)
        assert len(slug) <= 20

    def test_empty(self):
        assert generate_slug("") == "untitled"


class TestIsArxivUrl:
    def test_abs(self):
        assert is_arxiv_url("https://arxiv.org/abs/2301.00001") is True

    def test_pdf(self):
        assert is_arxiv_url("https://arxiv.org/pdf/2301.00001") is True

    def test_export(self):
        assert is_arxiv_url("https://export.arxiv.org/api/query?id=2301.00001") is True

    def test_negative(self):
        assert is_arxiv_url("https://example.com") is False


class TestIsHackernewsUrl:
    def test_item(self):
        assert is_hackernews_url("https://news.ycombinator.com/item?id=12345") is True

    def test_negative(self):
        assert is_hackernews_url("https://example.com") is False


class TestContentFingerprint:
    def test_same_content_same_fingerprint(self):
        fp1 = content_fingerprint("The quick brown fox jumps over the lazy dog")
        fp2 = content_fingerprint("The quick brown fox jumps over the lazy dog")
        assert fp1 == fp2

    def test_different_content_different_fingerprint(self):
        fp1 = content_fingerprint("The quick brown fox jumps over the lazy dog")
        fp2 = content_fingerprint("A completely different article about quantum computing")
        assert fp1 != fp2

    def test_similar_content_case_insensitive(self):
        fp1 = content_fingerprint("Hello World Test Content Here Now")
        fp2 = content_fingerprint("hello world test content here now")
        assert fp1 == fp2

    def test_empty_content(self):
        fp = content_fingerprint("")
        assert isinstance(fp, str)
        assert len(fp) > 0

    def test_empty_content_unique(self):
        """Empty content items should NOT share fingerprints (no false corroboration)."""
        fp1 = content_fingerprint("")
        fp2 = content_fingerprint("")
        assert fp1 != fp2

    def test_whitespace_normalized(self):
        fp1 = content_fingerprint("hello   world   test   content   here")
        fp2 = content_fingerprint("hello world test content here")
        assert fp1 == fp2


class TestSessionValid:
    def setup_method(self):
        _session_ttl_cache.clear()

    def test_no_session_file(self, tmp_path, monkeypatch):
        monkeypatch.setenv("DATAPULSE_SESSION_DIR", str(tmp_path))
        assert session_valid("xhs") is False

    def test_session_file_exists(self, tmp_path, monkeypatch):
        monkeypatch.setenv("DATAPULSE_SESSION_DIR", str(tmp_path))
        (tmp_path / "xhs.json").write_text("{}")
        assert session_valid("xhs") is True

    def test_cache_hit(self, tmp_path, monkeypatch):
        monkeypatch.setenv("DATAPULSE_SESSION_DIR", str(tmp_path))
        (tmp_path / "xhs.json").write_text("{}")
        session_valid("xhs")  # populate cache
        (tmp_path / "xhs.json").unlink()  # remove file
        # Should still return True from cache
        assert session_valid("xhs") is True

    def test_invalidate_cache(self, tmp_path, monkeypatch):
        monkeypatch.setenv("DATAPULSE_SESSION_DIR", str(tmp_path))
        (tmp_path / "xhs.json").write_text("{}")
        session_valid("xhs")  # populate cache
        (tmp_path / "xhs.json").unlink()  # remove file
        invalidate_session_cache("xhs")
        # After invalidation, should check filesystem again
        assert session_valid("xhs") is False

    def test_negative_not_cached(self, tmp_path, monkeypatch):
        monkeypatch.setenv("DATAPULSE_SESSION_DIR", str(tmp_path))
        assert session_valid("xhs") is False
        # Create file after a negative check
        (tmp_path / "xhs.json").write_text("{}")
        # Should now find it (negative was NOT cached)
        assert session_valid("xhs") is True
