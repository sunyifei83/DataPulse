"""Tests for the Digest Builder."""

from __future__ import annotations

import json
import os
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from datapulse.core.models import DataPulseItem, SourceType
from datapulse.reader import DataPulseReader


def _make_item(
    title: str = "Test",
    content: str = "Test content for digest builder testing",
    confidence: float = 0.8,
    source_name: str = "test_source",
    source_type: SourceType = SourceType.GENERIC,
    url: str = "https://example.com/page",
    fetched_at: str | None = None,
) -> DataPulseItem:
    item = DataPulseItem(
        source_type=source_type,
        source_name=source_name,
        title=title,
        content=content,
        url=url,
        confidence=confidence,
    )
    if fetched_at:
        item.fetched_at = fetched_at
    return item


def _setup_reader(tmp_path: Path, items: list[DataPulseItem]) -> DataPulseReader:
    inbox_path = str(tmp_path / "inbox.json")
    catalog_path = str(tmp_path / "catalog.json")
    Path(catalog_path).write_text(json.dumps({
        "version": 2, "sources": [], "subscriptions": {}, "packs": [],
    }), encoding="utf-8")
    payload = [item.to_dict() for item in items]
    Path(inbox_path).write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    os.environ["DATAPULSE_SOURCE_CATALOG"] = catalog_path
    return DataPulseReader(inbox_path=inbox_path)


@pytest.fixture(autouse=True)
def _cleanup_env():
    yield
    os.environ.pop("DATAPULSE_SOURCE_CATALOG", None)
    os.environ.pop("DATAPULSE_FACTUALITY_BACKEND_CMD", None)
    os.environ.pop("DATAPULSE_FACTUALITY_BACKEND_CALLABLE", None)
    os.environ.pop("DATAPULSE_FACTUALITY_BACKEND_WORKDIR", None)
    os.environ.pop("DATAPULSE_FACTUALITY_BACKEND_TIMEOUT_SECONDS", None)


class TestBuildDigest:
    def test_basic_structure(self, tmp_path):
        now = datetime.now(timezone.utc)
        items = [
            _make_item(title=f"Item {i}", url=f"https://example.com/{i}",
                       source_name=f"source_{i}",
                       content=f"unique content number {i} for testing digest builder",
                       fetched_at=now.isoformat())
            for i in range(10)
        ]
        reader = _setup_reader(tmp_path, items)
        digest = reader.build_digest()

        assert digest["version"] == "1.0"
        assert "generated_at" in digest
        assert "digest_date" in digest
        assert "stats" in digest
        assert "primary" in digest
        assert "secondary" in digest
        assert "factuality" in digest
        assert "provenance" in digest

    def test_primary_secondary_counts(self, tmp_path):
        now = datetime.now(timezone.utc)
        items = [
            _make_item(title=f"Item {i}", url=f"https://example.com/{i}",
                       source_name=f"source_{i}",
                       content=f"unique content number {i} for testing digest builder",
                       fetched_at=now.isoformat())
            for i in range(15)
        ]
        reader = _setup_reader(tmp_path, items)
        digest = reader.build_digest(top_n=3, secondary_n=5)

        assert digest["stats"]["selected_primary"] <= 3
        assert digest["stats"]["selected_secondary"] <= 5

    def test_diversity_max_per_source(self, tmp_path):
        """No source should appear more than max_per_source times."""
        now = datetime.now(timezone.utc)
        items = [
            _make_item(title=f"Same Source {i}", url=f"https://same.com/{i}",
                       source_name="same_source",
                       content=f"different content {i} from same source for diversity test",
                       fetched_at=now.isoformat())
            for i in range(10)
        ]
        reader = _setup_reader(tmp_path, items)
        digest = reader.build_digest(top_n=3, secondary_n=5, max_per_source=2)

        all_selected = digest["primary"] + digest["secondary"]
        same_source_count = sum(1 for it in all_selected if it["source_name"] == "same_source")
        assert same_source_count <= 2

    def test_provenance_metadata(self, tmp_path):
        now = datetime.now(timezone.utc)
        items = [
            _make_item(title=f"Item {i}", url=f"https://ex.com/{i}",
                       source_name=f"src_{i}",
                       content=f"content {i} for provenance testing of digest",
                       fetched_at=now.isoformat())
            for i in range(5)
        ]
        reader = _setup_reader(tmp_path, items)
        digest = reader.build_digest()

        assert "Curated from" in digest["provenance"]
        assert str(len(items)) in digest["provenance"]

    def test_digest_exposes_factuality_gate_and_item_governance(self, tmp_path):
        now = datetime.now(timezone.utc)
        items = [
            _make_item(
                title="OpenAI launch verified",
                url="https://ex.com/1",
                source_name="src_a",
                content="OpenAI launch verified for enterprise teams.",
                confidence=0.92,
                fetched_at=now.isoformat(),
            ),
            _make_item(
                title="OpenAI launch confirmed",
                url="https://ex.com/2",
                source_name="src_b",
                content="OpenAI launch confirmed by a second source.",
                confidence=0.9,
                fetched_at=now.isoformat(),
            ),
        ]
        items[0].review_state = "verified"
        items[0].processed = True
        items[1].review_state = "verified"
        items[1].processed = True
        reader = _setup_reader(tmp_path, items)

        digest = reader.build_digest(top_n=2, secondary_n=0)

        assert digest["factuality"]["status"] == "ready"
        assert digest["primary"][0]["governance"]["evidence_grade"] == "verified"
        assert digest["primary"][0]["governance"]["grounding"]["claim_count"] >= 1

    def test_digest_projects_factuality_backend_review(self, tmp_path, monkeypatch):
        monkeypatch.setenv("DATAPULSE_FACTUALITY_BACKEND_CMD", "factuality-backend --json")

        def fake_run(cmd, **kwargs):
            request = json.loads(kwargs["input"])
            assert request["surface"] == "factuality"
            assert request["subject"] == "digest"
            return subprocess.CompletedProcess(
                args=cmd,
                returncode=0,
                stdout=json.dumps(
                    {
                        "schema_version": "evidence_backend_result.v1",
                        "ok": True,
                        "surface": "factuality",
                        "backend_kind": "openfactverification_class",
                        "transport": "subprocess_json",
                        "result": {
                            "status": "review_required",
                            "summary": "Backend review flagged unresolved attribution context.",
                            "reasons": ["Backend review flagged unresolved attribution context."],
                            "signals": [
                                {
                                    "kind": "backend_verdict",
                                    "status": "review_required",
                                    "detail": "Cross-source attribution remains mixed.",
                                }
                            ],
                        },
                        "provenance": {
                            "status": "applied",
                            "backend_name": "openfactverification",
                            "latency_ms": 8,
                        },
                        "fallback": {
                            "used": False,
                            "baseline": "deterministic_gate",
                        },
                    }
                ),
                stderr="",
            )

        monkeypatch.setattr("datapulse.core.story.subprocess.run", fake_run)
        now = datetime.now(timezone.utc)
        items = [
            _make_item(
                title="OpenAI launch verified",
                url="https://ex.com/1",
                source_name="src_a",
                content="OpenAI launch verified for enterprise teams.",
                confidence=0.92,
                fetched_at=now.isoformat(),
            ),
            _make_item(
                title="OpenAI launch confirmed",
                url="https://ex.com/2",
                source_name="src_b",
                content="OpenAI launch confirmed by a second source.",
                confidence=0.9,
                fetched_at=now.isoformat(),
            ),
        ]
        items[0].review_state = "verified"
        items[0].processed = True
        items[1].review_state = "verified"
        items[1].processed = True
        reader = _setup_reader(tmp_path, items)

        digest = reader.build_digest(top_n=2, secondary_n=0)
        package_md = reader.emit_digest_package(top_n=2, secondary_n=0, output_format="markdown")

        assert digest["factuality"]["status"] == "ready"
        assert digest["factuality"]["effective_status"] == "review_required"
        assert digest["factuality"]["backend_review"]["status"] == "applied"
        assert digest["factuality"]["backend_review"]["backend_status"] == "review_required"
        assert "事实性生效状态" in package_md
        assert "后端复核: applied | verdict=review_required" in package_md

    def test_fingerprint_dedup(self, tmp_path):
        """Duplicate content should be deduped, keeping only the highest scored."""
        now = datetime.now(timezone.utc)
        shared_content = "identical article about machine learning breakthroughs in twenty twenty six"
        items = [
            _make_item(title="Copy 1", url="https://a.com/1", source_name="src_a",
                       content=shared_content, confidence=0.9, fetched_at=now.isoformat()),
            _make_item(title="Copy 2", url="https://b.com/2", source_name="src_b",
                       content=shared_content, confidence=0.7, fetched_at=now.isoformat()),
            _make_item(title="Unique", url="https://c.com/3", source_name="src_c",
                       content="completely different article about gardening tips and tricks",
                       confidence=0.8, fetched_at=now.isoformat()),
        ]
        reader = _setup_reader(tmp_path, items)
        digest = reader.build_digest(top_n=3, secondary_n=3)

        assert digest["stats"]["candidates_after_dedup"] < digest["stats"]["candidates_total"]

    def test_empty_inbox(self, tmp_path):
        reader = _setup_reader(tmp_path, [])
        digest = reader.build_digest()

        assert digest["stats"]["candidates_total"] == 0
        assert digest["primary"] == []
        assert digest["secondary"] == []

    def test_since_filter(self, tmp_path):
        now = datetime.now(timezone.utc)
        old = (now - timedelta(days=7)).isoformat()
        recent = now.isoformat()
        items = [
            _make_item(title="Old", url="https://old.com/1", content="old article content here for testing",
                       fetched_at=old, source_name="src_old"),
            _make_item(title="New", url="https://new.com/2", content="new article content here for testing",
                       fetched_at=recent, source_name="src_new"),
        ]
        reader = _setup_reader(tmp_path, items)
        since = (now - timedelta(days=1)).isoformat()
        digest = reader.build_digest(since=since)

        assert digest["stats"]["candidates_total"] == 1

    def test_min_confidence_filter(self, tmp_path):
        now = datetime.now(timezone.utc)
        items = [
            _make_item(title="Low Conf", url="https://low.com/1",
                       content="low confidence content for testing",
                       confidence=0.2, fetched_at=now.isoformat(), source_name="src_low"),
            _make_item(title="High Conf", url="https://high.com/2",
                       content="high confidence content for testing",
                       confidence=0.9, fetched_at=now.isoformat(), source_name="src_high"),
        ]
        reader = _setup_reader(tmp_path, items)
        digest = reader.build_digest(min_confidence=0.5)

        assert digest["stats"]["candidates_total"] == 1

    def test_digest_date_set(self, tmp_path):
        now = datetime.now(timezone.utc)
        items = [
            _make_item(title="Item 1", url="https://ex.com/1",
                       content="content for digest date test item one",
                       fetched_at=now.isoformat(), source_name="src_1"),
        ]
        reader = _setup_reader(tmp_path, items)
        digest = reader.build_digest()

        today = now.strftime("%Y-%m-%d")
        assert digest["digest_date"] == today

    def test_digest_excludes_ignored_and_duplicate_items(self, tmp_path):
        now = datetime.now(timezone.utc)
        keep = _make_item(title="Keep", url="https://ex.com/keep", source_name="src_keep", fetched_at=now.isoformat())
        ignored = _make_item(title="Ignore", url="https://ex.com/ignore", source_name="src_ignore", fetched_at=now.isoformat())
        ignored.review_state = "ignored"
        duplicate = _make_item(title="Dup", url="https://ex.com/dup", source_name="src_dup", fetched_at=now.isoformat())
        duplicate.review_state = "duplicate"
        items = [keep, ignored, duplicate]

        reader = _setup_reader(tmp_path, items)
        digest = reader.build_digest(top_n=3, secondary_n=3)
        selected_ids = {item["id"] for item in digest["primary"] + digest["secondary"]}

        assert keep.id in selected_ids
        assert ignored.id not in selected_ids
        assert duplicate.id not in selected_ids

    def test_prepare_digest_payload_replays_frozen_bundle_without_requery(self, tmp_path):
        now = datetime.now(timezone.utc)
        items = [
            _make_item(
                title="Frozen item 1",
                url="https://example.com/1",
                source_name="src_a",
                content="frozen bundle content one",
                confidence=0.91,
                fetched_at=now.isoformat(),
            ),
            _make_item(
                title="Frozen item 2",
                url="https://example.com/2",
                source_name="src_b",
                content="frozen bundle content two",
                confidence=0.87,
                fetched_at=(now - timedelta(hours=1)).isoformat(),
            ),
        ]
        reader = _setup_reader(tmp_path, items)
        bundle = reader.build_feed_bundle(limit=10)

        Path(tmp_path / "inbox.json").write_text("[]", encoding="utf-8")

        payload = reader.prepare_digest_payload(feed_bundle=bundle, top_n=1, secondary_n=1)

        assert payload["content"]["feed_bundle"]["items"][0]["title"] == "Frozen item 1"
        assert payload["content"]["digest_payload"]["stats"]["selected_primary"] == 1
        assert payload["content"]["delivery_package"]["summary"]["item_count"] == 2
        assert payload["stats"]["feed_bundle"]["items_selected"] == 2


class TestSelectDiverse:
    def test_penalty_same_source(self, tmp_path):
        """Items from the same source should be limited by max_per_source."""
        items = [
            _make_item(title=f"A{i}", source_name="src_a", url=f"https://a.com/{i}",
                       content=f"content from source a number {i}")
            for i in range(5)
        ] + [
            _make_item(title="B1", source_name="src_b", url="https://b.com/1",
                       content="content from source b number one"),
        ]
        # Score them so they're sorted by title (A0 first)
        for i, item in enumerate(items):
            item.score = 100 - i
            item.quality_rank = i + 1

        result = DataPulseReader._select_diverse(items, 4, max_per_source=2)
        source_a_count = sum(1 for it in result if it.source_name == "src_a")
        assert source_a_count <= 2
        assert len(result) <= 4

    def test_empty_input(self):
        assert DataPulseReader._select_diverse([], 5) == []

    def test_fewer_than_n(self):
        items = [_make_item(title="Only", url="https://only.com")]
        result = DataPulseReader._select_diverse(items, 5)
        assert len(result) == 1
