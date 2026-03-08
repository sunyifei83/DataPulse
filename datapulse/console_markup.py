"""HTML surface bundle for the DataPulse command chamber."""

from __future__ import annotations

import json
from typing import Any


def _json_blob(payload: Any) -> str:
    return json.dumps(payload, ensure_ascii=False)


def render_console_html(title: str) -> str:
    initial_state = _json_blob(
        {
            "title": title,
            "sections": ["overview", "missions", "cockpit", "alerts", "routes", "status", "triage", "stories"],
        }
    )
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
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
    button:disabled {{
      opacity: 0.62;
      cursor: wait;
      transform: none;
    }}
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
      transform-style: preserve-3d;
      transition: transform .28s ease, box-shadow .28s ease;
      will-change: transform;
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
      transition: transform .28s ease, filter .28s ease;
      will-change: transform;
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
      transition: transform .28s ease;
      will-change: transform;
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
      transition: transform .28s ease, box-shadow .28s ease;
      will-change: transform;
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
      transition: transform .28s ease;
      will-change: transform;
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
    .stage-hud {{
      position: absolute;
      left: 16px;
      right: 16px;
      top: 16px;
      display: grid;
      gap: 8px;
      padding: 12px 14px;
      border-radius: 18px;
      border: 1px solid rgba(147, 181, 215, 0.22);
      background: linear-gradient(180deg, rgba(8, 14, 24, 0.76), rgba(8, 14, 24, 0.28));
      backdrop-filter: blur(10px);
      box-shadow: inset 0 0 0 1px rgba(127, 228, 255, 0.05);
      z-index: 2;
      pointer-events: none;
    }}
    .stage-hud-title {{
      font-family: var(--headline);
      font-size: 1.1rem;
      letter-spacing: 0.02em;
      text-transform: uppercase;
    }}
    .stage-hud-summary {{
      color: var(--muted);
      font-size: 0.9rem;
      line-height: 1.4;
      max-width: 58ch;
    }}
    .stage-hud-meta {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
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
    .dual-grid {{
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 18px;
      animation: rise .76s ease-out both;
      animation-delay: .12s;
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
    .chip-row {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin-top: 8px;
    }}
    .chip-btn {{
      border: 1px solid var(--line);
      border-radius: 999px;
      padding: 6px 10px;
      background: rgba(127, 228, 255, 0.05);
      color: var(--muted);
      font: 700 11px/1 var(--mono);
      text-transform: uppercase;
      cursor: pointer;
      transition: background 140ms ease, border-color 140ms ease, color 140ms ease;
    }}
    .chip-btn:hover {{
      border-color: rgba(127, 228, 255, 0.32);
      color: var(--text);
    }}
    .chip-btn.active {{
      background: rgba(127, 228, 255, 0.16);
      border-color: rgba(127, 228, 255, 0.36);
      color: var(--accent-2);
    }}
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
    .control-cluster {{
      display: grid;
      gap: 10px;
      padding: 14px;
      border-radius: 18px;
      border: 1px solid rgba(147, 181, 215, 0.14);
      background: rgba(10, 18, 31, 0.44);
    }}
    .compact-stack {{
      gap: 8px;
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
    input, select, textarea {{
      width: 100%;
      border: 1px solid rgba(147, 181, 215, 0.16);
      border-radius: 14px;
      background: rgba(11, 18, 30, 0.86);
      color: var(--ink);
      padding: 13px 14px;
      font: 500 0.96rem/1.2 var(--body);
    }}
    textarea {{
      resize: vertical;
      min-height: 84px;
    }}
    input:focus, select:focus, textarea:focus {{
      outline: none;
      border-color: rgba(127, 228, 255, 0.48);
      box-shadow:
        0 0 0 1px rgba(127, 228, 255, 0.24),
        0 0 0 5px rgba(127, 228, 255, 0.08);
    }}
    .mission-preview.ready {{
      border-color: rgba(127, 228, 255, 0.28);
      box-shadow: inset 0 0 0 1px rgba(127, 228, 255, 0.08);
    }}
    .preview-grid {{
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 12px;
    }}
    .preview-line {{
      border-radius: 14px;
      border: 1px solid var(--line);
      padding: 12px;
      background: rgba(16, 27, 43, 0.64);
    }}
    .preview-label {{
      font: 700 11px/1 var(--mono);
      text-transform: uppercase;
      letter-spacing: 0.08em;
      color: var(--muted);
    }}
    .preview-value {{
      margin-top: 8px;
      font-size: 0.98rem;
      line-height: 1.35;
    }}
    .preview-meter {{
      position: relative;
      height: 10px;
      border-radius: 999px;
      overflow: hidden;
      background: rgba(127, 228, 255, 0.08);
      border: 1px solid rgba(147, 181, 215, 0.16);
    }}
    .preview-meter-fill {{
      height: 100%;
      border-radius: 999px;
      background: linear-gradient(90deg, rgba(127, 228, 255, 0.72), rgba(255, 106, 130, 0.82));
      transition: width .24s ease;
    }}
    .shortcut-strip {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
    }}
    .shortcut-strip .chip {{
      background: rgba(255, 255, 255, 0.04);
    }}
    .toast-rack {{
      position: fixed;
      right: 20px;
      bottom: 22px;
      z-index: 50;
      display: grid;
      gap: 10px;
      width: min(360px, calc(100vw - 32px));
      pointer-events: none;
    }}
    .toast {{
      padding: 14px 16px;
      border-radius: 18px;
      border: 1px solid rgba(147, 181, 215, 0.24);
      background: rgba(9, 15, 28, 0.94);
      color: var(--ink);
      box-shadow: var(--shadow);
      animation: rise .22s ease-out both;
    }}
    .toast.success {{
      border-color: rgba(127, 228, 255, 0.3);
      box-shadow:
        var(--shadow),
        0 0 0 1px rgba(127, 228, 255, 0.08);
    }}
    .toast.error {{
      border-color: rgba(255, 106, 130, 0.3);
      box-shadow:
        var(--shadow),
        0 0 0 1px rgba(255, 106, 130, 0.08);
    }}
    .action-log {{
      display: grid;
      gap: 10px;
    }}
    .action-log-item {{
      display: grid;
      gap: 8px;
      border-radius: 16px;
      border: 1px solid var(--line);
      padding: 12px;
      background: rgba(16, 27, 43, 0.72);
    }}
    .palette-backdrop {{
      position: fixed;
      inset: 0;
      background: rgba(4, 8, 16, 0.72);
      backdrop-filter: blur(10px);
      z-index: 60;
      display: none;
      align-items: start;
      justify-content: center;
      padding: 8vh 16px 16px;
    }}
    .palette-backdrop.open {{
      display: flex;
    }}
    .palette-shell {{
      width: min(760px, 100%);
      border-radius: 24px;
      border: 1px solid rgba(147, 181, 215, 0.24);
      background: rgba(7, 12, 22, 0.96);
      box-shadow: var(--shadow);
      overflow: hidden;
    }}
    .palette-head {{
      padding: 14px;
      border-bottom: 1px solid var(--line);
    }}
    .palette-input {{
      width: 100%;
      border-radius: 16px;
      border: 1px solid rgba(147, 181, 215, 0.18);
      background: rgba(11, 18, 30, 0.92);
      color: var(--ink);
      padding: 14px 16px;
      font: 500 1rem/1.2 var(--body);
    }}
    .palette-list {{
      display: grid;
      gap: 0;
      max-height: 56vh;
      overflow: auto;
    }}
    .palette-item {{
      display: grid;
      gap: 6px;
      padding: 14px 16px;
      border-bottom: 1px solid rgba(147, 181, 215, 0.1);
      cursor: pointer;
      transition: background .14s ease;
    }}
    .palette-item.active {{
      background: rgba(127, 228, 255, 0.12);
    }}
    .palette-item:hover {{
      background: rgba(127, 228, 255, 0.08);
    }}
    .palette-kicker {{
      font: 700 11px/1 var(--mono);
      text-transform: uppercase;
      letter-spacing: 0.08em;
      color: var(--muted);
    }}
    .suggestion-grid {{
      display: grid;
      gap: 12px;
    }}
    .suggestion-list {{
      display: grid;
      gap: 8px;
    }}
    .skeleton {{
      position: relative;
      overflow: hidden;
    }}
    .skeleton::after {{
      content: "";
      position: absolute;
      inset: 0;
      transform: translateX(-100%);
      background: linear-gradient(90deg, transparent, rgba(255,255,255,0.08), transparent);
      animation: shimmer 1.2s infinite;
    }}
    .skeleton-block {{
      height: 14px;
      border-radius: 999px;
      background: rgba(147, 181, 215, 0.12);
    }}
    .skeleton-block.short {{ width: 34%; }}
    .skeleton-block.medium {{ width: 58%; }}
    .skeleton-block.long {{ width: 84%; }}
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
    .card.selectable {{
      cursor: pointer;
      transition: transform .18s ease, border-color .18s ease, box-shadow .18s ease;
    }}
    .card.selectable:hover {{
      transform: translateY(-1px);
      border-color: rgba(127, 228, 255, 0.24);
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
    .timeline-strip {{
      display: grid;
      grid-auto-flow: column;
      grid-auto-columns: minmax(180px, 220px);
      gap: 10px;
      overflow-x: auto;
      padding-bottom: 6px;
    }}
    .timeline-event {{
      border-radius: 16px;
      border: 1px solid var(--line);
      padding: 12px;
      background: rgba(16, 27, 43, 0.78);
      display: grid;
      gap: 8px;
    }}
    .timeline-event.ok {{
      border-color: rgba(127, 228, 255, 0.28);
    }}
    .timeline-event.hot {{
      border-color: rgba(255, 106, 130, 0.28);
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
    @keyframes shimmer {{
      to {{ transform: translateX(100%); }}
    }}
    @media (max-width: 1100px) {{
      .hero, .grid, .dual-grid {{ grid-template-columns: 1fr; }}
      .story-grid, .story-columns {{ grid-template-columns: 1fr; }}
      .preview-grid {{ grid-template-columns: 1fr; }}
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
      <div class="hero-main" id="hero-main">
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
          <div class="stage-hud" id="stage-hud"></div>
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
            <div class="panel-sub">Create one watch and optionally attach one alert route, keyword, domain, or threshold.</div>
          </div>
        </div>
        <div class="control-cluster">
          <div class="mono">Mission Modes</div>
          <div class="panel-sub">Load an archetype, then steer schedule, platform, and alert gating without rebuilding the payload from zero.</div>
          <div class="chip-row" id="create-watch-presets"></div>
        </div>
        <form id="create-watch-form">
          <div class="field-grid">
            <label>Name<input name="name" placeholder="Launch Ops" required></label>
            <label>Schedule<input name="schedule" placeholder="@hourly / interval:15m"></label>
          </div>
          <label>Query<input name="query" placeholder="OpenAI launch" required></label>
          <div class="stack compact-stack">
            <div class="mono">Schedule Lanes</div>
            <div class="chip-row" id="create-watch-schedule-picks"></div>
          </div>
          <div class="field-grid">
            <label>Platform<input name="platform" placeholder="twitter"></label>
            <label>Alert Domain<input name="domain" placeholder="openai.com"></label>
          </div>
          <div class="stack compact-stack">
            <div class="mono">Platform Lanes</div>
            <div class="chip-row" id="create-watch-platform-picks"></div>
          </div>
          <div class="field-grid">
            <label>Alert Route<input name="route" placeholder="ops-webhook"></label>
            <label>Alert Keyword<input name="keyword" placeholder="launch"></label>
          </div>
          <div class="stack compact-stack">
            <div class="mono">Route Snap</div>
            <div class="chip-row" id="create-watch-route-picks"></div>
          </div>
          <div class="field-grid">
            <label>Min Score<input name="min_score" placeholder="70" type="number"></label>
            <label>Min Confidence<input name="min_confidence" placeholder="0.8" step="0.01" type="number"></label>
          </div>
          <div class="toolbar">
            <button class="btn-primary" type="submit">Create Watch</button>
            <button class="btn-secondary" id="create-watch-clear" type="button">Reset Draft</button>
          </div>
          <div class="panel-sub" id="create-watch-feedback">Required fields: `Name` and `Query`. Use `/` to focus the mission deck.</div>
        </form>
        <div class="card mission-preview" id="create-watch-preview"></div>
        <div class="card" id="create-watch-suggestions"></div>
        <div class="control-cluster">
          <div class="mono">Clone Existing Mission</div>
          <div class="panel-sub">Pull any existing mission into the deck, then fork its routing or thresholds instead of starting cold.</div>
          <div class="chip-row" id="create-watch-clones"></div>
        </div>
        <div class="shortcut-strip">
          <span class="chip">/ focus deck</span>
          <span class="chip">1-4 load preset</span>
          <span class="chip">Cmd/Ctrl+Enter deploy</span>
        </div>
        <div class="control-cluster">
          <div class="mono">Recent Actions</div>
          <div class="panel-sub">Track the last few mutations and undo the reversible ones before they disappear into the wider board refresh.</div>
          <div class="action-log" id="console-action-history"></div>
        </div>
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
            <div class="panel-sub">Collector health, watch metrics, route delivery, and latest scheduler failures.</div>
          </div>
        </div>
        <div class="status-shell" id="status-card"></div>
      </article>
    </section>

    <section class="dual-grid">
      <article class="panel">
        <div class="panel-head">
          <div>
            <h2 class="panel-title">Mission Cockpit</h2>
            <div class="panel-sub">Inspect one mission, recent runs, result stream, next schedule, and recent alert outcomes.</div>
          </div>
        </div>
        <div class="stack" id="watch-detail"></div>
      </article>

      <article class="panel">
        <div class="panel-head">
          <div>
            <h2 class="panel-title">Distribution Health</h2>
            <div class="panel-sub">Track named route delivery quality and surface degraded sinks before they become silent failures.</div>
          </div>
        </div>
        <div class="stack" id="route-health"></div>
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
  <div class="toast-rack" id="toast-rack" aria-live="polite" aria-atomic="false"></div>
  <div class="palette-backdrop" id="command-palette">
    <div class="palette-shell">
      <div class="palette-head">
        <input class="palette-input" id="command-palette-input" type="text" placeholder="Search actions, missions, stories, or routes">
      </div>
      <div class="palette-list" id="command-palette-list"></div>
    </div>
  </div>

    <script>
    const initial = {initial_state};
    const state = {{
      watches: [],
      watchDetails: {{}},
      watchResultFilters: {{}},
      selectedWatchId: "",
      alerts: [],
      routes: [],
      routeHealth: [],
      status: null,
      ops: null,
      overview: null,
      triage: [],
      triageStats: null,
      triageFilter: "open",
      selectedTriageId: "",
      triageExplain: {{}},
      triageNoteDrafts: {{}},
      stories: [],
      storyDetails: {{}},
      storyGraph: {{}},
      storyMarkdown: {{}},
      selectedStoryId: "",
      createWatchDraft: null,
      createWatchPresetId: "",
      createWatchSuggestions: null,
      createWatchSuggestionTimer: 0,
      actionLog: [],
      loading: {{
        board: false,
        watchDetail: false,
        storyDetail: false,
        suggestions: false,
      }},
      commandPalette: {{
        open: false,
        query: "",
        selectedIndex: 0,
      }},
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

    const createWatchStorageKey = "datapulse.console.create-watch-draft.v2";
    const createWatchFormFields = ["name", "schedule", "query", "platform", "domain", "route", "keyword", "min_score", "min_confidence"];
    const createWatchPresets = [
      {{
        id: "launch",
        label: "Launch Pulse",
        description: "Tight interval for product or company launches.",
        values: {{
          name: "Launch Pulse",
          schedule: "interval:15m",
          query: "OpenAI launch",
          platform: "twitter",
          domain: "",
          route: "",
          keyword: "launch",
          min_score: "70",
          min_confidence: "0.75",
        }},
      }},
      {{
        id: "risk",
        label: "Risk Sweep",
        description: "Higher confidence gate for operational risk review.",
        values: {{
          name: "Risk Sweep",
          schedule: "@hourly",
          query: "service outage rumor",
          platform: "web",
          domain: "",
          route: "",
          keyword: "outage",
          min_score: "80",
          min_confidence: "0.88",
        }},
      }},
      {{
        id: "market",
        label: "Market Shift",
        description: "Cross-signal watch for moves around listed names.",
        values: {{
          name: "Market Shift",
          schedule: "@hourly",
          query: "Xiaomi earnings",
          platform: "news",
          domain: "",
          route: "",
          keyword: "earnings",
          min_score: "68",
          min_confidence: "0.8",
        }},
      }},
      {{
        id: "creator",
        label: "Creator Surge",
        description: "Faster scan for creator and social breakout chatter.",
        values: {{
          name: "Creator Surge",
          schedule: "interval:30m",
          query: "viral creator trend",
          platform: "reddit",
          domain: "",
          route: "",
          keyword: "viral",
          min_score: "55",
          min_confidence: "0.65",
        }},
      }},
    ];
    const scheduleLaneOptions = [
      {{ label: "manual", value: "manual" }},
      {{ label: "15m", value: "interval:15m" }},
      {{ label: "30m", value: "interval:30m" }},
      {{ label: "hourly", value: "@hourly" }},
    ];
    const platformLaneOptions = [
      {{ label: "twitter", value: "twitter" }},
      {{ label: "reddit", value: "reddit" }},
      {{ label: "news", value: "news" }},
      {{ label: "web", value: "web" }},
    ];

    function defaultCreateWatchDraft() {{
      return {{
        name: "",
        schedule: "",
        query: "",
        platform: "",
        domain: "",
        route: "",
        keyword: "",
        min_score: "",
        min_confidence: "",
      }};
    }}

    function normalizeCreateWatchDraft(payload = {{}}) {{
      const draft = defaultCreateWatchDraft();
      createWatchFormFields.forEach((field) => {{
        draft[field] = String(payload[field] ?? "");
      }});
      return draft;
    }}

    function safeLocalStorageGet(key) {{
      try {{
        return window.localStorage.getItem(key);
      }} catch (error) {{
        return null;
      }}
    }}

    function safeLocalStorageSet(key, value) {{
      try {{
        window.localStorage.setItem(key, value);
      }} catch (error) {{
        console.warn("localStorage write skipped", error);
      }}
    }}

    function safeLocalStorageRemove(key) {{
      try {{
        window.localStorage.removeItem(key);
      }} catch (error) {{
        console.warn("localStorage remove skipped", error);
      }}
    }}

    function loadCreateWatchDraft() {{
      const raw = safeLocalStorageGet(createWatchStorageKey);
      if (!raw) {{
        return defaultCreateWatchDraft();
      }}
      try {{
        return normalizeCreateWatchDraft(JSON.parse(raw));
      }} catch (error) {{
        safeLocalStorageRemove(createWatchStorageKey);
        return defaultCreateWatchDraft();
      }}
    }}

    function persistCreateWatchDraft() {{
      const draft = normalizeCreateWatchDraft(state.createWatchDraft || defaultCreateWatchDraft());
      const hasSignal = createWatchFormFields.some((field) => String(draft[field] || "").trim());
      if (!hasSignal) {{
        safeLocalStorageRemove(createWatchStorageKey);
        return;
      }}
      safeLocalStorageSet(createWatchStorageKey, JSON.stringify(draft));
    }}

    function showToast(message, tone = "info") {{
      const rack = $("toast-rack");
      if (!rack) {{
        return;
      }}
      const toast = document.createElement("div");
      toast.className = `toast ${{tone}}`;
      toast.innerHTML = `
        <div class="mono">mission signal / ${{tone}}</div>
        <div style="margin-top:6px;">${{escapeHtml(message)}}</div>
      `;
      rack.appendChild(toast);
      window.setTimeout(() => {{
        toast.style.opacity = "0";
        toast.style.transform = "translateY(8px)";
        toast.style.transition = "opacity .18s ease, transform .18s ease";
        window.setTimeout(() => toast.remove(), 220);
      }}, 2800);
    }}

    window.alert = (message) => showToast(String(message || ""), "error");

    function reportError(error, prefix = "") {{
      console.error(error);
      const message = error && error.message ? error.message : String(error || "Unknown error");
      showToast(prefix ? `${{prefix}}: ${{message}}` : message, "error");
    }}

    function focusCreateWatchDeck(fieldName = "query") {{
      const form = $("create-watch-form");
      if (!form) {{
        return;
      }}
      form.scrollIntoView({{ block: "nearest", behavior: "smooth" }});
      const field = form.elements.namedItem(fieldName);
      if (field && typeof field.focus === "function") {{
        field.focus();
        if (typeof field.select === "function") {{
          field.select();
        }}
      }}
    }}

    function scheduleModeLabel(value) {{
      const schedule = String(value || "").trim();
      if (!schedule || schedule === "manual") {{
        return "manual dispatch";
      }}
      if (schedule.startsWith("interval:")) {{
        return `cadence ${{schedule.replace("interval:", "")}}`;
      }}
      if (schedule.startsWith("@")) {{
        return `cron alias ${{schedule}}`;
      }}
      return schedule;
    }}

    function buildCreateWatchPreview(draftInput) {{
      const draft = normalizeCreateWatchDraft(draftInput || defaultCreateWatchDraft());
      const requiredReady = Boolean(draft.name.trim() && draft.query.trim());
      const alertArmed = Boolean(
        draft.route.trim() ||
        draft.keyword.trim() ||
        draft.domain.trim() ||
        Number(draft.min_score || 0) > 0 ||
        Number(draft.min_confidence || 0) > 0,
      );
      const readiness = Math.min(
        100,
        (draft.name.trim() ? 34 : 0) +
        (draft.query.trim() ? 34 : 0) +
        (draft.schedule.trim() ? 8 : 0) +
        (draft.platform.trim() ? 8 : 0) +
        ((draft.route.trim() || draft.keyword.trim() || draft.domain.trim()) ? 8 : 0) +
        ((draft.min_score.trim() || draft.min_confidence.trim()) ? 8 : 0),
      );
      const filters = [draft.platform.trim(), draft.domain.trim(), draft.keyword.trim()].filter(Boolean);
      return {{
        draft,
        requiredReady,
        alertArmed,
        readiness,
        summary: draft.query.trim()
          ? `Track ${{draft.query.trim()}} with ${{scheduleModeLabel(draft.schedule)}} across ${{draft.platform.trim() || "cross-platform"}} surfaces.`
          : "Wire a query to project the mission into the chamber HUD and preview lane.",
        scoreLabel: draft.min_score.trim() ? `score >= ${{draft.min_score.trim()}}` : "score gate unset",
        confidenceLabel: draft.min_confidence.trim() ? `confidence >= ${{draft.min_confidence.trim()}}` : "confidence gate unset",
        filtersLabel: filters.length ? filters.join(" / ") : "no scope filter",
        routeLabel: draft.route.trim() || "route not attached",
        scheduleLabel: scheduleModeLabel(draft.schedule),
      }};
    }}

    function syncCreateWatchForm() {{
      const form = $("create-watch-form");
      const draft = normalizeCreateWatchDraft(state.createWatchDraft || defaultCreateWatchDraft());
      if (!form) {{
        return;
      }}
      createWatchFormFields.forEach((fieldName) => {{
        const field = form.elements.namedItem(fieldName);
        if (!field || field.value === draft[fieldName]) {{
          return;
        }}
        field.value = draft[fieldName];
      }});
    }}

    function collectCreateWatchDraft(form) {{
      if (!form) {{
        return defaultCreateWatchDraft();
      }}
      const next = defaultCreateWatchDraft();
      createWatchFormFields.forEach((fieldName) => {{
        const field = form.elements.namedItem(fieldName);
        next[fieldName] = field ? String(field.value ?? "") : "";
      }});
      return normalizeCreateWatchDraft(next);
    }}

    function setCreateWatchDraft(nextDraft, presetId = "") {{
      state.createWatchDraft = normalizeCreateWatchDraft(nextDraft || defaultCreateWatchDraft());
      state.createWatchPresetId = presetId;
      syncCreateWatchForm();
      persistCreateWatchDraft();
      renderCreateWatchDeck();
      queueCreateWatchSuggestions();
    }}

    function updateCreateWatchDraft(patch = {{}}, presetId = "") {{
      setCreateWatchDraft({{
        ...normalizeCreateWatchDraft(state.createWatchDraft || defaultCreateWatchDraft()),
        ...patch,
      }}, presetId);
    }}

    async function refreshCreateWatchSuggestions(force = false) {{
      const draft = normalizeCreateWatchDraft(state.createWatchDraft || defaultCreateWatchDraft());
      if (!force && !(draft.name.trim() || draft.query.trim() || draft.keyword.trim())) {{
        state.createWatchSuggestions = null;
        renderCreateWatchDeck();
        return;
      }}
      state.loading.suggestions = true;
      renderCreateWatchDeck();
      try {{
        state.createWatchSuggestions = await api("/api/console/deck/suggestions", {{
          method: "POST",
          headers: jsonHeaders,
          body: JSON.stringify(draft),
        }});
      }} catch (error) {{
        state.createWatchSuggestions = null;
        reportError(error, "Load mission suggestions");
      }} finally {{
        state.loading.suggestions = false;
        renderCreateWatchDeck();
      }}
    }}

    function queueCreateWatchSuggestions(force = false) {{
      if (state.createWatchSuggestionTimer) {{
        window.clearTimeout(state.createWatchSuggestionTimer);
      }}
      state.createWatchSuggestionTimer = window.setTimeout(() => {{
        refreshCreateWatchSuggestions(force).catch((error) => reportError(error, "Load mission suggestions"));
      }}, force ? 20 : 220);
    }}

    function renderCreateWatchDeck() {{
      const draft = normalizeCreateWatchDraft(state.createWatchDraft || defaultCreateWatchDraft());
      const preview = buildCreateWatchPreview(draft);
      const presetRoot = $("create-watch-presets");
      const scheduleRoot = $("create-watch-schedule-picks");
      const platformRoot = $("create-watch-platform-picks");
      const routeRoot = $("create-watch-route-picks");
      const cloneRoot = $("create-watch-clones");
      const previewRoot = $("create-watch-preview");
      const suggestionRoot = $("create-watch-suggestions");
      const feedbackRoot = $("create-watch-feedback");
      const stageHudRoot = $("stage-hud");

      if (presetRoot) {{
        presetRoot.innerHTML = createWatchPresets.map((preset, index) => `
          <button
            class="chip-btn ${{state.createWatchPresetId === preset.id ? "active" : ""}}"
            type="button"
            data-create-watch-preset="${{preset.id}}"
            title="${{escapeHtml(preset.description)}}"
          >${{index + 1}}. ${{escapeHtml(preset.label)}}</button>
        `).join("");
      }}

      if (scheduleRoot) {{
        scheduleRoot.innerHTML = scheduleLaneOptions.map((option) => `
          <button
            class="chip-btn ${{draft.schedule.trim() === option.value ? "active" : ""}}"
            type="button"
            data-create-watch-schedule="${{option.value}}"
          >${{escapeHtml(option.label)}}</button>
        `).join("");
      }}

      if (platformRoot) {{
        platformRoot.innerHTML = platformLaneOptions.map((option) => `
          <button
            class="chip-btn ${{draft.platform.trim() === option.value ? "active" : ""}}"
            type="button"
            data-create-watch-platform="${{option.value}}"
          >${{escapeHtml(option.label)}}</button>
        `).join("");
      }}

      if (routeRoot) {{
        const routeButtons = state.routes.length
          ? state.routes.slice(0, 6).map((route) => `
              <button
                class="chip-btn ${{draft.route.trim() === String(route.name || "").trim() ? "active" : ""}}"
                type="button"
                data-create-watch-route="${{escapeHtml(route.name || "")}}"
              >${{escapeHtml(route.name || "unnamed-route")}}</button>
            `).join("")
          : `<span class="chip">No named routes</span>`;
        routeRoot.innerHTML = routeButtons;
      }}

      if (cloneRoot) {{
        const cloneButtons = state.watches.length
          ? state.watches.slice(0, 6).map((watch) => `
              <button class="chip-btn" type="button" data-create-watch-clone="${{escapeHtml(watch.id)}}">${{escapeHtml(watch.name || watch.id)}}</button>
            `).join("")
          : `<span class="chip">No mission to clone</span>`;
        cloneRoot.innerHTML = cloneButtons;
      }}

      if (previewRoot) {{
        previewRoot.className = `card mission-preview ${{preview.requiredReady ? "ready" : ""}}`;
        previewRoot.innerHTML = `
          <div class="card-top">
            <div>
              <div class="mono">mission brief</div>
              <h3 class="card-title" style="margin-top:10px;">${{escapeHtml(draft.name.trim() || "Unnamed Mission")}}</h3>
            </div>
            <span class="chip ${{preview.requiredReady ? "ok" : "hot"}}">${{preview.requiredReady ? "ready" : "needs query/name"}}</span>
          </div>
          <div class="panel-sub">${{escapeHtml(preview.summary)}}</div>
          <div class="preview-meter">
            <div class="preview-meter-fill" style="width:${{preview.readiness}}%;"></div>
          </div>
          <div class="meta">
            <span>readiness=${{preview.readiness}}%</span>
            <span>alert=${{preview.alertArmed ? "armed" : "passive"}}</span>
            <span>schedule=${{escapeHtml(preview.scheduleLabel)}}</span>
          </div>
          <div class="preview-grid">
            <div class="preview-line">
              <div class="preview-label">Scope</div>
              <div class="preview-value">${{escapeHtml(preview.filtersLabel)}}</div>
            </div>
            <div class="preview-line">
              <div class="preview-label">Route</div>
              <div class="preview-value">${{escapeHtml(preview.routeLabel)}}</div>
            </div>
            <div class="preview-line">
              <div class="preview-label">Score Gate</div>
              <div class="preview-value">${{escapeHtml(preview.scoreLabel)}}</div>
            </div>
            <div class="preview-line">
              <div class="preview-label">Confidence Gate</div>
              <div class="preview-value">${{escapeHtml(preview.confidenceLabel)}}</div>
            </div>
          </div>
        `;
      }}

      if (suggestionRoot) {{
        if (state.loading.suggestions) {{
          suggestionRoot.innerHTML = `
            <div class="mono">mission suggestions</div>
            <div class="panel-sub">Deriving route, cadence, and duplicate signals from the current repository state.</div>
            <div class="stack" style="margin-top:12px;">${{skeletonCard(4)}}</div>
          `;
        }} else if (!state.createWatchSuggestions) {{
          suggestionRoot.innerHTML = `
            <div class="mono">mission suggestions</div>
            <div class="panel-sub">Start typing a mission draft and the deck will derive cadence, route, and duplicate pressure from current watches and stories.</div>
          `;
        }} else {{
          const suggestions = state.createWatchSuggestions;
          const warningBlock = Array.isArray(suggestions.warnings) && suggestions.warnings.length
            ? `<div class="suggestion-list">${{suggestions.warnings.map((item) => `<div class="mini-item">${{escapeHtml(item)}}</div>`).join("")}}</div>`
            : `<div class="panel-sub">No active conflict or delivery warning for this draft.</div>`;
          const similarWatches = Array.isArray(suggestions.similar_watches) ? suggestions.similar_watches : [];
          const relatedStories = Array.isArray(suggestions.related_stories) ? suggestions.related_stories : [];
          suggestionRoot.innerHTML = `
            <div class="card-top">
              <div>
                <div class="mono">mission suggestions</div>
                <div class="panel-sub" style="margin-top:8px;">${{escapeHtml(suggestions.summary || "")}}</div>
              </div>
              <button class="btn-secondary" id="apply-all-suggestions" type="button">Apply All</button>
            </div>
            <div class="suggestion-grid">
              <div class="preview-grid">
                <div class="preview-line">
                  <div class="preview-label">Cadence</div>
                  <div class="preview-value">${{escapeHtml(suggestions.recommended_schedule || "-")}}</div>
                  <div class="panel-sub">${{escapeHtml(suggestions.schedule_reason || "")}}</div>
                </div>
                <div class="preview-line">
                  <div class="preview-label">Platform</div>
                  <div class="preview-value">${{escapeHtml(suggestions.recommended_platform || "-")}}</div>
                  <div class="panel-sub">${{escapeHtml(suggestions.platform_reason || "")}}</div>
                </div>
                <div class="preview-line">
                  <div class="preview-label">Route</div>
                  <div class="preview-value">${{escapeHtml(suggestions.recommended_route || "-")}}</div>
                  <div class="panel-sub">${{escapeHtml(suggestions.route_reason || "")}}</div>
                </div>
                <div class="preview-line">
                  <div class="preview-label">Scope Hints</div>
                  <div class="preview-value">${{escapeHtml(suggestions.recommended_keyword || "-")}} / ${{escapeHtml(suggestions.recommended_domain || "-")}}</div>
                  <div class="panel-sub">${{escapeHtml(suggestions.keyword_reason || suggestions.domain_reason || "")}}</div>
                </div>
              </div>
              <div class="chip-row">
                <button class="chip-btn" type="button" data-suggestion-apply="schedule">${{escapeHtml(suggestions.recommended_schedule || "schedule")}}</button>
                <button class="chip-btn" type="button" data-suggestion-apply="platform">${{escapeHtml(suggestions.recommended_platform || "platform")}}</button>
                <button class="chip-btn" type="button" data-suggestion-apply="route">${{escapeHtml(suggestions.recommended_route || "route")}}</button>
                <button class="chip-btn" type="button" data-suggestion-apply="keyword">${{escapeHtml(suggestions.recommended_keyword || "keyword")}}</button>
                <button class="chip-btn" type="button" data-suggestion-apply="thresholds">score/confidence</button>
              </div>
              <div class="stack">
                <div class="mono">Warnings</div>
                ${{warningBlock}}
              </div>
              <div class="preview-grid">
                <div class="stack">
                  <div class="mono">Similar Missions</div>
                  ${{similarWatches.length ? similarWatches.map((item) => `<div class="mini-item">${{escapeHtml(item.name)}} | similarity=${{Number(item.similarity || 0).toFixed(2)}} | ${{escapeHtml(item.schedule || "manual")}}</div>`).join("") : '<div class="panel-sub">No mission conflict found.</div>'}}
                </div>
                <div class="stack">
                  <div class="mono">Related Stories</div>
                  ${{relatedStories.length ? relatedStories.map((item) => `<div class="mini-item">${{escapeHtml(item.title)}} | similarity=${{Number(item.similarity || 0).toFixed(2)}} | items=${{item.item_count || 0}}</div>`).join("") : '<div class="panel-sub">No story cluster overlap found.</div>'}}
                </div>
              </div>
            </div>
          `;
          suggestionRoot.querySelector("#apply-all-suggestions")?.addEventListener("click", () => {{
            const patch = suggestions.autofill_patch || {{}};
            updateCreateWatchDraft(patch);
            showToast("Applied suggested mission defaults", "success");
          }});
          suggestionRoot.querySelectorAll("[data-suggestion-apply]").forEach((button) => {{
            button.addEventListener("click", () => {{
              const patch = suggestions.autofill_patch || {{}};
              const field = String(button.dataset.suggestionApply || "").trim();
              if (field === "thresholds") {{
                updateCreateWatchDraft({{
                  min_score: String(patch.min_score || ""),
                  min_confidence: String(patch.min_confidence || ""),
                }});
                return;
              }}
              if (!field || !(field in patch)) {{
                return;
              }}
              updateCreateWatchDraft({{ [field]: String(patch[field] || "") }});
            }});
          }});
        }}
      }}

      if (feedbackRoot) {{
        feedbackRoot.textContent = preview.requiredReady
          ? `Deck armed. Use Cmd/Ctrl+Enter to dispatch${{preview.alertArmed ? " with alert gating." : "."}}`
          : "Required fields: Name and Query. Use / to focus the mission deck.";
      }}

      if (stageHudRoot) {{
        stageHudRoot.innerHTML = `
          <div class="card-top">
            <div>
              <div class="mono">Live Mission Projection</div>
              <div class="stage-hud-title">${{escapeHtml(draft.name.trim() || draft.query.trim() || "Awaiting Mission Draft")}}</div>
            </div>
            <span class="chip ${{preview.requiredReady ? "ok" : ""}}">${{preview.requiredReady ? "synced" : "draft"}}</span>
          </div>
          <div class="stage-hud-summary">${{escapeHtml(preview.summary)}}</div>
          <div class="stage-hud-meta">
            <span class="chip">${{escapeHtml(preview.scheduleLabel)}}</span>
            <span class="chip">${{escapeHtml(preview.filtersLabel)}}</span>
            <span class="chip ${{preview.alertArmed ? "hot" : ""}}">${{preview.alertArmed ? "alert armed" : "passive watch"}}</span>
          </div>
        `;
      }}
      renderActionHistory();
    }}

    async function cloneMissionIntoCreateWatch(identifier) {{
      if (!identifier) {{
        return;
      }}
      const detail = state.watchDetails[identifier] || await api(`/api/watches/${{identifier}}`);
      state.watchDetails[identifier] = detail;
      const firstRule = Array.isArray(detail.alert_rules) && detail.alert_rules.length ? detail.alert_rules[0] : {{}};
      setCreateWatchDraft({{
        name: detail.name ? `${{detail.name}} copy` : "",
        schedule: detail.schedule || "",
        query: detail.query || "",
        platform: Array.isArray(detail.platforms) && detail.platforms.length ? detail.platforms[0] : "",
        domain: Array.isArray(firstRule.domains) && firstRule.domains.length ? firstRule.domains[0] : "",
        route: Array.isArray(firstRule.routes) && firstRule.routes.length ? firstRule.routes[0] : "",
        keyword: Array.isArray(firstRule.keyword_any) && firstRule.keyword_any.length ? firstRule.keyword_any[0] : "",
        min_score: firstRule.min_score ? String(firstRule.min_score) : "",
        min_confidence: firstRule.min_confidence ? String(firstRule.min_confidence) : "",
      }});
      showToast(`Mission deck cloned from ${{detail.name || identifier}}`, "success");
      focusCreateWatchDeck("name");
    }}

    function bindCreateWatchDeck() {{
      const form = $("create-watch-form");
      const presetRoot = $("create-watch-presets");
      const scheduleRoot = $("create-watch-schedule-picks");
      const platformRoot = $("create-watch-platform-picks");
      const routeRoot = $("create-watch-route-picks");
      const cloneRoot = $("create-watch-clones");
      const clearButton = $("create-watch-clear");
      if (!form) {{
        return;
      }}

      syncCreateWatchForm();
      renderCreateWatchDeck();
      queueCreateWatchSuggestions(true);

      form.addEventListener("input", () => {{
        state.createWatchPresetId = "";
        state.createWatchDraft = collectCreateWatchDraft(form);
        persistCreateWatchDraft();
        renderCreateWatchDeck();
        queueCreateWatchSuggestions();
      }});

      form.addEventListener("keydown", (event) => {{
        if ((event.metaKey || event.ctrlKey) && String(event.key || "").toLowerCase() === "enter") {{
          event.preventDefault();
          form.requestSubmit();
        }}
      }});

      presetRoot?.addEventListener("click", (event) => {{
        const button = event.target.closest("[data-create-watch-preset]");
        if (!button) {{
          return;
        }}
        const preset = createWatchPresets.find((candidate) => candidate.id === button.dataset.createWatchPreset);
        if (!preset) {{
          return;
        }}
        setCreateWatchDraft(preset.values, preset.id);
        showToast(`${{preset.label}} loaded into the mission deck`, "success");
        focusCreateWatchDeck("query");
      }});

      scheduleRoot?.addEventListener("click", (event) => {{
        const button = event.target.closest("[data-create-watch-schedule]");
        if (!button) {{
          return;
        }}
        updateCreateWatchDraft({{ schedule: String(button.dataset.createWatchSchedule || "") }});
      }});

      platformRoot?.addEventListener("click", (event) => {{
        const button = event.target.closest("[data-create-watch-platform]");
        if (!button) {{
          return;
        }}
        updateCreateWatchDraft({{ platform: String(button.dataset.createWatchPlatform || "") }});
      }});

      routeRoot?.addEventListener("click", (event) => {{
        const button = event.target.closest("[data-create-watch-route]");
        if (!button) {{
          return;
        }}
        updateCreateWatchDraft({{ route: String(button.dataset.createWatchRoute || "") }});
      }});

      cloneRoot?.addEventListener("click", async (event) => {{
        const button = event.target.closest("[data-create-watch-clone]");
        if (!button) {{
          return;
        }}
        button.disabled = true;
        try {{
          await cloneMissionIntoCreateWatch(String(button.dataset.createWatchClone || ""));
        }} catch (error) {{
          reportError(error, "Clone mission");
        }} finally {{
          button.disabled = false;
        }}
      }});

      clearButton?.addEventListener("click", () => {{
        setCreateWatchDraft(defaultCreateWatchDraft());
        showToast("Mission deck draft cleared", "success");
        focusCreateWatchDeck("name");
      }});
    }}

    function bindHeroStageMotion() {{
      const hero = $("hero-main");
      const stage = hero?.querySelector(".hero-stage");
      const visual = hero?.querySelector(".hero-visual");
      const globe = hero?.querySelector(".stage-globe");
      const leftRing = hero?.querySelector(".stage-ring-left");
      const rightRing = hero?.querySelector(".stage-ring-right");
      const leftConsole = hero?.querySelector(".stage-console-left");
      const rightConsole = hero?.querySelector(".stage-console-right");
      if (!hero || !stage || !visual || !globe || !leftRing || !rightRing || !leftConsole || !rightConsole) {{
        return;
      }}

      const reset = () => {{
        stage.style.transform = "";
        visual.style.transform = "";
        globe.style.transform = "translateX(-50%)";
        leftRing.style.transform = "";
        rightRing.style.transform = "";
        leftConsole.style.transform = "";
        rightConsole.style.transform = "";
      }};

      hero.addEventListener("pointermove", (event) => {{
        const rect = hero.getBoundingClientRect();
        const x = ((event.clientX - rect.left) / rect.width) - 0.5;
        const y = ((event.clientY - rect.top) / rect.height) - 0.5;
        stage.style.transform = `perspective(1200px) rotateX(${{-y * 6}}deg) rotateY(${{x * 7}}deg)`;
        visual.style.transform = `scale(1.05) translate(${{x * -16}}px, ${{y * -12}}px)`;
        globe.style.transform = `translate(calc(-50% + ${{x * 20}}px), ${{y * 12}}px)`;
        leftRing.style.transform = `translateX(${{x * -10}}px)`;
        rightRing.style.transform = `translateX(${{x * 10}}px)`;
        leftConsole.style.transform = `translate(${{x * -8}}px, ${{y * 6}}px)`;
        rightConsole.style.transform = `translate(${{x * 8}}px, ${{y * 6}}px)`;
      }});

      hero.addEventListener("pointerleave", reset);
      reset();
    }}

    function buildCommandPaletteEntries() {{
      const entries = [
        {{
          id: "refresh",
          group: "system",
          title: "Refresh Chamber",
          subtitle: "Reload overview, missions, triage, stories, and ops.",
          run: async () => {{
            await refreshBoard();
            showToast("Command chamber refreshed", "success");
          }},
        }},
        {{
          id: "run-due",
          group: "system",
          title: "Run Due Missions",
          subtitle: "Dispatch every mission currently due.",
          run: async () => {{
            await api("/api/watches/run-due", {{ method: "POST", headers: jsonHeaders, body: JSON.stringify({{ limit: 0 }}) }});
            await refreshBoard();
            showToast("Due missions dispatched", "success");
          }},
        }},
        {{
          id: "focus-deck",
          group: "deck",
          title: "Focus Mission Deck",
          subtitle: "Jump to the draft deck and focus the main field.",
          run: async () => {{
            focusCreateWatchDeck((state.createWatchDraft && state.createWatchDraft.name.trim()) ? "query" : "name");
          }},
        }},
        {{
          id: "clear-deck",
          group: "deck",
          title: "Reset Mission Deck",
          subtitle: "Clear the current draft and its stored local state.",
          run: async () => {{
            setCreateWatchDraft(defaultCreateWatchDraft());
            showToast("Mission deck draft cleared", "success");
          }},
        }},
      ];
      if (state.actionLog.length && state.actionLog[0].undo) {{
        const latestAction = state.actionLog[0];
        entries.unshift({{
          id: `undo-${{latestAction.id}}`,
          group: "actions",
          title: `Undo: ${{latestAction.label}}`,
          subtitle: latestAction.detail || "Reverse the latest reversible action.",
          run: async () => {{
            await latestAction.undo();
            state.actionLog = state.actionLog.filter((entry) => entry.id !== latestAction.id);
            renderActionHistory();
          }},
        }});
      }}
      state.watches.slice(0, 6).forEach((watch) => {{
        entries.push({{
          id: `watch-open-${{watch.id}}`,
          group: "missions",
          title: `Open Mission: ${{watch.name}}`,
          subtitle: `${{watch.query || "-"}} | ${{watch.enabled ? "enabled" : "disabled"}}`,
          run: async () => {{
            await loadWatch(watch.id);
          }},
        }});
        entries.push({{
          id: `watch-clone-${{watch.id}}`,
          group: "missions",
          title: `Clone Mission: ${{watch.name}}`,
          subtitle: "Pull this mission into the deck as a draft fork.",
          run: async () => {{
            await cloneMissionIntoCreateWatch(watch.id);
          }},
        }});
      }});
      state.stories.slice(0, 5).forEach((story) => {{
        entries.push({{
          id: `story-open-${{story.id}}`,
          group: "stories",
          title: `Open Story: ${{story.title}}`,
          subtitle: `${{story.status || "active"}} | items=${{story.item_count || 0}}`,
          run: async () => {{
            await loadStory(story.id);
          }},
        }});
      }});
      return entries;
    }}

    function renderCommandPalette() {{
      const backdrop = $("command-palette");
      const input = $("command-palette-input");
      const list = $("command-palette-list");
      if (!backdrop || !input || !list) {{
        return;
      }}
      backdrop.classList.toggle("open", state.commandPalette.open);
      if (!state.commandPalette.open) {{
        return;
      }}
      const query = String(state.commandPalette.query || "").trim().toLowerCase();
      const entries = buildCommandPaletteEntries().filter((entry) => {{
        if (!query) {{
          return true;
        }}
        return [entry.group, entry.title, entry.subtitle].some((value) => String(value || "").toLowerCase().includes(query));
      }});
      if (state.commandPalette.selectedIndex >= entries.length) {{
        state.commandPalette.selectedIndex = Math.max(entries.length - 1, 0);
      }}
      list.innerHTML = entries.length
        ? entries.map((entry, index) => `
            <div class="palette-item ${{index === state.commandPalette.selectedIndex ? "active" : ""}}" data-palette-id="${{entry.id}}" data-palette-index="${{index}}">
              <div class="palette-kicker">${{escapeHtml(entry.group)}}</div>
              <div>${{escapeHtml(entry.title)}}</div>
              <div class="panel-sub">${{escapeHtml(entry.subtitle || "")}}</div>
            </div>
          `).join("")
        : `<div class="empty">No command matched the current search.</div>`;
      list.querySelectorAll("[data-palette-id]").forEach((item) => {{
        item.addEventListener("mouseenter", () => {{
          state.commandPalette.selectedIndex = Number(item.dataset.paletteIndex || 0);
          renderCommandPalette();
        }});
        item.addEventListener("click", async () => {{
          const entry = entries.find((candidate) => candidate.id === item.dataset.paletteId);
          if (!entry) {{
            return;
          }}
          closeCommandPalette();
          try {{
            await entry.run();
          }} catch (error) {{
            reportError(error, "Palette action");
          }}
        }});
      }});
      input.value = state.commandPalette.query;
    }}

    function openCommandPalette() {{
      state.commandPalette.open = true;
      state.commandPalette.selectedIndex = 0;
      renderCommandPalette();
      window.setTimeout(() => $("command-palette-input")?.focus(), 10);
    }}

    function closeCommandPalette() {{
      state.commandPalette.open = false;
      state.commandPalette.query = "";
      state.commandPalette.selectedIndex = 0;
      renderCommandPalette();
    }}

    function bindCommandPalette() {{
      const backdrop = $("command-palette");
      const input = $("command-palette-input");
      if (!backdrop || !input) {{
        return;
      }}
      backdrop.addEventListener("click", (event) => {{
        if (event.target === backdrop) {{
          closeCommandPalette();
        }}
      }});
      input.addEventListener("input", () => {{
        state.commandPalette.query = input.value;
        state.commandPalette.selectedIndex = 0;
        renderCommandPalette();
      }});
      input.addEventListener("keydown", async (event) => {{
        const list = buildCommandPaletteEntries().filter((entry) => {{
          const query = String(state.commandPalette.query || "").trim().toLowerCase();
          if (!query) {{
            return true;
          }}
          return [entry.group, entry.title, entry.subtitle].some((value) => String(value || "").toLowerCase().includes(query));
        }});
        if (event.key === "ArrowDown") {{
          event.preventDefault();
          state.commandPalette.selectedIndex = Math.min(state.commandPalette.selectedIndex + 1, Math.max(list.length - 1, 0));
          renderCommandPalette();
        }} else if (event.key === "ArrowUp") {{
          event.preventDefault();
          state.commandPalette.selectedIndex = Math.max(state.commandPalette.selectedIndex - 1, 0);
          renderCommandPalette();
        }} else if (event.key === "Enter") {{
          event.preventDefault();
          const entry = list[state.commandPalette.selectedIndex];
          if (!entry) {{
            return;
          }}
          closeCommandPalette();
          try {{
            await entry.run();
          }} catch (error) {{
            reportError(error, "Palette action");
          }}
        }} else if (event.key === "Escape") {{
          event.preventDefault();
          closeCommandPalette();
        }}
      }});
    }}

    state.createWatchDraft = loadCreateWatchDraft();

    function metricCard(label, value, tone = "") {{
      return `<div class="metric"><div class="metric-label">${{label}}</div><div class="metric-value ${{tone}}">${{value}}</div></div>`;
    }}

    function formatRate(value) {{
      if (value === null || value === undefined || Number.isNaN(Number(value))) {{
        return "-";
      }}
      return `${{Math.round(Number(value) * 100)}}%`;
    }}

    function skeletonCard(lines = 3) {{
      return `
        <div class="card skeleton">
          <div class="stack">
            ${{Array.from({{ length: lines }}).map((_, index) => `
              <div class="skeleton-block ${{index === 0 ? "short" : index === lines - 1 ? "long" : "medium"}}"></div>
            `).join("")}}
          </div>
        </div>
      `;
    }}

    function renderActionHistory() {{
      const root = $("console-action-history");
      if (!root) {{
        return;
      }}
      if (!state.actionLog.length) {{
        root.innerHTML = `<div class="empty">No reversible action yet. Create, tune, or triage something and it will show up here.</div>`;
        return;
      }}
      root.innerHTML = state.actionLog.slice(0, 6).map((entry) => `
        <div class="action-log-item">
          <div class="card-top">
            <div>
              <div class="mono">${{escapeHtml(entry.kind || "action")}}</div>
              <div>${{escapeHtml(entry.label || "")}}</div>
            </div>
            <span class="chip ${{entry.status === "error" ? "hot" : entry.status === "ready" ? "ok" : ""}}">${{escapeHtml(entry.status || "done")}}</span>
          </div>
          <div class="panel-sub">${{escapeHtml(entry.detail || "")}}</div>
          <div class="actions">
            ${{
              entry.undo
                ? `<button class="btn-secondary" type="button" data-action-undo="${{entry.id}}">${{escapeHtml(entry.undoLabel || "Undo")}}</button>`
                : ""
            }}
          </div>
        </div>
      `).join("");
      root.querySelectorAll("[data-action-undo]").forEach((button) => {{
        button.addEventListener("click", async () => {{
          const item = state.actionLog.find((entry) => entry.id === button.dataset.actionUndo);
          if (!item || !item.undo) {{
            return;
          }}
          button.disabled = true;
          try {{
            await item.undo();
            state.actionLog = state.actionLog.filter((entry) => entry.id !== item.id);
            renderActionHistory();
          }} catch (error) {{
            reportError(error, "Undo action");
          }} finally {{
            button.disabled = false;
          }}
        }});
      }});
    }}

    function pushActionEntry(entry) {{
      state.actionLog = [{{
        id: `action-${{Date.now()}}-${{Math.random().toString(16).slice(2, 8)}}`,
        timestamp: new Date().toISOString(),
        status: "ready",
        ...entry,
      }}, ...state.actionLog].slice(0, 8);
      renderActionHistory();
    }}

    function buildAlertRules({{ route = "", keyword = "", domain = "", minScore = 0, minConfidence = 0 }}) {{
      const cleanedRoute = String(route || "").trim();
      const cleanedKeyword = String(keyword || "").trim();
      const cleanedDomain = String(domain || "").trim();
      const scoreValue = Math.max(0, Number(minScore || 0));
      const confidenceValue = Math.max(0, Number(minConfidence || 0));
      if (!(cleanedRoute || cleanedKeyword || cleanedDomain || scoreValue > 0 || confidenceValue > 0)) {{
        return [];
      }}
      const alertRule = {{
        name: "console-threshold",
        min_score: scoreValue,
        min_confidence: confidenceValue,
        channels: ["json"],
      }};
      if (cleanedRoute) alertRule.routes = [cleanedRoute];
      if (cleanedKeyword) alertRule.keyword_any = [cleanedKeyword];
      if (cleanedDomain) alertRule.domains = [cleanedDomain];
      return [alertRule];
    }}

    function renderOverview() {{
      const metrics = state.overview || {{}};
      if (state.loading.board && !state.overview) {{
        $("overview-metrics").innerHTML = [metricCard("Loading", "..."), metricCard("Loading", "..."), metricCard("Loading", "...")].join("");
        return;
      }}
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
      if (state.loading.board && !state.watches.length) {{
        root.innerHTML = [skeletonCard(4), skeletonCard(4), skeletonCard(4)].join("");
        return;
      }}
      if (!state.watches.length) {{
        root.innerHTML = `<div class="empty">No watch mission configured yet.</div>`;
        return;
      }}
      root.innerHTML = state.watches.map((watch) => {{
        const platforms = (watch.platforms || []).join(", ") || "any";
        const sites = (watch.sites || []).join(", ") || "-";
        const stateChip = watch.enabled ? "ok" : "";
        const dueChip = watch.is_due ? "hot" : "";
        const selected = watch.id === state.selectedWatchId ? "selected" : "";
        return `
          <div class="card selectable ${{selected}}">
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
              <span>next=${{watch.next_run_at || "-"}}</span>
            </div>
            <div class="actions">
              <button class="btn-secondary" data-watch-open="${{watch.id}}">Open Cockpit</button>
              <button class="btn-secondary" data-run-watch="${{watch.id}}">Run Mission</button>
              <button class="btn-secondary" data-watch-toggle="${{watch.id}}" data-watch-enabled="${{watch.enabled ? "1" : "0"}}">${{watch.enabled ? "Disable" : "Enable"}}</button>
              <button class="btn-secondary" data-delete-watch="${{watch.id}}">Delete</button>
            </div>
          </div>`;
      }}).join("");

      root.querySelectorAll("[data-watch-open]").forEach((button) => {{
        button.addEventListener("click", async () => {{
          button.disabled = true;
          try {{
            await loadWatch(button.dataset.watchOpen);
          }} catch (error) {{
            alert(error.message);
          }} finally {{
            button.disabled = false;
          }}
        }});
      }});

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

      root.querySelectorAll("[data-watch-toggle]").forEach((button) => {{
        button.addEventListener("click", async () => {{
          const identifier = String(button.dataset.watchToggle || "").trim();
          const isEnabled = String(button.dataset.watchEnabled || "1") === "1";
          const previousWatch = state.watches.find((watch) => watch.id === identifier);
          const previousDetail = state.watchDetails[identifier] ? {{ ...state.watchDetails[identifier] }} : null;
          button.disabled = true;
          if (previousWatch) {{
            previousWatch.enabled = !isEnabled;
          }}
          if (state.watchDetails[identifier]) {{
            state.watchDetails[identifier].enabled = !isEnabled;
          }}
          renderWatches();
          renderWatchDetail();
          try {{
            await api(`/api/watches/${{identifier}}/${{isEnabled ? "disable" : "enable"}}`, {{ method: "POST" }});
            pushActionEntry({{
              kind: "mission state",
              label: `${{isEnabled ? "Disabled" : "Enabled"}} ${{previousWatch && previousWatch.name ? previousWatch.name : identifier}}`,
              detail: `${{identifier}} switched to ${{isEnabled ? "disabled" : "enabled"}}.`,
              undoLabel: isEnabled ? "Re-enable" : "Disable again",
              undo: async () => {{
                await api(`/api/watches/${{identifier}}/${{isEnabled ? "enable" : "disable"}}`, {{ method: "POST" }});
                await refreshBoard();
                showToast(`Mission ${{isEnabled ? "re-enabled" : "disabled"}}: ${{identifier}}`, "success");
              }},
            }});
            await refreshBoard();
          }} catch (error) {{
            if (previousWatch) {{
              previousWatch.enabled = isEnabled;
            }}
            if (previousDetail) {{
              state.watchDetails[identifier] = previousDetail;
            }}
            renderWatches();
            renderWatchDetail();
            reportError(error, `${{isEnabled ? "Disable" : "Enable"}} mission`);
          }} finally {{
            button.disabled = false;
          }}
        }});
      }});

      root.querySelectorAll("[data-delete-watch]").forEach((button) => {{
        button.addEventListener("click", async () => {{
          const identifier = String(button.dataset.deleteWatch || "").trim();
          const removedWatch = state.watches.find((watch) => watch.id === identifier);
          const removedDetail = state.watchDetails[identifier] ? {{ ...state.watchDetails[identifier] }} : null;
          button.disabled = true;
          state.watches = state.watches.filter((watch) => watch.id !== identifier);
          delete state.watchDetails[identifier];
          if (state.selectedWatchId === identifier) {{
            state.selectedWatchId = state.watches[0] ? state.watches[0].id : "";
          }}
          renderWatches();
          renderWatchDetail();
          try {{
            await api(`/api/watches/${{identifier}}`, {{ method: "DELETE" }});
            pushActionEntry({{
              kind: "mission delete",
              label: `Deleted ${{removedWatch && removedWatch.name ? removedWatch.name : identifier}}`,
              detail: "Deletion is reversible from the recent action log.",
              undoLabel: "Restore",
              undo: async () => {{
                if (!removedWatch) {{
                  return;
                }}
                const payload = {{
                  name: String(removedWatch.name || identifier),
                  query: String(removedWatch.query || ""),
                  schedule: String(removedWatch.schedule || removedWatch.schedule_label || "manual"),
                  platforms: Array.isArray(removedWatch.platforms) ? removedWatch.platforms : [],
                  alert_rules: removedDetail && Array.isArray(removedDetail.alert_rules) ? removedDetail.alert_rules : [],
                }};
                await api("/api/watches", {{ method: "POST", headers: jsonHeaders, body: JSON.stringify(payload) }});
                await refreshBoard();
                showToast(`Mission restored: ${{payload.name}}`, "success");
              }},
            }});
            await refreshBoard();
          }} catch (error) {{
            if (removedWatch) {{
              state.watches = [removedWatch, ...state.watches];
            }}
            if (removedDetail) {{
              state.watchDetails[identifier] = removedDetail;
            }}
            reportError(error, "Delete mission");
            await refreshBoard();
          }} finally {{
            button.disabled = false;
          }}
        }});
      }});
    }}

    async function loadWatch(identifier) {{
      state.selectedWatchId = identifier;
      state.loading.watchDetail = true;
      renderWatches();
      renderWatchDetail();
      try {{
        state.watchDetails[identifier] = await api(`/api/watches/${{identifier}}`);
      }} finally {{
        state.loading.watchDetail = false;
      }}
      renderWatches();
      renderWatchDetail();
    }}

    function renderWatchDetail() {{
      const root = $("watch-detail");
      const selected = state.selectedWatchId;
      if (state.loading.watchDetail && selected) {{
        root.innerHTML = [skeletonCard(4), skeletonCard(4), skeletonCard(4)].join("");
        return;
      }}
      const watch = state.watchDetails[selected] || state.watches.find((candidate) => candidate.id === selected);
      if (!watch) {{
        root.innerHTML = `<div class="empty">Select one mission from the board to inspect schedule, run history, and alert output.</div>`;
        return;
      }}
      const recentRuns = Array.isArray(watch.runs) ? watch.runs : [];
      const recentResults = Array.isArray(watch.recent_results) ? watch.recent_results : [];
      const recentAlerts = Array.isArray(watch.recent_alerts) ? watch.recent_alerts : [];
      const lastFailure = watch.last_failure || null;
      const retryAdvice = watch.retry_advice || null;
      const runStats = watch.run_stats || {{}};
      const resultStats = watch.result_stats || {{}};
      const deliveryStats = watch.delivery_stats || {{}};
      const resultFilters = watch.result_filters || {{}};
      const timelineEvents = Array.isArray(watch.timeline_strip) ? watch.timeline_strip : [];
      const stateOptions = Array.isArray(resultFilters.states) ? resultFilters.states : [];
      const sourceOptions = Array.isArray(resultFilters.sources) ? resultFilters.sources : [];
      const domainOptions = Array.isArray(resultFilters.domains) ? resultFilters.domains : [];
      const savedFilters = state.watchResultFilters[watch.id] || {{}};
      const normalizeFilterValue = (key, options) => {{
        const raw = String(savedFilters[key] || "all");
        return raw === "all" || options.some((option) => option.key === raw) ? raw : "all";
      }};
      const activeFilters = {{
        state: normalizeFilterValue("state", stateOptions),
        source: normalizeFilterValue("source", sourceOptions),
        domain: normalizeFilterValue("domain", domainOptions),
      }};
      state.watchResultFilters[watch.id] = activeFilters;
      const runsBlock = recentRuns.length
        ? recentRuns.map((run) => `
            <div class="card">
              <div class="card-top">
                <div>
                  <h3 class="card-title">${{run.status || "success"}}</h3>
                  <div class="meta">
                    <span>${{run.id || "-"}}</span>
                    <span>trigger=${{run.trigger || "manual"}}</span>
                    <span>items=${{run.item_count || 0}}</span>
                  </div>
                </div>
                <span class="chip ${{run.status === "success" ? "ok" : "hot"}}">${{run.status || "unknown"}}</span>
              </div>
              <div class="meta">
                <span>started=${{run.started_at || "-"}}</span>
                <span>finished=${{run.finished_at || "-"}}</span>
              </div>
              <div class="panel-sub">${{run.error || "No recorded error."}}</div>
            </div>
          `).join("")
        : `<div class="empty">No mission run recorded yet.</div>`;
      const alertsBlock = recentAlerts.length
        ? recentAlerts.map((alert) => `
            <div class="card">
              <div class="card-top">
                <div>
                  <h3 class="card-title">${{alert.rule_name}}</h3>
                  <div class="meta">
                    <span>${{alert.created_at || "-"}}</span>
                    <span>items=${{(alert.item_ids || []).length}}</span>
                  </div>
                </div>
                <span class="chip ${{alert.extra && alert.extra.delivery_errors ? "hot" : "ok"}}">${{(alert.delivered_channels || ["json"]).join(",")}}</span>
              </div>
              <div class="panel-sub">${{alert.summary || "No alert summary captured."}}</div>
            </div>
          `).join("")
        : `<div class="empty">No recent alert event for this mission.</div>`;
      const filteredResults = recentResults.filter((item) => {{
        const filters = item.watch_filters || {{}};
        if (activeFilters.state !== "all" && (filters.state || "new") !== activeFilters.state) {{
          return false;
        }}
        if (activeFilters.source !== "all" && (filters.source || "unknown") !== activeFilters.source) {{
          return false;
        }}
        if (activeFilters.domain !== "all" && (filters.domain || "unknown") !== activeFilters.domain) {{
          return false;
        }}
        return true;
      }});
      const filterGroups = [
        {{ key: "state", label: "state", options: stateOptions }},
        {{ key: "source", label: "source", options: sourceOptions }},
        {{ key: "domain", label: "domain", options: domainOptions }},
      ];
      const filterWindowCount = Number(resultFilters.window_count || recentResults.length || 0);
      const filterBlock = filterGroups.map((group) => `
          <div class="stack">
            <div class="panel-sub">${{group.label}}</div>
            <div class="chip-row">
              <button class="chip-btn ${{activeFilters[group.key] === "all" ? "active" : ""}}" type="button" data-filter-group="${{group.key}}" data-filter-value="all">all (${{filterWindowCount}})</button>
              ${{group.options.map((option) => `
                <button class="chip-btn ${{activeFilters[group.key] === option.key ? "active" : ""}}" type="button" data-filter-group="${{group.key}}" data-filter-value="${{escapeHtml(option.key)}}">${{escapeHtml(option.label)}} (${{option.count || 0}})</button>
              `).join("")}}
            </div>
          </div>
        `).join("");
      const resultsBlock = filteredResults.length
        ? filteredResults.map((item) => `
            <div class="card">
              <div class="card-top">
                <div>
                  <h3 class="card-title">${{item.title}}</h3>
                  <div class="meta">
                    <span>${{item.id}}</span>
                    <span>score=${{item.score || 0}}</span>
                    <span>confidence=${{Number(item.confidence || 0).toFixed(2)}}</span>
                    <span>${{item.source_name || item.source_type || "-"}}</span>
                  </div>
                </div>
                <span class="chip">${{item.review_state || "new"}}</span>
              </div>
              <div class="panel-sub">${{item.url || "-"}}</div>
            </div>
          `).join("")
        : `<div class="empty">No persisted result matched the active filter chips in the current mission window.</div>`;
      const timelineBlock = timelineEvents.length
        ? `<div class="timeline-strip">${{timelineEvents.map((event) => `
            <div class="timeline-event ${{event.tone || ""}}">
              <div class="card-top">
                <span class="chip ${{event.tone || ""}}">${{event.kind || "event"}}</span>
                <span class="panel-sub">${{event.time || "-"}}</span>
              </div>
              <div class="mono">${{event.label || "-"}}</div>
              <div class="panel-sub">${{event.detail || "-"}}</div>
            </div>
          `).join("")}}</div>`
        : `<div class="empty">No mission timeline event captured yet.</div>`;
      const retryCollectors = retryAdvice && Array.isArray(retryAdvice.suspected_collectors)
        ? retryAdvice.suspected_collectors
        : [];
      const retryNotes = retryAdvice && Array.isArray(retryAdvice.notes) ? retryAdvice.notes : [];
      const failureBlock = lastFailure
        ? `
            <div class="card">
              <div class="card-top">
                <div>
                  <h3 class="card-title">latest failure</h3>
                  <div class="meta">
                    <span>${{lastFailure.id || "-"}}</span>
                    <span>status=${{lastFailure.status || "error"}}</span>
                    <span>trigger=${{lastFailure.trigger || "manual"}}</span>
                    <span>finished=${{lastFailure.finished_at || "-"}}</span>
                  </div>
                </div>
                <span class="chip hot">${{retryAdvice && retryAdvice.failure_class ? retryAdvice.failure_class : "error"}}</span>
              </div>
              <div class="panel-sub">${{lastFailure.error || "No failure message captured."}}</div>
            </div>
          `
        : "";
      const retryAdviceBlock = retryAdvice
        ? `
            <div class="card">
              <div class="mono">retry advice</div>
              <div class="meta">
                <span>retry=${{retryAdvice.retry_command || "-"}}</span>
                <span>daemon=${{retryAdvice.daemon_retry_command || "-"}}</span>
              </div>
              <div class="panel-sub">${{retryAdvice.summary || "No retry guidance recorded."}}</div>
              ${{
                retryCollectors.length
                  ? `<div class="stack" style="margin-top:12px;">${{retryCollectors.map((collector) => `
                      <div class="mini-item">${{collector.name}} | ${{collector.tier || "-"}} | ${{collector.status || "-"}} | available=${{collector.available}} | ${{collector.setup_hint || collector.message || "-"}}</div>
                    `).join("")}}</div>`
                  : ""
              }}
              ${{
                retryNotes.length
                  ? `<div class="stack" style="margin-top:12px;">${{retryNotes.map((note) => `<div class="mini-item">${{note}}</div>`).join("")}}</div>`
                  : ""
              }}
            </div>
          `
        : "";

      root.innerHTML = `
        <div class="card">
          <div class="card-top">
            <div>
              <h3 class="card-title">${{watch.name}}</h3>
              <div class="meta">
                <span>${{watch.id}}</span>
                <span>schedule=${{watch.schedule_label || watch.schedule || "manual"}}</span>
                <span>next=${{watch.next_run_at || "-"}}</span>
                <span>query=${{watch.query || "-"}}</span>
              </div>
            </div>
            <span class="chip ${{watch.enabled ? "ok" : "hot"}}">${{watch.enabled ? "enabled" : "disabled"}}</span>
          </div>
          <div class="meta">
            <span>due=${{watch.is_due ? "yes" : "no"}}</span>
            <span>alert_rules=${{watch.alert_rule_count || 0}}</span>
            <span>runs=${{runStats.total || 0}}</span>
            <span>success=${{runStats.success || 0}}</span>
            <span>errors=${{runStats.error || 0}}</span>
            <span>results=${{resultStats.stored_result_count || 0}}</span>
            <span>alerts=${{deliveryStats.recent_alert_count || 0}}</span>
          </div>
          <div class="panel-sub">${{watch.last_run_error || "Mission history and recent delivery outcomes are visible below."}}</div>
        </div>
        ${{failureBlock}}
        ${{retryAdviceBlock}}
        <div class="card">
          <div class="mono">timeline strip</div>
          <div class="panel-sub">Recent run, result, and alert events are merged into one server-backed mission timeline.</div>
          <div style="margin-top:12px;">
            ${{timelineBlock}}
          </div>
        </div>
        <div class="story-columns">
          <div class="stack">
            <div class="mono">recent runs</div>
            ${{runsBlock}}
          </div>
          <div class="stack">
            <div class="mono">recent alerts</div>
            ${{alertsBlock}}
          </div>
        </div>
        <div class="stack">
          <div class="mono">result stream</div>
          <div class="card">
            <div class="mono">filter chips</div>
            <div class="panel-sub">Filter the current persisted result window by review state, source, or domain without leaving the cockpit.</div>
            <div class="stack" style="margin-top:12px;">
              ${{filterBlock}}
            </div>
          </div>
          ${{resultsBlock}}
        </div>
        <div class="card">
          <div class="card-top">
            <div>
              <div class="mono">alert rule editor</div>
              <div class="panel-sub">Edit multiple console threshold rules for this mission, then replace the saved rule set in one write.</div>
            </div>
            <span class="chip">${{(watch.alert_rules || []).length}} rule(s)</span>
          </div>
          <form id="watch-alert-form" data-watch-id="${{watch.id}}">
            <div class="stack" id="watch-alert-rules">
              ${{
                ((watch.alert_rules || []).length ? watch.alert_rules : [{{}}]).map((rule, index) => `
                  <div class="card" data-alert-rule-card="${{index}}">
                    <div class="card-top">
                      <div>
                        <div class="mono">rule ${{index + 1}}</div>
                        <div class="panel-sub">Current name: ${{rule.name || "console-threshold"}}</div>
                      </div>
                      <button class="btn-secondary" type="button" data-remove-alert-rule="${{index}}">Remove</button>
                    </div>
                    <div class="field-grid">
                      <label>Alert Route<input name="route" placeholder="ops-webhook" value="${{(rule.routes || [])[0] || ""}}"></label>
                      <label>Alert Keyword<input name="keyword" placeholder="launch" value="${{(rule.keyword_any || [])[0] || ""}}"></label>
                    </div>
                    <div class="field-grid">
                      <label>Alert Domain<input name="domain" placeholder="openai.com" value="${{(rule.domains || [])[0] || ""}}"></label>
                      <label>Min Score<input name="min_score" placeholder="70" type="number" value="${{(rule.min_score || 0) || ""}}"></label>
                    </div>
                    <div class="field-grid">
                      <label>Min Confidence<input name="min_confidence" placeholder="0.8" step="0.01" type="number" value="${{(rule.min_confidence || 0) || ""}}"></label>
                      <div class="stack">
                        <div class="panel-sub">Channels are still pinned to json; named route delivery is configured via Alert Route.</div>
                      </div>
                    </div>
                  </div>
                `).join("")
              }}
            </div>
            <div class="toolbar">
              <button class="btn-secondary" id="watch-alert-add" type="button">Add Alert Rule</button>
              <button class="btn-primary" type="submit">Save Alert Rules</button>
              <button class="btn-secondary" id="watch-alert-clear" type="button">Clear Alert Rules</button>
            </div>
          </form>
        </div>
      `;

      root.querySelectorAll("[data-filter-group]").forEach((button) => {{
        button.addEventListener("click", () => {{
          const filterGroup = String(button.dataset.filterGroup || "").trim();
          if (!filterGroup) {{
            return;
          }}
          const current = state.watchResultFilters[watch.id] || {{ state: "all", source: "all", domain: "all" }};
          current[filterGroup] = String(button.dataset.filterValue || "all");
          state.watchResultFilters[watch.id] = current;
          renderWatchDetail();
        }});
      }});

      const alertForm = document.getElementById("watch-alert-form");
      const addRuleButton = document.getElementById("watch-alert-add");
      if (addRuleButton) {{
        addRuleButton.addEventListener("click", () => {{
          const rulesRoot = document.getElementById("watch-alert-rules");
          if (!rulesRoot) {{
            return;
          }}
          const nextIndex = rulesRoot.querySelectorAll("[data-alert-rule-card]").length;
          rulesRoot.insertAdjacentHTML("beforeend", `
            <div class="card" data-alert-rule-card="${{nextIndex}}">
              <div class="card-top">
                <div>
                  <div class="mono">rule ${{nextIndex + 1}}</div>
                  <div class="panel-sub">New console threshold rule.</div>
                </div>
                <button class="btn-secondary" type="button" data-remove-alert-rule="${{nextIndex}}">Remove</button>
              </div>
              <div class="field-grid">
                <label>Alert Route<input name="route" placeholder="ops-webhook"></label>
                <label>Alert Keyword<input name="keyword" placeholder="launch"></label>
              </div>
              <div class="field-grid">
                <label>Alert Domain<input name="domain" placeholder="openai.com"></label>
                <label>Min Score<input name="min_score" placeholder="70" type="number"></label>
              </div>
              <div class="field-grid">
                <label>Min Confidence<input name="min_confidence" placeholder="0.8" step="0.01" type="number"></label>
                <div class="stack">
                  <div class="panel-sub">Channels stay pinned to json; named route delivery is configured via Alert Route.</div>
                </div>
              </div>
            </div>
          `);
          rulesRoot.querySelectorAll("[data-remove-alert-rule]").forEach((button) => {{
            button.onclick = () => {{
              button.closest("[data-alert-rule-card]")?.remove();
            }};
          }});
        }});
      }}
      root.querySelectorAll("[data-remove-alert-rule]").forEach((button) => {{
        button.onclick = () => {{
          button.closest("[data-alert-rule-card]")?.remove();
        }};
      }});
      if (alertForm) {{
        alertForm.addEventListener("submit", async (event) => {{
          event.preventDefault();
          const cards = Array.from(document.querySelectorAll("[data-alert-rule-card]"));
          const alertRules = cards.flatMap((card) => {{
            return buildAlertRules({{
              route: String(card.querySelector('[name=\"route\"]')?.value || "").trim(),
              keyword: String(card.querySelector('[name=\"keyword\"]')?.value || "").trim(),
              domain: String(card.querySelector('[name=\"domain\"]')?.value || "").trim(),
              minScore: Number(card.querySelector('[name=\"min_score\"]')?.value || 0),
              minConfidence: Number(card.querySelector('[name=\"min_confidence\"]')?.value || 0),
            }});
          }});
          const payload = {{
            alert_rules: alertRules,
          }};
          if (!payload.alert_rules.length) {{
            alert("Provide at least one route, keyword, domain, or threshold across the rule set.");
            return;
          }}
          try {{
            await api(`/api/watches/${{watch.id}}/alert-rules`, {{
              method: "PUT",
              headers: jsonHeaders,
              body: JSON.stringify(payload),
            }});
            await refreshBoard();
          }} catch (error) {{
            alert(error.message);
          }}
        }});
      }}

      const clearButton = document.getElementById("watch-alert-clear");
      if (clearButton) {{
        clearButton.addEventListener("click", async () => {{
          try {{
            await api(`/api/watches/${{watch.id}}/alert-rules`, {{
              method: "PUT",
              headers: jsonHeaders,
              body: JSON.stringify({{ alert_rules: [] }}),
            }});
            await refreshBoard();
          }} catch (error) {{
            alert(error.message);
          }}
        }});
      }}
    }}

    function renderAlerts() {{
      const root = $("alert-list");
      if (state.loading.board && !state.alerts.length) {{
        root.innerHTML = [skeletonCard(3), skeletonCard(3)].join("");
        return;
      }}
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

    function renderRouteHealth() {{
      const root = $("route-health");
      if (state.loading.board && !state.routeHealth.length) {{
        root.innerHTML = [skeletonCard(4), skeletonCard(4)].join("");
        return;
      }}
      if (!state.routeHealth.length) {{
        root.innerHTML = `<div class="empty">No route health signal yet. Trigger named-route alerts to populate delivery quality.</div>`;
        return;
      }}
      root.innerHTML = state.routeHealth.map((route) => `
        <div class="card">
          <div class="card-top">
            <div>
              <h3 class="card-title">${{route.name}}</h3>
              <div class="meta">
                <span>channel=${{route.channel || "unknown"}}</span>
                <span>status=${{route.status || "idle"}}</span>
                <span>rate=${{formatRate(route.success_rate)}}</span>
              </div>
            </div>
            <span class="chip ${{route.status === "healthy" ? "ok" : route.status === "idle" ? "" : "hot"}}">${{route.status || "idle"}}</span>
          </div>
          <div class="meta">
            <span>events=${{route.event_count || 0}}</span>
            <span>delivered=${{route.delivered_count || 0}}</span>
            <span>failed=${{route.failure_count || 0}}</span>
            <span>last=${{route.last_event_at || "-"}}</span>
          </div>
          <div class="panel-sub">${{route.last_error || route.last_summary || "No recent route delivery attempt recorded."}}</div>
        </div>
      `).join("");
    }}

    function renderRoutes() {{
      const root = $("route-list");
      if (state.loading.board && !state.routes.length) {{
        root.innerHTML = skeletonCard(3);
        return;
      }}
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
      if (state.loading.board && !state.status && !state.ops) {{
        root.innerHTML = [skeletonCard(4), skeletonCard(4), skeletonCard(4)].join("");
        return;
      }}
      const ops = state.ops || {{}};
      const status = ops.daemon || state.status || {{}};
      const metrics = status.metrics || {{}};
      const collectorSummary = ops.collector_summary || {{}};
      const collectorTiers = ops.collector_tiers || {{}};
      const collectorDrilldown = Array.isArray(ops.collector_drilldown) ? ops.collector_drilldown : [];
      const watchMetrics = ops.watch_metrics || {{}};
      const watchSummary = ops.watch_summary || {{}};
      const watchHealth = Array.isArray(ops.watch_health) ? ops.watch_health : [];
      const routeSummary = ops.route_summary || {{}};
      const routeDrilldown = Array.isArray(ops.route_drilldown) ? ops.route_drilldown : [];
      const routeTimeline = Array.isArray(ops.route_timeline) ? ops.route_timeline : [];
      const degradedCollectors = ops.degraded_collectors || [];
      const recentFailures = ops.recent_failures || [];
      const isError = status.state === "error";
      const tierBlock = Object.entries(collectorTiers).length
        ? Object.entries(collectorTiers).map(([tierName, tier]) => `
            <div class="mini-item">${{tierName}} | total=${{tier.total || 0}} | ok=${{tier.ok || 0}} | warn=${{tier.warn || 0}} | error=${{tier.error || 0}}</div>
          `).join("")
        : '<div class="empty">No collector tier breakdown available.</div>';
      const watchBlock = watchHealth.length
        ? watchHealth.slice(0, 5).map((mission) => `
            <div class="mini-item">${{mission.id}} | ${{mission.status || "idle"}} | due=${{mission.is_due ? "yes" : "no"}} | rate=${{formatRate(mission.success_rate)}}</div>
          `).join("")
        : '<div class="empty">No watch mission health record yet.</div>';
      const collectorBlock = degradedCollectors.length
        ? degradedCollectors.slice(0, 4).map((collector) => `
            <div class="mini-item">${{collector.name}} | ${{collector.tier}} | ${{collector.status}} | available=${{collector.available}}</div>
          `).join("")
        : '<div class="empty">No degraded collector currently reported.</div>';
      const collectorDrilldownBlock = collectorDrilldown.length
        ? collectorDrilldown.slice(0, 8).map((collector) => `
            <div class="mini-item">${{collector.name}} | ${{collector.tier || "-"}} | ${{collector.status || "ok"}} | available=${{collector.available}}</div>
            <div class="panel-sub">${{collector.setup_hint || collector.message || "No remediation note."}}</div>
          `).join("")
        : '<div class="empty">No collector drill-down entry available.</div>';
      const routeDrilldownBlock = routeDrilldown.length
        ? routeDrilldown.slice(0, 8).map((route) => `
            <div class="mini-item">${{route.name}} | channel=${{route.channel || "unknown"}} | status=${{route.status || "idle"}} | rate=${{formatRate(route.success_rate)}}</div>
            <div class="panel-sub">missions=${{route.mission_count || 0}} | rules=${{route.rule_count || 0}} | events=${{route.event_count || 0}} | failed=${{route.failure_count || 0}}</div>
            <div class="panel-sub">${{route.last_error || route.last_summary || "No recent route detail."}}</div>
          `).join("")
        : '<div class="empty">No route drill-down entry available.</div>';
      const routeTimelineBlock = routeTimeline.length
        ? routeTimeline.slice(0, 8).map((event) => `
            <div class="mini-item">${{event.created_at || "-"}} | ${{event.route || "-"}} | ${{event.status || "pending"}} | ${{event.mission_name || event.mission_id || "-"}}</div>
            <div class="panel-sub">${{event.error || event.summary || "No route event detail."}}</div>
          `).join("")
        : '<div class="empty">No route delivery timeline event available.</div>';
      const failureBlock = recentFailures.length
        ? recentFailures.slice(0, 4).map((failure) => `
            <div class="mini-item">${{failure.kind}} | ${{failure.mission_name || failure.name || "-"}} | ${{failure.status || "error"}} | ${{failure.error || "-"}}</div>
          `).join("")
        : '<div class="empty">No recent failure captured.</div>';
      root.innerHTML = `
        <div class="state-banner ${{isError ? "error" : ""}}">
          <div class="eyebrow"><span class="dot"></span> daemon / ${{status.state || "idle"}}</div>
          <h3 class="card-title" style="margin-top:12px;">Heartbeat: ${{status.heartbeat_at || "-"}}</h3>
          <div class="meta">
            <span>cycles=${{metrics.cycles_total || 0}}</span>
            <span>runs=${{metrics.runs_total || 0}}</span>
            <span>alerts=${{metrics.alerts_total || 0}}</span>
            <span>errors=${{metrics.error_total || 0}}</span>
            <span>success=${{metrics.success_total || 0}}</span>
          </div>
        </div>
        <div class="card">
          <div class="mono">collector health</div>
          <div class="meta">
            <span>total=${{collectorSummary.total || 0}}</span>
            <span>ok=${{collectorSummary.ok || 0}}</span>
            <span>warn=${{collectorSummary.warn || 0}}</span>
            <span>error=${{collectorSummary.error || 0}}</span>
            <span>unavailable=${{collectorSummary.unavailable || 0}}</span>
          </div>
        </div>
        <div class="card">
          <div class="mono">route health</div>
          <div class="meta">
            <span>healthy=${{routeSummary.healthy || 0}}</span>
            <span>degraded=${{routeSummary.degraded || 0}}</span>
            <span>missing=${{routeSummary.missing || 0}}</span>
            <span>idle=${{routeSummary.idle || 0}}</span>
          </div>
        </div>
        <div class="card">
          <div class="mono">watch health</div>
          <div class="meta">
            <span>total=${{watchSummary.total || 0}}</span>
            <span>enabled=${{watchSummary.enabled || 0}}</span>
            <span>healthy=${{watchSummary.healthy || 0}}</span>
            <span>degraded=${{watchSummary.degraded || 0}}</span>
            <span>idle=${{watchSummary.idle || 0}}</span>
            <span>disabled=${{watchSummary.disabled || 0}}</span>
            <span>due=${{watchSummary.due || 0}}</span>
            <span>rate=${{formatRate(watchMetrics.success_rate)}}</span>
          </div>
        </div>
        <div class="card">
          <div class="mono">last_error</div>
          <div>${{status.last_error || "-"}}</div>
        </div>
        <div class="graph-meta">
          <div class="mini-list">
            <div class="mono">collector tiers</div>
            ${{tierBlock}}
          </div>
          <div class="mini-list">
            <div class="mono">watch board</div>
            ${{watchBlock}}
          </div>
        </div>
        <div class="graph-meta">
          <div class="mini-list">
            <div class="mono">degraded collectors</div>
            ${{collectorBlock}}
          </div>
          <div class="mini-list">
            <div class="mono">collector drill-down</div>
            ${{collectorDrilldownBlock}}
          </div>
        </div>
        <div class="graph-meta">
          <div class="mini-list">
            <div class="mono">route drill-down</div>
            ${{routeDrilldownBlock}}
          </div>
          <div class="mini-list">
            <div class="mono">recent failures</div>
            ${{failureBlock}}
          </div>
        </div>
        <div class="graph-meta">
          <div class="mini-list">
            <div class="mono">route timeline</div>
            ${{routeTimelineBlock}}
          </div>
          <div class="mini-list">
            <div class="mono">degraded collectors</div>
            ${{collectorBlock}}
          </div>
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

    function renderReviewNotes(notes) {{
      const entries = Array.isArray(notes) ? notes : [];
      if (!entries.length) {{
        return `<div class="panel-sub">No review note recorded yet.</div>`;
      }}
      return `
        <div class="stack" style="margin-top:12px;">
          ${{entries.slice(-3).map((entry) => `
            <div class="mini-item">${{escapeHtml(entry.author || "console")}} | ${{escapeHtml(entry.created_at || "-")}}</div>
            <div class="panel-sub">${{escapeHtml(entry.note || "")}}</div>
          `).join("")}}
        </div>
      `;
    }}

    function getVisibleTriageItems() {{
      const activeFilter = state.triageFilter || "open";
      return state.triage.filter((item) => {{
        const reviewState = String(item.review_state || "new").trim().toLowerCase() || "new";
        if (activeFilter === "all") {{
          return true;
        }}
        if (activeFilter === "open") {{
          return !["verified", "duplicate", "ignored"].includes(reviewState);
        }}
        return reviewState === activeFilter;
      }});
    }}

    async function runTriageExplain(itemId) {{
      if (!itemId) {{
        return;
      }}
      state.selectedTriageId = itemId;
      state.triageExplain[itemId] = await api(`/api/triage/${{itemId}}/explain?limit=4`);
      renderTriage();
    }}

    async function runTriageStateUpdate(itemId, nextState) {{
      if (!itemId || !nextState) {{
        return;
      }}
      state.selectedTriageId = itemId;
      const currentItem = state.triage.find((item) => item.id === itemId);
      const previousState = currentItem ? String(currentItem.review_state || "new") : "new";
      if (currentItem) {{
        currentItem.review_state = nextState;
      }}
      renderTriage();
      try {{
        await api(`/api/triage/${{itemId}}/state`, {{
          method: "POST",
          headers: jsonHeaders,
          body: JSON.stringify({{ state: nextState, actor: "console" }}),
        }});
        pushActionEntry({{
          kind: "triage state",
          label: `Marked ${{itemId}} as ${{nextState}}`,
          detail: `Previous state was ${{previousState}}.`,
          undoLabel: `Restore ${{previousState}}`,
          undo: async () => {{
            await api(`/api/triage/${{itemId}}/state`, {{
              method: "POST",
              headers: jsonHeaders,
              body: JSON.stringify({{ state: previousState, actor: "console" }}),
            }});
            await refreshBoard();
            showToast(`Triage state restored: ${{itemId}} -> ${{previousState}}`, "success");
          }},
        }});
        await refreshBoard();
      }} catch (error) {{
        if (currentItem) {{
          currentItem.review_state = previousState;
        }}
        renderTriage();
        throw error;
      }}
    }}

    function focusTriageNoteComposer(itemId) {{
      if (!itemId) {{
        return;
      }}
      state.selectedTriageId = itemId;
      renderTriage();
      const field = document.querySelector(`[data-triage-note-input="${{itemId}}"]`);
      if (field) {{
        field.focus();
        field.setSelectionRange(field.value.length, field.value.length);
      }}
    }}

    function moveTriageSelection(delta) {{
      const visibleItems = getVisibleTriageItems();
      if (!visibleItems.length) {{
        return;
      }}
      const currentIndex = Math.max(
        0,
        visibleItems.findIndex((item) => item.id === state.selectedTriageId),
      );
      const nextIndex = Math.min(
        visibleItems.length - 1,
        Math.max(0, currentIndex + delta),
      );
      state.selectedTriageId = visibleItems[nextIndex].id;
      renderTriage();
      const selectedCard = document.querySelector(`[data-triage-card="${{state.selectedTriageId}}"]`);
      selectedCard?.scrollIntoView({{ block: "nearest", behavior: "smooth" }});
    }}

    function renderTriage() {{
      const root = $("triage-list");
      const inlineStats = $("triage-stats-inline");
      if (state.loading.board && !state.triage.length) {{
        inlineStats.innerHTML = `<span>loading=triage</span>`;
        root.innerHTML = [skeletonCard(4), skeletonCard(4), skeletonCard(4)].join("");
        return;
      }}
      const stats = state.triageStats || {{}};
      const triageStates = stats.states || {{}};
      const filterOptions = [
        {{ key: "open", label: "open", count: stats.open_count || 0 }},
        {{ key: "all", label: "all", count: stats.total || state.triage.length }},
        ...Object.entries(triageStates).map(([key, count]) => ({{ key, label: key, count: count || 0 }})),
      ];
      const activeFilter = state.triageFilter || "open";
      const filteredItems = getVisibleTriageItems();
      if (filteredItems.length && !filteredItems.some((item) => item.id === state.selectedTriageId)) {{
        state.selectedTriageId = filteredItems[0].id;
      }}
      if (!filteredItems.length) {{
        state.selectedTriageId = "";
      }}
      const filterBlock = filterOptions.map((option) => `
        <button class="chip-btn ${{activeFilter === option.key ? "active" : ""}}" type="button" data-triage-filter="${{escapeHtml(option.key)}}">${{escapeHtml(option.label)}} (${{option.count || 0}})</button>
      `).join("");
      inlineStats.innerHTML = `
        <span>open=${{stats.open_count || 0}}</span>
        <span>closed=${{stats.closed_count || 0}}</span>
        <span>notes=${{stats.note_count || 0}}</span>
        <span>verified=${{(stats.states || {{}}).verified || 0}}</span>
        <span>filter=${{activeFilter}}</span>
        <span>selected=${{state.selectedTriageId || "-"}}</span>
      `;
      if (!state.triage.length) {{
        root.innerHTML = `
          <div class="card">
            <div class="mono">triage filters</div>
            <div class="panel-sub">Slice the queue by current review state before applying notes or state transitions.</div>
            <div class="stack" style="margin-top:12px;">${{filterBlock}}</div>
          </div>
          <div class="card">
            <div class="mono">triage shortcuts</div>
            <div class="panel-sub">Use J/K to move, V to verify, T to triage, E to escalate, I to ignore, D to explain duplicates, and N to focus the note composer.</div>
          </div>
          <div class="empty">No triage item stored right now.</div>`;
        return;
      }}
      root.innerHTML = `
        <div class="card">
          <div class="mono">triage filters</div>
          <div class="panel-sub">Slice the queue by current review state before applying notes or state transitions.</div>
          <div class="stack" style="margin-top:12px;">${{filterBlock}}</div>
        </div>
        <div class="card">
          <div class="mono">triage shortcuts</div>
          <div class="panel-sub">Use J/K to move, V to verify, T to triage, E to escalate, I to ignore, D to explain duplicates, and N to focus the note composer.</div>
        </div>
        ${{
          filteredItems.length
            ? filteredItems.map((item) => `
        <div class="card selectable ${{item.id === state.selectedTriageId ? "selected" : ""}}" data-triage-card="${{item.id}}">
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
            <button class="btn-secondary" data-triage-state="triaged" data-triage-id="${{item.id}}">Triaged</button>
            <button class="btn-secondary" data-triage-state="verified" data-triage-id="${{item.id}}">Verify</button>
            <button class="btn-secondary" data-triage-state="escalated" data-triage-id="${{item.id}}">Escalate</button>
            <button class="btn-secondary" data-triage-state="ignored" data-triage-id="${{item.id}}">Ignore</button>
          </div>
          <div class="card" style="margin-top:12px;">
            <div class="mono">review notes</div>
            <div class="panel-sub">Capture reviewer rationale, routing hints, and merge context without leaving the queue.</div>
            ${{renderReviewNotes(item.review_notes)}}
            <form data-triage-note-form="${{item.id}}" style="margin-top:12px;">
              <label>note composer<textarea name="note" rows="3" data-triage-note-input="${{item.id}}" placeholder="Capture reviewer rationale, routing hint, or merge context.">${{escapeHtml(state.triageNoteDrafts[item.id] || "")}}</textarea></label>
              <div class="toolbar">
                <button class="btn-primary" type="submit">Save Note</button>
              </div>
            </form>
          </div>
          ${{renderDuplicateExplain(state.triageExplain[item.id])}}
        </div>
      `).join("")
            : `<div class="empty">No triage item matched the active queue filter.</div>`
        }}
      `;

      root.querySelectorAll("[data-triage-filter]").forEach((button) => {{
        button.addEventListener("click", () => {{
          state.triageFilter = String(button.dataset.triageFilter || "open").trim() || "open";
          renderTriage();
        }});
      }});

      root.querySelectorAll("[data-triage-card]").forEach((card) => {{
        card.addEventListener("click", (event) => {{
          if (event.target.closest("button, textarea, input, select, a, form")) {{
            return;
          }}
          state.selectedTriageId = String(card.dataset.triageCard || "").trim();
          renderTriage();
        }});
      }});

      root.querySelectorAll("[data-triage-explain]").forEach((button) => {{
        button.addEventListener("click", async () => {{
          button.disabled = true;
          try {{
            await runTriageExplain(String(button.dataset.triageExplain || "").trim());
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
            await runTriageStateUpdate(
              String(button.dataset.triageId || "").trim(),
              String(button.dataset.triageState || "").trim(),
            );
          }} catch (error) {{
            alert(error.message);
          }} finally {{
            button.disabled = false;
          }}
        }});
      }});

      root.querySelectorAll("[data-triage-note-input]").forEach((field) => {{
        field.addEventListener("input", () => {{
          state.triageNoteDrafts[field.dataset.triageNoteInput] = field.value;
        }});
      }});

      root.querySelectorAll("[data-triage-note-form]").forEach((form) => {{
        form.addEventListener("submit", async (event) => {{
          event.preventDefault();
          const itemId = String(form.dataset.triageNoteForm || "").trim();
          const note = String(new FormData(form).get("note") || "").trim();
          if (!note) {{
            alert("Provide a note before saving.");
            return;
          }}
          const submitButton = form.querySelector("button[type='submit']");
          if (submitButton) {{
            submitButton.disabled = true;
          }}
          try {{
            await api(`/api/triage/${{itemId}}/note`, {{
              method: "POST",
              headers: jsonHeaders,
              body: JSON.stringify({{ note, author: "console" }}),
            }});
            state.triageNoteDrafts[itemId] = "";
            await refreshBoard();
          }} catch (error) {{
            alert(error.message);
          }} finally {{
            if (submitButton) {{
              submitButton.disabled = false;
            }}
          }}
        }});
      }});
    }}

    async function loadStory(identifier) {{
      state.selectedStoryId = identifier;
      state.loading.storyDetail = true;
      renderStories();
      try {{
        const [detail, graph] = await Promise.all([
          api(`/api/stories/${{identifier}}`),
          api(`/api/stories/${{identifier}}/graph`),
        ]);
        state.storyDetails[identifier] = detail;
        state.storyGraph[identifier] = graph;
      }} finally {{
        state.loading.storyDetail = false;
      }}
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
      if (state.loading.storyDetail && selected) {{
        root.innerHTML = [skeletonCard(4), skeletonCard(4), skeletonCard(4)].join("");
        return;
      }}
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
      const storyStatusOptions = ["active", "monitoring", "resolved", "archived"];
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
        <div class="card">
          <div class="mono">story editor</div>
          <div class="panel-sub">Tune the persisted title, summary, and story status without rebuilding the whole workspace snapshot.</div>
          <form id="story-editor-form" data-story-id="${{story.id}}" style="margin-top:12px;">
            <div class="field-grid">
              <label>Story Title<input name="title" value="${{escapeHtml(story.title || "")}}" placeholder="OpenAI Launch Story"></label>
              <label>Story Status
                <select name="status">
                  ${{storyStatusOptions.map((value) => `<option value="${{value}}" ${{(story.status || "active") === value ? "selected" : ""}}>${{value}}</option>`).join("")}}
                </select>
              </label>
            </div>
            <label>Story Summary<textarea name="summary" rows="4" placeholder="Condense why this story matters right now.">${{escapeHtml(story.summary || "")}}</textarea></label>
            <div class="toolbar">
              <button class="btn-primary" type="submit">Save Story</button>
            </div>
          </form>
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

      const storyEditorForm = document.getElementById("story-editor-form");
      if (storyEditorForm) {{
        storyEditorForm.addEventListener("submit", async (event) => {{
          event.preventDefault();
          const form = new FormData(storyEditorForm);
          const payload = {{
            title: String(form.get("title") || "").trim(),
            summary: String(form.get("summary") || "").trim(),
            status: String(form.get("status") || "").trim(),
          }};
          if (!payload.title) {{
            alert("Provide a story title before saving.");
            return;
          }}
          const submitButton = storyEditorForm.querySelector("button[type='submit']");
          if (submitButton) {{
            submitButton.disabled = true;
          }}
          const previousStory = {{
            title: story.title || "",
            summary: story.summary || "",
            status: story.status || "active",
          }};
          if (state.storyDetails[story.id]) {{
            state.storyDetails[story.id] = {{
              ...state.storyDetails[story.id],
              ...payload,
            }};
          }}
          renderStories();
          try {{
            await api(`/api/stories/${{story.id}}`, {{
              method: "PUT",
              headers: jsonHeaders,
              body: JSON.stringify(payload),
            }});
            state.storyMarkdown[story.id] = "";
            pushActionEntry({{
              kind: "story update",
              label: `Updated story ${{payload.title}}`,
              detail: `Story status is now ${{payload.status || "active"}}.`,
              undoLabel: "Restore story",
              undo: async () => {{
                await api(`/api/stories/${{story.id}}`, {{
                  method: "PUT",
                  headers: jsonHeaders,
                  body: JSON.stringify(previousStory),
                }});
                await refreshBoard();
                showToast(`Story restored: ${{previousStory.title}}`, "success");
              }},
            }});
            await refreshBoard();
          }} catch (error) {{
            if (state.storyDetails[story.id]) {{
              state.storyDetails[story.id] = {{
                ...state.storyDetails[story.id],
                ...previousStory,
              }};
            }}
            renderStories();
            alert(error.message);
          }} finally {{
            if (submitButton) {{
              submitButton.disabled = false;
            }}
          }}
        }});
      }}
    }}

    function renderStories() {{
      const root = $("story-list");
      const inlineStats = $("story-stats-inline");
      if (state.loading.board && !state.stories.length) {{
        inlineStats.innerHTML = `<span>loading=stories</span>`;
        root.innerHTML = [skeletonCard(4), skeletonCard(4)].join("");
        $("story-detail").innerHTML = skeletonCard(5);
        return;
      }}
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
      state.loading.board = true;
      renderOverview();
      renderWatches();
      renderWatchDetail();
      renderAlerts();
      renderRoutes();
      renderRouteHealth();
      renderStatus();
      renderTriage();
      renderStories();
      try {{
        const [overview, watches, alerts, routes, routeHealth, status, ops, triage, triageStats, stories] = await Promise.all([
          api("/api/overview"),
          api("/api/watches?include_disabled=true"),
          api("/api/alerts?limit=8"),
          api("/api/alert-routes"),
          api("/api/alert-routes/health?limit=60"),
          api("/api/watch-status"),
          api("/api/ops"),
          api("/api/triage?limit=12&include_closed=true"),
          api("/api/triage/stats"),
          api("/api/stories?limit=6&min_items=2"),
        ]);
        state.overview = overview;
        state.watches = watches;
        state.alerts = alerts;
        state.routes = routes;
        state.routeHealth = routeHealth;
        state.status = status;
        state.ops = ops;
        state.triage = triage;
        state.triageStats = triageStats;
        state.stories = stories;
        if (state.watches.length) {{
          const selectedWatch = state.watches.some((watch) => watch.id === state.selectedWatchId)
            ? state.selectedWatchId
            : state.watches[0].id;
          state.selectedWatchId = selectedWatch;
          state.watchDetails[selectedWatch] = await api(`/api/watches/${{selectedWatch}}`);
        }} else {{
          state.selectedWatchId = "";
        }}
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
      }} finally {{
        state.loading.board = false;
      }}
      renderOverview();
      renderWatches();
      renderWatchDetail();
      renderAlerts();
      renderRoutes();
      renderRouteHealth();
      renderStatus();
      renderTriage();
      renderStories();
      renderCreateWatchDeck();
    }}

    bindCreateWatchDeck();
    bindHeroStageMotion();
    bindCommandPalette();
    renderActionHistory();
    renderCommandPalette();

    $("refresh-all").addEventListener("click", async () => {{
      const button = $("refresh-all");
      button.disabled = true;
      try {{
        await refreshBoard();
        showToast("Command chamber refreshed", "success");
      }} catch (error) {{
        reportError(error, "Refresh chamber");
      }} finally {{
        button.disabled = false;
      }}
    }});
    $("run-due").addEventListener("click", async () => {{
      const button = $("run-due");
      button.disabled = true;
      try {{
        await api("/api/watches/run-due", {{ method: "POST", headers: jsonHeaders, body: JSON.stringify({{ limit: 0 }}) }});
        await refreshBoard();
        showToast("Due missions dispatched", "success");
      }} catch (error) {{
        reportError(error, "Run due missions");
      }} finally {{
        button.disabled = false;
      }}
    }});

    $("create-watch-form").addEventListener("submit", async (event) => {{
      event.preventDefault();
      const formElement = event.target;
      const submitButton = formElement.querySelector("button[type='submit']");
      const draft = collectCreateWatchDraft(formElement);
      state.createWatchDraft = draft;
      persistCreateWatchDraft();
      renderCreateWatchDeck();
      if (!(draft.name.trim() && draft.query.trim())) {{
        showToast("Provide both Name and Query before creating a watch.", "error");
        focusCreateWatchDeck(draft.name.trim() ? "query" : "name");
        return;
      }}
      const alertRules = buildAlertRules({{
        route: draft.route.trim(),
        keyword: draft.keyword.trim(),
        domain: draft.domain.trim(),
        minScore: Number(draft.min_score || 0),
        minConfidence: Number(draft.min_confidence || 0),
      }});
      const payload = {{
        name: draft.name.trim(),
        query: draft.query.trim(),
        schedule: draft.schedule.trim() || "manual",
        platforms: draft.platform.trim() ? [draft.platform.trim()] : null,
        alert_rules: alertRules.length ? alertRules : null,
      }};
      if (submitButton) {{
        submitButton.disabled = true;
      }}
      const optimisticId = `draft-${{Date.now()}}`;
      const optimisticWatch = {{
        id: optimisticId,
        name: payload.name,
        query: payload.query,
        enabled: true,
        platforms: payload.platforms || [],
        sites: draft.domain.trim() ? [draft.domain.trim()] : [],
        schedule: payload.schedule,
        schedule_label: payload.schedule,
        is_due: false,
        next_run_at: "",
        alert_rule_count: Array.isArray(payload.alert_rules) ? payload.alert_rules.length : 0,
        alert_rules: payload.alert_rules || [],
        last_run_at: "",
        last_run_status: "pending",
      }};
      state.watches = [optimisticWatch, ...state.watches];
      state.selectedWatchId = optimisticId;
      state.watchDetails[optimisticId] = optimisticWatch;
      renderWatches();
      renderWatchDetail();
      try {{
        const created = await api("/api/watches", {{ method: "POST", headers: jsonHeaders, body: JSON.stringify(payload) }});
        setCreateWatchDraft(defaultCreateWatchDraft());
        formElement.reset();
        pushActionEntry({{
          kind: "mission create",
          label: `Created ${{payload.name}}`,
          detail: "The new mission can be removed from the recent action log if this was a false start.",
          undoLabel: "Delete mission",
          undo: async () => {{
            await api(`/api/watches/${{created.id}}`, {{ method: "DELETE" }});
            await refreshBoard();
            showToast(`Mission deleted: ${{created.name || created.id}}`, "success");
          }},
        }});
        await refreshBoard();
        showToast(`Watch created: ${{payload.name}}`, "success");
      }} catch (error) {{
        state.watches = state.watches.filter((watch) => watch.id !== optimisticId);
        delete state.watchDetails[optimisticId];
        if (state.selectedWatchId === optimisticId) {{
          state.selectedWatchId = state.watches[0] ? state.watches[0].id : "";
        }}
        renderWatches();
        renderWatchDetail();
        reportError(error, "Create watch");
      }} finally {{
        if (submitButton) {{
          submitButton.disabled = false;
        }}
      }}
    }});

    refreshBoard().catch((error) => {{
      reportError(error, "Console boot failed");
    }});

    document.addEventListener("keydown", (event) => {{
      const target = event.target;
      const tagName = target && target.tagName ? String(target.tagName).toLowerCase() : "";
      const key = String(event.key || "").toLowerCase();
      if ((event.metaKey || event.ctrlKey) && key === "k") {{
        event.preventDefault();
        if (state.commandPalette.open) {{
          closeCommandPalette();
        }} else {{
          openCommandPalette();
        }}
        return;
      }}
      if (key === "escape" && state.commandPalette.open) {{
        event.preventDefault();
        closeCommandPalette();
        return;
      }}
      if (state.commandPalette.open) {{
        return;
      }}
      if (event.metaKey || event.ctrlKey || event.altKey) {{
        return;
      }}
      if (["input", "textarea", "select", "button"].includes(tagName)) {{
        return;
      }}
      if (key === "/") {{
        event.preventDefault();
        focusCreateWatchDeck((state.createWatchDraft && state.createWatchDraft.name.trim()) ? "query" : "name");
        return;
      }}
      if (["1", "2", "3", "4"].includes(key)) {{
        const preset = createWatchPresets[Number(key) - 1];
        if (preset) {{
          event.preventDefault();
          setCreateWatchDraft(preset.values, preset.id);
          showToast(`${{preset.label}} loaded into the mission deck`, "success");
        }}
        return;
      }}
      const visibleItems = getVisibleTriageItems();
      if (!visibleItems.length) {{
        return;
      }}
      const selectedId = state.selectedTriageId || visibleItems[0].id;
      if (key === "j") {{
        event.preventDefault();
        moveTriageSelection(1);
      }} else if (key === "k") {{
        event.preventDefault();
        moveTriageSelection(-1);
      }} else if (key === "v") {{
        event.preventDefault();
        runTriageStateUpdate(selectedId, "verified").catch((error) => alert(error.message));
      }} else if (key === "t") {{
        event.preventDefault();
        runTriageStateUpdate(selectedId, "triaged").catch((error) => alert(error.message));
      }} else if (key === "e") {{
        event.preventDefault();
        runTriageStateUpdate(selectedId, "escalated").catch((error) => alert(error.message));
      }} else if (key === "i") {{
        event.preventDefault();
        runTriageStateUpdate(selectedId, "ignored").catch((error) => alert(error.message));
      }} else if (key === "d") {{
        event.preventDefault();
        runTriageExplain(selectedId).catch((error) => alert(error.message));
      }} else if (key === "n") {{
        event.preventDefault();
        focusTriageNoteComposer(selectedId);
      }}
    }});
  </script>
</body>
</html>"""

