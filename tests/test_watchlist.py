"""Tests for watch mission persistence and reader integration."""

from __future__ import annotations

import pytest

from datapulse.core.models import DataPulseItem, SourceType
from datapulse.core.watchlist import MissionRun, WatchlistStore
from datapulse.reader import DataPulseReader


class TestWatchlistStore:
    def test_create_save_reload(self, tmp_path):
        path = str(tmp_path / "watchlist.json")
        store = WatchlistStore(path)

        mission = store.create_mission(
            name="OpenAI Radar",
            query="OpenAI inference stack",
            platforms=["twitter", "reddit", "twitter"],
            sites=["openai.com", "reddit.com", "openai.com"],
            top_n=8,
        )

        reloaded = WatchlistStore(path)
        restored = reloaded.get(mission.id)

        assert restored is not None
        assert restored.name == "OpenAI Radar"
        assert restored.query == "OpenAI inference stack"
        assert restored.platforms == ["twitter", "reddit"]
        assert restored.sites == ["openai.com", "reddit.com"]
        assert restored.top_n == 8

    def test_duplicate_names_get_incremented_ids(self, tmp_path):
        store = WatchlistStore(str(tmp_path / "watchlist.json"))

        first = store.create_mission(name="AI Brief", query="LLM agents")
        second = store.create_mission(name="AI Brief", query="LLM infra")

        assert first.id == "ai-brief"
        assert second.id == "ai-brief-2"

    def test_disable_and_record_run_persist(self, tmp_path):
        path = str(tmp_path / "watchlist.json")
        store = WatchlistStore(path)
        mission = store.create_mission(name="AI Brief", query="LLM agents")

        store.record_run(mission.id, MissionRun(mission_id=mission.id, item_count=3))
        store.disable(mission.id)

        reloaded = WatchlistStore(path)
        restored = reloaded.get("AI Brief")

        assert restored is not None
        assert restored.enabled is False
        assert restored.last_run_count == 3
        assert restored.last_run_status == "success"
        assert len(restored.runs) == 1


@pytest.mark.asyncio
async def test_reader_run_watch_records_metadata(tmp_path, monkeypatch):
    watch_path = tmp_path / "watchlist.json"
    monkeypatch.setenv("DATAPULSE_WATCHLIST_PATH", str(watch_path))

    reader = DataPulseReader(inbox_path=str(tmp_path / "inbox.json"))
    mission = reader.create_watch(
        name="AI Radar",
        query="OpenAI agents",
        platforms=["twitter"],
        top_n=3,
    )

    async def fake_search(query, **kwargs):
        item = DataPulseItem(
            source_type=SourceType.GENERIC,
            source_name="search",
            title=f"{query} result",
            content="Synthetic search result content",
            url="https://example.com/openai-agents",
            confidence=0.81,
            score=72,
        )
        reader.inbox.add(item, fingerprint_dedup=False)
        reader.inbox.save()
        return [item]

    monkeypatch.setattr(reader, "search", fake_search)

    payload = await reader.run_watch(mission["id"])

    assert payload["run"]["status"] == "success"
    assert payload["run"]["item_count"] == 1
    assert payload["mission"]["last_run_count"] == 1
    assert payload["mission"]["last_run_status"] == "success"
    assert payload["items"][0]["extra"]["watch_mission_id"] == mission["id"]
    assert reader.inbox.items[0].extra["watch_mission_name"] == "AI Radar"
    assert "watch" in reader.inbox.items[0].tags


@pytest.mark.asyncio
async def test_reader_run_watch_rejects_disabled(tmp_path, monkeypatch):
    watch_path = tmp_path / "watchlist.json"
    monkeypatch.setenv("DATAPULSE_WATCHLIST_PATH", str(watch_path))

    reader = DataPulseReader(inbox_path=str(tmp_path / "inbox.json"))
    mission = reader.create_watch(name="Dormant Watch", query="quiet query")
    reader.disable_watch(mission["id"])

    with pytest.raises(ValueError, match="disabled"):
        await reader.run_watch(mission["id"])


@pytest.mark.asyncio
async def test_reader_run_due_watches_executes_due_only(tmp_path, monkeypatch):
    watch_path = tmp_path / "watchlist.json"
    monkeypatch.setenv("DATAPULSE_WATCHLIST_PATH", str(watch_path))

    reader = DataPulseReader(inbox_path=str(tmp_path / "inbox.json"))
    reader.create_watch(name="Hourly Watch", query="OpenAI agents", schedule="@hourly")
    fresh = reader.create_watch(name="Daily Watch", query="OpenAI infra", schedule="@daily")
    reader.watchlist.missions[fresh["id"]].last_run_at = "2099-01-01T00:00:00+00:00"
    reader.watchlist.save()

    seen: list[str] = []

    async def fake_run_watch(identifier, *, trigger="manual"):
        seen.append(f"{identifier}:{trigger}")
        return {
            "mission": {"id": identifier, "name": identifier, "query": "q"},
            "run": {"status": "success", "item_count": 2},
            "items": [],
        }

    monkeypatch.setattr(reader, "run_watch", fake_run_watch)

    payload = await reader.run_due_watches()

    assert payload["due_count"] == 1
    assert payload["run_count"] == 1
    assert payload["results"][0]["status"] == "success"
    assert seen == ["hourly-watch:scheduled"]


@pytest.mark.asyncio
async def test_reader_run_due_watches_retries_once(tmp_path, monkeypatch):
    watch_path = tmp_path / "watchlist.json"
    monkeypatch.setenv("DATAPULSE_WATCHLIST_PATH", str(watch_path))

    reader = DataPulseReader(inbox_path=str(tmp_path / "inbox.json"))
    reader.create_watch(name="Retry Watch", query="OpenAI agents", schedule="@hourly")

    attempts = {"count": 0}

    async def flaky_run_watch(identifier, *, trigger="manual"):
        attempts["count"] += 1
        if attempts["count"] == 1:
            raise RuntimeError("temporary failure")
        return {
            "mission": {"id": identifier, "name": identifier, "query": "q"},
            "run": {"status": "success", "item_count": 3},
            "items": [],
            "alert_events": [{"id": "alert-1"}],
        }

    monkeypatch.setattr(reader, "run_watch", flaky_run_watch)

    payload = await reader.run_due_watches(
        retry_attempts=2,
        retry_base_delay=0.001,
        retry_max_delay=0.01,
    )

    assert attempts["count"] == 2
    assert payload["results"][0]["status"] == "success"
    assert payload["results"][0]["attempts"] == 2
    assert payload["results"][0]["alert_count"] == 1
