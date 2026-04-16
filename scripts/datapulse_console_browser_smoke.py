#!/usr/bin/env python3
from __future__ import annotations

import contextlib
import json
import re
import socket
import threading
import time
from collections.abc import Iterable, Mapping, Sequence
from copy import deepcopy
from typing import Any, cast
from urllib.parse import urlsplit

import uvicorn

from datapulse.console_server import create_app

try:
    from playwright.sync_api import Page, Playwright, TimeoutError as PlaywrightTimeoutError, sync_playwright
except ImportError as exc:  # pragma: no cover - exercised in runtime only
    raise SystemExit("Playwright is not installed. Run with: uv run --with playwright python scripts/datapulse_console_browser_smoke.py") from exc


Row = dict[str, object]


def _clone(payload: Any) -> Any:
    return deepcopy(payload)


def _log(message: str) -> None:
    print(message, flush=True)


def _row(value: object) -> Row | None:
    return cast(Row, value) if isinstance(value, dict) else None


def _rows(value: object) -> list[Row]:
    if not isinstance(value, list):
        return []
    return [cast(Row, item) for item in value if isinstance(item, dict)]


def _strings(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    return [normalized for item in value if (normalized := str(item or "").strip())]


def _as_int(value: object, default: int = 0) -> int:
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    if isinstance(value, str):
        normalized = value.strip()
        if not normalized:
            return default
        try:
            return int(normalized)
        except ValueError:
            try:
                return int(float(normalized))
            except ValueError:
                return default
    return default


class _SmokeReader:
    def __init__(self) -> None:
        self.routes: list[Row] = [
            {
                "name": "ops-webhook",
                "channel": "webhook",
                "description": "Primary ops webhook",
                "webhook_url": "https://hooks.example.com/ops",
            }
        ]
        self.watches: list[Row] = [
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
        self.triage_items: list[Row] = [
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
        self.stories: list[Row] = [
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
        self.report_briefs: list[Row] = [
            {
                "id": "brief-openai-market",
                "title": "OpenAI Market Brief",
                "audience": "internal",
                "objective": "Track launch evidence and market reaction.",
                "status": "draft",
                "updated_at": "2026-03-06T00:00:00+00:00",
            }
        ]
        self.claim_cards: list[Row] = [
            {
                "id": "claim-openai-trend",
                "brief_id": "brief-openai-market",
                "title": "OpenAI launch signal remains elevated",
                "statement": "Demand signals remain elevated after the OpenAI launch window.",
                "rationale": "Cross-source evidence clusters around launch, ecosystem reaction, and analyst follow-up.",
                "confidence": 0.91,
                "status": "reviewed",
                "source_item_ids": ["item-1"],
                "citation_bundle_ids": ["bundle-openai"],
                "updated_at": "2026-03-06T00:00:00+00:00",
            }
        ]
        self.report_sections: list[Row] = [
            {
                "id": "section-market-context",
                "report_id": "report-openai-market",
                "title": "Market context",
                "position": 1,
                "summary": "Summarize market reaction and evidence-backed signals.",
                "claim_card_ids": ["claim-openai-trend"],
                "status": "draft",
                "updated_at": "2026-03-06T00:00:00+00:00",
            }
        ]
        self.citation_bundles: list[Row] = [
            {
                "id": "bundle-openai",
                "claim_card_id": "claim-openai-trend",
                "label": "OpenAI bundle",
                "source_item_ids": ["item-1"],
                "source_urls": ["https://example.com/openai-launch"],
                "note": "Primary launch coverage bundle.",
            }
        ]
        self.reports: list[Row] = [
            {
                "id": "report-openai-market",
                "brief_id": "brief-openai-market",
                "title": "OpenAI Market Report",
                "status": "draft",
                "audience": "internal",
                "summary": "A persisted report shell for launch-related market tracking.",
                "section_ids": ["section-market-context"],
                "claim_card_ids": ["claim-openai-trend"],
                "citation_bundle_ids": ["bundle-openai"],
                "export_profile_ids": ["profile-brief", "profile-full", "profile-sources", "profile-watch-pack"],
                "updated_at": "2026-03-06T00:00:00+00:00",
            }
        ]
        self.export_profiles: list[Row] = [
            {
                "id": "profile-brief",
                "report_id": "report-openai-market",
                "name": "brief",
                "output_format": "markdown",
                "include_sections": True,
                "include_claim_cards": False,
                "include_bundles": True,
                "include_export_profiles": True,
                "include_metadata": True,
                "status": "active",
            },
            {
                "id": "profile-full",
                "report_id": "report-openai-market",
                "name": "full",
                "output_format": "markdown",
                "include_sections": True,
                "include_claim_cards": True,
                "include_bundles": True,
                "include_export_profiles": True,
                "include_metadata": True,
                "status": "active",
            },
            {
                "id": "profile-sources",
                "report_id": "report-openai-market",
                "name": "sources",
                "output_format": "json",
                "include_sections": False,
                "include_claim_cards": True,
                "include_bundles": True,
                "include_export_profiles": True,
                "include_metadata": True,
                "status": "active",
            },
            {
                "id": "profile-watch-pack",
                "report_id": "report-openai-market",
                "name": "watch-pack",
                "output_format": "json",
                "include_sections": False,
                "include_claim_cards": False,
                "include_bundles": False,
                "include_export_profiles": True,
                "include_metadata": False,
                "status": "active",
            }
        ]
        self.delivery_subscriptions: list[Row] = []
        self.delivery_dispatch_records: list[Row] = []
        self.digest_profile: Row = {
            "language": "en",
            "timezone": "UTC",
            "frequency": "@daily",
            "default_delivery_target": {"kind": "route", "ref": "ops-webhook"},
        }
        self.digest_dispatch_records: list[Row] = []
        self.watch_runs_by_id: dict[str, list[Row]] = {
            "launch-ops": [
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
            ]
        }
        self.watch_results_by_id: dict[str, list[Row]] = {
            "launch-ops": [
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
            ]
        }
        self.watch_alerts_by_id: dict[str, list[Row]] = {
            "launch-ops": [
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
            ]
        }
        self.watch_last_failure_by_id: dict[str, Row] = {
            "launch-ops": {
                "id": "launch-ops:2026-03-05T23:00:00+00:00",
                "mission_id": "launch-ops",
                "status": "error",
                "item_count": 0,
                "trigger": "scheduled",
                "started_at": "2026-03-05T23:00:00+00:00",
                "finished_at": "2026-03-05T23:00:03+00:00",
                "error": "credentials missing",
            }
        }
        self.watch_retry_advice_by_id: dict[str, Row] = {
            "launch-ops": {
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
            }
        }

    @staticmethod
    def _timestamp() -> str:
        return "2026-03-06T00:00:00+00:00"

    @staticmethod
    def _slug(value: str, fallback: str) -> str:
        normalized = re.sub(r"[^a-z0-9]+", "-", str(value or "").strip().lower()).strip("-")
        return normalized or fallback

    def _make_id(self, prefix: str, value: str, rows: Sequence[Mapping[str, object]]) -> str:
        existing = {str(row.get("id") or "").strip() for row in rows}
        stem = self._slug(value, prefix)
        candidate = stem if stem.startswith(f"{prefix}-") else f"{prefix}-{stem}"
        if candidate not in existing:
            return candidate
        index = 2
        while f"{candidate}-{index}" in existing:
            index += 1
        return f"{candidate}-{index}"

    @staticmethod
    def _row_index(rows: Sequence[Mapping[str, object]], identifier: str, *, key: str = "id") -> int | None:
        normalized = str(identifier or "").strip()
        for index, row in enumerate(rows):
            if str(row.get(key) or "").strip() == normalized:
                return index
        return None

    def _upsert(self, rows: list[Row], item: Row, *, key: str = "id") -> Row:
        identifier = str(item.get(key) or "").strip()
        if not identifier:
            raise ValueError(f"Missing required row key: {key}")
        index = self._row_index(rows, identifier, key=key)
        if index is None:
            rows.insert(0, item)
        else:
            rows[index] = item
        return item

    @staticmethod
    def _unique_ids(values: Iterable[str]) -> list[str]:
        seen: list[str] = []
        for value in values:
            normalized = str(value or "").strip()
            if normalized and normalized not in seen:
                seen.append(normalized)
        return seen

    def _report_profiles(self, report_id: str) -> list[Row]:
        normalized = str(report_id or "").strip()
        return [row for row in self.export_profiles if str(row.get("report_id") or "").strip() == normalized]

    def _ensure_default_export_profiles(self, report_id: str) -> list[str]:
        normalized = str(report_id or "").strip()
        if not normalized:
            return []
        existing = {str(row.get("name") or "").strip().lower(): row for row in self._report_profiles(normalized)}
        templates = [
            {
                "id": f"profile-{self._slug(normalized, 'report')}-brief",
                "report_id": normalized,
                "name": "brief",
                "output_format": "markdown",
                "include_sections": True,
                "include_claim_cards": False,
                "include_bundles": True,
                "include_export_profiles": True,
                "include_metadata": True,
                "status": "active",
            },
            {
                "id": f"profile-{self._slug(normalized, 'report')}-full",
                "report_id": normalized,
                "name": "full",
                "output_format": "markdown",
                "include_sections": True,
                "include_claim_cards": True,
                "include_bundles": True,
                "include_export_profiles": True,
                "include_metadata": True,
                "status": "active",
            },
            {
                "id": f"profile-{self._slug(normalized, 'report')}-sources",
                "report_id": normalized,
                "name": "sources",
                "output_format": "json",
                "include_sections": False,
                "include_claim_cards": True,
                "include_bundles": True,
                "include_export_profiles": True,
                "include_metadata": True,
                "status": "active",
            },
            {
                "id": f"profile-{self._slug(normalized, 'report')}-watch-pack",
                "report_id": normalized,
                "name": "watch-pack",
                "output_format": "json",
                "include_sections": False,
                "include_claim_cards": False,
                "include_bundles": False,
                "include_export_profiles": True,
                "include_metadata": False,
                "status": "active",
            },
        ]
        ordered_ids: list[str] = []
        for template in templates:
            existing_profile = existing.get(str(template["name"]).lower())
            if existing_profile is None:
                self.export_profiles.append(template)
                ordered_ids.append(str(template["id"]))
            else:
                ordered_ids.append(str(existing_profile.get("id") or ""))
        report_index = self._row_index(self.reports, normalized)
        if report_index is not None:
            current = self.reports[report_index]
            current_ids = self._unique_ids([*_strings(current.get("export_profile_ids")), *ordered_ids])
            current["export_profile_ids"] = current_ids
            current["updated_at"] = self._timestamp()
        return [profile_id for profile_id in ordered_ids if profile_id]

    def _route_usage_names(self, route_name: str) -> list[str]:
        normalized = str(route_name or "").strip().lower()
        usage = []
        for watch in self.watches:
            for rule in _rows(watch.get("alert_rules")):
                routes = [route.lower() for route in _strings(rule.get("routes"))]
                if normalized and normalized in routes:
                    usage.append(str(watch.get("name") or watch.get("id") or route_name))
                    break
        return usage

    def _build_route_health(self, route: Mapping[str, object]) -> Row:
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
                    "item_count": _as_int(story.get("item_count")),
                    "source_count": _as_int(story.get("source_count")),
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

    @staticmethod
    def _watch_result_mode(watch: Mapping[str, object]) -> str:
        signature = " ".join(
            [
                str(watch.get("id") or ""),
                str(watch.get("name") or ""),
                str(watch.get("query") or ""),
            ]
        ).lower()
        if "no result" in signature or "no-result" in signature or "empty monitor" in signature:
            return "no_result"
        return "results"

    def _default_watch_results(self, watch: Mapping[str, object]) -> list[Row]:
        watch_id = str(watch.get("id") or "").strip() or "watch"
        watch_name = str(watch.get("name") or watch_id).strip() or watch_id
        if self._watch_result_mode(watch) == "no_result":
            return []
        return [
            {
                "id": f"{watch_id}-item-1",
                "title": f"{watch_name} signal",
                "url": f"https://example.com/{self._slug(watch_name, 'watch')}",
                "score": 78,
                "confidence": 0.88,
                "review_state": "new",
                "source_name": "Browser Smoke Feed",
                "source_type": "generic",
                "watch_filters": {
                    "state": "new",
                    "source": "browser smoke feed",
                    "domain": "example.com",
                },
            }
        ]

    @staticmethod
    def _result_filters(results: Sequence[Mapping[str, object]]) -> Row:
        if not results:
            return {
                "window_count": 0,
                "states": [],
                "sources": [],
                "domains": [],
            }
        state_counts: dict[str, int] = {}
        source_counts: dict[str, int] = {}
        domain_counts: dict[str, int] = {}
        for row in results:
            filters = _row(row.get("watch_filters")) or {}
            state_key = str(filters.get("state") or row.get("review_state") or "").strip().lower()
            source_key = str(filters.get("source") or row.get("source_name") or "").strip().lower()
            domain_key = str(filters.get("domain") or "").strip().lower()
            if state_key:
                state_counts[state_key] = state_counts.get(state_key, 0) + 1
            if source_key:
                source_counts[source_key] = source_counts.get(source_key, 0) + 1
            if domain_key:
                domain_counts[domain_key] = domain_counts.get(domain_key, 0) + 1
        return {
            "window_count": len(results),
            "states": [{"key": key, "label": key, "count": count} for key, count in state_counts.items()],
            "sources": [{"key": key, "label": key.title(), "count": count} for key, count in source_counts.items()],
            "domains": [{"key": key, "label": key, "count": count} for key, count in domain_counts.items()],
        }

    def _watch_detail(self, watch: Mapping[str, object]) -> Row:
        watch_id = str(watch.get("id") or "").strip()
        runs = _clone(self.watch_runs_by_id.get(watch_id, []))
        results = _clone(self.watch_results_by_id.get(watch_id, self._default_watch_results(watch)))
        alerts = _clone(self.watch_alerts_by_id.get(watch_id, []))
        success_runs = [row for row in runs if str(row.get("status") or "").strip().lower() == "success"]
        error_runs = [row for row in runs if str(row.get("status") or "").strip().lower() not in {"", "success"}]
        average_items = sum(_as_int(row.get("item_count")) for row in success_runs) / len(success_runs) if success_runs else 0.0
        latest_success = success_runs[0] if success_runs else None
        latest_failure = _clone(self.watch_last_failure_by_id.get(watch_id) or (error_runs[0] if error_runs else {}))
        retry_advice = _clone(self.watch_retry_advice_by_id.get(watch_id, {}))
        timeline_strip: list[Row] = []
        for alert in alerts:
            timeline_strip.append(
                {
                    "kind": "alert",
                    "time": str(alert.get("created_at") or ""),
                    "tone": "ok",
                    "label": f"alert: {str(alert.get('rule_name') or 'delivery')}",
                    "detail": f"{','.join(_strings(alert.get('delivered_channels')))} | {str(alert.get('summary') or '').strip()}",
                }
            )
        for result in results:
            timeline_strip.append(
                {
                    "kind": "result",
                    "time": str(watch.get("last_run_at") or self._timestamp()),
                    "tone": "ok",
                    "label": f"result: {str(result.get('title') or watch.get('name') or watch_id)}",
                    "detail": (
                        f"{str(result.get('source_name') or 'Source').strip()} | "
                        f"score={_as_int(result.get('score'))} | state={str(result.get('review_state') or 'new').strip()}"
                    ),
                }
            )
        return {
            **_clone(watch),
            "runs": runs,
            "run_stats": {
                "total": len(runs),
                "success": len(success_runs),
                "error": len(error_runs),
                "average_items": average_items,
                "last_status": str(watch.get("last_run_status") or ""),
                "last_error": str(latest_failure.get("error") or ""),
            },
            "last_failure": latest_failure,
            "retry_advice": retry_advice,
            "recent_results": results,
            "result_stats": {
                "stored_result_count": len(results),
                "returned_result_count": len(results),
                "latest_result_at": str(watch.get("last_run_at") or (latest_success or {}).get("finished_at") or ""),
            },
            "result_filters": self._result_filters(results),
            "recent_alerts": alerts,
            "delivery_stats": {
                "recent_alert_count": len(alerts),
                "recent_error_count": 0,
                "last_alert_at": str(alerts[0].get("created_at") or "") if alerts else "",
            },
            "timeline_strip": timeline_strip,
        }

    def list_watches(self, include_disabled: bool = False):
        rows = [watch for watch in self.watches if include_disabled or watch.get("enabled", True)]
        return _clone(rows)

    def show_watch(self, identifier: str):
        for watch in self.watches:
            if watch["id"] != identifier:
                continue
            return self._watch_detail(watch)
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
        self.watch_runs_by_id[next_id] = []
        self.watch_results_by_id[next_id] = []
        self.watch_alerts_by_id[next_id] = []
        return _clone(mission)

    def set_watch_alert_rules(self, identifier: str, *, alert_rules=None):
        for watch in self.watches:
            if watch["id"] == identifier:
                rules = _rows(alert_rules)
                watch["alert_rules"] = rules
                watch["alert_rule_count"] = len(rules)
                return self.show_watch(identifier)
        return None

    async def run_watch(self, identifier: str):
        watch = next((row for row in self.watches if str(row.get("id") or "").strip() == identifier), None)
        if watch is None:
            return {"mission": {"id": identifier}, "run": {"status": "error", "item_count": 0}, "items": [], "alert_events": []}
        results = self._default_watch_results(watch)
        alerts: list[Row] = []
        watch["last_run_at"] = self._timestamp()
        watch["last_run_status"] = "success"
        watch["is_due"] = False
        run = {
            "id": f"{identifier}:{self._timestamp()}",
            "mission_id": identifier,
            "status": "success",
            "item_count": len(results),
            "trigger": "manual",
            "started_at": self._timestamp(),
            "finished_at": self._timestamp(),
            "error": "",
        }
        self.watch_runs_by_id[identifier] = [run, *self.watch_runs_by_id.get(identifier, [])]
        self.watch_results_by_id[identifier] = results
        self.watch_alerts_by_id[identifier] = alerts
        return {
            "mission": {"id": identifier, "name": str(watch.get("name") or identifier)},
            "run": {"status": "success", "item_count": len(results)},
            "items": _clone(results),
            "alert_events": _clone(alerts),
        }

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
        watch = next((row for row in self.watches if str(row.get("id") or "").strip() == str(identifier or "").strip()), None)
        if watch is None:
            return None
        return {
            "surface": "mission_suggest",
            "mode": mode,
            "subject": {"kind": "WatchMission", "id": identifier},
            "precheck": self.ai_surface_precheck("mission_suggest", mode=mode),
            "output": {
                "contract_id": "datapulse_ai_watch_suggestion.v1",
                "payload": {
                    "summary": f"Mission `{watch.get('name') or identifier}` has 2 persisted result items and run readiness `ready`.",
                    "proposed_query": str(watch.get("query") or "OpenAI launch"),
                },
            },
            "runtime_facts": {"status": "fallback_used", "request_id": "mission-smoke-123"},
        }

    def ai_triage_assist(self, item_id, *, mode="assist", limit=5):
        item = next((row for row in self.triage_items if str(row.get("id") or "").strip() == str(item_id or "").strip()), None)
        if item is None:
            return None
        return {
            "surface": "triage_assist",
            "mode": mode,
            "subject": {"kind": "DataPulseItem", "id": item_id},
            "precheck": self.ai_surface_precheck("triage_assist", mode=mode),
            "output": {
                "contract_id": "datapulse_ai_triage_explain.v1",
                "payload": {
                    "item": {"id": item_id, "title": str(item.get("title") or item_id)},
                    "candidate_count": 1,
                    "returned_count": min(limit, 1),
                },
            },
            "runtime_facts": {"status": "fallback_used", "request_id": "triage-smoke-123"},
        }

    def ai_claim_draft(self, story_id, *, mode="assist", brief_id=""):
        story = next((row for row in self.stories if str(row.get("id") or "").strip() == str(story_id or "").strip()), None)
        if story is None:
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
                    "claim_cards": [{"id": "claim-openai-trend", "statement": f"{story.get('title') or story_id} remains elevated."}],
                },
            },
            "runtime_facts": {"status": "fallback_used", "request_id": "claim-smoke-123"},
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
        rows = [story for story in self.stories if _as_int(story.get("item_count")) >= min_items]
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

    def list_report_briefs(self, limit: int = 20, status: str | None = None, **_kwargs):
        rows = self.report_briefs
        if status:
            rows = [row for row in rows if row.get("status") == status]
        return _clone(rows[:limit])

    def create_report_brief(self, **payload):
        title = str(payload.get("title") or "Manual Brief").strip() or "Manual Brief"
        brief = {
            "id": str(payload.get("id") or self._make_id("brief", title, self.report_briefs)),
            "title": title,
            "audience": str(payload.get("audience") or "").strip(),
            "objective": str(payload.get("objective") or "").strip(),
            "intent": str(payload.get("intent") or "").strip(),
            "status": str(payload.get("status") or "draft").strip() or "draft",
            "updated_at": self._timestamp(),
        }
        self._upsert(self.report_briefs, brief)
        return _clone(brief)

    def show_report_brief(self, identifier: str):
        for brief in self.report_briefs:
            if brief["id"] == identifier:
                return _clone(brief)
        return None

    def update_report_brief(self, identifier: str, **payload):
        for brief in self.report_briefs:
            if brief["id"] == identifier:
                brief.update(payload)
                brief["updated_at"] = self._timestamp()
                return _clone(brief)
        return None

    def list_claim_cards(self, limit: int = 20, status: str | None = None, **_kwargs):
        rows = self.claim_cards
        if status:
            rows = [row for row in rows if row.get("status") == status]
        return _clone(rows[:limit])

    def create_claim_card(self, **payload):
        statement = str(payload.get("statement") or payload.get("title") or "Manual claim.").strip() or "Manual claim."
        card = {
            "id": str(payload.get("id") or self._make_id("claim", statement, self.claim_cards)),
            "brief_id": str(payload.get("brief_id") or "").strip(),
            "title": str(payload.get("title") or statement[:48]).strip(),
            "statement": statement,
            "rationale": str(payload.get("rationale") or "").strip(),
            "confidence": float(payload.get("confidence") or 0.0),
            "status": str(payload.get("status") or "draft").strip() or "draft",
            "source_item_ids": [str(item).strip() for item in payload.get("source_item_ids") or [] if str(item).strip()],
            "citation_bundle_ids": [str(item).strip() for item in payload.get("citation_bundle_ids") or [] if str(item).strip()],
            "updated_at": self._timestamp(),
        }
        self._upsert(self.claim_cards, card)
        return _clone(card)

    def show_claim_card(self, identifier: str):
        for card in self.claim_cards:
            if card["id"] == identifier:
                return _clone(card)
        return None

    def update_claim_card(self, identifier: str, **payload):
        for card in self.claim_cards:
            if card["id"] == identifier:
                card.update(payload)
                card["updated_at"] = self._timestamp()
                return _clone(card)
        return None

    def list_report_sections(self, limit: int = 20, status: str | None = None, report_id: str | None = None, **_kwargs):
        rows = self.report_sections
        if status:
            rows = [row for row in rows if row.get("status") == status]
        if report_id:
            rows = [row for row in rows if row.get("report_id") == report_id]
        return _clone(rows[:limit])

    def create_report_section(self, **payload):
        title = str(payload.get("title") or "Manual Section").strip() or "Manual Section"
        report_id = str(payload.get("report_id") or "").strip()
        section = {
            "id": str(payload.get("id") or self._make_id("section", f"{report_id}-{title}", self.report_sections)),
            "report_id": report_id,
            "title": title,
            "position": int(payload.get("position") or 0),
            "summary": str(payload.get("summary") or "").strip(),
            "claim_card_ids": [str(item).strip() for item in payload.get("claim_card_ids") or [] if str(item).strip()],
            "status": str(payload.get("status") or "draft").strip() or "draft",
            "updated_at": self._timestamp(),
        }
        self._upsert(self.report_sections, section)
        return _clone(section)

    def show_report_section(self, identifier: str):
        for section in self.report_sections:
            if section["id"] == identifier:
                return _clone(section)
        return None

    def update_report_section(self, identifier: str, **payload):
        for section in self.report_sections:
            if section["id"] == identifier:
                section.update(payload)
                section["updated_at"] = self._timestamp()
                return _clone(section)
        return None

    def list_citation_bundles(self, limit: int = 20):
        return _clone(self.citation_bundles[:limit])

    def create_citation_bundle(self, **payload):
        label = str(payload.get("label") or "Manual Bundle").strip() or "Manual Bundle"
        bundle = {
            "id": str(payload.get("id") or self._make_id("bundle", label, self.citation_bundles)),
            "claim_card_id": str(payload.get("claim_card_id") or "").strip(),
            "label": label,
            "source_item_ids": [str(item).strip() for item in payload.get("source_item_ids") or [] if str(item).strip()],
            "source_urls": [str(item).strip() for item in payload.get("source_urls") or [] if str(item).strip()],
            "note": str(payload.get("note") or "").strip(),
            "updated_at": self._timestamp(),
        }
        self._upsert(self.citation_bundles, bundle)
        return _clone(bundle)

    def show_citation_bundle(self, identifier: str):
        for bundle in self.citation_bundles:
            if bundle["id"] == identifier:
                return _clone(bundle)
        return None

    def update_citation_bundle(self, identifier: str, **payload):
        for bundle in self.citation_bundles:
            if bundle["id"] == identifier:
                bundle.update(payload)
                bundle["updated_at"] = self._timestamp()
                return _clone(bundle)
        return None

    def list_reports(self, limit: int = 20, status: str | None = None, **_kwargs):
        rows = self.reports
        if status:
            rows = [row for row in rows if row.get("status") == status]
        return _clone(rows[:limit])

    def create_report(self, **payload):
        title = str(payload.get("title") or "Manual Report").strip() or "Manual Report"
        report = {
            "id": str(payload.get("id") or self._make_id("report", title, self.reports)),
            "brief_id": str(payload.get("brief_id") or "").strip(),
            "title": title,
            "status": str(payload.get("status") or "draft").strip() or "draft",
            "audience": str(payload.get("audience") or "").strip(),
            "summary": str(payload.get("summary") or "").strip(),
            "section_ids": [str(item).strip() for item in payload.get("section_ids") or [] if str(item).strip()],
            "claim_card_ids": [str(item).strip() for item in payload.get("claim_card_ids") or [] if str(item).strip()],
            "citation_bundle_ids": [str(item).strip() for item in payload.get("citation_bundle_ids") or [] if str(item).strip()],
            "export_profile_ids": [str(item).strip() for item in payload.get("export_profile_ids") or [] if str(item).strip()],
            "updated_at": self._timestamp(),
        }
        self._upsert(self.reports, report)
        if not report["export_profile_ids"]:
            report["export_profile_ids"] = self._ensure_default_export_profiles(str(report["id"]))
        else:
            self._ensure_default_export_profiles(str(report["id"]))
        return _clone(report)

    def show_report(self, identifier: str):
        for report in self.reports:
            if report["id"] == identifier:
                return _clone(report)
        return None

    def update_report(self, identifier: str, **payload):
        for report in self.reports:
            if report["id"] == identifier:
                report.update(payload)
                report["updated_at"] = self._timestamp()
                self._ensure_default_export_profiles(identifier)
                return _clone(report)
        return None

    def compose_report(self, identifier: str, **kwargs):
        report = self.show_report(identifier)
        if report is None:
            return None
        profile_id = str(kwargs.get("profile_id") or "").strip()
        profile = self.show_export_profile(profile_id) if profile_id else None
        if profile_id and (profile is None or str(profile.get("report_id") or "").strip() != str(identifier).strip()):
            raise ValueError(f"Export profile not found: {profile_id}")
        include_sections = kwargs.get("include_sections")
        include_claim_cards = kwargs.get("include_claim_cards")
        include_citation_bundles = kwargs.get("include_citation_bundles")
        include_export_profiles = kwargs.get("include_export_profiles")
        if profile is not None:
            if include_sections is None:
                include_sections = bool(profile.get("include_sections", True))
            if include_claim_cards is None:
                include_claim_cards = bool(profile.get("include_claim_cards", True))
            if include_citation_bundles is None:
                include_citation_bundles = bool(profile.get("include_bundles", True))
            if include_export_profiles is None:
                include_export_profiles = bool(profile.get("include_export_profiles", True))
        include_sections = True if include_sections is None else bool(include_sections)
        include_claim_cards = True if include_claim_cards is None else bool(include_claim_cards)
        include_citation_bundles = True if include_citation_bundles is None else bool(include_citation_bundles)
        include_export_profiles = True if include_export_profiles is None else bool(include_export_profiles)
        section_map = {
            str(section.get("id") or "").strip(): section
            for section in self.report_sections
            if str(section.get("report_id") or "").strip() == str(identifier).strip()
        }
        report_section_ids = _strings(report.get("section_ids"))
        ordered_section_ids = self._unique_ids(
            [*report_section_ids, *[section_id for section_id in section_map if section_id not in report_section_ids]]
        )
        sections = [section_map[section_id] for section_id in ordered_section_ids if section_id in section_map]
        claim_map = {str(claim.get("id") or "").strip(): claim for claim in self.claim_cards}
        section_claim_ids = [claim_id for section in sections for claim_id in _strings(section.get("claim_card_ids"))]
        ordered_claim_ids = self._unique_ids([*_strings(report.get("claim_card_ids")), *section_claim_ids])
        claims = [claim_map[claim_id] for claim_id in ordered_claim_ids if claim_id in claim_map]
        bundle_map = {str(bundle.get("id") or "").strip(): bundle for bundle in self.citation_bundles}
        claim_bundle_ids = [bundle_id for claim in claims for bundle_id in _strings(claim.get("citation_bundle_ids"))]
        ordered_bundle_ids = self._unique_ids([*_strings(report.get("citation_bundle_ids")), *claim_bundle_ids])
        bundles = [bundle_map[bundle_id] for bundle_id in ordered_bundle_ids if bundle_id in bundle_map]
        profile_rows = self._report_profiles(str(identifier))
        profile_map = {str(row.get("id") or "").strip(): row for row in profile_rows}
        ordered_profile_ids = self._unique_ids(
            [*_strings(report.get("export_profile_ids")), *[str(row.get("id") or "").strip() for row in profile_rows]]
        )
        profiles = [profile_map[profile_row_id] for profile_row_id in ordered_profile_ids if profile_row_id in profile_map]
        claims_without_binding = []
        for claim in claims:
            direct_sources = _strings(claim.get("source_item_ids"))
            claim_bundles = [bundle_map[bundle_id] for bundle_id in _strings(claim.get("citation_bundle_ids")) if bundle_id in bundle_map]
            bundle_sources = any(
                (_strings(bundle.get("source_item_ids")) or _strings(bundle.get("source_urls")))
                for bundle in claim_bundles
            )
            if not direct_sources and not bundle_sources:
                claims_without_binding.append(str(claim.get("id") or ""))
        sections_without_claims = [
            str(section.get("id") or "")
            for section in sections
            if not _strings(section.get("claim_card_ids"))
        ]
        contradiction_entries = []
        for claim in claims:
            if str(claim.get("status") or "").strip().lower() in {"conflicted", "blocked", "disputed"}:
                contradiction_entries.append(
                    {
                        "detail": f"{claim.get('id')} is marked as {claim.get('status')}.",
                        "source": str(claim.get("id") or ""),
                        "severity": "error",
                    }
                )
        export_gate_issues = []
        if not profiles:
            export_gate_issues.append({"kind": "missing_export_profiles", "detail": "Report has no export profiles."})
        quality_status = "ready"
        operator_action = "allow_export"
        if contradiction_entries:
            quality_status = "blocked"
            operator_action = "hold_export"
        elif claims_without_binding or sections_without_claims or export_gate_issues:
            quality_status = "review_required"
            operator_action = "review_before_export"
        payload = {
            "report": report,
            "sections": _clone(sections if include_sections else []),
            "claim_cards": _clone(claims if include_claim_cards else []),
            "citation_bundles": _clone(bundles if include_citation_bundles else []),
            "export_profiles": _clone(profiles if include_export_profiles else []),
            "quality": {
                "status": quality_status,
                "score": 1.0 if quality_status == "ready" else (0.76 if quality_status == "review_required" else 0.24),
                "checks": {
                    "claim_source": {
                        "status": "pass" if not claims_without_binding else "review_required",
                        "issues": [
                            {
                                "kind": "uncited_claim",
                                "ids": claims_without_binding,
                                "detail": "Claims are missing source-bound evidence.",
                            }
                        ] if claims_without_binding else [],
                    },
                    "section_coverage": {
                        "status": "pass" if not sections_without_claims else "review_required",
                        "issues": [
                            {
                                "kind": "empty_sections",
                                "ids": sections_without_claims,
                                "detail": "Sections exist without attached claims.",
                            }
                        ] if sections_without_claims else [],
                    },
                    "contradictions": {
                        "status": "blocked" if contradiction_entries else "clear",
                        "entries": contradiction_entries,
                    },
                    "export_gates": {
                        "status": "pass" if not export_gate_issues else "review_required",
                        "issues": export_gate_issues,
                    },
                },
                "can_export": quality_status == "ready",
                "operator_action": operator_action,
            },
        }
        return payload

    def assess_report_quality(self, identifier: str, **kwargs):
        payload = self.compose_report(identifier, **kwargs)
        if payload is None:
            return None
        return payload.get("quality", {})

    def export_report(self, identifier: str, **kwargs):
        payload = self.compose_report(identifier, **kwargs)
        if payload is None:
            return None
        output_format = str(kwargs.get("output_format", "json")).strip().lower()
        if output_format == "json":
            return json.dumps(payload, ensure_ascii=False, indent=2)
        if output_format in {"md", "markdown"}:
            report = payload.get("report", {}) if isinstance(payload.get("report"), dict) else {}
            sections = payload.get("sections", []) if isinstance(payload.get("sections"), list) else []
            claims = payload.get("claim_cards", []) if isinstance(payload.get("claim_cards"), list) else []
            lines = [
                f"# {report.get('title', 'Report')}",
                "",
                f"- id: {report.get('id', identifier)}",
                f"- status: {report.get('status', 'draft')}",
                f"- audience: {report.get('audience', '-') or '-'}",
                "",
                "## Summary",
                str(report.get("summary") or "-"),
                "",
            ]
            if sections:
                lines.append("## Sections")
                for section in sections:
                    lines.append(f"### {section.get('title', 'Section')}")
                    if section.get("summary"):
                        lines.append(str(section["summary"]))
                    lines.append("")
            if claims:
                lines.append("## Claims")
                for claim in claims:
                    lines.append(f"- {claim.get('statement', claim.get('title', 'Claim'))}")
                lines.append("")
            return "\n".join(lines).strip() + "\n"
        raise ValueError(f"Unsupported report export format: {output_format}")

    def report_watch_pack(self, identifier: str, **kwargs):
        report = self.show_report(identifier)
        if report is None:
            return None
        profile_id = str(kwargs.get("profile_id") or "").strip()
        if profile_id:
            profile = self.show_export_profile(profile_id)
            if profile is None or str(profile.get("report_id") or "").strip() != str(identifier).strip():
                raise ValueError(f"Export profile not found: {profile_id}")
        payload = self.compose_report(identifier, profile_id=profile_id or None)
        if payload is None:
            return None
        sections = payload.get("sections", []) if isinstance(payload.get("sections"), list) else []
        claims = payload.get("claim_cards", []) if isinstance(payload.get("claim_cards"), list) else []
        bundles = payload.get("citation_bundles", []) if isinstance(payload.get("citation_bundles"), list) else []
        source_urls = [
            str(url).strip()
            for bundle in bundles
            for url in bundle.get("source_urls", [])
            if str(url).strip()
        ]
        return {
            "id": f"pack-{self._slug(str(identifier), 'report')}",
            "report_id": identifier,
            "mission_name": f"{report.get('title', 'Report').strip()} Follow-up Watch".strip(),
            "query": str(report.get("title") or identifier).strip(),
            "platforms": ["twitter", "news"],
            "sites": ["openai.com", "example.com", *source_urls[:1]],
            "schedule": "@hourly",
            "min_confidence": 0.6,
            "top_n": 10,
            "profile_id": profile_id or "",
            "sections": _clone(sections),
            "claim_cards": _clone(claims),
        }

    def create_watch_from_report_pack(
        self,
        identifier: str,
        *,
        profile_id: str | None = None,
        name: str | None = None,
        query: str | None = None,
        platforms: list[str] | None = None,
        sites: list[str] | None = None,
        schedule: str | None = None,
        min_confidence: float = 0.0,
        top_n: int = 10,
        alert_rules: list[dict[str, object]] | None = None,
    ):
        pack = self.report_watch_pack(identifier, profile_id=profile_id)
        if pack is None:
            return None
        mission_query = str(query or pack.get("query") or "").strip()
        mission_name = str(name or pack.get("mission_name") or "").strip()
        if not mission_query:
            mission_query = f"Watch {identifier}"
        if not mission_name:
            mission_name = f"{identifier} Watch"
        mission = self.create_watch(
            name=mission_name,
            query=mission_query,
            platforms=platforms or pack.get("platforms") or ["twitter"],
            sites=sites or pack.get("sites") or ["openai.com"],
            schedule=schedule or pack.get("schedule") or "@daily",
            min_confidence=min_confidence or pack.get("min_confidence") or 0.0,
            top_n=top_n or pack.get("top_n") or 10,
            alert_rules=alert_rules or [],
        )
        return _clone(mission)

    def list_export_profiles(self, limit: int = 20, status: str | None = None, report_id: str | None = None, **_kwargs):
        rows = self.export_profiles
        if status:
            rows = [row for row in rows if row.get("status") == status]
        if report_id:
            rows = [row for row in rows if row.get("report_id") == report_id]
        return _clone(rows[:limit])

    def create_export_profile(self, **payload):
        name = str(payload.get("name") or "manual").strip() or "manual"
        report_id = str(payload.get("report_id") or "").strip()
        profile = {
            "id": str(payload.get("id") or self._make_id("profile", f"{report_id}-{name}", self.export_profiles)),
            "report_id": report_id,
            "name": name,
            "output_format": str(payload.get("output_format") or "json").strip() or "json",
            "include_sections": bool(payload.get("include_sections", True)),
            "include_claim_cards": bool(payload.get("include_claim_cards", True)),
            "include_bundles": bool(payload.get("include_bundles", True)),
            "include_export_profiles": bool(payload.get("include_export_profiles", True)),
            "include_metadata": bool(payload.get("include_metadata", True)),
            "status": str(payload.get("status") or "active").strip() or "active",
        }
        self._upsert(self.export_profiles, profile)
        if report_id:
            report = self.show_report(report_id)
            if report is not None:
                next_ids = self._unique_ids([*(report.get("export_profile_ids") or []), str(profile["id"])])
                self.update_report(report_id, export_profile_ids=next_ids)
        return _clone(profile)

    def show_export_profile(self, identifier: str):
        for profile in self.export_profiles:
            if profile["id"] == identifier:
                return _clone(profile)
        return None

    def update_export_profile(self, identifier: str, **payload):
        for profile in self.export_profiles:
            if profile["id"] == identifier:
                profile.update(payload)
                profile["updated_at"] = self._timestamp()
                return _clone(profile)
        return None

    @staticmethod
    def _normalize_delivery_status(value: object) -> str:
        normalized = str(value or "").strip().lower() or "active"
        return normalized if normalized in {"active", "paused", "disabled"} else "active"

    @staticmethod
    def _normalize_delivery_mode(value: object) -> str:
        normalized = str(value or "").strip().lower() or "pull"
        return normalized if normalized in {"pull", "push"} else "pull"

    @staticmethod
    def _normalize_route_names(values: object) -> list[str]:
        seen: list[str] = []
        for value in _strings(values):
            normalized = str(value or "").strip().lower()
            if normalized and normalized not in seen:
                seen.append(normalized)
        return seen

    def list_delivery_subscriptions(
        self,
        limit: int = 20,
        status: str | None = None,
        subject_kind: str | None = None,
        subject_ref: str | None = None,
        output_kind: str | None = None,
        delivery_mode: str | None = None,
        route_name: str | None = None,
    ):
        rows = self.delivery_subscriptions
        if status:
            rows = [row for row in rows if str(row.get("status") or "").strip().lower() == str(status).strip().lower()]
        if subject_kind:
            rows = [row for row in rows if str(row.get("subject_kind") or "").strip().lower() == str(subject_kind).strip().lower()]
        if subject_ref:
            rows = [row for row in rows if str(row.get("subject_ref") or "").strip() == str(subject_ref).strip()]
        if output_kind:
            rows = [row for row in rows if str(row.get("output_kind") or "").strip().lower() == str(output_kind).strip().lower()]
        if delivery_mode:
            rows = [row for row in rows if str(row.get("delivery_mode") or "").strip().lower() == str(delivery_mode).strip().lower()]
        if route_name:
            normalized_route_name = str(route_name or "").strip().lower()
            rows = [row for row in rows if normalized_route_name in {name.lower() for name in _strings(row.get("route_names"))}]
        return _clone(rows[:limit])

    def create_delivery_subscription(self, **payload):
        subject_kind = str(payload.get("subject_kind") or "").strip().lower()
        subject_ref = str(payload.get("subject_ref") or "").strip()
        output_kind = str(payload.get("output_kind") or "").strip().lower()
        if subject_kind not in {"profile", "watch_mission", "story", "report"}:
            raise ValueError(f"Unsupported subject_kind: {subject_kind}")
        if output_kind not in {
            "alert_event",
            "feed_json",
            "feed_rss",
            "feed_atom",
            "story_json",
            "story_markdown",
            "report_brief",
            "report_full",
            "report_sources",
            "report_watch_pack",
        }:
            raise ValueError(f"Unsupported output_kind: {output_kind}")
        row = {
            "id": str(payload.get("id") or self._make_id("delivery-subscription", f"{subject_kind}-{subject_ref}-{output_kind}", self.delivery_subscriptions)),
            "subject_kind": subject_kind,
            "subject_ref": subject_ref,
            "output_kind": output_kind,
            "delivery_mode": self._normalize_delivery_mode(payload.get("delivery_mode")),
            "status": self._normalize_delivery_status(payload.get("status")),
            "route_names": self._normalize_route_names(payload.get("route_names")),
            "cursor_or_since": str(payload.get("cursor_or_since") or "").strip(),
            "created_at": self._timestamp(),
            "updated_at": self._timestamp(),
        }
        self.delivery_subscriptions.insert(0, row)
        return _clone(row)

    def show_delivery_subscription(self, identifier):
        for row in self.delivery_subscriptions:
            if str(row.get("id") or "").strip() == str(identifier or "").strip():
                return _clone(row)
        return None

    def update_delivery_subscription(self, identifier, **payload):
        for row in self.delivery_subscriptions:
            if str(row.get("id") or "").strip() != str(identifier or "").strip():
                continue
            if "subject_kind" in payload:
                row["subject_kind"] = str(payload.get("subject_kind") or row.get("subject_kind") or "").strip().lower()
            if "subject_ref" in payload:
                row["subject_ref"] = str(payload.get("subject_ref") or "").strip()
            if "output_kind" in payload:
                row["output_kind"] = str(payload.get("output_kind") or row.get("output_kind") or "").strip().lower()
            if "delivery_mode" in payload:
                row["delivery_mode"] = self._normalize_delivery_mode(payload.get("delivery_mode"))
            if "status" in payload:
                row["status"] = self._normalize_delivery_status(payload.get("status"))
            if "route_names" in payload:
                row["route_names"] = self._normalize_route_names(payload.get("route_names"))
            if "cursor_or_since" in payload:
                row["cursor_or_since"] = str(payload.get("cursor_or_since") or "").strip()
            row["updated_at"] = self._timestamp()
            return _clone(row)
        return None

    def delete_delivery_subscription(self, identifier):
        for index, row in enumerate(self.delivery_subscriptions):
            if str(row.get("id") or "").strip() == str(identifier or "").strip():
                return _clone(self.delivery_subscriptions.pop(index))
        return None

    def build_report_delivery_package(self, identifier, profile_id=None):
        subscription = self.show_delivery_subscription(identifier)
        if subscription is None:
            raise ValueError(f"Delivery subscription not found: {identifier}")
        if str(subscription.get("subject_kind") or "").strip().lower() != "report":
            raise ValueError("Only report subscriptions can be used for report delivery packages")
        report_id = str(subscription.get("subject_ref") or "").strip()
        report_payload = self.compose_report(report_id, profile_id=profile_id)
        if report_payload is None:
            raise ValueError(f"Report not found: {report_id}")
        normalized_profile_id = str(profile_id or "").strip()
        signature_source = f"{report_id}-{subscription.get('output_kind')}-{normalized_profile_id or 'default'}"
        signature = f"pkg-{self._slug(signature_source, 'delivery')}"
        return {
            "subscription_id": str(subscription.get("id") or "").strip(),
            "subject_kind": "report",
            "subject_ref": report_id,
            "output_kind": str(subscription.get("output_kind") or "").strip().lower(),
            "profile_id": normalized_profile_id,
            "package_signature": signature,
            "package_id": f"{report_id}:{subscription.get('output_kind')}:{signature}",
            "payload": {
                "kind": str(subscription.get("output_kind") or "").strip().lower(),
                "report": report_payload,
            },
        }

    def dispatch_report_delivery(self, identifier, profile_id=None):
        subscription = self.show_delivery_subscription(identifier)
        if subscription is None:
            raise ValueError(f"Delivery subscription not found: {identifier}")
        if str(subscription.get("subject_kind") or "").strip().lower() != "report":
            raise ValueError("Only report subscriptions can be dispatched by this method")
        package = self.build_report_delivery_package(identifier, profile_id=profile_id)
        rows: list[Row] = []
        for route_name in _strings(subscription.get("route_names")):
            route = next((item for item in self.routes if str(item.get("name") or "").strip().lower() == route_name.lower()), None)
            channel = str(route.get("channel") or "").strip().lower() if route else ""
            row = {
                "id": self._make_id("delivery-dispatch", f"{identifier}-{route_name}", self.delivery_dispatch_records),
                "subscription_id": str(subscription.get("id") or "").strip(),
                "subject_kind": "report",
                "subject_ref": str(subscription.get("subject_ref") or "").strip(),
                "output_kind": str(subscription.get("output_kind") or "").strip().lower(),
                "route_name": route_name.lower(),
                "route_label": f"{channel}:{route_name.lower()}" if route else f"route:{route_name.lower()}",
                "route_channel": channel,
                "package_id": str(package.get("package_id") or "").strip(),
                "package_signature": str(package.get("package_signature") or "").strip(),
                "package_profile_id": str(profile_id or "").strip(),
                "status": "delivered" if route else "missing_route",
                "error": "" if route else f"Missing route: {route_name.lower()}",
                "attempts": 1 if route else 0,
                "created_at": self._timestamp(),
                "updated_at": self._timestamp(),
            }
            self.delivery_dispatch_records.insert(0, row)
            rows.append(row)
        return _clone(rows)

    def list_delivery_dispatch_records(
        self,
        limit: int = 20,
        status: str | None = None,
        subscription_id: str | None = None,
        subject_kind: str | None = None,
        subject_ref: str | None = None,
        output_kind: str | None = None,
        route_name: str | None = None,
    ):
        rows = self.delivery_dispatch_records
        if status:
            rows = [row for row in rows if str(row.get("status") or "").strip().lower() == str(status).strip().lower()]
        if subscription_id:
            rows = [row for row in rows if str(row.get("subscription_id") or "").strip() == str(subscription_id).strip()]
        if subject_kind:
            rows = [row for row in rows if str(row.get("subject_kind") or "").strip().lower() == str(subject_kind).strip().lower()]
        if subject_ref:
            rows = [row for row in rows if str(row.get("subject_ref") or "").strip() == str(subject_ref).strip()]
        if output_kind:
            rows = [row for row in rows if str(row.get("output_kind") or "").strip().lower() == str(output_kind).strip().lower()]
        if route_name:
            rows = [row for row in rows if str(row.get("route_name") or "").strip().lower() == str(route_name).strip().lower()]
        return _clone(rows[:limit])

    def get_digest_profile(self):
        return {
            "schema_version": "digest_profile_projection.v1",
            "profile_path": "/tmp/datapulse-browser-smoke-digest-profile.json",
            "exists": True,
            "onboarding_status": "ready",
            "missing_fields": [],
            "profile": _clone(self.digest_profile),
        }

    def update_digest_profile(
        self,
        *,
        language: str | None = None,
        timezone: str | None = None,
        frequency: str | None = None,
        default_delivery_target_kind: str | None = None,
        default_delivery_target_ref: str | None = None,
    ):
        if language is not None:
            self.digest_profile["language"] = str(language or "").strip() or "en"
        if timezone is not None:
            self.digest_profile["timezone"] = str(timezone or "").strip() or "UTC"
        if frequency is not None:
            self.digest_profile["frequency"] = str(frequency or "").strip() or "@daily"
        if default_delivery_target_kind is not None or default_delivery_target_ref is not None:
            current_target = _row(self.digest_profile.get("default_delivery_target")) or {"kind": "route", "ref": ""}
            self.digest_profile["default_delivery_target"] = {
                "kind": str(default_delivery_target_kind or current_target.get("kind") or "route").strip() or "route",
                "ref": str(default_delivery_target_ref or current_target.get("ref") or "").strip().lower(),
            }
        return self.get_digest_profile()

    def digest_console_projection(self, *, profile: str = "default", limit: int = 12, min_confidence: float = 0.0, since: str | None = None):
        return {
            "schema_version": "digest_console_projection.v1",
            "profile": self.get_digest_profile(),
            "prepared_payload": {
                "schema_version": "prepare_digest_payload.v1",
                "generated_at": self._timestamp(),
                "content": {
                    "feed_bundle": {
                        "schema_version": "feed_bundle.v1",
                        "generated_at": self._timestamp(),
                        "selection": {
                            "profile": profile,
                            "pack_id": None,
                            "source_ids_requested": [],
                            "source_ids_resolved": ["openai-blog", "launch-recap"],
                            "since": since,
                            "limit": limit,
                            "min_confidence": min_confidence,
                        },
                        "window": {
                            "start_at": "2026-03-05T20:00:00+00:00",
                            "end_at": self._timestamp(),
                        },
                        "items": _clone(self.triage_items[: min(limit, 2)]),
                        "stats": {
                            "items_selected": min(limit, 2),
                            "sources_selected": 2,
                        },
                        "errors": [],
                    },
                    "digest_payload": {
                        "version": "1.0",
                        "generated_at": self._timestamp(),
                        "stats": {
                            "candidates_total": min(limit, 2),
                            "selected_primary": 1,
                            "selected_secondary": 1 if limit > 1 else 0,
                        },
                        "primary": [{"id": "item-1", "title": "OpenAI launch post"}],
                        "secondary": [{"id": "item-2", "title": "OpenAI launch recap"}] if limit > 1 else [],
                    },
                    "delivery_package": {
                        "summary": {
                            "item_count": min(limit, 2),
                            "high_confidence_count": 1,
                            "factuality_status": "ready",
                            "factuality_effective_status": "ready",
                        }
                    },
                },
                "config": {
                    "profile": profile,
                    "source_ids": ["openai-blog", "launch-recap"],
                    "top_n": 3,
                    "secondary_n": 7,
                    "min_confidence": min_confidence,
                    "since": since,
                    "max_per_source": 2,
                    "output_format": "json",
                    "digest_profile": _clone(self.digest_profile),
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
                    "feed_bundle": {"items_selected": min(limit, 2), "sources_selected": 2},
                    "digest": {"selected_primary": 1, "selected_secondary": 1 if limit > 1 else 0},
                    "delivery_package": {"item_count": min(limit, 2), "high_confidence_count": 1, "factuality_status": "ready"},
                },
                "errors": [],
            },
        }

    def prepare_digest_payload(self, *, profile: str = "default", limit: int = 12, min_confidence: float = 0.0, since: str | None = None):
        return self.digest_console_projection(
            profile=profile,
            limit=limit,
            min_confidence=min_confidence,
            since=since,
        )["prepared_payload"]

    def dispatch_digest_delivery(self, *, prepared_payload: dict[str, Any] | None = None, route_name: str | None = None):
        route_ref = str(route_name or _row(self.digest_profile.get("default_delivery_target") or {}).get("ref") or "").strip().lower()
        route = next((item for item in self.routes if str(item.get("name") or "").strip().lower() == route_ref), None)
        channel = str(route.get("channel") or "").strip().lower() if route else "unknown"
        status = "delivered" if route else "missing_route"
        row = {
            "subject_kind": "profile",
            "subject_ref": "default",
            "output_kind": "digest_delivery",
            "route_name": route_ref,
            "route_label": f"{channel}:{route_ref}" if route else f"route:{route_ref}",
            "route_channel": channel,
            "package_signature": "digest-browser-smoke-signature",
            "status": status,
            "attempts": 1 if route else 0,
            "error": "" if route else f"Missing route: {route_ref}",
            "governance": {
                "delivery_diagnostics": {
                    "route_label": f"{channel}:{route_ref}" if route else f"route:{route_ref}",
                    "route_name": route_ref,
                    "channel": channel,
                    "attempt_count": 1 if route else 0,
                    "chunk_count": 1 if route else 0,
                    "fallback_used": False,
                    "fallback_reason": "",
                    "attempts": [
                        {
                            "kind": "webhook_post" if route else "route_resolution",
                            "status": status,
                            "payload_kind": "digest_delivery",
                        }
                    ] if route_ref else [],
                }
            },
        }
        self.digest_dispatch_records.insert(0, row)
        return _clone([row])


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

    def handle_page_error(error) -> None:
        _log(f"[console-browser-smoke] {label} pageerror: {error}")

    page.on("pageerror", handle_page_error)

    def handle_console(message) -> None:
        if message.type not in {"error", "warning"}:
            return
        _log(f"[console-browser-smoke] {label} console:{message.type}: {message.text}")

    page.on("console", handle_console)
    page.on("dialog", lambda dialog: dialog.accept())


def _track_api_requests(page: Page) -> list[str]:
    requests: list[str] = []

    def handle_request(request) -> None:
        path = _request_path(request.url)
        if path.startswith("/api/"):
            requests.append(path)

    page.on("request", handle_request)
    return requests


def _request_path(url: str) -> str:
    split = urlsplit(url)
    path = split.path or "/"
    return f"{path}?{split.query}" if split.query else path


def _wait_for_console_ready(page: Page) -> None:
    page.wait_for_selector("#create-watch-form", state="attached", timeout=10000)
    page.wait_for_function("() => document.querySelector('#triage-list') && document.querySelector('#story-list')", timeout=20000)


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


def _wait_for_stage_shell(page: Page) -> None:
    page.wait_for_function(
        """() => {
            const shell = document.querySelector('#workspace-mode-shell');
            if (!shell || shell.hidden) {
                return false;
            }
            const chips = Array.from(shell.querySelectorAll('.workspace-mode-meta .chip')).filter((chip) => (chip.textContent || '').trim());
            const anchor = shell.querySelector('[data-workspace-object-anchor]');
            const anchorTitle = (anchor?.querySelector('.workspace-mode-object-title')?.textContent || '').trim();
            const anchorPrimary = (anchor?.querySelector('[data-card-action-primary] button, [data-card-action-primary] a')?.textContent || '').trim();
            const anchorFacts = anchor ? Array.from(anchor.querySelectorAll('.continuity-fact')).filter((fact) => (fact.textContent || '').trim()) : [];
            const cards = Array.from(shell.querySelectorAll('[data-workspace-jump]')).filter((button) => (button.textContent || '').trim());
            return cards.length >= 1 && (
                chips.length >= 4
                || (anchorTitle.length > 0 && anchorPrimary.length > 0 && anchorFacts.length >= 3)
            );
        }""",
        timeout=10000,
    )


def _stage_shell_snapshot(page: Page) -> Row:
    snapshot = page.evaluate(
        """() => {
            const shell = document.querySelector('#workspace-mode-shell');
            if (!shell || shell.hidden) {
                return null;
            }
            const chipMap = {};
            Array.from(shell.querySelectorAll('.workspace-mode-meta .chip')).forEach((chip) => {
                const text = (chip.textContent || '').trim();
                const parts = text.split(':');
                if (parts.length >= 2) {
                    chipMap[String(parts[0] || '').trim()] = parts.slice(1).join(':').trim();
                }
            });
            Array.from(shell.querySelectorAll('[data-workspace-object-anchor] .continuity-fact')).forEach((fact) => {
                const label = (fact.querySelector('span')?.textContent || '').trim();
                const value = (fact.querySelector('strong')?.textContent || '').trim();
                if (label && value) {
                    chipMap[label] = value;
                }
            });
            const cards = Array.from(shell.querySelectorAll('[data-workspace-jump]')).map((button) => ({
                jump: button.getAttribute('data-workspace-jump') || '',
                title: (button.querySelector('.workspace-mode-card-head .workspace-mode-title')?.textContent || '').trim(),
                active: button.classList.contains('active'),
            }));
            return {
                stage: (shell.querySelector('.workspace-mode-head .workspace-mode-title')?.textContent || '').trim(),
                chrome: shell.getAttribute('data-workspace-chrome') || '',
                anchor_title: (shell.querySelector('[data-workspace-object-anchor] .workspace-mode-object-title')?.textContent || '').trim(),
                anchor_primary: (shell.querySelector('[data-workspace-object-anchor] [data-card-action-primary] button, [data-workspace-object-anchor] [data-card-action-primary] a')?.textContent || '').trim(),
                anchor_fact_count: shell.querySelectorAll('[data-workspace-object-anchor] .continuity-fact').length,
                chips: chipMap,
                cards,
            };
        }"""
    )
    assert isinstance(snapshot, dict), "workspace mode shell snapshot was not available"
    return cast(Row, snapshot)


def _assert_stage_shell(
    page: Page,
    *,
    stage: str | Sequence[str],
    current_surface: str | Sequence[str],
    current_object_contains: str | Sequence[str],
    owned_output_contains: str | Sequence[str],
    next_action_contains: str | Sequence[str],
    compact: bool | None = None,
) -> None:
    def _options(value: str | Sequence[str]) -> list[str]:
        if isinstance(value, str):
            return [value]
        return [str(item).strip() for item in value if str(item).strip()]

    def _chip_value(chips: Row, *labels: str) -> str:
        for label in labels:
            value = str(chips.get(label) or "").strip()
            if value:
                return value
        return ""

    _wait_for_stage_shell(page)
    snapshot = _stage_shell_snapshot(page)
    chips = _row(snapshot.get("chips")) or {}
    stage_value = str(snapshot.get("stage") or "").strip()
    current_surface_value = _chip_value(chips, "Current surface", "当前视图", "Surface", "视图")
    current_object_value = _chip_value(chips, "Current object", "当前对象")
    owned_output_value = _chip_value(chips, "Owned output", "阶段产出")
    next_action_value = _chip_value(chips, "Next action", "下一步动作")
    assert any(stage_value == option for option in _options(stage)), f"stage shell stage mismatch: {snapshot}"
    if compact is True:
        anchor_title = str(snapshot.get("anchor_title") or "").strip()
        anchor_primary = str(snapshot.get("anchor_primary") or "").strip()
        anchor_fact_count = _as_int(snapshot.get("anchor_fact_count"))
        assert str(snapshot.get("chrome") or "").strip() == "compact", f"stage shell was not compact: {snapshot}"
        assert any(option in anchor_title for option in _options(current_object_contains)), f"compact current object mismatch: {snapshot}"
        assert any(option in current_surface_value for option in _options(current_surface)), f"current surface mismatch: {snapshot}"
        assert any(option in owned_output_value for option in _options(owned_output_contains)), f"owned output mismatch: {snapshot}"
        assert any(option in anchor_primary for option in _options(next_action_contains)), f"primary action mismatch: {snapshot}"
        assert anchor_fact_count >= 3, f"compact continuity facts missing: {snapshot}"
        return
    if compact is False:
        assert str(snapshot.get("chrome") or "").strip() == "default", f"stage shell unexpectedly compact: {snapshot}"
    assert any(option in current_surface_value for option in _options(current_surface)), f"current surface mismatch: {snapshot}"
    assert any(option in current_object_value for option in _options(current_object_contains)), f"current object mismatch: {snapshot}"
    assert any(option in owned_output_value for option in _options(owned_output_contains)), f"owned output mismatch: {snapshot}"
    assert any(option in next_action_value for option in _options(next_action_contains)), f"next action mismatch: {snapshot}"


def _assert_populated_intake_chrome(page: Page, expected_object: str | Sequence[str]) -> None:
    expected = [expected_object] if isinstance(expected_object, str) else [str(item).strip() for item in expected_object if str(item).strip()]
    page.wait_for_function(
        """(expectedObjects) => {
            const hero = document.querySelector('[data-intake-populated-hero="true"]');
            const guide = document.querySelector('[data-intake-guide-compact="true"]');
            const currentObject = hero?.querySelector('[data-intake-current-object]')?.textContent || '';
            const primary = hero?.querySelector('[data-card-action-primary] button, [data-card-action-primary] a')?.textContent || '';
            const factCount = hero?.querySelectorAll('.continuity-fact').length || 0;
            const onboardingHidden = document.querySelector('#intake-hero-onboarding')?.hidden === true
                && document.querySelector('#intake-side-onboarding')?.hidden === true;
            return !!hero
                && !!guide
                && onboardingHidden
                && expectedObjects.some((entry) => currentObject.includes(entry))
                && primary.trim().length > 0
                && factCount >= 3;
        }""",
        arg=expected,
        timeout=10000,
    )


def _wait_for_trace_and_signal_taxonomy(page: Page) -> None:
    page.wait_for_function(
        """() => {
            const trace = document.querySelector('[data-stage-trace="workflow"]');
            const stages = trace ? Array.from(trace.querySelectorAll('[data-trace-stage]')) : [];
            const taxonomy = document.querySelector('[data-shared-signal-taxonomy="true"]');
            const buttons = taxonomy ? Array.from(taxonomy.querySelectorAll('[data-shared-signal-button]')) : [];
            const panel = taxonomy ? taxonomy.querySelector('[data-shared-signal-panel]') : null;
            return !!trace && stages.length === 4 && !!taxonomy && buttons.length >= 4 && !!panel;
        }""",
        timeout=10000,
    )


def _wait_for_shared_signal_panel(page: Page, signal_id: str) -> None:
    page.wait_for_function(
        """(expectedSignalId) => {
            const panel = document.querySelector('[data-shared-signal-panel]');
            const button = document.querySelector(`[data-shared-signal-button="${expectedSignalId}"]`);
            return !!panel
                && typeof state === 'object'
                && state.sharedSignalFocus === expectedSignalId
                && !!button
                && button.classList.contains('active')
                && panel.getAttribute('data-shared-signal-panel') === expectedSignalId
                && (panel.textContent || '').trim().length > 0;
        }""",
        arg=signal_id,
        timeout=15000,
    )


def _select_shared_signal(page: Page, signal_id: str) -> None:
    selector = f'[data-shared-signal-button="{signal_id}"]'
    _wait_for_interactive_button(page, selector)
    last_error: Exception | None = None
    for _ in range(4):
        _click(page, selector)
        try:
            _wait_for_shared_signal_panel(page, signal_id)
            return
        except PlaywrightTimeoutError as exc:
            last_error = exc
            page.wait_for_timeout(250)
    if last_error is not None:
        raise last_error
    raise AssertionError(f"shared signal panel did not settle for {signal_id}")


def _wait_for_shared_signal_primary_action(page: Page, signal_id: str) -> str:
    selector = f'[data-shared-signal-panel="{signal_id}"] [data-card-action-primary] [data-empty-jump]'
    page.wait_for_function(
        """(expectedSelector) => {
            const action = document.querySelector(expectedSelector);
            return !!action
                && !action.hasAttribute('disabled')
                && (action.textContent || '').trim().length > 0;
        }""",
        arg=selector,
        timeout=10000,
    )
    return selector


def _assert_signal_owner(page: Page, signal_id: str, owner_contains: str | Sequence[str]) -> None:
    expected = [owner_contains] if isinstance(owner_contains, str) else [str(item).strip() for item in owner_contains if str(item).strip()]
    _select_shared_signal(page, signal_id)
    page.wait_for_function(
        """([signalId, expectedOwners]) => {
            const panel = document.querySelector('[data-shared-signal-panel]');
            const owner = panel?.querySelector('[data-shared-signal-owner]')?.textContent || '';
            return !!panel
                && panel.getAttribute('data-shared-signal-panel') === signalId
                && expectedOwners.some((expectedOwner) => owner.includes(expectedOwner));
        }""",
        arg=[signal_id, expected],
        timeout=10000,
    )


def _assert_signal_primary_action_routes(page: Page, signal_id: str, expected_hash: str, nav_id: str) -> None:
    _select_shared_signal(page, signal_id)
    primary_selector = _wait_for_shared_signal_primary_action(page, signal_id)
    _click(page, primary_selector)
    page.wait_for_function(
        """([signalId, hashValue]) => {
            const panel = document.querySelector(`[data-shared-signal-panel="${signalId}"]`);
            return !!panel && window.location.hash === hashValue;
        }""",
        arg=[signal_id, expected_hash],
        timeout=10000,
    )
    _wait_for_active_rail(page, nav_id, expected_hash)
    _wait_for_trace_and_signal_taxonomy(page)


def _assert_signal_no_action_outcome(page: Page, signal_id: str) -> None:
    _select_shared_signal(page, signal_id)
    page.wait_for_function(
        """(signalId) => {
            const panel = document.querySelector(`[data-shared-signal-panel="${signalId}"]`);
            const noop = panel?.querySelector('[data-shared-signal-noop="true"]')?.textContent || '';
            return !!panel && noop.trim().length > 0;
        }""",
        arg=signal_id,
        timeout=10000,
    )


def _assert_signal_explicit_outcome(page: Page, signal_id: str, expected_section: str) -> None:
    _select_shared_signal(page, signal_id)
    page.wait_for_function(
        """([signalId, expectedSection]) => {
            const panel = document.querySelector('[data-shared-signal-panel]');
            const action = panel?.querySelector('[data-card-action-primary] [data-empty-jump]');
            const noop = panel?.querySelector('[data-shared-signal-noop="true"]')?.textContent || '';
            return !!panel
                && panel.getAttribute('data-shared-signal-panel') === signalId
                && (
                    action?.getAttribute('data-empty-jump') === expectedSection
                    || noop.trim().length > 0
                );
        }""",
        arg=[signal_id, expected_section],
        timeout=10000,
    )


def _assert_signal_primary_action_target(page: Page, signal_id: str, expected_section: str) -> None:
    _select_shared_signal(page, signal_id)
    _wait_for_shared_signal_primary_action(page, signal_id)
    page.wait_for_function(
        """([signalId, expectedSection]) => {
            const panel = document.querySelector('[data-shared-signal-panel]');
            const action = panel?.querySelector('[data-card-action-primary] [data-empty-jump]');
            return !!panel
                && panel.getAttribute('data-shared-signal-panel') === signalId
                && action?.getAttribute('data-empty-jump') === expectedSection;
        }""",
        arg=[signal_id, expected_section],
        timeout=10000,
    )


def _wait_for_stage_feedback(page: Page, *, stage: str, kind: str, title_contains: str | Sequence[str]) -> None:
    expected_titles = [title_contains] if isinstance(title_contains, str) else [str(item).strip() for item in title_contains if str(item).strip()]
    page.wait_for_function(
        """([stageId, feedbackKind, expectedTitles]) => {
            const card = document.querySelector(`[data-stage-feedback-stage="${stageId}"][data-stage-feedback-kind="${feedbackKind}"]`);
            const title = card?.querySelector('.section-summary-title')?.textContent || '';
            return !!card && expectedTitles.some((expectedTitle) => title.includes(expectedTitle));
        }""",
        arg=[stage, kind, expected_titles],
        timeout=10000,
    )


def _wait_for_section_summary(page: Page, section_id: str) -> None:
    page.wait_for_function(
        """(sectionId) => {
            const root = document.querySelector(`[data-section-summary="${sectionId}"]`);
            const objective = root?.querySelector('[data-section-summary-kind="objective"]')?.textContent?.trim();
            const success = root?.querySelector('[data-section-summary-kind="success"]')?.textContent?.trim();
            const blocker = root?.querySelector('[data-section-summary-kind="blocker"]')?.textContent?.trim();
            return !!root && !!objective && !!success && !!blocker;
        }""",
        arg=section_id,
        timeout=10000,
    )

def _wait_for_operator_guidance_surface(page: Page, surface_id: str) -> None:
    page.wait_for_function(
        """(surfaceId) => {
            const root = document.querySelector(`#${surfaceId}`);
            const columns = root ? Array.from(root.querySelectorAll('[data-guidance-column]')) : [];
            const visibleColumns = columns.filter((column) => (column.textContent || '').trim());
            const items = root ? Array.from(root.querySelectorAll('[data-guidance-kind]')) : [];
            const visibleItems = items.filter((item) => (item.textContent || '').trim());
            return !!root && visibleColumns.length > 0 && visibleItems.length > 0;
        }""",
        arg=surface_id,
        timeout=10000,
    )


def _wait_for_interactive_button(page: Page, selector: str) -> None:
    page.wait_for_function(
        """(buttonSelector) => {
            const button = document.querySelector(buttonSelector);
            return !!button
                && !button.hasAttribute('disabled')
                && !button.hidden
                && button.getAttribute('aria-hidden') !== 'true'
                && (button.textContent || '').trim().length > 0;
        }""",
        arg=selector,
        timeout=10000,
    )


def _wait_for_context_lens_state(page: Page, *, open_state: bool) -> None:
    expression = (
        "() => document.body.dataset.contextLensOpen === 'true'"
        " && document.querySelector('#context-lens-backdrop')?.classList.contains('open')"
        " && document.querySelector('#context-lens-backdrop')?.hidden === false"
        " && document.querySelector('#context-lens')?.hidden === false"
        " && document.querySelector('#context-summary')?.getAttribute('aria-expanded') === 'true'"
        if open_state
        else "() => document.body.dataset.contextLensOpen !== 'true'"
        " && !document.querySelector('#context-lens-backdrop')?.classList.contains('open')"
        " && document.querySelector('#context-lens-backdrop')?.hidden === true"
        " && document.querySelector('#context-lens')?.hidden === true"
        " && document.querySelector('#context-summary')?.getAttribute('aria-expanded') === 'false'"
    )
    page.wait_for_function(expression, timeout=10000)


def _wait_for_context_dock_state(page: Page, *, visible: bool) -> None:
    expression = (
        "() => {"
        " const root = document.querySelector('#context-view-dock');"
        " return !!root"
        "   && root.hidden === false"
        "   && root.querySelectorAll('[data-context-dock-open]').length > 0;"
        "}"
        if visible
        else "() => {"
        " const root = document.querySelector('#context-view-dock');"
        " return !!root"
        "   && root.hidden === true"
        "   && !root.querySelector('[data-context-dock-open]');"
        "}"
    )
    page.wait_for_function(expression, timeout=10000)


def _wait_for_digest_dispatch_result(page: Page, *, route_name: str, status: str) -> None:
    page.wait_for_function(
        """([expectedRouteName, expectedStatus]) => {
            if (typeof state !== 'object' || !Array.isArray(state.digestDispatchResult)) {
                return false;
            }
            return state.digestDispatchResult.some((row) => {
                if (!row || typeof row !== 'object') {
                    return false;
                }
                const routeName = String(row.route_name || '').trim();
                const rowStatus = String(row.status || '').trim().toLowerCase();
                const diagnostics = row.governance?.delivery_diagnostics;
                return routeName === expectedRouteName
                    && rowStatus === expectedStatus
                    && !!diagnostics
                    && typeof diagnostics === 'object';
            });
        }""",
        arg=[route_name, status],
        timeout=20000,
    )


def _open_context_lens(page: Page, trigger_selector: str) -> None:
    _wait_for_interactive_button(page, trigger_selector)
    last_error: Exception | None = None
    for _ in range(3):
        _click(page, trigger_selector)
        try:
            _wait_for_context_lens_state(page, open_state=True)
            return
        except PlaywrightTimeoutError as exc:
            last_error = exc
            page.wait_for_timeout(150)
    if last_error is not None:
        raise last_error
    raise AssertionError(f"context lens did not open from trigger: {trigger_selector}")


def _close_context_lens(page: Page) -> None:
    _wait_for_interactive_button(page, "#context-lens-close")
    last_error: Exception | None = None
    for _ in range(3):
        _click(page, "#context-lens-close")
        try:
            _wait_for_context_lens_state(page, open_state=False)
            return
        except PlaywrightTimeoutError as exc:
            last_error = exc
            page.wait_for_timeout(150)
    if last_error is not None:
        raise last_error
    raise AssertionError("context lens did not close")


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
    last_error: Exception | None = None
    for _ in range(3):
        locator = page.locator(selector).first
        locator.wait_for(state="attached", timeout=10000)
        try:
            locator.click(force=True, timeout=5000)
            return
        except Exception as exc:
            last_error = exc
            try:
                page.evaluate(
                    """(targetSelector) => {
                        const node = document.querySelector(targetSelector);
                        if (!node) {
                            throw new Error(`missing selector: ${targetSelector}`);
                        }
                        node.click();
                    }""",
                    selector,
                )
                return
            except Exception as fallback_exc:
                last_error = fallback_exc
                page.wait_for_timeout(150)
    if last_error is not None:
        raise last_error


def _submit_form(page: Page, selector: str) -> None:
    page.locator(selector).evaluate("(form) => form.requestSubmit()")


def _submit_form_without_validation(page: Page, selector: str) -> None:
    page.locator(selector).evaluate(
        """(form) => {
            const event = new Event('submit', { bubbles: true, cancelable: true });
            form.dispatchEvent(event);
        }"""
    )


def _goto(page: Page, url: str) -> None:
    page.goto(url, wait_until="domcontentloaded", timeout=20000)


def _jump_to_section_with_fallback(page: Page, section_id: str, *, selector: str | None = None) -> None:
    expected_hash = f"#{section_id}"
    if selector:
        _click(page, selector)
    else:
        page.evaluate("(targetSection) => jumpToSection(targetSection)", section_id)
    try:
        page.wait_for_function("(hashValue) => window.location.hash === hashValue", arg=expected_hash, timeout=3000)
    except PlaywrightTimeoutError:
        page.evaluate("(targetSection) => jumpToSection(targetSection)", section_id)
        page.wait_for_function("(hashValue) => window.location.hash === hashValue", arg=expected_hash, timeout=10000)


def _fetch_json(page: Page, url: str, *, method: str = "GET", payload: Row | None = None) -> Row:
    response = page.evaluate(
        """async ({ url, method, payload }) => {
            const options = { method };
            if (payload) {
              options.headers = { "Content-Type": "application/json" };
              options.body = JSON.stringify(payload);
            }
            const resp = await fetch(url, options);
            let data = null;
            try {
              data = await resp.json();
            } catch (error) {
              data = { parse_error: String(error) };
            }
            return { status: resp.status, ok: resp.ok, data };
        }""",
        {"url": url, "method": method, "payload": payload},
    )
    if not isinstance(response, dict):
        raise AssertionError(f"Unexpected fetch payload for {url}: {response!r}")
    return cast(Row, response)


def _fetch_text(page: Page, url: str, *, method: str = "GET", payload: Row | None = None) -> Row:
    response = page.evaluate(
        """async ({ url, method, payload }) => {
            const options = { method };
            if (payload) {
              options.headers = { "Content-Type": "application/json" };
              options.body = JSON.stringify(payload);
            }
            const resp = await fetch(url, options);
            const text = await resp.text();
            return { status: resp.status, ok: resp.ok, text };
        }""",
        {"url": url, "method": method, "payload": payload},
    )
    if not isinstance(response, dict):
        raise AssertionError(f"Unexpected text fetch payload for {url}: {response!r}")
    return cast(Row, response)


def _wait_for_report_id(page: Page, title: str, *, timeout_ms: int = 20000) -> str:
    deadline = time.monotonic() + (timeout_ms / 1000)
    last_payload: Row | None = None
    while time.monotonic() < deadline:
        payload = _fetch_json(page, "/api/reports?limit=40")
        last_payload = payload
        if _as_int(payload.get("status")) == 200:
            for row in _rows(payload.get("data")):
                if str(row.get("title") or "").strip() == title:
                    identifier = str(row.get("id") or "").strip()
                    if identifier:
                        return identifier
        time.sleep(0.2)
    raise AssertionError(f"timed out waiting for report {title!r}: {last_payload}")


def _wait_for_report_section_id(page: Page, report_id: str, title: str, *, timeout_ms: int = 20000) -> str:
    deadline = time.monotonic() + (timeout_ms / 1000)
    last_payload: Row | None = None
    while time.monotonic() < deadline:
        payload = _fetch_json(page, "/api/report-sections?limit=40")
        last_payload = payload
        if _as_int(payload.get("status")) == 200:
            for row in _rows(payload.get("data")):
                if str(row.get("report_id") or "").strip() != report_id:
                    continue
                if str(row.get("title") or "").strip() != title:
                    continue
                identifier = str(row.get("id") or "").strip()
                if identifier:
                    return identifier
        time.sleep(0.2)
    raise AssertionError(f"timed out waiting for report section {title!r} on {report_id!r}: {last_payload}")


def _wait_for_report_compose_ready(page: Page, report_id: str, *, timeout_ms: int = 20000) -> Row:
    deadline = time.monotonic() + (timeout_ms / 1000)
    last_payload: Row | None = None
    while time.monotonic() < deadline:
        payload = _fetch_json(page, f"/api/reports/{report_id}/compose")
        last_payload = payload
        if _as_int(payload.get("status")) == 200:
            data = _row(payload.get("data"))
            quality = _row(data.get("quality")) if data is not None else None
            if quality is not None and str(quality.get("status") or "").strip().lower() == "ready" and bool(quality.get("can_export")):
                assert data is not None
                return data
        time.sleep(0.2)
    raise AssertionError(f"timed out waiting for report compose readiness on {report_id!r}: {last_payload}")


def _wait_for_claim_card(page: Page, statement: str, *, timeout_ms: int = 20000) -> Row:
    deadline = time.monotonic() + (timeout_ms / 1000)
    last_payload: Row | None = None
    while time.monotonic() < deadline:
        payload = _fetch_json(page, "/api/claim-cards?limit=40")
        last_payload = payload
        if _as_int(payload.get("status")) == 200:
            for row in _rows(payload.get("data")):
                if str(row.get("statement") or "").strip() == statement:
                    return row
        time.sleep(0.2)
    raise AssertionError(f"timed out waiting for claim card {statement!r}: {last_payload}")


def _wait_for_citation_bundle(page: Page, claim_id: str, url_fragment: str, *, timeout_ms: int = 20000) -> Row:
    deadline = time.monotonic() + (timeout_ms / 1000)
    last_payload: Row | None = None
    while time.monotonic() < deadline:
        payload = _fetch_json(page, "/api/citation-bundles?limit=40")
        last_payload = payload
        if _as_int(payload.get("status")) == 200:
            for row in _rows(payload.get("data")):
                if str(row.get("claim_card_id") or "").strip() != claim_id:
                    continue
                if any(url_fragment in value for value in _strings(row.get("source_urls"))):
                    return row
        time.sleep(0.2)
    raise AssertionError(f"timed out waiting for citation bundle on claim {claim_id!r}: {last_payload}")


def _wait_for_export_profile(page: Page, report_id: str, name: str, *, timeout_ms: int = 20000) -> Row:
    deadline = time.monotonic() + (timeout_ms / 1000)
    last_payload: Row | None = None
    while time.monotonic() < deadline:
        payload = _fetch_json(page, "/api/export-profiles?limit=40")
        last_payload = payload
        if _as_int(payload.get("status")) == 200:
            for row in _rows(payload.get("data")):
                if str(row.get("report_id") or "").strip() != report_id:
                    continue
                if str(row.get("name") or "").strip().lower() != name.strip().lower():
                    continue
                return row
        time.sleep(0.2)
    raise AssertionError(f"timed out waiting for export profile {name!r} on {report_id!r}: {last_payload}")


def _wait_for_delivery_subscription(page: Page, subject_ref: str, output_kind: str, *, timeout_ms: int = 20000) -> Row:
    deadline = time.monotonic() + (timeout_ms / 1000)
    last_payload: Row | None = None
    while time.monotonic() < deadline:
        payload = _fetch_json(page, "/api/delivery-subscriptions?limit=40")
        last_payload = payload
        if _as_int(payload.get("status")) == 200:
            for row in _rows(payload.get("data")):
                if str(row.get("subject_ref") or "").strip() != subject_ref:
                    continue
                if str(row.get("output_kind") or "").strip().lower() != output_kind.strip().lower():
                    continue
                return row
        time.sleep(0.2)
    raise AssertionError(
        f"timed out waiting for delivery subscription subject={subject_ref!r} output={output_kind!r}: {last_payload}"
    )


def _wait_for_delivery_dispatch_record(
    page: Page,
    subscription_id: str,
    *,
    status: str = "delivered",
    timeout_ms: int = 20000,
) -> Row:
    deadline = time.monotonic() + (timeout_ms / 1000)
    last_payload: Row | None = None
    while time.monotonic() < deadline:
        payload = _fetch_json(
            page,
            f"/api/delivery-dispatch-records?subscription_id={subscription_id}&status={status}&limit=20",
        )
        last_payload = payload
        if _as_int(payload.get("status")) == 200:
            rows = _rows(payload.get("data"))
            if rows:
                return rows[0]
        time.sleep(0.2)
    raise AssertionError(
        f"timed out waiting for delivery dispatch record subscription={subscription_id!r} status={status!r}: {last_payload}"
    )


def _wait_for_report_markdown(
    page: Page,
    report_id: str,
    *,
    expected_fragments: Sequence[str],
    timeout_ms: int = 20000,
) -> str:
    deadline = time.monotonic() + (timeout_ms / 1000)
    last_payload: Row | None = None
    while time.monotonic() < deadline:
        payload = _fetch_text(page, f"/api/reports/{report_id}/export?output_format=markdown")
        last_payload = payload
        text = str(payload.get("text") or "")
        if _as_int(payload.get("status")) == 200 and all(fragment in text for fragment in expected_fragments):
            return text
        time.sleep(0.2)
    raise AssertionError(f"timed out waiting for markdown export on {report_id!r}: {last_payload}")


def _export_console_overflow_evidence(page: Page) -> Row:
    _log("[console-browser-smoke] console overflow evidence")
    page.evaluate("jumpToSection('section-ops')")
    page.wait_for_function(
        """() => {
            return window.location.hash === '#section-ops'
                && !!document.querySelector('#console-overflow-evidence-card')
                && !!document.querySelector('[data-console-overflow-summary]')
                && !!document.querySelector('[data-console-overflow-hotspots]');
        }""",
        timeout=10000,
    )
    payload = page.evaluate(
        """() => {
            const evidence = typeof window.getConsoleOverflowEvidence === "function"
                ? window.getConsoleOverflowEvidence()
                : window.__DATAPULSE_CONSOLE_OVERFLOW__;
            return {
                evidence,
                summary_text: document.querySelector("[data-console-overflow-summary]")?.textContent || "",
                hotspot_lines: Array.from(
                    document.querySelectorAll("[data-overflow-surface]"),
                    (node) => node.textContent || "",
                ),
                body_hotspots: document.body?.dataset.consoleOverflowHotspots || "",
                body_survivors: document.body?.dataset.consoleOverflowSurvivors || "",
            };
        }"""
    )
    if not isinstance(payload, dict):
        raise AssertionError(f"console overflow evidence payload was not a mapping: {payload!r}")
    evidence = _row(payload.get("evidence"))
    if evidence is None:
        raise AssertionError(f"console overflow evidence was missing: {payload}")
    if _as_int(evidence.get("surface_count")) <= 0:
        raise AssertionError(f"console overflow evidence did not sample any surfaces: {payload}")
    if _as_int(evidence.get("checked_sample_count")) <= 0:
        raise AssertionError(f"console overflow evidence did not record any checked samples: {payload}")
    summary_text = str(payload.get("summary_text") or "")
    if "surfaces=" not in summary_text or "survivors=" not in summary_text:
        raise AssertionError(f"console overflow summary card was not operator-visible: {payload}")
    for hotspot in _rows(evidence.get("residual_surfaces")):
        if not str(hotspot.get("surface_id") or "").strip():
            raise AssertionError(f"console overflow hotspot omitted a surface id: {payload}")
    _log(f"[console-browser-smoke] overflow-evidence {json.dumps(payload, ensure_ascii=False, sort_keys=True)}")
    return cast(Row, payload)


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
    _log("[console-browser-smoke] deep-link watch")
    _goto(page, f"{base_url}/?watch_search=Launch&watch_id=launch-ops#section-cockpit")
    _wait_for_console_ready(page)
    page.wait_for_function("() => window.location.hash === '#section-cockpit'", timeout=10000)
    page.wait_for_function("() => window.location.search.includes('watch_search=Launch')", timeout=10000)
    page.wait_for_function("() => window.location.search.includes('watch_id=launch-ops')", timeout=10000)
    page.wait_for_function("() => document.querySelector('[data-watch-search]')?.value === 'Launch'", timeout=10000)
    page.wait_for_function("() => document.querySelector('#watch-detail')?.textContent?.includes('Launch Ops')", timeout=10000)
    _wait_for_section_summary(page, "section-cockpit")
    _wait_for_operator_guidance_surface(page, "cockpit-guidance-surface")
    page.wait_for_function(
        """() => {
            const railStep = document.querySelector('[data-context-object-step="mission"] .context-object-step-value');
            const summary = document.querySelector('#context-summary');
            return (railStep?.textContent || '').includes('Launch Ops')
                && (summary?.textContent || '').trim().length > 0
                && summary?.getAttribute('title') === summary?.textContent;
        }""",
        timeout=10000,
    )

    _log("[console-browser-smoke] palette run-due")
    page.evaluate("openCommandPalette()")
    page.wait_for_selector(".palette-backdrop.open", timeout=10000)
    page.fill("#command-palette-input", "run due")
    page.keyboard.press("Enter")
    page.wait_for_function("() => document.body.textContent.includes('Due missions dispatched')", timeout=10000)
    page.keyboard.press("Escape")
    page.wait_for_function("() => !document.querySelector('.palette-backdrop')?.classList.contains('open')", timeout=10000)


def _exercise_stage_aware_initial_hydration(page: Page, base_url: str) -> None:
    _log("[console-browser-smoke] stage-aware initial hydration")
    requests = _track_api_requests(page)
    _goto(page, base_url)
    _wait_for_console_ready(page)
    page.wait_for_function("() => !window.location.hash || window.location.hash === '#section-intake'", timeout=10000)
    time.sleep(0.4)
    api_paths = {path for path in requests if path.startswith("/api/")}
    assert api_paths == {"/api/overview"}, f"unexpected initial api scope: {sorted(api_paths)}"


def _exercise_navigation_convergence(page: Page) -> None:
    _log("[console-browser-smoke] navigation convergence")
    page.wait_for_function("() => document.querySelectorAll('.topbar-nav .nav-pill').length === 4", timeout=10000)
    page.wait_for_function(
        """() => {
            const navMissions = !!document.querySelector('#nav-missions');
            const navReview = !!document.querySelector('#nav-review');
            const navIntake = !!document.querySelector('#nav-intake');
            const navDelivery = !!document.querySelector('#nav-delivery');
            return navMissions && navReview && navIntake && navDelivery;
        }""",
        timeout=10000,
    )
    _wait_for_active_rail(page, "nav-missions", "#section-cockpit")
    _wait_for_stage_shell(page)
    _click(page, "#nav-review")
    _wait_for_active_rail(page, "nav-review", "#section-triage")
    _wait_for_stage_shell(page)
    _wait_for_section_summary(page, "section-triage")
    page.wait_for_function("() => !document.querySelector('#review-advanced-shell')?.open", timeout=10000)
    _click(page, "#nav-delivery")
    _wait_for_active_rail(page, "nav-delivery", "#section-ops")
    _wait_for_stage_shell(page)
    _wait_for_section_summary(page, "section-ops")
    page.wait_for_function("() => !document.querySelector('#delivery-advanced-shell')?.open", timeout=10000)
    _click(page, "#nav-intake")
    _wait_for_active_rail(page, "nav-intake", "#section-intake")
    _wait_for_stage_shell(page)
    _wait_for_section_summary(page, "section-intake")
    _click(page, "#nav-missions")
    _wait_for_active_rail(page, "nav-missions", "#section-board")
    _wait_for_stage_shell(page)
    _wait_for_section_summary(page, "section-board")


def _exercise_workflow_stage_acceptance(page: Page) -> None:
    _log("[console-browser-smoke] workflow stage acceptance")
    page.wait_for_function(
        """() => {
            const ids = Array.from(document.querySelectorAll('.topbar-nav .nav-pill')).map((button) => button.id || '');
            return ids.join('|') === 'nav-intake|nav-missions|nav-review|nav-delivery';
        }""",
        timeout=10000,
    )

    page.evaluate("jumpToSection('section-intake')")
    page.wait_for_function("() => window.location.hash === '#section-intake'", timeout=10000)
    _wait_for_active_rail(page, "nav-intake", "#section-intake")
    _assert_stage_shell(
        page,
        stage=["Start", "开始"],
        current_surface=["Mission Intake", "任务录入"],
        current_object_contains=["Launch Ops", "Launch Ops"],
        owned_output_contains=["live missions", "实时任务", "open triage", "待分诊"],
        next_action_contains=["Open Cockpit", "打开任务详情"],
        compact=True,
    )
    page.fill("#create-watch-form [name='name']", "")
    page.fill("#create-watch-form [name='query']", "")
    _submit_form_without_validation(page, "#create-watch-form")
    _wait_for_stage_feedback(
        page,
        stage="start",
        kind="blocked",
        title_contains=["blocked by required fields", "必填字段"],
    )
    _click(page, '[data-stage-feedback-stage="start"] [data-card-action-primary] button')
    page.wait_for_function("() => document.activeElement?.getAttribute('name') === 'name'", timeout=10000)

    no_result_watch_name = "Browser Smoke No Result Mission"
    page.fill("#create-watch-form [name='name']", no_result_watch_name)
    page.fill("#create-watch-form [name='query']", "browser smoke no result")
    _submit_form(page, "#create-watch-form")
    _wait_for_stage_feedback(page, stage="start", kind="completion", title_contains=["Watch created", "任务已创建"])
    page.wait_for_function(
        """() => {
            const button = document.querySelector('[data-stage-feedback-stage="start"] [data-card-action-primary] button');
            const text = button?.textContent || '';
            return !!button && (text.includes('Mission Board') || text.includes('任务列表'));
        }""",
        timeout=10000,
    )
    watches_payload = _fetch_json(page, "/api/watches")
    assert _as_int(watches_payload.get("status")) == 200, f"watch list failed after start acceptance create: {watches_payload}"
    watch_rows = _rows(watches_payload.get("data"))
    no_result_watch_row = next((row for row in watch_rows if str(row.get("name") or "").strip() == no_result_watch_name), None)
    if no_result_watch_row is None:
        create_payload = _fetch_json(
            page,
            "/api/watches",
            method="POST",
            payload={
                "name": no_result_watch_name,
                "query": "browser smoke no result",
                "schedule": "manual",
            },
        )
        assert _as_int(create_payload.get("status")) == 200, f"fallback watch create failed: {create_payload}"
        no_result_watch_row = _row(create_payload.get("data"))
    assert no_result_watch_row is not None, "no-result acceptance watch could not be resolved"
    no_result_watch_id = str(no_result_watch_row.get("id") or "").strip()
    assert no_result_watch_id, f"missing no-result watch id: {no_result_watch_row}"
    page.evaluate("(identifier) => loadWatch(identifier)", no_result_watch_id)
    page.evaluate("jumpToSection('section-intake')")
    page.wait_for_function("() => window.location.hash === '#section-intake'", timeout=10000)
    _wait_for_active_rail(page, "nav-intake", "#section-intake")
    _assert_stage_shell(
        page,
        stage=["Start", "开始"],
        current_surface=["Mission Intake", "任务录入"],
        current_object_contains=[no_result_watch_name, "Launch Ops"],
        owned_output_contains=["live missions", "实时任务", "open triage", "待分诊"],
        next_action_contains=["Open Cockpit", "Open Mission Board", "打开任务详情", "打开任务列表"],
        compact=True,
    )
    _assert_populated_intake_chrome(page, [no_result_watch_name, "Launch Ops"])
    page.evaluate("refreshBoard()")
    page.evaluate("jumpToSection('section-board')")
    page.wait_for_function("() => window.location.hash === '#section-board'", timeout=10000)
    _wait_for_active_rail(page, "nav-missions", "#section-board")
    page.fill("[data-watch-search]", "")
    _assert_stage_shell(
        page,
        stage=["Monitor", "监测"],
        current_surface=["Mission Board", "任务列表"],
        current_object_contains=[no_result_watch_name, "Launch Ops"],
        owned_output_contains=["stored results", "已存储结果"],
        next_action_contains=["Open Cockpit", "打开任务详情"],
        compact=True,
    )
    page.fill("[data-watch-search]", "__monitor_no_match__")
    page.wait_for_function(
        """() => {
            const board = document.querySelector('#watch-list');
            const summary = document.querySelector('[data-section-summary="section-board"]');
            const boardText = board ? board.textContent || '' : '';
            const summaryText = summary ? summary.textContent || '' : '';
            return (
                boardText.includes('No mission matched the current search.')
                || boardText.includes('没有任务匹配当前搜索。')
            ) && (
                summaryText.includes('zero matches')
                || summaryText.includes('没有命中')
            );
        }""",
        timeout=10000,
    )
    _click(page, "[data-watch-search-clear]")
    page.wait_for_function(
        "() => document.querySelector('#watch-list')?.textContent?.includes('Launch Ops')",
        timeout=10000,
    )

    page.evaluate("jumpToSection('section-triage')")
    page.wait_for_function("() => window.location.hash === '#section-triage'", timeout=10000)
    _wait_for_active_rail(page, "nav-review", "#section-triage")
    _assert_stage_shell(
        page,
        stage=["Review", "审阅"],
        current_surface=["Triage", "Triage Queue", "分诊", "分诊队列"],
        current_object_contains=["OpenAI launch post", "OpenAI launch post"],
        owned_output_contains=["open items in triage", "分诊中有"],
        next_action_contains=[
            "Open Story Editor",
            "Open Triage",
            "打开故事编辑",
            "打开分诊",
        ],
        compact=True,
    )

    page.evaluate("jumpToSection('section-ops')")
    page.wait_for_function("() => window.location.hash === '#section-ops'", timeout=10000)
    _wait_for_active_rail(page, "nav-delivery", "#section-ops")
    _assert_stage_shell(
        page,
        stage=["Deliver", "交付"],
        current_surface=["Delivery Lane", "Ops Snapshot", "交付工作线", "运行状态"],
        current_object_contains=["ops-webhook", "ops-webhook"],
        owned_output_contains=["healthy routes", "健康路由"],
        next_action_contains=["Open Delivery Lane", "打开交付工作线"],
        compact=True,
    )
    _wait_for_trace_and_signal_taxonomy(page)
    page.wait_for_function(
        """(expectedStarts) => {
            const stageIds = Array.from(document.querySelectorAll('[data-stage-trace="workflow"] [data-trace-stage]')).map((node) => node.getAttribute('data-trace-stage'));
            const start = document.querySelector('[data-trace-stage="start"]')?.textContent || '';
            const deliver = document.querySelector('[data-trace-stage="deliver"]')?.textContent || '';
            return JSON.stringify(stageIds) === JSON.stringify(['start', 'monitor', 'review', 'deliver'])
                && expectedStarts.some((entry) => start.includes(entry))
                && (deliver.includes('ops-webhook') || deliver.includes('Delivery outcome'));
        }""",
        arg=[no_result_watch_name, "Launch Ops"],
        timeout=10000,
    )
    _assert_signal_owner(
        page,
        "quality",
        [
            "Triage and promotion surfaces",
            "分诊与提升 surface",
            "Story evidence context",
            "故事证据上下文",
            "Story contradiction markers",
            "故事冲突标记",
            "Report quality guardrails",
            "报告质量门禁",
        ],
    )
    _assert_signal_owner(page, "delivery", ["Delivery workspace and dispatch record", "交付工作台与 dispatch 记录"])
    _assert_signal_owner(page, "overflow", "console-overflow-evidence-card")
    _assert_signal_owner(page, "trust", ["Retry guidance", "重试建议"])
    _assert_signal_primary_action_target(page, "delivery", "section-ops")
    _assert_signal_explicit_outcome(page, "overflow", "section-ops")
    _assert_signal_primary_action_routes(page, "quality", "#section-report-studio", "nav-review")
    _assert_signal_primary_action_target(page, "trust", "section-cockpit")


def _exercise_saved_views_and_dock(page: Page, base_url: str, browser) -> Page:
    saved_view_name = "Verified Queue 多语种切片缓存标签 for dense console handoff coverage"
    _log("[console-browser-smoke] save view and set default")
    _goto(page, f"{base_url}/?triage_filter=verified#section-triage")
    _wait_for_console_ready(page)
    page.wait_for_function("() => window.location.hash === '#section-triage'", timeout=10000)
    page.wait_for_function("() => window.location.search.includes('triage_filter=verified')", timeout=10000)
    page.wait_for_function("() => !!document.querySelector('[data-triage-card=\"item-2\"]')", timeout=10000)
    _wait_for_section_summary(page, "section-triage")
    _wait_for_context_dock_state(page, visible=False)
    _open_context_lens(page, "#context-summary")
    page.fill("#context-save-name", saved_view_name)
    _click(page, "#context-save-submit")
    page.wait_for_function("(expectedName) => document.querySelector('#context-lens-saved')?.textContent?.includes(expectedName)", arg=saved_view_name, timeout=10000)
    _wait_for_context_dock_state(page, visible=False)
    _click(page, "[data-context-saved-pin='0']")
    _wait_for_context_dock_state(page, visible=True)
    page.wait_for_function(
        """(expectedName) => {
            const button = document.querySelector('[data-context-dock-open="0"]');
            return !!button
                && button.dataset.fitTextOriginal === expectedName
                && button.dataset.fitApplied === 'true'
                && button.textContent !== expectedName
                && button.textContent.includes('…');
        }""",
        arg=saved_view_name,
        timeout=10000,
    )
    _click(page, "[data-context-saved-default='0']")
    page.wait_for_function(
        "() => JSON.parse(localStorage.getItem('datapulse.console.context-saved-views.v1') || '[]')[0]?.isDefault === true",
        timeout=10000,
    )

    _log("[console-browser-smoke] default boot and dock restore")
    next_page = browser.new_page()
    _bind_page_logging(next_page, "page-2")
    _goto(next_page, base_url)
    _wait_for_console_ready(next_page)
    next_page.wait_for_function("() => window.location.hash === '#section-triage'", timeout=10000)
    next_page.wait_for_function("() => window.location.search.includes('triage_filter=verified')", timeout=10000)
    next_page.wait_for_function("() => document.querySelector('[data-triage-card=\"item-2\"]')?.classList.contains('selected')", timeout=10000)
    _wait_for_section_summary(next_page, "section-triage")
    _wait_for_operator_guidance_surface(next_page, "triage-guidance-surface")
    _wait_for_context_dock_state(next_page, visible=True)
    next_page.wait_for_function(
        """(expectedName) => {
            const button = document.querySelector('[data-context-dock-open="0"]');
            return !!button
                && button.dataset.fitTextOriginal?.includes(expectedName)
                && button.dataset.fitApplied === 'true';
        }""",
        arg=saved_view_name,
        timeout=10000,
    )
    _wait_for_active_rail(next_page, "nav-review", "#section-triage")
    next_page.evaluate(
        """() => {
            const button = document.querySelector('#context-summary');
            if (!button) {
                return;
            }
            button.style.maxWidth = '180px';
            button.textContent = 'Mission intake | 多语言缓存像素拟合覆盖 for dense rail summary verification';
            delete button.dataset.fitTextOriginal;
            delete button.dataset.fitApplied;
            scheduleCanvasTextFit(button);
        }"""
    )
    next_page.wait_for_function(
        """() => {
            const button = document.querySelector('#context-summary');
            return !!button
                && button.dataset.fitApplied === 'true'
                && button.dataset.fitTextOriginal?.includes('多语言缓存像素拟合覆盖')
                && button.textContent.includes('…');
        }""",
        timeout=10000,
    )
    _jump_to_section_with_fallback(next_page, "section-story", selector="[data-context-section='section-story']")
    _wait_for_active_rail(next_page, "nav-review", "#section-story")
    _jump_to_section_with_fallback(next_page, "section-triage", selector="[data-context-section='section-triage']")
    _wait_for_active_rail(next_page, "nav-review", "#section-triage")
    _wait_for_section_summary(next_page, "section-triage")
    _open_context_lens(next_page, "[data-context-dock-manage]")
    _close_context_lens(next_page)
    next_page.evaluate("jumpToSection('section-intake')")
    next_page.wait_for_function("() => window.location.hash === '#section-intake'", timeout=10000)
    _wait_for_active_rail(next_page, "nav-intake", "#section-intake")
    next_page.evaluate("(viewName) => restoreContextSavedViewByName(viewName)", saved_view_name)
    next_page.wait_for_function("() => window.location.hash === '#section-triage'", timeout=10000)
    next_page.wait_for_function("() => window.location.search.includes('triage_filter=verified')", timeout=10000)
    _wait_for_active_rail(next_page, "nav-review", "#section-triage")
    _wait_for_section_summary(next_page, "section-triage")
    _wait_for_operator_guidance_surface(next_page, "triage-guidance-surface")
    _open_context_lens(next_page, "#context-summary")
    next_page.evaluate("renderTopbarContext()")
    _wait_for_context_lens_state(next_page, open_state=True)
    _close_context_lens(next_page)
    return next_page


def _exercise_route_crud(page: Page) -> None:
    _log("[console-browser-smoke] route crud")
    page.evaluate("jumpToSection('section-ops')")
    page.wait_for_function("() => window.location.hash === '#section-ops'", timeout=10000)
    _wait_for_active_rail(page, "nav-delivery", "#section-ops")
    _wait_for_section_summary(page, "section-ops")
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
    _log("[console-browser-smoke] triage to story")
    _goto(page, f"{base_url}/?triage_filter=all#section-triage")
    _wait_for_console_ready(page)
    page.wait_for_function("() => window.location.hash === '#section-triage'", timeout=10000)
    _wait_for_active_rail(page, "nav-review", "#section-triage")
    _wait_for_section_summary(page, "section-triage")
    page.wait_for_function(
        """() => {
            const primary = document.querySelector('[data-card-action-primary] button[data-triage-state="escalated"][data-triage-id="item-1"]');
            const verify = document.querySelector('[data-card-action-secondary] button[data-triage-state="verified"][data-triage-id="item-1"]');
            const story = document.querySelector('[data-card-action-secondary] button[data-empty-jump="section-story"]');
            const danger = document.querySelector('[data-card-action-danger] button[data-triage-delete="item-1"]');
            return !!primary && !!verify && !!story && !!danger;
        }""",
        timeout=20000,
    )
    page.wait_for_function(
        """() => {
            const primary = document.querySelector('[data-card-action-primary] button[data-triage-story="item-2"]');
            const secondary = document.querySelector('[data-card-action-secondary] button[data-triage-explain="item-2"]');
            const danger = document.querySelector('[data-card-action-danger] button[data-triage-delete="item-2"]');
            return !!primary && !!secondary && !!danger;
        }""",
        timeout=20000,
    )
    _click(page, "[data-triage-story='item-2']")
    page.wait_for_timeout(2000)
    assert page.evaluate("() => window.location.hash === '#section-story'"), "triage-to-story flow did not jump to section-story"
    page.wait_for_function("() => window.location.search.includes('story_id=story-triage-seed')", timeout=10000)
    page.wait_for_function("() => window.location.search.includes('story_mode=editor')", timeout=10000)
    _wait_for_active_rail(page, "nav-review", "#section-story")
    _wait_for_section_summary(page, "section-story")
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


def _exercise_report_workspaces(page: Page) -> Row:
    _log("[console-browser-smoke] report workspaces")
    brief_list = _fetch_json(page, "/api/report-briefs")
    assert _as_int(brief_list.get("status")) == 200, f"report brief list failed: {brief_list}"
    brief_payload = _fetch_json(
        page,
        "/api/report-briefs",
        method="POST",
        payload={
            "title": "Browser Smoke Brief",
            "objective": "Verify report browser workspace and watch-pack flows.",
            "status": "draft",
        },
    )
    assert _as_int(brief_payload.get("status")) == 200, f"report brief create failed: {brief_payload}"
    brief_row = _row(brief_payload.get("data"))
    assert brief_row is not None, f"unexpected report brief payload: {brief_payload}"
    brief_id = str(brief_row.get("id") or "").strip()
    assert brief_id, f"missing report brief id: {brief_payload}"

    report_title = "Browser Smoke Report"
    section_title = "Signal Summary"
    claim_statement = "Browser smoke claim is grounded."
    watch_name = "Browser Smoke Follow-up Watch"
    watch_query = "Browser smoke report follow-up"

    page.evaluate("jumpToSection('section-report-studio')")
    page.wait_for_function("() => window.location.hash === '#section-report-studio'", timeout=10000)
    _wait_for_active_rail(page, "nav-review", "#section-report-studio")
    page.wait_for_function("() => !!document.querySelector('#review-advanced-shell')?.open", timeout=10000)
    page.wait_for_selector("#report-create-form", state="attached", timeout=10000)
    page.fill("#report-create-form [name='title']", report_title)
    page.fill("#report-create-form [name='audience']", "ops")
    page.fill("#report-create-form [name='summary']", "Browser smoke validates report composition, export, and follow-up watch reuse.")
    _submit_form(page, "#report-create-form")
    report_id = _wait_for_report_id(page, report_title)
    page.evaluate("refreshBoard()")
    page.wait_for_function(
        "(reportId) => Array.from(document.querySelector('#report-studio-select')?.options || []).some((entry) => entry.value === reportId)",
        arg=report_id,
        timeout=20000,
    )
    page.select_option("#report-studio-select", report_id)
    page.wait_for_function(
        "(reportId) => document.querySelector('#report-studio-select')?.value === reportId",
        arg=report_id,
        timeout=20000,
    )
    assert report_id, "report create flow did not expose the new report id"
    report_update = _fetch_json(
        page,
        f"/api/reports/{report_id}",
        method="PUT",
        payload={"brief_id": brief_id},
    )
    assert _as_int(report_update.get("status")) == 200, f"report brief binding failed: {report_update}"
    page.evaluate("refreshBoard()")
    page.wait_for_function("([reportId, title]) => document.querySelector('#report-studio-select')?.value === reportId && document.querySelector('#section-report-studio')?.textContent?.includes(title)", arg=[report_id, report_title], timeout=20000)
    page.wait_for_function(
        "() => Array.from(document.querySelectorAll('#section-report-studio .chip')).some((chip) => chip.textContent?.includes('watch-pack'))",
        timeout=10000,
    )

    page.fill("#report-section-form [name='title']", section_title)
    page.fill("#report-section-form [name='position']", "1")
    page.fill("#report-section-form [name='summary']", "Track the grounded evidence that survives composition and export.")
    _submit_form(page, "#report-section-form")
    section_id = _wait_for_report_section_id(page, report_id, section_title)
    page.evaluate("refreshBoard()")
    page.wait_for_function(
        "([reportId, sectionId]) => document.querySelector('#report-studio-select')?.value === reportId && !!document.querySelector(`[data-report-section-focus=\"${sectionId}\"]`)",
        arg=[report_id, section_id],
        timeout=20000,
    )
    _click(page, f'[data-report-section-focus="{section_id}"]')
    page.wait_for_function("() => window.location.hash === '#section-claims'", timeout=10000)
    _wait_for_active_rail(page, "nav-review", "#section-claims")
    page.wait_for_function("() => !!document.querySelector('#review-advanced-shell')?.open", timeout=10000)
    page.wait_for_function(
        "(reportId) => document.querySelector('#claim-report-select')?.value === reportId && document.querySelector('#claim-section-select')?.value !== ''",
        arg=report_id,
        timeout=20000,
    )

    page.fill("#claim-composer-form [name='statement']", claim_statement)
    page.fill("#claim-composer-form [name='rationale']", "Browser smoke keeps the claim attached to both item ids and citation bundles.")
    page.fill("#claim-composer-form [name='confidence']", "0.93")
    page.fill("#claim-composer-form [name='source_item_ids']", "item-1")
    page.fill("#claim-composer-form [name='source_urls']", "https://example.com/browser-smoke-claim")
    page.fill("#claim-composer-form [name='bundle_note']", "Browser smoke source binding")
    _submit_form(page, "#claim-composer-form")
    created_claim = _wait_for_claim_card(page, claim_statement)
    created_bundle = _wait_for_citation_bundle(page, str(created_claim.get("id") or "").strip(), "browser-smoke-claim")
    assert _strings(created_claim.get("source_item_ids")) == ["item-1"], f"claim source binding mismatch: {created_claim}"
    assert "https://example.com/browser-smoke-claim" in _strings(created_bundle.get("source_urls")), f"bundle source url mismatch: {created_bundle}"
    page.evaluate("refreshBoard()")
    page.wait_for_function(
        "([statement, urlFragment]) => document.querySelector('#section-claims')?.textContent?.includes(statement) && document.querySelector('#section-claims')?.textContent?.includes(urlFragment)",
        arg=[claim_statement, "browser-smoke-claim"],
        timeout=20000,
    )

    page.evaluate("jumpToSection('section-report-studio')")
    page.wait_for_function("() => window.location.hash === '#section-report-studio'", timeout=10000)
    page.wait_for_function(
        "([sectionTitle, claimSnippet]) => document.querySelector('#section-report-studio')?.textContent?.includes(sectionTitle) && document.querySelector('#section-report-studio')?.textContent?.includes(claimSnippet)",
        arg=[section_title, "Browser smoke claim"],
        timeout=20000,
    )
    _click(page, "[data-report-compose-refresh]")
    composed_report = _wait_for_report_compose_ready(page, report_id)
    composed_quality = _row(composed_report.get("quality"))
    assert composed_quality is not None, f"compose payload missing quality: {composed_report}"
    assert str(composed_quality.get("status") or "").strip().lower() == "ready", f"compose quality was not ready: {composed_quality}"
    assert bool(composed_quality.get("can_export")), f"compose quality did not allow export: {composed_quality}"
    page.evaluate(
        """async (reportId) => {
            if (typeof selectReport === "function") {
                await selectReport(reportId);
            }
        }""",
        report_id,
    )
    _click(page, "[data-report-preview-markdown]")
    exported_markdown = _wait_for_report_markdown(
        page,
        report_id,
        expected_fragments=[report_title, section_title, claim_statement],
    )
    assert "## Signal Summary" in exported_markdown, f"markdown export did not include section heading: {exported_markdown}"
    page.evaluate(
        """async (reportId) => {
            if (typeof previewReportMarkdown === "function") {
                await previewReportMarkdown(reportId);
            }
        }""",
        report_id,
    )
    page.wait_for_function(
        "([reportTitle, sectionTitle, claimStatement]) => { const preview = document.querySelector('#section-report-studio pre.text-block'); return !!preview && preview.textContent.includes(reportTitle) && preview.textContent.includes(sectionTitle) && preview.textContent.includes(claimStatement); }",
        arg=[report_title, section_title, claim_statement],
        timeout=20000,
    )

    profiles_payload = _fetch_json(page, "/api/export-profiles")
    assert _as_int(profiles_payload.get("status")) == 200, f"export profile list failed: {profiles_payload}"
    profile_rows = _rows(profiles_payload.get("data"))
    watch_pack_profile = next(
        (
            row
            for row in profile_rows
            if isinstance(row, dict)
            and str(row.get("report_id") or "").strip() == report_id
            and str(row.get("name") or "").strip().lower() == "watch-pack"
        ),
        None,
    )
    assert watch_pack_profile is not None, f"missing watch-pack profile for {report_id}: {profile_rows}"
    watch_pack_payload = _fetch_json(page, f"/api/reports/{report_id}/watch-pack")
    assert _as_int(watch_pack_payload.get("status")) == 200, f"watch-pack route failed: {watch_pack_payload}"
    watch_pack = _row(watch_pack_payload.get("data"))
    assert watch_pack is not None, f"unexpected watch-pack payload: {watch_pack_payload}"
    assert str(watch_pack.get("report_id") or "") == report_id, f"watch-pack report id mismatch: {watch_pack}"
    assert str(watch_pack.get("query") or "") == report_title, f"watch-pack query mismatch: {watch_pack}"
    watch_create_payload = _fetch_json(
        page,
        f"/api/reports/{report_id}/watch-from-pack",
        method="POST",
        payload={
            "profile_id": str(watch_pack_profile.get("id") or ""),
            "name": watch_name,
            "query": watch_query,
            "platforms": ["twitter"],
        },
    )
    assert _as_int(watch_create_payload.get("status")) == 200, f"watch-from-pack failed: {watch_create_payload}"
    created_watch = _row(watch_create_payload.get("data"))
    assert created_watch is not None, f"unexpected watch-from-pack payload: {watch_create_payload}"
    assert str(created_watch.get("name") or "") == watch_name, f"watch name mismatch: {created_watch}"
    assert str(created_watch.get("query") or "") == watch_query, f"watch query mismatch: {created_watch}"

    page.evaluate("refreshBoard()")
    page.evaluate("jumpToSection('section-cockpit')")
    page.wait_for_function("() => window.location.hash === '#section-cockpit'", timeout=10000)
    _wait_for_active_rail(page, "nav-missions", "#section-cockpit")
    page.wait_for_function(
        "(expectedName) => document.querySelector('#watch-list')?.textContent?.includes(expectedName)",
        arg=watch_name,
        timeout=20000,
    )
    return {
        "report_id": report_id,
        "report_title": report_title,
        "watch_name": watch_name,
    }


def _exercise_delivery_workspace(page: Page, report_context: Row) -> None:
    _log("[console-browser-smoke] delivery workspace")
    report_id = str(report_context.get("report_id") or "").strip()
    assert report_id, f"missing report context for delivery workspace: {report_context}"
    brief_profile = _wait_for_export_profile(page, report_id, "brief")

    page.evaluate("jumpToSection('section-ops')")
    page.wait_for_function("() => window.location.hash === '#section-ops'", timeout=10000)
    _wait_for_active_rail(page, "nav-delivery", "#section-ops")
    _wait_for_stage_shell(page)
    page.wait_for_function("() => !document.querySelector('#delivery-advanced-shell')?.open", timeout=10000)
    page.evaluate("openAdvancedSurfaceShell('delivery-advanced-shell')")
    page.wait_for_function("() => !!document.querySelector('#delivery-advanced-shell')?.open", timeout=10000)
    page.wait_for_function(
        "() => !!document.querySelector('#delivery-subscription-form')",
        timeout=20000,
    )
    page.wait_for_function("() => !!document.querySelector('#digest-profile-form')", timeout=20000)
    page.fill("#digest-profile-form [name='language']", "zh-CN")
    page.fill("#digest-profile-form [name='timezone']", "Asia/Shanghai")
    page.fill("#digest-profile-form [name='frequency']", "@hourly")
    page.select_option("#digest-profile-form [name='default_delivery_target_ref']", "ops-webhook")
    _submit_form(page, "#digest-profile-form")

    digest_profile_payload = _fetch_json(page, "/api/digest-profile")
    assert _as_int(digest_profile_payload.get("status")) == 200, f"digest profile route failed: {digest_profile_payload}"
    digest_profile = _row(digest_profile_payload.get("data"))
    assert digest_profile is not None, f"unexpected digest profile payload: {digest_profile_payload}"
    profile_body = _row(digest_profile.get("profile"))
    assert profile_body is not None, f"missing digest profile body: {digest_profile}"
    assert str(profile_body.get("language") or "") == "zh-CN", f"digest language mismatch: {digest_profile}"
    assert str(profile_body.get("timezone") or "") == "Asia/Shanghai", f"digest timezone mismatch: {digest_profile}"
    assert str(profile_body.get("frequency") or "") == "@hourly", f"digest frequency mismatch: {digest_profile}"

    _click(page, "[data-digest-refresh]")
    page.wait_for_function(
        """() => {
            const promptPreview = document.querySelector('#digest-preview-prompts');
            return !!promptPreview && promptPreview.textContent.includes('digest_delivery_default');
        }""",
        timeout=20000,
    )
    _click(page, "[data-digest-dispatch]")
    _wait_for_digest_dispatch_result(page, route_name="ops-webhook", status="delivered")
    page.wait_for_function(
        """() => {
            const diagnostics = document.querySelector('#digest-route-diagnostics');
            const text = diagnostics ? (diagnostics.textContent || '').trim() : '';
            return !!text
                && !text.includes('No route-backed diagnostic row is visible yet.')
                && !text.includes('当前还没有看到路由诊断记录');
        }""",
        timeout=20000,
    )

    page.select_option("#delivery-subscription-form [name='subject_kind']", "report")
    page.wait_for_function(
        """(targetReportId) => {
            const select = document.querySelector('#delivery-subscription-form [name="subject_ref"]');
            return !!select && Array.from(select.options || []).some((option) => option.value === targetReportId);
        }""",
        arg=report_id,
        timeout=20000,
    )
    page.select_option("#delivery-subscription-form [name='subject_ref']", report_id)
    page.select_option("#delivery-subscription-form [name='output_kind']", "report_full")
    page.select_option("#delivery-subscription-form [name='delivery_mode']", "push")
    page.fill("#delivery-subscription-form [name='route_names']", "OPS-WEBHOOK, ops-webhook")
    _submit_form(page, "#delivery-subscription-form")

    created_subscription = _wait_for_delivery_subscription(page, report_id, "report_full")
    subscription_id = str(created_subscription.get("id") or "").strip()
    assert subscription_id, f"delivery create flow did not expose a subscription id: {created_subscription}"
    assert _strings(created_subscription.get("route_names")) == ["ops-webhook"], (
        f"delivery route normalization mismatch: {created_subscription}"
    )

    page.wait_for_function(
        "(subscriptionId) => document.querySelector('#delivery-subscription-select')?.value === subscriptionId",
        arg=subscription_id,
        timeout=20000,
    )
    page.select_option("#delivery-package-profile-select", str(brief_profile.get("id") or ""))
    page.wait_for_function(
        "(profileId) => document.querySelector('#delivery-package-profile-select')?.value === profileId",
        arg=str(brief_profile.get("id") or ""),
        timeout=10000,
    )

    package_payload = _fetch_json(
        page,
        f"/api/delivery-subscriptions/{subscription_id}/package?profile_id={brief_profile.get('id')}",
    )
    assert _as_int(package_payload.get("status")) == 200, f"delivery package route failed: {package_payload}"
    package = _row(package_payload.get("data"))
    assert package is not None, f"unexpected delivery package payload: {package_payload}"
    assert str(package.get("subscription_id") or "") == subscription_id, f"package subscription mismatch: {package}"
    assert str(package.get("profile_id") or "") == str(brief_profile.get("id") or ""), f"package profile mismatch: {package}"

    _click(page, f"[data-delivery-package-refresh='{subscription_id}']")
    page.wait_for_timeout(500)
    _click(page, f"[data-delivery-dispatch='{subscription_id}']")
    dispatch_payload = _fetch_json(
        page,
        f"/api/delivery-subscriptions/{subscription_id}/dispatch",
        method="POST",
        payload={"profile_id": str(brief_profile.get("id") or "")},
    )
    assert _as_int(dispatch_payload.get("status")) == 200, f"delivery dispatch route failed: {dispatch_payload}"
    dispatch_rows = _rows(dispatch_payload.get("data"))
    assert dispatch_rows, f"delivery dispatch returned no rows: {dispatch_payload}"
    dispatch_row = dispatch_rows[0]
    assert str(dispatch_row.get("package_profile_id") or "") == str(brief_profile.get("id") or ""), (
        f"delivery dispatch profile mismatch: {dispatch_row}"
    )
    assert str(dispatch_row.get("route_label") or "") == "webhook:ops-webhook", f"delivery dispatch route mismatch: {dispatch_row}"
    persisted_dispatch = _wait_for_delivery_dispatch_record(page, subscription_id, status="delivered")
    assert str(persisted_dispatch.get("route_label") or "") == "webhook:ops-webhook", f"delivery dispatch persistence mismatch: {persisted_dispatch}"

    pause_payload = _fetch_json(
        page,
        f"/api/delivery-subscriptions/{subscription_id}",
        method="PUT",
        payload={"status": "paused"},
    )
    assert _as_int(pause_payload.get("status")) == 200, f"delivery pause route failed: {pause_payload}"
    paused_subscription = _fetch_json(page, f"/api/delivery-subscriptions/{subscription_id}")
    assert _as_int(paused_subscription.get("status")) == 200, f"delivery show after pause failed: {paused_subscription}"
    assert _row(paused_subscription.get("data")) is not None
    assert str(_row(paused_subscription.get("data")).get("status") or "") == "paused"

    resume_payload = _fetch_json(
        page,
        f"/api/delivery-subscriptions/{subscription_id}",
        method="PUT",
        payload={"status": "active"},
    )
    assert _as_int(resume_payload.get("status")) == 200, f"delivery resume route failed: {resume_payload}"
    active_subscription = _fetch_json(page, f"/api/delivery-subscriptions/{subscription_id}")
    assert _as_int(active_subscription.get("status")) == 200, f"delivery show after resume failed: {active_subscription}"
    assert _row(active_subscription.get("data")) is not None
    assert str(_row(active_subscription.get("data")).get("status") or "") == "active"


def _exercise_responsive_interaction_safety(page: Page) -> None:
    _log("[console-browser-smoke] responsive interaction safety")
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
    _open_context_lens(page, "#context-summary")
    _close_context_lens(page)
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
    app = create_app(reader_factory=cast(Any, lambda: reader))
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
            _exercise_stage_aware_initial_hydration(page, base_url)
            _exercise_deep_link_and_existing_flow(page, base_url)
            _exercise_navigation_convergence(page)
            _exercise_workflow_stage_acceptance(page)
            second_page = _exercise_saved_views_and_dock(page, base_url, context)
            _exercise_route_crud(second_page)
            _exercise_triage_to_story(second_page, base_url)
            report_context = _exercise_report_workspaces(second_page)
            _exercise_delivery_workspace(second_page, report_context)
            _exercise_responsive_interaction_safety(second_page)
            _export_console_overflow_evidence(second_page)
            browser.close()
    finally:
        server.should_exit = True
        thread.join(timeout=5)

    _log("[console-browser-smoke] pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
