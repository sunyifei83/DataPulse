"""Tests for DataPulseReader feed generation."""

from __future__ import annotations

import json
import xml.etree.ElementTree as ET

import pytest

from datapulse.core.models import DataPulseItem, SourceType
from datapulse.core.storage import UnifiedInbox
from datapulse.reader import DataPulseReader


def _populate_inbox(inbox_path: str, items: list[DataPulseItem]) -> None:
    """Write items to an inbox file."""
    import json
    from pathlib import Path

    payload = [item.to_dict() for item in items]
    Path(inbox_path).write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")


class TestBuildJsonFeed:
    @pytest.fixture()
    def reader_with_items(self, tmp_path):
        inbox_path = str(tmp_path / "inbox.json")
        catalog_path = str(tmp_path / "catalog.json")
        # Write empty catalog
        import json
        from pathlib import Path

        Path(catalog_path).write_text(json.dumps({
            "version": 1, "sources": [], "subscriptions": {}, "packs": [],
        }), encoding="utf-8")

        items = [
            DataPulseItem(
                source_type=SourceType.TWITTER,
                source_name="@user",
                title="Tweet 1",
                content="Content 1",
                url="https://x.com/user/status/1",
                confidence=0.85,
            ),
            DataPulseItem(
                source_type=SourceType.REDDIT,
                source_name="u/redditor",
                title="Post 1",
                content="Reddit content",
                url="https://reddit.com/r/test/comments/abc/post/",
                confidence=0.90,
            ),
        ]
        _populate_inbox(inbox_path, items)

        import os
        os.environ["DATAPULSE_SOURCE_CATALOG"] = catalog_path
        reader = DataPulseReader(inbox_path=inbox_path)
        yield reader
        os.environ.pop("DATAPULSE_SOURCE_CATALOG", None)

    def test_json_feed_schema(self, reader_with_items):
        feed = reader_with_items.build_json_feed()
        assert feed["version"] == "https://jsonfeed.org/version/1.1"
        assert "title" in feed
        assert "items" in feed
        assert isinstance(feed["items"], list)

    def test_json_feed_items_have_required_fields(self, reader_with_items):
        feed = reader_with_items.build_json_feed()
        for item in feed["items"]:
            assert "id" in item
            assert "title" in item
            assert "content_text" in item
            assert "url" in item

    def test_json_feed_authors_v11_format(self, reader_with_items):
        """JSON Feed v1.1: authors must be list[dict], not string."""
        feed = reader_with_items.build_json_feed()
        for item in feed["items"]:
            assert "author" not in item, "'author' key should not exist in JSON Feed v1.1"
            assert "authors" in item
            assert isinstance(item["authors"], list)
            for author in item["authors"]:
                assert isinstance(author, dict)
                assert "name" in author

    def test_json_feed_limit(self, reader_with_items):
        feed = reader_with_items.build_json_feed(limit=1)
        assert len(feed["items"]) <= 1


class TestBuildRssFeed:
    @pytest.fixture()
    def reader_with_items(self, tmp_path):
        inbox_path = str(tmp_path / "inbox.json")
        catalog_path = str(tmp_path / "catalog.json")
        import json, os
        from pathlib import Path

        Path(catalog_path).write_text(json.dumps({
            "version": 1, "sources": [], "subscriptions": {}, "packs": [],
        }), encoding="utf-8")

        items = [
            DataPulseItem(
                source_type=SourceType.GENERIC,
                source_name="example",
                title="Test <Page> & More",
                content="Content with <html> & \"quotes\"",
                url="https://example.com/page?a=1&b=2",
                confidence=0.75,
            ),
        ]
        _populate_inbox(inbox_path, items)

        os.environ["DATAPULSE_SOURCE_CATALOG"] = catalog_path
        reader = DataPulseReader(inbox_path=inbox_path)
        yield reader
        os.environ.pop("DATAPULSE_SOURCE_CATALOG", None)

    def test_rss_well_formed_xml(self, reader_with_items):
        xml_str = reader_with_items.build_rss_feed()
        # Should parse as valid XML
        root = ET.fromstring(xml_str)
        assert root.tag == "rss"
        assert root.attrib.get("version") == "2.0"

    def test_rss_has_channel(self, reader_with_items):
        xml_str = reader_with_items.build_rss_feed()
        root = ET.fromstring(xml_str)
        channel = root.find("channel")
        assert channel is not None
        assert channel.find("title") is not None

    def test_rss_items_present(self, reader_with_items):
        xml_str = reader_with_items.build_rss_feed()
        root = ET.fromstring(xml_str)
        channel = root.find("channel")
        items = channel.findall("item")
        assert len(items) >= 1

    def test_rss_xml_escaping(self, reader_with_items):
        xml_str = reader_with_items.build_rss_feed()
        # Should parse without error (means special chars are properly escaped)
        root = ET.fromstring(xml_str)
        channel = root.find("channel")
        item = channel.find("item")
        title = item.find("title").text
        assert "&" in title or "<" not in title  # properly escaped


class TestBuildAtomFeed:
    @pytest.fixture()
    def reader_with_items(self, tmp_path):
        inbox_path = str(tmp_path / "inbox.json")
        catalog_path = str(tmp_path / "catalog.json")
        import json, os
        from pathlib import Path

        Path(catalog_path).write_text(json.dumps({
            "version": 1, "sources": [], "subscriptions": {}, "packs": [],
        }), encoding="utf-8")

        items = [
            DataPulseItem(
                source_type=SourceType.TWITTER,
                source_name="@atomuser",
                title="Atom Test <Item> & More",
                content="Content with <html> & \"quotes\"",
                url="https://x.com/atomuser/status/1",
                confidence=0.85,
            ),
            DataPulseItem(
                source_type=SourceType.GENERIC,
                source_name="example",
                title="Second Entry",
                content="More content here",
                url="https://example.com/page2",
                confidence=0.70,
            ),
        ]
        _populate_inbox(inbox_path, items)

        os.environ["DATAPULSE_SOURCE_CATALOG"] = catalog_path
        reader = DataPulseReader(inbox_path=inbox_path)
        yield reader
        os.environ.pop("DATAPULSE_SOURCE_CATALOG", None)

    def test_atom_well_formed_xml(self, reader_with_items):
        xml_str = reader_with_items.build_atom_feed()
        root = ET.fromstring(xml_str)
        assert root.tag == "{http://www.w3.org/2005/Atom}feed"

    def test_atom_namespace(self, reader_with_items):
        xml_str = reader_with_items.build_atom_feed()
        assert 'xmlns="http://www.w3.org/2005/Atom"' in xml_str

    def test_atom_entries_present(self, reader_with_items):
        xml_str = reader_with_items.build_atom_feed()
        root = ET.fromstring(xml_str)
        ns = {"atom": "http://www.w3.org/2005/Atom"}
        entries = root.findall("atom:entry", ns)
        assert len(entries) >= 1

    def test_atom_xml_escaping(self, reader_with_items):
        xml_str = reader_with_items.build_atom_feed()
        # Should parse without error (valid XML)
        root = ET.fromstring(xml_str)
        ns = {"atom": "http://www.w3.org/2005/Atom"}
        entry = root.find("atom:entry", ns)
        title = entry.find("atom:title", ns).text
        assert "<" not in title  # properly escaped

    def test_atom_limit(self, reader_with_items):
        xml_str = reader_with_items.build_atom_feed(limit=1)
        root = ET.fromstring(xml_str)
        ns = {"atom": "http://www.w3.org/2005/Atom"}
        entries = root.findall("atom:entry", ns)
        assert len(entries) <= 1

    def test_atom_entry_has_required_fields(self, reader_with_items):
        xml_str = reader_with_items.build_atom_feed()
        root = ET.fromstring(xml_str)
        ns = {"atom": "http://www.w3.org/2005/Atom"}
        entry = root.find("atom:entry", ns)
        assert entry.find("atom:title", ns) is not None
        assert entry.find("atom:link", ns) is not None
        assert entry.find("atom:id", ns) is not None
        assert entry.find("atom:updated", ns) is not None
        assert entry.find("atom:summary", ns) is not None
        assert entry.find("atom:author/atom:name", ns) is not None

    def test_atom_id_uses_urn(self, reader_with_items):
        xml_str = reader_with_items.build_atom_feed()
        root = ET.fromstring(xml_str)
        ns = {"atom": "http://www.w3.org/2005/Atom"}
        entry = root.find("atom:entry", ns)
        entry_id = entry.find("atom:id", ns).text
        assert entry_id.startswith("urn:datapulse:")
