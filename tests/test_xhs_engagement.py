"""Tests for XHS engagement metrics extraction."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from datapulse.collectors.xhs import _extract_engagement, XiaohongshuCollector
from datapulse.collectors.base import ParseResult
from datapulse.core.models import SourceType


class TestExtractEngagement:
    def test_chinese_metrics(self):
        content = "这篇笔记获得了 1234 赞 56 评论 789 收藏 12 分享"
        metrics = _extract_engagement(content)
        assert metrics["like_count"] == 1234
        assert metrics["comment_count"] == 56
        assert metrics["fav_count"] == 789
        assert metrics["share_count"] == 12

    def test_english_metrics(self):
        content = "This post has 500 likes 23 comments 100 favourites 8 shares"
        metrics = _extract_engagement(content)
        assert metrics["like_count"] == 500
        assert metrics["comment_count"] == 23
        assert metrics["fav_count"] == 100
        assert metrics["share_count"] == 8

    def test_mixed_language(self):
        content = "42 likes and 18 评论"
        metrics = _extract_engagement(content)
        assert metrics["like_count"] == 42
        assert metrics["comment_count"] == 18

    def test_no_metrics(self):
        content = "Just a regular post with no numbers that match engagement patterns."
        metrics = _extract_engagement(content)
        assert metrics == {}

    def test_comma_numbers(self):
        content = "12,345 likes 1,000 comments"
        metrics = _extract_engagement(content)
        assert metrics["like_count"] == 12345
        assert metrics["comment_count"] == 1000

    def test_partial_metrics(self):
        content = "This has 99 赞 but nothing else recognizable"
        metrics = _extract_engagement(content)
        assert metrics == {"like_count": 99}


class TestXhsParseEngagement:
    def test_parse_adds_engagement_to_extra(self):
        collector = XiaohongshuCollector()
        mock_result = ParseResult(
            url="https://www.xiaohongshu.com/explore/123",
            title="护肤分享",
            content="我的护肤心得 500 赞 30 评论 200 收藏",
            author="testuser",
            excerpt="我的护肤心得",
            source_type=SourceType.XHS,
            extra={},
        )
        with patch.object(
            collector, "parse",
            wraps=collector.parse,
        ):
            # Mock JinaCollector.parse to return our controlled result
            with patch(
                "datapulse.collectors.xhs.JinaCollector"
            ) as MockJina:
                MockJina.return_value.parse.return_value = mock_result
                result = collector.parse("https://www.xiaohongshu.com/explore/123")

        assert result.success is True
        assert "engagement" in result.extra
        assert result.extra["engagement"]["like_count"] == 500
        assert result.extra["engagement"]["comment_count"] == 30
        assert result.extra["engagement"]["fav_count"] == 200
        assert "engagement_metrics" in result.confidence_flags

    def test_parse_no_engagement_no_flag(self):
        collector = XiaohongshuCollector()
        mock_result = ParseResult(
            url="https://www.xiaohongshu.com/explore/456",
            title="No metrics post",
            content="Just plain content with no engagement numbers",
            author="testuser",
            excerpt="Just plain content",
            source_type=SourceType.XHS,
            extra={},
        )
        with patch(
            "datapulse.collectors.xhs.JinaCollector"
        ) as MockJina:
            MockJina.return_value.parse.return_value = mock_result
            result = collector.parse("https://www.xiaohongshu.com/explore/456")

        assert result.success is True
        assert "engagement" not in result.extra
        assert "engagement_metrics" not in result.confidence_flags
