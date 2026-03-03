"""Tests for entity extraction primitives and parsing."""

from __future__ import annotations

from datapulse.core.entities import (
    EntityType,
    _parse_tuple_line,
    extract_entities,
    extract_entities_fast,
    normalize_entity_name,
    parse_llm_output,
)


def test_normalize_entity_name():
    assert normalize_entity_name("OpenAI GPT-4") == "OPENAI_GPT_4"
    assert normalize_entity_name("Acme Corp") == "ACME_CORP"
    assert normalize_entity_name(" new-york, city ") == "NEW_YORK_CITY"


def test_parse_tuple_line_accepts_entity_tuple():
    value = _parse_tuple_line('("entity", "OpenAI", "ORG", "AI startup")')
    assert value is not None
    assert value[1] == "OpenAI"
    assert value[2] == "ORG"


def test_parse_llm_output_prefers_tuple_format():
    raw = """("entity", "OpenAI", "ORG", "AI startup")
("entity", "CES", "EVENT", "Conference")
"""
    entities, relations = parse_llm_output(raw)
    names = {ent.name for ent in entities}
    assert names == {"OPENAI", "CES"}
    assert not relations


def test_parse_llm_output_json_fallback():
    raw = (
        '{"entities":[{"name":"ChatGPT","type":"TECHNOLOGY","source_item_ids":["u1"]}],'
        '"relations":[{"source_entity":"ChatGPT","target_entity":"OpenAI","relation_type":"BUILT_BY"}]}'
    )
    entities, relations = parse_llm_output(raw)
    assert len(entities) == 1
    assert entities[0].name == "CHATGPT"
    assert entities[0].entity_type == EntityType.TECHNOLOGY
    assert len(relations) == 1
    assert relations[0].relation_type == "BUILT_BY"


def test_extract_entities_fast_basic_entities():
    text = "Python and GPT-4 were discussed by Alice Smith said launched OpenAI Corp during CES 2025."
    entities, relations = extract_entities_fast(text, "item-1")
    names = {e.name for e in entities}
    assert "PYTHON" in names
    assert "CES" in names
    assert any(entity.entity_type == EntityType.PERSON for entity in entities)
    assert not relations


def test_extract_entities_without_llm_key_returns_fast_fallback():
    entities, relations = extract_entities("Python release is coming", mode="llm", llm_api_key=None)
    assert len(entities) == 1
    assert entities[0].name == "PYTHON"
    assert relations == []


def test_parse_llm_output_invalid_lines_ignored():
    raw = "noise\n{not json}\n"
    entities, relations = parse_llm_output(raw)
    assert entities == []
    assert relations == []
