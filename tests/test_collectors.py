"""Tests for collector can_handle correctness (no network required)."""

from __future__ import annotations

import pytest

from datapulse.collectors import (
    TwitterCollector,
    RedditCollector,
    YouTubeCollector,
    BilibiliCollector,
    TelegramCollector,
    WeChatCollector,
    XiaohongshuCollector,
    RssCollector,
    GenericCollector,
    JinaCollector,
)


class TestTwitterCollectorCanHandle:
    @pytest.fixture()
    def collector(self):
        return TwitterCollector()

    @pytest.mark.parametrize("url", [
        "https://x.com/user/status/123456",
        "https://twitter.com/user/status/123456",
        "https://mobile.twitter.com/user/status/123",
        "https://mobile.x.com/user/status/123",
    ])
    def test_accepts(self, collector, url):
        assert collector.can_handle(url) is True

    @pytest.mark.parametrize("url", [
        "https://example.com",
        "https://reddit.com/r/test",
        "https://nottwitter.com/status/123",
    ])
    def test_rejects(self, collector, url):
        assert collector.can_handle(url) is False


class TestRedditCollectorCanHandle:
    @pytest.fixture()
    def collector(self):
        return RedditCollector()

    @pytest.mark.parametrize("url", [
        "https://www.reddit.com/r/python/comments/abc/test/",
        "https://old.reddit.com/r/test/comments/def/post/",
        "https://reddit.com/r/sub/comments/ghi/title/",
    ])
    def test_accepts(self, collector, url):
        assert collector.can_handle(url) is True

    def test_rejects_non_post(self):
        collector = RedditCollector()
        # Subreddit page without /comments/
        assert collector.can_handle("https://www.reddit.com/r/python/") is False

    def test_rejects_other(self):
        collector = RedditCollector()
        assert collector.can_handle("https://example.com") is False


class TestYouTubeCollectorCanHandle:
    @pytest.fixture()
    def collector(self):
        return YouTubeCollector()

    @pytest.mark.parametrize("url", [
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "https://youtube.com/watch?v=abc",
        "https://youtu.be/abc",
        "https://m.youtube.com/watch?v=abc",
    ])
    def test_accepts(self, collector, url):
        assert collector.can_handle(url) is True

    def test_rejects(self):
        collector = YouTubeCollector()
        assert collector.can_handle("https://vimeo.com/123") is False


class TestBilibiliCollectorCanHandle:
    @pytest.fixture()
    def collector(self):
        return BilibiliCollector()

    @pytest.mark.parametrize("url", [
        "https://www.bilibili.com/video/BV1234567890",
        "https://bilibili.com/video/BV1234567890",
        "https://b23.tv/abc",
    ])
    def test_accepts(self, collector, url):
        assert collector.can_handle(url) is True

    def test_rejects(self):
        collector = BilibiliCollector()
        assert collector.can_handle("https://example.com") is False


class TestTelegramCollectorCanHandle:
    @pytest.fixture()
    def collector(self):
        return TelegramCollector()

    def test_accepts(self, collector):
        assert collector.can_handle("https://t.me/channel/123") is True

    def test_rejects(self, collector):
        assert collector.can_handle("https://telegram.org") is False


class TestWeChatCollectorCanHandle:
    @pytest.fixture()
    def collector(self):
        return WeChatCollector()

    def test_accepts(self, collector):
        assert collector.can_handle("https://mp.weixin.qq.com/s/abc123") is True

    def test_rejects(self, collector):
        assert collector.can_handle("https://weixin.qq.com") is False


class TestXiaohongshuCollectorCanHandle:
    @pytest.fixture()
    def collector(self):
        return XiaohongshuCollector()

    @pytest.mark.parametrize("url", [
        "https://www.xiaohongshu.com/explore/123",
        "https://xiaohongshu.com/explore/123",
        "https://xhslink.com/abc",
        "https://xhslink.cn/abc",
    ])
    def test_accepts(self, collector, url):
        assert collector.can_handle(url) is True

    @pytest.mark.parametrize("url", [
        "https://example.com",
        "https://xiaomi.com/phone",
        "https://xiao.test.com/path",
    ])
    def test_rejects(self, collector, url):
        """Regression: substring matching like 'xiao' should not match."""
        assert collector.can_handle(url) is False


class TestRssCollectorCanHandle:
    @pytest.fixture()
    def collector(self):
        return RssCollector()

    @pytest.mark.parametrize("url", [
        "https://example.com/feed.xml",
        "https://example.com/rss",
        "https://example.com/atom.xml",
    ])
    def test_accepts(self, collector, url):
        assert collector.can_handle(url) is True

    def test_rejects(self):
        collector = RssCollector()
        assert collector.can_handle("https://example.com/page") is False


class TestGenericCollectorCanHandle:
    def test_accepts_everything(self):
        collector = GenericCollector()
        assert collector.can_handle("https://any-url.com/anything") is True


class TestJinaCollectorCanHandle:
    def test_accepts_everything(self):
        collector = JinaCollector()
        assert collector.can_handle("https://any-url.com/anything") is True
