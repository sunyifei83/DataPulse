"""Tests for RedditCollector parsing behavior (mocked network)."""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

from datapulse.collectors.reddit import RedditCollector


def _mock_urlopen_payload(payload: list[dict]) -> MagicMock:
    response = MagicMock()
    response.read.return_value = json.dumps(payload).encode("utf-8")

    context_manager = MagicMock()
    context_manager.__enter__.return_value = response
    context_manager.__exit__.return_value = False
    return context_manager


def _build_reddit_payload(*, num_comments: int = 3) -> list[dict]:
    post = {
        "title": "Which data quality tool do you use?",
        "author": "op",
        "subreddit": "dataengineering",
        "subreddit_name_prefixed": "r/dataengineering",
        "score": 123,
        "created_utc": 1_700_000_000,
        "num_comments": num_comments,
        "upvote_ratio": 0.93,
        "selftext": "Looking for practical recommendations.",
        "is_self": True,
        "link_flair_text": "Question",
    }
    comments = []
    for idx in range(num_comments):
        comments.append(
            {
                "kind": "t1",
                "data": {
                    "author": f"user{idx}",
                    "score": 100 - idx,
                    "body": f"comment-{idx}",
                    "replies": "",
                },
            }
        )
    return [
        {"data": {"children": [{"data": post}]}},
        {"data": {"children": comments}},
    ]


def test_parse_includes_subreddit_and_upvote_ratio_fields():
    collector = RedditCollector()
    payload = _build_reddit_payload(num_comments=3)
    with patch("urllib.request.urlopen", return_value=_mock_urlopen_payload(payload)):
        result = collector.parse("https://www.reddit.com/r/dataengineering/comments/abc123/test/")

    assert result.success is True
    assert result.extra["subreddit"] == "dataengineering"
    assert result.extra["subreddit_name_prefixed"] == "r/dataengineering"
    assert result.extra["upvote_ratio"] == 0.93


def test_parse_respects_max_comments_env_and_marks_truncation(monkeypatch):
    monkeypatch.setenv("DATAPULSE_REDDIT_MAX_COMMENTS", "2")
    collector = RedditCollector()
    payload = _build_reddit_payload(num_comments=5)
    with patch("urllib.request.urlopen", return_value=_mock_urlopen_payload(payload)):
        result = collector.parse("https://www.reddit.com/r/dataengineering/comments/abc123/test/")

    assert result.success is True
    assert result.content.count("### u/") == 2
    assert result.extra["comments_captured"] == 2
    assert result.extra["comments_available"] == 5
    assert result.extra["comments_truncated"] is True
    assert result.extra["max_comments"] == 2


def test_parse_extracts_comment_links_and_github_repos():
    collector = RedditCollector()
    payload = _build_reddit_payload(num_comments=2)
    payload[1]["data"]["children"][0]["data"]["body"] = (
        "Useful refs: https://github.com/openlineage/openlineage and https://docs.example.com/guide"
    )
    payload[1]["data"]["children"][1]["data"]["body"] = (
        "Another repo https://github.com/dbt-labs/dbt-core/issues/1"
    )

    with patch("urllib.request.urlopen", return_value=_mock_urlopen_payload(payload)):
        result = collector.parse("https://www.reddit.com/r/dataengineering/comments/abc123/test/")

    assert result.success is True
    assert result.extra["comment_link_count"] >= 3
    assert "https://github.com/openlineage/openlineage" in result.extra["comment_links"]
    assert "https://docs.example.com/guide" in result.extra["comment_links"]
    assert "openlineage/openlineage" in result.extra["github_repos"]
    assert "dbt-labs/dbt-core" in result.extra["github_repos"]
    assert result.extra["github_repo_count"] == 2
    assert result.extra["comment_link_extraction_degraded"] is False


def test_parse_can_disable_comment_link_extraction(monkeypatch):
    monkeypatch.setenv("DATAPULSE_REDDIT_EXTRACT_COMMENT_LINKS", "0")
    collector = RedditCollector()
    payload = _build_reddit_payload(num_comments=1)
    payload[1]["data"]["children"][0]["data"]["body"] = "https://github.com/acme/project"

    with patch("urllib.request.urlopen", return_value=_mock_urlopen_payload(payload)):
        result = collector.parse("https://www.reddit.com/r/dataengineering/comments/abc123/test/")

    assert result.success is True
    assert result.extra["comment_links"] == []
    assert result.extra["github_repos"] == []
    assert result.extra["comment_link_count"] == 0


def test_parse_sets_engagement_flags_and_community_signal():
    collector = RedditCollector()

    high_payload = _build_reddit_payload(num_comments=72)
    high_payload[0]["data"]["children"][0]["data"]["score"] = 180
    high_payload[0]["data"]["children"][0]["data"]["upvote_ratio"] = 0.93

    low_payload = _build_reddit_payload(num_comments=5)
    low_payload[0]["data"]["children"][0]["data"]["score"] = 0
    low_payload[0]["data"]["children"][0]["data"]["upvote_ratio"] = 0.61

    with patch("urllib.request.urlopen", return_value=_mock_urlopen_payload(high_payload)):
        high_result = collector.parse("https://www.reddit.com/r/dataengineering/comments/high/test/")
    with patch("urllib.request.urlopen", return_value=_mock_urlopen_payload(low_payload)):
        low_result = collector.parse("https://www.reddit.com/r/dataengineering/comments/low/test/")

    assert "high_engagement" in high_result.confidence_flags
    assert "low_engagement" in low_result.confidence_flags
    assert high_result.extra["community_signal"] > low_result.extra["community_signal"]
