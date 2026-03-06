"""Tests for confidence factor propagation in DataPulseReader."""

from __future__ import annotations

from datapulse.collectors.base import ParseResult
from datapulse.core.models import SourceType
from datapulse.reader import DataPulseReader


def test_to_item_preserves_collector_confidence_flags():
    reader = DataPulseReader.__new__(DataPulseReader)
    parse_result = ParseResult(
        url="https://x.com/luffy/status/123",
        title="Tweet by @luffy",
        content="content with media extraction degraded",
        author="@luffy",
        source_type=SourceType.TWITTER,
        confidence_flags=["fxtwitter", "media_extraction_degraded"],
    )

    item = reader._to_item(parse_result, "twitter")

    assert "fxtwitter" in item.confidence_factors
    assert "media_extraction_degraded" in item.confidence_factors
