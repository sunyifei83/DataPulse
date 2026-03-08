"""Tests for watch alert evaluation and distribution."""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from datapulse.core.models import DataPulseItem, SourceType
from datapulse.reader import DataPulseReader


@pytest.mark.asyncio
async def test_watch_alert_rule_triggers_and_writes_markdown(tmp_path, monkeypatch):
    monkeypatch.setenv("DATAPULSE_WATCHLIST_PATH", str(tmp_path / "watchlist.json"))
    monkeypatch.setenv("DATAPULSE_ALERTS_PATH", str(tmp_path / "alerts.json"))
    monkeypatch.setenv("DATAPULSE_ALERTS_MARKDOWN_PATH", str(tmp_path / "alerts.md"))

    reader = DataPulseReader(inbox_path=str(tmp_path / "inbox.json"))
    mission = reader.create_watch(
        name="AI Radar",
        query="OpenAI agents",
        alert_rules=[
            {
                "name": "threshold",
                "min_score": 70,
                "min_confidence": 0.8,
                "min_results": 1,
                "channels": ["json", "markdown"],
            }
        ],
    )

    async def fake_search(query, **kwargs):
        item = DataPulseItem(
            source_type=SourceType.GENERIC,
            source_name="search",
            title="OpenAI agents result",
            content="Synthetic search result content",
            url="https://example.com/openai-agents",
            confidence=0.91,
            score=74,
        )
        reader.inbox.add(item, fingerprint_dedup=False)
        reader.inbox.save()
        return [item]

    monkeypatch.setattr(reader, "search", fake_search)

    payload = await reader.run_watch(mission["id"])

    assert len(payload["alert_events"]) == 1
    assert payload["alert_events"][0]["governance"]["evidence_grade"] == "working"
    assert payload["alert_events"][0]["governance"]["delivery_risk"]["status"] == "review_required"
    alerts = reader.list_alerts(limit=10)
    assert len(alerts) == 1
    assert alerts[0]["rule_name"] == "threshold"
    assert alerts[0]["governance"]["provenance"]["mission_id"] == mission["id"]
    markdown = Path(tmp_path / "alerts.md").read_text(encoding="utf-8")
    assert "AI Radar | threshold" in markdown
    assert "evidence_grade: working" in markdown
    assert "OpenAI agents result" in markdown


@pytest.mark.asyncio
async def test_watch_alert_cooldown_suppresses_duplicate(tmp_path, monkeypatch):
    monkeypatch.setenv("DATAPULSE_WATCHLIST_PATH", str(tmp_path / "watchlist.json"))
    monkeypatch.setenv("DATAPULSE_ALERTS_PATH", str(tmp_path / "alerts.json"))

    reader = DataPulseReader(inbox_path=str(tmp_path / "inbox.json"))
    mission = reader.create_watch(
        name="AI Radar",
        query="OpenAI agents",
        alert_rules=[
            {
                "name": "threshold",
                "min_score": 70,
                "min_confidence": 0.8,
                "min_results": 1,
                "cooldown_seconds": 3600,
            }
        ],
    )

    async def fake_search(query, **kwargs):
        item = DataPulseItem(
            source_type=SourceType.GENERIC,
            source_name="search",
            title="OpenAI agents result",
            content="Synthetic search result content",
            url="https://example.com/openai-agents",
            confidence=0.91,
            score=74,
        )
        reader.inbox.add(item, fingerprint_dedup=False)
        reader.inbox.save()
        return [item]

    monkeypatch.setattr(reader, "search", fake_search)

    first = await reader.run_watch(mission["id"])
    second = await reader.run_watch(mission["id"])

    assert len(first["alert_events"]) == 1
    assert second["alert_events"] == []
    assert len(reader.list_alerts(limit=10)) == 1


@pytest.mark.asyncio
async def test_watch_alert_external_channels_dispatch(tmp_path, monkeypatch):
    monkeypatch.setenv("DATAPULSE_WATCHLIST_PATH", str(tmp_path / "watchlist.json"))
    monkeypatch.setenv("DATAPULSE_ALERTS_PATH", str(tmp_path / "alerts.json"))
    monkeypatch.setenv("DATAPULSE_ALERT_WEBHOOK_URL", "https://hooks.example.com/datapulse")
    monkeypatch.setenv("DATAPULSE_FEISHU_WEBHOOK_URL", "https://open.feishu.cn/hook/abc")
    monkeypatch.setenv("DATAPULSE_TELEGRAM_BOT_TOKEN", "bot-token")
    monkeypatch.setenv("DATAPULSE_TELEGRAM_CHAT_ID", "chat-1")

    reader = DataPulseReader(inbox_path=str(tmp_path / "inbox.json"))
    mission = reader.create_watch(
        name="AI Radar",
        query="OpenAI agents",
        alert_rules=[
            {
                "name": "notify",
                "min_score": 70,
                "min_confidence": 0.8,
                "channels": ["webhook", "feishu", "telegram"],
            }
        ],
    )

    async def fake_search(query, **kwargs):
        item = DataPulseItem(
            source_type=SourceType.GENERIC,
            source_name="search",
            title="OpenAI agents result",
            content="Synthetic search result content",
            url="https://example.com/openai-agents",
            confidence=0.91,
            score=74,
        )
        reader.inbox.add(item, fingerprint_dedup=False)
        reader.inbox.save()
        return [item]

    calls: list[tuple[str, dict]] = []

    class _Resp:
        def raise_for_status(self):
            return None

    def fake_post(url, json=None, headers=None, timeout=0):
        calls.append((url, json or {}))
        return _Resp()

    monkeypatch.setattr(reader, "search", fake_search)
    monkeypatch.setattr("datapulse.core.alerts.requests.post", fake_post)

    payload = await reader.run_watch(mission["id"])

    assert len(payload["alert_events"]) == 1
    delivered = payload["alert_events"][0]["delivered_channels"]
    assert "webhook" in delivered
    assert "feishu" in delivered
    assert "telegram" in delivered
    observations = payload["alert_events"][0]["governance"]["delivery_risk"]["route_observations"]
    assert any(row["label"] == "webhook" and row["status"] == "delivered" for row in observations)
    assert len(calls) == 3
    assert calls[0][0] == "https://hooks.example.com/datapulse"
    assert calls[1][0] == "https://open.feishu.cn/hook/abc"
    assert calls[2][0] == "https://api.telegram.org/botbot-token/sendMessage"


@pytest.mark.asyncio
async def test_watch_alert_rich_filters_and_named_routes(tmp_path, monkeypatch):
    monkeypatch.setenv("DATAPULSE_WATCHLIST_PATH", str(tmp_path / "watchlist.json"))
    monkeypatch.setenv("DATAPULSE_ALERTS_PATH", str(tmp_path / "alerts.json"))
    monkeypatch.setenv("DATAPULSE_ALERT_ROUTING_PATH", str(tmp_path / "alert-routes.json"))

    (tmp_path / "alert-routes.json").write_text(
        json.dumps(
            {
                "routes": {
                    "ops-webhook": {
                        "channel": "webhook",
                        "webhook_url": "https://hooks.example.com/ops",
                    },
                    "ops-telegram": {
                        "channel": "telegram",
                        "telegram_bot_token": "bot-token",
                        "telegram_chat_id": "chat-1",
                    },
                }
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    reader = DataPulseReader(inbox_path=str(tmp_path / "inbox.json"))
    mission = reader.create_watch(
        name="Launch Radar",
        query="OpenAI launch",
        alert_rules=[
            {
                "name": "launch-route",
                "min_score": 70,
                "min_confidence": 0.8,
                "required_tags": ["watch", "launch"],
                "domains": ["openai.com"],
                "keyword_any": ["launch"],
                "exclude_keywords": ["rumor"],
                "source_types": ["generic"],
                "max_age_minutes": 60,
                "routes": ["ops-webhook", "ops-telegram"],
            }
        ],
    )

    async def fake_search(query, **kwargs):
        now = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
        old = (datetime.now(timezone.utc) - timedelta(hours=3)).replace(microsecond=0).isoformat()
        matched = DataPulseItem(
            source_type=SourceType.GENERIC,
            source_name="search",
            title="OpenAI launch confirmed",
            content="OpenAI launch details are live now.",
            url="https://openai.com/blog/openai-launch",
            confidence=0.95,
            score=86,
            fetched_at=now,
            tags=["watch", "launch"],
        )
        excluded = DataPulseItem(
            source_type=SourceType.GENERIC,
            source_name="search",
            title="OpenAI launch rumor",
            content="Rumor only, not confirmed.",
            url="https://openai.com/blog/rumor",
            confidence=0.97,
            score=88,
            fetched_at=now,
            tags=["watch", "launch"],
        )
        stale = DataPulseItem(
            source_type=SourceType.GENERIC,
            source_name="search",
            title="Old launch note",
            content="Older OpenAI launch context.",
            url="https://openai.com/blog/old-launch",
            confidence=0.91,
            score=82,
            fetched_at=old,
            tags=["watch", "launch"],
        )
        return [matched, excluded, stale]

    calls: list[tuple[str, dict]] = []

    class _Resp:
        def raise_for_status(self):
            return None

    def fake_post(url, json=None, headers=None, timeout=0):
        calls.append((url, json or {}))
        return _Resp()

    monkeypatch.setattr(reader, "search", fake_search)
    monkeypatch.setattr("datapulse.core.alerts.requests.post", fake_post)

    payload = await reader.run_watch(mission["id"])

    assert len(payload["alert_events"]) == 1
    delivered = payload["alert_events"][0]["delivered_channels"]
    assert "webhook:ops-webhook" in delivered
    assert "telegram:ops-telegram" in delivered
    observations = payload["alert_events"][0]["governance"]["delivery_risk"]["route_observations"]
    assert any(row["label"] == "webhook:ops-webhook" and row["status"] == "delivered" for row in observations)
    assert any(row["label"] == "telegram:ops-telegram" and row["status"] == "delivered" for row in observations)
    assert len(calls) == 2
    assert calls[0][0] == "https://hooks.example.com/ops"
    assert calls[1][0] == "https://api.telegram.org/botbot-token/sendMessage"


def test_alert_route_store_redacts_sensitive_fields(tmp_path, monkeypatch):
    monkeypatch.setenv("DATAPULSE_ALERT_ROUTING_PATH", str(tmp_path / "alert-routes.json"))
    (tmp_path / "alert-routes.json").write_text(
        json.dumps(
            {
                "routes": {
                    "ops-webhook": {
                        "channel": "webhook",
                        "webhook_url": "https://hooks.example.com/ops",
                        "authorization": "Bearer secret",
                    }
                }
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    reader = DataPulseReader(inbox_path=str(tmp_path / "inbox.json"))
    routes = reader.list_alert_routes()

    assert routes[0]["name"] == "ops-webhook"
    assert routes[0]["authorization"] == "***"


@pytest.mark.asyncio
async def test_alert_route_health_reports_degraded_named_route(tmp_path, monkeypatch):
    monkeypatch.setenv("DATAPULSE_WATCHLIST_PATH", str(tmp_path / "watchlist.json"))
    monkeypatch.setenv("DATAPULSE_ALERTS_PATH", str(tmp_path / "alerts.json"))
    monkeypatch.setenv("DATAPULSE_ALERT_ROUTING_PATH", str(tmp_path / "alert-routes.json"))

    (tmp_path / "alert-routes.json").write_text(
        json.dumps(
            {
                "routes": {
                    "ops-webhook": {
                        "channel": "webhook",
                    }
                }
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    reader = DataPulseReader(inbox_path=str(tmp_path / "inbox.json"))
    mission = reader.create_watch(
        name="Launch Radar",
        query="OpenAI launch",
        alert_rules=[
            {
                "name": "route-alert",
                "min_score": 70,
                "min_confidence": 0.8,
                "routes": ["ops-webhook"],
            }
        ],
    )

    async def fake_search(query, **kwargs):
        item = DataPulseItem(
            source_type=SourceType.GENERIC,
            source_name="search",
            title="OpenAI launch confirmed",
            content="OpenAI launch details are live now.",
            url="https://openai.com/blog/openai-launch",
            confidence=0.95,
            score=86,
        )
        return [item]

    monkeypatch.setattr(reader, "search", fake_search)

    await reader.run_watch(mission["id"])
    health = reader.alert_route_health(limit=10)
    alerts = reader.list_alerts(limit=10)

    assert len(health) == 1
    assert health[0]["name"] == "ops-webhook"
    assert health[0]["status"] == "degraded"
    assert health[0]["delivered_count"] == 0
    assert health[0]["failure_count"] == 1
    assert "webhook_url is required" in health[0]["last_error"]
    assert alerts[0]["governance"]["delivery_risk"]["status"] == "degraded"
