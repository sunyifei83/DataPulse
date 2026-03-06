"""Tests for the multi-dimensional scoring engine."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from datapulse.core.models import DataPulseItem, SourceType
from datapulse.core.scoring import (
    authority_score,
    compute_composite_score,
    corroboration_score,
    engagement_score,
    rank_items,
    recency_score,
)
from datapulse.core.utils import content_fingerprint


def _make_item(
    title: str = "Test",
    content: str = "Test content here",
    confidence: float = 0.8,
    source_name: str = "test_source",
    url: str = "https://example.com/page",
    fetched_at: str | None = None,
    **kwargs,
) -> DataPulseItem:
    item = DataPulseItem(
        source_type=kwargs.get("source_type", SourceType.GENERIC),
        source_name=source_name,
        title=title,
        content=content,
        url=url,
        confidence=confidence,
    )
    if fetched_at:
        item.fetched_at = fetched_at
    return item


class TestRecencyScore:
    def test_fresh_item_high_score(self):
        now = datetime.now(timezone.utc)
        item = _make_item(fetched_at=now.isoformat())
        score = recency_score(item.fetched_at, now=now)
        assert score > 0.95

    def test_old_item_low_score(self):
        now = datetime.now(timezone.utc)
        old = (now - timedelta(hours=72)).isoformat()
        score = recency_score(old, now=now)
        assert score < 0.2

    def test_half_life_precision(self):
        """After exactly one half-life, score should be ~0.5."""
        now = datetime.now(timezone.utc)
        one_half_life_ago = (now - timedelta(hours=24)).isoformat()
        score = recency_score(one_half_life_ago, now=now)
        assert abs(score - 0.5) < 0.01

    def test_zero_age(self):
        now = datetime.now(timezone.utc)
        score = recency_score(now.isoformat(), now=now)
        assert abs(score - 1.0) < 0.01

    def test_unparseable_timestamp(self):
        score = recency_score("not-a-date")
        assert score == 0.5


class TestAuthorityScore:
    def test_known_source(self):
        item = _make_item(source_name="NYTimes")
        amap = {"nytimes": 0.95}
        assert authority_score(item, amap) == 0.95

    def test_unknown_source_default(self):
        item = _make_item(source_name="unknown_blog")
        assert authority_score(item, {}) == 0.5

    def test_domain_fallback(self):
        item = _make_item(source_name="random", url="https://nature.com/article/123")
        amap = {"nature.com": 0.9}
        assert authority_score(item, amap) == 0.9

    def test_name_takes_precedence_over_domain(self):
        item = _make_item(source_name="Nature", url="https://nature.com/article")
        amap = {"nature": 0.95, "nature.com": 0.8}
        assert authority_score(item, amap) == 0.95


class TestCorroborationScore:
    def test_single_source(self):
        item = _make_item(content="unique story about quantum computing breakthroughs")
        fp = content_fingerprint(item.content)
        score = corroboration_score(item, {fp: 1})
        assert score == 0.0

    def test_two_sources(self):
        item = _make_item(content="shared story about quantum computing breakthroughs")
        fp = content_fingerprint(item.content)
        score = corroboration_score(item, {fp: 2})
        assert score == 0.5

    def test_three_plus_sources(self):
        item = _make_item(content="viral story about quantum computing breakthroughs")
        fp = content_fingerprint(item.content)
        score = corroboration_score(item, {fp: 5})
        assert score == 1.0

    def test_boundary_single(self):
        item = _make_item(content="boundary test content for scoring")
        assert corroboration_score(item, {}) == 0.0


class TestEngagementScore:
    def test_empty_metadata_returns_zero(self):
        item = _make_item()
        assert engagement_score(item) == 0.0

    def test_reddit_metrics_increase_engagement(self):
        low = _make_item(source_type=SourceType.REDDIT)
        low.extra = {"score": 8, "num_comments": 5, "upvote_ratio": 0.61}

        high = _make_item(source_type=SourceType.REDDIT)
        high.extra = {"score": 320, "num_comments": 96, "upvote_ratio": 0.93}

        assert engagement_score(high) > engagement_score(low)


class TestCompositeScore:
    def test_all_dimensions_contribute(self):
        now = datetime.now(timezone.utc)
        item = _make_item(
            confidence=0.9,
            source_name="trusted",
            fetched_at=now.isoformat(),
        )
        amap = {"trusted": 0.9}
        fp = content_fingerprint(item.content)
        score, breakdown = compute_composite_score(
            item, authority_map=amap, fingerprint_counts={fp: 3}, now=now,
        )
        assert 0 <= score <= 100
        assert breakdown["confidence"] == 0.9
        assert breakdown["authority"] == 0.9
        assert breakdown["corroboration"] == 1.0
        assert breakdown["recency"] > 0.95

    def test_score_in_range(self):
        item = _make_item(confidence=0.5)
        score, _ = compute_composite_score(item)
        assert 0 <= score <= 100

    def test_confidence_not_changed(self):
        item = _make_item(confidence=0.75)
        original_confidence = item.confidence
        compute_composite_score(item)
        assert item.confidence == original_confidence

    def test_custom_weights(self):
        now = datetime.now(timezone.utc)
        item = _make_item(confidence=1.0, fetched_at=now.isoformat())
        # Weight only confidence
        weights = {"confidence": 1.0, "authority": 0.0, "corroboration": 0.0, "recency": 0.0}
        score, _ = compute_composite_score(item, weights=weights, now=now)
        assert score == 100

    def test_zero_confidence_low_score(self):
        item = _make_item(confidence=0.0)
        score, breakdown = compute_composite_score(item)
        assert breakdown["confidence"] == 0.0
        # Score should still incorporate other dimensions
        assert score >= 0

    def test_recency_uses_search_raw_published_date(self):
        now = datetime.now(timezone.utc)
        old = (now - timedelta(days=7)).isoformat()
        item = _make_item(confidence=0.8, fetched_at=now.isoformat())
        item.extra = {"search_raw": {"published_date": old}}
        _, breakdown = compute_composite_score(item, now=now)
        assert float(breakdown["recency"]) < 0.1
        assert breakdown["recency_source"] == "search_raw.published_date"

    def test_recency_can_use_twitter_status_time_proxy(self):
        now = datetime.now(timezone.utc)
        tw_epoch = 1288834974657
        old = now - timedelta(days=10)
        status_id = ((int(old.timestamp() * 1000) - tw_epoch) << 22) + 1
        item = _make_item(
            confidence=0.8,
            fetched_at=now.isoformat(),
            url=f"https://x.com/user/status/{status_id}",
            source_type=SourceType.TWITTER,
        )
        _, breakdown = compute_composite_score(item, now=now)
        assert float(breakdown["recency"]) < 0.1
        assert breakdown["recency_source"] == "twitter_status_id"

    def test_search_noise_penalty_reduces_listicle_score(self):
        now = datetime.now(timezone.utc)
        listicle = _make_item(
            title="Top 20 Best Data Governance Tools",
            content="Curated list for buyers.",
            confidence=0.85,
            url="https://example.com/top-data-governance-tools",
        )
        listicle.parser = "search_result"
        listicle.extra = {"search_query": "data governance open source"}

        actionable = _make_item(
            title="OpenLineage on GitHub",
            content="Project repo: https://github.com/OpenLineage/OpenLineage",
            confidence=0.85,
            url="https://github.com/OpenLineage/OpenLineage",
        )
        actionable.parser = "search_result"
        actionable.extra = {"search_query": "data governance open source"}

        weights = {
            "confidence": 1.0,
            "authority": 0.0,
            "corroboration": 0.0,
            "entity_corroboration": 0.0,
            "recency": 0.0,
            "source_diversity": 0.0,
            "cross_validation": 0.0,
            "recency_bonus": 0.0,
            "engagement": 0.0,
            "search_noise_penalty": 0.4,
        }
        listicle_score, listicle_breakdown = compute_composite_score(listicle, now=now, weights=weights)
        actionable_score, actionable_breakdown = compute_composite_score(actionable, now=now, weights=weights)

        assert listicle_breakdown["search_noise_penalty"] > actionable_breakdown["search_noise_penalty"]
        assert listicle_score < actionable_score


class TestRankItems:
    def test_sorted_order(self):
        now = datetime.now(timezone.utc)
        items = [
            _make_item(title="Low", confidence=0.3, content="low quality content here now",
                       fetched_at=(now - timedelta(hours=48)).isoformat()),
            _make_item(title="High", confidence=0.95, content="high quality content here now",
                       fetched_at=now.isoformat(), url="https://example.com/high"),
        ]
        ranked = rank_items(items, now=now)
        assert ranked[0].title == "High"
        assert ranked[1].title == "Low"

    def test_quality_rank_assigned(self):
        items = [
            _make_item(title="A", confidence=0.9, url="https://a.com"),
            _make_item(title="B", confidence=0.5, url="https://b.com"),
        ]
        ranked = rank_items(items)
        assert ranked[0].quality_rank == 1
        assert ranked[1].quality_rank == 2

    def test_score_breakdown_in_extra(self):
        items = [_make_item()]
        ranked = rank_items(items)
        assert "score_breakdown" in ranked[0].extra
        breakdown = ranked[0].extra["score_breakdown"]
        assert "confidence" in breakdown
        assert "authority" in breakdown
        assert "corroboration" in breakdown
        assert "recency" in breakdown
        assert "engagement" in breakdown

    def test_empty_list(self):
        assert rank_items([]) == []

    def test_corroboration_grouping(self):
        """Items with same content fingerprint should get corroboration boost."""
        now = datetime.now(timezone.utc)
        shared = "breaking news about artificial intelligence regulation in europe"
        items = [
            _make_item(title="A", content=shared, source_name="s1",
                       url="https://a.com", fetched_at=now.isoformat()),
            _make_item(title="B", content=shared, source_name="s2",
                       url="https://b.com", fetched_at=now.isoformat()),
            _make_item(title="C", content="totally unique unrelated content about gardening tips",
                       source_name="s3", url="https://c.com", fetched_at=now.isoformat()),
        ]
        ranked = rank_items(items, now=now)
        # Items A and B share fingerprint, so they get corroboration boost
        corr_a = ranked[0].extra["score_breakdown"]["corroboration"] if ranked[0].title in ("A", "B") else 0
        corr_c = next(it.extra["score_breakdown"]["corroboration"] for it in ranked if it.title == "C")
        # A/B have corroboration, C doesn't
        assert corr_a > corr_c

    def test_score_is_int(self):
        items = [_make_item()]
        ranked = rank_items(items)
        assert isinstance(ranked[0].score, int)

    def test_tie_breaks_by_engagement_signal(self):
        items = [
            _make_item(
                title="Higher engagement",
                confidence=0.7,
                source_type=SourceType.REDDIT,
                source_name="reddit.com",
                url="https://reddit.com/r/test/comments/1/high",
            ),
            _make_item(
                title="Lower engagement",
                confidence=0.7,
                source_type=SourceType.REDDIT,
                source_name="reddit.com",
                url="https://reddit.com/r/test/comments/1/low",
            ),
        ]
        items[0].extra = {"score": 300, "num_comments": 80, "upvote_ratio": 0.92}
        items[1].extra = {"score": 10, "num_comments": 5, "upvote_ratio": 0.6}

        zero_weights = {
            "confidence": 0.0,
            "authority": 0.0,
            "corroboration": 0.0,
            "entity_corroboration": 0.0,
            "recency": 0.0,
            "source_diversity": 0.0,
            "cross_validation": 0.0,
            "recency_bonus": 0.0,
            "engagement": 0.0,
        }
        ranked = rank_items(items, weights=zero_weights)
        assert ranked[0].title == "Higher engagement"
