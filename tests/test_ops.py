"""Tests for watch daemon ops status storage."""

from __future__ import annotations

import json

from datapulse.core.ops import WatchStatusStore


def test_watch_status_store_persists_json_and_html(tmp_path):
    status_path = tmp_path / "watch-status.json"
    html_path = tmp_path / "watch-status.html"
    store = WatchStatusStore(path=str(status_path), html_path=str(html_path))

    store.mark_started()
    store.mark_cycle_started()
    store.record_cycle(
        {
            "due_count": 1,
            "run_count": 1,
            "results": [
                {
                    "mission_name": "AI Radar",
                    "status": "success",
                    "alert_count": 2,
                }
            ],
        }
    )
    store.mark_stopped()

    payload = json.loads(status_path.read_text(encoding="utf-8"))
    assert payload["state"] == "idle"
    assert payload["metrics"]["cycles_total"] == 1
    assert payload["metrics"]["runs_total"] == 1
    assert payload["metrics"]["success_total"] == 1
    assert payload["metrics"]["alerts_total"] == 2
    assert payload["last_result"]["results"][0]["mission_name"] == "AI Radar"

    html = html_path.read_text(encoding="utf-8")
    assert "DataPulse Watch Daemon" in html
    assert "AI Radar" in html


def test_watch_status_store_records_error(tmp_path):
    status_path = tmp_path / "watch-status.json"
    html_path = tmp_path / "watch-status.html"
    store = WatchStatusStore(path=str(status_path), html_path=str(html_path))

    store.record_error("network timeout")

    payload = store.snapshot()
    assert payload["state"] == "error"
    assert payload["last_error"] == "network timeout"
    assert payload["metrics"]["error_total"] == 1
