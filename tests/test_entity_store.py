"""Tests for persistent entity and relation storage."""

from __future__ import annotations

from datapulse.core.entities import Entity, EntityType, Relation
from datapulse.core.entity_store import EntityStore


def _mk_entity(name: str, entity_type: EntityType, source_item_ids: list[str], mention_count: int = 1) -> Entity:
    return Entity(
        name=name,
        entity_type=entity_type,
        display_name=name.replace("_", " "),
        source_item_ids=source_item_ids,
        mention_count=mention_count,
    )


def test_add_entity_persists_and_merges(tmp_path):
    store = EntityStore(path=str(tmp_path / "entity_store.json"))
    first = _mk_entity("OPENAI", EntityType.ORG, ["i1"])
    second = _mk_entity("OPENAI", EntityType.ORG, ["i2"])

    assert store.add_entity(first)
    assert store.add_entity(second)
    entity = store.get_entity("openai")
    assert entity is not None
    assert entity.name == "OPENAI"
    assert set(entity.source_item_ids) == {"i1", "i2"}
    assert entity.mention_count >= 2

    reloaded = EntityStore(path=str(tmp_path / "entity_store.json"))
    loaded = reloaded.get_entity("OPENAI")
    assert loaded is not None
    assert set(loaded.source_item_ids) == {"i1", "i2"}


def test_add_entities_and_query_by_type(tmp_path):
    store = EntityStore(path=str(tmp_path / "entity_store.json"))
    count = store.add_entities(
        [
            _mk_entity("PYTHON", EntityType.TECHNOLOGY, ["i1"]),
            _mk_entity("TESLA", EntityType.ORG, ["i1"]),
            _mk_entity("MACHINE_LEARNING", EntityType.TECHNOLOGY, ["i2"]),
        ]
    )
    assert count == 3
    tech_entities = store.query_by_type("TECHNOLOGY")
    assert len(tech_entities) == 2


def test_relations_merge_and_query_related(tmp_path):
    store = EntityStore(path=str(tmp_path / "entity_store.json"))
    assert store.add_relation(
        Relation(
            source_entity="OPENAI",
            target_entity="PYTHON",
            relation_type="USES",
            keywords=["llm"],
            weight=1.0,
            source_item_ids=["i1"],
        )
    )
    # merge same edge with extra sources and higher weight
    assert store.add_relation(
        Relation(
            source_entity="OPENAI",
            target_entity="PYTHON",
            relation_type="USES",
            keywords=["ai"],
            weight=0.8,
            source_item_ids=["i2"],
        )
    )
    related = store.query_related("OPENAI")
    assert len(related) == 1
    assert related[0]["source_entity"] == "OPENAI"
    assert set(related[0]["source_item_ids"]) == {"i1", "i2"}
    assert related[0]["weight"] == 1.0


def test_cross_source_entities_and_stats(tmp_path):
    store = EntityStore(path=str(tmp_path / "entity_store.json"))
    store.add_entities(
        [
            _mk_entity("REDDIT", EntityType.ORG, ["i1", "i2"], 2),
            _mk_entity("XHS", EntityType.ORG, ["i1"]),
        ]
    )
    assert len(store.cross_source_entities(min_sources=2)) == 1

    stats = store.stats()
    assert stats["total_entities"] >= 2
    assert stats["cross_source_entities"] >= 1
    assert "ORG" in stats["by_type"]
