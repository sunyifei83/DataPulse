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


def _utcnow() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


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
        return {
            "total": len(filtered),
            "open_count": open_count,
            "closed_count": closed_count,
            "states": counts,
            "note_count": note_count,
            "processed_count": sum(1 for item in filtered if item.processed),
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
            },
            "candidate_count": candidate_count,
            "returned_count": len(top),
            "limit": max(0, limit),
            "candidates": top,
            "suggested_primary_id": suggested_primary,
        }
