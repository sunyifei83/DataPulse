"""Tests for triage queue state and persistence."""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

import pytest

from datapulse.core.models import DataPulseItem, SourceType
from datapulse.reader import DataPulseReader


def _make_item(
    item_id: str,
    *,
    title: str,
    confidence: float = 0.8,
    processed: bool = False,
    review_state: str = "new",
) -> DataPulseItem:
    return DataPulseItem(
        source_type=SourceType.GENERIC,
        source_name="source",
        title=title,
        content=f"{title} content for triage testing and persistence checks",
        url=f"https://example.com/{item_id}",
        id=item_id,
        confidence=confidence,
        processed=processed,
        review_state=review_state,
    )


def _reader(tmp_path: Path, items: list[DataPulseItem]) -> DataPulseReader:
    inbox_path = tmp_path / "inbox.json"
    catalog_path = tmp_path / "catalog.json"
    inbox_path.write_text(json.dumps([item.to_dict() for item in items], ensure_ascii=False), encoding="utf-8")
    catalog_path.write_text(json.dumps({"version": 2, "sources": [], "subscriptions": {}, "packs": []}), encoding="utf-8")
    os.environ["DATAPULSE_SOURCE_CATALOG"] = str(catalog_path)
    return DataPulseReader(inbox_path=str(inbox_path))


@pytest.fixture(autouse=True)
def _cleanup_env():
    yield
    os.environ.pop("DATAPULSE_SOURCE_CATALOG", None)
    os.environ.pop("DATAPULSE_GROUNDING_BACKEND_CMD", None)
    os.environ.pop("DATAPULSE_GROUNDING_BACKEND_CALLABLE", None)
    os.environ.pop("DATAPULSE_GROUNDING_BACKEND_WORKDIR", None)
    os.environ.pop("DATAPULSE_GROUNDING_BACKEND_TIMEOUT_SECONDS", None)


def test_processed_item_migrates_to_triaged_state(tmp_path):
    reader = _reader(tmp_path, [_make_item("item-1", title="Legacy", processed=True)])

    items = reader.list_memory(limit=10)

    assert items[0].review_state == "triaged"


def test_triage_update_persists_note_and_duplicate_of(tmp_path):
    reader = _reader(
        tmp_path,
        [
            _make_item("item-1", title="Candidate"),
            _make_item("item-2", title="Canonical"),
        ],
    )

    payload = reader.triage_update(
        "item-1",
        state="duplicate",
        note="same story as canonical",
        actor="test",
        duplicate_of="item-2",
    )
    reloaded = DataPulseReader(inbox_path=str(tmp_path / "inbox.json"))

    assert payload is not None
    assert payload["review_state"] == "duplicate"
    assert payload["duplicate_of"] == "item-2"
    assert payload["governance"]["evidence_grade"] == "discarded"
    assert payload["governance"]["provenance"]["duplicate_of"] == "item-2"
    assert payload["governance"]["delivery_risk"]["status"] == "suppressed"
    stored = next(item for item in reloaded.inbox.items if item.id == "item-1")
    assert stored.review_state == "duplicate"
    assert stored.review_notes[0]["note"] == "same story as canonical"
    assert stored.review_actions[0]["to_state"] == "duplicate"


def test_triage_list_defaults_to_open_states(tmp_path):
    reader = _reader(
        tmp_path,
        [
            _make_item("item-1", title="Open"),
            _make_item("item-2", title="Closed", review_state="verified", processed=True),
        ],
    )

    payload = reader.triage_list(limit=10)

    assert [item["id"] for item in payload] == ["item-1"]
    assert payload[0]["governance"]["evidence_grade"] == "working"
    assert payload[0]["governance"]["provenance"]["item_id"] == "item-1"
    assert payload[0]["governance"]["grounding"]["claim_count"] >= 1
    assert payload[0]["governance"]["grounding"]["claims"][0]["source_link"]["item_id"] == "item-1"
    assert payload[0]["governance"]["grounding"]["claims"][0]["evidence_spans"][0]["item_id"] == "item-1"


def test_triage_stats_counts_states(tmp_path):
    reader = _reader(
        tmp_path,
        [
            _make_item("item-1", title="Open"),
            _make_item("item-2", title="Verified", review_state="verified", processed=True),
            _make_item("item-3", title="Escalated", review_state="escalated"),
        ],
    )

    payload = reader.triage_stats()

    assert payload["total"] == 3
    assert payload["open_count"] == 2
    assert payload["states"]["verified"] == 1
    assert payload["evidence_grade_counts"]["verified"] == 1
    assert payload["delivery_risk_counts"]["high"] >= 1
    assert payload["grounding"]["items_with_claims"] >= 1
    assert payload["grounding"]["claim_count"] >= payload["grounding"]["items_with_claims"]
    assert payload["grounding"]["evidence_span_count"] >= payload["grounding"]["claim_count"]


def test_triage_delete_removes_item_from_inbox(tmp_path):
    reader = _reader(
        tmp_path,
        [
            _make_item("item-1", title="Delete Me"),
            _make_item("item-2", title="Keep Me"),
        ],
    )

    payload = reader.triage_delete("item-1")
    reloaded = DataPulseReader(inbox_path=str(tmp_path / "inbox.json"))

    assert payload is not None
    assert payload["id"] == "item-1"
    assert [item.id for item in reloaded.inbox.items] == ["item-2"]


def test_triage_explain_duplicate_ranks_candidate(tmp_path):
    reader = _reader(
        tmp_path,
        [
            _make_item("item-1", title="OpenAI Launch Event", confidence=0.95),
            _make_item("item-2", title="OpenAI Launch Event Recap", confidence=0.71),
            _make_item("item-3", title="Unrelated Market Update", confidence=0.88),
        ],
    )

    payload = reader.triage_explain("item-1", limit=3)

    assert payload is not None
    assert payload["item"]["id"] == "item-1"
    assert payload["item"]["governance"]["provenance"]["item_id"] == "item-1"
    assert payload["candidate_count"] >= 1
    assert payload["candidates"][0]["id"] == "item-2"
    assert "same_domain" in payload["candidates"][0]["signals"]
    assert payload["candidates"][0]["governance"]["provenance"]["source_name"] == "source"
    assert payload["item"]["governance"]["grounding"]["claim_count"] >= 1


def test_triage_projects_structured_grounded_claims(tmp_path):
    item = _make_item(
        "item-1",
        title="Revenue update",
        processed=True,
        review_state="verified",
    )
    item.content = "Revenue reached 12M ARR in 2025. Gross margin improved to 80%."
    item.extra["grounded_claims"] = [
        {
            "claim": "Revenue reached 12M ARR in 2025.",
            "evidence_spans": [
                {
                    "field": "content",
                    "text": "Revenue reached 12M ARR in 2025.",
                }
            ],
        }
    ]
    reader = _reader(tmp_path, [item])

    payload = reader.triage_list(limit=5, include_closed=True)

    assert len(payload) == 1
    grounding = payload[0]["governance"]["grounding"]
    assert grounding["mode"] == "provided"
    assert grounding["claim_count"] == 1
    assert grounding["claims"][0]["text"] == "Revenue reached 12M ARR in 2025."
    assert grounding["claims"][0]["source_link"]["url"] == "https://example.com/item-1"
    assert grounding["claims"][0]["evidence_spans"][0]["field"] == "content"
    assert grounding["claims"][0]["evidence_spans"][0]["start"] == 0
    assert payload[0]["governance"]["provenance"]["grounded_claim_count"] == 1


def test_triage_grounding_backend_applies_backend_claims(monkeypatch, tmp_path):
    monkeypatch.setenv("DATAPULSE_GROUNDING_BACKEND_CMD", "grounding-backend --json")
    item = _make_item("item-1", title="Revenue update", processed=True, review_state="triaged")
    item.content = "Revenue reached 12M ARR in 2025. Gross margin improved to 80%."
    reader = _reader(tmp_path, [item])
    captured: dict[str, object] = {}

    def fake_run(cmd, **kwargs):
        captured["cmd"] = cmd
        captured["request"] = json.loads(kwargs["input"])
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
                                "text": "Revenue reached 12M ARR in 2025.",
                                "evidence_spans": [
                                    {
                                        "field": "content",
                                        "text": "Revenue reached 12M ARR in 2025.",
                                    }
                                ],
                            }
                        ]
                    },
                    "provenance": {
                        "status": "applied",
                        "backend_name": "langextract",
                        "backend_version": "0.1.0",
                        "request_id": "req-1",
                        "latency_ms": 18,
                        "warnings": [],
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

    payload = reader.triage_list(limit=5, include_closed=True)

    grounding = payload[0]["governance"]["grounding"]
    assert grounding["mode"] == "backend"
    assert grounding["claim_count"] == 1
    assert grounding["claims"][0]["text"] == "Revenue reached 12M ARR in 2025."
    assert grounding["claims"][0]["evidence_spans"][0]["field"] == "content"
    assert grounding["backend"]["status"] == "applied"
    assert grounding["backend"]["backend_name"] == "langextract"
    assert grounding["backend"]["fallback_mode"] == "heuristic"
    assert grounding["backend"]["used_output"] is True
    assert grounding["backend"]["applied_claim_count"] == 1
    assert captured["cmd"] == ["grounding-backend", "--json"]
    assert captured["request"]["surface"] == "grounding"
    assert captured["request"]["subject"] == "item"
    assert captured["request"]["deterministic"]["fallback_mode"] == "heuristic"


def test_triage_grounding_backend_preserves_provided_claims(monkeypatch, tmp_path):
    monkeypatch.setenv("DATAPULSE_GROUNDING_BACKEND_CMD", "grounding-backend --json")
    monkeypatch.setattr(
        "datapulse.core.triage.subprocess.run",
        lambda *args, **kwargs: pytest.fail("backend should be skipped when provided claims exist"),
    )
    item = _make_item("item-1", title="Revenue update", processed=True, review_state="verified")
    item.content = "Revenue reached 12M ARR in 2025. Gross margin improved to 80%."
    item.extra["grounded_claims"] = [
        {
            "claim": "Revenue reached 12M ARR in 2025.",
            "evidence_spans": [
                {
                    "field": "content",
                    "text": "Revenue reached 12M ARR in 2025.",
                }
            ],
        }
    ]
    reader = _reader(tmp_path, [item])

    payload = reader.triage_list(limit=5, include_closed=True)

    grounding = payload[0]["governance"]["grounding"]
    assert grounding["mode"] == "provided"
    assert grounding["claim_count"] == 1
    assert grounding["backend"]["status"] == "skipped"
    assert grounding["backend"]["fallback_mode"] == "provided"
    assert grounding["backend"]["used_output"] is False


def test_triage_grounding_backend_falls_back_when_unavailable(monkeypatch, tmp_path):
    monkeypatch.setenv("DATAPULSE_GROUNDING_BACKEND_CMD", "grounding-backend --json")

    def fake_run(*args, **kwargs):
        raise OSError("backend missing")

    monkeypatch.setattr("datapulse.core.triage.subprocess.run", fake_run)
    item = _make_item("item-1", title="Revenue update", processed=True, review_state="triaged")
    item.content = "Revenue reached 12M ARR in 2025. Gross margin improved to 80%."
    reader = _reader(tmp_path, [item])

    payload = reader.triage_list(limit=5, include_closed=True)

    grounding = payload[0]["governance"]["grounding"]
    assert grounding["mode"] == "heuristic"
    assert grounding["claim_count"] >= 1
    assert grounding["backend"]["status"] == "unavailable"
    assert grounding["backend"]["fallback_mode"] == "heuristic"
    assert grounding["backend"]["used_output"] is False
    assert grounding["backend"]["error_code"] == "backend_unavailable"


def test_triage_ai_assist_returns_governed_explain_without_state_mutation(tmp_path):
    reader = _reader(
        tmp_path,
        [
            _make_item("item-1", title="OpenAI Launch Event", confidence=0.95),
            _make_item("item-2", title="OpenAI Launch Event Recap", confidence=0.73),
            _make_item("item-3", title="Unrelated Market Update", confidence=0.66),
        ],
    )

    before = reader.list_memory(limit=10)
    payload = reader.ai_triage_assist("item-1", mode="assist", limit=3)
    after = reader.list_memory(limit=10)

    assert payload is not None
    assert payload["output"]["contract_id"] == "datapulse_ai_triage_explain.v1"
    explain = payload["output"]["payload"]
    assert explain["item"]["id"] == "item-1"
    assert explain["candidate_count"] >= 1
    assert explain["candidates"][0]["rationale"]
    assert payload["runtime_facts"]["source"] == "deterministic"
    assert payload["runtime_facts"]["schema_valid"] is True
    assert before[0].review_state == after[0].review_state == "new"
    assert before[0].review_notes == after[0].review_notes == []
    assert before[0].review_actions == after[0].review_actions == []


def test_triage_ai_assist_off_mode_short_circuits(tmp_path):
    reader = _reader(
        tmp_path,
        [
            _make_item("item-1", title="OpenAI Launch Event", confidence=0.95),
            _make_item("item-2", title="OpenAI Launch Event Recap", confidence=0.73),
        ],
    )

    payload = reader.ai_triage_assist("item-1", mode="off")

    assert payload is not None
    assert payload["output"] is None
    assert payload["runtime_facts"]["status"] == "manual_only"
