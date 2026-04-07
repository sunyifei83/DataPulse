"""Structured report-production objects and repository-backed persistence."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, TypeAlias, TypeVar
from urllib.parse import urlparse

from .alerts import DeliveryDispatchError, resolve_delivery_targets
from .story import build_story_evidence_intake
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


def _as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def normalize_report_evidence_intake(payload: Any) -> dict[str, Any]:
    story_meta: dict[str, Any] = {}
    raw_rows: list[dict[str, Any]] = []

    if isinstance(payload, dict) and (
        isinstance(payload.get("primary_evidence"), list) or isinstance(payload.get("secondary_evidence"), list)
    ):
        story_intake = build_story_evidence_intake(payload)
        story_meta = dict(story_intake.get("story", {})) if isinstance(story_intake.get("story"), dict) else {}
        raw_rows = [row for row in story_intake.get("evidence_inputs", []) if isinstance(row, dict)]
    elif isinstance(payload, dict):
        story_meta = dict(payload.get("story", {})) if isinstance(payload.get("story"), dict) else {}
        raw_rows = [row for row in payload.get("evidence_inputs", []) if isinstance(row, dict)]
    elif isinstance(payload, list):
        raw_rows = [row for row in payload if isinstance(row, dict)]

    evidence_inputs: list[dict[str, Any]] = []
    source_refs: list[str] = []
    story_id = str(story_meta.get("id", "") or "").strip()
    story_title = str(story_meta.get("title", "") or "").strip()

    for index, raw_row in enumerate(raw_rows, start=1):
        provenance = dict(raw_row.get("provenance", {})) if isinstance(raw_row.get("provenance"), dict) else {}
        source_row_refs = _normalize_string_list([
            *_normalize_string_list(raw_row.get("source_refs")),
            raw_row.get("source_name"),
        ])
        source_refs.extend(source_row_refs)
        cross_validation = (
            dict(raw_row.get("cross_validation", {}))
            if isinstance(raw_row.get("cross_validation"), dict)
            else {}
        )
        evidence_id = _normalize_optional_string(raw_row.get("evidence_id")) or f"evidence-{index}"
        item_id = _normalize_optional_string(raw_row.get("item_id"))
        url = _normalize_optional_string(raw_row.get("url"))
        role = _normalize_optional_string(raw_row.get("role")).strip().lower() or "secondary"
        cross_validated = bool(raw_row.get("cross_validated")) or bool(cross_validation.get("is_cross_validated"))
        search_sources = _normalize_string_list(raw_row.get("search_sources"))
        search_source_count = _coerce_int(raw_row.get("search_source_count"), default=len(search_sources))
        if search_source_count <= 0 and search_sources:
            search_source_count = len(search_sources)
        stitched = bool(raw_row.get("stitched")) or len(source_row_refs) >= 2 or search_source_count >= 2 or cross_validated

        if not story_id:
            story_id = _normalize_optional_string(raw_row.get("story_id"))
        if not story_title:
            story_title = _normalize_optional_string(raw_row.get("story_title"))

        evidence_inputs.append(
            {
                "evidence_id": evidence_id,
                "story_id": _normalize_optional_string(raw_row.get("story_id")) or story_id,
                "story_title": _normalize_optional_string(raw_row.get("story_title")) or story_title,
                "item_id": item_id,
                "title": _normalize_optional_string(raw_row.get("title")),
                "url": url,
                "source_name": _normalize_optional_string(raw_row.get("source_name")),
                "source_type": _normalize_optional_string(raw_row.get("source_type")),
                "role": role,
                "review_state": _normalize_optional_string(raw_row.get("review_state")).strip().lower() or "new",
                "confidence": round(max(0.0, min(1.0, _coerce_float(raw_row.get("confidence"), default=0.0))), 4),
                "evidence_grade": _normalize_optional_string(raw_row.get("evidence_grade")).strip().lower() or "working",
                "evidence_score": round(max(0.0, _coerce_float(raw_row.get("evidence_score"), default=0.0)), 4),
                "grounded_claim_count": _coerce_int(raw_row.get("grounded_claim_count"), default=0),
                "source_refs": source_row_refs,
                "source_ref_count": len(source_row_refs),
                "search_query": _normalize_optional_string(raw_row.get("search_query")),
                "search_provider": _normalize_optional_string(raw_row.get("search_provider")),
                "search_mode": _normalize_optional_string(raw_row.get("search_mode")),
                "search_sources": search_sources,
                "search_source_count": search_source_count,
                "search_source_diversity": round(
                    max(0.0, min(1.0, _coerce_float(raw_row.get("search_source_diversity"), default=0.0))),
                    4,
                ),
                "cross_validation": cross_validation,
                "cross_validated": cross_validated,
                "stitched": stitched,
                "provenance": provenance,
            }
        )

    source_item_ids = _normalize_id_sequence([row.get("item_id") for row in evidence_inputs])
    source_urls = _normalize_string_list([row.get("url") for row in evidence_inputs])
    stitched_source_refs = _normalize_string_list(source_refs)
    evidence_status = "bound" if source_item_ids else "partial" if source_urls else "missing"

    return {
        "story": {
            "id": story_id,
            "title": story_title,
        },
        "summary": {
            "evidence_count": len(evidence_inputs),
            "primary_evidence_count": sum(1 for row in evidence_inputs if row.get("role") == "primary"),
            "secondary_evidence_count": sum(1 for row in evidence_inputs if row.get("role") == "secondary"),
            "source_item_count": len(source_item_ids),
            "source_url_count": len(source_urls),
            "source_ref_count": len(stitched_source_refs),
            "stitched_evidence_count": sum(1 for row in evidence_inputs if row.get("stitched")),
            "cross_validated_evidence_count": sum(1 for row in evidence_inputs if row.get("cross_validated")),
        },
        "evidence_status": evidence_status,
        "source_item_ids": source_item_ids,
        "source_urls": source_urls,
        "source_refs": stitched_source_refs,
        "evidence_inputs": evidence_inputs,
    }


def _build_citation_bundle_candidate(
    rows: list[dict[str, Any]],
    *,
    label: str,
    candidate_kind: str,
    story_meta: dict[str, Any],
    claim_card_id: str = "",
    evidence_status: str = "missing",
) -> dict[str, Any]:
    source_item_ids = _normalize_id_sequence([row.get("item_id") for row in rows])
    source_urls = _normalize_string_list([row.get("url") for row in rows])
    source_refs = _normalize_string_list(
        [source_ref for row in rows for source_ref in row.get("source_refs", []) if str(source_ref or "").strip()]
    )
    story_id = _normalize_optional_string(story_meta.get("id"))
    story_title = _normalize_optional_string(story_meta.get("title"))
    evidence_summaries = [
        {
            "evidence_id": _normalize_optional_string(row.get("evidence_id")),
            "item_id": _normalize_optional_string(row.get("item_id")),
            "url": _normalize_optional_string(row.get("url")),
            "source_name": _normalize_optional_string(row.get("source_name")),
            "role": _normalize_optional_string(row.get("role")).strip().lower() or "secondary",
            "stitched": bool(row.get("stitched")),
            "cross_validated": bool(row.get("cross_validated")),
        }
        for row in rows
    ]
    return {
        "label": label,
        "claim_card_id": _normalize_optional_string(claim_card_id),
        "source_item_ids": source_item_ids,
        "source_urls": source_urls,
        "note": (
            f"Prepared from story `{story_title or story_id or 'untitled-story'}` "
            f"with {len(rows)} evidence row(s) across {len(source_refs)} stitched source ref(s)."
        ),
        "governance": {
            "candidate_kind": candidate_kind,
            "evidence_status": evidence_status,
            "story_id": story_id,
            "story_title": story_title,
            "source_refs": source_refs,
            "source_ref_count": len(source_refs),
            "stitched_evidence_count": sum(1 for row in rows if row.get("stitched")),
            "cross_validated_evidence_count": sum(1 for row in rows if row.get("cross_validated")),
            "evidence_inputs": evidence_summaries,
        },
    }


def build_citation_bundle_candidates_from_story(
    story_payload: dict[str, Any],
    *,
    claim_card_id: str = "",
) -> list[dict[str, Any]]:
    intake = normalize_report_evidence_intake(story_payload)
    rows = intake.get("evidence_inputs", [])
    if not isinstance(rows, list) or not rows:
        return []
    story_meta = intake.get("story", {}) if isinstance(intake.get("story"), dict) else {}
    story_title = _normalize_optional_string(story_meta.get("title")) or "story"
    evidence_status = _normalize_optional_string(intake.get("evidence_status")) or "missing"
    primary_rows = [row for row in rows if isinstance(row, dict) and row.get("role") == "primary"]

    candidates: list[dict[str, Any]] = []
    if primary_rows:
        candidates.append(
            _build_citation_bundle_candidate(
                primary_rows,
                label=f"{story_title} primary evidence",
                candidate_kind="story_primary_evidence_bundle",
                story_meta=story_meta,
                claim_card_id=claim_card_id,
                evidence_status=evidence_status,
            )
        )
    if len(rows) > len(primary_rows):
        candidates.append(
            _build_citation_bundle_candidate(
                rows,
                label=f"{story_title} stitched evidence",
                candidate_kind="story_stitched_evidence_bundle",
                story_meta=story_meta,
                claim_card_id=claim_card_id,
                evidence_status=evidence_status,
            )
        )
    if not candidates:
        candidates.append(
            _build_citation_bundle_candidate(
                rows,
                label=f"{story_title} evidence",
                candidate_kind="story_evidence_bundle",
                story_meta=story_meta,
                claim_card_id=claim_card_id,
                evidence_status=evidence_status,
            )
        )
    return candidates


def build_report_intake_from_story(
    story_payload: dict[str, Any],
    *,
    claim_card_id: str = "",
) -> dict[str, Any]:
    intake = normalize_report_evidence_intake(story_payload)
    intake["citation_bundle_candidates"] = build_citation_bundle_candidates_from_story(
        story_payload,
        claim_card_id=claim_card_id,
    )
    return intake


def _research_source_plan_summary(
    *,
    provider_hints: list[str],
    sites: list[str],
    time_range: str,
    stitched_evidence_count: int,
) -> str:
    parts: list[str] = []
    if provider_hints:
        parts.append(f"keep provider coverage on {', '.join(provider_hints[:3])}")
    if sites:
        parts.append(f"maintain site coverage across {', '.join(sites[:3])}")
    if time_range:
        parts.append(f"hold a {time_range} freshness window")
    if stitched_evidence_count > 0:
        parts.append(f"preserve {stitched_evidence_count} stitched evidence path(s)")
    if not parts:
        return "Continue bounded evidence collection before drafting final claims."
    return "Research should " + "; ".join(parts) + "."


def build_story_research_projection(story_payload: dict[str, Any]) -> dict[str, Any]:
    intake = build_report_intake_from_story(story_payload)
    summary = _as_dict(intake.get("summary"))
    evidence_rows = intake.get("evidence_inputs", []) if isinstance(intake.get("evidence_inputs"), list) else []
    governance = _as_dict(story_payload.get("governance"))
    factuality = _as_dict(governance.get("factuality"))
    delivery_risk = _as_dict(governance.get("delivery_risk"))
    contradictions = story_payload.get("contradictions") if isinstance(story_payload.get("contradictions"), list) else []

    provider_hints = _normalize_string_list(
        [
            row.get("search_provider")
            for row in evidence_rows
            if isinstance(row, dict) and str(row.get("search_provider", "") or "").strip()
        ]
        + [
            source
            for row in evidence_rows
            if isinstance(row, dict)
            for source in _normalize_string_list(row.get("search_sources"))
        ]
    )
    sites = _normalize_string_list(
        [
            urlparse(str(url or "").strip()).netloc.lower()
            for url in intake.get("source_urls", [])
            if str(url or "").strip()
        ]
    )
    source_plan = {
        "summary": _research_source_plan_summary(
            provider_hints=provider_hints,
            sites=sites,
            time_range="",
            stitched_evidence_count=int(summary.get("stitched_evidence_count", 0) or 0),
        ),
        "provider_hints": provider_hints,
        "platforms": [],
        "sites": sites,
        "time_range": "",
        "deep": bool(int(summary.get("stitched_evidence_count", 0) or 0) > 0),
        "news": False,
    }

    reasons: list[str] = []
    evidence_status = _normalize_optional_string(intake.get("evidence_status")).strip().lower() or "missing"
    if evidence_status == "missing":
        reasons.append("No bound evidence rows are attached to this story yet.")
    elif evidence_status == "partial":
        reasons.append("Story evidence is only partially bound to persisted items.")
    if int(summary.get("source_ref_count", 0) or 0) < 2:
        reasons.append("Story evidence does not yet show multi-source stitching.")
    if int(summary.get("cross_validated_evidence_count", 0) or 0) <= 0:
        reasons.append("No story evidence row is marked cross-validated.")
    if contradictions:
        reasons.append("Story contradictions remain unresolved and should be reviewed before claim drafting.")
    factuality_status = _normalize_optional_string(factuality.get("status")).strip().lower()
    if factuality_status in {"review_required", "blocked"}:
        reasons.append("Factuality review is not yet ready for downstream delivery.")
    delivery_status = _normalize_optional_string(delivery_risk.get("status")).strip().lower()
    if delivery_status in {"review_required", "blocked"}:
        reasons.append("Delivery readiness is constrained by current story governance.")

    coverage_status = "clear"
    if evidence_status == "missing" or factuality_status == "blocked" or delivery_status == "blocked":
        coverage_status = "blocked"
    elif evidence_status == "partial" or contradictions or factuality_status == "review_required" or delivery_status == "review_required":
        coverage_status = "review_required"
    elif reasons:
        coverage_status = "watch"

    operator_action = "continue_claim_prep"
    if coverage_status == "blocked":
        operator_action = "add_bound_evidence_before_claims"
    elif coverage_status == "review_required":
        operator_action = "review_story_evidence"
    elif coverage_status == "watch":
        operator_action = "monitor_source_diversity"

    coverage_gap = {
        "status": coverage_status,
        "summary": (
            "Story evidence coverage is ready for claim drafting."
            if not reasons
            else f"Story evidence coverage has {len(reasons)} review signal(s) before claim drafting."
        ),
        "reasons": reasons,
        "operator_action": operator_action,
    }
    return {
        "source_plan": source_plan,
        "coverage_gap": coverage_gap,
    }


def _claim_governance_with_intake(existing: Any, intake: dict[str, Any]) -> dict[str, Any]:
    governance = dict(existing or {}) if isinstance(existing, dict) else {}
    summary = intake.get("summary", {}) if isinstance(intake.get("summary"), dict) else {}
    story_meta = intake.get("story", {}) if isinstance(intake.get("story"), dict) else {}
    current_evidence_intake = (
        dict(governance.get("evidence_intake", {}))
        if isinstance(governance.get("evidence_intake"), dict)
        else {}
    )
    governance["evidence_status"] = _normalize_optional_string(governance.get("evidence_status")) or str(
        intake.get("evidence_status", "missing") or "missing"
    )
    governance["evidence_intake"] = {
        **current_evidence_intake,
        "story_id": _normalize_optional_string(story_meta.get("id")),
        "story_title": _normalize_optional_string(story_meta.get("title")),
        "evidence_count": int(summary.get("evidence_count", 0) or 0),
        "source_ref_count": len(_normalize_string_list(intake.get("source_refs"))),
        "source_refs": _normalize_string_list(intake.get("source_refs")),
        "stitched_evidence_count": int(summary.get("stitched_evidence_count", 0) or 0),
        "cross_validated_evidence_count": int(summary.get("cross_validated_evidence_count", 0) or 0),
        "source_url_count": len(_normalize_string_list(intake.get("source_urls"))),
    }
    return governance


def _bundle_governance_with_intake(existing: Any, intake: dict[str, Any]) -> dict[str, Any]:
    governance = dict(existing or {}) if isinstance(existing, dict) else {}
    summary = intake.get("summary", {}) if isinstance(intake.get("summary"), dict) else {}
    story_meta = intake.get("story", {}) if isinstance(intake.get("story"), dict) else {}
    current_evidence_intake = (
        dict(governance.get("evidence_intake", {}))
        if isinstance(governance.get("evidence_intake"), dict)
        else {}
    )
    governance["evidence_status"] = _normalize_optional_string(governance.get("evidence_status")) or str(
        intake.get("evidence_status", "missing") or "missing"
    )
    governance["evidence_intake"] = {
        **current_evidence_intake,
        "story_id": _normalize_optional_string(story_meta.get("id")),
        "story_title": _normalize_optional_string(story_meta.get("title")),
        "evidence_count": int(summary.get("evidence_count", 0) or 0),
        "source_ref_count": len(_normalize_string_list(intake.get("source_refs"))),
        "source_refs": _normalize_string_list(intake.get("source_refs")),
        "stitched_evidence_count": int(summary.get("stitched_evidence_count", 0) or 0),
        "cross_validated_evidence_count": int(summary.get("cross_validated_evidence_count", 0) or 0),
        "source_url_count": len(_normalize_string_list(intake.get("source_urls"))),
    }
    return governance


def _prepare_claim_card_payload(payload: dict[str, Any]) -> dict[str, Any]:
    prepared = dict(payload)
    intake_payload = prepared.get("evidence_intake", prepared.get("evidence_inputs"))
    if intake_payload is None:
        prepared.pop("evidence_inputs", None)
        return prepared
    intake = normalize_report_evidence_intake(intake_payload)
    prepared["source_item_ids"] = _normalize_id_sequence(
        [*prepared.get("source_item_ids", []), *intake.get("source_item_ids", [])]
    )
    prepared["governance"] = _claim_governance_with_intake(prepared.get("governance"), intake)
    prepared.pop("evidence_inputs", None)
    prepared.pop("evidence_intake", None)
    return prepared


def _prepare_citation_bundle_payload(payload: dict[str, Any]) -> dict[str, Any]:
    prepared = dict(payload)
    intake_payload = prepared.get("evidence_intake", prepared.get("evidence_inputs"))
    if intake_payload is None:
        prepared.pop("evidence_inputs", None)
        return prepared
    intake = normalize_report_evidence_intake(intake_payload)
    prepared["source_item_ids"] = _normalize_id_sequence(
        [*prepared.get("source_item_ids", []), *intake.get("source_item_ids", [])]
    )
    prepared["source_urls"] = _normalize_string_list([*prepared.get("source_urls", []), *intake.get("source_urls", [])])
    prepared["governance"] = _bundle_governance_with_intake(prepared.get("governance"), intake)
    if not _normalize_optional_string(prepared.get("label")):
        story_title = _normalize_optional_string(intake.get("story", {}).get("title") if isinstance(intake.get("story"), dict) else "")
        if story_title:
            prepared["label"] = f"{story_title} evidence"
    prepared.pop("evidence_inputs", None)
    prepared.pop("evidence_intake", None)
    return prepared


def build_claim_draft_from_story(
    story_payload: dict[str, Any],
    *,
    brief_id: str = "",
    mode: str = "assist",
) -> dict[str, Any]:
    story_id = _normalize_optional_string(story_payload.get("id"))
    story_title = _normalize_optional_string(story_payload.get("title"))
    story_summary = _normalize_optional_string(story_payload.get("summary"))
    semantic_review = _as_dict(story_payload.get("semantic_review"))
    claim_candidates_raw = semantic_review.get("claim_candidates")
    claim_candidates: list[str] = []
    if isinstance(claim_candidates_raw, list):
        claim_candidates = _normalize_string_list(claim_candidates_raw)
    if not claim_candidates:
        for field in (story_summary, story_title):
            text = _normalize_optional_string(field)
            if text and text not in claim_candidates:
                claim_candidates.append(text)
            if claim_candidates:
                break

    evidence_intake = build_report_intake_from_story(story_payload)
    evidence_rows = evidence_intake.get("evidence_inputs", []) if isinstance(evidence_intake.get("evidence_inputs"), list) else []
    source_item_ids = _normalize_id_sequence(evidence_intake.get("source_item_ids"))
    source_urls = _normalize_string_list(evidence_intake.get("source_urls"))
    source_refs = _normalize_string_list(evidence_intake.get("source_refs"))
    contradictions_raw = story_payload.get("contradictions")
    contradictions: list[dict[str, Any]] = []
    if isinstance(contradictions_raw, list):
        for raw_row in contradictions_raw:
            if not isinstance(raw_row, dict):
                continue
            topic = _normalize_optional_string(raw_row.get("topic")) or "story_conflict"
            severity = "error" if int(raw_row.get("negative", 0) or 0) > 0 else "warning"
            note = _normalize_optional_string(raw_row.get("note")) or (
                f"Conflicting evidence remains on `{topic}` across the story evidence set."
            )
            contradictions.append({
                "topic": topic,
                "severity": severity,
                "note": note,
            })

    governance = _as_dict(story_payload.get("governance"))
    factuality = _as_dict(governance.get("factuality"))
    delivery_risk = _as_dict(governance.get("delivery_risk"))
    unresolved_flags: list[str] = []
    evidence_status = _normalize_optional_string(evidence_intake.get("evidence_status")).strip().lower() or "missing"
    if evidence_status not in {"bound", "partial", "missing"}:
        evidence_status = "bound" if source_item_ids else "partial" if source_urls else "missing"
    if evidence_status == "missing":
        unresolved_flags.append("missing_evidence_binding")
    if contradictions:
        unresolved_flags.append("story_contradictions_present")
    if str(factuality.get("status", "") or "").strip().lower() not in {"", "ready"}:
        unresolved_flags.append("factuality_review_required")
    if str(delivery_risk.get("status", "") or "").strip().lower() == "review_required":
        unresolved_flags.append("delivery_review_required")

    confidence = round(max(0.0, min(1.0, _coerce_float(story_payload.get("confidence"), default=0.0))), 4)
    if confidence <= 0.0:
        confidence = 0.55 if source_item_ids else 0.35
    if contradictions:
        confidence = min(confidence, 0.6)

    normalized_mode = str(mode or "assist").strip().lower() or "assist"
    default_status = "review" if normalized_mode == "review" or unresolved_flags else "draft"
    summary = (
        f"Claim draft prepared from story `{story_title or story_id or 'untitled-story'}` "
        f"using {len(source_item_ids)} bound evidence items."
    )

    claim_cards: list[dict[str, Any]] = []
    for statement in claim_candidates[:3]:
        text = _normalize_optional_string(statement)
        if not text:
            continue
        claim_cards.append(
            {
                "statement": text,
                "brief_id": brief_id,
                "rationale": (
                    f"Draft synthesized from story `{story_title or story_id or 'untitled-story'}` "
                    f"with {len(evidence_rows)} evidence rows."
                ),
                "confidence": confidence,
                "status": default_status,
                "source_item_ids": list(source_item_ids),
                "tags": _normalize_string_list(story_payload.get("entities"))[:5],
                "governance": {
                    "evidence_status": evidence_status,
                    "contradictions": contradictions,
                    "unresolved_flags": _normalize_string_list(unresolved_flags),
                    "evidence_intake": {
                        "story_id": _normalize_optional_string(evidence_intake.get("story", {}).get("id") if isinstance(evidence_intake.get("story"), dict) else ""),
                        "story_title": _normalize_optional_string(evidence_intake.get("story", {}).get("title") if isinstance(evidence_intake.get("story"), dict) else ""),
                        "evidence_count": int(evidence_intake.get("summary", {}).get("evidence_count", len(evidence_rows)) if isinstance(evidence_intake.get("summary"), dict) else len(evidence_rows)),
                        "source_ref_count": len(source_refs),
                        "source_refs": source_refs,
                        "stitched_evidence_count": int(evidence_intake.get("summary", {}).get("stitched_evidence_count", 0) if isinstance(evidence_intake.get("summary"), dict) else 0),
                        "cross_validated_evidence_count": int(evidence_intake.get("summary", {}).get("cross_validated_evidence_count", 0) if isinstance(evidence_intake.get("summary"), dict) else 0),
                        "citation_candidate_count": len(evidence_intake.get("citation_bundle_candidates", [])) if isinstance(evidence_intake.get("citation_bundle_candidates"), list) else 0,
                        "source_url_count": len(source_urls),
                    },
                },
            }
        )

    return {
        "summary": summary,
        "claim_cards": claim_cards,
        "evidence_intake": evidence_intake,
        "citation_bundle_candidates": evidence_intake.get("citation_bundle_candidates", []),
        "research_projection": build_story_research_projection(story_payload),
    }


def validate_claim_draft_payload(payload: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(payload, dict):
        return ["payload must be an object"]
    if not str(payload.get("summary", "") or "").strip():
        errors.append("summary is required")
    claim_cards = payload.get("claim_cards")
    if not isinstance(claim_cards, list) or not claim_cards:
        errors.append("claim_cards must contain at least one entry")
        claim_cards = []
    for index, claim in enumerate(claim_cards, start=1):
        if not isinstance(claim, dict):
            errors.append(f"claim_cards[{index}] must be an object")
            continue
        if not str(claim.get("statement", "") or "").strip():
            errors.append(f"claim_cards[{index}].statement is required")
        try:
            confidence = float(claim.get("confidence", 0.0) or 0.0)
        except Exception:
            errors.append(f"claim_cards[{index}].confidence must be numeric")
            confidence = 0.0
        if confidence < 0.0 or confidence > 1.0:
            errors.append(f"claim_cards[{index}].confidence must be between 0 and 1")
        if str(claim.get("status", "") or "").strip().lower() not in {"draft", "review"}:
            errors.append(f"claim_cards[{index}].status must be draft/review")
        source_item_ids = claim.get("source_item_ids")
        if not isinstance(source_item_ids, list) or not any(str(item or "").strip() for item in source_item_ids):
            errors.append(f"claim_cards[{index}].source_item_ids must contain at least one entry")
        governance = claim.get("governance")
        if not isinstance(governance, dict):
            errors.append(f"claim_cards[{index}].governance is required")
            continue
        if str(governance.get("evidence_status", "") or "").strip().lower() not in {"bound", "partial", "missing"}:
            errors.append(f"claim_cards[{index}].governance.evidence_status is invalid")
        contradictions = governance.get("contradictions")
        if not isinstance(contradictions, list):
            errors.append(f"claim_cards[{index}].governance.contradictions must be a list")
            continue
        for contradiction_index, contradiction in enumerate(contradictions, start=1):
            if not isinstance(contradiction, dict):
                errors.append(
                    f"claim_cards[{index}].governance.contradictions[{contradiction_index}] must be an object"
                )
                continue
            if not str(contradiction.get("topic", "") or "").strip():
                errors.append(
                    f"claim_cards[{index}].governance.contradictions[{contradiction_index}].topic is required"
                )
            if str(contradiction.get("severity", "") or "").strip().lower() not in {"warning", "error"}:
                errors.append(
                    f"claim_cards[{index}].governance.contradictions[{contradiction_index}].severity is invalid"
                )
            if not str(contradiction.get("note", "") or "").strip():
                errors.append(
                    f"claim_cards[{index}].governance.contradictions[{contradiction_index}].note is required"
                )
    evidence_intake = payload.get("evidence_intake")
    if evidence_intake is not None:
        if not isinstance(evidence_intake, dict):
            errors.append("evidence_intake must be an object when present")
        else:
            intake_summary = evidence_intake.get("summary")
            if not isinstance(intake_summary, dict):
                errors.append("evidence_intake.summary must be an object when present")
    citation_bundle_candidates = payload.get("citation_bundle_candidates")
    if citation_bundle_candidates is not None:
        if not isinstance(citation_bundle_candidates, list):
            errors.append("citation_bundle_candidates must be a list when present")
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
        if isinstance(payload, dict):
            payload = _prepare_claim_card_payload(payload)
        return self._create(payload, ClaimCard.from_dict, ClaimCard, self.claim_cards, id_prefix="claim-card")

    def list_claim_cards(self, *, limit: int = 20, status: str | None = None) -> list[ClaimCard]:
        return self._list_records(self.claim_cards, limit=limit, status=status)

    def get_claim_card(self, identifier: str) -> ClaimCard | None:
        return self._lookup(self.claim_cards, identifier)

    def update_claim_card(self, identifier: str, **payload: Any) -> ClaimCard | None:
        prepared_payload = _prepare_claim_card_payload(payload) if isinstance(payload, dict) else dict(payload)
        updates = {
            "statement": prepared_payload.get("statement"),
            "rationale": prepared_payload.get("rationale"),
            "status": prepared_payload.get("status"),
            "citation_bundle_ids": prepared_payload.get("citation_bundle_ids"),
            "source_item_ids": prepared_payload.get("source_item_ids"),
            "tags": prepared_payload.get("tags"),
            "brief_id": prepared_payload.get("brief_id"),
        }
        claim = self._update_generic(identifier, self.claim_cards, updates=updates)
        if claim is None:
            return None
        if "governance" in prepared_payload:
            claim.governance = dict(prepared_payload.get("governance") or {})
            self._touch(claim)
            self.save()
        if "confidence" in prepared_payload:
            claim.confidence = round(max(0.0, min(1.0, _coerce_float(prepared_payload.get("confidence"), default=claim.confidence))), 4)
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
        if isinstance(payload, dict):
            payload = _prepare_citation_bundle_payload(payload)
        return self._create(payload, CitationBundle.from_dict, CitationBundle, self.citation_bundles, id_prefix="citation-bundle")

    def list_citation_bundles(self, *, limit: int = 20) -> list[CitationBundle]:
        return self._list_records(self.citation_bundles, limit=limit, status=None)

    def get_citation_bundle(self, identifier: str) -> CitationBundle | None:
        return self._lookup(self.citation_bundles, identifier)

    def update_citation_bundle(self, identifier: str, **payload: Any) -> CitationBundle | None:
        prepared_payload = _prepare_citation_bundle_payload(payload) if isinstance(payload, dict) else dict(payload)
        updates = {
            "label": prepared_payload.get("label"),
            "claim_card_id": prepared_payload.get("claim_card_id"),
            "note": prepared_payload.get("note"),
            "source_item_ids": prepared_payload.get("source_item_ids"),
            "source_urls": prepared_payload.get("source_urls"),
        }
        bundle = self._update_generic(identifier, self.citation_bundles, updates=updates)
        if bundle is not None and "governance" in prepared_payload:
            bundle.governance = dict(prepared_payload.get("governance") or {})
            self._touch(bundle)
            self.save()
        return bundle

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


class ReportService:
    """Report and delivery lifecycle service behind the DataPulseReader facade."""

    def __init__(self, owner: Any, *, report_store: ReportStore):
        self.owner = owner
        self.report_store = report_store

    def list_report_briefs(self, *, limit: int = 20, status: str | None = None) -> list[dict[str, Any]]:
        return [brief.to_dict() for brief in self.report_store.list_report_briefs(limit=limit, status=status)]

    def create_report_brief(self, **payload: Any) -> dict[str, Any]:
        return self.report_store.create_report_brief(payload).to_dict()

    def show_report_brief(self, identifier: str) -> dict[str, Any] | None:
        brief = self.report_store.get_report_brief(identifier)
        return brief.to_dict() if brief is not None else None

    def update_report_brief(self, identifier: str, **payload: Any) -> dict[str, Any] | None:
        brief = self.report_store.update_report_brief(identifier, **payload)
        return brief.to_dict() if brief is not None else None

    def list_claim_cards(self, *, limit: int = 20, status: str | None = None) -> list[dict[str, Any]]:
        return [claim.to_dict() for claim in self.report_store.list_claim_cards(limit=limit, status=status)]

    def create_claim_card(self, **payload: Any) -> dict[str, Any]:
        return self.report_store.create_claim_card(payload).to_dict()

    def show_claim_card(self, identifier: str) -> dict[str, Any] | None:
        claim = self.report_store.get_claim_card(identifier)
        return claim.to_dict() if claim is not None else None

    def update_claim_card(self, identifier: str, **payload: Any) -> dict[str, Any] | None:
        claim = self.report_store.update_claim_card(identifier, **payload)
        return claim.to_dict() if claim is not None else None

    def list_report_sections(self, *, limit: int = 20, status: str | None = None) -> list[dict[str, Any]]:
        return [section.to_dict() for section in self.report_store.list_report_sections(limit=limit, status=status)]

    def create_report_section(self, **payload: Any) -> dict[str, Any]:
        return self.report_store.create_report_section(payload).to_dict()

    def show_report_section(self, identifier: str) -> dict[str, Any] | None:
        section = self.report_store.get_report_section(identifier)
        return section.to_dict() if section is not None else None

    def update_report_section(self, identifier: str, **payload: Any) -> dict[str, Any] | None:
        section = self.report_store.update_report_section(identifier, **payload)
        return section.to_dict() if section is not None else None

    def list_citation_bundles(self, *, limit: int = 20) -> list[dict[str, Any]]:
        return [bundle.to_dict() for bundle in self.report_store.list_citation_bundles(limit=limit)]

    def create_citation_bundle(self, **payload: Any) -> dict[str, Any]:
        return self.report_store.create_citation_bundle(payload).to_dict()

    def show_citation_bundle(self, identifier: str) -> dict[str, Any] | None:
        bundle = self.report_store.get_citation_bundle(identifier)
        return bundle.to_dict() if bundle is not None else None

    def update_citation_bundle(self, identifier: str, **payload: Any) -> dict[str, Any] | None:
        bundle = self.report_store.update_citation_bundle(identifier, **payload)
        return bundle.to_dict() if bundle is not None else None

    def list_reports(self, *, limit: int = 20, status: str | None = None) -> list[dict[str, Any]]:
        return [report.to_dict() for report in self.report_store.list_reports(limit=limit, status=status)]

    def create_report(self, **payload: Any) -> dict[str, Any]:
        return self.report_store.create_report(payload).to_dict()

    @staticmethod
    def _resolve_report_compose_setting(value: bool | None, profile_value: bool | None, default: bool) -> bool:
        if value is not None:
            return bool(value)
        if profile_value is not None:
            return bool(profile_value)
        return default

    def assemble_report(
        self,
        identifier: str,
        *,
        include_sections: bool = True,
        include_claim_cards: bool = True,
        include_citation_bundles: bool = True,
        include_export_profiles: bool = True,
    ) -> dict[str, Any] | None:
        return self.report_store.assemble_report(
            identifier,
            include_sections=include_sections,
            include_claim_cards=include_claim_cards,
            include_citation_bundles=include_citation_bundles,
            include_export_profiles=include_export_profiles,
        )

    def show_report(self, identifier: str) -> dict[str, Any] | None:
        report = self.report_store.get_report(identifier)
        return report.to_dict() if report is not None else None

    def compose_report(
        self,
        identifier: str,
        *,
        profile_id: str | None = None,
        include_sections: bool | None = None,
        include_claim_cards: bool | None = None,
        include_citation_bundles: bool | None = None,
        include_export_profiles: bool | None = None,
    ) -> dict[str, Any] | None:
        profile_payload: dict[str, Any] | None = None
        if profile_id:
            profile_payload = self.show_export_profile(profile_id)
            if profile_payload is None:
                raise ValueError(f"Export profile not found: {profile_id}")

        include_sections = self._resolve_report_compose_setting(
            include_sections,
            profile_payload.get("include_sections") if profile_payload else None,
            True,
        )
        include_claim_cards = self._resolve_report_compose_setting(
            include_claim_cards,
            profile_payload.get("include_claim_cards") if profile_payload else None,
            True,
        )
        include_citation_bundles = self._resolve_report_compose_setting(
            include_citation_bundles,
            profile_payload.get("include_bundles") if profile_payload else None,
            True,
        )
        include_export_profiles = self._resolve_report_compose_setting(
            include_export_profiles,
            (profile_payload or {}).get("include_export_profiles"),
            True,
        )
        payload = self.report_store.assemble_report(
            identifier,
            include_sections=include_sections,
            include_claim_cards=include_claim_cards,
            include_citation_bundles=include_citation_bundles,
            include_export_profiles=include_export_profiles,
        )
        if payload is None:
            return None

        if profile_payload and str(profile_payload.get("name", "")).strip().lower() == "watch-pack":
            payload["watch_pack"] = self._build_report_watch_pack_payload(identifier, payload)
        return payload

    @staticmethod
    def _normalize_report_id(identifier: str) -> str:
        return str(identifier or "").strip()

    @staticmethod
    def _normalize_profile_name(name: str | None) -> str:
        return str(name or "").strip().lower()

    def _find_report_profile(self, identifier: str, *, name: str) -> dict[str, Any] | None:
        normalized_name = self._normalize_profile_name(name)
        if not normalized_name:
            return None
        for row in self.list_export_profiles(report_id=identifier, limit=100):
            if self._normalize_profile_name(row.get("name")) == normalized_name:
                return row
        return None

    def _build_report_watch_pack_payload(
        self,
        identifier: str,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        report_payload = payload.get("report", {}) if isinstance(payload.get("report"), dict) else {}
        sections = payload.get("sections", [])
        claim_cards = payload.get("claim_cards", [])
        bundles = payload.get("citation_bundles", [])
        section_titles = [str(row.get("title", "")).strip() for row in sections if str(row.get("title", "")).strip()]
        claim_stmts = [str(row.get("statement", "")).strip() for row in claim_cards if str(row.get("statement", "")).strip()]
        bundle_entries = [row for row in bundles if isinstance(row, dict)]
        source_urls: list[str] = []
        for row in bundle_entries:
            source_urls.extend([str(url).strip() for url in row.get("source_urls", []) if str(url).strip()])
        source_urls = [url for i, url in enumerate(source_urls) if url and url not in source_urls[:i]]

        demand_intent = str(report_payload.get("summary", "") or "").strip()
        if not demand_intent:
            demand_intent = section_titles[0] if section_titles else (claim_stmts[0] if claim_stmts else "")
        if not demand_intent:
            demand_intent = f"Track follow-up evidence for {report_payload.get('title', '')}".strip() or "Track follow-up evidence."

        key_questions = [f"What changed in the {topic.lower()} area?" for topic in section_titles[:3]]
        if not key_questions and claim_stmts:
            key_questions = [f"What evidence supports: {statement[:100]}" for statement in claim_stmts[:3]]
        if not key_questions:
            key_questions = [
                "What changed since this report?",
                "What new evidence should trigger follow-up actions?",
            ]

        return {
            "report_id": self._normalize_report_id(identifier),
            "report_title": str(report_payload.get("title", "")).strip(),
            "query": str(report_payload.get("title", "")).strip() or f"watch-report-{identifier}",
            "mission_name": f"{report_payload.get('title', 'Report').strip()} Follow-up Watch".strip(),
            "mission_intent": {
                "demand_intent": demand_intent,
                "key_questions": key_questions[:3],
                "scope_topics": section_titles[:8],
                "scope_window": "watching",
                "freshness_expectation": "same day review",
                "freshness_max_age_hours": 24,
                "coverage_targets": ["official updates", "source-level evidence"],
            },
            "source_pack": {
                "source_pack_version": "1.0",
                "section_count": len(section_titles),
                "claim_count": len(claim_stmts),
                "bundle_count": len(bundle_entries),
                "key_sections": section_titles[:8],
                "source_urls": source_urls[:12],
                "report_summary": str(report_payload.get("summary", "")).strip() or None,
            },
            "suggested_followup": {
                "output_profile": "watch-pack",
                "source_profile_hint": "full",
                "default_query_prefix": str(report_payload.get("title", "")).strip() or "report follow-up",
            },
        }

    def report_watch_pack(
        self,
        identifier: str,
        *,
        profile_id: str | None = None,
    ) -> dict[str, Any] | None:
        report_payload = self.show_report(identifier)
        if report_payload is None:
            return None
        report_id = self._normalize_report_id(report_payload["id"])
        target_profile_id = profile_id
        if target_profile_id is None:
            target_profile = self._find_report_profile(report_id, name="watch-pack")
            if target_profile is not None:
                target_profile_id = target_profile.get("id")
        payload = self.compose_report(report_id, profile_id=target_profile_id)
        if payload is None:
            return None
        watch_pack = payload.get("watch_pack")
        if isinstance(watch_pack, dict):
            return watch_pack
        return self._build_report_watch_pack_payload(report_id, payload)

    def create_watch_from_report_pack(
        self,
        identifier: str,
        *,
        profile_id: str | None = None,
        name: str | None = None,
        query: str | None = None,
        platforms: list[str] | None = None,
        sites: list[str] | None = None,
        schedule: str = "manual",
        min_confidence: float = 0.0,
        top_n: int = 5,
        alert_rules: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any] | None:
        watch_pack = self.report_watch_pack(identifier, profile_id=profile_id)
        if watch_pack is None:
            return None
        mission_name = str(name).strip() if name else str(watch_pack.get("mission_name", "")).strip()
        mission_query = str(query).strip() if query else str(watch_pack.get("query", "")).strip()
        if not mission_name:
            mission_name = f"{self._normalize_report_id(identifier)} Watch"
        if not mission_query:
            mission_query = f"Watch {self._normalize_report_id(identifier)}"
        mission_intent = watch_pack.get("mission_intent")
        if not isinstance(mission_intent, dict):
            mission_intent = {}
        return self.owner.create_watch(
            name=mission_name,
            query=mission_query,
            mission_intent=mission_intent,
            platforms=platforms,
            sites=sites,
            schedule=schedule,
            min_confidence=min_confidence,
            top_n=top_n,
            alert_rules=alert_rules,
        )

    def assess_report_quality(
        self,
        identifier: str,
        *,
        profile_id: str | None = None,
        include_sections: bool | None = None,
        include_claim_cards: bool | None = None,
        include_citation_bundles: bool | None = None,
        include_export_profiles: bool | None = None,
    ) -> dict[str, Any] | None:
        payload = self.compose_report(
            identifier,
            profile_id=profile_id,
            include_sections=include_sections,
            include_claim_cards=include_claim_cards,
            include_citation_bundles=include_citation_bundles,
            include_export_profiles=include_export_profiles,
        )
        if payload is None:
            return None
        quality = payload.get("quality")
        return quality if isinstance(quality, dict) else {}

    def update_report(self, identifier: str, **payload: Any) -> dict[str, Any] | None:
        report = self.report_store.update_report(identifier, **payload)
        return report.to_dict() if report is not None else None

    def list_export_profiles(
        self,
        *,
        limit: int = 20,
        status: str | None = None,
        report_id: str | None = None,
    ) -> list[dict[str, Any]]:
        return [
            profile.to_dict()
            for profile in self.report_store.list_export_profiles(
                limit=limit,
                status=status,
                report_id=report_id,
            )
        ]

    def create_export_profile(self, **payload: Any) -> dict[str, Any]:
        return self.report_store.create_export_profile(payload).to_dict()

    def show_export_profile(self, identifier: str) -> dict[str, Any] | None:
        profile = self.report_store.get_export_profile(identifier)
        return profile.to_dict() if profile is not None else None

    def update_export_profile(self, identifier: str, **payload: Any) -> dict[str, Any] | None:
        profile = self.report_store.update_export_profile(identifier, **payload)
        return profile.to_dict() if profile is not None else None

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
    ) -> list[dict[str, Any]]:
        return [
            row.to_dict()
            for row in self.report_store.list_delivery_subscriptions(
                limit=limit,
                status=status,
                subject_kind=subject_kind,
                subject_ref=subject_ref,
                output_kind=output_kind,
                delivery_mode=delivery_mode,
                route_name=route_name,
            )
        ]

    def create_delivery_subscription(self, **payload: Any) -> dict[str, Any]:
        return self.report_store.create_delivery_subscription(payload).to_dict()

    def show_delivery_subscription(self, identifier: str) -> dict[str, Any] | None:
        subscription = self.report_store.get_delivery_subscription(identifier)
        return subscription.to_dict() if subscription is not None else None

    def update_delivery_subscription(self, identifier: str, **payload: Any) -> dict[str, Any] | None:
        subscription = self.report_store.update_delivery_subscription(identifier, **payload)
        return subscription.to_dict() if subscription is not None else None

    def delete_delivery_subscription(self, identifier: str) -> dict[str, Any] | None:
        subscription = self.report_store.delete_delivery_subscription(identifier)
        return subscription.to_dict() if subscription is not None else None

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
    ) -> list[dict[str, Any]]:
        return [
            record.to_dict()
            for record in self.report_store.list_delivery_dispatch_records(
                limit=limit,
                status=status,
                subscription_id=subscription_id,
                subject_kind=subject_kind,
                subject_ref=subject_ref,
                output_kind=output_kind,
                route_name=route_name,
            )
        ]

    def build_report_delivery_package(
        self,
        subscription_identifier: str,
        *,
        profile_id: str | None = None,
    ) -> dict[str, Any]:
        subscription = self.show_delivery_subscription(subscription_identifier)
        if subscription is None:
            raise ValueError(f"Delivery subscription not found: {subscription_identifier}")
        if str(subscription.get("subject_kind", "")).strip().lower() != "report":
            raise ValueError("Only report subscriptions can be used for report delivery packages")
        profile_payload = self.show_export_profile(profile_id) if profile_id else None
        return self.owner._build_report_delivery_package(subscription, profile_id=profile_id, profile_payload=profile_payload)

    def dispatch_report_delivery(
        self,
        subscription_identifier: str,
        *,
        profile_id: str | None = None,
    ) -> list[dict[str, Any]]:
        subscription = self.show_delivery_subscription(subscription_identifier)
        if subscription is None:
            raise ValueError(f"Delivery subscription not found: {subscription_identifier}")
        if str(subscription.get("subject_kind", "")).strip().lower() != "report":
            raise ValueError("Only report subscriptions can be dispatched by this method")
        output_kind = self.owner._normalize_report_dispatch_output_kind(subscription.get("output_kind"))
        if output_kind not in _DELIVERY_OUTPUT_KINDS:
            raise ValueError(f"Unsupported report delivery output kind: {output_kind}")
        package = self.owner._build_report_delivery_package(subscription, profile_id=profile_id)

        rule: dict[str, Any] = {
            "routes": list(subscription.get("route_names", [])),
        }
        route_targets, route_errors = resolve_delivery_targets(rule)
        target_by_name: dict[str, dict[str, Any]] = {}
        for row in route_targets:
            label = str(row.get("label", "")).strip()
            route_name = self.owner._extract_delivery_route_name(label)
            if route_name:
                target_by_name[route_name] = row

        route_names = _normalize_string_list(subscription.get("route_names"))
        dispatch_records: list[dict[str, Any]] = []
        for route_name in route_names:
            target = target_by_name.get(route_name)
            route_label = str(target.get("label", "") if isinstance(target, dict) else "").strip()
            channel = str(target.get("channel", "")).strip().lower() if isinstance(target, dict) else ""
            error = ""
            governance: dict[str, Any] = {}
            if not route_label:
                route_label = f"route:{route_name}"
            if not target:
                error = str(route_errors.get(f"route:{route_name}") or route_errors.get(route_label) or "")
                status = "missing_route"
                governance = {
                    "delivery_diagnostics": {
                        "route_label": route_label,
                        "route_name": route_name,
                        "channel": channel or "unknown",
                        "attempt_count": 0,
                        "chunk_count": 0,
                        "fallback_used": False,
                        "fallback_reason": "",
                        "attempts": [],
                        "resolution": "missing_route",
                        "error": error,
                    }
                }
            else:
                status = "pending"
            record = self.report_store.create_delivery_dispatch_record(
                {
                    "subscription_id": str(subscription.get("id", "")),
                    "subject_kind": "report",
                    "subject_ref": str(subscription.get("subject_ref", "")),
                    "output_kind": output_kind,
                    "route_name": route_name,
                    "route_label": route_label,
                    "route_channel": channel,
                    "package_id": str(package.get("package_id", "")),
                    "package_signature": str(package.get("package_signature", "")),
                    "package_profile_id": str(profile_id or ""),
                    "status": status,
                    "error": error,
                    "attempts": 0,
                    "governance": governance,
                }
            )
            dispatch_records.append(record.to_dict())

        for row in dispatch_records:
            if row.get("status") != "pending":
                continue
            route_name = str(row.get("route_name", "")).strip()
            target = target_by_name.get(route_name)
            if not isinstance(target, dict):
                continue
            record_id = str(row.get("id", "")).strip()
            diagnostics: dict[str, Any] = {}
            try:
                diagnostics = self.owner._dispatch_route_delivery_payload(
                    target,
                    webhook_payload={"report_delivery": package},
                    text_payload=self.owner._render_report_delivery_text(package),
                    markdown_title=f"Report Delivery | {route_name}",
                    markdown_metadata={
                        "package_id": str(package.get("package_id", "")),
                        "route_label": str(target.get("label", "")),
                        "channel": str(target.get("channel", "")),
                    },
                )
                new_error = ""
                current_status = "delivered"
            except DeliveryDispatchError as exc:
                diagnostics = dict(exc.diagnostics or {})
                new_error = str(exc)
                current_status = "failed"
            except Exception as exc:  # noqa: BLE001
                diagnostics = self.owner._route_delivery_base_diagnostics(target)
                diagnostics["error"] = str(exc)
                diagnostics["attempt_count"] = 1
                diagnostics["attempts"] = [
                    {
                        "kind": "route_dispatch",
                        "status": "failed",
                        "error": str(exc),
                    }
                ]
                new_error = str(exc)
                current_status = "failed"
            current_attempts = int(diagnostics.get("attempt_count", 1 if current_status == "failed" else 0) or 0)
            if current_status == "delivered" and current_attempts <= 0:
                current_attempts = 1
            self.report_store.update_delivery_dispatch_record(
                record_id,
                status=current_status,
                error=new_error,
                attempts=current_attempts,
                route_channel=target.get("channel", ""),
            )
            self.owner._persist_delivery_dispatch_governance(record_id, {"delivery_diagnostics": diagnostics})
            for idx, item in enumerate(dispatch_records):
                if str(item.get("id", "")) == record_id:
                    dispatch_records[idx]["status"] = current_status
                    dispatch_records[idx]["error"] = new_error
                    dispatch_records[idx]["attempts"] = current_attempts
                    dispatch_records[idx]["route_channel"] = str(target.get("channel", ""))
                    dispatch_records[idx]["governance"] = {"delivery_diagnostics": diagnostics}
                    break
        return dispatch_records

    def export_report(
        self,
        identifier: str,
        *,
        profile_id: str | None = None,
        output_format: str = "json",
        include_sections: bool | None = None,
        include_claim_cards: bool | None = None,
        include_citation_bundles: bool | None = None,
        include_metadata: bool | None = None,
    ) -> str | None:
        payload = self.compose_report(
            identifier,
            profile_id=profile_id,
            include_sections=include_sections,
            include_claim_cards=include_claim_cards,
            include_citation_bundles=include_citation_bundles,
        )
        if payload is None:
            return None

        profile_payload: dict[str, Any] | None = self.show_export_profile(profile_id) if profile_id else None
        resolved_format = self.owner._normalize_report_export_format(output_format)
        if resolved_format == "json":
            return json.dumps(payload, ensure_ascii=False, indent=2)

        include_metadata = bool(
            include_metadata
            if include_metadata is not None
            else (profile_payload.get("include_metadata", True) if profile_payload else True)
        )
        return self.owner._render_report_markdown(payload, include_metadata=include_metadata)
