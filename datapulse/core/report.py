"""Structured report-production objects and repository-backed persistence."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, TypeAlias, TypeVar

from .utils import generate_slug, reports_path_from_env


def _utcnow() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _normalize_optional_string(value: Any) -> str:
    text = str(value or "").strip()
    return text


def _normalize_status(value: Any, default: str = "draft") -> str:
    normalized = str(value or default).strip().lower()
    return normalized or default


def _normalize_string_list(values: Any) -> list[str]:
    if values is None:
        return []
    if isinstance(values, str):
        values = [values]
    if not isinstance(values, list):
        return []
    normalized: list[str] = []
    seen: set[str] = set()
    for raw in values:
        value = str(raw or "").strip()
        if not value or value in seen:
            continue
        seen.add(value)
        normalized.append(value)
    return normalized


def _normalize_id_sequence(values: Any) -> list[str]:
    normalized = _normalize_string_list(values)
    return [value for value in normalized if value]


def _unique_id(base_id: str, existing: set[str], *, prefix: str) -> str:
    candidate = (base_id or prefix).strip() or prefix
    if candidate not in existing:
        return candidate
    suffix = 2
    while f"{candidate}-{suffix}" in existing:
        suffix += 1
    return f"{candidate}-{suffix}"


def _coerce_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except Exception:
        return default


def _coerce_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except Exception:
        return default


_DELIVERY_SUBJECT_KINDS = ("profile", "watch_mission", "story", "report")
_DELIVERY_OUTPUT_KINDS = (
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
)
_DELIVERY_MODES = ("pull", "push")
_DELIVERY_SUBSCRIPTION_STATUSES = ("active", "paused", "disabled")
_DELIVERY_DISPATCH_STATUSES = ("pending", "delivered", "failed", "skipped", "missing_route")


_DEFAULT_EXPORT_PROFILES: tuple[dict[str, Any], ...] = (
    {
        "name": "brief",
        "output_format": "json",
        "include_sections": True,
        "include_claim_cards": False,
        "include_bundles": False,
        "include_metadata": True,
        "profile_version": "1.0",
    },
    {
        "name": "full",
        "output_format": "json",
        "include_sections": True,
        "include_claim_cards": True,
        "include_bundles": True,
        "include_metadata": True,
        "profile_version": "1.0",
    },
    {
        "name": "sources",
        "output_format": "json",
        "include_sections": False,
        "include_claim_cards": True,
        "include_bundles": True,
        "include_metadata": True,
        "profile_version": "1.0",
    },
    {
        "name": "watch-pack",
        "output_format": "json",
        "include_sections": False,
        "include_claim_cards": False,
        "include_bundles": False,
        "include_metadata": False,
        "profile_version": "1.0",
    },
)


@dataclass
class ReportBrief:
    title: str
    audience: str = ""
    objective: str = ""
    intent: str = ""
    tags: list[str] = field(default_factory=list)
    status: str = "draft"
    id: str = ""
    created_at: str = ""
    updated_at: str = ""
    governance: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.title = _normalize_optional_string(self.title)
        if not self.title:
            raise ValueError("ReportBrief title is required")
        self.audience = _normalize_optional_string(self.audience)
        self.objective = _normalize_optional_string(self.objective)
        self.intent = _normalize_optional_string(self.intent)
        self.tags = _normalize_string_list(self.tags)
        self.status = _normalize_status(self.status, default="draft")
        self.id = _normalize_optional_string(self.id) or generate_slug(self.title, max_length=48)
        now = _utcnow()
        if not self.created_at:
            self.created_at = now
        self.updated_at = _normalize_optional_string(self.updated_at) or self.created_at
        self.governance = dict(self.governance or {})

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ReportBrief":
        valid = {f.name for f in cls.__dataclass_fields__.values()}
        return cls(**{k: v for k, v in data.items() if k in valid})


@dataclass
class ClaimCard:
    statement: str
    brief_id: str = ""
    rationale: str = ""
    confidence: float = 0.0
    status: str = "draft"
    citation_bundle_ids: list[str] = field(default_factory=list)
    source_item_ids: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    id: str = ""
    created_at: str = ""
    updated_at: str = ""
    governance: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.statement = _normalize_optional_string(self.statement)
        if not self.statement:
            raise ValueError("ClaimCard statement is required")
        self.brief_id = _normalize_optional_string(self.brief_id)
        self.rationale = _normalize_optional_string(self.rationale)
        self.confidence = round(max(0.0, min(1.0, _coerce_float(self.confidence, default=0.0))), 4)
        self.status = _normalize_status(self.status, default="draft")
        self.citation_bundle_ids = _normalize_id_sequence(self.citation_bundle_ids)
        self.source_item_ids = _normalize_id_sequence(self.source_item_ids)
        self.tags = _normalize_string_list(self.tags)
        self.id = _normalize_optional_string(self.id) or generate_slug(self.statement, max_length=48)
        now = _utcnow()
        if not self.created_at:
            self.created_at = now
        self.updated_at = _normalize_optional_string(self.updated_at) or self.created_at
        self.governance = dict(self.governance or {})

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ClaimCard":
        valid = {f.name for f in cls.__dataclass_fields__.values()}
        return cls(**{k: v for k, v in data.items() if k in valid})


@dataclass
class ReportSection:
    title: str
    report_id: str
    position: int = 0
    claim_card_ids: list[str] = field(default_factory=list)
    summary: str = ""
    status: str = "draft"
    id: str = ""
    created_at: str = ""
    updated_at: str = ""
    governance: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.title = _normalize_optional_string(self.title)
        if not self.title:
            raise ValueError("ReportSection title is required")
        self.report_id = _normalize_optional_string(self.report_id)
        self.position = _coerce_int(self.position, default=0)
        self.claim_card_ids = _normalize_id_sequence(self.claim_card_ids)
        self.summary = _normalize_optional_string(self.summary)
        self.status = _normalize_status(self.status, default="draft")
        self.id = _normalize_optional_string(self.id) or generate_slug(f"{self.report_id}-{self.title}", max_length=48) if self.report_id else generate_slug(self.title, max_length=48)
        now = _utcnow()
        if not self.created_at:
            self.created_at = now
        self.updated_at = _normalize_optional_string(self.updated_at) or self.created_at
        self.governance = dict(self.governance or {})

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ReportSection":
        valid = {f.name for f in cls.__dataclass_fields__.values()}
        return cls(**{k: v for k, v in data.items() if k in valid})


@dataclass
class CitationBundle:
    label: str = ""
    claim_card_id: str = ""
    source_item_ids: list[str] = field(default_factory=list)
    source_urls: list[str] = field(default_factory=list)
    note: str = ""
    id: str = ""
    created_at: str = ""
    updated_at: str = ""
    governance: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.label = _normalize_optional_string(self.label)
        self.claim_card_id = _normalize_optional_string(self.claim_card_id)
        self.source_item_ids = _normalize_id_sequence(self.source_item_ids)
        self.source_urls = _normalize_string_list(self.source_urls)
        self.note = _normalize_optional_string(self.note)
        self.id = _normalize_optional_string(self.id) or generate_slug(self.label or ("bundle-" + "-".join(self.source_item_ids[:3])) if self.source_item_ids else "citation-bundle", max_length=48)
        now = _utcnow()
        if not self.created_at:
            self.created_at = now
        self.updated_at = _normalize_optional_string(self.updated_at) or self.created_at
        self.governance = dict(self.governance or {})

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "CitationBundle":
        valid = {f.name for f in cls.__dataclass_fields__.values()}
        return cls(**{k: v for k, v in data.items() if k in valid})


@dataclass
class Report:
    title: str
    brief_id: str = ""
    audience: str = ""
    section_ids: list[str] = field(default_factory=list)
    claim_card_ids: list[str] = field(default_factory=list)
    citation_bundle_ids: list[str] = field(default_factory=list)
    export_profile_ids: list[str] = field(default_factory=list)
    status: str = "draft"
    summary: str = ""
    tags: list[str] = field(default_factory=list)
    id: str = ""
    created_at: str = ""
    updated_at: str = ""
    governance: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.title = _normalize_optional_string(self.title)
        if not self.title:
            raise ValueError("Report title is required")
        self.brief_id = _normalize_optional_string(self.brief_id)
        self.audience = _normalize_optional_string(self.audience)
        self.section_ids = _normalize_id_sequence(self.section_ids)
        self.claim_card_ids = _normalize_id_sequence(self.claim_card_ids)
        self.citation_bundle_ids = _normalize_id_sequence(self.citation_bundle_ids)
        self.export_profile_ids = _normalize_id_sequence(self.export_profile_ids)
        self.status = _normalize_status(self.status, default="draft")
        self.summary = _normalize_optional_string(self.summary)
        self.tags = _normalize_string_list(self.tags)
        self.id = _normalize_optional_string(self.id) or generate_slug(self.title, max_length=48)
        now = _utcnow()
        if not self.created_at:
            self.created_at = now
        self.updated_at = _normalize_optional_string(self.updated_at) or self.created_at
        self.governance = dict(self.governance or {})

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Report":
        valid = {f.name for f in cls.__dataclass_fields__.values()}
        return cls(**{k: v for k, v in data.items() if k in valid})


@dataclass
class ExportProfile:
    name: str
    report_id: str
    output_format: str = "json"
    include_sections: bool = True
    include_claim_cards: bool = True
    include_bundles: bool = True
    include_metadata: bool = True
    profile_version: str = "1.0"
    id: str = ""
    created_at: str = ""
    updated_at: str = ""
    governance: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.name = _normalize_optional_string(self.name)
        if not self.name:
            raise ValueError("ExportProfile name is required")
        self.report_id = _normalize_optional_string(self.report_id)
        self.output_format = _normalize_status(self.output_format, default="json")
        self.include_sections = bool(self.include_sections)
        self.include_claim_cards = bool(self.include_claim_cards)
        self.include_bundles = bool(self.include_bundles)
        self.include_metadata = bool(self.include_metadata)
        self.profile_version = _normalize_optional_string(self.profile_version) or "1.0"
        self.id = _normalize_optional_string(self.id) or generate_slug(f"{self.report_id}-{self.name}", max_length=48) if self.report_id else generate_slug(self.name, max_length=48)
        now = _utcnow()
        if not self.created_at:
            self.created_at = now
        self.updated_at = _normalize_optional_string(self.updated_at) or self.created_at
        self.governance = dict(self.governance or {})

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ExportProfile":
        valid = {f.name for f in cls.__dataclass_fields__.values()}
        return cls(**{k: v for k, v in data.items() if k in valid})


@dataclass
class DeliverySubscription:
    subject_kind: str
    subject_ref: str
    output_kind: str
    delivery_mode: str = "pull"
    route_names: list[str] = field(default_factory=list)
    cursor_or_since: str = ""
    status: str = "active"
    id: str = ""
    created_at: str = ""
    updated_at: str = ""
    governance: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.subject_kind = _normalize_optional_string(self.subject_kind).strip().lower()
        if self.subject_kind not in _DELIVERY_SUBJECT_KINDS:
            raise ValueError(f"Unsupported subject_kind: {self.subject_kind}")
        self.subject_ref = _normalize_optional_string(self.subject_ref)
        if not self.subject_ref:
            raise ValueError("subject_ref is required")
        self.output_kind = _normalize_optional_string(self.output_kind).strip().lower()
        if not self.output_kind:
            raise ValueError("output_kind is required")
        if self.output_kind not in _DELIVERY_OUTPUT_KINDS:
            raise ValueError(f"Unsupported output_kind: {self.output_kind}")
        self.delivery_mode = _normalize_optional_string(self.delivery_mode).strip().lower() or "pull"
        if self.delivery_mode not in _DELIVERY_MODES:
            raise ValueError(f"Unsupported delivery_mode: {self.delivery_mode}")
        route_names: list[str] = []
        seen_route_names: set[str] = set()
        for raw in _normalize_string_list(self.route_names):
            name = str(raw or "").strip().lower()
            if not name or name in seen_route_names:
                continue
            seen_route_names.add(name)
            route_names.append(name)
        self.route_names = route_names
        self.cursor_or_since = _normalize_optional_string(self.cursor_or_since)
        self.status = _normalize_optional_string(self.status) or "active"
        if self.status not in _DELIVERY_SUBSCRIPTION_STATUSES:
            self.status = "active"
        self.id = _normalize_optional_string(self.id) or generate_slug(f"{self.subject_kind}-{self.subject_ref}-{self.output_kind}", max_length=64)
        now = _utcnow()
        if not self.created_at:
            self.created_at = now
        self.updated_at = _normalize_optional_string(self.updated_at) or self.created_at
        self.governance = dict(self.governance or {})

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "DeliverySubscription":
        valid = {f.name for f in cls.__dataclass_fields__.values()}
        return cls(**{k: v for k, v in data.items() if k in valid})


@dataclass
class DeliveryDispatchRecord:
    subscription_id: str
    subject_kind: str
    subject_ref: str
    output_kind: str
    route_name: str = ""
    route_label: str = ""
    route_channel: str = ""
    package_id: str = ""
    package_signature: str = ""
    package_profile_id: str = ""
    status: str = "pending"
    attempts: int = 0
    error: str = ""
    id: str = ""
    created_at: str = ""
    updated_at: str = ""
    governance: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.subscription_id = _normalize_optional_string(self.subscription_id)
        if not self.subscription_id:
            raise ValueError("subscription_id is required")
        self.subject_kind = _normalize_optional_string(self.subject_kind).strip().lower()
        if not self.subject_kind:
            raise ValueError("subject_kind is required")
        self.subject_ref = _normalize_optional_string(self.subject_ref)
        if not self.subject_ref:
            raise ValueError("subject_ref is required")
        self.output_kind = _normalize_optional_string(self.output_kind).strip().lower()
        if not self.output_kind:
            raise ValueError("output_kind is required")
        self.status = _normalize_optional_string(self.status).strip().lower() or "pending"
        if self.status not in _DELIVERY_DISPATCH_STATUSES:
            self.status = "pending"
        self.route_name = _normalize_optional_string(self.route_name)
        self.route_label = _normalize_optional_string(self.route_label)
        self.route_channel = _normalize_optional_string(self.route_channel).strip().lower()
        self.package_id = _normalize_optional_string(self.package_id)
        self.package_signature = _normalize_optional_string(self.package_signature)
        self.package_profile_id = _normalize_optional_string(self.package_profile_id)
        self.attempts = _coerce_int(self.attempts, default=0)
        self.error = _normalize_optional_string(self.error)
        self.id = _normalize_optional_string(self.id) or generate_slug(
            f"{self.subscription_id}-{self.route_name or 'route'}-{self.output_kind}",
            max_length=64,
        )
        now = _utcnow()
        if not self.created_at:
            self.created_at = now
        self.updated_at = _normalize_optional_string(self.updated_at) or self.created_at
        self.governance = dict(self.governance or {})

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "DeliveryDispatchRecord":
        valid = {f.name for f in cls.__dataclass_fields__.values()}
        return cls(**{k: v for k, v in data.items() if k in valid})


ReportRecord: TypeAlias = (
    ReportBrief
    | ClaimCard
    | ReportSection
    | CitationBundle
    | Report
    | ExportProfile
    | DeliverySubscription
    | DeliveryDispatchRecord
)
ReportRecordT = TypeVar(
    "ReportRecordT",
    ReportBrief,
    ClaimCard,
    ReportSection,
    CitationBundle,
    Report,
    ExportProfile,
    DeliverySubscription,
    DeliveryDispatchRecord,
)


class ReportStore:
    """File-backed storage for report-production objects."""

    def __init__(self, path: str | None = None):
        self.path = Path(path or reports_path_from_env()).expanduser()
        self.version = 1
        self.report_briefs: dict[str, ReportBrief] = {}
        self.claim_cards: dict[str, ClaimCard] = {}
        self.report_sections: dict[str, ReportSection] = {}
        self.citation_bundles: dict[str, CitationBundle] = {}
        self.reports: dict[str, Report] = {}
        self.export_profiles: dict[str, ExportProfile] = {}
        self.delivery_subscriptions: dict[str, DeliverySubscription] = {}
        self.delivery_dispatch_records: dict[str, DeliveryDispatchRecord] = {}
        self._load()

    def _load(self) -> None:
        if not self.path.exists():
            return
        try:
            raw = json.loads(self.path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return

        if isinstance(raw, dict):
            self.version = int(raw.get("version", self.version) or self.version)
            self._load_collection(raw.get("report_briefs"), ReportBrief.from_dict, self.report_briefs)
            self._load_collection(raw.get("claim_cards"), ClaimCard.from_dict, self.claim_cards)
            self._load_collection(raw.get("report_sections"), ReportSection.from_dict, self.report_sections)
            self._load_collection(raw.get("citation_bundles"), CitationBundle.from_dict, self.citation_bundles)
            self._load_collection(raw.get("reports"), Report.from_dict, self.reports)
            self._load_collection(raw.get("export_profiles"), ExportProfile.from_dict, self.export_profiles)
            self._load_collection(raw.get("delivery_subscriptions"), DeliverySubscription.from_dict, self.delivery_subscriptions)
            self._load_collection(
                raw.get("delivery_dispatch_records"),
                DeliveryDispatchRecord.from_dict,
                self.delivery_dispatch_records,
            )
        elif isinstance(raw, list):
            self._load_collection(raw, Report.from_dict, self.reports)

    def _load_collection(
        self,
        payload: Any,
        factory: Callable[[dict[str, Any]], ReportRecordT],
        target: dict[str, ReportRecordT],
    ) -> None:
        rows = payload if isinstance(payload, list) else []
        for item in rows:
            if not isinstance(item, dict):
                continue
            try:
                model_obj = factory(item)
            except (TypeError, ValueError):
                continue
            target[model_obj.id] = model_obj

    def _persistable_payload(self) -> dict[str, Any]:
        return {
            "version": self.version,
            "report_briefs": [brief.to_dict() for brief in self._list_records(self.report_briefs)],
            "claim_cards": [claim.to_dict() for claim in self._list_records(self.claim_cards)],
            "report_sections": [section.to_dict() for section in self._list_records(self.report_sections)],
            "citation_bundles": [bundle.to_dict() for bundle in self._list_records(self.citation_bundles)],
            "reports": [report.to_dict() for report in self._list_records(self.reports)],
            "export_profiles": [profile.to_dict() for profile in self._list_records(self.export_profiles)],
            "delivery_subscriptions": [
                subscription.to_dict() for subscription in self._list_records(self.delivery_subscriptions)
            ],
            "delivery_dispatch_records": [
                dispatch_record.to_dict()
                for dispatch_record in self._list_records(self.delivery_dispatch_records)
            ],
        }

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(self._persistable_payload(), ensure_ascii=False, indent=2), encoding="utf-8")

    def _touch(self, obj: ReportRecord) -> None:
        obj.updated_at = _utcnow()

    @staticmethod
    def _filter_status(values: list[ReportRecordT], status: str | None) -> list[ReportRecordT]:
        if not status:
            return values
        normalized = {s.strip().lower() for s in _normalize_string_list([status])}
        return [item for item in values if getattr(item, "status", "").strip().lower() in normalized]

    @staticmethod
    def _list_records(
        records: dict[str, ReportRecordT],
        *,
        limit: int = 20,
        status: str | None = None,
    ) -> list[ReportRecordT]:
        rows = list(records.values())
        if status is not None:
            allowed = {s.strip().lower() for s in _normalize_string_list([status])}
            rows = [row for row in rows if str(getattr(row, "status", "")).strip().lower() in allowed]
        rows.sort(key=lambda item: (str(item.updated_at), str(item.id)), reverse=True)
        return rows[: max(0, int(limit))]

    @staticmethod
    def _lookup(records: dict[str, ReportRecordT], identifier: str) -> ReportRecordT | None:
        key = _normalize_optional_string(identifier)
        if not key:
            return None
        if key in records:
            return records[key]
        lowered = key.casefold()
        for row in records.values():
            if str(getattr(row, "title", "")).strip().casefold() == lowered:
                return row
        return None

    @staticmethod
    def _to_status(value: str | None, default: str = "") -> str:
        return _normalize_status(value, default=default) if value is not None else default

    @staticmethod
    def _normalize_ids(values: list[str] | None) -> list[str]:
        return _normalize_id_sequence(values)

    def _create(
        self,
        payload: ReportRecordT | dict[str, Any],
        factory: Callable[[dict[str, Any]], ReportRecordT],
        model_type: type[ReportRecordT],
        container: dict[str, ReportRecordT],
        *,
        id_prefix: str,
    ) -> ReportRecordT:
        if isinstance(payload, model_type):
            candidate = payload
        else:
            if not isinstance(payload, dict):
                raise TypeError(f"Unsupported payload type for {model_type.__name__}: {type(payload)!r}")
            candidate = factory(payload)
        candidate.id = _unique_id(candidate.id, set(container), prefix=id_prefix)
        if not candidate.created_at:
            candidate.created_at = _utcnow()
        candidate.updated_at = candidate.created_at
        container[candidate.id] = candidate
        self.save()
        return candidate

    def _update_timestamp(self) -> None:
        self.version += 1

    def _update_generic(
        self,
        identifier: str,
        container: dict[str, ReportRecordT],
        *,
        updates: dict[str, Any],
    ) -> ReportRecordT | None:
        current = self._lookup(container, identifier)
        if current is None:
            return None
        for field_name, field_value in updates.items():
            if field_value is None:
                continue
            if isinstance(field_value, list):
                setattr(current, field_name, self._normalize_ids(field_value))
            elif isinstance(field_value, bool):
                setattr(current, field_name, bool(field_value))
            elif hasattr(current, field_name) and isinstance(getattr(current, field_name), float):
                setattr(current, field_name, _coerce_float(field_value, default=getattr(current, field_name)))
            elif isinstance(field_value, int) and hasattr(current, field_name) and isinstance(getattr(current, field_name), int):
                setattr(current, field_name, _coerce_int(field_value, default=getattr(current, field_name)))
            else:
                setattr(current, field_name, _normalize_optional_string(field_value))
        self._touch(current)
        self.save()
        return current

    # ReportBrief CRUD
    def create_report_brief(self, payload: ReportBrief | dict[str, Any]) -> ReportBrief:
        return self._create(payload, ReportBrief.from_dict, ReportBrief, self.report_briefs, id_prefix="report-brief")

    def list_report_briefs(self, *, limit: int = 20, status: str | None = None) -> list[ReportBrief]:
        return self._list_records(self.report_briefs, limit=limit, status=status)

    def get_report_brief(self, identifier: str) -> ReportBrief | None:
        return self._lookup(self.report_briefs, identifier)

    def update_report_brief(self, identifier: str, **payload: Any) -> ReportBrief | None:
        updates = {
            "title": payload.get("title"),
            "audience": payload.get("audience"),
            "objective": payload.get("objective"),
            "intent": payload.get("intent"),
            "status": payload.get("status"),
            "tags": payload.get("tags"),
        }
        return self._update_generic(identifier, self.report_briefs, updates=updates)

    # ClaimCard CRUD
    def create_claim_card(self, payload: ClaimCard | dict[str, Any]) -> ClaimCard:
        return self._create(payload, ClaimCard.from_dict, ClaimCard, self.claim_cards, id_prefix="claim-card")

    def list_claim_cards(self, *, limit: int = 20, status: str | None = None) -> list[ClaimCard]:
        return self._list_records(self.claim_cards, limit=limit, status=status)

    def get_claim_card(self, identifier: str) -> ClaimCard | None:
        return self._lookup(self.claim_cards, identifier)

    def update_claim_card(self, identifier: str, **payload: Any) -> ClaimCard | None:
        updates = {
            "statement": payload.get("statement"),
            "rationale": payload.get("rationale"),
            "status": payload.get("status"),
            "citation_bundle_ids": payload.get("citation_bundle_ids"),
            "source_item_ids": payload.get("source_item_ids"),
            "tags": payload.get("tags"),
            "brief_id": payload.get("brief_id"),
        }
        claim = self._update_generic(identifier, self.claim_cards, updates=updates)
        if claim is None:
            return None
        if "confidence" in payload:
            claim.confidence = round(max(0.0, min(1.0, _coerce_float(payload.get("confidence"), default=claim.confidence))), 4)
            self._touch(claim)
            self.save()
        return claim

    # ReportSection CRUD
    def create_report_section(self, payload: ReportSection | dict[str, Any]) -> ReportSection:
        return self._create(payload, ReportSection.from_dict, ReportSection, self.report_sections, id_prefix="report-section")

    def list_report_sections(self, *, limit: int = 20, status: str | None = None) -> list[ReportSection]:
        return self._list_records(self.report_sections, limit=limit, status=status)

    def get_report_section(self, identifier: str) -> ReportSection | None:
        return self._lookup(self.report_sections, identifier)

    def update_report_section(self, identifier: str, **payload: Any) -> ReportSection | None:
        updates = {
            "title": payload.get("title"),
            "summary": payload.get("summary"),
            "status": payload.get("status"),
            "claim_card_ids": payload.get("claim_card_ids"),
            "report_id": payload.get("report_id"),
        }
        current = self._update_generic(identifier, self.report_sections, updates=updates)
        if current is not None and "position" in payload:
            current.position = _coerce_int(payload.get("position"), default=current.position)
            self._touch(current)
            self.save()
        return current

    # CitationBundle CRUD
    def create_citation_bundle(self, payload: CitationBundle | dict[str, Any]) -> CitationBundle:
        return self._create(payload, CitationBundle.from_dict, CitationBundle, self.citation_bundles, id_prefix="citation-bundle")

    def list_citation_bundles(self, *, limit: int = 20) -> list[CitationBundle]:
        return self._list_records(self.citation_bundles, limit=limit, status=None)

    def get_citation_bundle(self, identifier: str) -> CitationBundle | None:
        return self._lookup(self.citation_bundles, identifier)

    def update_citation_bundle(self, identifier: str, **payload: Any) -> CitationBundle | None:
        updates = {
            "label": payload.get("label"),
            "claim_card_id": payload.get("claim_card_id"),
            "note": payload.get("note"),
            "source_item_ids": payload.get("source_item_ids"),
            "source_urls": payload.get("source_urls"),
        }
        return self._update_generic(identifier, self.citation_bundles, updates=updates)

    # Report CRUD
    def _normalize_report_identifier(self, identifier: str) -> str:
        return _normalize_optional_string(identifier)

    @staticmethod
    def _normalize_profile_name(name: Any) -> str:
        return _normalize_optional_string(name).strip().lower()

    def _default_export_profile_payload(self, report_id: str, template: dict[str, Any]) -> dict[str, Any]:
        payload = dict(template)
        payload["report_id"] = report_id
        payload["name"] = _normalize_optional_string(payload.get("name"))
        if not payload["name"]:
            raise ValueError("Export profile name is required")
        return payload

    def ensure_default_export_profiles(self, report: Report) -> list[str]:
        existing_profiles = {
            self._normalize_profile_name(profile.name): profile
            for profile in self.export_profiles.values()
            if profile.report_id == report.id
        }
        ordered_profile_ids: list[str] = []
        for template in _DEFAULT_EXPORT_PROFILES:
            normalized_name = self._normalize_profile_name(template.get("name"))
            profile = existing_profiles.get(normalized_name)
            if profile is None:
                profile = self._create(
                    self._default_export_profile_payload(report.id, template),
                    ExportProfile.from_dict,
                    ExportProfile,
                    self.export_profiles,
                    id_prefix="export-profile",
                )
            if profile.id:
                ordered_profile_ids.append(profile.id)
        existing_profile_ids = list(_normalize_id_sequence(report.export_profile_ids))
        merged_profile_ids = _normalize_id_sequence([*ordered_profile_ids, *existing_profile_ids])
        if merged_profile_ids != existing_profile_ids:
            report.export_profile_ids = merged_profile_ids
            self._touch(report)
            self.save()
        return merged_profile_ids

    def _resolve_default_profile(self, report: Report, *, profile_id: str | None = None, default_name: str | None = None) -> str | None:
        if profile_id:
            return profile_id
        normalized_default = self._normalize_profile_name(default_name)
        for profile in self._lookup_reports_with_name(report.id):
            if normalized_default and profile.name.strip().lower() == normalized_default:
                return profile.id
            if not normalized_default and profile.name:
                return profile.id
        return None

    def _lookup_reports_with_name(self, report_id: str) -> list[ExportProfile]:
        return [
            profile
            for profile in self._list_records(self.export_profiles, limit=max(0, len(self.export_profiles)))
            if profile.report_id == report_id
        ]

    def create_report(self, payload: Report | dict[str, Any]) -> Report:
        report = self._create(payload, Report.from_dict, Report, self.reports, id_prefix="report")
        report.export_profile_ids = self.ensure_default_export_profiles(report)
        return report

    def list_reports(self, *, limit: int = 20, status: str | None = None) -> list[Report]:
        return self._list_records(self.reports, limit=limit, status=status)

    def get_report(self, identifier: str) -> Report | None:
        return self._lookup(self.reports, identifier)

    def update_report(self, identifier: str, **payload: Any) -> Report | None:
        updates = {
            "title": payload.get("title"),
            "brief_id": payload.get("brief_id"),
            "audience": payload.get("audience"),
            "status": payload.get("status"),
            "summary": payload.get("summary"),
            "tags": payload.get("tags"),
            "section_ids": payload.get("section_ids"),
            "claim_card_ids": payload.get("claim_card_ids"),
            "citation_bundle_ids": payload.get("citation_bundle_ids"),
            "export_profile_ids": payload.get("export_profile_ids"),
        }
        return self._update_generic(identifier, self.reports, updates=updates)

    # ExportProfile CRUD
    def create_export_profile(self, payload: ExportProfile | dict[str, Any]) -> ExportProfile:
        return self._create(
            payload,
            ExportProfile.from_dict,
            ExportProfile,
            self.export_profiles,
            id_prefix="export-profile",
        )

    def list_export_profiles(
        self,
        *,
        limit: int = 20,
        status: str | None = None,
        report_id: str | None = None,
    ) -> list[ExportProfile]:
        rows = list(self.export_profiles.values())
        if report_id:
            normalized_report_id = self._normalize_report_identifier(report_id)
            rows = [row for row in rows if row.report_id == normalized_report_id]
        if status is not None:
            normalized = {s.strip().lower() for s in _normalize_string_list([status])}
            rows = [row for row in rows if str(getattr(row, "status", "")).strip().lower() in normalized]
        rows.sort(key=lambda item: (str(item.updated_at), str(item.id)), reverse=True)
        return rows[: max(0, int(limit))]

    def get_export_profile(self, identifier: str) -> ExportProfile | None:
        return self._lookup(self.export_profiles, identifier)

    def update_export_profile(self, identifier: str, **payload: Any) -> ExportProfile | None:
        updates = {
            "name": payload.get("name"),
            "report_id": payload.get("report_id"),
            "output_format": payload.get("output_format"),
            "profile_version": payload.get("profile_version"),
        }
        current = self._update_generic(identifier, self.export_profiles, updates=updates)
        if current is not None and ("include_sections" in payload or "include_claim_cards" in payload or "include_bundles" in payload or "include_metadata" in payload):
            if "include_sections" in payload:
                current.include_sections = bool(payload.get("include_sections", current.include_sections))
            if "include_claim_cards" in payload:
                current.include_claim_cards = bool(payload.get("include_claim_cards", current.include_claim_cards))
            if "include_bundles" in payload:
                current.include_bundles = bool(payload.get("include_bundles", current.include_bundles))
            if "include_metadata" in payload:
                current.include_metadata = bool(payload.get("include_metadata", current.include_metadata))
            self._touch(current)
            self.save()
        return current

    @staticmethod
    def _normalize_dict_list(values: Any) -> list[dict[str, Any]]:
        if not isinstance(values, list):
            return []
        normalized: list[dict[str, Any]] = []
        for raw in values:
            if not isinstance(raw, dict):
                continue
            normalized.append(raw)
        return normalized

    @staticmethod
    def _extract_contradictions(raw: Any) -> list[dict[str, Any]]:
        normalized: list[dict[str, Any]] = []
        for row in ReportStore._normalize_dict_list(raw):
            detail = str(row.get("detail", row.get("text", "") or "")).strip()
            if not detail:
                continue
            severity = str(row.get("severity", "warning")).strip().lower() or "warning"
            normalized.append(
                {
                    "detail": detail,
                    "source": str(row.get("source", "governance")).strip() or "governance",
                    "severity": severity if severity in {"info", "warning", "error"} else "warning",
                },
            )
        if isinstance(raw, str):
            detail = raw.strip()
            if detail:
                normalized.append({
                    "detail": detail,
                    "source": "governance",
                    "severity": "warning",
                })
        return normalized

    @staticmethod
    def _normalize_optional_subject_kind(value: str | None) -> str:
        normalized = _normalize_optional_string(value).strip().lower()
        if not normalized:
            return ""
        if normalized not in _DELIVERY_SUBJECT_KINDS:
            raise ValueError(f"Unsupported subject_kind: {normalized}")
        return normalized

    @staticmethod
    def _normalize_required_subject_kind(value: str | None) -> str:
        normalized = _normalize_optional_string(value).strip().lower()
        if not normalized:
            raise ValueError("subject_kind is required")
        if normalized not in _DELIVERY_SUBJECT_KINDS:
            raise ValueError(f"Unsupported subject_kind: {normalized}")
        return normalized

    @staticmethod
    def _normalize_required_output_kind(value: str | None) -> str:
        normalized = _normalize_optional_string(value).strip().lower()
        if not normalized:
            raise ValueError("output_kind is required")
        if normalized not in _DELIVERY_OUTPUT_KINDS:
            raise ValueError(f"Unsupported output_kind: {normalized}")
        return normalized

    @staticmethod
    def _normalize_optional_output_kind(value: str | None) -> str:
        normalized = _normalize_optional_string(value).strip().lower()
        if not normalized:
            return ""
        if normalized not in _DELIVERY_OUTPUT_KINDS:
            raise ValueError(f"Unsupported output_kind: {normalized}")
        return normalized

    @staticmethod
    def _normalize_optional_delivery_mode(value: str | None) -> str:
        normalized = _normalize_optional_string(value).strip().lower() or "pull"
        if normalized not in _DELIVERY_MODES:
            raise ValueError(f"Unsupported delivery_mode: {normalized}")
        return normalized

    @staticmethod
    def _normalize_optional_status(value: str | None) -> str:
        normalized = _normalize_optional_string(value) or "active"
        if normalized.lower() not in _DELIVERY_SUBSCRIPTION_STATUSES:
            return "active"
        return normalized.strip().lower()

    @staticmethod
    def _normalize_optional_dispatch_status(value: str | None) -> str:
        normalized = _normalize_optional_string(value) or "pending"
        if normalized not in _DELIVERY_DISPATCH_STATUSES:
            return "pending"
        return normalized

    def _normalize_delivery_route_names(self, values: Any) -> list[str]:
        normalized: list[str] = []
        seen: set[str] = set()
        for name in _normalize_string_list(values):
            lowered = str(name).strip().lower()
            if lowered and lowered not in seen:
                normalized.append(lowered)
                seen.add(lowered)
        return normalized

    # Delivery Subscription CRUD
    def create_delivery_subscription(self, payload: DeliverySubscription | dict[str, Any]) -> DeliverySubscription:
        if isinstance(payload, dict):
            if "route_names" in payload:
                payload = dict(payload)
                payload["route_names"] = self._normalize_delivery_route_names(payload["route_names"])
        return self._create(
            payload,
            DeliverySubscription.from_dict,
            DeliverySubscription,
            self.delivery_subscriptions,
            id_prefix="delivery-subscription",
        )

    def list_delivery_subscriptions(
        self,
        *,
        limit: int = 20,
        status: str | None = None,
        subject_kind: str | None = None,
        subject_ref: str | None = None,
        output_kind: str | None = None,
        delivery_mode: str | None = None,
        route_name: str | None = None,
    ) -> list[DeliverySubscription]:
        rows = list(self.delivery_subscriptions.values())
        if subject_kind is not None:
            normalized_subject_kind = self._normalize_required_subject_kind(subject_kind)
            rows = [row for row in rows if row.subject_kind == normalized_subject_kind]
        if subject_ref is not None:
            normalized_subject_ref = _normalize_optional_string(subject_ref)
            rows = [row for row in rows if row.subject_ref == normalized_subject_ref]
        if output_kind is not None:
            normalized_output_kind = self._normalize_required_output_kind(output_kind)
            rows = [row for row in rows if row.output_kind == normalized_output_kind]
        if delivery_mode is not None:
            normalized_delivery_mode = self._normalize_optional_delivery_mode(delivery_mode)
            rows = [row for row in rows if row.delivery_mode == normalized_delivery_mode]
        if route_name is not None:
            normalized_route_name = _normalize_optional_string(route_name).strip().lower()
            rows = [
                row
                for row in rows
                if normalized_route_name and normalized_route_name in {name.lower() for name in row.route_names}
            ]
        if status is not None:
            allowed = {s.strip().lower() for s in _normalize_string_list([status])}
            rows = [row for row in rows if str(getattr(row, "status", "")).strip().lower() in allowed]
        rows.sort(key=lambda item: (str(item.updated_at), str(item.id)), reverse=True)
        return rows[: max(0, int(limit))]

    def get_delivery_subscription(self, identifier: str) -> DeliverySubscription | None:
        return self._lookup(self.delivery_subscriptions, identifier)

    def update_delivery_subscription(self, identifier: str, **payload: Any) -> DeliverySubscription | None:
        updates: dict[str, Any] = {}
        if "subject_kind" in payload:
            updates["subject_kind"] = self._normalize_required_subject_kind(payload.get("subject_kind"))
        if "subject_ref" in payload:
            updates["subject_ref"] = _normalize_optional_string(payload.get("subject_ref"))
        if "output_kind" in payload:
            updates["output_kind"] = self._normalize_required_output_kind(payload.get("output_kind"))
        if "delivery_mode" in payload:
            updates["delivery_mode"] = self._normalize_optional_delivery_mode(payload.get("delivery_mode"))
        if "route_names" in payload:
            updates["route_names"] = self._normalize_delivery_route_names(payload.get("route_names"))
        if "cursor_or_since" in payload:
            updates["cursor_or_since"] = _normalize_optional_string(payload.get("cursor_or_since"))
        if "status" in payload:
            updates["status"] = self._normalize_optional_status(payload.get("status"))
        current = self._update_generic(identifier, self.delivery_subscriptions, updates=updates)
        if current is None:
            return None
        return current

    def delete_delivery_subscription(self, identifier: str) -> DeliverySubscription | None:
        current = self._lookup(self.delivery_subscriptions, identifier)
        if current is None:
            return None
        del self.delivery_subscriptions[current.id]
        self.save()
        return current

    # Delivery dispatch record CRUD
    def create_delivery_dispatch_record(self, payload: DeliveryDispatchRecord | dict[str, Any]) -> DeliveryDispatchRecord:
        return self._create(
            payload,
            DeliveryDispatchRecord.from_dict,
            DeliveryDispatchRecord,
            self.delivery_dispatch_records,
            id_prefix="delivery-dispatch",
        )

    def list_delivery_dispatch_records(
        self,
        *,
        limit: int = 20,
        status: str | None = None,
        subscription_id: str | None = None,
        subject_kind: str | None = None,
        subject_ref: str | None = None,
        output_kind: str | None = None,
        route_name: str | None = None,
    ) -> list[DeliveryDispatchRecord]:
        rows = list(self.delivery_dispatch_records.values())
        if subscription_id is not None:
            rows = [row for row in rows if row.subscription_id == _normalize_optional_string(subscription_id)]
        if subject_kind is not None:
            rows = [row for row in rows if row.subject_kind == _normalize_optional_string(subject_kind).strip().lower()]
        if subject_ref is not None:
            rows = [row for row in rows if row.subject_ref == _normalize_optional_string(subject_ref)]
        if output_kind is not None:
            rows = [row for row in rows if row.output_kind == _normalize_optional_string(output_kind).strip().lower()]
        if route_name is not None:
            normalized_route_name = _normalize_optional_string(route_name).strip().lower()
            rows = [row for row in rows if row.route_name == normalized_route_name]
        if status is not None:
            allowed = {s.strip().lower() for s in _normalize_string_list([status])}
            rows = [row for row in rows if str(getattr(row, "status", "")).strip().lower() in allowed]
        rows.sort(key=lambda item: (str(item.updated_at), str(item.id)), reverse=True)
        return rows[: max(0, int(limit))]

    def get_delivery_dispatch_record(self, identifier: str) -> DeliveryDispatchRecord | None:
        return self._lookup(self.delivery_dispatch_records, identifier)

    def update_delivery_dispatch_record(self, identifier: str, **payload: Any) -> DeliveryDispatchRecord | None:
        updates: dict[str, Any] = {}
        if "subscription_id" in payload:
            updates["subscription_id"] = _normalize_optional_string(payload.get("subscription_id"))
        if "subject_kind" in payload:
            updates["subject_kind"] = _normalize_optional_string(payload.get("subject_kind")).strip().lower()
        if "subject_ref" in payload:
            updates["subject_ref"] = _normalize_optional_string(payload.get("subject_ref"))
        if "output_kind" in payload:
            updates["output_kind"] = _normalize_optional_string(payload.get("output_kind")).strip().lower()
        if "route_name" in payload:
            updates["route_name"] = _normalize_optional_string(payload.get("route_name"))
        if "route_label" in payload:
            updates["route_label"] = _normalize_optional_string(payload.get("route_label"))
        if "route_channel" in payload:
            updates["route_channel"] = _normalize_optional_string(payload.get("route_channel")).strip().lower()
        if "package_id" in payload:
            updates["package_id"] = _normalize_optional_string(payload.get("package_id"))
        if "package_signature" in payload:
            updates["package_signature"] = _normalize_optional_string(payload.get("package_signature"))
        if "package_profile_id" in payload:
            updates["package_profile_id"] = _normalize_optional_string(payload.get("package_profile_id"))
        if "status" in payload:
            updates["status"] = self._normalize_optional_dispatch_status(payload.get("status"))
        if "error" in payload:
            updates["error"] = _normalize_optional_string(payload.get("error"))
        current = self._update_generic(identifier, self.delivery_dispatch_records, updates=updates)
        if current is None:
            return None
        if "attempts" in payload:
            try:
                current.attempts = _coerce_int(payload.get("attempts"), default=current.attempts)
            except Exception:
                current.attempts = _coerce_int(current.attempts, default=0)
            self._touch(current)
            self.save()
        return current

    def assemble_report(
        self,
        identifier: str,
        *,
        include_sections: bool = True,
        include_claim_cards: bool = True,
        include_citation_bundles: bool = True,
        include_export_profiles: bool = True,
    ) -> dict[str, Any] | None:
        report = self.get_report(identifier)
        if report is None:
            return None

        section_map = {row.id: row for row in self.report_sections.values() if row.report_id == report.id}
        claim_map = {row.id: row for row in self.claim_cards.values()}
        bundle_map = {row.id: row for row in self.citation_bundles.values()}
        profile_map = {row.id: row for row in self.export_profiles.values()}

        ordered_sections = [section_map[section_id] for section_id in report.section_ids if section_id in section_map]

        section_ids_set = {row.id for row in ordered_sections}
        section_claim_ids: set[str] = set()
        for section in ordered_sections:
            section_claim_ids.update(section.claim_card_ids)

        missing_section_ids: list[str] = [
            section_id for section_id in report.section_ids
            if section_id not in section_ids_set
        ]

        claim_ids = list(report.claim_card_ids)
        if include_sections:
            claim_ids = sorted(set(claim_ids) | section_claim_ids, key=lambda item: item)
        claim_ids_seen: set[str] = set()
        ordered_claims: list[ClaimCard] = []
        for claim_id in claim_ids:
            claim = claim_map.get(claim_id)
            if claim is None:
                continue
            if claim.id in claim_ids_seen:
                continue
            claim_ids_seen.add(claim.id)
            ordered_claims.append(claim)

        used_bundle_ids: set[str] = set()
        ordered_bundles: list[CitationBundle] = []
        if include_citation_bundles:
            bundle_ids: list[str] = []
            for claim in ordered_claims:
                for bundle_id in claim.citation_bundle_ids:
                    if bundle_id in bundle_ids:
                        continue
                    bundle_ids.append(bundle_id)
            for bundle_id in bundle_ids:
                bundle = bundle_map.get(bundle_id)
                if bundle is None:
                    continue
                used_bundle_ids.add(bundle.id)
                ordered_bundles.append(bundle)

        ordered_profiles: list[ExportProfile] = []
        if include_export_profiles:
            for profile_id in report.export_profile_ids:
                profile = profile_map.get(profile_id)
                if profile is not None:
                    ordered_profiles.append(profile)

        used_claim_ids = {claim.id for claim in ordered_claims}
        section_claims_missing = sorted(
            claim_id
            for section in ordered_sections
            for claim_id in section.claim_card_ids
            if claim_id and claim_id not in used_claim_ids
        )
        section_without_claims = [
            section.id for section in ordered_sections
            if not [claim_id for claim_id in section.claim_card_ids if claim_id]
        ]

        report_claim_ids = [claim_id for claim_id in report.claim_card_ids if claim_id]
        uncovered_report_claims = [
            claim_id
            for claim_id in report_claim_ids
            if claim_id not in section_claim_ids
        ]

        claims_without_binding: list[str] = []
        claim_bundle_issues: list[str] = []
        for claim in ordered_claims:
            has_direct_sources = bool(claim.source_item_ids)
            referenced_bundles = [bundle_id for bundle_id in claim.citation_bundle_ids if bundle_id in bundle_map]
            has_bundle_sources = any(
                bool(bundle_map[bundle_id].source_item_ids or bundle_map[bundle_id].source_urls)
                for bundle_id in referenced_bundles
            ) if referenced_bundles else False
            has_any_sources = has_direct_sources or has_bundle_sources
            missing_bundles = [
                bundle_id
                for bundle_id in claim.citation_bundle_ids
                if bundle_id not in bundle_map
            ]
            if not has_any_sources:
                claims_without_binding.append(claim.id)
            if missing_bundles:
                claim_bundle_issues.append(f"{claim.id}:{','.join(missing_bundles)}")

        claim_binding_issues: list[dict[str, Any]] = []
        if claims_without_binding:
            claim_binding_issues.append(
                {
                    "kind": "uncited_claim",
                    "ids": claims_without_binding,
                    "detail": "Claims are missing source_item_ids and valid citation bundle sources.",
                },
            )
        if claim_bundle_issues:
            claim_binding_issues.append(
                {
                    "kind": "missing_citation_bundle",
                    "ids": claim_bundle_issues,
                    "detail": "Claim references unknown citation bundles.",
                },
            )

        section_coverage_issues: list[dict[str, Any]] = []
        if missing_section_ids:
            section_coverage_issues.append(
                {
                    "kind": "missing_sections",
                    "ids": missing_section_ids,
                    "detail": "Report references section IDs that do not exist.",
                },
            )
        if section_without_claims:
            section_coverage_issues.append(
                {
                    "kind": "empty_sections",
                    "ids": section_without_claims,
                    "detail": "Sections have no claim references.",
                },
            )
        if section_claims_missing:
            section_coverage_issues.append(
                {
                    "kind": "missing_section_claims",
                    "ids": section_claims_missing,
                    "detail": "Sections reference claims that cannot be found.",
                },
            )
        if uncovered_report_claims:
            section_coverage_issues.append(
                {
                    "kind": "uncovered_report_claims",
                    "ids": uncovered_report_claims,
                    "detail": "Report-level claims are not referenced by any section.",
                },
            )

        contradiction_entries: list[dict[str, Any]] = []
        contradiction_entries.extend(self._extract_contradictions(report.governance.get("contradictions")))
        if report.status and str(report.status).strip().lower() in {"conflicted", "blocked"}:
            contradiction_entries.append(
                {
                    "detail": "Report status is conflicted and blocks export.",
                    "source": "report_status",
                    "severity": "error",
                },
            )
        for claim in ordered_claims:
            contradiction_entries.extend(self._extract_contradictions(claim.governance.get("contradictions")))
            if claim.status in {"conflicted", "blocked", "disputed"}:
                contradiction_entries.append(
                    {
                        "detail": f"Claim is marked as {claim.status}.",
                        "source": claim.id,
                        "severity": "error",
                    },
                )

        for section in ordered_sections:
            contradiction_entries.extend(self._extract_contradictions(section.governance.get("contradictions")))

        unresolved_contradictions = [
            row for row in contradiction_entries
            if str(row.get("severity", "")).strip().lower() in {"error", "warning"}
        ]

        export_gate_issues: list[dict[str, Any]] = []
        for profile in ordered_profiles:
            if include_sections and profile.include_sections and not ordered_sections:
                export_gate_issues.append(
                    {
                        "kind": "profile_sections_missing",
                        "profile_id": profile.id,
                        "detail": "Export profile expects sections but report has none.",
                    },
                )
            if include_claim_cards and profile.include_claim_cards and not ordered_claims:
                export_gate_issues.append(
                    {
                        "kind": "profile_claims_missing",
                        "profile_id": profile.id,
                        "detail": "Export profile expects claim cards but none are available.",
                    },
                )
            if profile.include_bundles and report.citation_bundle_ids and not used_bundle_ids:
                export_gate_issues.append(
                    {
                        "kind": "profile_bundles_missing",
                        "profile_id": profile.id,
                        "detail": "Export profile expects citation bundles but references have no valid bundle.",
                    },
                )

        missing_profile_ids = [
            profile_id
            for profile_id in report.export_profile_ids
            if profile_id and profile_id not in {row.id for row in ordered_profiles}
        ]
        if missing_profile_ids:
            export_gate_issues.append(
                {
                    "kind": "missing_export_profiles",
                    "ids": missing_profile_ids,
                    "detail": "Report references export profiles that do not exist.",
                },
            )

        checks: dict[str, Any] = {
            "claim_source": {
                "status": "pass",
                "issues": claim_binding_issues,
                "summary": {
                    "total_claims": len(ordered_claims),
                    "claims_without_binding": len(claims_without_binding),
                    "missing_citation_bundles": len(claim_bundle_issues),
                },
            },
            "section_coverage": {
                "status": "pass",
                "issues": section_coverage_issues,
                "summary": {
                    "total_sections": len(ordered_sections),
                    "missing_sections": len(missing_section_ids),
                    "sections_without_claims": len(section_without_claims),
                    "uncovered_report_claims": len(uncovered_report_claims),
                    "missing_section_claims": len(section_claims_missing),
                },
            },
            "contradictions": {
                "status": "clear",
                "entries": contradiction_entries,
                "summary": {
                    "unresolved_count": len(unresolved_contradictions),
                },
            },
            "export_gates": {
                "status": "pass",
                "issues": export_gate_issues,
                "summary": {
                    "profile_count": len(report.export_profile_ids),
                    "resolved_profiles": len(ordered_profiles),
                },
            },
        }

        if claim_binding_issues:
            checks["claim_source"]["status"] = "review_required"
        if section_coverage_issues:
            checks["section_coverage"]["status"] = "review_required"
        if export_gate_issues:
            checks["export_gates"]["status"] = "review_required"

        contradiction_blocks = [
            row for row in contradiction_entries if str(row.get("severity", "")).strip().lower() == "error"
        ]
        if contradiction_blocks:
            checks["contradictions"]["status"] = "blocked"
        elif contradiction_entries:
            checks["contradictions"]["status"] = "warning"

        if not contradiction_entries:
            checks["contradictions"]["status"] = "clear"

        blocked = checks["contradictions"]["status"] == "blocked"
        needs_review = (
            checks["claim_source"]["status"] == "review_required"
            or checks["section_coverage"]["status"] == "review_required"
            or checks["export_gates"]["status"] == "review_required"
            or checks["contradictions"]["status"] == "warning"
        ) and not blocked

        if blocked:
            status = "blocked"
            operator_action = "hold_export"
        elif needs_review:
            status = "review_required"
            operator_action = "review_before_export"
        else:
            status = "ready"
            operator_action = "allow_export"

        quality = {
            "status": status,
            "operator_action": operator_action,
            "score": round(
                max(
                    0.0,
                    min(
                        1.0,
                        1.0
                        - (0.18 * (len(claims_without_binding) > 0))
                        - (0.12 * (1 if section_without_claims else 0))
                        - (0.1 * (len(section_coverage_issues)))
                        - (0.16 * (len(unresolved_contradictions)))
                    ),
                ),
                4,
            ),
            "contradictions": contradiction_entries,
            "can_export": status == "ready",
            "checks": checks,
        }

        return {
            "report": report.to_dict(),
            "sections": [section.to_dict() for section in ordered_sections] if include_sections else [],
            "claim_cards": [claim.to_dict() for claim in ordered_claims] if include_claim_cards else [],
            "citation_bundles": [bundle.to_dict() for bundle in ordered_bundles] if include_citation_bundles else [],
            "export_profiles": [profile.to_dict() for profile in ordered_profiles] if include_export_profiles else [],
            "quality": quality,
        }
