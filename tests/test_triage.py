"""Tests for triage queue state and persistence."""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from datapulse.core.models import DataPulseItem, SourceType
from datapulse.reader import DataPulseReader


def _make_item(
    item_id: str,
    *,
    title: str,
    confidence: float = 0.8,
    processed: bool = False,
    review_state: str = "new",
) -> DataPulseItem:
    return DataPulseItem(
        source_type=SourceType.GENERIC,
        source_name="source",
        title=title,
        content=f"{title} content for triage testing and persistence checks",
        url=f"https://example.com/{item_id}",
        id=item_id,
        confidence=confidence,
        processed=processed,
        review_state=review_state,
    )


def _reader(tmp_path: Path, items: list[DataPulseItem]) -> DataPulseReader:
    inbox_path = tmp_path / "inbox.json"
    catalog_path = tmp_path / "catalog.json"
    inbox_path.write_text(json.dumps([item.to_dict() for item in items], ensure_ascii=False), encoding="utf-8")
    catalog_path.write_text(json.dumps({"version": 2, "sources": [], "subscriptions": {}, "packs": []}), encoding="utf-8")
    os.environ["DATAPULSE_SOURCE_CATALOG"] = str(catalog_path)
    return DataPulseReader(inbox_path=str(inbox_path))


@pytest.fixture(autouse=True)
def _cleanup_env():
    yield
    os.environ.pop("DATAPULSE_SOURCE_CATALOG", None)


def test_processed_item_migrates_to_triaged_state(tmp_path):
    reader = _reader(tmp_path, [_make_item("item-1", title="Legacy", processed=True)])

    items = reader.list_memory(limit=10)

    assert items[0].review_state == "triaged"


def test_triage_update_persists_note_and_duplicate_of(tmp_path):
    reader = _reader(
        tmp_path,
        [
            _make_item("item-1", title="Candidate"),
            _make_item("item-2", title="Canonical"),
        ],
    )

    payload = reader.triage_update(
        "item-1",
        state="duplicate",
        note="same story as canonical",
        actor="test",
        duplicate_of="item-2",
    )
    reloaded = DataPulseReader(inbox_path=str(tmp_path / "inbox.json"))

    assert payload is not None
    assert payload["review_state"] == "duplicate"
    assert payload["duplicate_of"] == "item-2"
    stored = next(item for item in reloaded.inbox.items if item.id == "item-1")
    assert stored.review_state == "duplicate"
    assert stored.review_notes[0]["note"] == "same story as canonical"
    assert stored.review_actions[0]["to_state"] == "duplicate"


def test_triage_list_defaults_to_open_states(tmp_path):
    reader = _reader(
        tmp_path,
        [
            _make_item("item-1", title="Open"),
            _make_item("item-2", title="Closed", review_state="verified", processed=True),
        ],
    )

    payload = reader.triage_list(limit=10)

    assert [item["id"] for item in payload] == ["item-1"]


def test_triage_stats_counts_states(tmp_path):
    reader = _reader(
        tmp_path,
        [
            _make_item("item-1", title="Open"),
            _make_item("item-2", title="Verified", review_state="verified", processed=True),
            _make_item("item-3", title="Escalated", review_state="escalated"),
        ],
    )

    payload = reader.triage_stats()

    assert payload["total"] == 3
    assert payload["open_count"] == 2
    assert payload["states"]["verified"] == 1


def test_triage_explain_duplicate_ranks_candidate(tmp_path):
    reader = _reader(
        tmp_path,
        [
            _make_item("item-1", title="OpenAI Launch Event", confidence=0.95),
            _make_item("item-2", title="OpenAI Launch Event Recap", confidence=0.71),
            _make_item("item-3", title="Unrelated Market Update", confidence=0.88),
        ],
    )

    payload = reader.triage_explain("item-1", limit=3)

    assert payload is not None
    assert payload["item"]["id"] == "item-1"
    assert payload["candidate_count"] >= 1
    assert payload["candidates"][0]["id"] == "item-2"
    assert "same_domain" in payload["candidates"][0]["signals"]
