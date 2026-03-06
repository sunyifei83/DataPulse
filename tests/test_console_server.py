"""Tests for the G0 browser console API."""

from __future__ import annotations

from fastapi.testclient import TestClient

from datapulse.console_server import CONSOLE_TITLE, create_app


class _ConsoleReader:
    def list_watches(self, include_disabled=False):
        rows = [
            {
                "id": "launch-ops",
                "name": "Launch Ops",
                "query": "OpenAI launch",
                "enabled": True,
                "platforms": ["twitter"],
                "sites": ["openai.com"],
                "schedule_label": "hourly",
                "is_due": True,
                "alert_rule_count": 1,
                "last_run_at": "2026-03-06T00:00:00+00:00",
                "last_run_status": "success",
            }
        ]
        if include_disabled:
            rows.append(
                {
                    "id": "old-watch",
                    "name": "Old Watch",
                    "query": "legacy",
                    "enabled": False,
                    "platforms": [],
                    "sites": [],
                    "schedule_label": "manual",
                    "is_due": False,
                    "alert_rule_count": 0,
                    "last_run_at": "",
                    "last_run_status": "",
                }
            )
        return rows

    def create_watch(self, **kwargs):
        return {
            "id": "launch-ops",
            "name": kwargs["name"],
            "query": kwargs["query"],
            "platforms": kwargs.get("platforms") or [],
            "sites": kwargs.get("sites") or [],
            "schedule": kwargs.get("schedule", "manual"),
            "alert_rules": kwargs.get("alert_rules") or [],
        }

    async def run_watch(self, identifier):
        return {
            "mission": {"id": identifier, "name": "Launch Ops"},
            "run": {"status": "success", "item_count": 2},
            "items": [],
            "alert_events": [],
        }

    async def run_due_watches(self, limit=None):
        return {
            "due_count": 1,
            "run_count": 1,
            "results": [{"mission_id": "launch-ops", "status": "success"}],
        }

    def disable_watch(self, identifier):
        return {"id": identifier, "enabled": False}

    def list_alerts(self, limit=20, mission_id=None):
        return [
            {
                "id": "alert-1",
                "mission_name": "Launch Ops",
                "rule_name": "console-threshold",
                "summary": "Launch Ops triggered console-threshold",
                "delivered_channels": ["json", "webhook:ops-webhook"],
            }
        ]

    def list_alert_routes(self):
        return [{"name": "ops-webhook", "channel": "webhook"}]

    def watch_status_snapshot(self):
        return {
            "state": "running",
            "heartbeat_at": "2026-03-06T00:00:00+00:00",
            "metrics": {"cycles_total": 3, "runs_total": 2, "alerts_total": 1, "error_total": 0},
            "last_error": "",
        }

    def triage_list(self, **kwargs):
        return [
            {
                "id": "item-1",
                "title": "OpenAI launch post",
                "review_state": "new",
                "score": 81,
                "confidence": 0.91,
                "url": "https://example.com/openai-launch",
                "review_notes": [],
            }
        ]

    def triage_stats(self):
        return {
            "total": 2,
            "open_count": 1,
            "closed_count": 1,
            "note_count": 0,
            "states": {"new": 1, "triaged": 0, "verified": 1, "duplicate": 0, "ignored": 0, "escalated": 0},
        }

    def triage_update(self, item_id, **kwargs):
        return {"id": item_id, "review_state": kwargs["state"]}

    def triage_note(self, item_id, **kwargs):
        return {"id": item_id, "review_notes": [{"note": kwargs["note"]}]}


def _client() -> TestClient:
    app = create_app(reader_factory=lambda: _ConsoleReader())
    return TestClient(app)


def test_console_index_serves_shell():
    client = _client()
    response = client.get("/")

    assert response.status_code == 200
    assert CONSOLE_TITLE in response.text
    assert "Mission Control For Signal Work" in response.text
    assert "create-watch-form" in response.text
    assert "Triage Queue" in response.text


def test_console_overview_returns_aggregates():
    client = _client()
    response = client.get("/api/overview")

    assert response.status_code == 200
    payload = response.json()
    assert payload["enabled_watches"] == 1
    assert payload["disabled_watches"] == 1
    assert payload["due_watches"] == 1
    assert payload["route_count"] == 1
    assert payload["triage_open_count"] == 1
    assert payload["daemon_state"] == "running"


def test_console_create_watch_route():
    client = _client()
    response = client.post(
        "/api/watches",
        json={
            "name": "Launch Ops",
            "query": "OpenAI launch",
            "platforms": ["twitter"],
            "schedule": "@hourly",
            "alert_rules": [{"name": "console-threshold", "routes": ["ops-webhook"]}],
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["name"] == "Launch Ops"
    assert payload["alert_rules"][0]["routes"] == ["ops-webhook"]


def test_console_run_due_route():
    client = _client()
    response = client.post("/api/watches/run-due", json={"limit": 0})

    assert response.status_code == 200
    payload = response.json()
    assert payload["due_count"] == 1
    assert payload["run_count"] == 1


def test_console_routes_and_status():
    client = _client()

    routes = client.get("/api/alert-routes")
    status = client.get("/api/watch-status")

    assert routes.status_code == 200
    assert routes.json()[0]["name"] == "ops-webhook"
    assert status.status_code == 200
    assert status.json()["metrics"]["cycles_total"] == 3


def test_console_triage_routes():
    client = _client()

    triage = client.get("/api/triage?limit=5")
    stats = client.get("/api/triage/stats")
    update = client.post("/api/triage/item-1/state", json={"state": "verified"})

    assert triage.status_code == 200
    assert triage.json()[0]["id"] == "item-1"
    assert stats.status_code == 200
    assert stats.json()["open_count"] == 1
    assert update.status_code == 200
    assert update.json()["review_state"] == "verified"
