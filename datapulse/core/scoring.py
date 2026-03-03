"""Multi-dimensional scoring engine for DataPulse items."""

import math
import os
from collections import Counter
from datetime import datetime

from .models import DataPulseItem
from .utils import content_fingerprint, get_domain


# Default dimension weights (sum to 1.0; source_diversity is configurable for controlled rollout).
def _env_float(name: str, default: float) -> float:
    raw = os.getenv(name)
    try:
        return float(raw) if raw is not None else default
    except (TypeError, ValueError):
        return default


def _default_weights() -> dict[str, float]:
    return {
        "confidence": 0.25,
        "authority": 0.30,
        "corroboration": 0.25,
        "recency": 0.20,
        "source_diversity": _env_float("DATAPULSE_SOURCE_DIVERSITY_WEIGHT", 0.07),
        "cross_validation": _env_float("DATAPULSE_CROSS_VALIDATION_WEIGHT", 0.06),
        "recency_bonus": _env_float("DATAPULSE_RECENCY_BONUS_WEIGHT", 0.00),
    }


DEFAULT_WEIGHTS = _default_weights()

# Default half-life for recency decay (hours)
_DEFAULT_HALF_LIFE_HOURS = 24.0


def recency_score(fetched_at: str, now: datetime | None = None) -> float:
    """Compute exponential decay recency score.

    Returns 1.0 for brand new, decays with half-life from DATAPULSE_RECENCY_HALF_LIFE env (default 24h).
    """
    if now is None:
        now = datetime.utcnow()
    try:
        raw = fetched_at.replace("Z", "+00:00").replace("+00:00", "")
        # Strip any remaining timezone offset (e.g. +05:30, -08:00)
        if len(raw) > 19 and (raw[-6] == "+" or raw[-6] == "-"):
            raw = raw[:-6]
        elif len(raw) > 19 and (raw[-5] == "+" or raw[-5] == "-"):
            raw = raw[:-5]
        ts = datetime.fromisoformat(raw)
    except (ValueError, AttributeError, TypeError):
        return 0.5  # fallback for unparseable timestamps

    age_hours = max(0.0, (now - ts).total_seconds() / 3600.0)
    half_life = float(os.getenv("DATAPULSE_RECENCY_HALF_LIFE", str(_DEFAULT_HALF_LIFE_HOURS)))
    if half_life <= 0:
        half_life = _DEFAULT_HALF_LIFE_HOURS

    return math.pow(2, -age_hours / half_life)


def authority_score(item: DataPulseItem, authority_map: dict[str, float]) -> float:
    """Look up source authority weight from the authority map.

    Checks source_name (lowered), then domain of url.
    Falls back to 0.5 if unknown.
    """
    name_key = item.source_name.lower()
    if name_key in authority_map:
        return authority_map[name_key]

    domain = get_domain(item.url)
    if domain in authority_map:
        return authority_map[domain]

    return 0.5


def corroboration_score(item: DataPulseItem, fingerprint_counts: dict[str, int]) -> float:
    """Score based on how many sources reported the same story.

    Single source → 0.0, two sources → 0.5, three+ → 1.0.
    """
    fp = content_fingerprint(item.content)
    count = fingerprint_counts.get(fp, 1)
    if count <= 1:
        return 0.0
    if count == 2:
        return 0.5
    return 1.0


def source_diversity_score(item: DataPulseItem) -> float:
    """Score based on multi-source search confirmation."""
    sources = item.extra.get("search_sources")
    if not sources:
        return 0.0
    uniq = {s.lower() for s in sources if s}
    if len(uniq) <= 1:
        return 0.0
    if len(uniq) == 2:
        return 0.8
    return 1.0


def cross_validation_score(item: DataPulseItem) -> float:
    """Score based on search cross-source consistency and multi-source hits."""
    search_consistency = item.extra.get("search_cross_validation") or item.extra.get(
        "search_consistency",
    )
    if isinstance(search_consistency, dict):
        if search_consistency.get("is_cross_validated"):
            return 1.0
        provider_count = search_consistency.get("provider_count", 0)
        if provider_count >= 2:
            return 0.7
        if provider_count == 1:
            return 0.1
    source_count = item.extra.get("search_source_count", 0)
    if source_count >= 2:
        return 0.4
    return 0.0


def compute_composite_score(
    item: DataPulseItem,
    *,
    authority_map: dict[str, float] | None = None,
    fingerprint_counts: dict[str, int] | None = None,
    now: datetime | None = None,
    weights: dict[str, float] | None = None,
) -> tuple[int, dict[str, float]]:
    """Compute composite score (0-100) and return dimension breakdown.

    Does NOT modify item.confidence.
    """
    w = weights or DEFAULT_WEIGHTS
    amap = authority_map or {}
    fp_counts = fingerprint_counts or {}

    dim_confidence = item.confidence
    dim_authority = authority_score(item, amap)
    dim_corroboration = corroboration_score(item, fp_counts)
    dim_recency = recency_score(item.fetched_at, now=now)
    dim_source_diversity = source_diversity_score(item)
    w_source_diversity = w.get("source_diversity", 0.0)
    dim_cross_validation = cross_validation_score(item)
    w_cross_validation = w.get("cross_validation", 0.0)
    # Backward-compatible alias to satisfy acceptance docs using "recency_bonus" naming.
    recency_bonus = dim_recency * w.get("recency_bonus", 0.0)

    raw = (
        w.get("confidence", 0.25) * dim_confidence
        + w.get("authority", 0.30) * dim_authority
        + w.get("corroboration", 0.25) * dim_corroboration
        + w.get("recency", 0.20) * dim_recency
        + w_source_diversity * dim_source_diversity
        + w_cross_validation * dim_cross_validation
        + recency_bonus
    )

    score = max(0, min(100, round(raw * 100)))

    breakdown = {
        "confidence": round(dim_confidence, 4),
        "authority": round(dim_authority, 4),
        "corroboration": round(dim_corroboration, 4),
        "recency": round(dim_recency, 4),
        "source_diversity": round(dim_source_diversity, 4),
        "source_diversity_weight": round(w_source_diversity, 4),
        "cross_validation": round(dim_cross_validation, 4),
        "cross_validation_weight": round(w_cross_validation, 4),
        "recency_bonus": round(dim_recency * w.get("recency_bonus", 0.0), 4),
    }

    return score, breakdown


def rank_items(
    items: list[DataPulseItem],
    *,
    authority_map: dict[str, float] | None = None,
    now: datetime | None = None,
    weights: dict[str, float] | None = None,
) -> list[DataPulseItem]:
    """Score, rank, and annotate items. Returns items sorted by score descending."""
    if not items:
        return []

    amap = authority_map or {}

    # Build fingerprint counts for corroboration
    fp_counter: Counter[str] = Counter()
    for item in items:
        fp = content_fingerprint(item.content)
        fp_counter[fp] += 1

    fingerprint_counts = dict(fp_counter)

    # Score each item
    for item in items:
        score, breakdown = compute_composite_score(
            item,
            authority_map=amap,
            fingerprint_counts=fingerprint_counts,
            now=now,
            weights=weights,
        )
        item.score = score
        item.extra["score_breakdown"] = breakdown

    # Sort by score descending, then by confidence as tiebreaker
    items.sort(key=lambda it: (it.score, it.confidence), reverse=True)

    # Assign quality_rank (1-based)
    for rank, item in enumerate(items, 1):
        item.quality_rank = rank

    return items
