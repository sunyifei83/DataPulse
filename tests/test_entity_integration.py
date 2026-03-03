"""Integration-style tests for reader-level entity flow."""

from __future__ import annotations

import asyncio

from datapulse.core.entities import Entity, EntityType, Relation
from datapulse.core.entity_store import EntityStore
from datapulse.core.models import DataPulseItem, SourceType
from datapulse.core.scoring import rank_items
from datapulse.reader import DataPulseReader


def _sample_item(url: str = "https://example.com/item", entities: list[str] | None = None) -> DataPulseItem:
    return DataPulseItem(
        source_type=SourceType.GENERIC,
        source_name="unit-test",
        title="Sample Item",
        content="Sample content for scoring",
        url=url,
        confidence=0.8,
        extra={"entities": [{"name": item} for item in (entities or [])]},
    )


def test_extract_entities_api_handles_item_input(tmp_path):
    reader = DataPulseReader.__new__(DataPulseReader)
    reader._entity_store = EntityStore(path=str(tmp_path / "entity_store.json"))

    item = _sample_item(entities=["PYTHON", "OPENAI"])
    monkey_entities = [Entity(name="PYTHON", entity_type=EntityType.TECHNOLOGY, display_name="Python", source_item_ids=["i1"])]
    monkey_relations = [
        Relation(source_entity="PYTHON", target_entity="OPENAI", relation_type="USES", source_item_ids=["i1"])
    ]

    reader._extract_entities = lambda *args, **kwargs: (monkey_entities, monkey_relations)

    payload = asyncio.run(reader.extract_entities(item, mode="fast", store=False))
    assert payload["item"]["extra"]["entities"][0]["name"] == "PYTHON"
    assert payload["item"]["extra"]["relations"][0]["relation_type"] == "USES"
    assert payload["entities"][0]["name"] == "PYTHON"


def test_reader_entity_query_and_graph(tmp_path):
    reader = DataPulseReader.__new__(DataPulseReader)
    reader._entity_store = EntityStore(path=str(tmp_path / "entity_store.json"))

    reader._entity_store.add_entity(
        Entity(
            name="OPENAI",
            entity_type=EntityType.ORG,
            display_name="OpenAI",
            source_item_ids=["i1", "i2"],
        )
    )
    reader._entity_store.add_entity(
        Entity(
            name="CHATGPT",
            entity_type=EntityType.PRODUCT,
            display_name="ChatGPT",
            source_item_ids=["i1"],
        )
    )
    reader._entity_store.add_relation(
        Relation(
            source_entity="OPENAI",
            target_entity="CHATGPT",
            relation_type="BUILT",
            source_item_ids=["i1"],
        )
    )

    rows = reader.query_entities(entity_type="ORG")
    assert len(rows) == 1
    assert rows[0]["name"] == "OPENAI"
    assert rows[0]["source_count"] == 2

    graph = reader.entity_graph("OpenAI", limit=10)
    assert graph["entity"]["name"] == "OPENAI"
    assert graph["relation_count"] == 1
    assert graph["related"][0]["target_entity"] == "CHATGPT"


def test_entity_source_counts_feed_ranking():
    item_a = _sample_item(url="https://example.com/a", entities=["PYTHON", "OPENAI"])
    item_b = _sample_item(url="https://example.com/b", entities=["PYTHON"])
    item_c = _sample_item(url="https://example.com/c", entities=[])

    reader = DataPulseReader.__new__(DataPulseReader)
    items = [item_a, item_b, item_c]
    counts = reader._collect_entity_source_counts(items)
    assert counts["PYTHON"] == 2
    assert counts["OPENAI"] == 1
    assert counts.get("PYTORCH", 0) == 0

    ranked = rank_items(items, entity_source_counts=counts)
    assert ranked[0].quality_rank == 1
