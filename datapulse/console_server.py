"""Local browser console for the DataPulse intelligence center."""

from __future__ import annotations

import argparse
import json
from typing import Any, Callable

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, Response
from pydantic import BaseModel, Field

from datapulse.reader import DataPulseReader

CONSOLE_TITLE = "DataPulse Intelligence Console"


def _json_blob(payload: Any) -> str:
    return json.dumps(payload, ensure_ascii=False)


def _console_html() -> str:
    initial_state = _json_blob(
        {
            "title": CONSOLE_TITLE,
            "sections": ["overview", "missions", "alerts", "routes", "status", "triage", "stories"],
        }
    )
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{CONSOLE_TITLE}</title>
  <style>
    :root {{
      --paper: #f4efe2;
      --mist: #e4dbc8;
      --panel: rgba(255, 249, 237, 0.82);
      --panel-strong: rgba(255, 247, 230, 0.94);
      --ink: #14231c;
      --muted: #56655e;
      --accent: #b04b2d;
      --accent-2: #0d7b61;
      --line: rgba(20, 35, 28, 0.14);
      --warn: #8f2318;
      --shadow: 0 24px 70px rgba(41, 33, 16, 0.12);
      --headline: "Avenir Next Condensed", "Arial Narrow", "Helvetica Neue", sans-serif;
      --body: "Iowan Old Style", "Palatino Linotype", "Book Antiqua", Georgia, serif;
      --mono: "SF Mono", "IBM Plex Mono", "Menlo", monospace;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      min-height: 100vh;
      color: var(--ink);
      background:
        radial-gradient(circle at 20% 20%, rgba(176, 75, 45, 0.16), transparent 28%),
        radial-gradient(circle at 80% 10%, rgba(13, 123, 97, 0.18), transparent 32%),
        linear-gradient(180deg, #efe5d2 0%, var(--paper) 100%);
      font-family: var(--body);
    }}
    body::before {{
      content: "";
      position: fixed;
      inset: 0;
      pointer-events: none;
      background-image:
        linear-gradient(rgba(20, 35, 28, 0.04) 1px, transparent 1px),
        linear-gradient(90deg, rgba(20, 35, 28, 0.04) 1px, transparent 1px);
      background-size: 28px 28px;
      mask-image: linear-gradient(180deg, rgba(0,0,0,0.55), transparent 92%);
    }}
    .shell {{
      max-width: 1440px;
      margin: 0 auto;
      padding: 24px;
      display: grid;
      gap: 18px;
    }}
    .hero {{
      display: grid;
      grid-template-columns: 1.4fr 0.8fr;
      gap: 18px;
      align-items: stretch;
      animation: rise .55s ease-out both;
    }}
    .hero-main, .hero-side, .panel {{
      border: 1px solid var(--line);
      border-radius: 26px;
      background: var(--panel);
      backdrop-filter: blur(10px);
      box-shadow: var(--shadow);
    }}
    .hero-main {{
      overflow: hidden;
      position: relative;
      padding: 28px;
    }}
    .hero-main::after {{
      content: "";
      position: absolute;
      inset: auto -8% -35% 30%;
      height: 240px;
      background: radial-gradient(circle, rgba(176, 75, 45, 0.22), transparent 62%);
    }}
    .hero-side {{
      padding: 24px;
      display: grid;
      gap: 12px;
      align-content: start;
    }}
    .eyebrow {{
      display: inline-flex;
      gap: 8px;
      align-items: center;
      font: 700 12px/1 var(--mono);
      text-transform: uppercase;
      letter-spacing: 0.16em;
      color: var(--accent-2);
    }}
    .dot {{
      width: 10px;
      height: 10px;
      border-radius: 999px;
      background: linear-gradient(180deg, var(--accent), #d57e4f);
      box-shadow: 0 0 0 5px rgba(176, 75, 45, 0.1);
    }}
    h1 {{
      margin: 12px 0 8px;
      font-family: var(--headline);
      font-size: clamp(2.8rem, 6vw, 5.8rem);
      line-height: 0.95;
      letter-spacing: -0.04em;
      text-transform: uppercase;
      max-width: 9ch;
    }}
    .hero-copy {{
      max-width: 60ch;
      color: var(--muted);
      font-size: 1.05rem;
    }}
    .toolbar {{
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      margin-top: 18px;
    }}
    button {{
      border: 0;
      cursor: pointer;
      border-radius: 999px;
      padding: 12px 16px;
      font: 700 0.88rem/1 var(--mono);
      letter-spacing: 0.02em;
      transition: transform .18s ease, box-shadow .18s ease, background .18s ease;
    }}
    button:hover {{ transform: translateY(-1px); }}
    .btn-primary {{
      background: linear-gradient(135deg, var(--accent), #d6844f);
      color: #fff9ee;
      box-shadow: 0 10px 24px rgba(176, 75, 45, 0.26);
    }}
    .btn-secondary {{
      background: rgba(20, 35, 28, 0.08);
      color: var(--ink);
    }}
    .hero-metrics {{
      display: grid;
      gap: 10px;
    }}
    .signal-strip {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
      gap: 12px;
      margin-top: 22px;
    }}
    .metric {{
      padding: 16px;
      border-radius: 18px;
      border: 1px solid var(--line);
      background: rgba(255, 255, 255, 0.44);
    }}
    .metric-label {{
      font: 700 11px/1 var(--mono);
      text-transform: uppercase;
      letter-spacing: 0.1em;
      color: var(--muted);
    }}
    .metric-value {{
      margin-top: 8px;
      font-family: var(--headline);
      font-size: clamp(1.8rem, 3vw, 2.8rem);
      line-height: 1;
    }}
    .grid {{
      display: grid;
      grid-template-columns: 1.05fr 1.05fr 0.9fr;
      gap: 18px;
      animation: rise .7s ease-out both;
      animation-delay: .08s;
    }}
    .panel {{
      padding: 22px;
      display: grid;
      gap: 14px;
      align-content: start;
    }}
    .panel-head {{
      display: flex;
      align-items: start;
      justify-content: space-between;
      gap: 12px;
    }}
    .panel-title {{
      margin: 0;
      font-family: var(--headline);
      font-size: 1.55rem;
      letter-spacing: -0.02em;
      text-transform: uppercase;
    }}
    .panel-sub {{
      color: var(--muted);
      font-size: 0.95rem;
    }}
    .stack {{
      display: grid;
      gap: 12px;
    }}
    .card {{
      border: 1px solid var(--line);
      border-radius: 18px;
      padding: 14px 16px;
      background: rgba(255, 255, 255, 0.52);
    }}
    .card-top {{
      display: flex;
      align-items: start;
      justify-content: space-between;
      gap: 12px;
    }}
    .card-title {{
      margin: 0;
      font-size: 1.08rem;
      line-height: 1.2;
    }}
    .chip {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      border-radius: 999px;
      padding: 5px 9px;
      font: 700 11px/1 var(--mono);
      text-transform: uppercase;
      background: rgba(20, 35, 28, 0.08);
      color: var(--muted);
    }}
    .chip.hot {{ background: rgba(176, 75, 45, 0.12); color: var(--accent); }}
    .chip.ok {{ background: rgba(13, 123, 97, 0.12); color: var(--accent-2); }}
    .meta {{
      margin-top: 10px;
      display: flex;
      flex-wrap: wrap;
      gap: 8px 12px;
      font: 700 12px/1.35 var(--mono);
      color: var(--muted);
    }}
    .actions {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin-top: 12px;
    }}
    .actions button {{
      padding: 9px 12px;
      font-size: 0.76rem;
    }}
    .actions a {{
      display: inline-flex;
      align-items: center;
      justify-content: center;
      border-radius: 999px;
      padding: 9px 12px;
      font: 700 0.76rem/1 var(--mono);
      letter-spacing: 0.02em;
      background: rgba(20, 35, 28, 0.08);
      color: var(--ink);
      text-decoration: none;
      transition: transform .18s ease, box-shadow .18s ease, background .18s ease;
    }}
    .actions a:hover {{
      transform: translateY(-1px);
    }}
    form {{
      display: grid;
      gap: 12px;
    }}
    .field-grid {{
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 12px;
    }}
    label {{
      display: grid;
      gap: 6px;
      font: 700 12px/1 var(--mono);
      text-transform: uppercase;
      letter-spacing: 0.08em;
      color: var(--muted);
    }}
    input, select {{
      width: 100%;
      border: 1px solid rgba(20, 35, 28, 0.12);
      border-radius: 14px;
      background: rgba(255,255,255,0.72);
      color: var(--ink);
      padding: 13px 14px;
      font: 500 0.96rem/1.2 var(--body);
    }}
    .status-shell {{
      display: grid;
      gap: 10px;
    }}
    .state-banner {{
      border-radius: 18px;
      padding: 16px;
      background: linear-gradient(135deg, rgba(13, 123, 97, 0.16), rgba(255,255,255,0.4));
      border: 1px solid rgba(13, 123, 97, 0.18);
    }}
    .state-banner.error {{
      background: linear-gradient(135deg, rgba(143, 35, 24, 0.16), rgba(255,255,255,0.4));
      border-color: rgba(143, 35, 24, 0.18);
    }}
    .mono {{
      font-family: var(--mono);
      color: var(--muted);
      font-size: 12px;
    }}
    .empty {{
      padding: 24px;
      border-radius: 16px;
      border: 1px dashed rgba(20, 35, 28, 0.18);
      color: var(--muted);
      text-align: center;
    }}
    .story-grid {{
      display: grid;
      grid-template-columns: 0.96fr 1.14fr;
      gap: 16px;
      align-items: start;
    }}
    .story-list {{
      display: grid;
      gap: 12px;
      max-height: 760px;
      overflow: auto;
      padding-right: 4px;
    }}
    .card.selected {{
      border-color: rgba(13, 123, 97, 0.34);
      box-shadow: inset 0 0 0 1px rgba(13, 123, 97, 0.16);
      background: rgba(252, 255, 249, 0.72);
    }}
    .entity-row {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin-top: 12px;
    }}
    .story-detail {{
      display: grid;
      gap: 12px;
    }}
    .story-columns {{
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 12px;
    }}
    .text-block {{
      margin: 0;
      padding: 14px;
      border-radius: 14px;
      border: 1px solid var(--line);
      background: rgba(255, 255, 255, 0.48);
      white-space: pre-wrap;
      overflow: auto;
      font: 500 12px/1.55 var(--mono);
      color: var(--ink);
    }}
    .footer-note {{
      padding: 18px 0 8px;
      color: var(--muted);
      font-size: 0.92rem;
      text-align: center;
    }}
    @keyframes rise {{
      from {{ opacity: 0; transform: translateY(12px); }}
      to {{ opacity: 1; transform: translateY(0); }}
    }}
    @media (max-width: 1100px) {{
      .hero, .grid {{ grid-template-columns: 1fr; }}
      .story-grid, .story-columns {{ grid-template-columns: 1fr; }}
    }}
    @media (max-width: 760px) {{
      .shell {{ padding: 16px; }}
      .signal-strip, .field-grid {{ grid-template-columns: 1fr 1fr; }}
      h1 {{ max-width: none; }}
    }}
    @media (max-width: 560px) {{
      .signal-strip, .field-grid {{ grid-template-columns: 1fr; }}
      .toolbar {{ flex-direction: column; }}
      button {{ width: 100%; }}
    }}
  </style>
</head>
<body>
  <div class="shell">
    <section class="hero">
      <div class="hero-main">
        <div class="eyebrow"><span class="dot"></span> Intelligence Center / G0 Console Shell</div>
        <h1>Mission Control For Signal Work</h1>
        <p class="hero-copy">DataPulse now runs as a local-first intelligence console. Track recurring missions, audit alert routes, inspect daemon state, and operate the watch layer without dropping back to CLI.</p>
        <div class="toolbar">
          <button class="btn-primary" id="refresh-all">Refresh Board</button>
          <button class="btn-secondary" id="run-due">Run Due Missions</button>
        </div>
        <div class="signal-strip" id="overview-metrics"></div>
      </div>
      <aside class="hero-side">
        <div class="panel-head">
          <div>
            <div class="panel-title">Launch Mission</div>
            <div class="panel-sub">Create a watch with an alert rule from the browser.</div>
          </div>
        </div>
        <form id="create-watch-form">
          <div class="field-grid">
            <label>Name<input name="name" placeholder="Launch Ops" required></label>
            <label>Schedule<input name="schedule" placeholder="@hourly"></label>
          </div>
          <label>Query<input name="query" placeholder="OpenAI launch" required></label>
          <div class="field-grid">
            <label>Platform<input name="platform" placeholder="twitter"></label>
            <label>Domain<input name="domain" placeholder="openai.com"></label>
          </div>
          <div class="field-grid">
            <label>Alert Route<input name="route" placeholder="ops-webhook"></label>
            <label>Keyword<input name="keyword" placeholder="launch"></label>
          </div>
          <div class="field-grid">
            <label>Min Score<input name="min_score" placeholder="70" type="number"></label>
            <label>Min Confidence<input name="min_confidence" placeholder="0.8" step="0.01" type="number"></label>
          </div>
          <button class="btn-primary" type="submit">Create Watch</button>
        </form>
      </aside>
    </section>

    <section class="grid">
      <article class="panel">
        <div class="panel-head">
          <div>
            <h2 class="panel-title">Mission Board</h2>
            <div class="panel-sub">Run, inspect, and disable watch missions.</div>
          </div>
        </div>
        <div class="stack" id="watch-list"></div>
      </article>

      <article class="panel">
        <div class="panel-head">
          <div>
            <h2 class="panel-title">Alert Stream</h2>
            <div class="panel-sub">Recent alert events and configured delivery routes.</div>
          </div>
        </div>
        <div class="stack" id="alert-list"></div>
        <div class="stack" id="route-list"></div>
      </article>

      <article class="panel">
        <div class="panel-head">
          <div>
            <h2 class="panel-title">Daemon State</h2>
            <div class="panel-sub">Heartbeat, metrics, and latest scheduler state.</div>
          </div>
        </div>
        <div class="status-shell" id="status-card"></div>
      </article>
    </section>

    <section class="panel">
      <div class="panel-head">
        <div>
          <h2 class="panel-title">Triage Queue</h2>
          <div class="panel-sub">Review open items, push high-signal stories forward, and suppress low-value noise.</div>
        </div>
      </div>
      <div class="meta" id="triage-stats-inline"></div>
      <div class="stack" id="triage-list"></div>
    </section>

    <section class="panel">
      <div class="panel-head">
        <div>
          <h2 class="panel-title">Story Workspace</h2>
          <div class="panel-sub">Inspect clustered stories, evidence stacks, contradictions, and timeline drift without leaving the browser.</div>
        </div>
      </div>
      <div class="meta" id="story-stats-inline"></div>
      <div class="story-grid">
        <div class="story-list" id="story-list"></div>
        <div class="story-detail" id="story-detail"></div>
      </div>
    </section>

    <div class="footer-note">Local-first console shell. CLI and MCP remain first-class control planes.</div>
  </div>

    <script>
    const initial = {initial_state};
    const state = {{
      watches: [],
      alerts: [],
      routes: [],
      status: null,
      overview: null,
      triage: [],
      triageStats: null,
      triageExplain: {{}},
      stories: [],
      storyDetails: {{}},
      storyMarkdown: {{}},
      selectedStoryId: "",
    }};

    const $ = (id) => document.getElementById(id);
    const jsonHeaders = {{ "Content-Type": "application/json" }};

    async function api(path, options = {{}}) {{
      const response = await fetch(path, options);
      if (!response.ok) {{
        const detail = await response.text();
        throw new Error(detail || `Request failed: ${{response.status}}`);
      }}
      return response.json();
    }}

    async function apiText(path, options = {{}}) {{
      const response = await fetch(path, options);
      if (!response.ok) {{
        const detail = await response.text();
        throw new Error(detail || `Request failed: ${{response.status}}`);
      }}
      return response.text();
    }}

    function escapeHtml(value) {{
      return String(value ?? "").replace(/[&<>"']/g, (char) => {{
        return {{ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }}[char];
      }});
    }}

    function metricCard(label, value, tone = "") {{
      return `<div class="metric"><div class="metric-label">${{label}}</div><div class="metric-value ${{tone}}">${{value}}</div></div>`;
    }}

    function renderOverview() {{
      const metrics = state.overview || {{}};
      $("overview-metrics").innerHTML = [
        metricCard("Enabled Missions", metrics.enabled_watches ?? 0),
        metricCard("Due Now", metrics.due_watches ?? 0, "hot"),
        metricCard("Stories", metrics.story_count ?? 0),
        metricCard("Alert Routes", metrics.route_count ?? 0),
        metricCard("Open Queue", metrics.triage_open_count ?? 0),
        metricCard("Daemon State", String(metrics.daemon_state || "idle").toUpperCase()),
      ].join("");
    }}

    function renderWatches() {{
      const root = $("watch-list");
      if (!state.watches.length) {{
        root.innerHTML = `<div class="empty">No watch mission configured yet.</div>`;
        return;
      }}
      root.innerHTML = state.watches.map((watch) => {{
        const platforms = (watch.platforms || []).join(", ") || "any";
        const sites = (watch.sites || []).join(", ") || "-";
        const stateChip = watch.enabled ? "ok" : "";
        const dueChip = watch.is_due ? "hot" : "";
        return `
          <div class="card">
            <div class="card-top">
              <div>
                <h3 class="card-title">${{watch.name}}</h3>
                <div class="meta">
                  <span>${{watch.id}}</span>
                  <span>schedule=${{watch.schedule_label || watch.schedule || "manual"}}</span>
                  <span>platforms=${{platforms}}</span>
                  <span>sites=${{sites}}</span>
                </div>
              </div>
              <div style="display:grid; gap:6px; justify-items:end;">
                <span class="chip ${{stateChip}}">${{watch.enabled ? "enabled" : "disabled"}}</span>
                <span class="chip ${{dueChip}}">${{watch.is_due ? "due" : "waiting"}}</span>
              </div>
            </div>
            <div class="meta">
              <span>alert_rules=${{watch.alert_rule_count || 0}}</span>
              <span>last_run=${{watch.last_run_at || "-"}}</span>
              <span>status=${{watch.last_run_status || "-"}}</span>
            </div>
            <div class="actions">
              <button class="btn-secondary" data-run-watch="${{watch.id}}">Run Mission</button>
              <button class="btn-secondary" data-disable-watch="${{watch.id}}">Disable</button>
            </div>
          </div>`;
      }}).join("");

      root.querySelectorAll("[data-run-watch]").forEach((button) => {{
        button.addEventListener("click", async () => {{
          button.disabled = true;
          try {{
            await api(`/api/watches/${{button.dataset.runWatch}}/run`, {{ method: "POST" }});
            await refreshBoard();
          }} catch (error) {{
            alert(error.message);
          }} finally {{
            button.disabled = false;
          }}
        }});
      }});

      root.querySelectorAll("[data-disable-watch]").forEach((button) => {{
        button.addEventListener("click", async () => {{
          button.disabled = true;
          try {{
            await api(`/api/watches/${{button.dataset.disableWatch}}/disable`, {{ method: "POST" }});
            await refreshBoard();
          }} catch (error) {{
            alert(error.message);
          }} finally {{
            button.disabled = false;
          }}
        }});
      }});
    }}

    function renderAlerts() {{
      const root = $("alert-list");
      if (!state.alerts.length) {{
        root.innerHTML = `<div class="empty">No alert event stored.</div>`;
        return;
      }}
      root.innerHTML = state.alerts.map((alert) => `
        <div class="card">
          <div class="card-top">
            <div>
              <h3 class="card-title">${{alert.mission_name}}</h3>
              <div class="meta">
                <span>${{alert.rule_name}}</span>
                <span>${{alert.created_at || "-"}}</span>
              </div>
            </div>
            <span class="chip hot">${{(alert.delivered_channels || ["json"]).join(",")}}</span>
          </div>
          <div class="panel-sub">${{alert.summary || ""}}</div>
        </div>
      `).join("");
    }}

    function renderRoutes() {{
      const root = $("route-list");
      if (!state.routes.length) {{
        root.innerHTML = `<div class="empty">No named alert route configured.</div>`;
        return;
      }}
      root.innerHTML = state.routes.map((route) => `
        <div class="card">
          <div class="card-top">
            <div>
              <h3 class="card-title">${{route.name}}</h3>
              <div class="meta"><span>channel=${{route.channel}}</span></div>
            </div>
            <span class="chip">${{route.channel}}</span>
          </div>
        </div>
      `).join("");
    }}

    function renderStatus() {{
      const root = $("status-card");
      const status = state.status || {{}};
      const metrics = status.metrics || {{}};
      const isError = status.state === "error";
      root.innerHTML = `
        <div class="state-banner ${{isError ? "error" : ""}}">
          <div class="eyebrow"><span class="dot"></span> daemon / ${{status.state || "idle"}}</div>
          <h3 class="card-title" style="margin-top:12px;">Heartbeat: ${{status.heartbeat_at || "-"}}</h3>
          <div class="meta">
            <span>cycles=${{metrics.cycles_total || 0}}</span>
            <span>runs=${{metrics.runs_total || 0}}</span>
            <span>alerts=${{metrics.alerts_total || 0}}</span>
            <span>errors=${{metrics.error_total || 0}}</span>
          </div>
        </div>
        <div class="card">
          <div class="mono">last_error</div>
          <div>${{status.last_error || "-"}}</div>
        </div>`;
    }}

    function renderDuplicateExplain(payload) {{
      if (!payload) {{
        return "";
      }}
      const candidates = payload.candidates || [];
      const header = `
        <div class="meta">
          <span>suggested_primary=${{payload.suggested_primary_id || "-"}}</span>
          <span>matches=${{payload.candidate_count || 0}}</span>
          <span>shown=${{payload.returned_count || 0}}</span>
        </div>
      `;
      if (!candidates.length) {{
        return `<div class="card" style="margin-top:12px;">${{header}}<div class="panel-sub">No close duplicate candidate found.</div></div>`;
      }}
      return `
        <div class="card" style="margin-top:12px;">
          ${{header}}
          <div class="stack" style="margin-top:12px;">
            ${{candidates.map((candidate) => `
              <div class="card">
                <div class="card-top">
                  <div>
                    <h3 class="card-title">${{candidate.title}}</h3>
                    <div class="meta">
                      <span>${{candidate.id}}</span>
                      <span>similarity=${{Number(candidate.similarity || 0).toFixed(2)}}</span>
                      <span>state=${{candidate.review_state || "new"}}</span>
                    </div>
                  </div>
                  <span class="chip ${{candidate.suggested_primary_id === candidate.id ? "ok" : ""}}">${{candidate.suggested_primary_id === candidate.id ? "keep" : "merge"}}</span>
                </div>
                <div class="meta">
                  <span>signals=${{(candidate.signals || []).join(", ") || "-"}}</span>
                  <span>domain=${{candidate.same_domain ? "same" : "mixed"}}</span>
                </div>
              </div>
            `).join("")}}
          </div>
        </div>
      `;
    }}

    function renderTriage() {{
      const root = $("triage-list");
      const inlineStats = $("triage-stats-inline");
      const stats = state.triageStats || {{}};
      inlineStats.innerHTML = `
        <span>open=${{stats.open_count || 0}}</span>
        <span>closed=${{stats.closed_count || 0}}</span>
        <span>notes=${{stats.note_count || 0}}</span>
        <span>verified=${{(stats.states || {{}}).verified || 0}}</span>
      `;
      if (!state.triage.length) {{
        root.innerHTML = `<div class="empty">No open triage item right now.</div>`;
        return;
      }}
      root.innerHTML = state.triage.map((item) => `
        <div class="card">
          <div class="card-top">
            <div>
              <h3 class="card-title">${{item.title}}</h3>
              <div class="meta">
                <span>${{item.id}}</span>
                <span>state=${{item.review_state || "new"}}</span>
                <span>score=${{item.score || 0}}</span>
                <span>confidence=${{Number(item.confidence || 0).toFixed(2)}}</span>
              </div>
            </div>
            <span class="chip ${{item.review_state === "escalated" ? "hot" : ""}}">${{item.review_state || "new"}}</span>
          </div>
          <div class="panel-sub">${{item.url}}</div>
          <div class="actions">
            <button class="btn-secondary" data-triage-explain="${{item.id}}">Explain Dup</button>
            <button class="btn-secondary" data-triage-state="verified" data-triage-id="${{item.id}}">Verify</button>
            <button class="btn-secondary" data-triage-state="escalated" data-triage-id="${{item.id}}">Escalate</button>
            <button class="btn-secondary" data-triage-state="ignored" data-triage-id="${{item.id}}">Ignore</button>
          </div>
          ${{renderDuplicateExplain(state.triageExplain[item.id])}}
        </div>
      `).join("");

      root.querySelectorAll("[data-triage-explain]").forEach((button) => {{
        button.addEventListener("click", async () => {{
          button.disabled = true;
          try {{
            const itemId = button.dataset.triageExplain;
            state.triageExplain[itemId] = await api(`/api/triage/${{itemId}}/explain?limit=4`);
            renderTriage();
          }} catch (error) {{
            alert(error.message);
          }} finally {{
            button.disabled = false;
          }}
        }});
      }});

      root.querySelectorAll("[data-triage-state]").forEach((button) => {{
        button.addEventListener("click", async () => {{
          button.disabled = true;
          try {{
            await api(`/api/triage/${{button.dataset.triageId}}/state`, {{
              method: "POST",
              headers: jsonHeaders,
              body: JSON.stringify({{ state: button.dataset.triageState, actor: "console" }}),
            }});
            await refreshBoard();
          }} catch (error) {{
            alert(error.message);
          }} finally {{
            button.disabled = false;
          }}
        }});
      }});
    }}

    async function loadStory(identifier) {{
      state.selectedStoryId = identifier;
      state.storyDetails[identifier] = await api(`/api/stories/${{identifier}}`);
      renderStories();
    }}

    async function previewStoryMarkdown(identifier) {{
      state.selectedStoryId = identifier;
      if (!state.storyDetails[identifier]) {{
        state.storyDetails[identifier] = await api(`/api/stories/${{identifier}}`);
      }}
      state.storyMarkdown[identifier] = await apiText(`/api/stories/${{identifier}}/export?format=markdown`);
      renderStories();
    }}

    function renderStoryDetail() {{
      const root = $("story-detail");
      const selected = state.selectedStoryId;
      const story = state.storyDetails[selected] || state.stories.find((candidate) => candidate.id === selected);
      if (!story) {{
        root.innerHTML = `<div class="empty">No persisted story snapshot yet. Build stories from CLI or MCP first.</div>`;
        return;
      }}
      const evidenceBlock = (rows, emptyLabel) => rows.length
        ? rows.map((row) => `
            <div class="card">
              <div class="card-top">
                <div>
                  <h3 class="card-title">${{row.title}}</h3>
                  <div class="meta">
                    <span>${{row.item_id}}</span>
                    <span>${{row.source_name || row.source_type || "-"}}</span>
                    <span>score=${{row.score || 0}}</span>
                    <span>confidence=${{Number(row.confidence || 0).toFixed(2)}}</span>
                  </div>
                </div>
                <span class="chip ${{row.role === "primary" ? "ok" : ""}}">${{row.role || "secondary"}}</span>
              </div>
              <div class="panel-sub">${{row.url || "-"}}</div>
            </div>
          `).join("")
        : `<div class="empty">${{emptyLabel}}</div>`;
      const contradictionBlock = (story.contradictions || []).length
        ? story.contradictions.map((conflict) => `
            <div class="card">
              <div class="card-top">
                <div>
                  <h3 class="card-title">${{conflict.topic}}</h3>
                  <div class="meta">
                    <span>positive=${{conflict.positive || 0}}</span>
                    <span>negative=${{conflict.negative || 0}}</span>
                    <span>neutral=${{conflict.neutral || 0}}</span>
                  </div>
                </div>
                <span class="chip hot">conflict</span>
              </div>
              <div class="panel-sub">${{conflict.note || "Cross-source stance divergence detected."}}</div>
            </div>
          `).join("")
        : `<div class="empty">No contradiction marker in this story.</div>`;
      const timelineBlock = (story.timeline || []).length
        ? story.timeline.map((event) => `
            <div class="card">
              <div class="card-top">
                <div>
                  <h3 class="card-title">${{event.title}}</h3>
                  <div class="meta">
                    <span>${{event.time || "-"}}</span>
                    <span>${{event.source_name || "-"}}</span>
                    <span>role=${{event.role || "secondary"}}</span>
                    <span>score=${{event.score || 0}}</span>
                  </div>
                </div>
              </div>
              <div class="panel-sub">${{event.url || "-"}}</div>
            </div>
          `).join("")
        : `<div class="empty">No timeline event captured.</div>`;
      const markdownPreview = state.storyMarkdown[selected]
        ? `
            <div class="card">
              <div class="mono">markdown evidence pack</div>
              <pre class="text-block">${{escapeHtml(state.storyMarkdown[selected])}}</pre>
            </div>
          `
        : "";
      root.innerHTML = `
        <div class="card">
          <div class="card-top">
            <div>
              <h3 class="card-title">${{story.title}}</h3>
              <div class="meta">
                <span>${{story.id}}</span>
                <span>status=${{story.status || "active"}}</span>
                <span>items=${{story.item_count || 0}}</span>
                <span>sources=${{story.source_count || 0}}</span>
                <span>score=${{Number(story.score || 0).toFixed(1)}}</span>
                <span>confidence=${{Number(story.confidence || 0).toFixed(2)}}</span>
              </div>
            </div>
            <span class="chip ${{(story.contradictions || []).length ? "hot" : "ok"}}">${{(story.contradictions || []).length ? "mixed signals" : "aligned"}}</span>
          </div>
          <div class="panel-sub">${{story.summary || "No summary captured."}}</div>
          <div class="entity-row">
            ${{(story.entities || []).slice(0, 8).map((entity) => `<span class="chip">${{entity}}</span>`).join("") || '<span class="chip">no entities</span>'}}
          </div>
          <div class="actions">
            <button class="btn-secondary" data-story-markdown="${{story.id}}">Preview Markdown</button>
            <a href="/api/stories/${{story.id}}" target="_blank" rel="noreferrer">Open JSON</a>
            <a href="/api/stories/${{story.id}}/export?format=markdown" target="_blank" rel="noreferrer">Export MD</a>
          </div>
        </div>
        <div class="story-columns">
          <div class="stack">
            <div class="mono">primary evidence</div>
            ${{evidenceBlock(story.primary_evidence || [], "No primary evidence captured.")}}
          </div>
          <div class="stack">
            <div class="mono">secondary evidence</div>
            ${{evidenceBlock(story.secondary_evidence || [], "No secondary evidence captured.")}}
          </div>
        </div>
        <div class="stack">
          <div class="mono">contradiction markers</div>
          ${{contradictionBlock}}
        </div>
        <div class="stack">
          <div class="mono">timeline</div>
          ${{timelineBlock}}
        </div>
        ${{markdownPreview}}
      `;

      root.querySelectorAll("[data-story-markdown]").forEach((button) => {{
        button.addEventListener("click", async () => {{
          button.disabled = true;
          try {{
            await previewStoryMarkdown(button.dataset.storyMarkdown);
          }} catch (error) {{
            alert(error.message);
          }} finally {{
            button.disabled = false;
          }}
        }});
      }});
    }}

    function renderStories() {{
      const root = $("story-list");
      const inlineStats = $("story-stats-inline");
      const contradictions = state.stories.reduce((count, story) => count + ((story.contradictions || []).length ? 1 : 0), 0);
      const totalEvidence = state.stories.reduce((count, story) => count + (story.item_count || 0), 0);
      inlineStats.innerHTML = `
        <span>stories=${{state.stories.length}}</span>
        <span>evidence=${{totalEvidence}}</span>
        <span>contradicted=${{contradictions}}</span>
        <span>selected=${{state.selectedStoryId || "-"}}</span>
      `;
      if (!state.stories.length) {{
        root.innerHTML = `<div class="empty">No story snapshot yet. Run datapulse --story-build or the MCP story tools first.</div>`;
        renderStoryDetail();
        return;
      }}
      root.innerHTML = state.stories.map((story) => {{
        const selected = story.id === state.selectedStoryId ? "selected" : "";
        const primary = (story.primary_evidence || [])[0];
        return `
          <div class="card ${{selected}}">
            <div class="card-top">
              <div>
                <h3 class="card-title">${{story.title}}</h3>
                <div class="meta">
                  <span>${{story.id}}</span>
                  <span>items=${{story.item_count || 0}}</span>
                  <span>sources=${{story.source_count || 0}}</span>
                  <span>score=${{Number(story.score || 0).toFixed(1)}}</span>
                </div>
              </div>
              <span class="chip ${{(story.contradictions || []).length ? "hot" : "ok"}}">${{(story.contradictions || []).length ? "mixed" : "aligned"}}</span>
            </div>
            <div class="panel-sub">${{story.summary || "No summary captured."}}</div>
            <div class="entity-row">
              ${{(story.entities || []).slice(0, 4).map((entity) => `<span class="chip">${{entity}}</span>`).join("") || '<span class="chip">no entities</span>'}}
            </div>
            <div class="meta">
              <span>primary=${{primary ? primary.title : "-"}}</span>
              <span>timeline=${{(story.timeline || []).length}}</span>
              <span>conflicts=${{(story.contradictions || []).length}}</span>
            </div>
            <div class="actions">
              <button class="btn-secondary" data-story-open="${{story.id}}">Open Story</button>
              <button class="btn-secondary" data-story-preview="${{story.id}}">Preview MD</button>
            </div>
          </div>
        `;
      }}).join("");

      root.querySelectorAll("[data-story-open]").forEach((button) => {{
        button.addEventListener("click", async () => {{
          button.disabled = true;
          try {{
            await loadStory(button.dataset.storyOpen);
          }} catch (error) {{
            alert(error.message);
          }} finally {{
            button.disabled = false;
          }}
        }});
      }});

      root.querySelectorAll("[data-story-preview]").forEach((button) => {{
        button.addEventListener("click", async () => {{
          button.disabled = true;
          try {{
            await previewStoryMarkdown(button.dataset.storyPreview);
          }} catch (error) {{
            alert(error.message);
          }} finally {{
            button.disabled = false;
          }}
        }});
      }});

      renderStoryDetail();
    }}

    async function refreshBoard() {{
      const [overview, watches, alerts, routes, status, triage, triageStats, stories] = await Promise.all([
        api("/api/overview"),
        api("/api/watches?include_disabled=true"),
        api("/api/alerts?limit=8"),
        api("/api/alert-routes"),
        api("/api/watch-status"),
        api("/api/triage?limit=6"),
        api("/api/triage/stats"),
        api("/api/stories?limit=6&min_items=2"),
      ]);
      state.overview = overview;
      state.watches = watches;
      state.alerts = alerts;
      state.routes = routes;
      state.status = status;
      state.triage = triage;
      state.triageStats = triageStats;
      state.stories = stories;
      if (state.stories.length) {{
        const selected = state.stories.some((story) => story.id === state.selectedStoryId)
          ? state.selectedStoryId
          : state.stories[0].id;
        state.selectedStoryId = selected;
        if (!state.storyDetails[selected]) {{
          const seeded = state.stories.find((story) => story.id === selected);
          if (seeded) {{
            state.storyDetails[selected] = seeded;
          }}
        }}
      }} else {{
        state.selectedStoryId = "";
      }}
      renderOverview();
      renderWatches();
      renderAlerts();
      renderRoutes();
      renderStatus();
      renderTriage();
      renderStories();
    }}

    $("refresh-all").addEventListener("click", refreshBoard);
    $("run-due").addEventListener("click", async () => {{
      try {{
        await api("/api/watches/run-due", {{ method: "POST", headers: jsonHeaders, body: JSON.stringify({{ limit: 0 }}) }});
        await refreshBoard();
      }} catch (error) {{
        alert(error.message);
      }}
    }});

    $("create-watch-form").addEventListener("submit", async (event) => {{
      event.preventDefault();
      const form = new FormData(event.target);
      const alertRule = {{
        name: "console-threshold",
        min_score: Number(form.get("min_score") || 0),
        min_confidence: Number(form.get("min_confidence") || 0),
        channels: ["json"],
      }};
      const route = String(form.get("route") || "").trim();
      const keyword = String(form.get("keyword") || "").trim();
      const domain = String(form.get("domain") || "").trim();
      if (route) alertRule.routes = [route];
      if (keyword) alertRule.keyword_any = [keyword];
      if (domain) alertRule.domains = [domain];
      const payload = {{
        name: String(form.get("name") || "").trim(),
        query: String(form.get("query") || "").trim(),
        schedule: String(form.get("schedule") || "manual").trim() || "manual",
        platforms: String(form.get("platform") || "").trim() ? [String(form.get("platform")).trim()] : null,
        alert_rules: [alertRule],
      }};
      try {{
        await api("/api/watches", {{ method: "POST", headers: jsonHeaders, body: JSON.stringify(payload) }});
        event.target.reset();
        await refreshBoard();
      }} catch (error) {{
        alert(error.message);
      }}
    }});

    refreshBoard().catch((error) => {{
      console.error(error);
      alert(`Console boot failed: ${{error.message}}`);
    }});
  </script>
</body>
</html>"""


class WatchCreateRequest(BaseModel):
    name: str
    query: str
    platforms: list[str] | None = None
    sites: list[str] | None = None
    schedule: str = "manual"
    min_confidence: float = 0.0
    top_n: int = 5
    alert_rules: list[dict[str, Any]] | None = None


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


def create_app(reader_factory: Callable[[], DataPulseReader] = DataPulseReader) -> FastAPI:
    app = FastAPI(title=CONSOLE_TITLE, version="0.7.0")

    @app.get("/", response_class=HTMLResponse)
    def index() -> str:
        return _console_html()

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
        stories = reader.list_stories(limit=5000, min_items=2)
        return {
            "enabled_watches": sum(1 for watch in watches if watch.get("enabled", True)),
            "disabled_watches": sum(1 for watch in watches if not watch.get("enabled", True)),
            "due_watches": sum(1 for watch in watches if watch.get("is_due")),
            "story_count": len(stories),
            "alert_count": len(alerts),
            "route_count": len(routes),
            "triage_open_count": reader.triage_stats().get("open_count", 0),
            "daemon_state": status.get("state", "idle"),
            "daemon_heartbeat_at": status.get("heartbeat_at", ""),
        }

    @app.get("/api/watches")
    def list_watches(include_disabled: bool = False) -> list[dict[str, Any]]:
        return reader_factory().list_watches(include_disabled=include_disabled)

    @app.post("/api/watches")
    def create_watch(payload: WatchCreateRequest) -> dict[str, Any]:
        return reader_factory().create_watch(**payload.model_dump())

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

    @app.get("/api/alerts")
    def list_alerts(limit: int = 20, mission_id: str = "") -> list[dict[str, Any]]:
        return reader_factory().list_alerts(limit=limit, mission_id=mission_id or None)

    @app.get("/api/alert-routes")
    def list_alert_routes() -> list[dict[str, Any]]:
        return reader_factory().list_alert_routes()

    @app.get("/api/watch-status")
    def watch_status() -> dict[str, Any]:
        return reader_factory().watch_status_snapshot()

    @app.get("/api/stories")
    def list_stories(limit: int = 8, min_items: int = 2) -> list[dict[str, Any]]:
        return reader_factory().list_stories(limit=limit, min_items=min_items)

    @app.get("/api/stories/{identifier}")
    def show_story(identifier: str) -> dict[str, Any]:
        story = reader_factory().show_story(identifier)
        if story is None:
            raise HTTPException(status_code=404, detail=f"Story not found: {identifier}")
        return story

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

    @app.get("/api/triage")
    def triage_list(limit: int = 20, state: list[str] | None = None, include_closed: bool = False) -> list[dict[str, Any]]:
        return reader_factory().triage_list(limit=limit, states=state, include_closed=include_closed)

    @app.get("/api/triage/stats")
    def triage_stats() -> dict[str, Any]:
        return reader_factory().triage_stats()

    @app.get("/api/triage/{item_id}/explain")
    def triage_explain(item_id: str, limit: int = 5) -> dict[str, Any]:
        payload = reader_factory().triage_explain(item_id, limit=limit)
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

    return app


def main() -> None:
    parser = argparse.ArgumentParser(description="Launch the DataPulse browser console.")
    parser.add_argument("--host", default="127.0.0.1", help="Bind host (default 127.0.0.1)")
    parser.add_argument("--port", type=int, default=8765, help="Bind port (default 8765)")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload for local development")
    args = parser.parse_args()

    import uvicorn

    uvicorn.run("datapulse.console_server:create_app", host=args.host, port=args.port, reload=args.reload, factory=True)
