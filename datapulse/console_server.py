"""Local browser console for the DataPulse intelligence center."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Callable

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, HTMLResponse, Response
from pydantic import BaseModel, Field

from datapulse.reader import DataPulseReader

CONSOLE_TITLE = "DataPulse Command Chamber"
BRAND_SOURCE_PATH = Path(__file__).resolve().parent.parent / "docs" / "形象.jpg"
BRAND_HERO_PATH = Path(__file__).resolve().parent.parent / "docs" / "assets" / "datapulse-command-chamber-hero.jpg"
BRAND_SQUARE_PATH = Path(__file__).resolve().parent.parent / "docs" / "assets" / "datapulse-command-chamber-square.jpg"
BRAND_ICON_PATH = Path(__file__).resolve().parent.parent / "docs" / "assets" / "datapulse-command-chamber-icon.png"


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
  <link rel="icon" type="image/png" href="/brand/icon">
  <link rel="apple-touch-icon" href="/brand/square">
  <style>
    :root {{
      --paper: #08111c;
      --mist: #112033;
      --panel: rgba(10, 18, 31, 0.76);
      --panel-strong: rgba(9, 15, 28, 0.9);
      --ink: #eaf4ff;
      --muted: #9fb3ca;
      --accent: #ff6a82;
      --accent-2: #7fe4ff;
      --line: rgba(146, 175, 210, 0.18);
      --warn: #ff6a82;
      --shadow: 0 28px 90px rgba(3, 8, 18, 0.5);
      --headline: "Eurostile Extended", "Avenir Next Condensed", "Arial Narrow", sans-serif;
      --body: "IBM Plex Sans", "Avenir Next", "Segoe UI", sans-serif;
      --mono: "SF Mono", "IBM Plex Mono", "Menlo", monospace;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      min-height: 100vh;
      color: var(--ink);
      background:
        radial-gradient(circle at 50% 24%, rgba(255, 106, 130, 0.16), transparent 18%),
        radial-gradient(circle at 50% 26%, rgba(127, 228, 255, 0.14), transparent 24%),
        radial-gradient(circle at 10% 10%, rgba(255, 106, 130, 0.14), transparent 26%),
        radial-gradient(circle at 90% 8%, rgba(127, 228, 255, 0.12), transparent 22%),
        linear-gradient(180deg, #101a2c 0%, #0a111c 52%, var(--paper) 100%);
      font-family: var(--body);
    }}
    body::before {{
      content: "";
      position: fixed;
      inset: 0;
      pointer-events: none;
      background-image:
        linear-gradient(rgba(148, 176, 209, 0.07) 1px, transparent 1px),
        linear-gradient(90deg, rgba(148, 176, 209, 0.07) 1px, transparent 1px);
      background-size: 28px 28px;
      mask-image: linear-gradient(180deg, rgba(0,0,0,0.55), transparent 92%);
    }}
    body::after {{
      content: "";
      position: fixed;
      right: 44px;
      bottom: 34px;
      width: 32px;
      height: 32px;
      transform: rotate(45deg);
      border: 1px solid rgba(234, 244, 255, 0.32);
      box-shadow:
        0 0 22px rgba(255, 106, 130, 0.14),
        0 0 32px rgba(127, 228, 255, 0.12);
      pointer-events: none;
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
      background:
        linear-gradient(160deg, rgba(20, 34, 53, 0.94), rgba(8, 14, 24, 0.92)),
        var(--panel);
    }}
    .hero-main::before {{
      content: "";
      position: absolute;
      inset: -12% 22% 26% 22%;
      border-radius: 999px;
      background:
        radial-gradient(circle, rgba(127, 228, 255, 0.16), transparent 46%),
        radial-gradient(circle, rgba(255, 106, 130, 0.12), transparent 58%);
      filter: blur(6px);
      pointer-events: none;
    }}
    .hero-main::after {{
      content: "";
      position: absolute;
      inset: 54px 54px auto auto;
      width: 240px;
      height: 240px;
      border-radius: 999px;
      border: 1px solid rgba(255, 136, 154, 0.28);
      box-shadow:
        inset 0 0 0 16px rgba(255, 106, 130, 0.06),
        0 0 48px rgba(255, 106, 130, 0.18);
      opacity: 0.7;
      pointer-events: none;
    }}
    .hero-side {{
      padding: 24px;
      display: grid;
      gap: 12px;
      align-content: start;
      background:
        linear-gradient(180deg, rgba(18, 28, 45, 0.92), rgba(9, 14, 24, 0.9)),
        var(--panel);
    }}
    .brand-tile {{
      display: grid;
      grid-template-columns: 88px 1fr;
      gap: 14px;
      align-items: center;
      padding: 12px;
      border-radius: 20px;
      border: 1px solid rgba(147, 181, 215, 0.18);
      background: linear-gradient(180deg, rgba(14, 24, 39, 0.9), rgba(9, 14, 24, 0.94));
      box-shadow: inset 0 0 0 1px rgba(127, 228, 255, 0.05);
    }}
    .brand-image {{
      width: 88px;
      height: 88px;
      border-radius: 20px;
      object-fit: cover;
      border: 1px solid rgba(147, 181, 215, 0.24);
      box-shadow:
        0 0 24px rgba(127, 228, 255, 0.08),
        0 0 18px rgba(255, 106, 130, 0.1);
    }}
    .brand-copy {{
      display: grid;
      gap: 4px;
    }}
    .brand-copy strong {{
      font-family: var(--headline);
      font-size: 1.08rem;
      letter-spacing: 0.04em;
      text-transform: uppercase;
    }}
    .brand-copy span {{
      color: var(--muted);
      font-size: 0.92rem;
      line-height: 1.35;
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
      background: linear-gradient(180deg, #ffa1b0, var(--accent));
      box-shadow:
        0 0 0 5px rgba(255, 106, 130, 0.12),
        0 0 18px rgba(255, 106, 130, 0.45);
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
      background: linear-gradient(135deg, #ff8c9f, var(--accent));
      color: #fff7fb;
      box-shadow: 0 10px 28px rgba(255, 106, 130, 0.3);
    }}
    .btn-secondary {{
      background: rgba(127, 228, 255, 0.08);
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
    .hero-stage {{
      position: relative;
      height: 220px;
      margin: 18px 0 10px;
      border-radius: 24px;
      border: 1px solid rgba(147, 181, 215, 0.16);
      background:
        radial-gradient(circle at 50% 42%, rgba(127, 228, 255, 0.12), transparent 18%),
        radial-gradient(circle at 50% 46%, rgba(255, 106, 130, 0.14), transparent 24%),
        linear-gradient(180deg, rgba(15, 24, 39, 0.82), rgba(7, 11, 18, 0.94));
      overflow: hidden;
    }}
    .hero-stage::after {{
      content: "";
      position: absolute;
      inset: 0;
      background:
        linear-gradient(180deg, rgba(8, 14, 24, 0.08), rgba(8, 14, 24, 0.44)),
        radial-gradient(circle at 50% 42%, rgba(127, 228, 255, 0.1), transparent 30%);
      pointer-events: none;
    }}
    .hero-stage::before {{
      content: "";
      position: absolute;
      inset: auto 0 0 0;
      height: 68px;
      background:
        linear-gradient(rgba(147, 181, 215, 0.08) 1px, transparent 1px),
        linear-gradient(90deg, rgba(147, 181, 215, 0.08) 1px, transparent 1px);
      background-size: 30px 30px;
      opacity: 0.85;
    }}
    .hero-visual {{
      position: absolute;
      inset: 0;
      width: 100%;
      height: 100%;
      object-fit: cover;
      object-position: center;
      opacity: 0.92;
      filter: saturate(1.02) contrast(1.03);
    }}
    .stage-ring {{
      position: absolute;
      top: 22px;
      bottom: 34px;
      width: 186px;
      border: 2px solid rgba(255, 125, 145, 0.44);
      border-radius: 999px;
      background: linear-gradient(180deg, rgba(255, 124, 144, 0.1), rgba(255, 124, 144, 0.04));
      box-shadow:
        inset 0 0 0 10px rgba(255, 106, 130, 0.06),
        0 0 36px rgba(255, 106, 130, 0.18);
    }}
    .stage-ring-left {{ left: -24px; }}
    .stage-ring-right {{ right: -24px; }}
    .stage-ring::after {{
      content: "";
      position: absolute;
      left: 12px;
      right: 12px;
      top: 18px;
      bottom: 18px;
      border-radius: 999px;
      border: 1px solid rgba(255, 175, 186, 0.28);
    }}
    .stage-globe {{
      position: absolute;
      left: 50%;
      top: 44px;
      width: 168px;
      height: 168px;
      transform: translateX(-50%);
      border-radius: 999px;
      border: 2px solid rgba(167, 238, 255, 0.48);
      background:
        radial-gradient(circle at 50% 46%, rgba(127, 228, 255, 0.14), transparent 58%),
        radial-gradient(circle at 42% 40%, rgba(255, 122, 143, 0.18), transparent 48%);
      box-shadow:
        inset 0 0 42px rgba(127, 228, 255, 0.12),
        0 0 42px rgba(127, 228, 255, 0.12);
    }}
    .stage-globe::before,
    .stage-globe::after {{
      content: "";
      position: absolute;
      border-radius: 999px;
      inset: 18px;
      border: 1px solid rgba(167, 238, 255, 0.22);
    }}
    .stage-globe::after {{
      inset: 48% 8px auto 8px;
      height: 1px;
      border: 0;
      background: rgba(167, 238, 255, 0.28);
    }}
    .stage-console {{
      position: absolute;
      bottom: 34px;
      width: 126px;
      height: 58px;
      border-radius: 16px;
      border: 1px solid rgba(147, 181, 215, 0.24);
      background:
        linear-gradient(180deg, rgba(16, 26, 41, 0.94), rgba(9, 14, 24, 0.98));
      box-shadow: inset 0 0 0 1px rgba(127, 228, 255, 0.06);
    }}
    .stage-console-left {{ left: 22%; }}
    .stage-console-right {{ right: 22%; }}
    .stage-console::before {{
      content: "";
      position: absolute;
      left: 16px;
      right: 16px;
      top: 16px;
      height: 4px;
      background:
        linear-gradient(90deg, rgba(127, 228, 255, 0.54), rgba(255, 106, 130, 0.72));
      border-radius: 999px;
    }}
    .metric {{
      padding: 16px;
      border-radius: 18px;
      border: 1px solid var(--line);
      background: rgba(17, 28, 45, 0.72);
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
      background: rgba(16, 27, 43, 0.76);
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
      background: rgba(127, 228, 255, 0.08);
      color: var(--muted);
    }}
    .chip.hot {{ background: rgba(255, 106, 130, 0.14); color: var(--accent); }}
    .chip.ok {{ background: rgba(127, 228, 255, 0.14); color: var(--accent-2); }}
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
      background: rgba(127, 228, 255, 0.08);
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
      border: 1px solid rgba(147, 181, 215, 0.16);
      border-radius: 14px;
      background: rgba(11, 18, 30, 0.86);
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
      background: linear-gradient(135deg, rgba(127, 228, 255, 0.12), rgba(10, 18, 31, 0.74));
      border: 1px solid rgba(127, 228, 255, 0.16);
    }}
    .state-banner.error {{
      background: linear-gradient(135deg, rgba(255, 106, 130, 0.16), rgba(10, 18, 31, 0.72));
      border-color: rgba(255, 106, 130, 0.18);
    }}
    .mono {{
      font-family: var(--mono);
      color: var(--muted);
      font-size: 12px;
    }}
    .empty {{
      padding: 24px;
      border-radius: 16px;
      border: 1px dashed rgba(147, 181, 215, 0.24);
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
      border-color: rgba(127, 228, 255, 0.3);
      box-shadow: inset 0 0 0 1px rgba(127, 228, 255, 0.16);
      background: rgba(15, 26, 41, 0.9);
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
    .graph-shell {{
      display: grid;
      gap: 12px;
    }}
    .graph-canvas {{
      border-radius: 18px;
      border: 1px solid var(--line);
      background:
        radial-gradient(circle at 50% 45%, rgba(127, 228, 255, 0.12), transparent 42%),
        linear-gradient(180deg, rgba(17, 27, 43, 0.92), rgba(9, 14, 24, 0.94));
      overflow: hidden;
    }}
    .graph-canvas svg {{
      width: 100%;
      height: auto;
      display: block;
    }}
    .graph-meta {{
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 12px;
    }}
    .mini-list {{
      display: grid;
      gap: 8px;
    }}
    .mini-item {{
      border-radius: 14px;
      border: 1px solid var(--line);
      padding: 10px 12px;
      background: rgba(16, 27, 43, 0.72);
      font: 700 12px/1.4 var(--mono);
      color: var(--muted);
    }}
    .text-block {{
      margin: 0;
      padding: 14px;
      border-radius: 14px;
      border: 1px solid var(--line);
      background: rgba(16, 27, 43, 0.74);
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
        <div class="eyebrow"><span class="dot"></span> Command Chamber / Local-first Intelligence Surface</div>
        <h1>Command Chamber For Signal Operations</h1>
        <p class="hero-copy">DataPulse now presents itself as a steel-blue intelligence chamber: recurring missions on the edge, evidence at the core, and alert telemetry under visible containment.</p>
        <div class="toolbar">
          <button class="btn-primary" id="refresh-all">Refresh Chamber</button>
          <button class="btn-secondary" id="run-due">Run Due Missions</button>
        </div>
        <div class="hero-stage" aria-hidden="true">
          <img class="hero-visual" src="/brand/hero" alt="DataPulse command chamber brand visual">
          <div class="stage-ring stage-ring-left"></div>
          <div class="stage-ring stage-ring-right"></div>
          <div class="stage-globe"></div>
          <div class="stage-console stage-console-left"></div>
          <div class="stage-console stage-console-right"></div>
        </div>
        <div class="signal-strip" id="overview-metrics"></div>
      </div>
      <aside class="hero-side">
        <div class="brand-tile">
          <img class="brand-image" src="/brand/square" alt="DataPulse compact brand mark">
          <div class="brand-copy">
            <div class="mono">Brand Frame</div>
            <strong>Command Chamber</strong>
            <span>Wide hero for primary surfaces. Square crop for compact brand placements.</span>
          </div>
        </div>
        <div class="panel-head">
          <div>
            <div class="panel-title">Deploy Mission</div>
            <div class="panel-sub">Create one watch, one route, and one threshold from the chamber.</div>
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

    <div class="footer-note">Command chamber is the primary visual surface. CLI and MCP remain first-class control planes.</div>
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
      storyGraph: {{}},
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
      const [detail, graph] = await Promise.all([
        api(`/api/stories/${{identifier}}`),
        api(`/api/stories/${{identifier}}/graph`),
      ]);
      state.storyDetails[identifier] = detail;
      state.storyGraph[identifier] = graph;
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

    function renderStoryGraph(payload) {{
      if (!payload || !Array.isArray(payload.nodes) || !payload.nodes.length) {{
        return `<div class="empty">No entity graph available for this story.</div>`;
      }}
      const storyNode = payload.nodes.find((node) => node.kind === "story") || payload.nodes[0];
      const entityNodes = payload.nodes.filter((node) => node.kind === "entity");
      const positions = {{}};
      positions[storyNode.id] = {{ x: 360, y: 160 }};
      const radius = Math.min(145, 88 + (entityNodes.length * 5));
      entityNodes.forEach((node, index) => {{
        const angle = ((Math.PI * 2) * index) / Math.max(entityNodes.length, 1) - (Math.PI / 2);
        positions[node.id] = {{
          x: 360 + (Math.cos(angle) * radius),
          y: 160 + (Math.sin(angle) * radius),
        }};
      }});

      const lines = (payload.edges || []).map((edge) => {{
        const source = positions[edge.source];
        const target = positions[edge.target];
        if (!source || !target) {{
          return "";
        }}
        const stroke = edge.kind === "entity_relation" ? "rgba(255, 106, 130, 0.78)" : "rgba(127, 228, 255, 0.42)";
        const dash = edge.kind === "entity_relation" ? "0" : "6 6";
        return `<line x1="${{source.x}}" y1="${{source.y}}" x2="${{target.x}}" y2="${{target.y}}" stroke="${{stroke}}" stroke-width="2.5" stroke-dasharray="${{dash}}" />`;
      }}).join("");

      const labels = [storyNode, ...entityNodes].map((node) => {{
        const pos = positions[node.id];
        if (!pos) {{
          return "";
        }}
        const isStory = node.kind === "story";
        const radiusValue = isStory ? 34 : 22 + Math.min(10, (Number(node.in_story_source_count || 0) * 2));
        const fill = isStory ? "#07111d" : "#102031";
        const stroke = isStory ? "rgba(234, 244, 255, 0.76)" : "rgba(127, 228, 255, 0.32)";
        const textFill = "#eaf4ff";
        const label = escapeHtml(node.label || node.id);
        const subtitle = isStory
          ? `${{node.item_count || 0}} items`
          : `${{node.entity_type || "UNKNOWN"}} / ${{node.in_story_source_count || 0}} src`;
        const subtitleY = isStory ? 8 : 6;
        return `
          <g>
            <circle cx="${{pos.x}}" cy="${{pos.y}}" r="${{radiusValue}}" fill="${{fill}}" stroke="${{stroke}}" stroke-width="2.5"></circle>
            <text x="${{pos.x}}" y="${{pos.y - 4}}" text-anchor="middle" font-family="Avenir Next Condensed, Arial Narrow, sans-serif" font-size="${{isStory ? 16 : 13}}" fill="${{textFill}}">
              ${{label.slice(0, isStory ? 22 : 14)}}
            </text>
            <text x="${{pos.x}}" y="${{pos.y + subtitleY}}" text-anchor="middle" font-family="SF Mono, IBM Plex Mono, monospace" font-size="10" fill="${{textFill}}">
              ${{escapeHtml(subtitle)}}
            </text>
          </g>
        `;
      }}).join("");

      const entityList = entityNodes.length
        ? entityNodes.map((node) => `
            <div class="mini-item">${{escapeHtml(node.label)}} | type=${{escapeHtml(node.entity_type || "UNKNOWN")}} | in_story=${{node.in_story_source_count || 0}}</div>
          `).join("")
        : '<div class="empty">No entity node captured.</div>';

      const relationList = (payload.edges || []).filter((edge) => edge.kind === "entity_relation").length
        ? (payload.edges || []).filter((edge) => edge.kind === "entity_relation").map((edge) => `
            <div class="mini-item">${{escapeHtml(edge.source)}} -> ${{escapeHtml(edge.target)}} | ${{escapeHtml(edge.relation_type || "RELATED")}}</div>
          `).join("")
        : '<div class="empty">No direct entity relation captured. Story-level mention edges are still shown above.</div>';

      return `
        <div class="graph-shell">
          <div class="graph-canvas">
            <svg viewBox="0 0 720 320" role="img" aria-label="Story entity graph">
              <rect x="0" y="0" width="720" height="320" fill="transparent"></rect>
              ${{lines}}
              ${{labels}}
            </svg>
          </div>
          <div class="meta">
            <span>nodes=${{payload.nodes.length}}</span>
            <span>edges=${{payload.edge_count || 0}}</span>
            <span>relations=${{payload.relation_count || 0}}</span>
            <span>entities=${{payload.entity_count || 0}}</span>
          </div>
          <div class="graph-meta">
            <div class="mini-list">${{entityList}}</div>
            <div class="mini-list">${{relationList}}</div>
          </div>
        </div>
      `;
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
      const graphPreview = renderStoryGraph(state.storyGraph[selected]);
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
        <div class="stack">
          <div class="mono">entity graph</div>
          ${{graphPreview}}
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
        if (!state.storyGraph[selected]) {{
          state.storyGraph[selected] = await api(`/api/stories/${{selected}}/graph`);
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
