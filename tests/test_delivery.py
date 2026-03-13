"""Tests for normalized delivery subscription persistence."""

from __future__ import annotations

import json
import os
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
