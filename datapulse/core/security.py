"""Security helpers for secret values and environment-backed credentials."""

from __future__ import annotations

import os


def get_secret(env_name: str, *, default: str = "", required: bool = False, required_for: str | None = None) -> str:
    """Read a secret-like environment value with optional required validation.

    The returned value is trimmed. If `required` is True and the value is empty
    or missing, a `ValueError` is raised.
    """

    raw = os.getenv(env_name, default)
    value = (raw or "").strip()
    if required and not value:
        raise ValueError(f"{required_for or env_name} is required")
    return value


def has_secret(env_name: str) -> bool:
    """Return whether a secret environment value is configured."""
    return bool(get_secret(env_name))


def mask_secret(secret: str, *, prefix: int = 4, suffix: int = 4, max_mid: int = 6) -> str:
    """Return a masked representation for logs and diagnostics."""
    if not secret:
        return "<empty>"

    clean = secret.strip()
    if len(clean) <= prefix + suffix:
        return "*" * len(clean)

    mid_len = len(clean) - (prefix + suffix)
    visible_mid = min(mid_len, max_mid)
    return f"{clean[:prefix]}{'*' * visible_mid}{clean[-suffix:]}"
