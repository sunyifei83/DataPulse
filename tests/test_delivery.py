"""Tests for normalized delivery subscription persistence."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from datapulse.reader import DataPulseReader


@pytest.fixture(autouse=True)
def _cleanup_env():
    yield
    os.environ.pop("DATAPULSE_SOURCE_CATALOG", None)
    os.environ.pop("DATAPULSE_STORIES_PATH", None)
    os.environ.pop("DATAPULSE_REPORTS_PATH", None)
    os.environ.pop("DATAPULSE_MEMORY_DIR", None)
    os.environ.pop("DATAPULSE_AI_SURFACE_ADMISSION_PATH", None)
    os.environ.pop("DATAPULSE_ALERT_ROUTING_PATH", None)
    os.environ.pop("DATAPULSE_WATCHLIST_PATH", None)
    os.environ.pop("DATAPULSE_GROUNDING_BACKEND_CMD", None)
    os.environ.pop("DATAPULSE_GROUNDING_BACKEND_CALLABLE", None)
    os.environ.pop("DATAPULSE_GROUNDING_BACKEND_WORKDIR", None)
    os.environ.pop("DATAPULSE_GROUNDING_BACKEND_TIMEOUT_SECONDS", None)


def _reader(tmp_path: Path) -> DataPulseReader:
    inbox_path = tmp_path / "inbox.json"
    catalog_path = tmp_path / "catalog.json"
    stories_path = tmp_path / "stories.json"
    reports_path = tmp_path / "reports.json"
    routes_path = tmp_path / "routes.json"
    watchlist_path = tmp_path / "watchlist.json"

    inbox_path.write_text("[]", encoding="utf-8")
    catalog_path.write_text('{"version":2,"sources":[],"subscriptions":{},"packs":[]}', encoding="utf-8")

    os.environ["DATAPULSE_MEMORY_DIR"] = str(tmp_path)
    os.environ["DATAPULSE_SOURCE_CATALOG"] = str(catalog_path)
    os.environ["DATAPULSE_STORIES_PATH"] = str(stories_path)
    os.environ["DATAPULSE_REPORTS_PATH"] = str(reports_path)
    os.environ["DATAPULSE_ALERT_ROUTING_PATH"] = str(routes_path)
    os.environ["DATAPULSE_WATCHLIST_PATH"] = str(watchlist_path)

    return DataPulseReader(inbox_path=str(inbox_path))


def test_normalized_delivery_subscriptions_are_persisted_for_multiple_subjects(tmp_path):
    reader = _reader(tmp_path)

    story = reader.create_story(
        title="Q4 Demand Story",
        summary="A synthetic story used for subscription binding.",
    )
    report = reader.create_report(
        title="Delivery Output Readiness",
        summary="Validate delivery subscription persistence.",
    )
    mission = reader.create_watch(name="Delivery Watch", query="AI chip recall")

    reader.create_alert_route(name="ops-webhook", channel="webhook", webhook_url="https://example.com/webhook")

    profile_sub = reader.create_delivery_subscription(
        subject_kind="profile",
        subject_ref="default",
        output_kind="feed_json",
        delivery_mode="pull",
        route_names=["Ops-Webhook", "ops-webhook"],
        cursor_or_since="2026-01-01T00:00:00Z",
    )
    watch_sub = reader.create_delivery_subscription(
        subject_kind="watch_mission",
        subject_ref=mission["id"],
        output_kind="alert_event",
        delivery_mode="push",
        route_names=["ops-webhook", "Ops-WebHook"],
    )
    story_sub = reader.create_delivery_subscription(
        subject_kind="story",
        subject_ref=story["id"],
        output_kind="story_json",
        delivery_mode="pull",
        cursor_or_since=story["id"],
    )
    report_sub = reader.create_delivery_subscription(
        subject_kind="report",
        subject_ref=report["id"],
        output_kind="report_full",
        delivery_mode="pull",
    )

    assert profile_sub["route_names"] == ["ops-webhook"]
    assert watch_sub["route_names"] == ["ops-webhook"]
    assert story_sub["status"] == "active"
    assert reader.update_delivery_subscription(report_sub["id"], status="paused", cursor_or_since="2026-03-01T00:00:00Z")["status"] == "paused"
    updated_profile = reader.update_delivery_subscription(
        profile_sub["id"],
        route_names=["OPS-WEBHOOK", "ops-webhook", ""],
        status="bogus",
    )
    assert updated_profile["route_names"] == ["ops-webhook"]
    assert updated_profile["status"] == "active"

    report_filtered = reader.list_delivery_subscriptions(
        subject_kind="report",
        output_kind="report_full",
    )
    mission_filtered = reader.list_delivery_subscriptions(
        subject_kind="watch_mission",
        delivery_mode="push",
        route_name="ops-webhook",
    )
    assert len(report_filtered) == 1
    assert len(mission_filtered) == 1

    reloaded_reader = _reader(tmp_path)
    assert reloaded_reader.show_delivery_subscription(report_sub["id"]) is not None
    assert reloaded_reader.show_delivery_subscription(profile_sub["id"]) is not None
    assert reloaded_reader.show_delivery_subscription(watch_sub["id"]) is not None
    assert reloaded_reader.show_delivery_subscription(story_sub["id"]) is not None

    payload = json.loads(Path(os.environ["DATAPULSE_REPORTS_PATH"]).read_text(encoding="utf-8"))
    assert "delivery_subscriptions" in payload
    assert len(payload["delivery_subscriptions"]) == 4
    for row in payload["delivery_subscriptions"]:
        assert isinstance(row["route_names"], list)
        assert "webhook_url" not in row
        assert "telegram_bot_token" not in row


def test_delivery_subscription_rejects_unknown_subject_and_output_kind(tmp_path):
    reader = _reader(tmp_path)

    with pytest.raises(ValueError, match="subject_kind"):
        reader.create_delivery_subscription(
            subject_kind="unknown",
            subject_ref="x",
            output_kind="feed_json",
            delivery_mode="pull",
        )

    with pytest.raises(ValueError, match="output_kind"):
        reader.create_delivery_subscription(
            subject_kind="profile",
            subject_ref="default",
            output_kind="unsupported_output",
            delivery_mode="pull",
        )


def test_ai_surface_admission_export_captures_runtime_semantics_and_rejections(tmp_path):
    script_path = Path(__file__).resolve().parents[1] / "scripts/governance/export_datapulse_ai_surface_admission_example.py"
    output_path = tmp_path / "datapulse-ai-surface-admission.example.json"

    subprocess.run(
        [sys.executable, str(script_path), "--output", str(output_path)],
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(output_path.read_text(encoding="utf-8"))
    surfaces = {row["surface"]: row for row in payload["surface_admissions"]}

    mission = surfaces["mission_suggest"]
    assert mission["mode_admission"] == {"off": "manual_only", "assist": "admitted", "review": "admitted"}
    assert set(mission["must_expose_runtime_facts"]) >= {
        "served_by_alias",
        "fallback_used",
        "degraded",
        "schema_valid",
        "manual_override_required",
    }
    assert mission["candidate_results"][0]["status"] == "admitted"

    report = surfaces["report_draft"]
    assert report["admission_status"] == "rejected"
    assert report["mode_admission"] == {"off": "manual_only", "assist": "rejected", "review": "rejected"}
    assert report["manual_fallback"] == "manual_or_deterministic_behavior"
    assert set(report["must_expose_runtime_facts"]) >= {
        "served_by_alias",
        "fallback_used",
        "degraded",
        "schema_valid",
        "manual_override_required",
    }
    gap_ids = {gap["gap_id"] for gap in report["rejectable_gaps"]}
    assert "missing_required_schema_contract" in gap_ids
    assert "report_draft.experimental:missing_contract_binding" in gap_ids


def test_report_delivery_package_is_deterministic_and_dispatch_records_are_attributable(tmp_path, monkeypatch):
    reader = _reader(tmp_path)

    report = reader.create_report(
        title="Dispatch Report",
        summary="A report used to validate deterministic package assembly.",
    )
    claim = reader.create_claim_card(
        statement="Report-backed output should preserve provenance.",
        brief_id="",
    )
    section = reader.create_report_section(
        report_id=report["id"],
        title="Dispatch Section",
        claim_card_ids=[claim["id"]],
        position=1,
    )
    reader.update_report(report["id"], section_ids=[section["id"]], claim_card_ids=[claim["id"]])

    reader.create_alert_route(name="ops-webhook", channel="webhook", webhook_url="https://example.com/report-dispatch")
    subscription = reader.create_delivery_subscription(
        subject_kind="report",
        subject_ref=report["id"],
        output_kind="report_full",
        delivery_mode="push",
        route_names=["ops-webhook"],
    )

    package_a = reader.build_report_delivery_package(subscription["id"])
    package_b = reader.build_report_delivery_package(subscription["id"])
    assert package_a["package_id"] == package_b["package_id"]
    assert package_a["package_signature"] == package_b["package_signature"]

    def _noop_send(route_target: dict[str, object], payload: dict[str, object]) -> None:
        return None

    monkeypatch.setattr(reader, "_send_report_delivery_payload_to_route", _noop_send)
    dispatch_rows = reader.dispatch_report_delivery(subscription["id"])

    assert len(dispatch_rows) == 1
    first = dispatch_rows[0]
    assert first["subscription_id"] == subscription["id"]
    assert first["subject_kind"] == "report"
    assert first["subject_ref"] == report["id"]
    assert first["route_name"] == "ops-webhook"
    assert first["status"] == "delivered"
    assert first["attempts"] == 1
    assert first["package_id"] == package_a["package_id"]

    persisted = reader.list_delivery_dispatch_records(subscription_id=subscription["id"], status="delivered")
    assert len(persisted) == 1
    assert persisted[0]["route_label"] == "webhook:ops-webhook"


def test_report_delivery_package_and_dispatch_reject_non_report_subscriptions(tmp_path):
    reader = _reader(tmp_path)

    story = reader.create_story(
        title="Delivery Story",
        summary="Used to validate report-only delivery helpers.",
    )
    subscription = reader.create_delivery_subscription(
        subject_kind="story",
        subject_ref=story["id"],
        output_kind="story_json",
        delivery_mode="pull",
    )

    with pytest.raises(ValueError, match="Only report subscriptions"):
        reader.build_report_delivery_package(subscription["id"])

    with pytest.raises(ValueError, match="Only report subscriptions"):
        reader.dispatch_report_delivery(subscription["id"])


def test_report_delivery_dispatch_records_capture_missing_routes_and_failures(tmp_path, monkeypatch):
    reader = _reader(tmp_path)

    report = reader.create_report(
        title="Dispatch Audit Report",
        summary="Validate missing-route and transport failure audit rows.",
    )
    claim = reader.create_claim_card(
        statement="Route-backed dispatch must stay attributable even when delivery fails.",
        source_item_ids=["item-route-audit"],
        brief_id="",
    )
    section = reader.create_report_section(
        report_id=report["id"],
        title="Audit Section",
        claim_card_ids=[claim["id"]],
        position=1,
    )
    reader.update_report(report["id"], section_ids=[section["id"]], claim_card_ids=[claim["id"]])

    reader.create_alert_route(name="ops-webhook", channel="webhook", webhook_url="https://example.com/report-audit")
    subscription = reader.create_delivery_subscription(
        subject_kind="report",
        subject_ref=report["id"],
        output_kind="report_full",
        delivery_mode="push",
        route_names=["OPS-WEBHOOK", "missing-route", "ops-webhook"],
    )

    def _fail_send(route_target: dict[str, object], payload: dict[str, object]) -> None:
        raise RuntimeError(f"transport down for {route_target.get('label', route_target.get('channel', 'route'))}")

    monkeypatch.setattr(reader, "_send_report_delivery_payload_to_route", _fail_send)
    dispatch_rows = reader.dispatch_report_delivery(subscription["id"])

    assert len(dispatch_rows) == 2
    rows_by_route = {row["route_name"]: row for row in dispatch_rows}
    assert set(rows_by_route) == {"ops-webhook", "missing-route"}

    missing_route = rows_by_route["missing-route"]
    assert missing_route["status"] == "missing_route"
    assert missing_route["attempts"] == 0
    assert missing_route["subscription_id"] == subscription["id"]
    assert missing_route["subject_ref"] == report["id"]
    assert missing_route["package_id"]

    failed_route = rows_by_route["ops-webhook"]
    assert failed_route["status"] == "failed"
    assert failed_route["attempts"] == 1
    assert failed_route["route_label"] == "webhook:ops-webhook"
    assert "transport down" in failed_route["error"]

    persisted_rows = reader.list_delivery_dispatch_records(subscription_id=subscription["id"])
    persisted_by_route = {row["route_name"]: row for row in persisted_rows}
    assert persisted_by_route["missing-route"]["status"] == "missing_route"
    assert persisted_by_route["missing-route"]["package_signature"] == failed_route["package_signature"]
    assert persisted_by_route["ops-webhook"]["status"] == "failed"
    assert persisted_by_route["ops-webhook"]["attempts"] == 1
