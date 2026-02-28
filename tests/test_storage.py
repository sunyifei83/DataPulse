"""Tests for UnifiedInbox storage."""

from __future__ import annotations

import json
from datetime import datetime, timedelta
from pathlib import Path

import pytest

from datapulse.core.models import DataPulseItem, SourceType
from datapulse.core.storage import UnifiedInbox


class TestUnifiedInbox:
    def _make_item(self, url: str = "https://example.com", title: str = "T",
                   content: str = "C", fetched_at: str | None = None) -> DataPulseItem:
        item = DataPulseItem(
            source_type=SourceType.GENERIC,
            source_name="test",
            title=title,
            content=content,
            url=url,
        )
        if fetched_at:
            item.fetched_at = fetched_at
        return item

    def test_add_new_item(self, tmp_inbox: Path):
        inbox = UnifiedInbox(str(tmp_inbox))
        item = self._make_item()
        assert inbox.add(item) is True
        assert len(inbox.items) == 1

    def test_dedup_same_id(self, tmp_inbox: Path):
        inbox = UnifiedInbox(str(tmp_inbox))
        item1 = self._make_item(url="https://a.com", title="Same")
        item2 = self._make_item(url="https://a.com", title="Same")
        assert item1.id == item2.id
        assert inbox.add(item1) is True
        assert inbox.add(item2) is False
        assert len(inbox.items) == 1

    def test_save_and_reload(self, tmp_inbox: Path):
        inbox = UnifiedInbox(str(tmp_inbox))
        inbox.add(self._make_item(url="https://a.com", title="A"))
        inbox.add(self._make_item(url="https://b.com", title="B"))
        inbox.save()

        inbox2 = UnifiedInbox(str(tmp_inbox))
        assert len(inbox2.items) == 2

    def test_prune_by_age(self, tmp_inbox: Path, monkeypatch):
        monkeypatch.setenv("DATAPULSE_KEEP_DAYS", "7")
        inbox = UnifiedInbox(str(tmp_inbox))
        old_date = (datetime.utcnow() - timedelta(days=10)).isoformat()
        recent_date = datetime.utcnow().isoformat()
        inbox.add(self._make_item(url="https://old.com", title="Old", fetched_at=old_date))
        inbox.add(self._make_item(url="https://new.com", title="New", fetched_at=recent_date))
        inbox.save()

        inbox2 = UnifiedInbox(str(tmp_inbox))
        # Only the recent item should survive
        assert len(inbox2.items) == 1
        assert inbox2.items[0].title == "New"

    def test_max_items_limit(self, tmp_inbox: Path, monkeypatch):
        monkeypatch.setenv("DATAPULSE_MAX_INBOX", "3")
        inbox = UnifiedInbox(str(tmp_inbox))
        for i in range(5):
            inbox.add(self._make_item(url=f"https://example.com/{i}", title=f"Item {i}"))
        assert len(inbox.items) <= 3

    def test_query_filters_by_confidence(self, tmp_inbox_with_items: Path):
        inbox = UnifiedInbox(str(tmp_inbox_with_items))
        results = inbox.query(limit=10, min_confidence=0.80)
        assert all(item.confidence >= 0.80 for item in results)

    def test_query_respects_limit(self, tmp_inbox_with_items: Path):
        inbox = UnifiedInbox(str(tmp_inbox_with_items))
        results = inbox.query(limit=1, min_confidence=0.0)
        assert len(results) == 1

    def test_all_items_filters(self, tmp_inbox_with_items: Path):
        inbox = UnifiedInbox(str(tmp_inbox_with_items))
        all_items = inbox.all_items(min_confidence=0.0)
        high_items = inbox.all_items(min_confidence=0.80)
        assert len(high_items) <= len(all_items)

    def test_empty_inbox_load(self, tmp_inbox: Path):
        inbox = UnifiedInbox(str(tmp_inbox))
        assert inbox.items == []

    def test_corrupt_json_load(self, tmp_inbox: Path):
        tmp_inbox.write_text("not valid json{{{", encoding="utf-8")
        inbox = UnifiedInbox(str(tmp_inbox))
        assert inbox.items == []

    def test_sorted_by_fetched_at_desc(self, tmp_inbox: Path):
        inbox = UnifiedInbox(str(tmp_inbox))
        for i in range(3):
            ts = (datetime.utcnow() - timedelta(hours=i)).isoformat()
            inbox.add(self._make_item(url=f"https://e.com/{i}", title=f"I{i}", fetched_at=ts))
        # Most recent first
        assert inbox.items[0].title == "I0"


class TestProcessedState:
    def _make_item(self, url: str = "https://example.com", title: str = "T",
                   content: str = "C", confidence: float = 0.8) -> DataPulseItem:
        return DataPulseItem(
            source_type=SourceType.GENERIC,
            source_name="test",
            title=title,
            content=content,
            url=url,
            confidence=confidence,
        )

    def test_mark_processed_success(self, tmp_path):
        inbox = UnifiedInbox(str(tmp_path / "inbox.json"))
        item = self._make_item()
        inbox.add(item)
        assert inbox.mark_processed(item.id) is True
        assert item.processed is True

    def test_mark_processed_not_found(self, tmp_path):
        inbox = UnifiedInbox(str(tmp_path / "inbox.json"))
        assert inbox.mark_processed("nonexistent") is False

    def test_query_unprocessed_filters_processed(self, tmp_path):
        inbox = UnifiedInbox(str(tmp_path / "inbox.json"))
        item1 = self._make_item(url="https://a.com", title="A")
        item2 = self._make_item(url="https://b.com", title="B")
        inbox.add(item1)
        inbox.add(item2)
        inbox.mark_processed(item1.id)
        unprocessed = inbox.query_unprocessed()
        assert len(unprocessed) == 1
        assert unprocessed[0].id == item2.id

    def test_query_unprocessed_confidence_filter(self, tmp_path):
        inbox = UnifiedInbox(str(tmp_path / "inbox.json"))
        item_low = self._make_item(url="https://low.com", title="Low", confidence=0.3)
        item_high = self._make_item(url="https://high.com", title="High", confidence=0.9)
        inbox.add(item_low)
        inbox.add(item_high)
        results = inbox.query_unprocessed(min_confidence=0.5)
        assert len(results) == 1
        assert results[0].id == item_high.id

    def test_processed_persists(self, tmp_path):
        path = str(tmp_path / "inbox.json")
        inbox = UnifiedInbox(path)
        item = self._make_item()
        inbox.add(item)
        inbox.mark_processed(item.id)
        inbox.save()

        inbox2 = UnifiedInbox(path)
        assert inbox2.items[0].processed is True
        assert len(inbox2.query_unprocessed()) == 0
