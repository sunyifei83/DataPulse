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


def render_story_markdown(story: Story) -> str:
    lines = [
        f"# {story.title}",
        "",
        f"- story_id: {story.id}",
        f"- status: {story.status}",
        f"- item_count: {story.item_count}",
        f"- source_count: {story.source_count}",
        f"- score: {story.score}",
        f"- confidence: {story.confidence:.3f}",
        f"- generated_at: {story.generated_at}",
        "",
        story.summary,
        "",
        "## Entities",
    ]
    for entity in story.entities:
        lines.append(f"- {entity}")
    if not story.entities:
        lines.append("- none")

    lines.extend(["", "## Primary Evidence"])
    for evidence in story.primary_evidence:
        lines.append(
            f"- [{evidence.title}]({evidence.url}) | {evidence.source_name} | "
            f"score={evidence.score} confidence={evidence.confidence:.3f} state={evidence.review_state}"
        )
    if not story.primary_evidence:
        lines.append("- none")

    lines.extend(["", "## Secondary Evidence"])
    for evidence in story.secondary_evidence:
        lines.append(
            f"- [{evidence.title}]({evidence.url}) | {evidence.source_name} | "
            f"score={evidence.score} confidence={evidence.confidence:.3f} state={evidence.review_state}"
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
            primary_item_id=primary_evidence[0].item_id if primary_evidence else "",
            entities=entities,
            source_names=source_names,
            primary_evidence=primary_evidence,
            secondary_evidence=secondary_evidence,
            timeline=timeline,
            contradictions=contradictions,
            semantic_review=semantic_review,
            id=generate_slug(title, max_length=48),
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
