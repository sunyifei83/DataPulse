"""Tests for the G0 browser console API."""

from __future__ import annotations

import json

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

    def triage_explain(self, item_id, **kwargs):
        return {
            "item": {"id": item_id, "title": "OpenAI launch post"},
            "candidate_count": 1,
            "returned_count": 1,
            "suggested_primary_id": item_id,
            "candidates": [
                {
                    "id": "item-2",
                    "title": "OpenAI launch recap",
                    "review_state": "triaged",
                    "similarity": 0.81,
                    "signals": ["same_domain", "title_overlap"],
                    "same_domain": True,
                    "suggested_primary_id": item_id,
                }
            ],
        }

    def list_stories(self, limit=20, min_items=1):
        return [
            {
                "id": "story-openai-launch",
                "title": "OpenAI Launch",
                "summary": "3 signals across 2 sources around 'OpenAI Launch'; key entities: OpenAI, GPT-5; contradictions: 1",
                "status": "active",
                "score": 87.4,
                "confidence": 0.91,
                "item_count": 3,
                "source_count": 2,
                "primary_item_id": "item-1",
                "entities": ["OpenAI", "GPT-5", "Sam Altman"],
                "source_names": ["OpenAI Blog", "The Verge"],
                "primary_evidence": [
                    {
                        "item_id": "item-1",
                        "title": "OpenAI launch post",
                        "url": "https://example.com/openai-launch",
                        "source_name": "OpenAI Blog",
                        "source_type": "generic",
                        "score": 91,
                        "confidence": 0.96,
                        "review_state": "verified",
                        "role": "primary",
                    }
                ],
                "secondary_evidence": [
                    {
                        "item_id": "item-2",
                        "title": "OpenAI launch recap",
                        "url": "https://example.com/openai-launch-recap",
                        "source_name": "The Verge",
                        "source_type": "generic",
                        "score": 83,
                        "confidence": 0.88,
                        "review_state": "triaged",
                        "role": "secondary",
                    }
                ],
                "timeline": [
                    {
                        "time": "2026-03-06T08:00:00+00:00",
                        "item_id": "item-1",
                        "title": "OpenAI launch post",
                        "source_name": "OpenAI Blog",
                        "url": "https://example.com/openai-launch",
                        "role": "primary",
                        "score": 91,
                    }
                ],
                "contradictions": [
                    {
                        "topic": "launch timing",
                        "positive": 1,
                        "negative": 1,
                        "neutral": 0,
                        "note": "Conflicting source timing windows.",
                    }
                ],
                "generated_at": "2026-03-06T00:00:00+00:00",
                "updated_at": "2026-03-06T00:05:00+00:00",
            }
        ]

    def show_story(self, identifier):
        if identifier != "story-openai-launch":
            return None
        return self.list_stories()[0]

    def story_graph(self, identifier, **kwargs):
        if identifier != "story-openai-launch":
            return None
        return {
            "story": {
                "id": "story-openai-launch",
                "title": "OpenAI Launch",
                "status": "active",
            },
            "nodes": [
                {"id": "story-openai-launch", "label": "OpenAI Launch", "kind": "story", "item_count": 3, "source_count": 2},
                {"id": "entity:openai", "label": "OpenAI", "kind": "entity", "entity_type": "ORG", "in_story_source_count": 2},
                {"id": "entity:gpt_5", "label": "GPT-5", "kind": "entity", "entity_type": "PRODUCT", "in_story_source_count": 1},
            ],
            "edges": [
                {"source": "story-openai-launch", "target": "entity:openai", "relation_type": "MENTIONED_IN_STORY", "kind": "story_entity"},
                {"source": "entity:openai", "target": "entity:gpt_5", "relation_type": "BUILT", "kind": "entity_relation"},
            ],
            "entity_count": 2,
            "relation_count": 1,
            "edge_count": 2,
        }

    def export_story(self, identifier, **kwargs):
        if identifier != "story-openai-launch":
            return None
        output_format = kwargs.get("output_format", "json")
        if output_format in {"markdown", "md"}:
            return "# OpenAI Launch\n\n- story_id: story-openai-launch"
        return json.dumps(self.list_stories()[0], ensure_ascii=False, indent=2)


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
    assert "Story Workspace" in response.text


def test_console_overview_returns_aggregates():
    client = _client()
    response = client.get("/api/overview")

    assert response.status_code == 200
    payload = response.json()
    assert payload["enabled_watches"] == 1
    assert payload["disabled_watches"] == 1
    assert payload["due_watches"] == 1
    assert payload["story_count"] == 1
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
    explain = client.get("/api/triage/item-1/explain?limit=3")
    update = client.post("/api/triage/item-1/state", json={"state": "verified"})

    assert triage.status_code == 200
    assert triage.json()[0]["id"] == "item-1"
    assert stats.status_code == 200
    assert stats.json()["open_count"] == 1
    assert explain.status_code == 200
    assert explain.json()["candidates"][0]["id"] == "item-2"
    assert update.status_code == 200
    assert update.json()["review_state"] == "verified"


def test_console_story_routes():
    client = _client()

    stories = client.get("/api/stories?limit=4&min_items=2")
    detail = client.get("/api/stories/story-openai-launch")
    graph = client.get("/api/stories/story-openai-launch/graph?entity_limit=6")
    export = client.get("/api/stories/story-openai-launch/export?format=markdown")

    assert stories.status_code == 200
    assert stories.json()[0]["id"] == "story-openai-launch"
    assert detail.status_code == 200
    assert detail.json()["primary_item_id"] == "item-1"
    assert graph.status_code == 200
    assert graph.json()["relation_count"] == 1
    assert graph.json()["nodes"][1]["label"] == "OpenAI"
    assert export.status_code == 200
    assert export.headers["content-type"].startswith("text/markdown")
    assert export.text.startswith("# OpenAI Launch")
