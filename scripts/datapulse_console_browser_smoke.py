#!/usr/bin/env python3
from __future__ import annotations

import contextlib
import socket
import threading
import time

import uvicorn

from datapulse.console_server import create_app

try:
    from playwright.sync_api import sync_playwright
except ImportError as exc:  # pragma: no cover - exercised in runtime only
    raise SystemExit("Playwright is not installed. Run with: uv run --with playwright python scripts/datapulse_console_browser_smoke.py") from exc


class _SmokeReader:
    def __init__(self) -> None:
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

    def list_watches(self, include_disabled: bool = False):
        return [dict(item) for item in self.watches if include_disabled or item.get("enabled", True)]

    def show_watch(self, identifier: str):
        for watch in self.watches:
            if watch["id"] == identifier:
                payload = dict(watch)
                payload.update(
                    {
                        "run_stats": {"total": 1, "success": 1, "error": 0},
                        "last_failure": None,
                        "retry_advice": None,
                        "recent_results": [],
                        "result_stats": {"stored_result_count": 0, "returned_result_count": 0, "latest_result_at": ""},
                        "result_filters": {"window_count": 0, "states": [], "sources": [], "domains": []},
                        "recent_alerts": [],
                        "delivery_stats": {"recent_alert_count": 0, "recent_error_count": 0, "last_alert_at": ""},
                        "timeline_strip": [],
                    }
                )
                return payload
        return None

    def list_watch_results(self, identifier: str, limit: int = 10, min_confidence: float = 0.0):
        return []

    def create_watch(self, **kwargs):
        next_id = f"watch-{len(self.watches) + 1}"
        mission = {
            "id": next_id,
            "name": kwargs["name"],
            "query": kwargs["query"],
            "enabled": True,
            "platforms": kwargs.get("platforms") or [],
            "sites": [],
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
        return dict(mission)

    def set_watch_alert_rules(self, identifier: str, *, alert_rules=None):
        for watch in self.watches:
            if watch["id"] == identifier:
                watch["alert_rules"] = list(alert_rules or [])
                watch["alert_rule_count"] = len(watch["alert_rules"])
                return self.show_watch(identifier)
        return None

    async def run_watch(self, identifier: str):
        return {"mission": {"id": identifier}, "run": {"status": "success", "item_count": 0}, "items": [], "alert_events": []}

    async def run_due_watches(self, limit=None):
        return {"due_count": 1, "run_count": 1, "results": [{"mission_id": "launch-ops", "status": "success"}]}

    def disable_watch(self, identifier: str):
        for watch in self.watches:
            if watch["id"] == identifier:
                watch["enabled"] = False
                return dict(watch)
        return None

    def enable_watch(self, identifier: str):
        for watch in self.watches:
            if watch["id"] == identifier:
                watch["enabled"] = True
                return dict(watch)
        return None

    def delete_watch(self, identifier: str):
        for index, watch in enumerate(self.watches):
            if watch["id"] == identifier:
                removed = self.watches.pop(index)
                return dict(removed)
        return None

    def list_alerts(self, limit: int = 20, mission_id: str | None = None):
        return [{"id": "alert-1", "mission_name": "Launch Ops", "rule_name": "console-threshold", "summary": "Launch Ops triggered."}]

    def list_alert_routes(self):
        return [{"name": "ops-webhook", "channel": "webhook"}]

    def alert_route_health(self, limit: int = 100):
        return [
            {
                "name": "ops-webhook",
                "channel": "webhook",
                "configured": True,
                "status": "healthy",
                "event_count": 4,
                "delivered_count": 4,
                "failure_count": 0,
                "success_rate": 1.0,
                "last_event_at": "2026-03-06T00:00:10+00:00",
                "last_summary": "Route healthy",
            }
        ]

    def watch_status_snapshot(self):
        return {"state": "running", "heartbeat_at": "2026-03-06T00:00:00+00:00", "metrics": {"cycles_total": 3, "runs_total": 2, "alerts_total": 1, "error_total": 0}, "last_error": ""}

    def ops_snapshot(self):
        return {
            "collector_summary": {"total": 2, "ok": 2, "warn": 0, "error": 0, "available": 2, "unavailable": 0},
            "collector_tiers": {"tier_0": {"total": 2, "ok": 2, "warn": 0, "error": 0}},
            "degraded_collectors": [],
            "collector_drilldown": [],
            "watch_metrics": {"success_rate": 1.0},
            "watch_summary": {"total": len(self.watches), "enabled": sum(1 for item in self.watches if item.get("enabled", True)), "healthy": 1, "degraded": 0, "idle": 0, "disabled": sum(1 for item in self.watches if not item.get("enabled", True)), "due": 1},
            "watch_health": [{"id": "launch-ops", "status": "healthy", "is_due": True, "success_rate": 1.0}],
            "route_summary": {"total": 1, "healthy": 1, "degraded": 0, "missing": 0, "idle": 0},
            "route_drilldown": [{"name": "ops-webhook", "channel": "webhook", "status": "healthy", "success_rate": 1.0, "mission_count": 1, "rule_count": 1, "event_count": 4, "failure_count": 0, "last_summary": "Route healthy"}],
            "route_timeline": [{"created_at": "2026-03-06T00:00:10+00:00", "route": "ops-webhook", "status": "delivered", "mission_name": "Launch Ops", "summary": "Delivered"}],
            "recent_failures": [],
            "recent_alerts": self.list_alerts(),
            "daemon": self.watch_status_snapshot(),
        }

    def triage_list(self, **kwargs):
        return [{"id": "item-1", "title": "OpenAI launch post", "review_state": "new", "score": 81, "confidence": 0.91, "url": "https://example.com/openai-launch", "review_notes": []}]

    def triage_stats(self):
        return {"total": 1, "open_count": 1, "closed_count": 0, "note_count": 0, "states": {"new": 1, "triaged": 0, "verified": 0, "duplicate": 0, "ignored": 0, "escalated": 0}}

    def triage_update(self, item_id, **kwargs):
        return {"id": item_id, "review_state": kwargs["state"]}

    def triage_note(self, item_id, **kwargs):
        return {"id": item_id, "review_notes": [{"note": kwargs["note"]}]}

    def triage_explain(self, item_id, **kwargs):
        return {"item": {"id": item_id, "title": "OpenAI launch post"}, "candidate_count": 0, "returned_count": 0, "suggested_primary_id": item_id, "candidates": []}

    def list_stories(self, limit: int = 8, min_items: int = 2):
        return [dict(item) for item in self.stories]

    def show_story(self, identifier: str):
        for story in self.stories:
            if story["id"] == identifier:
                return dict(story)
        return None

    def update_story(self, identifier: str, **kwargs):
        for story in self.stories:
            if story["id"] == identifier:
                story.update({key: value for key, value in kwargs.items() if value is not None})
                return dict(story)
        return None

    def story_graph(self, identifier: str, **kwargs):
        return {"story": {"id": identifier, "title": "OpenAI Launch"}, "nodes": [{"id": identifier, "label": "OpenAI Launch", "kind": "story", "item_count": 3}, {"id": "entity:openai", "label": "OpenAI", "kind": "entity", "entity_type": "ORG", "in_story_source_count": 2}], "edges": [{"source": identifier, "target": "entity:openai", "relation_type": "MENTIONED_IN_STORY", "kind": "story_entity"}], "entity_count": 1, "relation_count": 0, "edge_count": 1}

    def export_story(self, identifier: str, **kwargs):
        return "# OpenAI Launch\n"


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


def main() -> int:
    reader = _SmokeReader()
    app = create_app(reader_factory=lambda: reader)
    port = _find_free_port()
    server = uvicorn.Server(uvicorn.Config(app, host="127.0.0.1", port=port, log_level="error"))
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    _wait_for_port(port)

    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(channel="chrome", headless=True)
            page = browser.new_page()
            page.on("pageerror", lambda error: print("[console-browser-smoke] pageerror:", error))
            page.on("console", lambda message: print(f"[console-browser-smoke] console:{message.type}: {message.text}"))
            print("[console-browser-smoke] goto")
            page.goto(f"http://127.0.0.1:{port}/", wait_until="load")
            page.wait_for_selector("body", timeout=10000)
            try:
                page.wait_for_selector("#create-watch-presets", timeout=5000)
            except Exception:
                print("[console-browser-smoke] title:", page.title())
                print("[console-browser-smoke] body-snippet:", page.content()[:800])
                raise
            print("[console-browser-smoke] preset")
            page.click("[data-create-watch-preset='launch']")
            page.wait_for_function("() => document.querySelector('#create-watch-preview')?.textContent?.includes('Launch Pulse')", timeout=10000)
            page.wait_for_function("() => document.querySelector('#create-watch-suggestions')?.textContent?.includes('Mission deck sees')", timeout=10000)
            print("[console-browser-smoke] palette")
            page.evaluate("openCommandPalette()")
            page.wait_for_selector(".palette-backdrop.open", timeout=10000)
            page.fill("#command-palette-input", "run due")
            page.keyboard.press("Enter")
            page.wait_for_function("() => document.body.textContent.includes('Due missions dispatched')", timeout=10000)
            print("[console-browser-smoke] create")
            page.click("button[type='submit']")
            page.wait_for_function("() => document.querySelector('#console-action-history')?.textContent?.includes('Created Launch Pulse')", timeout=10000)
            print("[console-browser-smoke] undo")
            page.click("[data-action-undo]")
            page.wait_for_function("() => !document.querySelector('#console-action-history')?.textContent?.includes('Created Launch Pulse')", timeout=10000)
            browser.close()
    finally:
        server.should_exit = True
        thread.join(timeout=5)

    print("[console-browser-smoke] pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
