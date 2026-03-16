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
            "result_filters": {
                "window_count": 1,
                "states": [{"key": "new", "label": "new", "count": 1}],
                "sources": [{"key": "search", "label": "search", "count": 1}],
                "domains": [{"key": "example.com", "label": "example.com", "count": 1}],
            },
            "recent_alerts": [
                {
                    "id": "alert-1",
                    "rule_name": "threshold",
                    "created_at": "2026-03-06T00:00:10+00:00",
                }
            ],
            "timeline_strip": [
                {
                    "kind": "alert",
                    "time": "2026-03-06T00:00:10+00:00",
                    "label": "alert: threshold",
                    "detail": "json | AI Radar triggered threshold",
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
                "watch_filters": {
                    "state": "new",
                    "source": "search",
                    "domain": "example.com",
                },
            }
        ][:limit]

    def set_watch_alert_rules(self, identifier, *, alert_rules=None):
        if identifier != "ai-radar":
            return None
        payload = self.show_watch(identifier)
        payload["alert_rules"] = list(alert_rules or [])
        payload["alert_rule_count"] = len(payload["alert_rules"])
        return payload

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

    def governance_scorecard_snapshot(self):
        return {
            "generated_at": "2026-03-06T00:00:30+00:00",
            "summary": {"signal_count": 5, "ok": 4, "watch": 1, "missing": 0},
            "signals": {
                "coverage": {"covered_targets_total": 3},
                "story_conversion": {"converted_item_count": 1},
            },
        }

    def ai_surface_precheck(self, surface, *, mode="assist"):
        return {
            "ok": True,
            "surface": surface,
            "mode": mode,
            "mode_status": "admitted",
            "contract_id": f"{surface}.v1",
            "alias": f"{surface}-alias",
        }

    def ai_mission_suggest(self, identifier, *, mode="assist"):
        if identifier != "ai-radar":
            return None
        return {
            "surface": "mission_suggest",
            "mode": mode,
            "subject": {"kind": "WatchMission", "id": identifier},
            "precheck": self.ai_surface_precheck("mission_suggest", mode=mode),
            "output": {"contract_id": "datapulse_ai_watch_suggestion.v1", "payload": {"proposed_query": "OpenAI agents"}},
            "runtime_facts": {"status": "fallback_used", "request_id": "mission-123"},
        }

    def ai_triage_assist(self, item_id, *, mode="assist", limit=5):
        if item_id != "item-1":
            return None
        return {
            "surface": "triage_assist",
            "mode": mode,
            "subject": {"kind": "DataPulseItem", "id": item_id},
            "precheck": self.ai_surface_precheck("triage_assist", mode=mode),
            "output": {"contract_id": "datapulse_ai_triage_explain.v1", "payload": {"candidate_count": 1, "returned_count": min(limit, 1)}},
            "runtime_facts": {"status": "fallback_used", "request_id": "triage-123"},
        }

    def ai_claim_draft(self, story_id, *, mode="assist", brief_id=""):
        if story_id != "story-openai-launch":
            return None
        return {
            "surface": "claim_draft",
            "mode": mode,
            "subject": {"kind": "Story", "id": story_id},
            "precheck": self.ai_surface_precheck("claim_draft", mode=mode),
            "output": {"contract_id": "datapulse_ai_claim_draft.v1", "payload": {"claim_cards": [{"id": "claim-1"}]}},
            "runtime_facts": {"status": "fallback_used", "request_id": "claim-123"},
        }

    def ai_report_draft(self, report_id, *, mode="assist", profile_id=""):
        if report_id != "report-runtime-closure":
            return None
        return {
            "surface": "report_draft",
            "mode": mode,
            "subject": {"kind": "Report", "id": report_id},
            "precheck": {
                **self.ai_surface_precheck("report_draft", mode=mode),
                "ok": False,
                "mode_status": "rejected",
                "admission_status": "rejected",
                "alias": "dp.report.draft",
            },
            "output": None,
            "runtime_facts": {
                "status": "rejected",
                "request_id": "report-123",
                "served_by_alias": "dp.report.draft",
                "schema_valid": False,
                "errors": ["missing_structured_contract"],
            },
        }

    def ai_delivery_summary(self, identifier, *, mode="assist"):
        if identifier != "alert-1":
            return None
        return {
            "surface": "delivery_summary",
            "mode": mode,
            "subject": {"kind": "AlertEvent", "id": identifier},
            "precheck": self.ai_surface_precheck("delivery_summary", mode=mode),
            "output": {
                "contract_id": "datapulse_ai_delivery_summary.v1",
                "payload": {
                    "summary": "Alert `ops-threshold` is `healthy` across 1 delivery target.",
                    "overall_status": "healthy",
                    "routes": [
                        {
                            "name": "ops-webhook",
                            "channel": "webhook",
                            "status": "healthy",
                            "event_count": 1,
                            "delivered_count": 1,
                            "failure_count": 0,
                        }
                    ],
                },
            },
            "runtime_facts": {"status": "fallback_used", "request_id": "delivery-123"},
        }

    def ops_snapshot(self, **kwargs):
        return {
            "collector_summary": {"total": 4, "ok": 2, "warn": 1, "error": 1, "available": 3, "unavailable": 1},
            "collector_tiers": {
                "tier_0": {"total": 2, "ok": 2, "warn": 0, "error": 0, "available": 2, "unavailable": 0},
                "tier_1": {"total": 1, "ok": 0, "warn": 1, "error": 0, "available": 1, "unavailable": 0},
            },
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
            "watch_metrics": {"state": "idle", "runs_total": 2, "success_total": 1, "error_total": 1, "success_rate": 0.5},
            "watch_summary": {"total": 1, "enabled": 1, "disabled": 0, "healthy": 0, "degraded": 1, "idle": 0, "due": 1},
            "watch_health": [
                {
                    "id": "ai-radar",
                    "name": "AI Radar",
                    "enabled": True,
                    "status": "degraded",
                    "is_due": True,
                    "schedule_label": "hourly",
                    "next_run_at": "2026-03-06T01:00:00+00:00",
                    "last_run_at": "2026-03-06T00:00:00+00:00",
                    "last_run_status": "error",
                    "last_run_error": "temporary failure",
                    "alert_rule_count": 1,
                    "run_total": 2,
                    "success_total": 1,
                    "error_total": 1,
                    "success_rate": 0.5,
                    "average_items": 1.0,
                }
            ],
            "route_summary": {"total": 1, "healthy": 1, "degraded": 0, "missing": 0, "idle": 0},
            "route_drilldown": [
                {
                    "name": "ops-webhook",
                    "channel": "webhook",
                    "status": "healthy",
                    "event_count": 1,
                    "delivered_count": 1,
                    "failure_count": 0,
                    "success_rate": 1.0,
                    "mission_count": 1,
                    "rule_count": 1,
                    "last_summary": "AI Radar triggered threshold",
                }
            ],
            "route_timeline": [
                {
                    "route": "ops-webhook",
                    "channel": "webhook",
                    "mission_id": "ai-radar",
                    "mission_name": "AI Radar",
                    "rule_name": "threshold",
                    "created_at": "2026-03-06T00:00:10+00:00",
                    "status": "delivered",
                    "summary": "AI Radar triggered threshold",
                    "error": "",
                    "delivered_channels": ["json", "webhook:ops-webhook"],
                }
            ],
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

    def update_story(self, identifier, **kwargs):
        return {
            "id": identifier,
            "title": kwargs.get("title") or "OpenAI Launch Story",
            "summary": kwargs.get("summary") or "Condensed launch summary",
            "status": kwargs.get("status") or "monitoring",
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
        "watch_set_alert_rules",
        "watch_results",
        "run_watch",
        "disable_watch",
        "run_due_watches",
        "list_alerts",
        "list_alert_routes",
        "alert_route_health",
        "watch_status",
        "ops_overview",
        "ops_scorecard",
        "ai_surface_precheck",
        "ai_mission_suggest",
        "ai_triage_assist",
        "ai_claim_draft",
        "ai_report_draft",
        "ai_delivery_summary",
        "triage_list",
        "triage_explain",
        "triage_update",
        "triage_note",
        "triage_stats",
        "story_build",
        "story_list",
        "story_show",
        "story_update",
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
    assert payload["mission"]["result_filters"]["window_count"] == 1
    assert payload["mission"]["timeline_strip"][0]["kind"] == "alert"
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
async def test_mcp_watch_set_alert_rules_tool(monkeypatch):
    monkeypatch.setattr(mcp_server, "DataPulseReader", lambda: _WatchMCPReader())
    app = _make_app()

    raw = await app._run_tool(
        "watch_set_alert_rules",
        {"identifier": "ai-radar", "alert_rules": [{"name": "threshold", "routes": ["ops-webhook"]}]},
    )
    payload = json.loads(raw)

    assert payload["ok"] is True
    assert payload["mission"]["alert_rule_count"] == 1
    assert payload["mission"]["alert_rules"][0]["routes"] == ["ops-webhook"]


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
    assert payload["watch_summary"]["degraded"] == 1
    assert payload["watch_health"][0]["id"] == "ai-radar"
    assert payload["recent_failures"][0]["mission_name"] == "AI Radar"


@pytest.mark.asyncio
async def test_mcp_ops_scorecard_tool(monkeypatch):
    monkeypatch.setattr(mcp_server, "DataPulseReader", lambda: _WatchMCPReader())
    app = _make_app()

    raw = await app._run_tool("ops_scorecard", {})
    payload = json.loads(raw)

    assert payload["summary"]["signal_count"] == 5
    assert payload["signals"]["story_conversion"]["converted_item_count"] == 1


@pytest.mark.asyncio
async def test_mcp_ai_surface_precheck_tool(monkeypatch):
    monkeypatch.setattr(mcp_server, "DataPulseReader", lambda: _WatchMCPReader())
    app = _make_app()

    raw = await app._run_tool("ai_surface_precheck", {"surface": "mission_suggest", "mode": "review"})
    payload = json.loads(raw)

    assert payload["surface"] == "mission_suggest"
    assert payload["mode"] == "review"
    assert payload["mode_status"] == "admitted"


@pytest.mark.asyncio
async def test_mcp_ai_projection_tools(monkeypatch):
    monkeypatch.setattr(mcp_server, "DataPulseReader", lambda: _WatchMCPReader())
    app = _make_app()

    mission_raw = await app._run_tool("ai_mission_suggest", {"identifier": "ai-radar"})
    mission_payload = json.loads(mission_raw)
    assert mission_payload["ok"] is True
    assert mission_payload["projection"]["output"]["contract_id"] == "datapulse_ai_watch_suggestion.v1"

    triage_raw = await app._run_tool("ai_triage_assist", {"item_id": "item-1", "limit": 3})
    triage_payload = json.loads(triage_raw)
    assert triage_payload["ok"] is True
    assert triage_payload["projection"]["output"]["contract_id"] == "datapulse_ai_triage_explain.v1"
    assert triage_payload["projection"]["output"]["payload"]["returned_count"] == 1

    claim_raw = await app._run_tool("ai_claim_draft", {"story_id": "story-openai-launch", "brief_id": "brief-1"})
    claim_payload = json.loads(claim_raw)
    assert claim_payload["ok"] is True
    assert claim_payload["projection"]["output"]["contract_id"] == "datapulse_ai_claim_draft.v1"
    assert claim_payload["projection"]["runtime_facts"]["request_id"] == "claim-123"

    report_raw = await app._run_tool("ai_report_draft", {"report_id": "report-runtime-closure", "mode": "review"})
    report_payload = json.loads(report_raw)
    assert report_payload["ok"] is True
    assert report_payload["projection"]["output"] is None
    assert report_payload["projection"]["runtime_facts"]["request_id"] == "report-123"
    assert report_payload["projection"]["runtime_facts"]["served_by_alias"] == "dp.report.draft"

    delivery_raw = await app._run_tool("ai_delivery_summary", {"identifier": "alert-1", "mode": "review"})
    delivery_payload = json.loads(delivery_raw)
    assert delivery_payload["ok"] is True
    assert delivery_payload["projection"]["output"]["contract_id"] == "datapulse_ai_delivery_summary.v1"
    assert delivery_payload["projection"]["runtime_facts"]["request_id"] == "delivery-123"


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
async def test_mcp_story_update_tool(monkeypatch):
    monkeypatch.setattr(mcp_server, "DataPulseReader", lambda: _WatchMCPReader())
    app = _make_app()

    raw = await app._run_tool(
        "story_update",
        {
            "identifier": "story-openai-launch",
            "title": "OpenAI Launch Watch",
            "summary": "Condensed launch summary",
            "status": "monitoring",
        },
    )
    payload = json.loads(raw)

    assert payload["ok"] is True
    assert payload["story"]["title"] == "OpenAI Launch Watch"
    assert payload["story"]["status"] == "monitoring"


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
