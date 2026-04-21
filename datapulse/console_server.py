"""Local browser console for the DataPulse intelligence center."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from html import escape
from pathlib import Path
from typing import Any, Callable
from urllib.parse import urlencode

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ConfigDict, Field

from datapulse.console_deck import build_mission_deck_suggestions
from datapulse.console_markup import render_console_html
from datapulse.reader import DataPulseReader
from datapulse.surface_capabilities import build_runtime_surface_introspection, build_surface_capability_projection

CONSOLE_TITLE = "DataPulse Command Chamber"
STATIC_DIR = Path(__file__).resolve().parent / "static"
CONSOLE_SOURCE_DIR = STATIC_DIR / "console"
BRAND_SOURCE_PATH = Path(__file__).resolve().parent.parent / "docs" / "形象.jpg"
TRIAGE_FRAGMENT_AUDIT_ROOT = Path(__file__).resolve().parent.parent / "artifacts" / "runtime" / "triage_fragments"
TRIAGE_FRAGMENT_CRITICAL_QUERY_KEYS = (
    "triage_filter",
    "search",
    "selected_item_id",
    "selected_item_ids",
    "pinned_evidence_ids",
    "story_focus_id",
)
TRIAGE_FILTER_VALUES = {"all", "open", "new", "triaged", "verified", "duplicate", "ignored", "escalated"}
TRIAGE_OPEN_STATES = {"new", "triaged", "escalated"}


def _load_console_bundle() -> str:
    """Concat console source fragments in sorted filename order.

    Filenames like `00-common.js`, `99-main.js` guarantee deterministic order;
    all fragments share one global script scope once sent to the browser.
    """
    if not CONSOLE_SOURCE_DIR.is_dir():
        return ""
    parts = sorted(CONSOLE_SOURCE_DIR.glob("*.js"))
    return "\n".join(part.read_text(encoding="utf-8") for part in parts)


_CONSOLE_BUNDLE_CACHE: str | None = None


def _console_bundle_text() -> str:
    global _CONSOLE_BUNDLE_CACHE
    if _CONSOLE_BUNDLE_CACHE is None:
        _CONSOLE_BUNDLE_CACHE = _load_console_bundle()
    return _CONSOLE_BUNDLE_CACHE


def _unique_text(values: list[str]) -> list[str]:
    seen: set[str] = set()
    rows: list[str] = []
    for value in values:
        normalized = str(value or "").strip()
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        rows.append(normalized)
    return rows


def _normalize_triage_filter(value: str | None) -> str:
    normalized = str(value or "open").strip().lower() or "open"
    return normalized if normalized in TRIAGE_FILTER_VALUES else "open"


def _triage_fragment_state(request: Request) -> tuple[dict[str, Any], bool]:
    params = request.query_params
    state = {
        "triage_filter": _normalize_triage_filter(params.get("triage_filter")),
        "search": str(params.get("search") or "").strip(),
        "selected_item_id": str(params.get("selected_item_id") or "").strip(),
        "selected_item_ids": _unique_text(params.getlist("selected_item_ids")),
        "pinned_evidence_ids": _unique_text(params.getlist("pinned_evidence_ids")),
        "story_focus_id": str(params.get("story_focus_id") or "").strip(),
    }
    return state, all(key in params for key in TRIAGE_FRAGMENT_CRITICAL_QUERY_KEYS)


def _triage_fragment_query_string(state: dict[str, Any], **overrides: Any) -> str:
    payload = {
        "triage_filter": state.get("triage_filter", "open"),
        "search": state.get("search", ""),
        "selected_item_id": state.get("selected_item_id", ""),
        "selected_item_ids": list(state.get("selected_item_ids") or []),
        "pinned_evidence_ids": list(state.get("pinned_evidence_ids") or []),
        "story_focus_id": state.get("story_focus_id", ""),
    }
    payload.update(overrides)
    pairs: list[tuple[str, str]] = []
    for key, value in payload.items():
        if isinstance(value, list):
            rows = _unique_text([str(item or "").strip() for item in value])
            if not rows:
                pairs.append((key, ""))
                continue
            pairs.extend((key, row) for row in rows)
            continue
        pairs.append((key, str(value or "").strip()))
    return urlencode(pairs, doseq=True)


def _json_script_blob(payload: dict[str, Any]) -> str:
    return json.dumps(payload, ensure_ascii=False).replace("</", "<\\/")


def _triage_fragment_state_blob(state: dict[str, Any]) -> str:
    return (
        '<script type="application/json" data-triage-fragment-view-state>'
        f"{_json_script_blob(state)}</script>"
    )


def _filter_triage_items(items: list[dict[str, Any]], state: dict[str, Any]) -> list[dict[str, Any]]:
    active_filter = _normalize_triage_filter(str(state.get("triage_filter") or "open"))
    search_query = str(state.get("search") or "").strip().lower()
    pinned_ids = set(_unique_text([str(item or "").strip() for item in state.get("pinned_evidence_ids") or []]))
    filtered: list[dict[str, Any]] = []
    for item in items:
        item_id = str(item.get("id") or "").strip()
        if pinned_ids and item_id not in pinned_ids:
            continue
        review_state = str(item.get("review_state") or "new").strip().lower() or "new"
        if active_filter == "all":
            pass
        elif active_filter == "open":
            if review_state not in TRIAGE_OPEN_STATES:
                continue
        elif review_state != active_filter:
            continue
        if search_query:
            raw_notes = item.get("review_notes")
            notes: list[dict[str, Any]] = [
                note for note in raw_notes if isinstance(note, dict)
            ] if isinstance(raw_notes, list) else []
            note_text = " ".join(str(note.get("note") or "") for note in notes)
            haystack = " ".join(
                [
                    item_id,
                    str(item.get("title") or ""),
                    str(item.get("url") or ""),
                    note_text,
                ]
            ).lower()
            if search_query not in haystack:
                continue
        filtered.append(item)
    return filtered


def _render_triage_fragment_card(item: dict[str, Any], state: dict[str, Any]) -> str:
    item_id = str(item.get("id") or "").strip()
    review_state = str(item.get("review_state") or "new").strip() or "new"
    title = escape(str(item.get("title") or item_id or "Triage item"))
    url = escape(str(item.get("url") or ""))
    note_count = len(item.get("review_notes") or []) if isinstance(item.get("review_notes"), list) else 0
    selected = item_id == str(state.get("selected_item_id") or "").strip()
    batch_selected = item_id in set(state.get("selected_item_ids") or [])
    pinned = item_id in set(state.get("pinned_evidence_ids") or [])
    story_focus_id = str(state.get("story_focus_id") or "").strip()
    card_query = _triage_fragment_query_string(state, selected_item_id=item_id)
    score = escape(str(item.get("score") or 0))
    confidence = f"{float(item.get('confidence') or 0):.2f}"
    selected_label = "selected" if selected else "available"
    return f"""
<article class="card selectable {'selected' if selected else ''}" data-triage-fragment="card" data-triage-card="{escape(item_id)}" data-fragment-driver="htmx" data-replay-claim="__REPLAY_CLAIM__">
  <div class="card-top">
    <div>
      <div class="mono">triage card fragment</div>
      <h3 class="card-title">{title}</h3>
      <div class="meta">
        <span>{escape(item_id)}</span>
        <span>state={escape(review_state)}</span>
        <span>score={score}</span>
        <span>confidence={escape(confidence)}</span>
      </div>
    </div>
    <span class="chip {'ok' if selected else ''}">{selected_label}</span>
  </div>
  <div class="panel-sub">{url or '-'}</div>
  <div class="meta">
    <span>notes={note_count}</span>
    <span>batch={'on' if batch_selected else 'off'}</span>
    <span>pinned={'on' if pinned else 'off'}</span>
    <span>story_focus={escape(story_focus_id or '-')}</span>
  </div>
  <div class="actions" style="margin-top:12px;">
    <button class="btn-secondary" type="button" hx-get="/api/fragments/triage/card/{escape(item_id)}?{escape(card_query)}" hx-target="[data-triage-card=&quot;{escape(item_id)}&quot;]" hx-swap="outerHTML">Refresh Card</button>
  </div>
</article>
""".strip()


def _render_triage_fragment_banner(
    items: list[dict[str, Any]],
    filtered_items: list[dict[str, Any]],
    state: dict[str, Any],
) -> str:
    hidden_count = max(0, len(items) - len(filtered_items))
    reasons: list[str] = []
    if state.get("pinned_evidence_ids"):
        reasons.append("evidence focus")
    if state.get("search"):
        reasons.append(f'search "{escape(str(state["search"]))}"')
    triage_filter = str(state.get("triage_filter") or "open")
    if triage_filter not in {"open", "all"}:
        reasons.append(f"state={escape(triage_filter)}")
    controls: list[str] = []
    if state.get("pinned_evidence_ids"):
        query = _triage_fragment_query_string(state, pinned_evidence_ids=[])
        controls.append(
            f'<button class="btn-secondary" type="button" hx-get="/api/fragments/triage/banner?{escape(query)}" hx-target="#triage-fragment-banner" hx-swap="outerHTML">Show Full Queue</button>'
        )
    if state.get("search"):
        query = _triage_fragment_query_string(state, search="")
        controls.append(
            f'<button class="btn-secondary" type="button" hx-get="/api/fragments/triage/banner?{escape(query)}" hx-target="#triage-fragment-banner" hx-swap="outerHTML">Clear Search</button>'
        )
    if triage_filter not in {"open", "all"}:
        query = _triage_fragment_query_string(state, triage_filter="open")
        controls.append(
            f'<button class="btn-secondary" type="button" hx-get="/api/fragments/triage/banner?{escape(query)}" hx-target="#triage-fragment-banner" hx-swap="outerHTML">Reset To Open</button>'
        )
    return f"""
<section id="triage-fragment-banner" class="card" data-triage-fragment="banner" data-fragment-driver="htmx" data-replay-claim="__REPLAY_CLAIM__">
  <div class="mono">triage banner fragment</div>
  <div class="meta" style="margin-top:10px;">
    <span>shown={len(filtered_items)} / {len(items)}</span>
    <span>hidden={hidden_count}</span>
    <span>filter={escape(triage_filter)}</span>
    <span>selected={len(state.get('selected_item_ids') or [])}</span>
  </div>
  <div class="panel-sub" style="margin-top:10px;">{escape(" | ".join(reasons) if reasons else "All queue items shown.")}</div>
  {'<div class="actions" style="margin-top:12px;">' + ''.join(controls) + '</div>' if controls else ''}
</section>
""".strip()


def _render_triage_fragment_list(filtered_items: list[dict[str, Any]], state: dict[str, Any]) -> str:
    cards = "\n".join(_render_triage_fragment_card(item, state) for item in filtered_items)
    if not cards:
        cards = '<div class="empty">No triage item matched the active queue filter.</div>'
    return f"""
<section id="triage-fragment-list" class="stack" data-triage-fragment="list" data-fragment-driver="htmx" data-replay-claim="__REPLAY_CLAIM__">
  <div class="mono">triage queue fragment</div>
  <div class="panel-sub" style="margin-top:10px;">Server-rendered pilot for queue cards, bounded replay state, and htmx-compatible swaps.</div>
  <div class="meta" style="margin-top:10px;">
    <span>filter={escape(str(state.get('triage_filter') or 'open'))}</span>
    <span>search={escape(str(state.get('search') or '-') or '-')}</span>
    <span>selected={escape(str(state.get('selected_item_id') or '-') or '-')}</span>
    <span>story_focus={escape(str(state.get('story_focus_id') or '-') or '-')}</span>
  </div>
  <div class="stack" style="margin-top:12px;">{cards}</div>
</section>
""".strip()


def _write_triage_fragment_audit(
    *,
    surface: str,
    request: Request,
    state: dict[str, Any],
    rendered_item_ids: list[str],
    exact_replay_requested: bool,
) -> tuple[str, Path | None, str | None]:
    claim = "exact" if exact_replay_requested else "structural"
    record = {
        "logged_at_utc": datetime.now(timezone.utc).isoformat(),
        "surface": surface,
        "route_path": request.url.path,
        "query_string": request.url.query,
        "rendered_item_ids": rendered_item_ids,
        "replay_claim": claim,
        "view_state": state,
    }
    try:
        TRIAGE_FRAGMENT_AUDIT_ROOT.mkdir(parents=True, exist_ok=True)
        output_path = TRIAGE_FRAGMENT_AUDIT_ROOT / f"{datetime.now(timezone.utc):%Y%m%d}.jsonl"
        with output_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")
        return claim, output_path, None
    except OSError as exc:
        return "structural", None, str(exc)


def _triage_fragment_response(
    *,
    surface: str,
    request: Request,
    state: dict[str, Any],
    rendered_item_ids: list[str],
    exact_replay_requested: bool,
    html: str,
) -> HTMLResponse:
    replay_claim, audit_path, audit_error = _write_triage_fragment_audit(
        surface=surface,
        request=request,
        state=state,
        rendered_item_ids=rendered_item_ids,
        exact_replay_requested=exact_replay_requested,
    )
    body = html.replace("__REPLAY_CLAIM__", replay_claim) + _triage_fragment_state_blob(state)
    headers = {
        "Cache-Control": "no-store",
        "X-DataPulse-Triage-Replay-Claim": replay_claim,
    }
    if audit_path is not None:
        headers["X-DataPulse-Triage-Audit-Path"] = str(audit_path)
    if audit_error:
        headers["X-DataPulse-Triage-Audit-Error"] = audit_error
    return HTMLResponse(content=body, headers=headers)


BRAND_HERO_PATH = Path(__file__).resolve().parent.parent / "docs" / "assets" / "datapulse-command-chamber-hero.jpg"
BRAND_SQUARE_PATH = Path(__file__).resolve().parent.parent / "docs" / "assets" / "datapulse-command-chamber-square.jpg"
BRAND_ICON_PATH = Path(__file__).resolve().parent.parent / "docs" / "assets" / "datapulse-command-chamber-icon.png"


class WatchCreateRequest(BaseModel):
    name: str
    query: str
    platforms: list[str] | None = None
    sites: list[str] | None = None
    provider: str = "auto"
    schedule: str = "manual"
    min_confidence: float = 0.0
    top_n: int = 5
    alert_rules: list[dict[str, Any]] | None = None


class WatchUpdateRequest(BaseModel):
    name: str | None = None
    query: str | None = None
    platforms: list[str] | None = None
    sites: list[str] | None = None
    provider: str | None = None
    schedule: str | None = None
    min_confidence: float | None = None
    top_n: int | None = None
    alert_rules: list[dict[str, Any]] | None = None
    enabled: bool | None = None


class WatchAlertRuleRequest(BaseModel):
    alert_rules: list[dict[str, Any]] | None = None


class WatchDeckSuggestionRequest(BaseModel):
    name: str = ""
    query: str = ""
    schedule: str = ""
    platform: str = ""
    domain: str = ""
    provider: str = ""
    route: str = ""
    keyword: str = ""
    min_score: str = ""
    min_confidence: str = ""


class RunDueRequest(BaseModel):
    limit: int = Field(default=0, ge=0)


class TriageStateRequest(BaseModel):
    state: str
    note: str = ""
    actor: str = "console"
    duplicate_of: str | None = None


class TriageNoteRequest(BaseModel):
    note: str
    author: str = "console"


class StoryUpdateRequest(BaseModel):
    title: str | None = None
    summary: str | None = None
    status: str | None = None


class StoryCreateRequest(BaseModel):
    title: str
    summary: str = ""
    status: str = "active"
    model_config = ConfigDict(extra="allow")


class StoryFromTriageRequest(BaseModel):
    item_ids: list[str]
    title: str | None = None
    summary: str = ""
    status: str = "monitoring"


class AlertRouteCreateRequest(BaseModel):
    name: str
    channel: str
    description: str | None = None
    webhook_url: str | None = None
    authorization: str | None = None
    headers: dict[str, str] | None = None
    feishu_webhook: str | None = None
    telegram_bot_token: str | None = None
    telegram_chat_id: str | None = None
    timeout_seconds: float | None = Field(default=None, gt=0)


class AlertRouteUpdateRequest(BaseModel):
    channel: str | None = None
    description: str | None = None
    webhook_url: str | None = None
    authorization: str | None = None
    headers: dict[str, str] | None = None
    feishu_webhook: str | None = None
    telegram_bot_token: str | None = None
    telegram_chat_id: str | None = None
    timeout_seconds: float | None = Field(default=None, gt=0)


class ReportObjectPayload(BaseModel):
    model_config = ConfigDict(extra="allow")


class ReportComposeRequest(BaseModel):
    profile_id: str | None = None
    include_sections: bool | None = None
    include_claim_cards: bool | None = None
    include_citation_bundles: bool | None = None
    include_export_profiles: bool | None = None


class ReportExportRequest(ReportComposeRequest):
    output_format: str = "json"
    include_metadata: bool | None = None


class ReportWatchPackRequest(BaseModel):
    profile_id: str | None = None
    name: str | None = None
    query: str | None = None
    platforms: list[str] | None = None
    sites: list[str] | None = None
    schedule: str = "manual"
    min_confidence: float = 0.0
    top_n: int = 5
    alert_rules: list[dict[str, Any]] | None = None


class DeliverySubscriptionCreateRequest(BaseModel):
    subject_kind: str
    subject_ref: str
    output_kind: str
    delivery_mode: str = "pull"
    status: str = "active"
    route_names: list[str] | None = None
    cursor_or_since: str | None = None


class DeliverySubscriptionUpdateRequest(BaseModel):
    subject_kind: str | None = None
    subject_ref: str | None = None
    output_kind: str | None = None
    delivery_mode: str | None = None
    status: str | None = None
    route_names: list[str] | None = None
    cursor_or_since: str | None = None


class DeliveryDispatchRequest(BaseModel):
    profile_id: str | None = None


class DigestDeliveryTargetRequest(BaseModel):
    kind: str = "route"
    ref: str = ""


class DigestProfileRequest(BaseModel):
    language: str | None = None
    timezone: str | None = None
    frequency: str | None = None
    default_delivery_target: DigestDeliveryTargetRequest | None = None


class DigestDispatchRequest(BaseModel):
    profile: str = "default"
    limit: int = Field(default=12, ge=1, le=500)
    min_confidence: float = Field(default=0.0, ge=0.0)
    since: str | None = None
    route_name: str | None = None


def create_app(reader_factory: Callable[[], DataPulseReader] = DataPulseReader) -> FastAPI:
    app = FastAPI(title=CONSOLE_TITLE, version="0.8.0")

    @app.get("/static/console.js", include_in_schema=False)
    def console_bundle() -> Response:
        body = _console_bundle_text()
        return Response(content=body, media_type="application/javascript; charset=utf-8")

    if STATIC_DIR.is_dir():
        app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

    @app.get("/", response_class=HTMLResponse)
    def index() -> str:
        return render_console_html(CONSOLE_TITLE)

    @app.get("/brand/source")
    def brand_source() -> FileResponse:
        if not BRAND_SOURCE_PATH.exists():
            raise HTTPException(status_code=404, detail="brand source not found")
        return FileResponse(BRAND_SOURCE_PATH, media_type="image/jpeg")

    @app.get("/brand/hero")
    def brand_hero() -> FileResponse:
        if not BRAND_HERO_PATH.exists():
            raise HTTPException(status_code=404, detail="brand hero not found")
        return FileResponse(BRAND_HERO_PATH, media_type="image/jpeg")

    @app.get("/brand/square")
    def brand_square() -> FileResponse:
        if not BRAND_SQUARE_PATH.exists():
            raise HTTPException(status_code=404, detail="brand square not found")
        return FileResponse(BRAND_SQUARE_PATH, media_type="image/jpeg")

    @app.get("/brand/icon")
    def brand_icon() -> FileResponse:
        if not BRAND_ICON_PATH.exists():
            raise HTTPException(status_code=404, detail="brand icon not found")
        return FileResponse(BRAND_ICON_PATH, media_type="image/png")

    @app.get("/favicon.ico", include_in_schema=False)
    def favicon() -> Response:
        if not BRAND_ICON_PATH.exists():
            return Response(status_code=204)
        return FileResponse(BRAND_ICON_PATH, media_type="image/png")

    @app.get("/healthz")
    def healthz() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/readyz")
    def readyz() -> dict[str, str]:
        return {"status": "ready"}

    @app.get("/api/overview")
    def overview() -> dict[str, Any]:
        reader = reader_factory()
        watches = reader.list_watches(include_disabled=True)
        alerts = reader.list_alerts(limit=20)
        routes = reader.list_alert_routes()
        status = reader.watch_status_snapshot()
        stories = reader.list_stories(limit=5000, min_items=0)
        scorecard = reader.governance_scorecard_snapshot()
        signals = scorecard.get("signals", {}) if isinstance(scorecard, dict) else {}
        triage_signal = signals.get("triage_throughput", {}) if isinstance(signals, dict) else {}
        story_signal = signals.get("story_conversion", {}) if isinstance(signals, dict) else {}
        alert_signal = signals.get("alert_yield", {}) if isinstance(signals, dict) else {}
        return {
            "enabled_watches": sum(1 for watch in watches if watch.get("enabled", True)),
            "disabled_watches": sum(1 for watch in watches if not watch.get("enabled", True)),
            "due_watches": sum(1 for watch in watches if watch.get("is_due")),
            "story_count": len(stories),
            "story_ready_count": int(story_signal.get("ready_story_count", 0) or 0),
            "story_converted_count": int(story_signal.get("converted_item_count", 0) or 0),
            "alert_count": len(alerts),
            "alerting_mission_count": int(alert_signal.get("alerting_missions", 0) or 0),
            "route_count": len(routes),
            "triage_open_count": reader.triage_stats().get("open_count", 0),
            "triage_acted_on_count": int(triage_signal.get("acted_on_items", 0) or 0),
            "daemon_state": status.get("state", "idle"),
            "daemon_heartbeat_at": status.get("heartbeat_at", ""),
        }

    @app.get("/api/watches")
    def list_watches(include_disabled: bool = False) -> list[dict[str, Any]]:
        return reader_factory().list_watches(include_disabled=include_disabled)

    @app.get("/api/watches/{identifier}")
    def show_watch(identifier: str) -> dict[str, Any]:
        payload = reader_factory().show_watch(identifier)
        if payload is None:
            raise HTTPException(status_code=404, detail=f"Watch mission not found: {identifier}")
        return payload

    @app.get("/api/watches/{identifier}/results")
    def watch_results(identifier: str, limit: int = 10, min_confidence: float = 0.0) -> list[dict[str, Any]]:
        payload = reader_factory().list_watch_results(identifier, limit=limit, min_confidence=min_confidence)
        if payload is None:
            raise HTTPException(status_code=404, detail=f"Watch mission not found: {identifier}")
        return payload

    @app.post("/api/watches")
    def create_watch(payload: WatchCreateRequest) -> dict[str, Any]:
        try:
            return reader_factory().create_watch(**payload.model_dump())
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        except OSError as exc:
            raise HTTPException(status_code=500, detail=f"Unable to persist watch mission: {exc}") from exc

    @app.put("/api/watches/{identifier}")
    def update_watch(identifier: str, payload: WatchUpdateRequest) -> dict[str, Any]:
        try:
            mission = reader_factory().update_watch(identifier, **payload.model_dump())
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        except OSError as exc:
            raise HTTPException(status_code=500, detail=f"Unable to persist watch mission: {exc}") from exc
        if mission is None:
            raise HTTPException(status_code=404, detail=f"Watch mission not found: {identifier}")
        return mission

    @app.post("/api/console/deck/suggestions")
    def mission_deck_suggestions(payload: WatchDeckSuggestionRequest) -> dict[str, Any]:
        return build_mission_deck_suggestions(reader_factory(), payload.model_dump())

    @app.put("/api/watches/{identifier}/alert-rules")
    def set_watch_alert_rules(identifier: str, payload: WatchAlertRuleRequest) -> dict[str, Any]:
        mission = reader_factory().set_watch_alert_rules(identifier, alert_rules=payload.alert_rules)
        if mission is None:
            raise HTTPException(status_code=404, detail=f"Watch mission not found: {identifier}")
        return mission

    @app.post("/api/watches/run-due")
    async def run_due_watches(payload: RunDueRequest) -> dict[str, Any]:
        return await reader_factory().run_due_watches(limit=payload.limit or None)

    @app.post("/api/watches/{identifier}/run")
    async def run_watch(identifier: str) -> dict[str, Any]:
        try:
            return await reader_factory().run_watch(identifier)
        except ValueError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    @app.post("/api/watches/{identifier}/disable")
    def disable_watch(identifier: str) -> dict[str, Any]:
        payload = reader_factory().disable_watch(identifier)
        if payload is None:
            raise HTTPException(status_code=404, detail=f"Watch mission not found: {identifier}")
        return payload

    @app.post("/api/watches/{identifier}/enable")
    def enable_watch(identifier: str) -> dict[str, Any]:
        payload = reader_factory().enable_watch(identifier)
        if payload is None:
            raise HTTPException(status_code=404, detail=f"Watch mission not found: {identifier}")
        return payload

    @app.delete("/api/watches/{identifier}")
    def delete_watch(identifier: str) -> dict[str, Any]:
        payload = reader_factory().delete_watch(identifier)
        if payload is None:
            raise HTTPException(status_code=404, detail=f"Watch mission not found: {identifier}")
        return payload

    @app.get("/api/alerts")
    def list_alerts(limit: int = 20, mission_id: str = "") -> list[dict[str, Any]]:
        return reader_factory().list_alerts(limit=limit, mission_id=mission_id or None)

    @app.get("/api/alert-routes")
    def list_alert_routes() -> list[dict[str, Any]]:
        return reader_factory().list_alert_routes()

    @app.post("/api/alert-routes")
    def create_alert_route(payload: AlertRouteCreateRequest) -> dict[str, Any]:
        try:
            return reader_factory().create_alert_route(**payload.model_dump(exclude_none=True))
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.put("/api/alert-routes/{identifier}")
    def update_alert_route(identifier: str, payload: AlertRouteUpdateRequest) -> dict[str, Any]:
        try:
            route = reader_factory().update_alert_route(identifier, **payload.model_dump(exclude_none=True))
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        if route is None:
            raise HTTPException(status_code=404, detail=f"Alert route not found: {identifier}")
        return route

    @app.delete("/api/alert-routes/{identifier}")
    def delete_alert_route(identifier: str) -> dict[str, Any]:
        route = reader_factory().delete_alert_route(identifier)
        if route is None:
            raise HTTPException(status_code=404, detail=f"Alert route not found: {identifier}")
        return route

    @app.get("/api/alert-routes/health")
    def alert_route_health(limit: int = 100) -> list[dict[str, Any]]:
        return reader_factory().alert_route_health(limit=limit)

    @app.get("/api/watch-status")
    def watch_status() -> dict[str, Any]:
        return reader_factory().watch_status_snapshot()

    @app.get("/api/ops")
    def ops_snapshot() -> dict[str, Any]:
        return reader_factory().ops_snapshot()

    @app.get("/api/ops/scorecard")
    def ops_scorecard() -> dict[str, Any]:
        return reader_factory().governance_scorecard_snapshot()

    @app.get("/api/runtime/introspection")
    def runtime_introspection() -> dict[str, Any]:
        return build_runtime_surface_introspection()

    @app.get("/api/capabilities")
    def surface_capabilities(include_unavailable: bool = False) -> dict[str, Any]:
        return build_surface_capability_projection("console", include_unavailable=include_unavailable)

    @app.get("/api/capabilities/{surface}")
    def surface_capabilities_for_surface(surface: str, include_unavailable: bool = False) -> dict[str, Any]:
        try:
            return build_surface_capability_projection(surface, include_unavailable=include_unavailable)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.get("/api/ai/surfaces/{surface}/precheck")
    def ai_surface_precheck(surface: str, mode: str = "assist") -> dict[str, Any]:
        try:
            return reader_factory().ai_surface_precheck(surface, mode=mode)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.get("/api/alerts/{identifier}/ai/delivery-summary")
    def ai_delivery_summary(identifier: str, mode: str = "assist") -> dict[str, Any]:
        try:
            payload = reader_factory().ai_delivery_summary(identifier, mode=mode)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        if payload is None:
            raise HTTPException(status_code=404, detail=f"Alert event not found: {identifier}")
        return payload

    @app.get("/api/reports/{identifier}/ai/report-draft")
    def ai_report_draft(identifier: str, mode: str = "assist", profile_id: str | None = None) -> dict[str, Any]:
        try:
            payload = reader_factory().ai_report_draft(identifier, mode=mode, profile_id=profile_id)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        if payload is None:
            raise HTTPException(status_code=404, detail=f"Report not found: {identifier}")
        return payload

    @app.get("/api/watches/{identifier}/ai/mission-suggest")
    def ai_mission_suggest(identifier: str, mode: str = "assist") -> dict[str, Any]:
        try:
            payload = reader_factory().ai_mission_suggest(identifier, mode=mode)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        if payload is None:
            raise HTTPException(status_code=404, detail=f"Watch mission not found: {identifier}")
        return payload

    @app.get("/api/stories")
    def list_stories(limit: int = 8, min_items: int = 0) -> list[dict[str, Any]]:
        return reader_factory().list_stories(limit=limit, min_items=min_items)

    @app.post("/api/stories")
    def create_story(payload: StoryCreateRequest) -> dict[str, Any]:
        try:
            return reader_factory().create_story(**payload.model_dump(exclude_none=True))
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.post("/api/stories/from-triage")
    def create_story_from_triage(payload: StoryFromTriageRequest) -> dict[str, Any]:
        try:
            return reader_factory().create_story_from_triage(**payload.model_dump(exclude_none=True))
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.get("/api/stories/{identifier}")
    def show_story(identifier: str) -> dict[str, Any]:
        story = reader_factory().show_story(identifier)
        if story is None:
            raise HTTPException(status_code=404, detail=f"Story not found: {identifier}")
        return story

    @app.put("/api/stories/{identifier}")
    def update_story(identifier: str, payload: StoryUpdateRequest) -> dict[str, Any]:
        try:
            story = reader_factory().update_story(identifier, **payload.model_dump())
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        if story is None:
            raise HTTPException(status_code=404, detail=f"Story not found: {identifier}")
        return story

    @app.delete("/api/stories/{identifier}")
    def delete_story(identifier: str) -> dict[str, Any]:
        story = reader_factory().delete_story(identifier)
        if story is None:
            raise HTTPException(status_code=404, detail=f"Story not found: {identifier}")
        return story

    @app.get("/api/stories/{identifier}/graph")
    def story_graph(identifier: str, entity_limit: int = 12, relation_limit: int = 24) -> dict[str, Any]:
        graph = reader_factory().story_graph(
            identifier,
            entity_limit=entity_limit,
            relation_limit=relation_limit,
        )
        if graph is None:
            raise HTTPException(status_code=404, detail=f"Story not found: {identifier}")
        return graph

    @app.get("/api/stories/{identifier}/ai/claim-draft")
    def ai_claim_draft(identifier: str, mode: str = "assist", brief_id: str = "") -> dict[str, Any]:
        try:
            payload = reader_factory().ai_claim_draft(identifier, mode=mode, brief_id=brief_id)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        if payload is None:
            raise HTTPException(status_code=404, detail=f"Story not found: {identifier}")
        return payload

    @app.get("/api/stories/{identifier}/export")
    def export_story(identifier: str, format: str = "markdown") -> Response:
        output_format = str(format or "markdown").strip().lower() or "markdown"
        if output_format not in {"markdown", "md", "json"}:
            raise HTTPException(status_code=400, detail=f"Unsupported story export format: {format}")
        payload = reader_factory().export_story(identifier, output_format=output_format)
        if payload is None:
            raise HTTPException(status_code=404, detail=f"Story not found: {identifier}")
        media_type = "application/json" if output_format == "json" else "text/markdown"
        return Response(content=payload, media_type=media_type)

    @app.get("/api/report-briefs")
    def list_report_briefs(limit: int = 20, status: str | None = None) -> list[dict[str, Any]]:
        return reader_factory().list_report_briefs(limit=limit, status=status)

    @app.post("/api/report-briefs")
    def create_report_brief(payload: ReportObjectPayload) -> dict[str, Any]:
        try:
            return reader_factory().create_report_brief(**payload.model_dump(exclude_none=True))
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.get("/api/report-briefs/{identifier}")
    def show_report_brief(identifier: str) -> dict[str, Any]:
        brief = reader_factory().show_report_brief(identifier)
        if brief is None:
            raise HTTPException(status_code=404, detail=f"Report brief not found: {identifier}")
        return brief

    @app.put("/api/report-briefs/{identifier}")
    def update_report_brief(identifier: str, payload: ReportObjectPayload) -> dict[str, Any]:
        try:
            payload_data = payload.model_dump(exclude_none=True)
            brief = reader_factory().update_report_brief(identifier, **payload_data)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        if brief is None:
            raise HTTPException(status_code=404, detail=f"Report brief not found: {identifier}")
        return brief

    @app.get("/api/claim-cards")
    def list_claim_cards(limit: int = 20, status: str | None = None) -> list[dict[str, Any]]:
        return reader_factory().list_claim_cards(limit=limit, status=status)

    @app.post("/api/claim-cards")
    def create_claim_card(payload: ReportObjectPayload) -> dict[str, Any]:
        try:
            return reader_factory().create_claim_card(**payload.model_dump(exclude_none=True))
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.get("/api/claim-cards/{identifier}")
    def show_claim_card(identifier: str) -> dict[str, Any]:
        claim = reader_factory().show_claim_card(identifier)
        if claim is None:
            raise HTTPException(status_code=404, detail=f"Claim card not found: {identifier}")
        return claim

    @app.put("/api/claim-cards/{identifier}")
    def update_claim_card(identifier: str, payload: ReportObjectPayload) -> dict[str, Any]:
        try:
            payload_data = payload.model_dump(exclude_none=True)
            claim = reader_factory().update_claim_card(identifier, **payload_data)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        if claim is None:
            raise HTTPException(status_code=404, detail=f"Claim card not found: {identifier}")
        return claim

    @app.get("/api/report-sections")
    def list_report_sections(limit: int = 20, status: str | None = None) -> list[dict[str, Any]]:
        return reader_factory().list_report_sections(limit=limit, status=status)

    @app.post("/api/report-sections")
    def create_report_section(payload: ReportObjectPayload) -> dict[str, Any]:
        try:
            return reader_factory().create_report_section(**payload.model_dump(exclude_none=True))
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.get("/api/report-sections/{identifier}")
    def show_report_section(identifier: str) -> dict[str, Any]:
        section = reader_factory().show_report_section(identifier)
        if section is None:
            raise HTTPException(status_code=404, detail=f"Report section not found: {identifier}")
        return section

    @app.put("/api/report-sections/{identifier}")
    def update_report_section(identifier: str, payload: ReportObjectPayload) -> dict[str, Any]:
        try:
            payload_data = payload.model_dump(exclude_none=True)
            section = reader_factory().update_report_section(identifier, **payload_data)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        if section is None:
            raise HTTPException(status_code=404, detail=f"Report section not found: {identifier}")
        return section

    @app.get("/api/citation-bundles")
    def list_citation_bundles(limit: int = 20) -> list[dict[str, Any]]:
        return reader_factory().list_citation_bundles(limit=limit)

    @app.post("/api/citation-bundles")
    def create_citation_bundle(payload: ReportObjectPayload) -> dict[str, Any]:
        try:
            return reader_factory().create_citation_bundle(**payload.model_dump(exclude_none=True))
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.get("/api/citation-bundles/{identifier}")
    def show_citation_bundle(identifier: str) -> dict[str, Any]:
        bundle = reader_factory().show_citation_bundle(identifier)
        if bundle is None:
            raise HTTPException(status_code=404, detail=f"Citation bundle not found: {identifier}")
        return bundle

    @app.put("/api/citation-bundles/{identifier}")
    def update_citation_bundle(identifier: str, payload: ReportObjectPayload) -> dict[str, Any]:
        try:
            payload_data = payload.model_dump(exclude_none=True)
            bundle = reader_factory().update_citation_bundle(identifier, **payload_data)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        if bundle is None:
            raise HTTPException(status_code=404, detail=f"Citation bundle not found: {identifier}")
        return bundle

    @app.get("/api/reports")
    def list_reports(limit: int = 20, status: str | None = None) -> list[dict[str, Any]]:
        return reader_factory().list_reports(limit=limit, status=status)

    @app.post("/api/reports")
    def create_report(payload: ReportObjectPayload) -> dict[str, Any]:
        try:
            return reader_factory().create_report(**payload.model_dump(exclude_none=True))
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.get("/api/reports/{identifier}")
    def show_report(identifier: str) -> dict[str, Any]:
        report = reader_factory().show_report(identifier)
        if report is None:
            raise HTTPException(status_code=404, detail=f"Report not found: {identifier}")
        return report

    @app.put("/api/reports/{identifier}")
    def update_report(identifier: str, payload: ReportObjectPayload) -> dict[str, Any]:
        try:
            payload_data = payload.model_dump(exclude_none=True)
            report = reader_factory().update_report(identifier, **payload_data)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        if report is None:
            raise HTTPException(status_code=404, detail=f"Report not found: {identifier}")
        return report

    @app.post("/api/reports/{identifier}/compose")
    def compose_report(identifier: str, payload: ReportComposeRequest) -> dict[str, Any]:
        try:
            report = reader_factory().compose_report(
                identifier,
                **payload.model_dump(exclude_none=True),
            )
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        if report is None:
            raise HTTPException(status_code=404, detail=f"Report not found: {identifier}")
        return report

    @app.get("/api/reports/{identifier}/compose")
    def compose_report_view(
        identifier: str,
        profile_id: str | None = None,
        include_sections: bool | None = None,
        include_claim_cards: bool | None = None,
        include_citation_bundles: bool | None = None,
    ) -> dict[str, Any]:
        quality_payload = reader_factory().compose_report(
            identifier,
            profile_id=profile_id,
            include_sections=include_sections,
            include_claim_cards=include_claim_cards,
            include_citation_bundles=include_citation_bundles,
        )
        if quality_payload is None:
            raise HTTPException(status_code=404, detail=f"Report not found: {identifier}")
        return quality_payload

    @app.get("/api/reports/{identifier}/quality")
    def report_quality(
        identifier: str,
        profile_id: str | None = None,
        include_sections: bool | None = None,
        include_claim_cards: bool | None = None,
        include_citation_bundles: bool | None = None,
        include_export_profiles: bool | None = None,
    ) -> dict[str, Any]:
        quality = reader_factory().assess_report_quality(
            identifier,
            profile_id=profile_id,
            include_sections=include_sections,
            include_claim_cards=include_claim_cards,
            include_citation_bundles=include_citation_bundles,
            include_export_profiles=include_export_profiles,
        )
        if quality is None:
            raise HTTPException(status_code=404, detail=f"Report not found: {identifier}")
        return quality

    @app.get("/api/reports/{identifier}/export")
    def export_report(
        identifier: str,
        profile_id: str | None = None,
        output_format: str = "json",
        include_sections: bool | None = None,
        include_claim_cards: bool | None = None,
        include_citation_bundles: bool | None = None,
        include_metadata: bool | None = None,
    ) -> Response:
        output_format = str(output_format).strip().lower() or "json"
        if output_format not in {"json", "md", "markdown"}:
            raise HTTPException(status_code=400, detail=f"Unsupported report export format: {output_format}")
        try:
            payload = reader_factory().export_report(
                identifier,
                profile_id=profile_id,
                output_format=output_format,
                include_sections=include_sections,
                include_claim_cards=include_claim_cards,
                include_citation_bundles=include_citation_bundles,
                include_metadata=include_metadata,
            )
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        if payload is None:
            raise HTTPException(status_code=404, detail=f"Report not found: {identifier}")
        media_type = "application/json" if output_format == "json" else "text/markdown"
        return Response(content=payload, media_type=media_type)

    @app.get("/api/reports/{identifier}/watch-pack")
    def report_watch_pack(identifier: str, profile_id: str | None = None) -> dict[str, Any]:
        payload = reader_factory().report_watch_pack(identifier, profile_id=profile_id)
        if payload is None:
            raise HTTPException(status_code=404, detail=f"Report not found: {identifier}")
        return payload

    @app.post("/api/reports/{identifier}/watch-from-pack")
    def create_watch_from_report_pack(
        identifier: str,
        payload: ReportWatchPackRequest,
    ) -> dict[str, Any]:
        try:
            mission = reader_factory().create_watch_from_report_pack(
                identifier,
                profile_id=payload.profile_id,
                name=payload.name,
                query=payload.query,
                platforms=payload.platforms,
                sites=payload.sites,
                schedule=payload.schedule,
                min_confidence=payload.min_confidence,
                top_n=payload.top_n,
                alert_rules=payload.alert_rules,
            )
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        if mission is None:
            raise HTTPException(status_code=404, detail=f"Report not found: {identifier}")
        return mission

    @app.get("/api/digest-profile")
    def show_digest_profile() -> dict[str, Any]:
        return reader_factory().get_digest_profile()

    @app.put("/api/digest-profile")
    def update_digest_profile(payload: DigestProfileRequest) -> dict[str, Any]:
        target_payload = payload.default_delivery_target
        try:
            return reader_factory().update_digest_profile(
                language=payload.language,
                timezone=payload.timezone,
                frequency=payload.frequency,
                default_delivery_target_kind=target_payload.kind if target_payload else None,
                default_delivery_target_ref=target_payload.ref if target_payload else None,
            )
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.get("/api/digest/console")
    def digest_console_projection(
        profile: str = "default",
        limit: int = 12,
        min_confidence: float = 0.0,
        since: str | None = None,
    ) -> dict[str, Any]:
        try:
            return reader_factory().digest_console_projection(
                profile=profile,
                limit=limit,
                min_confidence=min_confidence,
                since=since,
            )
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.post("/api/digest/dispatch")
    def dispatch_digest_delivery(payload: DigestDispatchRequest) -> list[dict[str, Any]]:
        try:
            prepared_payload = reader_factory().prepare_digest_payload(
                profile=payload.profile,
                limit=payload.limit,
                min_confidence=payload.min_confidence,
                since=payload.since,
            )
            return reader_factory().dispatch_digest_delivery(
                prepared_payload=prepared_payload,
                route_name=payload.route_name,
            )
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.get("/api/export-profiles")
    def list_export_profiles(limit: int = 20, status: str | None = None) -> list[dict[str, Any]]:
        return reader_factory().list_export_profiles(limit=limit, status=status)

    @app.post("/api/export-profiles")
    def create_export_profile(payload: ReportObjectPayload) -> dict[str, Any]:
        try:
            return reader_factory().create_export_profile(**payload.model_dump(exclude_none=True))
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.get("/api/export-profiles/{identifier}")
    def show_export_profile(identifier: str) -> dict[str, Any]:
        profile = reader_factory().show_export_profile(identifier)
        if profile is None:
            raise HTTPException(status_code=404, detail=f"Export profile not found: {identifier}")
        return profile

    @app.put("/api/export-profiles/{identifier}")
    def update_export_profile(identifier: str, payload: ReportObjectPayload) -> dict[str, Any]:
        try:
            payload_data = payload.model_dump(exclude_none=True)
            profile = reader_factory().update_export_profile(identifier, **payload_data)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        if profile is None:
            raise HTTPException(status_code=404, detail=f"Export profile not found: {identifier}")
        return profile

    @app.get("/api/delivery-subscriptions")
    def list_delivery_subscriptions(
        limit: int = 20,
        status: str | None = None,
        subject_kind: str | None = None,
        subject_ref: str | None = None,
        output_kind: str | None = None,
        delivery_mode: str | None = None,
        route_name: str | None = None,
    ) -> list[dict[str, Any]]:
        return reader_factory().list_delivery_subscriptions(
            limit=limit,
            status=status,
            subject_kind=subject_kind,
            subject_ref=subject_ref,
            output_kind=output_kind,
            delivery_mode=delivery_mode,
            route_name=route_name,
        )

    @app.post("/api/delivery-subscriptions")
    def create_delivery_subscription(payload: DeliverySubscriptionCreateRequest) -> dict[str, Any]:
        try:
            return reader_factory().create_delivery_subscription(**payload.model_dump(exclude_none=True))
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.get("/api/delivery-subscriptions/{identifier}")
    def show_delivery_subscription(identifier: str) -> dict[str, Any]:
        subscription = reader_factory().show_delivery_subscription(identifier)
        if subscription is None:
            raise HTTPException(status_code=404, detail=f"Delivery subscription not found: {identifier}")
        return subscription

    @app.put("/api/delivery-subscriptions/{identifier}")
    def update_delivery_subscription(
        identifier: str,
        payload: DeliverySubscriptionUpdateRequest,
    ) -> dict[str, Any]:
        try:
            subscription = reader_factory().update_delivery_subscription(
                identifier,
                **payload.model_dump(exclude_none=True),
            )
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        if subscription is None:
            raise HTTPException(status_code=404, detail=f"Delivery subscription not found: {identifier}")
        return subscription

    @app.delete("/api/delivery-subscriptions/{identifier}")
    def delete_delivery_subscription(identifier: str) -> dict[str, Any]:
        subscription = reader_factory().delete_delivery_subscription(identifier)
        if subscription is None:
            raise HTTPException(status_code=404, detail=f"Delivery subscription not found: {identifier}")
        return subscription

    @app.get("/api/delivery-subscriptions/{identifier}/package")
    def build_delivery_package(identifier: str, profile_id: str | None = None) -> dict[str, Any]:
        try:
            return reader_factory().build_report_delivery_package(identifier, profile_id=profile_id)
        except ValueError as exc:
            detail = str(exc)
            if "not found" in detail.lower():
                raise HTTPException(status_code=404, detail=detail) from exc
            raise HTTPException(status_code=400, detail=detail) from exc

    @app.post("/api/delivery-subscriptions/{identifier}/dispatch")
    def dispatch_delivery_subscription(identifier: str, payload: DeliveryDispatchRequest) -> list[dict[str, Any]]:
        try:
            return reader_factory().dispatch_report_delivery(identifier, profile_id=payload.profile_id)
        except ValueError as exc:
            detail = str(exc)
            if "not found" in detail.lower():
                raise HTTPException(status_code=404, detail=detail) from exc
            raise HTTPException(status_code=400, detail=detail) from exc

    @app.get("/api/delivery-dispatch-records")
    def list_delivery_dispatch_records(
        limit: int = 20,
        status: str | None = None,
        subscription_id: str | None = None,
        subject_kind: str | None = None,
        subject_ref: str | None = None,
        output_kind: str | None = None,
        route_name: str | None = None,
    ) -> list[dict[str, Any]]:
        return reader_factory().list_delivery_dispatch_records(
            limit=limit,
            status=status,
            subscription_id=subscription_id,
            subject_kind=subject_kind,
            subject_ref=subject_ref,
            output_kind=output_kind,
            route_name=route_name,
        )

    @app.get("/api/triage")
    def triage_list(limit: int = 20, state: list[str] | None = None, include_closed: bool = False) -> list[dict[str, Any]]:
        return reader_factory().triage_list(limit=limit, states=state, include_closed=include_closed)

    @app.get("/api/fragments/triage/banner", response_class=HTMLResponse)
    def triage_fragment_banner(request: Request) -> HTMLResponse:
        state, exact_replay_requested = _triage_fragment_state(request)
        items = reader_factory().triage_list(limit=5000, include_closed=True)
        filtered_items = _filter_triage_items(items, state)
        html = _render_triage_fragment_banner(items, filtered_items, state)
        return _triage_fragment_response(
            surface="banner",
            request=request,
            state=state,
            rendered_item_ids=[str(item.get("id") or "").strip() for item in filtered_items],
            exact_replay_requested=exact_replay_requested,
            html=html,
        )

    @app.get("/api/fragments/triage/list", response_class=HTMLResponse)
    def triage_fragment_list(request: Request) -> HTMLResponse:
        state, exact_replay_requested = _triage_fragment_state(request)
        items = reader_factory().triage_list(limit=5000, include_closed=True)
        filtered_items = _filter_triage_items(items, state)
        html = _render_triage_fragment_list(filtered_items, state)
        return _triage_fragment_response(
            surface="list",
            request=request,
            state=state,
            rendered_item_ids=[str(item.get("id") or "").strip() for item in filtered_items],
            exact_replay_requested=exact_replay_requested,
            html=html,
        )

    @app.get("/api/fragments/triage/card/{item_id}", response_class=HTMLResponse)
    def triage_fragment_card(item_id: str, request: Request) -> HTMLResponse:
        state, exact_replay_requested = _triage_fragment_state(request)
        state["selected_item_id"] = item_id
        items = reader_factory().triage_list(limit=5000, include_closed=True)
        item = next((row for row in items if str(row.get("id") or "").strip() == item_id), None)
        if item is None:
            raise HTTPException(status_code=404, detail=f"Triage item not found: {item_id}")
        html = _render_triage_fragment_card(item, state)
        return _triage_fragment_response(
            surface="card",
            request=request,
            state=state,
            rendered_item_ids=[item_id],
            exact_replay_requested=exact_replay_requested,
            html=html,
        )

    @app.get("/api/triage/stats")
    def triage_stats() -> dict[str, Any]:
        return reader_factory().triage_stats()

    @app.get("/api/triage/{item_id}/explain")
    def triage_explain(item_id: str, limit: int = 5) -> dict[str, Any]:
        payload = reader_factory().triage_explain(item_id, limit=limit)
        if payload is None:
            raise HTTPException(status_code=404, detail=f"Triage item not found: {item_id}")
        return payload

    @app.get("/api/triage/{item_id}/ai/assist")
    def ai_triage_assist(item_id: str, mode: str = "assist", limit: int = 5) -> dict[str, Any]:
        try:
            payload = reader_factory().ai_triage_assist(item_id, mode=mode, limit=limit)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        if payload is None:
            raise HTTPException(status_code=404, detail=f"Triage item not found: {item_id}")
        return payload

    @app.post("/api/triage/{item_id}/state")
    def triage_update(item_id: str, payload: TriageStateRequest) -> dict[str, Any]:
        try:
            item = reader_factory().triage_update(item_id, **payload.model_dump())
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        if item is None:
            raise HTTPException(status_code=404, detail=f"Triage item not found: {item_id}")
        return item

    @app.post("/api/triage/{item_id}/note")
    def triage_note(item_id: str, payload: TriageNoteRequest) -> dict[str, Any]:
        item = reader_factory().triage_note(item_id, **payload.model_dump())
        if item is None:
            raise HTTPException(status_code=404, detail=f"Triage item not found: {item_id}")
        return item

    @app.delete("/api/triage/{item_id}")
    def triage_delete(item_id: str) -> dict[str, Any]:
        item = reader_factory().triage_delete(item_id)
        if item is None:
            raise HTTPException(status_code=404, detail=f"Triage item not found: {item_id}")
        return item

    return app


def main() -> None:
    parser = argparse.ArgumentParser(description="Launch the DataPulse browser console.")
    parser.add_argument("--host", default="127.0.0.1", help="Bind host (default 127.0.0.1)")
    parser.add_argument("--port", type=int, default=8765, help="Bind port (default 8765)")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload for local development")
    args = parser.parse_args()

    import uvicorn

    uvicorn.run("datapulse.console_server:create_app", host=args.host, port=args.port, reload=args.reload, factory=True)


if __name__ == "__main__":
    main()
