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
async def test_reader_show_watch_returns_cockpit_detail(tmp_path, monkeypatch):
    monkeypatch.setenv("DATAPULSE_WATCHLIST_PATH", str(tmp_path / "watchlist.json"))
    monkeypatch.setenv("DATAPULSE_ALERTS_PATH", str(tmp_path / "alerts.json"))

    reader = DataPulseReader(inbox_path=str(tmp_path / "inbox.json"))
    mission = reader.create_watch(
        name="Launch Ops",
        query="OpenAI launch",
        alert_rules=[
            {
                "name": "threshold",
                "min_score": 70,
                "min_confidence": 0.8,
            }
        ],
    )

    async def fake_search(query, **kwargs):
        item = DataPulseItem(
            source_type=SourceType.GENERIC,
            source_name="search",
            title=f"{query} result",
            content="Synthetic search result content",
            url="https://example.com/openai-launch",
            confidence=0.92,
            score=78,
        )
        reader.inbox.add(item, fingerprint_dedup=False)
        reader.inbox.save()
        return [item]

    monkeypatch.setattr(reader, "search", fake_search)

    await reader.run_watch(mission["id"])
    payload = reader.show_watch(mission["id"])

    assert payload is not None
    assert payload["id"] == mission["id"]
    assert payload["run_stats"]["total"] == 1
    assert payload["run_stats"]["success"] == 1
    assert payload["recent_results"][0]["title"] == "OpenAI launch result"
    assert payload["recent_results"][0]["extra"]["watch_mission_id"] == mission["id"]
    assert payload["result_stats"]["stored_result_count"] == 1
    assert payload["result_stats"]["returned_result_count"] == 1
    assert payload["recent_alerts"][0]["rule_name"] == "threshold"
    assert payload["delivery_stats"]["recent_alert_count"] == 1


@pytest.mark.asyncio
async def test_reader_list_watch_results_filters_by_mission(tmp_path, monkeypatch):
    monkeypatch.setenv("DATAPULSE_WATCHLIST_PATH", str(tmp_path / "watchlist.json"))

    reader = DataPulseReader(inbox_path=str(tmp_path / "inbox.json"))
    mission = reader.create_watch(name="AI Radar", query="OpenAI agents")

    matched = DataPulseItem(
        source_type=SourceType.GENERIC,
        source_name="search",
        title="OpenAI agents result",
        content="Synthetic search result content",
        url="https://example.com/openai-agents",
        fetched_at="2026-03-06T00:00:00+00:00",
        confidence=0.91,
        score=73,
        extra={"watch_mission_id": mission["id"], "watch_mission_name": mission["name"]},
    )
    unrelated = DataPulseItem(
        source_type=SourceType.GENERIC,
        source_name="search",
        title="Infra result",
        content="Synthetic unrelated result",
        url="https://example.com/infra",
        fetched_at="2026-03-06T00:01:00+00:00",
        confidence=0.95,
        score=88,
    )

    reader.inbox.add(matched, fingerprint_dedup=False)
    reader.inbox.add(unrelated, fingerprint_dedup=False)
    reader.inbox.save()

    payload = reader.list_watch_results(mission["id"], limit=5)

    assert payload is not None
    assert len(payload) == 1
    assert payload[0]["title"] == "OpenAI agents result"
    assert payload[0]["extra"]["watch_mission_id"] == mission["id"]


@pytest.mark.asyncio
async def test_reader_show_watch_includes_retry_advice_for_last_failure(tmp_path, monkeypatch):
    monkeypatch.setenv("DATAPULSE_WATCHLIST_PATH", str(tmp_path / "watchlist.json"))

    reader = DataPulseReader(inbox_path=str(tmp_path / "inbox.json"))
    mission = reader.create_watch(
        name="AI Radar",
        query="OpenAI agents",
        platforms=["twitter"],
        schedule="@hourly",
    )

    async def failing_search(query, **kwargs):
        raise RuntimeError("temporary upstream failure")

    monkeypatch.setattr(reader, "search", failing_search)
    monkeypatch.setattr(
        reader,
        "doctor",
        lambda: {
            "tier_0": [],
            "tier_1": [
                {
                    "name": "twitter",
                    "status": "warn",
                    "message": "credentials missing",
                    "available": True,
                    "setup_hint": "set API key",
                }
            ],
            "tier_2": [],
        },
    )

    with pytest.raises(RuntimeError, match="temporary upstream failure"):
        await reader.run_watch(mission["id"])

    payload = reader.show_watch(mission["id"])

    assert payload is not None
    assert payload["last_failure"]["status"] == "error"
    assert payload["last_failure"]["error"] == "temporary upstream failure"
    assert payload["retry_advice"]["failure_class"] == "transient"
    assert payload["retry_advice"]["retry_command"] == "datapulse --watch-run ai-radar"
    assert payload["retry_advice"]["daemon_retry_command"] == "datapulse --watch-daemon --watch-daemon-once"
    assert payload["retry_advice"]["suspected_collectors"][0]["name"] == "twitter"
    assert payload["retry_advice"]["suspected_collectors"][0]["setup_hint"] == "set API key"


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
