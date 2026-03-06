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
