"""Tests for report-production core objects and repository persistence."""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

import datapulse.reader as reader_module
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


def _write_modelbus_bundle(bundle_dir: Path, rows: list[dict[str, object]]) -> None:
    bundle_dir.mkdir(parents=True, exist_ok=True)
    alias_by_surface: dict[str, str] = {}
    for row in rows:
        surface_id = str(row.get("surface_id", "") or "").strip()
        alias = str(row.get("requested_alias", "") or row.get("admitted_alias", "") or "").strip()
        if surface_id and alias:
            alias_by_surface[surface_id] = alias
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
                    "release_level": "ci_proven",
                    "assured_verdict": "pass",
                    "constitutional_semantics": "BUNDLE-FIRST-REQUIRED",
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
                "alias_by_surface": alias_by_surface,
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
                "release_level": "ci_proven",
                "assured_verdict": "pass",
                "runtime": {"base_url": "https://modelbus.example.com"},
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )


@pytest.fixture(autouse=True)
def _cleanup_env():
    yield
    os.environ.pop("DATAPULSE_SOURCE_CATALOG", None)
    os.environ.pop("DATAPULSE_STORIES_PATH", None)
    os.environ.pop("DATAPULSE_REPORTS_PATH", None)
    os.environ.pop("DATAPULSE_MEMORY_DIR", None)
    os.environ.pop("DATAPULSE_AI_SURFACE_ADMISSION_PATH", None)
    os.environ.pop("DATAPULSE_MODELBUS_BUNDLE_DIR", None)
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


def test_report_creation_seeds_default_export_profiles_and_watch_pack(tmp_path):
    reader = _reader(tmp_path)
    report = reader.create_report(
        title="Watch Pack Readiness Report",
        summary="A synthetic report designed to validate report export defaults.",
    )
    claim = reader.create_claim_card(
        statement="Demand for compact edge inference spikes during launch windows.",
        source_item_ids=["item-edge-001"],
        brief_id="",
    )
    section = reader.create_report_section(
        report_id=report["id"],
        title="Signal Signals",
        claim_card_ids=[claim["id"]],
        position=1,
    )
    bundle = reader.create_citation_bundle(
        claim_card_id=claim["id"],
        label="Edge demand evidence",
        source_urls=["https://example.com/edge-sensor"],
    )
    claim = reader.update_claim_card(claim["id"], citation_bundle_ids=[bundle["id"]])
    reader.update_report(
        report["id"],
        section_ids=[section["id"]],
        claim_card_ids=[claim["id"]],
        citation_bundle_ids=[bundle["id"]],
    )
    profile_rows = reader.list_export_profiles(report_id=report["id"])
    profile_map = {row["name"]: row for row in profile_rows}

    assert set(profile_map.keys()) >= {"brief", "full", "sources", "watch-pack"}
    assert profile_map["brief"]["include_sections"] is True
    assert profile_map["brief"]["include_claim_cards"] is False
    assert profile_map["full"]["include_sections"] is True
    assert profile_map["full"]["include_claim_cards"] is True
    assert profile_map["full"]["include_bundles"] is True

    brief_payload = reader.compose_report(report["id"], profile_id=profile_map["brief"]["id"])
    sources_payload = reader.compose_report(report["id"], profile_id=profile_map["sources"]["id"])
    full_payload = reader.compose_report(report["id"], profile_id=profile_map["full"]["id"])
    watch_pack_payload = reader.compose_report(report["id"], profile_id=profile_map["watch-pack"]["id"])

    assert brief_payload is not None
    assert brief_payload["claim_cards"] == []
    assert full_payload["claim_cards"] == [claim]
    assert full_payload["citation_bundles"] == [bundle]
    assert sources_payload["citation_bundles"] == [bundle]
    assert "watch_pack" in watch_pack_payload
    assert watch_pack_payload["watch_pack"]["report_id"] == report["id"]
    assert watch_pack_payload["watch_pack"]["mission_name"].startswith("Watch Pack Readiness Report")


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


def test_ai_claim_draft_returns_bound_draft_without_persisting(tmp_path):
    reader = _reader(tmp_path)
    story = reader.create_story(
        title="Edge Inference Demand",
        summary="Demand for edge inference kits accelerated after launch week.",
        status="active",
        item_count=2,
        confidence=0.82,
        entities=["Acme", "Edge"],
        primary_evidence=[
            {
                "item_id": "item-1",
                "title": "Launch demand update",
                "url": "https://example.com/item-1",
                "source_name": "example",
                "source_type": "generic",
                "review_state": "verified",
            }
        ],
        secondary_evidence=[
            {
                "item_id": "item-2",
                "title": "Partner recap",
                "url": "https://example.com/item-2",
                "source_name": "example",
                "source_type": "generic",
                "review_state": "triaged",
            }
        ],
        semantic_review={
            "claim_candidates": [
                "Demand for edge inference kits accelerated after launch week.",
                "Channel partners reported higher attach rates for edge deployments.",
            ]
        },
        contradictions=[],
    )

    payload = reader.ai_claim_draft(story["id"], mode="assist")

    assert payload is not None
    assert payload["precheck"]["mode_status"] == "admitted"
    assert set(payload["precheck"]["must_expose_runtime_facts"]) >= {
        "served_by_alias",
        "fallback_used",
        "degraded",
        "schema_valid",
        "manual_override_required",
    }
    assert payload["bridge_request"]["governance"]["allow_final_state_write"] is False
    assert payload["bridge_request"]["governance"]["allow_degraded_result"] is False
    assert payload["output"]["contract_id"] == "datapulse_ai_claim_draft.v1"
    draft = payload["output"]["payload"]
    assert draft["claim_cards"]
    assert draft["claim_cards"][0]["source_item_ids"] == ["item-1", "item-2"]
    assert draft["claim_cards"][0]["governance"]["evidence_status"] == "bound"
    assert payload["runtime_facts"]["source"] == "deterministic"
    assert reader.list_claim_cards(limit=10) == []
    assert payload["runtime_facts"]["manual_override_required"] is True
    assert payload["runtime_facts"]["served_by_alias"] == payload["precheck"]["alias"]


def test_ai_claim_draft_rejects_when_admission_facts_are_missing(monkeypatch, tmp_path):
    reader = _reader(tmp_path)
    story = reader.create_story(
        title="Admission Missing Story",
        summary="Exercise fail-closed behavior when admission facts are unavailable.",
        status="active",
        item_count=1,
        confidence=0.6,
        primary_evidence=[
            {
                "item_id": "item-1",
                "title": "Only evidence row",
                "url": "https://example.com/item-1",
                "source_name": "example",
                "source_type": "generic",
                "review_state": "verified",
            }
        ],
    )
    missing_path = tmp_path / "missing-ai-surface-admission.json"
    monkeypatch.setattr(reader_module, "_CANONICAL_MODELBUS_BUNDLE_DIR", tmp_path / "missing-canonical-bundle")
    monkeypatch.setenv("DATAPULSE_AI_SURFACE_ADMISSION_PATH", str(missing_path))

    payload = reader.ai_claim_draft(story["id"], mode="review")

    assert payload is not None
    assert payload["precheck"]["ok"] is False
    assert payload["precheck"]["mode"] == "review"
    assert payload["precheck"]["mode_status"] == "rejected"
    assert payload["precheck"]["admission_errors"]
    assert payload["precheck"]["admission_errors"][0].startswith("canonical bundle failed:")
    assert any(
        "local snapshot diagnostic: admission file missing:" in error
        for error in payload["precheck"]["admission_errors"]
    )
    assert payload["output"] is None
    assert payload["runtime_facts"]["status"] == "rejected"
    assert payload["runtime_facts"]["fallback_used"] is True
    assert payload["runtime_facts"]["manual_override_required"] is True


def test_ai_claim_draft_fails_closed_on_invalid_payload(monkeypatch, tmp_path):
    reader = _reader(tmp_path)
    story = reader.create_story(
        title="Broken Story",
        summary="This story exists only to exercise invalid AI draft output.",
        status="active",
        item_count=1,
        confidence=0.4,
        primary_evidence=[
            {
                "item_id": "item-1",
                "title": "Only evidence row",
                "url": "https://example.com/item-1",
                "source_name": "example",
                "source_type": "generic",
                "review_state": "triaged",
            }
        ],
    )
    monkeypatch.setattr("datapulse.reader.build_claim_draft_from_story", lambda *args, **kwargs: {"summary": "bad", "claim_cards": []})

    payload = reader.ai_claim_draft(story["id"], mode="assist")

    assert payload is not None
    assert payload["output"] is None
    assert payload["runtime_facts"]["status"] == "invalid"
    assert payload["runtime_facts"]["schema_valid"] is False
    assert payload["runtime_facts"]["fallback_used"] is True
    assert payload["runtime_facts"]["manual_override_required"] is True
    assert payload["runtime_facts"]["served_by_alias"] == payload["precheck"]["alias"]


def test_ai_report_draft_returns_fail_closed_runtime_projection_when_contract_is_missing(monkeypatch, tmp_path):
    reader = _reader(tmp_path)
    report = reader.create_report(
        title="Runtime Closure Report",
        summary="Exercise report_draft fail-closed runtime projection under bundle-first admission.",
    )
    claim = reader.create_claim_card(
        statement="Fail-closed runtime surfaces must stay attributable and replayable.",
        brief_id="",
    )
    section = reader.create_report_section(
        report_id=report["id"],
        title="Runtime Closure",
        claim_card_ids=[claim["id"]],
        position=1,
    )
    reader.update_report(report["id"], section_ids=[section["id"]], claim_card_ids=[claim["id"]])

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
                "schema_contract": "",
                "manual_fallback": "manual_or_deterministic_behavior",
                "degraded_result_allowed": False,
                "must_expose_runtime_facts": [
                    "served_by_alias",
                    "fallback_used",
                    "degraded",
                    "schema_valid",
                    "manual_override_required",
                    "request_id",
                ],
                "rejectable_gaps": [
                    {
                        "gap_id": "missing_structured_contract",
                        "blocking": True,
                        "reason": "report_draft remains blocked until an admitted structured contract lands.",
                    }
                ],
            }
        ],
    )
    monkeypatch.setenv("DATAPULSE_MODELBUS_BUNDLE_DIR", str(bundle_dir))
    monkeypatch.setattr(reader_module, "_CANONICAL_MODELBUS_BUNDLE_DIR", tmp_path / "missing-canonical-bundle")

    payload = reader.ai_report_draft(report["id"], mode="review")

    assert payload is not None
    assert payload["surface"] == "report_draft"
    assert payload["precheck"]["ok"] is False
    assert payload["precheck"]["alias"] == "dp.report.draft"
    assert payload["bridge_request"]["alias"] == "dp.report.draft"
    assert payload["output"] is None
    assert payload["runtime_facts"]["status"] == "rejected"
    assert payload["runtime_facts"]["request_id"]
    assert payload["runtime_facts"]["schema_valid"] is False
    assert payload["runtime_facts"]["served_by_alias"] == "dp.report.draft"
    assert "missing_structured_contract" in payload["runtime_facts"]["errors"]
