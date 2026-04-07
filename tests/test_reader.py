"""Tests for DataPulseReader feed generation."""

import asyncio
import json
import xml.etree.ElementTree as ET

import pytest

import datapulse.reader as reader_module
from datapulse.core.models import DataPulseItem, SourceType
from datapulse.core.search_gateway import SearchHit
from datapulse.reader import DataPulseReader


@pytest.fixture(autouse=True)
def _cleanup_env():
    import os

    yield
    os.environ.pop("DATAPULSE_SOURCE_CATALOG", None)
    os.environ.pop("DATAPULSE_STORIES_PATH", None)
    os.environ.pop("DATAPULSE_REPORTS_PATH", None)
    os.environ.pop("DATAPULSE_MEMORY_DIR", None)
    os.environ.pop("DATAPULSE_AI_SURFACE_ADMISSION_PATH", None)
    os.environ.pop("DATAPULSE_MODELBUS_BUNDLE_DIR", None)
    os.environ.pop("DATAPULSE_RUNTIME_BUNDLE_ROOT", None)
    os.environ.pop("DATAPULSE_GOVERNANCE_SNAPSHOT_ROOT", None)
    os.environ.pop("DATAPULSE_EVIDENCE_BUNDLE_ROOT", None)


def _populate_inbox(inbox_path: str, items: list[DataPulseItem]) -> None:
    """Write items to an inbox file."""
    from pathlib import Path

    payload = [item.to_dict() for item in items]
    Path(inbox_path).write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")


def _write_local_ai_surface_admission(path, rows):
    from pathlib import Path

    Path(path).write_text(
        json.dumps(
            {
                "schema_version": "datapulse_ai_surface_admission.v1",
                "generated_at_utc": "2026-03-16T12:00:00Z",
                "surface_admissions": rows,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )


def _write_modelbus_bundle(bundle_dir, rows):
    from pathlib import Path

    bundle_dir = Path(bundle_dir)
    bundle_dir.mkdir(parents=True, exist_ok=True)
    (bundle_dir / "bundle_manifest.json").write_text(
        json.dumps(
            {
                "schema": "modelbus.consumer_bundle_manifest.v1",
                "generated_at_utc": "2026-03-16T12:10:00Z",
                "bundle_id": "datapulse.ai_surface_bus",
                "consumer_id": "datapulse",
                "artifacts": {
                    "surface_admission": {"path": "surface_admission.json"},
                    "bridge_config": {"path": "bridge_config.json"},
                    "release_status": {"path": "release_status.json"},
                },
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    (bundle_dir / "surface_admission.json").write_text(
        json.dumps(
            {
                "schema": "modelbus.consumer_surface_admission.v1",
                "generated_at_utc": "2026-03-16T12:11:00Z",
                "consumer_id": "datapulse",
                "release_window": {
                    "generated_at_utc": "2026-03-16T12:09:00Z",
                    "release_level": "inescapable",
                    "assured_verdict": "pass",
                    "constitutional_semantics": "CONSTRAINED-DEPLOYED",
                },
                "surface_admissions": rows,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    (bundle_dir / "bridge_config.json").write_text(
        json.dumps(
            {
                "schema": "modelbus.consumer_bridge_config.v1",
                "generated_at_utc": "2026-03-16T12:12:00Z",
                "consumer_id": "datapulse",
                "bundle_id": "datapulse.ai_surface_bus",
                "base_url": "https://modelbus.example.com",
                "request_protocol": "responses",
                "endpoint": "/v1/responses",
                "bus_key_env": "DATAPULSE_MODELBUS_BUS_KEY",
                "tenant_env": "DATAPULSE_MODELBUS_TENANT",
                "tenant_header": "X-ModelBus-Tenant",
                "alias_by_surface": {
                    "mission_suggest": "dp.mission.suggest",
                    "report_draft": "dp.report.draft",
                },
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    (bundle_dir / "release_status.json").write_text(
        json.dumps(
            {
                "schema": "modelbus.release_status.v1",
                "generated_at_utc": "2026-03-16T12:09:00Z",
                "release_level": "inescapable",
                "assured_verdict": "pass",
                "runtime": {"base_url": "https://modelbus.example.com"},
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )


def test_reader_initializes_domain_service_facades(tmp_path):
    inbox_path = str(tmp_path / "reader-services.json")
    reader = DataPulseReader(inbox_path=inbox_path)

    assert reader.watch_service.owner is reader
    assert reader.triage_service.triage is reader.triage
    assert reader.story_service.owner is reader
    assert reader.report_service.owner is reader
    assert reader.alert_service.owner is reader
    assert reader.ai_service.owner is reader


def _write_source_catalog(path: str) -> None:
    from pathlib import Path

    Path(path).write_text(
        json.dumps(
            {
                "version": 1,
                "sources": [],
                "subscriptions": {},
                "packs": [],
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )


class TestBuildJsonFeed:
    @pytest.fixture()
    def reader_with_items(self, tmp_path):
        inbox_path = str(tmp_path / "inbox.json")
        catalog_path = str(tmp_path / "catalog.json")
        # Write empty catalog
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

    def test_json_feed_includes_trend_seed_context(self, tmp_path, monkeypatch):
        inbox_path = str(tmp_path / "inbox.json")
        catalog_path = str(tmp_path / "catalog.json")
        watch_path = str(tmp_path / "watchlist.json")
        from pathlib import Path

        Path(catalog_path).write_text(json.dumps({
            "version": 1, "sources": [], "subscriptions": {}, "packs": [],
        }), encoding="utf-8")

        monkeypatch.setenv("DATAPULSE_SOURCE_CATALOG", catalog_path)
        monkeypatch.setenv("DATAPULSE_WATCHLIST_PATH", watch_path)

        seed_reader = DataPulseReader(inbox_path=inbox_path)
        mission = seed_reader.create_watch(
            name="AI Trend Watch",
            query="OpenAI agents",
            trend_inputs=[
                {
                    "provider": "trends24",
                    "label": "US AI trend seeds",
                    "location": "united-states",
                    "topics": ["#OpenAI", "Claude Code"],
                    "feed_url": "https://trends24.in/united-states/",
                    "snapshot_time": "2026-03-06T00:00:00Z",
                }
            ],
        )

        items = [
            DataPulseItem(
                source_type=SourceType.GENERIC,
                source_name="example",
                title="Watch-seeded evidence",
                content="Collected URL evidence remains separate from trend seeds.",
                url="https://example.com/openai-agents",
                confidence=0.88,
                extra={"watch_mission_id": mission["id"], "watch_mission_name": mission["name"]},
            ),
        ]
        _populate_inbox(inbox_path, items)

        reader = DataPulseReader(inbox_path=inbox_path)
        feed = reader.build_json_feed()

        assert feed["datapulse_context"]["trend_seeded_item_count"] == 1
        assert feed["datapulse_context"]["trend_seeded_watch_count"] == 1
        assert "item-level evidence" in feed["datapulse_context"]["seed_boundary"]
        assert feed["items"][0]["datapulse_context"]["trend_seeded"] is True
        assert feed["items"][0]["datapulse_context"]["seed_inputs"][0]["input_kind"] == "trend_feed"


class TestFeedBundleAndDigestPayload:
    def test_feed_bundle_freezes_membership_and_source_scope(self, tmp_path, monkeypatch):
        inbox_path = str(tmp_path / "inbox.json")
        catalog_path = str(tmp_path / "catalog.json")
        from pathlib import Path

        Path(catalog_path).write_text(
            json.dumps(
                {
                    "version": 1,
                    "sources": [
                        {
                            "id": "source_example",
                            "name": "Example Source",
                            "source_type": "generic",
                            "config": {"url": "https://example.com"},
                            "match": {"domain": "example.com"},
                            "is_active": True,
                            "is_public": True,
                        }
                    ],
                    "subscriptions": {"default": ["source_example"]},
                    "packs": [],
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        monkeypatch.setenv("DATAPULSE_SOURCE_CATALOG", catalog_path)

        items = [
            DataPulseItem(
                source_type=SourceType.GENERIC,
                source_name="example",
                title="Newer item",
                content="Newer content",
                url="https://example.com/newer",
                confidence=0.9,
                fetched_at="2026-03-20T12:00:00+00:00",
            ),
            DataPulseItem(
                source_type=SourceType.GENERIC,
                source_name="example",
                title="Older item",
                content="Older content",
                url="https://example.com/older",
                confidence=0.8,
                fetched_at="2026-03-19T10:00:00+00:00",
            ),
        ]
        _populate_inbox(inbox_path, items)

        reader = DataPulseReader(inbox_path=inbox_path)
        bundle = reader.build_feed_bundle(profile="default", limit=10)

        assert bundle["schema_version"] == "feed_bundle.v1"
        assert bundle["selection"]["profile"] == "default"
        assert bundle["selection"]["source_ids_requested"] == []
        assert bundle["selection"]["source_ids_resolved"] == ["source_example"]
        assert [item["title"] for item in bundle["items"]] == ["Newer item", "Older item"]
        assert bundle["window"]["oldest_fetched_at"] == "2026-03-19T10:00:00Z"
        assert bundle["window"]["newest_fetched_at"] == "2026-03-20T12:00:00Z"
        assert bundle["stats"]["items_selected"] == 2
        assert bundle["stats"]["sources_selected"] == 1
        assert bundle["errors"] == []

    def test_prepare_digest_payload_projects_shared_config_and_prompt_provenance(self, tmp_path, monkeypatch):
        inbox_path = str(tmp_path / "inbox.json")
        catalog_path = str(tmp_path / "catalog.json")
        prompt_path = tmp_path / "digest_override.md"
        from pathlib import Path

        Path(catalog_path).write_text(
            json.dumps(
                {
                    "version": 1,
                    "sources": [
                        {
                            "id": "source_example",
                            "name": "Example Source",
                            "source_type": "generic",
                            "config": {"url": "https://example.com"},
                            "match": {"domain": "example.com"},
                            "is_active": True,
                            "is_public": True,
                        }
                    ],
                    "subscriptions": {"default": ["source_example"]},
                    "packs": [],
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        prompt_path.write_text("Digest override prompt", encoding="utf-8")
        monkeypatch.setenv("DATAPULSE_SOURCE_CATALOG", catalog_path)

        items = [
            DataPulseItem(
                source_type=SourceType.GENERIC,
                source_name="example",
                title="Signal 1",
                content="Signal 1 content",
                url="https://example.com/1",
                confidence=0.95,
                fetched_at="2026-03-20T12:00:00+00:00",
            ),
            DataPulseItem(
                source_type=SourceType.GENERIC,
                source_name="example",
                title="Signal 2",
                content="Signal 2 content",
                url="https://example.com/2",
                confidence=0.88,
                fetched_at="2026-03-19T10:00:00+00:00",
            ),
        ]
        _populate_inbox(inbox_path, items)

        reader = DataPulseReader(inbox_path=inbox_path)
        payload = reader.prepare_digest_payload(
            profile="default",
            limit=10,
            top_n=1,
            secondary_n=1,
            digest_language="zh-CN",
            digest_timezone="Asia/Shanghai",
            digest_frequency="@hourly",
            digest_delivery_target_kind="route",
            digest_delivery_target_ref="ops-webhook",
            prompt_files=[str(prompt_path)],
        )

        assert payload["schema_version"] == "prepare_digest_payload.v1"
        assert payload["content"]["feed_bundle"]["schema_version"] == "feed_bundle.v1"
        assert payload["config"]["source_ids"] == ["source_example"]
        assert payload["config"]["digest_profile"]["language"] == "zh-CN"
        assert payload["config"]["digest_profile"]["timezone"] == "Asia/Shanghai"
        assert payload["config"]["digest_profile"]["frequency"] == "@hourly"
        assert payload["config"]["digest_profile"]["default_delivery_target"] == {"kind": "route", "ref": "ops-webhook"}
        assert payload["prompts"]["repo_default_pack"] == "digest_delivery_default"
        assert payload["prompts"]["overrides_applied"] == ["per_run_overrides"]
        assert str(prompt_path.resolve()) in payload["prompts"]["files"]
        assert payload["stats"]["delivery_package"]["item_count"] == 2
        assert payload["errors"] == []


class TestBuildRssFeed:
    @pytest.fixture()
    def reader_with_items(self, tmp_path):
        inbox_path = str(tmp_path / "inbox.json")
        catalog_path = str(tmp_path / "catalog.json")
        import os
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
        import os
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
        assert "&lt;" in xml_str
        assert "&amp;" in xml_str
        # Should parse without error (valid XML)
        root = ET.fromstring(xml_str)
        ns = {"atom": "http://www.w3.org/2005/Atom"}
        entry = root.find("atom:entry", ns)
        title = entry.find("atom:title", ns).text
        assert title == "Atom Test <Item> & More"

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


def test_search_audit_includes_qnaigc_candidate_fallback(tmp_path, monkeypatch):
    inbox_path = str(tmp_path / "inbox.json")
    catalog_path = str(tmp_path / "catalog.json")
    _write_source_catalog(catalog_path)
    monkeypatch.setenv("DATAPULSE_SOURCE_CATALOG", catalog_path)

    reader = DataPulseReader(inbox_path=inbox_path)

    def fake_search(
        query: str,
        *,
        sites: list[str] | None,
        limit: int,
        provider: str,
        mode: str,
        deep: bool,
        news: bool,
        time_range: str | None = None,
        provider_hints: list[str] | None = None,
    ):
        return [
            SearchHit(
                title="人工点火样例",
                url="https://example.com/china-ai",
                snippet="Sample snippet.",
                provider="tavily",
                source="tavily",
                score=0.7,
                raw={},
                extra={"sources": ["tavily"]},
            )
        ], {
            "query": query,
            "mode": mode,
            "requested_query": query,
            "effective_query": query,
            "provider_chain": ["qnaigc", "tavily"],
            "attempts": [
                {
                    "provider": "qnaigc",
                    "status": "error",
                    "count": 0,
                    "latency_ms": 0.0,
                    "retry_count": 0,
                    "attempts": 0,
                    "error": "QNAIGC rate limit",
                    "estimated_cost": 0.036,
                },
                {
                    "provider": "tavily",
                    "status": "ok",
                    "count": 1,
                    "latency_ms": 0.0,
                    "retry_count": 0,
                    "attempts": 0,
                    "estimated_cost": 0.0,
                },
            ],
            "estimated_cost_total": 0.036,
            "providers_selected": 2,
            "providers_with_hit": 1,
            "provider_count": 1,
            "fallback_applied": True,
            "fallback_reason": "rate limit",
            "requested_provider": provider,
            "effective_provider": "tavily",
        }

    monkeypatch.setattr(reader._search_gateway, "search", fake_search)
    items = asyncio.run(
        reader.search(
            "中文 技术",
            provider="qnaigc",
            limit=3,
            fetch_content=False,
        )
    )

    assert len(items) == 1
    audit = items[0].extra.get("search_audit", {})
    assert audit["provider_chain"] == ["qnaigc", "tavily"]
    assert audit["attempts"][0]["provider"] == "qnaigc"
    assert audit["attempts"][0]["status"] == "error"
    assert audit["estimated_cost_total"] == 0.036
    assert audit["fallback_applied"] is True


def test_search_planning_applies_chinese_query_hints(tmp_path, monkeypatch):
    from pathlib import Path

    inbox_path = str(tmp_path / "inbox.json")
    catalog_path = str(tmp_path / "catalog.json")
    Path(catalog_path).write_text(json.dumps({
        "version": 1, "sources": [], "subscriptions": {}, "packs": [],
    }), encoding="utf-8")
    monkeypatch.setenv("DATAPULSE_SOURCE_CATALOG", catalog_path)

    reader = DataPulseReader(inbox_path=inbox_path)
    captured: dict[str, object] = {}

    def fake_search(
        query: str,
        *,
        sites: list[str] | None,
        limit: int,
        provider: str,
        mode: str,
        deep: bool,
        news: bool,
        time_range: str | None = None,
        provider_hints: list[str] | None = None,
    ):
        captured["query"] = query
        captured["sites"] = list(sites or [])
        captured["provider"] = provider
        captured["mode"] = mode
        captured["deep"] = deep
        captured["news"] = news
        captured["time_range"] = time_range
        captured["provider_hints"] = list(provider_hints or [])
        return [
            SearchHit(
                title="小红书 AI 工具盘点",
                url="https://www.xiaohongshu.com/explore/123",
                snippet="Sample snippet.",
                provider="qnaigc",
                source="qnaigc",
                score=0.8,
                raw={},
                extra={"sources": ["qnaigc"]},
            )
        ], {
            "query": query,
            "mode": mode,
            "provider_chain": ["qnaigc", "tavily", "jina"],
            "attempts": [],
        }

    monkeypatch.setattr(reader._search_gateway, "search", fake_search)
    items = asyncio.run(
        reader.search(
            "小红书 AI 工具 最新",
            provider="auto",
            limit=3,
            fetch_content=False,
        )
    )

    assert len(items) == 1
    assert captured["provider_hints"] == ["qnaigc", "tavily"]
    assert captured["news"] is True
    assert captured["time_range"] == "week"
    assert "xiaohongshu.com" in captured["sites"]
    audit = items[0].extra.get("search_audit", {})
    assert audit["planning"]["language"] == "mixed"
    assert audit["planning"]["intent_kind"] == "news"
    assert audit["planning"]["chinese_relevance_uplift"] is True


def test_create_watch_applies_platform_and_site_hints_from_query(tmp_path, monkeypatch):
    from pathlib import Path

    inbox_path = str(tmp_path / "inbox.json")
    catalog_path = str(tmp_path / "catalog.json")
    watch_path = str(tmp_path / "watchlist.json")
    Path(catalog_path).write_text(json.dumps({
        "version": 1, "sources": [], "subscriptions": {}, "packs": [],
    }), encoding="utf-8")
    monkeypatch.setenv("DATAPULSE_SOURCE_CATALOG", catalog_path)
    monkeypatch.setenv("DATAPULSE_WATCHLIST_PATH", str(watch_path))

    reader = DataPulseReader(inbox_path=inbox_path)
    mission = reader.create_watch(
        name="CN Search Watch",
        query="小红书 AI 工具 site:36kr.com",
    )

    assert mission["platforms"] == ["xhs"]
    assert mission["sites"] == ["36kr.com"]


def test_ai_surface_precheck_rejects_report_draft_without_contract(tmp_path, monkeypatch):
    from pathlib import Path

    inbox_path = str(tmp_path / "inbox.json")
    catalog_path = str(tmp_path / "catalog.json")
    Path(catalog_path).write_text(json.dumps({
        "version": 1, "sources": [], "subscriptions": {}, "packs": [],
    }), encoding="utf-8")
    monkeypatch.setenv("DATAPULSE_SOURCE_CATALOG", catalog_path)

    reader = DataPulseReader(inbox_path=inbox_path)
    payload = reader.ai_surface_precheck("report_draft", mode="assist")

    assert payload["ok"] is False
    assert payload["mode_status"] == "rejected"
    assert payload["admission_status"] == "rejected"
    assert payload["contract_id"] == ""
    assert payload["contract_available"] is False
    assert payload["manual_fallback"] == "manual_or_deterministic_behavior"


def test_ai_surface_precheck_prefers_modelbus_bundle_when_present(tmp_path, monkeypatch):
    from pathlib import Path

    inbox_path = str(tmp_path / "inbox.json")
    catalog_path = str(tmp_path / "catalog.json")
    Path(catalog_path).write_text(json.dumps({
        "version": 1, "sources": [], "subscriptions": {}, "packs": [],
    }), encoding="utf-8")
    monkeypatch.setenv("DATAPULSE_SOURCE_CATALOG", catalog_path)

    bundle_dir = tmp_path / "modelbus-bundle"
    _write_modelbus_bundle(
        bundle_dir,
        [
            {
                "surface_id": "mission_suggest",
                "requested_alias": "dp.mission.suggest",
                "admission_status": "admitted",
                "admitted_alias": "dp.mission.suggest",
                "mode_admission": {"off": "manual_only", "assist": "admitted", "review": "admitted"},
                "schema_contract": "datapulse_ai_watch_suggestion.v1",
                "manual_fallback": "manual_or_deterministic_behavior",
                "degraded_result_allowed": True,
                "must_expose_runtime_facts": [
                    "served_by_alias",
                    "fallback_used",
                    "degraded",
                    "schema_valid",
                    "manual_override_required",
                ],
                "rejectable_gaps": [],
            }
        ],
    )
    monkeypatch.setenv("DATAPULSE_MODELBUS_BUNDLE_DIR", str(bundle_dir))

    reader = DataPulseReader(inbox_path=inbox_path)
    payload = reader.ai_surface_precheck("mission_suggest", mode="review")

    assert payload["ok"] is True
    assert payload["mode_status"] == "admitted"
    assert payload["alias"] == "dp.mission.suggest"
    assert payload["bridge_configured"] is True
    assert payload["admission_source"] == "modelbus_bundle"
    assert payload["admission_path"].endswith("surface_admission.json")
    assert payload["contract_id"] == "datapulse_ai_watch_suggestion.v1"
    assert payload["degraded_result_allowed"] is True
    assert payload["admission_errors"] == []


def test_ai_surface_precheck_prefers_explicit_env_bundle_over_canonical_default(tmp_path, monkeypatch):
    from pathlib import Path

    inbox_path = str(tmp_path / "inbox.json")
    catalog_path = str(tmp_path / "catalog.json")
    Path(catalog_path).write_text(json.dumps({
        "version": 1, "sources": [], "subscriptions": {}, "packs": [],
    }), encoding="utf-8")
    monkeypatch.setenv("DATAPULSE_SOURCE_CATALOG", catalog_path)

    canonical_dir = tmp_path / "ha_latest_release_bundle"
    env_dir = tmp_path / "explicit-modelbus-bundle"
    _write_modelbus_bundle(
        canonical_dir,
        [
            {
                "surface_id": "mission_suggest",
                "admission_status": "admitted",
                "admitted_alias": "dp.canonical.mission.suggest",
                "mode_admission": {"off": "manual_only", "assist": "admitted", "review": "admitted"},
                "schema_contract": "datapulse_ai_watch_suggestion.v1",
                "manual_fallback": "manual_or_deterministic_behavior",
                "degraded_result_allowed": True,
                "must_expose_runtime_facts": ["served_by_alias", "fallback_used", "degraded", "schema_valid", "manual_override_required"],
                "rejectable_gaps": [],
            }
        ],
    )
    _write_modelbus_bundle(
        env_dir,
        [
            {
                "surface_id": "mission_suggest",
                "admission_status": "admitted",
                "admitted_alias": "dp.env.mission.suggest",
                "mode_admission": {"off": "manual_only", "assist": "admitted", "review": "admitted"},
                "schema_contract": "datapulse_ai_watch_suggestion.v1",
                "manual_fallback": "manual_or_deterministic_behavior",
                "degraded_result_allowed": True,
                "must_expose_runtime_facts": ["served_by_alias", "fallback_used", "degraded", "schema_valid", "manual_override_required"],
                "rejectable_gaps": [],
            }
        ],
    )
    monkeypatch.setenv("DATAPULSE_RUNTIME_BUNDLE_ROOT", str(canonical_dir))
    monkeypatch.setenv("DATAPULSE_MODELBUS_BUNDLE_DIR", str(env_dir))

    reader = DataPulseReader(inbox_path=inbox_path)
    payload = reader.ai_surface_precheck("mission_suggest", mode="review")

    assert payload["ok"] is True
    assert payload["alias"] == "dp.env.mission.suggest"
    assert payload["admission_source"] == "modelbus_bundle"
    assert payload["bundle_selection"] == "explicit_env"
    assert payload["admission_errors"] == []


def test_ai_surface_precheck_uses_canonical_bundle_when_env_is_not_set(tmp_path, monkeypatch):
    from pathlib import Path

    inbox_path = str(tmp_path / "inbox.json")
    catalog_path = str(tmp_path / "catalog.json")
    Path(catalog_path).write_text(json.dumps({
        "version": 1, "sources": [], "subscriptions": {}, "packs": [],
    }), encoding="utf-8")
    monkeypatch.setenv("DATAPULSE_SOURCE_CATALOG", catalog_path)

    admission_path = tmp_path / "local-ai-surface-admission.json"
    _write_local_ai_surface_admission(
        admission_path,
        [
            {
                "surface": "mission_suggest",
                "lifecycle_anchor": "WatchMission",
                "required_output_kind": "suggestion",
                "required_schema_contract": "datapulse_ai_watch_suggestion.v1",
                "admission_status": "admitted",
                "mode_admission": {"off": "manual_only", "assist": "admitted", "review": "admitted"},
                "admitted_subscription_id": "mission_suggest.local",
                "admitted_alias": "dp.local.mission.suggest",
                "candidate_results": [{"subscription_id": "mission_suggest.local", "degraded_result_allowed": False}],
                "must_expose_runtime_facts": ["served_by_alias", "fallback_used", "degraded", "schema_valid", "manual_override_required"],
                "rejectable_gaps": [],
                "manual_fallback": "manual_or_deterministic_behavior",
            }
        ],
    )
    monkeypatch.setenv("DATAPULSE_AI_SURFACE_ADMISSION_PATH", str(admission_path))

    canonical_dir = tmp_path / "ha_latest_release_bundle"
    _write_modelbus_bundle(
        canonical_dir,
        [
            {
                "surface_id": "mission_suggest",
                "admission_status": "admitted",
                "admitted_alias": "dp.canonical.mission.suggest",
                "mode_admission": {"off": "manual_only", "assist": "admitted", "review": "admitted"},
                "schema_contract": "datapulse_ai_watch_suggestion.v1",
                "manual_fallback": "manual_or_deterministic_behavior",
                "degraded_result_allowed": True,
                "must_expose_runtime_facts": ["served_by_alias", "fallback_used", "degraded", "schema_valid", "manual_override_required"],
                "rejectable_gaps": [],
            }
        ],
    )
    monkeypatch.setattr(
        reader_module,
        "resolve_root_candidate_entries",
        lambda resolver_name, repo_root=None: [
            {"path": canonical_dir.resolve(), "source": "canonical_root", "resolver_name": resolver_name}
        ],
    )

    reader = DataPulseReader(inbox_path=inbox_path)
    payload = reader.ai_surface_precheck("mission_suggest", mode="assist")

    assert payload["ok"] is True
    assert payload["alias"] == "dp.canonical.mission.suggest"
    assert payload["admission_source"] == "modelbus_bundle"
    assert payload["bundle_selection"] == "canonical_default"
    assert payload["admission_errors"] == []


def test_ai_surface_precheck_rejects_when_bundle_is_invalid_and_local_snapshot_is_diagnostic_only(tmp_path, monkeypatch):
    from pathlib import Path

    inbox_path = str(tmp_path / "inbox.json")
    catalog_path = str(tmp_path / "catalog.json")
    Path(catalog_path).write_text(json.dumps({
        "version": 1, "sources": [], "subscriptions": {}, "packs": [],
    }), encoding="utf-8")
    monkeypatch.setenv("DATAPULSE_SOURCE_CATALOG", catalog_path)

    bundle_dir = tmp_path / "broken-modelbus-bundle"
    bundle_dir.mkdir(parents=True, exist_ok=True)
    monkeypatch.setenv("DATAPULSE_MODELBUS_BUNDLE_DIR", str(bundle_dir))
    monkeypatch.setattr(
        reader_module,
        "resolve_root_candidate_entries",
        lambda resolver_name, repo_root=None: [
            {"path": (tmp_path / "missing-canonical-bundle").resolve(), "source": "canonical_root", "resolver_name": resolver_name}
        ],
    )

    admission_path = tmp_path / "local-ai-surface-admission.json"
    _write_local_ai_surface_admission(
        admission_path,
        [
            {
                "surface": "mission_suggest",
                "lifecycle_anchor": "WatchMission",
                "required_output_kind": "suggestion",
                "required_schema_contract": "datapulse_ai_watch_suggestion.v1",
                "admission_status": "admitted",
                "mode_admission": {"off": "manual_only", "assist": "admitted", "review": "admitted"},
                "admitted_subscription_id": "mission_suggest.local",
                "admitted_alias": "dp.local.mission.suggest",
                "must_expose_runtime_facts": [
                    "served_by_alias",
                    "fallback_used",
                    "degraded",
                    "schema_valid",
                    "manual_override_required",
                ],
                "candidate_results": [
                    {
                        "subscription_id": "mission_suggest.local",
                        "degraded_result_allowed": False,
                    }
                ],
                "rejectable_gaps": [],
                "manual_fallback": "manual_or_deterministic_behavior",
            }
        ],
    )
    monkeypatch.setenv("DATAPULSE_AI_SURFACE_ADMISSION_PATH", str(admission_path))

    reader = DataPulseReader(inbox_path=inbox_path)
    payload = reader.ai_surface_precheck("mission_suggest", mode="assist")

    assert payload["ok"] is False
    assert payload["alias"] == ""
    assert payload["bridge_configured"] is False
    assert payload["admission_source"] == "modelbus_bundle_required"
    assert payload["admission_path"].endswith("bundle_manifest.json")
    assert payload["admission_errors"]
    assert payload["admission_errors"][0].startswith("explicit env bundle failed: modelbus bundle manifest missing:")
    assert any(
        "local snapshot available but disabled under bundle-first default:" in error
        for error in payload["admission_errors"]
    )


def test_ai_surface_precheck_rejects_when_canonical_bundle_is_invalid_even_if_local_snapshot_exists(tmp_path, monkeypatch):
    from pathlib import Path

    inbox_path = str(tmp_path / "inbox.json")
    catalog_path = str(tmp_path / "catalog.json")
    Path(catalog_path).write_text(json.dumps({
        "version": 1, "sources": [], "subscriptions": {}, "packs": [],
    }), encoding="utf-8")
    monkeypatch.setenv("DATAPULSE_SOURCE_CATALOG", catalog_path)

    admission_path = tmp_path / "local-ai-surface-admission.json"
    _write_local_ai_surface_admission(
        admission_path,
        [
            {
                "surface": "mission_suggest",
                "lifecycle_anchor": "WatchMission",
                "required_output_kind": "suggestion",
                "required_schema_contract": "datapulse_ai_watch_suggestion.v1",
                "admission_status": "admitted",
                "mode_admission": {"off": "manual_only", "assist": "admitted", "review": "admitted"},
                "admitted_subscription_id": "mission_suggest.local",
                "admitted_alias": "dp.local.mission.suggest",
                "candidate_results": [{"subscription_id": "mission_suggest.local", "degraded_result_allowed": False}],
                "must_expose_runtime_facts": ["served_by_alias", "fallback_used", "degraded", "schema_valid", "manual_override_required"],
                "rejectable_gaps": [],
                "manual_fallback": "manual_or_deterministic_behavior",
            }
        ],
    )
    monkeypatch.setenv("DATAPULSE_AI_SURFACE_ADMISSION_PATH", str(admission_path))

    canonical_dir = tmp_path / "ha_latest_release_bundle"
    canonical_dir.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(
        reader_module,
        "resolve_root_candidate_entries",
        lambda resolver_name, repo_root=None: [
            {"path": canonical_dir.resolve(), "source": "canonical_root", "resolver_name": resolver_name}
        ],
    )

    reader = DataPulseReader(inbox_path=inbox_path)
    payload = reader.ai_surface_precheck("mission_suggest", mode="assist")

    assert payload["ok"] is False
    assert payload["alias"] == ""
    assert payload["admission_source"] == "modelbus_bundle_required"
    assert payload["bundle_selection"] == "canonical_default"
    assert payload["admission_errors"]
    assert payload["admission_errors"][0].startswith("canonical bundle failed:")
    assert any(
        "local snapshot available but disabled under bundle-first default:" in error
        for error in payload["admission_errors"]
    )


def test_ai_surface_precheck_keeps_report_draft_fail_closed_under_modelbus_bundle(tmp_path, monkeypatch):
    from pathlib import Path

    inbox_path = str(tmp_path / "inbox.json")
    catalog_path = str(tmp_path / "catalog.json")
    Path(catalog_path).write_text(json.dumps({
        "version": 1, "sources": [], "subscriptions": {}, "packs": [],
    }), encoding="utf-8")
    monkeypatch.setenv("DATAPULSE_SOURCE_CATALOG", catalog_path)

    bundle_dir = tmp_path / "modelbus-bundle"
    _write_modelbus_bundle(
        bundle_dir,
        [
            {
                "surface_id": "report_draft",
                "requested_alias": "dp.report.draft",
                "admission_status": "rejected",
                "admitted_alias": "",
                "mode_admission": {"off": "manual_only", "assist": "rejected", "review": "rejected"},
                "schema_contract": None,
                "manual_fallback": "manual_or_deterministic_behavior",
                "degraded_result_allowed": False,
                "must_expose_runtime_facts": [
                    "served_by_alias",
                    "fallback_used",
                    "degraded",
                    "schema_valid",
                    "manual_override_required",
                ],
                "rejectable_gaps": [
                    {
                        "gap_id": "missing_structured_contract",
                        "blocking": True,
                        "reason": "surface is blocked_until_contract and has no admitted structured contract",
                    }
                ],
            }
        ],
    )
    monkeypatch.setenv("DATAPULSE_MODELBUS_BUNDLE_DIR", str(bundle_dir))

    reader = DataPulseReader(inbox_path=inbox_path)
    payload = reader.ai_surface_precheck("report_draft", mode="assist")

    assert payload["ok"] is False
    assert payload["mode_status"] == "rejected"
    assert payload["admission_status"] == "rejected"
    assert payload["bridge_configured"] is True
    assert payload["admission_source"] == "modelbus_bundle"
    assert payload["alias"] == "dp.report.draft"
    assert payload["requested_alias"] == "dp.report.draft"
    assert payload["contract_id"] == ""
    assert payload["contract_available"] is False
    assert payload["manual_fallback"] == "manual_or_deterministic_behavior"
    assert payload["rejectable_gaps"][0]["gap_id"] == "missing_structured_contract"


def test_ai_mission_suggest_returns_governed_payload_without_mutation(tmp_path, monkeypatch):
    from pathlib import Path

    inbox_path = str(tmp_path / "inbox.json")
    catalog_path = str(tmp_path / "catalog.json")
    watch_path = str(tmp_path / "watchlist.json")
    Path(catalog_path).write_text(json.dumps({
        "version": 1, "sources": [], "subscriptions": {}, "packs": [],
    }), encoding="utf-8")
    monkeypatch.setenv("DATAPULSE_SOURCE_CATALOG", catalog_path)
    monkeypatch.setenv("DATAPULSE_WATCHLIST_PATH", str(watch_path))

    reader = DataPulseReader(inbox_path=inbox_path)
    mission = reader.create_watch(
        name="AI Assist Watch",
        query="edge inference launch",
        mission_intent={
            "scope_entities": ["Acme"],
            "scope_topics": ["launch"],
            "scope_regions": ["us"],
        },
        sites=["example.com"],
        schedule="@hourly",
    )
    before = reader.show_watch(mission["id"])

    payload = reader.ai_mission_suggest(mission["id"], mode="assist")
    after = reader.show_watch(mission["id"])

    assert payload is not None
    assert payload["precheck"]["mode_status"] == "admitted"
    assert payload["output"]["contract_id"] == "datapulse_ai_watch_suggestion.v1"
    assert payload["output"]["payload"]["proposed_query"] == "edge inference launch"
    assert payload["output"]["payload"]["research_projection"]["source_plan"]["summary"]
    assert payload["output"]["payload"]["research_projection"]["coverage_gap"]["status"] in {"clear", "watch", "review_required", "blocked"}
    assert payload["output"]["payload"]["run_readiness"]["status"] in {"ready", "needs_review", "blocked"}
    assert payload["runtime_facts"]["source"] == "deterministic"
    assert payload["runtime_facts"]["schema_valid"] is True
    assert before["research_projection"]["source_plan"]["summary"]
    assert after["research_projection"]["coverage_gap"]["status"] in {"clear", "watch", "review_required", "blocked"}
    assert before["updated_at"] == after["updated_at"]


def test_ai_mission_suggest_off_mode_short_circuits(tmp_path, monkeypatch):
    from pathlib import Path

    inbox_path = str(tmp_path / "inbox.json")
    catalog_path = str(tmp_path / "catalog.json")
    watch_path = str(tmp_path / "watchlist.json")
    Path(catalog_path).write_text(json.dumps({
        "version": 1, "sources": [], "subscriptions": {}, "packs": [],
    }), encoding="utf-8")
    monkeypatch.setenv("DATAPULSE_SOURCE_CATALOG", catalog_path)
    monkeypatch.setenv("DATAPULSE_WATCHLIST_PATH", str(watch_path))

    reader = DataPulseReader(inbox_path=inbox_path)
    mission = reader.create_watch(name="Manual Watch", query="manual trigger only")

    payload = reader.ai_mission_suggest(mission["id"], mode="off")

    assert payload is not None
    assert payload["precheck"]["mode"] == "off"
    assert payload["output"] is None
    assert payload["runtime_facts"]["status"] == "manual_only"
