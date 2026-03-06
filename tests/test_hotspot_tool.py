"""Tests for hotspot evidence pack tool."""

from __future__ import annotations

import asyncio

from datapulse.collectors.base import ParseResult
from datapulse.core.models import DataPulseItem, SourceType
from datapulse.tools import hotspot


def test_extract_repo_slug():
    assert hotspot.extract_repo_slug("https://github.com/OpenLineage/OpenLineage") == "openlineage/openlineage"
    assert hotspot.extract_repo_slug("https://www.github.com/dbt-labs/dbt-core/issues/1") == "dbt-labs/dbt-core"
    assert hotspot.extract_repo_slug("https://example.com/foo/bar") == ""


def test_extract_repo_candidates_from_text_and_extra():
    item = DataPulseItem(
        source_type=SourceType.REDDIT,
        source_name="reddit.com",
        title="Useful links",
        content=(
            "See https://github.com/open-metadata/OpenMetadata and "
            "https://example.com/page"
        ),
        url="https://www.reddit.com/r/data/comments/abc/topic",
        confidence=0.82,
        extra={
            "github_repos": ["airbytehq/airbyte"],
            "comment_links": ["https://github.com/dbt-labs/dbt-core/discussions/1"],
        },
    )

    repos = hotspot.extract_repo_candidates(item)
    assert "open-metadata/openmetadata" in repos
    assert "airbytehq/airbyte" in repos
    assert "dbt-labs/dbt-core" in repos


def test_build_hotspot_evidence_pack(monkeypatch):
    class _FakeReader:
        async def search(self, *args, **kwargs):  # noqa: ANN002, ANN003
            return [
                DataPulseItem(
                    source_type=SourceType.GENERIC,
                    source_name="search",
                    title="OpenLineage project",
                    content="Repository: https://github.com/OpenLineage/OpenLineage",
                    url="https://example.com/post",
                    confidence=0.86,
                    confidence_factors=["search_result"],
                    extra={"search_cross_validation": {"provider_count": 2}},
                )
            ]

        async def read(self, *args, **kwargs):  # noqa: ANN002, ANN003
            raise AssertionError("should not call read in this test")

    class _FakeGitHubCollector:
        def parse(self, url: str) -> ParseResult:
            assert "openlineage/openlineage" in url.lower()
            return ParseResult(
                url=url,
                title="OpenLineage/OpenLineage",
                content="meta",
                author="OpenLineage",
                success=True,
                source_type=SourceType.GENERIC,
                confidence_flags=["github_api"],
                extra={
                    "repo": "openlineage/openlineage",
                    "stars": 2400,
                    "forks": 430,
                    "open_issues": 120,
                    "pushed_at": "2026-03-01T00:00:00Z",
                    "release": {"tag_name": "v1.0.0"},
                    "api_degraded": False,
                },
            )

    monkeypatch.setattr(hotspot, "DataPulseReader", lambda: _FakeReader())
    monkeypatch.setattr(hotspot, "GitHubCollector", lambda: _FakeGitHubCollector())

    rows = asyncio.run(
        hotspot.build_hotspot_evidence_pack(
            query="data lineage",
            platform="web",
            provider="auto",
            limit=5,
            min_confidence=0.5,
        )
    )

    assert len(rows) == 1
    assert rows[0]["github_repo"] == "openlineage/openlineage"
    assert rows[0]["repo_api_degraded"] is False
    assert rows[0]["confidence"] >= 0.86
