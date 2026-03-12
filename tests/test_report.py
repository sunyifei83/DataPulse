"""Tests for report-production core objects and repository persistence."""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from datapulse.reader import DataPulseReader


def _reader(
    tmp_path: Path,
    *,
    items: list[dict[str, str]] | None = None,
) -> DataPulseReader:
    inbox_path = tmp_path / "inbox.json"
    catalog_path = tmp_path / "catalog.json"
    stories_path = tmp_path / "stories.json"
    reports_path = tmp_path / "reports.json"
    inbox_path.write_text(json.dumps(items or [], ensure_ascii=False), encoding="utf-8")
    catalog_path.write_text(json.dumps({"version": 2, "sources": [], "subscriptions": {}, "packs": []}), encoding="utf-8")
    os.environ["DATAPULSE_MEMORY_DIR"] = str(tmp_path)
    os.environ["DATAPULSE_SOURCE_CATALOG"] = str(catalog_path)
    os.environ["DATAPULSE_STORIES_PATH"] = str(stories_path)
    os.environ["DATAPULSE_REPORTS_PATH"] = str(reports_path)
    return DataPulseReader(inbox_path=str(inbox_path))


@pytest.fixture(autouse=True)
def _cleanup_env():
    yield
    os.environ.pop("DATAPULSE_SOURCE_CATALOG", None)
    os.environ.pop("DATAPULSE_STORIES_PATH", None)
    os.environ.pop("DATAPULSE_REPORTS_PATH", None)
    os.environ.pop("DATAPULSE_MEMORY_DIR", None)
    os.environ.pop("DATAPULSE_GROUNDING_BACKEND_CMD", None)
    os.environ.pop("DATAPULSE_GROUNDING_BACKEND_CALLABLE", None)
    os.environ.pop("DATAPULSE_GROUNDING_BACKEND_WORKDIR", None)
    os.environ.pop("DATAPULSE_GROUNDING_BACKEND_TIMEOUT_SECONDS", None)


def test_report_objects_can_be_created_loaded_updated_and_listed(tmp_path):
    reader = _reader(tmp_path)

    brief = reader.create_report_brief(
        title="Q1 Intelligence Brief",
        audience="analysis team",
        objective="weekly research production",
    )
    claim = reader.create_claim_card(
        brief_id=brief["id"],
        statement="Demand signals remain elevated after launch week.",
        confidence=0.82,
    )
    report = reader.create_report(
        title="AI Market Brief",
        brief_id=brief["id"],
        audience="leadership",
        summary="Drafted from selected claims.",
    )
    section = reader.create_report_section(
        report_id=report["id"],
        title="Executive Summary",
        claim_card_ids=[claim["id"]],
        position=1,
    )
    bundle = reader.create_citation_bundle(
        claim_card_id=claim["id"],
        label="Primary citations",
        source_urls=["https://example.com/source-a", "https://example.com/source-b"],
    )
    profile = reader.create_export_profile(
        report_id=report["id"],
        name="brief",
        output_format="markdown",
    )

    updated = reader.update_report(
        report["id"],
        title="AI Market Brief (v1)",
        status="ready",
        section_ids=[section["id"]],
        claim_card_ids=[claim["id"]],
        citation_bundle_ids=[bundle["id"]],
        export_profile_ids=[profile["id"]],
    )
    assert updated["title"] == "AI Market Brief (v1)"
    assert updated["status"] == "ready"
    assert updated["section_ids"] == [section["id"]]
    assert updated["claim_card_ids"] == [claim["id"]]
    assert updated["citation_bundle_ids"] == [bundle["id"]]
    assert updated["export_profile_ids"] == [profile["id"]]

    reloaded_reader = _reader(tmp_path)
    loaded = reloaded_reader.show_report(report["id"])
    assert loaded is not None
    assert loaded["title"] == "AI Market Brief (v1)"
    assert loaded["brief_id"] == brief["id"]
    assert reloaded_reader.list_reports(status="ready")[0]["id"] == report["id"]
    assert reloaded_reader.show_report_brief(brief["id"]) is not None
    assert reloaded_reader.show_claim_card(claim["id"]) is not None
    assert reloaded_reader.show_report_section(section["id"]) is not None
    assert reloaded_reader.show_citation_bundle(bundle["id"])["label"] == "Primary citations"
    assert reloaded_reader.show_export_profile(profile["id"]) is not None

    payload = json.loads(Path(os.environ["DATAPULSE_REPORTS_PATH"]).read_text(encoding="utf-8"))
    assert "report_briefs" in payload
    assert "claim_cards" in payload
    assert "report_sections" in payload
    assert "citation_bundles" in payload
    assert "reports" in payload
    assert "export_profiles" in payload


def test_report_aux_objects_support_updates_and_reloads(tmp_path):
    reader = _reader(tmp_path)
    claim = reader.create_claim_card(
        brief_id="",
        statement="A new claim needs evidence binding and review.",
    )
    section = reader.create_report_section(
        report_id="pending-report",
        title="Method Notes",
        position=2,
    )
    bundle = reader.create_citation_bundle(label="Raw evidence")
    profile = reader.create_export_profile(
        report_id="pending-report",
        name="json",
        output_format="json",
        include_sections=True,
        include_claim_cards=True,
        include_bundles=True,
        include_metadata=True,
    )
    report = reader.create_report(
        title="Pending Report",
        section_ids=[section["id"]],
        claim_card_ids=[claim["id"]],
        citation_bundle_ids=[bundle["id"]],
        export_profile_ids=[profile["id"]],
    )

    assert reader.update_claim_card(
        claim["id"],
        status="reviewed",
        confidence=0.93,
    )["status"] == "reviewed"
    assert reader.update_report_section(
        section["id"],
        status="ready",
        position=4,
    )["status"] == "ready"
    assert reader.update_citation_bundle(
        bundle["id"],
        note="Validated by platform logs",
        source_urls=["https://example.com/source-c"],
    )["note"] == "Validated by platform logs"
    assert reader.update_export_profile(
        profile["id"],
        include_metadata=False,
        output_format="md",
    )["include_metadata"] is False

    reloaded_reader = _reader(tmp_path)
    reloaded_claim = reloaded_reader.show_claim_card(claim["id"])
    reloaded_section = reloaded_reader.show_report_section(section["id"])
    reloaded_bundle = reloaded_reader.show_citation_bundle(bundle["id"])
    reloaded_profile = reloaded_reader.show_export_profile(profile["id"])
    reloaded_report = reloaded_reader.show_report(report["id"])

    assert reloaded_claim is not None
    assert reloaded_claim["status"] == "reviewed"
    assert reloaded_claim["confidence"] == 0.93
    assert reloaded_section is not None
    assert reloaded_section["position"] == 4
    assert reloaded_bundle is not None
    assert "Validated" in reloaded_bundle["note"]
    assert reloaded_profile is not None
    assert reloaded_profile["include_metadata"] is False
    assert reloaded_profile["output_format"] == "md"
    assert reloaded_report is not None
    assert reloaded_report["status"] == "draft"


def test_report_assembly_surfaces_source_binding_and_section_coverage_gates(tmp_path):
    reader = _reader(tmp_path)
    report = reader.create_report(title="Assembly Gate Report", summary="Quality gate coverage.")
    claim_with_source = reader.create_claim_card(
        statement="Source-backed claim.",
        brief_id="",
        source_item_ids=["item-source-a"],
    )
    claim_unbound = reader.create_claim_card(
        statement="Unbound claim.",
        brief_id="",
        citation_bundle_ids=["missing-bundle"],
    )
    section = reader.create_report_section(
        report_id=report["id"],
        title="Findings",
        claim_card_ids=[claim_with_source["id"], claim_unbound["id"]],
        position=1,
    )
    reader.update_report(
        report["id"],
        section_ids=[section["id"]],
        claim_card_ids=[claim_with_source["id"], claim_unbound["id"]],
    )

    assembled = reader.assemble_report(report["id"])
    assert assembled is not None
    assert assembled["quality"]["status"] == "review_required"
    assert assembled["quality"]["can_export"] is False
    source_binding = assembled["quality"]["checks"]["claim_source"]
    section_coverage = assembled["quality"]["checks"]["section_coverage"]
    assert any(
        item["kind"] == "uncited_claim"
        for item in source_binding["issues"]
    )
    assert section_coverage["status"] == "pass"


def test_report_assembly_blocks_export_on_contradiction_signals(tmp_path):
    reader = _reader(tmp_path)
    report = reader.create_report(title="Contradiction Report")
    contradictory_claim = reader.create_claim_card(
        statement="Conflicting claim has unresolved contradictions.",
        brief_id="",
        status="conflicted",
        governance={
            "contradictions": [
                {"detail": "Conflicting source line observed in the same period.", "severity": "error"}
            ],
        },
    )
    section = reader.create_report_section(
        report_id=report["id"],
        title="Contradictions",
        claim_card_ids=[contradictory_claim["id"]],
        position=1,
    )
    reader.update_report(
        report["id"],
        section_ids=[section["id"]],
        claim_card_ids=[contradictory_claim["id"]],
    )

    assembled = reader.assemble_report(report["id"])
    assert assembled is not None
    assert assembled["quality"]["status"] == "blocked"
    assert assembled["quality"]["checks"]["contradictions"]["status"] == "blocked"
    assert assembled["quality"]["checks"]["contradictions"]["entries"]
