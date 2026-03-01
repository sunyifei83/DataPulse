"""Tests for web search integration via reader.search()."""

from __future__ import annotations

import asyncio
import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from datapulse.core.jina_client import JinaSearchResult
from datapulse.core.models import DataPulseItem, SourceType
from datapulse.reader import DataPulseReader


def _make_search_results(n: int = 3) -> list[JinaSearchResult]:
    return [
        JinaSearchResult(
            title=f"Result {i}",
            url=f"https://example{i}.com/page",
            description=f"Description of result {i} with enough text to be meaningful.",
            content=f"Full markdown content for result {i}. " * 20,
        )
        for i in range(1, n + 1)
    ]


def _run(coro):
    """Run an async coroutine synchronously."""
    return asyncio.get_event_loop().run_until_complete(coro)


class TestReaderSearch:
    @pytest.fixture()
    def reader(self, tmp_path: Path):
        return DataPulseReader(inbox_path=str(tmp_path / "inbox.json"))

    def test_search_without_fetch_content(self, reader):
        mock_results = _make_search_results(3)
        with patch.object(reader, "_jina_client") as mock_client:
            mock_client.search.return_value = mock_results
            items = _run(reader.search("test query", fetch_content=False))
            assert len(items) == 3
            assert all(isinstance(item, DataPulseItem) for item in items)
            for item in items:
                assert "jina_search" in item.tags
                assert item.extra.get("search_query") == "test query"

    def test_search_with_fetch_content(self, reader):
        """When fetch_content=True, each result URL goes through ParsePipeline."""
        mock_results = _make_search_results(2)
        with patch.object(reader, "_jina_client") as mock_client:
            mock_client.search.return_value = mock_results

            from datapulse.collectors.base import ParseResult

            success_result = ParseResult(
                url="https://example1.com/page",
                title="Better Title from Full Parse",
                content="Much richer content from full page parse. " * 30,
                success=True,
                source_type=SourceType.GENERIC,
                tags=["generic"],
                confidence_flags=[],
            )
            fail_result = ParseResult.failure(
                "https://example2.com/page", "Connection refused"
            )
            mock_parser = MagicMock()
            mock_parser.name = "generic"

            with patch.object(
                reader.router, "route",
                side_effect=[
                    (success_result, mock_parser),
                    (fail_result, mock_parser),
                ],
            ):
                items = _run(reader.search("test query", fetch_content=True))
                assert len(items) == 2

    def test_search_items_have_search_metadata(self, reader):
        mock_results = _make_search_results(1)
        with patch.object(reader, "_jina_client") as mock_client:
            mock_client.search.return_value = mock_results
            items = _run(reader.search("LLM optimization", fetch_content=False))
            assert len(items) == 1
            item = items[0]
            assert item.extra["search_query"] == "LLM optimization"
            assert "jina_search" in item.tags

    def test_search_batch_save(self, reader):
        """Verify inbox is saved once (not per-item)."""
        mock_results = _make_search_results(3)
        with patch.object(reader, "_jina_client") as mock_client:
            mock_client.search.return_value = mock_results
            with patch.object(reader.inbox, "save") as mock_save:
                _run(reader.search("test", fetch_content=False))
                assert mock_save.call_count == 1

    def test_search_with_sites(self, reader):
        from datapulse.core.jina_client import JinaSearchOptions

        mock_results = _make_search_results(1)
        with patch.object(reader, "_jina_client") as mock_client:
            mock_client.search.return_value = mock_results
            _run(reader.search(
                "async patterns",
                sites=["python.org", "docs.python.org"],
                fetch_content=False,
            ))
            call_kwargs = mock_client.search.call_args[1]
            opts = call_kwargs["options"]
            assert isinstance(opts, JinaSearchOptions)
            assert opts.sites == ["python.org", "docs.python.org"]

    def test_search_with_limit(self, reader):
        mock_results = _make_search_results(5)
        with patch.object(reader, "_jina_client") as mock_client:
            mock_client.search.return_value = mock_results
            _run(reader.search("test", limit=3, fetch_content=False))
            call_kwargs = mock_client.search.call_args[1]
            assert call_kwargs["options"].limit == 3

    def test_search_no_api_key_raises(self, reader):
        with patch.object(reader, "_jina_client") as mock_client:
            mock_client.search.side_effect = ValueError("API key required")
            with pytest.raises(ValueError, match="API key"):
                _run(reader.search("test"))

    def test_search_empty_results(self, reader):
        with patch.object(reader, "_jina_client") as mock_client:
            mock_client.search.return_value = []
            items = _run(reader.search("obscure query", fetch_content=False))
            assert items == []

    def test_search_results_scored(self, reader):
        """Results should have non-zero confidence."""
        mock_results = _make_search_results(3)
        with patch.object(reader, "_jina_client") as mock_client:
            mock_client.search.return_value = mock_results
            items = _run(reader.search("test", fetch_content=False))
            for item in items:
                assert item.confidence > 0

    def test_search_min_confidence_filter(self, reader):
        mock_results = _make_search_results(3)
        with patch.object(reader, "_jina_client") as mock_client:
            mock_client.search.return_value = mock_results
            items = _run(reader.search("test", fetch_content=False, min_confidence=0.99))
            for item in items:
                assert item.confidence >= 0.99
