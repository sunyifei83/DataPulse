"""Tests for SourceCatalog, matching, subscriptions, and packs."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from datapulse.core.models import DataPulseItem, SourceType
from datapulse.core.source_catalog import SourceCatalog, SourceRecord, SourcePack


class TestSourceRecord:
    def test_from_dict_basic(self):
        raw = {
            "id": "src1",
            "name": "Twitter Tech",
            "source_type": "twitter",
            "config": {"url": "https://x.com/tech"},
            "is_active": True,
            "is_public": True,
            "tags": ["twitter"],
            "match": {"domain": "x.com"},
        }
        rec = SourceRecord.from_dict(raw)
        assert rec.id == "src1"
        assert rec.name == "Twitter Tech"
        assert rec.source_type == "twitter"

    def test_from_dict_auto_id(self):
        raw = {"name": "auto", "source_type": "generic"}
        rec = SourceRecord.from_dict(raw)
        assert rec.id  # should be auto-generated

    def test_round_trip(self):
        raw = {
            "id": "rt1",
            "name": "RT",
            "source_type": "reddit",
            "config": {"url": "https://reddit.com/r/test"},
            "is_active": True,
            "is_public": False,
            "tags": ["reddit"],
            "match": {"domain": "reddit.com"},
        }
        rec = SourceRecord.from_dict(raw)
        restored = rec.to_dict()
        assert restored["id"] == "rt1"
        assert restored["source_type"] == "reddit"
        assert restored["is_public"] is False

    def test_matches_by_domain(self):
        rec = SourceRecord.from_dict({
            "name": "T", "source_type": "twitter",
            "match": {"domain": "x.com"},
        })
        item = DataPulseItem(
            source_type=SourceType.TWITTER,
            source_name="test",
            title="t",
            content="c",
            url="https://x.com/user/status/1",
        )
        assert rec.matches(item) is True

    def test_matches_by_url_prefix(self):
        rec = SourceRecord.from_dict({
            "name": "R", "source_type": "reddit",
            "match": {"url_prefix": "https://reddit.com/r/python"},
        })
        item = DataPulseItem(
            source_type=SourceType.REDDIT,
            source_name="test",
            title="t",
            content="c",
            url="https://reddit.com/r/python/comments/abc/test",
        )
        assert rec.matches(item) is True

    def test_matches_by_pattern(self):
        rec = SourceRecord.from_dict({
            "name": "P", "source_type": "generic",
            "match": {"pattern": r"example\.com/blog"},
        })
        item = DataPulseItem(
            source_type=SourceType.GENERIC,
            source_name="test",
            title="t",
            content="c",
            url="https://example.com/blog/post-1",
        )
        assert rec.matches(item) is True

    def test_no_match_wrong_type(self):
        rec = SourceRecord.from_dict({
            "name": "T", "source_type": "twitter",
            "match": {"domain": "x.com"},
        })
        item = DataPulseItem(
            source_type=SourceType.REDDIT,
            source_name="test",
            title="t",
            content="c",
            url="https://x.com/user",
        )
        assert rec.matches(item) is False


class TestSourcePack:
    def test_from_dict(self):
        raw = {
            "name": "Tech Pack",
            "slug": "tech-pack",
            "source_ids": ["s1", "s2"],
            "is_public": True,
        }
        pack = SourcePack.from_dict(raw)
        assert pack.name == "Tech Pack"
        assert pack.slug == "tech-pack"
        assert len(pack.source_ids) == 2

    def test_auto_slug(self):
        raw = {"name": "My Custom Pack", "source_ids": []}
        pack = SourcePack.from_dict(raw)
        assert pack.slug  # auto-generated from name


class TestSourceCatalog:
    def test_load_sources(self, tmp_catalog: Path):
        catalog = SourceCatalog(str(tmp_catalog))
        sources = catalog.list_sources()
        assert len(sources) >= 2  # active ones

    def test_list_sources_excludes_inactive(self, tmp_catalog: Path):
        catalog = SourceCatalog(str(tmp_catalog))
        sources = catalog.list_sources(include_inactive=False)
        assert all(s.is_active for s in sources)

    def test_list_sources_includes_inactive(self, tmp_catalog: Path):
        catalog = SourceCatalog(str(tmp_catalog))
        sources = catalog.list_sources(include_inactive=True)
        assert any(not s.is_active for s in sources)

    def test_get_source(self, tmp_catalog: Path):
        catalog = SourceCatalog(str(tmp_catalog))
        source = catalog.get_source("src_twitter_1")
        assert source is not None
        assert source.name == "Twitter Tech"

    def test_get_source_not_found(self, tmp_catalog: Path):
        catalog = SourceCatalog(str(tmp_catalog))
        assert catalog.get_source("nonexistent") is None

    def test_subscribe_and_unsubscribe(self, tmp_catalog: Path):
        catalog = SourceCatalog(str(tmp_catalog))
        # Unsubscribe
        assert catalog.unsubscribe("default", "src_twitter_1") is True
        subs = catalog.get_subscription("default")
        assert "src_twitter_1" not in subs
        # Re-subscribe
        assert catalog.subscribe("default", "src_twitter_1") is True
        subs = catalog.get_subscription("default")
        assert "src_twitter_1" in subs

    def test_subscribe_nonexistent_source(self, tmp_catalog: Path):
        catalog = SourceCatalog(str(tmp_catalog))
        assert catalog.subscribe("default", "nonexistent") is False

    def test_install_pack(self, tmp_catalog: Path):
        catalog = SourceCatalog(str(tmp_catalog))
        # Clear subscriptions first
        catalog.subscriptions["test_profile"] = []
        catalog._save()
        added = catalog.install_pack("test_profile", "tech-pack")
        assert added == 2
        subs = catalog.get_subscription("test_profile")
        assert "src_twitter_1" in subs

    def test_install_pack_nonexistent(self, tmp_catalog: Path):
        catalog = SourceCatalog(str(tmp_catalog))
        assert catalog.install_pack("default", "nonexistent-pack") == 0

    def test_list_packs(self, tmp_catalog: Path):
        catalog = SourceCatalog(str(tmp_catalog))
        packs = catalog.list_packs()
        assert len(packs) >= 1

    def test_resolve_source_known(self, tmp_catalog: Path):
        catalog = SourceCatalog(str(tmp_catalog))
        result = catalog.resolve_source("https://x.com/techuser/status/123")
        assert result.get("source_type") == "twitter"

    def test_resolve_source_unknown(self, tmp_catalog: Path):
        catalog = SourceCatalog(str(tmp_catalog))
        result = catalog.resolve_source("https://unknown-site.com/page")
        assert "source_type" in result

    def test_register_auto_source(self, tmp_catalog: Path):
        catalog = SourceCatalog(str(tmp_catalog))
        rec = catalog.register_auto_source("New Source", "generic", "https://new.com")
        assert rec.id in catalog.sources
        # Second call returns same record
        rec2 = catalog.register_auto_source("New Source", "generic", "https://new.com")
        assert rec2.id == rec.id

    def test_filter_by_subscription(self, tmp_catalog: Path):
        catalog = SourceCatalog(str(tmp_catalog))
        items = [
            DataPulseItem(
                source_type=SourceType.TWITTER,
                source_name="test",
                title="t",
                content="c",
                url="https://x.com/techuser/status/1",
            ),
            DataPulseItem(
                source_type=SourceType.GENERIC,
                source_name="other",
                title="o",
                content="c",
                url="https://random.com/page",
            ),
        ]
        filtered = catalog.filter_by_subscription(items, profile="default")
        # Twitter item should match, generic may or may not depending on catalog
        assert len(filtered) >= 1

    def test_empty_catalog(self, tmp_path: Path):
        catalog = SourceCatalog(str(tmp_path / "empty.json"))
        assert catalog.list_sources() == []
        assert catalog.list_packs() == []
