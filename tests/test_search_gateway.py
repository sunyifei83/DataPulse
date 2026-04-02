"""Tests for SearchGateway normalization and deduplication behavior."""

from __future__ import annotations

import pytest

from datapulse.core.search_gateway import SearchGateway, SearchHit


def test_resolve_providers_auto_chinese_candidate(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("DATAPULSE_SEARCH_QNAIGC_ENABLED", "1")
    monkeypatch.setenv("QNAIGC_TOKEN_A", "token-a")
    gateway = SearchGateway()

    providers = gateway._resolve_providers("how to 提升", provider="auto", mode="single")
    assert providers[:1] == ["qnaigc"]
    assert "tavily" in providers and "jina" in providers

    providers_non_chinese = gateway._resolve_providers("how to upgrade", provider="auto", mode="single")
    assert providers_non_chinese[0] == "tavily"
    assert "qnaigc" not in providers_non_chinese


def test_qnaigc_token_absence_removes_auto_candidate(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("DATAPULSE_SEARCH_QNAIGC_ENABLED", "1")
    gateway = SearchGateway()
    gateway._qnaigc_tokens = []

    providers = gateway._resolve_providers("中文", provider="auto", mode="single")
    assert providers[0] == "tavily"
    assert "qnaigc" not in providers


def test_resolve_providers_prefers_planning_hints(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("DATAPULSE_SEARCH_QNAIGC_ENABLED", "1")
    monkeypatch.setenv("QNAIGC_TOKEN_A", "token-a")
    gateway = SearchGateway()

    providers = gateway._resolve_providers(
        "OpenAI launch",
        provider="auto",
        mode="single",
        provider_hints=["qnaigc", "jina"],
    )

    assert providers[:3] == ["qnaigc", "jina", "tavily"]


def test_search_qnaigc_maps_authority_score_date_request_id(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("DATAPULSE_SEARCH_QNAIGC_ENABLED", "1")
    monkeypatch.setenv("QNAIGC_TOKEN_A", "token-a")

    class FakeResponse:
        def __init__(self, payload):
            self.status_code = 200
            self._payload = payload
            self.headers = {}

        def json(self):
            return self._payload

    captured = {}

    def fake_post(url, *, json, headers, timeout):
        captured["url"] = url
        captured["json"] = json
        captured["headers"] = headers
        captured["timeout"] = timeout
        return FakeResponse(
            {
                "request_id": "qnaigc-request-id",
                "results": [
                    {
                        "title": "演进测试",
                        "url": "https://search.example.com/article/123",
                        "snippet": "关键结论摘要",
                        "authority_score": 0.91,
                        "date": "2026-03-01",
                    }
                ],
            }
        )

    import requests

    monkeypatch.setattr(requests, "post", fake_post)

    gateway = SearchGateway()
    hits, audit = gateway.search("中文 搜索", limit=3, provider="auto", sites=["a.com", "b.com"])

    assert len(hits) == 1
    hit = hits[0]
    assert hit.provider == "qnaigc"
    assert hit.extra["authority_score"] == 0.91
    assert hit.extra["date"] == "2026-03-01"
    assert hit.extra["request_id"] == "qnaigc-request-id"
    assert audit["provider_chain"][0] == "qnaigc"
    assert captured["url"] == "https://api.qnaigc.com/v1/search/web"
    assert captured["json"]["max_results"] == 3
    assert captured["json"]["site_filter"] == ["a.com", "b.com"]
    assert audit["estimated_cost_total"] == gateway._qnaigc_cost_per_call


def test_search_qnaigc_429_falls_back_to_next_provider(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("DATAPULSE_SEARCH_QNAIGC_ENABLED", "1")
    monkeypatch.setenv("QNAIGC_TOKEN_A", "token-a")

    class FakeResponse:
        def __init__(self, status_code: int, payload=None):
            self.status_code = status_code
            self._payload = payload or {}
            self.headers = {}

        def json(self):
            return self._payload

    def fake_post(url, *, json, headers, timeout):
        return FakeResponse(429, {"error": "rate limited"})

    def fake_tavily(
        *,
        query: str,
        sites: list[str] | None,
        limit: int,
        deep: bool,
        news: bool,
        time_range=None,
    ):
        return [
            SearchHit(
                title="Tavily fallback",
                url="https://example.com/tavily",
                snippet="Fallback from tavily",
                provider="tavily",
                source="tavily",
                score=0.1,
                raw={},
                extra={"sources": ["tavily"]},
            )
        ]

    import requests

    monkeypatch.setattr(requests, "post", fake_post)

    gateway = SearchGateway()
    monkeypatch.setattr(gateway, "_search_tavily", fake_tavily)
    hits, audit = gateway.search("中文 热点", limit=1, provider="auto")

    assert len(hits) == 1
    assert hits[0].provider == "tavily"
    assert len(audit["attempts"]) == 2
    assert audit["attempts"][0]["provider"] == "qnaigc"
    assert audit["attempts"][0]["status"] == "error"
    assert "rate limit" in str(audit["attempts"][0]["error"]).lower()
    assert audit["attempts"][0]["estimated_cost"] == gateway._qnaigc_cost_per_call
    assert audit["estimated_cost_total"] == gateway._qnaigc_cost_per_call
    assert audit["attempts"][1]["provider"] == "tavily"
    assert audit["attempts"][1]["status"] == "ok"


def test_search_qnaigc_contract_drift_falls_back(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("DATAPULSE_SEARCH_QNAIGC_ENABLED", "1")
    monkeypatch.setenv("QNAIGC_TOKEN_A", "token-a")

    class FakeResponse:
        def __init__(self, payload):
            self.status_code = 200
            self._payload = payload
            self.headers = {}

        def json(self):
            return self._payload

    def fake_post(url, *, json, headers, timeout):
        return FakeResponse({"data": {"result": {"invalid": True}}})

    def fake_tavily(
        *,
        query: str,
        sites: list[str] | None,
        limit: int,
        deep: bool,
        news: bool,
        time_range=None,
    ):
        return [
            SearchHit(
                title="Tavily fallback",
                url="https://example.com/tavily",
                snippet="Fallback from tavily",
                provider="tavily",
                source="tavily",
                score=0.2,
                raw={},
                extra={"sources": ["tavily"]},
            )
        ]

    import requests

    monkeypatch.setattr(requests, "post", fake_post)

    gateway = SearchGateway()
    monkeypatch.setattr(gateway, "_search_tavily", fake_tavily)
    hits, audit = gateway.search("中文 资讯", limit=1, provider="auto")

    assert len(hits) == 1
    assert hits[0].provider == "tavily"
    assert len(audit["attempts"]) == 2
    assert audit["attempts"][0]["provider"] == "qnaigc"
    assert audit["attempts"][0]["status"] == "error"
    assert "malformed" in str(audit["attempts"][0]["error"]).lower()
    assert audit["estimated_cost_total"] == gateway._qnaigc_cost_per_call


def test_search_qnaigc_direct_call_fail_closed_when_token_missing(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("DATAPULSE_SEARCH_QNAIGC_ENABLED", "1")
    monkeypatch.delenv("QNAIGC_TOKEN_A", raising=False)
    monkeypatch.delenv("QNAIGC_TOKEN_B", raising=False)

    gateway = SearchGateway()
    gateway._qnaigc_tokens = []
    hits, audit = gateway.search("中文 search", provider="qnaigc", limit=1)

    assert hits == []
    assert audit["provider_chain"] == ["qnaigc"]
    assert audit["attempts"][0]["status"] == "error"
    assert audit["attempts"][0]["estimated_cost"] == 0.0
    assert audit["estimated_cost_total"] == 0.0


def test_normalize_url_collapses_research_mirror_subdomain():
    gateway = SearchGateway()
    mirror = "https://research.aimultiple.com/open-source-data-governance"
    canonical = "https://aimultiple.com/open-source-data-governance"

    assert gateway._normalize_url(mirror) == gateway._normalize_url(canonical)


def test_dedupe_hits_merges_mirror_pages():
    gateway = SearchGateway()
    hit_a = SearchHit(
        title="Open Source Data Governance Tools",
        url="https://research.aimultiple.com/open-source-data-governance",
        snippet="Top open source options for data governance.",
        provider="tavily",
        source="tavily",
        score=0.83,
        extra={"sources": ["tavily"]},
    )
    hit_b = SearchHit(
        title="Open Source Data Governance Tools",
        url="https://aimultiple.com/open-source-data-governance",
        snippet="Top open source options for data governance.",
        provider="jina",
        source="jina",
        score=0.81,
        extra={"sources": ["jina"]},
    )

    merged = gateway._dedupe_hits([hit_a, hit_b])
    assert len(merged) == 1
    assert set(merged[0].extra.get("sources", [])) == {"jina", "tavily"}
