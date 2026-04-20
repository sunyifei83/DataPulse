"""Persistent watch/mission definitions for recurring DataPulse workflows."""

from __future__ import annotations

import asyncio
import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .utils import content_fingerprint, generate_slug, watchlist_path_from_env


def _utcnow() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _dedup_lower(values: list[str]) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for raw in values:
        value = str(raw).strip().lower()
        if not value or value in seen:
            continue
        seen.add(value)
        out.append(value)
    return out


def _dedup_text(values: list[Any]) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for raw in values:
        value = str(raw or "").strip()
        if not value:
            continue
        key = value.casefold()
        if key in seen:
            continue
        seen.add(key)
        out.append(value)
    return out


_MARKET_CONTEXT_SIDECAR_USAGE_BY_TYPE = {
    "technical_regime_sidecar": "watch_seed_and_operator_context",
    "market_quote_snapshot": "watch_seed_and_quote_context",
    "strategy_robustness_backtest": "operator_context_only",
    "sentiment_news_contra_sidecar": "operator_context_only",
}


def build_watch_run_readiness(
    mission: "WatchMission",
    *,
    route_status_by_name: dict[str, str] | None = None,
) -> dict[str, Any]:
    reasons: list[str] = []
    blocking_facts: list[str] = []
    route_status_lookup = {
        str(name or "").strip().lower(): str(status or "").strip().lower()
        for name, status in (route_status_by_name or {}).items()
        if str(name or "").strip()
    }

    if not str(mission.query or "").strip():
        blocking_facts.append("missing_query")
        reasons.append("Mission query is empty, so no governed suggestion should be treated as runnable.")
    if not mission.enabled:
        blocking_facts.append("mission_disabled")
        reasons.append("Mission is currently disabled and requires operator enablement before live execution.")
    if str(mission.schedule or "manual").strip().lower() == "manual":
        reasons.append("Mission is manual-only, so operator trigger remains required.")
    if not mission.platforms and not mission.sites:
        reasons.append("Mission has no explicit platform or site scope yet and should be reviewed before broadening.")
    if mission.last_run_status and str(mission.last_run_status).strip().lower() != "success":
        reasons.append("Latest mission run did not complete successfully and should be reviewed before trusting new suggestions.")

    configured_routes: list[str] = []
    for rule in mission.alert_rules:
        if not isinstance(rule, dict):
            continue
        raw_values = rule.get("routes")
        if raw_values is None:
            raw_values = rule.get("route")
        if isinstance(raw_values, str):
            raw_values = [raw_values]
        if not isinstance(raw_values, list):
            continue
        for raw_route in raw_values:
            route_name = str(raw_route or "").strip().lower()
            if route_name and route_name not in configured_routes:
                configured_routes.append(route_name)

    unhealthy_routes: list[str] = []
    unknown_routes: list[str] = []
    for route_name in configured_routes:
        status = route_status_lookup.get(route_name, "")
        if not status:
            unknown_routes.append(route_name)
            continue
        if status not in {"healthy", "idle"}:
            unhealthy_routes.append(route_name)
    if unhealthy_routes:
        reasons.append(
            "Configured delivery routes are not currently healthy: "
            + ", ".join(sorted(unhealthy_routes))
            + "."
        )
    if unknown_routes:
        reasons.append(
            "Configured delivery routes have no observed health facts yet: "
            + ", ".join(sorted(unknown_routes))
            + "."
        )

    status = "ready"
    if blocking_facts:
        status = "blocked"
    elif reasons:
        status = "needs_review"
    if not reasons:
        reasons.append("Mission has query coverage and no blocking runtime facts.")

    payload = {
        "status": status,
        "reasons": _dedup_text(reasons),
    }
    if blocking_facts:
        payload["blocking_facts"] = _dedup_text(blocking_facts)
    return payload


def validate_watch_suggestion_payload(payload: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(payload, dict):
        return ["payload must be an object"]

    summary = str(payload.get("summary", "") or "").strip()
    if not summary:
        errors.append("summary is required")

    run_readiness = payload.get("run_readiness")
    if not isinstance(run_readiness, dict):
        errors.append("run_readiness is required")
    else:
        status = str(run_readiness.get("status", "") or "").strip().lower()
        reasons = run_readiness.get("reasons")
        if status not in {"ready", "needs_review", "blocked"}:
            errors.append("run_readiness.status must be ready/needs_review/blocked")
        if not isinstance(reasons, list) or not any(str(item or "").strip() for item in reasons):
            errors.append("run_readiness.reasons must contain at least one non-empty entry")

    suggestion_fields = (
        "proposed_query",
        "candidate_sites",
        "scope_entities",
        "scope_topics",
        "scope_regions",
    )
    if not any(payload.get(field) for field in suggestion_fields):
        errors.append("at least one suggestion field is required")

    proposed_query = payload.get("proposed_query")
    if proposed_query is not None and not str(proposed_query or "").strip():
        errors.append("proposed_query cannot be empty when present")

    for payload_field in ("candidate_sites", "scope_entities", "scope_topics", "scope_regions", "operator_notes"):
        value = payload.get(payload_field)
        if value is None:
            continue
        if not isinstance(value, list):
            errors.append(f"{payload_field} must be a list when present")
            continue
        normalized = [str(item or "").strip() for item in value if str(item or "").strip()]
        if payload_field != "operator_notes" and not normalized:
            errors.append(f"{payload_field} cannot be empty when present")
    research_projection = payload.get("research_projection")
    if research_projection is not None:
        if not isinstance(research_projection, dict):
            errors.append("research_projection must be an object when present")
        else:
            source_plan = research_projection.get("source_plan")
            if source_plan is not None:
                if not isinstance(source_plan, dict):
                    errors.append("research_projection.source_plan must be an object when present")
                elif not str(source_plan.get("summary", "") or "").strip():
                    errors.append("research_projection.source_plan.summary is required")
            coverage_gap = research_projection.get("coverage_gap")
            if coverage_gap is not None:
                if not isinstance(coverage_gap, dict):
                    errors.append("research_projection.coverage_gap must be an object when present")
                else:
                    if str(coverage_gap.get("status", "") or "").strip().lower() not in {
                        "clear",
                        "watch",
                        "review_required",
                        "blocked",
                    }:
                        errors.append("research_projection.coverage_gap.status is invalid")
                    if not str(coverage_gap.get("summary", "") or "").strip():
                        errors.append("research_projection.coverage_gap.summary is required")
    return errors


@dataclass
class MissionRun:
    mission_id: str
    status: str = "success"
    item_count: int = 0
    trigger: str = "manual"
    error: str = ""
    started_at: str = ""
    finished_at: str = ""
    id: str = ""

    def __post_init__(self) -> None:
        if not self.started_at:
            self.started_at = _utcnow()
        if not self.finished_at:
            self.finished_at = self.started_at
        if not self.id:
            self.id = f"{self.mission_id}:{self.started_at}"
        self.status = (self.status or "success").strip().lower()
        self.trigger = (self.trigger or "manual").strip().lower()
        self.error = str(self.error or "").strip()
        try:
            self.item_count = max(0, int(self.item_count))
        except Exception:
            self.item_count = 0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "MissionRun":
        valid = {f.name for f in cls.__dataclass_fields__.values()}
        return cls(**{k: v for k, v in data.items() if k in valid})


@dataclass
class MissionIntent:
    demand_intent: str = ""
    key_questions: list[str] = field(default_factory=list)
    scope_entities: list[str] = field(default_factory=list)
    scope_topics: list[str] = field(default_factory=list)
    scope_regions: list[str] = field(default_factory=list)
    scope_window: str = ""
    freshness_expectation: str = ""
    freshness_max_age_hours: int = 0
    coverage_targets: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.demand_intent = str(self.demand_intent or "").strip()
        self.key_questions = _dedup_text(self.key_questions)
        self.scope_entities = _dedup_text(self.scope_entities)
        self.scope_topics = _dedup_text(self.scope_topics)
        self.scope_regions = _dedup_text(self.scope_regions)
        self.scope_window = str(self.scope_window or "").strip()
        self.freshness_expectation = str(self.freshness_expectation or "").strip()
        try:
            self.freshness_max_age_hours = max(0, int(self.freshness_max_age_hours))
        except Exception:
            self.freshness_max_age_hours = 0
        self.coverage_targets = _dedup_text(self.coverage_targets)

    def has_content(self) -> bool:
        return any(
            (
                self.demand_intent,
                self.key_questions,
                self.scope_entities,
                self.scope_topics,
                self.scope_regions,
                self.scope_window,
                self.freshness_expectation,
                self.freshness_max_age_hours > 0,
                self.coverage_targets,
            )
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "MissionIntent":
        valid = {f.name for f in cls.__dataclass_fields__.values()}
        return cls(**{k: v for k, v in data.items() if k in valid})


@dataclass
class TrendFeedInput:
    provider: str = ""
    label: str = ""
    location: str = ""
    topics: list[str] = field(default_factory=list)
    feed_url: str = ""
    snapshot_time: str = ""
    input_kind: str = "trend_feed"
    usage_mode: str = "watch_seed_only"
    notes: str = ""

    def __post_init__(self) -> None:
        self.provider = str(self.provider or "").strip().lower()
        self.label = str(self.label or "").strip()
        self.location = str(self.location or "").strip()
        self.topics = _dedup_text(self.topics)
        self.feed_url = str(self.feed_url or "").strip()
        self.snapshot_time = str(self.snapshot_time or "").strip()
        self.input_kind = "trend_feed"
        self.usage_mode = "watch_seed_only"
        self.notes = str(self.notes or "").strip()

    def has_content(self) -> bool:
        return any(
            (
                self.label,
                self.location,
                self.topics,
                self.feed_url,
                self.snapshot_time,
                self.notes,
            )
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "TrendFeedInput":
        valid = {f.name for f in cls.__dataclass_fields__.values()}
        return cls(**{k: v for k, v in data.items() if k in valid})


@dataclass
class MarketContextSidecar:
    sidecar_type: str = ""
    label: str = ""
    summary: str = ""
    symbols: list[str] = field(default_factory=list)
    signals: list[str] = field(default_factory=list)
    as_of: str = ""
    source_ref: str = ""
    input_kind: str = "market_context_sidecar"
    usage_mode: str = "watch_seed_only"
    admissible_usage: str = ""
    notes: str = ""

    def __post_init__(self) -> None:
        self.sidecar_type = str(self.sidecar_type or "").strip().lower()
        if self.sidecar_type not in _MARKET_CONTEXT_SIDECAR_USAGE_BY_TYPE:
            raise ValueError(f"Unsupported market context sidecar type: {self.sidecar_type}")
        self.label = str(self.label or "").strip()
        self.summary = str(self.summary or "").strip()
        self.symbols = _dedup_text(self.symbols)
        self.signals = _dedup_text(self.signals)
        self.as_of = str(self.as_of or "").strip()
        self.source_ref = str(self.source_ref or "").strip()
        self.input_kind = "market_context_sidecar"
        self.usage_mode = "watch_seed_only"
        self.admissible_usage = _MARKET_CONTEXT_SIDECAR_USAGE_BY_TYPE[self.sidecar_type]
        self.notes = str(self.notes or "").strip()

    def has_content(self) -> bool:
        return any(
            (
                self.label,
                self.summary,
                self.symbols,
                self.signals,
                self.as_of,
                self.source_ref,
                self.notes,
            )
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "MarketContextSidecar":
        valid = {f.name for f in cls.__dataclass_fields__.values()}
        return cls(**{k: v for k, v in data.items() if k in valid})


@dataclass
class WatchMission:
    name: str
    query: str
    mission_intent: MissionIntent = field(default_factory=MissionIntent)
    trend_inputs: list[TrendFeedInput] = field(default_factory=list)
    market_context_sidecars: list[MarketContextSidecar] = field(default_factory=list)
    platforms: list[str] = field(default_factory=list)
    sites: list[str] = field(default_factory=list)
    provider: str = "auto"
    schedule: str = "manual"
    min_confidence: float = 0.0
    top_n: int = 5
    alert_rules: list[dict[str, Any]] = field(default_factory=list)
    enabled: bool = True
    created_at: str = ""
    updated_at: str = ""
    last_run_at: str = ""
    last_run_count: int = 0
    last_run_status: str = ""
    last_run_error: str = ""
    runs: list[MissionRun] = field(default_factory=list)
    id: str = ""

    def __post_init__(self) -> None:
        self.name = str(self.name or "").strip()
        self.query = str(self.query or "").strip()
        if not self.name:
            raise ValueError("Watch mission name is required")
        if not self.query:
            raise ValueError("Watch mission query is required")
        if not self.id:
            self.id = generate_slug(self.name, max_length=48)
        now = _utcnow()
        if not self.created_at:
            self.created_at = now
        if not self.updated_at:
            self.updated_at = self.created_at
        if isinstance(self.mission_intent, MissionIntent):
            normalized_intent = self.mission_intent
        elif isinstance(self.mission_intent, dict):
            normalized_intent = MissionIntent.from_dict(self.mission_intent)
        else:
            normalized_intent = MissionIntent()
        self.mission_intent = normalized_intent
        normalized_trend_inputs: list[TrendFeedInput] = []
        seen_trend_inputs: set[tuple[str, str, str, tuple[str, ...], str, str]] = set()
        for trend_raw in self.trend_inputs:
            if isinstance(trend_raw, TrendFeedInput):
                trend_input = trend_raw
            elif isinstance(trend_raw, dict):
                try:
                    trend_input = TrendFeedInput.from_dict(trend_raw)
                except (TypeError, ValueError):
                    continue
            else:
                continue
            if not trend_input.has_content():
                continue
            trend_signature = (
                trend_input.provider.casefold(),
                trend_input.label.casefold(),
                trend_input.location.casefold(),
                tuple(topic.casefold() for topic in trend_input.topics),
                trend_input.feed_url.casefold(),
                trend_input.snapshot_time,
            )
            if trend_signature in seen_trend_inputs:
                continue
            seen_trend_inputs.add(trend_signature)
            normalized_trend_inputs.append(trend_input)
        self.trend_inputs = normalized_trend_inputs
        normalized_market_context_sidecars: list[MarketContextSidecar] = []
        seen_market_context_sidecars: set[tuple[str, str, str, tuple[str, ...], tuple[str, ...], str, str]] = set()
        for sidecar_raw in self.market_context_sidecars:
            if isinstance(sidecar_raw, MarketContextSidecar):
                sidecar = sidecar_raw
            elif isinstance(sidecar_raw, dict):
                try:
                    sidecar = MarketContextSidecar.from_dict(sidecar_raw)
                except (TypeError, ValueError):
                    continue
            else:
                continue
            if not sidecar.has_content():
                continue
            sidecar_signature = (
                sidecar.sidecar_type.casefold(),
                sidecar.label.casefold(),
                sidecar.summary.casefold(),
                tuple(symbol.casefold() for symbol in sidecar.symbols),
                tuple(signal.casefold() for signal in sidecar.signals),
                sidecar.as_of,
                sidecar.source_ref.casefold(),
            )
            if sidecar_signature in seen_market_context_sidecars:
                continue
            seen_market_context_sidecars.add(sidecar_signature)
            normalized_market_context_sidecars.append(sidecar)
        self.market_context_sidecars = normalized_market_context_sidecars
        self.platforms = _dedup_lower(self.platforms)
        self.sites = _dedup_lower(self.sites)
        provider_raw = str(self.provider or "auto").strip().lower()
        self.provider = provider_raw if provider_raw in {"auto", "jina", "multi"} else "auto"
        self.schedule = str(self.schedule or "manual").strip().lower() or "manual"
        try:
            self.min_confidence = max(0.0, min(1.0, float(self.min_confidence)))
        except Exception:
            self.min_confidence = 0.0
        try:
            self.top_n = max(1, int(self.top_n))
        except Exception:
            self.top_n = 5
        self.alert_rules = [
            rule for rule in self.alert_rules
            if isinstance(rule, dict)
        ]
        self.enabled = bool(self.enabled)
        normalized_runs: list[MissionRun] = []
        for run_raw in self.runs:
            if isinstance(run_raw, MissionRun):
                normalized_runs.append(run_raw)
            elif isinstance(run_raw, dict):
                try:
                    normalized_runs.append(MissionRun.from_dict(run_raw))
                except (TypeError, ValueError):
                    continue
        self.runs = normalized_runs[:10]
        try:
            self.last_run_count = max(0, int(self.last_run_count))
        except Exception:
            self.last_run_count = 0
        self.last_run_status = str(self.last_run_status or "").strip().lower()
        self.last_run_error = str(self.last_run_error or "").strip()

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["runs"] = [run.to_dict() for run in self.runs]
        payload["mission_intent"] = (
            self.mission_intent.to_dict()
            if self.mission_intent.has_content()
            else {}
        )
        payload["trend_inputs"] = [trend_input.to_dict() for trend_input in self.trend_inputs]
        payload["market_context_sidecars"] = [
            sidecar.to_dict()
            for sidecar in self.market_context_sidecars
        ]
        return payload

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "WatchMission":
        valid = {f.name for f in cls.__dataclass_fields__.values()}
        payload = {k: v for k, v in data.items() if k in valid}
        payload["trend_inputs"] = [
            TrendFeedInput.from_dict(row)
            for row in payload.get("trend_inputs", [])
            if isinstance(row, dict)
        ]
        payload["market_context_sidecars"] = [
            MarketContextSidecar.from_dict(row)
            for row in payload.get("market_context_sidecars", [])
            if isinstance(row, dict)
        ]
        payload["runs"] = [
            MissionRun.from_dict(run)
            for run in payload.get("runs", [])
            if isinstance(run, dict)
        ]
        return cls(**payload)


class WatchlistStore:
    """File-backed storage for recurring watch missions."""

    def __init__(self, path: str | None = None):
        self.path = Path(path or watchlist_path_from_env()).expanduser()
        self.version = 1
        self.missions: dict[str, WatchMission] = {}
        self._load()

    def _load(self) -> None:
        if not self.path.exists():
            self.missions = {}
            return
        try:
            raw = json.loads(self.path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            self.missions = {}
            return
        mission_rows: list[dict[str, Any]]
        if isinstance(raw, dict):
            self.version = int(raw.get("version", 1) or 1)
            source_rows = raw.get("missions", [])
            mission_rows = source_rows if isinstance(source_rows, list) else []
        elif isinstance(raw, list):
            mission_rows = raw
        else:
            self.missions = {}
            return

        loaded: dict[str, WatchMission] = {}
        for row in mission_rows:
            if not isinstance(row, dict):
                continue
            try:
                mission = WatchMission.from_dict(row)
            except (TypeError, ValueError):
                continue
            loaded[mission.id] = mission
        self.missions = loaded

    def save(self) -> None:
        payload = {
            "version": self.version,
            "missions": [mission.to_dict() for mission in self.list_missions(include_disabled=True)],
        }
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    def list_missions(self, *, include_disabled: bool = False) -> list[WatchMission]:
        missions = list(self.missions.values())
        if not include_disabled:
            missions = [mission for mission in missions if mission.enabled]
        return sorted(
            missions,
            key=lambda mission: (mission.updated_at, mission.created_at, mission.id),
            reverse=True,
        )

    def _next_id(self, base_id: str) -> str:
        candidate = (base_id or "watch").strip() or "watch"
        if candidate not in self.missions:
            return candidate
        suffix = 2
        while f"{candidate}-{suffix}" in self.missions:
            suffix += 1
        return f"{candidate}-{suffix}"

    def create_mission(
        self,
        *,
        name: str,
        query: str,
        mission_intent: dict[str, Any] | MissionIntent | None = None,
        trend_inputs: list[dict[str, Any] | TrendFeedInput] | None = None,
        market_context_sidecars: list[dict[str, Any] | MarketContextSidecar] | None = None,
        platforms: list[str] | None = None,
        sites: list[str] | None = None,
        provider: str = "auto",
        schedule: str = "manual",
        min_confidence: float = 0.0,
        top_n: int = 5,
        alert_rules: list[dict[str, Any]] | None = None,
        enabled: bool = True,
    ) -> WatchMission:
        normalized_mission_intent = (
            mission_intent
            if isinstance(mission_intent, MissionIntent)
            else MissionIntent.from_dict(mission_intent)
            if isinstance(mission_intent, dict)
            else MissionIntent()
        )
        normalized_trend_inputs: list[TrendFeedInput] = []
        for trend_raw in trend_inputs or []:
            if isinstance(trend_raw, TrendFeedInput):
                trend_input = trend_raw
            elif isinstance(trend_raw, dict):
                try:
                    trend_input = TrendFeedInput.from_dict(trend_raw)
                except (TypeError, ValueError):
                    continue
            else:
                continue
            if trend_input.has_content():
                normalized_trend_inputs.append(trend_input)
        normalized_market_context_sidecars: list[MarketContextSidecar] = []
        for sidecar_raw in market_context_sidecars or []:
            if isinstance(sidecar_raw, MarketContextSidecar):
                sidecar = sidecar_raw
            elif isinstance(sidecar_raw, dict):
                try:
                    sidecar = MarketContextSidecar.from_dict(sidecar_raw)
                except (TypeError, ValueError):
                    continue
            else:
                continue
            if sidecar.has_content():
                normalized_market_context_sidecars.append(sidecar)
        mission = WatchMission(
            name=name,
            query=query,
            mission_intent=normalized_mission_intent,
            trend_inputs=normalized_trend_inputs,
            market_context_sidecars=normalized_market_context_sidecars,
            platforms=list(platforms or []),
            sites=list(sites or []),
            provider=provider,
            schedule=schedule,
            min_confidence=min_confidence,
            top_n=top_n,
            alert_rules=list(alert_rules or []),
            enabled=enabled,
        )
        mission.id = self._next_id(mission.id)
        mission.updated_at = mission.created_at
        self.missions[mission.id] = mission
        self.save()
        return mission

    def update_mission(
        self,
        identifier: str,
        *,
        name: str | None = None,
        query: str | None = None,
        mission_intent: dict[str, Any] | MissionIntent | None = None,
        trend_inputs: list[dict[str, Any] | TrendFeedInput] | None = None,
        market_context_sidecars: list[dict[str, Any] | MarketContextSidecar] | None = None,
        platforms: list[str] | None = None,
        sites: list[str] | None = None,
        provider: str | None = None,
        schedule: str | None = None,
        min_confidence: float | None = None,
        top_n: int | None = None,
        alert_rules: list[dict[str, Any]] | None = None,
        enabled: bool | None = None,
    ) -> WatchMission | None:
        mission = self.get(identifier)
        if mission is None:
            return None
        normalized_mission_intent = (
            mission.mission_intent
            if mission_intent is None
            else mission_intent
            if isinstance(mission_intent, MissionIntent)
            else MissionIntent.from_dict(mission_intent)
            if isinstance(mission_intent, dict)
            else MissionIntent()
        )
        normalized_trend_inputs = list(mission.trend_inputs)
        if trend_inputs is not None:
            normalized_trend_inputs = []
            for trend_raw in trend_inputs:
                if isinstance(trend_raw, TrendFeedInput):
                    trend_input = trend_raw
                elif isinstance(trend_raw, dict):
                    try:
                        trend_input = TrendFeedInput.from_dict(trend_raw)
                    except (TypeError, ValueError):
                        continue
                else:
                    continue
                if trend_input.has_content():
                    normalized_trend_inputs.append(trend_input)
        normalized_market_context_sidecars = list(mission.market_context_sidecars)
        if market_context_sidecars is not None:
            normalized_market_context_sidecars = []
            for sidecar_raw in market_context_sidecars:
                if isinstance(sidecar_raw, MarketContextSidecar):
                    sidecar = sidecar_raw
                elif isinstance(sidecar_raw, dict):
                    try:
                        sidecar = MarketContextSidecar.from_dict(sidecar_raw)
                    except (TypeError, ValueError):
                        continue
                else:
                    continue
                if sidecar.has_content():
                    normalized_market_context_sidecars.append(sidecar)
        updated = WatchMission(
            id=mission.id,
            name=mission.name if name is None else name,
            query=mission.query if query is None else query,
            mission_intent=normalized_mission_intent,
            trend_inputs=normalized_trend_inputs,
            market_context_sidecars=normalized_market_context_sidecars,
            platforms=mission.platforms if platforms is None else list(platforms),
            sites=mission.sites if sites is None else list(sites),
            provider=mission.provider if provider is None else provider,
            schedule=mission.schedule if schedule is None else schedule,
            min_confidence=mission.min_confidence if min_confidence is None else min_confidence,
            top_n=mission.top_n if top_n is None else top_n,
            alert_rules=mission.alert_rules if alert_rules is None else list(alert_rules),
            enabled=mission.enabled if enabled is None else enabled,
            created_at=mission.created_at,
            updated_at=_utcnow(),
            last_run_at=mission.last_run_at,
            last_run_count=mission.last_run_count,
            last_run_status=mission.last_run_status,
            last_run_error=mission.last_run_error,
            runs=list(mission.runs),
        )
        self.missions[mission.id] = updated
        self.save()
        return updated

    def get(self, identifier: str) -> WatchMission | None:
        key = str(identifier or "").strip()
        if not key:
            return None
        if key in self.missions:
            return self.missions[key]
        normalized = key.casefold()
        for mission in self.missions.values():
            if mission.name.casefold() == normalized:
                return mission
        return None

    def disable(self, identifier: str) -> WatchMission | None:
        mission = self.get(identifier)
        if mission is None:
            return None
        mission.enabled = False
        mission.updated_at = _utcnow()
        self.save()
        return mission

    def enable(self, identifier: str) -> WatchMission | None:
        mission = self.get(identifier)
        if mission is None:
            return None
        mission.enabled = True
        mission.updated_at = _utcnow()
        self.save()
        return mission

    def delete(self, identifier: str) -> WatchMission | None:
        mission = self.get(identifier)
        if mission is None:
            return None
        removed = self.missions.pop(mission.id, None)
        if removed is None:
            return None
        self.save()
        return removed

    def replace_alert_rules(self, identifier: str, alert_rules: list[dict[str, Any]] | None) -> WatchMission | None:
        mission = self.get(identifier)
        if mission is None:
            return None
        mission.alert_rules = [
            dict(rule)
            for rule in list(alert_rules or [])
            if isinstance(rule, dict)
        ]
        mission.updated_at = _utcnow()
        self.save()
        return mission

    def record_run(self, identifier: str, run: MissionRun) -> WatchMission | None:
        mission = self.get(identifier)
        if mission is None:
            return None
        mission.last_run_at = run.finished_at or run.started_at
        mission.last_run_count = run.item_count
        mission.last_run_status = run.status
        mission.last_run_error = run.error
        mission.updated_at = mission.last_run_at or _utcnow()
        mission.runs.insert(0, run)
        mission.runs = mission.runs[:10]
        self.save()
        return mission


class WatchService:
    """Mission lifecycle service behind the stable DataPulseReader facade."""

    def __init__(self, owner: Any, *, watchlist: WatchlistStore, scheduler: Any):
        self.owner = owner
        self.watchlist = watchlist
        self.scheduler = scheduler

    def create_watch(
        self,
        *,
        name: str,
        query: str,
        mission_intent: dict[str, Any] | None = None,
        trend_inputs: list[dict[str, Any] | TrendFeedInput] | None = None,
        market_context_sidecars: list[dict[str, Any] | MarketContextSidecar] | None = None,
        platforms: list[str] | None = None,
        sites: list[str] | None = None,
        provider: str = "auto",
        schedule: str = "manual",
        min_confidence: float = 0.0,
        top_n: int = 5,
        alert_rules: list[dict[str, Any]] | None = None,
        enabled: bool = True,
    ) -> dict[str, Any]:
        mission = self.watchlist.create_mission(
            name=name,
            query=query,
            mission_intent=mission_intent,
            trend_inputs=trend_inputs,
            market_context_sidecars=market_context_sidecars,
            platforms=platforms,
            sites=sites,
            provider=provider,
            schedule=schedule,
            min_confidence=min_confidence,
            top_n=top_n,
            alert_rules=alert_rules,
            enabled=enabled,
        )
        return self.owner._serialize_watch_mission(mission)

    def update_watch(
        self,
        identifier: str,
        *,
        name: str | None = None,
        query: str | None = None,
        mission_intent: dict[str, Any] | None = None,
        trend_inputs: list[dict[str, Any] | TrendFeedInput] | None = None,
        market_context_sidecars: list[dict[str, Any] | MarketContextSidecar] | None = None,
        platforms: list[str] | None = None,
        sites: list[str] | None = None,
        provider: str | None = None,
        schedule: str | None = None,
        min_confidence: float | None = None,
        top_n: int | None = None,
        alert_rules: list[dict[str, Any]] | None = None,
        enabled: bool | None = None,
    ) -> dict[str, Any] | None:
        mission = self.watchlist.update_mission(
            identifier,
            name=name,
            query=query,
            mission_intent=mission_intent,
            trend_inputs=trend_inputs,
            market_context_sidecars=market_context_sidecars,
            platforms=platforms,
            sites=sites,
            provider=provider,
            schedule=schedule,
            min_confidence=min_confidence,
            top_n=top_n,
            alert_rules=alert_rules,
            enabled=enabled,
        )
        if mission is None:
            return None
        return self.show_watch(mission.id)

    def set_watch_alert_rules(
        self,
        identifier: str,
        *,
        alert_rules: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any] | None:
        mission = self.watchlist.replace_alert_rules(identifier, alert_rules)
        if mission is None:
            return None
        return self.show_watch(mission.id)

    def list_watches(self, *, include_disabled: bool = False) -> list[dict[str, Any]]:
        return [
            self.owner._serialize_watch_mission(mission)
            for mission in self.watchlist.list_missions(include_disabled=include_disabled)
        ]

    def list_watch_results(
        self,
        identifier: str,
        *,
        limit: int = 10,
        min_confidence: float = 0.0,
    ) -> list[dict[str, Any]] | None:
        mission = self.watchlist.get(identifier)
        if mission is None:
            return None
        items = self.owner._watch_result_items(mission, min_confidence=min_confidence)
        return [self.owner._serialize_watch_result(item) for item in items[: max(0, int(limit))]]

    def show_watch(self, identifier: str) -> dict[str, Any] | None:
        mission = self.watchlist.get(identifier)
        if mission is None:
            return None
        payload = self.owner._serialize_watch_mission(mission)
        last_failure = self.owner._latest_failed_run(mission)
        payload["last_failure"] = last_failure.to_dict() if last_failure is not None else None
        payload["retry_advice"] = self.owner._watch_retry_advice(mission, last_failure)
        stored_result_items = self.owner._watch_result_items(
            mission,
            min_confidence=0.0,
            apply_query_filter=False,
        )
        result_items = self.owner._filter_watch_results_by_query(mission, stored_result_items)
        filtered_result_count = max(0, len(stored_result_items) - len(result_items))
        payload["recent_results"] = [self.owner._serialize_watch_result(item) for item in result_items[:8]]
        payload["result_stats"] = {
            "stored_result_count": len(stored_result_items),
            "visible_result_count": len(result_items),
            "filtered_result_count": filtered_result_count,
            "returned_result_count": min(8, len(result_items)),
            "latest_result_at": (
                result_items[0].fetched_at
                if result_items
                else (stored_result_items[0].fetched_at if stored_result_items else "")
            ),
        }
        payload["result_filters"] = self.owner._build_watch_result_filters(payload["recent_results"])
        recent_alerts = self.owner.list_alerts(limit=6, mission_id=mission.id)
        payload["recent_alerts"] = recent_alerts
        payload["delivery_stats"] = {
            "recent_alert_count": len(recent_alerts),
            "recent_error_count": sum(
                1
                for event in recent_alerts
                if isinstance(event.get("extra"), dict)
                and isinstance(event["extra"].get("delivery_errors"), dict)
                and event["extra"]["delivery_errors"]
            ),
            "last_alert_at": recent_alerts[0].get("created_at", "") if recent_alerts else "",
        }
        payload["timeline_strip"] = self.owner._build_watch_timeline_strip(mission, payload["recent_results"], recent_alerts)
        return payload

    def disable_watch(self, identifier: str) -> dict[str, Any] | None:
        mission = self.watchlist.disable(identifier)
        return mission.to_dict() if mission is not None else None

    def enable_watch(self, identifier: str) -> dict[str, Any] | None:
        mission = self.watchlist.enable(identifier)
        return mission.to_dict() if mission is not None else None

    def delete_watch(self, identifier: str) -> dict[str, Any] | None:
        mission = self.watchlist.delete(identifier)
        return mission.to_dict() if mission is not None else None

    async def run_watch(self, identifier: str, *, trigger: str = "manual") -> dict[str, Any]:
        mission = self.watchlist.get(identifier)
        if mission is None:
            raise ValueError(f"Watch mission not found: {identifier}")
        if not mission.enabled:
            raise ValueError(f"Watch mission is disabled: {identifier}")

        started_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
        effective_provider = mission.provider if mission.provider in {"auto", "jina", "multi"} else "auto"
        try:
            if mission.platforms:
                batches = await asyncio.gather(
                    *[
                        self.owner.search(
                            mission.query,
                            sites=mission.sites or None,
                            platform=platform,
                            limit=mission.top_n,
                            min_confidence=mission.min_confidence,
                            provider=effective_provider,
                        )
                        for platform in mission.platforms
                    ]
                )
                merged: dict[str, Any] = {}
                platform_hits: dict[str, set[str]] = {}
                fp_platform_hits: dict[str, set[str]] = {}
                item_fp: dict[str, str] = {}
                for platform, batch in zip(mission.platforms, batches):
                    for item in batch:
                        merged.setdefault(item.id, item)
                        platform_hits.setdefault(item.id, set()).add(platform)
                        fp = content_fingerprint(getattr(item, "content", "") or "")
                        item_fp[item.id] = fp
                        fp_platform_hits.setdefault(fp, set()).add(platform)
                for item_id, item in merged.items():
                    platforms_for_item = platform_hits.get(item_id, set())
                    fp_platforms = fp_platform_hits.get(item_fp.get(item_id, ""), set())
                    corroborated = max(len(platforms_for_item), len(fp_platforms))
                    if corroborated >= 2 and isinstance(getattr(item, "extra", None), dict):
                        item.extra["corroboration_platforms"] = sorted(fp_platforms or platforms_for_item)
                        item.extra["corroboration_count"] = corroborated
                items = sorted(
                    merged.values(),
                    key=lambda item: (
                        int((item.extra or {}).get("corroboration_count", 1)) if isinstance(getattr(item, "extra", None), dict) else 1,
                        item.score,
                        item.confidence,
                        item.fetched_at,
                    ),
                    reverse=True,
                )[: mission.top_n]
            else:
                items = await self.owner.search(
                    mission.query,
                    sites=mission.sites or None,
                    limit=mission.top_n,
                    min_confidence=mission.min_confidence,
                    provider=effective_provider,
                )

            items = self.owner._filter_watch_results_by_query(mission, items)
            self.owner._tag_items_with_watch(mission, items)
            alert_events = self.owner._evaluate_and_dispatch_watch_alerts(mission, items)
            run = MissionRun(
                mission_id=mission.id,
                status="success",
                item_count=len(items),
                trigger=trigger,
                started_at=started_at,
                finished_at=datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
            )
            updated = self.watchlist.record_run(mission.id, run) or mission
            return {
                "mission": self.owner._serialize_watch_mission(updated),
                "run": run.to_dict(),
                "items": [self.owner._serialize_watch_result(item) for item in items],
                "alert_events": alert_events,
            }
        except Exception as exc:
            run = MissionRun(
                mission_id=mission.id,
                status="error",
                item_count=0,
                trigger=trigger,
                error=str(exc),
                started_at=started_at,
                finished_at=datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
            )
            self.watchlist.record_run(mission.id, run)
            raise

    async def run_due_watches(
        self,
        limit: int | None = None,
        *,
        retry_attempts: int = 1,
        retry_base_delay: float = 1.0,
        retry_max_delay: float = 30.0,
        retry_backoff_factor: float = 2.0,
    ) -> dict[str, Any]:
        scheduled_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
        due_missions = self.scheduler.due_missions(limit=limit)
        results: list[dict[str, Any]] = []

        for mission in due_missions:
            attempt = 1
            delay = max(0.1, float(retry_base_delay))
            while True:
                try:
                    # Keep scheduled execution routed through the Reader facade so
                    # surface-level overrides and verification hooks observe the
                    # same entrypoint as direct watch runs.
                    payload = await self.owner.run_watch(mission.id, trigger="scheduled")
                    run_payload = payload.get("run", {})
                    alert_events = payload.get("alert_events", [])
                    results.append(
                        {
                            "mission_id": mission.id,
                            "mission_name": mission.name,
                            "status": run_payload.get("status", "success"),
                            "item_count": run_payload.get("item_count", 0),
                            "attempts": attempt,
                            "retry_count": max(0, attempt - 1),
                            "alert_count": len(alert_events) if isinstance(alert_events, list) else 0,
                        }
                    )
                    break
                except Exception as exc:
                    if attempt >= max(1, int(retry_attempts)):
                        results.append(
                            {
                                "mission_id": mission.id,
                                "mission_name": mission.name,
                                "status": "error",
                                "item_count": 0,
                                "attempts": attempt,
                                "retry_count": max(0, attempt - 1),
                                "error": str(exc),
                            }
                        )
                        break
                    await asyncio.sleep(min(delay, retry_max_delay))
                    delay = min(delay * retry_backoff_factor, retry_max_delay)
                    attempt += 1

        return {
            "scheduled_at": scheduled_at,
            "due_count": len(due_missions),
            "run_count": len(results),
            "results": results,
        }
