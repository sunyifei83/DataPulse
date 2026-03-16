"""Tests for normalized delivery subscription persistence."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from datapulse.core.alerts import AlertEvent
from datapulse.reader import DataPulseReader


@pytest.fixture(autouse=True)
def _cleanup_env():
    yield
    os.environ.pop("DATAPULSE_SOURCE_CATALOG", None)
    os.environ.pop("DATAPULSE_STORIES_PATH", None)
    os.environ.pop("DATAPULSE_REPORTS_PATH", None)
    os.environ.pop("DATAPULSE_MEMORY_DIR", None)
    os.environ.pop("DATAPULSE_AI_SURFACE_ADMISSION_PATH", None)
    os.environ.pop("DATAPULSE_MODELBUS_BUNDLE_DIR", None)
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
        "request_id",
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
        "request_id",
    }
    gap_ids = {gap["gap_id"] for gap in report["rejectable_gaps"]}
    assert "missing_required_schema_contract" in gap_ids
    assert "report_draft.experimental:missing_contract_binding" in gap_ids
    assert report["requested_alias"] == "dp.report.draft"


def test_ai_delivery_summary_returns_contract_bound_alert_event_payload(tmp_path):
    reader = _reader(tmp_path)
    reader.create_alert_route(name="ops-webhook", channel="webhook", webhook_url="https://example.com/alert")

    event = AlertEvent(
        mission_id="watch-delivery",
        mission_name="Delivery Watch",
        rule_name="ops-threshold",
        channels=["json"],
        item_ids=["item-1"],
        summary="Delivery Watch triggered ops-threshold",
        delivered_channels=["json", "webhook:ops-webhook"],
        extra={
            "rule": {
                "name": "ops-threshold",
                "routes": ["ops-webhook"],
                "channels": ["json"],
            },
            "delivery_errors": {},
        },
    )
    reader.alert_store.add(event, cooldown_seconds=0)

    payload = reader.ai_delivery_summary(event.id, mode="assist")

    assert payload is not None
    assert payload["surface"] == "delivery_summary"
    assert payload["subject"] == {"kind": "AlertEvent", "id": event.id}
    assert payload["output"]["contract_id"] == "datapulse_ai_delivery_summary.v1"
    assert payload["output"]["output_kind"] == "summary"
    assert payload["runtime_facts"]["source"] == "deterministic"
    assert payload["runtime_facts"]["schema_valid"] is True
    assert payload["output"]["payload"]["overall_status"] == "healthy"

    routes = {row["name"]: row for row in payload["output"]["payload"]["routes"]}
    assert "ops-webhook" in routes
    assert routes["ops-webhook"]["status"] == "healthy"
    assert routes["ops-webhook"]["delivered_count"] >= 1
    assert "dispatch_explanation" in payload["output"]["payload"]


def test_runtime_hit_evidence_export_verifies_delivery_and_report_fail_closed(tmp_path):
    script_path = Path(__file__).resolve().parents[1] / "scripts/governance/export_datapulse_surface_runtime_hit_evidence.py"
    output_path = tmp_path / "datapulse_surface_runtime_hit_evidence.draft.json"
    bundle_dir = tmp_path / "modelbus-bundle"
    _write_modelbus_bundle(
        bundle_dir,
        [
            {
                "surface_id": "delivery_summary",
                "requested_alias": "dp.delivery.summary",
                "admission_status": "admitted",
                "admitted_alias": "dp.delivery.summary",
                "mode_admission": {"off": "manual_only", "assist": "admitted", "review": "admitted"},
                "schema_contract": "datapulse_ai_delivery_summary.v1",
                "manual_fallback": "manual_or_deterministic_behavior",
                "degraded_result_allowed": True,
                "must_expose_runtime_facts": [
                    "served_by_alias",
                    "fallback_used",
                    "degraded",
                    "schema_valid",
                    "manual_override_required",
                    "request_id",
                ],
                "rejectable_gaps": [],
            },
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
            },
        ],
    )

    subprocess.run(
        [
            sys.executable,
            str(script_path),
            "--bundle-dir",
            str(bundle_dir),
            "--output",
            str(output_path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(output_path.read_text(encoding="utf-8"))
    surfaces = {row["surface"]: row for row in payload["surfaces"]}

    assert payload["release_level_prerequisites"]["bundle_first_default_ready"] is True
    assert payload["release_level_prerequisites"]["shadow_change_prerequisites_met"] is True
    assert payload["release_level_prerequisites"]["required_change_prerequisites_met"] is True

    delivery = surfaces["delivery_summary"]
    assert delivery["evidence_status"] == "verified"
    assert delivery["schema_valid"] is True
    assert delivery["served_by_alias"] == "dp.delivery.summary"
    assert delivery["request_id"]

    report = surfaces["report_draft"]
    assert report["evidence_status"] == "verified_fail_closed"
    assert report["schema_valid"] is False
    assert report["fail_closed"] is True
    assert report["served_by_alias"] == "dp.report.draft"
    assert report["request_id"]


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
