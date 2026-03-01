"""Tests for confidence scoring module."""

from __future__ import annotations

import pytest

from datapulse.core.confidence import compute_confidence, BASE_RELIABILITY


class TestComputeConfidence:
    def test_bounded_lower(self):
        """Score should never drop below 0.01."""
        score, reasons = compute_confidence(
            "unknown_parser",
            has_title=False,
            content_length=10,
            has_source=False,
            has_author=False,
            extra_flags=["jina"],
        )
        assert score >= 0.01

    def test_bounded_upper(self):
        """Score should never exceed 0.99."""
        score, reasons = compute_confidence(
            "manual",
            has_title=True,
            content_length=5000,
            has_source=True,
            has_author=True,
            media_hint="video",
            extra_flags=["transcript", "comments", "thread"],
        )
        assert score <= 0.99

    def test_base_reliability_known_parsers(self):
        for parser_name, expected_base in BASE_RELIABILITY.items():
            score, _ = compute_confidence(
                parser_name,
                has_title=False,
                content_length=500,
                has_source=False,
                has_author=False,
            )
            # base - 0.03 (no_title) = adjusted base
            assert score >= 0.01
            assert score <= 0.99

    def test_unknown_parser_fallback(self):
        score, _ = compute_confidence(
            "nonexistent",
            has_title=True,
            content_length=1000,
            has_source=True,
            has_author=True,
        )
        # fallback base is 0.62, + title(0.04) + source(0.03) + author(0.02) + medium(0.04) = 0.75
        assert 0.7 <= score <= 0.8

    def test_title_boost(self):
        with_title, _ = compute_confidence(
            "generic", has_title=True, content_length=500,
            has_source=False, has_author=False,
        )
        without_title, _ = compute_confidence(
            "generic", has_title=False, content_length=500,
            has_source=False, has_author=False,
        )
        assert with_title > without_title

    def test_source_boost(self):
        with_source, _ = compute_confidence(
            "generic", has_title=True, content_length=500,
            has_source=True, has_author=False,
        )
        without_source, _ = compute_confidence(
            "generic", has_title=True, content_length=500,
            has_source=False, has_author=False,
        )
        assert with_source > without_source

    def test_author_boost(self):
        with_author, _ = compute_confidence(
            "generic", has_title=True, content_length=500,
            has_source=False, has_author=True,
        )
        without_author, _ = compute_confidence(
            "generic", has_title=True, content_length=500,
            has_source=False, has_author=False,
        )
        assert with_author > without_author

    def test_content_length_tiers(self):
        thin, _ = compute_confidence(
            "generic", has_title=True, content_length=50,
            has_source=False, has_author=False,
        )
        medium, _ = compute_confidence(
            "generic", has_title=True, content_length=1000,
            has_source=False, has_author=False,
        )
        long, _ = compute_confidence(
            "generic", has_title=True, content_length=3000,
            has_source=False, has_author=False,
        )
        assert thin < medium < long

    def test_media_boost(self):
        # Use a parser with lower base to avoid hitting 0.99 ceiling
        video, _ = compute_confidence(
            "generic", has_title=True, content_length=1000,
            has_source=False, has_author=False, media_hint="video",
        )
        text, _ = compute_confidence(
            "generic", has_title=True, content_length=1000,
            has_source=False, has_author=False, media_hint="text",
        )
        assert video > text

    def test_transcript_flag(self):
        # Use a parser with lower base to avoid hitting 0.99 ceiling
        with_transcript, reasons = compute_confidence(
            "generic", has_title=True, content_length=500,
            has_source=False, has_author=False,
            extra_flags=["transcript"],
        )
        without_transcript, _ = compute_confidence(
            "generic", has_title=True, content_length=500,
            has_source=False, has_author=False,
        )
        assert with_transcript > without_transcript
        assert "transcript" in reasons

    def test_jina_flag_penalty(self):
        with_jina, reasons = compute_confidence(
            "generic", has_title=True, content_length=1000,
            has_source=True, has_author=False,
            extra_flags=["jina"],
        )
        without_jina, _ = compute_confidence(
            "generic", has_title=True, content_length=1000,
            has_source=True, has_author=False,
        )
        assert with_jina < without_jina
        assert "proxy_fallback" in reasons

    def test_reasons_no_duplicates(self):
        _, reasons = compute_confidence(
            "twitter", has_title=True, content_length=1000,
            has_source=True, has_author=True,
            extra_flags=["transcript", "comments"],
        )
        assert len(reasons) == len(set(reasons))

    def test_engagement_metrics_flag_boost(self):
        with_flag, reasons = compute_confidence(
            "xhs", has_title=True, content_length=1000,
            has_source=True, has_author=False,
            extra_flags=["engagement_metrics"],
        )
        without_flag, _ = compute_confidence(
            "xhs", has_title=True, content_length=1000,
            has_source=True, has_author=False,
        )
        assert with_flag > without_flag
        assert "engagement_metrics" in reasons

    def test_engagement_metrics_absent_no_effect(self):
        score_no_flag, reasons = compute_confidence(
            "xhs", has_title=True, content_length=1000,
            has_source=True, has_author=False,
        )
        assert "engagement_metrics" not in reasons

    def test_engagement_metrics_exact_delta(self):
        with_flag, _ = compute_confidence(
            "xhs", has_title=True, content_length=1000,
            has_source=True, has_author=False,
            extra_flags=["engagement_metrics"],
        )
        without_flag, _ = compute_confidence(
            "xhs", has_title=True, content_length=1000,
            has_source=True, has_author=False,
        )
        assert abs((with_flag - without_flag) - 0.03) < 1e-4

    def test_reasons_include_expected(self):
        _, reasons = compute_confidence(
            "twitter", has_title=True, content_length=1000,
            has_source=True, has_author=True,
        )
        assert "title" in reasons
        assert "source_name" in reasons
        assert "author" in reasons
        assert "medium_content" in reasons
