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
            "next_run_at": "2026-03-06T01:00:00+00:00",
            "alert_rule_count": 1,
            "alert_rules": [{"name": "console-threshold", "routes": ["ops-webhook"]}],
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
                    "next_run_at": "",
                    "alert_rule_count": 0,
                    "last_run_at": "",
                    "last_run_status": "",
                }
            )
        return rows

    def show_watch(self, identifier):
        if identifier != "launch-ops":
            return None
        return {
            "id": "launch-ops",
            "name": "Launch Ops",
            "query": "OpenAI launch",
            "enabled": True,
            "platforms": ["twitter"],
            "sites": ["openai.com"],
            "schedule": "@hourly",
            "schedule_label": "hourly",
            "is_due": True,
            "next_run_at": "2026-03-06T01:00:00+00:00",
            "alert_rule_count": 2,
            "alert_rules": [
                {
                    "name": "console-threshold",
                    "routes": ["ops-webhook"],
                    "keyword_any": ["launch"],
                    "domains": ["openai.com"],
                    "min_score": 70,
                    "min_confidence": 0.8,
                },
                {
                    "name": "console-threshold",
                    "routes": ["exec-telegram"],
                    "keyword_any": ["ship"],
                    "domains": ["example.com"],
                    "min_score": 55,
                    "min_confidence": 0.6,
                },
            ],
            "last_run_at": "2026-03-06T00:00:00+00:00",
            "last_run_status": "success",
            "last_run_error": "",
            "runs": [
                {
                    "id": "launch-ops:2026-03-06T00:00:00+00:00",
                    "mission_id": "launch-ops",
                    "status": "success",
                    "item_count": 2,
                    "trigger": "scheduled",
                    "started_at": "2026-03-06T00:00:00+00:00",
                    "finished_at": "2026-03-06T00:00:05+00:00",
                    "error": "",
                }
            ],
            "run_stats": {
                "total": 1,
                "success": 1,
                "error": 0,
                "average_items": 2.0,
                "last_status": "success",
                "last_error": "",
            },
            "last_failure": {
                "id": "launch-ops:2026-03-05T23:00:00+00:00",
                "mission_id": "launch-ops",
                "status": "error",
                "item_count": 0,
                "trigger": "scheduled",
                "started_at": "2026-03-05T23:00:00+00:00",
                "finished_at": "2026-03-05T23:00:03+00:00",
                "error": "credentials missing",
            },
            "retry_advice": {
                "failure_class": "credentials",
                "summary": "The last failed run looks blocked by missing credentials or an expired session.",
                "retry_command": "datapulse --watch-run launch-ops",
                "daemon_retry_command": "datapulse --watch-daemon --watch-daemon-once",
                "suspected_collectors": [
                    {
                        "name": "twitter",
                        "tier": "tier_1",
                        "status": "warn",
                        "available": True,
                        "message": "credentials missing",
                        "setup_hint": "set API key",
                    }
                ],
                "notes": [
                    "Validate upstream API keys or platform login state before rerunning.",
                    "Fix the degraded collector setup below before rerunning the mission.",
                ],
            },
            "recent_results": [
                {
                    "id": "item-1",
                    "title": "OpenAI launch post",
                    "url": "https://example.com/openai-launch",
                    "score": 91,
                    "confidence": 0.96,
                    "review_state": "verified",
                    "source_name": "OpenAI Blog",
                    "source_type": "generic",
                    "watch_filters": {
                        "state": "verified",
                        "source": "openai blog",
                        "domain": "example.com",
                    },
                }
            ],
            "result_stats": {
                "stored_result_count": 1,
                "returned_result_count": 1,
                "latest_result_at": "2026-03-06T00:00:00+00:00",
            },
            "result_filters": {
                "window_count": 1,
                "states": [{"key": "verified", "label": "verified", "count": 1}],
                "sources": [{"key": "openai blog", "label": "OpenAI Blog", "count": 1}],
                "domains": [{"key": "example.com", "label": "example.com", "count": 1}],
            },
            "recent_alerts": [
                {
                    "id": "alert-1",
                    "mission_id": "launch-ops",
                    "mission_name": "Launch Ops",
                    "rule_name": "console-threshold",
                    "summary": "Launch Ops triggered console-threshold",
                    "created_at": "2026-03-06T00:00:10+00:00",
                    "item_ids": ["item-1", "item-2"],
                    "delivered_channels": ["json", "webhook:ops-webhook"],
                    "extra": {},
                }
            ],
            "delivery_stats": {
                "recent_alert_count": 1,
                "recent_error_count": 0,
                "last_alert_at": "2026-03-06T00:00:10+00:00",
            },
            "timeline_strip": [
                {
                    "kind": "alert",
                    "time": "2026-03-06T00:00:10+00:00",
                    "tone": "ok",
                    "label": "alert: console-threshold",
                    "detail": "json,webhook:ops-webhook | Launch Ops triggered console-threshold",
                },
                {
                    "kind": "result",
                    "time": "2026-03-06T00:00:00+00:00",
                    "tone": "ok",
                    "label": "result: OpenAI launch post",
                    "detail": "OpenAI Blog | score=91 | state=verified",
                },
            ],
        }

    def list_watch_results(self, identifier, limit=10, min_confidence=0.0):
        if identifier != "launch-ops":
            return None
        return self.show_watch(identifier)["recent_results"][:limit]

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

    def set_watch_alert_rules(self, identifier, *, alert_rules=None):
        if identifier != "launch-ops":
            return None
        payload = self.show_watch(identifier)
        payload["alert_rules"] = list(alert_rules or [])
        payload["alert_rule_count"] = len(payload["alert_rules"])
        return payload

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

    def enable_watch(self, identifier):
        return {"id": identifier, "enabled": True}

    def delete_watch(self, identifier):
        return {"id": identifier, "deleted": True}

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

    def alert_route_health(self, limit=100):
        return [
            {
                "name": "ops-webhook",
                "channel": "webhook",
                "configured": True,
                "status": "healthy",
                "event_count": 1,
                "delivered_count": 1,
                "failure_count": 0,
                "success_rate": 1.0,
                "last_event_at": "2026-03-06T00:00:10+00:00",
                "last_delivered_at": "2026-03-06T00:00:10+00:00",
                "last_failed_at": "",
                "last_error": "",
                "last_summary": "Launch Ops triggered console-threshold",
                "mission_ids": ["launch-ops"],
                "rule_names": ["console-threshold"],
            }
        ]

    def watch_status_snapshot(self):
        return {
            "state": "running",
            "heartbeat_at": "2026-03-06T00:00:00+00:00",
            "metrics": {"cycles_total": 3, "runs_total": 2, "alerts_total": 1, "error_total": 0},
            "last_error": "",
        }

    def ops_snapshot(self):
        return {
            "collector_summary": {
                "total": 4,
                "ok": 3,
                "warn": 1,
                "error": 0,
                "available": 4,
                "unavailable": 0,
            },
            "collector_tiers": {
                "tier_0": {"total": 2, "ok": 2, "warn": 0, "error": 0, "available": 2, "unavailable": 0},
                "tier_1": {"total": 1, "ok": 0, "warn": 1, "error": 0, "available": 1, "unavailable": 0},
            },
            "degraded_collectors": [
                {
                    "tier": "tier_1",
                    "name": "twitter",
                    "status": "warn",
                    "available": True,
                    "message": "credentials missing",
                    "setup_hint": "set API key",
                }
            ],
            "collector_drilldown": [
                {
                    "tier": "tier_1",
                    "name": "twitter",
                    "status": "warn",
                    "available": True,
                    "message": "credentials missing",
                    "setup_hint": "set API key",
                }
            ],
            "watch_metrics": {
                "state": "running",
                "heartbeat_at": "2026-03-06T00:00:00+00:00",
                "cycles_total": 3,
                "runs_total": 2,
                "success_total": 2,
                "error_total": 0,
                "alerts_total": 1,
                "success_rate": 1.0,
                "last_error": "",
            },
            "watch_summary": {
                "total": 2,
                "enabled": 1,
                "disabled": 1,
                "healthy": 1,
                "degraded": 0,
                "idle": 0,
                "due": 1,
            },
            "watch_health": [
                {
                    "id": "launch-ops",
                    "name": "Launch Ops",
                    "enabled": True,
                    "status": "healthy",
                    "is_due": True,
                    "schedule_label": "hourly",
                    "next_run_at": "2026-03-06T01:00:00+00:00",
                    "last_run_at": "2026-03-06T00:00:00+00:00",
                    "last_run_status": "success",
                    "last_run_error": "",
                    "alert_rule_count": 1,
                    "run_total": 1,
                    "success_total": 1,
                    "error_total": 0,
                    "success_rate": 1.0,
                    "average_items": 2.0,
                },
                {
                    "id": "old-watch",
                    "name": "Old Watch",
                    "enabled": False,
                    "status": "disabled",
                    "is_due": False,
                    "schedule_label": "manual",
                    "next_run_at": "",
                    "last_run_at": "",
                    "last_run_status": "",
                    "last_run_error": "",
                    "alert_rule_count": 0,
                    "run_total": 0,
                    "success_total": 0,
                    "error_total": 0,
                    "success_rate": None,
                    "average_items": 0.0,
                },
            ],
            "route_summary": {"total": 1, "healthy": 1, "degraded": 0, "missing": 0, "idle": 0},
            "route_health": self.alert_route_health(),
            "route_drilldown": [
                {
                    "name": "ops-webhook",
                    "channel": "webhook",
                    "status": "healthy",
                    "configured": True,
                    "event_count": 1,
                    "delivered_count": 1,
                    "failure_count": 0,
                    "success_rate": 1.0,
                    "last_event_at": "2026-03-06T00:00:10+00:00",
                    "last_delivered_at": "2026-03-06T00:00:10+00:00",
                    "last_failed_at": "",
                    "last_error": "",
                    "last_summary": "Launch Ops triggered console-threshold",
                    "mission_count": 1,
                    "rule_count": 1,
                    "mission_ids": ["launch-ops"],
                    "rule_names": ["console-threshold"],
                }
            ],
            "route_timeline": [
                {
                    "route": "ops-webhook",
                    "channel": "webhook",
                    "mission_id": "launch-ops",
                    "mission_name": "Launch Ops",
                    "rule_name": "console-threshold",
                    "created_at": "2026-03-06T00:00:10+00:00",
                    "status": "delivered",
                    "summary": "Launch Ops triggered console-threshold",
                    "error": "",
                    "delivered_channels": ["json", "webhook:ops-webhook"],
                }
            ],
            "recent_failures": [
                {
                    "kind": "route_delivery",
                    "name": "ops-webhook",
                    "channel": "webhook",
                    "status": "degraded",
                    "error": "timeout",
                }
            ],
            "recent_alerts": self.list_alerts(),
            "daemon": self.watch_status_snapshot(),
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
            },
            {
                "id": "item-2",
                "title": "OpenAI launch recap",
                "review_state": "verified",
                "score": 74,
                "confidence": 0.82,
                "url": "https://example.com/openai-launch-recap",
                "review_notes": [
                    {
                        "note": "Validated against primary launch source.",
                        "author": "analyst",
                        "created_at": "2026-03-06T00:05:00+00:00",
                    }
                ],
            },
        ]

    def triage_stats(self):
        return {
            "total": 2,
            "open_count": 1,
            "closed_count": 1,
            "note_count": 1,
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

    def update_story(self, identifier, **kwargs):
        if identifier != "story-openai-launch":
            return None
        payload = self.show_story(identifier)
        if kwargs.get("title") is not None:
            payload["title"] = kwargs["title"]
        if kwargs.get("summary") is not None:
            payload["summary"] = kwargs["summary"]
        if kwargs.get("status") is not None:
            payload["status"] = kwargs["status"]
        payload["updated_at"] = "2026-03-07T00:00:00+00:00"
        return payload

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
    assert "Command Chamber For Signal Operations" in response.text
    assert "/brand/icon" in response.text
    assert "/brand/square" in response.text
    assert "create-watch-form" in response.text
    assert "create-watch-suggestions" in response.text
    assert "console-action-history" in response.text
    assert "command-palette" in response.text
    assert "Mission Cockpit" in response.text
    assert "retry advice" in response.text
    assert "timeline strip" in response.text
    assert "filter chips" in response.text
    assert "alert rule editor" in response.text
    assert "Add Alert Rule" in response.text
    assert "Save Alert Rules" in response.text
    assert "collector drill-down" in response.text
    assert "route drill-down" in response.text
    assert "route timeline" in response.text
    assert "Distribution Health" in response.text
    assert "Triage Queue" in response.text
    assert "triage filters" in response.text
    assert "triage shortcuts" in response.text
    assert "Use J/K to move" in response.text
    assert "note composer" in response.text
    assert "Save Note" in response.text
    assert "Story Workspace" in response.text
    assert "story editor" in response.text
    assert "Save Story" in response.text


def test_console_brand_hero_serves_jpeg():
    client = _client()
    response = client.get("/brand/hero")

    assert response.status_code == 200
    assert response.headers["content-type"] == "image/jpeg"
    assert response.content


def test_console_brand_source_serves_jpeg():
    client = _client()
    response = client.get("/brand/source")

    assert response.status_code == 200
    assert response.headers["content-type"] == "image/jpeg"
    assert response.content


def test_console_brand_square_serves_jpeg():
    client = _client()
    response = client.get("/brand/square")

    assert response.status_code == 200
    assert response.headers["content-type"] == "image/jpeg"
    assert response.content


def test_console_brand_icon_serves_png():
    client = _client()
    response = client.get("/brand/icon")

    assert response.status_code == 200
    assert response.headers["content-type"] == "image/png"
    assert response.content


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


def test_console_deck_suggestions_route():
    client = _client()
    response = client.post(
        "/api/console/deck/suggestions",
        json={
            "name": "Launch Pulse",
            "query": "OpenAI launch",
            "platform": "",
            "route": "",
            "keyword": "",
            "domain": "",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["recommended_route"] == "ops-webhook"
    assert payload["recommended_platform"] in {"twitter", "news", "web"}
    assert payload["similar_watches"][0]["id"] == "launch-ops"


def test_console_run_due_route():
    client = _client()
    response = client.post("/api/watches/run-due", json={"limit": 0})

    assert response.status_code == 200
    payload = response.json()
    assert payload["due_count"] == 1
    assert payload["run_count"] == 1


def test_console_set_watch_alert_rules_route():
    client = _client()
    response = client.put(
        "/api/watches/launch-ops/alert-rules",
        json={
            "alert_rules": [
                {"name": "console-threshold", "routes": ["ops-webhook"], "domains": ["openai.com"]},
                {"name": "console-threshold", "routes": ["exec-telegram"], "keyword_any": ["ship"]},
            ]
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["alert_rule_count"] == 2
    assert payload["alert_rules"][0]["routes"] == ["ops-webhook"]
    assert payload["alert_rules"][1]["routes"] == ["exec-telegram"]


def test_console_enable_and_delete_watch_routes():
    client = _client()

    enable_response = client.post("/api/watches/launch-ops/enable")
    delete_response = client.delete("/api/watches/launch-ops")

    assert enable_response.status_code == 200
    assert enable_response.json()["enabled"] is True
    assert delete_response.status_code == 200
    assert delete_response.json()["deleted"] is True


def test_console_routes_and_status():
    client = _client()

    routes = client.get("/api/alert-routes")
    health = client.get("/api/alert-routes/health?limit=20")
    status = client.get("/api/watch-status")
    ops = client.get("/api/ops")

    assert routes.status_code == 200
    assert routes.json()[0]["name"] == "ops-webhook"
    assert health.status_code == 200
    assert health.json()[0]["status"] == "healthy"
    assert health.json()[0]["success_rate"] == 1.0
    assert status.status_code == 200
    assert status.json()["metrics"]["cycles_total"] == 3
    assert ops.status_code == 200
    assert ops.json()["collector_summary"]["warn"] == 1
    assert ops.json()["watch_summary"]["healthy"] == 1
    assert ops.json()["watch_health"][0]["id"] == "launch-ops"
    assert ops.json()["collector_drilldown"][0]["name"] == "twitter"
    assert ops.json()["route_drilldown"][0]["name"] == "ops-webhook"
    assert ops.json()["route_timeline"][0]["route"] == "ops-webhook"
    assert ops.json()["degraded_collectors"][0]["name"] == "twitter"


def test_console_watch_detail_route():
    client = _client()
    response = client.get("/api/watches/launch-ops")

    assert response.status_code == 200
    payload = response.json()
    assert payload["id"] == "launch-ops"
    assert payload["run_stats"]["success"] == 1
    assert payload["last_failure"]["status"] == "error"
    assert payload["retry_advice"]["retry_command"] == "datapulse --watch-run launch-ops"
    assert payload["recent_results"][0]["id"] == "item-1"
    assert payload["result_filters"]["window_count"] == 1
    assert payload["timeline_strip"][0]["kind"] == "alert"
    assert payload["recent_alerts"][0]["rule_name"] == "console-threshold"


def test_console_watch_results_route():
    client = _client()
    response = client.get("/api/watches/launch-ops/results?limit=5")

    assert response.status_code == 200
    payload = response.json()
    assert payload[0]["id"] == "item-1"
    assert payload[0]["title"] == "OpenAI launch post"


def test_console_triage_routes():
    client = _client()

    triage = client.get("/api/triage?limit=5")
    stats = client.get("/api/triage/stats")
    explain = client.get("/api/triage/item-1/explain?limit=3")
    update = client.post("/api/triage/item-1/state", json={"state": "verified"})
    note = client.post("/api/triage/item-1/note", json={"note": "Escalate after duplicate review", "author": "console"})

    assert triage.status_code == 200
    assert triage.json()[0]["id"] == "item-1"
    assert stats.status_code == 200
    assert stats.json()["open_count"] == 1
    assert stats.json()["note_count"] == 1
    assert explain.status_code == 200
    assert explain.json()["candidates"][0]["id"] == "item-2"
    assert update.status_code == 200
    assert update.json()["review_state"] == "verified"
    assert note.status_code == 200
    assert note.json()["review_notes"][0]["note"] == "Escalate after duplicate review"


def test_console_story_routes():
    client = _client()

    stories = client.get("/api/stories?limit=4&min_items=2")
    detail = client.get("/api/stories/story-openai-launch")
    update = client.put(
        "/api/stories/story-openai-launch",
        json={
            "title": "OpenAI Launch Watch",
            "summary": "Condensed launch summary",
            "status": "monitoring",
        },
    )
    graph = client.get("/api/stories/story-openai-launch/graph?entity_limit=6")
    export = client.get("/api/stories/story-openai-launch/export?format=markdown")

    assert stories.status_code == 200
    assert stories.json()[0]["id"] == "story-openai-launch"
    assert detail.status_code == 200
    assert detail.json()["primary_item_id"] == "item-1"
    assert update.status_code == 200
    assert update.json()["title"] == "OpenAI Launch Watch"
    assert update.json()["status"] == "monitoring"
    assert graph.status_code == 200
    assert graph.json()["relation_count"] == 1
    assert graph.json()["nodes"][1]["label"] == "OpenAI"
    assert export.status_code == 200
    assert export.headers["content-type"].startswith("text/markdown")
    assert export.text.startswith("# OpenAI Launch")
