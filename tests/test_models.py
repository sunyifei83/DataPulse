"""Tests for DataPulseItem data model."""

from __future__ import annotations

import pytest

from datapulse.core.models import DataPulseItem, SourceType, MediaType


class TestDataPulseItem:
    def test_id_deterministic(self):
        """Same URL+title should produce same ID."""
        item1 = DataPulseItem(
            source_type=SourceType.TWITTER,
            source_name="test",
            title="Hello",
            content="world",
            url="https://x.com/test/status/1",
        )
        item2 = DataPulseItem(
            source_type=SourceType.TWITTER,
            source_name="test",
            title="Hello",
            content="different content",
            url="https://x.com/test/status/1",
        )
        assert item1.id == item2.id
        assert len(item1.id) == 12

    def test_id_differs_for_different_input(self):
        item1 = DataPulseItem(
            source_type=SourceType.GENERIC,
            source_name="a",
            title="Title A",
            content="c",
            url="https://example.com/a",
        )
        item2 = DataPulseItem(
            source_type=SourceType.GENERIC,
            source_name="a",
            title="Title B",
            content="c",
            url="https://example.com/b",
        )
        assert item1.id != item2.id

    def test_custom_id_preserved(self):
        item = DataPulseItem(
            source_type=SourceType.GENERIC,
            source_name="x",
            title="y",
            content="z",
            url="https://example.com",
            id="custom123",
        )
        assert item.id == "custom123"

    def test_fetched_at_auto_set(self):
        item = DataPulseItem(
            source_type=SourceType.GENERIC,
            source_name="x",
            title="y",
            content="z",
            url="https://example.com",
        )
        assert item.fetched_at
        assert "T" in item.fetched_at  # ISO format

    def test_round_trip_to_dict_from_dict(self):
        original = DataPulseItem(
            source_type=SourceType.YOUTUBE,
            source_name="channel",
            title="Video Title",
            content="transcript here",
            url="https://youtube.com/watch?v=abc",
            parser="youtube",
            media_type=MediaType.VIDEO,
            confidence=0.85,
            confidence_factors=["title", "transcript"],
            tags=["youtube", "video"],
            language="en",
            extra={"video_id": "abc"},
        )
        d = original.to_dict()
        restored = DataPulseItem.from_dict(d)

        assert restored.source_type == original.source_type
        assert restored.source_name == original.source_name
        assert restored.title == original.title
        assert restored.content == original.content
        assert restored.url == original.url
        assert restored.parser == original.parser
        assert restored.media_type == original.media_type
        assert restored.confidence == original.confidence
        assert restored.confidence_factors == original.confidence_factors
        assert restored.tags == original.tags
        assert restored.language == original.language
        assert restored.extra == original.extra
        assert restored.id == original.id

    def test_from_dict_string_enums(self):
        """from_dict should accept string enum values."""
        data = {
            "source_type": "twitter",
            "source_name": "test",
            "title": "t",
            "content": "c",
            "url": "https://x.com/test",
            "media_type": "text",
        }
        item = DataPulseItem.from_dict(data)
        assert item.source_type == SourceType.TWITTER
        assert item.media_type == MediaType.TEXT

    def test_from_dict_ignores_unknown_keys(self):
        data = {
            "source_type": "generic",
            "source_name": "test",
            "title": "t",
            "content": "c",
            "url": "https://example.com",
            "unknown_field": "should be ignored",
        }
        item = DataPulseItem.from_dict(data)
        assert item.title == "t"

    def test_source_type_values(self):
        expected = {"twitter", "reddit", "youtube", "bilibili", "telegram",
                    "wechat", "xhs", "rss", "generic", "manual"}
        actual = {st.value for st in SourceType}
        assert actual == expected

    def test_media_type_values(self):
        expected = {"text", "video", "audio", "image"}
        actual = {mt.value for mt in MediaType}
        assert actual == expected

    def test_default_field_values(self):
        item = DataPulseItem(
            source_type=SourceType.GENERIC,
            source_name="x",
            title="y",
            content="z",
            url="https://example.com",
        )
        assert item.score == 0
        assert item.confidence == 0.0
        assert item.confidence_factors == []
        assert item.tags == []
        assert item.language == "unknown"
        assert item.category == ""
        assert item.extra == {}
        assert item.processed is False
        assert item.digest_date is None
