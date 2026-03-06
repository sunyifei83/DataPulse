"""Tests for DataPulseReader.trending degraded behavior."""

from __future__ import annotations

import asyncio
from unittest.mock import patch

from datapulse.collectors.trending import TrendingCollector, TrendItem, TrendSnapshot
from datapulse.reader import DataPulseReader


def _run(coro):
    return asyncio.run(coro)


def test_trending_low_signal_returns_empty_with_reason():
    reader = DataPulseReader()
    low_signal_snapshot = TrendSnapshot(
        timestamp="Explore more apps",
        trends=[TrendItem(rank=1, name="YouTube Trending Videos", volume="", volume_raw=0)],
    )

    def _fake_fetch(self, location: str = "", top_n: int = 20):  # noqa: ARG001
        if location in {"us", "united-states"}:
            raise ValueError("Low-signal trending snapshot (placeholder topics)")
        return [low_signal_snapshot]

    with patch.object(TrendingCollector, "fetch_snapshots", _fake_fetch):
        result = _run(reader.trending(location="us", top_n=20))

    assert result["requested_location"] == "us"
    assert result["location"] == "worldwide"
    assert result["trend_count"] == 0
    assert result["trends"] == []
    assert result["degraded"] is True
    assert "Low-signal trending snapshot" in result["fallback_reason"]
