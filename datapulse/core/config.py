"""Centralized environment configuration helpers for DataPulse runtime settings."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Iterable


def _normalize_bool(value: str) -> bool:
    normalized = value.strip().lower()
    if not normalized:
        return False
    return normalized not in {"0", "false", "no", "off", "n"}


def read_env_str(name: str, default: str = "") -> str:
    return (os.getenv(name, default) or default).strip()


def read_env_int(name: str, default: int, *, min_value: int | None = None, max_value: int | None = None) -> int:
    raw = read_env_str(name, str(default)).strip()
    try:
        value = int(raw)
    except (TypeError, ValueError):
        return default
    if min_value is not None and value < min_value:
        return min_value
    if max_value is not None and value > max_value:
        return max_value
    return value


def read_env_float(name: str, default: float, *, min_value: float | None = None, max_value: float | None = None) -> float:
    raw = read_env_str(name, str(default)).strip()
    try:
        value = float(raw)
    except (TypeError, ValueError):
        return default
    if min_value is not None and value < min_value:
        return min_value
    if max_value is not None and value > max_value:
        return max_value
    return value


def read_env_bool(name: str, default: bool = False) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return _normalize_bool(raw)


def read_env_list(name: str, *, default: Iterable[str] | None = None, separator: str = ",") -> list[str]:
    raw = os.getenv(name, "")
    base = list(default or ())
    if not raw:
        return list(base)
    out: list[str] = []
    for value in raw.split(separator):
        cleaned = value.strip().lower()
        if cleaned:
            out.append(cleaned)
    return out


@dataclass(frozen=True)
class SearchGatewayConfig:
    """Config model for web search gateway tuning."""

    timeout_seconds: float = 8.0
    retry_attempts: int = 2
    retry_base_delay: float = 1.0
    retry_max_delay: float = 4.0
    retry_backoff_factor: float = 2.0
    retry_respect_retry_after: bool = True
    breaker_failure_threshold: int = 5
    breaker_recovery_timeout: float = 60.0
    breaker_rate_limit_weight: int = 2
    provider_preference: tuple[str, ...] = ("tavily", "jina")
    qnaigc_enabled: bool = False
    qnaigc_locale_patterns: tuple[str, ...] = ("zh", "zh-hans", "zh-hant", "中文")
    qnaigc_max_results: int = 20
    qnaigc_site_filter_limit: int = 20
    qnaigc_cost_per_call: float = 0.036
    qnaigc_cost_currency: str = "CNY"
    qnaigc_fail_closed_without_token: bool = True

    @classmethod
    def load(cls) -> "SearchGatewayConfig":
        return cls(
            timeout_seconds=read_env_float("DATAPULSE_SEARCH_TIMEOUT", 8.0, min_value=1.0),
            retry_attempts=read_env_int("DATAPULSE_SEARCH_RETRY_ATTEMPTS", 2, min_value=1, max_value=10),
            retry_base_delay=read_env_float("DATAPULSE_SEARCH_RETRY_BASE_DELAY", 1.0, min_value=0.1, max_value=10.0),
            retry_max_delay=read_env_float("DATAPULSE_SEARCH_RETRY_MAX_DELAY_SECONDS", 4.0, min_value=0.1, max_value=30.0),
            retry_backoff_factor=read_env_float("DATAPULSE_SEARCH_RETRY_BACKOFF", 2.0, min_value=1.0, max_value=5.0),
            retry_respect_retry_after=read_env_bool("DATAPULSE_SEARCH_RETRY_RESPECT_RETRY_AFTER", True),
            breaker_failure_threshold=read_env_int(
                "DATAPULSE_SEARCH_CB_FAILURE_THRESHOLD",
                5,
                min_value=1,
                max_value=50,
            ),
            breaker_recovery_timeout=read_env_float("DATAPULSE_SEARCH_CB_RECOVERY_TIMEOUT", 60.0, min_value=1.0, max_value=600.0),
            breaker_rate_limit_weight=read_env_int("DATAPULSE_SEARCH_CB_RATE_LIMIT_WEIGHT", 2, min_value=1, max_value=20),
            provider_preference=tuple(read_env_list("DATAPULSE_SEARCH_PROVIDER_PRECEDENCE", default=("tavily", "jina"))),
            qnaigc_enabled=read_env_bool("DATAPULSE_SEARCH_QNAIGC_ENABLED", False),
            qnaigc_locale_patterns=tuple(
                read_env_list(
                    "DATAPULSE_SEARCH_QNAIGC_LOCALE_PATTERNS",
                    default=("zh", "zh-hans", "zh-hant", "中文"),
                )
            ),
            qnaigc_max_results=read_env_int("DATAPULSE_SEARCH_QNAIGC_MAX_RESULTS", 20, min_value=1, max_value=50),
            qnaigc_site_filter_limit=read_env_int("DATAPULSE_SEARCH_QNAIGC_SITE_FILTER_LIMIT", 20, min_value=1, max_value=200),
            qnaigc_cost_per_call=read_env_float("DATAPULSE_SEARCH_QNAIGC_COST_PER_CALL", 0.036, min_value=0.0),
            qnaigc_cost_currency=read_env_str("DATAPULSE_SEARCH_QNAIGC_COST_CURRENCY", "CNY"),
            qnaigc_fail_closed_without_token=read_env_bool("DATAPULSE_SEARCH_QNAIGC_FAIL_CLOSED_WITHOUT_TOKEN", True),
        )
