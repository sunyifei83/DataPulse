"""Tests for MCP watch mission tools."""

from __future__ import annotations

import json

import pytest

import datapulse.mcp_server as mcp_server


class _WatchMCPReader:
    def create_watch(self, **kwargs):
        return {
            "id": "ai-radar",
            "name": kwargs["name"],
            "query": kwargs["query"],
            "platforms": kwargs.get("platforms", []) or [],
            "sites": kwargs.get("sites", []) or [],
            "schedule": kwargs.get("schedule", "manual"),
            "min_confidence": kwargs.get("min_confidence", 0.0),
            "top_n": kwargs.get("top_n", 5),
            "alert_rules": kwargs.get("alert_rules", []) or [],
            "enabled": True,
        }

    def list_watches(self, include_disabled=False):
        payload = [
            {
                "id": "ai-radar",
                "name": "AI Radar",
                "query": "OpenAI agents",
                "enabled": True,
            }
        ]
        if include_disabled:
            payload.append(
                {
                    "id": "old-watch",
                    "name": "Old Watch",
                    "query": "legacy",
                    "enabled": False,
                }
            )
        return payload

    def show_watch(self, identifier):
        if identifier != "ai-radar":
            return None
        return {
            "id": "ai-radar",
            "name": "AI Radar",
            "query": "OpenAI agents",
            "enabled": True,
            "schedule_label": "hourly",
            "is_due": True,
            "next_run_at": "2026-03-06T01:00:00+00:00",
            "run_stats": {"total": 2, "success": 1, "error": 1},
            "last_failure": {
                "id": "ai-radar:2026-03-05T23:00:00+00:00",
                "status": "error",
                "trigger": "scheduled",
                "item_count": 0,
                "finished_at": "2026-03-05T23:00:03+00:00",
                "error": "temporary upstream failure",
            },
            "retry_advice": {
                "failure_class": "transient",
                "summary": "The last failed run looks like a transient upstream or network failure.",
                "retry_command": "datapulse --watch-run ai-radar",
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
                    "A manual rerun is usually safe once the upstream recovers.",
                    "Fix the degraded collector setup below before rerunning the mission.",
                ],
            },
            "recent_results": self.list_watch_results(identifier),
            "result_stats": {
                "stored_result_count": 1,
                "returned_result_count": 1,
                "latest_result_at": "2026-03-06T00:00:00+00:00",
            },
            "recent_alerts": [
                {
                    "id": "alert-1",
                    "rule_name": "threshold",
                    "created_at": "2026-03-06T00:00:10+00:00",
                }
            ],
        }

    def list_watch_results(self, identifier, limit=10, min_confidence=0.0):
        if identifier != "ai-radar":
            return None
        return [
            {
                "id": "item-1",
                "title": "OpenAI agents result",
                "url": "https://example.com/openai-agents",
                "score": 73,
                "confidence": 0.91,
                "review_state": "new",
                "source_name": "search",
                "source_type": "generic",
            }
        ][:limit]

    async def run_watch(self, identifier):
        return {
            "mission": {"id": identifier, "name": "AI Radar", "query": "OpenAI agents"},
            "run": {"status": "success", "item_count": 1},
            "items": [
                {
                    "id": "item-1",
                    "title": "OpenAI agents result",
                    "url": "https://example.com/openai-agents",
                }
            ],
        }

    def disable_watch(self, identifier):
        return {"id": identifier, "enabled": False}

    async def run_due_watches(self, limit=None):
        return {
            "due_count": 1,
            "run_count": 1,
            "results": [
                {
                    "mission_id": "ai-radar",
                    "mission_name": "AI Radar",
                    "status": "success",
                    "item_count": 2,
                }
            ],
        }

    def list_alerts(self, limit=20, mission_id=None):
        return [
            {
                "id": "alert-1",
                "mission_name": "AI Radar",
                "rule_name": "threshold",
                "summary": "AI Radar triggered threshold",
            }
        ]

    def list_alert_routes(self):
        return [
            {
                "name": "ops-webhook",
                "channel": "webhook",
                "webhook_url": "***",
            }
        ]

    def alert_route_health(self, limit=100):
        return [
            {
                "name": "ops-webhook",
                "channel": "webhook",
                "status": "healthy",
                "event_count": 1,
                "delivered_count": 1,
                "failure_count": 0,
                "success_rate": 1.0,
            }
        ]

    def watch_status_snapshot(self):
        return {
            "state": "idle",
            "heartbeat_at": "2026-03-06T00:00:00+00:00",
            "metrics": {"cycles_total": 3},
        }

    def ops_snapshot(self, **kwargs):
        return {
            "collector_summary": {"total": 4, "ok": 2, "warn": 1, "error": 1, "available": 3, "unavailable": 1},
            "watch_metrics": {"state": "idle", "runs_total": 2, "success_total": 1, "error_total": 1, "success_rate": 0.5},
            "route_summary": {"total": 1, "healthy": 1, "degraded": 0, "missing": 0, "idle": 0},
            "recent_failures": [{"kind": "watch_run", "mission_name": "AI Radar", "status": "error", "error": "temporary failure"}],
        }

    def triage_list(self, **kwargs):
        return [
            {
                "id": "item-1",
                "title": "OpenAI launch post",
                "review_state": "new",
                "score": 81,
            }
        ]

    def triage_update(self, item_id, **kwargs):
        return {
            "id": item_id,
            "review_state": kwargs["state"],
            "duplicate_of": kwargs.get("duplicate_of"),
        }

    def triage_note(self, item_id, **kwargs):
        return {
            "id": item_id,
            "review_notes": [{"note": kwargs["note"]}],
            "review_state": "new",
        }

    def triage_stats(self, **kwargs):
        return {
            "total": 3,
            "open_count": 2,
            "closed_count": 1,
            "states": {"new": 1, "triaged": 0, "verified": 1, "duplicate": 1, "ignored": 0, "escalated": 0},
        }

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
                    "similarity": 0.82,
                    "signals": ["same_domain", "title_overlap"],
                }
            ],
        }

    def story_build(self, **kwargs):
        return {
            "stats": {"stories_built": 1, "stories_saved": 1},
            "stories": [
                {
                    "id": "story-openai-launch",
                    "title": "OpenAI Launch Story",
                    "item_count": 2,
                }
            ],
        }

    def list_stories(self, **kwargs):
        return [
            {
                "id": "story-openai-launch",
                "title": "OpenAI Launch Story",
                "item_count": 2,
            }
        ]

    def show_story(self, identifier):
        return {
            "id": identifier,
            "title": "OpenAI Launch Story",
            "item_count": 2,
        }

    def story_graph(self, identifier, **kwargs):
        return {
            "story": {
                "id": identifier,
                "title": "OpenAI Launch Story",
            },
            "nodes": [
                {"id": identifier, "label": "OpenAI Launch Story", "kind": "story"},
                {"id": "entity:openai", "label": "OpenAI", "kind": "entity", "entity_type": "ORG"},
            ],
            "edges": [
                {"source": identifier, "target": "entity:openai", "relation_type": "MENTIONED_IN_STORY", "kind": "story_entity"}
            ],
            "entity_count": 1,
            "relation_count": 0,
            "edge_count": 1,
        }

    def export_story(self, identifier, **kwargs):
        if kwargs.get("output_format") == "markdown":
            return "# OpenAI Launch Story\n\n## Timeline"
        return '{\n  "id": "story-openai-launch"\n}'


def _make_app() -> mcp_server._LocalMCP:
    app = mcp_server._LocalMCP("datapulse")
    mcp_server._register_tools(app)
    return app


def test_mcp_registers_watch_tools():
    app = _make_app()
    tool_names = set(app.tools)

    assert {
        "create_watch",
        "list_watches",
        "watch_show",
        "watch_results",
        "run_watch",
        "disable_watch",
        "run_due_watches",
        "list_alerts",
        "list_alert_routes",
        "alert_route_health",
        "watch_status",
        "ops_overview",
        "triage_list",
        "triage_explain",
        "triage_update",
        "triage_note",
        "triage_stats",
        "story_build",
        "story_list",
        "story_show",
        "story_graph",
        "story_export",
    } <= tool_names


@pytest.mark.asyncio
async def test_mcp_create_watch_tool(monkeypatch):
    monkeypatch.setattr(mcp_server, "DataPulseReader", lambda: _WatchMCPReader())
    app = _make_app()

    raw = await app._run_tool(
        "create_watch",
        {
            "name": "AI Radar",
            "query": "OpenAI agents",
            "platforms": ["twitter"],
            "top_n": 5,
            "alert_rules": [{"name": "threshold", "min_score": 70}],
        },
    )
    payload = json.loads(raw)

    assert payload["id"] == "ai-radar"
    assert payload["name"] == "AI Radar"
    assert payload["platforms"] == ["twitter"]
    assert payload["alert_rules"][0]["name"] == "threshold"


@pytest.mark.asyncio
async def test_mcp_run_watch_tool(monkeypatch):
    monkeypatch.setattr(mcp_server, "DataPulseReader", lambda: _WatchMCPReader())
    app = _make_app()

    raw = await app._run_tool("run_watch", {"identifier": "ai-radar"})
    payload = json.loads(raw)

    assert payload["mission"]["id"] == "ai-radar"
    assert payload["run"]["status"] == "success"
    assert payload["items"][0]["title"] == "OpenAI agents result"


@pytest.mark.asyncio
async def test_mcp_watch_show_tool(monkeypatch):
    monkeypatch.setattr(mcp_server, "DataPulseReader", lambda: _WatchMCPReader())
    app = _make_app()

    raw = await app._run_tool("watch_show", {"identifier": "ai-radar"})
    payload = json.loads(raw)

    assert payload["ok"] is True
    assert payload["mission"]["id"] == "ai-radar"
    assert payload["mission"]["run_stats"]["error"] == 1
    assert payload["mission"]["recent_results"][0]["id"] == "item-1"
    assert payload["mission"]["retry_advice"]["retry_command"] == "datapulse --watch-run ai-radar"


@pytest.mark.asyncio
async def test_mcp_watch_results_tool(monkeypatch):
    monkeypatch.setattr(mcp_server, "DataPulseReader", lambda: _WatchMCPReader())
    app = _make_app()

    raw = await app._run_tool("watch_results", {"identifier": "ai-radar", "limit": 5})
    payload = json.loads(raw)

    assert payload["ok"] is True
    assert payload["results"][0]["id"] == "item-1"
    assert payload["results"][0]["title"] == "OpenAI agents result"


@pytest.mark.asyncio
async def test_mcp_disable_watch_tool(monkeypatch):
    monkeypatch.setattr(mcp_server, "DataPulseReader", lambda: _WatchMCPReader())
    app = _make_app()

    raw = await app._run_tool("disable_watch", {"identifier": "ai-radar"})
    payload = json.loads(raw)

    assert payload["ok"] is True
    assert payload["mission"]["id"] == "ai-radar"


@pytest.mark.asyncio
async def test_mcp_run_due_watches_tool(monkeypatch):
    monkeypatch.setattr(mcp_server, "DataPulseReader", lambda: _WatchMCPReader())
    app = _make_app()

    raw = await app._run_tool("run_due_watches", {"limit": 5})
    payload = json.loads(raw)

    assert payload["due_count"] == 1
    assert payload["run_count"] == 1
    assert payload["results"][0]["mission_name"] == "AI Radar"


@pytest.mark.asyncio
async def test_mcp_list_alerts_tool(monkeypatch):
    monkeypatch.setattr(mcp_server, "DataPulseReader", lambda: _WatchMCPReader())
    app = _make_app()

    raw = await app._run_tool("list_alerts", {"limit": 5})
    payload = json.loads(raw)

    assert payload[0]["id"] == "alert-1"
    assert payload[0]["rule_name"] == "threshold"


@pytest.mark.asyncio
async def test_mcp_list_alert_routes_tool(monkeypatch):
    monkeypatch.setattr(mcp_server, "DataPulseReader", lambda: _WatchMCPReader())
    app = _make_app()

    raw = await app._run_tool("list_alert_routes", {})
    payload = json.loads(raw)

    assert payload[0]["name"] == "ops-webhook"
    assert payload[0]["channel"] == "webhook"


@pytest.mark.asyncio
async def test_mcp_alert_route_health_tool(monkeypatch):
    monkeypatch.setattr(mcp_server, "DataPulseReader", lambda: _WatchMCPReader())
    app = _make_app()

    raw = await app._run_tool("alert_route_health", {"limit": 20})
    payload = json.loads(raw)

    assert payload[0]["name"] == "ops-webhook"
    assert payload[0]["status"] == "healthy"
    assert payload[0]["success_rate"] == 1.0


@pytest.mark.asyncio
async def test_mcp_watch_status_tool(monkeypatch):
    monkeypatch.setattr(mcp_server, "DataPulseReader", lambda: _WatchMCPReader())
    app = _make_app()

    raw = await app._run_tool("watch_status", {})
    payload = json.loads(raw)

    assert payload["state"] == "idle"
    assert payload["metrics"]["cycles_total"] == 3


@pytest.mark.asyncio
async def test_mcp_ops_overview_tool(monkeypatch):
    monkeypatch.setattr(mcp_server, "DataPulseReader", lambda: _WatchMCPReader())
    app = _make_app()

    raw = await app._run_tool("ops_overview", {"alert_limit": 5})
    payload = json.loads(raw)

    assert payload["collector_summary"]["warn"] == 1
    assert payload["watch_metrics"]["success_rate"] == 0.5
    assert payload["recent_failures"][0]["mission_name"] == "AI Radar"


@pytest.mark.asyncio
async def test_mcp_triage_list_tool(monkeypatch):
    monkeypatch.setattr(mcp_server, "DataPulseReader", lambda: _WatchMCPReader())
    app = _make_app()

    raw = await app._run_tool("triage_list", {"limit": 5})
    payload = json.loads(raw)

    assert payload[0]["id"] == "item-1"
    assert payload[0]["review_state"] == "new"


@pytest.mark.asyncio
async def test_mcp_triage_update_tool(monkeypatch):
    monkeypatch.setattr(mcp_server, "DataPulseReader", lambda: _WatchMCPReader())
    app = _make_app()

    raw = await app._run_tool("triage_update", {"item_id": "item-1", "state": "verified", "note": "confirmed"})
    payload = json.loads(raw)

    assert payload["ok"] is True
    assert payload["item"]["review_state"] == "verified"


@pytest.mark.asyncio
async def test_mcp_triage_stats_tool(monkeypatch):
    monkeypatch.setattr(mcp_server, "DataPulseReader", lambda: _WatchMCPReader())
    app = _make_app()

    raw = await app._run_tool("triage_stats", {})
    payload = json.loads(raw)

    assert payload["total"] == 3
    assert payload["states"]["verified"] == 1


@pytest.mark.asyncio
async def test_mcp_triage_explain_tool(monkeypatch):
    monkeypatch.setattr(mcp_server, "DataPulseReader", lambda: _WatchMCPReader())
    app = _make_app()

    raw = await app._run_tool("triage_explain", {"item_id": "item-1", "limit": 3})
    payload = json.loads(raw)

    assert payload["ok"] is True
    assert payload["explanation"]["candidates"][0]["id"] == "item-2"


@pytest.mark.asyncio
async def test_mcp_story_build_and_show_tool(monkeypatch):
    monkeypatch.setattr(mcp_server, "DataPulseReader", lambda: _WatchMCPReader())
    app = _make_app()

    raw = await app._run_tool("story_build", {"max_stories": 5})
    payload = json.loads(raw)
    assert payload["stats"]["stories_built"] == 1

    raw_show = await app._run_tool("story_show", {"identifier": "story-openai-launch"})
    shown = json.loads(raw_show)
    assert shown["ok"] is True
    assert shown["story"]["id"] == "story-openai-launch"


@pytest.mark.asyncio
async def test_mcp_story_export_markdown_tool(monkeypatch):
    monkeypatch.setattr(mcp_server, "DataPulseReader", lambda: _WatchMCPReader())
    app = _make_app()

    raw = await app._run_tool("story_export", {"identifier": "story-openai-launch", "output_format": "markdown"})

    assert raw.startswith("# OpenAI Launch Story")


@pytest.mark.asyncio
async def test_mcp_story_graph_tool(monkeypatch):
    monkeypatch.setattr(mcp_server, "DataPulseReader", lambda: _WatchMCPReader())
    app = _make_app()

    raw = await app._run_tool("story_graph", {"identifier": "story-openai-launch", "entity_limit": 6})
    payload = json.loads(raw)

    assert payload["ok"] is True
    assert payload["graph"]["entity_count"] == 1
    assert payload["graph"]["nodes"][1]["label"] == "OpenAI"
