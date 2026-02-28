"""Shared fixtures for DataPulse test suite."""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from datapulse.collectors.base import ParseResult
from datapulse.core.models import DataPulseItem, SourceType, MediaType


@pytest.fixture()
def tmp_inbox(tmp_path: Path) -> Path:
    """Return a temporary inbox JSON path."""
    return tmp_path / "test_inbox.json"


@pytest.fixture()
def tmp_inbox_with_items(tmp_path: Path) -> Path:
    """Return a temp inbox pre-populated with sample items."""
    inbox_path = tmp_path / "test_inbox.json"
    items = [
        DataPulseItem(
            source_type=SourceType.TWITTER,
            source_name="@testuser",
            title="Test Tweet",
            content="Hello world from twitter " * 20,
            url="https://x.com/testuser/status/123",
            parser="twitter",
            confidence=0.85,
            confidence_factors=["title", "source_name"],
        ),
        DataPulseItem(
            source_type=SourceType.REDDIT,
            source_name="u/testuser",
            title="Test Reddit Post",
            content="Reddit content here " * 30,
            url="https://reddit.com/r/test/comments/abc123/test/",
            parser="reddit",
            confidence=0.90,
            confidence_factors=["title", "source_name", "comments"],
        ),
        DataPulseItem(
            source_type=SourceType.GENERIC,
            source_name="example.com",
            title="Generic Page",
            content="Short",
            url="https://example.com/page",
            parser="generic",
            confidence=0.55,
            confidence_factors=["title"],
        ),
    ]
    payload = [item.to_dict() for item in items]
    inbox_path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    return inbox_path


@pytest.fixture()
def tmp_catalog(tmp_path: Path) -> Path:
    """Return a temporary source catalog JSON path."""
    catalog_path = tmp_path / "test_catalog.json"
    catalog = {
        "version": 1,
        "sources": [
            {
                "id": "src_twitter_1",
                "name": "Twitter Tech",
                "source_type": "twitter",
                "config": {"url": "https://x.com/techuser"},
                "is_active": True,
                "is_public": True,
                "tags": ["twitter", "tech"],
                "match": {"domain": "x.com"},
            },
            {
                "id": "src_reddit_1",
                "name": "Reddit Python",
                "source_type": "reddit",
                "config": {"url": "https://reddit.com/r/python"},
                "is_active": True,
                "is_public": True,
                "tags": ["reddit", "python"],
                "match": {"url_prefix": "https://reddit.com/r/python"},
            },
            {
                "id": "src_inactive",
                "name": "Inactive Source",
                "source_type": "generic",
                "config": {},
                "is_active": False,
                "is_public": True,
                "tags": [],
                "match": {},
            },
        ],
        "subscriptions": {
            "default": ["src_twitter_1", "src_reddit_1"],
        },
        "packs": [
            {
                "name": "Tech Pack",
                "slug": "tech-pack",
                "source_ids": ["src_twitter_1", "src_reddit_1"],
                "is_public": True,
            },
        ],
    }
    catalog_path.write_text(json.dumps(catalog, ensure_ascii=False), encoding="utf-8")
    return catalog_path


def mock_parse_result(
    url: str = "https://example.com",
    title: str = "Test Title",
    content: str = "Test content " * 50,
    author: str = "Test Author",
    success: bool = True,
    source_type: SourceType = SourceType.GENERIC,
    **kwargs,
) -> ParseResult:
    """Factory for test ParseResult instances."""
    return ParseResult(
        url=url,
        title=title,
        content=content,
        author=author,
        success=success,
        source_type=source_type,
        excerpt=content[:200],
        tags=kwargs.get("tags", ["test"]),
        confidence_flags=kwargs.get("confidence_flags", []),
        extra=kwargs.get("extra", {}),
        media_type=kwargs.get("media_type", "text"),
    )
