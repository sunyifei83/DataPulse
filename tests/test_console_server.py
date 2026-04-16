"""Tests for the G0 browser console API."""

from __future__ import annotations

import json
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path

from fastapi.testclient import TestClient

from datapulse.console_api_client import render_console_api_client_script
from datapulse.console_client import render_console_client_script
from datapulse.console_server import CONSOLE_TITLE, create_app
from datapulse.core.alerts import AlertEvent
from datapulse.core.models import DataPulseItem, SourceType
from datapulse.core.story import Story, StoryEvidence
from datapulse.core.watchlist import MissionRun
from datapulse.reader import DataPulseReader


class _ConsoleReader:
    def __init__(self):
        self.digest_profile = {
            "language": "en",
            "timezone": "UTC",
            "frequency": "@daily",
            "default_delivery_target": {"kind": "route", "ref": "ops-webhook"},
        }

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
            "research_projection": {
                "source_plan": {
                    "summary": "Research should prefer qnaigc, tavily; focus on twitter; bound sites to openai.com.",
                    "provider_hints": ["qnaigc", "tavily"],
                    "platforms": ["twitter"],
                    "sites": ["openai.com"],
                    "time_range": "week",
                    "deep": False,
                    "news": True,
                },
                "coverage_gap": {
                    "status": "watch",
                    "summary": "Watch research coverage has 1 operator-visible gap signal.",
                    "reasons": ["Named coverage targets have not been observed in persisted watch output yet."],
                    "operator_action": "tighten_watch_scope",
                },
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

    def update_watch(self, identifier, **kwargs):
        if identifier != "launch-ops":
            return None
        payload = self.show_watch(identifier)
        for key, value in kwargs.items():
            if value is not None:
                payload[key] = value
        if kwargs.get("platforms") is not None:
            payload["platforms"] = kwargs["platforms"]
        if kwargs.get("alert_rules") is not None:
            payload["alert_rules"] = kwargs["alert_rules"]
            payload["alert_rule_count"] = len(kwargs["alert_rules"])
        return payload

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
                "research_projection": {
                    "coverage_gap": {
                        "status": "review_required",
                        "summary": "Alert delivery has 1 operator-visible coverage gap signal.",
                        "reasons": ["One or more delivery routes are degraded or missing."],
                        "operator_action": "review_delivery_and_evidence",
                    }
                },
            }
        ]

    def list_alert_routes(self):
        return [
            {
                "name": "ops-webhook",
                "channel": "webhook",
                "description": "Primary ops webhook",
                "webhook_url": "https://hooks.example.com/ops",
            }
        ]

    def create_alert_route(self, **payload):
        return {
            "name": payload["name"],
            "channel": payload["channel"],
            "description": payload.get("description", ""),
            "webhook_url": payload.get("webhook_url", ""),
        }

    def update_alert_route(self, identifier, **payload):
        if identifier != "ops-webhook":
            return None
        route = self.list_alert_routes()[0]
        route.update(payload)
        route["name"] = identifier
        return route

    def delete_alert_route(self, identifier):
        if identifier != "ops-webhook":
            return None
        return self.list_alert_routes()[0]

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

    def governance_scorecard_snapshot(self):
        return {
            "generated_at": "2026-03-06T00:00:30+00:00",
            "mission_scope": {"total": 2, "enabled": 1, "disabled": 1, "items": 2, "stories": 1},
            "signals": {
                "coverage": {
                    "id": "coverage",
                    "label": "Coverage",
                    "status": "ok",
                    "value": 1.0,
                    "unit": "ratio",
                    "display": "3/3 declared touchpoints observed",
                    "detail": "Matches enabled mission platforms, sites, and coverage_targets against persisted watch results.",
                    "expected_targets_total": 3,
                    "covered_targets_total": 3,
                },
                "freshness": {
                    "id": "freshness",
                    "label": "Freshness",
                    "status": "watch",
                    "value": 0.5,
                    "unit": "ratio",
                    "display": "1/2 SLA-backed missions are fresh",
                    "detail": "Uses mission_intent.freshness_max_age_hours and each mission's latest persisted result timestamp.",
                    "missions_with_sla": 2,
                    "fresh_missions": 1,
                },
                "alert_yield": {
                    "id": "alert_yield",
                    "label": "Alert Yield",
                    "status": "ok",
                    "value": 0.5,
                    "unit": "alerts_per_successful_run",
                    "display": "1 alerts across 2 successful runs",
                    "detail": "Compares persisted AlertEvent rows against successful MissionRun records for enabled missions.",
                    "alert_count": 1,
                    "successful_runs": 2,
                    "alerting_missions": 1,
                },
                "triage_throughput": {
                    "id": "triage_throughput",
                    "label": "Triage Throughput",
                    "status": "ok",
                    "value": 0.5,
                    "unit": "acted_item_ratio",
                    "display": "1/2 items moved beyond new",
                    "detail": "Measures how much of the persisted inbox has received analyst triage state changes or notes.",
                    "total_items": 2,
                    "acted_on_items": 1,
                    "open_items": 1,
                    "note_count": 1,
                },
                "story_conversion": {
                    "id": "story_conversion",
                    "label": "Story Conversion",
                    "status": "ok",
                    "value": 1.0,
                    "unit": "conversion_ratio",
                    "display": "1/1 triaged items referenced by stories",
                    "detail": "Tracks how much reviewed evidence is already represented in persisted story objects.",
                    "story_count": 1,
                    "ready_story_count": 1,
                    "eligible_item_count": 1,
                    "converted_item_count": 1,
                },
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
        if identifier != "launch-ops":
            return None
        return {
            "surface": "mission_suggest",
            "mode": mode,
            "subject": {"kind": "WatchMission", "id": identifier},
            "precheck": self.ai_surface_precheck("mission_suggest", mode=mode),
            "output": {
                "contract_id": "datapulse_ai_watch_suggestion.v1",
                "payload": {
                    "summary": "Mission `Launch Ops` has 2 persisted result items and run readiness `ready`.",
                    "proposed_query": "OpenAI launch",
                    "research_projection": {
                        "source_plan": {
                            "summary": "Research should prefer qnaigc, tavily; focus on twitter; bound sites to openai.com.",
                            "provider_hints": ["qnaigc", "tavily"],
                            "platforms": ["twitter"],
                            "sites": ["openai.com"],
                            "time_range": "week",
                            "deep": False,
                            "news": True,
                        },
                        "coverage_gap": {
                            "status": "watch",
                            "summary": "Watch research coverage has 1 operator-visible gap signal.",
                            "reasons": ["Named coverage targets have not been observed in persisted watch output yet."],
                            "operator_action": "tighten_watch_scope",
                        },
                    },
                },
            },
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
            "output": {
                "contract_id": "datapulse_ai_triage_explain.v1",
                "payload": {
                    "item": {"id": item_id, "title": "OpenAI launch post"},
                    "candidate_count": 1,
                    "returned_count": min(limit, 1),
                },
            },
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
            "output": {
                "contract_id": "datapulse_ai_claim_draft.v1",
                "payload": {
                    "summary": "Draft evidence-bound claim cards without writing final report state.",
                    "claim_cards": [{"id": "claim-1", "statement": "Demand remains elevated."}],
                    "research_projection": {
                        "source_plan": {
                            "summary": "Research should keep provider coverage on tavily; maintain site coverage across example.com.",
                            "provider_hints": ["tavily"],
                            "platforms": [],
                            "sites": ["example.com"],
                            "time_range": "",
                            "deep": True,
                            "news": False,
                        },
                        "coverage_gap": {
                            "status": "watch",
                            "summary": "Story evidence coverage has 1 review signal before claim drafting.",
                            "reasons": ["No story evidence row is marked cross-validated."],
                            "operator_action": "monitor_source_diversity",
                        },
                    },
                },
            },
            "runtime_facts": {"status": "fallback_used", "request_id": "claim-123"},
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
                    "summary": "Alert `console-threshold` is `healthy` across 1 delivery target.",
                    "overall_status": "healthy",
                    "research_projection": {
                        "source_plan": {
                            "summary": "Alert delivery should stay within the originating evidence chain.",
                            "provider_hints": [],
                            "platforms": [],
                            "sites": ["example.com"],
                            "time_range": "",
                            "deep": False,
                            "news": False,
                        },
                        "coverage_gap": {
                            "status": "review_required",
                            "summary": "Alert delivery has 1 operator-visible coverage gap signal.",
                            "reasons": ["One or more delivery routes are degraded or missing."],
                            "operator_action": "review_delivery_and_evidence",
                        },
                    },
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
            "governance_scorecard": self.governance_scorecard_snapshot(),
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

    def triage_delete(self, item_id):
        return {"id": item_id, "deleted": True}

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
                "research_projection": {
                    "source_plan": {
                        "summary": "Research should keep provider coverage on tavily; maintain site coverage across example.com.",
                        "provider_hints": ["tavily"],
                        "platforms": [],
                        "sites": ["example.com"],
                        "time_range": "",
                        "deep": True,
                        "news": False,
                    },
                    "coverage_gap": {
                        "status": "watch",
                        "summary": "Story evidence coverage has 1 review signal before claim drafting.",
                        "reasons": ["No story evidence row is marked cross-validated."],
                        "operator_action": "monitor_source_diversity",
                    },
                },
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

    def create_story(self, **payload):
        story = self.list_stories()[0]
        story.update(
            {
                "id": payload.get("id", "story-manual-brief"),
                "title": payload["title"],
                "summary": payload.get("summary", ""),
                "status": payload.get("status", "active"),
                "item_count": payload.get("item_count", 0),
                "source_count": payload.get("source_count", 0),
                "primary_evidence": payload.get("primary_evidence", []),
                "secondary_evidence": payload.get("secondary_evidence", []),
                "timeline": payload.get("timeline", []),
                "contradictions": payload.get("contradictions", []),
                "entities": payload.get("entities", []),
                "source_names": payload.get("source_names", []),
            }
        )
        return story

    def create_story_from_triage(self, **payload):
        story = self.list_stories()[0]
        item_ids = payload.get("item_ids") or []
        story.update(
            {
                "id": "story-triage-seed",
                "title": payload.get("title") or "Triage Story Seed",
                "summary": payload.get("summary") or "Seeded from triage queue.",
                "status": payload.get("status", "monitoring"),
                "item_count": len(item_ids) or 1,
                "primary_item_id": item_ids[0] if item_ids else "item-1",
            }
        )
        return story

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

    def delete_story(self, identifier):
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

    def list_report_briefs(self, limit=20, status=None):
        rows = [
            {
                "id": "brief-openai",
                "title": "OpenAI Report Brief",
                "audience": "internal",
                "objective": "Track launch evidence and market reaction",
                "status": "draft",
            }
        ]
        if status:
            rows = [row for row in rows if row.get("status") == status]
        return rows[:limit]

    def create_report_brief(self, **payload):
        row = self.list_report_briefs(limit=1)[0].copy()
        row["id"] = payload.get("id", "brief-manual")
        row.update(payload)
        return row

    def show_report_brief(self, identifier):
        if identifier != "brief-openai":
            return None
        return self.list_report_briefs(limit=1)[0].copy()

    def update_report_brief(self, identifier, **payload):
        if identifier != "brief-openai":
            return None
        row = self.show_report_brief(identifier)
        row.update(payload)
        return row

    def list_claim_cards(self, limit=20, status=None):
        rows = [
            {
                "id": "claim-openai-trend",
                "brief_id": "brief-openai",
                "title": "OpenAI launch claim",
                "statement": "Demand signals remain elevated after the OpenAI launch window.",
                "rationale": "Cross-source evidence continues to cluster around launch, ecosystem response, and analyst follow-up.",
                "confidence": 0.91,
                "status": "reviewed",
                "source_item_ids": ["item-1"],
                "citation_bundle_ids": ["bundle-openai"],
            }
        ]
        if status:
            rows = [row for row in rows if row.get("status") == status]
        return rows[:limit]

    def create_claim_card(self, **payload):
        row = self.list_claim_cards(limit=1)[0].copy()
        row["id"] = payload.get("id", "claim-manual")
        row.update(payload)
        return row

    def show_claim_card(self, identifier):
        if identifier != "claim-openai-trend":
            return None
        return self.list_claim_cards(limit=1)[0].copy()

    def update_claim_card(self, identifier, **payload):
        if identifier != "claim-openai-trend":
            return None
        row = self.show_claim_card(identifier)
        row.update(payload)
        return row

    def list_report_sections(self, limit=20, status=None):
        rows = [
            {
                "id": "section-market-context",
                "title": "Market context",
                "report_id": "report-openai-market",
                "position": 1,
                "summary": "Summarize market reaction and evidence-backed adoption signal.",
                "claim_card_ids": ["claim-openai-trend"],
                "status": "draft",
            }
        ]
        if status:
            rows = [row for row in rows if row.get("status") == status]
        return rows[:limit]

    def create_report_section(self, **payload):
        row = self.list_report_sections(limit=1)[0].copy()
        row["id"] = payload.get("id", "section-manual")
        row.update(payload)
        return row

    def show_report_section(self, identifier):
        if identifier != "section-market-context":
            return None
        return self.list_report_sections(limit=1)[0].copy()

    def update_report_section(self, identifier, **payload):
        if identifier != "section-market-context":
            return None
        row = self.show_report_section(identifier)
        row.update(payload)
        return row

    def list_citation_bundles(self, limit=20):
        rows = [
            {
                "id": "bundle-openai",
                "claim_card_id": "claim-openai-trend",
                "label": "OpenAI bundle",
                "source_item_ids": ["item-1"],
                "source_urls": ["https://example.com/openai-launch"],
                "note": "Primary launch coverage bundle.",
            }
        ]
        return rows[:limit]

    def create_citation_bundle(self, **payload):
        row = self.list_citation_bundles(limit=1)[0].copy()
        row["id"] = payload.get("id", "bundle-manual")
        row.update(payload)
        return row

    def show_citation_bundle(self, identifier):
        if identifier != "bundle-openai":
            return None
        return self.list_citation_bundles(limit=1)[0].copy()

    def update_citation_bundle(self, identifier, **payload):
        if identifier != "bundle-openai":
            return None
        row = self.show_citation_bundle(identifier)
        row.update(payload)
        return row

    def list_reports(self, limit=20, status=None):
        rows = [
            {
                "id": "report-openai-market",
                "brief_id": "brief-openai",
                "title": "OpenAI Market Report",
                "status": "draft",
                "audience": "internal",
                "summary": "A persisted report shell for launch-related market tracking.",
                "section_ids": ["section-market-context"],
                "claim_card_ids": ["claim-openai-trend"],
                "citation_bundle_ids": ["bundle-openai"],
                "export_profile_ids": ["profile-brief"],
            }
        ]
        if status:
            rows = [row for row in rows if row.get("status") == status]
        return rows[:limit]

    def create_report(self, **payload):
        row = self.list_reports(limit=1)[0].copy()
        row["id"] = payload.get("id", "report-manual")
        row.update(payload)
        return row

    def show_report(self, identifier):
        if identifier != "report-openai-market":
            return None
        return self.list_reports(limit=1)[0].copy()

    def update_report(self, identifier, **payload):
        if identifier != "report-openai-market":
            return None
        row = self.show_report(identifier)
        row.update(payload)
        return row

    def compose_report(self, identifier, **kwargs):
        if identifier != "report-openai-market":
            return None
        payload = {
            "report": self.show_report(identifier),
            "sections": self.list_report_sections(),
            "claim_cards": self.list_claim_cards(),
            "citation_bundles": self.list_citation_bundles(),
            "quality": {
                "status": "ok",
                "score": 0.96,
                "checks": {
                    "fact_consistency": {"status": "ok"},
                    "coverage": {"status": "ok"},
                },
                "can_export": True,
                "operator_action": "approve",
            },
        }
        if kwargs.get("profile_id"):
            profile = self.show_export_profile(kwargs["profile_id"])
            if profile is None:
                raise ValueError(f"Export profile not found: {kwargs['profile_id']}")
        if kwargs.get("include_sections") is False:
            payload["sections"] = []
        if kwargs.get("include_claim_cards") is False:
            payload["claim_cards"] = []
        if kwargs.get("include_citation_bundles") is False:
            payload["citation_bundles"] = []
        return payload

    def assess_report_quality(self, identifier, **kwargs):
        payload = self.compose_report(identifier, **kwargs)
        if payload is None:
            return None
        return payload.get("quality", {})

    def export_report(self, identifier, **kwargs):
        if identifier != "report-openai-market":
            return None
        output_format = str(kwargs.get("output_format", "json")).strip().lower()
        if output_format == "json":
            return json.dumps(self.compose_report(identifier, **kwargs), ensure_ascii=False, indent=2)
        if output_format in {"md", "markdown"}:
            report = self.show_report(identifier)
            return f"# {report['title']}\\n\\n- id: {report['id']}"
        raise ValueError(f"Unsupported report export format: {output_format}")

    def list_export_profiles(self, limit=20, status=None):
        rows = [
            {
                "id": "profile-brief",
                "report_id": "report-openai-market",
                "name": "Brief export profile",
                "output_format": "markdown",
                "include_sections": True,
                "include_claim_cards": True,
                "include_bundles": True,
                "include_export_profiles": True,
                "status": "active",
            }
        ]
        if status:
            rows = [row for row in rows if row.get("status") == status]
        return rows[:limit]

    def create_export_profile(self, **payload):
        row = self.list_export_profiles(limit=1)[0].copy()
        row["id"] = payload.get("id", "profile-manual")
        row.update(payload)
        return row

    def show_export_profile(self, identifier):
        if identifier != "profile-brief":
            return None
        return self.list_export_profiles(limit=1)[0].copy()

    def update_export_profile(self, identifier, **payload):
        if identifier != "profile-brief":
            return None
        row = self.show_export_profile(identifier)
        row.update(payload)
        return row

    def list_delivery_subscriptions(
        self,
        limit=20,
        status=None,
        subject_kind=None,
        subject_ref=None,
        output_kind=None,
        delivery_mode=None,
        route_name=None,
    ):
        rows = [
            {
                "id": "delivery-subscription-report",
                "subject_kind": "report",
                "subject_ref": "report-openai-market",
                "output_kind": "report_full",
                "delivery_mode": "push",
                "status": "active",
                "route_names": ["ops-webhook"],
                "cursor_or_since": "2026-03-06T00:00:00Z",
            }
        ]
        if status:
            rows = [row for row in rows if row.get("status") == status]
        if subject_kind:
            rows = [row for row in rows if row.get("subject_kind") == subject_kind]
        if subject_ref:
            rows = [row for row in rows if row.get("subject_ref") == subject_ref]
        if output_kind:
            rows = [row for row in rows if row.get("output_kind") == output_kind]
        if delivery_mode:
            rows = [row for row in rows if row.get("delivery_mode") == delivery_mode]
        if route_name:
            rows = [row for row in rows if route_name in row.get("route_names", [])]
        return rows[:limit]

    def create_delivery_subscription(self, **payload):
        row = self.list_delivery_subscriptions(limit=1)[0].copy()
        row["id"] = payload.get("id", "delivery-subscription-manual")
        row.update(payload)
        return row

    def show_delivery_subscription(self, identifier):
        if identifier != "delivery-subscription-report":
            return None
        return self.list_delivery_subscriptions(limit=1)[0].copy()

    def update_delivery_subscription(self, identifier, **payload):
        if identifier != "delivery-subscription-report":
            return None
        row = self.show_delivery_subscription(identifier)
        row.update(payload)
        return row

    def delete_delivery_subscription(self, identifier):
        if identifier != "delivery-subscription-report":
            return None
        return self.show_delivery_subscription(identifier)

    def build_report_delivery_package(self, identifier, profile_id=None):
        if identifier != "delivery-subscription-report":
            raise ValueError(f"Delivery subscription not found: {identifier}")
        return {
            "subscription_id": identifier,
            "subject_kind": "report",
            "subject_ref": "report-openai-market",
            "output_kind": "report_full",
            "profile_id": profile_id or "",
            "package_signature": "pkg-signature-1234",
            "package_id": "report-openai-market:report_full:pkg-signature-1234",
            "payload": {
                "kind": "report_full",
                "report": self.compose_report("report-openai-market", profile_id=profile_id),
            },
        }

    def dispatch_report_delivery(self, identifier, profile_id=None):
        if identifier != "delivery-subscription-report":
            raise ValueError(f"Delivery subscription not found: {identifier}")
        return [
            {
                "id": "delivery-dispatch-1",
                "subscription_id": identifier,
                "subject_kind": "report",
                "subject_ref": "report-openai-market",
                "output_kind": "report_full",
                "route_name": "ops-webhook",
                "route_label": "webhook:ops-webhook",
                "route_channel": "webhook",
                "package_id": "report-openai-market:report_full:pkg-signature-1234",
                "package_signature": "pkg-signature-1234",
                "package_profile_id": profile_id or "",
                "status": "delivered",
                "error": "",
                "attempts": 1,
            }
        ]

    def list_delivery_dispatch_records(
        self,
        limit=20,
        status=None,
        subscription_id=None,
        subject_kind=None,
        subject_ref=None,
        output_kind=None,
        route_name=None,
    ):
        rows = self.dispatch_report_delivery("delivery-subscription-report")
        if status:
            rows = [row for row in rows if row.get("status") == status]
        if subscription_id:
            rows = [row for row in rows if row.get("subscription_id") == subscription_id]
        if subject_kind:
            rows = [row for row in rows if row.get("subject_kind") == subject_kind]
        if subject_ref:
            rows = [row for row in rows if row.get("subject_ref") == subject_ref]
        if output_kind:
            rows = [row for row in rows if row.get("output_kind") == output_kind]
        if route_name:
            rows = [row for row in rows if row.get("route_name") == route_name]
        return rows[:limit]

    def get_digest_profile(self):
        return {
            "schema_version": "digest_profile_projection.v1",
            "profile_path": "/tmp/digest_profile.json",
            "exists": True,
            "onboarding_status": "ready",
            "missing_fields": [],
            "profile": json.loads(json.dumps(self.digest_profile)),
        }

    def update_digest_profile(
        self,
        *,
        language=None,
        timezone=None,
        frequency=None,
        default_delivery_target_kind=None,
        default_delivery_target_ref=None,
    ):
        if language is not None:
            self.digest_profile["language"] = language
        if timezone is not None:
            self.digest_profile["timezone"] = timezone
        if frequency is not None:
            self.digest_profile["frequency"] = frequency
        if default_delivery_target_kind is not None or default_delivery_target_ref is not None:
            current_target = self.digest_profile.get("default_delivery_target", {})
            self.digest_profile["default_delivery_target"] = {
                "kind": default_delivery_target_kind if default_delivery_target_kind is not None else current_target.get("kind", "route"),
                "ref": default_delivery_target_ref if default_delivery_target_ref is not None else current_target.get("ref", ""),
            }
        return self.get_digest_profile()

    def digest_console_projection(self, *, profile="default", limit=12, min_confidence=0.0, since=None):
        return {
            "schema_version": "digest_console_projection.v1",
            "profile": self.get_digest_profile(),
            "prepared_payload": {
                "schema_version": "prepare_digest_payload.v1",
                "generated_at": "2026-03-06T00:00:00Z",
                "content": {
                    "feed_bundle": {
                        "schema_version": "feed_bundle.v1",
                        "generated_at": "2026-03-06T00:00:00Z",
                        "selection": {
                            "profile": profile,
                            "pack_id": None,
                            "source_ids_requested": [],
                            "source_ids_resolved": ["openai-blog"],
                            "since": since,
                            "limit": limit,
                            "min_confidence": min_confidence,
                        },
                        "window": {
                            "start_at": "2026-03-05T00:00:00Z",
                            "end_at": "2026-03-06T00:00:00Z",
                        },
                        "items": [
                            {
                                "id": "item-1",
                                "title": "OpenAI launch post",
                                "url": "https://example.com/openai-launch",
                                "content": "Launch details",
                                "source_name": "OpenAI Blog",
                                "source_type": "generic",
                                "score": 91,
                                "confidence": 0.96,
                                "fetched_at": "2026-03-06T00:00:00Z",
                            },
                            {
                                "id": "item-2",
                                "title": "Operator recap",
                                "url": "https://example.com/operator-recap",
                                "content": "Recap",
                                "source_name": "Ops Notes",
                                "source_type": "generic",
                                "score": 78,
                                "confidence": 0.83,
                                "fetched_at": "2026-03-05T23:40:00Z",
                            },
                        ],
                        "stats": {
                            "items_selected": 2,
                            "sources_selected": 1,
                        },
                        "errors": [],
                    },
                    "digest_payload": {
                        "version": "1.0",
                        "generated_at": "2026-03-06T00:00:00Z",
                        "stats": {
                            "candidates_total": 2,
                            "selected_primary": 1,
                            "selected_secondary": 1,
                        },
                        "primary": [{"id": "item-1", "title": "OpenAI launch post"}],
                        "secondary": [{"id": "item-2", "title": "Operator recap"}],
                    },
                    "delivery_package": {
                        "summary": {
                            "item_count": 2,
                            "high_confidence_count": 1,
                            "factuality_status": "ready",
                            "factuality_effective_status": "ready",
                        }
                    },
                },
                "config": {
                    "profile": profile,
                    "source_ids": ["openai-blog"],
                    "top_n": 3,
                    "secondary_n": 7,
                    "min_confidence": min_confidence,
                    "since": since,
                    "max_per_source": 2,
                    "output_format": "json",
                    "digest_profile": json.loads(json.dumps(self.digest_profile)),
                },
                "prompts": {
                    "prompt_pack": "repo_default",
                    "repo_default_pack": "digest_delivery_default",
                    "render_intent": "digest_delivery",
                    "files": [
                        "/Users/example/DataPulse/prompts/digest_delivery_default/system.md",
                        "/Users/example/.datapulse/prompts/digest_delivery/operator.md",
                    ],
                    "override_order": [
                        "repo_default_pack",
                        "local_prompt_overrides",
                        "per_run_overrides",
                    ],
                    "overrides_applied": ["local_prompt_overrides"],
                },
                "stats": {
                    "feed_bundle": {"items_selected": 2, "sources_selected": 1},
                    "digest": {"selected_primary": 1, "selected_secondary": 1},
                    "delivery_package": {"item_count": 2, "high_confidence_count": 1, "factuality_status": "ready"},
                },
                "errors": [],
            },
        }

    def prepare_digest_payload(self, *, profile="default", limit=12, min_confidence=0.0, since=None):
        return self.digest_console_projection(
            profile=profile,
            limit=limit,
            min_confidence=min_confidence,
            since=since,
        )["prepared_payload"]

    def dispatch_digest_delivery(self, *, prepared_payload=None, route_name=None):
        route_ref = route_name or self.digest_profile["default_delivery_target"]["ref"]
        return [
            {
                "subject_kind": "profile",
                "subject_ref": "default",
                "output_kind": "digest_delivery",
                "route_name": route_ref,
                "route_label": f"webhook:{route_ref}",
                "route_channel": "webhook",
                "package_signature": "digest-signature-1234",
                "status": "delivered",
                "attempts": 1,
                "error": "",
                "governance": {
                    "delivery_diagnostics": {
                        "route_label": f"webhook:{route_ref}",
                        "route_name": route_ref,
                        "channel": "webhook",
                        "attempt_count": 1,
                        "chunk_count": 1,
                        "fallback_used": False,
                        "fallback_reason": "",
                        "attempts": [
                            {
                                "kind": "webhook_post",
                                "status": "delivered",
                                "payload_kind": "digest_delivery",
                            }
                        ],
                    }
                },
            }
        ]


def _client() -> TestClient:
    reader = _ConsoleReader()
    app = create_app(reader_factory=lambda: reader)
    return TestClient(app)


def test_console_index_serves_shell():
    client = _client()
    response = client.get("/")

    assert response.status_code == 200
    assert CONSOLE_TITLE in response.text
    assert "Run Missions, Review Signal, Publish Stories" in response.text
    assert "Draft Mission" in response.text
    assert "Run And Inspect" in response.text
    assert "Triage And Promote" in response.text
    assert "Set Route And Watch Delivery" in response.text
    assert "Workflow Stages" in response.text
    assert "Monitoring owns runs and results, Review owns triage and stories" in response.text
    assert "Current object" in response.text
    assert "Owned output" in response.text
    assert "Next action" in response.text
    assert "Stage-Linked Output Trace" in response.text
    assert "Shared Signal Taxonomy" in response.text
    assert 'data-stage-trace="workflow"' in response.text
    assert "data-trace-stage" in response.text
    assert 'data-shared-signal-taxonomy="true"' in response.text
    assert "data-shared-signal-button" in response.text
    assert "data-shared-signal-panel" in response.text
    assert "data-shared-signal-owner" in response.text
    assert "data-card-action-primary" in response.text
    assert "owner-backed" in response.text
    assert "language-switch" in response.text
    assert "palette-open" in response.text
    assert "section-intake" in response.text
    assert "section-claims" in response.text
    assert "section-report-studio" in response.text
    assert "Primary Workflow Stages" in response.text
    assert "Start -&gt; Monitor -&gt; Review -&gt; Deliver" in response.text
    assert 'data-context-object-step="report"' in response.text
    assert "Claim Composer" in response.text
    assert "Report Studio" in response.text
    assert "Delivery Workspace" in response.text
    assert "review-advanced-shell" in response.text
    assert "delivery-advanced-shell" in response.text
    assert "Advanced Review Surfaces" in response.text
    assert "Advanced Delivery Surfaces" in response.text
    assert "delivery-workspace-shell" in response.text
    assert "Subscription Intake" in response.text
    assert "Report Package Audit" in response.text
    assert "delivery-subscription-form" in response.text
    assert "delivery-package-profile-select" in response.text
    assert 'data-workspace-mode="intake"' in response.text
    assert 'data-workspace-mode="missions"' in response.text
    assert 'data-workspace-mode="review"' in response.text
    assert 'data-workspace-mode="delivery"' in response.text
    assert 'data-workspace-mode="operations"' not in response.text
    assert "/brand/icon" in response.text
    assert "/brand/square" in response.text
    assert "create-watch-form" in response.text
    assert "create-watch-suggestions" in response.text
    assert "mission-name-options-list" in response.text
    assert "route-options-list" in response.text
    assert "confidence-options-list" in response.text
    assert "console-action-history" in response.text
    assert "command-palette" in response.text
    assert "context-summary" in response.text
    assert "context-object-rail" in response.text
    assert '<button class="context-object-step" type="button"' in response.text
    assert "data-context-object-step=\"mission\"" in response.text
    assert "data-context-object-step=\"evidence\"" in response.text
    assert "data-context-object-step=\"story\"" in response.text
    assert "data-context-object-step=\"route\"" in response.text
    assert "data-context-object-id=\"\"" in response.text
    assert "data-context-object-section=\"section-board\"" in response.text
    assert "data-context-object-section=\"section-triage\"" in response.text
    assert "data-context-object-section=\"section-story\"" in response.text
    assert "data-context-object-section=\"section-ops\"" in response.text
    assert "function activateContextObjectRailStep" in response.text
    assert "data-empty-reset=" in response.text
    assert "Boolean(state.ops)" not in response.text
    assert "context-lens-backdrop" in response.text
    assert 'aria-modal="true"' in response.text
    assert "context-lens-close" in response.text
    assert "context-save-form" in response.text
    assert "context-view-dock" in response.text
    assert "intake-section-summary" in response.text
    assert "board-section-summary" in response.text
    assert "cockpit-section-summary" in response.text
    assert "triage-section-summary" in response.text
    assert "story-section-summary" in response.text
    assert "ops-section-summary" in response.text
    assert 'data-fit-text="context-summary"' in response.text
    assert 'data-fit-text="dock-summary"' in response.text
    assert 'data-fit-text="context-object-value"' in response.text
    assert 'data-fit-text="saved-view-chip"' in response.text
    assert 'data-fit-text="triage-mission-chip"' in response.text
    assert 'data-fit-text="claim-url-chip"' in response.text
    assert 'data-fit-text="report-section-claim-chip"' in response.text
    assert "console-overflow-evidence-card" in response.text
    assert "data-console-overflow-summary" in response.text
    assert "data-console-overflow-hotspots" in response.text
    assert 'data-responsive-viewport="desktop"' in response.text
    assert 'data-density-mode="comfortable"' in response.text
    assert 'data-pane-contract="split"' in response.text
    assert 'data-modal-presentation="side-panel"' in response.text
    assert 'data-action-sheet-mode="inline"' in response.text
    assert "data-context-dock-open" in response.text
    assert "data-context-saved-default" in response.text
    assert "function syncContextLensChrome" in response.text
    assert "const shouldShowDock = Boolean(pinnedEntries.length);" in response.text
    assert '<section class="workspace-mode-shell" id="workspace-mode-shell" hidden></section>' in response.text
    assert "Workspace Modes" not in response.text
    assert "function resolveResponsiveInteractionContract" in response.text
    assert "function applyResponsiveInteractionContract" in response.text
    assert "function bindResponsiveInteractionContract" in response.text
    assert "function fitTextToWidth" in response.text
    assert "function applyCanvasTextFit" in response.text
    assert "function scheduleCanvasTextFit" in response.text
    assert "function defaultConsoleOverflowEvidence" in response.text
    assert "function recordConsoleOverflowEvidence" in response.text
    assert "function getConsoleOverflowEvidence" in response.text
    assert "window.getConsoleOverflowEvidence = getConsoleOverflowEvidence" in response.text
    assert 'window.visualViewport.addEventListener("resize", scheduleContractApply' in response.text
    assert 'window.matchMedia(query)' in response.text
    assert 'media.addEventListener("change", scheduleContractApply)' in response.text
    assert "let lastViewportWidth = window.innerWidth" in response.text
    assert "window.setInterval(() => {" in response.text
    assert "function renderCardActionHierarchy" in response.text
    assert "function renderIntakeSectionSummary" in response.text
    assert "function renderBoardSectionSummary" in response.text
    assert "function renderCockpitSectionSummary" in response.text
    assert "function renderTriageSectionSummary" in response.text
    assert "function renderStorySectionSummary" in response.text
    assert "function renderOpsSectionSummary" in response.text
    assert "function setStageFeedback" in response.text
    assert "function renderStageFeedbackCard" in response.text
    assert "data-stage-feedback-kind" in response.text
    assert "data-stage-feedback-stage" in response.text
    assert "section-summary-feedback" in response.text
    assert "data-section-summary-kind" in response.text
    assert "Mission completed with no results" in response.text
    assert "Edit Mission Draft" in response.text
    assert "Story draft still needs a title" in response.text
    assert "Route draft still needs a name" in response.text
    assert "function renderOperatorGuidanceSurface" in response.text
    assert "function buildMissionGuidanceSurface" in response.text
    assert "function buildCockpitGuidanceSurface" in response.text
    assert "function buildTriageGuidanceSurface" in response.text
    assert "function buildStoryGuidanceSurface" in response.text
    assert "function buildRouteGuidanceSurface" in response.text
    assert "data-operator-guidance-surface" in response.text
    assert "mission-guidance-surface" in response.text
    assert "cockpit-guidance-surface" in response.text
    assert "triage-guidance-surface" in response.text
    assert "story-guidance-surface" in response.text
    assert "route-guidance-surface" in response.text
    assert "data-guidance-column" in response.text
    assert "data-guidance-kind" in response.text
    assert "section summary" in response.text
    assert "function getMissionCardActionHierarchy" in response.text
    assert "function getTriageCardActionHierarchy" in response.text
    assert "function getStoryCardActionHierarchy" in response.text
    assert "function getRouteCardActionHierarchy" in response.text
    assert "data-card-action-primary" in response.text
    assert "data-card-action-secondary" in response.text
    assert "data-card-action-danger" in response.text
    assert "data-card-action-sheet" in response.text
    assert "action-sheet-toggle" in response.text
    assert "action-danger-row" in response.text
    assert "watch_search" in response.text
    assert "triage_filter" in response.text
    assert "story_view" in response.text
    assert "Mission Cockpit" in response.text
    assert "Mission Continuity" in response.text
    assert "Retry Mission" in response.text
    assert "retry advice" in response.text
    assert "timeline strip" in response.text
    assert "filter chips" in response.text
    assert "alert rule editor" in response.text
    assert "Add Alert Rule" in response.text
    assert "Save Alert Rules" in response.text
    assert "collector drill-down" in response.text
    assert "route drill-down" in response.text
    assert "route timeline" in response.text
    assert "AI Assistance Surfaces" in response.text
    assert "ai-surface-shell" in response.text
    assert "Inspect the same governed AI projection facts that CLI and MCP expose" in response.text
    assert "Distribution Health" in response.text
    assert "data-route-edit" in response.text
    assert "data-route-attach" in response.text
    assert "Triage Queue" in response.text
    assert "triage filters" in response.text
    assert "triage shortcuts" in response.text
    assert "batch actions" in response.text
    assert "data-triage-select-visible" in response.text
    assert "data-triage-batch-state" in response.text
    assert "data-triage-batch-delete" in response.text
    assert "data-triage-story" in response.text
    assert "Selected Evidence Workbench" in response.text
    assert "Open Story Workspace" in response.text
    assert "Use J/K to move" in response.text
    assert "note composer" in response.text
    assert "Save Note" in response.text
    assert "Story Workspace" in response.text
    assert "Story Delivery Readiness" in response.text
    assert "story editor" in response.text
    assert "Save Story" in response.text
    assert "Inspect Route" in response.text
    assert "Delivery Continuity" in response.text
    assert "build stories from CLI/MCP" not in response.text
    assert "datapulse --story-build / MCP story tools first" not in response.text


def test_console_client_script_keeps_restored_context_and_guidance_contract():
    script = render_console_client_script("{}")

    assert "createConsoleApiClient" in script
    assert "normalizeRequestOptions" in script
    assert "payload" in script
    assert "watch_search" in script
    assert "triage_filter" in script
    assert "story_view" in script
    assert "restoreContextSavedViewByName" in script
    assert "buildCockpitGuidanceSurface" in script
    assert "buildTriageGuidanceSurface" in script
    assert "function syncAdvancedSurfaceShells" in script
    assert "function openAdvancedSurfaceShell" in script
    assert "function workspaceModeOwnedOutputLabel" in script
    assert "function stageFeedbackIdForSection" in script
    assert "function stageFeedbackKindLabel" in script
    assert "function buildStageLinkedTrace" in script
    assert "function renderStageLinkedTraceCard" in script
    assert "function buildSharedSignalTaxonomy" in script
    assert "function renderSharedSignalTaxonomyCard" in script
    assert "sharedSignalFocus: \"quality\"" in script
    assert "wireLifecycleGuideActions(root);" in script


def test_console_api_client_script_normalizes_payload_requests():
    script = render_console_api_client_script()

    assert "function createConsoleApiClient" in script
    assert '"Content-Type": "application/json"' in script
    assert "delete normalized.payload" in script
    assert "JSON.stringify(payload)" in script
    assert "Request failed:" in script


def test_console_wrapper_help_uses_resolved_python_environment():
    repo_root = Path(__file__).resolve().parents[1]
    result = subprocess.run(
        ["bash", "scripts/datapulse_console.sh", "--help"],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert "--host" in result.stdout


def test_console_smoke_wrapper_uses_direct_browser_smoke_command():
    repo_root = Path(__file__).resolve().parents[1]
    script = (repo_root / "scripts" / "datapulse_console_smoke.sh").read_text()

    assert "uv run --extra console --with playwright python scripts/datapulse_console_browser_smoke.py" in script


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
    assert payload["story_ready_count"] == 1
    assert payload["story_converted_count"] == 1
    assert payload["route_count"] == 1
    assert payload["triage_open_count"] == 1
    assert payload["triage_acted_on_count"] == 1
    assert payload["alerting_mission_count"] == 1
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


def test_console_create_watch_route_reports_persistence_error():
    class _FailingCreateReader(_ConsoleReader):
        def create_watch(self, **kwargs):
            raise OSError("Read-only file system")

    client = TestClient(create_app(reader_factory=lambda: _FailingCreateReader()))
    response = client.post(
        "/api/watches",
        json={
            "name": "Launch Ops",
            "query": "OpenAI launch",
        },
    )

    assert response.status_code == 500
    assert "Unable to persist watch mission" in response.text


def test_console_update_watch_route():
    client = _client()
    response = client.put(
        "/api/watches/launch-ops",
        json={
            "name": "Launch Ops Prime",
            "query": "OpenAI launch update",
            "platforms": ["reddit"],
            "schedule": "@daily",
            "alert_rules": [{"name": "console-threshold", "routes": ["exec-telegram"]}],
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["name"] == "Launch Ops Prime"
    assert payload["query"] == "OpenAI launch update"
    assert payload["platforms"] == ["reddit"]
    assert payload["schedule"] == "@daily"
    assert payload["alert_rules"][0]["routes"] == ["exec-telegram"]


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
    scorecard = client.get("/api/ops/scorecard")

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
    assert ops.json()["governance_scorecard"]["signals"]["coverage"]["covered_targets_total"] == 3
    assert ops.json()["governance_scorecard"]["signals"]["freshness"]["status"] == "watch"
    assert scorecard.status_code == 200
    assert scorecard.json()["summary"]["signal_count"] == 5
    assert scorecard.json()["signals"]["story_conversion"]["converted_item_count"] == 1


def test_console_ai_surface_routes():
    client = _client()

    mission_precheck = client.get("/api/ai/surfaces/mission_suggest/precheck?mode=review")
    delivery_projection = client.get("/api/alerts/alert-1/ai/delivery-summary?mode=review")
    report_projection = client.get("/api/reports/report-runtime-closure/ai/report-draft?mode=review")
    mission_projection = client.get("/api/watches/launch-ops/ai/mission-suggest?mode=assist")
    triage_projection = client.get("/api/triage/item-1/ai/assist?mode=assist&limit=3")
    claim_projection = client.get("/api/stories/story-openai-launch/ai/claim-draft?mode=assist&brief_id=brief-1")

    assert mission_precheck.status_code == 200
    assert mission_precheck.json()["surface"] == "mission_suggest"
    assert mission_precheck.json()["mode"] == "review"
    assert delivery_projection.status_code == 200
    assert delivery_projection.json()["output"]["contract_id"] == "datapulse_ai_delivery_summary.v1"
    assert delivery_projection.json()["output"]["payload"]["research_projection"]["coverage_gap"]["status"] == "review_required"
    assert delivery_projection.json()["runtime_facts"]["request_id"] == "delivery-123"
    assert report_projection.status_code == 200
    assert report_projection.json()["output"] is None
    assert report_projection.json()["runtime_facts"]["request_id"] == "report-123"
    assert report_projection.json()["runtime_facts"]["served_by_alias"] == "dp.report.draft"
    assert mission_projection.status_code == 200
    assert mission_projection.json()["output"]["contract_id"] == "datapulse_ai_watch_suggestion.v1"
    assert mission_projection.json()["output"]["payload"]["research_projection"]["source_plan"]["news"] is True
    assert triage_projection.status_code == 200
    assert triage_projection.json()["output"]["contract_id"] == "datapulse_ai_triage_explain.v1"
    assert triage_projection.json()["output"]["payload"]["returned_count"] == 1
    assert claim_projection.status_code == 200
    assert claim_projection.json()["output"]["contract_id"] == "datapulse_ai_claim_draft.v1"
    assert claim_projection.json()["output"]["payload"]["research_projection"]["coverage_gap"]["status"] == "watch"
    assert claim_projection.json()["runtime_facts"]["request_id"] == "claim-123"


def test_console_surface_capabilities_routes():
    client = _client()

    runtime_introspection = client.get("/api/runtime/introspection")
    console_projection = client.get("/api/capabilities")
    agent_projection = client.get("/api/capabilities/agent?include_unavailable=true")

    assert runtime_introspection.status_code == 200
    assert runtime_introspection.json()["schema_version"] == "datapulse_runtime_surface_introspection.v1"
    assert runtime_introspection.json()["parity"]["ok"] is True
    assert runtime_introspection.json()["reopen_rules"]["wave_id"] == "L27"
    assert runtime_introspection.json()["intent_research_verification"]["wave_id"] == "L29"
    assert runtime_introspection.json()["intent_research_verification"]["research_projection"]["coverage_gap_status_enum"] == [
        "clear",
        "watch",
        "review_required",
        "blocked",
    ]
    assert runtime_introspection.json()["intent_research_verification"]["reopen_rules"]["admissible_evidence"][2]["id"] == "cross_surface_contradiction"

    assert console_projection.status_code == 200
    assert console_projection.json()["surface"] == "console"
    assert any(row["id"] == "surface_capability_catalog" for row in console_projection.json()["capabilities"])

    assert agent_projection.status_code == 200
    assert agent_projection.json()["surface"] == "agent"
    capabilities = {row["id"]: row for row in agent_projection.json()["capabilities"]}
    assert capabilities["url_batch_intake"]["availability"] == "available"
    assert capabilities["governed_ai_delivery_summary"]["availability"] == "unavailable"


def test_console_alert_route_crud_routes():
    client = _client()

    create_response = client.post(
        "/api/alert-routes",
        json={
            "name": "exec-telegram",
            "channel": "telegram",
            "description": "Exec escalation path",
            "telegram_chat_id": "12345",
        },
    )
    update_response = client.put(
        "/api/alert-routes/ops-webhook",
        json={
            "description": "Updated ops webhook",
            "webhook_url": "https://hooks.example.com/ops-v2",
        },
    )
    delete_response = client.delete("/api/alert-routes/ops-webhook")

    assert create_response.status_code == 200
    assert create_response.json()["name"] == "exec-telegram"
    assert create_response.json()["channel"] == "telegram"
    assert update_response.status_code == 200
    assert update_response.json()["description"] == "Updated ops webhook"
    assert update_response.json()["webhook_url"] == "https://hooks.example.com/ops-v2"
    assert delete_response.status_code == 200
    assert delete_response.json()["name"] == "ops-webhook"


def test_console_watch_detail_route():
    client = _client()
    response = client.get("/api/watches/launch-ops")

    assert response.status_code == 200
    payload = response.json()
    assert payload["id"] == "launch-ops"
    assert payload["run_stats"]["success"] == 1
    assert payload["research_projection"]["coverage_gap"]["operator_action"] == "tighten_watch_scope"
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
    delete_response = client.delete("/api/triage/item-1")

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
    assert delete_response.status_code == 200
    assert delete_response.json()["deleted"] is True


def test_console_story_routes():
    client = _client()

    stories = client.get("/api/stories?limit=4&min_items=2")
    create = client.post(
        "/api/stories",
        json={
            "title": "Manual Brief",
            "summary": "Operator-authored short brief",
            "status": "monitoring",
        },
    )
    from_triage = client.post(
        "/api/stories/from-triage",
        json={
            "item_ids": ["item-1", "item-2"],
            "title": "Triage Seed",
            "status": "monitoring",
        },
    )
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
    delete = client.delete("/api/stories/story-openai-launch")

    assert stories.status_code == 200
    assert stories.json()[0]["id"] == "story-openai-launch"
    assert create.status_code == 200
    assert create.json()["title"] == "Manual Brief"
    assert create.json()["status"] == "monitoring"
    assert from_triage.status_code == 200
    assert from_triage.json()["id"] == "story-triage-seed"
    assert from_triage.json()["primary_item_id"] == "item-1"
    assert from_triage.json()["item_count"] == 2
    assert detail.status_code == 200
    assert detail.json()["primary_item_id"] == "item-1"
    assert detail.json()["research_projection"]["coverage_gap"]["status"] == "watch"
    assert update.status_code == 200
    assert update.json()["title"] == "OpenAI Launch Watch"
    assert update.json()["status"] == "monitoring"
    assert graph.status_code == 200
    assert graph.json()["relation_count"] == 1
    assert graph.json()["nodes"][1]["label"] == "OpenAI"
    assert export.status_code == 200
    assert export.headers["content-type"].startswith("text/markdown")
    assert export.text.startswith("# OpenAI Launch")
    assert delete.status_code == 200
    assert delete.json()["id"] == "story-openai-launch"


def test_console_report_routes():
    client = _client()

    report_briefs = client.get("/api/report-briefs")
    create_brief = client.post("/api/report-briefs", json={"id": "brief-manual", "title": "Manual Brief", "status": "draft"})
    show_brief = client.get("/api/report-briefs/brief-openai")
    update_brief = client.put("/api/report-briefs/brief-openai", json={"title": "Brief Updated"})

    claim_cards = client.get("/api/claim-cards")
    create_claim = client.post("/api/claim-cards", json={"id": "claim-manual", "title": "Manual Claim", "status": "draft"})
    show_claim = client.get("/api/claim-cards/claim-openai-trend")
    update_claim = client.put("/api/claim-cards/claim-openai-trend", json={"status": "ready"})

    report_sections = client.get("/api/report-sections")
    create_section = client.post("/api/report-sections", json={"id": "section-manual", "title": "Manual Section", "status": "draft"})
    show_section = client.get("/api/report-sections/section-market-context")
    update_section = client.put("/api/report-sections/section-market-context", json={"status": "ready"})

    citation_bundles = client.get("/api/citation-bundles")
    create_bundle = client.post("/api/citation-bundles", json={"id": "bundle-manual", "label": "Manual Bundle"})
    show_bundle = client.get("/api/citation-bundles/bundle-openai")
    update_bundle = client.put("/api/citation-bundles/bundle-openai", json={"label": "Updated bundle"})

    reports = client.get("/api/reports")
    create_report = client.post("/api/reports", json={"id": "report-manual", "title": "Manual Report", "status": "draft"})
    show_report = client.get("/api/reports/report-openai-market")
    update_report = client.put("/api/reports/report-openai-market", json={"status": "ready"})
    compose = client.post("/api/reports/report-openai-market/compose", json={"profile_id": "profile-brief"})
    compose_view = client.get("/api/reports/report-openai-market/compose?profile_id=profile-brief")
    quality = client.get("/api/reports/report-openai-market/quality?profile_id=profile-brief")
    export_json = client.get("/api/reports/report-openai-market/export?output_format=json&profile_id=profile-brief")
    export_markdown = client.get("/api/reports/report-openai-market/export?output_format=markdown&profile_id=profile-brief")

    export_profiles = client.get("/api/export-profiles")
    create_profile = client.post("/api/export-profiles", json={"id": "profile-manual", "name": "Manual Profile"})
    show_profile = client.get("/api/export-profiles/profile-brief")
    update_profile = client.put("/api/export-profiles/profile-brief", json={"name": "Updated Profile"})

    assert report_briefs.status_code == 200
    assert report_briefs.json()[0]["id"] == "brief-openai"
    assert create_brief.status_code == 200
    assert create_brief.json()["id"] == "brief-manual"
    assert show_brief.status_code == 200
    assert show_brief.json()["title"] == "OpenAI Report Brief"
    assert update_brief.status_code == 200
    assert update_brief.json()["title"] == "Brief Updated"

    assert claim_cards.status_code == 200
    assert claim_cards.json()[0]["id"] == "claim-openai-trend"
    assert create_claim.status_code == 200
    assert create_claim.json()["id"] == "claim-manual"
    assert show_claim.status_code == 200
    assert show_claim.json()["title"] == "OpenAI launch claim"
    assert update_claim.status_code == 200
    assert update_claim.json()["status"] == "ready"

    assert report_sections.status_code == 200
    assert report_sections.json()[0]["id"] == "section-market-context"
    assert create_section.status_code == 200
    assert create_section.json()["id"] == "section-manual"
    assert show_section.status_code == 200
    assert show_section.json()["title"] == "Market context"
    assert update_section.status_code == 200
    assert update_section.json()["status"] == "ready"

    assert citation_bundles.status_code == 200
    assert citation_bundles.json()[0]["id"] == "bundle-openai"
    assert create_bundle.status_code == 200
    assert create_bundle.json()["id"] == "bundle-manual"
    assert show_bundle.status_code == 200
    assert show_bundle.json()["label"] == "OpenAI bundle"
    assert update_bundle.status_code == 200
    assert update_bundle.json()["label"] == "Updated bundle"

    assert reports.status_code == 200
    assert reports.json()[0]["id"] == "report-openai-market"
    assert create_report.status_code == 200
    assert create_report.json()["id"] == "report-manual"
    assert show_report.status_code == 200
    assert show_report.json()["title"] == "OpenAI Market Report"
    assert update_report.status_code == 200
    assert update_report.json()["status"] == "ready"
    assert compose.status_code == 200
    assert compose.json()["report"]["id"] == "report-openai-market"
    assert compose_view.status_code == 200
    assert compose_view.json()["report"]["id"] == "report-openai-market"
    assert quality.status_code == 200
    assert quality.json()["status"] == "ok"
    assert export_json.status_code == 200
    assert export_json.json()["report"]["id"] == "report-openai-market"
    assert export_markdown.status_code == 200
    assert export_markdown.headers["content-type"].startswith("text/markdown")
    assert export_markdown.text.startswith("# OpenAI Market Report")

    assert export_profiles.status_code == 200
    assert export_profiles.json()[0]["id"] == "profile-brief"
    assert create_profile.status_code == 200
    assert create_profile.json()["id"] == "profile-manual"
    assert show_profile.status_code == 200
    assert show_profile.json()["name"] == "Brief export profile"
    assert update_profile.status_code == 200
    assert update_profile.json()["name"] == "Updated Profile"


def test_console_report_watch_pack_routes(tmp_path, monkeypatch):
    monkeypatch.setenv("DATAPULSE_WATCHLIST_PATH", str(tmp_path / "watchlist.json"))
    monkeypatch.setenv("DATAPULSE_REPORTS_PATH", str(tmp_path / "reports.json"))

    reader = DataPulseReader(inbox_path=str(tmp_path / "inbox.json"))
    report = reader.create_report(
        title="Console Watch Pack Report",
        summary="A synthetic report used for console watch-pack API checks.",
    )
    claim = reader.create_claim_card(
        statement="Console watch-pack synthesis keeps watch missions reproducible.",
        source_item_ids=["item-console"],
        brief_id="",
    )
    section = reader.create_report_section(
        report_id=report["id"],
        title="Console Section",
        claim_card_ids=[claim["id"]],
        position=1,
    )
    bundle = reader.create_citation_bundle(
        claim_card_id=claim["id"],
        label="Console evidence",
        source_urls=["https://example.com/console-watch"],
    )
    claim = reader.update_claim_card(claim["id"], citation_bundle_ids=[bundle["id"]])
    reader.update_report(
        report["id"],
        section_ids=[section["id"]],
        claim_card_ids=[claim["id"]],
        citation_bundle_ids=[bundle["id"]],
    )

    profile_map = {
        row["name"]: row["id"] for row in reader.list_export_profiles(report_id=report["id"])
    }

    client = TestClient(create_app(reader_factory=lambda: reader))
    watch_pack_response = client.get(f"/api/reports/{report['id']}/watch-pack")
    watch_pack = watch_pack_response.json()

    assert watch_pack_response.status_code == 200
    assert watch_pack["report_id"] == report["id"]
    assert watch_pack["query"] == report["title"]
    create_watch_response = client.post(
        f"/api/reports/{report['id']}/watch-from-pack",
        json={
            "profile_id": profile_map["watch-pack"],
            "name": "Console Follow-up Watch",
            "query": "Console follow-up launch query",
            "platforms": ["twitter"],
        },
    )
    mission = create_watch_response.json()

    assert create_watch_response.status_code == 200
    assert mission["name"] == "Console Follow-up Watch"
    assert mission["query"] == "Console follow-up launch query"
    assert mission["platforms"] == ["twitter"]


def test_console_delivery_routes():
    client = _client()

    subscriptions = client.get("/api/delivery-subscriptions?subject_kind=report&route_name=ops-webhook")
    create_subscription = client.post(
        "/api/delivery-subscriptions",
        json={
            "subject_kind": "report",
            "subject_ref": "report-openai-market",
            "output_kind": "report_full",
            "delivery_mode": "push",
            "route_names": ["ops-webhook"],
        },
    )
    show_subscription = client.get("/api/delivery-subscriptions/delivery-subscription-report")
    update_subscription = client.put(
        "/api/delivery-subscriptions/delivery-subscription-report",
        json={"status": "paused"},
    )
    package = client.get("/api/delivery-subscriptions/delivery-subscription-report/package?profile_id=profile-brief")
    dispatch = client.post(
        "/api/delivery-subscriptions/delivery-subscription-report/dispatch",
        json={"profile_id": "profile-brief"},
    )
    dispatch_records = client.get(
        "/api/delivery-dispatch-records?subscription_id=delivery-subscription-report&status=delivered"
    )
    delete_subscription = client.delete("/api/delivery-subscriptions/delivery-subscription-report")

    assert subscriptions.status_code == 200
    assert subscriptions.json()[0]["id"] == "delivery-subscription-report"
    assert create_subscription.status_code == 200
    assert create_subscription.json()["id"] == "delivery-subscription-manual"
    assert show_subscription.status_code == 200
    assert show_subscription.json()["subject_ref"] == "report-openai-market"
    assert update_subscription.status_code == 200
    assert update_subscription.json()["status"] == "paused"
    assert package.status_code == 200
    assert package.json()["package_id"] == "report-openai-market:report_full:pkg-signature-1234"
    assert package.json()["profile_id"] == "profile-brief"
    assert dispatch.status_code == 200
    assert dispatch.json()[0]["status"] == "delivered"
    assert dispatch.json()[0]["package_profile_id"] == "profile-brief"
    assert dispatch_records.status_code == 200
    assert dispatch_records.json()[0]["route_label"] == "webhook:ops-webhook"
    assert delete_subscription.status_code == 200
    assert delete_subscription.json()["id"] == "delivery-subscription-report"


def test_console_delivery_package_and_dispatch_require_report_subscription(tmp_path, monkeypatch):
    monkeypatch.setenv("DATAPULSE_STORIES_PATH", str(tmp_path / "stories.json"))
    monkeypatch.setenv("DATAPULSE_REPORTS_PATH", str(tmp_path / "reports.json"))

    reader = DataPulseReader(inbox_path=str(tmp_path / "inbox.json"))
    story = reader.create_story(
        title="Console Delivery Story",
        summary="Used to validate report-only delivery API guards.",
    )
    subscription = reader.create_delivery_subscription(
        subject_kind="story",
        subject_ref=story["id"],
        output_kind="story_json",
        delivery_mode="pull",
    )

    client = TestClient(create_app(reader_factory=lambda: reader))
    package_response = client.get(f"/api/delivery-subscriptions/{subscription['id']}/package")
    dispatch_response = client.post(f"/api/delivery-subscriptions/{subscription['id']}/dispatch", json={})

    assert package_response.status_code == 400
    assert "Only report subscriptions" in package_response.json()["detail"]
    assert dispatch_response.status_code == 400
    assert "Only report subscriptions" in dispatch_response.json()["detail"]


def test_console_digest_routes():
    client = _client()

    profile = client.get("/api/digest-profile")
    update = client.put(
        "/api/digest-profile",
        json={
            "language": "zh-CN",
            "timezone": "Asia/Shanghai",
            "frequency": "@hourly",
            "default_delivery_target": {"kind": "route", "ref": "ops-webhook"},
        },
    )
    projection = client.get("/api/digest/console?profile=default&limit=5")
    dispatch = client.post("/api/digest/dispatch", json={"profile": "default", "limit": 5})

    assert profile.status_code == 200
    assert profile.json()["profile"]["default_delivery_target"]["ref"] == "ops-webhook"
    assert update.status_code == 200
    assert update.json()["profile"]["language"] == "zh-CN"
    assert update.json()["profile"]["timezone"] == "Asia/Shanghai"
    assert update.json()["profile"]["frequency"] == "@hourly"
    assert projection.status_code == 200
    assert projection.json()["prepared_payload"]["content"]["feed_bundle"]["stats"]["items_selected"] == 2
    assert projection.json()["prepared_payload"]["prompts"]["repo_default_pack"] == "digest_delivery_default"
    assert dispatch.status_code == 200
    assert dispatch.json()[0]["status"] == "delivered"
    assert dispatch.json()[0]["route_label"] == "webhook:ops-webhook"


def test_console_digest_profile_persists_with_real_reader(tmp_path, monkeypatch):
    monkeypatch.setenv("DATAPULSE_DIGEST_PROFILE_PATH", str(tmp_path / "digest_profile.json"))

    reader = DataPulseReader(inbox_path=str(tmp_path / "inbox.json"))
    client = TestClient(create_app(reader_factory=lambda: reader))

    update = client.put(
        "/api/digest-profile",
        json={
            "language": "zh-CN",
            "timezone": "Asia/Shanghai",
            "frequency": "@daily",
            "default_delivery_target": {"kind": "route", "ref": "ops-webhook"},
        },
    )
    projection = client.get("/api/digest/console?profile=default&limit=3")

    persisted = json.loads((tmp_path / "digest_profile.json").read_text(encoding="utf-8"))

    assert update.status_code == 200
    assert update.json()["exists"] is True
    assert update.json()["onboarding_status"] == "ready"
    assert persisted["language"] == "zh-CN"
    assert persisted["timezone"] == "Asia/Shanghai"
    assert persisted["frequency"] == "@daily"
    assert persisted["default_delivery_target"] == {"kind": "route", "ref": "ops-webhook"}
    assert projection.status_code == 200
    assert projection.json()["profile"]["profile"]["language"] == "zh-CN"
    assert projection.json()["prepared_payload"]["config"]["digest_profile"]["default_delivery_target"]["ref"] == "ops-webhook"


def test_console_ops_scorecard_with_real_reader(tmp_path, monkeypatch):
    monkeypatch.setenv("DATAPULSE_WATCHLIST_PATH", str(tmp_path / "watchlist.json"))
    monkeypatch.setenv("DATAPULSE_STORIES_PATH", str(tmp_path / "stories.json"))
    monkeypatch.setenv("DATAPULSE_ALERTS_PATH", str(tmp_path / "alerts.json"))
    monkeypatch.setenv("DATAPULSE_ALERT_ROUTING_PATH", str(tmp_path / "routes.json"))

    reader = DataPulseReader(inbox_path=str(tmp_path / "inbox.json"))
    now = datetime.now(timezone.utc).replace(microsecond=0)
    fresh_at = (now - timedelta(hours=2)).isoformat()
    stale_at = (now - timedelta(hours=72)).isoformat()

    launch_watch = reader.create_watch(
        name="Launch Radar",
        query="OpenAI launch",
        mission_intent={
            "freshness_max_age_hours": 48,
            "coverage_targets": ["OpenAI Blog"],
        },
        platforms=["twitter"],
        sites=["openai.com"],
        schedule="@hourly",
    )
    community_watch = reader.create_watch(
        name="Community Radar",
        query="OpenAI forum",
        mission_intent={
            "freshness_max_age_hours": 24,
            "coverage_targets": ["Example Community"],
        },
        platforms=["reddit"],
        sites=["example.com"],
        schedule="@daily",
    )

    reader.watchlist.record_run(
        launch_watch["id"],
        MissionRun(
            mission_id=launch_watch["id"],
            status="success",
            item_count=1,
            finished_at=fresh_at,
        ),
    )
    reader.watchlist.record_run(
        community_watch["id"],
        MissionRun(
            mission_id=community_watch["id"],
            status="success",
            item_count=1,
            finished_at=stale_at,
        ),
    )

    for item in (
        DataPulseItem(
            id="item-1",
            source_type=SourceType.TWITTER,
            source_name="OpenAI Blog",
            title="OpenAI launch update",
            content="launch " * 20,
            url="https://openai.com/blog/launch",
            parser="twitter",
            fetched_at=fresh_at,
            score=91,
            confidence=0.96,
            review_state="verified",
            tags=["twitter"],
            extra={
                "watch_mission_id": launch_watch["id"],
                "watch_mission_name": launch_watch["name"],
            },
        ),
        DataPulseItem(
            id="item-2",
            source_type=SourceType.REDDIT,
            source_name="Example Community",
            title="Community reaction",
            content="community " * 20,
            url="https://example.com/thread/openai",
            parser="reddit",
            fetched_at=stale_at,
            score=67,
            confidence=0.74,
            review_state="triaged",
            tags=["reddit"],
            extra={
                "watch_mission_id": community_watch["id"],
                "watch_mission_name": community_watch["name"],
            },
        ),
        DataPulseItem(
            id="item-3",
            source_type=SourceType.GENERIC,
            source_name="Newswire",
            title="Loose lead",
            content="lead " * 20,
            url="https://news.example.net/lead",
            parser="generic",
            fetched_at=fresh_at,
            score=40,
            confidence=0.55,
            review_state="new",
        ),
    ):
        reader.inbox.add(item, fingerprint_dedup=False)
    reader.inbox.save()

    reader.alert_store.add(
        AlertEvent(
            mission_id=launch_watch["id"],
            mission_name=launch_watch["name"],
            rule_name="launch-threshold",
            item_ids=["item-1"],
            summary="Launch Radar triggered launch-threshold",
        ),
        cooldown_seconds=0,
    )
    reader.story_store.replace_stories(
        [
            Story(
                title="Launch Story",
                summary="Launch storyline",
                status="active",
                item_count=2,
                source_count=2,
                primary_item_id="item-1",
                primary_evidence=[
                    StoryEvidence(
                        item_id="item-1",
                        title="OpenAI launch update",
                        url="https://openai.com/blog/launch",
                        source_name="OpenAI Blog",
                        source_type="twitter",
                        review_state="verified",
                    )
                ],
                secondary_evidence=[
                    StoryEvidence(
                        item_id="item-2",
                        title="Community reaction",
                        url="https://example.com/thread/openai",
                        source_name="Example Community",
                        source_type="reddit",
                        review_state="triaged",
                    )
                ],
                governance={"delivery_risk": {"status": "ready"}},
            )
        ]
    )

    monkeypatch.setattr(reader, "doctor", lambda: {"tier_0": [], "tier_1": [], "tier_2": []})
    monkeypatch.setattr(
        reader,
        "watch_status_snapshot",
        lambda: {
            "state": "running",
            "heartbeat_at": now.isoformat(),
            "last_error": "",
            "metrics": {
                "cycles_total": 2,
                "runs_total": 2,
                "success_total": 2,
                "error_total": 0,
                "alerts_total": 1,
            },
        },
    )

    client = TestClient(create_app(reader_factory=lambda: reader))
    ops_response = client.get("/api/ops")
    scorecard_response = client.get("/api/ops/scorecard")

    assert ops_response.status_code == 200
    assert scorecard_response.status_code == 200

    ops_payload = ops_response.json()
    scorecard = ops_payload["governance_scorecard"]
    scorecard_direct = scorecard_response.json()
    signals = scorecard["signals"]

    assert scorecard["summary"]["signal_count"] == 5
    assert signals["coverage"]["status"] == "ok"
    assert signals["coverage"]["expected_targets_total"] == 6
    assert signals["coverage"]["covered_targets_total"] == 6
    assert signals["freshness"]["status"] == "watch"
    assert signals["freshness"]["missions_with_sla"] == 2
    assert signals["freshness"]["fresh_missions"] == 1
    assert signals["alert_yield"]["status"] == "ok"
    assert signals["alert_yield"]["alert_count"] == 1
    assert signals["alert_yield"]["successful_runs"] == 2
    assert signals["triage_throughput"]["status"] == "ok"
    assert signals["triage_throughput"]["acted_on_items"] == 2
    assert signals["triage_throughput"]["total_items"] == 3
    assert signals["story_conversion"]["status"] == "ok"
    assert signals["story_conversion"]["eligible_item_count"] == 2
    assert signals["story_conversion"]["converted_item_count"] == 2
    assert scorecard_direct["summary"] == scorecard["summary"]
    assert scorecard_direct["mission_scope"] == scorecard["mission_scope"]
    assert scorecard_direct["signals"] == scorecard["signals"]
