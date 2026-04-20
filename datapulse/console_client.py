"""Loader for the console client JS bundle.

The JS body lives in `datapulse/static/console/*.js` as real JS files split by
feature domain (00-common.js → 99-main.js etc.), so IDE tooling, linters, and
browser DevTools source maps all work. Source files are concatenated in sorted
filename order to form one classic `<script>` bundle that shares a single
global scope — identical semantics to the previous monolithic file.

This module exposes the concatenated body to callers that still expect the
legacy render helper (inline script rendering and tests).
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

_CONSOLE_SOURCE_DIR = Path(__file__).resolve().parent / "static" / "console"


@lru_cache(maxsize=1)
def _load_console_js() -> str:
    if not _CONSOLE_SOURCE_DIR.is_dir():
        return ""
    parts = sorted(_CONSOLE_SOURCE_DIR.glob("*.js"))
    return "\n".join(part.read_text(encoding="utf-8") for part in parts)


def render_console_client_script(initial_state: str | None = None) -> str:
    """Return the concatenated console client JS bundle.

    When callers still pass `initial_state`, the helper prepends a
    `window.__DP_INITIAL__ = ...;` line so inline-script renderers keep
    working. New code should prefer the static mount at `/static/console.js`
    plus a tiny bootstrap `<script>` that sets `window.__DP_INITIAL__`.
    """
    body = _load_console_js()
    if initial_state is None:
        return body
    return f"window.__DP_INITIAL__ = {initial_state};\n{body}"
