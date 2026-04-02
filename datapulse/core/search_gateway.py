"""Search provider gateway for DataPulse.

Provides single-provider, fallback, and multi-source search paths:
- `provider` = `jina`, `tavily`, `auto`, `multi`
- `mode` = `single` or `multi` (aggregation)
"""

from __future__ import annotations

import logging
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from datetime import datetime, timezone
from time import monotonic
from typing import Any
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

import requests

from datapulse.core.config import SearchGatewayConfig
from datapulse.core.jina_client import JinaAPIClient, JinaSearchOptions
from datapulse.core.retry import CircuitBreaker, CircuitBreakerOpen, RateLimitError, retry
from datapulse.core.security import get_secret
from datapulse.core.utils import get_domain

logger = logging.getLogger("datapulse.search_gateway")


DEFAULT_TIMEOUT = 8.0


@dataclass
class SearchHit:
    title: str
    url: str
    snippet: str
    provider: str
    source: str
    score: float = 0.0
    raw: dict[str, Any] = field(default_factory=dict)
    extra: dict[str, Any] = field(default_factory=dict)


class SearchProviderUnavailable(RuntimeError):
    """Raised when a provider cannot run (missing key/unsupported mode/etc.)."""


class SearchGateway:
    """Provider registry + execution engine for web search."""

    def __init__(self, timeout_seconds: float | None = None):
        gateway_config = SearchGatewayConfig.load()
        timeout = timeout_seconds if timeout_seconds is not None else gateway_config.timeout_seconds
        timeout = max(1.0, timeout)

        self._timeout_seconds = timeout
        self._jina_key = get_secret("JINA_API_KEY")
        self._tavily_key = get_secret("TAVILY_API_KEY")

        # Keep API key-based behavior aligned with existing Jina client contract.
        self._jina_client = JinaAPIClient(api_key=self._jina_key, timeout=int(timeout))

        self._seq = gateway_config.provider_preference or ("tavily", "jina")
        self._retry_attempts = gateway_config.retry_attempts
        self._retry_base_delay = gateway_config.retry_base_delay
        self._retry_max_delay = gateway_config.retry_max_delay
        self._retry_backoff_factor = gateway_config.retry_backoff_factor
        self._retry_respect_retry_after = gateway_config.retry_respect_retry_after
        self._breaker_failure_threshold = gateway_config.breaker_failure_threshold
        self._breaker_recovery_timeout = gateway_config.breaker_recovery_timeout
        self._breaker_rate_limit_weight = gateway_config.breaker_rate_limit_weight
        self._qnaigc_enabled = gateway_config.qnaigc_enabled
        self._qnaigc_locale_patterns = tuple(
            p.lower() for p in gateway_config.qnaigc_locale_patterns if p.strip()
        )
        self._qnaigc_max_results = max(1, int(gateway_config.qnaigc_max_results))
        self._qnaigc_site_filter_limit = max(1, int(gateway_config.qnaigc_site_filter_limit))
        self._qnaigc_cost_per_call = float(gateway_config.qnaigc_cost_per_call)
        self._qnaigc_cost_currency = (gateway_config.qnaigc_cost_currency or "CNY").strip() or "CNY"
        self._qnaigc_fail_closed_without_token = gateway_config.qnaigc_fail_closed_without_token
        self._qnaigc_tokens = self._load_qnaigc_tokens()
        self._provider_breakers: dict[str, CircuitBreaker] = {
            "tavily": self._new_circuit_breaker("tavily"),
            "jina": self._new_circuit_breaker("jina"),
            "qnaigc": self._new_circuit_breaker("qnaigc"),
        }

    def _new_circuit_breaker(self, name: str) -> CircuitBreaker:
        return CircuitBreaker(
            name=f"search_gateway_{name}",
            failure_threshold=self._breaker_failure_threshold,
            recovery_timeout=self._breaker_recovery_timeout,
            rate_limit_weight=self._breaker_rate_limit_weight,
        )

    def search(
        self,
        query: str,
        *,
        sites: list[str] | None = None,
        limit: int = 5,
        provider: str = "auto",
        mode: str = "single",
        deep: bool = False,
        news: bool = False,
        time_range: str | None = None,
        freshness: str | None = None,
        provider_hints: list[str] | None = None,
    ) -> tuple[list[SearchHit], dict[str, Any]]:
        """Execute search with fallback/multi-mode and return normalized hits + audit."""
        providers = self._resolve_providers(
            query=query,
            provider=provider,
            mode=mode,
            provider_hints=provider_hints,
        )
        requested_time_range = time_range or freshness
        search_meta: dict[str, Any] = {
            "query": query,
            "mode": mode,
            "requested_provider": provider,
            "provider_chain": providers[:],
            "provider_hints": list(provider_hints or []),
            "attempts": [],
            "timeout_seconds": self._timeout_seconds,
            "providers_selected": 0,
            "providers_with_hit": 0,
            "source_count": 0,
            "provider_count": 0,
            "cost_currency": self._qnaigc_cost_currency,
            "estimated_cost_total": 0.0,
        }

        sampled_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
        if mode == "multi":
            hits, attempts = self._search_multi(
                query,
                sites=sites,
                limit=limit,
                providers=providers,
                deep=deep,
                news=news,
                time_range=requested_time_range,
            )
        else:
            hits, attempts = self._search_single(
                query,
                sites=sites,
                limit=limit,
                providers=providers,
                deep=deep,
                news=news,
                time_range=requested_time_range,
            )

        search_meta["attempts"] = attempts
        search_meta["providers_with_hit"] = sum(
            1 for a in attempts if a.get("status") == "ok" and a.get("count", 0) > 0
        )
        search_meta["provider_count"] = len(attempts)
        search_meta["providers_selected"] = len(providers)
        search_meta["source_count"] = len({self._normalize_source(h.source) for h in hits})
        search_meta["sampled_at"] = sampled_at
        search_meta["estimated_cost_total"] = round(
            sum(float(a.get("estimated_cost", 0.0) or 0.0) for a in attempts),
            6,
        )

        # Sort and trim final output for predictable downstream behavior.
        merged = self._dedupe_hits(hits)
        merged = sorted(
            merged,
            key=lambda h: (-h.score, -len(h.extra.get("sources", [h.provider]))),
        )[:limit]

        for hit in merged:
            sources = set(hit.extra.get("sources", [hit.provider]))
            hit.extra["source_count"] = len(sources)
            hit.extra["source_diversity"] = self._source_diversity_score(len(sources))
            hit.extra["sources"] = sorted(sources)
            hit.extra["search_audit"] = {**search_meta}
            hit.extra["cross_validation"] = hit.extra.get("cross_validation", {})

        return merged, search_meta

    def _search_single(
        self,
        query: str,
        *,
        sites: list[str] | None,
        limit: int,
        providers: list[str],
        deep: bool = False,
        news: bool = False,
        time_range: str | None = None,
    ) -> tuple[list[SearchHit], list[dict[str, Any]]]:
        attempts: list[dict[str, Any]] = []

        for provider_name in providers:
            start = monotonic()
            try:
                hits, middleware_meta = self._run_provider_with_middleware(
                    provider_name,
                    query=query,
                    sites=sites,
                    limit=limit,
                    deep=deep,
                    news=news,
                    time_range=time_range,
                )
                attempts.append(
                    {
                        "provider": provider_name,
                        "status": "ok",
                        "count": len(hits),
                        "latency_ms": round((monotonic() - start) * 1000, 2),
                        "retry_count": middleware_meta.get("retry_count", 0),
                        "attempts": middleware_meta.get("attempts", 0),
                        "estimated_cost": middleware_meta.get("estimated_cost", 0.0),
                        "circuit_state_before": middleware_meta.get("circuit_state_before"),
                        "circuit_state_after": middleware_meta.get("circuit_state_after"),
                    }
                )
                # If one provider returns items, use immediately in single mode.
                if hits:
                    return hits, attempts
            except Exception as exc:  # pragma: no cover
                estimated_cost = self._provider_estimated_cost(provider_name)
                if provider_name == "qnaigc" and "token not configured" in str(exc).lower():
                    estimated_cost = 0.0
                attempts.append(
                    {
                        "provider": provider_name,
                        "status": "error",
                        "error": str(exc),
                        "latency_ms": round((monotonic() - start) * 1000, 2),
                        "attempts": 0,
                        "retry_count": 0,
                        "estimated_cost": estimated_cost,
                        "circuit_state_before": None,
                        "circuit_state_after": None,
                    }
                )
                logger.warning("Provider %s failed: %s", provider_name, exc)

                # Continue to next provider for fallback.
                continue

        return [], attempts

    def _search_multi(
        self,
        query: str,
        *,
        sites: list[str] | None,
        limit: int,
        providers: list[str],
        deep: bool = False,
        news: bool = False,
        time_range: str | None = None,
    ) -> tuple[list[SearchHit], list[dict[str, Any]]]:
        attempts: list[dict[str, Any]] = []
        all_hits: list[SearchHit] = []

        if not providers:
            return all_hits, attempts

        max_workers = min(len(providers), 2)
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_map = {
                executor.submit(
                    self._run_provider_with_middleware,
                    provider_name,
                    query=query,
                    sites=sites,
                    limit=limit,
                    deep=deep,
                    news=news,
                    time_range=time_range,
                ): provider_name
                for provider_name in providers
            }
            for fut in as_completed(future_map):
                provider_name = future_map[fut]
                start = monotonic()
                try:
                    hits, middleware_meta = fut.result()
                    all_hits.extend(hits)
                    attempts.append(
                        {
                            "provider": provider_name,
                            "status": "ok",
                            "count": len(hits),
                            "latency_ms": round((monotonic() - start) * 1000, 2),
                            "retry_count": middleware_meta.get("retry_count", 0),
                            "attempts": middleware_meta.get("attempts", 0),
                            "estimated_cost": middleware_meta.get("estimated_cost", 0.0),
                            "circuit_state_before": middleware_meta.get("circuit_state_before"),
                            "circuit_state_after": middleware_meta.get("circuit_state_after"),
                        }
                    )
                except Exception as exc:  # pragma: no cover
                    estimated_cost = self._provider_estimated_cost(provider_name)
                    if provider_name == "qnaigc" and "token not configured" in str(exc).lower():
                        estimated_cost = 0.0
                    attempts.append(
                        {
                            "provider": provider_name,
                            "status": "error",
                            "error": str(exc),
                            "latency_ms": round((monotonic() - start) * 1000, 2),
                            "attempts": 0,
                            "retry_count": 0,
                            "estimated_cost": estimated_cost,
                            "circuit_state_before": None,
                            "circuit_state_after": None,
                        }
                    )
                    logger.warning("Provider %s failed: %s", provider_name, exc)

        # Cross-provider consistency signals (title/snippet-level).
        if all_hits:
            self._annotate_cross_validation(all_hits)

        if all_hits:
            # Keep top-K input to avoid one-provider oversaturation before ranking later.
            all_hits = sorted(
                all_hits,
                key=lambda h: (-(h.score), -len(h.extra.get("sources", [h.provider]))),
            )[: max(1, min(limit * 3, 30))]
        return all_hits, attempts

    def _run_provider_with_middleware(
        self,
        provider_name: str,
        *,
        query: str,
        sites: list[str] | None,
        limit: int,
        deep: bool = False,
        news: bool = False,
        time_range: str | None = None,
    ) -> tuple[list[SearchHit], dict[str, Any]]:
        breaker = self._provider_breakers.get(provider_name)
        if breaker is None:
            breaker = self._new_circuit_breaker(provider_name)
            self._provider_breakers[provider_name] = breaker

        middleware_meta: dict[str, Any] = {"attempts": 0, "retry_count": 0}
        circuit_state_before = breaker.state

        def _attempt() -> list[SearchHit]:
            middleware_meta["attempts"] += 1
            return self._run_provider(
                provider_name,
                query=query,
                sites=sites,
                limit=limit,
                deep=deep,
                news=news,
                time_range=time_range,
            )

        wrapped = retry(
            max_attempts=self._retry_attempts,
            base_delay=self._retry_base_delay,
            max_delay=self._retry_max_delay,
            backoff_factor=self._retry_backoff_factor,
            retryable=(RateLimitError, requests.RequestException),
            respect_retry_after=self._retry_respect_retry_after,
        )(_attempt)

        try:
            hits = breaker.call(wrapped)
        except CircuitBreakerOpen as exc:
            raise SearchProviderUnavailable(
                f"Search circuit for '{provider_name}' is open"
            ) from exc

        middleware_meta["retry_count"] = max(0, middleware_meta["attempts"] - 1)
        middleware_meta["circuit_state_before"] = circuit_state_before
        middleware_meta["circuit_state_after"] = breaker.state
        middleware_meta["estimated_cost"] = self._provider_estimated_cost(provider_name)
        return hits, middleware_meta

    def _provider_estimated_cost(self, provider_name: str) -> float:
        return self._qnaigc_cost_per_call if provider_name == "qnaigc" else 0.0

    def _run_provider(
        self,
        provider_name: str,
        *,
        query: str,
        sites: list[str] | None,
        limit: int,
        deep: bool = False,
        news: bool = False,
        time_range: str | None = None,
    ) -> list[SearchHit]:
        if provider_name == "tavily":
            return self._search_tavily(
                query=query,
                sites=sites,
                limit=limit,
                deep=deep,
                news=news,
                time_range=time_range,
            )
        if provider_name == "jina":
            return self._search_jina(query=query, sites=sites, limit=limit)
        if provider_name == "qnaigc":
            return self._search_qnaigc(query=query, sites=sites, limit=limit)
        raise SearchProviderUnavailable(f"Unsupported search provider: {provider_name}")

    @staticmethod
    def _coalesce_key(item: dict[str, Any], keys: tuple[str, ...], default: Any = None) -> Any:
        for key in keys:
            value = item.get(key)
            if value is None or value == "":
                continue
            return value
        return default

    @staticmethod
    def _coerce_float(value: Any) -> float:
        try:
            return float(value)
        except Exception:
            return 0.0

    @staticmethod
    def _safe_str(value: Any) -> str:
        if value is None:
            return ""
        text = str(value)
        return text.strip()

    def _load_qnaigc_tokens(self) -> list[str]:
        tokens = [
            get_secret("QNAIGC_TOKEN_A"),
            get_secret("QNAIGC_TOKEN_B"),
        ]
        return [token.strip() for token in tokens if token.strip()]

    def _next_qnaigc_token(self) -> str | None:
        for token in self._qnaigc_tokens:
            if token:
                return token
        return None

    @staticmethod
    def _is_chinese_query(query: str) -> bool:
        return bool(re.search(r"[\u4e00-\u9fff]", query or ""))

    def _is_qnaigc_candidate_query(self, query: str) -> bool:
        if not query:
            return False
        if not self._qnaigc_enabled:
            return False
        if not self._qnaigc_tokens:
            return False
        if self._is_chinese_query(query):
            return True
        lowered = query.lower()
        for pattern in self._qnaigc_locale_patterns:
            if pattern and pattern in lowered:
                return True
        return False

    def _build_qnaigc_site_filter(self, sites: list[str] | None) -> list[str]:
        if not sites:
            return []
        normalized: list[str] = []
        for site in sites:
            text = (site or "").strip()
            if not text:
                continue
            if text not in normalized:
                normalized.append(text)
            if len(normalized) >= self._qnaigc_site_filter_limit:
                break
        return normalized

    def _extract_qnaigc_request_id(self, body: dict[str, Any]) -> str:
        if not isinstance(body, dict):
            return ""
        for key in ("request_id", "requestId", "rid", "trace_id"):
            value = self._safe_str(body.get(key))
            if value:
                return value

        payload = body.get("data")
        if isinstance(payload, dict):
            for key in ("request_id", "requestId", "rid", "trace_id"):
                value = self._safe_str(payload.get(key))
                if value:
                    return value
        return ""

    def _extract_qnaigc_results(self, body: dict[str, Any]) -> list[dict[str, Any]] | None:
        if not isinstance(body, dict):
            return None

        payload: Any = body.get("data", body)
        if isinstance(payload, dict):
            for key in ("results", "items", "list", "data"):
                value = payload.get(key)
                if isinstance(value, list):
                    return value
        for key in ("results", "items", "list", "data"):
            value = body.get(key)
            if isinstance(value, list):
                return value
        return None

    def _search_qnaigc(
        self,
        *,
        query: str,
        sites: list[str] | None,
        limit: int,
    ) -> list[SearchHit]:
        token = self._next_qnaigc_token()
        if not token:
            if self._qnaigc_fail_closed_without_token:
                raise SearchProviderUnavailable("QNAIGC token not configured")
            return []

        payload: dict[str, Any] = {
            "query": query,
            "max_results": min(max(1, int(limit)), self._qnaigc_max_results),
        }
        site_filter = self._build_qnaigc_site_filter(sites)
        if site_filter:
            payload["site_filter"] = site_filter

        resp = requests.post(
            "https://api.qnaigc.com/v1/search/web",
            json=payload,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            timeout=self._timeout_seconds,
        )

        if resp.status_code == 429:
            retry_after = self._parse_retry_after(resp.headers.get("Retry-After"))
            raise RateLimitError("QNAIGC rate limit", retry_after=retry_after)
        if resp.status_code == 401:
            raise SearchProviderUnavailable("QNAIGC API key invalid")
        if resp.status_code >= 400:
            raise RuntimeError(f"QNAIGC request failed: HTTP {resp.status_code}")

        body = self._safe_json(resp)
        if not isinstance(body, dict):
            raise RuntimeError("QNAIGC response malformed: non-object payload")

        request_id = self._extract_qnaigc_request_id(body)
        results = self._extract_qnaigc_results(body)
        if results is None:
            raise RuntimeError("QNAIGC response malformed: missing results list")

        out: list[SearchHit] = []
        max_results = min(max(1, int(limit)), self._qnaigc_max_results)
        for item in results[:max_results]:
            if not isinstance(item, dict):
                continue
            url = self._safe_str(item.get("url"))
            if not url:
                continue
            title = self._safe_str(item.get("title")) or self._safe_str(item.get("name")) or url
            snippet = self._safe_str(
                self._coalesce_key(
                    item,
                    ("snippet", "description", "summary", "abstract", "content", "text"),
                    "",
                )
            )
            score = self._coerce_float(
                self._coalesce_key(item, ("score", "relevance", "rank_score", "similarity"), 0.0)
            )
            hit = SearchHit(
                title=title[:300],
                url=self._sanitize_url(url),
                snippet=snippet,
                provider="qnaigc",
                source="qnaigc",
                score=score,
                raw=item,
                extra={
                    "sources": ["qnaigc"],
                    "authority_score": self._coalesce_key(item, ("authority_score", "authorityScore"), None),
                    "date": self._coalesce_key(
                        item,
                        ("date", "published_date", "publish_date", "publishTime", "published"),
                        None,
                    ),
                    "request_id": request_id or self._safe_str(
                        self._coalesce_key(item, ("request_id", "requestId"), "")
                    ),
                },
            )
            out.append(hit)
        return out

    def _search_tavily(
        self,
        *,
        query: str,
        sites: list[str] | None,
        limit: int,
        deep: bool = False,
        news: bool = False,
        time_range: str | None = None,
    ) -> list[SearchHit]:
        if not self._tavily_key:
            raise SearchProviderUnavailable("Tavily API key not configured")

        payload: dict[str, Any] = {
            "query": self._with_sites(query, sites),
            "max_results": max(1, int(limit)),
            "search_depth": "advanced" if deep else "basic",
            "include_answer": False,
            "include_raw_content": False,
        }
        if news:
            payload["topic"] = "news"
        if time_range:
            payload["time_range"] = time_range

        headers = {
            "Authorization": f"Bearer {self._tavily_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        resp = requests.post(
            "https://api.tavily.com/search",
            json=payload,
            headers=headers,
            timeout=self._timeout_seconds,
        )

        if resp.status_code == 429:
            retry_after = self._parse_retry_after(resp.headers.get("Retry-After"))
            raise RateLimitError("Tavily rate limit", retry_after=retry_after)
        if resp.status_code == 401:
            raise SearchProviderUnavailable("Tavily API key invalid")
        if resp.status_code >= 400:
            raise RuntimeError(f"Tavily request failed: HTTP {resp.status_code}")

        body = self._safe_json(resp)
        results = body.get("results", [])

        out: list[SearchHit] = []
        for item in results[:limit]:
            url = item.get("url", "").strip()
            if not url:
                continue
            title = str(item.get("title", "") or "").strip() or url
            snippet = str(
                item.get("content", "")
                or item.get("description", "")
                or item.get("snippet", "")
            ).strip()
            hit = SearchHit(
                title=title[:300],
                url=self._sanitize_url(url),
                snippet=snippet,
                provider="tavily",
                source=self._normalize_source(item.get("source", "")) or "tavily",
                score=float(item.get("score", 0.0) or 0.0),
                raw=item,
                extra={
                    "response_time": body.get("response_time"),
                    "score": item.get("score"),
                    "position": item.get("position"),
                    "sources": ["tavily"],
                },
            )
            out.append(hit)
        return out

    def _search_jina(
        self,
        *,
        query: str,
        sites: list[str] | None,
        limit: int,
    ) -> list[SearchHit]:
        if not self._jina_key:
            raise SearchProviderUnavailable("Jina API key not configured")

        opts = JinaSearchOptions(sites=sites or [], limit=max(1, int(limit)))
        results = self._jina_client.search(query, options=opts)
        out: list[SearchHit] = []
        for r in results:
            url = (r.url or "").strip()
            if not url:
                continue
            snippet = str(r.description or r.content or "").strip()
            hit = SearchHit(
                title=str(r.title or "").strip()[:300] or "Untitled",
                url=self._sanitize_url(url),
                snippet=snippet,
                provider="jina",
                source="jina",
                score=0.45,
                raw={
                    "title": r.title,
                    "description": r.description,
                    "content": r.content,
                },
                extra={"sources": ["jina"]},
            )
            out.append(hit)
        return out

    @staticmethod
    def _source_diversity_score(count: int) -> float:
        if count <= 1:
            return 0.0
        return 1.0

    @staticmethod
    def _normalize_summary(value: str | None) -> str:
        source = (value or "").lower()
        source = re.sub(r"[^a-z0-9\\s]", " ", source)
        tokens = [token for token in source.split() if len(token) > 1]
        if not tokens:
            return ""
        return " ".join(tokens[:18])

    @staticmethod
    def _token_set(text: str) -> set[str]:
        if not text:
            return set()
        words = [w for w in re.sub(r"[^a-z0-9\\s]", " ", text.lower()).split() if len(w) > 1]
        return {w for w in words}

    @staticmethod
    def _summary_similarity(a: str, b: str) -> float:
        left = SearchGateway._token_set(a)
        right = SearchGateway._token_set(b)
        if not left or not right:
            return 1.0 if a == b else 0.0
        intersection = len(left.intersection(right))
        union = len(left.union(right))
        if union == 0:
            return 0.0
        return intersection / union

    def _annotate_cross_validation(self, hits: list[SearchHit]) -> None:
        clusters: dict[str, list[SearchHit]] = {}
        for hit in hits:
            key = self._normalize_summary(f"{hit.title} {hit.snippet}")
            if not key:
                key = self._normalize_summary(hit.url) or self._sanitize_url(hit.url)
            clusters.setdefault(key, []).append(hit)

        for hit_list in clusters.values():
            providers = sorted({h.provider for h in hit_list})
            provider_count = len(providers)
            summary_consistency = 1.0
            if len(hit_list) > 1:
                pairs = 0
                match: float = 0.0
                for i in range(len(hit_list)):
                    for j in range(i + 1, len(hit_list)):
                        pairs += 1
                        match += self._summary_similarity(
                            f"{hit_list[i].snippet}",
                            f"{hit_list[j].snippet}",
                        )
                if pairs > 0:
                    summary_consistency = match / pairs
            for hit in hit_list:
                hit.extra["cross_validation"] = {
                    "providers": providers,
                    "provider_count": provider_count,
                    "summary_cluster_size": len(hit_list),
                    "summary_consistency": round(summary_consistency, 4),
                    "is_cross_validated": provider_count >= 2 and summary_consistency >= 0.35,
                }

    def _resolve_providers(
        self,
        query: str,
        provider: str,
        mode: str,
        provider_hints: list[str] | None = None,
    ) -> list[str]:
        preferred = ",".join(self._seq)
        if preferred:
            parts = [x.strip() for x in preferred.split(",") if x.strip()]
            base = [p for p in parts if p in {"tavily", "jina"}]
        else:
            base = list(self._seq)

        if provider == "jina":
            base = ["jina"]
        elif provider == "tavily":
            base = ["tavily", "jina"]
        elif provider == "multi":
            base = ["tavily", "jina"]
        elif provider == "qnaigc":
            base = ["qnaigc"]
        elif provider in {"auto", ""}:
            # If provider is auto, add QNAIGC as a narrow candidate before default chain.
            base = ["tavily", "jina"]
            if self._is_qnaigc_candidate_query(query):
                base = ["qnaigc", *base]
        else:
            base = ["jina", "tavily"]

        if provider in {"auto", "", "multi"}:
            hinted: list[str] = []
            for raw_hint in provider_hints or []:
                hint = str(raw_hint or "").strip().lower()
                if hint not in {"qnaigc", "tavily", "jina"}:
                    continue
                if hint == "qnaigc" and (not self._qnaigc_enabled or not self._qnaigc_tokens):
                    continue
                if hint not in hinted:
                    hinted.append(hint)
            if hinted:
                base = [*hinted, *base]

        # Deduplicate while preserving order.
        seen: list[str] = []
        for item in base:
            if item not in seen:
                seen.append(item)

        if mode == "single":
            if seen == ["jina"]:
                return seen
            # tavily/auto/multi modes keep fallback chain for reliability
            return seen
        return seen

    def _dedupe_hits(self, hits: list[SearchHit]) -> list[SearchHit]:
        merged: dict[str, SearchHit] = {}

        for hit in hits:
            if not hit.url:
                continue
            key = self._normalize_url(hit.url)
            if not key:
                continue

            if key not in merged:
                hit.extra["sources"] = list(dict.fromkeys([hit.provider]))
                merged[key] = hit
                continue

            existing = merged[key]
            existing_sources = existing.extra.setdefault("sources", [existing.provider])
            if hit.provider not in existing_sources:
                existing_sources.append(hit.provider)
                existing_sources.sort()

            if not existing.snippet and hit.snippet:
                existing.snippet = hit.snippet
            if len(hit.title) > len(existing.title):
                existing.title = hit.title
            if not existing.raw:
                existing.raw = hit.raw

            # Keep highest confidence-like score across providers as signal proxy.
            if hit.score > existing.score:
                existing.score = hit.score

        return list(merged.values())

    @staticmethod
    def _sanitize_url(url: str) -> str:
        return re.sub(r"\s+", "", url)

    @staticmethod
    def _with_sites(query: str, sites: list[str] | None) -> str:
        if not sites:
            return query
        suffix = " ".join(f"site:{s.strip()}" for s in sites if s.strip())
        if not suffix:
            return query
        return f"{query} {suffix}"

    @staticmethod
    def _normalize_source(source: str) -> str:
        value = source.strip().lower().replace(" ", "_")
        return re.sub(r"[^a-z0-9_\\-]", "", value) or "search"

    @staticmethod
    def _normalize_url(url: str) -> str:
        parsed = urlparse(url.strip())
        scheme = parsed.scheme.lower() or "https"
        host = (parsed.hostname or "").lower()
        if not host:
            return ""
        root_domain = get_domain(url)
        collapse_prefix = ("www.", "m.", "mobile.", "research.")
        canonical_host = root_domain if host.startswith(collapse_prefix) else host
        netloc = canonical_host
        if parsed.port:
            netloc = f"{netloc}:{parsed.port}"
        path = parsed.path.rstrip("/") or "/"
        params = parsed.params
        fragment = ""

        # Keep non-privacy query params; strip UTM-like noise.
        raw_pairs = parse_qsl(parsed.query, keep_blank_values=True)
        pairs = []
        for key, value in raw_pairs:
            key_l = key.lower()
            if key_l.startswith("utm_") or key_l in {"ref", "ref_src", "fbclid"}:
                continue
            pairs.append((key, value))
        query = urlencode(sorted(pairs), doseq=True)
        return urlunparse((scheme, netloc, path, params, query, fragment))

    @staticmethod
    def _safe_json(response: requests.Response) -> dict[str, Any]:
        try:
            return response.json()
        except Exception:
            return {}

    @staticmethod
    def _parse_retry_after(header_value: str | None) -> float:
        if not header_value:
            return 0.0
        value = header_value.strip()
        if not value:
            return 0.0
        try:
            return float(value)
        except Exception:
            return 0.0
