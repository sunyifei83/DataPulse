"""Tests for story workspace clustering and persistence."""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

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
    assert "## Grounded Claims" in exported
    assert "evidence_grade:" in exported
    assert "## Timeline" in exported


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
