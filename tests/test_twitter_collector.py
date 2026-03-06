"""Tests for TwitterCollector media extraction behavior."""

from __future__ import annotations

import json
from unittest.mock import patch

import requests

from datapulse.collectors.twitter import TwitterCollector


class _FakeHTTPResponse:
    def __init__(self, payload: dict):
        self._payload = payload

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def read(self) -> bytes:
        return json.dumps(self._payload).encode("utf-8")


def _sample_fxtwitter_payload() -> dict:
    return {
        "code": 200,
        "user": {
            "screen_name": "luffy",
            "name": "Luffy",
        },
        "tweet": {
            "created_at": "2026-03-05",
            "text": "8 prompts are in the attached image.",
            "stats": {
                "likes": 12,
                "retweets": 3,
                "views": 556,
            },
            "media": {
                "all": [
                    {
                        "type": "photo",
                        "url": "https://img.example.com/p1.jpg",
                        "altText": "Prompt 1: find moat. Prompt 2: check management quality.",
                    },
                ],
            },
        },
    }


def _sample_fxtwitter_payload_zero_engagement() -> dict:
    payload = _sample_fxtwitter_payload()
    payload["tweet"]["stats"] = {"likes": 0, "retweets": 0, "views": 0}
    return payload


class TestTwitterMediaExtraction:
    def test_not_applicable_without_media(self):
        collector = TwitterCollector()

        payload = collector._build_media_extraction([])

        assert payload["status"] == "not_applicable"
        assert payload["method"] == "none"
        assert payload["items"] == []
        assert payload["confidence"] == 0.0

    def test_extracts_from_fxtwitter_metadata(self, monkeypatch):
        monkeypatch.delenv("DATAPULSE_TWITTER_MEDIA_EXTRACT", raising=False)
        collector = TwitterCollector()

        payload = collector._build_media_extraction([
            {
                "type": "photo",
                "url": "https://img.example.com/p1.jpg",
                "altText": "Prompt 1: identify catalysts. Prompt 2: map downside.",
            },
        ])

        assert payload["status"] == "ok"
        assert payload["method"] == "fxtwitter_metadata"
        assert payload["confidence"] == 0.78
        assert len(payload["items"]) == 1
        assert "Prompt 1" in payload["items"][0]["text"]

    def test_uses_optional_generated_alt_when_enabled(self, monkeypatch):
        monkeypatch.setenv("DATAPULSE_TWITTER_MEDIA_EXTRACT", "1")
        collector = TwitterCollector()

        with patch.object(
            collector,
            "_extract_media_text_via_jina",
            return_value="Image text includes 8 investment prompts and examples.",
        ), patch("datapulse.collectors.twitter.get_secret", return_value="test-key"):
            payload = collector._build_media_extraction([
                {
                    "type": "photo",
                    "url": "https://img.example.com/p2.jpg",
                },
            ])

        assert payload["status"] == "ok"
        assert payload["method"] == "jina_generated_alt"
        assert payload["attempted"] == 1
        assert payload["failed"] == 0
        assert payload["items"][0]["method"] == "jina_generated_alt"
        assert payload["error_code"] == ""

    def test_fail_closed_marks_degraded_when_generated_alt_fails(self, monkeypatch):
        monkeypatch.setenv("DATAPULSE_TWITTER_MEDIA_EXTRACT", "1")
        collector = TwitterCollector()

        with patch.object(
            collector,
            "_extract_media_text_via_jina",
            side_effect=RuntimeError("timeout"),
        ), patch("datapulse.collectors.twitter.get_secret", return_value="test-key"):
            payload = collector._build_media_extraction([
                {
                    "type": "photo",
                    "url": "https://img.example.com/p3.jpg",
                },
            ])

        assert payload["status"] == "degraded"
        assert payload["failed"] == 1
        assert payload["items"] == []
        assert payload["error_code"] == "unknown_error"

    def test_marks_auth_missing_without_jina_api_key(self, monkeypatch):
        monkeypatch.setenv("DATAPULSE_TWITTER_MEDIA_EXTRACT", "1")
        collector = TwitterCollector()

        with patch.object(collector, "_extract_media_text_via_jina") as mocked_extract, patch(
            "datapulse.collectors.twitter.get_secret",
            return_value="",
        ):
            payload = collector._build_media_extraction([
                {
                    "type": "photo",
                    "url": "https://img.example.com/p4.jpg",
                },
            ])

        mocked_extract.assert_not_called()
        assert payload["status"] == "degraded"
        assert payload["attempted"] == 0
        assert payload["failed"] == 0
        assert payload["error_code"] == "auth_missing"

    def test_classifies_unauthorized_generated_alt_error(self, monkeypatch):
        monkeypatch.setenv("DATAPULSE_TWITTER_MEDIA_EXTRACT", "1")
        collector = TwitterCollector()
        response = requests.Response()
        response.status_code = 401
        http_error = requests.HTTPError("401 Client Error: Unauthorized", response=response)

        with patch.object(
            collector,
            "_extract_media_text_via_jina",
            side_effect=http_error,
        ), patch("datapulse.collectors.twitter.get_secret", return_value="test-key"):
            payload = collector._build_media_extraction([
                {
                    "type": "photo",
                    "url": "https://img.example.com/p5.jpg",
                },
            ])

        assert payload["status"] == "degraded"
        assert payload["attempted"] == 1
        assert payload["failed"] == 1
        assert payload["error_code"] == "auth_unauthorized"

    def test_parse_fxtwitter_exposes_structured_media_extraction(self, monkeypatch):
        monkeypatch.delenv("DATAPULSE_TWITTER_MEDIA_EXTRACT", raising=False)
        collector = TwitterCollector()
        payload = _sample_fxtwitter_payload()

        with patch("datapulse.collectors.twitter.urllib.request.urlopen", return_value=_FakeHTTPResponse(payload)):
            result = collector._parse_fxtwitter(
                "https://x.com/luffy/status/2029045175264461301",
                "luffy",
                "2029045175264461301",
            )

        assert result.success is True
        media_extraction = result.extra["media_extraction"]
        assert media_extraction["status"] == "ok"
        assert media_extraction["method"] == "fxtwitter_metadata"
        assert len(media_extraction["items"]) == 1
        assert "Media Extracted Signals" in result.content
        assert "engagement" in result.confidence_flags
        assert result.extra["engagement_available"] is True
        assert "media_extraction_available" in result.confidence_flags

    def test_parse_fxtwitter_zero_engagement_marks_unavailable(self, monkeypatch):
        monkeypatch.delenv("DATAPULSE_TWITTER_MEDIA_EXTRACT", raising=False)
        collector = TwitterCollector()
        payload = _sample_fxtwitter_payload_zero_engagement()

        with patch("datapulse.collectors.twitter.urllib.request.urlopen", return_value=_FakeHTTPResponse(payload)):
            result = collector._parse_fxtwitter(
                "https://x.com/luffy/status/2029045175264461302",
                "luffy",
                "2029045175264461302",
            )

        assert result.success is True
        assert "engagement" not in result.confidence_flags
        assert "engagement_unavailable" in result.confidence_flags
        assert result.extra["engagement_available"] is False
