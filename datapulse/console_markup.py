"""HTML surface bundle for the DataPulse command chamber."""

from __future__ import annotations

import json
from typing import Any

from datapulse.console_client import render_console_client_script


def _json_blob(payload: Any) -> str:
    return json.dumps(payload, ensure_ascii=False)


def render_console_html(title: str) -> str:
    initial_state = _json_blob(
        {
            "title": title,
            "sections": [
                "section-intake",
                "section-board",
                "section-cockpit",
                "section-triage",
                "section-story",
                "section-claims",
                "section-report-studio",
                "section-ops",
            ],
        }
    )
    client_script = render_console_client_script(initial_state)
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
      --headline-zh: "PingFang SC", "Hiragino Sans GB", "Noto Sans SC", "Microsoft YaHei", sans-serif;
      --body-zh: "PingFang SC", "Hiragino Sans GB", "Noto Sans SC", "Microsoft YaHei", sans-serif;
      --mono-zh: "SF Mono", "IBM Plex Mono", "PingFang SC", "Microsoft YaHei", monospace;
      --panel-padding: 22px;
      --card-padding: 14px 16px;
      --cluster-padding: 14px;
      --guide-padding: 14px;
      --deck-padding: 14px;
      --control-height: 44px;
      --action-control-height: 36px;
      --context-lens-width: 540px;
      --context-lens-radius: 28px;
      --context-lens-padding: 24px 22px;
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
    body[data-context-lens-open="true"] {{
      overflow: hidden;
    }}
    body[data-density-mode="comfortable"] {{
      --panel-padding: 22px;
      --card-padding: 14px 16px;
      --cluster-padding: 14px;
      --guide-padding: 14px;
      --deck-padding: 14px;
      --control-height: 44px;
      --action-control-height: 36px;
      --context-lens-width: 540px;
      --context-lens-radius: 28px;
      --context-lens-padding: 24px 22px;
    }}
    body[data-density-mode="compact"] {{
      --panel-padding: 20px;
      --card-padding: 14px 15px;
      --cluster-padding: 13px;
      --guide-padding: 13px;
      --deck-padding: 13px;
      --control-height: 44px;
      --action-control-height: 38px;
      --context-lens-width: 680px;
      --context-lens-radius: 24px;
      --context-lens-padding: 22px 20px;
    }}
    body[data-density-mode="touch"] {{
      --panel-padding: 18px;
      --card-padding: 16px;
      --cluster-padding: 14px;
      --guide-padding: 12px;
      --deck-padding: 12px;
      --control-height: 48px;
      --action-control-height: 42px;
      --context-lens-width: 100%;
      --context-lens-radius: 0;
      --context-lens-padding: 20px 18px;
    }}
    body[data-lang="zh"] {{
      font-family: var(--body-zh);
      line-break: strict;
      word-break: keep-all;
    }}
    body[data-lang="zh"] .eyebrow,
    body[data-lang="zh"] .mono,
    body[data-lang="zh"] .metric-label,
    body[data-lang="zh"] .preview-label,
    body[data-lang="zh"] .palette-kicker,
    body[data-lang="zh"] .chip,
    body[data-lang="zh"] .chip-btn,
    body[data-lang="zh"] button,
    body[data-lang="zh"] label {{
      font-family: var(--body-zh);
      letter-spacing: 0.01em;
      text-transform: none;
    }}
    body[data-lang="zh"] .panel-title,
    body[data-lang="zh"] .topbar-copy strong,
    body[data-lang="zh"] .brand-copy strong,
    body[data-lang="zh"] .stage-hud-title,
    body[data-lang="zh"] .context-lens-title,
    body[data-lang="zh"] .workspace-mode-title {{
      font-family: var(--headline-zh);
      letter-spacing: 0;
      text-transform: none;
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
    .topbar {{
      position: sticky;
      top: 14px;
      z-index: 35;
      display: grid;
      grid-template-columns: auto 1fr auto;
      gap: 16px;
      align-items: center;
      padding: 14px 18px;
      border: 1px solid rgba(147, 181, 215, 0.16);
      border-radius: 22px;
      background: rgba(8, 14, 24, 0.78);
      backdrop-filter: blur(14px);
      box-shadow: 0 18px 44px rgba(3, 8, 18, 0.28);
    }}
    .topbar-brand {{
      display: flex;
      align-items: center;
      gap: 12px;
      min-width: 0;
    }}
    .topbar-copy {{
      display: grid;
      gap: 3px;
      min-width: 0;
    }}
    .topbar-copy strong {{
      font-family: var(--headline);
      font-size: 1rem;
      letter-spacing: 0.04em;
      text-transform: uppercase;
    }}
    .topbar-copy span {{
      color: var(--muted);
      font-size: 0.86rem;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }}
    .topbar-nav {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      justify-content: center;
    }}
    .nav-pill {{
      padding: 10px 14px;
      border: 1px solid rgba(147, 181, 215, 0.16);
      background: rgba(127, 228, 255, 0.05);
      color: var(--muted);
      font-size: 0.82rem;
    }}
    .nav-pill.active {{
      color: var(--ink);
      border-color: rgba(127, 228, 255, 0.34);
      background:
        linear-gradient(180deg, rgba(127, 228, 255, 0.16), rgba(127, 228, 255, 0.08));
      box-shadow: inset 0 0 0 1px rgba(127, 228, 255, 0.08);
    }}
    .nav-pill:hover,
    .nav-pill:focus-visible {{
      color: var(--ink);
      border-color: rgba(127, 228, 255, 0.3);
      background: rgba(127, 228, 255, 0.1);
    }}
    .topbar-tools {{
      position: relative;
      display: flex;
      align-items: center;
      justify-content: flex-end;
      gap: 10px;
    }}
    .context-view-dock {{
      display: grid;
      gap: 10px;
      padding: 12px 14px;
      border: 1px solid rgba(147, 181, 215, 0.14);
      border-radius: 20px;
      background:
        linear-gradient(180deg, rgba(10, 18, 31, 0.64), rgba(9, 15, 25, 0.42));
      box-shadow:
        inset 0 0 0 1px rgba(127, 228, 255, 0.03),
        0 10px 24px rgba(3, 8, 18, 0.12);
    }}
    .context-view-dock[hidden] {{
      display: none;
    }}
    .context-view-dock-head {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      align-items: center;
      justify-content: space-between;
    }}
    .context-view-dock-title {{
      color: var(--muted);
      font-size: 0.74rem;
      letter-spacing: 0.06em;
      text-transform: uppercase;
    }}
    .context-view-dock-summary {{
      min-width: 0;
      color: var(--ink);
      font-size: 0.92rem;
      line-height: 1.4;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }}
    .context-view-dock-section {{
      display: grid;
      gap: 8px;
    }}
    .context-view-dock-list {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
    }}
    .context-view-dock-tools {{
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      justify-content: space-between;
      gap: 10px;
      padding-top: 4px;
    }}
    .context-view-dock-copy {{
      min-width: 0;
      max-width: 72ch;
      color: var(--muted);
      font-size: 0.84rem;
      line-height: 1.5;
    }}
    .context-view-dock-actions {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      justify-content: flex-end;
    }}
    .context-view-dock-form {{
      display: grid;
      grid-template-columns: minmax(0, 1fr) auto auto;
      gap: 8px;
      align-items: center;
    }}
    .context-view-dock-form input {{
      min-width: 0;
      padding: 10px 12px;
      font-size: 0.84rem;
    }}
    .topbar-context {{
      position: relative;
      min-width: 0;
    }}
    .context-object-rail {{
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
      align-items: center;
      margin-bottom: 8px;
      color: var(--muted);
      font: 600 0.74rem/1.2 var(--mono);
      letter-spacing: 0.02em;
    }}
    .context-object-step {{
      display: inline-flex;
      align-items: center;
      gap: 7px;
      padding: 3px 8px;
      border-radius: 999px;
      border: 1px solid rgba(127, 228, 255, 0.24);
      background: rgba(127, 228, 255, 0.06);
      min-height: 26px;
      max-width: 210px;
      appearance: none;
      color: inherit;
      cursor: pointer;
      font: inherit;
      text-align: left;
    }}
    .context-object-step-title {{
      opacity: 0.85;
      white-space: nowrap;
    }}
    .context-object-step-value {{
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
      max-width: 130px;
    }}
    .context-object-divider {{
      color: rgba(127, 228, 255, 0.4);
      font-weight: 700;
      margin: 0 1px;
    }}
    .context-chip {{
      max-width: min(360px, 38vw);
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
      padding: 10px 14px;
      font: 700 0.84rem/1.2 var(--body);
      letter-spacing: 0.01em;
      text-transform: none;
    }}
    .context-chip-button {{
      appearance: none;
      cursor: pointer;
      text-align: left;
    }}
    .context-chip-button[aria-expanded="true"] {{
      color: var(--ink);
      border-color: rgba(127, 228, 255, 0.34);
      background:
        linear-gradient(180deg, rgba(127, 228, 255, 0.16), rgba(127, 228, 255, 0.08));
      box-shadow: inset 0 0 0 1px rgba(127, 228, 255, 0.08);
    }}
    .context-lens-backdrop {{
      position: fixed;
      inset: 0;
      z-index: 65;
      display: none;
      align-items: stretch;
      justify-content: flex-end;
      padding: 16px;
      background: rgba(4, 8, 16, 0.6);
      backdrop-filter: blur(12px);
    }}
    .context-lens-backdrop.open {{
      display: flex;
    }}
    .context-lens-shell {{
      width: min(var(--context-lens-width), 100%);
      height: 100%;
      border: 1px solid rgba(147, 181, 215, 0.18);
      border-radius: var(--context-lens-radius);
      background:
        linear-gradient(180deg, rgba(17, 29, 46, 0.98), rgba(8, 14, 24, 0.97));
      box-shadow: 0 30px 80px rgba(3, 8, 18, 0.52);
      overflow: hidden;
    }}
    .context-lens-shell:focus {{
      outline: 2px solid rgba(127, 228, 255, 0.38);
      outline-offset: 0;
    }}
    .context-lens {{
      height: 100%;
      padding: var(--context-lens-padding);
      display: grid;
      gap: 16px;
      align-content: start;
      overflow-y: auto;
    }}
    .context-lens-head {{
      display: flex;
      gap: 14px;
      align-items: start;
      justify-content: space-between;
    }}
    .context-lens-head-copy {{
      min-width: 0;
      display: grid;
      gap: 6px;
    }}
    .context-lens-title {{
      font-family: var(--headline);
      font-size: 0.92rem;
      letter-spacing: 0.08em;
      text-transform: uppercase;
    }}
    .context-lens-close {{
      flex: 0 0 auto;
      min-width: 86px;
    }}
    .context-lens-copy {{
      color: var(--muted);
      font-size: 0.88rem;
      line-height: 1.6;
    }}
    .context-lens-body {{
      display: grid;
      gap: 12px;
    }}
    .context-lens-row {{
      display: grid;
      grid-template-columns: minmax(0, 124px) minmax(0, 1fr);
      gap: 12px;
      align-items: start;
      padding: 12px 14px;
      border-radius: 16px;
      border: 1px solid rgba(147, 181, 215, 0.12);
      background: rgba(127, 228, 255, 0.04);
    }}
    .context-lens-label {{
      color: var(--muted);
      font-size: 0.76rem;
      letter-spacing: 0.06em;
      text-transform: uppercase;
    }}
    .context-lens-value {{
      min-width: 0;
      font-size: 0.92rem;
      line-height: 1.6;
      color: var(--ink);
      word-break: break-word;
    }}
    .context-lens-value.muted {{
      color: var(--muted);
    }}
    .context-lens-value.mono {{
      font-family: var(--mono);
      font-size: 0.84rem;
    }}
    .context-lens-actions {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      padding-top: 8px;
      border-top: 1px solid rgba(147, 181, 215, 0.12);
    }}
    .context-lens-history {{
      display: grid;
      gap: 12px;
    }}
    .context-lens-save {{
      display: grid;
      gap: 12px;
    }}
    .context-save-form {{
      display: grid;
      grid-template-columns: minmax(0, 1fr) auto;
      gap: 10px;
      align-items: center;
    }}
    .context-save-input {{
      min-width: 0;
    }}
    .context-lens-history-head {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      align-items: center;
      justify-content: space-between;
    }}
    .context-lens-history-title {{
      color: var(--muted);
      font-size: 0.76rem;
      letter-spacing: 0.06em;
      text-transform: uppercase;
    }}
    .context-lens-history-list {{
      display: grid;
      gap: 8px;
    }}
    .context-history-item {{
      display: grid;
      gap: 8px;
      padding: 12px;
      border-radius: 14px;
      border: 1px solid rgba(147, 181, 215, 0.12);
      background: rgba(255, 255, 255, 0.03);
    }}
    .context-history-summary {{
      font-size: 0.9rem;
      line-height: 1.6;
      color: var(--ink);
    }}
    .context-history-meta {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      color: var(--muted);
      font-size: 0.8rem;
    }}
    .context-history-url {{
      color: var(--muted);
      font-family: var(--mono);
      font-size: 0.78rem;
      word-break: break-all;
    }}
    .context-history-actions {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
    }}
    .context-lens-saved {{
      display: grid;
      gap: 10px;
    }}
    .palette-trigger {{
      padding: 10px 12px;
      font-size: 0.76rem;
    }}
    .lang-switch {{
      display: inline-flex;
      align-items: center;
      padding: 4px;
      gap: 4px;
      border-radius: 999px;
      border: 1px solid rgba(147, 181, 215, 0.16);
      background: rgba(16, 27, 43, 0.7);
    }}
    .lang-btn {{
      min-width: 68px;
      padding: 9px 12px;
      background: transparent;
      color: var(--muted);
      font-size: 0.76rem;
    }}
    .lang-btn.active {{
      background: linear-gradient(135deg, rgba(127, 228, 255, 0.22), rgba(255, 106, 130, 0.18));
      color: var(--ink);
      box-shadow: inset 0 0 0 1px rgba(127, 228, 255, 0.12);
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
    body[data-lang="zh"] h1 {{
      font-family: var(--headline-zh);
      font-size: clamp(2.3rem, 7vw, 4.6rem);
      line-height: 1.08;
      letter-spacing: -0.02em;
      text-transform: none;
      max-width: 12em;
    }}
    .hero-copy {{
      max-width: 60ch;
      color: var(--muted);
      font-size: 1.05rem;
      line-height: 1.65;
    }}
    .toolbar {{
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      margin-top: 18px;
    }}
    .guide-grid {{
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 12px;
      margin-top: 20px;
    }}
    .guide-card {{
      display: grid;
      gap: 8px;
      padding: var(--guide-padding);
      border-radius: 18px;
      border: 1px solid rgba(147, 181, 215, 0.16);
      background: rgba(12, 20, 34, 0.68);
      box-shadow: inset 0 0 0 1px rgba(127, 228, 255, 0.04);
    }}
    .guide-step {{
      width: 34px;
      height: 34px;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      border-radius: 999px;
      font: 700 12px/1 var(--mono);
      color: var(--ink);
      border: 1px solid rgba(127, 228, 255, 0.26);
      background: linear-gradient(180deg, rgba(127, 228, 255, 0.12), rgba(255, 106, 130, 0.12));
    }}
    button {{
      border: 0;
      cursor: pointer;
      border-radius: 999px;
      padding: 12px 16px;
      min-height: var(--control-height);
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
    .btn-danger {{
      background: rgba(255, 106, 130, 0.14);
      color: #ffd7de;
      box-shadow: inset 0 0 0 1px rgba(255, 106, 130, 0.14);
    }}
    .workspace-mode-shell {{
      display: grid;
      gap: 16px;
      padding: 20px;
      border: 1px solid rgba(147, 181, 215, 0.16);
      border-radius: 24px;
      background:
        linear-gradient(180deg, rgba(13, 21, 35, 0.84), rgba(9, 15, 25, 0.62));
      box-shadow: inset 0 0 0 1px rgba(127, 228, 255, 0.04);
      animation: rise .6s ease-out both;
      animation-delay: .04s;
    }}
    .workspace-mode-head {{
      display: flex;
      flex-wrap: wrap;
      gap: 12px;
      align-items: start;
      justify-content: space-between;
    }}
    .workspace-mode-summary {{
      display: grid;
      gap: 6px;
      max-width: 72ch;
    }}
    .workspace-mode-title {{
      font-family: var(--headline);
      font-size: 1.4rem;
      letter-spacing: 0.03em;
      text-transform: uppercase;
    }}
    .workspace-mode-meta {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      align-items: center;
      justify-content: flex-end;
    }}
    .workspace-mode-grid {{
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 12px;
    }}
    .workspace-mode-card {{
      width: 100%;
      display: grid;
      gap: 14px;
      text-align: left;
      padding: 18px;
      border-radius: 20px;
      border: 1px solid rgba(147, 181, 215, 0.14);
      background: rgba(10, 18, 31, 0.52);
      color: var(--ink);
      box-shadow: inset 0 0 0 1px rgba(127, 228, 255, 0.03);
    }}
    .workspace-mode-card.active {{
      border-color: rgba(127, 228, 255, 0.32);
      background:
        linear-gradient(180deg, rgba(127, 228, 255, 0.12), rgba(255, 106, 130, 0.08)),
        rgba(10, 18, 31, 0.72);
      box-shadow:
        0 14px 34px rgba(3, 8, 18, 0.24),
        inset 0 0 0 1px rgba(127, 228, 255, 0.08);
    }}
    .workspace-mode-card:hover,
    .workspace-mode-card:focus-visible {{
      transform: translateY(-1px);
      border-color: rgba(127, 228, 255, 0.24);
      background: rgba(12, 21, 36, 0.7);
    }}
    .workspace-mode-card-head {{
      display: flex;
      gap: 12px;
      justify-content: space-between;
      align-items: start;
    }}
    .workspace-mode-kicker {{
      color: var(--muted);
      font-size: 0.76rem;
      letter-spacing: 0.08em;
      text-transform: uppercase;
    }}
    .workspace-mode-copy {{
      color: var(--muted);
      font-size: 0.92rem;
      line-height: 1.6;
    }}
    .workspace-mode-modules {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
    }}
    .workspace-mode-module {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      border-radius: 999px;
      padding: 6px 10px;
      border: 1px solid rgba(147, 181, 215, 0.14);
      background: rgba(255, 255, 255, 0.03);
      color: var(--ink);
      font: 700 11px/1 var(--mono);
      text-transform: uppercase;
    }}
    .workspace-mode-foot {{
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      color: var(--muted);
      font-size: 0.76rem;
    }}
    .workspace-mode-group {{
      display: grid;
      gap: 18px;
    }}
    .workspace-mode-group[data-workspace-group="review"] {{
      grid-template-columns: repeat(2, minmax(0, 1fr));
      align-items: start;
    }}
    .workspace-mode-group[hidden] {{
      display: none;
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
    .intake-live-shell {{
      display: grid;
      gap: 12px;
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
      padding: var(--panel-padding);
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
      line-height: 1.6;
    }}
    .stack {{
      display: grid;
      gap: 12px;
    }}
    .card {{
      border: 1px solid var(--line);
      border-radius: 18px;
      padding: var(--card-padding);
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
      padding: 6px 10px;
      font: 700 12px/1 var(--mono);
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
      min-height: var(--action-control-height);
      font-size: 0.76rem;
    }}
    .actions a {{
      display: inline-flex;
      align-items: center;
      justify-content: center;
      border-radius: 999px;
      padding: 9px 12px;
      min-height: var(--action-control-height);
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
    .action-hierarchy {{
      display: grid;
      gap: 8px;
      margin-top: 12px;
    }}
    .action-hierarchy .actions {{
      margin-top: 0;
    }}
    .action-primary-row button,
    .action-primary-row a {{
      min-width: 156px;
      justify-content: center;
    }}
    .action-danger-row {{
      padding-top: 8px;
      border-top: 1px solid rgba(255, 106, 130, 0.12);
    }}
    .action-sheet {{
      display: none;
      margin: 0;
    }}
    .action-sheet-toggle {{
      list-style: none;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      width: 100%;
      padding: 10px 12px;
      min-height: var(--action-control-height);
      border-radius: 999px;
      background: rgba(127, 228, 255, 0.08);
      color: var(--ink);
      font: 700 0.76rem/1 var(--mono);
      letter-spacing: 0.02em;
      cursor: pointer;
      user-select: none;
    }}
    .action-sheet-toggle::before {{
      content: "+";
      font-size: 0.9rem;
      line-height: 1;
    }}
    .action-sheet[open] .action-sheet-toggle::before {{
      content: "-";
    }}
    .action-sheet-toggle::-webkit-details-marker {{
      display: none;
    }}
    .action-sheet-panel {{
      display: grid;
      gap: 8px;
      margin-top: 10px;
      padding-top: 10px;
      border-top: 1px solid rgba(147, 181, 215, 0.12);
    }}
    form {{
      display: grid;
      gap: 12px;
    }}
    .control-cluster {{
      display: grid;
      gap: 10px;
      padding: var(--cluster-padding);
      border-radius: 18px;
      border: 1px solid rgba(147, 181, 215, 0.14);
      background: rgba(10, 18, 31, 0.44);
    }}
    .deck-mode-strip {{
      display: grid;
      gap: 12px;
      padding: 14px;
      border-radius: 18px;
      border: 1px solid rgba(147, 181, 215, 0.14);
      background:
        linear-gradient(180deg, rgba(13, 22, 37, 0.84), rgba(10, 18, 31, 0.58));
      box-shadow: inset 0 0 0 1px rgba(127, 228, 255, 0.04);
    }}
    .deck-mode-head {{
      display: flex;
      flex-wrap: wrap;
      gap: 12px;
      align-items: start;
      justify-content: space-between;
    }}
    .advanced-toggle {{
      white-space: nowrap;
    }}
    .advanced-summary {{
      min-height: 36px;
    }}
    .advanced-summary .chip {{
      background: rgba(255, 255, 255, 0.04);
    }}
    .compact-stack {{
      gap: 8px;
    }}
    .deck-advanced-panel {{
      display: grid;
      gap: 12px;
      overflow: hidden;
      max-height: 1200px;
      opacity: 1;
      transform: translateY(0);
      transition: max-height .24s ease, opacity .2s ease, transform .2s ease, margin .2s ease;
    }}
    .deck-advanced-panel.collapsed {{
      max-height: 0;
      opacity: 0;
      transform: translateY(-8px);
      pointer-events: none;
      margin-top: -8px;
    }}
    .deck-section {{
      display: grid;
      gap: 12px;
      padding: var(--deck-padding);
      border-radius: 18px;
      border: 1px solid rgba(147, 181, 215, 0.14);
      background: rgba(10, 18, 31, 0.5);
    }}
    .deck-section-head {{
      display: flex;
      gap: 12px;
      align-items: start;
    }}
    .step-index {{
      width: 34px;
      height: 34px;
      flex: 0 0 auto;
      border-radius: 12px;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      font: 700 12px/1 var(--mono);
      color: var(--ink);
      border: 1px solid rgba(147, 181, 215, 0.16);
      background: rgba(127, 228, 255, 0.08);
    }}
    .field-hint {{
      display: block;
      margin-top: 2px;
      font: 500 12px/1.45 var(--body);
      letter-spacing: 0;
      text-transform: none;
      color: var(--muted);
    }}
    .section-jumps {{
      margin-top: 2px;
    }}
    .field-grid {{
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 12px;
    }}
    .section-toolbox {{
      display: grid;
      gap: 12px;
      padding: 14px;
      border-radius: 18px;
      border: 1px solid rgba(147, 181, 215, 0.14);
      background:
        linear-gradient(180deg, rgba(11, 19, 31, 0.78), rgba(9, 15, 25, 0.54));
      box-shadow: inset 0 0 0 1px rgba(127, 228, 255, 0.04);
    }}
    .section-toolbox-head {{
      display: flex;
      flex-wrap: wrap;
      gap: 12px;
      align-items: start;
      justify-content: space-between;
    }}
    .section-toolbox-meta {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
    }}
    .search-shell {{
      display: grid;
      grid-template-columns: minmax(0, 1fr) auto;
      gap: 10px;
      align-items: center;
    }}
    .batch-toolbar {{
      display: grid;
      gap: 12px;
    }}
    .batch-toolbar-card {{
      position: sticky;
      top: 92px;
      z-index: 12;
      backdrop-filter: blur(12px);
      background: rgba(9, 15, 26, 0.86);
    }}
    .batch-toolbar-card.selection-live {{
      border-color: rgba(127, 228, 255, 0.24);
      box-shadow:
        var(--shadow),
        inset 0 0 0 1px rgba(127, 228, 255, 0.08);
    }}
    .batch-toolbar-head {{
      display: flex;
      flex-wrap: wrap;
      gap: 12px;
      justify-content: space-between;
      align-items: start;
    }}
    .continuity-shell {{
      display: grid;
      gap: 14px;
    }}
    .section-summary-shell {{
      display: grid;
      gap: 12px;
    }}
    .section-summary-card {{
      display: grid;
      gap: 14px;
      background:
        linear-gradient(180deg, rgba(14, 24, 39, 0.88), rgba(9, 15, 25, 0.72));
      box-shadow: inset 0 0 0 1px rgba(127, 228, 255, 0.04);
    }}
    .section-summary-grid {{
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 10px;
    }}
    .section-summary-signal {{
      display: grid;
      gap: 10px;
      padding: 14px;
      border-radius: 18px;
      border: 1px solid rgba(147, 181, 215, 0.14);
      background: rgba(12, 21, 34, 0.74);
    }}
    .section-summary-signal.ok {{
      border-color: rgba(127, 228, 255, 0.26);
      box-shadow: inset 0 0 0 1px rgba(127, 228, 255, 0.04);
    }}
    .section-summary-signal.hot {{
      border-color: rgba(255, 106, 130, 0.28);
      box-shadow: inset 0 0 0 1px rgba(255, 106, 130, 0.05);
    }}
    .section-summary-kicker {{
      font: 700 11px/1 var(--mono);
      letter-spacing: 0.08em;
      text-transform: uppercase;
      color: var(--muted);
    }}
    .section-summary-title {{
      font-size: 1rem;
      line-height: 1.35;
      color: var(--ink);
    }}
    .section-summary-copy {{
      font-size: 0.84rem;
      line-height: 1.55;
      color: var(--muted);
    }}
    .operator-guidance-surface {{
      display: grid;
      gap: 14px;
      background:
        linear-gradient(180deg, rgba(13, 23, 36, 0.88), rgba(8, 14, 24, 0.78));
      box-shadow:
        var(--shadow),
        inset 0 0 0 1px rgba(127, 228, 255, 0.05);
    }}
    .operator-guidance-grid {{
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 10px;
    }}
    .operator-guidance-column {{
      display: grid;
      gap: 10px;
      padding: 14px;
      border-radius: 18px;
      border: 1px solid rgba(147, 181, 215, 0.14);
      background: rgba(12, 21, 34, 0.72);
    }}
    .operator-guidance-column-head {{
      display: grid;
      gap: 4px;
    }}
    .operator-guidance-column-head .mono {{
      color: var(--muted);
    }}
    .operator-guidance-list {{
      display: grid;
      gap: 10px;
    }}
    .operator-guidance-item {{
      display: grid;
      gap: 8px;
      padding: 12px;
      border-radius: 16px;
      border: 1px solid rgba(147, 181, 215, 0.12);
      background: rgba(7, 14, 24, 0.72);
    }}
    .operator-guidance-item.ok {{
      border-color: rgba(127, 228, 255, 0.26);
      box-shadow: inset 0 0 0 1px rgba(127, 228, 255, 0.04);
    }}
    .operator-guidance-item.hot {{
      border-color: rgba(255, 106, 130, 0.28);
      box-shadow: inset 0 0 0 1px rgba(255, 106, 130, 0.05);
    }}
    .operator-guidance-item-head {{
      display: flex;
      align-items: start;
      justify-content: space-between;
      gap: 10px;
    }}
    .operator-guidance-item-title {{
      font-size: 0.92rem;
      line-height: 1.4;
      color: var(--ink);
    }}
    .operator-guidance-item-copy {{
      font-size: 0.82rem;
      line-height: 1.55;
      color: var(--muted);
    }}
    .continuity-lane {{
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 10px;
    }}
    .continuity-stage {{
      display: grid;
      gap: 10px;
      padding: 14px;
      border-radius: 18px;
      border: 1px solid rgba(147, 181, 215, 0.14);
      background: rgba(12, 21, 34, 0.74);
    }}
    .continuity-stage.ok {{
      border-color: rgba(127, 228, 255, 0.26);
    }}
    .continuity-stage.hot {{
      border-color: rgba(255, 106, 130, 0.28);
    }}
    .continuity-stage-kicker {{
      font: 700 11px/1 var(--mono);
      letter-spacing: 0.08em;
      text-transform: uppercase;
      color: var(--muted);
    }}
    .continuity-stage-title {{
      font-size: 0.98rem;
      line-height: 1.35;
      color: var(--ink);
    }}
    .continuity-stage-copy {{
      font-size: 0.84rem;
      line-height: 1.55;
      color: var(--muted);
    }}
    .continuity-fact-list {{
      display: grid;
      gap: 8px;
    }}
    .continuity-fact {{
      display: flex;
      align-items: start;
      justify-content: space-between;
      gap: 12px;
      font-size: 0.82rem;
      line-height: 1.45;
      color: var(--muted);
    }}
    .continuity-fact strong {{
      flex: 0 0 auto;
      font: 700 12px/1.3 var(--mono);
      color: var(--ink);
      text-align: right;
    }}
    .workbench-shell {{
      display: grid;
      gap: 12px;
    }}
    .workbench-columns {{
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 12px;
      align-items: start;
    }}
    .workbench-meta {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
    }}
    .workbench-story-links {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
    }}
    .checkbox-inline {{
      display: inline-flex;
      align-items: center;
      gap: 8px;
      font: 700 12px/1 var(--mono);
      color: var(--muted);
      letter-spacing: 0.06em;
      text-transform: uppercase;
    }}
    .checkbox-inline input {{
      width: 18px;
      height: 18px;
      margin: 0;
      accent-color: var(--accent-2);
      cursor: pointer;
    }}
    .triage-card-head {{
      display: grid;
      gap: 10px;
      min-width: 0;
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
    .story-workspace-mode-switch {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      align-items: center;
      margin: 12px 0 6px;
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
    body[data-story-workspace-mode="editor"] .story-list {{
      display: none;
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
    body[data-pane-contract="stacked"] .dual-grid,
    body[data-pane-contract="stacked"] .grid,
    body[data-pane-contract="stacked"] .story-grid,
    body[data-pane-contract="stacked"] .story-columns,
    body[data-pane-contract="stacked"] .preview-grid,
    body[data-pane-contract="stacked"] .guide-grid,
    body[data-pane-contract="stacked"] .operator-guidance-grid,
    body[data-pane-contract="stacked"] .section-summary-grid,
    body[data-pane-contract="stacked"] .continuity-lane,
    body[data-pane-contract="stacked"] .workbench-columns,
    body[data-pane-contract="single"] .dual-grid,
    body[data-pane-contract="single"] .grid,
    body[data-pane-contract="single"] .story-grid,
    body[data-pane-contract="single"] .story-columns,
    body[data-pane-contract="single"] .preview-grid,
    body[data-pane-contract="single"] .guide-grid,
    body[data-pane-contract="single"] .operator-guidance-grid,
    body[data-pane-contract="single"] .section-summary-grid,
    body[data-pane-contract="single"] .continuity-lane,
    body[data-pane-contract="single"] .workbench-columns {{
      grid-template-columns: 1fr;
    }}
    body[data-modal-presentation="sheet"] .context-lens-backdrop {{
      align-items: flex-end;
      justify-content: center;
      padding: 12px;
    }}
    body[data-modal-presentation="sheet"] .context-lens-shell {{
      width: min(var(--context-lens-width), 100%);
      height: min(84vh, 780px);
      border-bottom-left-radius: 0;
      border-bottom-right-radius: 0;
    }}
    body[data-modal-presentation="fullscreen"] .context-lens-backdrop {{
      padding: 0;
      align-items: stretch;
      justify-content: stretch;
    }}
    body[data-modal-presentation="fullscreen"] .context-lens-shell {{
      width: 100%;
      height: 100%;
      border-radius: 0;
      border-left: 0;
      border-right: 0;
    }}
    body[data-modal-presentation="fullscreen"] .palette-backdrop {{
      padding: 0;
      align-items: stretch;
      justify-content: stretch;
    }}
    body[data-modal-presentation="fullscreen"] .palette-shell {{
      width: 100%;
      height: 100%;
      display: grid;
      grid-template-rows: auto minmax(0, 1fr);
      border-radius: 0;
    }}
    body[data-modal-presentation="fullscreen"] .palette-list {{
      max-height: none;
    }}
    body[data-action-sheet-mode="sheet"] [data-card-action-secondary],
    body[data-action-sheet-mode="sheet"] [data-card-action-danger] {{
      display: none;
    }}
    body[data-action-sheet-mode="sheet"] .action-sheet {{
      display: grid;
    }}
    body[data-action-sheet-mode="sheet"] .action-sheet-toggle {{
      width: 100%;
    }}
    @keyframes rise {{
      from {{ opacity: 0; transform: translateY(12px); }}
      to {{ opacity: 1; transform: translateY(0); }}
    }}
    @keyframes shimmer {{
      to {{ transform: translateX(100%); }}
    }}
    @media (max-width: 1100px) {{
      .topbar {{ grid-template-columns: 1fr; }}
      .topbar-nav {{
        justify-content: start;
        flex-wrap: nowrap;
        overflow-x: auto;
        padding-bottom: 2px;
        scrollbar-width: none;
      }}
      .topbar-nav::-webkit-scrollbar {{ display: none; }}
      .workspace-mode-grid {{ grid-template-columns: 1fr; }}
      .workspace-mode-group[data-workspace-group="review"] {{
        grid-template-columns: 1fr;
      }}
      .hero, .grid, .dual-grid {{ grid-template-columns: 1fr; }}
      .hero-main {{ order: 0; }}
      .hero-side {{ order: 1; }}
      .story-grid, .story-columns {{ grid-template-columns: 1fr; }}
      .preview-grid, .guide-grid, .operator-guidance-grid, .section-summary-grid {{ grid-template-columns: 1fr; }}
      .batch-toolbar-card {{ top: 152px; }}
    }}
    @media (max-width: 760px) {{
      .shell {{ padding: 16px; }}
      .topbar {{
        top: 10px;
        padding: 12px 14px;
      }}
      .topbar-copy span {{ white-space: normal; }}
      .signal-strip, .field-grid {{ grid-template-columns: 1fr 1fr; }}
      .topbar-tools {{ flex-wrap: wrap; justify-content: start; }}
      .topbar-context {{ width: 100%; }}
      .context-view-dock-tools {{
        flex-direction: column;
        align-items: start;
      }}
      .context-view-dock-actions {{
        justify-content: start;
      }}
      .context-chip-button {{ max-width: 100%; width: 100%; }}
      .context-lens-backdrop {{
        padding: 12px;
      }}
      .context-lens-shell {{
        width: min(100%, 520px);
        border-radius: 24px;
      }}
      .continuity-lane,
      .operator-guidance-grid,
      .section-summary-grid,
      .workbench-columns {{
        grid-template-columns: 1fr;
      }}
      .context-chip {{ max-width: 100%; }}
      .hero-main, .hero-side, .panel {{ border-radius: 22px; }}
      .hero-main, .hero-side, .panel {{ padding: 18px; }}
      h1 {{
        max-width: none;
        font-size: clamp(2.2rem, 11vw, 3.3rem);
        line-height: 1.02;
      }}
      body[data-lang="zh"] h1 {{
        font-size: clamp(2rem, 10vw, 3.1rem);
        line-height: 1.14;
      }}
      .hero-copy {{ font-size: 0.98rem; }}
      .hero-stage {{ height: 150px; }}
      .stage-ring {{ top: 24px; bottom: 20px; width: 124px; }}
      .stage-globe {{ width: 112px; height: 112px; top: 22px; }}
      .stage-console {{ width: 88px; height: 42px; bottom: 18px; }}
      .guide-grid {{ gap: 10px; }}
      .workspace-mode-shell {{ padding: 14px; }}
      .workspace-mode-card {{ padding: 14px; }}
      .guide-card, .deck-section, .control-cluster {{ padding: 12px; }}
      .deck-mode-strip {{ padding: 12px; }}
      .batch-toolbar-card {{ top: 132px; }}
    }}
    @media (max-width: 560px) {{
      .signal-strip, .field-grid {{ grid-template-columns: 1fr; }}
      .toolbar {{ flex-direction: column; }}
      .search-shell {{ grid-template-columns: 1fr; }}
      .toolbar > button,
      .toolbar > a,
      .actions > button,
      .actions > a {{
        width: 100%;
      }}
      .topbar-tools {{ width: 100%; }}
      .context-lens-backdrop {{
        padding: 10px;
      }}
      .context-lens-shell {{
        width: 100%;
        border-radius: 22px;
      }}
      .continuity-stage {{
        padding: 12px;
      }}
      .context-lens-row {{
        grid-template-columns: 1fr;
        gap: 4px;
      }}
      .context-view-dock-form {{
        grid-template-columns: 1fr;
      }}
      .context-save-form {{
        grid-template-columns: 1fr;
      }}
      .palette-trigger {{ flex: 1 1 auto; }}
      .lang-switch {{ margin-left: auto; }}
      .hero-stage {{ display: none; }}
      .nav-pill {{ white-space: nowrap; }}
      .batch-toolbar-card {{ top: 122px; }}
    }}
  </style>
</head>
<body data-responsive-viewport="desktop" data-density-mode="comfortable" data-pane-contract="split" data-modal-presentation="side-panel" data-action-sheet-mode="inline">
  <div class="shell">
    <header class="topbar">
      <div class="topbar-brand">
        <span class="dot"></span>
        <div class="topbar-copy">
          <strong id="topbar-title">DataPulse Operations Console</strong>
          <span id="topbar-subtitle">Lifecycle rail | Intake -&gt; Missions -&gt; Review -&gt; Delivery</span>
        </div>
      </div>
      <nav class="topbar-nav" aria-label="Primary Lifecycle Rail">
        <button class="nav-pill" id="nav-intake" type="button" data-jump-target="section-intake" data-workspace-mode="intake">Intake</button>
        <button class="nav-pill" id="nav-missions" type="button" data-jump-target="section-board" data-workspace-mode="missions">Missions</button>
        <button class="nav-pill" id="nav-review" type="button" data-jump-target="section-triage" data-workspace-mode="review">Review</button>
        <button class="nav-pill" id="nav-delivery" type="button" data-jump-target="section-ops" data-workspace-mode="delivery">Delivery</button>
      </nav>
    <div class="topbar-tools">
        <div class="topbar-context" id="context-shell">
          <div class="context-object-rail" id="context-object-rail" data-context-object-rail>
            <button class="context-object-step" type="button" data-context-object-step="mission" data-context-object-id="" data-context-object-section="section-board">
              <span class="context-object-step-title">Mission</span>
              <span class="context-object-step-value" data-fit-text="context-object-value" data-fit-fallback="18">Not set</span>
            </button>
            <span class="context-object-divider">→</span>
            <button class="context-object-step" type="button" data-context-object-step="evidence" data-context-object-id="" data-context-object-section="section-triage">
              <span class="context-object-step-title">Evidence</span>
              <span class="context-object-step-value" data-fit-text="context-object-value" data-fit-fallback="18">Not set</span>
            </button>
            <span class="context-object-divider">→</span>
            <button class="context-object-step" type="button" data-context-object-step="story" data-context-object-id="" data-context-object-section="section-story">
              <span class="context-object-step-title">Story</span>
              <span class="context-object-step-value" data-fit-text="context-object-value" data-fit-fallback="18">Not set</span>
            </button>
            <span class="context-object-divider">→</span>
            <button class="context-object-step" type="button" data-context-object-step="report" data-context-object-id="" data-context-object-section="section-report-studio">
              <span class="context-object-step-title">Report</span>
              <span class="context-object-step-value" data-fit-text="context-object-value" data-fit-fallback="18">Not set</span>
            </button>
            <span class="context-object-divider">→</span>
            <button class="context-object-step" type="button" data-context-object-step="route" data-context-object-id="" data-context-object-section="section-ops">
              <span class="context-object-step-title">Route</span>
              <span class="context-object-step-value" data-fit-text="context-object-value" data-fit-fallback="18">Not set</span>
            </button>
          </div>
          <button class="chip context-chip context-chip-button" id="context-summary" type="button" aria-expanded="false" aria-haspopup="dialog" aria-controls="context-lens-shell" data-fit-text="context-summary" data-fit-fallback="28">Intake | Mission intake</button>
        </div>
        <button class="btn-secondary palette-trigger" id="palette-open" type="button">Command Palette</button>
        <button class="btn-secondary" id="context-reset" type="button">Reset Context</button>
        <div class="lang-switch" id="language-switch" aria-label="Language Switch">
          <button class="lang-btn active" id="lang-en" type="button" data-lang="en">EN</button>
          <button class="lang-btn" id="lang-zh" type="button" data-lang="zh">简中</button>
        </div>
      </div>
    </header>

    <div class="context-view-dock" id="context-view-dock" hidden></div>

    <div class="workspace-mode-group" data-workspace-group="intake">
      <section class="hero" id="section-intake">
      <div class="hero-main" id="hero-main">
        <div id="intake-hero-onboarding">
          <div class="eyebrow" id="hero-eyebrow"><span class="dot"></span> Guided Analyst Workflow</div>
          <h1 id="hero-title">Run Missions, Review Signal, Publish Stories</h1>
          <p class="hero-copy" id="hero-copy">Start with one mission draft, run it from the board, triage the inbox, promote verified evidence into a story, then wire a route when delivery should turn on.</p>
          <div class="toolbar">
            <button class="btn-primary" id="refresh-all">Refresh Console</button>
            <button class="btn-secondary" id="run-due">Run Due Missions</button>
            <button class="btn-secondary" id="jump-watch-board" type="button" data-jump-target="section-board">Open Mission Board</button>
          </div>
          <div class="guide-grid">
            <div class="guide-card">
              <div class="guide-step">01</div>
              <div class="mono" id="guide-step-1-title">Draft Mission</div>
              <div class="panel-sub" id="guide-step-1-copy">Use a preset, clone an existing watch, or enter just Name + Query to create the first watch.</div>
            </div>
            <div class="guide-card">
              <div class="guide-step">02</div>
              <div class="mono" id="guide-step-2-title">Run And Inspect</div>
              <div class="panel-sub" id="guide-step-2-copy">Mission Board and Cockpit run the watch, show results, and expose alert rules before review work starts.</div>
            </div>
            <div class="guide-card">
              <div class="guide-step">03</div>
              <div class="mono" id="guide-step-3-title">Triage And Promote</div>
              <div class="panel-sub" id="guide-step-3-copy">Triage reviews inbox items, captures analyst notes, and promotes verified evidence into story drafts.</div>
            </div>
            <div class="guide-card">
              <div class="guide-step">04</div>
              <div class="mono" id="guide-step-4-title">Set Route And Watch Delivery</div>
              <div class="panel-sub" id="guide-step-4-copy">Route Manager creates reusable sinks; mission alert rules attach them when stories are ready to notify downstream.</div>
            </div>
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
        <div class="intake-live-shell" id="intake-hero-live" hidden></div>
      </div>
      <aside class="hero-side">
        <div id="intake-side-onboarding">
          <div class="guide-card">
            <div class="card-top">
              <div>
                <div class="mono" id="guide-kicker">Operator Guidance</div>
                <h2 class="panel-title" id="guide-panel-title">Browser Lifecycle</h2>
              </div>
              <span class="chip ok" id="guide-chip">Mission -> Triage -> Story -> Route</span>
            </div>
            <div class="panel-sub" id="guide-panel-copy">Create or clone a mission here. The board runs it, the triage queue reviews incoming evidence, stories promote verified signal, and routes turn delivery on.</div>
            <div class="shortcut-strip">
              <span class="chip" id="shortcut-focus">/ focus draft</span>
              <span class="chip" id="shortcut-preset">1-4 load preset</span>
              <span class="chip" id="shortcut-submit">Cmd/Ctrl+Enter deploy</span>
            </div>
            <div class="chip-row section-jumps">
              <button class="chip-btn" id="jump-cockpit" type="button" data-jump-target="section-cockpit">Cockpit</button>
              <button class="chip-btn" id="jump-triage" type="button" data-jump-target="section-triage">Triage</button>
              <button class="chip-btn" id="jump-story" type="button" data-jump-target="section-story">Stories</button>
              <button class="chip-btn" id="jump-ops" type="button" data-jump-target="section-ops">Ops</button>
            </div>
            <div class="chip-row section-jumps" id="story-view-jumps"></div>
          </div>
        </div>
        <div class="intake-live-shell" id="intake-side-live" hidden></div>
        <div class="panel-head">
          <div>
            <div class="panel-title" id="deploy-title">Deploy Mission</div>
            <div class="panel-sub" id="deploy-copy">Create one watch, add optional scope, then decide whether alert routing is needed.</div>
          </div>
        </div>
        <div class="control-cluster" id="create-watch-preset-panel">
          <div class="mono" id="preset-title">Mission Modes</div>
          <div class="panel-sub" id="preset-copy">Start from an archetype when the workflow is familiar, then only adjust the fields that matter.</div>
          <div class="chip-row" id="create-watch-presets"></div>
        </div>
        <form id="create-watch-form">
          <div class="deck-section">
            <div class="deck-section-head">
              <span class="step-index">01</span>
              <div>
                <div class="mono" id="deck-step-1-title">Required Mission Input</div>
                <div class="panel-sub" id="deck-step-1-copy">Name and query define the watch. Everything else can be layered on later.</div>
              </div>
            </div>
            <div class="field-grid">
              <label><span id="label-name">Name</span><input id="input-name" name="name" list="mission-name-options-list" placeholder="Launch Ops" required><span class="field-hint" id="hint-name">Use a short operator-facing label.</span></label>
              <label><span id="label-query">Query</span><input id="input-query" name="query" list="query-options-list" placeholder="OpenAI launch" required><span class="field-hint" id="hint-query">Describe the signal you want tracked.</span></label>
            </div>
          </div>
          <div class="deck-mode-strip">
            <div class="deck-mode-head">
              <div>
                <div class="mono" id="deck-advanced-title">Keep It Simple First</div>
                <div class="panel-sub" id="deck-advanced-copy">Most missions only need Name and Query. Open advanced settings only when you need scope or alert delivery.</div>
              </div>
              <button class="btn-secondary advanced-toggle" id="create-watch-advanced-toggle" type="button">Show Advanced</button>
            </div>
            <div class="chip-row advanced-summary" id="create-watch-advanced-summary"></div>
          </div>
          <div class="deck-advanced-panel" id="create-watch-advanced-panel">
          <div class="deck-section">
            <div class="deck-section-head">
              <span class="step-index">02</span>
              <div>
                <div class="mono" id="deck-step-2-title">Scope And Cadence</div>
                <div class="panel-sub" id="deck-step-2-copy">Use schedule and platform to narrow the mission only when you already know the operating lane.</div>
              </div>
            </div>
            <div class="field-grid">
              <label><span id="label-schedule">Schedule</span><input id="input-schedule" name="schedule" list="schedule-options-list" placeholder="@hourly / interval:15m"><span class="field-hint" id="hint-schedule">Manual is fine for first exploration.</span></label>
              <label><span id="label-platform">Platform</span><input id="input-platform" name="platform" list="platform-options-list" placeholder="twitter"><span class="field-hint" id="hint-platform">Leave empty for broader discovery.</span></label>
            </div>
            <label><span id="label-domain">Alert Domain</span><input id="input-domain" name="domain" list="domain-options-list" placeholder="openai.com"><span class="field-hint" id="hint-domain">Optional domain guard for tighter recall.</span></label>
            <div class="stack compact-stack">
              <div class="mono" id="schedule-lanes-title">Schedule Lanes</div>
              <div class="chip-row" id="create-watch-schedule-picks"></div>
            </div>
            <div class="stack compact-stack">
              <div class="mono" id="platform-lanes-title">Platform Lanes</div>
              <div class="chip-row" id="create-watch-platform-picks"></div>
            </div>
          </div>
          <div class="deck-section">
            <div class="deck-section-head">
              <span class="step-index">03</span>
              <div>
                <div class="mono" id="deck-step-3-title">Optional Alert Gate</div>
                <div class="panel-sub" id="deck-step-3-copy">Attach delivery only when the mission is ready to trigger downstream action.</div>
              </div>
            </div>
            <div class="field-grid">
              <label><span id="label-route">Alert Route</span><input id="input-route" name="route" list="route-options-list" placeholder="ops-webhook"><span class="field-hint" id="hint-route">Choose a named route when the watch should notify someone.</span></label>
              <label><span id="label-keyword">Alert Keyword</span><input id="input-keyword" name="keyword" list="keyword-options-list" placeholder="launch"><span class="field-hint" id="hint-keyword">Use a high-signal term to reduce noise.</span></label>
            </div>
            <div class="stack compact-stack">
              <div class="mono" id="route-snap-title">Route Snap</div>
              <div class="chip-row" id="create-watch-route-picks"></div>
            </div>
            <div class="field-grid">
              <label><span id="label-score">Min Score</span><input id="input-score" name="min_score" list="score-options-list" placeholder="70" inputmode="numeric"><span class="field-hint" id="hint-score">Use when you only want stronger ranked hits.</span></label>
              <label><span id="label-confidence">Min Confidence</span><input id="input-confidence" name="min_confidence" list="confidence-options-list" placeholder="0.8" inputmode="decimal"><span class="field-hint" id="hint-confidence">Use when analyst quality matters more than coverage.</span></label>
            </div>
          </div>
          </div>
          <div class="toolbar">
            <button class="btn-primary" id="create-watch-submit" type="submit">Create Watch</button>
            <button class="btn-secondary" id="create-watch-clear" type="button">Reset Draft</button>
          </div>
          <div class="panel-sub" id="create-watch-feedback">Required fields: `Name` and `Query`. Use `/` to focus the mission deck.</div>
        </form>
        <datalist id="mission-name-options-list"></datalist>
        <datalist id="query-options-list"></datalist>
        <datalist id="schedule-options-list"></datalist>
        <datalist id="platform-options-list"></datalist>
        <datalist id="domain-options-list"></datalist>
        <datalist id="route-options-list"></datalist>
        <datalist id="keyword-options-list"></datalist>
        <datalist id="score-options-list"></datalist>
        <datalist id="confidence-options-list"></datalist>
        <div class="section-summary-shell" id="intake-section-summary"></div>
        <div class="card mission-preview" id="create-watch-preview"></div>
        <div class="card" id="create-watch-suggestions"></div>
        <div class="control-cluster" id="create-watch-clone-panel">
          <div class="mono" id="clone-title">Clone Existing Mission</div>
          <div class="panel-sub" id="clone-copy">Fork an existing watch when the current mission is only a variation in route, threshold, or query wording.</div>
          <div class="chip-row" id="create-watch-clones"></div>
        </div>
        <div class="control-cluster">
          <div class="mono" id="actions-title">Recent Actions</div>
          <div class="panel-sub" id="actions-copy">Every reversible mutation stays here briefly so you can undo false starts without losing flow.</div>
          <div class="action-log" id="console-action-history"></div>
        </div>
      </aside>
    </section>
    </div>

    <section class="workspace-mode-shell" id="workspace-mode-shell" hidden></section>

    <div class="workspace-mode-group" data-workspace-group="missions" hidden>
    <section class="dual-grid">
      <article class="panel" id="section-board">
        <div class="panel-head">
          <div>
            <h2 class="panel-title" id="board-title">Mission Board</h2>
            <div class="panel-sub" id="board-copy">Run missions and keep cockpit handoff facts close before review starts.</div>
          </div>
        </div>
        <div class="section-summary-shell" id="board-section-summary"></div>
        <div class="stack" id="watch-list"></div>
      </article>

      <article class="panel" id="section-cockpit">
        <div class="panel-head">
          <div>
            <h2 class="panel-title" id="cockpit-title">Mission Cockpit</h2>
            <div class="panel-sub" id="cockpit-copy">Open one mission to inspect runs, review continuity, and delivery state in one cockpit.</div>
          </div>
        </div>
        <div class="section-summary-shell" id="cockpit-section-summary"></div>
        <div class="stack" id="watch-detail"></div>
      </article>
    </section>
    </div>

    <div class="workspace-mode-group" data-workspace-group="review" hidden>
    <section class="panel" id="section-triage">
      <div class="panel-head">
        <div>
          <h2 class="panel-title" id="triage-title">Triage Queue</h2>
          <div class="panel-sub" id="triage-copy">Review evidence with one selected workbench and a visible story handoff.</div>
        </div>
      </div>
      <div class="meta" id="triage-stats-inline"></div>
      <div class="section-summary-shell" id="triage-section-summary"></div>
      <div class="stack" id="triage-list"></div>
    </section>

    <section class="panel" id="section-story">
      <div class="panel-head">
        <div>
          <h2 class="panel-title" id="story-title">Story Workspace</h2>
          <div class="panel-sub" id="story-copy">Keep evidence, editing, and delivery readiness visible around the same story.</div>
        </div>
      </div>
      <div class="meta" id="story-stats-inline"></div>
      <div class="story-workspace-mode-switch" id="story-workspace-mode-switch">
        <span class="mono" id="story-mode-switch-label"></span>
        <button class="chip-btn" id="story-mode-board-button" type="button" data-story-workspace-mode="board"></button>
        <button class="chip-btn" id="story-mode-editor-button" type="button" data-story-workspace-mode="editor"></button>
      </div>
      <div class="section-summary-shell" id="story-section-summary"></div>
      <div class="control-cluster" id="story-intake-shell">
        <div class="deck-mode-head">
          <div>
            <div class="mono" id="story-intake-title">Story Intake</div>
            <div class="panel-sub" id="story-intake-copy">Capture a manual brief when a story should exist before clustering catches up, then refine it inside the workspace.</div>
          </div>
          <span class="chip ok" id="story-intake-mode">Editable</span>
        </div>
        <div class="card" id="story-intake-deck"></div>
      </div>
      <div class="story-grid">
        <div class="story-list" id="story-list"></div>
        <div class="story-detail" id="story-detail"></div>
      </div>
    </section>

    <section class="panel" id="section-claims">
      <div class="panel-head">
        <div>
          <h2 class="panel-title" id="claims-title">Claim Composer</h2>
          <div class="panel-sub" id="claims-copy">Compose source-bound claims and attach them to report sections without leaving the review lane.</div>
        </div>
      </div>
      <div class="stack" id="claim-composer-shell"></div>
    </section>

    <section class="panel" id="section-report-studio">
      <div class="panel-head">
        <div>
          <h2 class="panel-title" id="report-studio-title">Report Studio</h2>
          <div class="panel-sub" id="report-studio-copy">Inspect report sections, quality guardrails, and export previews over persisted report objects.</div>
        </div>
      </div>
      <div class="stack" id="report-studio-shell"></div>
    </section>
    </div>

    <div class="workspace-mode-group" data-workspace-group="delivery" hidden>
    <section class="grid">
      <article class="panel" id="section-ops">
        <div class="panel-head">
          <div>
            <h2 class="panel-title" id="ops-title">Ops Snapshot</h2>
            <div class="panel-sub" id="ops-copy">Watch alerting missions, ready stories, route delivery, and recent failures in one slice.</div>
          </div>
        </div>
        <div class="section-summary-shell" id="ops-section-summary"></div>
        <div class="status-shell" id="status-card"></div>
      </article>

      <article class="panel">
        <div class="panel-head">
          <div>
            <h2 class="panel-title" id="ai-surface-title">AI Assistance Surfaces</h2>
            <div class="panel-sub" id="ai-surface-copy">Inspect the same governed AI projection facts that CLI and MCP expose, without creating browser-only AI state.</div>
          </div>
          <span class="chip" id="ai-surface-mode">Read-only</span>
        </div>
        <div class="stack" id="ai-surface-shell"></div>
      </article>

      <article class="panel">
        <div class="panel-head">
          <div>
            <h2 class="panel-title" id="alert-stream-title">Alert Stream</h2>
            <div class="panel-sub" id="alert-stream-copy">Read alert events beside route editing and health, not in a detached feed.</div>
          </div>
          <span class="chip" id="alert-stream-mode">Events read-only</span>
        </div>
        <div class="stack" id="alert-list"></div>
        <div class="control-cluster" id="route-manager-shell">
          <div class="deck-mode-head">
            <div>
              <div class="mono" id="route-manager-title">Route Manager</div>
              <div class="panel-sub" id="route-manager-copy">Create named delivery sinks once, then reuse them across missions without retyping webhook or chat details.</div>
            </div>
            <span class="chip ok" id="route-manager-mode">Editable</span>
          </div>
          <div class="card" id="route-deck"></div>
          <div class="stack" id="route-list"></div>
        </div>
      </article>

      <article class="panel">
        <div class="panel-head">
          <div>
            <h2 class="panel-title" id="distribution-title">Distribution Health</h2>
            <div class="panel-sub" id="distribution-copy">See whether named delivery routes are healthy and which upstream work is feeding them.</div>
          </div>
          <span class="chip" id="distribution-mode">Read-only</span>
        </div>
        <div class="stack" id="route-health"></div>
      </article>

      <article class="panel">
        <div class="panel-head">
          <div>
            <h2 class="panel-title" id="delivery-workspace-title">Delivery Workspace</h2>
            <div class="panel-sub" id="delivery-workspace-copy">Subscribe to persisted outputs, inspect one report package, and dispatch it through named routes without leaving the shell.</div>
          </div>
          <span class="chip ok" id="delivery-workspace-mode">Editable</span>
        </div>
        <div class="stack" id="delivery-workspace-shell"></div>
      </article>
    </section>
    </div>

    <div class="footer-note" id="footer-note">The browser is the operating surface. CLI and MCP remain first-class control planes.</div>
  </div>
  <div class="toast-rack" id="toast-rack" aria-live="polite" aria-atomic="false"></div>
  <div class="context-lens-backdrop" id="context-lens-backdrop" hidden>
    <div class="context-lens-shell" id="context-lens-shell" role="dialog" aria-modal="true" aria-labelledby="context-lens-title" aria-describedby="context-lens-copy" tabindex="-1">
      <div class="context-lens" id="context-lens">
        <div class="context-lens-head">
          <div class="context-lens-head-copy">
            <div class="context-lens-title" id="context-lens-title">Workspace Context</div>
            <div class="context-lens-copy" id="context-lens-copy">See the current section, active filters, and save or share the current workspace state.</div>
          </div>
          <button class="btn-secondary context-lens-close" id="context-lens-close" type="button">Close</button>
        </div>
        <div class="context-lens-body" id="context-lens-body"></div>
        <div class="context-lens-save">
          <div class="context-lens-history-head">
            <div class="context-lens-history-title" id="context-save-title">Save Current View</div>
          </div>
          <form class="context-save-form" id="context-save-form">
            <input class="context-save-input" id="context-save-name" type="text" maxlength="72" placeholder="Ops desk / Escalations">
            <button class="btn-secondary" id="context-save-submit" type="submit">Save View</button>
          </form>
        </div>
        <div class="context-lens-saved" id="context-lens-saved"></div>
        <div class="context-lens-history" id="context-lens-history"></div>
        <div class="context-lens-actions">
          <button class="btn-secondary" id="context-open-section" type="button">Open Section</button>
          <button class="btn-secondary" id="context-copy-link" type="button">Copy Link</button>
        </div>
      </div>
    </div>
  </div>
  <div class="palette-backdrop" id="command-palette">
    <div class="palette-shell">
      <div class="palette-head">
        <input class="palette-input" id="command-palette-input" type="text" placeholder="Search actions, missions, stories, or routes">
      </div>
      <div class="palette-list" id="command-palette-list"></div>
    </div>
  </div>

        <script>
{client_script}
    </script>
</body>
</html>"""
