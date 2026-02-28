"""Tests for ParsePipeline routing."""

from __future__ import annotations

import pytest

from datapulse.core.router import ParsePipeline
from datapulse.collectors.base import BaseCollector, ParseResult
from datapulse.core.models import SourceType


class StubCollector(BaseCollector):
    """A minimal test collector."""

    def __init__(self, name: str, handles: list[str], succeed: bool = True):
        self.name = name
        self.source_type = SourceType.GENERIC
        self._handles = handles
        self._succeed = succeed

    def can_handle(self, url: str) -> bool:
        return any(h in url for h in self._handles)

    def parse(self, url: str) -> ParseResult:
        if self._succeed:
            return ParseResult(
                url=url,
                title=f"Parsed by {self.name}",
                content=f"Content from {self.name}",
                source_type=self.source_type,
            )
        return ParseResult.failure(url, f"{self.name} failed")


class TestParsePipeline:
    def test_available_parsers_listed(self):
        pipeline = ParsePipeline()
        names = pipeline.available_parsers
        assert "twitter" in names
        assert "youtube" in names
        assert "reddit" in names
        assert "bilibili" in names
        assert "rss" in names
        assert "generic" in names
        assert "jina" in names

    def test_register_parser_default(self):
        pipeline = ParsePipeline()
        stub = StubCollector("stub", ["stub.com"])
        pipeline.register_parser(stub)
        assert "stub" in pipeline.available_parsers
        assert pipeline.available_parsers[-1] == "stub"

    def test_register_parser_priority(self):
        pipeline = ParsePipeline()
        stub = StubCollector("priority_stub", ["priority.com"])
        pipeline.register_parser(stub, priority=True)
        assert pipeline.available_parsers[0] == "priority_stub"

    def test_route_returns_failure_for_impossible_url(self):
        pipeline = ParsePipeline(extra_parsers=[])
        # Use only stub collectors that won't handle the URL
        stub = StubCollector("nope", ["impossible.xyz"])
        pipeline.parsers = [stub]
        result, parser = pipeline.route("https://never-matched.com/page")
        assert result.success is False

    def test_route_with_custom_parsers(self):
        stub = StubCollector("custom", ["custom.io"])
        pipeline = ParsePipeline(extra_parsers=[stub])
        result, parser = pipeline.route("https://custom.io/page")
        assert result.success is True
        assert parser.name == "custom"

    def test_fallback_chain(self):
        """If first parser fails, should try next."""
        fail = StubCollector("fail_first", ["test.com"], succeed=False)
        succeed = StubCollector("succeed_second", ["test.com"], succeed=True)
        pipeline = ParsePipeline(extra_parsers=[])
        pipeline.parsers = [fail, succeed]
        result, parser = pipeline.route("https://test.com/page")
        assert result.success is True
        assert parser.name == "succeed_second"
