"""Tests for story workspace clustering and persistence."""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

import pytest
import tldextract

from datapulse.core import utils as core_utils
from datapulse.core.entities import Entity, EntityType, Relation
from datapulse.core.entity_store import EntityStore
from datapulse.core.models import DataPulseItem, SourceType
from datapulse.reader import DataPulseReader


def _make_item(
    item_id: str,
    *,
    title: str,
    content: str,
    url: str,
    source_name: str,
    confidence: float = 0.8,
    entities: list[str] | None = None,
    review_state: str = "new",
    processed: bool = False,
) -> DataPulseItem:
    item = DataPulseItem(
        source_type=SourceType.GENERIC,
        source_name=source_name,
        title=title,
        content=content,
        url=url,
        id=item_id,
        confidence=confidence,
        review_state=review_state,
        processed=processed,
    )
    if entities:
        item.extra["entities"] = [{"name": entity.upper(), "display_name": entity} for entity in entities]
    return item


def _reader(
    tmp_path: Path,
    items: list[DataPulseItem],
    *,
    entities: list[Entity] | None = None,
    relations: list[Relation] | None = None,
) -> DataPulseReader:
    inbox_path = tmp_path / "inbox.json"
    catalog_path = tmp_path / "catalog.json"
    stories_path = tmp_path / "stories.json"
    entity_store_path = tmp_path / "entity_store.json"
    inbox_path.write_text(json.dumps([item.to_dict() for item in items], ensure_ascii=False), encoding="utf-8")
    catalog_path.write_text(json.dumps({"version": 2, "sources": [], "subscriptions": {}, "packs": []}), encoding="utf-8")
    os.environ["DATAPULSE_SOURCE_CATALOG"] = str(catalog_path)
    os.environ["DATAPULSE_STORIES_PATH"] = str(stories_path)
    os.environ["DATAPULSE_ENTITY_STORE"] = str(entity_store_path)
    os.environ["TLDEXTRACT_CACHE"] = str(tmp_path / "tldextract-cache")
    core_utils.tldextract.extract = tldextract.TLDExtract(
        suffix_list_urls=(),
        cache_dir=str(tmp_path / "tldextract-cache"),
    )
    if entities or relations:
        store = EntityStore(path=str(entity_store_path))
        for entity in entities or []:
            store.add_entity(entity)
        for relation in relations or []:
            store.add_relation(relation)
    return DataPulseReader(inbox_path=str(inbox_path))


@pytest.fixture(autouse=True)
def _cleanup_env():
    yield
    os.environ.pop("DATAPULSE_SOURCE_CATALOG", None)
    os.environ.pop("DATAPULSE_STORIES_PATH", None)
    os.environ.pop("DATAPULSE_ENTITY_STORE", None)
    os.environ.pop("DATAPULSE_MEMORY_DIR", None)
    os.environ.pop("DATAPULSE_WATCHLIST_PATH", None)
    os.environ.pop("DATAPULSE_AI_SURFACE_ADMISSION_PATH", None)
    os.environ.pop("DATAPULSE_MODELBUS_BUNDLE_DIR", None)
    os.environ.pop("TLDEXTRACT_CACHE", None)
    os.environ.pop("DATAPULSE_GROUNDING_BACKEND_CMD", None)
    os.environ.pop("DATAPULSE_GROUNDING_BACKEND_CALLABLE", None)
    os.environ.pop("DATAPULSE_GROUNDING_BACKEND_WORKDIR", None)
    os.environ.pop("DATAPULSE_GROUNDING_BACKEND_TIMEOUT_SECONDS", None)
    os.environ.pop("DATAPULSE_FACTUALITY_BACKEND_CMD", None)
    os.environ.pop("DATAPULSE_FACTUALITY_BACKEND_CALLABLE", None)
    os.environ.pop("DATAPULSE_FACTUALITY_BACKEND_WORKDIR", None)
    os.environ.pop("DATAPULSE_FACTUALITY_BACKEND_TIMEOUT_SECONDS", None)


def test_story_build_clusters_related_items(tmp_path):
    reader = _reader(
        tmp_path,
        [
            _make_item(
                "item-1",
                title="OpenAI Launch Event",
                content="OpenAI launch event works well for ChatGPT users and enterprise teams.",
                url="https://example.com/openai-launch",
                source_name="src-a",
                confidence=0.93,
                entities=["OpenAI", "ChatGPT"],
            ),
            _make_item(
                "item-2",
                title="OpenAI Launch Event Recap",
                content="OpenAI launch event recap says ChatGPT enterprise rollout works for more teams.",
                url="https://another.com/openai-launch-recap",
                source_name="src-b",
                confidence=0.88,
                entities=["OpenAI", "ChatGPT"],
            ),
            _make_item(
                "item-3",
                title="Unrelated Market Update",
                content="A market update about semiconductor demand and supply chains.",
                url="https://example.com/market-update",
                source_name="src-c",
                confidence=0.61,
                entities=["Semiconductor"],
            ),
        ],
    )

    payload = reader.story_build(max_stories=5, evidence_limit=4)

    assert payload["stats"]["stories_built"] == 2
    first = payload["stories"][0]
    assert first["item_count"] == 2
    assert first["source_count"] == 2
    assert any(entity == "OpenAI" for entity in first["entities"])
    assert first["governance"]["provenance"]["story_id"] == first["id"]
    assert first["primary_evidence"][0]["governance"]["provenance"]["item_id"] == first["primary_item_id"]
    assert payload["stats"]["grounded_story_count"] >= 1
    assert payload["stats"]["grounded_claim_count"] >= 1
    assert first["governance"]["grounding"]["claim_count"] >= 1
    assert first["governance"]["factuality"]["status"] == "review_required"
    assert first["governance"]["factuality"]["signals"]
    assert first["governance"]["grounding"]["claims"][0]["source_link"]["story_id"] == first["id"]
    assert first["governance"]["grounding"]["claims"][0]["evidence_spans"][0]["item_id"] == first["primary_item_id"]


def test_story_build_detects_security_contradiction(tmp_path):
    reader = _reader(
        tmp_path,
        [
            _make_item(
                "item-1",
                title="OpenAI Security Update",
                content="OpenAI security update works and is reliable for enterprise rollout.",
                url="https://example.com/security-good",
                source_name="src-a",
                confidence=0.92,
                entities=["OpenAI"],
            ),
            _make_item(
                "item-2",
                title="OpenAI Security Update Risk",
                content="OpenAI security update is fake, risky, and misleading for enterprise teams.",
                url="https://another.com/security-bad",
                source_name="src-b",
                confidence=0.91,
                entities=["OpenAI"],
            ),
        ],
    )

    payload = reader.story_build(max_stories=3, evidence_limit=4)

    assert payload["stories"][0]["contradictions"][0]["topic"] == "security"
    assert payload["stories"][0]["status"] == "conflicted"
    assert payload["stories"][0]["governance"]["delivery_risk"]["level"] == "high"
    assert payload["stories"][0]["governance"]["factuality"]["status"] == "blocked"


def test_story_show_and_export_markdown(tmp_path):
    reader = _reader(
        tmp_path,
        [
            _make_item(
                "item-1",
                title="Launch Watch",
                content="Launch watch says OpenAI product launch works for developers.",
                url="https://example.com/launch-watch",
                source_name="src-a",
                confidence=0.9,
                entities=["OpenAI"],
            ),
            _make_item(
                "item-2",
                title="Launch Watch Recap",
                content="Launch watch recap confirms OpenAI rollout for developers.",
                url="https://another.com/launch-watch-recap",
                source_name="src-b",
                confidence=0.86,
                entities=["OpenAI"],
            ),
        ],
    )

    build_payload = reader.story_build(max_stories=3, evidence_limit=4)
    story_id = build_payload["stories"][0]["id"]

    shown = reader.show_story(story_id)
    exported = reader.export_story(story_id, output_format="markdown")

    assert shown is not None
    assert shown["id"] == story_id
    assert shown["governance"]["provenance"]["story_id"] == story_id
    assert shown["governance"]["grounding"]["claim_count"] >= 1
    assert exported is not None
    assert exported.startswith("# ")
    assert "## Governance" in exported
    assert "## Factuality Gate" in exported
    assert "## Grounded Claims" in exported
    assert "evidence_grade:" in exported
    assert "factuality_status:" in exported
    assert "## Timeline" in exported


def test_story_create_and_delete_roundtrip(tmp_path):
    reader = _reader(tmp_path, [])

    created = reader.create_story(
        title="Manual Brief",
        summary="Operator-authored manual brief",
        status="monitoring",
    )

    assert created["title"] == "Manual Brief"
    assert created["status"] == "monitoring"
    assert created["item_count"] == 0
    assert reader.list_stories(limit=10, min_items=0)[0]["id"] == created["id"]

    deleted = reader.delete_story(created["id"])

    assert deleted is not None
    assert deleted["id"] == created["id"]
    assert reader.list_stories(limit=10, min_items=0) == []


def test_ai_mission_suggest_runtime_semantics_cover_switch_modes_and_fallback_visibility(tmp_path):
    os.environ["DATAPULSE_MEMORY_DIR"] = str(tmp_path)
    reader = _reader(tmp_path, [])
    mission = reader.create_watch(
        name="AI Runtime Watch",
        query="edge inference launch",
        mission_intent={
            "scope_topics": ["launch"],
            "freshness_expectation": "daily",
        },
        schedule="@daily",
    )

    off_payload = reader.ai_mission_suggest(mission["id"], mode="off")
    review_payload = reader.ai_mission_suggest(mission["id"], mode="review")

    assert off_payload is not None
    assert off_payload["precheck"]["mode"] == "off"
    assert off_payload["precheck"]["mode_status"] == "manual_only"
    assert off_payload["bridge_request"] is None
    assert off_payload["output"] is None
    assert off_payload["runtime_facts"]["status"] == "manual_only"
    assert off_payload["runtime_facts"]["manual_override_required"] is False

    assert review_payload is not None
    assert review_payload["precheck"]["mode"] == "review"
    assert review_payload["precheck"]["mode_status"] == "admitted"
    assert set(review_payload["precheck"]["must_expose_runtime_facts"]) >= {
        "served_by_alias",
        "fallback_used",
        "degraded",
        "schema_valid",
        "manual_override_required",
    }
    assert review_payload["bridge_request"]["governance"]["allow_final_state_write"] is False
    assert review_payload["bridge_request"]["governance"]["allow_degraded_result"] is True
    assert review_payload["runtime_facts"]["status"] == "fallback_used"
    assert review_payload["runtime_facts"]["fallback_used"] is True
    assert review_payload["runtime_facts"]["degraded"] is True
    assert review_payload["runtime_facts"]["schema_valid"] is True
    assert review_payload["runtime_facts"]["manual_override_required"] is True
    assert review_payload["runtime_facts"]["served_by_alias"] == review_payload["precheck"]["alias"]


def test_story_create_from_triage_items(tmp_path):
    reader = _reader(
        tmp_path,
        [
            _make_item(
                "item-1",
                title="Launch Watch",
                content="Launch watch says OpenAI product launch works for developers.",
                url="https://example.com/launch-watch",
                source_name="src-a",
                confidence=0.9,
                entities=["OpenAI"],
                review_state="triaged",
            ),
            _make_item(
                "item-2",
                title="Launch Follow-up",
                content="Follow-up confirms rollout timing and developer impact.",
                url="https://example.com/launch-follow-up",
                source_name="src-b",
                confidence=0.83,
                entities=["OpenAI", "Developers"],
                review_state="verified",
            ),
        ],
    )

    created = reader.create_story_from_triage(
        ["item-1", "item-2"],
        title="Launch Queue Seed",
        status="monitoring",
    )

    assert created["title"] == "Launch Queue Seed"
    assert created["status"] == "monitoring"
    assert created["item_count"] == 2
    assert created["primary_item_id"] == "item-1"
    assert created["primary_evidence"][0]["item_id"] == "item-1"
    assert created["secondary_evidence"][0]["item_id"] == "item-2"
    assert created["governance"]["provenance"]["story_id"] == created["id"]


def test_story_build_governance_tracks_verified_primary_evidence(tmp_path):
    reader = _reader(
        tmp_path,
        [
            _make_item(
                "item-1",
                title="Verified Launch Watch",
                content="OpenAI launch watch confirms enterprise rollout for developers.",
                url="https://example.com/verified-launch",
                source_name="src-a",
                confidence=0.95,
                entities=["OpenAI"],
                review_state="verified",
                processed=True,
            ),
            _make_item(
                "item-2",
                title="Verified Launch Watch Recap",
                content="OpenAI launch watch recap confirms enterprise rollout for more teams.",
                url="https://another.com/verified-launch-recap",
                source_name="src-b",
                confidence=0.89,
                entities=["OpenAI"],
                review_state="triaged",
            ),
        ],
    )

    payload = reader.story_build(max_stories=3, evidence_limit=4)
    story = payload["stories"][0]

    assert story["governance"]["evidence_grade"] == "verified"
    assert story["governance"]["delivery_risk"]["status"] in {"ready", "review_required"}
    assert story["governance"]["provenance"]["primary_item_id"] == "item-1"
    assert story["governance"]["grounding"]["primary_claim_count"] >= 1
    assert story["governance"]["factuality"]["status"] == "ready"


def test_story_build_projects_grounding_backend_provenance(monkeypatch, tmp_path):
    monkeypatch.setenv("DATAPULSE_GROUNDING_BACKEND_CMD", "grounding-backend --json")

    def fake_run(cmd, **kwargs):
        request = json.loads(kwargs["input"])
        claim_text = str(request["input"]["content"]).split(".", 1)[0].strip() + "."
        return subprocess.CompletedProcess(
            args=cmd,
            returncode=0,
            stdout=json.dumps(
                {
                    "schema_version": "evidence_backend_result.v1",
                    "ok": True,
                    "surface": "grounding",
                    "backend_kind": "langextract_class",
                    "transport": "subprocess_json",
                    "result": {
                        "claims": [
                            {
                                "text": claim_text,
                                "evidence_spans": [
                                    {
                                        "field": "content",
                                        "text": claim_text,
                                    }
                                ],
                            }
                        ]
                    },
                    "provenance": {
                        "status": "applied",
                        "backend_name": "langextract",
                        "latency_ms": 11,
                    },
                    "fallback": {
                        "used": False,
                        "baseline": "heuristic",
                    },
                }
            ),
            stderr="",
        )

    monkeypatch.setattr("datapulse.core.triage.subprocess.run", fake_run)
    reader = _reader(
        tmp_path,
        [
            _make_item(
                "item-1",
                title="OpenAI Launch Event",
                content="OpenAI launch event generated 12% more enterprise usage.",
                url="https://example.com/openai-launch",
                source_name="src-a",
                confidence=0.93,
                entities=["OpenAI"],
            ),
            _make_item(
                "item-2",
                title="OpenAI Launch Event Recap",
                content="OpenAI launch event recap confirms 12% more enterprise usage.",
                url="https://another.com/openai-launch-recap",
                source_name="src-b",
                confidence=0.88,
                entities=["OpenAI"],
            ),
        ],
    )

    payload = reader.story_build(max_stories=3, evidence_limit=4)
    story = payload["stories"][0]
    exported = reader.export_story(story["id"], output_format="markdown")

    backend = story["governance"]["grounding"]["backend"]
    assert backend["status"] == "applied"
    assert backend["backend_kind"] == "langextract_class"
    assert backend["applied_item_count"] >= 1
    assert any(row["item_id"] == story["primary_item_id"] for row in backend["items"])
    assert "grounding_backend_status: applied" in exported


def test_story_build_projects_factuality_backend_review(monkeypatch, tmp_path):
    monkeypatch.setenv("DATAPULSE_FACTUALITY_BACKEND_CMD", "factuality-backend --json")

    def fake_run(cmd, **kwargs):
        request = json.loads(kwargs["input"])
        assert request["surface"] == "factuality"
        assert request["subject"] == "story"
        assert request["input"]["surface"] == "story_export"
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
                        "summary": "OpenFactVerification flagged unresolved attribution context.",
                        "reasons": ["Backend review flagged unresolved attribution context."],
                        "signals": [
                            {
                                "kind": "backend_verdict",
                                "status": "review_required",
                                "detail": "Attribution support remains mixed across the selected evidence.",
                            }
                        ],
                    },
                    "provenance": {
                        "status": "applied",
                        "backend_name": "openfactverification",
                        "latency_ms": 9,
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
    reader = _reader(
        tmp_path,
        [
            _make_item(
                "item-1",
                title="Verified Launch Watch",
                content="OpenAI launch watch confirms enterprise rollout for developers.",
                url="https://example.com/verified-launch",
                source_name="src-a",
                confidence=0.95,
                entities=["OpenAI"],
                review_state="verified",
                processed=True,
            ),
            _make_item(
                "item-2",
                title="Verified Launch Watch Recap",
                content="OpenAI launch watch recap confirms enterprise rollout for more teams.",
                url="https://another.com/verified-launch-recap",
                source_name="src-b",
                confidence=0.89,
                entities=["OpenAI"],
                review_state="verified",
                processed=True,
            ),
        ],
    )

    payload = reader.story_build(max_stories=3, evidence_limit=4)
    story = payload["stories"][0]
    exported = reader.export_story(story["id"], output_format="markdown")

    backend = story["governance"]["factuality"]["backend_review"]
    assert story["governance"]["factuality"]["status"] == "ready"
    assert story["governance"]["factuality"]["effective_status"] == "review_required"
    assert backend["status"] == "applied"
    assert backend["backend_kind"] == "openfactverification_class"
    assert backend["backend_status"] == "review_required"
    assert story["governance"]["delivery_risk"]["status"] == "review_required"
    assert "factuality_backend_status: applied" in exported
    assert "factuality_effective_status: review_required" in exported


def test_story_graph_uses_entity_store_relations(tmp_path):
    reader = _reader(
        tmp_path,
        [
            _make_item(
                "item-1",
                title="OpenAI Launch Event",
                content="OpenAI launch event works well for ChatGPT users and enterprise teams.",
                url="https://example.com/openai-launch",
                source_name="src-a",
                confidence=0.93,
                entities=["OpenAI", "ChatGPT"],
            ),
            _make_item(
                "item-2",
                title="OpenAI Launch Event Recap",
                content="OpenAI launch event recap says ChatGPT enterprise rollout works for more teams.",
                url="https://another.com/openai-launch-recap",
                source_name="src-b",
                confidence=0.88,
                entities=["OpenAI", "ChatGPT"],
            ),
        ],
        entities=[
            Entity(name="OPENAI", entity_type=EntityType.ORG, display_name="OpenAI", source_item_ids=["item-1", "item-2"]),
            Entity(name="CHATGPT", entity_type=EntityType.PRODUCT, display_name="ChatGPT", source_item_ids=["item-1", "item-2"]),
        ],
        relations=[
            Relation(
                source_entity="OPENAI",
                target_entity="CHATGPT",
                relation_type="BUILT",
                source_item_ids=["item-1"],
            )
        ],
    )

    build_payload = reader.story_build(max_stories=3, evidence_limit=4)
    story_id = build_payload["stories"][0]["id"]
    graph = reader.story_graph(story_id, entity_limit=6, relation_limit=6)

    assert graph is not None
    assert graph["story"]["id"] == story_id
    assert any(node["kind"] == "story" for node in graph["nodes"])
    assert any(node["label"] == "OpenAI" for node in graph["nodes"])
    assert any(edge["kind"] == "story_entity" for edge in graph["edges"])
    assert any(edge["kind"] == "entity_relation" and edge["relation_type"] == "BUILT" for edge in graph["edges"])
