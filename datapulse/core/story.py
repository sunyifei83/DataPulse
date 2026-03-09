"""Story aggregation models, clustering, and storage for intelligence workspaces."""

from __future__ import annotations

import json
import re
from collections import Counter
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .entities import normalize_entity_name
from .entity_store import EntityStore
from .models import DataPulseItem
from .semantic import build_semantic_review
from .triage import build_item_governance, evidence_grade_priority
from .utils import content_fingerprint, generate_slug, get_domain, stories_path_from_env


def _utcnow() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _parse_dt(value: str) -> datetime:
    text = str(value or "").strip()
    if not text:
        return datetime.fromtimestamp(0, tz=timezone.utc)
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return datetime.fromtimestamp(0, tz=timezone.utc)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _tokenize(text: str) -> set[str]:
    return {
        token
        for token in re.findall(r"[\w\-]{2,}", str(text or "").lower())
        if token
    }


def _jaccard(left: set[str], right: set[str]) -> float:
    if not left or not right:
        return 0.0
    union = left | right
    if not union:
        return 0.0
    return len(left & right) / len(union)


def _entity_labels_for_item(item: DataPulseItem, *, entity_store: EntityStore | None = None) -> list[str]:
    rows: list[str] = []
    raw_entities = item.extra.get("entities")
    if isinstance(raw_entities, list):
        for raw in raw_entities:
            if isinstance(raw, dict):
                value = str(raw.get("display_name") or raw.get("name") or "").strip()
            elif isinstance(raw, str):
                value = raw.strip()
            else:
                continue
            if value:
                rows.append(value)

    if not rows and entity_store is not None:
        for entity in entity_store.query_by_source_item(item.id):
            value = str(entity.display_name or entity.name).strip()
            if value:
                rows.append(value)

    out: list[str] = []
    seen: set[str] = set()
    for raw in rows:
        normalized = normalize_entity_name(raw)
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        out.append(raw)
    return out


@dataclass
class StoryEvidence:
    item_id: str
    title: str
    url: str
    source_name: str
    source_type: str
    score: int = 0
    confidence: float = 0.0
    fetched_at: str = ""
    review_state: str = "new"
    role: str = "secondary"
    entities: list[str] = field(default_factory=list)
    governance: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.item_id = str(self.item_id or "").strip()
        self.title = str(self.title or "").strip()
        self.url = str(self.url or "").strip()
        self.source_name = str(self.source_name or "").strip()
        self.source_type = str(self.source_type or "").strip()
        self.role = str(self.role or "secondary").strip().lower() or "secondary"
        self.review_state = str(self.review_state or "new").strip().lower() or "new"
        try:
            self.score = int(self.score)
        except Exception:
            self.score = 0
        try:
            self.confidence = max(0.0, min(1.0, float(self.confidence)))
        except Exception:
            self.confidence = 0.0
        self.entities = [str(entity).strip() for entity in self.entities if str(entity).strip()]
        self.governance = dict(self.governance or {})

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "StoryEvidence":
        valid = {f.name for f in cls.__dataclass_fields__.values()}
        return cls(**{k: v for k, v in data.items() if k in valid})


@dataclass
class StoryTimelineEvent:
    time: str
    item_id: str
    title: str
    source_name: str
    url: str
    role: str = "secondary"
    score: int = 0

    def __post_init__(self) -> None:
        self.time = str(self.time or "").strip()
        self.item_id = str(self.item_id or "").strip()
        self.title = str(self.title or "").strip()
        self.source_name = str(self.source_name or "").strip()
        self.url = str(self.url or "").strip()
        self.role = str(self.role or "secondary").strip().lower() or "secondary"
        try:
            self.score = int(self.score)
        except Exception:
            self.score = 0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "StoryTimelineEvent":
        valid = {f.name for f in cls.__dataclass_fields__.values()}
        return cls(**{k: v for k, v in data.items() if k in valid})


@dataclass
class StoryConflict:
    topic: str
    positive: int = 0
    negative: int = 0
    neutral: int = 0
    note: str = ""

    def __post_init__(self) -> None:
        self.topic = str(self.topic or "").strip()
        self.note = str(self.note or "").strip()
        for field_name in ("positive", "negative", "neutral"):
            try:
                setattr(self, field_name, max(0, int(getattr(self, field_name))))
            except Exception:
                setattr(self, field_name, 0)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "StoryConflict":
        valid = {f.name for f in cls.__dataclass_fields__.values()}
        return cls(**{k: v for k, v in data.items() if k in valid})


@dataclass
class Story:
    title: str
    summary: str = ""
    status: str = "active"
    score: float = 0.0
    confidence: float = 0.0
    item_count: int = 0
    source_count: int = 0
    primary_item_id: str = ""
    entities: list[str] = field(default_factory=list)
    source_names: list[str] = field(default_factory=list)
    primary_evidence: list[StoryEvidence] = field(default_factory=list)
    secondary_evidence: list[StoryEvidence] = field(default_factory=list)
    timeline: list[StoryTimelineEvent] = field(default_factory=list)
    contradictions: list[StoryConflict] = field(default_factory=list)
    semantic_review: dict[str, Any] = field(default_factory=dict)
    governance: dict[str, Any] = field(default_factory=dict)
    generated_at: str = ""
    updated_at: str = ""
    id: str = ""

    def __post_init__(self) -> None:
        self.title = str(self.title or "").strip()
        if not self.title:
            raise ValueError("Story title is required")
        self.summary = str(self.summary or "").strip()
        self.status = str(self.status or "active").strip().lower() or "active"
        if not self.id:
            self.id = generate_slug(self.title, max_length=48)
        now = _utcnow()
        if not self.generated_at:
            self.generated_at = now
        if not self.updated_at:
            self.updated_at = self.generated_at
        try:
            self.score = round(float(self.score), 2)
        except Exception:
            self.score = 0.0
        try:
            self.confidence = round(max(0.0, min(1.0, float(self.confidence))), 4)
        except Exception:
            self.confidence = 0.0
        for field_name in ("item_count", "source_count"):
            try:
                setattr(self, field_name, max(0, int(getattr(self, field_name))))
            except Exception:
                setattr(self, field_name, 0)
        self.primary_item_id = str(self.primary_item_id or "").strip()
        self.entities = [str(entity).strip() for entity in self.entities if str(entity).strip()]
        self.source_names = [str(source).strip() for source in self.source_names if str(source).strip()]
        self.primary_evidence = [
            evidence if isinstance(evidence, StoryEvidence) else StoryEvidence.from_dict(evidence)
            for evidence in self.primary_evidence
            if isinstance(evidence, (StoryEvidence, dict))
        ]
        self.secondary_evidence = [
            evidence if isinstance(evidence, StoryEvidence) else StoryEvidence.from_dict(evidence)
            for evidence in self.secondary_evidence
            if isinstance(evidence, (StoryEvidence, dict))
        ]
        self.timeline = [
            event if isinstance(event, StoryTimelineEvent) else StoryTimelineEvent.from_dict(event)
            for event in self.timeline
            if isinstance(event, (StoryTimelineEvent, dict))
        ]
        self.contradictions = [
            conflict if isinstance(conflict, StoryConflict) else StoryConflict.from_dict(conflict)
            for conflict in self.contradictions
            if isinstance(conflict, (StoryConflict, dict))
        ]
        self.semantic_review = dict(self.semantic_review or {})
        self.governance = dict(self.governance or {})

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["primary_evidence"] = [evidence.to_dict() for evidence in self.primary_evidence]
        payload["secondary_evidence"] = [evidence.to_dict() for evidence in self.secondary_evidence]
        payload["timeline"] = [event.to_dict() for event in self.timeline]
        payload["contradictions"] = [conflict.to_dict() for conflict in self.contradictions]
        return payload

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Story":
        valid = {f.name for f in cls.__dataclass_fields__.values()}
        payload = {k: v for k, v in data.items() if k in valid}
        payload["primary_evidence"] = [
            StoryEvidence.from_dict(row)
            for row in payload.get("primary_evidence", [])
            if isinstance(row, dict)
        ]
        payload["secondary_evidence"] = [
            StoryEvidence.from_dict(row)
            for row in payload.get("secondary_evidence", [])
            if isinstance(row, dict)
        ]
        payload["timeline"] = [
            StoryTimelineEvent.from_dict(row)
            for row in payload.get("timeline", [])
            if isinstance(row, dict)
        ]
        payload["contradictions"] = [
            StoryConflict.from_dict(row)
            for row in payload.get("contradictions", [])
            if isinstance(row, dict)
        ]
        return cls(**payload)


class StoryStore:
    """File-backed storage for persisted story aggregation snapshots."""

    def __init__(self, path: str | None = None):
        self.path = Path(path or stories_path_from_env()).expanduser()
        self.version = 1
        self.stories: dict[str, Story] = {}
        self._load()

    def _load(self) -> None:
        if not self.path.exists():
            self.stories = {}
            return
        try:
            raw = json.loads(self.path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            self.stories = {}
            return
        if isinstance(raw, dict):
            self.version = int(raw.get("version", 1) or 1)
            rows = raw.get("stories", [])
        elif isinstance(raw, list):
            rows = raw
        else:
            rows = []
        loaded: dict[str, Story] = {}
        for row in rows if isinstance(rows, list) else []:
            if not isinstance(row, dict):
                continue
            try:
                story = Story.from_dict(row)
            except (TypeError, ValueError):
                continue
            loaded[story.id] = story
        self.stories = loaded

    def save(self) -> None:
        payload = {
            "version": self.version,
            "stories": [story.to_dict() for story in self.list_stories(limit=5000)],
        }
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    @staticmethod
    def _unique_id(base_id: str, existing: set[str]) -> str:
        candidate = (base_id or "story").strip() or "story"
        if candidate not in existing:
            return candidate
        suffix = 2
        while f"{candidate}-{suffix}" in existing:
            suffix += 1
        return f"{candidate}-{suffix}"

    def replace_stories(self, stories: list[Story]) -> list[Story]:
        normalized: dict[str, Story] = {}
        for story in stories:
            candidate = story if isinstance(story, Story) else Story.from_dict(story)
            candidate.id = self._unique_id(candidate.id, set(normalized))
            provenance = (
                candidate.governance.get("provenance", {})
                if isinstance(candidate.governance, dict)
                else {}
            )
            if isinstance(provenance, dict):
                provenance["story_id"] = candidate.id
            normalized[candidate.id] = candidate
        self.stories = normalized
        self.save()
        return self.list_stories(limit=len(normalized) or 20)

    def list_stories(self, *, limit: int = 20, min_items: int = 1) -> list[Story]:
        rows = [
            story for story in self.stories.values()
            if story.item_count >= max(1, int(min_items))
        ]
        rows.sort(
            key=lambda story: (
                story.score,
                story.confidence,
                story.source_count,
                story.updated_at,
                story.id,
            ),
            reverse=True,
        )
        return rows[: max(0, limit)]

    def get_story(self, identifier: str) -> Story | None:
        key = str(identifier or "").strip()
        if not key:
            return None
        story = self.stories.get(key)
        if story is not None:
            return story
        lowered = key.casefold()
        for candidate in self.stories.values():
            if candidate.title.casefold() == lowered:
                return candidate
        return None

    def update_story(
        self,
        identifier: str,
        *,
        title: str | None = None,
        summary: str | None = None,
        status: str | None = None,
    ) -> Story | None:
        story = self.get_story(identifier)
        if story is None:
            return None
        if title is not None:
            next_title = str(title or "").strip()
            if not next_title:
                raise ValueError("Story title cannot be empty")
            story.title = next_title
        if summary is not None:
            story.summary = str(summary or "").strip()
        if status is not None:
            next_status = str(status or "").strip().lower()
            if not next_status:
                raise ValueError("Story status cannot be empty")
            story.status = next_status
        story.updated_at = _utcnow()
        self.save()
        return story


def _descriptor_for_item(item: DataPulseItem, *, entity_store: EntityStore | None = None) -> dict[str, Any]:
    entity_labels = _entity_labels_for_item(item, entity_store=entity_store)
    return {
        "item": item,
        "fingerprint": content_fingerprint(item.content) if len(item.content) >= 50 else "",
        "title_tokens": _tokenize(item.title),
        "content_tokens": _tokenize(item.content[:1500]),
        "domain": get_domain(item.url),
        "entity_labels": entity_labels,
        "entity_keys": {normalize_entity_name(label) for label in entity_labels if normalize_entity_name(label)},
    }


def _cluster_similarity(descriptor: dict[str, Any], cluster: dict[str, Any]) -> float:
    if descriptor["fingerprint"] and descriptor["fingerprint"] in cluster["fingerprints"]:
        return 1.0
    title_overlap = _jaccard(descriptor["title_tokens"], cluster["title_tokens"])
    content_overlap = _jaccard(descriptor["content_tokens"], cluster["content_tokens"])
    entity_overlap = _jaccard(descriptor["entity_keys"], cluster["entity_keys"])
    same_domain = descriptor["domain"] == cluster["domain"] and descriptor["domain"] != "unknown"
    score = (0.45 * title_overlap) + (0.20 * content_overlap) + (0.25 * entity_overlap)
    if same_domain:
        score += 0.10
    if title_overlap >= 0.25 and entity_overlap >= 0.25:
        score += 0.08
    return round(min(score, 1.0), 4)


def _select_primary_count(item_count: int, evidence_limit: int) -> int:
    if evidence_limit <= 1:
        return 1
    if item_count >= 4:
        return min(2, evidence_limit)
    return 1


def _story_summary(title: str, *, item_count: int, source_count: int, entities: list[str], contradictions: int) -> str:
    lead = f"{item_count} signals across {source_count} sources around {title!r}"
    if entities:
        lead += f"; key entities: {', '.join(entities[:3])}"
    if contradictions:
        lead += f"; contradictions: {contradictions}"
    return lead


def _max_risk_level(left: str, right: str) -> str:
    priority = {"none": 0, "low": 1, "medium": 2, "high": 3}
    return left if priority.get(left, 0) >= priority.get(right, 0) else right


def build_factuality_gate(
    *,
    subject: str,
    surface: str,
    evidence_rows: list[dict[str, Any]],
    source_names: list[str] | None = None,
    grounded_claim_count: int = 0,
    contradiction_count: int = 0,
) -> dict[str, Any]:
    normalized_rows: list[dict[str, Any]] = []
    for raw in evidence_rows:
        if not isinstance(raw, dict):
            continue
        normalized_rows.append(raw)

    resolved_sources = {
        str(name or "").strip()
        for name in source_names or []
        if str(name or "").strip()
    }
    if not resolved_sources:
        resolved_sources = {
            str(row.get("source_name", "") or "").strip()
            for row in normalized_rows
            if str(row.get("source_name", "") or "").strip()
        }

    signals: list[dict[str, Any]] = []
    reasons: list[str] = []
    if not normalized_rows:
        return {
            "subject": subject,
            "surface": surface,
            "status": "empty",
            "score": 0.0,
            "operator_action": "review_before_delivery",
            "summary": "No evidence rows were selected for factuality review.",
            "counts": {
                "evidence_count": 0,
                "source_count": 0,
                "grounded_claim_count": 0,
                "grounded_item_count": 0,
                "verified_evidence_count": 0,
                "working_evidence_count": 0,
                "low_confidence_count": 0,
                "contradiction_count": max(0, int(contradiction_count)),
            },
            "signals": [
                {
                    "kind": "selection",
                    "status": "empty",
                    "detail": "No evidence rows reached the factuality gate.",
                }
            ],
            "reasons": ["No evidence rows reached the factuality gate."],
        }

    evidence_scores = [
        max(0.0, min(1.0, float(row.get("evidence_score", 0.0) or 0.0)))
        for row in normalized_rows
    ]
    avg_evidence_score = sum(evidence_scores) / max(1, len(evidence_scores))
    verified_count = sum(
        1
        for row in normalized_rows
        if str(row.get("evidence_grade", "working")).strip().lower() == "verified"
    )
    working_count = sum(
        1
        for row in normalized_rows
        if str(row.get("evidence_grade", "working")).strip().lower() in {"working", "discarded"}
    )
    low_confidence_count = sum(
        1
        for row in normalized_rows
        if float(row.get("confidence", 0.0) or 0.0) < 0.55
    )
    grounded_item_count = sum(
        1
        for row in normalized_rows
        if int(row.get("grounded_claim_count", 0) or 0) > 0
    )
    resolved_grounded_claim_count = max(
        0,
        int(grounded_claim_count or 0)
        or sum(int(row.get("grounded_claim_count", 0) or 0) for row in normalized_rows),
    )
    resolved_contradiction_count = max(0, int(contradiction_count or 0))
    source_count = len(resolved_sources)

    signals.append(
        {
            "kind": "source_support",
            "status": "strong" if source_count >= 2 else "limited",
            "detail": (
                f"{source_count} independent source(s) back this delivery surface."
                if source_count
                else "No source names were resolved for this delivery surface."
            ),
        }
    )
    signals.append(
        {
            "kind": "claim_grounding",
            "status": "grounded" if resolved_grounded_claim_count > 0 else "missing",
            "detail": (
                f"{resolved_grounded_claim_count} grounded claim(s) across {grounded_item_count} evidence row(s)."
                if resolved_grounded_claim_count > 0
                else "No grounded claims are attached to the selected evidence rows."
            ),
        }
    )
    signals.append(
        {
            "kind": "evidence_maturity",
            "status": (
                "verified"
                if verified_count == len(normalized_rows)
                else "mixed"
                if working_count > 0
                else "reviewed"
            ),
            "detail": (
                f"{verified_count}/{len(normalized_rows)} evidence row(s) are verified;"
                f" {working_count} remain working-grade."
            ),
        }
    )
    signals.append(
        {
            "kind": "contradiction_scan",
            "status": "detected" if resolved_contradiction_count > 0 else "clear",
            "detail": (
                f"{resolved_contradiction_count} contradiction signal(s) remain unresolved."
                if resolved_contradiction_count > 0
                else "No contradiction signals were detected in the selected evidence."
            ),
        }
    )
    signals.append(
        {
            "kind": "confidence_floor",
            "status": "low" if low_confidence_count > 0 else "ok",
            "detail": (
                f"{low_confidence_count} evidence row(s) fall below the 0.55 confidence floor."
                if low_confidence_count > 0
                else "All selected evidence rows meet the default confidence floor."
            ),
        }
    )

    status = "ready"
    operator_action = "allow_delivery"
    if resolved_contradiction_count > 0:
        status = "blocked"
        operator_action = "review_before_delivery"
        reasons.append("Contradiction signals remain unresolved across the selected evidence.")
    if source_count <= 1:
        if status != "blocked":
            status = "review_required"
            operator_action = "review_before_delivery"
        reasons.append("Only one source currently backs this delivery surface.")
    if resolved_grounded_claim_count <= 0:
        if status != "blocked":
            status = "review_required"
            operator_action = "review_before_delivery"
        reasons.append("Grounded claims are missing from the selected delivery evidence.")
    if working_count > 0:
        if status != "blocked":
            status = "review_required"
            operator_action = "review_before_delivery"
        reasons.append("Working-grade evidence is still present in the selected delivery evidence.")
    if low_confidence_count > 0:
        if status != "blocked":
            status = "review_required"
            operator_action = "review_before_delivery"
        reasons.append("At least one selected evidence row is below the default confidence floor.")

    score = avg_evidence_score
    if source_count >= 2:
        score += 0.12
    elif source_count == 1:
        score -= 0.08
    if resolved_grounded_claim_count > 0:
        score += min(0.12, 0.03 * min(4, resolved_grounded_claim_count))
    else:
        score -= 0.08
    if working_count > 0:
        score -= min(0.18, 0.06 * working_count)
    if low_confidence_count > 0:
        score -= min(0.12, 0.04 * low_confidence_count)
    if resolved_contradiction_count > 0:
        score -= 0.3
    score = round(max(0.0, min(1.0, score)), 4)

    return {
        "subject": subject,
        "surface": surface,
        "status": status,
        "score": score,
        "operator_action": operator_action,
        "summary": (
            f"{len(normalized_rows)} evidence row(s), {source_count} source(s), "
            f"{resolved_grounded_claim_count} grounded claim(s), {resolved_contradiction_count} contradiction signal(s)."
        ),
        "counts": {
            "evidence_count": len(normalized_rows),
            "source_count": source_count,
            "grounded_claim_count": resolved_grounded_claim_count,
            "grounded_item_count": grounded_item_count,
            "verified_evidence_count": verified_count,
            "working_evidence_count": working_count,
            "low_confidence_count": low_confidence_count,
            "contradiction_count": resolved_contradiction_count,
        },
        "signals": signals,
        "reasons": reasons,
    }


def _aggregate_story_evidence_grade(governances: list[dict[str, Any]]) -> str:
    if not governances:
        return "working"
    ranks = [evidence_grade_priority(row.get("evidence_grade")) for row in governances]
    if ranks and min(ranks) >= evidence_grade_priority("verified"):
        return "verified"
    if ranks and min(ranks) >= evidence_grade_priority("reviewed"):
        return "reviewed"
    return "working"


def _build_story_grounding(story_id: str, evidence_rows: list[StoryEvidence]) -> dict[str, Any]:
    claims: list[dict[str, Any]] = []
    grounded_items: set[str] = set()
    seen_claims: set[tuple[str, str]] = set()
    primary_claim_count = 0
    evidence_span_count = 0

    for evidence in evidence_rows:
        governance = evidence.governance if isinstance(evidence.governance, dict) else {}
        grounding = governance.get("grounding", {}) if isinstance(governance.get("grounding"), dict) else {}
        raw_claims = grounding.get("claims", []) if isinstance(grounding.get("claims"), list) else []
        if not raw_claims:
            continue
        evidence_claim_added = False
        for raw_claim in raw_claims:
            if not isinstance(raw_claim, dict):
                continue
            text = str(raw_claim.get("text", "") or "").strip()
            if not text:
                continue
            claim_key = (evidence.item_id, text.casefold())
            if claim_key in seen_claims:
                continue
            seen_claims.add(claim_key)

            claim_id = f"{story_id}:{evidence.item_id}:claim:{len(claims) + 1}"
            source_link = dict(raw_claim.get("source_link", {})) if isinstance(raw_claim.get("source_link"), dict) else {}
            source_link.setdefault("item_id", evidence.item_id)
            source_link.setdefault("title", evidence.title)
            source_link.setdefault("url", evidence.url)
            source_link.setdefault("source_name", evidence.source_name)
            source_link.setdefault("source_type", evidence.source_type)
            source_link["story_id"] = story_id

            spans: list[dict[str, Any]] = []
            for span_index, raw_span in enumerate(raw_claim.get("evidence_spans", []), start=1):
                if not isinstance(raw_span, dict):
                    continue
                span = dict(raw_span)
                span.setdefault("span_id", f"{claim_id}:span:{span_index}")
                span.setdefault("item_id", evidence.item_id)
                span.setdefault("url", evidence.url)
                spans.append(span)
            evidence_span_count += len(spans)

            claims.append(
                {
                    "claim_id": claim_id,
                    "origin_claim_id": str(raw_claim.get("claim_id", "") or "").strip(),
                    "text": text,
                    "role": evidence.role,
                    "source_link": source_link,
                    "evidence_spans": spans,
                }
            )
            evidence_claim_added = True
            if evidence.role == "primary":
                primary_claim_count += 1
        if evidence_claim_added:
            grounded_items.add(evidence.item_id)

    return {
        "mode": "projected" if claims else "empty",
        "grounded_item_count": len(grounded_items),
        "claim_count": len(claims),
        "primary_claim_count": primary_claim_count,
        "evidence_span_count": evidence_span_count,
        "claims": claims,
    }


def _build_story_governance(
    *,
    story_id: str,
    primary_item_id: str,
    source_names: list[str],
    evidence_rows: list[StoryEvidence],
    contradictions: list[StoryConflict],
    generated_at: str,
) -> dict[str, Any]:
    primary_governances = [
        dict(evidence.governance)
        for evidence in evidence_rows
        if evidence.role == "primary" and isinstance(evidence.governance, dict)
    ]
    all_governances = [
        dict(evidence.governance)
        for evidence in evidence_rows
        if isinstance(evidence.governance, dict)
    ]
    aggregated = primary_governances or all_governances
    evidence_grade = _aggregate_story_evidence_grade(aggregated)
    evidence_score = round(
        sum(float(row.get("evidence_score", 0.0) or 0.0) for row in aggregated) / max(1, len(aggregated)),
        4,
    )
    story_grounding = _build_story_grounding(story_id, evidence_rows)
    factuality_rows: list[dict[str, Any]] = []
    for evidence in evidence_rows:
        governance = evidence.governance if isinstance(evidence.governance, dict) else {}
        factuality_rows.append(
            {
                "item_id": evidence.item_id,
                "title": evidence.title,
                "source_name": evidence.source_name,
                "evidence_grade": str(governance.get("evidence_grade", "working")).strip().lower() or "working",
                "evidence_score": float(governance.get("evidence_score", 0.0) or 0.0),
                "review_state": str(governance.get("review_state") or evidence.review_state).strip().lower() or "new",
                "confidence": evidence.confidence,
                "grounded_claim_count": int(
                    (
                        governance.get("grounding", {})
                        if isinstance(governance.get("grounding"), dict)
                        else {}
                    ).get("claim_count", 0) or 0
                ),
            }
        )
    factuality = build_factuality_gate(
        subject="story",
        surface="story_export",
        evidence_rows=factuality_rows,
        source_names=source_names,
        grounded_claim_count=int(story_grounding.get("claim_count", 0) or 0),
        contradiction_count=len(contradictions),
    )

    delivery_status = "ready"
    delivery_level = "low"
    delivery_reasons: list[str] = []

    if contradictions:
        delivery_status = "review_required"
        delivery_level = "high"
        delivery_reasons.append("Story contains unresolved contradiction signals.")
    if any(str(row.get("evidence_grade", "working")).strip().lower() == "working" for row in aggregated):
        delivery_status = "review_required"
        delivery_level = _max_risk_level(delivery_level, "medium")
        delivery_reasons.append("Primary story evidence still includes working-grade signals.")
    if len(source_names) <= 1:
        delivery_status = "review_required"
        delivery_level = _max_risk_level(delivery_level, "medium")
        delivery_reasons.append("Story is currently backed by a single source.")
    if str(factuality.get("status", "review_required")).strip().lower() == "blocked":
        delivery_status = "review_required"
        delivery_level = _max_risk_level(delivery_level, "high")
        delivery_reasons.append("Factuality gate blocked outward-facing story delivery pending analyst review.")
    elif str(factuality.get("status", "review_required")).strip().lower() != "ready":
        delivery_status = "review_required"
        delivery_level = _max_risk_level(delivery_level, "medium")
        delivery_reasons.append("Factuality gate requires analyst review before outward-facing story delivery.")

    provenance_chain: list[dict[str, Any]] = []
    review_states: dict[str, int] = {}
    for evidence in evidence_rows:
        governance = evidence.governance if isinstance(evidence.governance, dict) else {}
        provenance = governance.get("provenance", {}) if isinstance(governance.get("provenance"), dict) else {}
        grounding = governance.get("grounding", {}) if isinstance(governance.get("grounding"), dict) else {}
        review_state = str(governance.get("review_state") or evidence.review_state).strip().lower() or "new"
        review_states[review_state] = review_states.get(review_state, 0) + 1
        provenance_chain.append(
            {
                "item_id": evidence.item_id,
                "role": evidence.role,
                "title": evidence.title,
                "source_name": evidence.source_name,
                "source_type": evidence.source_type,
                "review_state": review_state,
                "evidence_grade": str(governance.get("evidence_grade", "working")).strip().lower() or "working",
                "url": evidence.url,
                "fetched_at": provenance.get("fetched_at", evidence.fetched_at),
                "grounded_claim_count": int(grounding.get("claim_count", 0) or 0),
                "grounded_evidence_span_count": int(grounding.get("evidence_span_count", 0) or 0),
            }
        )

    return {
        "subject": "story",
        "evidence_grade": evidence_grade,
        "evidence_score": evidence_score,
        "grounding": story_grounding,
        "factuality": factuality,
        "provenance": {
            "kind": "story",
            "story_id": story_id,
            "primary_item_id": primary_item_id,
            "item_ids": [row["item_id"] for row in provenance_chain if row.get("item_id")],
            "source_names": list(source_names),
            "review_states": review_states,
            "evidence_chain": provenance_chain,
            "grounded_claim_count": int(story_grounding.get("claim_count", 0) or 0),
            "grounded_evidence_span_count": int(story_grounding.get("evidence_span_count", 0) or 0),
            "generated_at": generated_at,
        },
        "delivery_risk": {
            "surface": "story_package",
            "status": delivery_status,
            "level": delivery_level,
            "reasons": delivery_reasons,
            "route_observations": [],
        },
    }


def render_story_markdown(story: Story) -> str:
    governance = story.governance if isinstance(story.governance, dict) else {}
    delivery_risk = governance.get("delivery_risk", {}) if isinstance(governance.get("delivery_risk"), dict) else {}
    provenance = governance.get("provenance", {}) if isinstance(governance.get("provenance"), dict) else {}
    grounding = governance.get("grounding", {}) if isinstance(governance.get("grounding"), dict) else {}
    factuality = governance.get("factuality", {}) if isinstance(governance.get("factuality"), dict) else {}
    lines = [
        f"# {story.title}",
        "",
        f"- story_id: {story.id}",
        f"- status: {story.status}",
        f"- item_count: {story.item_count}",
        f"- source_count: {story.source_count}",
        f"- score: {story.score}",
        f"- confidence: {story.confidence:.3f}",
        f"- evidence_grade: {governance.get('evidence_grade', 'working')}",
        f"- factuality_status: {factuality.get('status', 'review_required')}",
        f"- factuality_score: {float(factuality.get('score', 0.0) or 0.0):.3f}",
        f"- delivery_status: {delivery_risk.get('status', 'review_required')}",
        f"- delivery_risk: {delivery_risk.get('level', 'medium')}",
        f"- generated_at: {story.generated_at}",
        "",
        story.summary,
        "",
        "## Governance",
        f"- primary_item_id: {provenance.get('primary_item_id', story.primary_item_id)}",
        f"- evidence_items: {len(provenance.get('item_ids', [])) if isinstance(provenance.get('item_ids'), list) else 0}",
        f"- sources: {', '.join(provenance.get('source_names', story.source_names)) if isinstance(provenance.get('source_names'), list) else ', '.join(story.source_names)}",
        f"- grounded_claims: {int(grounding.get('claim_count', 0) or 0)}",
        f"- grounded_evidence_spans: {int(grounding.get('evidence_span_count', 0) or 0)}",
    ]
    for reason in delivery_risk.get("reasons", []) if isinstance(delivery_risk.get("reasons"), list) else []:
        lines.append(f"- delivery_note: {reason}")

    lines.extend(["", "## Factuality Gate"])
    lines.append(f"- action: {factuality.get('operator_action', 'review_before_delivery')}")
    lines.append(f"- summary: {factuality.get('summary', 'No factuality summary recorded.')}")
    for reason in factuality.get("reasons", []) if isinstance(factuality.get("reasons"), list) else []:
        lines.append(f"- factuality_note: {reason}")
    for signal in factuality.get("signals", []) if isinstance(factuality.get("signals"), list) else []:
        if not isinstance(signal, dict):
            continue
        lines.append(
            f"- factuality_signal: {signal.get('kind', 'signal')}={signal.get('status', 'unknown')} | {signal.get('detail', '')}"
        )

    lines.extend([
        "",
        "## Entities",
    ])
    for entity in story.entities:
        lines.append(f"- {entity}")
    if not story.entities:
        lines.append("- none")

    lines.extend(["", "## Grounded Claims"])
    claim_rows = grounding.get("claims", []) if isinstance(grounding.get("claims"), list) else []
    for claim in claim_rows:
        if not isinstance(claim, dict):
            continue
        source_link = claim.get("source_link", {}) if isinstance(claim.get("source_link"), dict) else {}
        span_bits: list[str] = []
        for span in claim.get("evidence_spans", []) if isinstance(claim.get("evidence_spans"), list) else []:
            if not isinstance(span, dict):
                continue
            field = str(span.get("field", "content") or "content").strip()
            start = span.get("start")
            end = span.get("end")
            locator = f"{field}[{start}:{end}]" if isinstance(start, int) and isinstance(end, int) else field
            excerpt = str(span.get("text", "") or "").strip()
            span_bits.append(f"{locator} {excerpt!r}".strip())
        lines.append(
            f"- {str(claim.get('text', '') or '').strip()} | "
            f"source={source_link.get('source_name', '')}:{source_link.get('item_id', '')} | "
            f"evidence={'; '.join(span_bits) if span_bits else 'none'}"
        )
    if not claim_rows:
        lines.append("- none")

    lines.extend(["", "## Primary Evidence"])
    for evidence in story.primary_evidence:
        evidence_governance = evidence.governance if isinstance(evidence.governance, dict) else {}
        evidence_grounding = (
            evidence_governance.get("grounding", {})
            if isinstance(evidence_governance.get("grounding"), dict)
            else {}
        )
        lines.append(
            f"- [{evidence.title}]({evidence.url}) | {evidence.source_name} | "
            f"score={evidence.score} confidence={evidence.confidence:.3f} state={evidence.review_state} "
            f"grade={evidence_governance.get('evidence_grade', 'working')} "
            f"grounded_claims={int(evidence_grounding.get('claim_count', 0) or 0)} "
            f"spans={int(evidence_grounding.get('evidence_span_count', 0) or 0)}"
        )
    if not story.primary_evidence:
        lines.append("- none")

    lines.extend(["", "## Secondary Evidence"])
    for evidence in story.secondary_evidence:
        evidence_governance = evidence.governance if isinstance(evidence.governance, dict) else {}
        evidence_grounding = (
            evidence_governance.get("grounding", {})
            if isinstance(evidence_governance.get("grounding"), dict)
            else {}
        )
        lines.append(
            f"- [{evidence.title}]({evidence.url}) | {evidence.source_name} | "
            f"score={evidence.score} confidence={evidence.confidence:.3f} state={evidence.review_state} "
            f"grade={evidence_governance.get('evidence_grade', 'working')} "
            f"grounded_claims={int(evidence_grounding.get('claim_count', 0) or 0)} "
            f"spans={int(evidence_grounding.get('evidence_span_count', 0) or 0)}"
        )
    if not story.secondary_evidence:
        lines.append("- none")

    lines.extend(["", "## Contradictions"])
    for conflict in story.contradictions:
        lines.append(
            f"- {conflict.topic}: positive={conflict.positive} negative={conflict.negative} neutral={conflict.neutral}"
        )
    if not story.contradictions:
        lines.append("- none")

    lines.extend(["", "## Timeline"])
    for event in story.timeline:
        lines.append(f"- {event.time} | [{event.title}]({event.url}) | {event.source_name} | role={event.role}")
    if not story.timeline:
        lines.append("- none")

    return "\n".join(lines)


def _story_item_ids(story: Story) -> list[str]:
    rows: list[str] = []
    if story.primary_item_id:
        rows.append(story.primary_item_id)
    for evidence in [*story.primary_evidence, *story.secondary_evidence]:
        if evidence.item_id:
            rows.append(evidence.item_id)
    for event in story.timeline:
        if event.item_id:
            rows.append(event.item_id)
    return list(dict.fromkeys(rows))


def build_story_graph(
    story: Story,
    *,
    entity_store: EntityStore | None = None,
    entity_limit: int = 12,
    relation_limit: int = 24,
) -> dict[str, Any]:
    entity_limit = max(0, int(entity_limit))
    relation_limit = max(0, int(relation_limit))
    story_item_ids = set(_story_item_ids(story))

    entity_rows: list[dict[str, Any]] = []
    seen_entities: set[str] = set()
    for raw_label in story.entities:
        normalized = normalize_entity_name(raw_label)
        if not normalized or normalized in seen_entities:
            continue
        seen_entities.add(normalized)
        entity = entity_store.get_entity(raw_label) if entity_store is not None else None
        source_item_ids = set(entity.source_item_ids) if entity is not None else set()
        in_story_source_ids = sorted(story_item_ids & source_item_ids)
        entity_rows.append(
            {
                "id": f"entity:{normalized.lower()}",
                "entity_key": normalized,
                "label": entity.display_name if entity is not None else raw_label,
                "kind": "entity",
                "entity_type": entity.entity_type.value if entity is not None else "UNKNOWN",
                "source_count": len(source_item_ids),
                "mention_count": entity.mention_count if entity is not None else 0,
                "in_story_source_count": len(in_story_source_ids),
                "in_story_source_ids": in_story_source_ids,
            }
        )

    entity_rows.sort(
        key=lambda row: (
            row["in_story_source_count"],
            row["source_count"],
            row["mention_count"],
            row["label"],
        ),
        reverse=True,
    )
    selected_entities = entity_rows[:entity_limit]
    selected_keys = {row["entity_key"] for row in selected_entities}

    nodes: list[dict[str, Any]] = [
        {
            "id": story.id,
            "label": story.title,
            "kind": "story",
            "status": story.status,
            "item_count": story.item_count,
            "source_count": story.source_count,
            "focus": True,
        }
    ]
    for row in selected_entities:
        nodes.append({key: value for key, value in row.items() if key != "entity_key"})

    mention_edges: list[dict[str, Any]] = []
    for row in selected_entities:
        mention_edges.append(
            {
                "id": f"{story.id}->{row['id']}",
                "source": story.id,
                "target": row["id"],
                "kind": "story_entity",
                "relation_type": "MENTIONED_IN_STORY",
                "weight": max(1.0, float(row["in_story_source_count"] or row["source_count"] or 1)),
                "source_item_count": row["in_story_source_count"] or row["source_count"] or 1,
                "keywords": [],
            }
        )

    relation_edges: list[dict[str, Any]] = []
    if entity_store is not None and selected_keys:
        seen_relations: set[tuple[str, str, str]] = set()
        for relation in entity_store.relations:
            if relation.source_entity not in selected_keys or relation.target_entity not in selected_keys:
                continue
            relation_source_ids = {item_id for item_id in relation.source_item_ids if item_id}
            if relation_source_ids and story_item_ids and not (relation_source_ids & story_item_ids):
                continue
            relation_key = (relation.source_entity, relation.target_entity, relation.relation_type)
            if relation_key in seen_relations:
                continue
            seen_relations.add(relation_key)
            overlap_ids = sorted(story_item_ids & relation_source_ids) if relation_source_ids else []
            relation_edges.append(
                {
                    "id": f"rel:{relation.source_entity}:{relation.target_entity}:{relation.relation_type}",
                    "source": f"entity:{relation.source_entity.lower()}",
                    "target": f"entity:{relation.target_entity.lower()}",
                    "kind": "entity_relation",
                    "relation_type": relation.relation_type,
                    "weight": float(relation.weight or 1.0),
                    "source_item_count": len(overlap_ids) or len(relation_source_ids),
                    "source_item_ids": overlap_ids or sorted(relation_source_ids),
                    "keywords": list(relation.keywords),
                }
            )

    relation_edges.sort(
        key=lambda edge: (
            edge["source_item_count"],
            edge["weight"],
            edge["relation_type"],
            edge["id"],
        ),
        reverse=True,
    )
    relation_edges = relation_edges[:relation_limit]
    edges = [*mention_edges, *relation_edges]

    return {
        "story": {
            "id": story.id,
            "title": story.title,
            "status": story.status,
            "item_count": story.item_count,
            "source_count": story.source_count,
        },
        "nodes": nodes,
        "edges": edges,
        "entity_count": len(selected_entities),
        "edge_count": len(edges),
        "relation_count": len(relation_edges),
    }


def build_story_clusters(
    items: list[DataPulseItem],
    *,
    entity_store: EntityStore | None = None,
    max_stories: int = 10,
    evidence_limit: int = 6,
) -> list[Story]:
    if not items:
        return []

    ranked = sorted(
        items,
        key=lambda item: (item.score, item.confidence, _parse_dt(item.fetched_at).timestamp(), item.id),
        reverse=True,
    )
    clusters: list[dict[str, Any]] = []

    for item in ranked:
        descriptor = _descriptor_for_item(item, entity_store=entity_store)
        best_cluster: dict[str, Any] | None = None
        best_similarity = 0.0
        for cluster in clusters:
            similarity = _cluster_similarity(descriptor, cluster)
            if similarity > best_similarity:
                best_similarity = similarity
                best_cluster = cluster
        if best_cluster is None or best_similarity < 0.34:
            clusters.append(
                {
                    "descriptors": [descriptor],
                    "fingerprints": {descriptor["fingerprint"]} if descriptor["fingerprint"] else set(),
                    "title_tokens": set(descriptor["title_tokens"]),
                    "content_tokens": set(descriptor["content_tokens"]),
                    "entity_keys": set(descriptor["entity_keys"]),
                    "domain": descriptor["domain"],
                }
            )
            continue

        best_cluster["descriptors"].append(descriptor)
        if descriptor["fingerprint"]:
            best_cluster["fingerprints"].add(descriptor["fingerprint"])
        best_cluster["title_tokens"].update(descriptor["title_tokens"])
        best_cluster["content_tokens"].update(descriptor["content_tokens"])
        best_cluster["entity_keys"].update(descriptor["entity_keys"])

    stories: list[Story] = []
    for cluster in clusters:
        descriptors: list[dict[str, Any]] = sorted(
            cluster["descriptors"],
            key=lambda row: (
                row["item"].score,
                row["item"].confidence,
                _parse_dt(row["item"].fetched_at).timestamp(),
                row["item"].id,
            ),
            reverse=True,
        )
        cluster_items = [row["item"] for row in descriptors]
        exemplar = descriptors[0]
        evidence_limit_safe = max(1, int(evidence_limit))
        primary_count = _select_primary_count(len(cluster_items), evidence_limit_safe)

        entity_counter: Counter[str] = Counter()
        entity_display: dict[str, str] = {}
        for row in descriptors:
            for label in row["entity_labels"]:
                normalized = normalize_entity_name(label)
                if not normalized:
                    continue
                entity_counter[normalized] += 1
                entity_display[normalized] = label
        entities = [entity_display[key] for key, _ in entity_counter.most_common(6)]

        evidence_rows: list[StoryEvidence] = []
        for index, row in enumerate(descriptors[:evidence_limit_safe]):
            item = row["item"]
            role = "primary" if index < primary_count else "secondary"
            evidence_rows.append(
                StoryEvidence(
                    item_id=item.id,
                    title=item.title,
                    url=item.url,
                    source_name=item.source_name,
                    source_type=item.source_type.value,
                    score=item.score,
                    confidence=item.confidence,
                    fetched_at=item.fetched_at,
                    review_state=item.review_state,
                    role=role,
                    entities=row["entity_labels"],
                    governance=build_item_governance(item),
                )
            )

        primary_evidence = [row for row in evidence_rows if row.role == "primary"]
        secondary_evidence = [row for row in evidence_rows if row.role == "secondary"]
        timeline_rows = sorted(
            descriptors,
            key=lambda row: (_parse_dt(row["item"].extra.get("date_published", row["item"].fetched_at)), row["item"].id),
        )
        timeline = [
            StoryTimelineEvent(
                time=str(item.extra.get("date_published") or item.fetched_at),
                item_id=item.id,
                title=item.title,
                source_name=item.source_name,
                url=item.url,
                role="primary" if item.id == primary_evidence[0].item_id else "secondary",
                score=item.score,
            )
            for item in [row["item"] for row in timeline_rows]
        ]

        semantic_review = build_semantic_review(cluster_items)
        contradictions = [
            StoryConflict(
                topic=str(row.get("topic", "")),
                positive=int(row.get("positive", 0) or 0),
                negative=int(row.get("negative", 0) or 0),
                neutral=int(row.get("neutral", 0) or 0),
                note="semantic contradiction hint",
            )
            for row in semantic_review.get("contradictions", [])
            if isinstance(row, dict)
        ]
        status = "conflicted" if contradictions else "active"
        source_names = sorted({item.source_name for item in cluster_items})
        top_slice = cluster_items[: min(3, len(cluster_items))]
        avg_score = round(sum(item.score for item in top_slice) / max(1, len(top_slice)), 2)
        avg_confidence = round(sum(item.confidence for item in top_slice) / max(1, len(top_slice)), 4)
        title = exemplar["item"].title
        story_id = generate_slug(title, max_length=48)
        primary_item_id = primary_evidence[0].item_id if primary_evidence else ""
        generated_at = _utcnow()
        story = Story(
            title=title,
            summary=_story_summary(
                title,
                item_count=len(cluster_items),
                source_count=len(source_names),
                entities=entities,
                contradictions=len(contradictions),
            ),
            status=status,
            score=avg_score,
            confidence=avg_confidence,
            item_count=len(cluster_items),
            source_count=len(source_names),
            primary_item_id=primary_item_id,
            entities=entities,
            source_names=source_names,
            primary_evidence=primary_evidence,
            secondary_evidence=secondary_evidence,
            timeline=timeline,
            contradictions=contradictions,
            semantic_review=semantic_review,
            generated_at=generated_at,
            governance=_build_story_governance(
                story_id=story_id,
                primary_item_id=primary_item_id,
                source_names=source_names,
                evidence_rows=evidence_rows,
                contradictions=contradictions,
                generated_at=generated_at,
            ),
            id=story_id,
        )
        stories.append(story)

    stories.sort(
        key=lambda story: (
            story.score,
            story.confidence,
            story.item_count,
            story.source_count,
            story.id,
        ),
        reverse=True,
    )
    return stories[: max(0, max_stories)]
