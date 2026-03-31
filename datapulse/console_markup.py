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
    body[data-pane-contract="stacked"] .continuity-lane,
    body[data-pane-contract="stacked"] .workbench-columns,
    body[data-pane-contract="single"] .dual-grid,
    body[data-pane-contract="single"] .grid,
    body[data-pane-contract="single"] .story-grid,
    body[data-pane-contract="single"] .story-columns,
    body[data-pane-contract="single"] .preview-grid,
    body[data-pane-contract="single"] .guide-grid,
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
      .preview-grid, .guide-grid {{ grid-template-columns: 1fr; }}
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
        <div class="stack" id="watch-list"></div>
      </article>

      <article class="panel" id="section-cockpit">
        <div class="panel-head">
          <div>
            <h2 class="panel-title" id="cockpit-title">Mission Cockpit</h2>
            <div class="panel-sub" id="cockpit-copy">Open one mission to inspect runs, review continuity, and delivery state in one cockpit.</div>
          </div>
        </div>
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
    const initial = {initial_state};
    const state = {{
      watches: [],
      watchDetails: {{}},
      watchResultFilters: {{}},
      consoleOverflowEvidence: null,
      consoleOverflowEvidenceSignature: "",
      selectedWatchId: "",
      watchSearch: "",
      watchUrlFocusPending: false,
      alerts: [],
      routes: [],
      routeSearch: "",
      routeDraft: null,
      routeEditingId: "",
      routeAdvancedOpen: null,
      routeHealth: [],
      deliverySubscriptions: [],
      deliveryDispatchRecords: [],
      deliveryDraft: null,
      selectedDeliverySubscriptionId: "",
      deliveryPackageAudits: {{}},
      deliveryPackageErrors: {{}},
      deliveryPackageProfileIds: {{}},
      digestConsole: null,
      digestProfileDraft: null,
      digestDispatchResult: [],
      digestDispatchError: "",
      contextRouteName: "",
      contextRouteSection: "",
      status: null,
      ops: null,
      aiSurfacePrechecks: {{}},
      aiSurfaceProjections: {{}},
      overview: null,
      activeSectionId: "section-intake",
      activeWorkspaceMode: "intake",
      triage: [],
      triageStats: null,
      triageFilter: "open",
      triageSearch: "",
      triagePinnedIds: [],
      triageUrlFocusPending: false,
      selectedTriageId: "",
      selectedTriageIds: [],
      triageBulkBusy: false,
      triageExplain: {{}},
      triageNoteDrafts: {{}},
      stories: [],
      storyDraft: null,
      storySearch: "",
      storyFilter: "all",
      storySort: "attention",
      storyWorkspaceMode: "board",
      storyUrlFocusPending: false,
      selectedStoryIds: [],
      storyBulkBusy: false,
      storyDetails: {{}},
      storyGraph: {{}},
      storyMarkdown: {{}},
      selectedStoryId: "",
      reportBriefs: [],
      claimCards: [],
      citationBundles: [],
      reportSections: [],
      reports: [],
      exportProfiles: [],
      reportCompositions: {{}},
      reportMarkdown: {{}},
      selectedClaimId: "",
      selectedReportId: "",
      selectedReportSectionId: "",
      createWatchDraft: null,
      createWatchEditingId: "",
      createWatchAdvancedOpen: null,
      createWatchPresetId: "",
      createWatchSuggestions: null,
      createWatchSuggestionTimer: 0,
      actionLog: [],
      language: "en",
      contextLensOpen: false,
      contextLinkHistory: [],
      contextSavedViews: [],
      contextDockEditingName: "",
      contextLensRestoreFocusId: "context-summary",
      contextDefaultBootPending: true,
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
        recentIds: [],
      }},
      responsiveContract: {{
        viewport: "desktop",
        density: "comfortable",
        pane: "split",
        modal: "side-panel",
        actionSheet: "inline",
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

    function jumpToSection(targetId, {{ updateHash = true }} = {{}}) {{
      const normalized = normalizeSectionId(targetId);
      if (!normalized) {{
        return;
      }}
      const target = document.getElementById(normalized);
      if (!target) {{
        return;
      }}
      const currentSectionId = normalizeSectionId(state.activeSectionId);
      const currentMode = workspaceModeForSection(currentSectionId);
      const targetMode = workspaceModeForSection(normalized);
      const paneContract = String(document.body && document.body.dataset ? document.body.dataset.paneContract : "").trim() || "split";
      const shouldScroll = targetMode !== currentMode || paneContract !== "split";
      setContextLensOpen(false);
      state.activeSectionId = normalized;
      renderWorkspaceModeChrome();
      renderTopbarContext();
      if (shouldScroll) {{
        target.scrollIntoView({{ block: "start", behavior: "smooth" }});
      }}
      if (!updateHash) {{
        return;
      }}
      const url = new URL(window.location.href);
      const nextHash = `#${{normalized}}`;
      if (url.hash === nextHash) {{
        return;
      }}
      const nextSearch = url.searchParams.toString();
      window.history.replaceState(
        window.history.state,
        "",
        `${{url.pathname}}${{nextSearch ? `?${{nextSearch}}` : ""}}${{nextHash}}`,
      );
    }}

    function escapeHtml(value) {{
      return String(value ?? "").replace(/[&<>"']/g, (char) => {{
        return {{ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }}[char];
      }});
    }}

    function clampLabel(value, maxLength = 34) {{
      const text = String(value || "").trim();
      if (text.length <= maxLength) {{
        return text;
      }}
      return `${{text.slice(0, Math.max(0, maxLength - 1)).trimEnd()}}…`;
    }}

    const textFitSegmenter = typeof Intl !== "undefined" && typeof Intl.Segmenter === "function"
      ? new Intl.Segmenter(undefined, {{ granularity: "grapheme" }})
      : null;
    const canvasTextWidthCache = new Map();
    const consoleOverflowEvidenceLedger = new Map();
    let canvasTextMeasureContext = null;
    let pendingTextFitFrame = 0;
    let pendingOverflowEvidenceRender = 0;
    const pendingTextFitRoots = new Set();

    function defaultConsoleOverflowEvidence() {{
      return {{
        surface_count: 0,
        checked_sample_count: 0,
        fitted_sample_count: 0,
        survivor_count: 0,
        residual_surface_count: 0,
        surfaces: [],
        residual_surfaces: [],
        updated_at: "",
      }};
    }}

    function consoleOverflowEvidenceSignature(evidence) {{
      return JSON.stringify({{
        surface_count: Number(evidence?.surface_count || 0),
        checked_sample_count: Number(evidence?.checked_sample_count || 0),
        fitted_sample_count: Number(evidence?.fitted_sample_count || 0),
        survivor_count: Number(evidence?.survivor_count || 0),
        residual_surface_count: Number(evidence?.residual_surface_count || 0),
        surfaces: Array.isArray(evidence?.surfaces)
          ? evidence.surfaces.map((surface) => ({{
              surface_id: String(surface?.surface_id || ""),
              checked_sample_count: Number(surface?.checked_sample_count || 0),
              fitted_sample_count: Number(surface?.fitted_sample_count || 0),
              survivor_count: Number(surface?.survivor_count || 0),
              sample_labels: Array.isArray(surface?.sample_labels) ? surface.sample_labels : [],
            }}))
          : [],
      }});
    }}

    function buildConsoleOverflowSampleKey(surfaceId, originalText) {{
      return `${{surfaceId}}::${{originalText}}`;
    }}

    function isNodeVisibleForOverflowEvidence(node) {{
      if (!(node instanceof HTMLElement) || !node.isConnected) {{
        return false;
      }}
      const style = window.getComputedStyle(node);
      if (style.display === "none" || style.visibility === "hidden") {{
        return false;
      }}
      const rect = node.getBoundingClientRect();
      return Number(node.clientWidth || rect.width || 0) > 0 && Number(node.clientHeight || rect.height || 0) > 0;
    }}

    function hasResidualInlineOverflow(node) {{
      if (!isNodeVisibleForOverflowEvidence(node)) {{
        return false;
      }}
      const clientWidth = Number(node.clientWidth || node.getBoundingClientRect().width || 0);
      const scrollWidth = Number(node.scrollWidth || 0);
      return scrollWidth > clientWidth + 1;
    }}

    function recordConsoleOverflowEvidence(nodes) {{
      nodes.forEach((node) => {{
        if (!(node instanceof HTMLElement) || !isNodeVisibleForOverflowEvidence(node)) {{
          return;
        }}
        const surfaceId = String(node.dataset.fitText || "").trim();
        const originalText = String(node.dataset.fitTextOriginal || node.textContent || "").trim();
        if (!surfaceId || !originalText) {{
          return;
        }}
        const sampleKey = buildConsoleOverflowSampleKey(surfaceId, originalText);
        const surface = consoleOverflowEvidenceLedger.get(surfaceId) || {{
          surface_id: surfaceId,
          checked_keys: new Set(),
          fitted_keys: new Set(),
          survivor_keys: new Set(),
          sample_labels: [],
        }};
        surface.checked_keys.add(sampleKey);
        if (String(node.dataset.fitApplied || "").trim() === "true") {{
          surface.fitted_keys.add(sampleKey);
        }}
        if (hasResidualInlineOverflow(node)) {{
          surface.survivor_keys.add(sampleKey);
          const sampleLabel = clampLabel(originalText, 52);
          if (sampleLabel && !surface.sample_labels.includes(sampleLabel) && surface.sample_labels.length < 3) {{
            surface.sample_labels.push(sampleLabel);
          }}
        }}
        consoleOverflowEvidenceLedger.set(surfaceId, surface);
      }});
    }}

    function buildConsoleOverflowEvidenceSnapshot() {{
      const surfaces = Array.from(consoleOverflowEvidenceLedger.values())
        .map((surface) => ({{
          surface_id: surface.surface_id,
          checked_sample_count: surface.checked_keys.size,
          fitted_sample_count: surface.fitted_keys.size,
          survivor_count: surface.survivor_keys.size,
          sample_labels: surface.sample_labels.slice(0, 3),
        }}))
        .sort((left, right) => (
          right.survivor_count - left.survivor_count
          || right.checked_sample_count - left.checked_sample_count
          || left.surface_id.localeCompare(right.surface_id)
        ));
      const residualSurfaces = surfaces.filter((surface) => surface.survivor_count > 0);
      return {{
        surface_count: surfaces.length,
        checked_sample_count: surfaces.reduce((sum, surface) => sum + surface.checked_sample_count, 0),
        fitted_sample_count: surfaces.reduce((sum, surface) => sum + surface.fitted_sample_count, 0),
        survivor_count: surfaces.reduce((sum, surface) => sum + surface.survivor_count, 0),
        residual_surface_count: residualSurfaces.length,
        surfaces,
        residual_surfaces: residualSurfaces,
        updated_at: new Date().toISOString(),
      }};
    }}

    function scheduleConsoleOverflowEvidenceRender() {{
      if (pendingOverflowEvidenceRender || !$("status-card")) {{
        return;
      }}
      pendingOverflowEvidenceRender = window.requestAnimationFrame(() => {{
        pendingOverflowEvidenceRender = 0;
        if ($("status-card") && !(state.loading.board && !state.status && !state.ops)) {{
          renderStatus();
        }}
      }});
    }}

    function refreshConsoleOverflowEvidence() {{
      const nodes = Array.from(document.querySelectorAll("[data-fit-text]"));
      recordConsoleOverflowEvidence(nodes);
      const nextEvidence = buildConsoleOverflowEvidenceSnapshot();
      const nextSignature = consoleOverflowEvidenceSignature(nextEvidence);
      if (nextSignature === state.consoleOverflowEvidenceSignature && state.consoleOverflowEvidence) {{
        window.__DATAPULSE_CONSOLE_OVERFLOW__ = state.consoleOverflowEvidence;
        return state.consoleOverflowEvidence;
      }}
      state.consoleOverflowEvidence = nextEvidence;
      state.consoleOverflowEvidenceSignature = nextSignature;
      if (document.body?.dataset) {{
        document.body.dataset.consoleOverflowHotspots = String(nextEvidence.residual_surface_count || 0);
        document.body.dataset.consoleOverflowSurvivors = String(nextEvidence.survivor_count || 0);
      }}
      window.__DATAPULSE_CONSOLE_OVERFLOW__ = nextEvidence;
      scheduleConsoleOverflowEvidenceRender();
      return nextEvidence;
    }}

    function getConsoleOverflowEvidence() {{
      return JSON.parse(JSON.stringify(state.consoleOverflowEvidence || defaultConsoleOverflowEvidence()));
    }}

    function segmentTextForFit(value) {{
      const text = String(value || "").trim();
      if (!text) {{
        return [];
      }}
      if (textFitSegmenter) {{
        return Array.from(textFitSegmenter.segment(text), (entry) => entry.segment);
      }}
      return Array.from(text);
    }}

    function getCanvasTextMeasureContext() {{
      if (canvasTextMeasureContext) {{
        return canvasTextMeasureContext;
      }}
      if (typeof document === "undefined" || typeof document.createElement !== "function") {{
        return null;
      }}
      const canvas = document.createElement("canvas");
      canvasTextMeasureContext = typeof canvas.getContext === "function" ? canvas.getContext("2d") : null;
      return canvasTextMeasureContext;
    }}

    function measureCanvasTextWidth(text, font) {{
      const context = getCanvasTextMeasureContext();
      if (!context || !font) {{
        return -1;
      }}
      const cacheKey = `${{font}}::${{text}}`;
      if (canvasTextWidthCache.has(cacheKey)) {{
        return canvasTextWidthCache.get(cacheKey);
      }}
      context.font = font;
      const width = Number(context.measureText(text).width || 0);
      canvasTextWidthCache.set(cacheKey, width);
      return width;
    }}

    function resolveCanvasFitFont(node) {{
      const style = window.getComputedStyle(node);
      return style.font || `${{style.fontWeight || 400}} ${{style.fontSize || "14px"}} ${{style.fontFamily || "sans-serif"}}`;
    }}

    function resolveCanvasFitWidth(node) {{
      const style = window.getComputedStyle(node);
      const explicitWidth = Number(node.dataset.fitMaxWidth || 0);
      const measuredWidth = explicitWidth > 0
        ? explicitWidth
        : Number(node.getBoundingClientRect().width || node.clientWidth || 0);
      if (measuredWidth <= 0) {{
        return 0;
      }}
      const chromeWidth = (
        parseFloat(style.paddingLeft || "0")
        + parseFloat(style.paddingRight || "0")
        + parseFloat(style.borderLeftWidth || "0")
        + parseFloat(style.borderRightWidth || "0")
      );
      return Math.max(0, measuredWidth - chromeWidth);
    }}

    function fitTextToWidth(value, maxWidth, {{ font = "", fallbackLength = 34 }} = {{}}) {{
      const text = String(value || "").trim();
      if (!text) {{
        return "";
      }}
      const widthBudget = Number(maxWidth || 0);
      if (widthBudget <= 0) {{
        return clampLabel(text, fallbackLength);
      }}
      const measuredFullWidth = measureCanvasTextWidth(text, font);
      if (measuredFullWidth >= 0 && measuredFullWidth <= widthBudget) {{
        return text;
      }}
      const segments = segmentTextForFit(text);
      if (!segments.length) {{
        return clampLabel(text, fallbackLength);
      }}
      const ellipsis = "…";
      const ellipsisWidth = measureCanvasTextWidth(ellipsis, font);
      if (ellipsisWidth < 0) {{
        return clampLabel(text, fallbackLength);
      }}
      if (ellipsisWidth >= widthBudget) {{
        return ellipsis;
      }}
      let low = 0;
      let high = segments.length;
      let best = ellipsis;
      while (low <= high) {{
        const mid = Math.floor((low + high) / 2);
        const head = segments.slice(0, mid).join("").trimEnd();
        const candidate = head ? `${{head}}${{ellipsis}}` : ellipsis;
        if (measureCanvasTextWidth(candidate, font) <= widthBudget) {{
          best = candidate;
          low = mid + 1;
        }} else {{
          high = mid - 1;
        }}
      }}
      return best || clampLabel(text, fallbackLength);
    }}

    function applyCanvasTextFit(root = document) {{
      const scope = root && typeof root.querySelectorAll === "function" ? root : document;
      if (!scope) {{
        return;
      }}
      const candidates = scope.matches?.("[data-fit-text]")
        ? [scope, ...scope.querySelectorAll("[data-fit-text]")]
        : Array.from(scope.querySelectorAll("[data-fit-text]"));
      candidates.forEach((node) => {{
        if (!(node instanceof HTMLElement)) {{
          return;
        }}
        const originalText = String(node.dataset.fitTextOriginal || node.textContent || "").trim();
        if (!originalText) {{
          return;
        }}
        node.dataset.fitTextOriginal = originalText;
        if (!node.getAttribute("title")) {{
          node.setAttribute("title", originalText);
        }}
        const fallbackLength = Number(node.dataset.fitFallback || 34);
        const fittedText = fitTextToWidth(originalText, resolveCanvasFitWidth(node), {{
          font: resolveCanvasFitFont(node),
          fallbackLength,
        }});
        node.textContent = fittedText;
        node.dataset.fitApplied = fittedText !== originalText ? "true" : "false";
      }});
      refreshConsoleOverflowEvidence();
    }}

    function scheduleCanvasTextFit(root = document) {{
      pendingTextFitRoots.add(root && typeof root.querySelectorAll === "function" ? root : document);
      if (pendingTextFitFrame) {{
        return;
      }}
      pendingTextFitFrame = window.requestAnimationFrame(() => {{
        pendingTextFitFrame = 0;
        const roots = Array.from(pendingTextFitRoots);
        pendingTextFitRoots.clear();
        roots.forEach((candidate) => applyCanvasTextFit(candidate));
      }});
    }}

    const responsiveInteractionContracts = {{
      desktop: {{
        viewport: "desktop",
        density: "comfortable",
        pane: "split",
        modal: "side-panel",
        actionSheet: "inline",
      }},
      compact: {{
        viewport: "compact",
        density: "compact",
        pane: "stacked",
        modal: "sheet",
        actionSheet: "inline",
      }},
      touch: {{
        viewport: "touch",
        density: "touch",
        pane: "single",
        modal: "fullscreen",
        actionSheet: "sheet",
      }},
    }};

    function resolveResponsiveInteractionContract(width = 0) {{
      const viewportWidth = Number(width) > 0
        ? Number(width)
        : window.innerWidth || document.documentElement?.clientWidth || 1280;
      if (viewportWidth <= 760) {{
        return responsiveInteractionContracts.touch;
      }}
      if (viewportWidth <= 1100) {{
        return responsiveInteractionContracts.compact;
      }}
      return responsiveInteractionContracts.desktop;
    }}

    function applyResponsiveInteractionContract() {{
      const contract = resolveResponsiveInteractionContract();
      state.responsiveContract = contract;
      if (!document.body) {{
        return contract;
      }}
      document.body.dataset.responsiveViewport = contract.viewport;
      document.body.dataset.densityMode = contract.density;
      document.body.dataset.paneContract = contract.pane;
      document.body.dataset.modalPresentation = contract.modal;
      document.body.dataset.actionSheetMode = contract.actionSheet;
      if (contract.actionSheet !== "sheet") {{
        document.querySelectorAll("[data-card-action-sheet]").forEach((sheet) => {{
          sheet.removeAttribute("open");
        }});
      }}
      scheduleCanvasTextFit(document);
      return contract;
    }}

    function bindResponsiveInteractionContract() {{
      applyResponsiveInteractionContract();
      let resizeTimer = 0;
      let lastViewportWidth = window.innerWidth || document.documentElement?.clientWidth || 0;
      const scheduleContractApply = () => {{
        window.clearTimeout(resizeTimer);
        resizeTimer = window.setTimeout(() => {{
          applyResponsiveInteractionContract();
        }}, 80);
      }};
      window.addEventListener("resize", scheduleContractApply, {{ passive: true }});
      if (window.visualViewport?.addEventListener) {{
        window.visualViewport.addEventListener("resize", scheduleContractApply, {{ passive: true }});
      }}
      ["(max-width: 760px)", "(max-width: 1100px)"].forEach((query) => {{
        const media = window.matchMedia ? window.matchMedia(query) : null;
        if (!media) {{
          return;
        }}
        if (typeof media.addEventListener === "function") {{
          media.addEventListener("change", scheduleContractApply);
        }} else if (typeof media.addListener === "function") {{
          media.addListener(scheduleContractApply);
        }}
      }});
      window.setInterval(() => {{
        const nextViewportWidth = window.innerWidth || document.documentElement?.clientWidth || 0;
        if (!nextViewportWidth || nextViewportWidth === lastViewportWidth) {{
          return;
        }}
        lastViewportWidth = nextViewportWidth;
        scheduleContractApply();
      }}, 250);
    }}

    const languageStorageKey = "datapulse.console.language.v1";
    const createWatchStorageKey = "datapulse.console.create-watch-draft.v2";
    const commandPaletteQueryStorageKey = "datapulse.console.palette-query.v1";
    const commandPaletteRecentStorageKey = "datapulse.console.palette-recent.v1";
    const contextLinkHistoryStorageKey = "datapulse.console.context-history.v1";
    const contextSavedViewsStorageKey = "datapulse.console.context-saved-views.v1";
    const watchUrlSearchParam = "watch_search";
    const watchUrlIdParam = "watch_id";
    const triageUrlFilterParam = "triage_filter";
    const triageUrlSearchParam = "triage_search";
    const triageUrlIdParam = "triage_id";
    const storyUrlViewParam = "story_view";
    const storyUrlFilterParam = "story_filter";
    const storyUrlSortParam = "story_sort";
    const storyUrlSearchParam = "story_search";
    const storyUrlIdParam = "story_id";
    const storyUrlModeParam = "story_mode";
    const storyFilterStorageKey = "datapulse.console.story-filter.v1";
    const storySortStorageKey = "datapulse.console.story-sort.v1";
    const storyWorkspaceModeStorageKey = "datapulse.console.story-workspace-mode.v1";
    const createWatchFormFields = ["name", "schedule", "query", "platform", "domain", "route", "keyword", "min_score", "min_confidence"];
    const routeFormFields = [
      "name",
      "channel",
      "description",
      "webhook_url",
      "authorization",
      "headers_json",
      "feishu_webhook",
      "telegram_bot_token",
      "telegram_chat_id",
      "timeout_seconds",
    ];
    const triageFilterOptions = ["open", "all", "new", "triaged", "verified", "duplicate", "ignored", "escalated"];
    const workspaceModeSectionMap = {{
      intake: ["section-intake"],
      missions: ["section-board", "section-cockpit"],
      review: ["section-triage", "section-story", "section-claims", "section-report-studio"],
      delivery: ["section-ops"],
    }};

    function copy(enText, zhText) {{
      return state.language === "zh" ? zhText : enText;
    }}

    function phrase(enText, zhText, values = {{}}) {{
      const template = copy(enText, zhText);
      return String(template).replace(/\\{{(\\w+)\\}}/g, (_, key) => String(values[key] ?? ""));
    }}

    function localizeWord(value) {{
      const raw = String(value || "").trim();
      const key = raw.toLowerCase();
      const map = {{
        active: ["active", "活跃"],
        aligned: ["aligned", "一致"],
        all: ["all", "全部"],
        approve: ["approve", "批准"],
        approved: ["approved", "已批准"],
        blocked: ["blocked", "已阻断"],
        brief: ["brief", "摘要"],
        closed: ["closed", "关闭"],
        clear: ["clear", "清晰"],
        conflicted: ["conflicted", "冲突"],
        degraded: ["degraded", "降级"],
        disabled: ["disabled", "已停用"],
        done: ["done", "完成"],
        draft: ["draft", "草稿"],
        due: ["due", "待执行"],
        editable: ["editable", "可编辑"],
        duplicate: ["duplicate", "重复"],
        escalated: ["escalated", "已升级"],
        error: ["error", "错误"],
        events: ["events", "事件"],
        feishu: ["feishu", "飞书"],
        full: ["full", "完整版"],
        healthy: ["healthy", "健康"],
        hold_export: ["hold export", "暂停导出"],
        idle: ["idle", "空闲"],
        ignored: ["ignored", "已忽略"],
        keep: ["keep", "保留"],
        pass: ["pass", "通过"],
        manual: ["manual", "手动"],
        merge: ["merge", "合并"],
        missing: ["missing", "缺失"],
        mixed: ["mixed", "混合"],
        monitoring: ["monitoring", "监控中"],
        new: ["new", "新建"],
        ok: ["ok", "正常"],
        open: ["open", "开放"],
        pending: ["pending", "处理中"],
        paused: ["paused", "已暂停"],
        profile: ["profile", "配置"],
        pull: ["pull", "拉取"],
        push: ["push", "推送"],
        ready: ["ready", "就绪"],
        report: ["report", "报告"],
        resolved: ["resolved", "已解决"],
        rss: ["rss", "rss"],
        review_before_export: ["review before export", "导出前复核"],
        reviewed: ["reviewed", "已复核"],
        review_required: ["review required", "需要复核"],
        running: ["running", "运行中"],
        same: ["same", "相同"],
        sources: ["sources", "来源清单"],
        story: ["story", "故事"],
        success: ["success", "成功"],
        synced: ["synced", "已同步"],
        telegram: ["telegram", "telegram"],
        triaged: ["triaged", "已分诊"],
        unknown: ["unknown", "未知"],
        verified: ["verified", "已核验"],
        waiting: ["waiting", "等待"],
        warn: ["warn", "警告"],
        warning: ["warning", "警告"],
        watch_mission: ["watch mission", "监控任务"],
        webhook: ["webhook", "webhook"],
        markdown: ["markdown", "markdown"],
      }};
      const pair = map[key];
      return pair ? copy(pair[0], pair[1]) : raw;
    }}

    function localizeBoolean(value) {{
      return value ? copy("yes", "是") : copy("no", "否");
    }}
    const createWatchPresets = [
      {{
        id: "launch",
        label: "Launch Pulse",
        zhLabel: "发布脉冲",
        description: "Tight interval for product or company launches.",
        zhDescription: "适合产品或公司发布场景的高频任务。",
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
        zhLabel: "风险巡检",
        description: "Higher confidence gate for operational risk review.",
        zhDescription: "适合运维风险巡检的高置信度门槛。",
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
        zhLabel: "市场异动",
        description: "Cross-signal watch for moves around listed names.",
        zhDescription: "适合上市主体异动监测的跨信号任务。",
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
        zhLabel: "创作者热度",
        description: "Faster scan for creator and social breakout chatter.",
        zhDescription: "适合创作者与社媒爆发信号的快速扫描。",
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
    const routeChannelOptions = [
      {{ label: "Webhook", zhLabel: "Webhook", value: "webhook" }},
      {{ label: "Telegram", zhLabel: "Telegram", value: "telegram" }},
      {{ label: "Feishu", zhLabel: "飞书", value: "feishu" }},
      {{ label: "Markdown", zhLabel: "Markdown", value: "markdown" }},
    ];
    const claimStatusOptions = ["draft", "reviewed", "ready", "conflicted", "blocked"];
    const reportStatusOptions = ["draft", "review_required", "ready", "blocked"];
    const storyStatusOptions = ["active", "monitoring", "resolved", "archived"];
    const storySortOptions = ["attention", "recent", "evidence", "conflict", "score"];
    const storyWorkspaceModeOptions = ["board", "editor"];
    const storyViewPresetOptions = ["desk", "fresh", "conflicts", "archive"];
    const scoreSuggestionOptions = ["40", "55", "68", "70", "80", "90"];
    const confidenceSuggestionOptions = ["0.6", "0.65", "0.75", "0.8", "0.88", "0.95"];
    const deliverySubjectOptions = ["profile", "watch_mission", "story", "report"];
    const deliveryModeOptions = ["pull", "push"];
    const deliveryStatusOptions = ["active", "paused", "disabled"];
    const deliveryOutputOptionsBySubject = {{
      profile: ["feed_json", "feed_rss", "feed_atom"],
      watch_mission: ["alert_event"],
      story: ["story_json", "story_markdown"],
      report: ["report_brief", "report_full", "report_sources", "report_watch_pack"],
    }};

    function uniqueValues(values) {{
      return Array.from(new Set((Array.isArray(values) ? values : [values])
        .flatMap((value) => Array.isArray(value) ? value : [value])
        .map((value) => String(value ?? "").trim())
        .filter(Boolean)));
    }}

    function normalizeStorySort(value) {{
      const normalized = String(value || "").trim().toLowerCase() || "attention";
      return storySortOptions.includes(normalized) ? normalized : "attention";
    }}

    function normalizeStoryFilter(value) {{
      const normalized = String(value || "").trim().toLowerCase() || "all";
      if (normalized === "all" || normalized === "conflicted") {{
        return normalized;
      }}
      return storyStatusOptions.includes(normalized) ? normalized : "all";
    }}

    function normalizeStoryWorkspaceMode(value) {{
      const normalized = String(value || "").trim().toLowerCase() || "board";
      return storyWorkspaceModeOptions.includes(normalized) ? normalized : "board";
    }}

    function normalizeTriageFilter(value) {{
      const normalized = String(value || "").trim().toLowerCase() || "open";
      return triageFilterOptions.includes(normalized) ? normalized : "open";
    }}

    function storyViewPresetLabel(viewKey) {{
      const labels = {{
        desk: copy("Ops Desk", "运营台"),
        fresh: copy("Fresh Radar", "新近雷达"),
        conflicts: copy("Conflict Queue", "冲突队列"),
        archive: copy("Archive Review", "归档回看"),
        custom: copy("Custom", "自定义"),
      }};
      return labels[String(viewKey || "").trim().toLowerCase()] || labels.custom;
    }}

    function storyViewPresetDescription(viewKey) {{
      const descriptions = {{
        desk: copy(
          "Default operating lane for active story review.",
          "默认的日常运营视角，先看当前应处理的故事。"
        ),
        fresh: copy(
          "Pull the latest story updates to the top.",
          "把最新更新的故事优先提到最前。"
        ),
        conflicts: copy(
          "Narrow to contradiction-heavy stories first.",
          "直接聚焦冲突较多的故事。"
        ),
        archive: copy(
          "Review recently archived stories without reopening the whole queue.",
          "查看最近归档的故事，而不用重新打开整个队列。"
        ),
        custom: copy(
          "You are using a manual filter or sort combination.",
          "当前使用的是手动组合的筛选与排序。"
        ),
      }};
      return descriptions[String(viewKey || "").trim().toLowerCase()] || descriptions.custom;
    }}

    function getStoryViewPreset(viewKey) {{
      const normalized = String(viewKey || "").trim().toLowerCase();
      const presets = {{
        desk: {{ key: "desk", filter: "all", sort: "attention" }},
        fresh: {{ key: "fresh", filter: "all", sort: "recent" }},
        conflicts: {{ key: "conflicts", filter: "conflicted", sort: "conflict" }},
        archive: {{ key: "archive", filter: "archived", sort: "recent" }},
      }};
      return presets[normalized] || null;
    }}

    function detectStoryViewPreset({{ filter = "all", sort = "attention", search = "" }} = {{}}) {{
      if (String(search || "").trim()) {{
        return "custom";
      }}
      const normalizedFilter = normalizeStoryFilter(filter);
      const normalizedSort = normalizeStorySort(sort);
      const matchedPreset = storyViewPresetOptions.find((viewKey) => {{
        const preset = getStoryViewPreset(viewKey);
        return preset && preset.filter === normalizedFilter && preset.sort === normalizedSort;
      }});
      return matchedPreset || "custom";
    }}

    function storySortLabel(sortKey) {{
      const normalized = normalizeStorySort(sortKey);
      const labels = {{
        attention: copy("Attention Order", "优先级排序"),
        recent: copy("Most Recent", "最近更新"),
        evidence: copy("Most Evidence", "证据最多"),
        conflict: copy("Conflict Load", "冲突强度"),
        score: copy("Highest Score", "最高分数"),
      }};
      return labels[normalized] || labels.attention;
    }}

    function storySortSummary(sortKey) {{
      const normalized = normalizeStorySort(sortKey);
      const summaries = {{
        attention: copy(
          "Default lane: unresolved conflicts, fresh updates, and active stories float to the top first.",
          "默认把未解决冲突、最近更新且仍在活跃队列里的故事放在最前面。"
        ),
        recent: copy(
          "Use when recency matters more than story depth.",
          "当时效比故事深度更重要时，用这个排序。"
        ),
        evidence: copy(
          "Use when you want the densest evidence packs first.",
          "当你想先看证据最密集的故事时，用这个排序。"
        ),
        conflict: copy(
          "Use when contradiction triage is the current priority.",
          "当处理冲突信号是当前优先级时，用这个排序。"
        ),
        score: copy(
          "Use when ranked signal quality should lead the queue.",
          "当你想按综合分数先看高质量信号时，用这个排序。"
        ),
      }};
      return summaries[normalized] || summaries.attention;
    }}

    function parseDateValue(value) {{
      const stamp = Date.parse(String(value || "").trim());
      return Number.isFinite(stamp) ? stamp : 0;
    }}

    function formatCompactDateTime(value) {{
      const stamp = parseDateValue(value);
      if (!stamp) {{
        return "-";
      }}
      const formatter = new Intl.DateTimeFormat(state.language === "zh" ? "zh-CN" : "en-US", {{
        month: "short",
        day: "2-digit",
        hour: "2-digit",
        minute: "2-digit",
      }});
      return formatter.format(new Date(stamp));
    }}

    function getStoryUpdatedAt(story) {{
      return parseDateValue((story && (story.updated_at || story.generated_at)) || "");
    }}

    function getStoryContradictionCount(story) {{
      return Array.isArray(story?.contradictions) ? story.contradictions.length : 0;
    }}

    function getStoryAttentionScore(story) {{
      const status = String(story?.status || "active").trim().toLowerCase() || "active";
      const contradictionCount = getStoryContradictionCount(story);
      const itemCount = Math.max(0, Number(story?.item_count || 0));
      const sourceCount = Math.max(0, Number(story?.source_count || 0));
      const score = Number(story?.score || 0);
      const confidence = Number(story?.confidence || 0);
      const updatedAt = getStoryUpdatedAt(story);
      const ageHours = updatedAt ? Math.max(0, (Date.now() - updatedAt) / 3600000) : 999;
      const freshness = Math.max(0, 48 - Math.min(48, ageHours));
      const statusWeights = {{
        active: 40,
        monitoring: 26,
        resolved: 10,
        archived: -24,
      }};
      return (
        contradictionCount * 70 +
        itemCount * 8 +
        sourceCount * 4 +
        score * 0.4 +
        confidence * 18 +
        freshness +
        (statusWeights[status] ?? 16)
      );
    }}

    function compareNumberDesc(leftValue, rightValue) {{
      if (leftValue === rightValue) {{
        return 0;
      }}
      return leftValue < rightValue ? 1 : -1;
    }}

    function compareStoriesByWorkspaceOrder(left, right, sortKey) {{
      const normalized = normalizeStorySort(sortKey);
      const leftUpdated = getStoryUpdatedAt(left);
      const rightUpdated = getStoryUpdatedAt(right);
      const leftAttention = getStoryAttentionScore(left);
      const rightAttention = getStoryAttentionScore(right);
      const leftConflicts = getStoryContradictionCount(left);
      const rightConflicts = getStoryContradictionCount(right);
      const leftItems = Math.max(0, Number(left?.item_count || 0));
      const rightItems = Math.max(0, Number(right?.item_count || 0));
      const leftSources = Math.max(0, Number(left?.source_count || 0));
      const rightSources = Math.max(0, Number(right?.source_count || 0));
      const leftScore = Number(left?.score || 0);
      const rightScore = Number(right?.score || 0);
      const leftConfidence = Number(left?.confidence || 0);
      const rightConfidence = Number(right?.confidence || 0);
      const chain = normalized === "recent"
        ? [
            compareNumberDesc(leftUpdated, rightUpdated),
            compareNumberDesc(leftAttention, rightAttention),
            compareNumberDesc(leftItems, rightItems),
          ]
        : normalized === "evidence"
          ? [
              compareNumberDesc(leftItems, rightItems),
              compareNumberDesc(leftSources, rightSources),
              compareNumberDesc(leftAttention, rightAttention),
              compareNumberDesc(leftUpdated, rightUpdated),
            ]
          : normalized === "conflict"
            ? [
                compareNumberDesc(leftConflicts, rightConflicts),
                compareNumberDesc(leftAttention, rightAttention),
                compareNumberDesc(leftUpdated, rightUpdated),
              ]
            : normalized === "score"
              ? [
                  compareNumberDesc(leftScore, rightScore),
                  compareNumberDesc(leftConfidence, rightConfidence),
                  compareNumberDesc(leftAttention, rightAttention),
                  compareNumberDesc(leftUpdated, rightUpdated),
                ]
              : [
                  compareNumberDesc(leftAttention, rightAttention),
                  compareNumberDesc(leftConflicts, rightConflicts),
                  compareNumberDesc(leftUpdated, rightUpdated),
                  compareNumberDesc(leftItems, rightItems),
                ];
      for (const result of chain) {{
        if (result) {{
          return result;
        }}
      }}
      return String(left?.title || left?.id || "").localeCompare(String(right?.title || right?.id || ""));
    }}

    function describeStoryPriority(story) {{
      const contradictionCount = getStoryContradictionCount(story);
      const itemCount = Math.max(0, Number(story?.item_count || 0));
      const status = String(story?.status || "active").trim().toLowerCase() || "active";
      const updatedAt = getStoryUpdatedAt(story);
      const ageHours = updatedAt ? Math.max(0, (Date.now() - updatedAt) / 3600000) : 999;
      if (status === "archived") {{
        return {{ tone: "", label: copy("cold lane", "冷队列") }};
      }}
      if (contradictionCount > 0) {{
        return {{
          tone: "hot",
          label: phrase("conflict x{{count}}", "冲突 x{{count}}", {{ count: contradictionCount }}),
        }};
      }}
      if (ageHours <= 12) {{
        return {{ tone: "ok", label: copy("fresh update", "新近更新") }};
      }}
      if (itemCount >= 4) {{
        return {{ tone: "ok", label: copy("deep evidence", "证据较多") }};
      }}
      if (status === "monitoring") {{
        return {{ tone: "", label: copy("watching", "持续监控") }};
      }}
      if (status === "resolved") {{
        return {{ tone: "", label: copy("resolved lane", "已解决") }};
      }}
      return {{ tone: "ok", label: copy("active lane", "活跃队列") }};
    }}

    function renderDatalist(identifier, values) {{
      const root = $(identifier);
      if (!root) {{
        return;
      }}
      root.innerHTML = uniqueValues(values).slice(0, 32).map((value) => `<option value="${{escapeHtml(value)}}"></option>`).join("");
    }}

    function collectWatchValues(fieldName) {{
      return [
        ...state.watches.map((watch) => watch ? watch[fieldName] : ""),
        ...Object.values(state.watchDetails || {{}}).map((watch) => watch ? watch[fieldName] : ""),
      ];
    }}

    function collectWatchArrayValues(fieldName) {{
      return [
        ...state.watches.flatMap((watch) => Array.isArray(watch?.[fieldName]) ? watch[fieldName] : []),
        ...Object.values(state.watchDetails || {{}}).flatMap((watch) => Array.isArray(watch?.[fieldName]) ? watch[fieldName] : []),
      ];
    }}

    function collectAlertRuleValues(fieldName) {{
      return Object.values(state.watchDetails || {{}}).flatMap((watch) => {{
        return (Array.isArray(watch?.alert_rules) ? watch.alert_rules : []).flatMap((rule) => {{
          const raw = rule ? rule[fieldName] : "";
          return Array.isArray(raw) ? raw : [raw];
        }});
      }});
    }}

    function collectRouteNames() {{
      return state.routes.map((route) => route && (route.name || route.route_name || route.id || ""));
    }}

    function renderFormSuggestionLists() {{
      const suggestionPatch = state.createWatchSuggestions?.autofill_patch || {{}};
      renderDatalist("mission-name-options-list", [
        state.createWatchDraft?.name,
        ...createWatchPresets.map((preset) => preset.values.name),
        ...collectWatchValues("name"),
      ]);
      renderDatalist("query-options-list", [
        state.createWatchDraft?.query,
        ...createWatchPresets.map((preset) => preset.values.query),
        ...collectWatchValues("query"),
      ]);
      renderDatalist("schedule-options-list", [
        state.createWatchDraft?.schedule,
        suggestionPatch.schedule,
        state.createWatchSuggestions?.recommended_schedule,
        ...scheduleLaneOptions.map((option) => option.value),
        ...collectWatchValues("schedule"),
      ]);
      renderDatalist("platform-options-list", [
        state.createWatchDraft?.platform,
        suggestionPatch.platform,
        state.createWatchSuggestions?.recommended_platform,
        ...platformLaneOptions.map((option) => option.value),
        ...collectWatchArrayValues("platforms"),
      ]);
      renderDatalist("domain-options-list", [
        state.createWatchDraft?.domain,
        suggestionPatch.domain,
        state.createWatchSuggestions?.recommended_domain,
        ...collectWatchArrayValues("sites"),
        ...collectAlertRuleValues("domains"),
      ]);
      renderDatalist("route-options-list", [
        state.createWatchDraft?.route,
        suggestionPatch.route,
        state.createWatchSuggestions?.recommended_route,
        ...collectRouteNames(),
        ...collectAlertRuleValues("routes"),
      ]);
      renderDatalist("keyword-options-list", [
        state.createWatchDraft?.keyword,
        suggestionPatch.keyword,
        state.createWatchSuggestions?.recommended_keyword,
        ...createWatchPresets.map((preset) => preset.values.keyword),
        ...collectAlertRuleValues("keyword_any"),
      ]);
      renderDatalist("score-options-list", [
        state.createWatchDraft?.min_score,
        suggestionPatch.min_score,
        ...scoreSuggestionOptions,
        ...collectAlertRuleValues("min_score").filter((value) => Number(value || 0) > 0),
      ]);
      renderDatalist("confidence-options-list", [
        state.createWatchDraft?.min_confidence,
        suggestionPatch.min_confidence,
        ...confidenceSuggestionOptions,
        ...collectAlertRuleValues("min_confidence").filter((value) => Number(value || 0) > 0),
      ]);
    }}

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

    function draftHasAdvancedSignal(payload = {{}}) {{
      const draft = normalizeCreateWatchDraft(payload || defaultCreateWatchDraft());
      return Boolean(
        draft.schedule.trim() ||
        draft.platform.trim() ||
        draft.domain.trim() ||
        draft.route.trim() ||
        draft.keyword.trim() ||
        draft.min_score.trim() ||
        draft.min_confidence.trim()
      );
    }}

    function normalizeCreateWatchDraft(payload = {{}}) {{
      const draft = defaultCreateWatchDraft();
      createWatchFormFields.forEach((field) => {{
        draft[field] = String(payload[field] ?? "");
      }});
      return draft;
    }}

    function isCreateWatchAdvancedOpen(draftInput) {{
      const draft = normalizeCreateWatchDraft(draftInput || defaultCreateWatchDraft());
      if (typeof state.createWatchAdvancedOpen === "boolean") {{
        return state.createWatchAdvancedOpen;
      }}
      return Boolean(String(state.createWatchEditingId || "").trim() || draftHasAdvancedSignal(draft));
    }}

    function summarizeCreateWatchAdvanced(draftInput) {{
      const draft = normalizeCreateWatchDraft(draftInput || defaultCreateWatchDraft());
      const chips = [];
      if (draft.schedule.trim()) {{
        chips.push(scheduleModeLabel(draft.schedule));
      }}
      if (draft.platform.trim()) {{
        chips.push(phrase("platform: {{value}}", "平台：{{value}}", {{ value: draft.platform.trim() }}));
      }}
      if (draft.domain.trim()) {{
        chips.push(phrase("domain: {{value}}", "域名：{{value}}", {{ value: draft.domain.trim() }}));
      }}
      if (draft.route.trim()) {{
        chips.push(phrase("route: {{value}}", "路由：{{value}}", {{ value: draft.route.trim() }}));
      }}
      if (draft.keyword.trim()) {{
        chips.push(phrase("keyword: {{value}}", "关键词：{{value}}", {{ value: draft.keyword.trim() }}));
      }}
      if (draft.min_score.trim()) {{
        chips.push(phrase("score >= {{value}}", "分数 >= {{value}}", {{ value: draft.min_score.trim() }}));
      }}
      if (draft.min_confidence.trim()) {{
        chips.push(phrase("confidence >= {{value}}", "置信度 >= {{value}}", {{ value: draft.min_confidence.trim() }}));
      }}
      if (!chips.length) {{
        chips.push(copy("No scope or alert gate yet", "当前还没有范围或告警门槛"));
      }}
      return chips.slice(0, 6);
    }}

    function defaultRouteDraft() {{
      return {{
        name: "",
        channel: "webhook",
        description: "",
        webhook_url: "",
        authorization: "",
        headers_json: "",
        feishu_webhook: "",
        telegram_bot_token: "",
        telegram_chat_id: "",
        timeout_seconds: "",
      }};
    }}

    function normalizeRouteDraft(payload = {{}}) {{
      const draft = defaultRouteDraft();
      routeFormFields.forEach((field) => {{
        if (field === "channel") {{
          return;
        }}
        draft[field] = String(payload[field] ?? draft[field] ?? "");
      }});
      const channel = String(payload.channel ?? draft.channel ?? "webhook").trim().toLowerCase();
      draft.channel = routeChannelOptions.some((option) => option.value === channel) ? channel : "webhook";
      return draft;
    }}

    function routeChannelLabel(channel) {{
      const normalized = String(channel || "").trim().toLowerCase();
      const option = routeChannelOptions.find((candidate) => candidate.value === normalized);
      if (!option) {{
        return normalized || copy("unknown", "未知");
      }}
      return copy(option.label, option.zhLabel || option.label);
    }}

    function routeDraftHasAdvancedSignal(payload = {{}}) {{
      const draft = normalizeRouteDraft(payload || defaultRouteDraft());
      return Boolean(
        draft.description.trim() ||
        draft.authorization.trim() ||
        draft.headers_json.trim() ||
        draft.timeout_seconds.trim()
      );
    }}

    function isRouteAdvancedOpen(draftInput) {{
      const draft = normalizeRouteDraft(draftInput || defaultRouteDraft());
      if (typeof state.routeAdvancedOpen === "boolean") {{
        return state.routeAdvancedOpen;
      }}
      return Boolean(String(state.routeEditingId || "").trim() || routeDraftHasAdvancedSignal(draft));
    }}

    function normalizeRouteName(value) {{
      return String(value || "").trim().toLowerCase();
    }}

    function normalizeRouteRuleNames(rule) {{
      if (!rule) {{
        return [];
      }}
      const raw = Array.isArray(rule.routes) ? rule.routes : [rule.route];
      return uniqueValues(raw).map((value) => normalizeRouteName(value)).filter(Boolean);
    }}

    function watchUsesRoute(watch, routeName) {{
      const normalized = normalizeRouteName(routeName);
      if (!normalized) {{
        return false;
      }}
      return (Array.isArray(watch?.alert_rules) ? watch.alert_rules : []).some((rule) => {{
        return normalizeRouteRuleNames(rule).includes(normalized);
      }});
    }}

    function getRouteUsageRows(routeName) {{
      const rows = [
        ...state.watches,
        ...Object.values(state.watchDetails || {{}}),
      ];
      const seen = new Set();
      return rows.filter((watch) => {{
        const identifier = String(watch?.id || "").trim();
        if (!identifier || seen.has(identifier)) {{
          return false;
        }}
        seen.add(identifier);
        return watchUsesRoute(watch, routeName);
      }});
    }}

    function getRouteUsageCount(routeName) {{
      return getRouteUsageRows(routeName).length;
    }}

    function getRouteUsageNames(routeName) {{
      return getRouteUsageRows(routeName).map((watch) => String(watch.name || watch.id || "").trim()).filter(Boolean);
    }}

    function getRouteHealthRow(routeName) {{
      const normalized = normalizeRouteName(routeName);
      if (!normalized) {{
        return null;
      }}
      return state.routeHealth.find((route) => normalizeRouteName(route?.name) === normalized) || null;
    }}

    function summarizeUrlHost(rawUrl) {{
      const value = String(rawUrl || "").trim();
      if (!value) {{
        return "";
      }}
      try {{
        const parsed = new URL(value);
        const path = parsed.pathname && parsed.pathname !== "/" ? parsed.pathname.slice(0, 18) : "";
        return `${{parsed.host}}${{path}}`;
      }} catch {{
        return value;
      }}
    }}

    function summarizeRouteDestination(route) {{
      const channel = normalizeRouteName(route?.channel);
      if (channel === "webhook") {{
        return route?.webhook_url
          ? summarizeUrlHost(route.webhook_url)
          : copy("Webhook URL missing", "Webhook URL 未配置");
      }}
      if (channel === "feishu") {{
        return route?.feishu_webhook
          ? summarizeUrlHost(route.feishu_webhook)
          : copy("Feishu webhook missing", "飞书 webhook 未配置");
      }}
      if (channel === "telegram") {{
        return route?.telegram_chat_id
          ? phrase("chat {{value}}", "会话 {{value}}", {{ value: route.telegram_chat_id }})
          : copy("Telegram chat missing", "Telegram 会话未配置");
      }}
      if (channel === "markdown") {{
        return copy("Append to alert markdown log", "追加到告警 Markdown 日志");
      }}
      return copy("Route target not configured", "路由目标未配置");
    }}

    function createRouteDraftFromRoute(route) {{
      const rawHeaders = route && typeof route.headers === "object" && !Array.isArray(route.headers)
        ? {{ ...route.headers }}
        : {{}};
      let authorization = "";
      if (typeof route?.authorization === "string" && route.authorization !== "***") {{
        authorization = route.authorization;
      }}
      if (!authorization && typeof rawHeaders.Authorization === "string" && rawHeaders.Authorization !== "***") {{
        authorization = rawHeaders.Authorization;
      }}
      delete rawHeaders.Authorization;
      return normalizeRouteDraft({{
        name: String(route?.name || ""),
        channel: String(route?.channel || "webhook"),
        description: String(route?.description || ""),
        webhook_url: String(route?.webhook_url || ""),
        authorization,
        headers_json: Object.keys(rawHeaders).length ? JSON.stringify(rawHeaders, null, 2) : "",
        feishu_webhook: String(route?.feishu_webhook || ""),
        telegram_bot_token: "",
        telegram_chat_id: String(route?.telegram_chat_id || ""),
        timeout_seconds: route?.timeout_seconds != null ? String(route.timeout_seconds) : "",
      }});
    }}

    function collectRouteDraft(form) {{
      if (!form) {{
        return normalizeRouteDraft(state.routeDraft || defaultRouteDraft());
      }}
      const next = defaultRouteDraft();
      routeFormFields.forEach((fieldName) => {{
        const field = form.elements.namedItem(fieldName);
        next[fieldName] = field ? String(field.value ?? "") : "";
      }});
      return normalizeRouteDraft(next);
    }}

    function setRouteDraft(nextDraft, editingId = state.routeEditingId) {{
      state.routeDraft = normalizeRouteDraft(nextDraft || defaultRouteDraft());
      state.routeEditingId = String(editingId || "").trim();
      renderRouteDeck();
    }}

    function focusRouteDeck(fieldName = "name") {{
      jumpToSection("section-ops");
      window.setTimeout(() => {{
        $("route-manager-shell")?.scrollIntoView({{ block: "start", behavior: "smooth" }});
        const form = $("route-form");
        const field = form?.elements?.namedItem(fieldName);
        if (field && typeof field.focus === "function") {{
          field.focus();
        }}
      }}, 140);
    }}

    async function editRouteInDeck(identifier) {{
      const normalized = normalizeRouteName(identifier);
      if (!normalized) {{
        return;
      }}
      const route = state.routes.find((item) => normalizeRouteName(item?.name) === normalized);
      if (!route) {{
        throw new Error(copy("Alert route not found in current board state.", "当前看板中没有找到该告警路由。"));
      }}
      setContextRouteName(normalized, "section-ops");
      state.routeAdvancedOpen = true;
      setRouteDraft(createRouteDraftFromRoute(route), normalized);
      focusRouteDeck(route.channel === "markdown" ? "description" : "name");
    }}

    async function applyRouteToMissionDraft(identifier) {{
      const normalized = normalizeRouteName(identifier);
      if (!normalized) {{
        return;
      }}
      state.createWatchAdvancedOpen = true;
      updateCreateWatchDraft({{ route: normalized }});
      focusCreateWatchDeck("route");
      showToast(
        state.language === "zh"
          ? `已把路由载入任务草稿：${{normalized}}`
          : `Route loaded into mission deck: ${{normalized}}`,
        "success",
      );
    }}

    function parseRouteHeaders(rawValue) {{
      const text = String(rawValue || "").trim();
      if (!text) {{
        return null;
      }}
      let parsed;
      try {{
        parsed = JSON.parse(text);
      }} catch (error) {{
        throw new Error(copy("Custom headers must be valid JSON.", "自定义请求头必须是合法 JSON。"));
      }}
      if (!parsed || typeof parsed !== "object" || Array.isArray(parsed)) {{
        throw new Error(copy("Custom headers must be a JSON object.", "自定义请求头必须是 JSON 对象。"));
      }}
      return Object.fromEntries(
        Object.entries(parsed)
          .map(([key, value]) => [String(key || "").trim(), String(value ?? "").trim()])
          .filter(([key]) => Boolean(key)),
      );
    }}

    function defaultStoryDraft() {{
      return {{
        title: "",
        summary: "",
        status: "active",
      }};
    }}

    function normalizeStoryDraft(payload = {{}}) {{
      return {{
        title: String(payload.title ?? "").trimStart(),
        summary: String(payload.summary ?? ""),
        status: storyStatusOptions.includes(String(payload.status || "").trim().toLowerCase())
          ? String(payload.status || "").trim().toLowerCase()
          : "active",
      }};
    }}

    function collectStoryDraft(form) {{
      if (!form) {{
        return normalizeStoryDraft(state.storyDraft || defaultStoryDraft());
      }}
      return normalizeStoryDraft({{
        title: String(form.elements.namedItem("title")?.value || ""),
        summary: String(form.elements.namedItem("summary")?.value || ""),
        status: String(form.elements.namedItem("status")?.value || "active"),
      }});
    }}

    function setStoryDraft(nextDraft) {{
      state.storyDraft = normalizeStoryDraft(nextDraft || defaultStoryDraft());
      renderStoryCreateDeck();
    }}

    function focusStoryDeck(fieldName = "title") {{
      jumpToSection("section-story");
      window.setTimeout(() => {{
        $("story-intake-shell")?.scrollIntoView({{ block: "start", behavior: "smooth" }});
        const form = $("story-create-form");
        const field = form?.elements?.namedItem(fieldName);
        if (field && typeof field.focus === "function") {{
          field.focus();
        }}
      }}, 140);
    }}

    function getStoryRecord(identifier) {{
      const normalized = String(identifier || "").trim();
      if (!normalized) {{
        return null;
      }}
      return state.storyDetails[normalized] || state.stories.find((story) => story.id === normalized) || null;
    }}

    function removeStoryFromState(identifier) {{
      const normalized = String(identifier || "").trim();
      if (!normalized) {{
        return;
      }}
      state.stories = state.stories.filter((story) => story.id !== normalized);
      delete state.storyDetails[normalized];
      delete state.storyGraph[normalized];
      delete state.storyMarkdown[normalized];
      if (state.selectedStoryId === normalized) {{
        state.selectedStoryId = state.stories[0] ? state.stories[0].id : "";
      }}
    }}

    function parseDelimitedInput(value) {{
      return uniqueValues(
        String(value || "")
          .split(",")
          .flatMap((value) => value.split(String.fromCharCode(10)).map((value) => value.replace(String.fromCharCode(13), "")))
      );
    }}

    function getClaimCardLabel(claim) {{
      if (!claim || typeof claim !== "object") {{
        return "";
      }}
      return String(claim.statement || claim.title || claim.id || "").trim();
    }}

    function getClaimCardRecord(identifier) {{
      const normalized = String(identifier || "").trim();
      if (!normalized) {{
        return null;
      }}
      return state.claimCards.find((claim) => String(claim.id || "").trim() === normalized) || null;
    }}

    function getReportRecord(identifier) {{
      const normalized = String(identifier || "").trim();
      if (!normalized) {{
        return null;
      }}
      const compositionReport = state.reportCompositions[normalized]?.report;
      if (compositionReport && typeof compositionReport === "object") {{
        return compositionReport;
      }}
      return state.reports.find((report) => String(report.id || "").trim() === normalized) || null;
    }}

    function getReportSectionsForReport(reportId) {{
      const normalized = String(reportId || "").trim();
      if (!normalized) {{
        return [];
      }}
      return state.reportSections
        .filter((section) => String(section.report_id || "").trim() === normalized)
        .sort((left, right) => {{
          const leftPosition = Number(left.position || 0);
          const rightPosition = Number(right.position || 0);
          if (leftPosition !== rightPosition) {{
            return leftPosition - rightPosition;
          }}
          return String(left.title || left.id || "").localeCompare(String(right.title || right.id || ""));
        }});
    }}

    function getReportComposition(identifier) {{
      const normalized = String(identifier || "").trim();
      if (!normalized) {{
        return null;
      }}
      const payload = state.reportCompositions[normalized];
      return payload && typeof payload === "object" ? payload : null;
    }}

    function getSelectedClaimCard() {{
      return getClaimCardRecord(state.selectedClaimId);
    }}

    function getSelectedReportRecord() {{
      return getReportRecord(state.selectedReportId);
    }}

    function getSelectedReportSectionRecord() {{
      const selectedReport = getSelectedReportRecord();
      if (!selectedReport) {{
        return null;
      }}
      const sections = getReportSectionsForReport(selectedReport.id);
      return sections.find((section) => String(section.id || "").trim() === String(state.selectedReportSectionId || "").trim()) || null;
    }}

    function getReportClaimIds(reportId) {{
      const composition = getReportComposition(reportId);
      if (composition && Array.isArray(composition.claim_cards)) {{
        return uniqueValues(composition.claim_cards.map((claim) => String(claim.id || "").trim()));
      }}
      const report = getReportRecord(reportId);
      return uniqueValues(Array.isArray(report?.claim_card_ids) ? report.claim_card_ids : []);
    }}

    function getCitationBundleRecord(identifier) {{
      const normalized = String(identifier || "").trim();
      if (!normalized) {{
        return null;
      }}
      return state.citationBundles.find((bundle) => String(bundle.id || "").trim() === normalized) || null;
    }}

    function reportStatusTone(status) {{
      const normalized = String(status || "").trim().toLowerCase();
      if (["ready", "ok", "pass", "clear", "success", "approved"].includes(normalized)) {{
        return "ok";
      }}
      if (["blocked", "error", "fail", "failed", "review_required", "warning", "warn", "conflicted"].includes(normalized)) {{
        return "hot";
      }}
      return "";
    }}

    function formatReportCheckLabel(key) {{
      const normalized = String(key || "").trim().toLowerCase();
      const labels = {{
        claim_source: copy("Claim source binding", "主张来源绑定"),
        section_coverage: copy("Section coverage", "章节覆盖"),
        contradictions: copy("Contradictions", "冲突"),
        export_gates: copy("Export gates", "导出门禁"),
        fact_consistency: copy("Fact consistency", "事实一致性"),
        coverage: copy("Coverage", "覆盖度"),
      }};
      return labels[normalized] || String(key || "").replace(/_/g, " ").trim();
    }}

    function formatReportOperatorAction(action) {{
      const normalized = String(action || "").trim().toLowerCase();
      const labels = {{
        allow_export: copy("Allow export", "允许导出"),
        review_before_export: copy("Review before export", "导出前复核"),
        hold_export: copy("Hold export", "暂停导出"),
        approve: copy("Approve", "批准"),
      }};
      return labels[normalized] || String(action || "").replace(/_/g, " ").trim();
    }}

    function syncReportSelectionState() {{
      const availableReports = Array.isArray(state.reports) ? state.reports : [];
      if (!availableReports.some((report) => String(report.id || "").trim() === String(state.selectedReportId || "").trim())) {{
        state.selectedReportId = availableReports[0] ? String(availableReports[0].id || "") : "";
      }}
      const sections = getReportSectionsForReport(state.selectedReportId);
      if (!sections.some((section) => String(section.id || "").trim() === String(state.selectedReportSectionId || "").trim())) {{
        state.selectedReportSectionId = sections[0] ? String(sections[0].id || "") : "";
      }}
      const availableClaims = Array.isArray(state.claimCards) ? state.claimCards : [];
      if (!availableClaims.some((claim) => String(claim.id || "").trim() === String(state.selectedClaimId || "").trim())) {{
        const reportClaimIds = getReportClaimIds(state.selectedReportId);
        const matchingClaim = availableClaims.find((claim) => reportClaimIds.includes(String(claim.id || "").trim()));
        state.selectedClaimId = matchingClaim
          ? String(matchingClaim.id || "")
          : (availableClaims[0] ? String(availableClaims[0].id || "") : "");
      }}
    }}

    async function loadReportComposition(identifier, {{ includeMarkdown = false, render = true }} = {{}}) {{
      const normalized = String(identifier || "").trim();
      if (!normalized) {{
        return;
      }}
      state.reportCompositions[normalized] = await api(`/api/reports/${{normalized}}/compose`);
      if (includeMarkdown) {{
        state.reportMarkdown[normalized] = await apiText(`/api/reports/${{normalized}}/export?output_format=markdown`);
      }}
      if (render) {{
        renderClaimsWorkspace();
        renderReportStudio();
        renderTopbarContext();
      }}
    }}

    async function selectReport(identifier, {{ sectionId = "" }} = {{}}) {{
      state.selectedReportId = String(identifier || "").trim();
      if (sectionId) {{
        state.selectedReportSectionId = String(sectionId || "").trim();
      }}
      syncReportSelectionState();
      renderClaimsWorkspace();
      renderReportStudio();
      renderTopbarContext();
      if (state.selectedReportId) {{
        await loadReportComposition(state.selectedReportId);
      }}
    }}

    async function previewReportMarkdown(identifier) {{
      const normalized = String(identifier || "").trim();
      if (!normalized) {{
        return;
      }}
      state.reportMarkdown[normalized] = await apiText(`/api/reports/${{normalized}}/export?output_format=markdown`);
      renderReportStudio();
    }}

    function formatDeliverySubjectKind(value) {{
      const normalized = String(value || "").trim().toLowerCase();
      const labels = {{
        profile: copy("Profile", "配置"),
        watch_mission: copy("Mission", "任务"),
        story: copy("Story", "故事"),
        report: copy("Report", "报告"),
      }};
      return labels[normalized] || String(value || "").replace(/_/g, " ").trim();
    }}

    function formatDeliveryOutputKind(value) {{
      const normalized = String(value || "").trim().toLowerCase();
      const labels = {{
        alert_event: copy("Alert Event", "告警事件"),
        feed_json: copy("JSON Feed", "JSON 订阅"),
        feed_rss: copy("RSS Feed", "RSS 订阅"),
        feed_atom: copy("Atom Feed", "Atom 订阅"),
        story_json: copy("Story JSON", "故事 JSON"),
        story_markdown: copy("Story Markdown", "故事 Markdown"),
        report_brief: copy("Report Brief", "报告摘要"),
        report_full: copy("Report Full", "完整报告"),
        report_sources: copy("Report Sources", "报告来源"),
        report_watch_pack: copy("Report Watch Pack", "报告监控包"),
      }};
      return labels[normalized] || String(value || "").replace(/_/g, " ").trim();
    }}

    function defaultDeliveryDraft() {{
      const selectedReport = getSelectedReportRecord();
      const firstReport = Array.isArray(state.reports) && state.reports.length ? state.reports[0] : null;
      const report = selectedReport || firstReport;
      const firstRoute = Array.isArray(state.routes) && state.routes.length
        ? normalizeRouteName(state.routes[0]?.name)
        : "";
      return {{
        subject_kind: report ? "report" : "profile",
        subject_ref: report ? String(report.id || "").trim() : "default",
        output_kind: report ? "report_full" : "feed_json",
        delivery_mode: firstRoute ? "push" : "pull",
        status: "active",
        route_names: firstRoute ? [firstRoute] : [],
        cursor_or_since: "",
      }};
    }}

    function getDeliverySubjectRefOptions(subjectKind) {{
      const normalized = String(subjectKind || "").trim().toLowerCase();
      if (normalized === "profile") {{
        return [{{
          value: "default",
          label: copy("Default profile", "默认配置"),
          detail: copy("Use the canonical feed subscription target.", "使用默认的订阅配置目标。"),
        }}];
      }}
      if (normalized === "watch_mission") {{
        return (Array.isArray(state.watches) ? state.watches : []).map((watch) => ({{
          value: String(watch.id || "").trim(),
          label: String(watch.name || watch.id || "").trim(),
          detail: String(watch.query || "").trim(),
        }}));
      }}
      if (normalized === "story") {{
        return (Array.isArray(state.stories) ? state.stories : []).map((story) => ({{
          value: String(story.id || "").trim(),
          label: String(story.title || story.id || "").trim(),
          detail: String(story.summary || "").trim(),
        }}));
      }}
      if (normalized === "report") {{
        return (Array.isArray(state.reports) ? state.reports : []).map((report) => ({{
          value: String(report.id || "").trim(),
          label: String(report.title || report.id || "").trim(),
          detail: String(report.summary || "").trim(),
        }}));
      }}
      return [];
    }}

    function getDeliveryOutputOptions(subjectKind) {{
      const normalized = String(subjectKind || "").trim().toLowerCase();
      return (deliveryOutputOptionsBySubject[normalized] || []).map((value) => ({{
        value,
        label: formatDeliveryOutputKind(value),
      }}));
    }}

    function normalizeDeliveryDraft(draft) {{
      const source = draft && typeof draft === "object" ? draft : defaultDeliveryDraft();
      const subjectKind = deliverySubjectOptions.includes(String(source.subject_kind || "").trim().toLowerCase())
        ? String(source.subject_kind || "").trim().toLowerCase()
        : defaultDeliveryDraft().subject_kind;
      const subjectOptions = getDeliverySubjectRefOptions(subjectKind);
      const outputOptions = getDeliveryOutputOptions(subjectKind);
      const subjectRef = subjectOptions.some((option) => option.value === String(source.subject_ref || "").trim())
        ? String(source.subject_ref || "").trim()
        : (subjectOptions[0]?.value || "");
      const outputKind = outputOptions.some((option) => option.value === String(source.output_kind || "").trim())
        ? String(source.output_kind || "").trim()
        : (outputOptions[0]?.value || "");
      const deliveryMode = deliveryModeOptions.includes(String(source.delivery_mode || "").trim().toLowerCase())
        ? String(source.delivery_mode || "").trim().toLowerCase()
        : "pull";
      const status = deliveryStatusOptions.includes(String(source.status || "").trim().toLowerCase())
        ? String(source.status || "").trim().toLowerCase()
        : "active";
      const routeNames = uniqueValues((Array.isArray(source.route_names) ? source.route_names : parseDelimitedInput(source.route_names))
        .map((value) => normalizeRouteName(value))
        .filter(Boolean));
      return {{
        subject_kind: subjectKind,
        subject_ref: subjectRef,
        output_kind: outputKind,
        delivery_mode: deliveryMode,
        status,
        route_names: routeNames,
        cursor_or_since: String(source.cursor_or_since || "").trim(),
      }};
    }}

    function collectDeliveryDraft(form) {{
      const formData = new FormData(form);
      return normalizeDeliveryDraft({{
        subject_kind: formData.get("subject_kind"),
        subject_ref: formData.get("subject_ref"),
        output_kind: formData.get("output_kind"),
        delivery_mode: formData.get("delivery_mode"),
        status: formData.get("status"),
        route_names: parseDelimitedInput(formData.get("route_names")),
        cursor_or_since: formData.get("cursor_or_since"),
      }});
    }}

    function syncDeliveryDraft() {{
      state.deliveryDraft = normalizeDeliveryDraft(state.deliveryDraft || defaultDeliveryDraft());
    }}

    function defaultDigestProfileDraft() {{
      const profile = state.digestConsole?.profile?.profile && typeof state.digestConsole.profile.profile === "object"
        ? state.digestConsole.profile.profile
        : {{}};
      const target = profile.default_delivery_target && typeof profile.default_delivery_target === "object"
        ? profile.default_delivery_target
        : {{}};
      const firstRoute = Array.isArray(state.routes) && state.routes.length
        ? normalizeRouteName(state.routes[0]?.name)
        : "";
      return {{
        language: String(profile.language || "en").trim() || "en",
        timezone: String(profile.timezone || "UTC").trim() || "UTC",
        frequency: String(profile.frequency || "@daily").trim() || "@daily",
        default_delivery_target: {{
          kind: "route",
          ref: normalizeRouteName(target.ref || firstRoute),
        }},
      }};
    }}

    function normalizeDigestProfileDraft(draft) {{
      const source = draft && typeof draft === "object" ? draft : defaultDigestProfileDraft();
      const target = source.default_delivery_target && typeof source.default_delivery_target === "object"
        ? source.default_delivery_target
        : {{}};
      return {{
        language: String(source.language || "en").trim() || "en",
        timezone: String(source.timezone || "UTC").trim() || "UTC",
        frequency: String(source.frequency || "@daily").trim() || "@daily",
        default_delivery_target: {{
          kind: "route",
          ref: normalizeRouteName(target.ref || ""),
        }},
      }};
    }}

    function syncDigestProfileDraft() {{
      state.digestProfileDraft = normalizeDigestProfileDraft(state.digestProfileDraft || defaultDigestProfileDraft());
    }}

    function collectDigestProfileDraft(form) {{
      const formData = new FormData(form);
      return normalizeDigestProfileDraft({{
        language: formData.get("language"),
        timezone: formData.get("timezone"),
        frequency: formData.get("frequency"),
        default_delivery_target: {{
          kind: "route",
          ref: formData.get("default_delivery_target_ref"),
        }},
      }});
    }}

    function summarizePathTail(value, depth = 2) {{
      const parts = String(value || "").split("/").filter(Boolean);
      if (!parts.length) {{
        return "";
      }}
      return parts.slice(-Math.max(1, depth)).join("/");
    }}

    function getDeliverySubscriptionRecord(identifier) {{
      const normalized = String(identifier || "").trim();
      if (!normalized) {{
        return null;
      }}
      return (Array.isArray(state.deliverySubscriptions) ? state.deliverySubscriptions : [])
        .find((row) => String(row.id || "").trim() === normalized) || null;
    }}

    function getSelectedDeliverySubscription() {{
      return getDeliverySubscriptionRecord(state.selectedDeliverySubscriptionId);
    }}

    function syncDeliverySelectionState() {{
      const rows = Array.isArray(state.deliverySubscriptions) ? state.deliverySubscriptions : [];
      if (!rows.some((row) => String(row.id || "").trim() === String(state.selectedDeliverySubscriptionId || "").trim())) {{
        state.selectedDeliverySubscriptionId = rows[0] ? String(rows[0].id || "").trim() : "";
      }}
      const selected = getSelectedDeliverySubscription();
      if (!selected) {{
        return;
      }}
      const subscriptionId = String(selected.id || "").trim();
      const reportProfiles = String(selected.subject_kind || "").trim().toLowerCase() === "report"
        ? state.exportProfiles.filter((profile) => String(profile.report_id || "").trim() === String(selected.subject_ref || "").trim())
        : [];
      const currentProfileId = String(state.deliveryPackageProfileIds[subscriptionId] || "").trim();
      if (!reportProfiles.some((profile) => String(profile.id || "").trim() === currentProfileId)) {{
        state.deliveryPackageProfileIds[subscriptionId] = reportProfiles[0] ? String(reportProfiles[0].id || "").trim() : "";
      }}
    }}

    function summarizeDeliverySubject(subscription) {{
      if (!subscription || typeof subscription !== "object") {{
        return "";
      }}
      const subjectKind = String(subscription.subject_kind || "").trim().toLowerCase();
      const subjectRef = String(subscription.subject_ref || "").trim();
      if (subjectKind === "report") {{
        return getReportRecord(subjectRef)?.title || subjectRef;
      }}
      if (subjectKind === "story") {{
        return (Array.isArray(state.stories) ? state.stories : [])
          .find((story) => String(story.id || "").trim() === subjectRef)?.title || subjectRef;
      }}
      if (subjectKind === "watch_mission") {{
        return (Array.isArray(state.watches) ? state.watches : [])
          .find((watch) => String(watch.id || "").trim() === subjectRef)?.name || subjectRef;
      }}
      return subjectRef || copy("Default profile", "默认配置");
    }}

    function getDeliveryDispatchRowsForSubscription(identifier) {{
      const normalized = String(identifier || "").trim();
      if (!normalized) {{
        return [];
      }}
      return (Array.isArray(state.deliveryDispatchRecords) ? state.deliveryDispatchRecords : [])
        .filter((row) => String(row.subscription_id || "").trim() === normalized);
    }}

    async function loadDeliveryPackageAudit(identifier, {{ profileId = "", render = true }} = {{}}) {{
      const normalized = String(identifier || "").trim();
      if (!normalized) {{
        return null;
      }}
      const query = profileId ? `?profile_id=${{encodeURIComponent(profileId)}}` : "";
      try {{
        const payload = await api(`/api/delivery-subscriptions/${{normalized}}/package${{query}}`);
        state.deliveryPackageAudits[normalized] = payload;
        state.deliveryPackageErrors[normalized] = "";
        state.deliveryPackageProfileIds[normalized] = String(payload.profile_id || profileId || "").trim();
        if (render) {{
          renderDeliveryWorkspace();
        }}
        return payload;
      }} catch (error) {{
        state.deliveryPackageErrors[normalized] = error.message;
        if (render) {{
          renderDeliveryWorkspace();
        }}
        throw error;
      }}
    }}

    async function loadDigestConsole({{ render = true, preserveDraft = true }} = {{}}) {{
      const payload = await api("/api/digest/console?profile=default&limit=8");
      state.digestConsole = payload;
      if (!preserveDraft || !state.digestProfileDraft) {{
        state.digestProfileDraft = normalizeDigestProfileDraft(payload?.profile?.profile || defaultDigestProfileDraft());
      }}
      if (render) {{
        renderDeliveryWorkspace();
      }}
      return payload;
    }}

    async function attachClaimToReport(claimId, reportId, sectionId = "", bundleId = "") {{
      const normalizedClaimId = String(claimId || "").trim();
      const normalizedReportId = String(reportId || "").trim();
      const normalizedSectionId = String(sectionId || "").trim();
      const normalizedBundleId = String(bundleId || "").trim();
      if (!normalizedClaimId || !normalizedReportId) {{
        return;
      }}
      const report = getReportRecord(normalizedReportId) || await api(`/api/reports/${{normalizedReportId}}`);
      const nextReportClaimIds = uniqueValues([...(Array.isArray(report?.claim_card_ids) ? report.claim_card_ids : []), normalizedClaimId]);
      const nextReportBundleIds = normalizedBundleId
        ? uniqueValues([...(Array.isArray(report?.citation_bundle_ids) ? report.citation_bundle_ids : []), normalizedBundleId])
        : (Array.isArray(report?.citation_bundle_ids) ? report.citation_bundle_ids : []);
      await api(`/api/reports/${{normalizedReportId}}`, {{
        method: "PUT",
        headers: jsonHeaders,
        body: JSON.stringify({{ claim_card_ids: nextReportClaimIds, citation_bundle_ids: nextReportBundleIds }}),
      }});
      if (normalizedSectionId) {{
        const section = getReportSectionsForReport(normalizedReportId).find((entry) => String(entry.id || "").trim() === normalizedSectionId)
          || await api(`/api/report-sections/${{normalizedSectionId}}`);
        const nextSectionClaimIds = uniqueValues([...(Array.isArray(section?.claim_card_ids) ? section.claim_card_ids : []), normalizedClaimId]);
        await api(`/api/report-sections/${{normalizedSectionId}}`, {{
          method: "PUT",
          headers: jsonHeaders,
          body: JSON.stringify({{ claim_card_ids: nextSectionClaimIds }}),
        }});
      }}
    }}

    async function submitStoryDeck(form) {{
      const draft = collectStoryDraft(form);
      state.storyDraft = draft;
      if (!draft.title.trim()) {{
        showToast(copy("Provide a story title before creating a brief.", "创建故事前请先填写标题。"), "error");
        focusStoryDeck("title");
        return;
      }}
      const submitButton = form?.querySelector("button[type='submit']");
      if (submitButton) {{
        submitButton.disabled = true;
      }}
      try {{
        const created = await api("/api/stories", {{
          method: "POST",
          headers: jsonHeaders,
          body: JSON.stringify(draft),
        }});
        setStoryDraft(defaultStoryDraft());
        pushActionEntry({{
          kind: copy("story create", "故事创建"),
          label: state.language === "zh" ? `已创建故事：${{created.title}}` : `Created story: ${{created.title}}`,
          detail: copy("The story is now part of the workspace and can be archived or refined in place.", "该故事已进入工作台，后续可以继续编辑或归档。"),
          undoLabel: copy("Delete story", "删除故事"),
          undo: async () => {{
            await api(`/api/stories/${{created.id}}`, {{ method: "DELETE" }});
            await refreshBoard();
            showToast(
              state.language === "zh" ? `已删除故事：${{created.title}}` : `Story deleted: ${{created.title}}`,
              "success",
            );
          }},
        }});
        await refreshBoard();
        state.selectedStoryId = created.id;
        state.storyDetails[created.id] = created;
        renderStories();
        showToast(
          state.language === "zh" ? `故事已创建：${{created.title}}` : `Story created: ${{created.title}}`,
          "success",
        );
      }} catch (error) {{
        reportError(error, copy("Create story", "创建故事"));
      }} finally {{
        if (submitButton) {{
          submitButton.disabled = false;
        }}
      }}
    }}

    async function setStoryStatusQuick(identifier, nextStatus) {{
      const story = getStoryRecord(identifier);
      if (!story) {{
        throw new Error(copy("Story not found in the current workspace.", "当前工作区中没有找到该故事。"));
      }}
      const targetStatus = String(nextStatus || "").trim().toLowerCase();
      if (!targetStatus || targetStatus === String(story.status || "active").trim().toLowerCase()) {{
        return;
      }}
      const previousStory = {{
        title: story.title || "",
        summary: story.summary || "",
        status: story.status || "active",
      }};
      try {{
        await api(`/api/stories/${{story.id}}`, {{
          method: "PUT",
          headers: jsonHeaders,
          body: JSON.stringify({{ status: targetStatus }}),
        }});
        pushActionEntry({{
          kind: copy("story state", "故事状态"),
          label: state.language === "zh"
            ? `已将故事切换为 ${{localizeWord(targetStatus)}}：${{story.title}}`
            : `Story moved to ${{targetStatus}}: ${{story.title}}`,
          detail: copy("Use undo to restore the previous workspace state.", "如需回退，可在最近操作里恢复。"),
          undoLabel: copy("Restore story", "恢复故事"),
          undo: async () => {{
            await api(`/api/stories/${{story.id}}`, {{
              method: "PUT",
              headers: jsonHeaders,
              body: JSON.stringify(previousStory),
            }});
            await refreshBoard();
            showToast(
              state.language === "zh" ? `已恢复故事：${{previousStory.title}}` : `Story restored: ${{previousStory.title}}`,
              "success",
            );
          }},
        }});
        await refreshBoard();
        showToast(
          state.language === "zh"
            ? `故事状态已更新：${{story.title}}`
            : `Story status updated: ${{story.title}}`,
          "success",
        );
      }} catch (error) {{
        reportError(error, copy("Update story state", "更新故事状态"));
      }}
    }}

    async function deleteStoryFromWorkspace(identifier) {{
      const story = getStoryRecord(identifier);
      if (!story) {{
        throw new Error(copy("Story not found in the current workspace.", "当前工作区中没有找到该故事。"));
      }}
      const confirmed = window.confirm(
        state.language === "zh"
          ? `确认删除故事 ${{story.title}}？这会把它从当前工作台移除。`
          : `Delete story ${{story.title}} from the workspace?`,
      );
      if (!confirmed) {{
        return;
      }}
      const snapshot = JSON.parse(JSON.stringify(story));
      try {{
        await api(`/api/stories/${{story.id}}`, {{ method: "DELETE" }});
        removeStoryFromState(story.id);
        pushActionEntry({{
          kind: copy("story delete", "故事删除"),
          label: state.language === "zh" ? `已删除故事：${{story.title}}` : `Deleted story: ${{story.title}}`,
          detail: copy("The full story payload is kept in recent actions so you can restore it once.", "完整故事快照会暂存在最近操作中，方便你单次恢复。"),
          undoLabel: copy("Restore story", "恢复故事"),
          undo: async () => {{
            await api("/api/stories", {{
              method: "POST",
              headers: jsonHeaders,
              body: JSON.stringify(snapshot),
            }});
            await refreshBoard();
            showToast(
              state.language === "zh" ? `已恢复故事：${{snapshot.title}}` : `Story restored: ${{snapshot.title}}`,
              "success",
            );
          }},
        }});
        await refreshBoard();
        showToast(
          state.language === "zh" ? `故事已删除：${{story.title}}` : `Story deleted: ${{story.title}}`,
          "success",
        );
      }} catch (error) {{
        reportError(error, copy("Delete story", "删除故事"));
      }}
    }}

    function isStorySelected(storyId) {{
      return state.selectedStoryIds.includes(storyId);
    }}

    function toggleStorySelection(storyId, checked = null) {{
      if (!storyId) {{
        return;
      }}
      const next = new Set(state.selectedStoryIds);
      const shouldSelect = checked === null ? !next.has(storyId) : Boolean(checked);
      if (shouldSelect) {{
        next.add(storyId);
        state.selectedStoryId = storyId;
      }} else {{
        next.delete(storyId);
      }}
      state.selectedStoryIds = Array.from(next);
    }}

    function selectVisibleStories(filteredStories) {{
      const visibleIds = (Array.isArray(filteredStories) ? filteredStories : []).map((story) => story.id);
      state.selectedStoryIds = visibleIds;
      if (visibleIds.length && !visibleIds.includes(state.selectedStoryId)) {{
        state.selectedStoryId = visibleIds[0];
      }}
    }}

    function clearStorySelection() {{
      state.selectedStoryIds = [];
    }}

    async function runStoryBatchStatusUpdate(storyIds, nextStatus) {{
      const normalizedIds = uniqueValues(storyIds).filter((storyId) => state.stories.some((story) => story.id === storyId));
      if (!normalizedIds.length || !nextStatus || state.storyBulkBusy) {{
        return;
      }}
      state.storyBulkBusy = true;
      const previousStates = {{}};
      normalizedIds.forEach((storyId) => {{
        const currentStory = getStoryRecord(storyId);
        previousStates[storyId] = currentStory ? String(currentStory.status || "active") : "active";
        if (currentStory && state.storyDetails[storyId]) {{
          state.storyDetails[storyId] = {{
            ...state.storyDetails[storyId],
            status: nextStatus,
          }};
        }}
      }});
      renderStories();
      try {{
        for (const storyId of normalizedIds) {{
          await api(`/api/stories/${{storyId}}`, {{
            method: "PUT",
            headers: jsonHeaders,
            body: JSON.stringify({{ status: nextStatus }}),
          }});
        }}
        state.selectedStoryIds = [];
        pushActionEntry({{
          kind: copy("story batch", "故事批处理"),
          label: state.language === "zh"
            ? `已批量将 ${{normalizedIds.length}} 条故事切换为 ${{localizeWord(nextStatus)}}`
            : `Moved ${{normalizedIds.length}} stories to ${{nextStatus}}`,
          detail: state.language === "zh"
            ? `涉及故事：${{normalizedIds.join(", ")}}`
            : `Stories: ${{normalizedIds.join(", ")}}`,
          undoLabel: copy("Restore stories", "恢复故事"),
          undo: async () => {{
            for (const storyId of normalizedIds) {{
              await api(`/api/stories/${{storyId}}`, {{
                method: "PUT",
                headers: jsonHeaders,
                body: JSON.stringify({{ status: previousStates[storyId] || "active" }}),
              }});
            }}
            await refreshBoard();
            showToast(
              state.language === "zh"
                ? `已恢复 ${{normalizedIds.length}} 条故事`
                : `Restored ${{normalizedIds.length}} stories`,
              "success",
            );
          }},
        }});
        await refreshBoard();
        showToast(
          state.language === "zh"
            ? `已批量更新 ${{normalizedIds.length}} 条故事`
            : `Updated ${{normalizedIds.length}} stories`,
          "success",
        );
      }} catch (error) {{
        normalizedIds.forEach((storyId) => {{
          if (state.storyDetails[storyId]) {{
            state.storyDetails[storyId] = {{
              ...state.storyDetails[storyId],
              status: previousStates[storyId] || "active",
            }};
          }}
        }});
        renderStories();
        throw error;
      }} finally {{
        state.storyBulkBusy = false;
        renderStories();
      }}
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

    function persistStoryWorkspacePrefs() {{
      safeLocalStorageSet(storyFilterStorageKey, normalizeStoryFilter(state.storyFilter));
      safeLocalStorageSet(storySortStorageKey, normalizeStorySort(state.storySort));
      safeLocalStorageSet(storyWorkspaceModeStorageKey, normalizeStoryWorkspaceMode(state.storyWorkspaceMode));
    }}

    function loadCommandPaletteQuery() {{
      return String(safeLocalStorageGet(commandPaletteQueryStorageKey) || "").trim();
    }}

    function persistCommandPaletteQuery() {{
      const query = String(state.commandPalette.query || "").trim();
      if (!query) {{
        safeLocalStorageRemove(commandPaletteQueryStorageKey);
        return;
      }}
      safeLocalStorageSet(commandPaletteQueryStorageKey, query);
    }}

    function loadCommandPaletteRecent() {{
      const raw = safeLocalStorageGet(commandPaletteRecentStorageKey);
      if (!raw) {{
        return [];
      }}
      try {{
        return uniqueValues(JSON.parse(raw)).slice(0, 8);
      }} catch (error) {{
        safeLocalStorageRemove(commandPaletteRecentStorageKey);
        return [];
      }}
    }}

    function persistCommandPaletteRecent() {{
      const recentIds = uniqueValues(state.commandPalette.recentIds || []).slice(0, 8);
      if (!recentIds.length) {{
        safeLocalStorageRemove(commandPaletteRecentStorageKey);
        return;
      }}
      safeLocalStorageSet(commandPaletteRecentStorageKey, JSON.stringify(recentIds));
    }}

    function noteCommandPaletteRecent(entryId) {{
      const normalized = String(entryId || "").trim();
      if (!normalized) {{
        return;
      }}
      state.commandPalette.recentIds = [normalized, ...uniqueValues(state.commandPalette.recentIds || []).filter((id) => id !== normalized)].slice(0, 8);
      persistCommandPaletteRecent();
    }}

    function normalizeContextLinkHistoryEntry(entry) {{
      const url = String(entry?.url || "").trim();
      if (!url) {{
        return null;
      }}
      const summary = clampLabel(String(entry?.summary || "").trim(), 96) || url;
      const sectionId = normalizeSectionId(entry?.sectionId || "section-intake");
      const timestamp = String(entry?.timestamp || "").trim() || new Date().toISOString();
      return {{ url, summary, sectionId, timestamp }};
    }}

    function loadContextLinkHistory() {{
      const raw = safeLocalStorageGet(contextLinkHistoryStorageKey);
      if (!raw) {{
        return [];
      }}
      try {{
        const parsed = JSON.parse(raw);
        return (Array.isArray(parsed) ? parsed : [])
          .map((entry) => normalizeContextLinkHistoryEntry(entry))
          .filter(Boolean)
          .slice(0, 6);
      }} catch (error) {{
        safeLocalStorageRemove(contextLinkHistoryStorageKey);
        return [];
      }}
    }}

    function persistContextLinkHistory() {{
      const entries = (Array.isArray(state.contextLinkHistory) ? state.contextLinkHistory : [])
        .map((entry) => normalizeContextLinkHistoryEntry(entry))
        .filter(Boolean)
        .slice(0, 6);
      if (!entries.length) {{
        safeLocalStorageRemove(contextLinkHistoryStorageKey);
        return;
      }}
      safeLocalStorageSet(contextLinkHistoryStorageKey, JSON.stringify(entries));
    }}

    function noteContextLinkHistory(entry) {{
      const normalized = normalizeContextLinkHistoryEntry(entry);
      if (!normalized) {{
        return;
      }}
      state.contextLinkHistory = [
        normalized,
        ...(Array.isArray(state.contextLinkHistory) ? state.contextLinkHistory : [])
          .map((candidate) => normalizeContextLinkHistoryEntry(candidate))
          .filter((candidate) => candidate && candidate.url !== normalized.url),
      ].slice(0, 6);
      persistContextLinkHistory();
      renderCommandPalette();
    }}

    function clearContextLinkHistory({{ toast = true }} = {{}}) {{
      state.contextLinkHistory = [];
      persistContextLinkHistory();
      renderCommandPalette();
      renderTopbarContext();
      if (toast) {{
        showToast(copy("Shared context history cleared", "已清空分享上下文历史"), "success");
      }}
    }}

    function normalizeContextSavedViewEntry(entry) {{
      const url = String(entry?.url || "").trim();
      const rawName = String(entry?.name || "").trim();
      if (!(url && rawName)) {{
        return null;
      }}
      const name = clampLabel(rawName, 72);
      const summary = clampLabel(String(entry?.summary || "").trim(), 96) || url;
      const sectionId = normalizeSectionId(entry?.sectionId || "section-intake");
      const timestamp = String(entry?.timestamp || "").trim() || new Date().toISOString();
      const pinned = Boolean(entry?.pinned);
      const isDefault = Boolean(entry?.isDefault);
      return {{ name, url, summary, sectionId, timestamp, pinned, isDefault }};
    }}

    function loadContextSavedViews() {{
      const raw = safeLocalStorageGet(contextSavedViewsStorageKey);
      if (!raw) {{
        return [];
      }}
      try {{
        const parsed = JSON.parse(raw);
        return (Array.isArray(parsed) ? parsed : [])
          .map((entry) => normalizeContextSavedViewEntry(entry))
          .filter(Boolean)
          .slice(0, 8);
      }} catch (error) {{
        safeLocalStorageRemove(contextSavedViewsStorageKey);
        return [];
      }}
    }}

    function persistContextSavedViews() {{
      const entries = (Array.isArray(state.contextSavedViews) ? state.contextSavedViews : [])
        .map((entry) => normalizeContextSavedViewEntry(entry))
        .filter(Boolean)
        .slice(0, 8);
      if (!entries.length) {{
        safeLocalStorageRemove(contextSavedViewsStorageKey);
        return;
      }}
      safeLocalStorageSet(contextSavedViewsStorageKey, JSON.stringify(entries));
    }}

    function upsertContextSavedView(entry) {{
      const normalized = normalizeContextSavedViewEntry(entry);
      if (!normalized) {{
        return false;
      }}
      const hasPinnedOverride = Object.prototype.hasOwnProperty.call(entry || {{}}, "pinned");
      const hasDefaultOverride = Object.prototype.hasOwnProperty.call(entry || {{}}, "isDefault");
      const existing = (Array.isArray(state.contextSavedViews) ? state.contextSavedViews : [])
        .map((candidate) => normalizeContextSavedViewEntry(candidate))
        .filter(Boolean);
      const existingIndex = existing.findIndex((candidate) => candidate.name.toLowerCase() === normalized.name.toLowerCase());
      const existingPinned = existingIndex >= 0 ? Boolean(existing[existingIndex]?.pinned) : false;
      const existingDefault = existingIndex >= 0 ? Boolean(existing[existingIndex]?.isDefault) : false;
      const resolvedEntry = {{
        ...normalized,
        pinned: hasPinnedOverride ? Boolean(entry.pinned) : existingPinned,
        isDefault: hasDefaultOverride ? Boolean(entry.isDefault) : existingDefault,
      }};
      const next = existingIndex >= 0
        ? existing.map((candidate, index) => (index === existingIndex ? resolvedEntry : candidate))
        : [resolvedEntry, ...existing].slice(0, 8);
      state.contextSavedViews = next;
      persistContextSavedViews();
      renderCommandPalette();
      renderTopbarContext();
      return existingIndex >= 0;
    }}

    function findContextSavedViewIndexByName(viewName) {{
      const normalizedName = String(viewName || "").trim().toLowerCase();
      if (!normalizedName) {{
        return -1;
      }}
      return (Array.isArray(state.contextSavedViews) ? state.contextSavedViews : [])
        .map((entry) => normalizeContextSavedViewEntry(entry))
        .findIndex((entry) => entry && entry.name.toLowerCase() === normalizedName);
    }}

    function findContextSavedViewIndexByUrl(viewUrl) {{
      const normalizedUrl = String(viewUrl || "").trim();
      if (!normalizedUrl) {{
        return -1;
      }}
      return (Array.isArray(state.contextSavedViews) ? state.contextSavedViews : [])
        .map((entry) => normalizeContextSavedViewEntry(entry))
        .findIndex((entry) => entry && entry.url === normalizedUrl);
    }}

    function buildUniqueContextSavedViewName(baseName) {{
      const trimmedBase = clampLabel(String(baseName || "").trim(), 72) || copy("Saved View", "保存视图");
      const normalizedExisting = new Set(
        (Array.isArray(state.contextSavedViews) ? state.contextSavedViews : [])
          .map((entry) => normalizeContextSavedViewEntry(entry))
          .filter(Boolean)
          .map((entry) => entry.name.toLowerCase())
      );
      if (!normalizedExisting.has(trimmedBase.toLowerCase())) {{
        return trimmedBase;
      }}
      let counter = 2;
      while (counter < 100) {{
        const candidate = clampLabel(`${{trimmedBase}} ${{counter}}`, 72);
        if (!normalizedExisting.has(candidate.toLowerCase())) {{
          return candidate;
        }}
        counter += 1;
      }}
      return clampLabel(`${{trimmedBase}} copy`, 72);
    }}

    function saveCurrentContextView(rawName = "") {{
      const base = buildCurrentContextLinkRecord();
      if (!base) {{
        return;
      }}
      const preferredName = String(rawName || "").trim() || base.summary;
      const wasOverwrite = upsertContextSavedView({{
        name: preferredName,
        ...base,
        timestamp: new Date().toISOString(),
      }});
      const input = $("context-save-name");
      if (input) {{
        input.value = "";
      }}
      showToast(
        wasOverwrite
          ? copy("Saved view updated", "已更新保存视图")
          : copy("Saved view added", "已保存当前视图"),
        "success",
      );
    }}

    function saveAndPinCurrentContextView() {{
      const current = buildCurrentContextLinkRecord();
      if (!current) {{
        return;
      }}
      const existingIndex = findContextSavedViewIndexByUrl(current.url);
      if (existingIndex >= 0) {{
        const existing = normalizeContextSavedViewEntry(state.contextSavedViews[existingIndex]);
        if (existing?.pinned) {{
          showToast(copy("Current view is already pinned", "当前视图已固定到坞站"), "success");
          return;
        }}
        if (countPinnedContextSavedViews() >= 4) {{
          showToast(copy("Pin up to four saved views in the top dock.", "顶部坞站最多固定四个保存视图。"), "error");
          return;
        }}
        upsertContextSavedView({{
          ...existing,
          ...current,
          name: existing.name,
          pinned: true,
          isDefault: existing.isDefault,
          timestamp: new Date().toISOString(),
        }});
        showToast(copy("Current view saved to the top dock", "已将当前视图固定到顶部坞站"), "success");
        return;
      }}
      if (countPinnedContextSavedViews() >= 4) {{
        showToast(copy("Pin up to four saved views in the top dock.", "顶部坞站最多固定四个保存视图。"), "error");
        return;
      }}
      upsertContextSavedView({{
        name: buildUniqueContextSavedViewName(current.summary),
        ...current,
        pinned: true,
        timestamp: new Date().toISOString(),
      }});
      showToast(copy("Current view saved and pinned", "已保存并固定当前视图"), "success");
    }}

    function startContextDockRename(viewName) {{
      const index = findContextSavedViewIndexByName(viewName);
      if (index < 0) {{
        return;
      }}
      const entry = normalizeContextSavedViewEntry(state.contextSavedViews[index]);
      if (!entry || !entry.pinned) {{
        return;
      }}
      state.contextDockEditingName = entry.name;
      renderTopbarContext();
      window.setTimeout(() => {{
        const input = $("context-dock-rename-input");
        input?.focus();
        input?.select();
      }}, 10);
    }}

    function cancelContextDockRename() {{
      if (!String(state.contextDockEditingName || "").trim()) {{
        return;
      }}
      state.contextDockEditingName = "";
      renderTopbarContext();
    }}

    function renameContextSavedView(viewName, rawNextName) {{
      const index = findContextSavedViewIndexByName(viewName);
      if (index < 0) {{
        return;
      }}
      const current = normalizeContextSavedViewEntry(state.contextSavedViews[index]);
      if (!current) {{
        return;
      }}
      const nextName = clampLabel(String(rawNextName || "").trim(), 72);
      if (!nextName) {{
        showToast(copy("Provide a name before saving the view label.", "保存视图标签前请先填写名称。"), "error");
        return;
      }}
      const duplicateIndex = findContextSavedViewIndexByName(nextName);
      if (duplicateIndex >= 0 && duplicateIndex !== index) {{
        showToast(copy("A saved view with that name already exists.", "已有同名保存视图。"), "error");
        return;
      }}
      state.contextSavedViews = (Array.isArray(state.contextSavedViews) ? state.contextSavedViews : []).map((candidate, candidateIndex) => {{
        const normalized = normalizeContextSavedViewEntry(candidate);
        if (!normalized) {{
          return candidate;
        }}
        if (candidateIndex !== index) {{
          return normalized;
        }}
        return {{
          ...normalized,
          name: nextName,
          timestamp: new Date().toISOString(),
        }};
      }});
      state.contextDockEditingName = "";
      persistContextSavedViews();
      renderCommandPalette();
      renderTopbarContext();
      showToast(
        state.language === "zh" ? `已重命名视图：${{nextName}}` : `Saved view renamed: ${{nextName}}`,
        "success",
      );
    }}

    function deleteContextSavedView(entryIndex, {{ toast = true }} = {{}}) {{
      const index = Number(entryIndex);
      const current = normalizeContextSavedViewEntry(state.contextSavedViews[index]);
      if (!current) {{
        return;
      }}
      if (String(state.contextDockEditingName || "").trim().toLowerCase() === String(current.name || "").trim().toLowerCase()) {{
        state.contextDockEditingName = "";
      }}
      state.contextSavedViews = (Array.isArray(state.contextSavedViews) ? state.contextSavedViews : [])
        .filter((_, candidateIndex) => candidateIndex !== index);
      persistContextSavedViews();
      renderCommandPalette();
      renderTopbarContext();
      if (toast) {{
        showToast(
          state.language === "zh" ? `已删除保存视图：${{current.name}}` : `Saved view removed: ${{current.name}}`,
          "success",
        );
      }}
    }}

    function clearContextSavedViews({{ toast = true }} = {{}}) {{
      state.contextSavedViews = [];
      state.contextDockEditingName = "";
      persistContextSavedViews();
      renderCommandPalette();
      renderTopbarContext();
      if (toast) {{
        showToast(copy("Saved views cleared", "已清空保存视图"), "success");
      }}
    }}

    function getDefaultContextSavedView() {{
      return (Array.isArray(state.contextSavedViews) ? state.contextSavedViews : [])
        .map((entry) => normalizeContextSavedViewEntry(entry))
        .find((entry) => entry && entry.isDefault) || null;
    }}

    function clearDefaultContextSavedView({{ toast = true }} = {{}}) {{
      const currentDefault = getDefaultContextSavedView();
      if (!currentDefault) {{
        return;
      }}
      state.contextSavedViews = (Array.isArray(state.contextSavedViews) ? state.contextSavedViews : []).map((candidate) => {{
        const normalized = normalizeContextSavedViewEntry(candidate);
        return normalized ? {{ ...normalized, isDefault: false }} : candidate;
      }});
      persistContextSavedViews();
      renderCommandPalette();
      renderTopbarContext();
      if (toast) {{
        showToast(copy("Default landing view cleared", "已清除默认落地视图"), "success");
      }}
    }}

    function setDefaultContextSavedView(entryIndex) {{
      const index = Number(entryIndex);
      const target = normalizeContextSavedViewEntry(state.contextSavedViews[index]);
      if (!target) {{
        return;
      }}
      const shouldUnset = Boolean(target.isDefault);
      state.contextSavedViews = (Array.isArray(state.contextSavedViews) ? state.contextSavedViews : []).map((candidate, candidateIndex) => {{
        const normalized = normalizeContextSavedViewEntry(candidate);
        if (!normalized) {{
          return candidate;
        }}
        return {{
          ...normalized,
          isDefault: shouldUnset ? false : candidateIndex === index,
        }};
      }});
      persistContextSavedViews();
      renderCommandPalette();
      renderTopbarContext();
      showToast(
        shouldUnset
          ? copy("Default landing view cleared", "已清除默认落地视图")
          : copy("Default landing view updated", "已更新默认落地视图"),
        "success",
      );
    }}

    function hasExplicitWorkspaceUrlContext() {{
      return Boolean(
        readWatchUrlState().hasWatchContext ||
        readTriageUrlState().hasTriageContext ||
        readStoryUrlState().hasStoryContext ||
        String(window.location.hash || "").trim()
      );
    }}

    function countPinnedContextSavedViews() {{
      return (Array.isArray(state.contextSavedViews) ? state.contextSavedViews : [])
        .map((entry) => normalizeContextSavedViewEntry(entry))
        .filter((entry) => entry && entry.pinned)
        .length;
    }}

    function getPinnedContextSavedViewIndexes() {{
      return (Array.isArray(state.contextSavedViews) ? state.contextSavedViews : [])
        .map((entry, index) => {{
          const normalized = normalizeContextSavedViewEntry(entry);
          return normalized && normalized.pinned ? index : -1;
        }})
        .filter((index) => index >= 0);
    }}

    function toggleContextSavedViewPinned(entryIndex) {{
      const index = Number(entryIndex);
      const entry = normalizeContextSavedViewEntry(state.contextSavedViews[index]);
      if (!entry) {{
        return;
      }}
      if (!entry.pinned && countPinnedContextSavedViews() >= 4) {{
        showToast(copy("Pin up to four saved views in the top dock.", "顶部坞站最多固定四个保存视图。"), "error");
        return;
      }}
      if (entry.pinned && String(state.contextDockEditingName || "").trim().toLowerCase() === String(entry.name || "").trim().toLowerCase()) {{
        state.contextDockEditingName = "";
      }}
      state.contextSavedViews = (Array.isArray(state.contextSavedViews) ? state.contextSavedViews : []).map((candidate, candidateIndex) => {{
        const normalized = normalizeContextSavedViewEntry(candidate);
        if (!normalized) {{
          return candidate;
        }}
        if (candidateIndex !== index) {{
          return normalized;
        }}
        return {{
          ...normalized,
          pinned: !normalized.pinned,
          timestamp: new Date().toISOString(),
        }};
      }});
      persistContextSavedViews();
      renderCommandPalette();
      renderTopbarContext();
      showToast(
        entry.pinned
          ? copy("Saved view removed from the top dock", "已从顶部坞站取消固定")
          : copy("Saved view pinned to the top dock", "已固定到顶部坞站"),
        "success",
      );
    }}

    function moveContextSavedViewInDock(entryIndex, direction = "left") {{
      const index = Number(entryIndex);
      const entry = normalizeContextSavedViewEntry(state.contextSavedViews[index]);
      if (!entry || !entry.pinned) {{
        return;
      }}
      const pinnedIndexes = getPinnedContextSavedViewIndexes();
      const currentPosition = pinnedIndexes.indexOf(index);
      if (currentPosition < 0) {{
        return;
      }}
      const offset = direction === "right" ? 1 : -1;
      const nextPosition = currentPosition + offset;
      if (nextPosition < 0 || nextPosition >= pinnedIndexes.length) {{
        return;
      }}
      const swapIndex = pinnedIndexes[nextPosition];
      const reordered = (Array.isArray(state.contextSavedViews) ? state.contextSavedViews : [])
        .map((candidate) => normalizeContextSavedViewEntry(candidate))
        .filter(Boolean);
      [reordered[index], reordered[swapIndex]] = [reordered[swapIndex], reordered[index]];
      state.contextSavedViews = reordered;
      persistContextSavedViews();
      renderCommandPalette();
      renderTopbarContext();
      showToast(
        direction === "right"
          ? copy("Pinned view moved right", "已将固定视图右移")
          : copy("Pinned view moved left", "已将固定视图左移"),
        "success",
      );
    }}

    function resetWorkspaceContext({{ jump = true, toast = true }} = {{}}) {{
      setContextLensOpen(false);
      state.watchSearch = "";
      state.selectedWatchId = state.watches[0] ? state.watches[0].id : "";
      state.watchResultFilters = {{}};
      setContextRouteName("", "");

      state.triageFilter = "open";
      state.triageSearch = "";
      state.triagePinnedIds = [];
      state.selectedTriageIds = [];
      state.selectedTriageId = "";
      state.triageUrlFocusPending = false;

      state.storySearch = "";
      state.storyWorkspaceMode = "board";
      state.storyFilter = "all";
      state.storySort = "attention";
      state.selectedStoryIds = [];
      state.selectedStoryId = state.stories[0] ? state.stories[0].id : "";
      state.storyUrlFocusPending = false;
      persistStoryWorkspacePrefs();

      state.selectedClaimId = state.claimCards[0] ? state.claimCards[0].id : "";
      state.selectedReportId = state.reports[0] ? state.reports[0].id : "";
      const defaultSections = getReportSectionsForReport(state.selectedReportId);
      state.selectedReportSectionId = defaultSections[0] ? defaultSections[0].id : "";

      state.commandPalette.query = "";
      persistCommandPaletteQuery();
      closeCommandPalette();

      state.watchUrlFocusPending = false;
      renderWatches();
      renderWatchDetail();
      renderTriage();
      renderStories();
      renderClaimsWorkspace();
      renderReportStudio();
      renderCommandPalette();
      if (jump) {{
        jumpToSection("section-intake");
      }}
      if (toast) {{
        showToast(copy("Workspace context reset", "当前工作上下文已重置"), "success");
      }}
    }}

    function applyStoryViewPreset(viewKey, {{ jump = false, toast = false }} = {{}}) {{
      const preset = getStoryViewPreset(viewKey);
      if (!preset) {{
        return;
      }}
      state.storySearch = "";
      state.storyFilter = preset.filter;
      state.storySort = preset.sort;
      persistStoryWorkspacePrefs();
      renderStories();
      if (jump) {{
        jumpToSection("section-story");
      }}
      if (toast) {{
        showToast(
          state.language === "zh"
            ? `故事视图已切换：${{storyViewPresetLabel(preset.key)}}`
            : `Story view switched: ${{storyViewPresetLabel(preset.key)}}`,
          "success",
        );
      }}
    }}

    function renderStoryViewJumpStrip() {{
      const root = $("story-view-jumps");
      if (!root) {{
        return;
      }}
      const activeStoryView = detectStoryViewPreset({{
        filter: state.storyFilter,
        sort: state.storySort,
        search: state.storySearch,
      }});
      root.innerHTML = `
        ${{storyViewPresetOptions.map((option) => `
          <button class="chip-btn ${{activeStoryView === option ? "active" : ""}}" type="button" data-story-view-shortcut="${{escapeHtml(option)}}">
            ${{escapeHtml(storyViewPresetLabel(option))}}
          </button>
        `).join("")}}
        ${{activeStoryView === "custom" ? `<span class="chip hot">${{storyViewPresetLabel("custom")}}</span>` : ""}}
      `;
      root.querySelectorAll("[data-story-view-shortcut]").forEach((button) => {{
        button.addEventListener("click", () => {{
          applyStoryViewPreset(String(button.dataset.storyViewShortcut || "").trim(), {{ jump: true }});
        }});
      }});
    }}

    function readWatchUrlState() {{
      const url = new URL(window.location.href);
      const params = url.searchParams;
      const search = String(params.get(watchUrlSearchParam) || "").trim();
      const watchId = String(params.get(watchUrlIdParam) || "").trim();
      const hasWatchContext = Boolean(search || watchId || url.hash === "#section-board" || url.hash === "#section-cockpit");
      return {{ hasWatchContext, search, watchId }};
    }}

    function applyWatchUrlStateFromLocation() {{
      const urlState = readWatchUrlState();
      if (!urlState.hasWatchContext) {{
        return;
      }}
      state.watchSearch = urlState.search;
      if (urlState.watchId) {{
        state.selectedWatchId = urlState.watchId;
      }}
      state.watchUrlFocusPending = true;
    }}

    function syncWatchUrlState({{ defaultWatchId = "" }} = {{}}) {{
      if (state.loading.board) {{
        return;
      }}
      const url = new URL(window.location.href);
      const params = url.searchParams;
      const search = String(state.watchSearch || "").trim();
      const watchId = String(state.selectedWatchId || "").trim();

      if (search) {{
        params.set(watchUrlSearchParam, search);
      }} else {{
        params.delete(watchUrlSearchParam);
      }}

      if (watchId && watchId !== String(defaultWatchId || "").trim()) {{
        params.set(watchUrlIdParam, watchId);
      }} else {{
        params.delete(watchUrlIdParam);
      }}

      const nextSearch = params.toString();
      const nextUrl = `${{url.pathname}}${{nextSearch ? `?${{nextSearch}}` : ""}}${{url.hash || ""}}`;
      const currentUrl = `${{window.location.pathname}}${{window.location.search}}${{window.location.hash}}`;
      if (nextUrl !== currentUrl) {{
        window.history.replaceState(window.history.state, "", nextUrl);
      }}
    }}

    function flushWatchUrlFocus() {{
      if (!state.watchUrlFocusPending) {{
        return;
      }}
      state.watchUrlFocusPending = false;
      window.setTimeout(() => {{
        jumpToSection(window.location.hash === "#section-board" ? "section-board" : "section-cockpit", {{ updateHash: false }});
      }}, 0);
    }}

    function readTriageUrlState() {{
      const url = new URL(window.location.href);
      const params = url.searchParams;
      const filter = String(params.get(triageUrlFilterParam) || "").trim().toLowerCase();
      const search = String(params.get(triageUrlSearchParam) || "").trim();
      const itemId = String(params.get(triageUrlIdParam) || "").trim();
      const hasTriageContext = Boolean(filter || search || itemId || url.hash === "#section-triage");
      return {{
        hasTriageContext,
        filter: normalizeTriageFilter(filter || state.triageFilter),
        search,
        itemId,
      }};
    }}

    function applyTriageUrlStateFromLocation() {{
      const urlState = readTriageUrlState();
      if (!urlState.hasTriageContext) {{
        return;
      }}
      state.triageFilter = urlState.filter;
      state.triageSearch = urlState.search;
      if (urlState.itemId) {{
        state.selectedTriageId = urlState.itemId;
      }}
      state.triageUrlFocusPending = true;
    }}

    function syncTriageUrlState({{ defaultItemId = "" }} = {{}}) {{
      if (state.loading.board) {{
        return;
      }}
      const url = new URL(window.location.href);
      const params = url.searchParams;
      const filter = normalizeTriageFilter(state.triageFilter);
      const search = String(state.triageSearch || "").trim();
      const itemId = String(state.selectedTriageId || "").trim();

      if (filter !== "open") {{
        params.set(triageUrlFilterParam, filter);
      }} else {{
        params.delete(triageUrlFilterParam);
      }}

      if (search) {{
        params.set(triageUrlSearchParam, search);
      }} else {{
        params.delete(triageUrlSearchParam);
      }}

      if (itemId && itemId !== String(defaultItemId || "").trim()) {{
        params.set(triageUrlIdParam, itemId);
      }} else {{
        params.delete(triageUrlIdParam);
      }}

      const nextSearch = params.toString();
      const nextUrl = `${{url.pathname}}${{nextSearch ? `?${{nextSearch}}` : ""}}${{url.hash || ""}}`;
      const currentUrl = `${{window.location.pathname}}${{window.location.search}}${{window.location.hash}}`;
      if (nextUrl !== currentUrl) {{
        window.history.replaceState(window.history.state, "", nextUrl);
      }}
    }}

    function flushTriageUrlFocus() {{
      if (!state.triageUrlFocusPending) {{
        return;
      }}
      state.triageUrlFocusPending = false;
      window.setTimeout(() => {{
        jumpToSection("section-triage", {{ updateHash: false }});
      }}, 0);
    }}

    function applyStoryWorkspaceMode(mode, {{ persist = true, syncUrl = false, defaultStoryId = "" }} = {{}}) {{
      state.storyWorkspaceMode = normalizeStoryWorkspaceMode(mode);
      if (document.body) {{
        document.body.dataset.storyWorkspaceMode = state.storyWorkspaceMode;
      }}
      const storyWorkspaceModeSwitch = $("story-workspace-mode-switch");
      if (storyWorkspaceModeSwitch) {{
        storyWorkspaceModeSwitch.querySelectorAll("[data-story-workspace-mode]").forEach((button) => {{
          const buttonMode = normalizeStoryWorkspaceMode(button.dataset.storyWorkspaceMode);
          const isActive = buttonMode === state.storyWorkspaceMode;
          button.classList.toggle("active", isActive);
          button.setAttribute("aria-pressed", isActive ? "true" : "false");
        }});
      }}
      if (persist) {{
        safeLocalStorageSet(storyWorkspaceModeStorageKey, normalizeStoryWorkspaceMode(state.storyWorkspaceMode));
      }}
      if (syncUrl) {{
        syncStoryUrlState({{ defaultStoryId }});
      }}
    }}

    function readStoryUrlState() {{
      const url = new URL(window.location.href);
      const params = url.searchParams;
      const view = String(params.get(storyUrlViewParam) || "").trim().toLowerCase();
      const filter = String(params.get(storyUrlFilterParam) || "").trim().toLowerCase();
      const sort = String(params.get(storyUrlSortParam) || "").trim().toLowerCase();
      const search = String(params.get(storyUrlSearchParam) || "").trim();
      const storyId = String(params.get(storyUrlIdParam) || "").trim();
      const storyWorkspaceMode = String(params.get(storyUrlModeParam) || "").trim().toLowerCase();
      const preset = getStoryViewPreset(view);
      const resolvedFilter = filter
        ? normalizeStoryFilter(filter)
        : (preset ? normalizeStoryFilter(preset.filter) : normalizeStoryFilter(state.storyFilter));
      const resolvedSort = sort
        ? normalizeStorySort(sort)
        : (preset ? normalizeStorySort(preset.sort) : normalizeStorySort(state.storySort));
      const resolvedStoryWorkspaceMode = normalizeStoryWorkspaceMode(storyWorkspaceMode);
      const hasStoryContext = Boolean(view || filter || sort || search || storyId || url.hash === "#section-story");
      return {{
        hasStoryContext,
        filter: resolvedFilter,
        sort: resolvedSort,
        search,
        storyId,
        storyWorkspaceMode: resolvedStoryWorkspaceMode,
      }};
    }}

    function applyStoryUrlStateFromLocation() {{
      const urlState = readStoryUrlState();
      if (!urlState.hasStoryContext) {{
        return;
      }}
      state.storyFilter = urlState.filter;
      state.storySort = urlState.sort;
      state.storySearch = urlState.search;
      state.storyWorkspaceMode = urlState.storyWorkspaceMode;
      if (urlState.storyId) {{
        state.selectedStoryId = urlState.storyId;
      }}
      state.storyUrlFocusPending = true;
    }}

    function syncStoryUrlState({{ defaultStoryId = "" }} = {{}}) {{
      if (state.loading.board) {{
        return;
      }}
      const url = new URL(window.location.href);
      const params = url.searchParams;
      const filter = normalizeStoryFilter(state.storyFilter);
      const sort = normalizeStorySort(state.storySort);
      const search = String(state.storySearch || "").trim();
      const storyId = String(state.selectedStoryId || "").trim();
      const activeView = detectStoryViewPreset({{ filter, sort, search }});

      if (!search && activeView !== "custom" && activeView !== "desk") {{
        params.set(storyUrlViewParam, activeView);
      }} else {{
        params.delete(storyUrlViewParam);
      }}

      if (activeView === "custom") {{
        if (filter !== "all") {{
          params.set(storyUrlFilterParam, filter);
        }} else {{
          params.delete(storyUrlFilterParam);
        }}
        if (sort !== "attention") {{
          params.set(storyUrlSortParam, sort);
        }} else {{
          params.delete(storyUrlSortParam);
        }}
      }} else {{
        params.delete(storyUrlFilterParam);
        params.delete(storyUrlSortParam);
      }}

      if (search) {{
        params.set(storyUrlSearchParam, search);
      }} else {{
        params.delete(storyUrlSearchParam);
      }}

      if (storyId && storyId !== String(defaultStoryId || "").trim()) {{
        params.set(storyUrlIdParam, storyId);
      }} else {{
        params.delete(storyUrlIdParam);
      }}
      if (state.storyWorkspaceMode === "editor") {{
        params.set(storyUrlModeParam, state.storyWorkspaceMode);
      }} else {{
        params.delete(storyUrlModeParam);
      }}

      const nextSearch = params.toString();
      const nextUrl = `${{url.pathname}}${{nextSearch ? `?${{nextSearch}}` : ""}}${{url.hash || ""}}`;
      const currentUrl = `${{window.location.pathname}}${{window.location.search}}${{window.location.hash}}`;
      if (nextUrl !== currentUrl) {{
        window.history.replaceState(window.history.state, "", nextUrl);
      }}
    }}

    function flushStoryUrlFocus() {{
      if (!state.storyUrlFocusPending) {{
        return;
      }}
      state.storyUrlFocusPending = false;
      window.setTimeout(() => {{
        jumpToSection("section-story", {{ updateHash: false }});
      }}, 0);
    }}

    applyWatchUrlStateFromLocation();
    applyTriageUrlStateFromLocation();
    state.storyWorkspaceMode = normalizeStoryWorkspaceMode(safeLocalStorageGet(storyWorkspaceModeStorageKey) || state.storyWorkspaceMode);
    state.storyFilter = normalizeStoryFilter(safeLocalStorageGet(storyFilterStorageKey) || state.storyFilter);
    state.storySort = normalizeStorySort(safeLocalStorageGet(storySortStorageKey) || state.storySort);
    applyStoryUrlStateFromLocation();
    applyStoryWorkspaceMode(state.storyWorkspaceMode, {{ persist: false }});
    state.commandPalette.query = loadCommandPaletteQuery();
    state.commandPalette.recentIds = loadCommandPaletteRecent();
    state.contextLinkHistory = loadContextLinkHistory();
    state.contextSavedViews = loadContextSavedViews();
    state.contextDefaultBootPending = !hasExplicitWorkspaceUrlContext();

    function detectInitialLanguage() {{
      const stored = String(safeLocalStorageGet(languageStorageKey) || "").trim().toLowerCase();
      if (stored === "zh" || stored === "en") {{
        return stored;
      }}
      const browserLanguage = String(window.navigator.language || "").trim().toLowerCase();
      return browserLanguage.startsWith("zh") ? "zh" : "en";
    }}

    function normalizeSectionId(value) {{
      const normalized = String(value || "").trim().replace(/^#/, "");
      return [
        "section-intake",
        "section-board",
        "section-cockpit",
        "section-triage",
        "section-story",
        "section-claims",
        "section-report-studio",
        "section-ops",
      ].includes(normalized)
        ? normalized
        : "section-intake";
    }}

    state.activeSectionId = normalizeSectionId(window.location.hash || state.activeSectionId);

    function setText(id, value) {{
      const node = $(id);
      if (node) {{
        node.textContent = value;
        if (node instanceof HTMLElement && node.hasAttribute("data-fit-text")) {{
          delete node.dataset.fitTextOriginal;
          delete node.dataset.fitApplied;
        }}
      }}
    }}

    function setHTML(id, value) {{
      const node = $(id);
      if (node) {{
        node.innerHTML = value;
      }}
    }}

    function setPlaceholder(id, value) {{
      const node = $(id);
      if (node) {{
        node.placeholder = value;
      }}
    }}

    function activeSectionLabel(sectionId) {{
      const labels = {{
        "section-intake": copy("Mission Intake", "任务录入"),
        "section-board": copy("Mission Board", "任务列表"),
        "section-cockpit": copy("Cockpit", "任务详情"),
        "section-triage": copy("Triage", "分诊"),
        "section-story": copy("Stories", "故事"),
        "section-claims": copy("Claim Composer", "主张装配"),
        "section-report-studio": copy("Report Studio", "报告工作台"),
        "section-ops": copy("Ops Snapshot", "运行状态"),
      }};
      return labels[normalizeSectionId(sectionId)] || labels["section-intake"];
    }}

    function normalizeWorkspaceMode(value) {{
      const normalized = String(value || "").trim().toLowerCase();
      return Object.prototype.hasOwnProperty.call(workspaceModeSectionMap, normalized) ? normalized : "intake";
    }}

    function workspaceModeForSection(sectionId) {{
      const normalizedSection = normalizeSectionId(sectionId);
      if (workspaceModeSectionMap.missions.includes(normalizedSection)) {{
        return "missions";
      }}
      if (workspaceModeSectionMap.review.includes(normalizedSection)) {{
        return "review";
      }}
      if (workspaceModeSectionMap.delivery.includes(normalizedSection)) {{
        return "delivery";
      }}
      return "intake";
    }}

    function workspaceModeDescriptor(modeId) {{
      const normalized = normalizeWorkspaceMode(modeId);
      const descriptors = {{
        intake: {{
          id: "intake",
          label: copy("Intake", "录入"),
          kicker: copy("Start", "开始"),
          summary: copy(
            "Keep mission intake as the clean landing surface so the first decision is just what to monitor next.",
            "把任务录入单独作为落地面，确保进入控制台后的第一个判断只是下一步要监测什么。"
          ),
          modules: [
            copy("Mission Intake", "任务录入"),
          ],
          landingSection: "section-intake",
          footnote: copy("Best for starting or cloning one mission without downstream noise.", "适合在不受下游噪音干扰的情况下新建或复制任务。"),
          topbarSubtitle: copy("Lifecycle rail | Intake -> Missions -> Review -> Delivery", "生命周期主轨 | 录入 -> 任务 -> 审阅 -> 交付"),
        }},
        missions: {{
          id: "missions",
          label: copy("Missions", "任务"),
          kicker: copy("Run", "执行"),
          summary: copy(
            "Keep board control and cockpit inspection in one lane so dispatch, recent evidence, and downstream handoff facts stay together.",
            "把任务列表和任务详情收进同一条工作线，让执行、近期证据和下游交接事实保持连贯。"
          ),
          modules: [
            copy("Mission Board", "任务列表"),
            copy("Cockpit", "任务详情"),
          ],
          landingSection: "section-board",
          footnote: copy("Best for dispatch, inspection, and alert-rule tuning.", "适合执行任务、查看结果和调整告警规则。"),
          topbarSubtitle: copy("Missions | Board -> Cockpit", "任务 | 列表 -> 详情"),
        }},
        review: {{
          id: "review",
          label: copy("Review", "审阅"),
          kicker: copy("Review", "审阅"),
          summary: copy(
            "Keep triage, stories, claims, and report composition in one evidence lane so review can move into exportable judgment without losing context.",
            "把分诊、故事、主张装配和报告编排收进同一条证据工作线，让审阅可以在不丢上下文的前提下推进成可导出的判断。"
          ),
          modules: [
            copy("Triage", "分诊"),
            copy("Stories", "故事"),
            copy("Claim Composer", "主张装配"),
            copy("Report Studio", "报告工作台"),
          ],
          landingSection: "section-triage",
          footnote: copy("Best for evidence review, claim composition, and report assembly.", "适合证据审阅、主张装配与报告编排。"),
          topbarSubtitle: copy("Review | Triage -> Stories -> Claims -> Report Studio", "审阅 | 分诊 -> 故事 -> 主张 -> 报告"),
        }},
        delivery: {{
          id: "delivery",
          label: copy("Delivery", "交付"),
          kicker: copy("Deliver", "交付"),
          summary: copy(
            "Keep alerting missions, route-backed delivery, and output health in one lane so downstream status stays visible without backtracking.",
            "把触发告警的任务、路由交付和输出健康收进同一条工作线，让下游状态保持可见而不用来回跳转。"
          ),
          modules: [
            copy("Ops Snapshot", "运行状态"),
            copy("Alert Stream", "告警动态"),
            copy("Route Manager", "路由管理"),
            copy("Distribution Health", "分发健康"),
          ],
          landingSection: "section-ops",
          footnote: copy("Best for delivery sinks, route health, and operator setup.", "适合交付路由、分发健康和配置维护。"),
          topbarSubtitle: copy("Delivery | Ops -> Alerts -> Routes", "交付 | 运行状态 -> 告警 -> 路由"),
        }},
      }};
      return descriptors[normalized] || descriptors.intake;
    }}

    function renderWorkspaceModeShell() {{
      const root = $("workspace-mode-shell");
      if (!root) {{
        return;
      }}
      root.hidden = true;
      root.innerHTML = "";
    }}

    function renderWorkspaceModeChrome() {{
      const activeSectionId = normalizeSectionId(state.activeSectionId);
      state.activeSectionId = activeSectionId;
      state.activeWorkspaceMode = workspaceModeForSection(activeSectionId);
      const modeDescriptor = workspaceModeDescriptor(state.activeWorkspaceMode);
      document.querySelectorAll("[data-workspace-group]").forEach((group) => {{
        const groupMode = normalizeWorkspaceMode(group.dataset.workspaceGroup || "");
        group.hidden = groupMode !== modeDescriptor.id;
      }});
      document.querySelectorAll(".topbar-nav [data-jump-target]").forEach((button) => {{
        const buttonMode = normalizeWorkspaceMode(button.dataset.workspaceMode || workspaceModeForSection(button.dataset.jumpTarget || ""));
        const active = buttonMode === modeDescriptor.id;
        button.hidden = false;
        button.classList.toggle("active", active);
        button.setAttribute("aria-current", active ? "page" : "false");
      }});
      setText("topbar-subtitle", modeDescriptor.topbarSubtitle);
      renderWorkspaceModeShell();
    }}

    state.activeWorkspaceMode = workspaceModeForSection(state.activeSectionId);

    function contextLensEmptyValue() {{
      return copy("Not set", "未设置");
    }}

    function buildTopbarContextDescriptor() {{
      const activeSectionId = normalizeSectionId(state.activeSectionId);
      state.activeSectionId = activeSectionId;
      state.activeWorkspaceMode = workspaceModeForSection(activeSectionId);
      const descriptor = {{
        modeId: state.activeWorkspaceMode,
        modeLabel: workspaceModeDescriptor(state.activeWorkspaceMode).label,
        sectionId: activeSectionId,
        sectionLabel: activeSectionLabel(activeSectionId),
        detail: "",
        rows: [],
      }};
      const pushRow = (label, value, {{ mono = false, muted = false }} = {{}}) => {{
        const hasValue = ![null, undefined].includes(value) && String(value).trim() !== "";
        descriptor.rows.push({{
          label,
          value: hasValue ? String(value).trim() : contextLensEmptyValue(),
          className: [
            mono ? "mono" : "",
            !hasValue || muted ? "muted" : "",
          ].filter(Boolean).join(" "),
        }});
      }};
      pushRow(copy("Rail", "主轨"), descriptor.modeLabel);

      if (activeSectionId === "section-intake") {{
        const draftName = String(state.createWatchDraft?.name || "").trim();
        const draftQuery = String(state.createWatchDraft?.query || "").trim();
        descriptor.detail = draftName || draftQuery
          ? clampLabel(draftName || draftQuery, 28)
          : copy("mission intake", "任务录入");
        pushRow(copy("Mode", "模式"), String(state.createWatchEditingId || "").trim() ? copy("Editing mission", "编辑任务") : copy("New mission", "新建任务"));
        pushRow(copy("Name", "名称"), clampLabel(draftName, 52));
        pushRow(copy("Query", "查询词"), clampLabel(draftQuery, 72), {{ mono: true }});
        pushRow(copy("Schedule", "频率"), String(state.createWatchDraft?.schedule || "").trim() || "manual", {{ mono: true }});
      }} else if (activeSectionId === "section-board" || activeSectionId === "section-cockpit") {{
        const selectedWatch = state.watchDetails[state.selectedWatchId] || state.watches.find((watch) => watch.id === state.selectedWatchId);
        const watchLabel = selectedWatch ? clampLabel(selectedWatch.name || selectedWatch.id, 28) : "";
        const watchSearch = String(state.watchSearch || "").trim();
        descriptor.detail = watchSearch
          ? phrase("q={{query}}", "搜索={{query}}", {{ query: clampLabel(watchSearch, 20) }})
          : (watchLabel || copy("mission focus", "任务聚焦"));
        pushRow(copy("Mission", "任务"), selectedWatch ? clampLabel(selectedWatch.name || selectedWatch.id, 52) : "");
        pushRow(copy("Search", "搜索"), clampLabel(watchSearch, 52), {{ mono: true }});
        pushRow(copy("Schedule", "频率"), String(selectedWatch?.schedule_label || selectedWatch?.schedule || "").trim(), {{ mono: true }});
        pushRow(copy("Alerts", "告警"), selectedWatch ? String(selectedWatch.alert_rule_count || (Array.isArray(selectedWatch.alert_rules) ? selectedWatch.alert_rules.length : 0) || 0) : "", {{ mono: true }});
      }} else if (activeSectionId === "section-triage") {{
        const triageFocus = state.triage.find((item) => item.id === state.selectedTriageId);
        const triageSearch = String(state.triageSearch || "").trim();
        if (state.triagePinnedIds.length) {{
          descriptor.detail = phrase("evidence x{{count}}", "证据 x{{count}}", {{ count: state.triagePinnedIds.length }});
        }} else if (triageSearch) {{
          descriptor.detail = phrase("{{filter}} | {{query}}", "{{filter}} | {{query}}", {{
            filter: localizeWord(state.triageFilter || "open"),
            query: clampLabel(triageSearch, 18),
          }});
        }} else {{
          descriptor.detail = triageFocus
            ? clampLabel(triageFocus.title || triageFocus.id, 28)
            : localizeWord(state.triageFilter || "open");
        }}
        pushRow(copy("Queue", "队列"), localizeWord(state.triageFilter || "open"));
        pushRow(copy("Search", "搜索"), clampLabel(triageSearch, 52), {{ mono: true }});
        pushRow(copy("Selected", "当前条目"), triageFocus ? clampLabel(triageFocus.title || triageFocus.id, 52) : "");
        pushRow(copy("Evidence focus", "证据聚焦"), state.triagePinnedIds.length ? phrase("{{count}} linked items", "{{count}} 个关联条目", {{ count: state.triagePinnedIds.length }}) : "");
        pushRow(copy("Batch", "批量"), state.selectedTriageIds.length ? phrase("{{count}} selected", "{{count}} 个已选", {{ count: state.selectedTriageIds.length }}) : "");
      }} else if (activeSectionId === "section-story") {{
        const activeStoryView = detectStoryViewPreset({{
          filter: state.storyFilter,
          sort: state.storySort,
          search: state.storySearch,
        }});
        const selectedStory = getStoryRecord(state.selectedStoryId);
        const storySearch = String(state.storySearch || "").trim();
        descriptor.detail = storySearch
          ? phrase("{{view}} | {{query}}", "{{view}} | {{query}}", {{
            view: storyViewPresetLabel(activeStoryView),
            query: clampLabel(storySearch, 18),
          }})
          : (selectedStory
              ? phrase("{{view}} | {{title}}", "{{view}} | {{title}}", {{
                  view: storyViewPresetLabel(activeStoryView),
                  title: clampLabel(selectedStory.title || selectedStory.id, 18),
                }})
              : storyViewPresetLabel(activeStoryView));
        pushRow(copy("View", "视图"), storyViewPresetLabel(activeStoryView));
        pushRow(
          copy("Workspace Mode", "工作区模式"),
          state.storyWorkspaceMode === "editor" ? copy("Editor", "编辑") : copy("Board", "看板"),
        );
        pushRow(copy("Sort", "排序"), storySortLabel(state.storySort));
        pushRow(copy("Search", "搜索"), clampLabel(storySearch, 52), {{ mono: true }});
        pushRow(copy("Selected", "当前故事"), selectedStory ? clampLabel(selectedStory.title || selectedStory.id, 52) : "");
        pushRow(copy("Batch", "批量"), state.selectedStoryIds.length ? phrase("{{count}} selected", "{{count}} 个已选", {{ count: state.selectedStoryIds.length }}) : "");
      }} else if (activeSectionId === "section-claims") {{
        const selectedReport = getSelectedReportRecord();
        const selectedSection = getSelectedReportSectionRecord();
        const selectedClaim = getSelectedClaimCard();
        const selectedQuality = getReportComposition(selectedReport?.id || "")?.quality || null;
        descriptor.detail = selectedClaim
          ? clampLabel(getClaimCardLabel(selectedClaim), 28)
          : (selectedReport
              ? phrase("report={{title}}", "报告={{title}}", {{ title: clampLabel(selectedReport.title || selectedReport.id, 18) }})
              : copy("claim composition", "主张装配"));
        pushRow(copy("Report", "报告"), selectedReport ? clampLabel(selectedReport.title || selectedReport.id, 52) : "");
        pushRow(copy("Section", "章节"), selectedSection ? clampLabel(selectedSection.title || selectedSection.id, 52) : "");
        pushRow(copy("Claim", "主张"), selectedClaim ? clampLabel(getClaimCardLabel(selectedClaim), 72) : "");
        pushRow(copy("Quality", "质量"), selectedQuality ? `${{localizeWord(selectedQuality.status || "draft")}} / ${{Number(selectedQuality.score || 0).toFixed(2)}}` : "");
      }} else if (activeSectionId === "section-report-studio") {{
        const selectedReport = getSelectedReportRecord();
        const selectedComposition = getReportComposition(selectedReport?.id || "");
        const selectedQuality = selectedComposition?.quality || null;
        const reportSections = getReportSectionsForReport(selectedReport?.id || "");
        const reportClaimIds = getReportClaimIds(selectedReport?.id || "");
        descriptor.detail = selectedReport
          ? clampLabel(selectedReport.title || selectedReport.id, 28)
          : copy("report studio", "报告工作台");
        pushRow(copy("Report", "报告"), selectedReport ? clampLabel(selectedReport.title || selectedReport.id, 52) : "");
        pushRow(copy("Audience", "受众"), selectedReport ? clampLabel(selectedReport.audience || "", 52) : "");
        pushRow(copy("Sections", "章节"), selectedReport ? String(reportSections.length) : "", {{ mono: true }});
        pushRow(copy("Claims", "主张"), selectedReport ? String(reportClaimIds.length) : "", {{ mono: true }});
        pushRow(copy("Quality", "质量"), selectedQuality ? `${{localizeWord(selectedQuality.status || "draft")}} / ${{Number(selectedQuality.score || 0).toFixed(2)}}` : "");
      }} else if (activeSectionId === "section-ops") {{
        const daemonState = String(state.status?.state || "").trim();
        const routeSummary = state.ops?.route_summary || {{}};
        descriptor.detail = copy("health and delivery", "健康与交付");
        pushRow(copy("Daemon", "守护进程"), daemonState ? localizeWord(daemonState) : "");
        pushRow(copy("Routes", "路由"), String(state.routes.length || 0), {{ mono: true }});
        pushRow(copy("Healthy", "健康"), String(routeSummary.healthy || 0), {{ mono: true }});
        pushRow(copy("Alerts", "告警"), String(state.alerts.length || 0), {{ mono: true }});
      }}

      descriptor.summary = descriptor.detail
        ? `${{descriptor.modeLabel}} / ${{descriptor.sectionLabel}} | ${{descriptor.detail}}`
        : `${{descriptor.modeLabel}} / ${{descriptor.sectionLabel}}`;
      return descriptor;
    }}

    function buildCurrentContextLinkRecord(descriptor = buildTopbarContextDescriptor()) {{
      const url = new URL(window.location.href);
      url.hash = descriptor.sectionId ? `#${{descriptor.sectionId}}` : "";
      return normalizeContextLinkHistoryEntry({{
        url: `${{url.pathname}}${{url.search}}${{url.hash}}`,
        summary: descriptor.summary,
        sectionId: descriptor.sectionId,
        timestamp: new Date().toISOString(),
      }});
    }}

    function renderContextViewDock() {{
      const root = $("context-view-dock");
      if (!root) {{
        return;
      }}
      const modeDescriptor = workspaceModeDescriptor(state.activeWorkspaceMode || workspaceModeForSection(state.activeSectionId));
      const stageSections = workspaceModeSectionMap[modeDescriptor.id] || [];
      const current = buildCurrentContextLinkRecord();
      const currentUrl = current ? current.url : "";
      const currentSavedIndex = current ? findContextSavedViewIndexByUrl(current.url) : -1;
      const currentSavedEntry = currentSavedIndex >= 0 ? normalizeContextSavedViewEntry(state.contextSavedViews[currentSavedIndex]) : null;
      const defaultEntry = getDefaultContextSavedView();
      const pinnedEntries = (Array.isArray(state.contextSavedViews) ? state.contextSavedViews : [])
        .map((entry) => normalizeContextSavedViewEntry(entry))
        .filter((entry) => entry && entry.pinned)
        .slice(0, 4);
      const pinnedCount = pinnedEntries.length;
      const remainingSlots = Math.max(0, 4 - pinnedCount);
      const onIntake = normalizeSectionId(state.activeSectionId) === "section-intake";
      const showSectionRail = stageSections.length > 1;
      const shouldShowDock = Boolean(
        pinnedEntries.length ||
        showSectionRail ||
        !onIntake ||
        currentSavedEntry ||
        defaultEntry
      );
      const showUnsavedHint = Boolean(
        current &&
        !currentSavedEntry &&
        !onIntake
      );
      const showSavedOnlyHint = Boolean(currentSavedEntry && !currentSavedEntry.pinned);
      const canSaveCurrent = Boolean(!onIntake && current && !currentSavedEntry);
      const canPinCurrent = Boolean(currentSavedIndex >= 0 && currentSavedEntry && !currentSavedEntry.pinned);
      const summaryLabel = current?.summary || copy("No active context", "当前没有激活上下文");
      const summaryCopy = pinnedEntries.length
        ? copy(
            "Use the lifecycle rail for primary movement. Pinned views stay here as accelerators, while deep links and palette actions remain optional speed paths.",
            "主导航仍由生命周期主轨负责；这里保留固定视图作为加速入口，而深链和命令面板继续只是可选捷径。"
          )
        : copy(
            "Use the lifecycle rail for primary movement. Open Workspace Context only when you need section detail, saved views, or shareable links.",
            "主导航由生命周期主轨负责；只有在需要区块细节、保存视图或分享链接时，再展开“工作上下文”。"
          );
      root.hidden = !shouldShowDock;
      if (!shouldShowDock) {{
        root.innerHTML = "";
        return;
      }}
      root.innerHTML = `
        <div class="context-view-dock-head">
          <div>
            <div class="context-view-dock-title">${{copy("Workspace Context", "工作上下文")}}</div>
            <div class="context-view-dock-summary" data-fit-text="dock-summary" data-fit-fallback="40">${{escapeHtml(summaryLabel)}}</div>
          </div>
          <div class="meta">
            <span class="chip ok">${{escapeHtml(modeDescriptor.label)}}</span>
            <span class="chip">${{remainingSlots ? phrase("{{count}} open", "{{count}} 个空位", {{ count: remainingSlots }}) : copy("Rail full", "轨道已满")}}</span>
            ${{showUnsavedHint ? `<span class="chip hot">${{copy("Unsaved", "未保存")}}</span>` : ""}}
            ${{showSavedOnlyHint ? `<span class="chip">${{copy("Saved only", "仅已保存")}}</span>` : ""}}
            ${{defaultEntry ? `<span class="chip ok" data-fit-text="dock-default-chip" data-fit-max-width="190" data-fit-fallback="24">${{copy("Default", "默认")}}: ${{escapeHtml(defaultEntry.name)}}</span>` : ""}}
            <button class="btn-secondary" type="button" data-context-dock-manage>${{copy("Open Context", "打开上下文")}}</button>
          </div>
        </div>
        ${{showSectionRail
          ? `<div class="context-view-dock-section">
              <div class="context-view-dock-title">${{copy("Current Rail", "当前主轨")}}</div>
              <div class="context-view-dock-list">
                ${{stageSections.map((sectionId) => `
                  <button
                    class="chip-btn ${{sectionId === normalizeSectionId(state.activeSectionId) ? "active" : ""}}"
                    type="button"
                    data-context-section="${{sectionId}}"
                  >
                    ${{escapeHtml(activeSectionLabel(sectionId))}}
                  </button>
                `).join("")}}
              </div>
            </div>`
          : ""}}
        ${{pinnedEntries.length
          ? `<div class="context-view-dock-section">
              <div class="context-view-dock-title">${{copy("Pinned Views", "已固定视图")}}</div>
              <div class="context-view-dock-list">
              ${{pinnedEntries.map((entry, index) => `
                <button
                  class="chip-btn ${{entry.url === currentUrl ? "active" : ""}}"
                  type="button"
                  data-context-dock-open="${{index}}"
                  data-fit-text="saved-view-chip"
                  data-fit-max-width="184"
                  data-fit-fallback="22"
                  title="${{escapeHtml(entry.isDefault ? phrase("Default | {{summary}}", "默认 | {{summary}}", {{ summary: entry.summary }}) : entry.summary)}}"
                >
                  ${{escapeHtml(entry.isDefault ? phrase("{{name}} [default]", "{{name}} [默认]", {{ name: entry.name }}) : entry.name)}}
                </button>
              `).join("")}}
              </div>
            </div>`
          : ""}}
        <div class="context-view-dock-tools">
          <div class="context-view-dock-copy">${{escapeHtml(summaryCopy)}}</div>
          <div class="context-view-dock-actions">
            ${{currentSavedEntry?.pinned ? `<span class="chip ok">${{copy("Current pinned", "当前已固定")}}</span>` : ""}}
            ${{canPinCurrent ? `<button class="btn-secondary" type="button" data-context-dock-pin-current>${{copy("Pin Current View", "固定当前视图")}}</button>` : ""}}
            ${{canSaveCurrent ? `<button class="btn-secondary" type="button" data-context-dock-save-pin>${{copy("Save + Pin Current", "保存并固定当前视图")}}</button>` : ""}}
          </div>
        </div>
      `;
      root.querySelector("[data-context-dock-manage]")?.addEventListener("click", () => {{
        state.contextLensRestoreFocusId = "context-summary";
        setContextLensOpen(true);
      }});
      root.querySelectorAll("[data-context-section]").forEach((button) => {{
        button.addEventListener("click", () => {{
          const sectionId = String(button.dataset.contextSection || "").trim();
          if (sectionId) {{
            jumpToSection(sectionId);
          }}
        }});
      }});
      root.querySelectorAll("[data-context-dock-open]").forEach((button) => {{
        button.addEventListener("click", () => {{
          const pinnedIndex = Number(button.dataset.contextDockOpen || -1);
          const entry = pinnedEntries[pinnedIndex];
          if (entry) {{
            restoreContextSavedViewByName(entry.name);
          }}
        }});
      }});
      root.querySelector("[data-context-dock-pin-current]")?.addEventListener("click", () => {{
        if (currentSavedIndex >= 0) {{
          toggleContextSavedViewPinned(currentSavedIndex);
        }}
      }});
      root.querySelector("[data-context-dock-save-pin]")?.addEventListener("click", () => {{
        saveAndPinCurrentContextView();
      }});
      scheduleCanvasTextFit(root);
    }}

    function renderContextSavedViews() {{
      const root = $("context-lens-saved");
      if (!root) {{
        return;
      }}
      const entries = (Array.isArray(state.contextSavedViews) ? state.contextSavedViews : [])
        .map((entry) => normalizeContextSavedViewEntry(entry))
        .filter(Boolean)
        .slice(0, 8);
      const pinnedIndexes = entries
        .map((entry, index) => (entry.pinned ? index : -1))
        .filter((index) => index >= 0);
      root.innerHTML = `
        <div class="context-lens-history-head">
          <div class="context-lens-history-title">${{copy("Saved Views", "已保存视图")}}</div>
          ${{entries.length ? `<button class="btn-secondary" type="button" data-context-saved-clear>${{copy("Clear", "清空")}}</button>` : ""}}
        </div>
        ${{entries.length
          ? `<div class="context-lens-history-list">
              ${{entries.map((entry, index) => {{
                const pinnedPosition = pinnedIndexes.indexOf(index);
                const canMoveLeft = pinnedPosition > 0;
                const canMoveRight = pinnedPosition >= 0 && pinnedPosition < pinnedIndexes.length - 1;
                return `
                <div class="context-history-item">
                  <div class="context-history-summary">${{escapeHtml(entry.name)}}</div>
                  <div class="context-history-meta">
                    <span>${{escapeHtml(activeSectionLabel(entry.sectionId))}}</span>
                    <span>${{escapeHtml(formatCompactDateTime(entry.timestamp))}}</span>
                    ${{entry.isDefault ? `<span class="chip ok">${{copy("Default", "默认")}}</span>` : ""}}
                    ${{entry.pinned ? `<span class="chip">${{copy("Pinned", "已固定")}}</span>` : ""}}
                  </div>
                  <div class="panel-sub">${{escapeHtml(entry.summary)}}</div>
                  <div class="context-history-url">${{escapeHtml(clampLabel(entry.url, 96))}}</div>
                  <div class="context-history-actions">
                    <button class="btn-secondary" type="button" data-context-saved-open="${{index}}">${{copy("Open", "打开")}}</button>
                    <button class="btn-secondary" type="button" data-context-saved-copy="${{index}}">${{copy("Copy", "复制")}}</button>
                    <button class="btn-secondary" type="button" data-context-saved-pin="${{index}}">${{entry.pinned ? copy("Unpin", "取消固定") : copy("Pin", "固定")}}</button>
                    ${{entry.pinned ? `<button class="btn-secondary" type="button" data-context-saved-move-left="${{index}}" ${{canMoveLeft ? "" : "disabled"}}>${{copy("Move Left", "左移")}}</button>` : ""}}
                    ${{entry.pinned ? `<button class="btn-secondary" type="button" data-context-saved-move-right="${{index}}" ${{canMoveRight ? "" : "disabled"}}>${{copy("Move Right", "右移")}}</button>` : ""}}
                    <button class="btn-secondary" type="button" data-context-saved-default="${{index}}">${{entry.isDefault ? copy("Clear Default", "取消默认") : copy("Set Default", "设为默认")}}</button>
                    <button class="btn-secondary" type="button" data-context-saved-delete="${{index}}">${{copy("Delete", "删除")}}</button>
                  </div>
                </div>
              `;
              }}).join("")}}
            </div>`
          : `<div class="empty">${{copy("No saved view yet. Name one above and it will stay here.", "还没有保存视图。给上面的当前视图起个名字，它就会保留在这里。")}}</div>`}}
      `;
      root.querySelector("[data-context-saved-clear]")?.addEventListener("click", () => {{
        clearContextSavedViews();
      }});
      root.querySelectorAll("[data-context-saved-open]").forEach((button) => {{
        button.addEventListener("click", () => {{
          restoreContextSavedViewEntry(Number(button.dataset.contextSavedOpen || -1));
        }});
      }});
      root.querySelectorAll("[data-context-saved-copy]").forEach((button) => {{
        button.addEventListener("click", async () => {{
          await copyContextSavedViewEntry(Number(button.dataset.contextSavedCopy || -1));
        }});
      }});
      root.querySelectorAll("[data-context-saved-pin]").forEach((button) => {{
        button.addEventListener("click", () => {{
          toggleContextSavedViewPinned(Number(button.dataset.contextSavedPin || -1));
        }});
      }});
      root.querySelectorAll("[data-context-saved-move-left]").forEach((button) => {{
        button.addEventListener("click", () => {{
          moveContextSavedViewInDock(Number(button.dataset.contextSavedMoveLeft || -1), "left");
        }});
      }});
      root.querySelectorAll("[data-context-saved-move-right]").forEach((button) => {{
        button.addEventListener("click", () => {{
          moveContextSavedViewInDock(Number(button.dataset.contextSavedMoveRight || -1), "right");
        }});
      }});
      root.querySelectorAll("[data-context-saved-default]").forEach((button) => {{
        button.addEventListener("click", () => {{
          setDefaultContextSavedView(Number(button.dataset.contextSavedDefault || -1));
        }});
      }});
      root.querySelectorAll("[data-context-saved-delete]").forEach((button) => {{
        button.addEventListener("click", () => {{
          deleteContextSavedView(Number(button.dataset.contextSavedDelete || -1));
        }});
      }});
    }}

    function renderContextLinkHistory() {{
      const root = $("context-lens-history");
      if (!root) {{
        return;
      }}
      const entries = (Array.isArray(state.contextLinkHistory) ? state.contextLinkHistory : [])
        .map((entry) => normalizeContextLinkHistoryEntry(entry))
        .filter(Boolean)
        .slice(0, 6);
      root.innerHTML = `
        <div class="context-lens-history-head">
          <div class="context-lens-history-title">${{copy("Recently Shared", "最近分享")}}</div>
          ${{entries.length ? `<button class="btn-secondary" type="button" data-context-history-clear>${{copy("Clear", "清空")}}</button>` : ""}}
        </div>
        ${{entries.length
          ? `<div class="context-lens-history-list">
              ${{entries.map((entry, index) => `
                <div class="context-history-item">
                  <div class="context-history-summary">${{escapeHtml(entry.summary)}}</div>
                  <div class="context-history-meta">
                    <span>${{escapeHtml(activeSectionLabel(entry.sectionId))}}</span>
                    <span>${{escapeHtml(formatCompactDateTime(entry.timestamp))}}</span>
                  </div>
                  <div class="context-history-url">${{escapeHtml(clampLabel(entry.url, 96))}}</div>
                  <div class="context-history-actions">
                    <button class="btn-secondary" type="button" data-context-history-open="${{index}}">${{copy("Open", "打开")}}</button>
                    <button class="btn-secondary" type="button" data-context-history-copy="${{index}}">${{copy("Copy", "复制")}}</button>
                  </div>
                </div>
              `).join("")}}
            </div>`
          : `<div class="empty">${{copy("No shared context yet. Copy a deep link and it will appear here.", "还没有分享上下文。复制一次深链后，这里就会出现。")}}</div>`}}
      `;
      root.querySelector("[data-context-history-clear]")?.addEventListener("click", () => {{
        clearContextLinkHistory();
      }});
      root.querySelectorAll("[data-context-history-open]").forEach((button) => {{
        button.addEventListener("click", () => {{
          restoreContextLinkHistoryEntry(Number(button.dataset.contextHistoryOpen || -1));
        }});
      }});
      root.querySelectorAll("[data-context-history-copy]").forEach((button) => {{
        button.addEventListener("click", async () => {{
          await copyContextLinkHistoryEntry(Number(button.dataset.contextHistoryCopy || -1));
        }});
      }});
    }}

    function renderContextLens(descriptor = buildTopbarContextDescriptor()) {{
      const body = $("context-lens-body");
      if (!body) {{
        return;
      }}
      body.innerHTML = descriptor.rows.length
        ? descriptor.rows.map((row) => `
            <div class="context-lens-row">
              <div class="context-lens-label">${{escapeHtml(row.label)}}</div>
              <div class="context-lens-value ${{escapeHtml(row.className || "")}}">${{escapeHtml(row.value)}}</div>
            </div>
          `).join("")
        : `<div class="empty">${{copy("No active workspace context.", "当前没有工作上下文。")}}</div>`;
      renderContextSavedViews();
      renderContextLinkHistory();
    }}

    function getContextLensFocusableElements() {{
      const shell = $("context-lens-shell");
      if (!shell) {{
        return [];
      }}
      return Array.from(shell.querySelectorAll('button:not([disabled]), [href], input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])'))
        .filter((element) => !element.hasAttribute("hidden") && element.getAttribute("aria-hidden") !== "true");
    }}

    function setContextLensOpen(nextOpen) {{
      state.contextLensOpen = Boolean(nextOpen);
      const summary = $("context-summary");
      const lens = $("context-lens");
      const backdrop = $("context-lens-backdrop");
      const shell = $("context-lens-shell");
      if (summary) {{
        summary.setAttribute("aria-expanded", state.contextLensOpen ? "true" : "false");
      }}
      if (document.body) {{
        document.body.dataset.contextLensOpen = state.contextLensOpen ? "true" : "false";
      }}
      if (backdrop) {{
        backdrop.hidden = !state.contextLensOpen;
        backdrop.classList.toggle("open", state.contextLensOpen);
      }}
      if (lens) {{
        lens.hidden = !state.contextLensOpen;
      }}
      if (state.contextLensOpen) {{
        renderContextLens();
        window.setTimeout(() => {{
          shell?.focus();
        }}, 10);
        return;
      }}
      window.setTimeout(() => {{
        $(state.contextLensRestoreFocusId || "context-summary")?.focus();
      }}, 0);
    }}

    function toggleContextLens() {{
      setContextLensOpen(!state.contextLensOpen);
    }}

    function applyWorkspaceUrlStateFromLocation({{ jump = true }} = {{}}) {{
      state.watchSearch = "";
      state.selectedWatchId = state.watches[0] ? state.watches[0].id : "";
      state.watchResultFilters = {{}};
      state.watchUrlFocusPending = false;

      state.triageFilter = "open";
      state.triageSearch = "";
      state.triagePinnedIds = [];
      state.selectedTriageIds = [];
      state.selectedTriageId = "";
      state.triageUrlFocusPending = false;

      state.storySearch = "";
      state.storyWorkspaceMode = "board";
      state.storyFilter = "all";
      state.storySort = "attention";
      state.selectedStoryIds = [];
      state.selectedStoryId = state.stories[0] ? state.stories[0].id : "";
      state.storyUrlFocusPending = false;

      applyWatchUrlStateFromLocation();
      applyTriageUrlStateFromLocation();
      applyStoryUrlStateFromLocation();
      state.storyWorkspaceMode = normalizeStoryWorkspaceMode(state.storyWorkspaceMode);
      applyStoryWorkspaceMode(state.storyWorkspaceMode, {{ persist: false }});
      setContextRouteFromWatch();
      persistStoryWorkspacePrefs();
      state.activeSectionId = normalizeSectionId(window.location.hash || "section-intake");
      renderWatches();
      renderWatchDetail();
      renderTriage();
      renderStories();
      renderClaimsWorkspace();
      renderReportStudio();
      renderWorkspaceModeChrome();
      renderTopbarContext();
      const hasFocusedSection = state.watchUrlFocusPending || state.triageUrlFocusPending || state.storyUrlFocusPending;
      if (state.watchUrlFocusPending) {{
        flushWatchUrlFocus();
      }}
      if (state.triageUrlFocusPending) {{
        flushTriageUrlFocus();
      }}
      if (state.storyUrlFocusPending) {{
        flushStoryUrlFocus();
      }}
      if (jump && !hasFocusedSection) {{
        window.setTimeout(() => {{
          jumpToSection(state.activeSectionId, {{ updateHash: false }});
        }}, 0);
      }}
    }}

    async function copyContextLinkRecord(entry, {{ toastMessage = "" }} = {{}}) {{
      const normalized = normalizeContextLinkHistoryEntry(entry);
      if (!normalized) {{
        return;
      }}
      const href = new URL(normalized.url, window.location.origin).href;
      try {{
        if (window.navigator.clipboard?.writeText) {{
          await window.navigator.clipboard.writeText(href);
        }} else {{
          const helper = document.createElement("textarea");
          helper.value = href;
          helper.setAttribute("readonly", "readonly");
          helper.style.position = "absolute";
          helper.style.left = "-9999px";
          document.body.appendChild(helper);
          helper.select();
          document.execCommand("copy");
          document.body.removeChild(helper);
        }}
        noteContextLinkHistory({{
          ...normalized,
          timestamp: new Date().toISOString(),
        }});
        renderTopbarContext();
        showToast(toastMessage || copy("Context link copied", "已复制当前上下文链接"), "success");
      }} catch (error) {{
        reportError(error, copy("Copy context link", "复制上下文链接"));
      }}
    }}

    async function copyCurrentContextLink() {{
      await copyContextLinkRecord(buildCurrentContextLinkRecord());
    }}

    async function copyContextSavedViewEntry(entryIndex) {{
      const entry = normalizeContextSavedViewEntry(state.contextSavedViews[Number(entryIndex)]);
      if (!entry) {{
        return;
      }}
      await copyContextLinkRecord(entry, {{
        toastMessage: copy("Saved view link copied", "已复制保存视图链接"),
      }});
    }}

    async function copyContextLinkHistoryEntry(entryIndex) {{
      const entry = state.contextLinkHistory[Number(entryIndex)];
      if (!entry) {{
        return;
      }}
      await copyContextLinkRecord(entry, {{
        toastMessage: copy("Shared context link copied", "已复制分享上下文链接"),
      }});
    }}

    function restoreContextLinkRecord(entry, toastMessage, {{ noteHistory = true, closeLens = true, showToastMessage = true }} = {{}}) {{
      const normalized = normalizeContextLinkHistoryEntry(entry);
      if (!normalized) {{
        return;
      }}
      const target = new URL(normalized.url, window.location.origin);
      if (target.pathname !== window.location.pathname) {{
        window.location.assign(target.href);
        return;
      }}
      window.history.replaceState(
        window.history.state,
        "",
        `${{target.pathname}}${{target.search}}${{target.hash}}`,
      );
      if (noteHistory) {{
        noteContextLinkHistory({{
          ...normalized,
          timestamp: new Date().toISOString(),
        }});
      }}
      if (closeLens) {{
        setContextLensOpen(false);
      }}
      applyWorkspaceUrlStateFromLocation({{ jump: true }});
      if (showToastMessage && toastMessage) {{
        showToast(toastMessage, "success");
      }}
    }}

    function restoreContextLinkHistoryEntry(entryIndex) {{
      const entry = state.contextLinkHistory[Number(entryIndex)];
      if (!entry) {{
        return;
      }}
      restoreContextLinkRecord(entry, copy("Shared context restored", "已恢复分享上下文"));
    }}

    function restoreContextSavedViewEntry(entryIndex) {{
      const entry = state.contextSavedViews[Number(entryIndex)];
      if (!entry) {{
        return;
      }}
      restoreContextLinkRecord(entry, copy("Saved view restored", "已恢复保存视图"));
    }}

    function restoreContextSavedViewByName(viewName) {{
      const normalizedName = String(viewName || "").trim().toLowerCase();
      if (!normalizedName) {{
        return;
      }}
      const index = (Array.isArray(state.contextSavedViews) ? state.contextSavedViews : [])
        .map((entry) => normalizeContextSavedViewEntry(entry))
        .findIndex((entry) => entry && entry.name.toLowerCase() === normalizedName);
      if (index >= 0) {{
        restoreContextSavedViewEntry(index);
      }}
    }}

    function applyDefaultSavedViewOnBoot() {{
      if (!state.contextDefaultBootPending) {{
        return;
      }}
      state.contextDefaultBootPending = false;
      const defaultEntry = getDefaultContextSavedView();
      if (!defaultEntry) {{
        return;
      }}
      restoreContextLinkRecord(defaultEntry, "", {{
        noteHistory: false,
        closeLens: false,
        showToastMessage: false,
      }});
    }}

    function hasIntakePopulation() {{
      return (
        (Array.isArray(state.watches) && state.watches.length > 0) ||
        (Array.isArray(state.triage) && state.triage.length > 0) ||
        (Array.isArray(state.stories) && state.stories.length > 0) ||
        (Array.isArray(state.alerts) && state.alerts.length > 0) ||
        (Array.isArray(state.routes) && state.routes.length > 0) ||
        Boolean(
          state.overview && [
            "enabled_watches",
            "due_watches",
            "triage_open_count",
            "story_ready_count",
            "alerting_mission_count",
            "story_count",
            "alert_count",
            "route_count"
          ].some((key) => Number(state.overview?.[key] || 0) > 0)
        )
      );
    }}

    function renderIntakeLiveDesk() {{
      const onboardingHero = $("intake-hero-onboarding");
      const liveHero = $("intake-hero-live");
      const onboardingSide = $("intake-side-onboarding");
      const liveSide = $("intake-side-live");
      if (!onboardingHero || !liveHero || !onboardingSide || !liveSide) {{
        return;
      }}

      const hasPopulation = hasIntakePopulation();
      onboardingHero.hidden = hasPopulation;
      onboardingSide.hidden = hasPopulation;
      liveHero.hidden = !hasPopulation;
      liveSide.hidden = !hasPopulation;

      if (!hasPopulation) {{
        return;
      }}

      const overview = state.overview || {{}};
      const selectedWatch = state.watches.find((watch) => watch.id === state.selectedWatchId) || null;
      const selectedName = String((selectedWatch && (selectedWatch.name || selectedWatch.id)) || "").trim() || copy("No mission selected", "未选择任务");
      const enabledCount = Number(overview.enabled_watches ?? 0);
      const dueCount = Number(overview.due_watches ?? 0);
      const openQueue = Number(overview.triage_open_count ?? 0);
      const readyStories = Number(overview.story_ready_count ?? 0);
      const alertingMissions = Number(overview.alerting_mission_count ?? 0);
      const heroActions = selectedWatch ? [
        {{ label: copy("Open Cockpit", "打开任务详情"), section: "section-cockpit" }},
        {{ label: copy("Open Triage", "打开分诊"), section: "section-triage" }},
        {{ label: copy("Run Mission", "立即执行任务"), runWatch: selectedWatch.id }},
      ] : [
        {{ label: copy("Create Mission", "新建任务"), focus: "mission", field: "name" }},
        {{ label: copy("Open Mission Board", "打开任务列表"), section: "section-board" }},
      ];
      const heroActionsHtml = heroActions.length
        ? heroActions.map((action) => `
            <button
              class="btn-primary"
              type="button"
              ${{action.runWatch ? `data-empty-run-watch="${{escapeHtml(action.runWatch)}}"` : ""}}
              ${{action.section ? `data-empty-jump="${{escapeHtml(action.section)}}"` : ""}}
              ${{action.focus ? `data-empty-focus="${{escapeHtml(action.focus)}}"` : ""}}
              ${{action.field ? `data-empty-field="${{escapeHtml(action.field)}}"` : ""}}
            >${{escapeHtml(action.label)}}</button>
          `).join("")
        : "";
      const sideActions = [
        {{ label: copy("Open Story Workspace", "打开故事工作台"), section: "section-story" }},
        {{ label: copy("Open Delivery", "打开交付"), section: "section-ops" }},
        {{ label: copy("Reset Draft", "清空草稿"), reset: "mission" }},
      ];
      const sideActionsHtml = sideActions.map((action) => `
        <button
          class="chip-btn"
          type="button"
          ${{action.section ? `data-empty-jump="${{escapeHtml(action.section)}}"` : ""}}
          ${{action.focus ? `data-empty-focus="${{escapeHtml(action.focus)}}"` : ""}}
          ${{action.field ? `data-empty-field="${{escapeHtml(action.field)}}"` : ""}}
          ${{action.reset ? `data-empty-reset="${{escapeHtml(action.reset)}}"` : ""}}
        >${{escapeHtml(action.label)}}</button>
      `).join("");

      liveHero.innerHTML = `
        <div class="card">
          <div class="card-top">
            <div>
              <div class="mono">${{copy("Live Intake Desk", "实时工作台")}}</div>
              <h3 class="panel-title" style="margin-top:8px;">${{escapeHtml(selectedName)}}</h3>
            </div>
            <span class="chip ${{selectedWatch ? "ok" : "hot"}}">${{selectedWatch ? copy("Mission Focus", "任务聚焦") : copy("Population Present", "已有数据")}}</span>
          </div>
          <div class="panel-sub">${{copy("Current object facts and pressure signal", "先显示当前对象事实与压力信号，再展示下一步动作。")}}</div>
          <div class="meta">
            <span class="chip ok">${{copy("Enabled missions", "活跃任务")}}=${{enabledCount}}</span>
            <span class="chip hot">${{copy("Due now", "当前待执行")}}=${{dueCount}}</span>
            <span class="chip">${{copy("Open queue", "待分诊")}}=${{openQueue}}</span>
            <span class="chip">${{copy("Ready stories", "待交付故事")}}=${{readyStories}}</span>
            <span class="chip">${{copy("Alerting missions", "告警中任务")}}=${{alertingMissions}}</span>
          </div>
          <div class="meta">${{copy("Next actions", "下一步动作")}}</div>
          <div class="actions">${{heroActionsHtml}}</div>
        </div>
      `;

      liveSide.innerHTML = `
        <div class="card">
          <div class="card-top">
            <div>
              <div class="mono">${{copy("Current Object", "当前对象")}}</div>
              <h3 class="panel-title" style="margin-top:8px;">${{copy("Mission and Route Handoff", "任务与交付交接")}}</h3>
            </div>
          </div>
          <div class="panel-sub">${{copy("Mission continuity keeps review and routing actions close to live evidence so the shell opens on actionability before guidance text.", "任务连续性优先显示审阅与交付动作，避免先看到引导文案。")}}</div>
          <div class="meta">
            <span class="chip">${{copy("Object", "对象")}}=${{escapeHtml(selectedName)}}</span>
            <span class="chip">${{copy("Status", "状态")}}=${{selectedWatch ? (selectedWatch.enabled ? copy("enabled", "已启用") : copy("paused", "已暂停")) : copy("idle", "空闲")}}</span>
            <span class="chip">${{copy("Pressure", "压力")}}=${{openQueue + dueCount}}</span>
          </div>
          <div class="actions">${{sideActionsHtml}}</div>
        </div>
      `;

      wireLifecycleGuideActions(liveHero);
      wireLifecycleGuideActions(liveSide);
    }}

    function renderTopbarContext() {{
      const descriptor = buildTopbarContextDescriptor();
      setText("context-summary", descriptor.summary);
      $("context-summary")?.setAttribute("title", descriptor.summary);
      setPlaceholder("context-save-name", descriptor.summary);
      renderContextObjectRail();
      renderContextLens(descriptor);
      renderContextViewDock();
      renderIntakeLiveDesk();
      scheduleCanvasTextFit($("context-shell"));
      scheduleCanvasTextFit($("context-view-dock"));
    }}

    function normalizeContextObjectId(value) {{
      return String(value || "").trim();
    }}

    function setContextRouteName(value, section = "") {{
      state.contextRouteName = normalizeContextObjectId(normalizeRouteName(value));
      state.contextRouteSection = String(section || "").trim();
    }}

    function getRouteRecordByName(routeName) {{
      const normalized = normalizeRouteName(routeName);
      if (!normalized) {{
        return null;
      }}
      return state.routes.find((route) => normalizeRouteName(route?.name) === normalized) || null;
    }}

    function getSelectedWatchForContext() {{
      const selectedWatchId = normalizeContextObjectId(state.selectedWatchId);
      if (!selectedWatchId) {{
        return null;
      }}
      return (
        state.watchDetails[selectedWatchId]
        || state.watches.find((watch) => watch.id === selectedWatchId)
        || null
      );
    }}

    function collectWatchRouteCandidates(watch) {{
      const watchRecord = watch || {{}};
      const rules = Array.isArray(watchRecord.alert_rules) ? watchRecord.alert_rules : [];
      const out = [];
      rules.forEach((rule) => {{
        const routeNames = normalizeRouteRuleNames(rule);
        routeNames.forEach((routeName) => {{
          if (routeName && !out.includes(routeName)) {{
            out.push(routeName);
          }}
        }});
      }});
      return out;
    }}

    function setContextRouteFromWatch() {{
      const selectedWatch = getSelectedWatchForContext();
      const draftRouteName = normalizeRouteName(state.createWatchDraft?.route);
      const routeCandidates = collectWatchRouteCandidates(selectedWatch);
      const contextRouteName = normalizeContextObjectId(state.contextRouteName);
      const activeSectionId = normalizeSectionId(state.activeSectionId);
      const activeRouteRecord = getRouteRecordByName(contextRouteName);

      if (draftRouteName) {{
        setContextRouteName(draftRouteName, "section-ops");
        return;
      }}

      if (contextRouteName && activeSectionId === "section-ops" && activeRouteRecord) {{
        setContextRouteName(contextRouteName, "section-ops");
        return;
      }}

      if (contextRouteName && routeCandidates.includes(contextRouteName)) {{
        setContextRouteName(contextRouteName, state.contextRouteSection || "section-board");
        return;
      }}

      if (routeCandidates.length) {{
        setContextRouteName(routeCandidates[0], "section-board");
        return;
      }}
      setContextRouteName("", "");
    }}

    function buildContextObjectRailDescriptor() {{
      const mission = getSelectedWatchForContext();
      const missionId = normalizeContextObjectId(mission?.id);
      const missionLabel = mission ? clampLabel(String(mission.name || mission.id || ""), 22) : contextLensEmptyValue();
      const missionRecentEvidence = Array.isArray(mission?.recent_results) && mission.recent_results.length
        ? mission.recent_results[0]
        : null;

      const selectedTriage = state.triage.find((item) => item.id === state.selectedTriageId) || null;
      const evidenceId = selectedTriage
        ? normalizeContextObjectId(selectedTriage.id)
        : normalizeContextObjectId(missionRecentEvidence?.id);
      const evidenceLabel = selectedTriage
        ? clampLabel(String(selectedTriage.title || selectedTriage.url || selectedTriage.id || ""), 24)
        : (missionRecentEvidence
          ? clampLabel(String(missionRecentEvidence.title || missionRecentEvidence.url || missionRecentEvidence.id || ""), 24)
          : contextLensEmptyValue());

      const selectedStory = getStoryRecord(state.selectedStoryId);
      const storyId = normalizeContextObjectId(selectedStory?.id);
      const storyLabel = selectedStory
        ? clampLabel(String(selectedStory.title || selectedStory.id || ""), 24)
        : contextLensEmptyValue();

      const selectedReport = getSelectedReportRecord();
      const reportId = normalizeContextObjectId(selectedReport?.id);
      const reportLabel = selectedReport
        ? clampLabel(String(selectedReport.title || selectedReport.id || ""), 24)
        : contextLensEmptyValue();

      const draftRouteName = normalizeRouteName(state.createWatchDraft?.route);
      const routeName = normalizeRouteName(state.contextRouteName) || draftRouteName || collectWatchRouteCandidates(mission)[0] || "";
      const routeRecord = getRouteRecordByName(routeName);

      return {{
        steps: [
          {{
            step: "mission",
            sectionId: "section-board",
            id: missionId,
            title: copy("Mission", "任务"),
            label: missionLabel,
          }},
          {{
            step: "evidence",
            sectionId: "section-triage",
            id: evidenceId,
            title: copy("Evidence", "证据"),
            label: evidenceLabel,
          }},
          {{
            step: "story",
            sectionId: "section-story",
            id: storyId,
            title: copy("Story", "故事"),
            label: storyLabel,
          }},
          {{
            step: "report",
            sectionId: "section-report-studio",
            id: reportId,
            title: copy("Report", "报告"),
            label: reportLabel,
          }},
          {{
            step: "route",
            sectionId: "section-ops",
            id: routeName,
            title: copy("Route", "路由"),
            label: routeRecord?.name || routeName || contextLensEmptyValue(),
          }},
        ],
      }};
    }}

    function renderContextObjectRail(descriptor = buildContextObjectRailDescriptor()) {{
      const root = $("context-object-rail");
      if (!root) {{
        return;
      }}
      const steps = Array.isArray(descriptor?.steps) ? descriptor.steps : [];
      root.innerHTML = steps
        .map((step) => `
          <button
            class="context-object-step"
            type="button"
            data-context-object-step="${{step.step}}"
            data-context-object-id="${{escapeHtml(step.id || "")}}"
            data-context-object-section="${{step.sectionId}}"
            title="${{escapeHtml(`${{step.title}}: ${{step.label || contextLensEmptyValue()}}`)}}"
          >
            <span class="context-object-step-title">${{escapeHtml(step.title)}}</span>
            <span class="context-object-step-value" data-fit-text="context-object-value" data-fit-fallback="18">${{escapeHtml(step.label || contextLensEmptyValue())}}</span>
          </button>`)
        .join('<span class="context-object-divider">→</span>');
      scheduleCanvasTextFit(root);
    }}

    async function activateContextObjectRailStep(stepName, objectId, sectionId) {{
      const normalizedStep = String(stepName || "").trim().toLowerCase();
      const normalizedObjectId = normalizeContextObjectId(objectId);
      const normalizedSectionId = normalizeSectionId(sectionId);

      if (normalizedStep === "mission" && normalizedObjectId) {{
        try {{
          await loadWatch(normalizedObjectId);
        }} catch (error) {{
          reportError(error, copy("Open mission", "打开任务"));
        }}
      }} else if (normalizedStep === "evidence" && normalizedObjectId) {{
        const triageItem = state.triage.find((item) => item.id === normalizedObjectId) || null;
        if (triageItem) {{
          focusTriageEvidence([normalizedObjectId], {{ itemId: normalizedObjectId, jump: false, showToastMessage: false }});
        }}
      }} else if (normalizedStep === "story" && normalizedObjectId) {{
        try {{
          await loadStory(normalizedObjectId);
        }} catch (error) {{
          reportError(error, copy("Open story", "打开故事"));
        }}
      }} else if (normalizedStep === "report" && normalizedObjectId) {{
        try {{
          await selectReport(normalizedObjectId);
        }} catch (error) {{
          reportError(error, copy("Open report", "打开报告"));
        }}
      }} else if (normalizedStep === "route" && normalizedObjectId) {{
        try {{
          await editRouteInDeck(normalizedObjectId);
          return;
        }} catch (error) {{
          reportError(error, copy("Open route", "打开路由"));
        }}
      }}

      if (normalizedSectionId) {{
        jumpToSection(normalizedSectionId);
      }}
    }}

    function bindContextObjectRail() {{
      const root = $("context-object-rail");
      if (!root) {{
        return;
      }}
      root.addEventListener("click", async (event) => {{
        const step = event.target.closest("[data-context-object-step]");
        if (!step) {{
          return;
        }}
        await activateContextObjectRailStep(
          String(step.dataset.contextObjectStep || ""),
          String(step.dataset.contextObjectId || ""),
          String(step.dataset.contextObjectSection || ""),
        );
      }});
    }}

    function applyLanguageChrome() {{
      document.documentElement.lang = state.language === "zh" ? "zh-CN" : "en";
      document.body.dataset.lang = state.language;
      document.title = state.language === "zh" ? "DataPulse 情报控制台" : initial.title;
      setText("topbar-title", copy("DataPulse Operations Console", "DataPulse 情报控制台"));
      setText("nav-intake", copy("Intake", "录入"));
      setText("nav-missions", copy("Missions", "任务"));
      setText("nav-review", copy("Review", "审阅"));
      setText("nav-delivery", copy("Delivery", "交付"));
      setText("context-lens-title", copy("Workspace Context", "工作上下文"));
      setText("context-lens-copy", copy("See the current rail, active filters, and save or share the current workspace state.", "查看当前主轨、正在生效的筛选条件，并保存或分享当前工作区状态。"));
      setText("context-lens-close", copy("Close", "关闭"));
      setText("context-save-title", copy("Save Current View", "保存当前视图"));
      setText("context-save-submit", copy("Save View", "保存视图"));
      setPlaceholder("context-save-name", copy("Ops desk / Escalations", "运营台 / 升级队列"));
      setText("context-open-section", copy("Open Current Surface", "打开当前区块"));
      setText("context-copy-link", copy("Copy Link", "复制链接"));
      setText("palette-open", copy("Command Palette", "快速命令"));
      setText("context-reset", copy("Reset Context", "重置上下文"));
      setText("hero-eyebrow", copy("Guided Analyst Workflow", "引导式工作流"));
      setHTML("hero-title", state.language === "zh" ? "运行任务<br>审阅信号<br>沉淀故事" : "Run Missions, Review Signal, Publish Stories");
      setText("hero-copy", copy(
        "Start with one mission draft, run it from the board, triage the inbox, promote verified evidence into a story, then wire a route when delivery should turn on.",
        "先创建一个任务草稿，再从列表执行、进入分诊、把已核验信号提升为故事，最后在需要交付时接上路由。"
      ));
      setText("refresh-all", copy("Refresh Console", "刷新控制台"));
      setText("run-due", copy("Run Due Missions", "运行待执行任务"));
      setText("jump-watch-board", copy("Open Mission Board", "查看任务列表"));
      setText("guide-step-1-title", copy("Draft Mission", "创建任务"));
      setText("guide-step-1-copy", copy("Use a preset, clone an existing watch, or enter just Name + Query to create the first watch.", "可以使用预设、复制已有任务，或者只填名称和查询词先把第一个任务建起来。"));
      setText("guide-step-2-title", copy("Run And Inspect", "执行并查看"));
      setText("guide-step-2-copy", copy("Mission Board and Cockpit run the watch, show results, and expose alert rules before review work starts.", "任务列表和任务详情负责执行任务、查看结果，并在进入审阅前暴露告警规则。"));
      setText("guide-step-3-title", copy("Triage And Promote", "分诊并提升"));
      setText("guide-step-3-copy", copy("Triage reviews inbox items, captures analyst notes, and promotes verified evidence into story drafts.", "分诊队列负责审阅收件箱条目、记录分析师备注，并把已核验的证据提升为故事草稿。"));
      setText("guide-step-4-title", copy("Set Route And Watch Delivery", "配置路由并观察交付"));
      setText("guide-step-4-copy", copy("Route Manager creates reusable sinks; mission alert rules attach them when stories are ready to notify downstream.", "路由管理先创建可复用的交付目标；当故事准备好触发下游通知时，再从任务告警规则里把它接上。"));
      setText("guide-kicker", copy("Operator Guidance", "操作提示"));
      setText("guide-panel-title", copy("Browser Lifecycle", "浏览器生命周期"));
      setText("guide-chip", copy("Mission -> Triage -> Story -> Claim -> Report -> Route", "任务 -> 分诊 -> 故事 -> 主张 -> 报告 -> 路由"));
      setText("guide-panel-copy", copy("Create or clone a mission here. The board runs it, triage reviews incoming evidence, stories promote verified signal, Claim Composer binds judgments, Report Studio checks guardrails, and routes turn delivery on.", "先在这里创建或复制任务；任务列表负责执行，分诊队列负责审阅证据，故事工作台负责沉淀信号，主张装配负责绑定判断，报告工作台负责检查门禁，路由则在需要时开启交付。"));
      setText("shortcut-focus", copy("/ focus draft", "/ 聚焦任务草稿"));
      setText("shortcut-preset", copy("1-4 load preset", "1-4 套用预设"));
      setText("shortcut-submit", copy("Cmd/Ctrl+Enter deploy", "Cmd/Ctrl+Enter 提交"));
      setText("jump-cockpit", copy("Cockpit", "任务详情"));
      setText("jump-triage", copy("Triage", "分诊"));
      setText("jump-story", copy("Stories", "故事"));
      setText("jump-ops", copy("Delivery", "交付"));
      setText("deploy-title", copy("Deploy Mission", "创建监测任务"));
      setText("deploy-copy", copy("Create one watch, add optional scope, then decide whether alert routing is needed.", "先定义监测任务，再按需补充范围和通知条件。"));
      setText("preset-title", copy("Mission Modes", "任务预设"));
      setText("preset-copy", copy("Start from an archetype when the workflow is familiar, then only adjust the fields that matter.", "如果任务模式比较固定，可以直接套用预设，再修改关键字段。"));
      setText("deck-step-1-title", copy("Required Mission Input", "基础信息"));
      setText("deck-step-1-copy", copy("Name and query define the watch. Everything else can be layered on later.", "名称和查询词决定这个任务监测什么，其余设置都可以后补。"));
      setText("label-name", copy("Name", "名称"));
      setText("label-query", copy("Query", "查询词"));
      setText("hint-name", copy("Use a short operator-facing label.", "建议填写一个便于识别的简短名称。"));
      setText("hint-query", copy("Describe the signal you want tracked.", "描述你希望持续跟踪的主题、事件或对象。"));
      setText("deck-step-2-title", copy("Scope And Cadence", "范围与频率"));
      setText("deck-step-2-copy", copy("Use schedule and platform to narrow the mission only when you already know the operating lane.", "只有当你已经知道主要监测通道时，再补充频率、平台或站点。"));
      setText("label-schedule", copy("Schedule", "调度频率"));
      setText("label-platform", copy("Platform", "平台"));
      setText("label-domain", copy("Alert Domain", "站点/域名"));
      setText("hint-schedule", copy("Manual is fine for first exploration.", "初次探索时，用手动执行就够了。"));
      setText("hint-platform", copy("Leave empty for broader discovery.", "如果还不确定监测来源，可以先留空。"));
      setText("hint-domain", copy("Optional domain guard for tighter recall.", "可选的站点约束，用来提升结果收敛度。"));
      setText("schedule-lanes-title", copy("Schedule Lanes", "常用频率"));
      setText("platform-lanes-title", copy("Platform Lanes", "常用平台"));
      setText("deck-step-3-title", copy("Optional Alert Gate", "通知条件（可选）"));
      setText("deck-step-3-copy", copy("Attach delivery only when the mission is ready to trigger downstream action.", "只有当这个任务需要自动通知外部时，再补充告警条件。"));
      setText("label-route", copy("Alert Route", "告警路由"));
      setText("label-keyword", copy("Alert Keyword", "告警关键词"));
      setText("label-score", copy("Min Score", "最低分数"));
      setText("label-confidence", copy("Min Confidence", "最低置信度"));
      setText("hint-route", copy("Choose a named route when the watch should notify someone.", "如果需要自动通知，就选择一个命名路由。"));
      setText("hint-keyword", copy("Use a high-signal term to reduce noise.", "用高信号关键词减少无关结果。"));
      setText("hint-score", copy("Use when you only want stronger ranked hits.", "只想保留高分结果时再设置。"));
      setText("hint-confidence", copy("Use when analyst quality matters more than coverage.", "当质量比覆盖更重要时再设置。"));
      setText("route-snap-title", copy("Route Snap", "常用路由"));
      setText("create-watch-submit", copy("Create Watch", "创建任务"));
      setText("create-watch-clear", copy("Reset Draft", "清空草稿"));
      setText("clone-title", copy("Clone Existing Mission", "从已有任务复制"));
      setText("clone-copy", copy("Fork an existing watch when the current mission is only a variation in route, threshold, or query wording.", "如果当前任务只是查询词、阈值或路由的小改动，直接复制已有任务会更快。"));
      setText("actions-title", copy("Recent Actions", "最近变更"));
      setText("actions-copy", copy("Every reversible mutation stays here briefly so you can undo false starts without losing flow.", "最近的可撤销操作会暂时保留在这里，方便你快速回退。"));
      setText("board-title", copy("Mission Board", "任务看板"));
      setText("board-copy", copy("Run missions, open the cockpit, and keep review handoff facts attached to the active board lane.", "在一个列表里完成执行任务、打开详情，并把审阅交接事实保持在当前任务工作线附近。"));
      setText("alert-stream-title", copy("Alert Stream", "告警动态"));
      setText("alert-stream-copy", copy("Read recent alert events beside route editing and health instead of treating them as a detached feed.", "把最近告警事件放在路由编辑和健康状态旁边查看，而不是再把它当成一条脱离上下文的独立信息流。"));
      setText("alert-stream-mode", copy("Events read-only", "事件只读"));
      setText("route-manager-title", copy("Route Manager", "路由管理"));
      setText("route-manager-copy", copy("Create named delivery sinks once, then attach them from Mission Intake or the Cockpit alert editor without retyping webhook or chat details.", "把命名交付路由先配置一次，后续在新建任务或任务详情的告警编辑器里直接绑定，不必重复填写 webhook 或会话信息。"));
      setText("route-manager-mode", copy("Editable", "可编辑"));
      setText("ops-title", copy("Ops Snapshot", "运行状态"));
      setText("ops-copy", copy("Watch alerting missions, story readiness, route delivery, and recent failures in one delivery slice.", "把触发告警的任务、故事就绪度、路由投递和近期失败集中到一个交付视图。"));
      setText("ai-surface-title", copy("AI Assistance Surfaces", "AI 辅助面"));
      setText("ai-surface-copy", copy("Inspect the same governed AI projection facts that CLI and MCP expose, without creating browser-only AI state.", "查看与 CLI 和 MCP 同源的 AI 投影治理事实，不在浏览器里制造私有 AI 状态。"));
      setText("ai-surface-mode", copy("Read-only", "只读"));
      setText("cockpit-title", copy("Mission Cockpit", "任务详情"));
      setText("cockpit-copy", copy("Open one mission to inspect runs, review continuity, follow-up actions, and route-backed delivery without losing the cockpit context.", "打开单个任务后，可以在不离开任务详情的前提下查看执行记录、审阅连续性、后续动作和路由交付。"));
      setText("distribution-title", copy("Distribution Health", "分发健康"));
      setText("distribution-copy", copy("See whether named delivery routes are healthy and which upstream work is feeding them before they go silent.", "提前发现命名路由是否健康，以及哪些上游工作正在给它们供流，避免进入静默失败。"));
      setText("distribution-mode", copy("Read-only", "只读"));
      setText("delivery-workspace-title", copy("Delivery Workspace", "交付工作区"));
      setText("delivery-workspace-copy", copy("Subscribe to persisted outputs, inspect one report package, and dispatch it through named routes without leaving the shell.", "在不离开当前 shell 的前提下完成持久化订阅、报告输出包审计和命名路由 dispatch。"));
      setText("delivery-workspace-mode", copy("Editable", "可编辑"));
      setText("triage-title", copy("Triage Queue", "分诊队列"));
      setText("triage-copy", copy("Review open items with one selected evidence workbench, keep analyst reasoning visible, and hand verified signal into stories without leaving the queue.", "通过一个选中证据工作台完成审阅，持续看到分析师推理，并在不离开队列的前提下把已核验信号交接给故事。"));
      setText("story-title", copy("Story Workspace", "故事工作台"));
      setText("story-copy", copy("Inspect promoted stories, evidence stacks, contradictions, and delivery readiness before the narrative leaves the browser.", "查看已提升的故事、证据堆栈、冲突点和交付就绪度，并在叙事离开浏览器前完成整理。"));
      setText("claims-title", copy("Claim Composer", "主张装配"));
      setText("claims-copy", copy("Compose source-bound claims and attach them to report sections without leaving the review lane.", "在不离开审阅主轨的前提下，编排带来源绑定的主张并把它挂进报告章节。"));
      setText("report-studio-title", copy("Report Studio", "报告工作台"));
      setText("report-studio-copy", copy("Inspect report sections, quality guardrails, and export previews over persisted report objects.", "围绕持久化报告对象查看章节结构、质量门禁和导出预览。"));
      setText("story-mode-switch-label", copy("Workspace mode", "工作区模式"));
      setText("story-mode-board-button", copy("Board", "看板"));
      setText("story-mode-editor-button", copy("Editor", "编辑"));
      setText("story-intake-title", copy("Story Intake", "故事录入"));
      setText("story-intake-copy", copy("Capture a manual brief when a story should exist before clustering catches up, then refine it inside the workspace.", "当某个故事需要先落下来、而聚类还没跟上时，可以先手工补录，再在工作台里继续完善。"));
      setText("story-intake-mode", copy("Editable", "可编辑"));
      setText("footer-note", copy("The browser is the operating surface. CLI and MCP remain first-class control planes.", "浏览器是主要操作界面；CLI 和 MCP 仍保持一等能力。"));
      setPlaceholder("command-palette-input", copy("Search actions, missions, stories, or routes", "搜索操作、任务、故事或路由"));
      setPlaceholder("input-name", copy("Launch Ops", "新品发布监测"));
      setPlaceholder("input-query", copy("OpenAI launch", "OpenAI 发布"));
      setPlaceholder("input-schedule", copy("@hourly / interval:15m", "@hourly / interval:15m"));
      setPlaceholder("input-platform", copy("twitter", "twitter"));
      setPlaceholder("input-domain", copy("openai.com", "openai.com"));
      setPlaceholder("input-route", copy("ops-webhook", "ops-webhook"));
      setPlaceholder("input-keyword", copy("launch", "发布"));
      setPlaceholder("input-score", copy("70", "70"));
      setPlaceholder("input-confidence", copy("0.8", "0.8"));
      document.querySelectorAll("[data-lang]").forEach((button) => {{
        button.classList.toggle("active", String(button.dataset.lang || "") === state.language);
      }});
      renderWorkspaceModeChrome();
      renderTopbarContext();
    }}

    state.language = detectInitialLanguage();

    function showToast(message, tone = "info") {{
      const rack = $("toast-rack");
      if (!rack) {{
        return;
      }}
      const toast = document.createElement("div");
      toast.className = `toast ${{tone}}`;
      toast.innerHTML = `
        <div class="mono">${{copy("mission signal", "任务信号")}} / ${{localizeWord(tone)}}</div>
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
      jumpToSection("section-intake");
      window.setTimeout(() => {{
        form.scrollIntoView({{ block: "nearest", behavior: "smooth" }});
        const field = form.elements.namedItem(fieldName);
        if (field && typeof field.focus === "function") {{
          field.focus();
          if (typeof field.select === "function") {{
            field.select();
          }}
        }}
      }}, 140);
    }}

    function scheduleModeLabel(value) {{
      const schedule = String(value || "").trim();
      if (!schedule || schedule === "manual") {{
        return copy("manual dispatch", "手动执行");
      }}
      if (schedule.startsWith("interval:")) {{
        return state.language === "zh"
          ? `频率 ${{schedule.replace("interval:", "")}}`
          : `cadence ${{schedule.replace("interval:", "")}}`;
      }}
      if (schedule.startsWith("@")) {{
        return state.language === "zh" ? `Cron 别名 ${{schedule}}` : `cron alias ${{schedule}}`;
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
          ? phrase(
              "Track {{query}} with {{schedule}} across {{platform}} surfaces.",
              "围绕 {{query}} 以 {{schedule}} 跟踪 {{platform}} 信号。",
              {{
                query: draft.query.trim(),
                schedule: scheduleModeLabel(draft.schedule),
                platform: draft.platform.trim() || copy("cross-platform", "跨平台"),
              }},
            )
          : copy("Add a query to project the mission into the live preview lane.", "填入查询词后，任务会立即投射到实时预览区。"),
        scoreLabel: draft.min_score.trim() ? copy(`score >= ${{draft.min_score.trim()}}`, `分数 >= ${{draft.min_score.trim()}}`) : copy("score gate unset", "未设置分数门槛"),
        confidenceLabel: draft.min_confidence.trim() ? copy(`confidence >= ${{draft.min_confidence.trim()}}`, `置信度 >= ${{draft.min_confidence.trim()}}`) : copy("confidence gate unset", "未设置置信度门槛"),
        filtersLabel: filters.length ? filters.join(" / ") : copy("no scope filter", "未设置范围过滤"),
        routeLabel: draft.route.trim() || copy("route not attached", "未绑定路由"),
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

    function setCreateWatchDraft(nextDraft, presetId = "", editingId = state.createWatchEditingId) {{
      state.createWatchDraft = normalizeCreateWatchDraft(nextDraft || defaultCreateWatchDraft());
      state.createWatchPresetId = presetId;
      state.createWatchEditingId = String(editingId || "").trim();
      syncCreateWatchForm();
      persistCreateWatchDraft();
      renderCreateWatchDeck();
      queueCreateWatchSuggestions();
      setContextRouteFromWatch();
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
      const editingId = String(state.createWatchEditingId || "").trim();
      const editing = Boolean(editingId);
      const advancedOpen = isCreateWatchAdvancedOpen(draft);
      const preview = buildCreateWatchPreview(draft);
      renderFormSuggestionLists();
      const presetPanel = $("create-watch-preset-panel");
      const presetRoot = $("create-watch-presets");
      const scheduleRoot = $("create-watch-schedule-picks");
      const platformRoot = $("create-watch-platform-picks");
      const routeRoot = $("create-watch-route-picks");
      const advancedTitle = $("deck-advanced-title");
      const advancedCopy = $("deck-advanced-copy");
      const advancedToggle = $("create-watch-advanced-toggle");
      const advancedSummary = $("create-watch-advanced-summary");
      const advancedPanel = $("create-watch-advanced-panel");
      const clonePanel = $("create-watch-clone-panel");
      const cloneRoot = $("create-watch-clones");
      const previewRoot = $("create-watch-preview");
      const suggestionRoot = $("create-watch-suggestions");
      const feedbackRoot = $("create-watch-feedback");
      const stageHudRoot = $("stage-hud");
      const submitButton = $("create-watch-submit");
      const clearButton = $("create-watch-clear");
      const deployTitle = $("deploy-title");
      const deployCopy = $("deploy-copy");

      if (deployTitle) {{
        deployTitle.textContent = editing ? copy("Edit Mission", "编辑监测任务") : copy("Deploy Mission", "创建监测任务");
      }}
      if (deployCopy) {{
        deployCopy.textContent = editing
          ? copy("Update one existing watch in place using the same mission deck.", "沿用同一套任务草稿面板，直接原位修改已有任务。")
          : copy("Create one watch, add optional scope, then decide whether alert routing is needed.", "先定义监测任务，再按需补充范围和通知条件。");
      }}
      if (advancedTitle) {{
        advancedTitle.textContent = editing ? copy("Refine Scope Carefully", "精细调整范围") : copy("Keep It Simple First", "先从简单输入开始");
      }}
      if (advancedCopy) {{
        advancedCopy.textContent = advancedOpen
          ? copy("Only fill the extra controls you actually need. Empty fields keep the mission broad and easier to operate.", "只填写真正需要的额外条件；留空代表任务保持更宽、更易操作。")
          : copy("Most missions only need Name and Query. Open advanced settings only when you need scope or alert delivery.", "大多数任务只需要名称和查询词；只有在要限定范围或接入告警时，再展开高级设置。");
      }}
      if (advancedToggle) {{
        advancedToggle.textContent = advancedOpen ? copy("Hide Advanced", "收起高级设置") : copy("Show Advanced", "展开高级设置");
        advancedToggle.setAttribute("aria-expanded", String(advancedOpen));
      }}
      if (advancedSummary) {{
        advancedSummary.innerHTML = summarizeCreateWatchAdvanced(draft).map((item) => `<span class="chip">${{escapeHtml(item)}}</span>`).join("");
      }}
      if (advancedPanel) {{
        advancedPanel.classList.toggle("collapsed", !advancedOpen);
        advancedPanel.setAttribute("aria-hidden", String(!advancedOpen));
      }}
      if (presetPanel) {{
        presetPanel.hidden = editing;
      }}
      if (clonePanel) {{
        clonePanel.hidden = editing;
      }}

      if (submitButton) {{
        submitButton.textContent = editing ? copy("Save Changes", "保存修改") : copy("Create Watch", "创建任务");
      }}
      if (clearButton) {{
        clearButton.textContent = editing ? copy("Cancel Edit", "取消编辑") : copy("Reset Draft", "清空草稿");
      }}

      if (presetRoot) {{
        presetRoot.innerHTML = createWatchPresets.map((preset, index) => `
          <button
            class="chip-btn ${{state.createWatchPresetId === preset.id ? "active" : ""}}"
            type="button"
            data-create-watch-preset="${{preset.id}}"
            title="${{escapeHtml(copy(preset.description, preset.zhDescription || preset.description))}}"
          >${{index + 1}}. ${{escapeHtml(copy(preset.label, preset.zhLabel || preset.label))}}</button>
        `).join("");
      }}

      if (scheduleRoot) {{
        scheduleRoot.innerHTML = scheduleLaneOptions.map((option) => `
          <button
            class="chip-btn ${{draft.schedule.trim() === option.value ? "active" : ""}}"
            type="button"
            data-create-watch-schedule="${{option.value}}"
          >${{escapeHtml(option.value === "manual" ? copy("manual", "手动") : option.label)}}</button>
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
          : `<span class="chip">${{copy("No named routes", "暂无命名路由")}}</span>`;
        routeRoot.innerHTML = routeButtons;
      }}

      if (cloneRoot) {{
        const cloneButtons = state.watches.length
          ? state.watches.slice(0, 6).map((watch) => `
              <button class="chip-btn" type="button" data-create-watch-clone="${{escapeHtml(watch.id)}}">${{escapeHtml(watch.name || watch.id)}}</button>
            `).join("")
          : `<span class="chip">${{copy("No mission to clone", "暂无可克隆任务")}}</span>`;
        cloneRoot.innerHTML = cloneButtons;
      }}

      if (previewRoot) {{
        previewRoot.className = `card mission-preview ${{preview.requiredReady ? "ready" : ""}}`;
        previewRoot.innerHTML = `
          <div class="card-top">
            <div>
              <div class="mono">${{copy("mission brief", "任务概览")}}</div>
              <h3 class="card-title" style="margin-top:10px;">${{escapeHtml(draft.name.trim() || copy("Unnamed Mission", "未命名任务"))}}</h3>
            </div>
            <span class="chip ${{preview.requiredReady ? "ok" : "hot"}}">${{preview.requiredReady ? copy("ready", "就绪") : copy("needs query/name", "缺少名称或查询词")}}</span>
          </div>
          <div class="panel-sub">${{escapeHtml(preview.summary)}}</div>
          <div class="preview-meter">
            <div class="preview-meter-fill" style="width:${{preview.readiness}}%;"></div>
          </div>
          <div class="meta">
            <span>${{copy("mode", "模式")}}=${{editing ? copy("edit existing", "编辑已有任务") : copy("create new", "新建任务")}}</span>
            <span>${{copy("readiness", "就绪度")}}=${{preview.readiness}}%</span>
            <span>${{copy("alert", "告警")}}=${{preview.alertArmed ? copy("armed", "已启用") : copy("passive", "未启用")}}</span>
            <span>${{copy("schedule", "频率")}}=${{escapeHtml(preview.scheduleLabel)}}</span>
          </div>
          <div class="preview-grid">
            <div class="preview-line">
              <div class="preview-label">${{copy("Scope", "范围")}}</div>
              <div class="preview-value">${{escapeHtml(preview.filtersLabel)}}</div>
            </div>
            <div class="preview-line">
              <div class="preview-label">${{copy("Route", "路由")}}</div>
              <div class="preview-value">${{escapeHtml(preview.routeLabel)}}</div>
            </div>
            <div class="preview-line">
              <div class="preview-label">${{copy("Score Gate", "分数门槛")}}</div>
              <div class="preview-value">${{escapeHtml(preview.scoreLabel)}}</div>
            </div>
            <div class="preview-line">
              <div class="preview-label">${{copy("Confidence Gate", "置信度门槛")}}</div>
              <div class="preview-value">${{escapeHtml(preview.confidenceLabel)}}</div>
            </div>
          </div>
        `;
      }}

      if (suggestionRoot) {{
        if (state.loading.suggestions) {{
          suggestionRoot.innerHTML = `
            <div class="mono">${{copy("mission suggestions", "任务建议")}}</div>
            <div class="panel-sub">${{copy("Deriving route, cadence, and duplicate signals from the current repository state.", "正在基于当前仓库状态推导路由、频率和重复信号。")}}</div>
            <div class="stack" style="margin-top:12px;">${{skeletonCard(4)}}</div>
          `;
        }} else if (!state.createWatchSuggestions) {{
          suggestionRoot.innerHTML = `
            <div class="mono">${{copy("mission suggestions", "任务建议")}}</div>
            <div class="panel-sub">${{copy("Start typing a mission draft and the deck will derive cadence, route, and duplicate pressure from current watches and stories.", "开始输入任务草稿后，系统会根据现有任务和故事自动推导频率、路由与重复风险。")}}</div>
          `;
        }} else {{
          const suggestions = state.createWatchSuggestions;
          const warningBlock = Array.isArray(suggestions.warnings) && suggestions.warnings.length
            ? `<div class="suggestion-list">${{suggestions.warnings.map((item) => `<div class="mini-item">${{escapeHtml(item)}}</div>`).join("")}}</div>`
            : `<div class="panel-sub">${{copy("No active conflict or delivery warning for this draft.", "当前草稿没有冲突或交付告警。")}}</div>`;
          const similarWatches = Array.isArray(suggestions.similar_watches) ? suggestions.similar_watches : [];
          const relatedStories = Array.isArray(suggestions.related_stories) ? suggestions.related_stories : [];
          suggestionRoot.innerHTML = `
            <div class="card-top">
              <div>
                <div class="mono">${{copy("mission suggestions", "任务建议")}}</div>
                <div class="panel-sub" style="margin-top:8px;">${{escapeHtml(suggestions.summary || "")}}</div>
              </div>
              <button class="btn-secondary" id="apply-all-suggestions" type="button">${{copy("Apply All", "全部应用")}}</button>
            </div>
            <div class="suggestion-grid">
              <div class="preview-grid">
                <div class="preview-line">
                  <div class="preview-label">${{copy("Cadence", "频率")}}</div>
                  <div class="preview-value">${{escapeHtml(suggestions.recommended_schedule || "-")}}</div>
                  <div class="panel-sub">${{escapeHtml(suggestions.schedule_reason || "")}}</div>
                </div>
                <div class="preview-line">
                  <div class="preview-label">${{copy("Platform", "平台")}}</div>
                  <div class="preview-value">${{escapeHtml(suggestions.recommended_platform || "-")}}</div>
                  <div class="panel-sub">${{escapeHtml(suggestions.platform_reason || "")}}</div>
                </div>
                <div class="preview-line">
                  <div class="preview-label">${{copy("Route", "路由")}}</div>
                  <div class="preview-value">${{escapeHtml(suggestions.recommended_route || "-")}}</div>
                  <div class="panel-sub">${{escapeHtml(suggestions.route_reason || "")}}</div>
                </div>
                <div class="preview-line">
                  <div class="preview-label">${{copy("Scope Hints", "范围提示")}}</div>
                  <div class="preview-value">${{escapeHtml(suggestions.recommended_keyword || "-")}} / ${{escapeHtml(suggestions.recommended_domain || "-")}}</div>
                  <div class="panel-sub">${{escapeHtml(suggestions.keyword_reason || suggestions.domain_reason || "")}}</div>
                </div>
              </div>
              <div class="chip-row">
                <button class="chip-btn" type="button" data-suggestion-apply="schedule">${{escapeHtml(suggestions.recommended_schedule || "schedule")}}</button>
                <button class="chip-btn" type="button" data-suggestion-apply="platform">${{escapeHtml(suggestions.recommended_platform || "platform")}}</button>
                <button class="chip-btn" type="button" data-suggestion-apply="route">${{escapeHtml(suggestions.recommended_route || "route")}}</button>
                <button class="chip-btn" type="button" data-suggestion-apply="keyword">${{escapeHtml(suggestions.recommended_keyword || "keyword")}}</button>
                <button class="chip-btn" type="button" data-suggestion-apply="thresholds">${{copy("score/confidence", "分数/置信度")}}</button>
              </div>
              <div class="stack">
                <div class="mono">${{copy("Warnings", "提醒")}}</div>
                ${{warningBlock}}
              </div>
              <div class="preview-grid">
                <div class="stack">
                  <div class="mono">${{copy("Similar Missions", "相似任务")}}</div>
                  ${{similarWatches.length ? similarWatches.map((item) => `<div class="mini-item">${{escapeHtml(item.name)}} | ${{copy("similarity", "相似度")}}=${{Number(item.similarity || 0).toFixed(2)}} | ${{escapeHtml(item.schedule || copy("manual", "手动"))}}</div>`).join("") : `<div class="panel-sub">${{copy("No mission conflict found.", "未发现任务冲突。")}}</div>`}}
                </div>
                <div class="stack">
                  <div class="mono">${{copy("Related Stories", "相关故事")}}</div>
                  ${{relatedStories.length ? relatedStories.map((item) => `<div class="mini-item">${{escapeHtml(item.title)}} | ${{copy("similarity", "相似度")}}=${{Number(item.similarity || 0).toFixed(2)}} | ${{copy("items", "条目")}}=${{item.item_count || 0}}</div>`).join("") : `<div class="panel-sub">${{copy("No story cluster overlap found.", "未发现故事簇重叠。")}}</div>`}}
                </div>
              </div>
            </div>
          `;
          suggestionRoot.querySelector("#apply-all-suggestions")?.addEventListener("click", () => {{
            const patch = suggestions.autofill_patch || {{}};
            state.createWatchAdvancedOpen = true;
            updateCreateWatchDraft(patch);
            showToast(copy("Applied suggested mission defaults", "已应用建议的任务默认值"), "success");
          }});
          suggestionRoot.querySelectorAll("[data-suggestion-apply]").forEach((button) => {{
            button.addEventListener("click", () => {{
              const patch = suggestions.autofill_patch || {{}};
              const field = String(button.dataset.suggestionApply || "").trim();
              if (field === "thresholds") {{
                state.createWatchAdvancedOpen = true;
                updateCreateWatchDraft({{
                  min_score: String(patch.min_score || ""),
                  min_confidence: String(patch.min_confidence || ""),
                }});
                return;
              }}
              if (!field || !(field in patch)) {{
                return;
              }}
              if (["schedule", "platform", "route", "keyword", "domain", "min_score", "min_confidence"].includes(field)) {{
                state.createWatchAdvancedOpen = true;
              }}
              updateCreateWatchDraft({{ [field]: String(patch[field] || "") }});
            }});
          }});
        }}
      }}

      if (feedbackRoot) {{
        if (editing) {{
          feedbackRoot.textContent = preview.requiredReady
            ? copy(
                `Editing ${{editingId}}. Use Cmd/Ctrl+Enter to save${{preview.alertArmed ? " with alert gating." : "."}}`,
                `正在编辑 ${{editingId}}。使用 Cmd/Ctrl+Enter 保存${{preview.alertArmed ? "，并带上告警门槛。" : "。"}}`,
              )
            : copy(
                `Editing ${{editingId}}. Name and Query are still required before saving.`,
                `正在编辑 ${{editingId}}。保存前仍需填写名称和查询词。`,
              );
        }} else {{
          feedbackRoot.textContent = preview.requiredReady
            ? copy(
                `Deck armed. Use Cmd/Ctrl+Enter to dispatch${{preview.alertArmed ? " with alert gating." : "."}}`,
                `草稿已就绪。使用 Cmd/Ctrl+Enter 提交${{preview.alertArmed ? "，并带上告警门槛。" : "。"}}`,
              )
            : copy("Required fields: Name and Query. Use / to focus the mission deck.", "必填字段：名称和查询词。按 / 可快速聚焦任务草稿。");
        }}
      }}

      if (stageHudRoot) {{
        stageHudRoot.innerHTML = `
          <div class="card-top">
            <div>
              <div class="mono">${{copy("Live Mission Projection", "实时任务投影")}}</div>
              <div class="stage-hud-title">${{escapeHtml(draft.name.trim() || draft.query.trim() || copy("Awaiting Mission Draft", "等待任务草稿"))}}</div>
            </div>
            <span class="chip ${{preview.requiredReady ? "ok" : ""}}">${{preview.requiredReady ? copy("synced", "已同步") : copy("draft", "草稿")}}</span>
          </div>
          <div class="stage-hud-summary">${{escapeHtml(preview.summary)}}</div>
          <div class="stage-hud-meta">
            <span class="chip">${{escapeHtml(preview.scheduleLabel)}}</span>
            <span class="chip">${{escapeHtml(preview.filtersLabel)}}</span>
            <span class="chip ${{preview.alertArmed ? "hot" : ""}}">${{preview.alertArmed ? copy("alert armed", "告警已启用") : copy("passive watch", "仅监测")}}</span>
          </div>
        `;
      }}
      renderActionHistory();
    }}

    function createWatchDraftFromMissionDetail(detail, {{ copyName = false }} = {{}}) {{
      const firstRule = Array.isArray(detail.alert_rules) && detail.alert_rules.length ? detail.alert_rules[0] : {{}};
      return {{
        name: copyName && detail.name ? `${{detail.name}} copy` : (detail.name || ""),
        schedule: detail.schedule || "",
        query: detail.query || "",
        platform: Array.isArray(detail.platforms) && detail.platforms.length ? detail.platforms[0] : "",
        domain: Array.isArray(firstRule.domains) && firstRule.domains.length ? firstRule.domains[0] : "",
        route: Array.isArray(firstRule.routes) && firstRule.routes.length ? firstRule.routes[0] : "",
        keyword: Array.isArray(firstRule.keyword_any) && firstRule.keyword_any.length ? firstRule.keyword_any[0] : "",
        min_score: firstRule.min_score ? String(firstRule.min_score) : "",
        min_confidence: firstRule.min_confidence ? String(firstRule.min_confidence) : "",
      }};
    }}

    async function editMissionInCreateWatch(identifier) {{
      if (!identifier) {{
        return;
      }}
      const detail = state.watchDetails[identifier] || await api(`/api/watches/${{identifier}}`);
      state.watchDetails[identifier] = detail;
      state.createWatchAdvancedOpen = true;
      setCreateWatchDraft(createWatchDraftFromMissionDetail(detail), "", detail.id || identifier);
      showToast(
        state.language === "zh"
          ? `已载入任务编辑：${{detail.name || identifier}}`
          : `Editing mission: ${{detail.name || identifier}}`,
        "success",
      );
      focusCreateWatchDeck("name");
    }}

    async function cloneMissionIntoCreateWatch(identifier) {{
      if (!identifier) {{
        return;
      }}
      const detail = state.watchDetails[identifier] || await api(`/api/watches/${{identifier}}`);
      state.watchDetails[identifier] = detail;
      state.createWatchAdvancedOpen = true;
      setCreateWatchDraft(createWatchDraftFromMissionDetail(detail, {{ copyName: true }}), "", "");
      showToast(
        state.language === "zh"
          ? `已从 ${{detail.name || identifier}} 克隆任务草稿`
          : `Mission deck cloned from ${{detail.name || identifier}}`,
        "success",
      );
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
      const advancedToggle = $("create-watch-advanced-toggle");
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

      advancedToggle?.addEventListener("click", () => {{
        state.createWatchAdvancedOpen = !isCreateWatchAdvancedOpen(state.createWatchDraft || defaultCreateWatchDraft());
        renderCreateWatchDeck();
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
        state.createWatchAdvancedOpen = draftHasAdvancedSignal(preset.values);
        setCreateWatchDraft(preset.values, preset.id, "");
        showToast(
          state.language === "zh"
            ? `${{preset.zhLabel || preset.label}} 已载入任务草稿`
            : `${{preset.label}} loaded into the mission deck`,
          "success",
        );
        focusCreateWatchDeck("query");
      }});

      scheduleRoot?.addEventListener("click", (event) => {{
        const button = event.target.closest("[data-create-watch-schedule]");
        if (!button) {{
          return;
        }}
        state.createWatchAdvancedOpen = true;
        updateCreateWatchDraft({{ schedule: String(button.dataset.createWatchSchedule || "") }});
      }});

      platformRoot?.addEventListener("click", (event) => {{
        const button = event.target.closest("[data-create-watch-platform]");
        if (!button) {{
          return;
        }}
        state.createWatchAdvancedOpen = true;
        updateCreateWatchDraft({{ platform: String(button.dataset.createWatchPlatform || "") }});
      }});

      routeRoot?.addEventListener("click", (event) => {{
        const button = event.target.closest("[data-create-watch-route]");
        if (!button) {{
          return;
        }}
        state.createWatchAdvancedOpen = true;
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
          reportError(error, copy("Clone mission", "克隆任务"));
        }} finally {{
          button.disabled = false;
        }}
      }});

      clearButton?.addEventListener("click", () => {{
        const wasEditing = Boolean(String(state.createWatchEditingId || "").trim());
        state.createWatchAdvancedOpen = null;
        setCreateWatchDraft(defaultCreateWatchDraft(), "", "");
        showToast(
          wasEditing
            ? copy("Mission edit cancelled", "已取消任务编辑")
            : copy("Mission deck draft cleared", "已清空任务草稿"),
          "success",
        );
        focusCreateWatchDeck("name");
      }});
    }}

    function bindRouteDeck() {{
      if (!state.routeDraft) {{
        state.routeDraft = defaultRouteDraft();
      }}
      renderRouteDeck();
    }}

    function bindStoryDeck() {{
      if (!state.storyDraft) {{
        state.storyDraft = defaultStoryDraft();
      }}
      renderStoryCreateDeck();
      const storyWorkspaceModeSwitch = $("story-workspace-mode-switch");
      if (storyWorkspaceModeSwitch) {{
        storyWorkspaceModeSwitch.querySelectorAll("[data-story-workspace-mode]").forEach((button) => {{
          button.addEventListener("click", () => {{
            const nextMode = String(button.dataset.storyWorkspaceMode || "").trim().toLowerCase();
            applyStoryWorkspaceMode(nextMode, {{ persist: true, syncUrl: true }});
          }});
        }});
      }}
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

    function rerenderLanguageSensitiveViews() {{
      applyLanguageChrome();
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
      renderCommandPalette();
    }}

    function setLanguage(nextLanguage) {{
      const normalized = String(nextLanguage || "").trim().toLowerCase() === "zh" ? "zh" : "en";
      state.language = normalized;
      safeLocalStorageSet(languageStorageKey, normalized);
      rerenderLanguageSensitiveViews();
    }}

    function bindLanguageSwitch() {{
      document.querySelectorAll("[data-lang]").forEach((button) => {{
        button.addEventListener("click", () => {{
          const nextLanguage = String(button.dataset.lang || "").trim();
          if (!nextLanguage || nextLanguage === state.language) {{
            return;
          }}
          setLanguage(nextLanguage);
        }});
      }});
    }}

    function bindSectionJumps() {{
      document.querySelectorAll("[data-jump-target]").forEach((button) => {{
        button.addEventListener("click", () => {{
          const targetId = String(button.dataset.jumpTarget || "").trim();
          jumpToSection(targetId);
        }});
      }});
    }}

    function bindSectionTracking() {{
      const sectionIds = [
        "section-intake",
        "section-board",
        "section-cockpit",
        "section-triage",
        "section-story",
        "section-claims",
        "section-report-studio",
        "section-ops",
      ];
      const sections = sectionIds
        .map((sectionId) => document.getElementById(sectionId))
        .filter(Boolean);
      if (!sections.length) {{
        return;
      }}
      if ("IntersectionObserver" in window) {{
        const observer = new IntersectionObserver((entries) => {{
          const visible = entries
            .filter((entry) => entry.isIntersecting)
            .sort((left, right) => right.intersectionRatio - left.intersectionRatio);
          if (!visible.length) {{
            return;
          }}
          const nextSectionId = normalizeSectionId(visible[0].target.id);
          if (nextSectionId === state.activeSectionId) {{
            return;
          }}
          state.activeSectionId = nextSectionId;
          renderWorkspaceModeChrome();
          renderTopbarContext();
        }}, {{
          root: null,
          rootMargin: "-18% 0px -56% 0px",
          threshold: [0.18, 0.35, 0.55],
        }});
        sections.forEach((section) => observer.observe(section));
      }}
      window.addEventListener("hashchange", () => {{
        state.activeSectionId = normalizeSectionId(window.location.hash || state.activeSectionId);
        renderWorkspaceModeChrome();
        renderTopbarContext();
      }});
    }}

    function buildCommandPaletteEntries() {{
      const entries = [
        {{
          id: "refresh",
          group: copy("system", "系统"),
          title: copy("Refresh Console", "刷新控制台"),
          subtitle: copy("Reload overview, missions, triage, stories, and ops.", "重新加载总览、任务、分诊、故事和运维视图。"),
          run: async () => {{
            await refreshBoard();
            showToast(copy("Console refreshed", "控制台已刷新"), "success");
          }},
        }},
        {{
          id: "run-due",
          group: copy("system", "系统"),
          title: copy("Run Due Missions", "执行到点任务"),
          subtitle: copy("Dispatch every mission currently due.", "立即执行当前所有到点任务。"),
          run: async () => {{
            await api("/api/watches/run-due", {{ method: "POST", headers: jsonHeaders, body: JSON.stringify({{ limit: 0 }}) }});
            await refreshBoard();
            showToast(copy("Due missions dispatched", "到点任务已触发执行"), "success");
          }},
        }},
        {{
          id: "reset-context",
          group: copy("system", "系统"),
          title: copy("Reset Workspace Context", "重置工作上下文"),
          subtitle: copy("Clear mission, triage, story, and palette browsing context without touching drafts or saved data.", "清除任务、分诊、故事和命令面板的浏览上下文，但不影响草稿和已保存数据。"),
          run: async () => {{
            resetWorkspaceContext();
          }},
        }},
        {{
          id: "copy-context-link",
          group: copy("system", "系统"),
          title: copy("Copy Context Link", "复制当前上下文链接"),
          subtitle: copy("Copy the current deep link with section, filters, and focused records.", "复制包含当前区块、筛选条件和焦点记录的深链。"),
          run: async () => {{
            await copyCurrentContextLink();
          }},
        }},
        {{
          id: "save-current-view",
          group: copy("system", "系统"),
          title: copy("Save Current View", "保存当前视图"),
          subtitle: copy("Pin the current workspace context as a reusable saved view.", "把当前工作上下文固定成一个可复用的保存视图。"),
          run: async () => {{
            saveCurrentContextView();
          }},
        }},
        {{
          id: "save-pin-current-view",
          group: copy("system", "系统"),
          title: copy("Save + Pin Current View", "保存并固定当前视图"),
          subtitle: copy("Save the current workspace context and pin it into the top dock in one step.", "一步把当前工作上下文保存并固定到顶部坞站。"),
          run: async () => {{
            saveAndPinCurrentContextView();
          }},
        }},
        ...(state.contextLinkHistory[0]
          ? [{{
              id: "open-last-context-link",
              group: copy("system", "系统"),
              title: copy("Open Last Shared Context", "打开最近分享上下文"),
              subtitle: copy("Restore the most recently copied deep link without reloading the page.", "在不刷新页面的情况下恢复最近一次复制的深链。"),
              run: async () => {{
                restoreContextLinkHistoryEntry(0);
              }},
            }}]
          : []),
        ...(state.contextLinkHistory.length
          ? [{{
              id: "clear-context-link-history",
              group: copy("system", "系统"),
              title: copy("Clear Shared Context History", "清空分享上下文历史"),
              subtitle: copy("Remove recent shared deep links from the context lens.", "清空上下文透镜中的最近分享深链。"),
              run: async () => {{
                clearContextLinkHistory();
              }},
            }}]
          : []),
        ...(state.contextSavedViews.length
          ? state.contextSavedViews
              .map((entry, index) => normalizeContextSavedViewEntry(entry))
              .filter(Boolean)
              .slice(0, 6)
              .map((entry, index) => ({{
                id: `open-saved-context-${{index}}`,
                group: copy("system", "系统"),
                title: state.language === "zh"
                  ? `打开保存视图：${{entry.pinned ? "[已固定] " : ""}}${{entry.name}}`
                  : `Open Saved View: ${{entry.pinned ? "[Pinned] " : ""}}${{entry.name}}`,
                subtitle: entry.pinned
                  ? phrase("Pinned | {{summary}}", "已固定 | {{summary}}", {{ summary: entry.summary }})
                  : entry.summary,
                run: async () => {{
                  restoreContextSavedViewEntry(index);
                }},
              }}))
          : []),
        ...(getDefaultContextSavedView()
          ? [{{
              id: "open-default-saved-view",
              group: copy("system", "系统"),
              title: copy("Open Default Landing View", "打开默认落地视图"),
              subtitle: getDefaultContextSavedView()?.summary || copy("Restore the default saved workspace view.", "恢复默认保存工作视图。"),
              run: async () => {{
                const entry = getDefaultContextSavedView();
                if (entry) {{
                  restoreContextSavedViewByName(entry.name);
                }}
              }},
            }},
            {{
              id: "clear-default-saved-view",
              group: copy("system", "系统"),
              title: copy("Clear Default Landing View", "清除默认落地视图"),
              subtitle: copy("Stop auto-opening a saved view when the console boots without a deep link.", "控制台在没有深链时启动时，不再自动打开保存视图。"),
              run: async () => {{
                clearDefaultContextSavedView();
              }},
            }}]
          : []),
        ...(state.contextSavedViews.length
          ? [{{
              id: "clear-saved-context-views",
              group: copy("system", "系统"),
              title: copy("Clear Saved Views", "清空保存视图"),
              subtitle: copy("Remove every named saved view from the context lens.", "移除上下文透镜里的全部命名保存视图。"),
              run: async () => {{
                clearContextSavedViews();
              }},
            }}]
          : []),
        {{
          id: "focus-deck",
          group: copy("deck", "草稿"),
          title: copy("Focus Mission Deck", "聚焦任务草稿"),
          subtitle: copy("Jump to the draft deck and focus the main field.", "跳转到任务草稿区并聚焦主输入框。"),
          run: async () => {{
            focusCreateWatchDeck((state.createWatchDraft && state.createWatchDraft.name.trim()) ? "query" : "name");
          }},
        }},
        {{
          id: "clear-deck",
          group: copy("deck", "草稿"),
          title: copy("Reset Mission Deck", "清空任务草稿"),
          subtitle: copy("Clear the current draft and its stored local state.", "清空当前草稿及其本地缓存。"),
          run: async () => {{
            const wasEditing = Boolean(String(state.createWatchEditingId || "").trim());
            state.createWatchAdvancedOpen = null;
            setCreateWatchDraft(defaultCreateWatchDraft(), "", "");
            showToast(
              wasEditing
                ? copy("Mission edit cancelled", "已取消任务编辑")
                : copy("Mission deck draft cleared", "已清空任务草稿"),
              "success",
            );
          }},
        }},
        {{
          id: "focus-route-deck",
          group: copy("routes", "路由"),
          title: copy("Focus Route Deck", "聚焦路由草稿"),
          subtitle: copy("Jump to the route manager and focus the route name field.", "跳转到路由管理区并聚焦路由名称。"),
          run: async () => {{
            focusRouteDeck((state.routeDraft && state.routeDraft.name.trim()) ? "description" : "name");
          }},
        }},
        {{
          id: "clear-route-deck",
          group: copy("routes", "路由"),
          title: copy("Reset Route Deck", "清空路由草稿"),
          subtitle: copy("Clear the current route draft or exit edit mode.", "清空当前路由草稿或退出编辑模式。"),
          run: async () => {{
            const wasEditing = Boolean(normalizeRouteName(state.routeEditingId));
            state.routeAdvancedOpen = null;
            setRouteDraft(defaultRouteDraft(), "");
            showToast(
              wasEditing
                ? copy("Route edit cancelled", "已取消路由编辑")
                : copy("Route deck draft cleared", "已清空路由草稿"),
              "success",
            );
          }},
        }},
        {{
          id: "focus-story-deck",
          group: copy("stories", "故事"),
          title: copy("Focus Story Intake", "聚焦故事录入"),
          subtitle: copy("Jump to the manual story deck and start a new brief.", "跳转到手工故事草稿区，直接开始新建简报。"),
          run: async () => {{
            focusStoryDeck((state.storyDraft && state.storyDraft.title.trim()) ? "summary" : "title");
          }},
        }},
      ];
      storyViewPresetOptions.forEach((viewKey) => {{
        entries.push({{
          id: `story-view-${{viewKey}}`,
          group: copy("stories", "故事"),
          title: state.language === "zh"
            ? `切换故事视图：${{storyViewPresetLabel(viewKey)}}`
            : `Story View: ${{storyViewPresetLabel(viewKey)}}`,
          subtitle: storyViewPresetDescription(viewKey),
          run: async () => {{
            applyStoryViewPreset(viewKey, {{ jump: true, toast: true }});
          }},
        }});
      }});
      if (state.actionLog.length && state.actionLog[0].undo) {{
        const latestAction = state.actionLog[0];
        entries.unshift({{
          id: `undo-${{latestAction.id}}`,
          group: copy("actions", "操作"),
          title: state.language === "zh" ? `撤销：${{latestAction.label}}` : `Undo: ${{latestAction.label}}`,
          subtitle: latestAction.detail || copy("Reverse the latest reversible action.", "撤销最近一次可回退操作。"),
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
          group: copy("missions", "任务"),
          title: state.language === "zh" ? `打开任务：${{watch.name}}` : `Open Mission: ${{watch.name}}`,
          subtitle: `${{watch.query || "-"}} | ${{watch.enabled ? copy("enabled", "已启用") : copy("disabled", "已停用")}}`,
          run: async () => {{
            await loadWatch(watch.id);
          }},
        }});
        entries.push({{
          id: `watch-edit-${{watch.id}}`,
          group: copy("missions", "任务"),
          title: state.language === "zh" ? `编辑任务：${{watch.name}}` : `Edit Mission: ${{watch.name}}`,
          subtitle: copy("Load this mission into the deck for in-place editing.", "把该任务载入草稿区，直接原位编辑。"),
          run: async () => {{
            await editMissionInCreateWatch(watch.id);
          }},
        }});
        entries.push({{
          id: `watch-clone-${{watch.id}}`,
          group: copy("missions", "任务"),
          title: state.language === "zh" ? `克隆任务：${{watch.name}}` : `Clone Mission: ${{watch.name}}`,
          subtitle: copy("Pull this mission into the deck as a draft fork.", "把这个任务拉进草稿区，作为分支任务继续编辑。"),
          run: async () => {{
            await cloneMissionIntoCreateWatch(watch.id);
          }},
        }});
      }});
      state.routes.slice(0, 6).forEach((route) => {{
        entries.push({{
          id: `route-edit-${{route.name}}`,
          group: copy("routes", "路由"),
          title: state.language === "zh" ? `编辑路由：${{route.name}}` : `Edit Route: ${{route.name}}`,
          subtitle: `${{routeChannelLabel(route.channel)}} | ${{summarizeRouteDestination(route)}}`,
          run: async () => {{
            await editRouteInDeck(route.name);
          }},
        }});
        entries.push({{
          id: `route-apply-${{route.name}}`,
          group: copy("routes", "路由"),
          title: state.language === "zh" ? `把路由用于任务：${{route.name}}` : `Use Route In Mission: ${{route.name}}`,
          subtitle: copy("Attach this named route to the mission intake deck.", "把这个命名路由直接带入任务草稿。"),
          run: async () => {{
            await applyRouteToMissionDraft(route.name);
          }},
        }});
      }});
      const visibleTriage = getVisibleTriageItems();
      const focusedTriageId = state.selectedTriageId || (visibleTriage[0] ? visibleTriage[0].id : "");
      const focusedTriage = focusedTriageId
        ? visibleTriage.find((item) => item.id === focusedTriageId) || state.triage.find((item) => item.id === focusedTriageId)
        : null;
      if (focusedTriage) {{
        entries.push({{
          id: `triage-story-${{focusedTriage.id}}`,
          group: copy("triage", "分诊"),
          title: state.language === "zh" ? `从分诊生成故事：${{focusedTriage.title}}` : `Create Story From Triage: ${{focusedTriage.title}}`,
          subtitle: copy("Promote the focused triage item into a story draft and jump to Story Workspace.", "把当前焦点分诊条目提升为故事草稿，并跳转到故事工作台。"),
          run: async () => {{
            await createStoryFromTriageItems([focusedTriage.id]);
          }},
        }});
        entries.push({{
          id: `triage-note-${{focusedTriage.id}}`,
          group: copy("triage", "分诊"),
          title: state.language === "zh" ? `聚焦备注：${{focusedTriage.title}}` : `Focus Note: ${{focusedTriage.title}}`,
          subtitle: copy("Jump back to the queue and place the cursor in the note composer.", "跳回分诊队列，并把光标放进备注输入框。"),
          run: async () => {{
            focusTriageNoteComposer(focusedTriage.id);
          }},
        }});
      }}
      state.stories.slice(0, 5).forEach((story) => {{
        entries.push({{
          id: `story-open-${{story.id}}`,
          group: copy("stories", "故事"),
          title: state.language === "zh" ? `打开故事：${{story.title}}` : `Open Story: ${{story.title}}`,
          subtitle: `${{localizeWord(story.status || "active")}} | ${{copy("items", "条目")}}=${{story.item_count || 0}}`,
          run: async () => {{
            await loadStory(story.id);
          }},
        }});
      }});
      return entries;
    }}

    function getCommandPaletteEntriesForQuery() {{
      const query = String(state.commandPalette.query || "").trim().toLowerCase();
      const filteredEntries = buildCommandPaletteEntries().filter((entry) => {{
        if (!query) {{
          return true;
        }}
        return [entry.group, entry.title, entry.subtitle].some((value) => String(value || "").toLowerCase().includes(query));
      }});
      if (query) {{
        return filteredEntries;
      }}
      const recentIds = uniqueValues(state.commandPalette.recentIds || []).slice(0, 8);
      if (!recentIds.length) {{
        return filteredEntries;
      }}
      const recentEntries = recentIds
        .map((entryId) => filteredEntries.find((entry) => entry.id === entryId))
        .filter(Boolean)
        .map((entry) => ({{
          ...entry,
          group: copy("recent", "最近"),
          subtitle: entry.subtitle
            ? `${{copy("from", "来自")}} ${{entry.group}} | ${{entry.subtitle}}`
            : `${{copy("from", "来自")}} ${{entry.group}}`,
        }}));
      const seen = new Set(recentEntries.map((entry) => entry.id));
      return [...recentEntries, ...filteredEntries.filter((entry) => !seen.has(entry.id))];
    }}

    async function executePaletteEntry(entry) {{
      if (!entry) {{
        return;
      }}
      closeCommandPalette();
      noteCommandPaletteRecent(entry.id);
      try {{
        await entry.run();
      }} catch (error) {{
        reportError(error, "Palette action");
      }}
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
      const entries = getCommandPaletteEntriesForQuery();
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
        : `<div class="empty">${{copy("No command matched the current search.", "当前搜索没有匹配到命令。")}}</div>`;
      list.querySelectorAll("[data-palette-id]").forEach((item) => {{
        item.addEventListener("mouseenter", () => {{
          state.commandPalette.selectedIndex = Number(item.dataset.paletteIndex || 0);
          renderCommandPalette();
        }});
        item.addEventListener("click", async () => {{
          const entry = entries.find((candidate) => candidate.id === item.dataset.paletteId);
          await executePaletteEntry(entry);
        }});
      }});
      input.value = state.commandPalette.query;
    }}

    function openCommandPalette() {{
      setContextLensOpen(false);
      state.commandPalette.open = true;
      state.commandPalette.selectedIndex = 0;
      renderCommandPalette();
      window.setTimeout(() => $("command-palette-input")?.focus(), 10);
    }}

    function closeCommandPalette() {{
      state.commandPalette.open = false;
      state.commandPalette.selectedIndex = 0;
      renderCommandPalette();
    }}

    function bindContextLens() {{
      const summary = $("context-summary");
      const lens = $("context-lens");
      const backdrop = $("context-lens-backdrop");
      const dialog = $("context-lens-shell");
      const saveForm = $("context-save-form");
      const saveInput = $("context-save-name");
      if (!summary || !lens || !backdrop || !dialog) {{
        return;
      }}
      summary.addEventListener("click", (event) => {{
        event.stopPropagation();
        state.contextLensRestoreFocusId = "context-summary";
        toggleContextLens();
      }});
      backdrop.addEventListener("click", (event) => {{
        if (event.target === backdrop) {{
          setContextLensOpen(false);
        }}
      }});
      dialog.addEventListener("keydown", (event) => {{
        if (String(event.key || "") !== "Tab" || !state.contextLensOpen) {{
          return;
        }}
        const focusable = getContextLensFocusableElements();
        if (!focusable.length) {{
          event.preventDefault();
          dialog.focus();
          return;
        }}
        const first = focusable[0];
        const last = focusable[focusable.length - 1];
        const active = document.activeElement;
        if (event.shiftKey && (active === first || active === dialog)) {{
          event.preventDefault();
          last.focus();
          return;
        }}
        if (!event.shiftKey && active === last) {{
          event.preventDefault();
          first.focus();
        }}
      }});
      saveForm?.addEventListener("submit", (event) => {{
        event.preventDefault();
        saveCurrentContextView(saveInput?.value || "");
      }});
      $("context-lens-close")?.addEventListener("click", () => {{
        setContextLensOpen(false);
      }});
      $("context-open-section")?.addEventListener("click", () => {{
        setContextLensOpen(false);
        jumpToSection(state.activeSectionId);
      }});
      $("context-copy-link")?.addEventListener("click", async () => {{
        await copyCurrentContextLink();
        setContextLensOpen(false);
      }});
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
        persistCommandPaletteQuery();
        renderCommandPalette();
      }});
      input.addEventListener("keydown", async (event) => {{
        const list = getCommandPaletteEntriesForQuery();
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
          await executePaletteEntry(entry);
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
        root.innerHTML = `<div class="empty">${{copy("No reversible action yet. Create, tune, or triage something and it will show up here.", "当前还没有可回退的操作。创建、调整或分诊后，会在这里显示。")}}</div>`;
        return;
      }}
      root.innerHTML = state.actionLog.slice(0, 6).map((entry) => `
        <div class="action-log-item">
          <div class="card-top">
            <div>
              <div class="mono">${{escapeHtml(entry.kind || "action")}}</div>
              <div>${{escapeHtml(entry.label || "")}}</div>
            </div>
            <span class="chip ${{entry.status === "error" ? "hot" : entry.status === "ready" ? "ok" : ""}}">${{escapeHtml(localizeWord(entry.status || "done"))}}</span>
          </div>
          <div class="panel-sub">${{escapeHtml(entry.detail || "")}}</div>
          <div class="actions">
            ${{
              entry.undo
                ? `<button class="btn-secondary" type="button" data-action-undo="${{entry.id}}">${{escapeHtml(entry.undoLabel || copy("Undo", "撤销"))}}</button>`
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

    function renderLifecycleGuideCard({{ title = "", summary = "", steps = [], actions = [], tone = "ok" }} = {{}}) {{
      const stepsHtml = steps.map((step, index) => `
        <div class="guide-card">
          <div class="guide-step">${{String(index + 1).padStart(2, "0")}}</div>
          <div class="mono">${{escapeHtml(step.title || "")}}</div>
          <div class="panel-sub">${{escapeHtml(step.copy || "")}}</div>
        </div>
      `).join("");
      const actionsHtml = actions.length
        ? `<div class="actions" style="margin-top:14px;">${{actions.map((action) => `
            <button
              class="${{action.primary ? "btn-primary" : "btn-secondary"}}"
              type="button"
              ${{action.section ? `data-empty-jump="${{escapeHtml(action.section)}}"` : ""}}
              ${{action.focus ? `data-empty-focus="${{escapeHtml(action.focus)}}"` : ""}}
              ${{action.field ? `data-empty-field="${{escapeHtml(action.field)}}"` : ""}}
              ${{action.watch ? `data-empty-watch="${{escapeHtml(action.watch)}}"` : ""}}
              ${{action.runWatch ? `data-empty-run-watch="${{escapeHtml(action.runWatch)}}"` : ""}}
            >${{escapeHtml(action.label || "")}}</button>
          `).join("")}}</div>`
        : "";
      return `
        <div class="card">
          <div class="card-top">
            <div>
              <div class="mono">${{copy("lifecycle guide", "生命周期引导")}}</div>
              <h3 class="card-title" style="margin-top:10px;">${{escapeHtml(title)}}</h3>
            </div>
            <span class="chip ${{tone}}">${{copy("browser-first", "浏览器优先")}}</span>
          </div>
          <div class="panel-sub">${{escapeHtml(summary)}}</div>
          <div class="guide-grid" style="margin-top:14px;">${{stepsHtml}}</div>
          ${{actionsHtml}}
        </div>
      `;
    }}

    function wireLifecycleGuideActions(root) {{
      if (!root) {{
        return;
      }}
      root.querySelectorAll("[data-empty-jump]").forEach((button) => {{
        button.addEventListener("click", () => {{
          const requestedMode = normalizeStoryWorkspaceMode(button.dataset.storyWorkspaceMode || "");
          if (requestedMode) {{
            applyStoryWorkspaceMode(requestedMode, {{ persist: true, syncUrl: true }});
          }}
          const section = String(button.dataset.emptyJump || "").trim();
          if (section) {{
            jumpToSection(section);
          }}
        }});
      }});
      root.querySelectorAll("[data-empty-focus]").forEach((button) => {{
        button.addEventListener("click", () => {{
          const focus = String(button.dataset.emptyFocus || "").trim();
          const field = String(button.dataset.emptyField || "").trim();
          if (focus === "mission") {{
            focusCreateWatchDeck(field || "name");
          }} else if (focus === "story") {{
            focusStoryDeck(field || "title");
          }} else if (focus === "route") {{
            focusRouteDeck(field || "name");
          }}
        }});
      }});
      root.querySelectorAll("[data-empty-reset]").forEach((button) => {{
        button.addEventListener("click", () => {{
          const target = String(button.dataset.emptyReset || "").trim();
          if (target === "mission") {{
            const wasEditing = Boolean(String(state.createWatchEditingId || "").trim());
            state.createWatchAdvancedOpen = null;
            setCreateWatchDraft(defaultCreateWatchDraft(), "", "");
            focusCreateWatchDeck("name");
            showToast(
              wasEditing
                ? copy("Mission edit cancelled", "已取消任务编辑")
                : copy("Mission deck draft cleared", "已清空任务草稿"),
              "success",
            );
          }} else if (target === "route") {{
            const wasEditing = Boolean(normalizeRouteName(state.routeEditingId));
            state.routeAdvancedOpen = null;
            setRouteDraft(defaultRouteDraft(), "");
            focusRouteDeck("name");
            showToast(
              wasEditing
                ? copy("Route edit cancelled", "已取消路由编辑")
                : copy("Route deck draft cleared", "已清空路由草稿"),
              "success",
            );
          }}
        }});
      }});
      root.querySelectorAll("[data-empty-watch]").forEach((button) => {{
        button.addEventListener("click", async () => {{
          const identifier = String(button.dataset.emptyWatch || "").trim();
          if (!identifier) {{
            return;
          }}
          button.disabled = true;
          try {{
            await loadWatch(identifier);
          }} catch (error) {{
            reportError(error, copy("Open mission", "打开任务"));
          }} finally {{
            button.disabled = false;
          }}
        }});
      }});
      root.querySelectorAll("[data-empty-run-watch]").forEach((button) => {{
        button.addEventListener("click", async () => {{
          const identifier = String(button.dataset.emptyRunWatch || "").trim();
          if (!identifier) {{
            return;
          }}
          button.disabled = true;
          try {{
            await api(`/api/watches/${{identifier}}/run`, {{ method: "POST" }});
            await refreshBoard();
          }} catch (error) {{
            reportError(error, copy("Run mission", "执行任务"));
          }} finally {{
            button.disabled = false;
          }}
        }});
      }});
    }}

    function getGovernanceSignals() {{
      const scorecard = state.ops?.governance_scorecard;
      return scorecard && typeof scorecard.signals === "object" ? scorecard.signals : {{}};
    }}

    function getGovernanceSignal(signalId) {{
      const signal = getGovernanceSignals()[signalId];
      return signal && typeof signal === "object" ? signal : {{}};
    }}

    function getAiSurfacePrecheck(surfaceId) {{
      const payload = state.aiSurfacePrechecks?.[surfaceId];
      return payload && typeof payload === "object" ? payload : {{}};
    }}

    function getAiSurfaceProjection(surfaceId) {{
      const payload = state.aiSurfaceProjections?.[surfaceId];
      return payload && typeof payload === "object" ? payload : null;
    }}

    function summarizeAiSurfaceProjection(surfaceId, projection) {{
      if (!projection || typeof projection !== "object") {{
        return copy("No selected subject is loaded for this surface yet.", "这个 surface 还没有加载选中的对象。");
      }}
      const runtime = projection.runtime_facts && typeof projection.runtime_facts === "object" ? projection.runtime_facts : {{}};
      const output = projection.output && typeof projection.output === "object" ? projection.output : null;
      const payload = output && output.payload && typeof output.payload === "object" ? output.payload : {{}};
      if (surfaceId === "mission_suggest" && payload.summary) {{
        return String(payload.summary);
      }}
      if (surfaceId === "triage_assist") {{
        const candidateCount = payload.candidate_count ?? payload.returned_count;
        if (candidateCount !== undefined) {{
          return state.language === "zh"
            ? `重复解释候选数：${{candidateCount}}。`
            : `Duplicate explain candidates: ${{candidateCount}}.`;
        }}
      }}
      if (surfaceId === "claim_draft") {{
        if (payload.summary) {{
          return String(payload.summary);
        }}
        const claimCount = Array.isArray(payload.claim_cards) ? payload.claim_cards.length : 0;
        return state.language === "zh"
          ? `待审核主张卡：${{claimCount}} 条。`
          : `Claim cards ready for review: ${{claimCount}}.`;
      }}
      if (runtime.status) {{
        return state.language === "zh"
          ? `运行状态：${{localizeWord(runtime.status)}}。`
          : `Runtime status: ${{runtime.status}}.`;
      }}
      return copy("Governed projection loaded.", "治理投影已加载。");
    }}

    function getStoryEvidenceIds(story) {{
      return uniqueValues([
        story?.primary_item_id,
        ...(Array.isArray(story?.primary_evidence) ? story.primary_evidence.map((row) => row.item_id) : []),
        ...(Array.isArray(story?.secondary_evidence) ? story.secondary_evidence.map((row) => row.item_id) : []),
      ]);
    }}

    function getStoriesForEvidenceItem(itemId) {{
      const normalizedId = String(itemId || "").trim();
      if (!normalizedId) {{
        return [];
      }}
      return state.stories.filter((story) => getStoryEvidenceIds(story).includes(normalizedId));
    }}

    function getStoryDeliveryStatus(story) {{
      const governance = story && typeof story.governance === "object" ? story.governance : {{}};
      const deliveryRisk = governance && typeof governance.delivery_risk === "object" ? governance.delivery_risk : {{}};
      const rawStatus = String(deliveryRisk.status || "").trim().toLowerCase();
      if (rawStatus === "ready") {{
        return {{ key: "ready", label: copy("Ready", "已就绪"), tone: "ok" }};
      }}
      if (rawStatus === "blocked") {{
        return {{ key: "blocked", label: copy("Blocked", "已阻塞"), tone: "hot" }};
      }}
      if (rawStatus) {{
        return {{ key: rawStatus, label: localizeWord(rawStatus), tone: rawStatus === "watch" ? "hot" : "" }};
      }}
      return {{ key: "pending", label: copy("Not assessed", "未评估"), tone: "" }};
    }}

    function renderLifecycleContinuityCard({{ title = "", summary = "", stages = [], actions = [], tone = "ok" }} = {{}}) {{
      const stagesHtml = stages.map((stage) => `
        <div class="continuity-stage ${{escapeHtml(stage.tone || "")}}">
          <div class="continuity-stage-kicker">${{escapeHtml(stage.kicker || "")}}</div>
          <div class="continuity-stage-title">${{escapeHtml(stage.title || "")}}</div>
          <div class="continuity-stage-copy">${{escapeHtml(stage.copy || "")}}</div>
          <div class="continuity-fact-list">
            ${{(stage.facts || []).map((fact) => {{
              const hasValue = ![null, undefined].includes(fact.value) && String(fact.value).trim() !== "";
              return `
                <div class="continuity-fact">
                  <span>${{escapeHtml(fact.label || "")}}</span>
                  <strong>${{escapeHtml(hasValue ? String(fact.value).trim() : copy("n/a", "暂无"))}}</strong>
                </div>
              `;
            }}).join("")}}
          </div>
        </div>
      `).join("");
      const actionsHtml = actions.length
        ? `<div class="actions" style="margin-top:14px;">${{actions.map((action) => `
            <button
              class="${{action.primary ? "btn-primary" : "btn-secondary"}}"
              type="button"
              ${{action.section ? `data-empty-jump="${{escapeHtml(action.section)}}"` : ""}}
              ${{action.focus ? `data-empty-focus="${{escapeHtml(action.focus)}}"` : ""}}
              ${{action.field ? `data-empty-field="${{escapeHtml(action.field)}}"` : ""}}
              ${{action.watch ? `data-empty-watch="${{escapeHtml(action.watch)}}"` : ""}}
              ${{action.runWatch ? `data-empty-run-watch="${{escapeHtml(action.runWatch)}}"` : ""}}
            >${{escapeHtml(action.label || "")}}</button>
          `).join("")}}</div>`
        : "";
      return `
        <div class="card">
          <div class="card-top">
            <div>
              <div class="mono">${{copy("lifecycle continuity", "生命周期衔接")}}</div>
              <h3 class="card-title" style="margin-top:10px;">${{escapeHtml(title)}}</h3>
            </div>
            <span class="chip ${{tone}}">${{copy("cross-stage", "跨阶段")}}</span>
          </div>
          <div class="panel-sub">${{escapeHtml(summary)}}</div>
          <div class="continuity-lane" style="margin-top:14px;">${{stagesHtml}}</div>
          ${{actionsHtml}}
        </div>
      `;
    }}

    function makeSurfaceAction(label, attrs = {{}}, extra = {{}}) {{
      return {{ label, attrs, ...extra }};
    }}

    function renderCardActionControl(action, tone = "secondary") {{
      if (!action || !action.label) {{
        return "";
      }}
      const className = tone === "primary" ? "btn-primary" : tone === "danger" ? "btn-danger" : "btn-secondary";
      const attrList = Object.entries(action.attrs || {{}})
        .filter(([, value]) => value !== null && value !== undefined && value !== false && value !== "")
        .map(([key, value]) => (value === true ? key : `${{key}}="${{escapeHtml(String(value))}}"`));
      if (action.href) {{
        attrList.push(`href="${{escapeHtml(String(action.href))}}"`);
        if (action.target) {{
          attrList.push(`target="${{escapeHtml(String(action.target))}}"`);
        }}
        if (action.rel) {{
          attrList.push(`rel="${{escapeHtml(String(action.rel))}}"`);
        }}
        return `<a class="${{className}}" data-action-tone="${{tone}}" ${{attrList.join(" ")}}>${{escapeHtml(action.label)}}</a>`;
      }}
      if (action.disabled) {{
        attrList.push("disabled");
      }}
      return `<button class="${{className}}" type="button" data-action-tone="${{tone}}" ${{attrList.join(" ")}}>${{escapeHtml(action.label)}}</button>`;
    }}

    function renderCardActionHierarchy({{ primary = null, secondary = [], danger = [] }} = {{}}) {{
      const sections = [];
      if (primary) {{
        sections.push(`
          <div class="actions action-primary-row" data-card-action-primary>
            ${{renderCardActionControl(primary, "primary")}}
          </div>
        `);
      }}
      const secondaryActions = secondary.filter(Boolean);
      if (secondaryActions.length) {{
        sections.push(`
          <div class="actions action-secondary-row" data-card-action-secondary>
            ${{secondaryActions.map((action) => renderCardActionControl(action, "secondary")).join("")}}
          </div>
        `);
      }}
      const dangerActions = danger.filter(Boolean);
      if (dangerActions.length) {{
        sections.push(`
          <div class="actions action-danger-row" data-card-action-danger>
            ${{dangerActions.map((action) => renderCardActionControl(action, "danger")).join("")}}
          </div>
        `);
      }}
      if (secondaryActions.length || dangerActions.length) {{
        sections.push(`
          <details class="action-sheet" data-card-action-sheet>
            <summary class="action-sheet-toggle">${{copy("More Actions", "更多操作")}}</summary>
            <div class="action-sheet-panel">
              ${{secondaryActions.length
                ? `<div class="actions action-secondary-row" data-card-action-sheet-secondary>
                    ${{secondaryActions.map((action) => renderCardActionControl(action, "secondary")).join("")}}
                  </div>`
                : ""}}
              ${{dangerActions.length
                ? `<div class="actions action-danger-row" data-card-action-sheet-danger>
                    ${{dangerActions.map((action) => renderCardActionControl(action, "danger")).join("")}}
                  </div>`
                : ""}}
            </div>
          </details>
        `);
      }}
      return sections.length ? `<div class="action-hierarchy">${{sections.join("")}}</div>` : "";
    }}

    function isHighRiskTriageItem(item) {{
      return Number(item?.score || 0) >= 80 || Number(item?.confidence || 0) >= 0.9;
    }}

    function getMissionCardActionHierarchy(watch) {{
      const enabled = Boolean(watch?.enabled);
      const lastStatus = String(watch?.last_run_status || "").trim().toLowerCase();
      const neverRun = !String(watch?.last_run_at || "").trim();
      const due = Boolean(watch?.is_due);
      const secondary = [];
      const danger = [];
      if (!watch || !watch.id) {{
        return {{ primary: null, secondary, danger }};
      }}
      const openCockpit = makeSurfaceAction(copy("Open Cockpit", "打开驾驶舱"), {{ "data-watch-open": watch.id }});
      const editMission = makeSurfaceAction(copy("Edit Mission", "编辑任务"), {{ "data-edit-watch": watch.id }});
      const runMission = makeSurfaceAction(copy("Run Mission", "执行任务"), {{ "data-run-watch": watch.id }});
      const retryMission = makeSurfaceAction(copy("Retry Mission", "重试任务"), {{ "data-run-watch": watch.id }});
      const enableMission = makeSurfaceAction(copy("Enable", "启用"), {{
        "data-watch-toggle": watch.id,
        "data-watch-enabled": "0",
      }});
      const disableMission = makeSurfaceAction(copy("Disable", "停用"), {{
        "data-watch-toggle": watch.id,
        "data-watch-enabled": "1",
      }});
      const deleteMission = makeSurfaceAction(copy("Delete", "删除"), {{ "data-delete-watch": watch.id }});
      if (!enabled) {{
        return {{
          primary: enableMission,
          secondary: [openCockpit, editMission],
          danger: [deleteMission],
        }};
      }}
      danger.push(disableMission, deleteMission);
      if (lastStatus === "error") {{
        secondary.push(openCockpit, editMission);
        return {{ primary: retryMission, secondary, danger }};
      }}
      if (due || neverRun) {{
        secondary.push(openCockpit, editMission);
        return {{ primary: runMission, secondary, danger }};
      }}
      secondary.push(runMission, editMission);
      return {{ primary: openCockpit, secondary, danger }};
    }}

    function getTriageCardActionHierarchy(item, linkedStories = []) {{
      const reviewState = String(item?.review_state || "new").trim().toLowerCase() || "new";
      const hasLinkedStory = Array.isArray(linkedStories) && linkedStories.length > 0;
      const isOpenState = reviewState === "new" || reviewState === "triaged";
      const openStoryWorkspace = makeSurfaceAction(copy("Open Story Workspace", "打开故事工作台"), {{
        "data-empty-jump": "section-story",
        "data-story-workspace-mode": "editor",
      }});
      const createStory = makeSurfaceAction(copy("Create Story", "生成故事"), {{ "data-triage-story": item.id }});
      const explainDup = makeSurfaceAction(copy("Explain Dup", "查看重复解释"), {{ "data-triage-explain": item.id }});
      const verifyItem = makeSurfaceAction(copy("Verify", "核验"), {{
        "data-triage-state": "verified",
        "data-triage-id": item.id,
      }});
      const escalateItem = makeSurfaceAction(copy("Escalate", "升级"), {{
        "data-triage-state": "escalated",
        "data-triage-id": item.id,
      }});
      const ignoreItem = makeSurfaceAction(copy("Ignore", "忽略"), {{
        "data-triage-state": "ignored",
        "data-triage-id": item.id,
      }});
      const deleteItem = makeSurfaceAction(copy("Delete", "删除"), {{ "data-triage-delete": item.id }});
      const storyAction = hasLinkedStory ? openStoryWorkspace : createStory;
      const danger = reviewState === "ignored" ? [deleteItem] : [ignoreItem, deleteItem];
      if (isOpenState && isHighRiskTriageItem(item)) {{
        return {{
          primary: escalateItem,
          secondary: [verifyItem, storyAction],
          danger,
        }};
      }}
      if (isOpenState) {{
        return {{
          primary: verifyItem,
          secondary: [escalateItem, storyAction],
          danger,
        }};
      }}
      if (reviewState === "verified" || reviewState === "escalated") {{
        return {{
          primary: storyAction,
          secondary: [explainDup, reviewState === "escalated" ? verifyItem : null].filter(Boolean).slice(0, 2),
          danger,
        }};
      }}
      return {{
        primary: hasLinkedStory ? openStoryWorkspace : explainDup,
        secondary: [storyAction, verifyItem],
        danger,
      }};
    }}

    function getTriageWorkbenchActionHierarchy(item, linkedStories = []) {{
      const base = getTriageCardActionHierarchy(item, linkedStories);
      const hasLinkedStory = Array.isArray(linkedStories) && linkedStories.length > 0;
      const primary = hasLinkedStory
        ? makeSurfaceAction(copy("Open Story Workspace", "打开故事工作台"), {{
          "data-empty-jump": "section-story",
          "data-story-workspace-mode": "editor",
        }})
        : makeSurfaceAction(copy("Create Story", "生成故事"), {{ "data-triage-story": item.id }});
      const explainDup = makeSurfaceAction(copy("Explain Dup", "查看重复解释"), {{ "data-triage-explain": item.id }});
      const secondary = [];
      if (base.primary && base.primary.label !== primary.label) {{
        secondary.push(base.primary);
      }}
      secondary.push(explainDup);
      const reviewState = String(item?.review_state || "new").trim().toLowerCase() || "new";
      const danger = reviewState === "ignored"
        ? [makeSurfaceAction(copy("Delete", "删除"), {{ "data-triage-delete": item.id }})]
        : [
            makeSurfaceAction(copy("Ignore", "忽略"), {{
              "data-triage-state": "ignored",
              "data-triage-id": item.id,
            }}),
            makeSurfaceAction(copy("Delete", "删除"), {{ "data-triage-delete": item.id }}),
          ];
      return {{
        primary,
        secondary: secondary.filter(Boolean).slice(0, 2),
        danger,
      }};
    }}

    function getStoryCardActionHierarchy(story) {{
      const archived = String(story?.status || "active").trim().toLowerCase() === "archived";
      return {{
        primary: makeSurfaceAction(copy("Open Story", "打开故事"), {{
          "data-story-open": story.id,
          "data-story-open-mode": state.storyWorkspaceMode,
        }}),
        secondary: [
          makeSurfaceAction(
            archived ? copy("Restore", "恢复") : copy("Archive", "归档"),
            {{
              "data-story-quick-status": story.id,
              "data-story-next-status": archived ? "active" : "archived",
            }},
          ),
          makeSurfaceAction(copy("Preview MD", "预览 MD"), {{ "data-story-preview": story.id }}),
        ],
        danger: [],
      }};
    }}

    function getRouteCardActionHierarchy(route, health = null, usageCount = 0) {{
      const routeName = String(route?.name || health?.name || "").trim();
      if (!routeName) {{
        return {{ primary: null, secondary: [], danger: [] }};
      }}
      const healthStatus = String(health?.status || route?.status || "idle").trim().toLowerCase() || "idle";
      const unhealthy = healthStatus && !["healthy", "idle"].includes(healthStatus);
      const editRoute = makeSurfaceAction(
        unhealthy ? copy("Inspect Route", "检查路由") : copy("Edit Route", "编辑路由"),
        {{ "data-route-edit": routeName }},
      );
      const attachRoute = makeSurfaceAction(copy("Attach To Mission", "绑定到任务"), {{ "data-route-attach": routeName }});
      const deleteRoute = makeSurfaceAction(copy("Delete", "删除"), {{ "data-route-delete": routeName }});
      if (unhealthy) {{
        return {{
          primary: editRoute,
          secondary: [attachRoute],
          danger: [deleteRoute],
        }};
      }}
      if (!usageCount) {{
        return {{
          primary: attachRoute,
          secondary: [editRoute],
          danger: [deleteRoute],
        }};
      }}
      return {{
        primary: editRoute,
        secondary: [attachRoute],
        danger: [deleteRoute],
      }};
    }}

    function renderOverview() {{
      const metrics = state.overview || {{}};
      if (state.loading.board && !state.overview) {{
        $("overview-metrics").innerHTML = [metricCard(copy("Loading", "加载中"), "..."), metricCard(copy("Loading", "加载中"), "..."), metricCard(copy("Loading", "加载中"), "...")].join("");
        renderTopbarContext();
        return;
      }}
      $("overview-metrics").innerHTML = [
        metricCard(copy("Enabled Missions", "已启用任务"), metrics.enabled_watches ?? 0),
        metricCard(copy("Due Now", "当前到点"), metrics.due_watches ?? 0, "hot"),
        metricCard(copy("Acted On Queue", "已处理队列"), metrics.triage_acted_on_count ?? 0),
        metricCard(copy("Stories", "故事"), metrics.story_count ?? 0),
        metricCard(copy("Ready Stories", "待交付故事"), metrics.story_ready_count ?? 0),
        metricCard(copy("Alert Routes", "告警路由"), metrics.route_count ?? 0),
        metricCard(copy("Open Queue", "待分诊队列"), metrics.triage_open_count ?? 0),
        metricCard(copy("Daemon State", "守护进程状态"), localizeWord(String(metrics.daemon_state || "idle")).toUpperCase()),
      ].join("");
      renderTopbarContext();
    }}

    function renderWatches() {{
      const root = $("watch-list");
      if (state.loading.board && !state.watches.length) {{
        root.innerHTML = [skeletonCard(4), skeletonCard(4), skeletonCard(4)].join("");
        renderTopbarContext();
        return;
      }}
      if (!state.watches.length) {{
        root.innerHTML = `
          ${{renderLifecycleGuideCard({{
            title: copy("Start the lifecycle with one mission draft", "先用一个任务草稿启动生命周期"),
            summary: copy(
              "Name and Query are enough to create the first watch. Once it runs, the browser can guide you through triage, story promotion, and delivery setup without leaving this shell.",
              "只用名称和查询词就能先把第一个任务建起来。任务执行后，浏览器会继续把你带到分诊、故事沉淀和交付设置，不需要离开当前界面。"
            ),
            steps: [
              {{
                title: copy("Create Watch", "创建任务"),
                copy: copy("Use Mission Intake to create or clone the first watch.", "先在任务创建区新建或复制第一个任务。"),
              }},
              {{
                title: copy("Run From Board", "从列表执行"),
                copy: copy("Mission Board turns the draft into real evidence collection.", "任务列表会把草稿真正推进到实时证据采集。"),
              }},
              {{
                title: copy("Review In Triage", "进入分诊审阅"),
                copy: copy("Inbox items arrive in Triage after the first successful run.", "第一次成功执行后，收件箱条目会进入分诊队列。"),
              }},
              {{
                title: copy("Promote And Route", "提升并接入路由"),
                copy: copy("Stories and named routes matter once signal is worth downstream action.", "当信号值得触发下游动作时，再去沉淀故事和接入命名路由。"),
              }},
            ],
            actions: [
              {{ label: copy("Open Mission Draft", "打开任务草稿"), focus: "mission", field: "name", primary: true }},
              {{ label: copy("Open Route Manager", "打开路由管理"), focus: "route", field: "name" }},
            ],
          }})}}
          <div class="empty">${{copy("No watch mission configured yet.", "当前还没有配置监测任务。")}}</div>`;
        wireLifecycleGuideActions(root);
        syncWatchUrlState();
        flushWatchUrlFocus();
        renderTopbarContext();
        return;
      }}
      const searchValue = String(state.watchSearch || "");
      const searchQuery = searchValue.trim().toLowerCase();
      const defaultWatchId = state.watches[0] ? state.watches[0].id : "";
      const filteredWatches = state.watches.filter((watch) => {{
        if (!searchQuery) {{
          return true;
        }}
        const haystack = [
          watch.id,
          watch.name,
          watch.query,
          ...(Array.isArray(watch.platforms) ? watch.platforms : []),
          ...(Array.isArray(watch.sites) ? watch.sites : []),
          watch.schedule,
          watch.schedule_label,
        ].join(" ").toLowerCase();
        return haystack.includes(searchQuery);
      }});
      const searchToolbar = `
        <div class="card section-toolbox">
          <div class="section-toolbox-head">
            <div>
              <div class="mono">${{copy("mission search", "任务搜索")}}</div>
              <div class="panel-sub">${{copy("Search by name, query, id, platform, or site to narrow the board before acting.", "可按名称、查询词、任务 ID、平台或站点快速缩小任务列表。")}}</div>
            </div>
            <div class="section-toolbox-meta">
              <span class="chip">${{copy("shown", "显示")}}=${{filteredWatches.length}}</span>
              <span class="chip">${{copy("total", "总数")}}=${{state.watches.length}}</span>
            </div>
          </div>
          <div class="search-shell">
            <input type="search" value="${{escapeHtml(searchValue)}}" data-watch-search placeholder="${{copy("Search missions", "搜索任务")}}">
            <button class="btn-secondary" type="button" data-watch-search-clear ${{searchValue.trim() ? "" : "disabled"}}>${{copy("Clear", "清空")}}</button>
          </div>
        </div>
      `;
      if (!filteredWatches.length) {{
        root.innerHTML = `${{searchToolbar}}<div class="empty">${{copy("No mission matched the current search.", "没有任务匹配当前搜索。")}}</div>`;
        root.querySelector("[data-watch-search]")?.addEventListener("input", (event) => {{
          state.watchSearch = event.target.value;
          renderWatches();
        }});
        root.querySelector("[data-watch-search-clear]")?.addEventListener("click", () => {{
          state.watchSearch = "";
          renderWatches();
        }});
        syncWatchUrlState({{ defaultWatchId }});
        flushWatchUrlFocus();
        return;
      }}
      root.innerHTML = `${{searchToolbar}}${{filteredWatches.map((watch) => {{
        const platforms = (watch.platforms || []).join(", ") || copy("any", "任意");
        const sites = (watch.sites || []).join(", ") || "-";
        const stateChip = watch.enabled ? "ok" : "";
        const dueChip = watch.is_due ? "hot" : "";
        const selected = watch.id === state.selectedWatchId ? "selected" : "";
        const actionHierarchy = getMissionCardActionHierarchy(watch);
        return `
          <div class="card selectable ${{selected}}">
            <div class="card-top">
              <div>
                <h3 class="card-title">${{watch.name}}</h3>
                <div class="meta">
                  <span>${{watch.id}}</span>
                  <span>${{copy("schedule", "频率")}}=${{watch.schedule_label || watch.schedule || copy("manual", "手动")}}</span>
                  <span>${{copy("platforms", "平台")}}=${{platforms}}</span>
                  <span>${{copy("sites", "站点")}}=${{sites}}</span>
                </div>
              </div>
              <div style="display:grid; gap:6px; justify-items:end;">
                <span class="chip ${{stateChip}}">${{watch.enabled ? copy("enabled", "已启用") : copy("disabled", "已停用")}}</span>
                <span class="chip ${{dueChip}}">${{watch.is_due ? copy("due", "待执行") : copy("waiting", "等待")}}</span>
              </div>
            </div>
            <div class="meta">
              <span>${{copy("alert_rules", "告警规则")}}=${{watch.alert_rule_count || 0}}</span>
              <span>${{copy("last_run", "上次执行")}}=${{watch.last_run_at || "-"}}</span>
              <span>${{copy("status", "状态")}}=${{localizeWord(watch.last_run_status || "-")}}</span>
              <span>${{copy("next", "下次")}}=${{watch.next_run_at || "-"}}</span>
            </div>
            ${{renderCardActionHierarchy(actionHierarchy)}}
          </div>`;
      }}).join("")}}`;

      root.querySelector("[data-watch-search]")?.addEventListener("input", (event) => {{
        state.watchSearch = event.target.value;
        renderWatches();
      }});
      root.querySelector("[data-watch-search-clear]")?.addEventListener("click", () => {{
        state.watchSearch = "";
        renderWatches();
      }});

      root.querySelectorAll("[data-watch-open]").forEach((button) => {{
        button.addEventListener("click", async () => {{
          button.disabled = true;
          try {{
            await loadWatch(button.dataset.watchOpen);
          }} catch (error) {{
            reportError(error, copy("Open mission", "打开任务"));
          }} finally {{
            button.disabled = false;
          }}
        }});
      }});

      root.querySelectorAll("[data-edit-watch]").forEach((button) => {{
        button.addEventListener("click", async () => {{
          button.disabled = true;
          try {{
            await editMissionInCreateWatch(button.dataset.editWatch);
          }} catch (error) {{
            reportError(error, copy("Edit mission", "编辑任务"));
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
            reportError(error, copy("Run mission", "执行任务"));
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
      syncWatchUrlState({{ defaultWatchId }});
      flushWatchUrlFocus();
      renderTopbarContext();
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
      setContextRouteFromWatch();
      renderWatches();
      renderWatchDetail();
    }}

    function renderWatchDetail() {{
      const root = $("watch-detail");
      renderFormSuggestionLists();
      const selected = state.selectedWatchId;
      if (state.loading.watchDetail && selected) {{
        root.innerHTML = [skeletonCard(4), skeletonCard(4), skeletonCard(4)].join("");
        renderTopbarContext();
        return;
      }}
      const watch = state.watchDetails[selected] || state.watches.find((candidate) => candidate.id === selected);
      if (!watch) {{
        const firstWatch = state.watches[0] || null;
        root.innerHTML = `
          ${{renderLifecycleGuideCard({{
            title: copy("Open one mission to move from draft into live evidence", "打开一个任务，把草稿推进到实时证据"),
            summary: copy(
              "Cockpit is the handoff point between mission setup and downstream review. Open a mission here to run it, inspect recent output, and decide whether triage or delivery needs attention next.",
              "任务详情是“创建任务”和“进入审阅”之间的交接点。先在这里打开一个任务，执行它、查看近期输出，再决定下一步是进入分诊还是补充交付设置。"
            ),
            steps: [
              {{
                title: copy("Open Cockpit", "打开任务详情"),
                copy: copy("Pick a mission from the board to inspect its current operating lane.", "先从任务列表里选中一个任务，查看它当前的运行状态。"),
              }},
              {{
                title: copy("Run Mission", "执行任务"),
                copy: copy("One run is enough to populate results, timeline, and future triage work.", "先执行一次任务，就能填充结果流、时间线和后续分诊工作。"),
              }},
              {{
                title: copy("Inspect Output", "检查输出"),
                copy: copy("Review result filters, retry guidance, and alert rules before you leave the cockpit.", "离开任务详情前，先看结果筛选、重试建议和告警规则。"),
              }},
              {{
                title: copy("Follow The Lifecycle", "沿生命周期推进"),
                copy: copy("From here, the next hop is usually Triage, then Stories, then route-backed delivery.", "从这里出发，通常下一站是分诊，然后是故事，最后才是路由交付。"),
              }},
            ],
            actions: [
              firstWatch
                ? {{ label: copy("Open First Mission", "打开第一个任务"), watch: firstWatch.id, primary: true }}
                : {{ label: copy("Open Mission Board", "打开任务列表"), section: "section-board", primary: true }},
              {{ label: copy("Focus Mission Draft", "聚焦任务草稿"), focus: "mission", field: "name" }},
            ],
          }})}}
          <div class="empty">${{copy("Select one mission from the board to inspect schedule, run history, and alert output.", "从看板中选择一个任务，以查看调度、执行历史和告警输出。")}}</div>`;
        wireLifecycleGuideActions(root);
        renderTopbarContext();
        return;
      }}
      const recentRuns = Array.isArray(watch.runs) ? watch.runs : [];
      const recentResults = Array.isArray(watch.recent_results) ? watch.recent_results : [];
      const recentAlerts = Array.isArray(watch.recent_alerts) ? watch.recent_alerts : [];
      const lastFailure = watch.last_failure || null;
      const retryAdvice = watch.retry_advice || null;
      const runStats = watch.run_stats || {{}};
      const resultStats = watch.result_stats || {{}};
      const visibleResultCount = Number(resultStats.visible_result_count);
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
                    <span>${{copy("trigger", "触发方式")}}=${{localizeWord(run.trigger || "manual")}}</span>
                    <span>${{copy("items", "条目")}}=${{run.item_count || 0}}</span>
                  </div>
                </div>
                <span class="chip ${{run.status === "success" ? "ok" : "hot"}}">${{localizeWord(run.status || "unknown")}}</span>
              </div>
              <div class="meta">
                <span>${{copy("started", "开始")}}=${{run.started_at || "-"}}</span>
                <span>${{copy("finished", "结束")}}=${{run.finished_at || "-"}}</span>
              </div>
              <div class="panel-sub">${{run.error || copy("No recorded error.", "没有记录到错误。")}}</div>
            </div>
          `).join("")
        : `
            <div class="card">
              <div class="mono">${{copy("no run yet", "尚未执行")}}</div>
              <div class="panel-sub">${{copy("Run this mission once to seed the triage queue, story workspace, and alert history with real evidence.", "先执行一次这个任务，分诊队列、故事工作台和告警历史才会开始出现真实证据。")}}</div>
              <div class="actions" style="margin-top:12px;">
                <button class="btn-primary" type="button" data-empty-run-watch="${{escapeHtml(watch.id)}}">${{copy("Run Mission Now", "立即执行任务")}}</button>
                <button class="btn-secondary" type="button" data-empty-jump="section-triage">${{copy("Open Triage", "打开分诊")}}</button>
              </div>
            </div>
          `;
      const alertsBlock = recentAlerts.length
        ? recentAlerts.map((alert) => `
            <div class="card">
              <div class="card-top">
                <div>
                  <h3 class="card-title">${{alert.rule_name}}</h3>
                  <div class="meta">
                    <span>${{alert.created_at || "-"}}</span>
                    <span>${{copy("items", "条目")}}=${{(alert.item_ids || []).length}}</span>
                  </div>
                </div>
                <span class="chip ${{alert.extra && alert.extra.delivery_errors ? "hot" : "ok"}}">${{(alert.delivered_channels || ["json"]).join(",")}}</span>
              </div>
              <div class="panel-sub">${{alert.summary || copy("No alert summary captured.", "没有记录到告警摘要。")}}</div>
            </div>
          `).join("")
        : `
            <div class="card">
              <div class="mono">${{copy("delivery is still quiet", "交付尚未启动")}}</div>
              <div class="panel-sub">${{copy("No recent alert event is recorded for this mission. Add or tune alert rules here, then attach a named route once the mission should notify downstream.", "这个任务近期还没有告警事件。先在这里补充或调整告警规则，等任务需要通知下游时，再绑定命名路由。")}}</div>
              <div class="actions" style="margin-top:12px;">
                <button class="btn-secondary" type="button" data-empty-focus="route" data-empty-field="name">${{copy("Open Route Manager", "打开路由管理")}}</button>
                <button class="btn-secondary" type="button" data-empty-jump="section-ops">${{copy("Open Delivery Surfaces", "打开交付视图")}}</button>
              </div>
            </div>
          `;
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
        {{ key: "state", label: copy("state", "状态"), options: stateOptions }},
        {{ key: "source", label: copy("source", "来源"), options: sourceOptions }},
        {{ key: "domain", label: copy("domain", "域名"), options: domainOptions }},
      ];
      const filterWindowCount = Number(resultFilters.window_count || recentResults.length || 0);
      const filterBlock = filterGroups.map((group) => `
          <div class="stack">
            <div class="panel-sub">${{group.label}}</div>
            <div class="chip-row">
              <button class="chip-btn ${{activeFilters[group.key] === "all" ? "active" : ""}}" type="button" data-filter-group="${{group.key}}" data-filter-value="all">${{copy("all", "全部")}} (${{filterWindowCount}})</button>
              ${{group.options.map((option) => `
                <button class="chip-btn ${{activeFilters[group.key] === option.key ? "active" : ""}}" type="button" data-filter-group="${{group.key}}" data-filter-value="${{escapeHtml(option.key)}}">${{escapeHtml(localizeWord(option.label))}} (${{option.count || 0}})</button>
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
                    <span>${{copy("score", "分数")}}=${{item.score || 0}}</span>
                    <span>${{copy("confidence", "置信度")}}=${{Number(item.confidence || 0).toFixed(2)}}</span>
                    <span>${{item.source_name || item.source_type || "-"}}</span>
                  </div>
                </div>
                <span class="chip">${{localizeWord(item.review_state || "new")}}</span>
              </div>
              <div class="panel-sub">${{item.url || "-"}}</div>
            </div>
          `).join("")
        : `<div class="empty">${{copy("No persisted result matched the active filter chips in the current mission window.", "当前任务窗口内没有结果匹配所选筛选条件。")}}</div>`;
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
        : `<div class="empty">${{copy("No mission timeline event captured yet.", "当前还没有记录到任务时间线事件。")}}</div>`;
      const retryCollectors = retryAdvice && Array.isArray(retryAdvice.suspected_collectors)
        ? retryAdvice.suspected_collectors
        : [];
      const retryNotes = retryAdvice && Array.isArray(retryAdvice.notes) ? retryAdvice.notes : [];
      const failureBlock = lastFailure
        ? `
            <div class="card">
              <div class="card-top">
                <div>
                  <h3 class="card-title">${{copy("latest failure", "最近失败")}}</h3>
                  <div class="meta">
                    <span>${{lastFailure.id || "-"}}</span>
                    <span>${{copy("status", "状态")}}=${{localizeWord(lastFailure.status || "error")}}</span>
                    <span>${{copy("trigger", "触发方式")}}=${{localizeWord(lastFailure.trigger || "manual")}}</span>
                    <span>${{copy("finished", "结束")}}=${{lastFailure.finished_at || "-"}}</span>
                  </div>
                </div>
                <span class="chip hot">${{retryAdvice && retryAdvice.failure_class ? retryAdvice.failure_class : localizeWord("error")}}</span>
              </div>
              <div class="panel-sub">${{lastFailure.error || copy("No failure message captured.", "没有记录到失败信息。")}}</div>
            </div>
          `
        : "";
      const retryAdviceBlock = retryAdvice
        ? `
            <div class="card">
              <div class="mono">${{copy("retry advice", "重试建议")}}</div>
              <div class="meta">
                <span>${{copy("retry", "重试")}}=${{retryAdvice.retry_command || "-"}}</span>
                <span>${{copy("daemon", "守护进程")}}=${{retryAdvice.daemon_retry_command || "-"}}</span>
              </div>
              <div class="panel-sub">${{retryAdvice.summary || copy("No retry guidance recorded.", "没有记录到重试建议。")}}</div>
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
      const triageSignal = getGovernanceSignal("triage_throughput");
      const storySignal = getGovernanceSignal("story_conversion");
      const routeSummary = state.ops?.route_summary || {{}};
      const missionContinuityBlock = renderLifecycleContinuityCard({{
        title: copy("Mission Continuity", "任务连续性"),
        summary: copy(
          "Mission output, review backlog, and downstream delivery facts stay visible together before you leave the cockpit.",
          "在离开任务详情之前，任务输出、审阅积压和下游交付事实会同时保持可见。"
        ),
        stages: [
          {{
            kicker: copy("Current", "当前"),
            title: copy("Mission Output", "任务输出"),
            copy: copy(
              "Runs, result filters, and retry context stay attached to the active mission instead of splitting into separate hops.",
              "执行记录、结果筛选和重试上下文会继续附着在当前任务上，而不是被拆成多个跳转。"
            ),
            tone: Number.isFinite(visibleResultCount) && visibleResultCount > 0 ? "ok" : "",
            facts: [
              {{ label: copy("Visible results", "可见结果"), value: String(Number.isFinite(visibleResultCount) ? visibleResultCount : (resultStats.stored_result_count || 0)) }},
              {{ label: copy("Filtered out", "已过滤"), value: String(resultStats.filtered_result_count || 0) }},
              {{ label: copy("Last run", "最近执行"), value: formatCompactDateTime(watch.last_run_at || recentRuns[0]?.finished_at || "") }},
            ],
          }},
          {{
            kicker: copy("Review", "审阅"),
            title: copy("Review Lane", "审阅工作线"),
            copy: copy(
              "Queue load and story carry-over stay visible here so you can decide whether this mission needs review attention next.",
              "这里直接保留队列压力和故事承接情况，方便判断这个任务下一步是否需要进入审阅。"
            ),
            tone: (state.overview?.triage_open_count ?? triageSignal.open_items ?? 0) > 0 ? "hot" : "ok",
            facts: [
              {{ label: copy("Open queue", "开放队列"), value: String(state.overview?.triage_open_count ?? triageSignal.open_items ?? 0) }},
              {{ label: copy("Acted on", "已处理"), value: String(state.overview?.triage_acted_on_count ?? triageSignal.acted_on_items ?? 0) }},
              {{ label: copy("Stories", "故事"), value: String(state.overview?.story_count ?? storySignal.story_count ?? state.stories.length) }},
            ],
          }},
          {{
            kicker: copy("Delivery", "交付"),
            title: copy("Delivery Lane", "交付工作线"),
            copy: copy(
              "Alert events, ready stories, and healthy routes stay one glance away from the same mission.",
              "告警事件、待交付故事和健康路由会与同一任务保持一眼可见。"
            ),
            tone: (deliveryStats.recent_alert_count || 0) > 0 || (routeSummary.healthy || 0) > 0 ? "ok" : "",
            facts: [
              {{ label: copy("Recent alerts", "最近告警"), value: String(deliveryStats.recent_alert_count || 0) }},
              {{ label: copy("Ready stories", "待交付故事"), value: String(state.overview?.story_ready_count ?? storySignal.ready_story_count ?? 0) }},
              {{ label: copy("Healthy routes", "健康路由"), value: String(routeSummary.healthy || 0) }},
            ],
          }},
        ],
        actions: [
          {{ label: copy("Open Triage", "打开分诊"), section: "section-triage", primary: true }},
          {{ label: copy("Open Stories", "打开故事"), section: "section-story" }},
          {{ label: copy("Open Delivery", "打开交付"), section: "section-ops" }},
        ],
      }});

      root.innerHTML = `
        <div class="card">
          <div class="card-top">
            <div>
                <h3 class="card-title">${{watch.name}}</h3>
                <div class="meta">
                  <span>${{watch.id}}</span>
                  <span>${{copy("schedule", "频率")}}=${{watch.schedule_label || watch.schedule || copy("manual", "手动")}}</span>
                  <span>${{copy("next", "下次")}}=${{watch.next_run_at || "-"}}</span>
                  <span>${{copy("query", "查询")}}=${{watch.query || "-"}}</span>
                </div>
              </div>
            <span class="chip ${{watch.enabled ? "ok" : "hot"}}">${{watch.enabled ? copy("enabled", "已启用") : copy("disabled", "已停用")}}</span>
          </div>
          <div class="meta">
            <span>${{copy("due", "到点")}}=${{localizeBoolean(watch.is_due)}}</span>
            <span>${{copy("alert_rules", "告警规则")}}=${{watch.alert_rule_count || 0}}</span>
            <span>${{copy("runs", "执行")}}=${{runStats.total || 0}}</span>
            <span>${{copy("success", "成功")}}=${{runStats.success || 0}}</span>
            <span>${{copy("errors", "错误")}}=${{runStats.error || 0}}</span>
            <span>${{copy("results", "结果")}}=${{Number.isFinite(visibleResultCount) ? visibleResultCount : (resultStats.stored_result_count || 0)}}</span>
            <span>${{copy("alerts", "告警")}}=${{deliveryStats.recent_alert_count || 0}}</span>
          </div>
          <div class="actions" style="margin-top:12px;">
            <button class="btn-secondary" type="button" data-watch-edit="${{watch.id}}">${{copy("Edit Mission", "编辑任务")}}</button>
            <button class="btn-secondary" type="button" data-empty-run-watch="${{escapeHtml(watch.id)}}">${{copy("Run Mission", "执行任务")}}</button>
            <button class="btn-secondary" type="button" data-empty-jump="section-triage">${{copy("Open Triage", "打开分诊")}}</button>
            <button class="btn-secondary" type="button" data-empty-focus="route" data-empty-field="name">${{copy("Focus Route Manager", "聚焦路由管理")}}</button>
          </div>
          <div class="panel-sub">${{watch.last_run_error || copy("Mission history and recent delivery outcomes are visible below.", "下方可查看任务历史和最近交付结果。")}}</div>
        </div>
        ${{missionContinuityBlock}}
        ${{failureBlock}}
        ${{retryAdviceBlock}}
        <div class="card">
          <div class="mono">${{copy("timeline strip", "时间线")}}</div>
          <div class="panel-sub">${{copy("Recent run, result, and alert events are merged into one server-backed mission timeline.", "最近的运行、结果和告警事件会合并成一条服务端驱动的任务时间线。")}}</div>
          <div style="margin-top:12px;">
            ${{timelineBlock}}
          </div>
        </div>
        <div class="story-columns">
          <div class="stack">
            <div class="mono">${{copy("recent runs", "最近执行")}}</div>
            ${{runsBlock}}
          </div>
          <div class="stack">
            <div class="mono">${{copy("recent alerts", "最近告警")}}</div>
            ${{alertsBlock}}
          </div>
        </div>
        <div class="stack">
          <div class="mono">${{copy("result stream", "结果流")}}</div>
          <div class="card">
            <div class="mono">${{copy("filter chips", "筛选标签")}}</div>
            <div class="panel-sub">${{copy("Filter the current persisted result window by review state, source, or domain without leaving the cockpit.", "在不离开驾驶舱的情况下，按审核状态、来源或域名筛选当前结果窗口。")}}</div>
            <div class="stack" style="margin-top:12px;">
              ${{filterBlock}}
            </div>
          </div>
          ${{resultsBlock}}
        </div>
        <div class="card">
          <div class="card-top">
            <div>
              <div class="mono">${{copy("alert rule editor", "告警规则编辑器")}}</div>
              <div class="panel-sub">${{copy("Edit multiple console threshold rules for this mission, then replace the saved rule set in one write.", "可以在这里为任务编辑多条阈值规则，并一次性替换已保存的规则集。")}}</div>
            </div>
            <span class="chip">${{(watch.alert_rules || []).length}} ${{copy("rule(s)", "条规则")}}</span>
          </div>
          <form id="watch-alert-form" data-watch-id="${{watch.id}}">
            <div class="stack" id="watch-alert-rules">
              ${{
                ((watch.alert_rules || []).length ? watch.alert_rules : [{{}}]).map((rule, index) => `
                  <div class="card" data-alert-rule-card="${{index}}">
                    <div class="card-top">
                      <div>
                        <div class="mono">${{copy("rule", "规则")}} ${{index + 1}}</div>
                        <div class="panel-sub">${{copy("Current name", "当前名称")}}: ${{rule.name || "console-threshold"}}</div>
                      </div>
                      <button class="btn-secondary" type="button" data-remove-alert-rule="${{index}}">${{copy("Remove", "移除")}}</button>
                    </div>
                    <div class="field-grid">
                      <label>${{copy("Alert Route", "告警路由")}}<input name="route" list="route-options-list" placeholder="ops-webhook" value="${{(rule.routes || [])[0] || ""}}"></label>
                      <label>${{copy("Alert Keyword", "告警关键词")}}<input name="keyword" list="keyword-options-list" placeholder="launch" value="${{(rule.keyword_any || [])[0] || ""}}"></label>
                    </div>
                    <div class="field-grid">
                      <label>${{copy("Alert Domain", "告警域名")}}<input name="domain" list="domain-options-list" placeholder="openai.com" value="${{(rule.domains || [])[0] || ""}}"></label>
                      <label>${{copy("Min Score", "最低分数")}}<input name="min_score" list="score-options-list" placeholder="70" inputmode="numeric" value="${{(rule.min_score || 0) || ""}}"></label>
                    </div>
                    <div class="field-grid">
                      <label>${{copy("Min Confidence", "最低置信度")}}<input name="min_confidence" list="confidence-options-list" placeholder="0.8" inputmode="decimal" value="${{(rule.min_confidence || 0) || ""}}"></label>
                      <div class="stack">
                        <div class="panel-sub">${{copy("Channels are still pinned to json; named route delivery is configured via Alert Route.", "通道仍固定为 json；命名路由交付通过“告警路由”配置。")}}</div>
                      </div>
                    </div>
                  </div>
                `).join("")
              }}
            </div>
            <div class="toolbar">
              <button class="btn-secondary" id="watch-alert-add" type="button">${{copy("Add Alert Rule", "新增告警规则")}}</button>
              <button class="btn-primary" type="submit">${{copy("Save Alert Rules", "保存告警规则")}}</button>
              <button class="btn-secondary" id="watch-alert-clear" type="button">${{copy("Clear Alert Rules", "清空告警规则")}}</button>
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
                  <div class="mono">${{copy("rule", "规则")}} ${{nextIndex + 1}}</div>
                  <div class="panel-sub">${{copy("New console threshold rule.", "新的控制台阈值规则。")}}</div>
                </div>
                <button class="btn-secondary" type="button" data-remove-alert-rule="${{nextIndex}}">${{copy("Remove", "移除")}}</button>
              </div>
              <div class="field-grid">
                <label>${{copy("Alert Route", "告警路由")}}<input name="route" list="route-options-list" placeholder="ops-webhook"></label>
                <label>${{copy("Alert Keyword", "告警关键词")}}<input name="keyword" list="keyword-options-list" placeholder="launch"></label>
              </div>
              <div class="field-grid">
                <label>${{copy("Alert Domain", "告警域名")}}<input name="domain" list="domain-options-list" placeholder="openai.com"></label>
                <label>${{copy("Min Score", "最低分数")}}<input name="min_score" list="score-options-list" placeholder="70" inputmode="numeric"></label>
              </div>
              <div class="field-grid">
                <label>${{copy("Min Confidence", "最低置信度")}}<input name="min_confidence" list="confidence-options-list" placeholder="0.8" inputmode="decimal"></label>
                <div class="stack">
                  <div class="panel-sub">${{copy("Channels stay pinned to json; named route delivery is configured via Alert Route.", "通道仍固定为 json；命名路由交付通过“告警路由”配置。")}}</div>
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
            showToast(copy("Provide at least one route, keyword, domain, or threshold across the rule set.", "请至少提供一个路由、关键词、域名或阈值。"), "error");
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
            reportError(error, copy("Update alert rules", "更新告警规则"));
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
            reportError(error, copy("Clear alert rules", "清空告警规则"));
          }}
        }});
      }}

      root.querySelectorAll("[data-watch-edit]").forEach((button) => {{
        button.addEventListener("click", async () => {{
          button.disabled = true;
          try {{
            await editMissionInCreateWatch(String(button.dataset.watchEdit || "").trim());
          }} catch (error) {{
            reportError(error, copy("Edit mission", "编辑任务"));
          }} finally {{
            button.disabled = false;
          }}
        }});
      }});
      wireLifecycleGuideActions(root);
      renderTopbarContext();
    }}

    function renderAlerts() {{
      const root = $("alert-list");
      if (state.loading.board && !state.alerts.length) {{
        root.innerHTML = [skeletonCard(3), skeletonCard(3)].join("");
        return;
      }}
      if (!state.alerts.length) {{
        root.innerHTML = `<div class="empty">${{copy("No alert event stored.", "当前没有告警事件。")}}</div>`;
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

    async function submitRouteDeck(form) {{
      const draft = collectRouteDraft(form);
      state.routeDraft = draft;
      const editingId = normalizeRouteName(state.routeEditingId);
      let headers = null;
      try {{
        headers = parseRouteHeaders(draft.headers_json);
      }} catch (error) {{
        showToast(error.message, "error");
        focusRouteDeck("headers_json");
        return;
      }}
      if (!draft.name.trim()) {{
        showToast(copy("Provide a route name before saving.", "保存前请先填写路由名称。"), "error");
        focusRouteDeck("name");
        return;
      }}
      if (draft.channel === "webhook" && !draft.webhook_url.trim()) {{
        showToast(copy("Webhook routes need a webhook URL.", "Webhook 路由需要填写 webhook URL。"), "error");
        focusRouteDeck("webhook_url");
        return;
      }}
      if (draft.channel === "feishu" && !draft.feishu_webhook.trim()) {{
        showToast(copy("Feishu routes need a webhook URL.", "飞书路由需要填写 webhook URL。"), "error");
        focusRouteDeck("feishu_webhook");
        return;
      }}
      if (draft.channel === "telegram" && !draft.telegram_chat_id.trim()) {{
        showToast(copy("Telegram routes need a chat ID.", "Telegram 路由需要填写 chat ID。"), "error");
        focusRouteDeck("telegram_chat_id");
        return;
      }}
      if (draft.channel === "telegram" && !editingId && !draft.telegram_bot_token.trim()) {{
        showToast(copy("Telegram routes need a bot token when created.", "创建 Telegram 路由时必须填写 bot token。"), "error");
        focusRouteDeck("telegram_bot_token");
        return;
      }}
      let timeoutSeconds = null;
      if (draft.timeout_seconds.trim()) {{
        timeoutSeconds = Number(draft.timeout_seconds);
        if (!(timeoutSeconds > 0)) {{
          showToast(copy("Timeout must be greater than 0.", "超时时间必须大于 0。"), "error");
          focusRouteDeck("timeout_seconds");
          return;
        }}
      }}

      const payload = {{
        channel: draft.channel,
      }};
      if (draft.description.trim()) {{
        payload.description = draft.description.trim();
      }}
      if (timeoutSeconds !== null) {{
        payload.timeout_seconds = timeoutSeconds;
      }}
      if (draft.channel === "webhook") {{
        payload.webhook_url = draft.webhook_url.trim();
        if (draft.authorization.trim()) {{
          payload.authorization = draft.authorization.trim();
        }}
        if (headers && Object.keys(headers).length) {{
          payload.headers = headers;
        }}
      }}
      if (draft.channel === "feishu") {{
        payload.feishu_webhook = draft.feishu_webhook.trim();
      }}
      if (draft.channel === "telegram") {{
        payload.telegram_chat_id = draft.telegram_chat_id.trim();
        if (draft.telegram_bot_token.trim()) {{
          payload.telegram_bot_token = draft.telegram_bot_token.trim();
        }}
      }}

      const submitButton = form?.querySelector("button[type='submit']");
      if (submitButton) {{
        submitButton.disabled = true;
      }}
      try {{
        if (editingId) {{
          const updated = await api(`/api/alert-routes/${{editingId}}`, {{
            method: "PUT",
            headers: jsonHeaders,
            body: JSON.stringify(payload),
          }});
          setContextRouteName(normalizeRouteName(updated.name), "section-ops");
          state.routeAdvancedOpen = null;
          setRouteDraft(defaultRouteDraft(), "");
          pushActionEntry({{
            kind: copy("route update", "路由修改"),
            label: state.language === "zh" ? `已更新路由：${{updated.name}}` : `Updated route: ${{updated.name}}`,
            detail: state.language === "zh"
              ? `通道：${{routeChannelLabel(updated.channel)}}`
              : `Channel: ${{routeChannelLabel(updated.channel)}}`,
          }});
          await refreshBoard();
          showToast(
            state.language === "zh" ? `路由已更新：${{updated.name}}` : `Route updated: ${{updated.name}}`,
            "success",
          );
          return;
        }}
        const created = await api("/api/alert-routes", {{
          method: "POST",
          headers: jsonHeaders,
          body: JSON.stringify({{ name: draft.name.trim(), ...payload }}),
        }});
        setContextRouteName(normalizeRouteName(created.name), "section-ops");
        const nextChannel = draft.channel;
        state.routeAdvancedOpen = null;
        setRouteDraft({{ ...defaultRouteDraft(), channel: nextChannel }}, "");
        pushActionEntry({{
          kind: copy("route create", "路由创建"),
          label: state.language === "zh" ? `已创建路由：${{created.name}}` : `Created route: ${{created.name}}`,
          detail: copy("The route is now available in mission alert rules and route quick-picks.", "该路由现在已可用于任务告警规则和快捷选择。"),
          undoLabel: copy("Delete route", "删除路由"),
          undo: async () => {{
            await api(`/api/alert-routes/${{created.name}}`, {{ method: "DELETE" }});
            await refreshBoard();
            showToast(
              state.language === "zh" ? `已删除路由：${{created.name}}` : `Route deleted: ${{created.name}}`,
              "success",
            );
          }},
        }});
        await refreshBoard();
        showToast(
          state.language === "zh" ? `路由已创建：${{created.name}}` : `Route created: ${{created.name}}`,
          "success",
        );
      }} catch (error) {{
        reportError(error, copy("Save route", "保存路由"));
      }} finally {{
        if (submitButton) {{
          submitButton.disabled = false;
        }}
      }}
    }}

    async function deleteRouteFromBoard(identifier) {{
      const normalized = normalizeRouteName(identifier);
      if (!normalized) {{
        return;
      }}
      const usageNames = getRouteUsageNames(normalized);
      const confirmation = usageNames.length
        ? copy(
            `Delete route ${{normalized}}? It is referenced by ${{usageNames.length}} mission(s): ${{usageNames.slice(0, 3).join(", ")}}.`,
            `确认删除路由 ${{normalized}}？它仍被 ${{usageNames.length}} 个任务引用：${{usageNames.slice(0, 3).join("、")}}。`,
          )
        : copy(
            `Delete route ${{normalized}}?`,
            `确认删除路由 ${{normalized}}？`,
          );
      if (!window.confirm(confirmation)) {{
        return;
      }}
      try {{
        const deleted = await api(`/api/alert-routes/${{normalized}}`, {{ method: "DELETE" }});
        if (normalizeRouteName(state.contextRouteName) === normalized) {{
          setContextRouteName("", "");
        }}
        if (normalizeRouteName(state.routeEditingId) === normalized) {{
          state.routeAdvancedOpen = null;
          setRouteDraft(defaultRouteDraft(), "");
        }}
        const createDraftRoute = normalizeRouteName(state.createWatchDraft?.route);
        if (createDraftRoute === normalized) {{
          updateCreateWatchDraft({{ route: "" }});
        }}
        pushActionEntry({{
          kind: copy("route delete", "路由删除"),
          label: state.language === "zh" ? `已删除路由：${{deleted.name}}` : `Deleted route: ${{deleted.name}}`,
          detail: usageNames.length
            ? copy("This route was still referenced by one or more missions. Review mission alert rules before the next run.", "该路由此前仍被任务引用，请在下一次执行前检查相关任务的告警规则。")
            : copy("Unused route removed from the delivery surface.", "未使用路由已从交付面移除。"),
        }});
        await refreshBoard();
        showToast(
          state.language === "zh" ? `路由已删除：${{deleted.name}}` : `Route deleted: ${{deleted.name}}`,
          "success",
        );
      }} catch (error) {{
        reportError(error, copy("Delete route", "删除路由"));
      }}
    }}

    function wireRouteSurfaceActions(root) {{
      if (!root) {{
        return;
      }}
      root.querySelectorAll("[data-route-edit]").forEach((button) => {{
        button.addEventListener("click", async () => {{
          button.disabled = true;
          try {{
            await editRouteInDeck(String(button.dataset.routeEdit || ""));
          }} catch (error) {{
            reportError(error, copy("Edit route", "编辑路由"));
          }} finally {{
            button.disabled = false;
          }}
        }});
      }});
      root.querySelectorAll("[data-route-attach]").forEach((button) => {{
        button.addEventListener("click", async () => {{
          button.disabled = true;
          try {{
            await applyRouteToMissionDraft(String(button.dataset.routeAttach || ""));
          }} catch (error) {{
            reportError(error, copy("Apply route", "应用路由"));
          }} finally {{
            button.disabled = false;
          }}
        }});
      }});
      root.querySelectorAll("[data-route-delete]").forEach((button) => {{
        button.addEventListener("click", async () => {{
          button.disabled = true;
          try {{
            await deleteRouteFromBoard(String(button.dataset.routeDelete || ""));
          }} finally {{
            button.disabled = false;
          }}
        }});
      }});
    }}

    function renderRouteDeck() {{
      const root = $("route-deck");
      if (!root) {{
        return;
      }}
      const draft = normalizeRouteDraft(state.routeDraft || defaultRouteDraft());
      const editingId = normalizeRouteName(state.routeEditingId);
      const editing = Boolean(editingId);
      const advancedOpen = isRouteAdvancedOpen(draft);
      const routeName = normalizeRouteName(editing ? editingId : draft.name);
      const usageCount = routeName ? getRouteUsageCount(routeName) : 0;
      const health = routeName ? getRouteHealthRow(routeName) : null;
      const advancedChips = [];
      if (draft.description.trim()) {{
        advancedChips.push(copy("description added", "已补充说明"));
      }}
      if (draft.authorization.trim()) {{
        advancedChips.push(copy("auth attached", "已附带认证"));
      }}
      if (draft.headers_json.trim()) {{
        advancedChips.push(copy("custom headers", "自定义请求头"));
      }}
      if (draft.timeout_seconds.trim()) {{
        advancedChips.push(phrase("timeout {{value}}s", "超时 {{value}} 秒", {{ value: draft.timeout_seconds.trim() }}));
      }}
      if (!advancedChips.length) {{
        advancedChips.push(copy("No advanced control yet", "当前没有高级设置"));
      }}

      root.innerHTML = `
        <form id="route-form">
          <div class="card-top">
            <div>
              <div class="mono">${{editing ? copy("route edit", "路由编辑") : copy("route create", "路由创建")}}</div>
              <h3 class="card-title" style="margin-top:10px;">${{editing ? escapeHtml(draft.name) : copy("Create Named Route", "创建命名路由")}}</h3>
            </div>
            <div style="display:grid; gap:6px; justify-items:end;">
              <span class="chip ${{health && health.status === "healthy" ? "ok" : health && health.status && health.status !== "idle" ? "hot" : ""}}">${{health ? localizeWord(health.status || "idle") : localizeWord(editing ? "editable" : "new")}}</span>
              <span class="chip">${{copy("used", "已引用")}}=${{usageCount}}</span>
            </div>
          </div>
          <div class="panel-sub">${{
            editing
              ? copy("Update the sink in place. Route name stays fixed so existing mission rules do not drift.", "原位更新交付路由。路由名称保持不变，避免已有任务规则漂移。")
              : copy("Add a reusable sink once, then pick it from mission alert rules and quick route chips.", "先把可复用的交付路由配置好，后续在任务告警规则和快捷路由里直接选择。")
          }}</div>
          <div class="chip-row" style="margin-top:4px;">
            ${{
              routeChannelOptions.map((option) => `
                <button
                  class="chip-btn ${{draft.channel === option.value ? "active" : ""}}"
                  type="button"
                  data-route-channel="${{option.value}}"
                >${{escapeHtml(copy(option.label, option.zhLabel || option.label))}}</button>
              `).join("")
            }}
          </div>
          <div class="field-grid" style="margin-top:2px;">
            <label>${{copy("Route Name", "路由名称")}}<input name="name" placeholder="ops-webhook" value="${{escapeHtml(draft.name)}}" ${{editing ? "readonly" : ""}}><span class="field-hint">${{editing ? copy("Name is fixed during edit so existing mission rules keep resolving.", "编辑时名称固定，避免已有任务规则失效。") : copy("Use a short reusable id, such as ops-webhook or exec-telegram.", "建议使用可复用的简短 ID，例如 ops-webhook 或 exec-telegram。")}}</span></label>
            <label>${{copy("Channel", "通道")}}<input name="channel" value="${{escapeHtml(routeChannelLabel(draft.channel))}}" readonly><span class="field-hint">${{copy("Change channel with the route type chips above.", "通过上方的路由类型按钮切换通道。")}}</span></label>
          </div>
          <div class="field-grid">
            ${{
              draft.channel === "webhook"
                ? `
                    <label>${{copy("Webhook URL", "Webhook URL")}}<input name="webhook_url" placeholder="https://hooks.example.com/ops" value="${{escapeHtml(draft.webhook_url)}}"><span class="field-hint">${{copy("Paste the receiver endpoint once, then reuse the route everywhere else.", "把接收端地址配置一次，后续在其他地方直接复用。")}}</span></label>
                    <label>${{copy("Destination Preview", "目标预览")}}<input value="${{escapeHtml(draft.webhook_url.trim() ? summarizeUrlHost(draft.webhook_url) : copy("Waiting for URL", "等待输入 URL"))}}" readonly><span class="field-hint">${{copy("Only the host preview is shown here to keep scanning fast.", "这里只显示主机预览，方便快速扫描。")}}</span></label>
                  `
                : draft.channel === "feishu"
                  ? `
                    <label>${{copy("Feishu Webhook", "飞书 Webhook")}}<input name="feishu_webhook" placeholder="https://open.feishu.cn/..." value="${{escapeHtml(draft.feishu_webhook)}}"><span class="field-hint">${{copy("Use the bot webhook issued by the target Feishu group.", "填写目标飞书群机器人提供的 webhook。")}}</span></label>
                    <label>${{copy("Destination Preview", "目标预览")}}<input value="${{escapeHtml(draft.feishu_webhook.trim() ? summarizeUrlHost(draft.feishu_webhook) : copy("Waiting for URL", "等待输入 URL"))}}" readonly><span class="field-hint">${{copy("Preview keeps the card readable without exposing the full URL at a glance.", "保留预览而不是完整地址，列表浏览时更轻量。")}}</span></label>
                  `
                  : draft.channel === "telegram"
                    ? `
                      <label>${{copy("Telegram Chat ID", "Telegram Chat ID")}}<input name="telegram_chat_id" placeholder="-1001234567890" value="${{escapeHtml(draft.telegram_chat_id)}}"><span class="field-hint">${{copy("The chat id remains visible so you can confirm the destination quickly.", "保留 chat id 可见，便于快速确认目标会话。")}}</span></label>
                      <label>${{copy("Bot Token", "Bot Token")}}<input name="telegram_bot_token" type="password" placeholder="${{editing ? copy("Leave blank to keep the current token", "留空则保留当前 token") : "123456:ABCDEF"}}" value="${{escapeHtml(draft.telegram_bot_token)}}"><span class="field-hint">${{editing ? copy("Leave blank to keep the existing bot token.", "留空会保留当前 bot token。") : copy("Required when the route is created.", "创建路由时必须填写。")}}</span></label>
                    `
                    : `
                      <label>${{copy("Markdown Delivery", "Markdown 交付")}}<input value="${{copy("Append alert summaries to the local markdown log.", "把告警摘要追加到本地 Markdown 日志。")}}" readonly><span class="field-hint">${{copy("Use this when operators want a file-backed trail with zero external dependency.", "当你需要零外部依赖的文件留痕时，用这个通道。")}}</span></label>
                      <label>${{copy("Destination Preview", "目标预览")}}<input value="${{copy("alerts.md append target", "alerts.md 追加目标")}}" readonly><span class="field-hint">${{copy("Markdown routes need no extra endpoint fields.", "Markdown 路由不需要额外的目标配置字段。")}}</span></label>
                    `
            }}
          </div>
          <div class="deck-mode-strip">
            <div class="deck-mode-head">
              <div>
                <div class="mono">${{copy("advanced controls", "高级设置")}}</div>
                <div class="panel-sub">${{copy("Keep advanced fields closed until you need auth headers, timeout control, or delivery notes.", "只有在需要认证、超时控制或交付备注时，再展开高级设置。")}}</div>
              </div>
              <button class="btn-secondary advanced-toggle" id="route-advanced-toggle" type="button" aria-expanded="${{String(advancedOpen)}}">${{advancedOpen ? copy("Hide Advanced", "收起高级设置") : copy("Show Advanced", "展开高级设置")}}</button>
            </div>
            <div class="chip-row advanced-summary">${{advancedChips.map((chip) => `<span class="chip">${{escapeHtml(chip)}}</span>`).join("")}}</div>
            <div class="deck-advanced-panel ${{advancedOpen ? "" : "collapsed"}}" aria-hidden="${{String(!advancedOpen)}}">
              <div class="field-grid">
                <label>${{copy("Description", "说明")}}<input name="description" placeholder="${{copy("Primary route for on-call ops", "值班运维主路由")}}" value="${{escapeHtml(draft.description)}}"><span class="field-hint">${{copy("Use one short note so operators know why this sink exists.", "补一句简短说明，让操作者知道这个路由的用途。")}}</span></label>
                <label>${{copy("Timeout Seconds", "超时秒数")}}<input name="timeout_seconds" inputmode="decimal" placeholder="10" value="${{escapeHtml(draft.timeout_seconds)}}"><span class="field-hint">${{copy("Optional override for slower receivers.", "当接收端偏慢时，可以单独覆盖超时时间。")}}</span></label>
              </div>
              ${{
                draft.channel === "webhook"
                  ? `
                      <div class="field-grid">
                        <label>${{copy("Authorization Header", "Authorization 请求头")}}<input name="authorization" type="password" placeholder="${{editing ? copy("Leave blank to keep current auth", "留空则保留当前认证") : "Bearer ..."}}" value="${{escapeHtml(draft.authorization)}}"><span class="field-hint">${{editing ? copy("Leave blank to keep the current secret.", "留空会保留当前密钥。") : copy("Optional bearer token or pre-shared auth header.", "可选的 bearer token 或预共享认证头。")}}</span></label>
                        <label>${{copy("Custom Headers JSON", "自定义请求头 JSON")}}<textarea name="headers_json" rows="4" placeholder='{{"X-Env":"prod"}}'>${{escapeHtml(draft.headers_json)}}</textarea><span class="field-hint">${{copy("Only include extra headers that are not already captured above.", "这里只填写上方未覆盖的额外请求头。")}}</span></label>
                      </div>
                    `
                  : ""
              }}
            </div>
          </div>
          <div class="toolbar">
            <button class="btn-primary" id="route-submit" type="submit">${{editing ? copy("Save Route", "保存路由") : copy("Create Route", "创建路由")}}</button>
            <button class="btn-secondary" id="route-clear" type="button">${{editing ? copy("Cancel Edit", "取消编辑") : copy("Reset Draft", "清空草稿")}}</button>
            ${{
              editing
                ? `<button class="btn-secondary" id="route-apply" type="button">${{copy("Use In Mission", "用于任务草稿")}}</button>`
                : ""
            }}
          </div>
        </form>
      `;

      const form = $("route-form");
      form?.addEventListener("input", () => {{
        state.routeDraft = collectRouteDraft(form);
      }});
      form?.addEventListener("submit", async (event) => {{
        event.preventDefault();
        await submitRouteDeck(form);
      }});
      $("route-advanced-toggle")?.addEventListener("click", () => {{
        state.routeDraft = collectRouteDraft(form);
        state.routeAdvancedOpen = !isRouteAdvancedOpen(state.routeDraft || defaultRouteDraft());
        renderRouteDeck();
      }});
      root.querySelectorAll("[data-route-channel]").forEach((button) => {{
        button.addEventListener("click", () => {{
          const nextChannel = String(button.dataset.routeChannel || "webhook").trim().toLowerCase();
          state.routeDraft = {{
            ...collectRouteDraft(form),
            channel: nextChannel,
          }};
          if (nextChannel !== "markdown") {{
            state.routeAdvancedOpen = true;
          }}
          renderRouteDeck();
        }});
      }});
      $("route-clear")?.addEventListener("click", () => {{
        const wasEditing = Boolean(normalizeRouteName(state.routeEditingId));
        state.routeAdvancedOpen = null;
        setRouteDraft(defaultRouteDraft(), "");
        showToast(
          wasEditing
            ? copy("Route edit cancelled", "已取消路由编辑")
            : copy("Route draft cleared", "已清空路由草稿"),
          "success",
        );
      }});
      $("route-apply")?.addEventListener("click", async () => {{
        await applyRouteToMissionDraft(draft.name);
      }});
    }}

    function renderRouteHealth() {{
      const root = $("route-health");
      if (state.loading.board && !state.routeHealth.length) {{
        root.innerHTML = [skeletonCard(4), skeletonCard(4)].join("");
        return;
      }}
      if (!state.routeHealth.length) {{
        root.innerHTML = `
          ${{renderLifecycleGuideCard({{
            title: copy("Delivery health appears after one named-route alert lands", "至少触发一次命名路由告警后，才会看到交付健康"),
            summary: copy(
              "Create a named route, attach it from Mission Intake or Cockpit alert rules, then let one alert flow through so this panel can report delivery quality.",
              "先创建命名路由，再从任务创建区或任务详情的告警规则里把它接上，等至少一条告警流过后，这里就会开始显示交付质量。"
            ),
            steps: [
              {{
                title: copy("Create Route", "创建路由"),
                copy: copy("Route Manager stores reusable delivery sinks inside the browser shell.", "路由管理会把可复用的交付目标直接保存在浏览器工作流里。"),
              }},
              {{
                title: copy("Attach To Mission", "绑定到任务"),
                copy: copy("Use Mission Intake or Cockpit alert rules to attach the named route.", "在任务创建区或任务详情的告警规则里绑定这个命名路由。"),
              }},
              {{
                title: copy("Trigger Alert", "触发告警"),
                copy: copy("One route-backed alert is enough to seed health and timeline facts.", "只要有一次带路由的告警，就足以开始沉淀健康和时间线事实。"),
              }},
            ],
            actions: [
              {{ label: copy("Focus Route Deck", "聚焦路由草稿"), focus: "route", field: "name", primary: true }},
              {{ label: copy("Focus Mission Draft", "聚焦任务草稿"), focus: "mission", field: "route" }},
            ],
          }})}}
          <div class="empty">${{copy("No route health signal yet. Trigger named-route alerts to populate delivery quality.", "当前还没有路由健康信号。触发命名路由告警后会出现交付质量数据。")}}</div>`;
        wireLifecycleGuideActions(root);
        return;
      }}
      root.innerHTML = state.routeHealth.map((route) => {{
        const usageCount = Array.isArray(route.mission_ids) && route.mission_ids.length
          ? route.mission_ids.length
          : getRouteUsageCount(route.name);
        const actionHierarchy = getRouteCardActionHierarchy(route, route, usageCount);
        return `
          <div class="card">
            <div class="card-top">
              <div>
                <h3 class="card-title">${{route.name}}</h3>
                <div class="meta">
                  <span>${{copy("channel", "通道")}}=${{routeChannelLabel(route.channel || "unknown")}}</span>
                  <span>${{copy("status", "状态")}}=${{localizeWord(route.status || "idle")}}</span>
                  <span>${{copy("rate", "成功率")}}=${{formatRate(route.success_rate)}}</span>
                </div>
              </div>
              <span class="chip ${{route.status === "healthy" ? "ok" : route.status === "idle" ? "" : "hot"}}">${{localizeWord(route.status || "idle")}}</span>
            </div>
            <div class="meta">
              <span>${{copy("events", "事件")}}=${{route.event_count || 0}}</span>
              <span>${{copy("delivered", "送达")}}=${{route.delivered_count || 0}}</span>
              <span>${{copy("failed", "失败")}}=${{route.failure_count || 0}}</span>
              <span>${{copy("last", "最近")}}=${{route.last_event_at || "-"}}</span>
            </div>
            <div class="panel-sub">${{route.last_error || route.last_summary || copy("No recent route delivery attempt recorded.", "近期没有记录到路由投递尝试。")}}</div>
            ${{renderCardActionHierarchy(actionHierarchy)}}
          </div>
        `;
      }}).join("");
      wireRouteSurfaceActions(root);
    }}

    function renderRoutes() {{
      const root = $("route-list");
      renderRouteDeck();
      if (state.loading.board && !state.routes.length) {{
        root.innerHTML = skeletonCard(3);
        return;
      }}
      const searchValue = String(state.routeSearch || "");
      const searchQuery = searchValue.trim().toLowerCase();
      const filteredRoutes = state.routes.filter((route) => {{
        if (!searchQuery) {{
          return true;
        }}
        const health = getRouteHealthRow(route.name);
        const haystack = [
          route.name,
          route.channel,
          route.description,
          route.webhook_url,
          route.feishu_webhook,
          route.telegram_chat_id,
          summarizeRouteDestination(route),
          health?.status,
          health?.last_error,
          ...getRouteUsageNames(route.name),
        ].join(" ").toLowerCase();
        return haystack.includes(searchQuery);
      }});
      const toolbox = `
        <div class="card section-toolbox">
          <div class="section-toolbox-head">
            <div>
              <div class="mono">${{copy("route search", "路由搜索")}}</div>
              <div class="panel-sub">${{copy("Search by name, channel, destination, or attached mission before you edit or delete a route.", "可按名称、通道、目标地址或引用任务快速定位路由。")}}</div>
            </div>
            <div class="section-toolbox-meta">
              <span class="chip">${{copy("shown", "显示")}}=${{filteredRoutes.length}}</span>
              <span class="chip">${{copy("total", "总数")}}=${{state.routes.length}}</span>
            </div>
          </div>
          <div class="search-shell">
            <input type="search" value="${{escapeHtml(searchValue)}}" data-route-search placeholder="${{copy("Search routes", "搜索路由")}}">
            <button class="btn-secondary" type="button" data-route-search-clear ${{searchValue.trim() ? "" : "disabled"}}>${{copy("Clear", "清空")}}</button>
          </div>
        </div>
      `;
      if (!filteredRoutes.length) {{
        root.innerHTML = `${{toolbox}}${{
          state.routes.length
            ? ""
            : renderLifecycleGuideCard({{
                title: copy("Create one reusable route before missions need delivery", "在任务需要交付前，先准备一个可复用路由"),
                summary: copy(
                  "Routes are browser-managed delivery sinks. Create one here once, then attach it from Mission Intake or Cockpit alert rules instead of retyping destination details each time.",
                  "路由是浏览器内管理的交付目标。先在这里建一次，后续在任务创建区或任务详情的告警规则里直接绑定，不必每次重复填写目标信息。"
                ),
                steps: [
                  {{
                    title: copy("Create Named Sink", "创建命名目标"),
                    copy: copy("Give the route a stable name such as ops-webhook or exec-telegram.", "先给路由一个稳定的名字，比如 ops-webhook 或 exec-telegram。"),
                  }},
                  {{
                    title: copy("Attach In Mission", "在任务里绑定"),
                    copy: copy("Mission Intake and Cockpit reuse the route through Alert Route fields.", "任务创建区和任务详情会通过“告警路由”字段复用它。"),
                  }},
                  {{
                    title: copy("Monitor Health", "观察健康状态"),
                    copy: copy("Distribution Health and Alert Stream show whether downstream delivery is behaving.", "分发健康和告警动态会继续告诉你下游投递是否正常。"),
                  }},
                ],
                actions: [
                  {{ label: copy("Focus Route Deck", "聚焦路由草稿"), focus: "route", field: "name", primary: true }},
                  {{ label: copy("Focus Mission Draft", "聚焦任务草稿"), focus: "mission", field: "route" }},
                ],
              }})
        }}<div class="empty">${{state.routes.length ? copy("No route matched the current search.", "没有路由匹配当前搜索。") : copy("No named alert route configured yet. Start with one route so mission alerts can attach to a reusable sink.", "当前还没有配置命名告警路由。先创建一个路由，任务告警才能直接复用。")}}</div>`;
        wireLifecycleGuideActions(root);
        root.querySelector("[data-route-search]")?.addEventListener("input", (event) => {{
          state.routeSearch = event.target.value;
          renderRoutes();
        }});
        root.querySelector("[data-route-search-clear]")?.addEventListener("click", () => {{
          state.routeSearch = "";
          renderRoutes();
        }});
        return;
      }}
      root.innerHTML = `${{toolbox}}${{filteredRoutes.map((route) => {{
        const health = getRouteHealthRow(route.name);
        const usageNames = getRouteUsageNames(route.name);
        const usageCount = usageNames.length;
        const healthTone = health?.status === "healthy" ? "ok" : health?.status && health.status !== "idle" ? "hot" : "";
        const destination = summarizeRouteDestination(route);
        const actionHierarchy = getRouteCardActionHierarchy(route, health, usageCount);
        return `
          <div class="card">
            <div class="card-top">
              <div>
                <h3 class="card-title">${{escapeHtml(route.name || "unnamed-route")}}</h3>
                <div class="meta">
                  <span>${{copy("channel", "通道")}}=${{escapeHtml(routeChannelLabel(route.channel))}}</span>
                  <span>${{copy("used", "已引用")}}=${{usageCount}}</span>
                  <span>${{copy("status", "状态")}}=${{escapeHtml(localizeWord(health?.status || "idle"))}}</span>
                </div>
              </div>
              <div style="display:grid; gap:6px; justify-items:end;">
                <span class="chip ${{healthTone}}">${{escapeHtml(localizeWord(health?.status || "idle"))}}</span>
                <span class="chip">${{escapeHtml(routeChannelLabel(route.channel))}}</span>
              </div>
            </div>
            <div class="panel-sub">${{escapeHtml(route.description || destination)}}</div>
            <div class="meta">
              <span>${{copy("destination", "目标")}}=${{escapeHtml(destination)}}</span>
              <span>${{copy("rate", "成功率")}}=${{formatRate(health?.success_rate)}}</span>
              <span>${{copy("last", "最近")}}=${{escapeHtml(health?.last_event_at || "-")}}</span>
            </div>
            ${{
              usageCount
                ? `<div class="panel-sub">${{copy("Used by", "正在被这些任务引用")}}: ${{escapeHtml(usageNames.slice(0, 3).join(", "))}}${{usageCount > 3 ? " ..." : ""}}</div>`
                : ""
            }}
            ${{renderCardActionHierarchy(actionHierarchy)}}
          </div>
        `;
      }}).join("")}}`;
      root.querySelector("[data-route-search]")?.addEventListener("input", (event) => {{
        state.routeSearch = event.target.value;
        renderRoutes();
      }});
      root.querySelector("[data-route-search-clear]")?.addEventListener("click", () => {{
        state.routeSearch = "";
        renderRoutes();
      }});
      wireRouteSurfaceActions(root);
    }}

    function renderDeliveryWorkspace() {{
      const root = $("delivery-workspace-shell");
      if (!root) {{
        return;
      }}
      syncDeliveryDraft();
      syncDigestProfileDraft();
      syncDeliverySelectionState();
      if (state.loading.board && !state.deliverySubscriptions.length) {{
        root.innerHTML = [skeletonCard(4), skeletonCard(4)].join("");
        return;
      }}

      const draft = normalizeDeliveryDraft(state.deliveryDraft || defaultDeliveryDraft());
      state.deliveryDraft = draft;
      const digestConsole = state.digestConsole && typeof state.digestConsole === "object" ? state.digestConsole : {{}};
      const digestProjection = digestConsole.prepared_payload && typeof digestConsole.prepared_payload === "object"
        ? digestConsole.prepared_payload
        : {{}};
      const digestProfileShell = digestConsole.profile && typeof digestConsole.profile === "object"
        ? digestConsole.profile
        : {{}};
      const digestProfileDraft = normalizeDigestProfileDraft(state.digestProfileDraft || defaultDigestProfileDraft());
      state.digestProfileDraft = digestProfileDraft;
      const digestBundle = digestProjection.content?.feed_bundle && typeof digestProjection.content.feed_bundle === "object"
        ? digestProjection.content.feed_bundle
        : {{}};
      const digestPromptConfig = digestProjection.prompts && typeof digestProjection.prompts === "object"
        ? digestProjection.prompts
        : {{}};
      const digestStats = digestProjection.stats && typeof digestProjection.stats === "object"
        ? digestProjection.stats
        : {{}};
      const digestProfile = digestProjection.config?.digest_profile && typeof digestProjection.config.digest_profile === "object"
        ? digestProjection.config.digest_profile
        : digestProfileDraft;
      const digestTarget = digestProfile.default_delivery_target && typeof digestProfile.default_delivery_target === "object"
        ? digestProfile.default_delivery_target
        : {{}};
      const digestRouteName = normalizeRouteName(digestTarget.ref || digestProfileDraft.default_delivery_target.ref);
      const digestRouteHealth = digestRouteName ? getRouteHealthRow(digestRouteName) : null;
      const digestBundleItems = Array.isArray(digestBundle.items) ? digestBundle.items.slice(0, 4) : [];
      const digestPromptFiles = Array.isArray(digestPromptConfig.files) ? digestPromptConfig.files.slice(0, 6) : [];
      const digestPromptOverrides = Array.isArray(digestPromptConfig.overrides_applied) ? digestPromptConfig.overrides_applied : [];
      const digestProjectionErrors = Array.isArray(digestProjection.errors) ? digestProjection.errors : [];
      const digestRouteDispatchRows = digestRouteName
        ? state.deliveryDispatchRecords.filter((row) => String(row.route_name || "").trim().toLowerCase() === digestRouteName).slice(0, 4)
        : [];
      const digestDispatchRows = Array.isArray(state.digestDispatchResult) ? state.digestDispatchResult : [];
      const subjectOptions = getDeliverySubjectRefOptions(draft.subject_kind);
      const outputOptions = getDeliveryOutputOptions(draft.subject_kind);
      const routeInputValue = draft.route_names.join(", ");
      const selectedSubscription = getSelectedDeliverySubscription();
      const selectedSubscriptionId = String(selectedSubscription?.id || "").trim();
      const selectedPackage = selectedSubscriptionId ? state.deliveryPackageAudits[selectedSubscriptionId] || null : null;
      const selectedPackageError = selectedSubscriptionId ? String(state.deliveryPackageErrors[selectedSubscriptionId] || "").trim() : "";
      const selectedReportProfiles = selectedSubscription && String(selectedSubscription.subject_kind || "").trim().toLowerCase() === "report"
        ? state.exportProfiles.filter((profile) => String(profile.report_id || "").trim() === String(selectedSubscription.subject_ref || "").trim())
        : [];
      const selectedProfileId = selectedSubscriptionId
        ? String(state.deliveryPackageProfileIds[selectedSubscriptionId] || "").trim()
        : "";
      const selectedDispatchRows = selectedSubscription ? getDeliveryDispatchRowsForSubscription(selectedSubscription.id).slice(0, 8) : [];
      const dispatchTimeline = selectedDispatchRows.length
        ? selectedDispatchRows.map((row) => `
            <div class="mini-item">${{row.route_label || row.route_name || "-"}} | ${{localizeWord(row.status || "pending")}} | ${{row.package_profile_id || copy("default", "默认")}}</div>
            <div class="panel-sub">${{row.error || row.package_id || copy("No package audit detail.", "当前没有包审计详情。")}}</div>
          `).join("")
        : `<div class="empty">${{copy("No dispatch audit recorded for the current selection.", "当前选中的订阅还没有 dispatch 审计记录。")}}</div>`;
      const inventoryRows = state.deliverySubscriptions.length
        ? state.deliverySubscriptions.map((subscription) => {{
            const subscriptionId = String(subscription.id || "").trim();
            const isSelected = subscriptionId === selectedSubscriptionId;
            const routeNames = Array.isArray(subscription.route_names) ? subscription.route_names : [];
            const auditCount = getDeliveryDispatchRowsForSubscription(subscriptionId).length;
            return `
              <div class="card">
                <div class="card-top">
                  <div>
                    <h3 class="card-title">${{escapeHtml(summarizeDeliverySubject(subscription) || subscriptionId)}}</h3>
                    <div class="meta">
                      <span>${{formatDeliverySubjectKind(subscription.subject_kind)}}</span>
                      <span>${{formatDeliveryOutputKind(subscription.output_kind)}}</span>
                      <span>${{localizeWord(subscription.delivery_mode || "pull")}}</span>
                    </div>
                  </div>
                  <span class="chip ${{reportStatusTone(subscription.status)}}">${{escapeHtml(localizeWord(subscription.status || "active"))}}</span>
                </div>
                <div class="panel-sub">${{escapeHtml(subscription.subject_ref || copy("No subject ref.", "没有 subject ref。"))}}</div>
                <div class="meta">
                  <span>${{copy("routes", "路由")}}=${{routeNames.length ? routeNames.join(", ") : copy("none", "无")}}</span>
                  <span>${{copy("cursor", "游标")}}=${{subscription.cursor_or_since || "-"}}</span>
                  <span>${{copy("audit", "审计")}}=${{auditCount}}</span>
                </div>
                <div class="actions">
                  <button class="btn-secondary" type="button" data-delivery-select="${{escapeHtml(subscriptionId)}}">${{isSelected ? copy("Inspecting", "查看中") : copy("Inspect", "查看")}}</button>
                  <button class="btn-secondary" type="button" data-delivery-toggle-status="${{escapeHtml(subscriptionId)}}" data-next-status="${{subscription.status === "active" ? "paused" : "active"}}">${{subscription.status === "active" ? copy("Pause", "暂停") : copy("Resume", "恢复")}}</button>
                  <button class="btn-secondary" type="button" data-delivery-delete="${{escapeHtml(subscriptionId)}}">${{copy("Delete", "删除")}}</button>
                </div>
              </div>
            `;
          }}).join("")
        : `${{renderLifecycleGuideCard({{
              title: copy("Create one persisted subscription before delivery turns into habit", "在交付进入常态前，先创建一个持久化订阅"),
              summary: copy(
                "Use the same Reader-backed delivery objects the API, CLI, and MCP already share. The browser should only project those persisted nouns.",
                "直接复用 API、CLI 和 MCP 已共享的 Reader-backed 交付对象。浏览器只负责投影这些持久化名词。"
              ),
              steps: [
                {{
                  title: copy("Pick Subject", "选择主体"),
                  copy: copy("Reports, stories, watch missions, and profile feeds all stay under one delivery contract.", "报告、故事、监控任务和配置订阅都共用同一套交付契约。"),
                }},
                {{
                  title: copy("Bind Route", "绑定路由"),
                  copy: copy("Push delivery stays attached to named routes instead of ad hoc browser state.", "推送交付继续绑定命名路由，而不是浏览器私有状态。"),
                }},
                {{
                  title: copy("Inspect Package", "检查包"),
                  copy: copy("Report subscriptions can preview the exact package before dispatch.", "报告订阅可以在 dispatch 前预览准确的输出包。"),
                }},
              ],
              actions: [
                {{ label: copy("Open Report Studio", "打开报告工作台"), section: "section-report-studio", primary: true }},
                {{ label: copy("Focus Route Deck", "聚焦路由草稿"), focus: "route", field: "name" }},
              ],
            }})}}`;
      const recentDispatchRows = state.deliveryDispatchRecords.length
        ? state.deliveryDispatchRecords.slice(0, 8).map((row) => `
            <div class="mini-item">${{row.route_label || row.route_name || "-"}} | ${{localizeWord(row.status || "pending")}} | ${{formatDeliveryOutputKind(row.output_kind)}}</div>
            <div class="panel-sub">${{row.subject_ref || "-"}} | ${{row.package_id || copy("No package id.", "没有 package id。")}}</div>
          `).join("")
        : `<div class="empty">${{copy("No delivery dispatch audit recorded yet.", "当前还没有记录到交付 dispatch 审计。")}}</div>`;

      root.innerHTML = `
        <div class="story-columns">
          <div class="stack">
            <div class="card" id="digest-console-card">
              <div class="card-top">
                <div>
                  <h3 class="card-title">${{copy("Digest Command Surface", "摘要控制面")}}</h3>
                  <div class="panel-sub">${{copy("Edit the shared digest profile, inspect the replayable feed bundle, and surface prompt-pack plus route diagnostics over Reader-backed truth.", "直接编辑共享 digest_profile，查看可回放 feed_bundle，并把 prompt-pack 与路由诊断建立在 Reader 真实状态上。")}}</div>
                </div>
                <span class="chip ${{digestProfileShell.onboarding_status === "ready" ? "ok" : "hot"}}">${{digestProfileShell.onboarding_status === "ready" ? copy("Shared profile", "共享配置") : copy("Onboarding", "待初始化")}}</span>
              </div>
              <form id="digest-profile-form" style="margin-top:12px;">
                <div class="field-grid">
                  <label>${{copy("Language", "语言")}}<input name="language" value="${{escapeHtml(digestProfileDraft.language)}}" placeholder="en"></label>
                  <label>${{copy("Timezone", "时区")}}<input name="timezone" value="${{escapeHtml(digestProfileDraft.timezone)}}" placeholder="UTC"></label>
                </div>
                <div class="field-grid">
                  <label>${{copy("Frequency", "频率")}}<input name="frequency" value="${{escapeHtml(digestProfileDraft.frequency)}}" placeholder="@daily"></label>
                  <label>${{copy("Default Route", "默认路由")}}
                    <select name="default_delivery_target_ref">
                      <option value="">${{copy("Select route", "选择路由")}}</option>
                      ${{state.routes.map((route) => {{
                        const routeName = normalizeRouteName(route.name);
                        return `<option value="${{escapeHtml(routeName)}}" ${{routeName === digestProfileDraft.default_delivery_target.ref ? "selected" : ""}}>${{escapeHtml(routeName)}}</option>`;
                      }}).join("")}}
                    </select>
                  </label>
                </div>
                <div class="meta">
                  <span>${{copy("status", "状态")}}=${{localizeWord(digestProfileShell.onboarding_status || "needs_setup")}}</span>
                  <span>${{copy("path", "路径")}}=${{escapeHtml(summarizePathTail(digestProfileShell.profile_path || "", 3) || "-")}}</span>
                  <span>${{copy("route", "路由")}}=${{escapeHtml(digestRouteName || copy("unset", "未设置"))}}</span>
                </div>
                <div class="toolbar">
                  <button class="btn-primary" type="submit">${{copy("Save Shared Defaults", "保存共享默认值")}}</button>
                  <button class="btn-secondary" type="button" data-digest-refresh>${{copy("Refresh Preview", "刷新预览")}}</button>
                  <button class="btn-secondary" type="button" data-digest-dispatch ${{digestRouteName ? "" : "disabled"}}>${{copy("Dispatch Digest", "发送摘要")}}</button>
                </div>
              </form>
              <div class="graph-meta" style="margin-top:14px;">
                <div class="mini-list" id="digest-preview-feed">
                  <div class="mono">${{copy("Feed Bundle Preview", "Feed Bundle 预览")}}</div>
                  <div class="meta">
                    <span>${{copy("items", "条目")}}=${{digestStats.feed_bundle?.items_selected ?? digestBundle.stats?.items_selected ?? 0}}</span>
                    <span>${{copy("sources", "来源")}}=${{digestStats.feed_bundle?.sources_selected ?? digestBundle.stats?.sources_selected ?? 0}}</span>
                    <span>${{copy("window end", "窗口结束")}}=${{escapeHtml(digestBundle.window?.end_at || "-")}}</span>
                  </div>
                  ${{digestBundleItems.length
                    ? digestBundleItems.map((item) => `<div class="mini-item">${{escapeHtml(item.title || item.id || "-")}}</div><div class="panel-sub">${{escapeHtml(item.source_name || item.url || "-")}}</div>`).join("")
                    : `<div class="empty">${{copy("No feed-bundle item projected yet.", "当前还没有投影出 feed-bundle 条目。")}}</div>`}}
                </div>
                <div class="mini-list" id="digest-preview-prompts">
                  <div class="mono">${{copy("Prompt Readiness", "Prompt 就绪度")}}</div>
                  <div class="meta">
                    <span>${{copy("pack", "包")}}=${{escapeHtml(digestPromptConfig.repo_default_pack || "-")}}</span>
                    <span>${{copy("overrides", "覆盖")}}=${{digestPromptOverrides.length || 0}}</span>
                    <span>${{copy("files", "文件")}}=${{digestPromptFiles.length || 0}}</span>
                  </div>
                  <div class="panel-sub">${{escapeHtml((digestPromptConfig.override_order || []).join(" -> ") || copy("No prompt order projected.", "当前没有 prompt 顺序信息。"))}}</div>
                  ${{digestPromptFiles.length
                    ? digestPromptFiles.map((path) => `<div class="mini-item">${{escapeHtml(summarizePathTail(path, 3))}}</div>`).join("")
                    : `<div class="empty">${{copy("No prompt provenance file projected yet.", "当前还没有投影出 prompt 来源文件。")}}</div>`}}
                </div>
              </div>
              <div class="graph-meta" style="margin-top:14px;">
                <div class="mini-list" id="digest-route-diagnostics">
                  <div class="mono">${{copy("Route Diagnostics", "路由诊断")}}</div>
                  <div class="meta">
                    <span>${{copy("route", "路由")}}=${{escapeHtml(digestRouteName || copy("unset", "未设置"))}}</span>
                    <span>${{copy("health", "健康")}}=${{escapeHtml(localizeWord(digestRouteHealth?.status || "idle"))}}</span>
                    <span>${{copy("report audit", "报告审计")}}=${{digestRouteDispatchRows.length}}</span>
                  </div>
                  ${{digestDispatchRows.length
                    ? digestDispatchRows.map((row) => `<div class="mini-item">${{escapeHtml(row.route_label || row.route_name || "-")}} | ${{escapeHtml(localizeWord(row.status || "pending"))}}</div><div class="panel-sub">${{escapeHtml(row.governance?.delivery_diagnostics?.rendering?.selected_format || copy("Digest dispatch completed.", "摘要发送已完成。"))}}</div>`).join("")
                    : digestRouteDispatchRows.length
                      ? digestRouteDispatchRows.map((row) => `<div class="mini-item">${{escapeHtml(row.route_label || row.route_name || "-")}} | ${{escapeHtml(localizeWord(row.status || "pending"))}}</div><div class="panel-sub">${{escapeHtml(row.package_id || row.error || "-")}}</div>`).join("")
                      : `<div class="empty">${{escapeHtml(state.digestDispatchError || copy("No route-backed diagnostic row is visible yet. Dispatch once or inspect report-backed audit on the same route.", "当前还没有看到路由诊断记录。先发送一次摘要，或查看同一路由上的报告审计。"))}}</div>`}}
                </div>
                <div class="mini-list" id="digest-preview-errors">
                  <div class="mono">${{copy("Projection Notes", "投影说明")}}</div>
                  <div class="meta">
                    <span>${{copy("exists", "已持久化")}}=${{digestProfileShell.exists ? copy("yes", "是") : copy("no", "否")}}</span>
                    <span>${{copy("missing", "缺字段")}}=${{(digestProfileShell.missing_fields || []).length || 0}}</span>
                    <span>${{copy("errors", "错误")}}=${{digestProjectionErrors.length}}</span>
                  </div>
                  <div class="panel-sub">${{escapeHtml((digestProfileShell.missing_fields || []).join(", ") || copy("Shared digest defaults are projected from the persisted profile.", "共享 digest 默认值正从持久化 profile 投影而来。"))}}</div>
                  ${{digestProjectionErrors.length
                    ? digestProjectionErrors.map((error) => `<div class="mini-item">${{escapeHtml(error.code || "error")}}</div><div class="panel-sub">${{escapeHtml(error.message || "")}}</div>`).join("")
                    : `<div class="mini-item">${{copy("Route-backed digest dispatch stays on the same Reader nouns as CLI and MCP.", "摘要路由发送继续复用与 CLI / MCP 相同的 Reader 名词。")}}</div>`}}
                </div>
              </div>
            </div>

            <div class="card">
              <div class="card-top">
                <div>
                  <h3 class="card-title">${{copy("Subscription Intake", "订阅创建")}}</h3>
                  <div class="panel-sub">${{copy("Create one persisted delivery subscription in the same shell. No browser-only delivery state is introduced here.", "直接在同一个 shell 里创建持久化交付订阅；这里不会引入浏览器私有状态。")}}</div>
                </div>
                <span class="chip ok">${{copy("persisted", "持久化")}}</span>
              </div>
              <form id="delivery-subscription-form" style="margin-top:12px;">
                <div class="field-grid">
                  <label>${{copy("Subject Kind", "主体类型")}}
                    <select name="subject_kind">
                      ${{deliverySubjectOptions.map((value) => `<option value="${{value}}" ${{draft.subject_kind === value ? "selected" : ""}}>${{escapeHtml(formatDeliverySubjectKind(value))}}</option>`).join("")}}
                    </select>
                  </label>
                  <label>${{copy("Subject Ref", "主体对象")}}
                    <select name="subject_ref">
                      ${{subjectOptions.map((option) => `<option value="${{escapeHtml(option.value)}}" ${{draft.subject_ref === option.value ? "selected" : ""}}>${{escapeHtml(option.label || option.value)}}</option>`).join("")}}
                    </select>
                  </label>
                </div>
                <div class="field-grid">
                  <label>${{copy("Output Kind", "输出类型")}}
                    <select name="output_kind">
                      ${{outputOptions.map((option) => `<option value="${{option.value}}" ${{draft.output_kind === option.value ? "selected" : ""}}>${{escapeHtml(option.label)}}</option>`).join("")}}
                    </select>
                  </label>
                  <label>${{copy("Delivery Mode", "交付模式")}}
                    <select name="delivery_mode">
                      ${{deliveryModeOptions.map((value) => `<option value="${{value}}" ${{draft.delivery_mode === value ? "selected" : ""}}>${{escapeHtml(localizeWord(value))}}</option>`).join("")}}
                    </select>
                  </label>
                </div>
                <div class="field-grid">
                  <label>${{copy("Status", "状态")}}
                    <select name="status">
                      ${{deliveryStatusOptions.map((value) => `<option value="${{value}}" ${{draft.status === value ? "selected" : ""}}>${{escapeHtml(localizeWord(value))}}</option>`).join("")}}
                    </select>
                  </label>
                  <label>${{copy("Cursor Or Since", "游标或起点")}}<input name="cursor_or_since" placeholder="2026-03-01T00:00:00Z" value="${{escapeHtml(draft.cursor_or_since)}}"></label>
                </div>
                <label>${{copy("Route Names", "路由名称")}}<input name="route_names" placeholder="ops-webhook, exec-telegram" value="${{escapeHtml(routeInputValue)}}"><span class="field-hint">${{copy("Push delivery should reference one or more named routes. Pull delivery can leave this blank.", "推送交付应绑定一个或多个命名路由；拉取模式可以留空。")}}</span></label>
                <div class="chip-row" style="margin-top:4px;">
                  ${{state.routes.map((route) => {{
                    const routeName = normalizeRouteName(route.name);
                    const active = draft.route_names.includes(routeName);
                    return `<button class="chip-btn ${{active ? "active" : ""}}" type="button" data-delivery-route-toggle="${{escapeHtml(routeName)}}">${{escapeHtml(routeName)}}</button>`;
                  }}).join("") || `<span class="chip">${{copy("No route available yet", "当前还没有路由")}}</span>`}}
                </div>
                <div class="toolbar">
                  <button class="btn-primary" type="submit">${{copy("Create Subscription", "创建订阅")}}</button>
                  <button class="btn-secondary" type="button" data-delivery-reset>${{copy("Reset Draft", "重置草稿")}}</button>
                  <button class="btn-secondary" type="button" data-delivery-jump-report>${{copy("Open Report Studio", "打开报告工作台")}}</button>
                </div>
              </form>
            </div>

            <div class="card">
              <div class="card-top">
                <div>
                  <h3 class="card-title">${{copy("Report Package Audit", "报告包审计")}}</h3>
                  <div class="panel-sub">${{copy("Inspect the exact Reader-backed package before dispatch. This stays tied to the selected persisted subscription.", "在 dispatch 前检查准确的 Reader-backed 输出包，并始终绑定到当前选中的持久化订阅。")}}</div>
                </div>
                <span class="chip ${{selectedSubscription ? "ok" : ""}}">${{selectedSubscription ? escapeHtml(formatDeliveryOutputKind(selectedSubscription.output_kind)) : copy("No selection", "未选择")}}</span>
              </div>
              ${{selectedSubscription
                ? `
                  <div class="field-grid" style="margin-top:12px;">
                    <label>${{copy("Selected Subscription", "当前订阅")}}
                      <select id="delivery-subscription-select">
                        ${{state.deliverySubscriptions.map((subscription) => `<option value="${{escapeHtml(subscription.id)}}" ${{String(subscription.id || "").trim() === selectedSubscriptionId ? "selected" : ""}}>${{escapeHtml(summarizeDeliverySubject(subscription) || subscription.id)}}</option>`).join("")}}
                      </select>
                    </label>
                    <label>${{copy("Package Profile", "包配置")}}
                      <select id="delivery-package-profile-select" ${{String(selectedSubscription.subject_kind || "").trim().toLowerCase() === "report" ? "" : "disabled"}}>
                        <option value="">${{copy("Default package", "默认包")}}</option>
                        ${{selectedReportProfiles.map((profile) => `<option value="${{escapeHtml(profile.id)}}" ${{String(profile.id || "").trim() === selectedProfileId ? "selected" : ""}}>${{escapeHtml(profile.name || profile.id)}}</option>`).join("")}}
                      </select>
                    </label>
                  </div>
                  <div class="meta">
                    <span>${{formatDeliverySubjectKind(selectedSubscription.subject_kind)}}</span>
                    <span>${{escapeHtml(summarizeDeliverySubject(selectedSubscription))}}</span>
                    <span>${{copy("routes", "路由")}}=${{(selectedSubscription.route_names || []).join(", ") || copy("none", "无")}}</span>
                  </div>
                  ${{String(selectedSubscription.subject_kind || "").trim().toLowerCase() === "report"
                    ? `
                      <div class="actions">
                        <button class="btn-secondary" type="button" data-delivery-package-refresh="${{escapeHtml(selectedSubscriptionId)}}">${{copy("Refresh Package", "刷新输出包")}}</button>
                        <button class="btn-primary" type="button" data-delivery-dispatch="${{escapeHtml(selectedSubscriptionId)}}">${{copy("Dispatch Now", "立即 dispatch")}}</button>
                        <button class="btn-secondary" type="button" data-delivery-open-report="${{escapeHtml(selectedSubscription.subject_ref || "")}}">${{copy("Open Report Studio", "打开报告工作台")}}</button>
                      </div>
                      ${{
                        selectedPackage
                          ? `
                            <div class="meta">
                              <span>${{copy("package", "输出包")}}=${{escapeHtml(selectedPackage.package_id || "-")}}</span>
                              <span>${{copy("signature", "签名")}}=${{escapeHtml(selectedPackage.package_signature || "-")}}</span>
                              <span>${{copy("profile", "配置")}}=${{escapeHtml(selectedPackage.profile_id || copy("default", "默认"))}}</span>
                            </div>
                            <pre class="text-block">${{escapeHtml(JSON.stringify(selectedPackage.payload || {{}}, null, 2))}}</pre>
                          `
                          : selectedPackageError
                            ? `<div class="empty">${{escapeHtml(selectedPackageError)}}</div>`
                            : `<div class="empty">${{copy("Load one report-backed package to inspect the payload before dispatch.", "先加载一次报告输出包，再在 dispatch 前检查具体载荷。")}}</div>`
                      }}
                    `
                    : `
                      <div class="empty">${{copy("Package audit is only available for report subscriptions. The selected subscription remains persisted and auditable through dispatch records below.", "当前只有报告订阅支持 package 审计；已选中的其他订阅仍会通过下方 dispatch 记录保持可审计。")}}</div>
                    `}}
                `
                : `<div class="empty">${{copy("Select one subscription from the inventory on the right to inspect its package and dispatch audit.", "先从右侧库存里选中一个订阅，再查看它的输出包和 dispatch 审计。")}}</div>`}}
            </div>
          </div>

          <div class="stack">
            <div class="meta">
              <span class="mono">${{copy("subscription inventory", "订阅库存")}}</span>
              <span class="chip ok">${{copy("count", "数量")}}=${{state.deliverySubscriptions.length}}</span>
              <span class="chip">${{copy("dispatch", "dispatch")}}=${{state.deliveryDispatchRecords.length}}</span>
            </div>
            ${{inventoryRows}}
            <div class="card">
              <div class="card-top">
                <div>
                  <h3 class="card-title">${{copy("Dispatch Audit", "Dispatch 审计")}}</h3>
                  <div class="panel-sub">${{copy("Route-backed dispatch stays attributable to one subscription and one package signature.", "路由驱动的 dispatch 会继续精确归因到具体订阅和具体包签名。")}}</div>
                </div>
                <span class="chip">${{selectedSubscription ? copy("selected focus", "当前聚焦") : copy("recent", "最近记录")}}</span>
              </div>
              <div class="mini-list">${{selectedSubscription ? dispatchTimeline : recentDispatchRows}}</div>
            </div>
          </div>
        </div>
      `;

      wireLifecycleGuideActions(root);
      const digestForm = root.querySelector("#digest-profile-form");
      digestForm?.addEventListener("input", () => {{
        state.digestProfileDraft = collectDigestProfileDraft(digestForm);
      }});
      digestForm?.addEventListener("submit", async (event) => {{
        event.preventDefault();
        const submitButton = digestForm.querySelector("button[type='submit']");
        const nextDraft = collectDigestProfileDraft(digestForm);
        state.digestProfileDraft = nextDraft;
        if (!nextDraft.default_delivery_target.ref) {{
          showToast(copy("Choose one named route before saving shared digest defaults.", "保存共享 digest 默认值前请先选择一个命名路由。"), "error");
          return;
        }}
        if (submitButton) {{
          submitButton.disabled = true;
        }}
        try {{
          const updated = await api("/api/digest-profile", {{
            method: "PUT",
            headers: jsonHeaders,
            body: JSON.stringify(nextDraft),
          }});
          state.digestProfileDraft = normalizeDigestProfileDraft(updated?.profile || nextDraft);
          await loadDigestConsole({{ preserveDraft: false }});
          showToast(copy("Shared digest defaults saved.", "共享 digest 默认值已保存。"), "success");
        }} catch (error) {{
          reportError(error, copy("Save digest profile", "保存 digest 配置"));
        }} finally {{
          if (submitButton) {{
            submitButton.disabled = false;
          }}
        }}
      }});
      root.querySelector("[data-digest-refresh]")?.addEventListener("click", async (event) => {{
        const button = event.currentTarget;
        button.disabled = true;
        try {{
          await loadDigestConsole({{ preserveDraft: false }});
          showToast(copy("Digest preview refreshed.", "摘要预览已刷新。"), "success");
        }} catch (error) {{
          reportError(error, copy("Refresh digest preview", "刷新摘要预览"));
        }} finally {{
          button.disabled = false;
        }}
      }});
      root.querySelector("[data-digest-dispatch]")?.addEventListener("click", async (event) => {{
        const button = event.currentTarget;
        button.disabled = true;
        state.digestDispatchError = "";
        try {{
          state.digestDispatchResult = await api("/api/digest/dispatch", {{
            method: "POST",
            headers: jsonHeaders,
            body: JSON.stringify({{ profile: "default", limit: 8 }}),
          }});
          renderDeliveryWorkspace();
          showToast(copy("Digest dispatch completed.", "摘要发送已完成。"), "success");
        }} catch (error) {{
          state.digestDispatchResult = [];
          state.digestDispatchError = error.message;
          renderDeliveryWorkspace();
          reportError(error, copy("Dispatch digest", "发送摘要"));
        }} finally {{
          button.disabled = false;
        }}
      }});
      const form = root.querySelector("#delivery-subscription-form");
      form?.addEventListener("input", () => {{
        state.deliveryDraft = collectDeliveryDraft(form);
      }});
      form?.addEventListener("change", (event) => {{
        state.deliveryDraft = collectDeliveryDraft(form);
        const fieldName = String(event.target?.name || "").trim();
        if (fieldName === "subject_kind" || fieldName === "subject_ref" || fieldName === "delivery_mode") {{
          renderDeliveryWorkspace();
        }}
      }});
      form?.addEventListener("submit", async (event) => {{
        event.preventDefault();
        const submitButton = form.querySelector("button[type='submit']");
        const nextDraft = collectDeliveryDraft(form);
        state.deliveryDraft = nextDraft;
        if (!nextDraft.subject_ref) {{
          showToast(copy("Pick one subject before saving the subscription.", "保存订阅前请先选择一个主体对象。"), "error");
          return;
        }}
        if (nextDraft.delivery_mode === "push" && !nextDraft.route_names.length) {{
          showToast(copy("Push delivery needs at least one named route.", "推送交付至少需要绑定一个命名路由。"), "error");
          return;
        }}
        if (submitButton) {{
          submitButton.disabled = true;
        }}
        try {{
          const created = await api("/api/delivery-subscriptions", {{
            method: "POST",
            headers: jsonHeaders,
            body: JSON.stringify(nextDraft),
          }});
          state.selectedDeliverySubscriptionId = String(created.id || "").trim();
          state.deliveryDraft = defaultDeliveryDraft();
          pushActionEntry({{
            kind: copy("delivery create", "交付创建"),
            label: state.language === "zh"
              ? `已创建订阅：${{summarizeDeliverySubject(created) || created.id}}`
              : `Created subscription: ${{summarizeDeliverySubject(created) || created.id}}`,
            detail: state.language === "zh"
              ? `输出：${{formatDeliveryOutputKind(created.output_kind)}}`
              : `Output: ${{formatDeliveryOutputKind(created.output_kind)}}`,
          }});
          await refreshBoard();
          showToast(copy("Delivery subscription created.", "交付订阅已创建。"), "success");
        }} catch (error) {{
          reportError(error, copy("Create delivery subscription", "创建交付订阅"));
        }} finally {{
          if (submitButton) {{
            submitButton.disabled = false;
          }}
        }}
      }});
      root.querySelectorAll("[data-delivery-route-toggle]").forEach((button) => {{
        button.addEventListener("click", () => {{
          const routeName = normalizeRouteName(button.dataset.deliveryRouteToggle || "");
          const draftRoutes = state.deliveryDraft?.route_names || [];
          state.deliveryDraft = normalizeDeliveryDraft({{
            ...(state.deliveryDraft || draft),
            route_names: draftRoutes.includes(routeName)
              ? draftRoutes.filter((value) => value !== routeName)
              : [...draftRoutes, routeName],
          }});
          renderDeliveryWorkspace();
        }});
      }});
      root.querySelector("[data-delivery-reset]")?.addEventListener("click", () => {{
        state.deliveryDraft = defaultDeliveryDraft();
        renderDeliveryWorkspace();
        showToast(copy("Delivery draft reset.", "交付草稿已重置。"), "success");
      }});
      root.querySelector("[data-delivery-jump-report]")?.addEventListener("click", () => {{
        jumpToSection("section-report-studio");
      }});
      root.querySelector("#delivery-subscription-select")?.addEventListener("change", async (event) => {{
        state.selectedDeliverySubscriptionId = String(event.target.value || "").trim();
        renderDeliveryWorkspace();
        const subscription = getSelectedDeliverySubscription();
        if (subscription && String(subscription.subject_kind || "").trim().toLowerCase() === "report") {{
          try {{
            await loadDeliveryPackageAudit(subscription.id, {{
              profileId: String(state.deliveryPackageProfileIds[subscription.id] || "").trim(),
            }});
          }} catch (error) {{
            reportError(error, copy("Load report package", "加载报告输出包"));
          }}
        }}
      }});
      root.querySelector("#delivery-package-profile-select")?.addEventListener("change", async (event) => {{
        const subscription = getSelectedDeliverySubscription();
        if (!subscription) {{
          return;
        }}
        const profileId = String(event.target.value || "").trim();
        state.deliveryPackageProfileIds[String(subscription.id || "").trim()] = profileId;
        try {{
          await loadDeliveryPackageAudit(subscription.id, {{ profileId }});
        }} catch (error) {{
          reportError(error, copy("Load report package", "加载报告输出包"));
        }}
      }});
      root.querySelector("[data-delivery-package-refresh]")?.addEventListener("click", async (event) => {{
        const subscriptionId = String(event.currentTarget.dataset.deliveryPackageRefresh || "").trim();
        const button = event.currentTarget;
        button.disabled = true;
        try {{
          await loadDeliveryPackageAudit(subscriptionId, {{
            profileId: String(state.deliveryPackageProfileIds[subscriptionId] || "").trim(),
          }});
          showToast(copy("Report package refreshed.", "报告输出包已刷新。"), "success");
        }} catch (error) {{
          reportError(error, copy("Refresh report package", "刷新报告输出包"));
        }} finally {{
          button.disabled = false;
        }}
      }});
      root.querySelector("[data-delivery-dispatch]")?.addEventListener("click", async (event) => {{
        const subscriptionId = String(event.currentTarget.dataset.deliveryDispatch || "").trim();
        const button = event.currentTarget;
        button.disabled = true;
        try {{
          const profileId = String(state.deliveryPackageProfileIds[subscriptionId] || "").trim();
          await api(`/api/delivery-subscriptions/${{subscriptionId}}/dispatch`, {{
            method: "POST",
            headers: jsonHeaders,
            body: JSON.stringify({{ profile_id: profileId || null }}),
          }});
          pushActionEntry({{
            kind: copy("delivery dispatch", "交付执行"),
            label: state.language === "zh"
              ? `已执行 dispatch：${{subscriptionId}}`
              : `Dispatched subscription: ${{subscriptionId}}`,
            detail: state.language === "zh"
              ? `配置：${{profileId || "default"}}`
              : `Profile: ${{profileId || "default"}}`,
          }});
          await refreshBoard();
          showToast(copy("Delivery dispatch completed.", "交付 dispatch 已完成。"), "success");
        }} catch (error) {{
          reportError(error, copy("Dispatch delivery subscription", "执行交付订阅"));
        }} finally {{
          button.disabled = false;
        }}
      }});
      root.querySelector("[data-delivery-open-report]")?.addEventListener("click", async (event) => {{
        const reportId = String(event.currentTarget.dataset.deliveryOpenReport || "").trim();
        if (reportId) {{
          await selectReport(reportId);
        }}
        jumpToSection("section-report-studio");
      }});
      root.querySelectorAll("[data-delivery-select]").forEach((button) => {{
        button.addEventListener("click", async () => {{
          const subscriptionId = String(button.dataset.deliverySelect || "").trim();
          state.selectedDeliverySubscriptionId = subscriptionId;
          renderDeliveryWorkspace();
          const subscription = getDeliverySubscriptionRecord(subscriptionId);
          if (subscription && String(subscription.subject_kind || "").trim().toLowerCase() === "report") {{
            try {{
              await loadDeliveryPackageAudit(subscriptionId, {{
                profileId: String(state.deliveryPackageProfileIds[subscriptionId] || "").trim(),
              }});
            }} catch (error) {{
              reportError(error, copy("Load report package", "加载报告输出包"));
            }}
          }}
        }});
      }});
      root.querySelectorAll("[data-delivery-toggle-status]").forEach((button) => {{
        button.addEventListener("click", async () => {{
          const subscriptionId = String(button.dataset.deliveryToggleStatus || "").trim();
          const nextStatus = String(button.dataset.nextStatus || "active").trim().toLowerCase();
          button.disabled = true;
          try {{
            await api(`/api/delivery-subscriptions/${{subscriptionId}}`, {{
              method: "PUT",
              headers: jsonHeaders,
              body: JSON.stringify({{ status: nextStatus }}),
            }});
            await refreshBoard();
            showToast(
              nextStatus === "paused"
                ? copy("Delivery subscription paused.", "交付订阅已暂停。")
                : copy("Delivery subscription resumed.", "交付订阅已恢复。"),
              "success",
            );
          }} catch (error) {{
            reportError(error, copy("Update delivery subscription", "更新交付订阅"));
          }} finally {{
            button.disabled = false;
          }}
        }});
      }});
      root.querySelectorAll("[data-delivery-delete]").forEach((button) => {{
        button.addEventListener("click", async () => {{
          const subscriptionId = String(button.dataset.deliveryDelete || "").trim();
          if (!subscriptionId) {{
            return;
          }}
          const confirmed = window.confirm(copy(
            `Delete delivery subscription ${{subscriptionId}}?`,
            `确认删除交付订阅 ${{subscriptionId}}？`,
          ));
          if (!confirmed) {{
            return;
          }}
          button.disabled = true;
          try {{
            await api(`/api/delivery-subscriptions/${{subscriptionId}}`, {{ method: "DELETE" }});
            if (state.selectedDeliverySubscriptionId === subscriptionId) {{
              state.selectedDeliverySubscriptionId = "";
            }}
            await refreshBoard();
            showToast(copy("Delivery subscription deleted.", "交付订阅已删除。"), "success");
          }} catch (error) {{
            reportError(error, copy("Delete delivery subscription", "删除交付订阅"));
          }} finally {{
            button.disabled = false;
          }}
        }});
      }});
    }}

    function renderAiSurfaces() {{
      const root = $("ai-surface-shell");
      if (!root) {{
        return;
      }}
      const hasPrechecks = Object.keys(state.aiSurfacePrechecks || {{}}).length > 0;
      if (state.loading.board && !hasPrechecks) {{
        root.innerHTML = [skeletonCard(4), skeletonCard(4), skeletonCard(4)].join("");
        return;
      }}
      const surfaces = [
        {{
          id: "mission_suggest",
          title: copy("Mission Suggest", "任务建议"),
          subjectLabel: copy("watch", "任务"),
          section: "section-board",
        }},
        {{
          id: "triage_assist",
          title: copy("Triage Assist", "分诊辅助"),
          subjectLabel: copy("evidence", "证据"),
          section: "section-triage",
        }},
        {{
          id: "claim_draft",
          title: copy("Claim Draft", "主张草稿"),
          subjectLabel: copy("story", "故事"),
          section: "section-story",
        }},
      ];
      root.innerHTML = surfaces.map((surface) => {{
        const precheck = getAiSurfacePrecheck(surface.id);
        const projection = getAiSurfaceProjection(surface.id);
        const runtime = projection?.runtime_facts && typeof projection.runtime_facts === "object" ? projection.runtime_facts : {{}};
        const subject = projection?.subject && typeof projection.subject === "object" ? projection.subject : {{}};
        const rejectableGaps = Array.isArray(precheck.rejectable_gaps) ? precheck.rejectable_gaps : [];
        const mustExposeFacts = Array.isArray(precheck.must_expose_runtime_facts) ? precheck.must_expose_runtime_facts : [];
        const tone = runtime.status === "invalid" || precheck.mode_status === "rejected"
          ? "hot"
          : runtime.status === "fallback_used" || precheck.mode_status === "admitted"
            ? "ok"
            : "";
        return `
          <div class="card">
            <div class="card-top">
              <div>
                <div class="mono">${{escapeHtml(surface.id)}}</div>
                <h3 class="card-title" style="margin-top:10px;">${{escapeHtml(surface.title)}}</h3>
              </div>
              <span class="chip ${{tone}}">${{escapeHtml(localizeWord(runtime.status || precheck.mode_status || "pending"))}}</span>
            </div>
            <div class="meta">
              <span>${{copy("mode", "模式")}}=${{escapeHtml(precheck.mode || "assist")}}</span>
              <span>${{copy("subject", "对象")}}=${{escapeHtml(subject.id || "-")}}</span>
              <span>${{copy("contract", "契约")}}=${{escapeHtml(precheck.contract_id || "-")}}</span>
            </div>
            <div class="panel-sub">${{escapeHtml(summarizeAiSurfaceProjection(surface.id, projection))}}</div>
            <div class="meta" style="margin-top:10px;">
              <span>${{copy("alias", "别名")}}=${{escapeHtml(precheck.alias || "-")}}</span>
              <span>${{copy("fallback", "回退")}}=${{escapeHtml(localizeWord(precheck.manual_fallback || "-"))}}</span>
              <span>${{copy("gaps", "缺口")}}=${{rejectableGaps.length}}</span>
              <span>${{copy("runtime facts", "运行事实")}}=${{mustExposeFacts.length}}</span>
            </div>
            <div class="panel-sub">${{escapeHtml(runtime.request_id || copy("No runtime request id yet.", "当前还没有运行请求 ID。"))}}</div>
            <div class="actions" style="margin-top:12px;">
              <button class="btn-secondary" type="button" data-empty-jump="${{escapeHtml(surface.section)}}">${{copy("Open Surface", "打开对应界面")}}</button>
            </div>
          </div>
        `;
      }}).join("");
      wireLifecycleGuideActions(root);
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
        : `<div class="empty">${{copy("No collector tier breakdown available.", "没有采集器层级拆分数据。")}}</div>`;
      const watchBlock = watchHealth.length
        ? watchHealth.slice(0, 5).map((mission) => `
            <div class="mini-item">${{mission.id}} | ${{mission.status || "idle"}} | due=${{mission.is_due ? "yes" : "no"}} | rate=${{formatRate(mission.success_rate)}}</div>
          `).join("")
        : `<div class="empty">${{copy("No watch mission health record yet.", "当前没有任务健康记录。")}}</div>`;
      const collectorBlock = degradedCollectors.length
        ? degradedCollectors.slice(0, 4).map((collector) => `
            <div class="mini-item">${{collector.name}} | ${{collector.tier}} | ${{collector.status}} | available=${{collector.available}}</div>
          `).join("")
        : `<div class="empty">${{copy("No degraded collector currently reported.", "当前没有降级采集器。")}}</div>`;
      const collectorDrilldownBlock = collectorDrilldown.length
        ? collectorDrilldown.slice(0, 8).map((collector) => `
            <div class="mini-item">${{collector.name}} | ${{collector.tier || "-"}} | ${{collector.status || "ok"}} | available=${{collector.available}}</div>
            <div class="panel-sub">${{collector.setup_hint || collector.message || copy("No remediation note.", "没有修复说明。")}}</div>
          `).join("")
        : `<div class="empty">${{copy("No collector drill-down entry available.", "没有采集器下钻条目。")}}</div>`;
      const routeDrilldownBlock = routeDrilldown.length
        ? routeDrilldown.slice(0, 8).map((route) => `
            <div class="mini-item">${{route.name}} | channel=${{route.channel || "unknown"}} | status=${{route.status || "idle"}} | rate=${{formatRate(route.success_rate)}}</div>
            <div class="panel-sub">missions=${{route.mission_count || 0}} | rules=${{route.rule_count || 0}} | events=${{route.event_count || 0}} | failed=${{route.failure_count || 0}}</div>
            <div class="panel-sub">${{route.last_error || route.last_summary || copy("No recent route detail.", "没有最近路由详情。")}}</div>
          `).join("")
        : `<div class="empty">${{copy("No route drill-down entry available.", "没有路由下钻条目。")}}</div>`;
      const routeTimelineBlock = routeTimeline.length
        ? routeTimeline.slice(0, 8).map((event) => `
            <div class="mini-item">${{event.created_at || "-"}} | ${{event.route || "-"}} | ${{event.status || "pending"}} | ${{event.mission_name || event.mission_id || "-"}}</div>
            <div class="panel-sub">${{event.error || event.summary || copy("No route event detail.", "没有路由事件详情。")}}</div>
          `).join("")
        : `<div class="empty">${{copy("No route delivery timeline event available.", "没有路由投递时间线事件。")}}</div>`;
      const failureBlock = recentFailures.length
        ? recentFailures.slice(0, 4).map((failure) => `
            <div class="mini-item">${{failure.kind}} | ${{failure.mission_name || failure.name || "-"}} | ${{localizeWord(failure.status || "error")}} | ${{failure.error || "-"}}</div>
          `).join("")
        : `<div class="empty">${{copy("No recent failure captured.", "近期没有失败记录。")}}</div>`;
      const overflowEvidence = state.consoleOverflowEvidence || defaultConsoleOverflowEvidence();
      const overflowSampledAt = overflowEvidence.updated_at
        ? formatCompactDateTime(overflowEvidence.updated_at)
        : copy("not sampled yet", "尚未采样");
      const overflowResidualBlock = Array.isArray(overflowEvidence.residual_surfaces) && overflowEvidence.residual_surfaces.length
        ? overflowEvidence.residual_surfaces.map((surface) => {{
            const samples = Array.isArray(surface.sample_labels) ? surface.sample_labels : [];
            const sampleLine = samples.length
              ? `<div class="panel-sub">${{samples.map((label) => escapeHtml(label)).join(" | ")}}</div>`
              : `<div class="panel-sub">${{copy("No residual sample label captured.", "没有残余样本文本。")}}</div>`;
            return `
              <div class="mini-item" data-overflow-surface="${{escapeHtml(surface.surface_id || "")}}">
                ${{escapeHtml(surface.surface_id || "unknown")}} | survivors=${{surface.survivor_count || 0}} | fitted=${{surface.fitted_sample_count || 0}}/${{surface.checked_sample_count || 0}}
              </div>
              ${{sampleLine}}
            `;
          }}).join("")
        : `<div class="empty" data-overflow-surface-empty="true">${{copy("No residual overflow survivors captured in this runtime session.", "当前运行会话没有捕获到残余溢出样本。")}}</div>`;
      const alertSignal = getGovernanceSignal("alert_yield");
      const storySignal = getGovernanceSignal("story_conversion");
      const deliveryContinuityBlock = renderLifecycleContinuityCard({{
        title: copy("Delivery Continuity", "交付连续性"),
        summary: copy(
          "Alerting missions, ready stories, and route-backed delivery health stay in one lane so downstream status is visible without backtracking.",
          "触发告警的任务、待交付故事和路由健康会保持在同一条工作线里，让下游状态无需回跳即可看清。"
        ),
        stages: [
          {{
            kicker: copy("Mission", "任务"),
            title: copy("Alerting Missions", "触发告警任务"),
            copy: copy(
              "Mission-side alert load stays visible here so delivery work starts from real upstream pressure instead of guesswork.",
              "这里会持续展示任务侧的告警压力，让交付工作基于真实上游负载，而不是靠猜测。"
            ),
            tone: (state.overview?.alerting_mission_count ?? alertSignal.alerting_missions ?? 0) > 0 ? "ok" : "",
            facts: [
              {{ label: copy("Alerting missions", "触发告警任务"), value: String(state.overview?.alerting_mission_count ?? alertSignal.alerting_missions ?? 0) }},
              {{ label: copy("Recent alerts", "最近告警"), value: String(alertSignal.alert_count ?? state.alerts.length ?? 0) }},
              {{ label: copy("Successful runs", "成功执行"), value: String(alertSignal.successful_runs ?? metrics.runs_total ?? 0) }},
            ],
          }},
          {{
            kicker: copy("Story", "故事"),
            title: copy("Story Readiness", "故事就绪度"),
            copy: copy(
              "Ready stories stay visible beside delivery operations so handoff decisions do not require a separate story audit pass.",
              "待交付故事会与交付操作并排可见，避免为了判断交接是否成立再单独回去审计故事。"
            ),
            tone: (state.overview?.story_ready_count ?? storySignal.ready_story_count ?? 0) > 0 ? "ok" : "",
            facts: [
              {{ label: copy("Stories", "故事"), value: String(state.overview?.story_count ?? storySignal.story_count ?? state.stories.length) }},
              {{ label: copy("Ready", "已就绪"), value: String(state.overview?.story_ready_count ?? storySignal.ready_story_count ?? 0) }},
              {{ label: copy("Converted items", "已转化条目"), value: String(storySignal.converted_item_count ?? 0) }},
            ],
          }},
          {{
            kicker: copy("Route", "路由"),
            title: copy("Route Delivery", "路由交付"),
            copy: copy(
              "Route health and the latest delivery event stay close to the editor so fix-or-forward decisions happen in one place.",
              "路由健康和最新投递事件会贴近编辑器展示，让修复或继续推进都能在同一位置完成。"
            ),
            tone: (routeSummary.degraded || 0) > 0 ? "hot" : "ok",
            facts: [
              {{ label: copy("Healthy", "健康"), value: String(routeSummary.healthy || 0) }},
              {{ label: copy("Degraded", "降级"), value: String(routeSummary.degraded || 0) }},
              {{ label: copy("Last event", "最近事件"), value: formatCompactDateTime(routeTimeline[0]?.created_at || "") }},
            ],
          }},
        ],
        actions: [
          {{ label: copy("Focus Route Deck", "聚焦路由草稿"), focus: "route", field: "name", primary: true }},
          {{ label: copy("Open Mission Board", "打开任务列表"), section: "section-board" }},
          {{ label: copy("Open Stories", "打开故事"), section: "section-story" }},
        ],
      }});
      root.innerHTML = `
        ${{deliveryContinuityBlock}}
        <div class="state-banner ${{isError ? "error" : ""}}">
          <div class="eyebrow"><span class="dot"></span> ${{copy("daemon", "守护进程")}} / ${{localizeWord(status.state || "idle")}}</div>
          <h3 class="card-title" style="margin-top:12px;">${{copy("Heartbeat", "心跳")}}: ${{status.heartbeat_at || "-"}}</h3>
          <div class="meta">
            <span>${{copy("cycles", "轮次")}}=${{metrics.cycles_total || 0}}</span>
            <span>${{copy("runs", "执行")}}=${{metrics.runs_total || 0}}</span>
            <span>${{copy("alerts", "告警")}}=${{metrics.alerts_total || 0}}</span>
            <span>${{copy("errors", "错误")}}=${{metrics.error_total || 0}}</span>
            <span>${{copy("success", "成功")}}=${{metrics.success_total || 0}}</span>
          </div>
        </div>
        <div class="card">
          <div class="mono">${{copy("collector health", "采集器健康")}}</div>
          <div class="meta">
            <span>total=${{collectorSummary.total || 0}}</span>
            <span>ok=${{collectorSummary.ok || 0}}</span>
            <span>warn=${{collectorSummary.warn || 0}}</span>
            <span>error=${{collectorSummary.error || 0}}</span>
            <span>unavailable=${{collectorSummary.unavailable || 0}}</span>
          </div>
        </div>
        <div class="card">
          <div class="mono">${{copy("route health", "路由健康")}}</div>
          <div class="meta">
            <span>healthy=${{routeSummary.healthy || 0}}</span>
            <span>degraded=${{routeSummary.degraded || 0}}</span>
            <span>missing=${{routeSummary.missing || 0}}</span>
            <span>idle=${{routeSummary.idle || 0}}</span>
          </div>
        </div>
        <div class="card">
          <div class="mono">${{copy("watch health", "任务健康")}}</div>
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
        <div class="card" id="console-overflow-evidence-card">
          <div class="mono">${{copy("text overflow evidence", "文本溢出证据")}}</div>
          <div class="meta" data-console-overflow-summary>
            <span>surfaces=${{overflowEvidence.surface_count || 0}}</span>
            <span>checked=${{overflowEvidence.checked_sample_count || 0}}</span>
            <span>fitted=${{overflowEvidence.fitted_sample_count || 0}}</span>
            <span>survivors=${{overflowEvidence.survivor_count || 0}}</span>
            <span>hotspots=${{overflowEvidence.residual_surface_count || 0}}</span>
            <span>sampled=${{overflowSampledAt}}</span>
          </div>
          <div class="panel-sub">${{copy(
            "Session-scoped evidence for data-fit console text surfaces after the current truncation and canvas-fit layers run.",
            "会话级证据，覆盖当前截断与 canvas-fit 层运行后的 data-fit 控制台文本表面。"
          )}}</div>
          <div class="mini-list" style="margin-top:12px;" data-console-overflow-hotspots>
            <div class="mono">${{copy("residual hotspots", "残余热点")}}</div>
            ${{overflowResidualBlock}}
          </div>
        </div>
        <div class="card">
          <div class="mono">${{copy("last_error", "最近错误")}}</div>
          <div>${{status.last_error || "-"}}</div>
        </div>
        <div class="graph-meta">
          <div class="mini-list">
            <div class="mono">${{copy("collector tiers", "采集器层级")}}</div>
            ${{tierBlock}}
          </div>
          <div class="mini-list">
            <div class="mono">${{copy("watch board", "任务面板")}}</div>
            ${{watchBlock}}
          </div>
        </div>
        <div class="graph-meta">
          <div class="mini-list">
            <div class="mono">${{copy("degraded collectors", "降级采集器")}}</div>
            ${{collectorBlock}}
          </div>
          <div class="mini-list">
            <div class="mono">${{copy("collector drill-down", "采集器下钻")}}</div>
            ${{collectorDrilldownBlock}}
          </div>
        </div>
        <div class="graph-meta">
          <div class="mini-list">
            <div class="mono">${{copy("route drill-down", "路由下钻")}}</div>
            ${{routeDrilldownBlock}}
          </div>
          <div class="mini-list">
            <div class="mono">${{copy("recent failures", "最近失败")}}</div>
            ${{failureBlock}}
          </div>
        </div>
        <div class="graph-meta">
          <div class="mini-list">
            <div class="mono">${{copy("route timeline", "路由时间线")}}</div>
            ${{routeTimelineBlock}}
          </div>
          <div class="mini-list">
            <div class="mono">${{copy("degraded collectors", "降级采集器")}}</div>
            ${{collectorBlock}}
          </div>
        </div>`;
      wireLifecycleGuideActions(root);
    }}

    function renderDuplicateExplain(payload) {{
      if (!payload) {{
        return "";
      }}
      const candidates = payload.candidates || [];
      const header = `
        <div class="meta">
          <span>${{copy("suggested_primary", "建议主项")}}=${{payload.suggested_primary_id || "-"}}</span>
          <span>${{copy("matches", "匹配数")}}=${{payload.candidate_count || 0}}</span>
          <span>${{copy("shown", "显示数")}}=${{payload.returned_count || 0}}</span>
        </div>
      `;
      if (!candidates.length) {{
        return `<div class="card" style="margin-top:12px;">${{header}}<div class="panel-sub">${{copy("No close duplicate candidate found.", "没有找到接近的重复候选项。")}}</div></div>`;
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
                      <span>${{copy("similarity", "相似度")}}=${{Number(candidate.similarity || 0).toFixed(2)}}</span>
                      <span>${{copy("state", "状态")}}=${{localizeWord(candidate.review_state || "new")}}</span>
                    </div>
                  </div>
                  <span class="chip ${{candidate.suggested_primary_id === candidate.id ? "ok" : ""}}">${{candidate.suggested_primary_id === candidate.id ? copy("keep", "保留") : copy("merge", "合并")}}</span>
                </div>
                <div class="meta">
                  <span>${{copy("signals", "信号")}}=${{(candidate.signals || []).join(", ") || "-"}}</span>
                  <span>${{copy("domain", "域名")}}=${{candidate.same_domain ? copy("same", "相同") : copy("mixed", "混合")}}</span>
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
        return `<div class="panel-sub">${{copy("No review note recorded yet.", "当前还没有审核备注。")}}</div>`;
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

    function renderTriageWorkbench(item, {{ filteredCount = 0, evidenceFocusCount = 0 }} = {{}}) {{
      if (!item) {{
        return "";
      }}
      const linkedStories = getStoriesForEvidenceItem(item.id);
      const nextHopActions = getTriageWorkbenchActionHierarchy(item, linkedStories);
      const triageSignal = getGovernanceSignal("triage_throughput");
      const storySignal = getGovernanceSignal("story_conversion");
      const noteCount = Array.isArray(item.review_notes) ? item.review_notes.length : 0;
      const itemMission = String(item?.extra?.watch_mission_name || item?.watch_mission_name || "").trim();
      const duplicateExplain = state.triageExplain[item.id];
      return `
        <div class="card workbench-shell">
          <div class="card-top">
            <div>
              <div class="mono">${{copy("Selected Evidence Workbench", "选中证据工作台")}}</div>
              <h3 class="card-title" style="margin-top:10px;">${{escapeHtml(item.title || item.id || copy("Selected evidence", "选中证据"))}}</h3>
            </div>
            <span class="chip ${{item.review_state === "escalated" ? "hot" : "ok"}}">${{localizeWord(item.review_state || "new")}}</span>
          </div>
          <div class="panel-sub">${{copy(
            "Keep queue context, reviewer notes, and story handoff in one focused surface while the list stays available for fast switching.",
            "把队列上下文、审核备注和故事交接集中在一个聚焦工作面里，同时保留列表用于快速切换。"
          )}}</div>
          <div class="workbench-meta">
            <span class="chip">${{copy("Queue", "队列")}}: ${{escapeHtml(localizeWord(state.triageFilter || "open"))}}</span>
            <span class="chip">${{copy("Shown", "显示")}}: ${{filteredCount}}</span>
            <span class="chip">${{copy("Score", "分数")}}: ${{item.score || 0}}</span>
            <span class="chip">${{copy("Confidence", "置信度")}}: ${{Number(item.confidence || 0).toFixed(2)}}</span>
            ${{itemMission ? `<span class="chip ok" data-fit-text="triage-mission-chip" data-fit-max-width="190" data-fit-fallback="28">${{copy("Mission", "任务")}}: ${{escapeHtml(itemMission)}}</span>` : ""}}
            ${{evidenceFocusCount ? `<span class="chip hot">${{copy("Evidence Focus", "证据聚焦")}}: ${{evidenceFocusCount}}</span>` : ""}}
          </div>
          ${{linkedStories.length
            ? `<div class="workbench-story-links">
                ${{linkedStories.map((story) => `<span class="chip ok" data-fit-text="triage-story-chip" data-fit-max-width="176" data-fit-fallback="24">${{escapeHtml(story.title || story.id)}}</span>`).join("")}}
              </div>`
            : ""}}
          <div class="continuity-lane">
            <div class="continuity-stage ${{itemMission ? "ok" : ""}}">
              <div class="continuity-stage-kicker">${{copy("From", "来自")}}</div>
              <div class="continuity-stage-title">${{copy("Mission Intake", "任务入口")}}</div>
              <div class="continuity-stage-copy">${{copy(
                "The queue keeps mission context close so evidence review does not require bouncing back to the board first.",
                "队列会把任务上下文保持在附近，避免为了回忆来源而先跳回任务列表。"
              )}}</div>
              <div class="continuity-fact-list">
                <div class="continuity-fact"><span>${{copy("Mission", "任务")}}</span><strong>${{escapeHtml(itemMission || copy("Shared queue", "共享队列"))}}</strong></div>
                <div class="continuity-fact"><span>${{copy("Open queue", "开放队列")}}</span><strong>${{String(state.overview?.triage_open_count ?? triageSignal.open_items ?? 0)}}</strong></div>
                <div class="continuity-fact"><span>${{copy("Enabled missions", "已启用任务")}}</span><strong>${{String(state.overview?.enabled_watches ?? 0)}}</strong></div>
              </div>
            </div>
            <div class="continuity-stage ok">
              <div class="continuity-stage-kicker">${{copy("Now", "当前")}}</div>
              <div class="continuity-stage-title">${{copy("Selected Evidence", "选中证据")}}</div>
              <div class="continuity-stage-copy">${{copy(
                "State transitions and reviewer notes stay attached to the selected evidence instead of being buried inside the full queue.",
                "状态切换和审核备注会直接附着在当前证据上，而不是继续埋在整条长队列里。"
              )}}</div>
              <div class="continuity-fact-list">
                <div class="continuity-fact"><span>${{copy("State", "状态")}}</span><strong>${{escapeHtml(localizeWord(item.review_state || "new"))}}</strong></div>
                <div class="continuity-fact"><span>${{copy("Notes", "备注")}}</span><strong>${{String(noteCount)}}</strong></div>
                <div class="continuity-fact"><span>${{copy("URL", "链接")}}</span><strong>${{escapeHtml(clampLabel(item.url || "-", 28))}}</strong></div>
              </div>
            </div>
            <div class="continuity-stage ${{linkedStories.length ? "ok" : ""}}">
              <div class="continuity-stage-kicker">${{copy("Next", "下一步")}}</div>
              <div class="continuity-stage-title">${{copy("Story Handoff", "故事交接")}}</div>
              <div class="continuity-stage-copy">${{copy(
                "Linked stories and conversion headroom stay visible so you can decide when this evidence should become narrative work.",
                "已关联故事和转化余量会继续可见，方便判断这条证据何时该进入叙事工作。"
              )}}</div>
              <div class="continuity-fact-list">
                <div class="continuity-fact"><span>${{copy("Linked stories", "已关联故事")}}</span><strong>${{String(linkedStories.length)}}</strong></div>
                <div class="continuity-fact"><span>${{copy("Eligible evidence", "可转故事证据")}}</span><strong>${{String(storySignal.eligible_item_count ?? 0)}}</strong></div>
                <div class="continuity-fact"><span>${{copy("Ready stories", "待交付故事")}}</span><strong>${{String(state.overview?.story_ready_count ?? storySignal.ready_story_count ?? 0)}}</strong></div>
              </div>
            </div>
          </div>
          <div class="workbench-columns">
            <div class="card">
              <div class="mono">${{copy("review notes", "审核备注")}}</div>
              <div class="panel-sub">${{copy("Capture reviewer rationale, route hints, and merge context without losing the selected evidence lane.", "在不丢失当前证据工作线的前提下，记录审核理由、路由提示和合并上下文。")}}</div>
              ${{renderReviewNotes(item.review_notes)}}
              <form data-triage-note-form="${{item.id}}" style="margin-top:12px;">
                <label>${{copy("note composer", "备注编辑")}}<textarea name="note" rows="3" data-triage-note-input="${{item.id}}" placeholder="${{copy("Capture reviewer rationale, routing hint, or merge context.", "记录审核理由、路由提示或合并上下文。")}}">${{escapeHtml(state.triageNoteDrafts[item.id] || "")}}</textarea></label>
                <div class="toolbar">
                  <button class="btn-primary" type="submit">${{copy("Save Note", "保存备注")}}</button>
                </div>
              </form>
            </div>
            <div class="card">
              <div class="mono">${{copy("next hop controls", "下一跳控制")}}</div>
              <div class="panel-sub">${{copy("Create a story, inspect duplicate context, or jump into the story lane without reselecting this evidence.", "无需重新选择这条证据，就可以直接生成故事、查看重复上下文或跳转到故事工作线。")}}</div>
              ${{renderCardActionHierarchy(nextHopActions)}}
              ${{duplicateExplain
                ? renderDuplicateExplain(duplicateExplain)
                : `<div class="panel-sub" style="margin-top:12px;">${{copy("Duplicate explain stays here once loaded so the list can remain focused on switching items.", "加载后的重复解释会留在这里，列表本身只负责切换条目。")}}</div>`}}
            </div>
          </div>
        </div>
      `;
    }}

    function getVisibleTriageItems() {{
      const activeFilter = state.triageFilter || "open";
      const searchQuery = String(state.triageSearch || "").trim().toLowerCase();
      const pinnedIds = new Set(uniqueValues(state.triagePinnedIds));
      return state.triage.filter((item) => {{
        if (pinnedIds.size && !pinnedIds.has(String(item.id || "").trim())) {{
          return false;
        }}
        const reviewState = String(item.review_state || "new").trim().toLowerCase() || "new";
        if (activeFilter === "all") {{
          // pass
        }} else if (activeFilter === "open") {{
          if (["verified", "duplicate", "ignored"].includes(reviewState)) {{
            return false;
          }}
        }} else if (reviewState !== activeFilter) {{
          return false;
        }}
        if (!searchQuery) {{
          return true;
        }}
        const noteText = Array.isArray(item.review_notes)
          ? item.review_notes.map((note) => String(note.note || "")).join(" ")
          : "";
        const haystack = [
          item.id,
          item.title,
          item.url,
          noteText,
        ].join(" ").toLowerCase();
        return haystack.includes(searchQuery);
      }});
    }}

    function isTriageItemSelected(itemId) {{
      return state.selectedTriageIds.includes(itemId);
    }}

    function toggleTriageSelection(itemId, checked = null) {{
      if (!itemId) {{
        return;
      }}
      const next = new Set(state.selectedTriageIds);
      const shouldSelect = checked === null ? !next.has(itemId) : Boolean(checked);
      if (shouldSelect) {{
        next.add(itemId);
        state.selectedTriageId = itemId;
      }} else {{
        next.delete(itemId);
      }}
      state.selectedTriageIds = Array.from(next);
    }}

    function selectVisibleTriageItems() {{
      const visibleIds = getVisibleTriageItems().map((item) => item.id);
      state.selectedTriageIds = visibleIds;
      if (visibleIds.length && !visibleIds.includes(state.selectedTriageId)) {{
        state.selectedTriageId = visibleIds[0];
      }}
    }}

    function clearTriageSelection() {{
      state.selectedTriageIds = [];
    }}

    function clearTriageEvidenceFocus() {{
      state.triagePinnedIds = [];
      renderTriage();
      showToast(copy("Returned to the full triage queue.", "已返回完整分诊队列。"), "success");
    }}

    function focusTriageEvidence(itemIds, {{ itemId = "", jump = true, showToastMessage = true }} = {{}}) {{
      const normalizedIds = uniqueValues(itemIds).filter((candidate) => state.triage.some((item) => item.id === candidate));
      if (!normalizedIds.length) {{
        if (showToastMessage) {{
          showToast(copy("No matching triage evidence is available for this story.", "当前没有可回查的分诊证据。"), "error");
        }}
        return;
      }}
      state.triagePinnedIds = normalizedIds;
      state.triageFilter = "all";
      state.triageSearch = "";
      state.selectedTriageId = itemId && normalizedIds.includes(itemId) ? itemId : normalizedIds[0];
      state.selectedTriageIds = [];
      renderTriage();
      if (jump) {{
        jumpToSection("section-triage");
      }}
      if (showToastMessage) {{
        showToast(
          state.language === "zh"
            ? `已聚焦 ${{normalizedIds.length}} 条相关分诊证据`
            : `Focused ${{normalizedIds.length}} related triage item(s)`,
          "success",
        );
      }}
    }}

    async function postTriageState(itemId, nextState) {{
      return api(`/api/triage/${{itemId}}/state`, {{
        method: "POST",
        headers: jsonHeaders,
        body: JSON.stringify({{ state: nextState, actor: "console" }}),
      }});
    }}

    async function deleteTriageItem(itemId) {{
      return api(`/api/triage/${{itemId}}`, {{
        method: "DELETE",
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
        await postTriageState(itemId, nextState);
        pushActionEntry({{
          kind: copy("triage state", "分诊状态"),
          label: state.language === "zh" ? `已将 ${{itemId}} 标记为 ${{localizeWord(nextState)}}` : `Marked ${{itemId}} as ${{nextState}}`,
          detail: state.language === "zh" ? `之前状态为 ${{localizeWord(previousState)}}。` : `Previous state was ${{previousState}}.`,
          undoLabel: state.language === "zh" ? `恢复为 ${{localizeWord(previousState)}}` : `Restore ${{previousState}}`,
          undo: async () => {{
            await postTriageState(itemId, previousState);
            await refreshBoard();
            showToast(
              state.language === "zh"
                ? `已恢复分诊状态：${{itemId}} -> ${{localizeWord(previousState)}}`
                : `Triage state restored: ${{itemId}} -> ${{previousState}}`,
              "success",
            );
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

    async function runTriageDelete(itemId) {{
      if (!itemId) {{
        return;
      }}
      const currentItem = state.triage.find((item) => item.id === itemId);
      const itemLabel = currentItem && currentItem.title ? currentItem.title : itemId;
      const confirmed = window.confirm(
        state.language === "zh"
          ? `确认删除分诊条目：${{itemLabel}}？该操作会把条目从当前收件箱中移除。`
          : `Delete triage item "${{itemLabel}}" from the inbox?`,
      );
      if (!confirmed) {{
        return;
      }}
      await deleteTriageItem(itemId);
      state.selectedTriageIds = state.selectedTriageIds.filter((selectedId) => selectedId !== itemId);
      delete state.triageExplain[itemId];
      delete state.triageNoteDrafts[itemId];
      pushActionEntry({{
        kind: copy("triage delete", "分诊删除"),
        label: state.language === "zh" ? `已删除：${{itemLabel}}` : `Deleted ${{itemLabel}}`,
        detail: state.language === "zh" ? `条目 ID：${{itemId}}` : `Item id: ${{itemId}}`,
      }});
      await refreshBoard();
      showToast(
        state.language === "zh" ? `已删除分诊条目：${{itemLabel}}` : `Deleted triage item: ${{itemLabel}}`,
        "success",
      );
    }}

    async function createStoryFromTriageItems(itemIds) {{
      const normalizedIds = uniqueValues(itemIds).filter((itemId) => state.triage.some((item) => item.id === itemId));
      if (!normalizedIds.length) {{
        return;
      }}
      const selectedItems = normalizedIds
        .map((itemId) => state.triage.find((item) => item.id === itemId))
        .filter(Boolean);
      const created = await api("/api/stories/from-triage", {{
        method: "POST",
        headers: jsonHeaders,
        body: JSON.stringify({{
          item_ids: normalizedIds,
          status: "monitoring",
        }}),
      }});
      state.storySearch = "";
      state.storyFilter = "all";
      state.storySort = "attention";
      persistStoryWorkspacePrefs();
      state.selectedStoryId = created.id;
      state.storyDetails[created.id] = created;
      state.selectedTriageIds = state.selectedTriageIds.filter((itemId) => !normalizedIds.includes(itemId));
      pushActionEntry({{
        kind: copy("story seed", "故事生成"),
        label: state.language === "zh"
          ? `已从分诊生成故事：${{created.title}}`
          : `Created story from triage: ${{created.title}}`,
        detail: state.language === "zh"
          ? `来源条目：${{selectedItems.map((item) => item.title || item.id).slice(0, 3).join("、")}}`
          : `Source items: ${{selectedItems.map((item) => item.title || item.id).slice(0, 3).join(", ")}}`,
        undoLabel: copy("Delete story", "删除故事"),
        undo: async () => {{
          await api(`/api/stories/${{created.id}}`, {{ method: "DELETE" }});
          await refreshBoard();
          showToast(
            state.language === "zh" ? `已删除故事：${{created.title}}` : `Story deleted: ${{created.title}}`,
            "success",
          );
        }},
      }});
      await refreshBoard();
      await loadStory(created.id, {{ mode: "editor", syncUrl: true }});
      jumpToSection("section-story");
      showToast(
        state.language === "zh"
          ? `已从 ${{normalizedIds.length}} 条分诊记录生成故事`
          : `Created story from ${{normalizedIds.length}} triage item(s)`,
        "success",
      );
    }}

    async function runTriageBatchStateUpdate(nextState) {{
      const itemIds = uniqueValues(state.selectedTriageIds).filter((itemId) => state.triage.some((item) => item.id === itemId));
      if (!itemIds.length || !nextState || state.triageBulkBusy) {{
        return;
      }}
      state.triageBulkBusy = true;
      if (!itemIds.includes(state.selectedTriageId)) {{
        state.selectedTriageId = itemIds[0];
      }}
      const previousStates = {{}};
      itemIds.forEach((itemId) => {{
        const currentItem = state.triage.find((item) => item.id === itemId);
        previousStates[itemId] = currentItem ? String(currentItem.review_state || "new") : "new";
        if (currentItem) {{
          currentItem.review_state = nextState;
        }}
      }});
      renderTriage();
      const appliedIds = [];
      try {{
        for (const itemId of itemIds) {{
          await postTriageState(itemId, nextState);
          appliedIds.push(itemId);
        }}
        state.selectedTriageIds = [];
        pushActionEntry({{
          kind: copy("triage batch", "分诊批处理"),
          label: state.language === "zh"
            ? `已批量将 ${{itemIds.length}} 条记录标记为 ${{localizeWord(nextState)}}`
            : `Marked ${{itemIds.length}} triage items as ${{nextState}}`,
          detail: state.language === "zh"
            ? `涉及条目：${{itemIds.join(", ")}}`
            : `Items: ${{itemIds.join(", ")}}`,
          undoLabel: state.language === "zh"
            ? `恢复这 ${{itemIds.length}} 条记录`
            : `Restore ${{itemIds.length}} items`,
          undo: async () => {{
            for (const itemId of itemIds) {{
              await postTriageState(itemId, previousStates[itemId] || "new");
            }}
            await refreshBoard();
            showToast(
              state.language === "zh"
                ? `已恢复 ${{itemIds.length}} 条分诊记录`
                : `Restored ${{itemIds.length}} triage items`,
              "success",
            );
          }},
        }});
        await refreshBoard();
        showToast(
          state.language === "zh"
            ? `已批量处理 ${{itemIds.length}} 条分诊记录`
            : `Processed ${{itemIds.length}} triage items`,
          "success",
        );
      }} catch (error) {{
        itemIds.forEach((itemId) => {{
          const currentItem = state.triage.find((item) => item.id === itemId);
          if (currentItem) {{
            currentItem.review_state = previousStates[itemId] || "new";
          }}
        }});
        renderTriage();
        for (const itemId of appliedIds.reverse()) {{
          try {{
            await postTriageState(itemId, previousStates[itemId] || "new");
          }} catch (rollbackError) {{
            console.error("triage batch rollback failed", rollbackError);
          }}
        }}
        await refreshBoard();
        throw error;
      }} finally {{
        state.triageBulkBusy = false;
        renderTriage();
      }}
    }}

    async function runTriageBatchDelete() {{
      const itemIds = uniqueValues(state.selectedTriageIds).filter((itemId) => state.triage.some((item) => item.id === itemId));
      if (!itemIds.length || state.triageBulkBusy) {{
        return;
      }}
      const confirmed = window.confirm(
        state.language === "zh"
          ? `确认删除已选的 ${{itemIds.length}} 条分诊记录？该操作会把它们从当前收件箱中移除。`
          : `Delete ${{itemIds.length}} selected triage items from the inbox?`,
      );
      if (!confirmed) {{
        return;
      }}
      state.triageBulkBusy = true;
      renderTriage();
      let deletedCount = 0;
      try {{
        for (const itemId of itemIds) {{
          await deleteTriageItem(itemId);
          deletedCount += 1;
          delete state.triageExplain[itemId];
          delete state.triageNoteDrafts[itemId];
        }}
        state.selectedTriageIds = [];
        pushActionEntry({{
          kind: copy("triage batch delete", "分诊批量删除"),
          label: state.language === "zh"
            ? `已批量删除 ${{itemIds.length}} 条分诊记录`
            : `Deleted ${{itemIds.length}} triage items`,
          detail: state.language === "zh"
            ? `涉及条目：${{itemIds.join(", ")}}`
            : `Items: ${{itemIds.join(", ")}}`,
        }});
        await refreshBoard();
        showToast(
          state.language === "zh"
            ? `已批量删除 ${{itemIds.length}} 条分诊记录`
            : `Deleted ${{itemIds.length}} triage items`,
          "success",
        );
      }} catch (error) {{
        await refreshBoard();
        const message = error && error.message ? error.message : String(error || "Unknown error");
        if (deletedCount > 0) {{
          throw new Error(
            state.language === "zh"
              ? `已删除 ${{deletedCount}}/${{itemIds.length}} 条记录后失败：${{message}}`
              : `Deleted ${{deletedCount}}/${{itemIds.length}} items before failure: ${{message}}`,
          );
        }}
        throw error;
      }} finally {{
        state.triageBulkBusy = false;
        renderTriage();
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
        inlineStats.innerHTML = `<span>${{copy("loading", "加载中")}}=triage</span>`;
        root.innerHTML = [skeletonCard(4), skeletonCard(4), skeletonCard(4)].join("");
        renderTopbarContext();
        return;
      }}
      const stats = state.triageStats || {{}};
      const triageStates = stats.states || {{}};
      const triageSearchValue = String(state.triageSearch || "");
      const filterOptions = [
        {{ key: "open", label: copy("open", "开放"), count: stats.open_count || 0 }},
        {{ key: "all", label: copy("all", "全部"), count: stats.total || state.triage.length }},
        ...Object.entries(triageStates).map(([key, count]) => ({{ key, label: localizeWord(key), count: count || 0 }})),
      ];
      const activeFilter = normalizeTriageFilter(state.triageFilter);
      state.triageFilter = activeFilter;
      const filteredItems = getVisibleTriageItems();
      const defaultItemId = filteredItems[0] ? filteredItems[0].id : (state.triage[0] ? state.triage[0].id : "");
      const evidenceFocusCount = uniqueValues(state.triagePinnedIds).filter((itemId) => state.triage.some((item) => item.id === itemId)).length;
      const visibleIds = new Set(filteredItems.map((item) => item.id));
      state.selectedTriageIds = uniqueValues(state.selectedTriageIds).filter((itemId) => visibleIds.has(itemId));
      if (filteredItems.length && !filteredItems.some((item) => item.id === state.selectedTriageId)) {{
        state.selectedTriageId = filteredItems[0].id;
      }}
      if (!filteredItems.length) {{
        state.selectedTriageId = "";
      }}
      const selectedCount = state.selectedTriageIds.length;
      const batchBusy = Boolean(state.triageBulkBusy);
      const triageSearchCard = `
        <div class="card section-toolbox">
          <div class="section-toolbox-head">
            <div>
              <div class="mono">${{copy("queue search", "队列搜索")}}</div>
              <div class="panel-sub">${{copy("Search the visible queue by title, url, id, or recent review notes.", "按标题、链接、条目 ID 或最近备注搜索当前可见队列。")}}</div>
            </div>
            <div class="section-toolbox-meta">
              <span class="chip">${{copy("shown", "显示")}}=${{filteredItems.length}}</span>
              <span class="chip">${{copy("selected", "已选")}}=${{selectedCount}}</span>
              <span class="chip ${{evidenceFocusCount ? "hot" : ""}}">${{copy("evidence", "证据")}}=${{evidenceFocusCount || 0}}</span>
            </div>
          </div>
          <div class="search-shell">
            <input type="search" value="${{escapeHtml(triageSearchValue)}}" data-triage-search placeholder="${{copy("Search visible queue", "搜索当前队列")}}">
            <button class="btn-secondary" type="button" data-triage-search-clear ${{triageSearchValue.trim() ? "" : "disabled"}}>${{copy("Clear", "清空")}}</button>
          </div>
          ${{
            evidenceFocusCount
              ? `
                <div class="actions" style="margin-top:12px;">
                  <span class="chip hot">${{copy("evidence focus active", "证据聚焦中")}}</span>
                  <span class="panel-sub">${{copy(`Showing ${{evidenceFocusCount}} triage evidence item(s) linked to the current story.`, `当前只显示与故事关联的 ${{evidenceFocusCount}} 条分诊证据。`)}}</span>
                  <button class="btn-secondary" type="button" data-triage-pin-clear>${{copy("Show Full Queue", "显示完整队列")}}</button>
                </div>
              `
              : ""
          }}
        </div>
      `;
      const batchCopy = selectedCount
        ? copy(
            `Selected ${{selectedCount}} items. Apply one queue action or clear the selection.`,
            `已选 ${{selectedCount}} 条。直接执行一个批量动作，或先清空选择。`,
          )
        : copy(
            "Select visible items, then apply one review action across the queue without leaving the page.",
            "先选择当前列表中的条目，再在当前页面内一次性执行统一审核动作。",
          );
      const filterBlock = filterOptions.map((option) => `
        <button class="chip-btn ${{activeFilter === option.key ? "active" : ""}}" type="button" data-triage-filter="${{escapeHtml(option.key)}}">${{escapeHtml(option.label)}} (${{option.count || 0}})</button>
      `).join("");
      const batchToolbar = `
        <div class="card batch-toolbar-card ${{selectedCount ? "selection-live" : ""}}">
          <div class="batch-toolbar">
            <div class="batch-toolbar-head">
              <div>
                <div class="mono">${{copy("batch actions", "批量操作")}}</div>
                <div class="panel-sub">${{batchCopy}}</div>
              </div>
              <span class="chip ${{selectedCount ? "ok" : ""}}">${{copy("selected", "已选")}}=${{selectedCount}}</span>
            </div>
            ${{
              selectedCount
                ? `<div class="actions">
                    <button class="btn-secondary" type="button" data-triage-selection-clear ${{batchBusy ? "disabled" : ""}}>${{copy("Clear Selection", "清空选择")}}</button>
                    <button class="btn-secondary" type="button" data-triage-batch-state="triaged" ${{batchBusy ? "disabled" : ""}}>${{copy("Batch Triage", "批量分诊")}}</button>
                    <button class="btn-secondary" type="button" data-triage-batch-state="verified" ${{batchBusy ? "disabled" : ""}}>${{copy("Batch Verify", "批量核验")}}</button>
                    <button class="btn-secondary" type="button" data-triage-batch-state="escalated" ${{batchBusy ? "disabled" : ""}}>${{copy("Batch Escalate", "批量升级")}}</button>
                    <button class="btn-secondary" type="button" data-triage-batch-state="ignored" ${{batchBusy ? "disabled" : ""}}>${{copy("Batch Ignore", "批量忽略")}}</button>
                    <button class="btn-secondary" type="button" data-triage-batch-story ${{batchBusy ? "disabled" : ""}}>${{copy("Batch Story", "批量生成故事")}}</button>
                    <button class="btn-danger" type="button" data-triage-batch-delete ${{batchBusy ? "disabled" : ""}}>${{copy("Batch Delete", "批量删除")}}</button>
                  </div>`
                : `<div class="actions">
                    <button class="btn-secondary" type="button" data-triage-select-visible ${{(!filteredItems.length || batchBusy) ? "disabled" : ""}}>${{copy("Select Visible", "选择当前列表")}}</button>
                  </div>`
            }}
          </div>
        </div>
      `;
      const selectedTriageItem = filteredItems.find((item) => item.id === state.selectedTriageId) || null;
      const triageWorkbench = selectedTriageItem
        ? renderTriageWorkbench(selectedTriageItem, {{ filteredCount: filteredItems.length, evidenceFocusCount }})
        : "";
      inlineStats.innerHTML = `
        <span>${{copy("open", "开放")}}=${{stats.open_count || 0}}</span>
        <span>${{copy("closed", "关闭")}}=${{stats.closed_count || 0}}</span>
        <span>${{copy("notes", "备注")}}=${{stats.note_count || 0}}</span>
        <span>${{copy("verified", "已核验")}}=${{(stats.states || {{}}).verified || 0}}</span>
        <span>${{copy("filter", "筛选")}}=${{localizeWord(activeFilter)}}</span>
        <span>${{copy("selected", "选中")}}=${{selectedCount}}</span>
        <span>${{copy("evidence", "证据")}}=${{evidenceFocusCount}}</span>
        <span>${{copy("focus", "焦点")}}=${{state.selectedTriageId || "-"}}</span>
      `;
      if (!state.triage.length) {{
        root.innerHTML = `
          ${{triageSearchCard}}
          <div class="card">
            <div class="mono">${{copy("triage filters", "分诊筛选")}}</div>
            <div class="panel-sub">${{copy("Slice the queue by current review state before applying notes or state transitions.", "在写备注或修改状态前，先按审核状态切分队列。")}}</div>
            <div class="stack" style="margin-top:12px;">${{filterBlock}}</div>
          </div>
          <div class="card">
            <div class="mono">${{copy("triage shortcuts", "分诊快捷键")}}</div>
            <div class="panel-sub">${{copy("Use J/K to move, V to verify, T to triage, E to escalate, I to ignore, S to create a story, D to explain duplicates, and N to focus the note composer.", "使用 J/K 上下移动，V 核验，T 分诊，E 升级，I 忽略，S 生成故事，D 查看重复解释，N 聚焦备注输入。")}}</div>
          </div>
          ${{batchToolbar}}
          ${{renderLifecycleGuideCard({{
            title: copy("Triage opens after the first mission run writes inbox items", "任务第一次执行并写入收件箱后，分诊区才会展开"),
            summary: copy(
              "You do not need CLI-first setup to use the review lane. Create or run a mission in the browser, then use this queue to verify signal, mark duplicates, and promote stories.",
              "进入审阅工作流不需要先读 CLI 文档。先在浏览器里创建或执行任务，随后就在这个队列里完成核验、去重和故事提升。"
            ),
            steps: [
              {{
                title: copy("Run A Mission", "先执行任务"),
                copy: copy("Mission Board or Cockpit will populate the inbox once evidence is collected.", "任务列表或任务详情执行后，收件箱就会开始积累证据。"),
              }},
              {{
                title: copy("Review Evidence", "审阅证据"),
                copy: copy("Mark duplicates, verify findings, or escalate items directly inside this queue.", "直接在这个队列里完成去重、核验或升级处理。"),
              }},
              {{
                title: copy("Promote Story", "提升故事"),
                copy: copy("Use Create Story when the queue has enough verified signal to become a narrative.", "当队列里积累了足够的已核验信号时，就可以直接生成故事。"),
              }},
              {{
                title: copy("Attach Delivery Later", "稍后再接交付"),
                copy: copy("Routes stay optional until the mission or story is ready to notify downstream.", "只有在任务或故事需要通知下游时，才需要回去接入路由。"),
              }},
            ],
            actions: [
              {{ label: copy("Open Mission Board", "打开任务列表"), section: "section-board", primary: true }},
              {{ label: copy("Focus Story Intake", "聚焦故事录入"), focus: "story", field: "title" }},
              {{ label: copy("Open Route Manager", "打开路由管理"), focus: "route", field: "name" }},
            ],
          }})}}
          <div class="empty">${{copy("No triage item stored right now.", "当前没有分诊条目。")}}</div>`;
        wireLifecycleGuideActions(root);
        syncTriageUrlState({{ defaultItemId }});
        flushTriageUrlFocus();
        renderTopbarContext();
        scheduleCanvasTextFit(root);
        return;
      }}
      root.innerHTML = `
        ${{triageSearchCard}}
        <div class="card">
          <div class="mono">${{copy("triage filters", "分诊筛选")}}</div>
          <div class="panel-sub">${{copy("Slice the queue by current review state before applying notes or state transitions.", "在写备注或修改状态前，先按审核状态切分队列。")}}</div>
          <div class="stack" style="margin-top:12px;">${{filterBlock}}</div>
        </div>
        <div class="card">
          <div class="mono">${{copy("triage shortcuts", "分诊快捷键")}}</div>
          <div class="panel-sub">${{copy("Use J/K to move, V to verify, T to triage, E to escalate, I to ignore, S to create a story, D to explain duplicates, and N to focus the note composer.", "使用 J/K 上下移动，V 核验，T 分诊，E 升级，I 忽略，S 生成故事，D 查看重复解释，N 聚焦备注输入。")}}</div>
        </div>
        ${{batchToolbar}}
        ${{triageWorkbench}}
        ${{
          filteredItems.length
            ? filteredItems.map((item) => {{
                const linkedStories = getStoriesForEvidenceItem(item.id);
                const noteCount = Array.isArray(item.review_notes) ? item.review_notes.length : 0;
                const itemMission = String(item?.extra?.watch_mission_name || item?.watch_mission_name || "").trim();
                const actionHierarchy = getTriageCardActionHierarchy(item, linkedStories);
                return `
        <div class="card selectable ${{item.id === state.selectedTriageId ? "selected" : ""}}" data-triage-card="${{item.id}}">
          <div class="card-top">
            <div class="triage-card-head">
              <label class="checkbox-inline">
                <input type="checkbox" data-triage-select="${{item.id}}" ${{isTriageItemSelected(item.id) ? "checked" : ""}}>
                <span>${{copy("select", "选择")}}</span>
              </label>
              <div>
                <h3 class="card-title">${{item.title}}</h3>
                <div class="meta">
                  <span>${{item.id}}</span>
                  <span>${{copy("state", "状态")}}=${{localizeWord(item.review_state || "new")}}</span>
                  <span>${{copy("score", "分数")}}=${{item.score || 0}}</span>
                  <span>${{copy("confidence", "置信度")}}=${{Number(item.confidence || 0).toFixed(2)}}</span>
                </div>
              </div>
            </div>
            <span class="chip ${{item.review_state === "escalated" ? "hot" : ""}}">${{localizeWord(item.review_state || "new")}}</span>
          </div>
          <div class="panel-sub">${{item.url}}</div>
          <div class="meta">
            <span>${{copy("notes", "备注")}}=${{noteCount}}</span>
            <span>${{copy("stories", "故事")}}=${{linkedStories.length}}</span>
            ${{itemMission ? `<span>${{copy("mission", "任务")}}=${{escapeHtml(clampLabel(itemMission, 28))}}</span>` : ""}}
          </div>
          ${{renderCardActionHierarchy(actionHierarchy)}}
        </div>
      `;
              }}).join("")
            : `<div class="empty">${{copy("No triage item matched the active queue filter.", "没有条目匹配当前分诊筛选。")}}</div>`
        }}
      `;

      root.querySelectorAll("[data-triage-filter]").forEach((button) => {{
        button.addEventListener("click", () => {{
          state.triageFilter = normalizeTriageFilter(button.dataset.triageFilter);
          renderTriage();
        }});
      }});

      root.querySelector("[data-triage-search]")?.addEventListener("input", (event) => {{
        state.triageSearch = event.target.value;
        renderTriage();
      }});

      root.querySelector("[data-triage-search-clear]")?.addEventListener("click", () => {{
        state.triageSearch = "";
        renderTriage();
      }});

      root.querySelector("[data-triage-pin-clear]")?.addEventListener("click", () => {{
        clearTriageEvidenceFocus();
      }});

      root.querySelector("[data-triage-select-visible]")?.addEventListener("click", () => {{
        selectVisibleTriageItems();
        renderTriage();
      }});

      root.querySelector("[data-triage-selection-clear]")?.addEventListener("click", () => {{
        clearTriageSelection();
        renderTriage();
      }});

      root.querySelectorAll("[data-triage-batch-state]").forEach((button) => {{
        button.addEventListener("click", async () => {{
          button.disabled = true;
          try {{
            await runTriageBatchStateUpdate(String(button.dataset.triageBatchState || "").trim());
          }} catch (error) {{
            reportError(error, copy("Batch triage", "批量分诊"));
          }} finally {{
            button.disabled = false;
          }}
        }});
      }});

      root.querySelector("[data-triage-batch-story]")?.addEventListener("click", async (event) => {{
        const button = event.currentTarget;
        button.disabled = true;
        try {{
          await createStoryFromTriageItems(state.selectedTriageIds);
        }} catch (error) {{
          reportError(error, copy("Create story from triage", "从分诊生成故事"));
        }} finally {{
          button.disabled = false;
        }}
      }});

      root.querySelector("[data-triage-batch-delete]")?.addEventListener("click", async (event) => {{
        const button = event.currentTarget;
        button.disabled = true;
        try {{
          await runTriageBatchDelete();
        }} catch (error) {{
          reportError(error, copy("Batch delete", "批量删除"));
        }} finally {{
          button.disabled = false;
        }}
      }});

      root.querySelectorAll("[data-triage-card]").forEach((card) => {{
        card.addEventListener("click", (event) => {{
          if (event.target.closest("button, textarea, input, select, a, form, label")) {{
            return;
          }}
          state.selectedTriageId = String(card.dataset.triageCard || "").trim();
          renderTriage();
        }});
      }});

      root.querySelectorAll("[data-triage-select]").forEach((input) => {{
        input.addEventListener("change", () => {{
          toggleTriageSelection(String(input.dataset.triageSelect || "").trim(), input.checked);
          renderTriage();
        }});
      }});

      root.querySelectorAll("[data-triage-explain]").forEach((button) => {{
        button.addEventListener("click", async () => {{
          button.disabled = true;
          try {{
            await runTriageExplain(String(button.dataset.triageExplain || "").trim());
          }} catch (error) {{
            reportError(error, copy("Explain duplicates", "查看重复解释"));
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
            reportError(error, copy("Update triage state", "更新分诊状态"));
          }} finally {{
            button.disabled = false;
          }}
        }});
      }});

      root.querySelectorAll("[data-triage-story]").forEach((button) => {{
        button.addEventListener("click", async () => {{
          button.disabled = true;
          try {{
            await createStoryFromTriageItems([String(button.dataset.triageStory || "").trim()]);
          }} catch (error) {{
            reportError(error, copy("Create story from triage", "从分诊生成故事"));
          }} finally {{
            button.disabled = false;
          }}
        }});
      }});

      root.querySelectorAll("[data-triage-delete]").forEach((button) => {{
        button.addEventListener("click", async () => {{
          button.disabled = true;
          try {{
            await runTriageDelete(String(button.dataset.triageDelete || "").trim());
          }} catch (error) {{
            reportError(error, copy("Delete triage item", "删除分诊条目"));
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
            showToast(copy("Provide a note before saving.", "保存前请先填写备注。"), "error");
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
            reportError(error, copy("Save triage note", "保存分诊备注"));
          }} finally {{
            if (submitButton) {{
              submitButton.disabled = false;
            }}
          }}
        }});
      }});
      wireLifecycleGuideActions(root);
      syncTriageUrlState({{ defaultItemId }});
      flushTriageUrlFocus();
      renderTopbarContext();
      scheduleCanvasTextFit(root);
    }}

    async function loadStory(identifier, {{ mode = null, syncUrl = true }} = {{}}) {{
      const normalizedId = String(identifier || "").trim();
      if (!normalizedId) {{
        return;
      }}
      const normalizedMode = mode == null ? null : normalizeStoryWorkspaceMode(mode);
      if (normalizedMode !== null) {{
        applyStoryWorkspaceMode(normalizedMode, {{ persist: true, syncUrl: false }});
      }}
      state.selectedStoryId = normalizedId;
      state.loading.storyDetail = true;
      renderStories();
      try {{
        const [detail, graph] = await Promise.all([
          api(`/api/stories/${{normalizedId}}`),
          api(`/api/stories/${{normalizedId}}/graph`),
        ]);
        state.storyDetails[normalizedId] = detail;
        state.storyGraph[normalizedId] = graph;
      }} finally {{
        state.loading.storyDetail = false;
      }}
      if (syncUrl) {{
        syncStoryUrlState({{ defaultStoryId: normalizedId }});
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
        return `<div class="empty">${{copy("No entity graph available for this story.", "这个故事当前没有实体图谱。")}}</div>`;
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
            <div class="mini-item">${{escapeHtml(node.label)}} | ${{copy("type", "类型")}}=${{escapeHtml(node.entity_type || "UNKNOWN")}} | ${{copy("in_story", "故事内来源")}}=${{node.in_story_source_count || 0}}</div>
          `).join("")
        : `<div class="empty">${{copy("No entity node captured.", "没有捕获到实体节点。")}}</div>`;

      const relationList = (payload.edges || []).filter((edge) => edge.kind === "entity_relation").length
        ? (payload.edges || []).filter((edge) => edge.kind === "entity_relation").map((edge) => `
            <div class="mini-item">${{escapeHtml(edge.source)}} -> ${{escapeHtml(edge.target)}} | ${{escapeHtml(edge.relation_type || "RELATED")}}</div>
          `).join("")
        : `<div class="empty">${{copy("No direct entity relation captured. Story-level mention edges are still shown above.", "没有直接实体关系；上方仍会展示故事级提及关系。")}}</div>`;

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
            <span>${{copy("nodes", "节点")}}=${{payload.nodes.length}}</span>
            <span>${{copy("edges", "边")}}=${{payload.edge_count || 0}}</span>
            <span>${{copy("relations", "关系")}}=${{payload.relation_count || 0}}</span>
            <span>${{copy("entities", "实体")}}=${{payload.entity_count || 0}}</span>
          </div>
          <div class="graph-meta">
            <div class="mini-list">${{entityList}}</div>
            <div class="mini-list">${{relationList}}</div>
          </div>
        </div>
      `;
    }}

    function renderStoryCreateDeck() {{
      const root = $("story-intake-deck");
      if (!root) {{
        return;
      }}
      const draft = normalizeStoryDraft(state.storyDraft || defaultStoryDraft());
      const selectedStory = getStoryRecord(state.selectedStoryId);
      root.innerHTML = `
        <form id="story-create-form">
          <div class="card-top">
            <div>
              <div class="mono">${{copy("manual story", "手工故事")}}</div>
              <h3 class="card-title" style="margin-top:10px;">${{copy("Capture A Brief Before It Gets Lost", "在信号散掉前先补一条故事")}}</h3>
            </div>
            <span class="chip ok">${{copy("lightweight", "轻量录入")}}</span>
          </div>
          <div class="panel-sub">${{copy("Use this for operator-authored briefs, incident notes, or tracking stubs that should be visible before automated clustering catches up.", "适合录入人工简报、事故备注，或那些需要先被看见、再等待自动聚类补齐的追踪占位。")}}</div>
          <div class="chip-row">
            ${{
              storyStatusOptions.map((status) => `
                <button class="chip-btn ${{draft.status === status ? "active" : ""}}" type="button" data-story-draft-status="${{status}}">${{escapeHtml(localizeWord(status))}}</button>
              `).join("")
            }}
          </div>
          <div class="field-grid">
            <label>${{copy("Story Title", "故事标题")}}<input name="title" value="${{escapeHtml(draft.title)}}" placeholder="${{copy("OpenAI launch brief", "OpenAI 发布简报")}}"><span class="field-hint">${{copy("Keep it short and legible in the story list.", "标题尽量短，方便在故事列表里快速扫读。")}}</span></label>
            <label>${{copy("Story Status", "故事状态")}}
              <select name="status">
                ${{storyStatusOptions.map((value) => `<option value="${{value}}" ${{draft.status === value ? "selected" : ""}}>${{localizeWord(value)}}</option>`).join("")}}
              </select>
              <span class="field-hint">${{copy("Status decides which lane this manual story enters first.", "状态决定这条手工故事先落在哪个工作阶段。")}}</span>
            </label>
          </div>
          <label>${{copy("Story Summary", "故事摘要")}}<textarea name="summary" rows="4" placeholder="${{copy("Capture what happened, why it matters, and what still needs confirmation.", "记录发生了什么、为什么重要，以及哪些部分仍待确认。")}}">${{escapeHtml(draft.summary)}}</textarea><span class="field-hint">${{copy("A compact summary is enough. Evidence and timeline can remain empty for manual stories.", "摘要写到够用即可；手工故事不需要一开始就补齐证据和时间线。")}}</span></label>
          <div class="toolbar">
            <button class="btn-primary" type="submit">${{copy("Create Story", "创建故事")}}</button>
            <button class="btn-secondary" type="button" id="story-draft-clear">${{copy("Clear Draft", "清空草稿")}}</button>
            <button class="btn-secondary" type="button" id="story-draft-template" ${{selectedStory ? "" : "disabled"}}>${{copy("Use Selected As Template", "以当前故事为模板")}}</button>
          </div>
        </form>
      `;
      const form = $("story-create-form");
      form?.addEventListener("input", () => {{
        state.storyDraft = collectStoryDraft(form);
      }});
      form?.addEventListener("submit", async (event) => {{
        event.preventDefault();
        await submitStoryDeck(form);
      }});
      root.querySelectorAll("[data-story-draft-status]").forEach((button) => {{
        button.addEventListener("click", () => {{
          state.storyDraft = {{
            ...collectStoryDraft(form),
            status: String(button.dataset.storyDraftStatus || "active").trim().toLowerCase() || "active",
          }};
          renderStoryCreateDeck();
        }});
      }});
      $("story-draft-clear")?.addEventListener("click", () => {{
        setStoryDraft(defaultStoryDraft());
        showToast(copy("Story draft cleared", "已清空故事草稿"), "success");
      }});
      $("story-draft-template")?.addEventListener("click", () => {{
        if (!selectedStory) {{
          return;
        }}
        setStoryDraft({{
          title: `${{selectedStory.title || copy("Story", "故事")}} ${{copy("Follow-up", "跟进")}}`,
          summary: String(selectedStory.summary || ""),
          status: String(selectedStory.status || "active"),
        }});
        focusStoryDeck("title");
        showToast(
          state.language === "zh"
            ? `已从 ${{selectedStory.title}} 生成故事草稿`
            : `Story draft cloned from ${{selectedStory.title}}`,
          "success",
        );
      }});
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
        root.innerHTML = state.stories.length
          ? `<div class="empty">${{copy("No story is selected in the current filtered workspace.", "当前筛选后的工作区里没有选中的故事。")}}</div>`
          : `
              ${{renderLifecycleGuideCard({{
                title: copy("Stories are the promoted evidence layer", "故事层是被提升后的证据层"),
                summary: copy(
                  "Seed a story manually here when editorial context comes first, or promote one directly from Triage once verified signal is ready. The browser flow does not require a CLI detour.",
                  "如果编辑背景先于聚类出现，可以先在这里手工起一个故事；如果分诊里的已核验证据已经准备好，也可以直接从分诊提升。整个流程不需要再绕回 CLI。"
                ),
                steps: [
                  {{
                    title: copy("Review Triage", "先看分诊"),
                    copy: copy("Use Triage when the story should be grounded in reviewed inbox evidence.", "当故事需要建立在已审阅的收件箱证据上时，先从分诊开始。"),
                  }},
                  {{
                    title: copy("Create Story", "创建故事"),
                    copy: copy("Story Intake captures a manual brief when the narrative should exist immediately.", "如果叙事需要先落下来，故事录入可以直接创建手工简报。"),
                  }},
                  {{
                    title: copy("Refine Summary", "完善摘要"),
                    copy: copy("The workspace lets you tune title, summary, status, and evidence context in one place.", "工作台会把标题、摘要、状态和证据上下文集中到一个位置继续打磨。"),
                  }},
                  {{
                    title: copy("Prepare Delivery", "准备交付"),
                    copy: copy("Attach routes from missions once the story is ready to notify downstream teams.", "当故事准备好触发下游通知时，再回到任务里绑定路由。"),
                  }},
                ],
                actions: [
                  {{ label: copy("Focus Story Intake", "聚焦故事录入"), focus: "story", field: "title", primary: true }},
                  {{ label: copy("Open Triage", "打开分诊"), section: "section-triage" }},
                  {{ label: copy("Open Route Manager", "打开路由管理"), focus: "route", field: "name" }},
                ],
              }})}}
              <div class="empty">${{copy("No persisted story snapshot yet.", "当前还没有持久化故事快照。")}}</div>
            `;
        wireLifecycleGuideActions(root);
        return;
      }}
      const storyEvidenceIds = getStoryEvidenceIds(story);
      const storyDeliveryStatus = getStoryDeliveryStatus(story);
      const storySignal = getGovernanceSignal("story_conversion");
      const alertSignal = getGovernanceSignal("alert_yield");
      const routeSummary = state.ops?.route_summary || {{}};
      const evidenceBlock = (rows, emptyLabel) => rows.length
        ? rows.map((row) => `
            <div class="card">
              <div class="card-top">
                <div>
                    <h3 class="card-title">${{row.title}}</h3>
                    <div class="meta">
                      <span>${{row.item_id}}</span>
                      <span>${{row.source_name || row.source_type || "-"}}</span>
                      <span>${{copy("score", "分数")}}=${{row.score || 0}}</span>
                      <span>${{copy("confidence", "置信度")}}=${{Number(row.confidence || 0).toFixed(2)}}</span>
                    </div>
                  </div>
                <span class="chip ${{row.role === "primary" ? "ok" : ""}}">${{copy(row.role || "secondary", row.role === "primary" ? "主证据" : "次证据")}}</span>
              </div>
              <div class="panel-sub">${{row.url || "-"}}</div>
              <div class="actions">
                <button class="btn-secondary" type="button" data-story-evidence-triage="${{row.item_id}}">${{copy("Open In Triage", "回到分诊")}}</button>
              </div>
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
                    <span>${{copy("positive", "正向")}}=${{conflict.positive || 0}}</span>
                    <span>${{copy("negative", "负向")}}=${{conflict.negative || 0}}</span>
                    <span>${{copy("neutral", "中性")}}=${{conflict.neutral || 0}}</span>
                    </div>
                  </div>
                <span class="chip hot">${{copy("conflict", "冲突")}}</span>
              </div>
              <div class="panel-sub">${{conflict.note || copy("Cross-source stance divergence detected.", "检测到跨来源立场分歧。")}}</div>
            </div>
          `).join("")
        : `<div class="empty">${{copy("No contradiction marker in this story.", "这个故事没有冲突标记。")}}</div>`;
      const timelineBlock = (story.timeline || []).length
        ? story.timeline.map((event) => `
            <div class="card">
              <div class="card-top">
                <div>
                    <h3 class="card-title">${{event.title}}</h3>
                    <div class="meta">
                      <span>${{event.time || "-"}}</span>
                      <span>${{event.source_name || "-"}}</span>
                      <span>${{copy("role", "角色")}}=${{copy(event.role || "secondary", event.role === "primary" ? "主证据" : "次证据")}}</span>
                      <span>${{copy("score", "分数")}}=${{event.score || 0}}</span>
                    </div>
                  </div>
                </div>
              <div class="panel-sub">${{event.url || "-"}}</div>
            </div>
          `).join("")
        : `<div class="empty">${{copy("No timeline event captured.", "当前没有时间线事件。")}}</div>`;
      const markdownPreview = state.storyMarkdown[selected]
        ? `
            <div class="card">
              <div class="mono">${{copy("markdown evidence pack", "Markdown 证据包")}}</div>
              <pre class="text-block">${{escapeHtml(state.storyMarkdown[selected])}}</pre>
            </div>
          `
        : "";
      const graphPreview = renderStoryGraph(state.storyGraph[selected]);
      const storyContinuityBlock = renderLifecycleContinuityCard({{
        title: copy("Story Delivery Readiness", "故事交付就绪度"),
        summary: copy(
          "Evidence, story editing, and downstream delivery status stay connected around the same narrative object.",
          "证据、故事编辑和下游交付状态会继续围绕同一个叙事对象保持连贯。"
        ),
        stages: [
          {{
            kicker: copy("Review", "审阅"),
            title: copy("Evidence Context", "证据上下文"),
            copy: copy(
              "Primary and secondary evidence stay visible so the story never drifts away from reviewed signal.",
              "主次证据会继续保持可见，避免故事脱离已审阅信号。"
            ),
            tone: storyEvidenceIds.length ? "ok" : "",
            facts: [
              {{ label: copy("Evidence", "证据"), value: String(storyEvidenceIds.length) }},
              {{ label: copy("Primary item", "主条目"), value: story.primary_item_id || "-" }},
              {{ label: copy("Conflicts", "冲突"), value: String((story.contradictions || []).length) }},
            ],
          }},
          {{
            kicker: copy("Current", "当前"),
            title: copy("Story Workspace", "故事工作台"),
            copy: copy(
              "Narrative edits happen beside evidence, timeline, and entity structure instead of in a detached editor.",
              "叙事编辑会与证据、时间线和实体结构并排存在，而不是进入一个脱离上下文的编辑器。"
            ),
            tone: storyDeliveryStatus.tone || "ok",
            facts: [
              {{ label: copy("Status", "状态"), value: localizeWord(story.status || "active") }},
              {{ label: copy("Updated", "更新"), value: formatCompactDateTime(story.updated_at || story.generated_at || "") }},
              {{ label: copy("Delivery", "交付"), value: storyDeliveryStatus.label }},
            ],
          }},
          {{
            kicker: copy("Delivery", "交付"),
            title: copy("Output Handoff", "输出交接"),
            copy: copy(
              "Ready stories, alerting missions, and route health stay nearby so the delivery decision is visible before you leave the workspace.",
              "待交付故事、触发告警的任务和路由健康会保留在附近，方便在离开工作台前判断是否该进入交付。"
            ),
            tone: (state.overview?.story_ready_count ?? storySignal.ready_story_count ?? 0) > 0 ? "ok" : "",
            facts: [
              {{ label: copy("Ready stories", "待交付故事"), value: String(state.overview?.story_ready_count ?? storySignal.ready_story_count ?? 0) }},
              {{ label: copy("Alerting missions", "触发告警任务"), value: String(state.overview?.alerting_mission_count ?? alertSignal.alerting_missions ?? 0) }},
              {{ label: copy("Healthy routes", "健康路由"), value: String(routeSummary.healthy || 0) }},
            ],
          }},
        ],
        actions: [
          {{ label: copy("Focus Evidence In Triage", "回查分诊证据"), section: "section-triage", primary: true }},
          {{ label: copy("Open Delivery", "打开交付"), section: "section-ops" }},
          {{ label: copy("Open Route Manager", "打开路由管理"), focus: "route", field: "name" }},
        ],
      }});
      root.innerHTML = `
        <div class="card">
          <div class="card-top">
            <div>
              <h3 class="card-title">${{story.title}}</h3>
              <div class="meta">
                <span>${{story.id}}</span>
                <span>${{copy("status", "状态")}}=${{localizeWord(story.status || "active")}}</span>
                <span>${{copy("items", "条目")}}=${{story.item_count || 0}}</span>
                <span>${{copy("sources", "来源")}}=${{story.source_count || 0}}</span>
                <span>${{copy("score", "分数")}}=${{Number(story.score || 0).toFixed(1)}}</span>
                <span>${{copy("confidence", "置信度")}}=${{Number(story.confidence || 0).toFixed(2)}}</span>
              </div>
            </div>
            <span class="chip ${{(story.contradictions || []).length ? "hot" : "ok"}}">${{(story.contradictions || []).length ? copy("mixed signals", "信号冲突") : copy("aligned", "一致")}}</span>
          </div>
          <div class="panel-sub">${{story.summary || copy("No summary captured.", "没有记录到摘要。")}}</div>
          <div class="entity-row">
            ${{(story.entities || []).slice(0, 8).map((entity) => `<span class="chip">${{entity}}</span>`).join("") || `<span class="chip">${{copy("no entities", "无实体")}}</span>`}}
          </div>
          <div class="actions">
            <button class="btn-secondary" data-story-markdown="${{story.id}}">${{copy("Preview Markdown", "预览 Markdown")}}</button>
            <button class="btn-secondary" type="button" data-story-focus-triage="${{story.id}}" ${{storyEvidenceIds.length ? "" : "disabled"}}>${{copy("Focus Evidence In Triage", "回查分诊证据")}}</button>
            <a href="/api/stories/${{story.id}}" target="_blank" rel="noreferrer">${{copy("Open JSON", "打开 JSON")}}</a>
            <a href="/api/stories/${{story.id}}/export?format=markdown" target="_blank" rel="noreferrer">${{copy("Export MD", "导出 MD")}}</a>
          </div>
        </div>
        ${{storyContinuityBlock}}
        <div class="card">
          <div class="mono">${{copy("story editor", "故事编辑器")}}</div>
          <div class="meta" style="margin-top:8px;">
            <span class="chip ok">${{copy("editable", "可编辑")}}</span>
            <span>${{copy("Only title, summary, and status change here.", "这里只修改标题、摘要和状态。")}}</span>
          </div>
          <div class="panel-sub">${{copy("Tune the persisted title, summary, and story status without rebuilding the whole workspace snapshot.", "无需重建整个工作区快照，也能直接调整已持久化的标题、摘要和故事状态。")}}</div>
          <form id="story-editor-form" data-story-id="${{story.id}}" style="margin-top:12px;">
            <div class="field-grid">
              <label>${{copy("Story Title", "故事标题")}}<input name="title" value="${{escapeHtml(story.title || "")}}" placeholder="${{copy("OpenAI Launch Story", "OpenAI 发布故事")}}"></label>
              <label>${{copy("Story Status", "故事状态")}}
                <select name="status">
                  ${{storyStatusOptions.map((value) => `<option value="${{value}}" ${{(story.status || "active") === value ? "selected" : ""}}>${{localizeWord(value)}}</option>`).join("")}}
                </select>
              </label>
            </div>
            <label>${{copy("Story Summary", "故事摘要")}}<textarea name="summary" rows="4" placeholder="${{copy("Condense why this story matters right now.", "简要说明这个故事此刻为什么重要。")}}">${{escapeHtml(story.summary || "")}}</textarea></label>
            <div class="toolbar">
              <button class="btn-primary" type="submit">${{copy("Save Story", "保存故事")}}</button>
              <button class="btn-secondary" type="button" data-story-detail-status="${{story.status === "archived" ? "active" : "archived"}}">${{story.status === "archived" ? copy("Restore Story", "恢复故事") : copy("Archive Story", "归档故事")}}</button>
              <button class="btn-danger" type="button" data-story-delete="${{story.id}}">${{copy("Delete Story", "删除故事")}}</button>
            </div>
          </form>
        </div>
        <div class="story-columns">
          <div class="stack">
            <div class="meta"><span class="mono">${{copy("primary evidence", "主证据")}}</span><span class="chip">${{copy("read-only snapshot", "只读快照")}}</span></div>
            ${{evidenceBlock(story.primary_evidence || [], copy("No primary evidence captured.", "没有主证据。"))}}
          </div>
          <div class="stack">
            <div class="meta"><span class="mono">${{copy("secondary evidence", "次证据")}}</span><span class="chip">${{copy("read-only snapshot", "只读快照")}}</span></div>
            ${{evidenceBlock(story.secondary_evidence || [], copy("No secondary evidence captured.", "没有次证据。"))}}
          </div>
        </div>
        <div class="stack">
          <div class="meta"><span class="mono">${{copy("contradiction markers", "冲突标记")}}</span><span class="chip">${{copy("read-only analysis", "只读分析")}}</span></div>
          ${{contradictionBlock}}
        </div>
        <div class="stack">
          <div class="meta"><span class="mono">${{copy("timeline", "时间线")}}</span><span class="chip">${{copy("read-only analysis", "只读分析")}}</span></div>
          ${{timelineBlock}}
        </div>
        <div class="stack">
          <div class="meta"><span class="mono">${{copy("entity graph", "实体图谱")}}</span><span class="chip">${{copy("read-only analysis", "只读分析")}}</span></div>
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
            reportError(error, copy("Preview story markdown", "预览故事 Markdown"));
          }} finally {{
            button.disabled = false;
          }}
        }});
      }});
      root.querySelector("[data-story-focus-triage]")?.addEventListener("click", () => {{
        focusTriageEvidence(storyEvidenceIds, {{ itemId: story.primary_item_id || storyEvidenceIds[0] || "" }});
      }});
      root.querySelectorAll("[data-story-evidence-triage]").forEach((button) => {{
        button.addEventListener("click", () => {{
          const itemId = String(button.dataset.storyEvidenceTriage || "").trim();
          if (!itemId) {{
            return;
          }}
          focusTriageEvidence(storyEvidenceIds, {{ itemId }});
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
            showToast(copy("Provide a story title before saving.", "保存前请先填写故事标题。"), "error");
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
              kind: copy("story update", "故事更新"),
              label: state.language === "zh" ? `已更新故事：${{payload.title}}` : `Updated story ${{payload.title}}`,
              detail: state.language === "zh" ? `当前故事状态为 ${{localizeWord(payload.status || "active")}}。` : `Story status is now ${{payload.status || "active"}}.`,
              undoLabel: copy("Restore story", "恢复故事"),
              undo: async () => {{
                await api(`/api/stories/${{story.id}}`, {{
                  method: "PUT",
                  headers: jsonHeaders,
                  body: JSON.stringify(previousStory),
                }});
                await refreshBoard();
                showToast(
                  state.language === "zh" ? `已恢复故事：${{previousStory.title}}` : `Story restored: ${{previousStory.title}}`,
                  "success",
                );
              }},
            }});
            await refreshBoard();
            showToast(
              state.language === "zh" ? `故事已更新：${{payload.title}}` : `Story updated: ${{payload.title}}`,
              "success",
            );
          }} catch (error) {{
            if (state.storyDetails[story.id]) {{
              state.storyDetails[story.id] = {{
                ...state.storyDetails[story.id],
                ...previousStory,
              }};
            }}
            renderStories();
            reportError(error, copy("Update story", "更新故事"));
          }} finally {{
            if (submitButton) {{
              submitButton.disabled = false;
            }}
          }}
        }});
      }}
      root.querySelector("[data-story-detail-status]")?.addEventListener("click", async (event) => {{
        const button = event.currentTarget;
        button.disabled = true;
        try {{
          await setStoryStatusQuick(story.id, String(button.dataset.storyDetailStatus || ""));
        }} catch (error) {{
          reportError(error, copy("Update story state", "更新故事状态"));
        }} finally {{
          button.disabled = false;
        }}
      }});
      root.querySelector("[data-story-delete]")?.addEventListener("click", async (event) => {{
        const button = event.currentTarget;
        button.disabled = true;
        try {{
          await deleteStoryFromWorkspace(String(button.dataset.storyDelete || story.id));
        }} catch (error) {{
          reportError(error, copy("Delete story", "删除故事"));
        }} finally {{
          button.disabled = false;
        }}
      }});
      wireLifecycleGuideActions(root);
    }}

    function renderStories() {{
      const root = $("story-list");
      const inlineStats = $("story-stats-inline");
      renderStoryViewJumpStrip();
      renderStoryCreateDeck();
      if (state.loading.board && !state.stories.length) {{
        inlineStats.innerHTML = `<span>${{copy("loading", "加载中")}}=stories</span>`;
        root.innerHTML = [skeletonCard(4), skeletonCard(4)].join("");
        $("story-detail").innerHTML = skeletonCard(5);
        renderTopbarContext();
        return;
      }}
      const contradictions = state.stories.reduce((count, story) => count + ((story.contradictions || []).length ? 1 : 0), 0);
      const totalEvidence = state.stories.reduce((count, story) => count + (story.item_count || 0), 0);
      const storySearchValue = String(state.storySearch || "");
      const storySearchQuery = storySearchValue.trim().toLowerCase();
      const storyFilter = normalizeStoryFilter(state.storyFilter);
      const storySort = normalizeStorySort(state.storySort);
      const activeStoryView = detectStoryViewPreset({{ filter: storyFilter, sort: storySort, search: storySearchValue }});
      const matchedStories = state.stories.filter((story) => {{
        const storyStatus = String(story.status || "active").trim().toLowerCase() || "active";
        if (storyFilter === "conflicted" && !(Array.isArray(story.contradictions) && story.contradictions.length)) {{
          return false;
        }}
        if (storyFilter !== "all" && storyFilter !== "conflicted" && storyStatus !== storyFilter) {{
          return false;
        }}
        if (!storySearchQuery) {{
          return true;
        }}
        const primaryTitles = Array.isArray(story.primary_evidence)
          ? story.primary_evidence.map((row) => String(row.title || "")).join(" ")
          : "";
        const haystack = [
          story.id,
          story.title,
          story.summary,
          ...(Array.isArray(story.entities) ? story.entities : []),
          primaryTitles,
        ].join(" ").toLowerCase();
        return haystack.includes(storySearchQuery);
      }});
      const filteredStories = [...matchedStories].sort((left, right) => compareStoriesByWorkspaceOrder(left, right, storySort));
      const defaultStoryId = filteredStories[0] ? filteredStories[0].id : (state.stories[0] ? state.stories[0].id : "");
      const visibleStoryIds = new Set(filteredStories.map((story) => story.id));
      state.selectedStoryIds = uniqueValues(state.selectedStoryIds).filter((storyId) => visibleStoryIds.has(storyId));
      const storyFilterOptions = [
        {{ key: "all", label: copy("all", "全部"), count: state.stories.length }},
        {{ key: "conflicted", label: copy("conflicted", "冲突"), count: contradictions }},
        ...["active", "monitoring", "resolved", "archived"].map((key) => ({{
          key,
          label: localizeWord(key),
          count: state.stories.filter((story) => (String(story.status || "active").trim().toLowerCase() || "active") === key).length,
        }})),
      ];
      inlineStats.innerHTML = `
        <span>${{copy("stories", "故事")}}=${{state.stories.length}}</span>
        <span>${{copy("evidence", "证据")}}=${{totalEvidence}}</span>
        <span>${{copy("contradicted", "冲突故事")}}=${{contradictions}}</span>
        <span>${{copy("shown", "显示")}}=${{filteredStories.length}}</span>
        <span>${{copy("view", "视图")}}=${{storyViewPresetLabel(activeStoryView)}}</span>
        <span>${{copy("sort", "排序")}}=${{storySortLabel(storySort)}}</span>
        <span>${{copy("selected", "已选")}}=${{state.selectedStoryIds.length}}</span>
        <span>${{copy("selected", "选中")}}=${{state.selectedStoryId || "-"}}</span>
      `;
      const storyBatchCount = state.selectedStoryIds.length;
      const storyBatchBusy = Boolean(state.storyBulkBusy);
      const storySearchCard = `
        <div class="card section-toolbox">
          <div class="section-toolbox-head">
            <div>
              <div class="mono">${{copy("story search", "故事搜索")}}</div>
              <div class="panel-sub">${{copy("Search by story title, summary, entity, id, or primary evidence title before opening the workspace.", "可按故事标题、摘要、实体、故事 ID 或主证据标题快速定位。")}}</div>
            </div>
            <div class="section-toolbox-meta">
              <button class="btn-secondary" type="button" data-story-deck-focus>${{copy("New Story", "新建故事")}}</button>
              <span class="chip ${{activeStoryView === "custom" ? "hot" : "ok"}}">${{storyViewPresetLabel(activeStoryView)}}</span>
              <span class="chip ok">${{storySortLabel(storySort)}}</span>
              <span class="chip">${{copy("shown", "显示")}}=${{filteredStories.length}}</span>
              <span class="chip">${{copy("total", "总数")}}=${{state.stories.length}}</span>
            </div>
          </div>
          <div class="search-shell">
            <input type="search" value="${{escapeHtml(storySearchValue)}}" data-story-search placeholder="${{copy("Search stories", "搜索故事")}}">
            <button class="btn-secondary" type="button" data-story-search-clear ${{storySearchValue.trim() ? "" : "disabled"}}>${{copy("Clear", "清空")}}</button>
          </div>
          <div class="field-grid" style="margin-top:12px;">
            <label>${{copy("Story Sort", "故事排序")}}
              <select data-story-sort>
                ${{storySortOptions.map((option) => `<option value="${{option}}" ${{storySort === option ? "selected" : ""}}>${{storySortLabel(option)}}</option>`).join("")}}
              </select>
            </label>
            <div>
              <div class="mono">${{copy("view hint", "视图提示")}}</div>
              <div class="panel-sub">${{activeStoryView === "custom" ? storySortSummary(storySort) : storyViewPresetDescription(activeStoryView)}}</div>
            </div>
          </div>
          <div class="chip-row">
            ${{storyViewPresetOptions.map((option) => `
              <button class="chip-btn ${{activeStoryView === option ? "active" : ""}}" type="button" data-story-view="${{escapeHtml(option)}}">${{escapeHtml(storyViewPresetLabel(option))}}</button>
            `).join("")}}
            ${{activeStoryView === "custom" ? `<span class="chip hot">${{storyViewPresetLabel("custom")}}</span>` : ""}}
          </div>
          <div class="chip-row">
            ${{storyFilterOptions.map((option) => `
              <button class="chip-btn ${{storyFilter === option.key ? "active" : ""}}" type="button" data-story-filter="${{escapeHtml(option.key)}}">${{escapeHtml(option.label)}} (${{option.count || 0}})</button>
            `).join("")}}
          </div>
        </div>
      `;
      const storyBatchToolbar = `
        <div class="card batch-toolbar-card ${{storyBatchCount ? "selection-live" : ""}}">
          <div class="batch-toolbar">
            <div class="batch-toolbar-head">
              <div>
                <div class="mono">${{copy("story batch", "故事批量操作")}}</div>
                <div class="panel-sub">${{
                  storyBatchCount
                    ? copy(`Selected ${{storyBatchCount}} stories. Move them together to reduce workspace churn.`, `已选 ${{storyBatchCount}} 条故事，可以一起切换状态。`)
                    : copy("Select visible stories when you need to archive, monitor, or resolve a whole lane together.", "当你需要整体归档、恢复监控或批量解决时，可以先选择当前可见故事。")
                }}</div>
              </div>
              <span class="chip ${{storyBatchCount ? "ok" : ""}}">${{copy("selected", "已选")}}=${{storyBatchCount}}</span>
            </div>
            ${{
              storyBatchCount
                ? `<div class="actions">
                    <button class="btn-secondary" type="button" data-story-selection-clear ${{storyBatchBusy ? "disabled" : ""}}>${{copy("Clear Selection", "清空选择")}}</button>
                    <button class="btn-secondary" type="button" data-story-batch-status="monitoring" ${{storyBatchBusy ? "disabled" : ""}}>${{copy("Batch Monitor", "批量监控")}}</button>
                    <button class="btn-secondary" type="button" data-story-batch-status="resolved" ${{storyBatchBusy ? "disabled" : ""}}>${{copy("Batch Resolve", "批量解决")}}</button>
                    <button class="btn-secondary" type="button" data-story-batch-status="archived" ${{storyBatchBusy ? "disabled" : ""}}>${{copy("Batch Archive", "批量归档")}}</button>
                  </div>`
                : `<div class="actions">
                    <button class="btn-secondary" type="button" data-story-select-visible ${{(!filteredStories.length || storyBatchBusy) ? "disabled" : ""}}>${{copy("Select Visible", "选择当前列表")}}</button>
                  </div>`
            }}
          </div>
        </div>
      `;
      if (!state.stories.length) {{
        root.innerHTML = `${{storySearchCard}}${{storyBatchToolbar}}${{renderLifecycleGuideCard({{
          title: copy("Promote verified signal into a story without leaving the browser", "无需离开浏览器，也能把已核验信号提升为故事"),
          summary: copy(
            "Use Story Intake for a manual brief, or create a story from Triage once the queue has enough evidence. Story edits, evidence review, and route setup can all stay inside this shell.",
            "可以用故事录入先写一条手工简报，也可以在分诊证据足够时直接提升成故事。后续的故事编辑、证据回查和路由设置都可以继续留在这个界面里完成。"
          ),
          steps: [
            {{
              title: copy("Start From Triage", "从分诊开始"),
              copy: copy("Create Story is the fastest path when verified inbox evidence already exists.", "如果收件箱里已经有已核验证据，直接创建故事是最快路径。"),
            }},
            {{
              title: copy("Or Seed Manually", "或手工起稿"),
              copy: copy("Story Intake is better when the narrative needs to exist before clustering catches up.", "如果叙事需要先存在、而聚类还没跟上，故事录入会更合适。"),
            }},
            {{
              title: copy("Refine In Workspace", "在工作台完善"),
              copy: copy("Tune title, summary, status, contradictions, and evidence context here.", "标题、摘要、状态、冲突点和证据上下文都可以在这里继续完善。"),
            }},
            {{
              title: copy("Link Delivery", "连接交付"),
              copy: copy("Attach named routes from missions once the story is ready for downstream notification.", "当故事准备好通知下游时，再从任务里把命名路由接上。"),
            }},
          ],
          actions: [
            {{ label: copy("Focus Story Intake", "聚焦故事录入"), focus: "story", field: "title", primary: true }},
            {{ label: copy("Open Triage", "打开分诊"), section: "section-triage" }},
            {{ label: copy("Open Route Manager", "打开路由管理"), focus: "route", field: "name" }},
          ],
        }})}}<div class="empty">${{copy("No story snapshot yet.", "当前还没有故事快照。")}}</div>`;
        wireLifecycleGuideActions(root);
        root.querySelector("[data-story-deck-focus]")?.addEventListener("click", () => {{
          focusStoryDeck("title");
        }});
        root.querySelector("[data-story-search]")?.addEventListener("input", (event) => {{
          state.storySearch = event.target.value;
          renderStories();
        }});
        root.querySelector("[data-story-search-clear]")?.addEventListener("click", () => {{
          state.storySearch = "";
          renderStories();
        }});
        root.querySelector("[data-story-sort]")?.addEventListener("change", (event) => {{
          state.storySort = normalizeStorySort(event.target.value);
          persistStoryWorkspacePrefs();
          renderStories();
        }});
        root.querySelectorAll("[data-story-view]").forEach((button) => {{
          button.addEventListener("click", () => {{
            applyStoryViewPreset(String(button.dataset.storyView || "").trim());
          }});
        }});
        root.querySelectorAll("[data-story-filter]").forEach((button) => {{
          button.addEventListener("click", () => {{
            state.storyFilter = normalizeStoryFilter(button.dataset.storyFilter);
            persistStoryWorkspacePrefs();
            renderStories();
          }});
        }});
        syncStoryUrlState({{ defaultStoryId }});
        flushStoryUrlFocus();
        renderTopbarContext();
        renderStoryDetail();
        return;
      }}
      if (filteredStories.length && !filteredStories.some((story) => story.id === state.selectedStoryId)) {{
        state.selectedStoryId = filteredStories[0].id;
      }}
      if (!filteredStories.length) {{
        state.selectedStoryId = "";
        root.innerHTML = `${{storySearchCard}}${{storyBatchToolbar}}<div class="empty">${{copy("No story matched the current search or filter.", "没有故事匹配当前搜索或筛选。")}}</div>`;
        renderStoryDetail();
        root.querySelector("[data-story-deck-focus]")?.addEventListener("click", () => {{
          focusStoryDeck("title");
        }});
        root.querySelector("[data-story-search]")?.addEventListener("input", (event) => {{
          state.storySearch = event.target.value;
          renderStories();
        }});
        root.querySelector("[data-story-search-clear]")?.addEventListener("click", () => {{
          state.storySearch = "";
          renderStories();
        }});
        root.querySelector("[data-story-sort]")?.addEventListener("change", (event) => {{
          state.storySort = normalizeStorySort(event.target.value);
          persistStoryWorkspacePrefs();
          renderStories();
        }});
        root.querySelectorAll("[data-story-view]").forEach((button) => {{
          button.addEventListener("click", () => {{
            applyStoryViewPreset(String(button.dataset.storyView || "").trim());
          }});
        }});
        root.querySelectorAll("[data-story-filter]").forEach((button) => {{
          button.addEventListener("click", () => {{
            state.storyFilter = normalizeStoryFilter(button.dataset.storyFilter);
            persistStoryWorkspacePrefs();
            renderStories();
          }});
        }});
        syncStoryUrlState({{ defaultStoryId }});
        flushStoryUrlFocus();
        renderTopbarContext();
        return;
      }}
      root.innerHTML = `${{storySearchCard}}${{storyBatchToolbar}}${{filteredStories.map((story) => {{
        const selected = story.id === state.selectedStoryId ? "selected" : "";
        const primary = (story.primary_evidence || [])[0];
        const updatedLabel = formatCompactDateTime(story.updated_at || story.generated_at || "");
        const priority = describeStoryPriority(story);
        const deliveryStatus = getStoryDeliveryStatus(story);
        const actionHierarchy = getStoryCardActionHierarchy(story);
        return `
          <div class="card selectable ${{selected}}" data-story-card="${{story.id}}">
            <div class="card-top">
              <div>
                <label class="checkbox-inline" style="margin-bottom:8px;">
                  <input type="checkbox" data-story-select="${{story.id}}" ${{isStorySelected(story.id) ? "checked" : ""}}>
                  <span>${{copy("select", "选择")}}</span>
                </label>
                <h3 class="card-title">${{story.title}}</h3>
                <div class="meta">
                  <span>${{story.id}}</span>
                  <span>${{copy("status", "状态")}}=${{localizeWord(story.status || "active")}}</span>
                  <span>${{copy("updated", "更新")}}=${{updatedLabel}}</span>
                </div>
                <div class="meta">
                  <span>${{copy("items", "条目")}}=${{story.item_count || 0}}</span>
                  <span>${{copy("sources", "来源")}}=${{story.source_count || 0}}</span>
                  <span>${{copy("score", "分数")}}=${{Number(story.score || 0).toFixed(1)}}</span>
                  <span>${{copy("confidence", "置信度")}}=${{Number(story.confidence || 0).toFixed(2)}}</span>
                </div>
              </div>
              <span class="chip ${{(story.contradictions || []).length ? "hot" : "ok"}}">${{(story.contradictions || []).length ? copy("mixed", "冲突") : copy("aligned", "一致")}}</span>
            </div>
            <div class="panel-sub">${{story.summary || copy("No summary captured.", "没有记录到摘要。")}}</div>
            <div class="entity-row">
              <span class="chip ${{priority.tone}}">${{priority.label}}</span>
              ${{(story.entities || []).slice(0, 4).map((entity) => `<span class="chip">${{entity}}</span>`).join("") || `<span class="chip">${{copy("no entities", "无实体")}}</span>`}}
            </div>
            <div class="meta">
              <span>${{copy("primary", "主证据")}}=${{primary ? primary.title : "-"}}</span>
              <span>${{copy("timeline", "时间线")}}=${{(story.timeline || []).length}}</span>
              <span>${{copy("conflicts", "冲突")}}=${{(story.contradictions || []).length}}</span>
              <span>${{copy("delivery", "交付")}}=${{deliveryStatus.label}}</span>
            </div>
            ${{renderCardActionHierarchy(actionHierarchy)}}
          </div>
        `;
      }}).join("")}}`;

      root.querySelector("[data-story-deck-focus]")?.addEventListener("click", () => {{
        focusStoryDeck("title");
      }});

      root.querySelector("[data-story-search]")?.addEventListener("input", (event) => {{
        state.storySearch = event.target.value;
        renderStories();
      }});

      root.querySelector("[data-story-search-clear]")?.addEventListener("click", () => {{
        state.storySearch = "";
        renderStories();
      }});

      root.querySelector("[data-story-sort]")?.addEventListener("change", (event) => {{
        state.storySort = normalizeStorySort(event.target.value);
        persistStoryWorkspacePrefs();
        renderStories();
      }});

      root.querySelectorAll("[data-story-view]").forEach((button) => {{
        button.addEventListener("click", () => {{
          applyStoryViewPreset(String(button.dataset.storyView || "").trim());
        }});
      }});

      root.querySelector("[data-story-select-visible]")?.addEventListener("click", () => {{
        selectVisibleStories(filteredStories);
        renderStories();
      }});

      root.querySelector("[data-story-selection-clear]")?.addEventListener("click", () => {{
        clearStorySelection();
        renderStories();
      }});

      root.querySelectorAll("[data-story-filter]").forEach((button) => {{
        button.addEventListener("click", () => {{
          state.storyFilter = normalizeStoryFilter(button.dataset.storyFilter);
          persistStoryWorkspacePrefs();
          renderStories();
        }});
      }});

      root.querySelectorAll("[data-story-batch-status]").forEach((button) => {{
        button.addEventListener("click", async () => {{
          button.disabled = true;
          try {{
            await runStoryBatchStatusUpdate(state.selectedStoryIds, String(button.dataset.storyBatchStatus || "").trim());
          }} catch (error) {{
            reportError(error, copy("Batch update stories", "批量更新故事"));
          }} finally {{
            button.disabled = false;
          }}
        }});
      }});

      root.querySelectorAll("[data-story-card]").forEach((card) => {{
        card.addEventListener("click", (event) => {{
          if (event.target.closest("button, textarea, input, select, a, form, label")) {{
            return;
          }}
          state.selectedStoryId = String(card.dataset.storyCard || "").trim();
          renderStories();
        }});
      }});

      root.querySelectorAll("[data-story-select]").forEach((input) => {{
        input.addEventListener("change", () => {{
          toggleStorySelection(String(input.dataset.storySelect || "").trim(), input.checked);
          renderStories();
        }});
      }});

      root.querySelectorAll("[data-story-open]").forEach((button) => {{
        button.addEventListener("click", async () => {{
          button.disabled = true;
          try {{
            const requestedMode = String(button.dataset.storyOpenMode || "").trim();
            await loadStory(button.dataset.storyOpen, {{
              mode: requestedMode || undefined,
              syncUrl: true,
            }});
          }} catch (error) {{
            reportError(error, copy("Open story", "打开故事"));
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
            reportError(error, copy("Preview story markdown", "预览故事 Markdown"));
          }} finally {{
            button.disabled = false;
          }}
        }});
      }});

      root.querySelectorAll("[data-story-quick-status]").forEach((button) => {{
        button.addEventListener("click", async () => {{
          button.disabled = true;
          try {{
            await setStoryStatusQuick(
              String(button.dataset.storyQuickStatus || ""),
              String(button.dataset.storyNextStatus || ""),
            );
          }} catch (error) {{
            reportError(error, copy("Update story state", "更新故事状态"));
          }} finally {{
            button.disabled = false;
          }}
        }});
      }});

      syncStoryUrlState({{ defaultStoryId }});
      flushStoryUrlFocus();
      renderTopbarContext();
      renderStoryDetail();
    }}

    function renderReportQualityBlock(quality) {{
      if (!quality || typeof quality !== "object") {{
        return `<div class="empty">${{copy("No quality snapshot yet. Refresh the report composition to inspect guardrails.", "还没有质量快照。刷新一次报告编排后再查看门禁。")}}</div>`;
      }}
      const checks = quality.checks && typeof quality.checks === "object" ? quality.checks : {{}};
      const renderedChecks = Object.entries(checks).length
        ? Object.entries(checks).map(([key, check]) => {{
            const status = String(check?.status || "draft").trim().toLowerCase();
            const issues = Array.isArray(check?.issues)
              ? check.issues
              : (Array.isArray(check?.entries) ? check.entries : []);
            const summaryPairs = check?.summary && typeof check.summary === "object"
              ? Object.entries(check.summary)
              : [];
            return `
              <div class="card">
                <div class="card-top">
                  <div>
                    <h3 class="card-title">${{escapeHtml(formatReportCheckLabel(key))}}</h3>
                    <div class="meta">
                      <span>${{copy("status", "状态")}}=${{escapeHtml(localizeWord(status || "draft"))}}</span>
                      ${{summaryPairs.map(([summaryKey, summaryValue]) => `<span>${{escapeHtml(String(summaryKey).replace(/_/g, " "))}}=${{escapeHtml(String(summaryValue))}}</span>`).join("")}}
                    </div>
                  </div>
                  <span class="chip ${{reportStatusTone(status)}}">${{escapeHtml(localizeWord(status || "draft"))}}</span>
                </div>
                <div class="stack">
                  ${{issues.length
                    ? issues.slice(0, 4).map((issue) => `
                        <div class="card">
                          <div class="panel-sub">${{escapeHtml(issue.detail || issue.kind || JSON.stringify(issue))}}</div>
                        </div>
                      `).join("")
                    : `<div class="empty">${{copy("No blocking issue recorded for this gate.", "这个门禁当前没有阻断问题。")}}</div>`}}
                </div>
              </div>
            `;
          }}).join("")
        : `<div class="empty">${{copy("No guardrail checks were returned.", "当前没有返回质量门禁检查。")}}</div>`;

      return `
        <div class="card">
          <div class="card-top">
            <div>
              <h3 class="card-title">${{copy("Quality Guardrails", "质量门禁")}}</h3>
              <div class="meta">
                <span>${{copy("status", "状态")}}=${{escapeHtml(localizeWord(quality.status || "draft"))}}</span>
                <span>${{copy("score", "分数")}}=${{escapeHtml(Number(quality.score || 0).toFixed(2))}}</span>
                <span>${{copy("action", "动作")}}=${{escapeHtml(formatReportOperatorAction(quality.operator_action || ""))}}</span>
              </div>
            </div>
            <span class="chip ${{reportStatusTone(quality.status)}}">${{quality.can_export ? copy("export ready", "可导出") : copy("hold", "暂停")}}</span>
          </div>
          <div class="panel-sub">${{quality.can_export
            ? copy("The current report composition satisfies the visible guardrails.", "当前报告编排满足可见质量门禁。")
            : copy("Resolve the highlighted guardrails before treating this report as ready.", "先解决下面标出的质量门禁，再把这份报告视为就绪。")}}</div>
        </div>
        <div class="stack">${{renderedChecks}}</div>
      `;
    }}

    function renderClaimsWorkspace() {{
      const root = $("claim-composer-shell");
      if (!root) {{
        return;
      }}
      if (state.loading.board && !state.claimCards.length && !state.reports.length) {{
        root.innerHTML = [skeletonCard(4), skeletonCard(4)].join("");
        return;
      }}
      syncReportSelectionState();
      const selectedReport = getSelectedReportRecord();
      const selectedSection = getSelectedReportSectionRecord();
      const selectedClaim = getSelectedClaimCard();
      const selectedQuality = getReportComposition(selectedReport?.id || "")?.quality || null;
      const sections = getReportSectionsForReport(selectedReport?.id || "");
      const reportClaimIds = new Set(getReportClaimIds(selectedReport?.id || ""));
      const selectedSectionClaimIds = new Set(Array.isArray(selectedSection?.claim_card_ids) ? selectedSection.claim_card_ids : []);
      const selectedClaimBundles = Array.isArray(selectedClaim?.citation_bundle_ids)
        ? selectedClaim.citation_bundle_ids.map((bundleId) => getCitationBundleRecord(bundleId)).filter(Boolean)
        : [];
      const selectedClaimSources = uniqueValues([
        ...(Array.isArray(selectedClaim?.source_item_ids) ? selectedClaim.source_item_ids : []),
        ...selectedClaimBundles.flatMap((bundle) => Array.isArray(bundle.source_item_ids) ? bundle.source_item_ids : []),
      ]);
      const selectedClaimUrls = uniqueValues(selectedClaimBundles.flatMap((bundle) => Array.isArray(bundle.source_urls) ? bundle.source_urls : []));
      const claimRows = state.claimCards.length
        ? state.claimCards.map((claim) => {{
            const claimId = String(claim.id || "").trim();
            const claimLabel = getClaimCardLabel(claim) || claimId;
            const isSelected = claimId === String(state.selectedClaimId || "").trim();
            const inReport = reportClaimIds.has(claimId);
            const inSection = selectedSectionClaimIds.has(claimId);
            return `
              <div class="card">
                <div class="card-top">
                  <div>
                    <h3 class="card-title">${{escapeHtml(claimLabel)}}</h3>
                    <div class="meta">
                      <span>${{claimId}}</span>
                      <span>${{copy("status", "状态")}}=${{escapeHtml(localizeWord(claim.status || "draft"))}}</span>
                      <span>${{copy("confidence", "置信度")}}=${{escapeHtml(Number(claim.confidence || 0).toFixed(2))}}</span>
                    </div>
                  </div>
                  <span class="chip ${{isSelected ? "ok" : reportStatusTone(claim.status)}}">${{escapeHtml(localizeWord(claim.status || "draft"))}}</span>
                </div>
                <div class="panel-sub">${{escapeHtml(claim.rationale || copy("No rationale captured yet.", "当前还没有记录理由。"))}}</div>
                <div class="meta">
                  <span class="chip ${{inReport ? "ok" : ""}}">${{inReport ? copy("in report", "已挂入报告") : copy("unassigned", "未挂接")}}</span>
                  <span class="chip ${{inSection ? "ok" : ""}}">${{selectedSection ? (inSection ? copy("in section", "已挂入章节") : copy("outside section", "未挂入章节")) : copy("report only", "仅报告级")}}</span>
                </div>
                <div class="actions">
                  <button class="btn-secondary" type="button" data-claim-select="${{claimId}}">${{copy("Inspect", "查看")}}</button>
                  <button class="btn-secondary" type="button" data-claim-attach="${{claimId}}" ${{selectedReport ? "" : "disabled"}}>${{selectedSection ? copy("Attach To Section", "挂到章节") : copy("Attach To Report", "挂到报告")}}</button>
                </div>
              </div>
            `;
          }}).join("")
        : `<div class="empty">${{copy("No claim cards yet. Create the first source-bound claim on the left.", "当前还没有主张卡。先在左侧创建第一条带来源的主张。")}}</div>`;

      root.innerHTML = `
        <div class="story-columns">
          <div class="stack">
            <div class="card">
              <div class="card-top">
                <div>
                  <h3 class="card-title">${{copy("Current Composition Target", "当前编排目标")}}</h3>
                  <div class="meta">
                    <span>${{copy("report", "报告")}}=${{escapeHtml(selectedReport ? (selectedReport.title || selectedReport.id) : copy("not set", "未设置"))}}</span>
                    <span>${{copy("section", "章节")}}=${{escapeHtml(selectedSection ? (selectedSection.title || selectedSection.id) : copy("report level", "报告级"))}}</span>
                    <span>${{copy("quality", "质量")}}=${{escapeHtml(selectedQuality ? localizeWord(selectedQuality.status || "draft") : copy("not loaded", "未加载"))}}</span>
                  </div>
                </div>
                <span class="chip ${{reportStatusTone(selectedQuality?.status || selectedReport?.status || "")}}">${{escapeHtml(localizeWord(selectedQuality?.status || selectedReport?.status || "draft"))}}</span>
              </div>
              <div class="panel-sub">${{selectedReport
                ? copy("Claims stay report-backed. Pick a section when the judgment should appear inside a specific narrative block.", "主张始终绑定到持久化报告。只有在需要进入具体叙事块时，再选择某个章节。")
                : copy("Choose or create a report in Report Studio, then come back to bind claims into sections.", "先去报告工作台选择或创建一份报告，再回来把主张挂进章节。")}}</div>
              <div class="field-grid" style="margin-top:12px;">
                <label>${{copy("Report", "报告")}}
                  <select id="claim-report-select">
                    <option value="">${{copy("No report selected", "未选择报告")}}</option>
                    ${{state.reports.map((report) => `<option value="${{escapeHtml(report.id)}}" ${{String(report.id || "") === String(state.selectedReportId || "") ? "selected" : ""}}>${{escapeHtml(report.title || report.id)}}</option>`).join("")}}
                  </select>
                </label>
                <label>${{copy("Section", "章节")}}
                  <select id="claim-section-select" ${{selectedReport ? "" : "disabled"}}>
                    <option value="">${{copy("Attach at report level", "挂到报告级")}}</option>
                    ${{sections.map((section) => `<option value="${{escapeHtml(section.id)}}" ${{String(section.id || "") === String(state.selectedReportSectionId || "") ? "selected" : ""}}>${{escapeHtml(section.title || section.id)}}</option>`).join("")}}
                  </select>
                </label>
              </div>
              <div class="actions">
                <button class="btn-secondary" type="button" data-claims-open-report-studio>${{copy("Open Report Studio", "打开报告工作台")}}</button>
                ${{selectedReport ? `<a href="/api/reports/${{selectedReport.id}}" target="_blank" rel="noreferrer">${{copy("Open Report JSON", "打开报告 JSON")}}</a>` : ""}}
              </div>
            </div>

            <div class="card">
              <div class="card-top">
                <div>
                  <h3 class="card-title">${{copy("Create Claim", "创建主张")}}</h3>
                  <div class="panel-sub">${{copy("Capture the bounded judgment here, then persist its source binding immediately.", "先记录边界明确的判断，再立即把来源绑定写进去。")}}</div>
                </div>
                <span class="chip ok">${{copy("persisted", "持久化")}}</span>
              </div>
              <form id="claim-composer-form" style="margin-top:12px;">
                <label>${{copy("Statement", "主张语句")}}<textarea name="statement" rows="3" placeholder="${{copy("AI adoption is landing first in quantity takeoff and schedule control.", "AI 最先在算量和计划控制环节跑通。")}}"></textarea></label>
                <label>${{copy("Rationale", "理由")}}<textarea name="rationale" rows="3" placeholder="${{copy("State the boundary, evidence pattern, or operational reason behind the claim.", "记录这个主张背后的边界、证据模式或业务理由。")}}"></textarea></label>
                <div class="field-grid">
                  <label>${{copy("Confidence", "置信度")}}<input name="confidence" type="number" min="0" max="1" step="0.01" value="0.8"></label>
                  <label>${{copy("Status", "状态")}}
                    <select name="status">
                      ${{claimStatusOptions.map((status) => `<option value="${{status}}">${{localizeWord(status)}}</option>`).join("")}}
                    </select>
                  </label>
                </div>
                <label>${{copy("Source Item IDs", "来源条目 ID")}}<input name="source_item_ids" placeholder="${{copy("item-123, item-456", "item-123, item-456")}}"><span class="field-hint">${{copy("Use commas or new lines when the claim already points to stored inbox items.", "如果主张已经对应到已存储条目，可以用逗号或换行补充 item ID。")}}</span></label>
                <label>${{copy("Source URLs", "来源 URL")}}<textarea name="source_urls" rows="3" placeholder="${{copy("https://example.com/source-a", "https://example.com/source-a")}}"></textarea><span class="field-hint">${{copy("URLs create a citation bundle so the claim stays source-bound even before every item is normalized into inbox IDs.", "URL 会生成 citation bundle，这样即使条目还没完全落进 inbox ID，主张也能保持来源绑定。")}}</span></label>
                <label>${{copy("Citation Note", "引用备注")}}<input name="bundle_note" placeholder="${{copy("Why these sources support the claim", "说明这些来源为什么支撑该主张")}}"></label>
                <div class="toolbar">
                  <button class="btn-primary" type="submit">${{copy("Create Claim", "创建主张")}}</button>
                  <button class="btn-secondary" type="button" data-claim-form-focus-report-studio>${{copy("Need A Report First", "先去创建报告")}}</button>
                </div>
              </form>
            </div>

            <div class="card">
              <div class="card-top">
                <div>
                  <h3 class="card-title">${{copy("Selected Claim", "当前主张")}}</h3>
                  <div class="meta">
                    <span>${{escapeHtml(selectedClaim ? (selectedClaim.id || "-") : "-")}}</span>
                  <span>${{copy("bundles", "引用包")}}=${{selectedClaimBundles.length}}</span>
                  <span>${{copy("sources", "来源")}}=${{selectedClaimSources.length + selectedClaimUrls.length}}</span>
                </div>
              </div>
                <span class="chip ${{reportStatusTone(selectedClaim?.status || "")}}">${{escapeHtml(localizeWord(selectedClaim?.status || "draft"))}}</span>
              </div>
              ${{selectedClaim
                ? `
                  <div class="panel-sub">${{escapeHtml(selectedClaim.rationale || copy("No rationale captured yet.", "当前还没有记录理由。"))}}</div>
                  <div class="meta">
                    ${{selectedClaimSources.map((value) => `<span class="chip ok">${{escapeHtml(value)}}</span>`).join("") || `<span class="chip">${{copy("no direct item id", "没有直接 item id")}}</span>`}}
                    ${{selectedClaimUrls.map((value) => `<span class="chip" data-fit-text="claim-url-chip" data-fit-max-width="210" data-fit-fallback="42">${{escapeHtml(value)}}</span>`).join("")}}
                  </div>
                `
                : `<div class="empty">${{copy("Pick one claim from the right rail to inspect its binding and reuse it in the current section.", "先从右侧选中一条主张，再查看它的来源绑定并复用到当前章节。")}}</div>`}}
            </div>
          </div>

          <div class="stack">
            <div class="meta">
              <span class="mono">${{copy("claim inventory", "主张库存")}}</span>
              <span class="chip">${{copy("selected", "已选")}}=${{selectedClaim ? 1 : 0}}</span>
              <span class="chip ok">${{copy("report claims", "报告内主张")}}=${{reportClaimIds.size}}</span>
            </div>
            ${{claimRows}}
          </div>
        </div>
      `;

      root.querySelector("#claim-report-select")?.addEventListener("change", async (event) => {{
        state.selectedReportSectionId = "";
        await selectReport(String(event.target.value || "").trim());
      }});
      root.querySelector("#claim-section-select")?.addEventListener("change", (event) => {{
        state.selectedReportSectionId = String(event.target.value || "").trim();
        renderClaimsWorkspace();
        renderReportStudio();
        renderTopbarContext();
      }});
      root.querySelector("[data-claims-open-report-studio]")?.addEventListener("click", () => {{
        jumpToSection("section-report-studio");
      }});
      root.querySelector("[data-claim-form-focus-report-studio]")?.addEventListener("click", () => {{
        jumpToSection("section-report-studio");
      }});
      root.querySelector("#claim-composer-form")?.addEventListener("submit", async (event) => {{
        event.preventDefault();
        const form = new FormData(event.target);
        const statement = String(form.get("statement") || "").trim();
        if (!statement) {{
          showToast(copy("Provide a claim statement before saving.", "保存前请先填写主张语句。"), "error");
          return;
        }}
        const reportId = String(state.selectedReportId || form.get("report_id") || "").trim();
        const sectionId = String(state.selectedReportSectionId || "").trim();
        const sourceItemIds = parseDelimitedInput(form.get("source_item_ids"));
        const sourceUrls = parseDelimitedInput(form.get("source_urls"));
        const rationale = String(form.get("rationale") || "").trim();
        const status = String(form.get("status") || "draft").trim().toLowerCase() || "draft";
        const confidence = Number(form.get("confidence") || 0);
        const selectedReportRecord = getReportRecord(reportId);
        const submitButton = event.target.querySelector("button[type='submit']");
        if (submitButton) {{
          submitButton.disabled = true;
        }}
        try {{
          let createdClaim = await api("/api/claim-cards", {{
            method: "POST",
            headers: jsonHeaders,
            body: JSON.stringify({{
              statement,
              rationale,
              confidence,
              status,
              brief_id: String(selectedReportRecord?.brief_id || "").trim(),
              source_item_ids: sourceItemIds,
            }}),
          }});
          let createdBundleId = "";
          const bundleNote = String(form.get("bundle_note") || "").trim();
          if (sourceUrls.length || sourceItemIds.length) {{
            const bundle = await api("/api/citation-bundles", {{
              method: "POST",
              headers: jsonHeaders,
              body: JSON.stringify({{
                claim_card_id: createdClaim.id,
                label: `${{statement.slice(0, 42)}} ${{copy("sources", "来源")}}`,
                source_item_ids: sourceItemIds,
                source_urls: sourceUrls,
                note: bundleNote,
              }}),
            }});
            createdBundleId = String(bundle.id || "").trim();
            createdClaim = await api(`/api/claim-cards/${{createdClaim.id}}`, {{
              method: "PUT",
              headers: jsonHeaders,
              body: JSON.stringify({{
                source_item_ids: sourceItemIds,
                citation_bundle_ids: uniqueValues([...(Array.isArray(createdClaim.citation_bundle_ids) ? createdClaim.citation_bundle_ids : []), createdBundleId]),
              }}),
            }});
          }}
          if (reportId) {{
            await attachClaimToReport(createdClaim.id, reportId, sectionId, createdBundleId);
          }}
          state.selectedClaimId = String(createdClaim.id || "").trim();
          if (reportId) {{
            state.selectedReportId = reportId;
          }}
          if (sectionId) {{
            state.selectedReportSectionId = sectionId;
          }}
          await refreshBoard();
          showToast(
            state.language === "zh"
              ? `主张已创建：${{statement}}`
              : `Claim created: ${{statement}}`,
            "success",
          );
        }} catch (error) {{
          reportError(error, copy("Create claim", "创建主张"));
        }} finally {{
          if (submitButton) {{
            submitButton.disabled = false;
          }}
        }}
      }});
      root.querySelectorAll("[data-claim-select]").forEach((button) => {{
        button.addEventListener("click", () => {{
          state.selectedClaimId = String(button.dataset.claimSelect || "").trim();
          renderClaimsWorkspace();
          renderReportStudio();
          renderTopbarContext();
        }});
      }});
      root.querySelectorAll("[data-claim-attach]").forEach((button) => {{
        button.addEventListener("click", async () => {{
          const claimId = String(button.dataset.claimAttach || "").trim();
          const reportId = String(state.selectedReportId || "").trim();
          const sectionId = String(state.selectedReportSectionId || "").trim();
          if (!claimId || !reportId) {{
            return;
          }}
          button.disabled = true;
          try {{
            await attachClaimToReport(claimId, reportId, sectionId);
            state.selectedClaimId = claimId;
            await refreshBoard();
            showToast(copy("Claim attached to the current report target.", "主张已挂接到当前报告目标。"), "success");
          }} catch (error) {{
            reportError(error, copy("Attach claim", "挂接主张"));
          }} finally {{
            button.disabled = false;
          }}
        }});
      }});
      scheduleCanvasTextFit(root);
    }}

    function renderReportStudio() {{
      const root = $("report-studio-shell");
      if (!root) {{
        return;
      }}
      if (state.loading.board && !state.reports.length) {{
        root.innerHTML = [skeletonCard(4), skeletonCard(4)].join("");
        return;
      }}
      syncReportSelectionState();
      const selectedReport = getSelectedReportRecord();
      const composition = getReportComposition(selectedReport?.id || "");
      const quality = composition?.quality || null;
      const sections = composition?.sections && Array.isArray(composition.sections)
        ? composition.sections
        : getReportSectionsForReport(selectedReport?.id || "");
      const claims = composition?.claim_cards && Array.isArray(composition.claim_cards)
        ? composition.claim_cards
        : state.claimCards.filter((claim) => getReportClaimIds(selectedReport?.id || "").includes(String(claim.id || "").trim()));
      const exportProfiles = state.exportProfiles.filter((profile) => String(profile.report_id || "").trim() === String(selectedReport?.id || "").trim());
      const markdownPreview = String(state.reportMarkdown[selectedReport?.id || ""] || "").trim();
      const sectionRows = sections.length
        ? sections.map((section) => {{
            const sectionClaimIds = Array.isArray(section.claim_card_ids) ? section.claim_card_ids : [];
            const sectionClaims = sectionClaimIds
              .map((claimId) => claims.find((claim) => String(claim.id || "").trim() === String(claimId || "").trim()) || getClaimCardRecord(claimId))
              .filter(Boolean);
            return `
              <div class="card">
                <div class="card-top">
                  <div>
                    <h3 class="card-title">${{escapeHtml(section.title || section.id)}}</h3>
                    <div class="meta">
                      <span>${{copy("position", "位置")}}=${{escapeHtml(String(section.position || 0))}}</span>
                      <span>${{copy("status", "状态")}}=${{escapeHtml(localizeWord(section.status || "draft"))}}</span>
                      <span>${{copy("claims", "主张")}}=${{sectionClaimIds.length}}</span>
                    </div>
                  </div>
                  <span class="chip ${{reportStatusTone(section.status)}}">${{escapeHtml(localizeWord(section.status || "draft"))}}</span>
                </div>
                <div class="panel-sub">${{escapeHtml(section.summary || copy("No section summary yet.", "当前还没有章节摘要。"))}}</div>
                <div class="meta">
                  ${{sectionClaims.length
                    ? sectionClaims.map((claim) => `<span class="chip ok" data-fit-text="report-section-claim-chip" data-fit-max-width="198" data-fit-fallback="32">${{escapeHtml(getClaimCardLabel(claim))}}</span>`).join("")
                    : `<span class="chip hot">${{copy("no claims attached", "当前没有挂接主张")}}</span>`}}
                </div>
                <div class="actions">
                  <button class="btn-secondary" type="button" data-report-section-focus="${{escapeHtml(section.id)}}">${{copy("Focus In Claim Composer", "去主张装配")}}</button>
                </div>
              </div>
            `;
          }}).join("")
        : `<div class="empty">${{copy("No report section yet. Create one on the left, then bind claims into it.", "当前还没有章节。先在左侧创建一个章节，再把主张挂进去。")}}</div>`;

      root.innerHTML = `
        <div class="story-columns">
          <div class="stack">
            <div class="card">
              <div class="card-top">
                <div>
                  <h3 class="card-title">${{copy("Report Workspace", "报告工作区")}}</h3>
                  <div class="panel-sub">${{copy("The browser stays a projection over persisted report objects. No report-only browser state is hidden here.", "浏览器仍然只是持久化报告对象的投射，这里不会偷偷生成浏览器专属状态。")}}</div>
                </div>
                <span class="chip ${{reportStatusTone(quality?.status || selectedReport?.status || "")}}">${{escapeHtml(localizeWord(quality?.status || selectedReport?.status || "draft"))}}</span>
              </div>
              <div class="field-grid" style="margin-top:12px;">
                <label>${{copy("Current Report", "当前报告")}}
                  <select id="report-studio-select">
                    <option value="">${{copy("No report selected", "未选择报告")}}</option>
                    ${{state.reports.map((report) => `<option value="${{escapeHtml(report.id)}}" ${{String(report.id || "") === String(state.selectedReportId || "") ? "selected" : ""}}>${{escapeHtml(report.title || report.id)}}</option>`).join("")}}
                  </select>
                </label>
                <label>${{copy("Export Profiles", "导出配置")}}
                  <div class="meta">
                    ${{exportProfiles.length
                      ? exportProfiles.map((profile) => `<span class="chip ok">${{escapeHtml(profile.name || profile.id)}}</span>`).join("")
                      : `<span class="chip">${{copy("none yet", "暂无")}}</span>`}}
                  </div>
                </label>
              </div>
              <div class="actions">
                <button class="btn-secondary" type="button" data-report-compose-refresh ${{selectedReport ? "" : "disabled"}}>${{copy("Refresh Composition", "刷新编排")}}</button>
                <button class="btn-secondary" type="button" data-report-preview-markdown ${{selectedReport ? "" : "disabled"}}>${{copy("Preview Markdown", "预览 Markdown")}}</button>
                ${{selectedReport ? `<a href="/api/reports/${{selectedReport.id}}" target="_blank" rel="noreferrer">${{copy("Open JSON", "打开 JSON")}}</a>` : ""}}
                ${{selectedReport ? `<a href="/api/reports/${{selectedReport.id}}/export?output_format=markdown" target="_blank" rel="noreferrer">${{copy("Export MD", "导出 MD")}}</a>` : ""}}
              </div>
            </div>

            <div class="card">
              <div class="card-top">
                <div>
                  <h3 class="card-title">${{copy("Create Report", "创建报告")}}</h3>
                  <div class="panel-sub">${{copy("Start a persisted report shell first. Claim Composer can bind judgments into it immediately after.", "先创建一个持久化报告壳，再回到主张装配里把判断挂进去。")}}</div>
                </div>
              </div>
              <form id="report-create-form" style="margin-top:12px;">
                <div class="field-grid">
                  <label>${{copy("Title", "标题")}}<input name="title" placeholder="${{copy("AI Infrastructure Brief", "AI 基建调研报告")}}"></label>
                  <label>${{copy("Audience", "受众")}}<input name="audience" placeholder="${{copy("leadership", "管理层")}}"></label>
                </div>
                <label>${{copy("Summary", "摘要")}}<textarea name="summary" rows="3" placeholder="${{copy("Describe what this report is trying to help decide.", "描述这份报告希望帮助回答什么决策问题。")}}"></textarea></label>
                <div class="toolbar">
                  <button class="btn-primary" type="submit">${{copy("Create Report", "创建报告")}}</button>
                </div>
              </form>
            </div>

            <div class="card">
              <div class="card-top">
                <div>
                  <h3 class="card-title">${{copy("Report Editor", "报告编辑")}}</h3>
                  <div class="panel-sub">${{copy("Tune report metadata and keep the assembled surface aligned with the persisted object graph.", "调整报告元数据，并让浏览器展示继续和持久化对象图保持一致。")}}</div>
                </div>
              </div>
              ${{selectedReport
                ? `
                  <form id="report-editor-form" data-report-id="${{selectedReport.id}}" style="margin-top:12px;">
                    <div class="field-grid">
                      <label>${{copy("Title", "标题")}}<input name="title" value="${{escapeHtml(selectedReport.title || "")}}"></label>
                      <label>${{copy("Audience", "受众")}}<input name="audience" value="${{escapeHtml(selectedReport.audience || "")}}"></label>
                    </div>
                    <label>${{copy("Status", "状态")}}
                      <select name="status">
                        ${{reportStatusOptions.map((status) => `<option value="${{status}}" ${{String(selectedReport.status || "draft") === status ? "selected" : ""}}>${{localizeWord(status)}}</option>`).join("")}}
                      </select>
                    </label>
                    <label>${{copy("Summary", "摘要")}}<textarea name="summary" rows="4">${{escapeHtml(selectedReport.summary || "")}}</textarea></label>
                    <div class="toolbar">
                      <button class="btn-primary" type="submit">${{copy("Save Report", "保存报告")}}</button>
                      <button class="btn-secondary" type="button" data-report-jump-claims>${{copy("Open Claim Composer", "打开主张装配")}}</button>
                    </div>
                  </form>
                `
                : `<div class="empty">${{copy("Create or select a report to edit it here.", "先创建或选中一份报告，再在这里编辑。")}}</div>`}}
            </div>

            <div class="card">
              <div class="card-top">
                <div>
                  <h3 class="card-title">${{copy("Section Builder", "章节构建")}}</h3>
                  <div class="panel-sub">${{copy("Create one deterministic section, then bind claims into it from Claim Composer.", "先创建一个确定性的章节，再回到主张装配里把主张挂进去。")}}</div>
                </div>
              </div>
              ${{selectedReport
                ? `
                  <form id="report-section-form" data-report-id="${{selectedReport.id}}" style="margin-top:12px;">
                    <div class="field-grid">
                      <label>${{copy("Title", "标题")}}<input name="title" placeholder="${{copy("Executive Summary", "执行摘要")}}"></label>
                      <label>${{copy("Position", "位置")}}<input name="position" type="number" min="0" step="1" value="${{escapeHtml(String(sections.length + 1))}}"></label>
                    </div>
                    <label>${{copy("Section Summary", "章节摘要")}}<textarea name="summary" rows="3" placeholder="${{copy("What should this section conclude or frame?", "这个章节主要要承接什么判断或框架？")}}"></textarea></label>
                    <div class="toolbar">
                      <button class="btn-primary" type="submit">${{copy("Create Section", "创建章节")}}</button>
                    </div>
                  </form>
                `
                : `<div class="empty">${{copy("No report selected, so there is nowhere to attach a section yet.", "当前没有选中报告，因此还没有章节可挂接。")}}</div>`}}
            </div>
          </div>

          <div class="stack">
            ${{selectedReport ? renderReportQualityBlock(quality) : `<div class="empty">${{copy("Select one report to inspect guardrails, sections, and export preview.", "选中一份报告后，这里会显示质量门禁、章节结构和导出预览。")}}</div>`}}
            <div class="stack">
              <div class="meta">
                <span class="mono">${{copy("report sections", "报告章节")}}</span>
                <span class="chip ok">${{copy("count", "数量")}}=${{sections.length}}</span>
                <span class="chip">${{copy("claims", "主张")}}=${{claims.length}}</span>
              </div>
              ${{sectionRows}}
            </div>
            <div class="card">
              <div class="card-top">
                <div>
                  <h3 class="card-title">${{copy("Markdown Preview", "Markdown 预览")}}</h3>
                  <div class="panel-sub">${{copy("Use the same Reader-backed export surface the CLI and API already share.", "直接复用 CLI 和 API 已共享的 Reader-backed 导出面。")}}</div>
                </div>
              </div>
              ${{markdownPreview
                ? `<pre class="text-block">${{escapeHtml(markdownPreview)}}</pre>`
                : `<div class="empty">${{copy("No Markdown preview cached yet. Click Preview Markdown above.", "当前还没有缓存的 Markdown 预览。点击上方“预览 Markdown”即可。")}}</div>`}}
            </div>
          </div>
        </div>
      `;

      root.querySelector("#report-studio-select")?.addEventListener("change", async (event) => {{
        await selectReport(String(event.target.value || "").trim());
      }});
      root.querySelector("[data-report-compose-refresh]")?.addEventListener("click", async (event) => {{
        if (!selectedReport) {{
          return;
        }}
        const button = event.currentTarget;
        button.disabled = true;
        try {{
          await loadReportComposition(selectedReport.id);
          showToast(copy("Report composition refreshed.", "报告编排已刷新。"), "success");
        }} catch (error) {{
          reportError(error, copy("Refresh report composition", "刷新报告编排"));
        }} finally {{
          button.disabled = false;
        }}
      }});
      root.querySelector("[data-report-preview-markdown]")?.addEventListener("click", async (event) => {{
        if (!selectedReport) {{
          return;
        }}
        const button = event.currentTarget;
        button.disabled = true;
        try {{
          await previewReportMarkdown(selectedReport.id);
          showToast(copy("Markdown preview refreshed.", "Markdown 预览已刷新。"), "success");
        }} catch (error) {{
          reportError(error, copy("Preview report markdown", "预览报告 Markdown"));
        }} finally {{
          button.disabled = false;
        }}
      }});
      root.querySelector("#report-create-form")?.addEventListener("submit", async (event) => {{
        event.preventDefault();
        const form = new FormData(event.target);
        const title = String(form.get("title") || "").trim();
        if (!title) {{
          showToast(copy("Provide a report title before saving.", "保存前请先填写报告标题。"), "error");
          return;
        }}
        const payload = {{
          title,
          audience: String(form.get("audience") || "").trim(),
          summary: String(form.get("summary") || "").trim(),
        }};
        const submitButton = event.target.querySelector("button[type='submit']");
        if (submitButton) {{
          submitButton.disabled = true;
        }}
        try {{
          const created = await api("/api/reports", {{
            method: "POST",
            headers: jsonHeaders,
            body: JSON.stringify(payload),
          }});
          state.selectedReportId = String(created.id || "").trim();
          state.selectedReportSectionId = "";
          await refreshBoard();
          showToast(
            state.language === "zh"
              ? `报告已创建：${{title}}`
              : `Report created: ${{title}}`,
            "success",
          );
        }} catch (error) {{
          reportError(error, copy("Create report", "创建报告"));
        }} finally {{
          if (submitButton) {{
            submitButton.disabled = false;
          }}
        }}
      }});
      root.querySelector("#report-editor-form")?.addEventListener("submit", async (event) => {{
        event.preventDefault();
        if (!selectedReport) {{
          return;
        }}
        const form = new FormData(event.target);
        const payload = {{
          title: String(form.get("title") || "").trim(),
          audience: String(form.get("audience") || "").trim(),
          status: String(form.get("status") || "draft").trim().toLowerCase() || "draft",
          summary: String(form.get("summary") || "").trim(),
        }};
        if (!payload.title) {{
          showToast(copy("Provide a report title before saving.", "保存前请先填写报告标题。"), "error");
          return;
        }}
        const submitButton = event.target.querySelector("button[type='submit']");
        if (submitButton) {{
          submitButton.disabled = true;
        }}
        try {{
          await api(`/api/reports/${{selectedReport.id}}`, {{
            method: "PUT",
            headers: jsonHeaders,
            body: JSON.stringify(payload),
          }});
          await refreshBoard();
          showToast(copy("Report saved.", "报告已保存。"), "success");
        }} catch (error) {{
          reportError(error, copy("Save report", "保存报告"));
        }} finally {{
          if (submitButton) {{
            submitButton.disabled = false;
          }}
        }}
      }});
      root.querySelector("[data-report-jump-claims]")?.addEventListener("click", () => {{
        jumpToSection("section-claims");
      }});
      root.querySelector("#report-section-form")?.addEventListener("submit", async (event) => {{
        event.preventDefault();
        if (!selectedReport) {{
          return;
        }}
        const form = new FormData(event.target);
        const title = String(form.get("title") || "").trim();
        if (!title) {{
          showToast(copy("Provide a section title before saving.", "保存前请先填写章节标题。"), "error");
          return;
        }}
        const payload = {{
          report_id: selectedReport.id,
          title,
          position: Number(form.get("position") || sections.length + 1),
          summary: String(form.get("summary") || "").trim(),
        }};
        const submitButton = event.target.querySelector("button[type='submit']");
        if (submitButton) {{
          submitButton.disabled = true;
        }}
        try {{
          const created = await api("/api/report-sections", {{
            method: "POST",
            headers: jsonHeaders,
            body: JSON.stringify(payload),
          }});
          await api(`/api/reports/${{selectedReport.id}}`, {{
            method: "PUT",
            headers: jsonHeaders,
            body: JSON.stringify({{
              section_ids: uniqueValues([...(Array.isArray(selectedReport.section_ids) ? selectedReport.section_ids : []), created.id]),
            }}),
          }});
          state.selectedReportSectionId = String(created.id || "").trim();
          await refreshBoard();
          showToast(copy("Report section created.", "报告章节已创建。"), "success");
        }} catch (error) {{
          reportError(error, copy("Create report section", "创建报告章节"));
        }} finally {{
          if (submitButton) {{
            submitButton.disabled = false;
          }}
        }}
      }});
      root.querySelectorAll("[data-report-section-focus]").forEach((button) => {{
        button.addEventListener("click", () => {{
          state.selectedReportSectionId = String(button.dataset.reportSectionFocus || "").trim();
          renderClaimsWorkspace();
          renderReportStudio();
          renderTopbarContext();
          jumpToSection("section-claims");
        }});
      }});
      scheduleCanvasTextFit(root);
    }}

    async function refreshBoard() {{
      state.loading.board = true;
      renderOverview();
      renderWatches();
      renderWatchDetail();
      renderAlerts();
      renderRoutes();
      renderRouteHealth();
      renderDeliveryWorkspace();
      renderAiSurfaces();
      renderStatus();
      renderTriage();
      renderStories();
      renderClaimsWorkspace();
      renderReportStudio();
      try {{
        const [overview, watches, alerts, routes, routeHealth, deliverySubscriptions, deliveryDispatchRecords, digestConsole, status, ops, triage, triageStats, stories, reportBriefs, claimCards, citationBundles, reportSections, reports, exportProfiles, missionSuggestPrecheck, triageAssistPrecheck, claimDraftPrecheck] = await Promise.all([
          api("/api/overview"),
          api("/api/watches?include_disabled=true"),
          api("/api/alerts?limit=8"),
          api("/api/alert-routes"),
          api("/api/alert-routes/health?limit=60"),
          api("/api/delivery-subscriptions?limit=40"),
          api("/api/delivery-dispatch-records?limit=40"),
          api("/api/digest/console?profile=default&limit=8"),
          api("/api/watch-status"),
          api("/api/ops"),
          api("/api/triage?limit=12&include_closed=true"),
          api("/api/triage/stats"),
          api("/api/stories?limit=6&min_items=0"),
          api("/api/report-briefs?limit=20"),
          api("/api/claim-cards?limit=40"),
          api("/api/citation-bundles?limit=40"),
          api("/api/report-sections?limit=40"),
          api("/api/reports?limit=20"),
          api("/api/export-profiles?limit=40"),
          api("/api/ai/surfaces/mission_suggest/precheck?mode=assist"),
          api("/api/ai/surfaces/triage_assist/precheck?mode=assist"),
          api("/api/ai/surfaces/claim_draft/precheck?mode=assist"),
        ]);
        state.overview = overview;
        state.watches = watches;
        state.alerts = alerts;
        state.routes = routes;
        state.routeHealth = routeHealth;
        state.deliverySubscriptions = deliverySubscriptions;
        state.deliveryDispatchRecords = deliveryDispatchRecords;
        state.digestConsole = digestConsole;
        if (!state.digestProfileDraft) {{
          state.digestProfileDraft = normalizeDigestProfileDraft(digestConsole?.profile?.profile || defaultDigestProfileDraft());
        }}
        state.status = status;
        state.ops = ops;
        state.triage = triage;
        state.triageStats = triageStats;
        state.stories = stories;
        state.reportBriefs = reportBriefs;
        state.claimCards = claimCards;
        state.citationBundles = citationBundles;
        state.reportSections = reportSections;
        state.reports = reports;
        state.exportProfiles = exportProfiles;
        state.aiSurfacePrechecks = {{
          mission_suggest: missionSuggestPrecheck,
          triage_assist: triageAssistPrecheck,
          claim_draft: claimDraftPrecheck,
        }};
        if (state.watches.length) {{
          const selectedWatch = state.watches.some((watch) => watch.id === state.selectedWatchId)
            ? state.selectedWatchId
            : state.watches[0].id;
          state.selectedWatchId = selectedWatch;
          state.watchDetails[selectedWatch] = await api(`/api/watches/${{selectedWatch}}`);
        }} else {{
          state.selectedWatchId = "";
          setContextRouteName("", "");
        }}
        setContextRouteFromWatch();
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
        if (state.triage.length && !state.triage.some((item) => item.id === state.selectedTriageId)) {{
          state.selectedTriageId = state.triage[0].id;
        }}
        if (!state.triage.length) {{
          state.selectedTriageId = "";
        }}
        syncReportSelectionState();
        syncDeliverySelectionState();
        if (state.selectedReportId) {{
          state.reportCompositions[state.selectedReportId] = await api(`/api/reports/${{state.selectedReportId}}/compose`);
        }}
        const [missionSuggest, triageAssist, claimDraft] = await Promise.all([
          state.selectedWatchId
            ? api(`/api/watches/${{state.selectedWatchId}}/ai/mission-suggest?mode=assist`)
            : Promise.resolve(null),
          state.selectedTriageId
            ? api(`/api/triage/${{state.selectedTriageId}}/ai/assist?mode=assist&limit=5`)
            : Promise.resolve(null),
          state.selectedStoryId
            ? api(`/api/stories/${{state.selectedStoryId}}/ai/claim-draft?mode=assist`)
            : Promise.resolve(null),
        ]);
        state.aiSurfaceProjections = {{
          mission_suggest: missionSuggest,
          triage_assist: triageAssist,
          claim_draft: claimDraft,
        }};
        const selectedDelivery = getSelectedDeliverySubscription();
        if (selectedDelivery && String(selectedDelivery.subject_kind || "").trim().toLowerCase() === "report") {{
          try {{
            await loadDeliveryPackageAudit(String(selectedDelivery.id || "").trim(), {{
              profileId: String(state.deliveryPackageProfileIds[selectedDelivery.id] || "").trim(),
              render: false,
            }});
          }} catch (error) {{
            state.deliveryPackageErrors[String(selectedDelivery.id || "").trim()] = error.message;
          }}
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
      renderDeliveryWorkspace();
      renderAiSurfaces();
      renderStatus();
      renderTriage();
      renderStories();
      renderClaimsWorkspace();
      renderReportStudio();
      renderCreateWatchDeck();
      applyDefaultSavedViewOnBoot();
    }}

    bindCreateWatchDeck();
    bindRouteDeck();
    bindStoryDeck();
    bindContextObjectRail();
    bindHeroStageMotion();
    bindSectionJumps();
    bindSectionTracking();
    bindContextLens();
    bindLanguageSwitch();
    bindCommandPalette();
    bindResponsiveInteractionContract();
    applyLanguageChrome();
    renderActionHistory();
    renderCommandPalette();
    $("palette-open")?.addEventListener("click", () => {{
      if (state.commandPalette.open) {{
        closeCommandPalette();
      }} else {{
        openCommandPalette();
      }}
    }});
    $("context-reset")?.addEventListener("click", () => {{
      resetWorkspaceContext();
    }});

    $("refresh-all").addEventListener("click", async () => {{
      const button = $("refresh-all");
      button.disabled = true;
      try {{
        await refreshBoard();
        showToast(copy("Console refreshed", "控制台已刷新"), "success");
      }} catch (error) {{
        reportError(error, copy("Refresh console", "刷新控制台"));
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
        showToast(copy("Due missions dispatched", "到点任务已触发执行"), "success");
      }} catch (error) {{
        reportError(error, copy("Run due missions", "执行到点任务"));
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
        showToast(
          String(state.createWatchEditingId || "").trim()
            ? copy("Provide both Name and Query before saving changes.", "保存修改前请同时填写名称和查询词。")
            : copy("Provide both Name and Query before creating a watch.", "创建任务前请同时填写名称和查询词。"),
          "error",
        );
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
      const editingId = String(state.createWatchEditingId || "").trim();
      if (submitButton) {{
        submitButton.disabled = true;
      }}
      if (editingId) {{
        try {{
          const updated = await api(`/api/watches/${{editingId}}`, {{
            method: "PUT",
            headers: jsonHeaders,
            body: JSON.stringify(payload),
          }});
          state.selectedWatchId = updated.id || editingId;
          state.watchDetails[state.selectedWatchId] = updated;
          state.createWatchAdvancedOpen = null;
          setCreateWatchDraft(defaultCreateWatchDraft(), "", "");
          formElement.reset();
          pushActionEntry({{
            kind: copy("mission update", "任务修改"),
            label: state.language === "zh" ? `已更新任务：${{payload.name}}` : `Updated ${{payload.name}}`,
            detail: state.language === "zh" ? `任务 ID：${{editingId}}` : `Mission id: ${{editingId}}`,
          }});
          await refreshBoard();
          showToast(
            state.language === "zh" ? `任务已更新：${{payload.name}}` : `Mission updated: ${{payload.name}}`,
            "success",
          );
        }} catch (error) {{
          reportError(error, copy("Update watch", "更新任务"));
        }} finally {{
          if (submitButton) {{
            submitButton.disabled = false;
          }}
        }}
        return;
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
        state.createWatchAdvancedOpen = null;
        setCreateWatchDraft(defaultCreateWatchDraft(), "", "");
        formElement.reset();
        pushActionEntry({{
          kind: copy("mission create", "任务创建"),
          label: state.language === "zh" ? `已创建任务：${{payload.name}}` : `Created ${{payload.name}}`,
          detail: copy("The new mission can be removed from the recent action log if this was a false start.", "如果这是误创建，可以在最近操作中直接删除。"),
          undoLabel: copy("Delete mission", "删除任务"),
          undo: async () => {{
            await api(`/api/watches/${{created.id}}`, {{ method: "DELETE" }});
            await refreshBoard();
            showToast(
              state.language === "zh" ? `已删除任务：${{created.name || created.id}}` : `Mission deleted: ${{created.name || created.id}}`,
              "success",
            );
          }},
        }});
        await refreshBoard();
        showToast(
          state.language === "zh" ? `任务已创建：${{payload.name}}` : `Watch created: ${{payload.name}}`,
          "success",
        );
      }} catch (error) {{
        state.watches = state.watches.filter((watch) => watch.id !== optimisticId);
        delete state.watchDetails[optimisticId];
        if (state.selectedWatchId === optimisticId) {{
          state.selectedWatchId = state.watches[0] ? state.watches[0].id : "";
        }}
        renderWatches();
        renderWatchDetail();
        reportError(error, copy("Create watch", "创建任务"));
      }} finally {{
        if (submitButton) {{
          submitButton.disabled = false;
        }}
      }}
    }});

    state.consoleOverflowEvidence = defaultConsoleOverflowEvidence();
    window.getConsoleOverflowEvidence = getConsoleOverflowEvidence;

    refreshBoard().catch((error) => {{
      reportError(error, copy("Console boot failed", "控制台启动失败"));
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
      if (key === "escape" && state.contextLensOpen) {{
        event.preventDefault();
        setContextLensOpen(false);
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
          state.createWatchAdvancedOpen = draftHasAdvancedSignal(preset.values);
          setCreateWatchDraft(preset.values, preset.id, "");
          showToast(
            state.language === "zh"
              ? `${{preset.zhLabel || preset.label}} 已载入任务草稿`
              : `${{preset.label}} loaded into the mission deck`,
            "success",
          );
        }}
        return;
      }}
      const visibleItems = getVisibleTriageItems();
      if (!visibleItems.length) {{
        return;
      }}
      const selectedId = state.selectedTriageId || visibleItems[0].id;
      const hasBatchSelection = state.selectedTriageIds.length > 0;
      if (key === "j") {{
        event.preventDefault();
        moveTriageSelection(1);
      }} else if (key === "k") {{
        event.preventDefault();
        moveTriageSelection(-1);
      }} else if (key === "v") {{
        event.preventDefault();
        (hasBatchSelection ? runTriageBatchStateUpdate("verified") : runTriageStateUpdate(selectedId, "verified")).catch((error) => reportError(error, copy("Verify triage item", "核验分诊条目")));
      }} else if (key === "t") {{
        event.preventDefault();
        (hasBatchSelection ? runTriageBatchStateUpdate("triaged") : runTriageStateUpdate(selectedId, "triaged")).catch((error) => reportError(error, copy("Triage item", "分诊条目")));
      }} else if (key === "e") {{
        event.preventDefault();
        (hasBatchSelection ? runTriageBatchStateUpdate("escalated") : runTriageStateUpdate(selectedId, "escalated")).catch((error) => reportError(error, copy("Escalate triage item", "升级分诊条目")));
      }} else if (key === "i") {{
        event.preventDefault();
        (hasBatchSelection ? runTriageBatchStateUpdate("ignored") : runTriageStateUpdate(selectedId, "ignored")).catch((error) => reportError(error, copy("Ignore triage item", "忽略分诊条目")));
      }} else if (key === "s") {{
        event.preventDefault();
        (hasBatchSelection ? createStoryFromTriageItems(state.selectedTriageIds) : createStoryFromTriageItems([selectedId])).catch((error) => reportError(error, copy("Create story from triage", "从分诊生成故事")));
      }} else if (key === "d") {{
        event.preventDefault();
        runTriageExplain(selectedId).catch((error) => reportError(error, copy("Explain duplicates", "查看重复解释")));
      }} else if (key === "n") {{
        event.preventDefault();
        focusTriageNoteComposer(selectedId);
      }}
    }});
  </script>
</body>
</html>"""
