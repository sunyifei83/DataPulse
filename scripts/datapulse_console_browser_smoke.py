#!/usr/bin/env python3
from __future__ import annotations

import contextlib
from copy import deepcopy
import socket
import threading
import time

import uvicorn

from datapulse.console_server import create_app

try:
    from playwright.sync_api import Page, Playwright, sync_playwright
except ImportError as exc:  # pragma: no cover - exercised in runtime only
    raise SystemExit("Playwright is not installed. Run with: uv run --with playwright python scripts/datapulse_console_browser_smoke.py") from exc


def _clone(payload):
    return deepcopy(payload)


class _SmokeReader:
    def __init__(self) -> None:
        self.routes = [
            {
                "name": "ops-webhook",
                "channel": "webhook",
                "description": "Primary ops webhook",
                "webhook_url": "https://hooks.example.com/ops",
            }
        ]
        self.watches = [
            {
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
                "alert_rule_count": 1,
                "alert_rules": [{"name": "console-threshold", "routes": ["ops-webhook"], "keyword_any": ["launch"]}],
                "last_run_at": "2026-03-06T00:00:00+00:00",
                "last_run_status": "success",
            }
        ]
        self.triage_items = [
            {
                "id": "item-1",
                "title": "OpenAI launch post",
                "review_state": "new",
                "score": 81,
                "confidence": 0.91,
                "url": "https://example.com/openai-launch",
                "source_name": "OpenAI Blog",
                "source_type": "generic",
                "review_notes": [],
            },
            {
                "id": "item-2",
                "title": "OpenAI launch recap",
                "review_state": "verified",
                "score": 74,
                "confidence": 0.82,
                "url": "https://example.com/openai-launch-recap",
                "source_name": "The Verge",
                "source_type": "news",
                "review_notes": [
                    {
                        "note": "Validated against primary launch source.",
                        "author": "analyst",
                        "created_at": "2026-03-06T00:05:00+00:00",
                    }
                ],
            },
        ]
        self.stories = [
            {
                "id": "story-openai-launch",
                "title": "OpenAI Launch",
                "summary": "3 signals across 2 sources around OpenAI Launch",
                "status": "active",
                "score": 87.4,
                "confidence": 0.91,
                "item_count": 3,
                "source_count": 2,
                "primary_item_id": "item-1",
                "entities": ["OpenAI", "GPT-5"],
                "source_names": ["OpenAI Blog", "The Verge"],
                "primary_evidence": [],
                "secondary_evidence": [],
                "timeline": [],
                "contradictions": [],
                "generated_at": "2026-03-06T00:00:00+00:00",
                "updated_at": "2026-03-06T00:05:00+00:00",
            }
        ]

    def _route_usage_names(self, route_name: str) -> list[str]:
        normalized = str(route_name or "").strip().lower()
        usage = []
        for watch in self.watches:
            for rule in watch.get("alert_rules") or []:
                routes = [str(item).strip().lower() for item in rule.get("routes") or []]
                if normalized and normalized in routes:
                    usage.append(str(watch.get("name") or watch.get("id") or route_name))
                    break
        return usage

    def _build_route_health(self, route: dict[str, str]) -> dict[str, object]:
        usage_names = self._route_usage_names(str(route.get("name") or ""))
        return {
            "name": route["name"],
            "channel": route["channel"],
            "configured": True,
            "status": "healthy",
            "event_count": 4 if usage_names else 0,
            "delivered_count": 4 if usage_names else 0,
            "failure_count": 0,
            "success_rate": 1.0 if usage_names else None,
            "last_event_at": "2026-03-06T00:00:10+00:00" if usage_names else "",
            "last_delivered_at": "2026-03-06T00:00:10+00:00" if usage_names else "",
            "last_failed_at": "",
            "last_error": "",
            "last_summary": "Route healthy" if usage_names else "No route delivery yet",
            "mission_ids": ["launch-ops"] if usage_names else [],
            "rule_names": ["console-threshold"] if usage_names else [],
        }

    def _base_story_graph(self, story: dict[str, object]) -> dict[str, object]:
        title = str(story.get("title") or "Untitled Story")
        story_id = str(story.get("id") or "story")
        return {
            "story": {
                "id": story_id,
                "title": title,
            },
            "nodes": [
                {
                    "id": story_id,
                    "label": title,
                    "kind": "story",
                    "item_count": int(story.get("item_count") or 0),
                    "source_count": int(story.get("source_count") or 0),
                },
                {
                    "id": "entity:openai",
                    "label": "OpenAI",
                    "kind": "entity",
                    "entity_type": "ORG",
                    "in_story_source_count": 2,
                },
            ],
            "edges": [
                {
                    "source": story_id,
                    "target": "entity:openai",
                    "relation_type": "MENTIONED_IN_STORY",
                    "kind": "story_entity",
                }
            ],
            "entity_count": 1,
            "relation_count": 1,
            "edge_count": 1,
        }

    def list_watches(self, include_disabled: bool = False):
        rows = [watch for watch in self.watches if include_disabled or watch.get("enabled", True)]
        return _clone(rows)

    def show_watch(self, identifier: str):
        for watch in self.watches:
            if watch["id"] != identifier:
                continue
            payload = _clone(watch)
            payload.update(
                {
                    "run_stats": {"total": 1, "success": 1, "error": 0, "average_items": 2.0},
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
            )
            return payload
        return None

    def list_watch_results(self, identifier: str, limit: int = 10, min_confidence: float = 0.0):
        payload = self.show_watch(identifier)
        if payload is None:
            return None
        rows = [
            row
            for row in payload.get("recent_results", [])
            if float(row.get("confidence", 0.0) or 0.0) >= min_confidence
        ]
        return _clone(rows[:limit])

    def create_watch(self, **kwargs):
        next_id = f"watch-{len(self.watches) + 1}"
        mission = {
            "id": next_id,
            "name": kwargs["name"],
            "query": kwargs["query"],
            "enabled": True,
            "platforms": kwargs.get("platforms") or [],
            "sites": kwargs.get("sites") or [],
            "schedule": kwargs.get("schedule", "manual"),
            "schedule_label": kwargs.get("schedule", "manual"),
            "is_due": False,
            "next_run_at": "",
            "alert_rule_count": len(kwargs.get("alert_rules") or []),
            "alert_rules": kwargs.get("alert_rules") or [],
            "last_run_at": "",
            "last_run_status": "",
        }
        self.watches.append(mission)
        return _clone(mission)

    def set_watch_alert_rules(self, identifier: str, *, alert_rules=None):
        for watch in self.watches:
            if watch["id"] == identifier:
                watch["alert_rules"] = list(alert_rules or [])
                watch["alert_rule_count"] = len(watch["alert_rules"])
                return self.show_watch(identifier)
        return None

    async def run_watch(self, identifier: str):
        return {"mission": {"id": identifier}, "run": {"status": "success", "item_count": 2}, "items": [], "alert_events": []}

    async def run_due_watches(self, limit=None):
        return {"due_count": 1, "run_count": 1, "results": [{"mission_id": "launch-ops", "status": "success"}]}

    def disable_watch(self, identifier: str):
        for watch in self.watches:
            if watch["id"] == identifier:
                watch["enabled"] = False
                return _clone(watch)
        return None

    def enable_watch(self, identifier: str):
        for watch in self.watches:
            if watch["id"] == identifier:
                watch["enabled"] = True
                return _clone(watch)
        return None

    def delete_watch(self, identifier: str):
        for index, watch in enumerate(self.watches):
            if watch["id"] == identifier:
                removed = self.watches.pop(index)
                return _clone(removed)
        return None

    def list_alerts(self, limit: int = 20, mission_id: str | None = None):
        alerts = [
            {
                "id": "alert-1",
                "mission_id": "launch-ops",
                "mission_name": "Launch Ops",
                "rule_name": "console-threshold",
                "summary": "Launch Ops triggered console-threshold",
                "created_at": "2026-03-06T00:00:10+00:00",
                "item_ids": ["item-1", "item-2"],
                "delivered_channels": ["json", "webhook:ops-webhook"],
            }
        ]
        if mission_id:
            alerts = [alert for alert in alerts if alert["mission_id"] == mission_id]
        return _clone(alerts[:limit])

    def list_alert_routes(self):
        return _clone(self.routes)

    def create_alert_route(self, **payload):
        route = {
            "name": payload["name"],
            "channel": payload["channel"],
            "description": payload.get("description", ""),
            "webhook_url": payload.get("webhook_url", ""),
            "authorization": payload.get("authorization", ""),
            "headers": payload.get("headers") or {},
            "feishu_webhook": payload.get("feishu_webhook", ""),
            "telegram_bot_token": payload.get("telegram_bot_token", ""),
            "telegram_chat_id": payload.get("telegram_chat_id", ""),
            "timeout_seconds": payload.get("timeout_seconds"),
        }
        self.routes.append(route)
        return _clone(route)

    def update_alert_route(self, identifier: str, **payload):
        for route in self.routes:
            if route["name"] == identifier:
                route.update({key: value for key, value in payload.items() if value is not None})
                route["name"] = identifier
                return _clone(route)
        return None

    def delete_alert_route(self, identifier: str):
        for index, route in enumerate(self.routes):
            if route["name"] == identifier:
                removed = self.routes.pop(index)
                return _clone(removed)
        return None

    def alert_route_health(self, limit: int = 100):
        rows = [self._build_route_health(route) for route in self.routes]
        return _clone(rows[:limit])

    def watch_status_snapshot(self):
        return {
            "state": "running",
            "heartbeat_at": "2026-03-06T00:00:00+00:00",
            "metrics": {"cycles_total": 3, "runs_total": 2, "alerts_total": 1, "error_total": 0, "success_total": 2},
            "last_error": "",
        }

    def governance_scorecard_snapshot(self):
        return {
            "generated_at": "2026-03-06T00:00:30+00:00",
            "mission_scope": {"total": len(self.watches), "enabled": 1, "disabled": 0, "items": len(self.triage_items), "stories": len(self.stories)},
            "signals": {
                "coverage": {"id": "coverage", "label": "Coverage", "status": "ok", "covered_targets_total": 3},
                "freshness": {"id": "freshness", "label": "Freshness", "status": "watch"},
                "alert_yield": {"id": "alert_yield", "label": "Alert Yield", "status": "ok"},
                "triage_throughput": {"id": "triage_throughput", "label": "Triage Throughput", "status": "ok"},
                "story_conversion": {"id": "story_conversion", "label": "Story Conversion", "status": "ok"},
            },
            "summary": {"signal_count": 5, "ok": 4, "watch": 1, "missing": 0},
        }

    def ops_snapshot(self):
        route_health = self.alert_route_health(limit=100)
        healthy_routes = sum(1 for route in route_health if route.get("status") == "healthy")
        watch_summary = {
            "total": len(self.watches),
            "enabled": sum(1 for watch in self.watches if watch.get("enabled", True)),
            "disabled": sum(1 for watch in self.watches if not watch.get("enabled", True)),
            "healthy": sum(1 for watch in self.watches if watch.get("enabled", True)),
            "degraded": 0,
            "idle": 0,
            "due": sum(1 for watch in self.watches if watch.get("is_due")),
        }
        route_drilldown = []
        for route in route_health:
            usage_names = self._route_usage_names(str(route.get("name") or ""))
            route_drilldown.append(
                {
                    "name": route["name"],
                    "channel": route["channel"],
                    "status": route["status"],
                    "configured": route["configured"],
                    "event_count": route["event_count"],
                    "delivered_count": route["delivered_count"],
                    "failure_count": route["failure_count"],
                    "success_rate": route["success_rate"],
                    "last_event_at": route["last_event_at"],
                    "last_delivered_at": route["last_delivered_at"],
                    "last_failed_at": route["last_failed_at"],
                    "last_error": route["last_error"],
                    "last_summary": route["last_summary"],
                    "mission_count": len(usage_names),
                    "rule_count": len(usage_names),
                    "mission_ids": ["launch-ops"] if usage_names else [],
                    "rule_names": ["console-threshold"] if usage_names else [],
                }
            )
        return {
            "collector_summary": {"total": 2, "ok": 2, "warn": 0, "error": 0, "available": 2, "unavailable": 0},
            "collector_tiers": {"tier_0": {"total": 2, "ok": 2, "warn": 0, "error": 0, "available": 2, "unavailable": 0}},
            "degraded_collectors": [],
            "collector_drilldown": [],
            "watch_metrics": {"state": "running", "success_rate": 1.0},
            "watch_summary": watch_summary,
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
                }
            ],
            "route_summary": {
                "total": len(route_health),
                "healthy": healthy_routes,
                "degraded": 0,
                "missing": 0,
                "idle": max(0, len(route_health) - healthy_routes),
            },
            "route_health": _clone(route_health),
            "route_drilldown": route_drilldown,
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
            "recent_failures": [],
            "recent_alerts": self.list_alerts(),
            "governance_scorecard": self.governance_scorecard_snapshot(),
            "daemon": self.watch_status_snapshot(),
        }

    def triage_list(self, **kwargs):
        states = kwargs.get("states") or []
        rows = self.triage_items
        if states:
            allowed = {str(state).strip().lower() for state in states if str(state).strip()}
            rows = [item for item in rows if str(item.get("review_state") or "").strip().lower() in allowed]
        limit = int(kwargs.get("limit") or len(rows))
        return _clone(rows[:limit])

    def triage_stats(self):
        states = {"new": 0, "triaged": 0, "verified": 0, "duplicate": 0, "ignored": 0, "escalated": 0}
        for item in self.triage_items:
            key = str(item.get("review_state") or "new").strip().lower() or "new"
            states[key] = states.get(key, 0) + 1
        return {
            "total": len(self.triage_items),
            "open_count": states["new"] + states["triaged"] + states["verified"] + states["escalated"],
            "closed_count": states["duplicate"] + states["ignored"],
            "note_count": sum(len(item.get("review_notes") or []) for item in self.triage_items),
            "states": states,
        }

    def triage_update(self, item_id, **kwargs):
        for item in self.triage_items:
            if item["id"] == item_id:
                item["review_state"] = kwargs["state"]
                note = str(kwargs.get("note") or "").strip()
                if note:
                    item.setdefault("review_notes", []).append({"note": note, "author": kwargs.get("actor", "console")})
                return _clone(item)
        return None

    def triage_note(self, item_id, **kwargs):
        for item in self.triage_items:
            if item["id"] == item_id:
                item.setdefault("review_notes", []).append({"note": kwargs["note"], "author": kwargs.get("author", "console")})
                return _clone(item)
        return None

    def triage_delete(self, item_id):
        for index, item in enumerate(self.triage_items):
            if item["id"] == item_id:
                removed = self.triage_items.pop(index)
                return {"id": removed["id"], "deleted": True}
        return None

    def triage_explain(self, item_id, **kwargs):
        if item_id != "item-1":
            return {
                "item": {"id": item_id, "title": "Triage item"},
                "candidate_count": 0,
                "returned_count": 0,
                "suggested_primary_id": item_id,
                "candidates": [],
            }
        return {
            "item": {"id": "item-1", "title": "OpenAI launch post"},
            "candidate_count": 1,
            "returned_count": 1,
            "suggested_primary_id": "item-1",
            "candidates": [
                {
                    "id": "item-2",
                    "title": "OpenAI launch recap",
                    "review_state": "verified",
                    "similarity": 0.81,
                    "signals": ["same_domain", "title_overlap"],
                    "same_domain": True,
                    "suggested_primary_id": "item-1",
                }
            ],
        }

    def list_stories(self, limit: int = 8, min_items: int = 2):
        rows = [story for story in self.stories if int(story.get("item_count") or 0) >= min_items]
        return _clone(rows[:limit])

    def create_story(self, **payload):
        story = {
            "id": payload.get("id", f"story-manual-{len(self.stories) + 1}"),
            "title": payload.get("title", "Manual Brief"),
            "summary": payload.get("summary", ""),
            "status": payload.get("status", "active"),
            "score": 70.0,
            "confidence": 0.8,
            "item_count": 1,
            "source_count": 1,
            "primary_item_id": "item-1",
            "entities": ["OpenAI"],
            "source_names": ["OpenAI Blog"],
            "primary_evidence": [],
            "secondary_evidence": [],
            "timeline": [],
            "contradictions": [],
            "generated_at": "2026-03-06T00:00:00+00:00",
            "updated_at": "2026-03-06T00:00:00+00:00",
        }
        self.stories.insert(0, story)
        return _clone(story)

    def create_story_from_triage(self, **payload):
        item_ids = [str(item_id).strip() for item_id in payload.get("item_ids") or [] if str(item_id).strip()]
        selected = [item for item in self.triage_items if item["id"] in item_ids]
        primary = selected[0] if selected else self.triage_items[0]
        secondaries = selected[1:]
        story = {
            "id": "story-triage-seed",
            "title": payload.get("title") or "Triage Seed",
            "summary": payload.get("summary") or "Seeded from triage queue.",
            "status": payload.get("status") or "monitoring",
            "score": max(float(item.get("score", 0) or 0) for item in selected) if selected else 0.0,
            "confidence": max(float(item.get("confidence", 0) or 0) for item in selected) if selected else 0.0,
            "item_count": len(selected) or 1,
            "source_count": len({str(item.get("source_name") or "") for item in selected}) or 1,
            "primary_item_id": primary["id"],
            "entities": ["OpenAI"],
            "source_names": [str(item.get("source_name") or "Unknown") for item in selected] or ["OpenAI Blog"],
            "primary_evidence": [
                {
                    "item_id": primary["id"],
                    "title": primary["title"],
                    "url": primary["url"],
                    "source_name": primary.get("source_name", "Unknown"),
                    "source_type": primary.get("source_type", "generic"),
                    "review_state": primary.get("review_state", "new"),
                }
            ],
            "secondary_evidence": [
                {
                    "item_id": item["id"],
                    "title": item["title"],
                    "url": item["url"],
                    "source_name": item.get("source_name", "Unknown"),
                    "source_type": item.get("source_type", "generic"),
                    "review_state": item.get("review_state", "new"),
                }
                for item in secondaries
            ],
            "timeline": [],
            "contradictions": [],
            "generated_at": "2026-03-06T00:10:00+00:00",
            "updated_at": "2026-03-06T00:10:00+00:00",
        }
        self.stories = [story] + [existing for existing in self.stories if existing["id"] != story["id"]]
        return _clone(story)

    def show_story(self, identifier: str):
        for story in self.stories:
            if story["id"] == identifier:
                return _clone(story)
        return None

    def update_story(self, identifier: str, **kwargs):
        for story in self.stories:
            if story["id"] == identifier:
                story.update({key: value for key, value in kwargs.items() if value is not None})
                story["updated_at"] = "2026-03-06T00:15:00+00:00"
                return _clone(story)
        return None

    def delete_story(self, identifier: str):
        for index, story in enumerate(self.stories):
            if story["id"] == identifier:
                removed = self.stories.pop(index)
                return _clone(removed)
        return None

    def story_graph(self, identifier: str, **kwargs):
        story = self.show_story(identifier)
        if story is None:
            return None
        return self._base_story_graph(story)

    def export_story(self, identifier: str, **kwargs):
        story = self.show_story(identifier)
        title = story["title"] if story else "Story"
        return f"# {title}\n\n- story_id: {identifier}\n"


def _find_free_port() -> int:
    with contextlib.closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def _wait_for_port(port: int, timeout: float = 8.0) -> None:
    deadline = time.time() + timeout
    while time.time() < deadline:
        with contextlib.closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
            sock.settimeout(0.2)
            if sock.connect_ex(("127.0.0.1", port)) == 0:
                return
        time.sleep(0.1)
    raise RuntimeError(f"console server did not start on port {port}")


def _bind_page_logging(page: Page, label: str) -> None:
    page.set_default_timeout(10000)
    page.on("pageerror", lambda error: print(f"[console-browser-smoke] {label} pageerror: {error}"))
    def handle_console(message) -> None:
        if message.type not in {"error", "warning"}:
            return
        print(f"[console-browser-smoke] {label} console:{message.type}: {message.text}")

    page.on("console", handle_console)
    page.on("dialog", lambda dialog: dialog.accept())


def _wait_for_console_ready(page: Page) -> None:
    page.wait_for_selector("#create-watch-form", state="attached", timeout=10000)
    page.wait_for_function("() => document.querySelector('#watch-list')?.textContent?.includes('Launch Ops')", timeout=10000)
    page.wait_for_function("() => document.querySelector('#route-form') && document.querySelector('#triage-list') && document.querySelector('#story-list')", timeout=10000)


def _wait_for_active_rail(page: Page, nav_id: str, expected_hash: str) -> None:
    page.wait_for_function(
        """([selector, hashValue]) => {
            const button = document.querySelector(selector);
            return !!button
                && button.getAttribute('aria-current') === 'page'
                && button.classList.contains('active')
                && window.location.hash === hashValue;
        }""",
        arg=[f"#{nav_id}", expected_hash],
        timeout=10000,
    )


def _wait_for_responsive_contract(
    page: Page,
    *,
    viewport: str,
    density: str,
    pane: str,
    modal: str,
    action_sheet: str,
) -> None:
    expected = {
        "responsiveViewport": viewport,
        "densityMode": density,
        "paneContract": pane,
        "modalPresentation": modal,
        "actionSheetMode": action_sheet,
    }
    deadline = time.time() + 10
    current = {}
    while time.time() < deadline:
        current = page.evaluate(
            """() => ({
                responsiveViewport: document.body?.dataset.responsiveViewport || "",
                densityMode: document.body?.dataset.densityMode || "",
                paneContract: document.body?.dataset.paneContract || "",
                modalPresentation: document.body?.dataset.modalPresentation || "",
                actionSheetMode: document.body?.dataset.actionSheetMode || "",
            })"""
        )
        if current == expected:
            return
        page.wait_for_timeout(150)
    raise AssertionError(f"responsive contract mismatch: expected {expected}, got {current}")


def _click(page: Page, selector: str) -> None:
    locator = page.locator(selector).first
    locator.wait_for(state="attached", timeout=10000)
    try:
        locator.click(force=True)
    except Exception:
        locator.evaluate("(node) => node.click()")


def _submit_form(page: Page, selector: str) -> None:
    page.locator(selector).evaluate("(form) => form.requestSubmit()")


def _goto(page: Page, url: str) -> None:
    page.goto(url, wait_until="domcontentloaded", timeout=20000)


def _launch_browser(playwright: Playwright):
    launch_attempts = [
        {"channel": "chrome", "headless": True},
        {"headless": True},
    ]
    errors = []
    for options in launch_attempts:
        try:
            return playwright.chromium.launch(**options)
        except Exception as exc:  # pragma: no cover - depends on local browser availability
            errors.append(f"{options}: {exc}")
    raise RuntimeError("Could not launch a Playwright browser. Attempts: " + " | ".join(errors))


def _exercise_deep_link_and_existing_flow(page: Page, base_url: str) -> None:
    print("[console-browser-smoke] deep-link watch")
    _goto(page, f"{base_url}/?watch_search=Launch#section-cockpit")
    _wait_for_console_ready(page)
    page.wait_for_function("() => window.location.hash === '#section-cockpit'", timeout=10000)
    page.wait_for_function("() => window.location.search.includes('watch_search=Launch')", timeout=10000)
    page.wait_for_function("() => document.querySelector('[data-watch-search]')?.value === 'Launch'", timeout=10000)
    page.wait_for_function("() => document.querySelector('#watch-detail')?.textContent?.includes('Launch Ops')", timeout=10000)

    print("[console-browser-smoke] palette run-due")
    page.evaluate("openCommandPalette()")
    page.wait_for_selector(".palette-backdrop.open", timeout=10000)
    page.fill("#command-palette-input", "run due")
    page.keyboard.press("Enter")
    page.wait_for_function("() => document.body.textContent.includes('Due missions dispatched')", timeout=10000)
    page.keyboard.press("Escape")
    page.wait_for_function("() => !document.querySelector('.palette-backdrop')?.classList.contains('open')", timeout=10000)


def _exercise_navigation_convergence(page: Page) -> None:
    print("[console-browser-smoke] navigation convergence")
    page.wait_for_function("() => document.querySelectorAll('.topbar-nav .nav-pill').length === 4", timeout=10000)
    _wait_for_active_rail(page, "nav-missions", "#section-cockpit")
    _click(page, "#nav-review")
    _wait_for_active_rail(page, "nav-review", "#section-triage")
    _click(page, "#nav-delivery")
    _wait_for_active_rail(page, "nav-delivery", "#section-ops")
    _click(page, "#nav-intake")
    _wait_for_active_rail(page, "nav-intake", "#section-intake")
    _click(page, "#nav-missions")
    _wait_for_active_rail(page, "nav-missions", "#section-board")


def _exercise_saved_views_and_dock(page: Page, base_url: str, browser) -> Page:
    print("[console-browser-smoke] save view and set default")
    _goto(page, f"{base_url}/?triage_filter=verified#section-triage")
    _wait_for_console_ready(page)
    page.wait_for_function("() => window.location.hash === '#section-triage'", timeout=10000)
    page.wait_for_function("() => window.location.search.includes('triage_filter=verified')", timeout=10000)
    page.wait_for_function("() => document.querySelector('[data-triage-card=\"item-2\"]')?.classList.contains('selected')", timeout=10000)
    _click(page, "#context-summary")
    page.wait_for_function("() => document.querySelector('#context-summary')?.getAttribute('aria-expanded') === 'true'", timeout=10000)
    page.fill("#context-save-name", "Verified Queue")
    _click(page, "#context-save-submit")
    page.wait_for_function("() => document.querySelector('#context-lens-saved')?.textContent?.includes('Verified Queue')", timeout=10000)
    _click(page, "[data-context-saved-pin='0']")
    page.wait_for_function("() => document.querySelector('[data-context-dock-open=\"0\"]')?.textContent?.includes('Verified Queue')", timeout=10000)
    _click(page, "[data-context-saved-default='0']")
    page.wait_for_function(
        "() => JSON.parse(localStorage.getItem('datapulse.console.context-saved-views.v1') || '[]')[0]?.isDefault === true",
        timeout=10000,
    )

    print("[console-browser-smoke] default boot and dock restore")
    next_page = browser.new_page()
    _bind_page_logging(next_page, "page-2")
    _goto(next_page, base_url)
    _wait_for_console_ready(next_page)
    next_page.wait_for_function("() => window.location.hash === '#section-triage'", timeout=10000)
    next_page.wait_for_function("() => window.location.search.includes('triage_filter=verified')", timeout=10000)
    next_page.wait_for_function("() => document.querySelector('[data-triage-card=\"item-2\"]')?.classList.contains('selected')", timeout=10000)
    next_page.wait_for_function("() => document.querySelector('[data-context-dock-open=\"0\"]')?.textContent?.includes('Verified Queue')", timeout=10000)
    _wait_for_active_rail(next_page, "nav-review", "#section-triage")
    _click(next_page, "[data-context-section='section-story']")
    next_page.wait_for_function("() => window.location.hash === '#section-story'", timeout=10000)
    _wait_for_active_rail(next_page, "nav-review", "#section-story")
    _click(next_page, "[data-context-section='section-triage']")
    next_page.wait_for_function("() => window.location.hash === '#section-triage'", timeout=10000)
    _click(next_page, "[data-context-dock-manage]")
    next_page.wait_for_function(
        "() => document.body.dataset.contextLensOpen === 'true' && document.querySelector('#context-lens-backdrop')?.classList.contains('open')",
        timeout=10000,
    )
    _click(next_page, "#context-lens-close")
    next_page.wait_for_function(
        "() => document.body.dataset.contextLensOpen !== 'true' && document.querySelector('#context-summary')?.getAttribute('aria-expanded') === 'false'",
        timeout=10000,
    )
    next_page.evaluate("jumpToSection('section-intake')")
    next_page.wait_for_function("() => window.location.hash === '#section-intake'", timeout=10000)
    _wait_for_active_rail(next_page, "nav-intake", "#section-intake")
    _click(next_page, "[data-context-dock-open='0']")
    next_page.wait_for_function("() => window.location.hash === '#section-triage'", timeout=10000)
    next_page.wait_for_function("() => window.location.search.includes('triage_filter=verified')", timeout=10000)
    _wait_for_active_rail(next_page, "nav-review", "#section-triage")
    return next_page


def _exercise_route_crud(page: Page) -> None:
    print("[console-browser-smoke] route crud")
    page.evaluate("jumpToSection('section-ops')")
    page.wait_for_function("() => window.location.hash === '#section-ops'", timeout=10000)
    _wait_for_active_rail(page, "nav-delivery", "#section-ops")
    page.wait_for_function(
        """() => {
            const primary = document.querySelector('[data-card-action-primary] button[data-route-edit="ops-webhook"]');
            const secondary = document.querySelector('[data-card-action-secondary] button[data-route-attach="ops-webhook"]');
            const danger = document.querySelector('[data-card-action-danger] button[data-route-delete="ops-webhook"]');
            return !!primary && !!secondary && !!danger;
        }""",
        timeout=10000,
    )
    page.fill("#route-form [name='name']", "shadow-webhook")
    page.fill("#route-form [name='webhook_url']", "https://hooks.example.com/shadow")
    _submit_form(page, "#route-form")
    page.wait_for_timeout(1500)
    assert page.evaluate("() => !!document.querySelector('[data-route-edit=\"shadow-webhook\"]')"), "shadow-webhook route was not rendered after create"
    page.wait_for_function(
        """() => {
            const primary = document.querySelector('[data-card-action-primary] button[data-route-attach="shadow-webhook"]');
            const secondary = document.querySelector('[data-card-action-secondary] button[data-route-edit="shadow-webhook"]');
            const danger = document.querySelector('[data-card-action-danger] button[data-route-delete="shadow-webhook"]');
            return !!primary && !!secondary && !!danger;
        }""",
        timeout=10000,
    )
    page.evaluate("editRouteInDeck('shadow-webhook')")
    page.wait_for_function("() => document.querySelector('#route-form [name=\"name\"]')?.value === 'shadow-webhook'", timeout=10000)
    page.fill("#route-form [name='description']", "Shadow webhook route")
    page.fill("#route-form [name='webhook_url']", "https://hooks.example.com/shadow-v2")
    _submit_form(page, "#route-form")
    page.wait_for_timeout(1000)
    assert page.evaluate("() => !!document.querySelector('[data-route-delete=\"shadow-webhook\"]')"), "shadow-webhook route was not available after update"
    page.evaluate("window.confirm = () => true")
    page.evaluate("deleteRouteFromBoard('shadow-webhook')")
    page.wait_for_function("() => !document.querySelector('[data-route-edit=\"shadow-webhook\"]')", timeout=10000)


def _exercise_triage_to_story(page: Page, base_url: str) -> None:
    print("[console-browser-smoke] triage to story")
    _goto(page, f"{base_url}/?triage_filter=all#section-triage")
    _wait_for_console_ready(page)
    page.wait_for_function("() => window.location.hash === '#section-triage'", timeout=10000)
    _wait_for_active_rail(page, "nav-review", "#section-triage")
    page.wait_for_function(
        """() => {
            const primary = document.querySelector('[data-card-action-primary] button[data-triage-state="escalated"][data-triage-id="item-1"]');
            const verify = document.querySelector('[data-card-action-secondary] button[data-triage-state="verified"][data-triage-id="item-1"]');
            const story = document.querySelector('[data-card-action-secondary] button[data-empty-jump="section-story"]');
            const danger = document.querySelector('[data-card-action-danger] button[data-triage-delete="item-1"]');
            return !!primary && !!verify && !!story && !!danger;
        }""",
        timeout=10000,
    )
    page.wait_for_function(
        """() => {
            const primary = document.querySelector('[data-card-action-primary] button[data-triage-story="item-2"]');
            const secondary = document.querySelector('[data-card-action-secondary] button[data-triage-explain="item-2"]');
            const danger = document.querySelector('[data-card-action-danger] button[data-triage-delete="item-2"]');
            return !!primary && !!secondary && !!danger;
        }""",
        timeout=10000,
    )
    _click(page, "[data-triage-story='item-2']")
    page.wait_for_timeout(2000)
    assert page.evaluate("() => window.location.hash === '#section-story'"), "triage-to-story flow did not jump to section-story"
    _wait_for_active_rail(page, "nav-review", "#section-story")
    assert page.evaluate("() => document.querySelector('[data-story-card=\"story-triage-seed\"]')?.classList.contains('selected')"), "story-triage-seed was not selected after create"
    assert page.evaluate("() => document.querySelector('#story-list')?.textContent?.includes('Triage Seed')"), "story list did not include Triage Seed"
    assert page.evaluate("() => document.querySelector('#story-detail')?.textContent?.includes('Seeded from triage queue.')"), "story detail did not show seeded summary"
    page.wait_for_function(
        """() => {
            const primary = document.querySelector('[data-card-action-primary] button[data-story-open="story-triage-seed"]');
            const preview = document.querySelector('[data-card-action-secondary] button[data-story-preview="story-triage-seed"]');
            const archive = document.querySelector('[data-card-action-secondary] button[data-story-quick-status="story-triage-seed"]');
            const hierarchy = primary?.closest('.action-hierarchy');
            return !!primary && !!preview && !!archive && !!hierarchy && !hierarchy.querySelector('[data-card-action-danger]');
        }""",
        timeout=10000,
    )


def _exercise_responsive_interaction_safety(page: Page) -> None:
    print("[console-browser-smoke] responsive interaction safety")
    page.set_viewport_size({"width": 980, "height": 1100})
    _wait_for_responsive_contract(
        page,
        viewport="compact",
        density="compact",
        pane="stacked",
        modal="sheet",
        action_sheet="inline",
    )
    page.set_viewport_size({"width": 720, "height": 1280})
    _wait_for_responsive_contract(
        page,
        viewport="touch",
        density="touch",
        pane="single",
        modal="fullscreen",
        action_sheet="sheet",
    )
    _click(page, "#context-summary")
    page.wait_for_function(
        "() => document.body.dataset.contextLensOpen === 'true' && document.querySelector('#context-lens-backdrop')?.classList.contains('open')",
        timeout=10000,
    )
    _click(page, "#context-lens-close")
    page.wait_for_function(
        "() => document.body.dataset.contextLensOpen !== 'true' && document.querySelector('#context-summary')?.getAttribute('aria-expanded') === 'false'",
        timeout=10000,
    )
    page.wait_for_function(
        """() => {
            const primary = document.querySelector('[data-card-action-primary] button[data-run-watch="launch-ops"]');
            const hierarchy = primary?.closest('.action-hierarchy');
            const secondary = hierarchy?.querySelector('[data-card-action-secondary]');
            const danger = hierarchy?.querySelector('[data-card-action-danger]');
            const sheet = hierarchy?.querySelector('[data-card-action-sheet]');
            const sheetSecondary = hierarchy?.querySelector('[data-card-action-sheet-secondary] button[data-watch-open="launch-ops"]');
            const sheetDanger = hierarchy?.querySelector('[data-card-action-sheet-danger] button[data-delete-watch="launch-ops"]');
            return !!primary
                && !!secondary
                && !!danger
                && !!sheet
                && getComputedStyle(secondary).display === 'none'
                && getComputedStyle(danger).display === 'none'
                && getComputedStyle(sheet).display !== 'none'
                && !!sheetSecondary
                && !!sheetDanger;
        }""",
        timeout=10000,
    )
    page.evaluate(
        """() => {
            const primary = document.querySelector('[data-card-action-primary] button[data-run-watch="launch-ops"]');
            const hierarchy = primary?.closest('.action-hierarchy');
            const sheet = hierarchy?.querySelector('[data-card-action-sheet]');
            if (sheet) {
                sheet.open = true;
            }
        }"""
    )
    page.wait_for_function(
        """() => {
            const primary = document.querySelector('[data-card-action-primary] button[data-run-watch="launch-ops"]');
            const hierarchy = primary?.closest('.action-hierarchy');
            const sheet = hierarchy?.querySelector('[data-card-action-sheet]');
            return !!sheet?.open && !!hierarchy?.querySelector('[data-card-action-sheet-secondary] button[data-watch-open="launch-ops"]');
        }""",
        timeout=10000,
    )
    page.set_viewport_size({"width": 1360, "height": 1100})
    _wait_for_responsive_contract(
        page,
        viewport="desktop",
        density="comfortable",
        pane="split",
        modal="side-panel",
        action_sheet="inline",
    )


def main() -> int:
    reader = _SmokeReader()
    app = create_app(reader_factory=lambda: reader)
    port = _find_free_port()
    server = uvicorn.Server(uvicorn.Config(app, host="127.0.0.1", port=port, log_level="error"))
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    _wait_for_port(port)
    base_url = f"http://127.0.0.1:{port}"

    try:
        with sync_playwright() as playwright:
            browser = _launch_browser(playwright)
            context = browser.new_context()
            page = context.new_page()
            _bind_page_logging(page, "page-1")
            _exercise_deep_link_and_existing_flow(page, base_url)
            _exercise_navigation_convergence(page)
            second_page = _exercise_saved_views_and_dock(page, base_url, context)
            _exercise_route_crud(second_page)
            _exercise_triage_to_story(second_page, base_url)
            _exercise_responsive_interaction_safety(second_page)
            browser.close()
    finally:
        server.should_exit = True
        thread.join(timeout=5)

    print("[console-browser-smoke] pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
