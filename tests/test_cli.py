"""CLI output behavior tests."""

from __future__ import annotations

import sys

import datapulse.cli as cli


class _TrendingReader:
    async def trending(self, **kwargs):
        return {
            "location": "worldwide",
            "requested_location": "china",
            "fallback_reason": "404 Client Error: Not Found for url: https://trends24.in/china/",
            "snapshot_time": "2026-03-06T00:00:00Z",
            "trend_count": 1,
            "trends": [
                {"rank": 1, "name": "YouTube Trending Videos", "volume": "200K posts"},
            ],
        }


class _SearchReader:
    def __init__(self, results):
        self._results = results

    async def search(self, *args, **kwargs):
        return self._results


class _TrendingEmptyReader:
    async def trending(self, **kwargs):
        return {
            "location": "worldwide",
            "requested_location": "us",
            "fallback_reason": "Low-signal trending snapshot (placeholder topics)",
            "snapshot_time": "",
            "trend_count": 0,
            "trends": [],
            "degraded": True,
        }


class _WatchReader:
    def create_watch(self, **kwargs):
        return {
            "id": "ai-radar",
            "name": kwargs["name"],
            "query": kwargs["query"],
            "mission_intent": kwargs.get("mission_intent", {}) or {},
            "intent_summary": {
                "has_intent": True,
                "demand_intent": "Track AI launches that could change competitive posture.",
                "key_questions": ["What changed?"],
                "scope": "entities=OpenAI | topics=agents",
                "freshness": "same day review | max_age<=24h",
                "coverage": "official blog, developer reaction",
                "coverage_target_count": 2,
            },
            "platforms": kwargs.get("platforms", []) or [],
            "sites": kwargs.get("sites", []) or [],
            "top_n": kwargs.get("top_n", 5),
            "alert_rules": kwargs.get("alert_rules", []) or [],
            "schedule_label": "manual",
            "is_due": False,
            "enabled": True,
        }

    def set_watch_alert_rules(self, identifier, *, alert_rules=None):
        if identifier != "ai-radar":
            return None
        payload = self.show_watch(identifier)
        payload["alert_rules"] = list(alert_rules or [])
        payload["alert_rule_count"] = len(payload["alert_rules"])
        return payload

    def list_watches(self, include_disabled=False):
        items = [
            {
                "id": "ai-radar",
                "name": "AI Radar",
                "query": "OpenAI agents",
                "intent_summary": {
                    "has_intent": True,
                    "demand_intent": "Track AI launches that could change competitive posture.",
                    "key_questions": ["What changed?"],
                    "scope": "entities=OpenAI | topics=agents",
                    "freshness": "same day review | max_age<=24h",
                    "coverage": "official blog, developer reaction",
                    "coverage_target_count": 2,
                },
                "platforms": ["twitter"],
                "sites": ["openai.com"],
                "top_n": 5,
                "schedule_label": "hourly",
                "is_due": True,
                "alert_rule_count": 1,
                "enabled": True,
                "last_run_at": "2026-03-06T00:00:00",
                "last_run_status": "success",
            }
        ]
        if include_disabled:
            items.append(
                {
                    "id": "old-watch",
                    "name": "Old Watch",
                    "query": "legacy",
                    "platforms": [],
                    "sites": [],
                    "top_n": 5,
                    "schedule_label": "manual",
                    "is_due": False,
                    "alert_rule_count": 0,
                    "enabled": False,
                    "last_run_at": "",
                    "last_run_status": "",
                }
            )
        return items

    def show_watch(self, identifier):
        if identifier != "ai-radar":
            return None
        return {
            "id": "ai-radar",
            "name": "AI Radar",
            "query": "OpenAI agents",
            "mission_intent": {
                "demand_intent": "Track AI launches that could change competitive posture.",
                "key_questions": ["What changed?", "How fast should we react?"],
                "scope_entities": ["OpenAI"],
                "scope_topics": ["agents"],
                "scope_regions": ["US"],
                "scope_window": "last 7 days",
                "freshness_expectation": "same day review",
                "freshness_max_age_hours": 24,
                "coverage_targets": ["official blog", "developer reaction"],
            },
            "intent_summary": {
                "has_intent": True,
                "demand_intent": "Track AI launches that could change competitive posture.",
                "key_questions": ["What changed?", "How fast should we react?"],
                "scope": "entities=OpenAI | topics=agents | regions=US | window=last 7 days",
                "freshness": "same day review | max_age<=24h",
                "coverage": "official blog, developer reaction",
                "coverage_target_count": 2,
            },
            "enabled": True,
            "schedule": "@hourly",
            "schedule_label": "hourly",
            "is_due": True,
            "next_run_at": "2026-03-06T01:00:00+00:00",
            "last_run_at": "2026-03-06T00:00:00+00:00",
            "last_run_status": "success",
            "last_run_error": "",
            "run_stats": {
                "total": 2,
                "success": 1,
                "error": 1,
                "average_items": 1.5,
            },
            "delivery_stats": {
                "recent_alert_count": 1,
                "recent_error_count": 1,
            },
            "runs": [
                {
                    "id": "ai-radar:2026-03-06T00:00:00+00:00",
                    "status": "success",
                    "trigger": "scheduled",
                    "item_count": 1,
                    "finished_at": "2026-03-06T00:00:05+00:00",
                    "error": "",
                },
                {
                    "id": "ai-radar:2026-03-05T23:00:00+00:00",
                    "status": "error",
                    "trigger": "scheduled",
                    "item_count": 0,
                    "finished_at": "2026-03-05T23:00:03+00:00",
                    "error": "temporary upstream failure",
                },
            ],
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
            "recent_alerts": [
                {
                    "id": "alert-1",
                    "rule_name": "threshold",
                    "delivered_channels": ["json", "webhook:ops-webhook"],
                    "created_at": "2026-03-06T00:00:10+00:00",
                    "summary": "AI Radar triggered threshold",
                }
            ],
            "result_filters": {
                "window_count": 1,
                "states": [{"key": "new", "label": "new", "count": 1}],
                "sources": [{"key": "search", "label": "search", "count": 1}],
                "domains": [{"key": "example.com", "label": "example.com", "count": 1}],
            },
            "timeline_strip": [
                {
                    "kind": "alert",
                    "time": "2026-03-06T00:00:10+00:00",
                    "label": "alert: threshold",
                    "detail": "json,webhook:ops-webhook | AI Radar triggered threshold",
                },
                {
                    "kind": "run",
                    "time": "2026-03-06T00:00:05+00:00",
                    "label": "run: success",
                    "detail": "trigger=scheduled | items=1",
                },
            ],
            "recent_results": self.list_watch_results(identifier),
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

    async def run_watch(self, identifier):
        return {
            "mission": {
                "id": identifier,
                "name": "AI Radar",
                "query": "OpenAI agents",
            },
            "run": {
                "status": "success",
                "item_count": 1,
            },
            "alert_events": [
                {
                    "id": "alert-1",
                    "mission_name": "AI Radar",
                    "rule_name": "threshold",
                }
            ],
            "items": [
                {
                    "title": "OpenAI agents result",
                    "confidence": 0.91,
                    "score": 73,
                    "url": "https://example.com/openai-agents",
                    "content": "Synthetic search result snippet",
                }
            ],
        }

    def disable_watch(self, identifier):
        return {"id": identifier, "enabled": False}

    async def run_due_watches(self, limit=None, **kwargs):
        return {
            "due_count": 1,
            "run_count": 1,
            "results": [
                {
                    "mission_id": "ai-radar",
                    "mission_name": "AI Radar",
                    "status": "success",
                    "item_count": 2,
                    "attempts": 1,
                    "alert_count": 1,
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
                "created_at": "2026-03-06T00:00:00+00:00",
                "delivered_channels": ["json", "markdown"],
                "extra": {},
            }
        ]

    def list_alert_routes(self):
        return [
            {
                "name": "ops-webhook",
                "channel": "webhook",
            }
        ]

    def alert_route_health(self, limit=100):
        return [
            {
                "name": "ops-webhook",
                "channel": "webhook",
                "status": "degraded",
                "event_count": 2,
                "delivered_count": 1,
                "failure_count": 1,
                "success_rate": 0.5,
                "last_event_at": "2026-03-06T00:00:10+00:00",
                "last_error": "webhook_url is required",
            }
        ]

    async def run_watch_daemon(self, **kwargs):
        return {
            "cycles": 1,
            "last_result": {
                "due_count": 1,
                "run_count": 1,
            },
        }

    def watch_status_snapshot(self):
        return {
            "state": "idle",
            "heartbeat_at": "2026-03-06T00:00:00+00:00",
            "last_error": "",
            "metrics": {
                "cycles_total": 3,
                "runs_total": 2,
                "alerts_total": 1,
            },
        }

    def ops_snapshot(self, **kwargs):
        return {
            "collector_summary": {
                "total": 4,
                "ok": 2,
                "warn": 1,
                "error": 1,
                "available": 3,
                "unavailable": 1,
            },
            "collector_tiers": {
                "tier_0": {"total": 2, "ok": 2, "warn": 0, "error": 0, "available": 2, "unavailable": 0},
                "tier_2": {"total": 1, "ok": 0, "warn": 0, "error": 1, "available": 0, "unavailable": 1},
            },
            "degraded_collectors": [
                {
                    "name": "telegram",
                    "tier": "tier_2",
                    "status": "error",
                    "available": False,
                    "message": "missing credentials",
                }
            ],
            "collector_drilldown": [
                {
                    "name": "telegram",
                    "tier": "tier_2",
                    "status": "error",
                    "available": False,
                    "message": "missing credentials",
                    "setup_hint": "add TG_API_ID/TG_API_HASH",
                }
            ],
            "watch_metrics": {
                "state": "idle",
                "heartbeat_at": "2026-03-06T00:00:00+00:00",
                "cycles_total": 3,
                "runs_total": 2,
                "success_total": 1,
                "error_total": 1,
                "alerts_total": 1,
                "success_rate": 0.5,
                "last_error": "",
            },
            "watch_summary": {
                "total": 2,
                "enabled": 1,
                "disabled": 1,
                "healthy": 0,
                "degraded": 1,
                "idle": 0,
                "due": 1,
            },
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
            "route_summary": {
                "total": 1,
                "healthy": 0,
                "degraded": 1,
                "missing": 0,
                "idle": 0,
            },
            "route_drilldown": [
                {
                    "name": "ops-webhook",
                    "channel": "webhook",
                    "status": "degraded",
                    "event_count": 2,
                    "delivered_count": 1,
                    "failure_count": 1,
                    "success_rate": 0.5,
                    "mission_count": 1,
                    "rule_count": 1,
                    "last_error": "webhook_url is required",
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
                    "status": "failed",
                    "summary": "AI Radar triggered threshold",
                    "error": "webhook_url is required",
                    "delivered_channels": ["json"],
                }
            ],
            "recent_failures": [
                {
                    "kind": "watch_run",
                    "mission_name": "AI Radar",
                    "status": "error",
                    "attempts": 2,
                    "error": "temporary failure",
                }
            ],
        }

    def governance_scorecard_snapshot(self):
        return {
            "generated_at": "2026-03-06T00:00:30+00:00",
            "mission_scope": {"total": 2, "enabled": 1, "disabled": 1, "items": 3, "stories": 1},
            "signals": {
                "coverage": {"status": "ok", "covered_targets_total": 3},
                "freshness": {"status": "watch", "fresh_missions": 1},
                "alert_yield": {"status": "ok", "alert_count": 1},
                "triage_throughput": {"status": "ok", "acted_on_items": 2},
                "story_conversion": {"status": "ok", "converted_item_count": 1},
            },
            "summary": {"signal_count": 5, "ok": 4, "watch": 1, "missing": 0},
        }

    def ai_surface_precheck(self, surface, *, mode="assist"):
        return {
            "ok": True,
            "surface": surface,
            "mode": mode,
            "mode_status": "admitted",
            "admission_status": "admitted",
            "alias": f"{surface}-alias",
            "contract_id": f"{surface}.v1",
            "manual_fallback": "manual_or_deterministic_behavior",
            "rejectable_gaps": [],
            "must_expose_runtime_facts": ["status", "request_id"],
        }

    def ai_mission_suggest(self, identifier, *, mode="assist"):
        if identifier != "ai-radar":
            return None
        return {
            "surface": "mission_suggest",
            "mode": mode,
            "subject": {"kind": "WatchMission", "id": identifier},
            "precheck": self.ai_surface_precheck("mission_suggest", mode=mode),
            "output": {
                "contract_id": "datapulse_ai_watch_suggestion.v1",
                "payload": {
                    "summary": "Mission `AI Radar` has 1 persisted result items and run readiness `ready`.",
                    "proposed_query": "OpenAI agents",
                },
            },
            "runtime_facts": {
                "status": "fallback_used",
                "source": "deterministic",
                "schema_valid": True,
                "request_id": "mission-123",
            },
        }

    def ai_triage_assist(self, item_id, *, mode="assist", limit=5):
        if item_id != "item-1":
            return None
        return {
            "surface": "triage_assist",
            "mode": mode,
            "subject": {"kind": "DataPulseItem", "id": item_id},
            "precheck": self.ai_surface_precheck("triage_assist", mode=mode),
            "output": {
                "contract_id": "datapulse_ai_triage_explain.v1",
                "payload": {
                    "item": {"id": item_id, "title": "OpenAI launch post"},
                    "candidate_count": 1,
                    "returned_count": min(limit, 1),
                },
            },
            "runtime_facts": {
                "status": "fallback_used",
                "source": "deterministic",
                "schema_valid": True,
                "request_id": "triage-123",
            },
        }

    def ai_claim_draft(self, story_id, *, mode="assist", brief_id=""):
        if story_id != "story-openai-launch":
            return None
        return {
            "surface": "claim_draft",
            "mode": mode,
            "subject": {"kind": "Story", "id": story_id},
            "precheck": self.ai_surface_precheck("claim_draft", mode=mode),
            "output": {
                "contract_id": "datapulse_ai_claim_draft.v1",
                "payload": {
                    "summary": "Draft evidence-bound claim cards without writing final report state.",
                    "claim_cards": [{"id": "claim-1", "statement": "Demand remains elevated."}],
                },
            },
            "runtime_facts": {
                "status": "fallback_used",
                "source": "deterministic",
                "schema_valid": True,
                "request_id": "claim-123",
            },
        }

    def ai_report_draft(self, report_id, *, mode="assist", profile_id=None):
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
                "source": "manual",
                "schema_valid": False,
                "served_by_alias": "dp.report.draft",
                "request_id": "report-123",
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
            "runtime_facts": {
                "status": "fallback_used",
                "source": "deterministic",
                "schema_valid": True,
                "request_id": "delivery-123",
            },
        }

    def triage_list(self, **kwargs):
        return [
            {
                "id": "item-1",
                "title": "OpenAI launch post",
                "review_state": "new",
                "score": 78,
                "confidence": 0.92,
                "review_notes": [],
                "duplicate_of": None,
            }
        ]

    def triage_update(self, item_id, **kwargs):
        return {
            "id": item_id,
            "review_state": kwargs["state"],
            "review_notes": [{"note": kwargs.get("note", ""), "author": kwargs.get("actor", "cli")}],
            "duplicate_of": kwargs.get("duplicate_of"),
        }

    def triage_note(self, item_id, **kwargs):
        return {
            "id": item_id,
            "review_notes": [{"note": kwargs["note"], "author": kwargs.get("author", "cli")}],
            "review_state": "new",
        }

    def triage_stats(self, **kwargs):
        return {
            "total": 4,
            "open_count": 2,
            "closed_count": 2,
            "processed_count": 2,
            "note_count": 3,
            "states": {
                "new": 1,
                "triaged": 0,
                "verified": 1,
                "duplicate": 1,
                "ignored": 0,
                "escalated": 1,
            },
        }

    def triage_explain(self, item_id, **kwargs):
        return {
            "item": {
                "id": item_id,
                "title": "OpenAI launch post",
            },
            "suggested_primary_id": item_id,
            "candidate_count": 1,
            "returned_count": 1,
            "candidates": [
                {
                    "id": "item-2",
                    "title": "OpenAI launch recap",
                    "review_state": "triaged",
                    "similarity": 0.84,
                    "signals": ["same_domain", "title_overlap"],
                }
            ],
        }

    def story_build(self, **kwargs):
        return {
            "stats": {
                "stories_built": 1,
                "stories_saved": 1,
            },
            "stories": [
                {
                    "id": "story-openai-launch",
                    "title": "OpenAI Launch Story",
                    "item_count": 2,
                    "source_count": 2,
                    "score": 82.0,
                    "status": "active",
                }
            ],
        }

    def list_stories(self, **kwargs):
        return [
            {
                "id": "story-openai-launch",
                "title": "OpenAI Launch Story",
                "item_count": 2,
                "source_count": 2,
                "score": 82.0,
                "status": "active",
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
                "status": "active",
            },
            "nodes": [
                {"id": identifier, "label": "OpenAI Launch Story", "kind": "story"},
                {"id": "entity:openai", "label": "OpenAI", "kind": "entity", "entity_type": "ORG", "in_story_source_count": 2},
                {"id": "entity:chatgpt", "label": "ChatGPT", "kind": "entity", "entity_type": "PRODUCT", "in_story_source_count": 1},
            ],
            "edges": [
                {"source": identifier, "target": "entity:openai", "relation_type": "MENTIONED_IN_STORY", "kind": "story_entity"},
                {"source": "entity:openai", "target": "entity:chatgpt", "relation_type": "BUILT", "kind": "entity_relation"},
            ],
            "entity_count": 2,
            "relation_count": 1,
            "edge_count": 2,
        }

    def export_story(self, identifier, **kwargs):
        if kwargs.get("output_format") == "markdown":
            return "# OpenAI Launch Story\n\n## Timeline"
        return '{\n  "id": "story-openai-launch"\n}'


def test_trending_prints_fallback_context(monkeypatch, capsys):
    monkeypatch.setattr(cli, "DataPulseReader", lambda: _TrendingReader())
    monkeypatch.setattr(
        sys,
        "argv",
        ["datapulse", "--trending", "china", "--trending-limit", "1"],
    )

    cli.main()
    out = capsys.readouterr().out

    assert "Trending Topics on X (worldwide)" in out
    assert "Requested location: china" in out
    assert "Fallback reason: 404 Client Error: Not Found" in out


def test_trending_empty_prints_reason(monkeypatch, capsys):
    monkeypatch.setattr(cli, "DataPulseReader", lambda: _TrendingEmptyReader())
    monkeypatch.setattr(
        sys,
        "argv",
        ["datapulse", "--trending", "us", "--trending-limit", "20"],
    )

    cli.main()
    out = capsys.readouterr().out

    assert "No trending data found" in out
    assert "Requested location: us" in out
    assert "Fallback reason: Low-signal trending snapshot" in out


def test_search_empty_with_zero_threshold_message(monkeypatch, capsys):
    monkeypatch.setattr(cli, "DataPulseReader", lambda: _SearchReader(results=[]))
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "datapulse",
            "--search",
            "data governance",
            "--min-confidence",
            "0.0",
        ],
    )

    cli.main()
    out = capsys.readouterr().out

    assert "No search results returned" in out


def test_search_empty_with_positive_threshold_message(monkeypatch, capsys):
    monkeypatch.setattr(cli, "DataPulseReader", lambda: _SearchReader(results=[]))
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "datapulse",
            "--search",
            "data governance",
            "--min-confidence",
            "0.5",
        ],
    )

    cli.main()
    out = capsys.readouterr().out

    assert "No search results above confidence threshold" in out


def test_watch_create_prints_summary(monkeypatch, capsys):
    monkeypatch.setattr(cli, "DataPulseReader", lambda: _WatchReader())
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "datapulse",
            "--watch-create",
            "--watch-name",
            "AI Radar",
            "--watch-query",
            "OpenAI agents",
            "--watch-platform",
            "twitter",
        ],
    )

    cli.main()
    out = capsys.readouterr().out

    assert "created watch mission: ai-radar" in out
    assert "name: AI Radar" in out
    assert "platforms: twitter" in out


def test_watch_create_passes_rich_alert_rule(monkeypatch, capsys):
    captured: dict[str, object] = {}

    class _CaptureWatchReader(_WatchReader):
        def create_watch(self, **kwargs):
            captured.update(kwargs)
            return super().create_watch(**kwargs)

    monkeypatch.setattr(cli, "DataPulseReader", lambda: _CaptureWatchReader())
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "datapulse",
            "--watch-create",
            "--watch-name",
            "Launch Radar",
            "--watch-query",
            "OpenAI launch",
            "--watch-alert-route",
            "ops-webhook",
            "--watch-alert-keyword",
            "launch",
            "--watch-alert-exclude-keyword",
            "rumor",
            "--watch-alert-required-tag",
            "watch",
            "--watch-alert-domain",
            "openai.com",
            "--watch-alert-max-age-minutes",
            "60",
        ],
    )

    cli.main()
    capsys.readouterr()

    alert_rules = captured["alert_rules"]
    assert isinstance(alert_rules, list)
    assert alert_rules[0]["routes"] == ["ops-webhook"]
    assert alert_rules[0]["keyword_any"] == ["launch"]
    assert alert_rules[0]["exclude_keywords"] == ["rumor"]
    assert alert_rules[0]["required_tags"] == ["watch"]
    assert alert_rules[0]["domains"] == ["openai.com"]
    assert alert_rules[0]["max_age_minutes"] == 60


def test_watch_list_prints_rows(monkeypatch, capsys):
    monkeypatch.setattr(cli, "DataPulseReader", lambda: _WatchReader())
    monkeypatch.setattr(sys, "argv", ["datapulse", "--watch-list", "--watch-include-disabled"])

    cli.main()
    out = capsys.readouterr().out

    assert "Watch missions: 2" in out
    assert "ai-radar: AI Radar | enabled" in out
    assert "schedule=hourly | due=yes | alerts=1" in out
    assert "intent: Track AI launches that could change competitive posture." in out
    assert "freshness: same day review | max_age<=24h" in out
    assert "old-watch: Old Watch | disabled" in out


def test_watch_run_prints_results(monkeypatch, capsys):
    monkeypatch.setattr(cli, "DataPulseReader", lambda: _WatchReader())
    monkeypatch.setattr(sys, "argv", ["datapulse", "--watch-run", "ai-radar"])

    cli.main()
    out = capsys.readouterr().out

    assert "Watch mission: AI Radar (ai-radar)" in out
    assert "Results: 1" in out
    assert "Alerts: 1" in out
    assert "OpenAI agents result" in out


def test_watch_run_due_prints_summary(monkeypatch, capsys):
    monkeypatch.setattr(cli, "DataPulseReader", lambda: _WatchReader())
    monkeypatch.setattr(sys, "argv", ["datapulse", "--watch-run-due"])

    cli.main()
    out = capsys.readouterr().out

    assert "Due watch missions: 1" in out
    assert "Executed: 1" in out
    assert "- AI Radar [success] items=2 attempts=1 alerts=1" in out


def test_watch_show_prints_cockpit_detail(monkeypatch, capsys):
    monkeypatch.setattr(cli, "DataPulseReader", lambda: _WatchReader())
    monkeypatch.setattr(sys, "argv", ["datapulse", "--watch-show", "ai-radar"])

    cli.main()
    out = capsys.readouterr().out

    assert "id: ai-radar" in out
    assert "next_run_at: 2026-03-06T01:00:00+00:00" in out
    assert "mission_intent:" in out
    assert "demand_intent: Track AI launches that could change competitive posture." in out
    assert "scope_entities: OpenAI" in out
    assert "freshness: same day review | max_age<=24h" in out
    assert "coverage_targets: official blog, developer reaction" in out
    assert "run_total: 2" in out
    assert "recent_runs:" in out
    assert "temporary upstream failure" in out
    assert "retry_advice:" in out
    assert "retry_command: datapulse --watch-run ai-radar" in out
    assert "setup_hint: set API key" in out
    assert "recent_alerts:" in out
    assert "recent_results:" in out
    assert "result_filters:" in out
    assert "states: new(1)" in out
    assert "timeline_strip:" in out
    assert "alert | alert: threshold" in out
    assert "OpenAI agents result" in out


def test_watch_results_prints_rows(monkeypatch, capsys):
    monkeypatch.setattr(cli, "DataPulseReader", lambda: _WatchReader())
    monkeypatch.setattr(sys, "argv", ["datapulse", "--watch-results", "ai-radar"])

    cli.main()
    out = capsys.readouterr().out

    assert "Watch results: 1" in out
    assert "item-1: score=73 | confidence=0.910 | state=new | source=search" in out
    assert "OpenAI agents result" in out


def test_watch_alert_set_replaces_rules(monkeypatch, capsys):
    monkeypatch.setattr(cli, "DataPulseReader", lambda: _WatchReader())
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "datapulse",
            "--watch-alert-set",
            "ai-radar",
            "--watch-alert-route",
            "ops-webhook",
            "--watch-alert-keyword",
            "launch",
            "--watch-alert-domain",
            "openai.com",
            "--watch-alert-min-score",
            "70",
        ],
    )

    cli.main()
    out = capsys.readouterr().out

    assert "updated alert rules for: ai-radar" in out
    assert "alert_rules: 1" in out
    assert "id: ai-radar" in out


def test_watch_alert_clear_removes_rules(monkeypatch, capsys):
    monkeypatch.setattr(cli, "DataPulseReader", lambda: _WatchReader())
    monkeypatch.setattr(sys, "argv", ["datapulse", "--watch-alert-clear", "ai-radar"])

    cli.main()
    out = capsys.readouterr().out

    assert "cleared alert rules for: ai-radar" in out
    assert "alert_rules: 0" in out


def test_alert_list_prints_rows(monkeypatch, capsys):
    monkeypatch.setattr(cli, "DataPulseReader", lambda: _WatchReader())
    monkeypatch.setattr(sys, "argv", ["datapulse", "--alert-list"])

    cli.main()
    out = capsys.readouterr().out

    assert "Alert events: 1" in out
    assert "alert-1: AI Radar | threshold | channels=json,markdown" in out


def test_alert_route_list_prints_rows(monkeypatch, capsys):
    monkeypatch.setattr(cli, "DataPulseReader", lambda: _WatchReader())
    monkeypatch.setattr(sys, "argv", ["datapulse", "--alert-route-list"])

    cli.main()
    out = capsys.readouterr().out

    assert "Alert routes: 1" in out
    assert "ops-webhook: channel=webhook" in out


def test_alert_route_health_prints_rows(monkeypatch, capsys):
    monkeypatch.setattr(cli, "DataPulseReader", lambda: _WatchReader())
    monkeypatch.setattr(sys, "argv", ["datapulse", "--alert-route-health"])

    cli.main()
    out = capsys.readouterr().out

    assert "Alert route health: 1" in out
    assert "ops-webhook: channel=webhook | status=degraded | events=2 | delivered=1 | failed=1" in out
    assert "success_rate: 50.0%" in out
    assert "last_error: webhook_url is required" in out


def test_watch_daemon_once_prints_summary(monkeypatch, capsys):
    monkeypatch.setattr(cli, "DataPulseReader", lambda: _WatchReader())
    monkeypatch.setattr(sys, "argv", ["datapulse", "--watch-daemon", "--watch-daemon-once"])

    cli.main()
    out = capsys.readouterr().out

    assert "Watch daemon cycles: 1" in out
    assert "Last due count: 1" in out


def test_watch_status_prints_metrics(monkeypatch, capsys):
    monkeypatch.setattr(cli, "DataPulseReader", lambda: _WatchReader())
    monkeypatch.setattr(sys, "argv", ["datapulse", "--watch-status"])

    cli.main()
    out = capsys.readouterr().out

    assert "state: idle" in out
    assert "cycles_total: 3" in out
    assert "alerts_total: 1" in out


def test_ops_overview_prints_summary(monkeypatch, capsys):
    monkeypatch.setattr(cli, "DataPulseReader", lambda: _WatchReader())
    monkeypatch.setattr(sys, "argv", ["datapulse", "--ops-overview"])

    cli.main()
    out = capsys.readouterr().out

    assert "collector_health:" in out
    assert "warn: 1" in out
    assert "error: 1" in out
    assert "tier_2 | total=1 | ok=0 | warn=0 | error=1" in out
    assert "watch_metrics:" in out
    assert "success_rate: 50.0%" in out
    assert "watch_health:" in out
    assert "degraded: 1" in out
    assert "ai-radar | status=degraded | enabled=True | due=True | rate=50.0%" in out
    assert "telegram | tier=tier_2 | status=error | available=False" in out
    assert "route_health:" in out
    assert "ops-webhook | channel=webhook | status=degraded | rate=50.0%" in out
    assert "timeline:" in out
    assert "ops-webhook | failed | mission=AI Radar" in out
    assert "recent_failures:" in out
    assert "temporary failure" in out


def test_ops_scorecard_prints_json(monkeypatch, capsys):
    monkeypatch.setattr(cli, "DataPulseReader", lambda: _WatchReader())
    monkeypatch.setattr(sys, "argv", ["datapulse", "--ops-scorecard"])

    cli.main()
    out = capsys.readouterr().out

    assert '"signal_count": 5' in out
    assert '"converted_item_count": 1' in out


def test_ai_surface_precheck_prints_json(monkeypatch, capsys):
    monkeypatch.setattr(cli, "DataPulseReader", lambda: _WatchReader())
    monkeypatch.setattr(sys, "argv", ["datapulse", "--ai-surface-precheck", "mission_suggest", "--ai-mode", "review"])

    cli.main()
    out = capsys.readouterr().out

    assert '"surface": "mission_suggest"' in out
    assert '"mode": "review"' in out
    assert '"mode_status": "admitted"' in out


def test_ai_surface_precheck_accepts_report_draft(monkeypatch, capsys):
    monkeypatch.setattr(cli, "DataPulseReader", lambda: _WatchReader())
    monkeypatch.setattr(sys, "argv", ["datapulse", "--ai-surface-precheck", "report_draft", "--ai-mode", "review"])

    cli.main()
    out = capsys.readouterr().out

    assert '"surface": "report_draft"' in out
    assert '"mode": "review"' in out
    assert '"alias": "report_draft-alias"' in out


def test_ai_surface_precheck_accepts_delivery_summary(monkeypatch, capsys):
    monkeypatch.setattr(cli, "DataPulseReader", lambda: _WatchReader())
    monkeypatch.setattr(sys, "argv", ["datapulse", "--ai-surface-precheck", "delivery_summary", "--ai-mode", "review"])

    cli.main()
    out = capsys.readouterr().out

    assert '"surface": "delivery_summary"' in out
    assert '"mode": "review"' in out
    assert '"alias": "delivery_summary-alias"' in out


def test_ai_mission_suggest_prints_projection(monkeypatch, capsys):
    monkeypatch.setattr(cli, "DataPulseReader", lambda: _WatchReader())
    monkeypatch.setattr(sys, "argv", ["datapulse", "--ai-mission-suggest", "ai-radar"])

    cli.main()
    out = capsys.readouterr().out

    assert '"surface": "mission_suggest"' in out
    assert '"contract_id": "datapulse_ai_watch_suggestion.v1"' in out
    assert '"request_id": "mission-123"' in out


def test_ai_triage_assist_prints_projection(monkeypatch, capsys):
    monkeypatch.setattr(cli, "DataPulseReader", lambda: _WatchReader())
    monkeypatch.setattr(sys, "argv", ["datapulse", "--ai-triage-assist", "item-1", "--triage-explain-limit", "3"])

    cli.main()
    out = capsys.readouterr().out

    assert '"surface": "triage_assist"' in out
    assert '"contract_id": "datapulse_ai_triage_explain.v1"' in out
    assert '"returned_count": 1' in out


def test_ai_claim_draft_prints_projection(monkeypatch, capsys):
    monkeypatch.setattr(cli, "DataPulseReader", lambda: _WatchReader())
    monkeypatch.setattr(sys, "argv", ["datapulse", "--ai-claim-draft", "story-openai-launch", "--ai-brief-id", "brief-1"])

    cli.main()
    out = capsys.readouterr().out

    assert '"surface": "claim_draft"' in out
    assert '"contract_id": "datapulse_ai_claim_draft.v1"' in out
    assert '"statement": "Demand remains elevated."' in out


def test_ai_delivery_summary_prints_projection(monkeypatch, capsys):
    monkeypatch.setattr(cli, "DataPulseReader", lambda: _WatchReader())
    monkeypatch.setattr(sys, "argv", ["datapulse", "--ai-delivery-summary", "alert-1", "--ai-mode", "review"])

    cli.main()
    out = capsys.readouterr().out

    assert '"surface": "delivery_summary"' in out
    assert '"mode": "review"' in out
    assert '"contract_id": "datapulse_ai_delivery_summary.v1"' in out
    assert '"request_id": "delivery-123"' in out


def test_ai_report_draft_prints_fail_closed_projection(monkeypatch, capsys):
    monkeypatch.setattr(cli, "DataPulseReader", lambda: _WatchReader())
    monkeypatch.setattr(sys, "argv", ["datapulse", "--ai-report-draft", "report-runtime-closure", "--ai-mode", "review"])

    cli.main()
    out = capsys.readouterr().out

    assert '"surface": "report_draft"' in out
    assert '"mode": "review"' in out
    assert '"served_by_alias": "dp.report.draft"' in out
    assert '"request_id": "report-123"' in out
    assert '"schema_valid": false' in out


def test_triage_list_prints_rows(monkeypatch, capsys):
    monkeypatch.setattr(cli, "DataPulseReader", lambda: _WatchReader())
    monkeypatch.setattr(sys, "argv", ["datapulse", "--triage-list"])

    cli.main()
    out = capsys.readouterr().out

    assert "Triage queue: 1" in out
    assert "item-1: new | score=78 | confidence=0.920 | notes=0" in out


def test_triage_update_prints_summary(monkeypatch, capsys):
    monkeypatch.setattr(cli, "DataPulseReader", lambda: _WatchReader())
    monkeypatch.setattr(
        sys,
        "argv",
        ["datapulse", "--triage-update", "item-1", "--triage-state", "verified", "--triage-note-text", "confirmed"],
    )

    cli.main()
    out = capsys.readouterr().out

    assert "triage updated: item-1 -> verified" in out


def test_triage_note_prints_summary(monkeypatch, capsys):
    monkeypatch.setattr(cli, "DataPulseReader", lambda: _WatchReader())
    monkeypatch.setattr(
        sys,
        "argv",
        ["datapulse", "--triage-note", "item-1", "--triage-note-text", "needs follow-up"],
    )

    cli.main()
    out = capsys.readouterr().out

    assert "triage note added: item-1" in out


def test_triage_stats_prints_counts(monkeypatch, capsys):
    monkeypatch.setattr(cli, "DataPulseReader", lambda: _WatchReader())
    monkeypatch.setattr(sys, "argv", ["datapulse", "--triage-stats"])

    cli.main()
    out = capsys.readouterr().out

    assert "total: 4" in out
    assert "open_count: 2" in out
    assert "verified: 1" in out


def test_triage_explain_prints_candidates(monkeypatch, capsys):
    monkeypatch.setattr(cli, "DataPulseReader", lambda: _WatchReader())
    monkeypatch.setattr(sys, "argv", ["datapulse", "--triage-explain", "item-1"])

    cli.main()
    out = capsys.readouterr().out

    assert "item: item-1" in out
    assert "suggested_primary_id: item-1" in out
    assert "item-2: similarity=0.840 | state=triaged | signals=same_domain,title_overlap" in out


def test_story_build_prints_summary(monkeypatch, capsys):
    monkeypatch.setattr(cli, "DataPulseReader", lambda: _WatchReader())
    monkeypatch.setattr(sys, "argv", ["datapulse", "--story-build"])

    cli.main()
    out = capsys.readouterr().out

    assert "Stories built: 1" in out
    assert "story-openai-launch: items=2 | sources=2 | score=82.0 | status=active" in out


def test_story_list_and_export(monkeypatch, capsys):
    monkeypatch.setattr(cli, "DataPulseReader", lambda: _WatchReader())
    monkeypatch.setattr(sys, "argv", ["datapulse", "--story-list"])

    cli.main()
    out = capsys.readouterr().out
    assert "📚 Stories: 1" in out

    monkeypatch.setattr(sys, "argv", ["datapulse", "--story-export", "story-openai-launch", "--story-format", "markdown"])
    cli.main()
    out = capsys.readouterr().out
    assert "# OpenAI Launch Story" in out

    monkeypatch.setattr(sys, "argv", ["datapulse", "--story-graph", "story-openai-launch"])
    cli.main()
    out = capsys.readouterr().out
    assert "story: story-openai-launch" in out
    assert "relation_count: 1" in out
    assert "OpenAI | type=ORG" in out
    assert "entity:openai -> entity:chatgpt | BUILT | kind=entity_relation" in out


def test_story_update_prints_payload(monkeypatch, capsys):
    monkeypatch.setattr(cli, "DataPulseReader", lambda: _WatchReader())
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "datapulse",
            "--story-update",
            "story-openai-launch",
            "--story-title",
            "OpenAI Launch Watch",
            "--story-summary",
            "Condensed launch summary",
            "--story-status",
            "monitoring",
        ],
    )

    cli.main()
    out = capsys.readouterr().out

    assert "✅ story updated: story-openai-launch" in out
    assert '"title": "OpenAI Launch Watch"' in out
    assert '"status": "monitoring"' in out


def test_skill_contract_lists_watch_status_and_alert_envs(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["datapulse", "--skill-contract"])

    cli.main()
    out = capsys.readouterr().out

    assert "watch_status" in out
    assert "triage_list" in out
    assert "triage_explain" in out
    assert "story_build" in out
    assert "story_graph" in out
    assert "story_update" in out
    assert "watch_show" in out
    assert "watch_set_alert_rules" in out
    assert "watch_results" in out
    assert "alert_route_health" in out
    assert "ops_overview" in out
    assert "--triage-list" in out
    assert "--triage-explain" in out
    assert "--story-build" in out
    assert "--story-graph" in out
    assert "--story-update" in out
    assert "--watch-alert-set" in out
    assert "--watch-alert-clear" in out
    assert "--watch-show" in out
    assert "--watch-results" in out
    assert "--alert-route-health" in out
    assert "--ops-overview" in out
    assert "DATAPULSE_WATCH_STATUS_PATH" in out
    assert "DATAPULSE_STORIES_PATH" in out
    assert "DATAPULSE_WATCH_STATUS_HTML" in out
    assert "DATAPULSE_ALERT_ROUTING_PATH" in out
    assert "DATAPULSE_ALERT_WEBHOOK_URL" in out
    assert "DATAPULSE_FEISHU_WEBHOOK_URL" in out
    assert "DATAPULSE_TELEGRAM_BOT_TOKEN" in out
