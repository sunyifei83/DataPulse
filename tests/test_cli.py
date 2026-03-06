"""CLI output behavior tests."""

from __future__ import annotations

import sys

import datapulse.cli as cli


class _TrendingReader:
    async def trending(self, **kwargs):
        return {
            "location": "worldwide",
            "requested_location": "china",
            "fallback_reason": "404 Client Error: Not Found for url: https://trends24.in/china/",
            "snapshot_time": "2026-03-06T00:00:00Z",
            "trend_count": 1,
            "trends": [
                {"rank": 1, "name": "YouTube Trending Videos", "volume": "200K posts"},
            ],
        }


class _SearchReader:
    def __init__(self, results):
        self._results = results

    async def search(self, *args, **kwargs):
        return self._results


def test_trending_prints_fallback_context(monkeypatch, capsys):
    monkeypatch.setattr(cli, "DataPulseReader", lambda: _TrendingReader())
    monkeypatch.setattr(
        sys,
        "argv",
        ["datapulse", "--trending", "china", "--trending-limit", "1"],
    )

    cli.main()
    out = capsys.readouterr().out

    assert "Trending Topics on X (worldwide)" in out
    assert "Requested location: china" in out
    assert "Fallback reason: 404 Client Error: Not Found" in out


def test_search_empty_with_zero_threshold_message(monkeypatch, capsys):
    monkeypatch.setattr(cli, "DataPulseReader", lambda: _SearchReader(results=[]))
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "datapulse",
            "--search",
            "data governance",
            "--min-confidence",
            "0.0",
        ],
    )

    cli.main()
    out = capsys.readouterr().out

    assert "No search results returned" in out


def test_search_empty_with_positive_threshold_message(monkeypatch, capsys):
    monkeypatch.setattr(cli, "DataPulseReader", lambda: _SearchReader(results=[]))
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "datapulse",
            "--search",
            "data governance",
            "--min-confidence",
            "0.5",
        ],
    )

    cli.main()
    out = capsys.readouterr().out

    assert "No search results above confidence threshold" in out
