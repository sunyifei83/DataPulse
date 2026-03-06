"""Tests for lightweight watch mission scheduling."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from datapulse.core.scheduler import (
    WatchDaemon,
    WatchDaemonLock,
    WatchScheduler,
    describe_schedule,
    is_watch_due,
    schedule_to_seconds,
)
from datapulse.core.watchlist import WatchlistStore, WatchMission


def test_schedule_to_seconds_aliases():
    assert schedule_to_seconds("@hourly") == 3600
    assert schedule_to_seconds("@daily") == 86400
    assert schedule_to_seconds("interval:15m") == 900
    assert schedule_to_seconds("every:2h") == 7200
    assert schedule_to_seconds("manual") is None


def test_describe_schedule_normalizes_labels():
    assert describe_schedule("@hourly") == "hourly"
    assert describe_schedule("interval:15m") == "every 15m"
    assert describe_schedule("manual") == "manual"


def test_is_watch_due_without_last_run():
    mission = WatchMission(name="AI Radar", query="agents", schedule="@hourly")
    assert is_watch_due(mission) is True


def test_is_watch_due_with_recent_run_false():
    recent = (datetime.now(timezone.utc) - timedelta(minutes=10)).isoformat()
    mission = WatchMission(name="AI Radar", query="agents", schedule="@hourly", last_run_at=recent)
    assert is_watch_due(mission) is False


def test_scheduler_selects_only_due_missions(tmp_path):
    store = WatchlistStore(str(tmp_path / "watchlist.json"))
    due = store.create_mission(name="Due Watch", query="agents", schedule="@hourly")
    not_due = store.create_mission(name="Fresh Watch", query="infra", schedule="@daily")
    not_due.last_run_at = (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()
    store.save()

    scheduler = WatchScheduler(store)
    due_ids = [mission.id for mission in scheduler.due_missions()]

    assert due.id in due_ids
    assert not_due.id not in due_ids


def test_watch_daemon_lock_blocks_second_holder(tmp_path):
    path = str(tmp_path / "watch.lock")
    first = WatchDaemonLock(path)
    second = WatchDaemonLock(path)

    first.acquire()
    try:
        with pytest.raises(RuntimeError, match="already held"):
            second.acquire()
    finally:
        first.release()


@pytest.mark.asyncio
async def test_watch_daemon_runs_one_cycle_and_releases_lock(tmp_path):
    class _Reader:
        def __init__(self):
            self.calls = 0

        async def run_due_watches(self, **kwargs):
            self.calls += 1
            return {"due_count": 1, "run_count": 1, "results": []}

    lock_path = str(tmp_path / "daemon.lock")
    reader = _Reader()
    daemon = WatchDaemon(reader, lock_path=lock_path)

    payload = await daemon.run_forever(max_cycles=1)

    assert payload["ok"] is True
    assert payload["cycles"] == 1
    assert reader.calls == 1
    assert not (tmp_path / "daemon.lock").exists()
