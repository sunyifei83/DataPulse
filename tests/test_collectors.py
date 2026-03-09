"""Tests for collector can_handle correctness (no network required)."""

from __future__ import annotations

import json
import subprocess
import sys
from types import ModuleType

import pytest

from datapulse.collectors import (
    BilibiliCollector,
    GenericCollector,
    GitHubCollector,
    JinaCollector,
    NativeBridgeCollector,
    RedditCollector,
    RssCollector,
    TelegramCollector,
    TwitterCollector,
    WeChatCollector,
    WeiboCollector,
    XiaohongshuCollector,
    YouTubeCollector,
)
from datapulse.collectors.base import ParseResult
from datapulse.core.models import SourceType
from datapulse.core.router import ParsePipeline


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


class TestWeChatCollectorParse:
    def test_prefers_native_when_bridge_and_session_ready(self, monkeypatch, tmp_path):
        monkeypatch.setenv("DATAPULSE_NATIVE_COLLECTOR_BRIDGE_CMD", "bridge --json")
        monkeypatch.setenv("DATAPULSE_SESSION_DIR", str(tmp_path / "sessions"))
        monkeypatch.setattr("datapulse.collectors.wechat.session_valid", lambda platform: True)
        monkeypatch.setattr(
            "datapulse.collectors.wechat.JinaCollector.parse",
            lambda self, url: pytest.fail("Jina fallback should not run after native success"),
        )

        captured: dict[str, object] = {}

        def fake_run(cmd, **kwargs):
            captured["cmd"] = cmd
            captured["input"] = kwargs["input"]
            return subprocess.CompletedProcess(
                args=cmd,
                returncode=0,
                stdout=json.dumps(
                    {
                        "schema_version": "native_collector_bridge_result.v1",
                        "ok": True,
                        "profile": "wechat_spider",
                        "canonical_url": "https://mp.weixin.qq.com/s/native123",
                        "source_type": "wechat",
                        "title": "Native WeChat title",
                        "content": "这是微信原生桥接返回的正文内容，长度足够用于成功归一化。",
                        "author": "native-author",
                        "excerpt": "",
                        "tags": [],
                        "confidence_flags": [],
                        "extra": {"engagement": {"read_count": 1234}},
                        "provenance": {
                            "collector_family": "native_sidecar",
                            "bridge_profile": "wechat_spider",
                            "transport": "subprocess_json",
                            "session_key": "wechat",
                            "session_mode": "playwright_storage_state",
                            "raw_source_type": "wechat",
                            "fallback_policy": "wechat_native_then_jina_then_browser",
                        },
                    }
                ),
                stderr="",
            )

        monkeypatch.setattr("datapulse.collectors.native_bridge.subprocess.run", fake_run)

        result = WeChatCollector().parse("https://mp.weixin.qq.com/s/abc123")

        assert result.success is True
        assert result.source_type == SourceType.WECHAT
        assert "native-bridge" in result.tags
        assert "wechat_spider" in result.tags
        assert "session-authenticated" in result.confidence_flags
        assert result.extra["collector_provenance"]["bridge_profile"] == "wechat_spider"
        assert result.extra["collector_provenance"]["fallback_policy"] == "wechat_native_then_jina_then_browser"
        assert result.extra["engagement"]["read_count"] == 1234

        request_payload = json.loads(str(captured["input"]))
        assert captured["cmd"] == ["bridge", "--json"]
        assert request_payload["profile"] == "wechat_spider"
        assert request_payload["source_type_hint"] == "wechat"
        assert request_payload["metadata"]["fallback_chain"] == ["jina", "browser"]
        assert request_payload["session"]["key"] == "wechat"
        assert request_payload["session"]["required"] is True
        assert request_payload["session"]["path"].endswith("/wechat.json")

    def test_skips_native_without_wechat_session_and_uses_jina_fallback(self, monkeypatch):
        monkeypatch.setenv("DATAPULSE_NATIVE_COLLECTOR_BRIDGE_CMD", "bridge --json")
        monkeypatch.setattr("datapulse.collectors.wechat.session_valid", lambda platform: False)
        monkeypatch.setattr(
            "datapulse.collectors.native_bridge.subprocess.run",
            lambda *args, **kwargs: pytest.fail("native bridge should be skipped without a WeChat session"),
        )
        monkeypatch.setattr(
            "datapulse.collectors.wechat.JinaCollector.parse",
            lambda self, url: ParseResult(
                url=url,
                title="Jina title",
                content="wechat fallback content",
                author="jina-author",
                excerpt="wechat excerpt",
                source_type=SourceType.WECHAT,
                extra={},
            ),
        )

        result = WeChatCollector().parse("https://mp.weixin.qq.com/s/abc123")

        assert result.success is True
        assert result.source_type == SourceType.WECHAT
        assert "jina-fallback" in result.tags
        assert result.extra["collector_provenance"]["collector_family"] == "jina_fallback"
        assert result.extra["collector_provenance"]["bridge_profile"] == "wechat_spider"
        assert result.extra["collector_provenance"]["transport"] == "jina_reader"
        assert result.extra["collector_provenance"]["fallback_policy"] == "wechat_native_then_jina_then_browser"

    def test_preserves_browser_fallback_provenance(self, monkeypatch):
        monkeypatch.delenv("DATAPULSE_NATIVE_COLLECTOR_BRIDGE_CMD", raising=False)
        monkeypatch.setattr("datapulse.collectors.wechat.session_valid", lambda platform: True)
        monkeypatch.setattr(
            "datapulse.collectors.wechat.JinaCollector.parse",
            lambda self, url: ParseResult.failure(url, "jina blocked by policy"),
        )
        monkeypatch.setattr(
            "datapulse.collectors.browser.BrowserCollector.parse",
            lambda self, url, storage_state=None: ParseResult(
                url=url,
                title="Browser title",
                content="Browser recovered content",
                author="browser-author",
                excerpt="browser excerpt",
                source_type=SourceType.GENERIC,
                extra={},
            ),
        )

        result = WeChatCollector().parse("https://mp.weixin.qq.com/s/abc123")

        assert result.success is True
        assert result.source_type == SourceType.WECHAT
        assert "browser-fallback" in result.tags
        assert "wechat-browser" in result.confidence_flags
        assert result.extra["collector_provenance"]["collector_family"] == "browser_fallback"
        assert result.extra["collector_provenance"]["session_key"] == "wechat"
        assert result.extra["collector_provenance"]["fallback_policy"] == "wechat_native_then_jina_then_browser"


class TestWeiboCollectorCanHandle:
    @pytest.fixture()
    def collector(self):
        return WeiboCollector()

    @pytest.mark.parametrize("url", [
        "https://weibo.com/123456/abcdef",
        "https://www.weibo.com/123456/abcdef",
        "https://m.weibo.cn/detail/1234567890",
        "https://weibo.cn/status/1234567890",
    ])
    def test_accepts(self, collector, url):
        assert collector.can_handle(url) is True

    @pytest.mark.parametrize("url", [
        "https://example.com/post",
        "https://mp.weixin.qq.com/s/abc123",
        "https://www.xiaohongshu.com/explore/123",
    ])
    def test_rejects(self, collector, url):
        assert collector.can_handle(url) is False


class TestWeiboCollectorParse:
    def test_prefers_native_bridge_and_normalizes_weibo_source(self, monkeypatch):
        monkeypatch.setenv("DATAPULSE_NATIVE_COLLECTOR_BRIDGE_CMD", "bridge --json")
        monkeypatch.setattr(
            "datapulse.collectors.weibo.JinaCollector.parse",
            lambda self, url: pytest.fail("Jina fallback should not run after native Weibo success"),
        )

        captured: dict[str, object] = {}

        def fake_run(cmd, **kwargs):
            captured["cmd"] = cmd
            captured["input"] = kwargs["input"]
            return subprocess.CompletedProcess(
                args=cmd,
                returncode=0,
                stdout=json.dumps(
                    {
                        "schema_version": "native_collector_bridge_result.v1",
                        "ok": True,
                        "profile": "weibo_spider",
                        "canonical_url": "https://weibo.com/123456/native",
                        "source_type": "weibo",
                        "title": "Native Weibo title",
                        "content": "这是微博原生桥接返回的正文内容，长度足够用于成功归一化。",
                        "author": "native-weibo-author",
                        "excerpt": "",
                        "tags": [],
                        "confidence_flags": [],
                        "extra": {"engagement": {"repost_count": 88}},
                        "provenance": {
                            "collector_family": "native_sidecar",
                            "bridge_profile": "weibo_spider",
                            "transport": "subprocess_json",
                            "session_key": "",
                            "session_mode": "none",
                            "raw_source_type": "weibo",
                            "fallback_policy": "weibo_native_then_jina",
                        },
                    }
                ),
                stderr="",
            )

        monkeypatch.setattr("datapulse.collectors.native_bridge.subprocess.run", fake_run)

        result = WeiboCollector().parse("https://weibo.com/123456/abcdef")

        assert result.success is True
        assert result.source_type == SourceType.WEIBO
        assert result.url == "https://weibo.com/123456/native"
        assert "native-bridge" in result.tags
        assert "weibo_spider" in result.tags
        assert "weibo" in result.tags
        assert "native-bridge" in result.confidence_flags
        assert "session-authenticated" not in result.confidence_flags
        assert result.extra["collector_provenance"]["bridge_profile"] == "weibo_spider"
        assert result.extra["collector_provenance"]["fallback_policy"] == "weibo_native_then_jina"
        assert result.extra["engagement"]["repost_count"] == 88

        request_payload = json.loads(str(captured["input"]))
        assert captured["cmd"] == ["bridge", "--json"]
        assert request_payload["profile"] == "weibo_spider"
        assert request_payload["source_type_hint"] == "weibo"
        assert request_payload["metadata"]["fallback_chain"] == ["jina"]
        assert "session" not in request_payload

    def test_falls_back_to_jina_and_keeps_weibo_provenance(self, monkeypatch):
        monkeypatch.delenv("DATAPULSE_NATIVE_COLLECTOR_BRIDGE_CMD", raising=False)
        monkeypatch.setattr(
            "datapulse.collectors.weibo.JinaCollector.parse",
            lambda self, url: ParseResult(
                url=url,
                title="Jina Weibo title",
                content="weibo fallback content",
                author="jina-weibo-author",
                excerpt="weibo excerpt",
                source_type=SourceType.GENERIC,
                extra={},
            ),
        )

        result = WeiboCollector().parse("https://weibo.com/123456/abcdef")

        assert result.success is True
        assert result.source_type == SourceType.WEIBO
        assert "weibo" in result.tags
        assert "jina-fallback" in result.tags
        assert "jina" in result.confidence_flags
        assert result.extra["collector_provenance"]["collector_family"] == "jina_fallback"
        assert result.extra["collector_provenance"]["bridge_profile"] == "weibo_spider"
        assert result.extra["collector_provenance"]["fallback_policy"] == "weibo_native_then_jina"

    def test_pipeline_routes_weibo_urls_to_first_class_collector(self, monkeypatch):
        monkeypatch.setattr(
            "datapulse.collectors.weibo.WeiboCollector.parse",
            lambda self, url: ParseResult(
                url=url,
                title="Weibo routed title",
                content="Weibo routed content",
                source_type=SourceType.WEIBO,
            ),
        )
        monkeypatch.setattr(
            "datapulse.collectors.generic.GenericCollector.parse",
            lambda self, url: pytest.fail("Generic collector should not run before the Weibo collector"),
        )

        result, parser = ParsePipeline().route("https://weibo.com/123456/abcdef")

        assert result.success is True
        assert result.source_type == SourceType.WEIBO
        assert parser.name == "weibo"


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


class TestNativeBridgeCollectorCanHandle:
    @pytest.fixture()
    def collector(self):
        return NativeBridgeCollector()

    @pytest.mark.parametrize("url", [
        "https://www.xiaohongshu.com/explore/123",
        "https://xhslink.cn/abc",
        "https://www.zhihu.com/question/1",
        "https://tieba.baidu.com/p/123",
        "https://www.douyin.com/video/123",
        "https://www.kuaishou.com/short-video/abc",
    ])
    def test_accepts(self, collector, url):
        assert collector.can_handle(url) is True

    @pytest.mark.parametrize("url", [
        "https://mp.weixin.qq.com/s/abc123",
        "https://weibo.com/123456",
        "https://www.bilibili.com/video/BV1234567890",
        "https://example.com/page",
    ])
    def test_rejects(self, collector, url):
        assert collector.can_handle(url) is False


class TestNativeBridgeCollectorParse:
    def test_normalizes_native_bridge_success(self, monkeypatch, tmp_path):
        monkeypatch.setenv("DATAPULSE_NATIVE_COLLECTOR_BRIDGE_CMD", "bridge --json")
        monkeypatch.setenv("DATAPULSE_SESSION_DIR", str(tmp_path / "sessions"))
        session_file = tmp_path / "sessions" / "xhs.json"
        session_file.parent.mkdir(parents=True, exist_ok=True)
        session_file.write_text("{}", encoding="utf-8")

        captured: dict[str, object] = {}

        def fake_run(cmd, **kwargs):
            captured["cmd"] = cmd
            captured["input"] = kwargs["input"]
            return subprocess.CompletedProcess(
                args=cmd,
                returncode=0,
                stdout=json.dumps(
                    {
                        "schema_version": "native_collector_bridge_result.v1",
                        "ok": True,
                        "profile": "mediacrawler",
                        "canonical_url": "https://www.xiaohongshu.com/explore/abc123",
                        "source_type": "xhs",
                        "title": "Native title",
                        "content": "这是来自原生桥接的正文内容，长度足够用于归一化。",
                        "author": "native-author",
                        "excerpt": "",
                        "tags": ["already-tagged"],
                        "confidence_flags": [],
                        "extra": {"engagement": {"like_count": 12}},
                        "provenance": {
                            "collector_family": "native_sidecar",
                            "bridge_profile": "mediacrawler",
                            "transport": "subprocess_json",
                            "session_key": "xhs",
                            "session_mode": "playwright_storage_state",
                            "raw_source_type": "xhs",
                            "fallback_policy": "xhs_native_then_jina_then_browser",
                            "sidecar_name": "mediacrawler-sidecar",
                        },
                    }
                ),
                stderr="",
            )

        monkeypatch.setattr("datapulse.collectors.native_bridge.subprocess.run", fake_run)

        collector = NativeBridgeCollector()
        result = collector.parse("https://www.xiaohongshu.com/explore/abc123")

        assert result.success is True
        assert result.source_type == SourceType.XHS
        assert result.url == "https://www.xiaohongshu.com/explore/abc123"
        assert "native-bridge" in result.tags
        assert "mediacrawler" in result.tags
        assert "xhs" in result.tags
        assert "native-bridge" in result.confidence_flags
        assert "session-authenticated" in result.confidence_flags
        assert result.extra["collector_provenance"]["transport"] == "subprocess_json"
        assert result.extra["collector_provenance"]["sidecar_name"] == "mediacrawler-sidecar"
        assert result.extra["engagement"]["like_count"] == 12

        request_payload = json.loads(str(captured["input"]))
        assert captured["cmd"] == ["bridge", "--json"]
        assert request_payload["profile"] == "mediacrawler"
        assert request_payload["source_type_hint"] == "xhs"
        assert request_payload["metadata"]["fallback_chain"] == ["jina", "browser"]
        assert request_payload["session"]["key"] == "xhs"
        assert request_payload["session"]["path"].endswith("/xhs.json")

    def test_pipeline_keeps_xhs_fallback_when_bridge_unavailable(self, monkeypatch):
        monkeypatch.setenv("DATAPULSE_NATIVE_COLLECTOR_BRIDGE_CMD", "bridge --json")

        def fake_run(*args, **kwargs):
            raise OSError("bridge missing")

        monkeypatch.setattr("datapulse.collectors.native_bridge.subprocess.run", fake_run)
        monkeypatch.setattr(
            "datapulse.collectors.xhs.JinaCollector.parse",
            lambda self, url: ParseResult(
                url=url,
                title="Fallback title",
                content="fallback content with 20 赞",
                author="fallback-author",
                excerpt="fallback excerpt",
                source_type=SourceType.XHS,
                extra={},
            ),
        )

        pipeline = ParsePipeline()
        result, parser = pipeline.route("https://www.xiaohongshu.com/explore/abc123")

        assert result.success is True
        assert parser.name == "xhs"
        assert result.source_type == SourceType.XHS
        assert result.extra["collector_provenance"]["collector_family"] == "jina_fallback"
        assert result.extra["collector_provenance"]["transport"] == "jina_reader"
        assert result.extra["collector_provenance"]["fallback_policy"] == "xhs_native_then_jina_then_browser"


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


class TestGitHubCollectorCanHandle:
    @pytest.fixture()
    def collector(self):
        return GitHubCollector()

    @pytest.mark.parametrize("url", [
        "https://github.com/openlineage/OpenLineage",
        "https://www.github.com/dbt-labs/dbt-core",
        "https://github.com/apache/spark/issues/1",
    ])
    def test_accepts(self, collector, url):
        assert collector.can_handle(url) is True

    @pytest.mark.parametrize("url", [
        "https://github.com/topics/data-engineering",
        "https://github.com/explore",
        "https://example.com/repo",
    ])
    def test_rejects(self, collector, url):
        assert collector.can_handle(url) is False


class TestGenericCollectorCanHandle:
    def test_accepts_everything(self):
        collector = GenericCollector()
        assert collector.can_handle("https://any-url.com/anything") is True


class TestGenericCollectorParse:
    def test_prefers_general_news_extractor_for_chinese_news(self, monkeypatch):
        html = """
        <html lang="zh-CN">
          <head>
            <title>HTML fallback title</title>
            <meta name="author" content="meta-author" />
          </head>
          <body><article>测试页面</article></body>
        </html>
        """

        def fake_fetch(self, url):
            return html

        def fail_bs(self, html):
            pytest.fail("BeautifulSoup fallback should not run after GeneralNewsExtractor success")

        monkeypatch.setattr(GenericCollector, "_fetch_html", fake_fetch)
        monkeypatch.setattr(GenericCollector, "_extract_with_bs", fail_bs)
        monkeypatch.setattr(
            GenericCollector,
            "_extract_with_firecrawl",
            lambda self, url: pytest.fail("Firecrawl fallback should not run after GeneralNewsExtractor success"),
        )
        monkeypatch.setattr(
            GenericCollector,
            "_extract_with_jina",
            lambda self, url: pytest.fail("Jina fallback should not run after GeneralNewsExtractor success"),
        )

        fake_gne = ModuleType("gne")

        class FakeExtractor:
            def extract(self, html):
                return {
                    "title": "中文新闻标题",
                    "author": "中文作者",
                    "content": "这是中文新闻正文。" * 12,
                }

        fake_gne.GeneralNewsExtractor = FakeExtractor
        monkeypatch.setitem(sys.modules, "gne", fake_gne)

        result = GenericCollector().parse("https://example.com/china-news")

        assert result.success is True
        assert result.title == "中文新闻标题"
        assert result.author == "中文作者"
        assert "general_news_extractor" in result.tags
        assert "chinese-news-body" in result.tags
        assert result.confidence_flags == ["general_news_extractor"]
        assert result.extra["collector_provenance"]["collector_family"] == "native_library"
        assert result.extra["collector_provenance"]["bridge_profile"] == "general_news_extractor"
        assert result.extra["collector_provenance"]["transport"] == "in_process"
        assert (
            result.extra["collector_provenance"]["fallback_policy"]
            == "general_news_extractor_then_trafilatura_then_beautifulsoup_then_firecrawl_then_jina"
        )

    def test_falls_back_to_trafilatura_with_backend_provenance(self, monkeypatch):
        html = "<html><head><title>Fallback title</title></head><body><article>test</article></body></html>"

        monkeypatch.setattr(GenericCollector, "_fetch_html", lambda self, url: html)
        monkeypatch.setattr(
            GenericCollector,
            "_extract_with_general_news_extractor",
            lambda self, html, url: None,
        )
        monkeypatch.setattr(
            GenericCollector,
            "_extract_with_bs",
            lambda self, html: pytest.fail("BeautifulSoup fallback should not run after trafilatura success"),
        )
        monkeypatch.setattr(
            GenericCollector,
            "_extract_with_firecrawl",
            lambda self, url: pytest.fail("Firecrawl fallback should not run after trafilatura success"),
        )
        monkeypatch.setattr(
            GenericCollector,
            "_extract_with_jina",
            lambda self, url: pytest.fail("Jina fallback should not run after trafilatura success"),
        )

        fake_trafilatura = ModuleType("trafilatura")
        fake_trafilatura.extract = lambda *args, **kwargs: "Trafilatura extracted body. " * 8
        monkeypatch.setitem(sys.modules, "trafilatura", fake_trafilatura)

        result = GenericCollector().parse("https://example.com/fallback-news")

        assert result.success is True
        assert result.title == "Fallback title"
        assert "trafilatura" in result.tags
        assert result.confidence_flags == ["trafilatura"]
        assert result.extra["collector_provenance"]["collector_family"] == "html_parser"
        assert result.extra["collector_provenance"]["bridge_profile"] == "trafilatura"
        assert result.extra["collector_provenance"]["transport"] == "in_process"


def test_generic_check_reports_general_news_extractor_when_available(monkeypatch):
    fake_gne = ModuleType("gne")
    fake_gne.GeneralNewsExtractor = object
    monkeypatch.setitem(sys.modules, "gne", fake_gne)

    result = GenericCollector().check()

    assert result["available"] is True
    assert "general_news_extractor" in result["message"]


class TestJinaCollectorCanHandle:
    def test_accepts_everything(self):
        collector = JinaCollector()
        assert collector.can_handle("https://any-url.com/anything") is True
