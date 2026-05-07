#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import threading
from pathlib import Path
from typing import Any, cast

import uvicorn

from datapulse.console_server import create_app
from scripts.datapulse_console_browser_smoke import (
    _SmokeReader,
    _close_context_lens,
    _find_free_port,
    _goto,
    _launch_browser,
    _open_context_lens,
    _wait_for_console_ready,
    _wait_for_port,
)

try:
    from playwright.sync_api import Page, sync_playwright
except ImportError as exc:  # pragma: no cover - exercised in runtime only
    raise SystemExit("Playwright is not installed. Run with: uv run --with playwright python scripts/datapulse_console_a11y_smoke.py") from exc


ROOT_DIR = Path(__file__).resolve().parents[1]
AXE_SCRIPT = ROOT_DIR / "node_modules" / "axe-core" / "axe.min.js"
IMPACT_ORDER = {"minor": 1, "moderate": 2, "serious": 3, "critical": 4}


def _log(message: str) -> None:
    print(message, flush=True)


def _bind_strict_logging(page: Page) -> list[str]:
    errors: list[str] = []

    page.on("pageerror", lambda error: errors.append(f"pageerror: {error}"))

    def handle_console(message) -> None:
        if message.type == "error":
            errors.append(f"console:error: {message.text}")

    page.on("console", handle_console)
    page.on("dialog", lambda dialog: dialog.accept())
    return errors


def _inject_axe(page: Page) -> None:
    if not AXE_SCRIPT.exists():
        raise RuntimeError("axe-core is not installed. Run: npm install")
    page.add_script_tag(path=str(AXE_SCRIPT))
    page.wait_for_function("() => typeof axe === 'object' && typeof axe.run === 'function'", timeout=10000)


def _scan(page: Page, label: str) -> list[dict[str, Any]]:
    _log(f"[console-a11y-smoke] scan {label}")
    _inject_axe(page)
    result = page.evaluate(
        """async () => {
            const result = await axe.run(document, {
                resultTypes: ["violations"],
                rules: {
                    "color-contrast": { enabled: true },
                },
            });
            return result.violations.map((violation) => ({
                id: violation.id,
                impact: violation.impact,
                description: violation.description,
                nodes: violation.nodes.slice(0, 5).map((node) => ({
                    target: node.target,
                    failureSummary: node.failureSummary,
                })),
            }));
        }"""
    )
    if not isinstance(result, list):
        raise AssertionError(f"axe returned an unexpected payload for {label}: {result!r}")
    minimum = os.environ.get("DATAPULSE_CONSOLE_A11Y_MIN_IMPACT", "serious").strip().lower() or "serious"
    minimum_rank = IMPACT_ORDER.get(minimum, IMPACT_ORDER["serious"])
    violations = []
    for item in result:
        if not isinstance(item, dict):
            continue
        impact = str(item.get("impact") or "").strip().lower()
        if IMPACT_ORDER.get(impact, 0) >= minimum_rank:
            violations.append(cast(dict[str, Any], item))
    return violations


def _open_palette(page: Page) -> None:
    page.evaluate("openCommandPalette()")
    page.wait_for_selector(".palette-backdrop.open", timeout=10000)
    page.fill("#command-palette-input", "triage")


def _exercise_a11y(page: Page, base_url: str) -> list[dict[str, Any]]:
    violations: list[dict[str, Any]] = []
    _goto(page, base_url)
    _wait_for_console_ready(page)
    violations.extend({"state": "initial", **item} for item in _scan(page, "initial"))

    page.evaluate("jumpToSection('section-triage')")
    page.wait_for_function("() => window.location.hash === '#section-triage'", timeout=10000)
    violations.extend({"state": "triage", **item} for item in _scan(page, "triage"))

    _open_context_lens(page, "#context-summary")
    violations.extend({"state": "context-lens", **item} for item in _scan(page, "context-lens"))
    _close_context_lens(page)

    _open_palette(page)
    violations.extend({"state": "command-palette", **item} for item in _scan(page, "command-palette"))
    page.keyboard.press("Escape")
    page.wait_for_function("() => !document.querySelector('.palette-backdrop')?.classList.contains('open')", timeout=10000)

    page.set_viewport_size({"width": 390, "height": 920})
    page.evaluate("jumpToSection('section-story')")
    page.wait_for_function("() => window.location.hash === '#section-story'", timeout=10000)
    violations.extend({"state": "mobile-story", **item} for item in _scan(page, "mobile-story"))
    return violations


def main() -> int:
    reader = _SmokeReader()
    app = create_app(reader_factory=cast(Any, lambda: reader))
    port = _find_free_port()
    server = uvicorn.Server(uvicorn.Config(app, host="127.0.0.1", port=port, log_level="error"))
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    _wait_for_port(port)
    base_url = f"http://127.0.0.1:{port}"

    page_errors: list[str] = []
    try:
        with sync_playwright() as playwright:
            browser = _launch_browser(playwright)
            context = browser.new_context(locale="en-US", viewport={"width": 1360, "height": 1100})
            page = context.new_page()
            page_errors = _bind_strict_logging(page)
            violations = _exercise_a11y(page, base_url)
            browser.close()
    finally:
        server.should_exit = True
        thread.join(timeout=5)

    if page_errors:
        raise AssertionError("browser errors during a11y smoke:\n" + "\n".join(page_errors))
    if violations:
        raise AssertionError("axe violations:\n" + json.dumps(violations, ensure_ascii=False, indent=2, sort_keys=True))

    _log("[console-a11y-smoke] pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
