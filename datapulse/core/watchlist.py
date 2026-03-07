"""Persistent watch/mission definitions for recurring DataPulse workflows."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .utils import generate_slug, watchlist_path_from_env


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
class WatchMission:
    name: str
    query: str
    platforms: list[str] = field(default_factory=list)
    sites: list[str] = field(default_factory=list)
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
        self.platforms = _dedup_lower(self.platforms)
        self.sites = _dedup_lower(self.sites)
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
        for raw in self.runs:
            if isinstance(raw, MissionRun):
                normalized_runs.append(raw)
            elif isinstance(raw, dict):
                try:
                    normalized_runs.append(MissionRun.from_dict(raw))
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
        return payload

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "WatchMission":
        valid = {f.name for f in cls.__dataclass_fields__.values()}
        payload = {k: v for k, v in data.items() if k in valid}
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
        platforms: list[str] | None = None,
        sites: list[str] | None = None,
        schedule: str = "manual",
        min_confidence: float = 0.0,
        top_n: int = 5,
        alert_rules: list[dict[str, Any]] | None = None,
        enabled: bool = True,
    ) -> WatchMission:
        mission = WatchMission(
            name=name,
            query=query,
            platforms=list(platforms or []),
            sites=list(sites or []),
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
