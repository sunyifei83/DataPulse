"""Tests for SearchGateway normalization and deduplication behavior."""

from __future__ import annotations

from datapulse.core.search_gateway import SearchGateway, SearchHit


def test_normalize_url_collapses_research_mirror_subdomain():
    gateway = SearchGateway()
    mirror = "https://research.aimultiple.com/open-source-data-governance"
    canonical = "https://aimultiple.com/open-source-data-governance"

    assert gateway._normalize_url(mirror) == gateway._normalize_url(canonical)


def test_dedupe_hits_merges_mirror_pages():
    gateway = SearchGateway()
    hit_a = SearchHit(
        title="Open Source Data Governance Tools",
        url="https://research.aimultiple.com/open-source-data-governance",
        snippet="Top open source options for data governance.",
        provider="tavily",
        source="tavily",
        score=0.83,
        extra={"sources": ["tavily"]},
    )
    hit_b = SearchHit(
        title="Open Source Data Governance Tools",
        url="https://aimultiple.com/open-source-data-governance",
        snippet="Top open source options for data governance.",
        provider="jina",
        source="jina",
        score=0.81,
        extra={"sources": ["jina"]},
    )

    merged = gateway._dedupe_hits([hit_a, hit_b])
    assert len(merged) == 1
    assert set(merged[0].extra.get("sources", [])) == {"jina", "tavily"}
