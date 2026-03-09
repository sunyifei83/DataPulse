"""Review queue helpers for inbox triage workflows."""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any, Iterable

from .utils import content_fingerprint, get_domain

if TYPE_CHECKING:
    from .models import DataPulseItem

REVIEW_STATES = (
    "new",
    "triaged",
    "verified",
    "duplicate",
    "ignored",
    "escalated",
)
OPEN_REVIEW_STATES = {"new", "triaged", "escalated"}
TERMINAL_REVIEW_STATES = {"verified", "duplicate", "ignored"}
REVIEW_STATE_PRIORITY = {
    "escalated": 0,
    "new": 1,
    "triaged": 2,
    "verified": 3,
    "duplicate": 4,
    "ignored": 5,
}
REVIEW_STATE_SCORES = {
    "new": 0.0,
    "triaged": 0.25,
    "verified": 1.0,
    "duplicate": -0.8,
    "ignored": -1.0,
    "escalated": 0.6,
}
EVIDENCE_GRADE_PRIORITY = {
    "discarded": 0,
    "working": 1,
    "reviewed": 2,
    "verified": 3,
}
DELIVERY_RISK_PRIORITY = {
    "none": 0,
    "low": 1,
    "medium": 2,
    "high": 3,
}
GROUNDING_CLAIM_HINTS = (
    " is ",
    " are ",
    " was ",
    " were ",
    " will ",
    " can ",
    " should ",
    " works ",
    " confirms ",
    " confirmed ",
    " says ",
    " said ",
    " reports ",
    " reported ",
    " shows ",
    " showed ",
    " launched ",
    " rollout ",
    ">=",
    "<=",
    "=",
)
GROUNDING_SENTENCE_RE = re.compile(r"[^.!?\n\u3002\uff01\uff1f]+(?:[.!?\u3002\uff01\uff1f]+|$)")


def _utcnow() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


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


def _clamp_confidence(value: Any) -> float:
    try:
        return max(0.0, min(1.0, float(value)))
    except Exception:
        return 0.0


def normalize_review_state(value: str | None, *, processed: bool = False) -> str:
    normalized = str(value or "").strip().lower()
    if normalized in REVIEW_STATES:
        if processed and normalized == "new":
            return "triaged"
        return normalized
    return "triaged" if processed else "new"


def review_state_priority(state: str | None) -> int:
    normalized = normalize_review_state(state)
    return REVIEW_STATE_PRIORITY.get(normalized, REVIEW_STATE_PRIORITY["new"])


def review_state_score(state: str | None) -> float:
    normalized = normalize_review_state(state)
    return REVIEW_STATE_SCORES.get(normalized, 0.0)


def evidence_grade_priority(value: str | None) -> int:
    normalized = str(value or "").strip().lower()
    return EVIDENCE_GRADE_PRIORITY.get(normalized, EVIDENCE_GRADE_PRIORITY["working"])


def delivery_risk_priority(value: str | None) -> int:
    normalized = str(value or "").strip().lower()
    return DELIVERY_RISK_PRIORITY.get(normalized, DELIVERY_RISK_PRIORITY["medium"])


def _max_delivery_risk_level(left: str, right: str) -> str:
    return left if delivery_risk_priority(left) >= delivery_risk_priority(right) else right


def is_open_review_state(state: str | None) -> bool:
    return normalize_review_state(state) in OPEN_REVIEW_STATES


def is_digest_candidate(item: "DataPulseItem") -> bool:
    return normalize_review_state(item.review_state, processed=item.processed) not in {"duplicate", "ignored"}


def build_review_note(
    note: str,
    *,
    author: str = "system",
    created_at: str | None = None,
) -> dict[str, str]:
    text = str(note or "").strip()
    if not text:
        raise ValueError("Review note cannot be empty.")
    return {
        "author": str(author or "system").strip() or "system",
        "note": text,
        "created_at": created_at or _utcnow(),
    }


def build_review_action(
    *,
    from_state: str,
    to_state: str,
    actor: str = "system",
    note: str = "",
    duplicate_of: str | None = None,
    created_at: str | None = None,
) -> dict[str, str]:
    payload = {
        "actor": str(actor or "system").strip() or "system",
        "from_state": normalize_review_state(from_state),
        "to_state": normalize_review_state(to_state),
        "created_at": created_at or _utcnow(),
    }
    if note.strip():
        payload["note"] = note.strip()
    if duplicate_of:
        payload["duplicate_of"] = duplicate_of.strip()
    return payload


def _normalize_excerpt(value: Any, *, limit: int = 320) -> str:
    text = re.sub(r"\s+", " ", str(value or "")).strip()
    if limit > 0 and len(text) > limit:
        return text[:limit].rstrip()
    return text


def _build_grounding_source_link(item: "DataPulseItem") -> dict[str, str]:
    return {
        "item_id": item.id,
        "title": item.title,
        "url": item.url,
        "source_name": item.source_name,
        "source_type": item.source_type.value,
        "fetched_at": item.fetched_at,
    }


def _source_text_for_field(item: "DataPulseItem", field: str) -> str:
    normalized = str(field or "content").strip().lower()
    if normalized == "title":
        return str(item.title or "")
    return str(item.content or "")


def _locate_grounding_span(item: "DataPulseItem", snippet: str, *, preferred_field: str = "content") -> tuple[str, int, int] | None:
    needle = str(snippet or "").strip()
    if not needle:
        return None
    search_fields = [preferred_field, "title", "content"]
    seen_fields: set[str] = set()
    for field in search_fields:
        normalized_field = str(field or "content").strip().lower() or "content"
        if normalized_field in seen_fields:
            continue
        seen_fields.add(normalized_field)
        haystack = _source_text_for_field(item, normalized_field)
        if not haystack:
            continue
        start = haystack.find(needle)
        if start >= 0:
            return normalized_field, start, start + len(needle)
    return None


def _build_grounding_span(
    item: "DataPulseItem",
    *,
    field: str,
    start: int,
    end: int,
    text: str,
    span_id: str,
) -> dict[str, Any]:
    return {
        "span_id": span_id,
        "field": field,
        "start": max(0, int(start)),
        "end": max(0, int(end)),
        "text": text,
        "item_id": item.id,
        "url": item.url,
    }


def _normalize_grounding_span(
    item: "DataPulseItem",
    raw_span: Any,
    *,
    span_id: str,
    claim_text: str,
) -> dict[str, Any] | None:
    if isinstance(raw_span, str):
        located = _locate_grounding_span(item, raw_span)
        if located is None:
            return None
        field, start, end = located
        return _build_grounding_span(
            item,
            field=field,
            start=start,
            end=end,
            text=str(raw_span).strip(),
            span_id=span_id,
        )

    if not isinstance(raw_span, dict):
        return None

    field = str(raw_span.get("field") or raw_span.get("location") or "content").strip().lower() or "content"
    text = _normalize_excerpt(
        raw_span.get("text")
        or raw_span.get("quote")
        or raw_span.get("excerpt")
        or raw_span.get("evidence")
        or "",
        limit=0,
    )
    start = raw_span.get("start")
    end = raw_span.get("end")

    if isinstance(start, int) and isinstance(end, int) and end >= start:
        source_text = _source_text_for_field(item, field)
        resolved_text = text or source_text[start:end]
        if resolved_text:
            return _build_grounding_span(
                item,
                field=field,
                start=start,
                end=end,
                text=resolved_text,
                span_id=span_id,
            )

    located = _locate_grounding_span(item, text or claim_text, preferred_field=field)
    if located is None:
        return None
    resolved_field, resolved_start, resolved_end = located
    resolved_text = text or _source_text_for_field(item, resolved_field)[resolved_start:resolved_end]
    return _build_grounding_span(
        item,
        field=resolved_field,
        start=resolved_start,
        end=resolved_end,
        text=resolved_text,
        span_id=span_id,
    )


def _grounding_claim_signature(item_id: str, text: str) -> tuple[str, str]:
    return item_id, _normalize_excerpt(text, limit=0).casefold()


def _normalize_grounded_claim(
    item: "DataPulseItem",
    raw_claim: Any,
    *,
    index: int,
) -> dict[str, Any] | None:
    if isinstance(raw_claim, str):
        claim_text = _normalize_excerpt(raw_claim, limit=0)
        raw_spans: list[Any] = [raw_claim]
    elif isinstance(raw_claim, dict):
        claim_text = _normalize_excerpt(
            raw_claim.get("claim")
            or raw_claim.get("text")
            or raw_claim.get("statement")
            or raw_claim.get("summary")
            or "",
            limit=0,
        )
        raw_spans = raw_claim.get("evidence_spans") or raw_claim.get("spans") or raw_claim.get("evidence") or []
        if isinstance(raw_spans, (str, dict)):
            raw_spans = [raw_spans]
        if not isinstance(raw_spans, list):
            raw_spans = []
    else:
        return None

    if not claim_text:
        return None

    claim_id = f"{item.id}:claim:{index}"
    spans: list[dict[str, Any]] = []
    for span_index, raw_span in enumerate(raw_spans, start=1):
        normalized_span = _normalize_grounding_span(
            item,
            raw_span,
            span_id=f"{claim_id}:span:{span_index}",
            claim_text=claim_text,
        )
        if normalized_span is None:
            continue
        spans.append(normalized_span)

    if not spans:
        located = _locate_grounding_span(item, claim_text)
        if located is not None:
            field, start, end = located
            spans.append(
                _build_grounding_span(
                    item,
                    field=field,
                    start=start,
                    end=end,
                    text=claim_text,
                    span_id=f"{claim_id}:span:1",
                )
            )

    source_link = _build_grounding_source_link(item)
    if isinstance(raw_claim, dict) and isinstance(raw_claim.get("source_link"), dict):
        source_link.update(
            {
                str(key): str(value)
                for key, value in raw_claim.get("source_link", {}).items()
                if value is not None
            }
        )

    return {
        "claim_id": claim_id,
        "text": claim_text,
        "source_link": source_link,
        "evidence_spans": spans,
    }


def _structured_grounded_claims(item: "DataPulseItem") -> list[dict[str, Any]]:
    extra = item.extra if isinstance(item.extra, dict) else {}
    raw_claims = extra.get("grounded_claims")
    if not isinstance(raw_claims, list):
        grounding = extra.get("grounding")
        if isinstance(grounding, dict) and isinstance(grounding.get("claims"), list):
            raw_claims = grounding.get("claims")
    if not isinstance(raw_claims, list):
        return []

    claims: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    for index, raw_claim in enumerate(raw_claims, start=1):
        normalized = _normalize_grounded_claim(item, raw_claim, index=index)
        if normalized is None:
            continue
        signature = _grounding_claim_signature(item.id, normalized["text"])
        if signature in seen:
            continue
        seen.add(signature)
        claims.append(normalized)
    return claims


def _iter_sentence_spans(text: str) -> list[tuple[str, int, int]]:
    source = str(text or "")
    if not source.strip():
        return []
    spans: list[tuple[str, int, int]] = []
    for match in GROUNDING_SENTENCE_RE.finditer(source):
        chunk = match.group(0)
        trimmed = chunk.strip()
        if not trimmed:
            continue
        left_trim = len(chunk) - len(chunk.lstrip())
        start = match.start() + left_trim
        end = start + len(trimmed)
        spans.append((trimmed, start, end))
    if spans:
        return spans
    trimmed = source.strip()
    start = source.find(trimmed)
    return [(trimmed, start, start + len(trimmed))] if trimmed else []


def _looks_like_grounded_claim(text: str) -> bool:
    normalized = f" {_normalize_excerpt(text, limit=0).lower()} "
    if any(hint in normalized for hint in GROUNDING_CLAIM_HINTS):
        return True
    return bool(re.search(r"[$¥€]?\d+(?:[.,]\d+)?%?", normalized))


def _heuristic_grounded_claims(item: "DataPulseItem") -> list[dict[str, Any]]:
    claims: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()

    def _append_claims(field: str, text: str) -> None:
        for sentence, start, end in _iter_sentence_spans(text):
            if not _looks_like_grounded_claim(sentence):
                continue
            signature = _grounding_claim_signature(item.id, sentence)
            if signature in seen:
                continue
            seen.add(signature)
            claim_id = f"{item.id}:claim:{len(claims) + 1}"
            claims.append(
                {
                    "claim_id": claim_id,
                    "text": sentence,
                    "source_link": _build_grounding_source_link(item),
                    "evidence_spans": [
                        _build_grounding_span(
                            item,
                            field=field,
                            start=start,
                            end=end,
                            text=sentence,
                            span_id=f"{claim_id}:span:1",
                        )
                    ],
                }
            )
            if len(claims) >= 3:
                return

    _append_claims("title", item.title)
    if len(claims) < 3:
        _append_claims("content", item.content)

    if claims:
        return claims

    fallback_sentences = _iter_sentence_spans(item.content or item.title)
    if not fallback_sentences:
        return []
    sentence, start, end = fallback_sentences[0]
    claim_id = f"{item.id}:claim:1"
    field = "content" if item.content.strip() else "title"
    return [
        {
            "claim_id": claim_id,
            "text": sentence,
            "source_link": _build_grounding_source_link(item),
            "evidence_spans": [
                _build_grounding_span(
                    item,
                    field=field,
                    start=start,
                    end=end,
                    text=sentence,
                    span_id=f"{claim_id}:span:1",
                )
            ],
        }
    ]


def build_item_grounding(item: "DataPulseItem") -> dict[str, Any]:
    claims = _structured_grounded_claims(item)
    mode = "provided"
    if not claims:
        claims = _heuristic_grounded_claims(item)
        mode = "heuristic" if claims else "empty"
    evidence_span_count = sum(
        len(claim.get("evidence_spans", []))
        for claim in claims
        if isinstance(claim.get("evidence_spans"), list)
    )
    return {
        "mode": mode,
        "claim_count": len(claims),
        "evidence_span_count": evidence_span_count,
        "claims": claims,
    }


def build_item_provenance(
    item: "DataPulseItem",
    *,
    grounding: dict[str, Any] | None = None,
) -> dict[str, Any]:
    search_sources = _normalize_string_list(item.extra.get("search_sources"))
    source_refs = _normalize_string_list([item.source_name, *search_sources])
    grounding_payload = grounding if isinstance(grounding, dict) else {}
    return {
        "kind": "item",
        "item_id": item.id,
        "url": item.url,
        "source_name": item.source_name,
        "source_type": item.source_type.value,
        "fetched_at": item.fetched_at,
        "review_state": normalize_review_state(item.review_state, processed=item.processed),
        "duplicate_of": item.duplicate_of or "",
        "watch_mission_id": str(item.extra.get("watch_mission_id", "") or "").strip(),
        "watch_mission_name": str(item.extra.get("watch_mission_name", "") or "").strip(),
        "search_query": str(item.extra.get("search_query", "") or "").strip(),
        "search_provider": str(item.extra.get("search_provider", "") or "").strip(),
        "source_refs": source_refs,
        "review_note_count": len(item.review_notes),
        "review_action_count": len(item.review_actions),
        "grounded_claim_count": int(grounding_payload.get("claim_count", 0) or 0),
        "grounded_evidence_span_count": int(grounding_payload.get("evidence_span_count", 0) or 0),
    }


def build_item_governance(item: "DataPulseItem") -> dict[str, Any]:
    review_state = normalize_review_state(item.review_state, processed=item.processed)
    confidence = _clamp_confidence(item.confidence)
    grounding = build_item_grounding(item)
    review_signal = {
        "new": 0.2,
        "triaged": 0.55,
        "verified": 1.0,
        "duplicate": 0.0,
        "ignored": 0.0,
        "escalated": 0.7,
    }.get(review_state, 0.2)
    evidence_score = round((confidence * 0.6) + (review_signal * 0.4), 4)

    if review_state in {"duplicate", "ignored"}:
        evidence_grade = "discarded"
        evidence_score = 0.0
    elif review_state == "verified":
        evidence_grade = "verified"
        evidence_score = max(evidence_score, 0.9)
    elif review_state in {"triaged", "escalated"} and confidence >= 0.4:
        evidence_grade = "reviewed"
    else:
        evidence_grade = "working"

    delivery_status = "ready"
    delivery_level = "low"
    delivery_reasons: list[str] = []

    if review_state in {"duplicate", "ignored"}:
        delivery_status = "suppressed"
        delivery_level = "high"
        delivery_reasons.append("Item is excluded from downstream evidence because review_state is terminal.")
    elif review_state == "new":
        delivery_status = "review_required"
        delivery_level = "high"
        delivery_reasons.append("Item has not been triaged yet.")
    else:
        if evidence_grade != "verified":
            delivery_status = "review_required"
            delivery_level = "medium"
            delivery_reasons.append("Item remains actionable evidence, but it is not yet fully verified.")
        if confidence < 0.55:
            delivery_status = "review_required"
            delivery_level = _max_delivery_risk_level(delivery_level, "high")
            delivery_reasons.append("Item confidence is below the default delivery comfort threshold (0.55).")
        if review_state == "escalated":
            delivery_status = "review_required"
            delivery_level = _max_delivery_risk_level(delivery_level, "medium")
            delivery_reasons.append("Escalated review state still requires analyst confirmation before broad delivery.")

    return {
        "subject": "item",
        "evidence_grade": evidence_grade,
        "evidence_score": evidence_score,
        "review_state": review_state,
        "confidence": confidence,
        "provenance": build_item_provenance(item, grounding=grounding),
        "grounding": grounding,
        "delivery_risk": {
            "surface": "pre_delivery",
            "status": delivery_status,
            "level": delivery_level,
            "reasons": delivery_reasons,
            "route_observations": [],
        },
    }


def serialize_item_with_governance(item: "DataPulseItem") -> dict[str, Any]:
    payload = item.to_dict()
    payload["governance"] = build_item_governance(item)
    return payload


def triage_counts(items: Iterable["DataPulseItem"]) -> dict[str, int]:
    counts = {state: 0 for state in REVIEW_STATES}
    for item in items:
        counts[normalize_review_state(item.review_state, processed=item.processed)] += 1
    return counts


def _sortable_epoch(value: str) -> float:
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp()
    except Exception:
        return 0.0


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


class TriageQueue:
    """Reader-facing triage service backed by UnifiedInbox."""

    def __init__(self, inbox: Any):
        self.inbox = inbox

    def _find_item(self, item_id: str) -> "DataPulseItem | None":
        for item in self.inbox.items:
            if item.id == item_id:
                return item
        return None

    def list_items(
        self,
        *,
        limit: int = 20,
        min_confidence: float = 0.0,
        states: list[str] | None = None,
        include_closed: bool = False,
    ) -> list["DataPulseItem"]:
        normalized_states = None
        if states:
            normalized_states = {normalize_review_state(state) for state in states}
        items: list[DataPulseItem] = []
        for item in self.inbox.items:
            if item.confidence < min_confidence:
                continue
            state = normalize_review_state(item.review_state, processed=item.processed)
            if normalized_states is not None and state not in normalized_states:
                continue
            if normalized_states is None and not include_closed and state not in OPEN_REVIEW_STATES:
                continue
            items.append(item)
        items.sort(
            key=lambda item: (
                review_state_priority(item.review_state),
                -item.score,
                -item.confidence,
                -_sortable_epoch(item.fetched_at),
            ),
        )
        return items[: max(0, limit)]

    def update_state(
        self,
        item_id: str,
        *,
        state: str,
        note: str = "",
        actor: str = "system",
        duplicate_of: str | None = None,
    ) -> "DataPulseItem | None":
        item = self._find_item(item_id)
        if item is None:
            return None
        next_state = normalize_review_state(state, processed=item.processed)
        if next_state == "duplicate" and duplicate_of == item.id:
            raise ValueError("duplicate_of cannot equal item id")
        previous_state = normalize_review_state(item.review_state, processed=item.processed)
        item.review_state = next_state
        item.processed = next_state in TERMINAL_REVIEW_STATES
        if next_state == "duplicate":
            item.duplicate_of = str(duplicate_of or "").strip() or item.duplicate_of
        else:
            item.duplicate_of = None
        item.review_actions.append(
            build_review_action(
                from_state=previous_state,
                to_state=next_state,
                actor=actor,
                note=note,
                duplicate_of=item.duplicate_of,
            )
        )
        if note.strip():
            item.review_notes.append(build_review_note(note, author=actor))
        self.inbox.save()
        return item

    def add_note(
        self,
        item_id: str,
        *,
        note: str,
        author: str = "system",
    ) -> "DataPulseItem | None":
        item = self._find_item(item_id)
        if item is None:
            return None
        if normalize_review_state(item.review_state, processed=item.processed) == "new":
            item.review_state = "triaged"
        item.review_notes.append(build_review_note(note, author=author))
        item.review_actions.append(
            {
                "actor": str(author or "system").strip() or "system",
                "action": "note",
                "created_at": _utcnow(),
            }
        )
        self.inbox.save()
        return item

    def stats(self, *, min_confidence: float = 0.0) -> dict[str, Any]:
        filtered = [item for item in self.inbox.items if item.confidence >= min_confidence]
        counts = triage_counts(filtered)
        open_count = sum(count for state, count in counts.items() if state in OPEN_REVIEW_STATES)
        closed_count = sum(count for state, count in counts.items() if state in TERMINAL_REVIEW_STATES)
        note_count = sum(len(item.review_notes) for item in filtered)
        evidence_grade_counts = {grade: 0 for grade in EVIDENCE_GRADE_PRIORITY}
        delivery_risk_counts = {level: 0 for level in DELIVERY_RISK_PRIORITY}
        grounding_totals = {
            "items_with_claims": 0,
            "claim_count": 0,
            "evidence_span_count": 0,
        }
        for item in filtered:
            governance = build_item_governance(item)
            evidence_grade = str(governance.get("evidence_grade", "working")).strip().lower() or "working"
            delivery_risk = governance.get("delivery_risk", {})
            delivery_level = (
                str(delivery_risk.get("level", "medium")).strip().lower()
                if isinstance(delivery_risk, dict)
                else "medium"
            )
            grounding = governance.get("grounding", {}) if isinstance(governance.get("grounding"), dict) else {}
            claim_count = int(grounding.get("claim_count", 0) or 0)
            span_count = int(grounding.get("evidence_span_count", 0) or 0)
            evidence_grade_counts[evidence_grade] = evidence_grade_counts.get(evidence_grade, 0) + 1
            delivery_risk_counts[delivery_level] = delivery_risk_counts.get(delivery_level, 0) + 1
            if claim_count > 0:
                grounding_totals["items_with_claims"] += 1
            grounding_totals["claim_count"] += claim_count
            grounding_totals["evidence_span_count"] += span_count
        return {
            "total": len(filtered),
            "open_count": open_count,
            "closed_count": closed_count,
            "states": counts,
            "note_count": note_count,
            "processed_count": sum(1 for item in filtered if item.processed),
            "evidence_grade_counts": evidence_grade_counts,
            "delivery_risk_counts": delivery_risk_counts,
            "grounding": grounding_totals,
        }

    def explain_duplicate(self, item_id: str, *, limit: int = 5) -> dict[str, Any] | None:
        item = self._find_item(item_id)
        if item is None:
            return None

        title_tokens = _tokenize(item.title)
        content_tokens = _tokenize(item.content[:1200])
        domain = get_domain(item.url)
        fingerprint = content_fingerprint(item.content) if len(item.content) >= 50 else ""
        candidates: list[dict[str, Any]] = []

        for other in self.inbox.items:
            if other.id == item.id:
                continue
            other_title_tokens = _tokenize(other.title)
            other_content_tokens = _tokenize(other.content[:1200])
            title_overlap = _jaccard(title_tokens, other_title_tokens)
            content_overlap = _jaccard(content_tokens, other_content_tokens)
            domain_match = domain == get_domain(other.url)
            fingerprint_match = bool(fingerprint) and len(other.content) >= 50 and fingerprint == content_fingerprint(other.content)
            similarity = 1.0 if fingerprint_match else round((0.55 * title_overlap) + (0.35 * content_overlap) + (0.10 if domain_match else 0.0), 4)
            if similarity < 0.18 and not fingerprint_match:
                continue

            keep_current = (item.score, item.confidence, item.fetched_at) >= (other.score, other.confidence, other.fetched_at)
            signals: list[str] = []
            if fingerprint_match:
                signals.append("same_fingerprint")
            if domain_match:
                signals.append("same_domain")
            if title_overlap >= 0.25:
                signals.append("title_overlap")
            if content_overlap >= 0.25:
                signals.append("content_overlap")

            candidates.append(
                {
                    "id": other.id,
                    "title": other.title,
                    "url": other.url,
                    "review_state": normalize_review_state(other.review_state, processed=other.processed),
                    "similarity": similarity,
                    "title_overlap": round(title_overlap, 4),
                    "content_overlap": round(content_overlap, 4),
                    "same_domain": domain_match,
                    "fingerprint_match": fingerprint_match,
                    "signals": signals,
                    "suggested_primary_id": item.id if keep_current else other.id,
                    "governance": build_item_governance(other),
                }
            )

        candidates.sort(key=lambda row: (row["similarity"], row["fingerprint_match"], row["title_overlap"]), reverse=True)
        candidate_count = len(candidates)
        top = candidates[: max(0, limit)]
        suggested_primary = item.id
        if top and top[0]["suggested_primary_id"] != item.id:
            suggested_primary = str(top[0]["suggested_primary_id"])
        return {
            "item": {
                "id": item.id,
                "title": item.title,
                "url": item.url,
                "review_state": normalize_review_state(item.review_state, processed=item.processed),
                "governance": build_item_governance(item),
            },
            "candidate_count": candidate_count,
            "returned_count": len(top),
            "limit": max(0, limit),
            "candidates": top,
            "suggested_primary_id": suggested_primary,
        }
