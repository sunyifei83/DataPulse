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
      --paper: #16110d;
      --mist: #261d16;
      --panel: rgba(31, 24, 19, 0.84);
      --panel-strong: rgba(24, 18, 15, 0.94);
      --ink: #f6efe8;
      --muted: #b8aa9b;
      --accent: #cf815e;
      --accent-2: #91a17d;
      --line: rgba(214, 196, 177, 0.16);
      --line-strong: rgba(214, 196, 177, 0.22);
      --surface-soft: rgba(248, 239, 230, 0.04);
      --surface-warm: rgba(207, 129, 94, 0.08);
      --warn: #d36c57;
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
      --action-control-height: 44px;
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
        radial-gradient(circle at 48% 22%, rgba(207, 129, 94, 0.16), transparent 18%),
        radial-gradient(circle at 72% 18%, rgba(145, 161, 125, 0.12), transparent 22%),
        radial-gradient(circle at 12% 12%, rgba(207, 129, 94, 0.12), transparent 26%),
        radial-gradient(circle at 88% 9%, rgba(248, 239, 230, 0.06), transparent 20%),
        linear-gradient(180deg, #2b2119 0%, #1f1813 54%, var(--paper) 100%);
      font-family: var(--body);
    }}
    body[data-context-lens-open="true"],
    body[data-story-inspector-open="true"] {{
      overflow: hidden;
    }}
    body[data-density-mode="comfortable"] {{
      --panel-padding: 22px;
      --card-padding: 14px 16px;
      --cluster-padding: 14px;
      --guide-padding: 14px;
      --deck-padding: 14px;
      --control-height: 44px;
      --action-control-height: 44px;
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
      --action-control-height: 44px;
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
      --action-control-height: 44px;
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
        linear-gradient(rgba(214, 196, 177, 0.05) 1px, transparent 1px),
        linear-gradient(90deg, rgba(214, 196, 177, 0.05) 1px, transparent 1px);
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
      border: 1px solid rgba(214, 196, 177, 0.26);
      box-shadow:
        0 0 22px rgba(207, 129, 94, 0.16),
        0 0 30px rgba(145, 161, 125, 0.12);
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
      border: 1px solid rgba(214, 196, 177, 0.16);
      border-radius: 22px;
      background: rgba(24, 18, 15, 0.8);
      backdrop-filter: blur(14px);
      box-shadow: 0 18px 44px rgba(8, 5, 3, 0.28);
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
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 4px;
      padding: 4px;
      border-radius: 999px;
      border: 1px solid rgba(214, 196, 177, 0.14);
      background: rgba(248, 239, 230, 0.03);
    }}
    .nav-pill {{
      min-height: 44px;
      padding: 10px 16px;
      border: 1px solid transparent;
      background: transparent;
      color: var(--muted);
      font-size: 0.8rem;
    }}
    .nav-pill.active {{
      color: var(--ink);
      border-color: rgba(214, 196, 177, 0.18);
      background:
        linear-gradient(180deg, rgba(207, 129, 94, 0.18), rgba(207, 129, 94, 0.1));
      box-shadow:
        0 8px 22px rgba(8, 5, 3, 0.16),
        inset 0 0 0 1px rgba(248, 239, 230, 0.04);
    }}
    .nav-pill:hover,
    .nav-pill:focus-visible {{
      color: var(--ink);
      border-color: rgba(214, 196, 177, 0.2);
      background: rgba(248, 239, 230, 0.04);
    }}
    .topbar-tools {{
      position: relative;
      display: flex;
      align-items: center;
      justify-content: flex-end;
      gap: 12px;
    }}
    .topbar-object-anchor {{
      min-width: min(340px, 32vw);
      max-width: 100%;
      display: grid;
      gap: 4px;
      padding: 10px 16px;
      border-radius: 20px;
      border: 1px solid rgba(214, 196, 177, 0.16);
      background:
        linear-gradient(180deg, rgba(248, 239, 230, 0.03), rgba(248, 239, 230, 0.01)),
        rgba(16, 12, 10, 0.72);
      text-align: left;
      box-shadow: inset 0 0 0 1px rgba(248, 239, 230, 0.02);
    }}
    .topbar-object-anchor[aria-expanded="true"] {{
      border-color: rgba(207, 129, 94, 0.28);
      background:
        linear-gradient(180deg, rgba(207, 129, 94, 0.16), rgba(207, 129, 94, 0.08)),
        rgba(16, 12, 10, 0.76);
    }}
    .topbar-object-kicker {{
      color: var(--muted);
      font: 700 0.7rem/1 var(--mono);
      letter-spacing: 0.08em;
      text-transform: uppercase;
    }}
    .topbar-object-title {{
      min-width: 0;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
      color: var(--ink);
      font: 600 0.94rem/1.25 var(--body);
      letter-spacing: 0.01em;
    }}
    .ui-badge {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      min-height: 28px;
      padding: 6px 10px;
      border-radius: 999px;
      border: 1px solid rgba(214, 196, 177, 0.14);
      background: rgba(248, 239, 230, 0.04);
      color: var(--muted);
      font: 700 12px/1 var(--mono);
      text-transform: uppercase;
    }}
    .ui-segment {{
      display: inline-flex;
      align-items: center;
      gap: 4px;
      padding: 4px;
      border-radius: 999px;
      border: 1px solid rgba(214, 196, 177, 0.14);
      background: rgba(248, 239, 230, 0.03);
    }}
    .ui-segment-wrap {{
      display: flex;
      flex-wrap: wrap;
      width: 100%;
    }}
    .ui-segment-button {{
      min-height: 44px;
      padding: 10px 16px;
      border-radius: 999px;
      border: 1px solid transparent;
      background: transparent;
      color: var(--muted);
    }}
    .ui-segment-button.active {{
      color: var(--ink);
      border-color: rgba(214, 196, 177, 0.18);
      background: linear-gradient(180deg, rgba(207, 129, 94, 0.18), rgba(207, 129, 94, 0.1));
    }}
    .ui-action-button {{
      min-height: 44px;
    }}
    .context-view-dock {{
      display: none;
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
      border: 1px solid rgba(214, 196, 177, 0.18);
      background: rgba(248, 239, 230, 0.04);
      min-height: 26px;
      max-width: 210px;
      appearance: none;
      color: inherit;
      cursor: pointer;
      font: inherit;
      text-align: left;
    }}
    .context-lens .context-object-rail {{
      display: grid;
      gap: 10px;
      margin-bottom: 0;
    }}
    .context-lens .context-object-divider {{
      display: none;
    }}
    .context-lens .context-object-step {{
      width: 100%;
      min-height: 44px;
      max-width: none;
      justify-content: space-between;
      padding: 10px 12px;
      border-color: rgba(214, 196, 177, 0.14);
      background: rgba(248, 239, 230, 0.03);
    }}
    .context-lens .context-object-step-value {{
      max-width: min(58%, 320px);
      text-align: right;
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
      color: rgba(214, 196, 177, 0.36);
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
      border-color: rgba(207, 129, 94, 0.32);
      background:
        linear-gradient(180deg, rgba(207, 129, 94, 0.18), rgba(248, 239, 230, 0.08));
      box-shadow: inset 0 0 0 1px rgba(248, 239, 230, 0.04);
    }}
    .context-lens-backdrop {{
      position: fixed;
      inset: 0;
      z-index: 65;
      display: none;
      align-items: stretch;
      justify-content: flex-end;
      padding: 16px;
      background: rgba(15, 11, 9, 0.56);
      backdrop-filter: blur(12px);
    }}
    .context-lens-backdrop.open {{
      display: flex;
    }}
    .context-lens-shell {{
      width: min(var(--context-lens-width), 100%);
      height: 100%;
      border: 1px solid rgba(214, 196, 177, 0.16);
      border-radius: var(--context-lens-radius);
      background:
        linear-gradient(180deg, rgba(38, 29, 22, 0.98), rgba(22, 17, 14, 0.97));
      box-shadow: 0 30px 80px rgba(8, 5, 3, 0.42);
      overflow: hidden;
    }}
    .context-lens-shell:focus {{
      outline: 2px solid rgba(207, 129, 94, 0.38);
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
      border: 1px solid rgba(214, 196, 177, 0.12);
      background: rgba(248, 239, 230, 0.03);
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
      border-top: 1px solid rgba(214, 196, 177, 0.12);
    }}
    .context-lens-utility-shell {{
      display: grid;
      gap: 10px;
      width: 100%;
      padding: 14px;
      border-radius: 18px;
      border: 1px solid rgba(214, 196, 177, 0.12);
      background: rgba(248, 239, 230, 0.025);
    }}
    .context-lens-utility-title {{
      color: var(--muted);
      font: 700 0.72rem/1 var(--mono);
      letter-spacing: 0.08em;
      text-transform: uppercase;
    }}
    .context-lens-utility-row {{
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
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
      border: 1px solid rgba(214, 196, 177, 0.12);
      background: rgba(248, 239, 230, 0.03);
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
      border: 1px solid rgba(214, 196, 177, 0.16);
      background: rgba(16, 12, 10, 0.72);
    }}
    .lang-btn {{
      min-width: 68px;
      min-height: 44px;
      padding: 9px 12px;
      background: transparent;
      color: var(--muted);
      font-size: 0.76rem;
    }}
    .lang-btn.active {{
      background: linear-gradient(135deg, rgba(207, 129, 94, 0.22), rgba(145, 161, 125, 0.16));
      color: var(--ink);
      box-shadow: inset 0 0 0 1px rgba(248, 239, 230, 0.06);
    }}
    .hero {{
      display: grid;
      grid-template-columns: 1.4fr 0.8fr;
      gap: 18px;
      align-items: start;
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
        linear-gradient(160deg, rgba(49, 36, 28, 0.95), rgba(23, 18, 15, 0.92)),
        var(--panel);
    }}
    .hero-main::before {{
      content: "";
      position: absolute;
      inset: -12% 22% 26% 22%;
      border-radius: 999px;
      background:
        radial-gradient(circle, rgba(207, 129, 94, 0.16), transparent 46%),
        radial-gradient(circle, rgba(145, 161, 125, 0.12), transparent 58%);
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
      border: 1px solid rgba(207, 129, 94, 0.24);
      box-shadow:
        inset 0 0 0 16px rgba(248, 239, 230, 0.04),
        0 0 48px rgba(207, 129, 94, 0.16);
      opacity: 0.7;
      pointer-events: none;
    }}
    .hero-side {{
      padding: 24px;
      display: grid;
      gap: 12px;
      align-content: start;
      background:
        linear-gradient(180deg, rgba(39, 30, 24, 0.92), rgba(20, 16, 13, 0.9)),
        var(--panel);
    }}
    body[data-responsive-viewport="desktop"] .hero-side {{
      align-self: start;
      max-height: calc(100vh - 146px);
      overflow-y: auto;
      overscroll-behavior: contain;
      scrollbar-gutter: stable both-edges;
    }}
    .brand-tile {{
      display: grid;
      grid-template-columns: 88px 1fr;
      gap: 14px;
      align-items: center;
      padding: 12px;
      border-radius: 20px;
      border: 1px solid rgba(214, 196, 177, 0.18);
      background: linear-gradient(180deg, rgba(45, 34, 27, 0.92), rgba(24, 18, 15, 0.94));
      box-shadow: inset 0 0 0 1px rgba(248, 239, 230, 0.04);
    }}
    .brand-image {{
      width: 88px;
      height: 88px;
      border-radius: 20px;
      object-fit: cover;
      border: 1px solid rgba(214, 196, 177, 0.22);
      box-shadow:
        0 0 24px rgba(248, 239, 230, 0.06),
        0 0 18px rgba(207, 129, 94, 0.1);
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
      grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
      gap: 12px;
      margin-top: 20px;
    }}
    .guide-card {{
      display: grid;
      gap: 8px;
      min-width: 0;
      overflow: hidden;
      overflow-wrap: anywhere;
      padding: var(--guide-padding);
      border-radius: 18px;
      border: 1px solid rgba(214, 196, 177, 0.16);
      background: linear-gradient(180deg, rgba(40, 30, 24, 0.72), rgba(24, 18, 15, 0.68));
      box-shadow: inset 0 0 0 1px rgba(248, 239, 230, 0.03);
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
      border: 1px solid rgba(214, 196, 177, 0.22);
      background: linear-gradient(180deg, rgba(207, 129, 94, 0.16), rgba(145, 161, 125, 0.12));
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
    button:focus-visible {{
      outline: none;
      box-shadow:
        0 0 0 1px rgba(248, 239, 230, 0.18),
        0 0 0 4px rgba(207, 129, 94, 0.18);
    }}
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
      background: linear-gradient(180deg, rgba(248, 239, 230, 0.05), rgba(207, 129, 94, 0.07));
      color: var(--ink);
      box-shadow: inset 0 0 0 1px rgba(214, 196, 177, 0.12);
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
      border: 1px solid rgba(214, 196, 177, 0.16);
      border-radius: 24px;
      background:
        linear-gradient(180deg, rgba(39, 30, 24, 0.84), rgba(21, 17, 14, 0.66));
      box-shadow: inset 0 0 0 1px rgba(248, 239, 230, 0.03);
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
    .workspace-mode-shell[data-workspace-chrome="compact"] {{
      gap: 12px;
      padding: 16px 18px;
    }}
    .workspace-mode-shell[data-workspace-chrome="compact"] .workspace-mode-head {{
      display: grid;
      grid-template-columns: minmax(0, 1fr) minmax(320px, 0.9fr);
      gap: 12px;
      align-items: start;
    }}
    .workspace-mode-summary {{
      display: grid;
      gap: 6px;
      max-width: 72ch;
      align-content: start;
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
    .workspace-mode-object-anchor {{
      display: grid;
      gap: 12px;
      padding: 16px;
      border-radius: 20px;
      border: 1px solid rgba(214, 196, 177, 0.22);
      background:
        linear-gradient(180deg, rgba(207, 129, 94, 0.14), rgba(248, 239, 230, 0.05)),
        rgba(26, 20, 16, 0.8);
      box-shadow:
        0 14px 34px rgba(8, 5, 3, 0.18),
        inset 0 0 0 1px rgba(248, 239, 230, 0.05);
    }}
    .workspace-mode-shell[data-workspace-chrome="compact"] .workspace-mode-object-anchor {{
      gap: 10px;
      padding: 14px;
    }}
    .workspace-mode-object-head {{
      display: flex;
      gap: 10px;
      justify-content: space-between;
      align-items: start;
    }}
    .workspace-mode-object-kicker {{
      color: var(--accent);
      font: 700 0.74rem/1 var(--mono);
      letter-spacing: 0.08em;
      text-transform: uppercase;
    }}
    .workspace-mode-object-title {{
      margin-top: 6px;
      font-family: var(--headline);
      font-size: clamp(1.4rem, 3vw, 2.2rem);
      line-height: 1;
      letter-spacing: 0.02em;
      text-transform: uppercase;
    }}
    body[data-lang="zh"] .workspace-mode-object-title {{
      font-family: var(--headline-zh);
      text-transform: none;
      letter-spacing: 0;
      line-height: 1.15;
    }}
    .workspace-mode-object-copy {{
      color: var(--muted);
      font-size: 0.9rem;
      line-height: 1.55;
    }}
    .workspace-mode-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(320px, 480px));
      justify-content: start;
      gap: 12px;
    }}
    .workspace-mode-card {{
      width: 100%;
      min-width: 0;
      display: grid;
      gap: 14px;
      text-align: left;
      padding: 18px;
      border-radius: 20px;
      border: 1px solid rgba(214, 196, 177, 0.14);
      background: linear-gradient(180deg, rgba(36, 28, 22, 0.72), rgba(23, 18, 15, 0.58));
      color: var(--ink);
      box-shadow: inset 0 0 0 1px rgba(248, 239, 230, 0.03);
      overflow: hidden;
      overflow-wrap: anywhere;
    }}
    .workspace-mode-card.active {{
      border-color: rgba(214, 196, 177, 0.22);
      background:
        linear-gradient(180deg, rgba(207, 129, 94, 0.14), rgba(248, 239, 230, 0.05)),
        rgba(28, 21, 17, 0.82);
      box-shadow:
        0 14px 34px rgba(8, 5, 3, 0.24),
        inset 0 0 0 1px rgba(248, 239, 230, 0.06);
    }}
    .workspace-mode-card:hover {{
      transform: translateY(-1px);
      position: relative;
      z-index: 2;
      border-color: rgba(214, 196, 177, 0.2);
      background: linear-gradient(180deg, rgba(41, 31, 24, 0.78), rgba(27, 20, 16, 0.72));
      box-shadow: 0 10px 26px rgba(8, 5, 3, 0.28), inset 0 0 0 1px rgba(248, 239, 230, 0.04);
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
      border: 1px solid rgba(214, 196, 177, 0.14);
      background: rgba(248, 239, 230, 0.03);
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
    .workspace-mode-actions {{
      margin-top: 0;
    }}
    .workspace-mode-insight-grid {{
      display: grid;
      grid-template-columns: minmax(0, 1.3fr) minmax(0, 1fr);
      gap: 12px;
      align-items: start;
    }}
    .workspace-mode-shell[data-workspace-chrome="compact"] .workspace-mode-insight-grid {{
      gap: 10px;
    }}
    .workflow-trace-card,
    .shared-signal-taxonomy-card {{
      background:
        linear-gradient(180deg, rgba(38, 29, 22, 0.88), rgba(22, 17, 14, 0.74));
      box-shadow: inset 0 0 0 1px rgba(248, 239, 230, 0.03);
    }}
    .trace-stage-grid {{
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 10px;
      margin-top: 14px;
    }}
    .workspace-mode-shell[data-workspace-chrome="compact"] .trace-stage-grid {{
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 8px;
      margin-top: 12px;
    }}
    .trace-stage {{
      display: grid;
      gap: 10px;
      padding: 14px;
      border-radius: 18px;
      border: 1px solid rgba(214, 196, 177, 0.14);
      background: rgba(248, 239, 230, 0.03);
      min-width: 0;
      overflow: hidden;
    }}
    .trace-stage-title,
    .trace-stage-copy,
    .trace-stage-head {{
      min-width: 0;
      overflow-wrap: anywhere;
      word-break: break-word;
    }}
    .workspace-mode-shell[data-workspace-chrome="compact"] .trace-stage,
    .workspace-mode-shell[data-workspace-chrome="compact"] .shared-signal-detail {{
      gap: 8px;
      padding: 12px;
    }}
    .trace-stage.ok {{
      border-color: rgba(145, 161, 125, 0.3);
      box-shadow: inset 0 0 0 1px rgba(145, 161, 125, 0.06);
    }}
    .trace-stage.hot {{
      border-color: rgba(255, 106, 130, 0.28);
      box-shadow: inset 0 0 0 1px rgba(255, 106, 130, 0.05);
    }}
    .trace-stage-head,
    .shared-signal-detail-head {{
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      justify-content: space-between;
      align-items: start;
    }}
    .trace-stage-kicker {{
      font: 700 11px/1 var(--mono);
      letter-spacing: 0.08em;
      text-transform: uppercase;
      color: var(--muted);
    }}
    .trace-stage-title {{
      font-size: 1rem;
      line-height: 1.35;
      color: var(--ink);
    }}
    .trace-stage-copy {{
      font-size: 0.84rem;
      line-height: 1.55;
      color: var(--muted);
    }}
    .shared-signal-row {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin-top: 14px;
    }}
    .workspace-mode-shell[data-workspace-chrome="compact"] .shared-signal-row {{
      gap: 6px;
      margin-top: 12px;
    }}
    .shared-signal-button.ok {{
      border-color: rgba(145, 161, 125, 0.3);
    }}
    .shared-signal-button.hot {{
      border-color: rgba(255, 106, 130, 0.28);
    }}
    .shared-signal-detail {{
      display: grid;
      gap: 12px;
      margin-top: 14px;
      padding: 14px;
      border-radius: 18px;
      border: 1px solid rgba(214, 196, 177, 0.14);
      background: rgba(248, 239, 230, 0.03);
    }}
    .workspace-mode-shell[data-workspace-chrome="compact"] .workflow-trace-card .panel-sub,
    .workspace-mode-shell[data-workspace-chrome="compact"] .shared-signal-taxonomy-card .panel-sub {{
      font-size: 0.82rem;
      line-height: 1.5;
    }}
    body[data-responsive-viewport="desktop"] .workspace-mode-shell[data-workspace-chrome="compact"] .workspace-mode-object-anchor .continuity-fact-list {{
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 8px 12px;
    }}
    body[data-responsive-viewport="desktop"] .workspace-mode-shell[data-workspace-chrome="compact"] .workspace-mode-object-anchor .continuity-fact {{
      display: grid;
      gap: 4px;
    }}
    body[data-responsive-viewport="desktop"] .workspace-mode-shell[data-workspace-chrome="compact"] .workspace-mode-object-anchor .continuity-fact strong {{
      text-align: left;
    }}
    body[data-responsive-viewport="desktop"] .workspace-mode-shell[data-workspace-chrome="compact"] .workspace-mode-object-anchor .action-secondary-row {{
      display: none;
    }}
    .shared-signal-detail.ok {{
      border-color: rgba(145, 161, 125, 0.3);
      box-shadow: inset 0 0 0 1px rgba(145, 161, 125, 0.06);
    }}
    .shared-signal-detail.hot {{
      border-color: rgba(255, 106, 130, 0.28);
      box-shadow: inset 0 0 0 1px rgba(255, 106, 130, 0.05);
    }}
    .advanced-surface-shell {{
      grid-column: 1 / -1;
      border: 1px solid rgba(214, 196, 177, 0.14);
      border-radius: 22px;
      background:
        linear-gradient(180deg, rgba(18, 16, 17, 0.82), rgba(10, 14, 20, 0.74));
      box-shadow: inset 0 0 0 1px rgba(248, 239, 230, 0.03);
      overflow: hidden;
    }}
    .advanced-surface-shell summary {{
      list-style: none;
      display: flex;
      flex-wrap: wrap;
      gap: 12px;
      align-items: flex-start;
      justify-content: space-between;
      padding: 16px 18px;
      cursor: pointer;
    }}
    .advanced-surface-shell summary::-webkit-details-marker {{
      display: none;
    }}
    .advanced-surface-shell[open] summary {{
      border-bottom: 1px solid rgba(214, 196, 177, 0.12);
      background: rgba(207, 129, 94, 0.06);
    }}
    .advanced-surface-summary-copy {{
      display: grid;
      gap: 6px;
      flex: 1 1 320px;
      min-width: 0;
    }}
    .advanced-surface-kicker {{
      font: 700 11px/1 var(--mono);
      letter-spacing: 0.08em;
      text-transform: uppercase;
      color: var(--muted);
    }}
    .advanced-surface-title {{
      font-family: var(--headline);
      font-size: 1rem;
      letter-spacing: 0.01em;
      text-transform: none;
    }}
    .advanced-surface-meta {{
      display: inline-flex;
      flex-wrap: wrap;
      gap: 8px 12px;
      align-items: center;
      justify-content: flex-end;
      font: 700 12px/1.35 var(--mono);
      color: var(--muted);
    }}
    .advanced-surface-grid {{
      display: grid;
      gap: 18px;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      padding: 0 18px 18px;
    }}
    .workspace-mode-group {{
      display: grid;
      gap: 18px;
    }}
    .workspace-mode-group[data-workspace-group="review"] {{
      grid-template-columns: 1fr;
      align-items: start;
    }}
    .workspace-mode-group[data-workspace-group="delivery"] > .grid {{
      grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
      gap: 18px;
    }}
    .workspace-mode-group[data-workspace-group="delivery"] > .grid > article.panel {{
      min-width: 0;
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
      border: 1px solid rgba(214, 196, 177, 0.18);
      background:
        radial-gradient(circle at 50% 42%, rgba(207, 129, 94, 0.14), transparent 18%),
        radial-gradient(circle at 50% 46%, rgba(145, 161, 125, 0.12), transparent 24%),
        linear-gradient(180deg, rgba(43, 33, 25, 0.82), rgba(18, 13, 10, 0.94));
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
        linear-gradient(180deg, rgba(18, 13, 10, 0.08), rgba(18, 13, 10, 0.42)),
        radial-gradient(circle at 50% 42%, rgba(248, 239, 230, 0.08), transparent 30%);
      pointer-events: none;
    }}
    .hero-stage::before {{
      content: "";
      position: absolute;
      inset: auto 0 0 0;
      height: 68px;
      background:
        linear-gradient(rgba(214, 196, 177, 0.08) 1px, transparent 1px),
        linear-gradient(90deg, rgba(214, 196, 177, 0.08) 1px, transparent 1px);
      background-size: 30px 30px;
      opacity: 0.85;
    }}
    .intake-live-shell {{
      display: grid;
      gap: 12px;
    }}
    .live-object-anchor {{
      display: grid;
      gap: 14px;
      padding: 18px;
      background:
        linear-gradient(160deg, rgba(47, 35, 28, 0.92), rgba(18, 13, 10, 0.9)),
        var(--panel);
      box-shadow:
        0 18px 44px rgba(3, 8, 18, 0.28),
        inset 0 0 0 1px rgba(248, 239, 230, 0.04);
    }}
    .live-object-head {{
      display: flex;
      gap: 12px;
      justify-content: space-between;
      align-items: start;
    }}
    .live-object-kicker {{
      color: var(--accent-2);
      font: 700 0.74rem/1 var(--mono);
      letter-spacing: 0.08em;
      text-transform: uppercase;
    }}
    .live-object-title {{
      margin-top: 8px;
      font-family: var(--headline);
      font-size: clamp(1.8rem, 4vw, 3.1rem);
      line-height: 0.95;
      letter-spacing: -0.03em;
      text-transform: uppercase;
    }}
    body[data-lang="zh"] .live-object-title {{
      font-family: var(--headline-zh);
      line-height: 1.12;
      letter-spacing: 0;
      text-transform: none;
    }}
    .live-object-copy {{
      max-width: 56ch;
      color: var(--muted);
      font-size: 0.95rem;
      line-height: 1.58;
    }}
    .guide-compact-card {{
      display: grid;
      gap: 12px;
      padding: 18px;
      background:
        linear-gradient(180deg, rgba(41, 31, 25, 0.9), rgba(20, 16, 13, 0.88)),
        var(--panel);
      box-shadow: inset 0 0 0 1px rgba(248, 239, 230, 0.03);
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
      border: 2px solid rgba(145, 161, 125, 0.38);
      background:
        radial-gradient(circle at 50% 46%, rgba(145, 161, 125, 0.14), transparent 58%),
        radial-gradient(circle at 42% 40%, rgba(207, 129, 94, 0.18), transparent 48%);
      box-shadow:
        inset 0 0 42px rgba(145, 161, 125, 0.1),
        0 0 42px rgba(207, 129, 94, 0.12);
      transition: transform .28s ease, box-shadow .28s ease;
      will-change: transform;
    }}
    .stage-globe::before,
    .stage-globe::after {{
      content: "";
      position: absolute;
      border-radius: 999px;
      inset: 18px;
      border: 1px solid rgba(214, 196, 177, 0.22);
    }}
    .stage-globe::after {{
      inset: 48% 8px auto 8px;
      height: 1px;
      border: 0;
      background: rgba(214, 196, 177, 0.26);
    }}
    .stage-console {{
      position: absolute;
      bottom: 34px;
      width: 126px;
      height: 58px;
      border-radius: 16px;
      border: 1px solid rgba(214, 196, 177, 0.22);
      background:
        linear-gradient(180deg, rgba(38, 29, 22, 0.94), rgba(18, 13, 10, 0.98));
      box-shadow: inset 0 0 0 1px rgba(248, 239, 230, 0.05);
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
        linear-gradient(90deg, rgba(145, 161, 125, 0.62), rgba(207, 129, 94, 0.78));
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
      border: 1px solid rgba(214, 196, 177, 0.18);
      background: linear-gradient(180deg, rgba(24, 18, 15, 0.78), rgba(24, 18, 15, 0.32));
      backdrop-filter: blur(10px);
      box-shadow: inset 0 0 0 1px rgba(248, 239, 230, 0.03);
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
      align-items: start;
      animation: rise .7s ease-out both;
      animation-delay: .08s;
    }}
    .dual-grid {{
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 18px;
      align-items: start;
      animation: rise .76s ease-out both;
      animation-delay: .12s;
    }}
    .dual-grid[data-layout="master-detail"] {{
      grid-template-columns: minmax(300px, 34%) 1fr;
    }}
    .dual-grid[data-layout="master-detail"] > #section-board {{
      position: sticky;
      top: 92px;
      max-height: calc(100vh - 120px);
      overflow: hidden;
      display: grid;
      grid-template-rows: auto auto 1fr;
    }}
    .dual-grid[data-layout="master-detail"] > #section-board > #watch-list {{
      min-height: 0;
      overflow-y: auto;
      overflow-x: hidden;
      padding-right: 4px;
      scrollbar-width: thin;
    }}
    .dual-grid[data-layout="master-detail"] > #section-board > #watch-list::-webkit-scrollbar {{ width: 6px; }}
    .dual-grid[data-layout="master-detail"] > #section-board > #watch-list::-webkit-scrollbar-thumb {{
      background: rgba(214, 196, 177, 0.18);
      border-radius: 3px;
    }}
    .dual-grid[data-layout="master-detail"] > #section-cockpit {{
      min-width: 0;
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
      background: linear-gradient(180deg, rgba(37, 28, 22, 0.76), rgba(24, 18, 15, 0.72));
      box-shadow: inset 0 0 0 1px rgba(248, 239, 230, 0.03);
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
      background: rgba(248, 239, 230, 0.06);
      color: var(--muted);
    }}
    .chip.hot {{ background: rgba(207, 129, 94, 0.14); color: var(--accent); }}
    .chip.ok {{ background: rgba(145, 161, 125, 0.16); color: var(--accent-2); }}
    .chip-row {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin-top: 8px;
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
      background: linear-gradient(180deg, rgba(248, 239, 230, 0.05), rgba(207, 129, 94, 0.07));
      color: var(--ink);
      text-decoration: none;
      transition: transform .18s ease, box-shadow .18s ease, background .18s ease;
      box-shadow: inset 0 0 0 1px rgba(214, 196, 177, 0.12);
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
      background: linear-gradient(180deg, rgba(248, 239, 230, 0.05), rgba(207, 129, 94, 0.07));
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
      border-top: 1px solid rgba(214, 196, 177, 0.12);
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
      border: 1px solid rgba(214, 196, 177, 0.14);
      background: linear-gradient(180deg, rgba(38, 29, 22, 0.54), rgba(22, 17, 14, 0.42));
    }}
    .deck-mode-strip {{
      display: grid;
      gap: 12px;
      padding: 14px;
      border-radius: 18px;
      border: 1px solid rgba(214, 196, 177, 0.14);
      background:
        linear-gradient(180deg, rgba(41, 31, 24, 0.84), rgba(24, 18, 15, 0.6));
      box-shadow: inset 0 0 0 1px rgba(248, 239, 230, 0.03);
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
      background: rgba(248, 239, 230, 0.05);
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
      border: 1px solid rgba(214, 196, 177, 0.14);
      background: linear-gradient(180deg, rgba(38, 29, 22, 0.6), rgba(22, 17, 14, 0.5));
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
      border: 1px solid rgba(214, 196, 177, 0.16);
      background: linear-gradient(180deg, rgba(207, 129, 94, 0.14), rgba(248, 239, 230, 0.05));
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
      border: 1px solid rgba(214, 196, 177, 0.14);
      background:
        linear-gradient(180deg, rgba(38, 29, 22, 0.8), rgba(22, 17, 14, 0.56));
      box-shadow: inset 0 0 0 1px rgba(248, 239, 230, 0.03);
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
      background: rgba(24, 18, 15, 0.88);
    }}
    .batch-toolbar-card.selection-live {{
      border-color: rgba(145, 161, 125, 0.28);
      box-shadow:
        var(--shadow),
        inset 0 0 0 1px rgba(145, 161, 125, 0.08);
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
        linear-gradient(180deg, rgba(38, 29, 22, 0.88), rgba(22, 17, 14, 0.74));
      box-shadow: inset 0 0 0 1px rgba(248, 239, 230, 0.03);
    }}
    .section-summary-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(min(100%, 220px), 1fr));
      gap: 10px;
    }}
    .section-summary-signal {{
      display: grid;
      gap: 10px;
      padding: 14px;
      border-radius: 18px;
      border: 1px solid rgba(214, 196, 177, 0.14);
      background: rgba(248, 239, 230, 0.03);
    }}
    .section-summary-signal.ok {{
      border-color: rgba(145, 161, 125, 0.3);
      box-shadow: inset 0 0 0 1px rgba(145, 161, 125, 0.06);
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
    .section-summary-feedback {{
      display: grid;
      gap: 12px;
      padding: 14px;
      border-radius: 18px;
      border: 1px solid rgba(214, 196, 177, 0.16);
      background: rgba(248, 239, 230, 0.03);
    }}
    .section-summary-feedback.ok {{
      border-color: rgba(145, 161, 125, 0.3);
      box-shadow: inset 0 0 0 1px rgba(145, 161, 125, 0.06);
    }}
    .section-summary-feedback.hot {{
      border-color: rgba(255, 106, 130, 0.28);
      box-shadow: inset 0 0 0 1px rgba(255, 106, 130, 0.05);
    }}
    .section-summary-feedback-head {{
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      justify-content: space-between;
      align-items: start;
    }}
    .section-summary-feedback-copy {{
      font-size: 0.88rem;
      line-height: 1.6;
      color: var(--muted);
    }}
    .operator-guidance-surface {{
      display: grid;
      gap: 14px;
      background:
        linear-gradient(180deg, rgba(37, 28, 22, 0.88), rgba(18, 13, 10, 0.78));
      box-shadow:
        var(--shadow),
        inset 0 0 0 1px rgba(248, 239, 230, 0.03);
    }}
    .operator-guidance-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(min(100%, 220px), 1fr));
      gap: 10px;
    }}
    .operator-guidance-column {{
      display: grid;
      gap: 10px;
      min-width: 0;
      padding: 14px;
      border-radius: 18px;
      border: 1px solid rgba(214, 196, 177, 0.14);
      background: rgba(248, 239, 230, 0.03);
    }}
    .operator-guidance-column-head {{
      display: grid;
      gap: 4px;
      min-width: 0;
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
      min-width: 0;
      padding: 12px;
      border-radius: 16px;
      border: 1px solid rgba(214, 196, 177, 0.12);
      background: rgba(248, 239, 230, 0.02);
    }}
    .operator-guidance-item.ok {{
      border-color: rgba(145, 161, 125, 0.3);
      box-shadow: inset 0 0 0 1px rgba(145, 161, 125, 0.06);
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
      min-width: 0;
    }}
    .operator-guidance-item-title {{
      min-width: 0;
      font-size: 0.92rem;
      line-height: 1.4;
      color: var(--ink);
      overflow-wrap: anywhere;
    }}
    .operator-guidance-item-copy {{
      min-width: 0;
      font-size: 0.82rem;
      line-height: 1.55;
      color: var(--muted);
      overflow-wrap: anywhere;
    }}
    .continuity-lane {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(min(100%, 220px), 1fr));
      gap: 10px;
    }}
    .continuity-stage {{
      display: grid;
      gap: 10px;
      padding: 14px;
      border-radius: 18px;
      border: 1px solid rgba(214, 196, 177, 0.14);
      background: rgba(248, 239, 230, 0.03);
    }}
    .continuity-stage.ok {{
      border-color: rgba(145, 161, 125, 0.3);
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
      border: 1px solid rgba(214, 196, 177, 0.16);
      border-radius: 14px;
      background: rgba(24, 18, 15, 0.84);
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
      border-color: rgba(207, 129, 94, 0.42);
      box-shadow:
        0 0 0 1px rgba(207, 129, 94, 0.22),
        0 0 0 5px rgba(207, 129, 94, 0.08);
    }}
    .mission-preview.ready {{
      border-color: rgba(145, 161, 125, 0.3);
      box-shadow: inset 0 0 0 1px rgba(145, 161, 125, 0.08);
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
      background: rgba(248, 239, 230, 0.04);
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
      background: rgba(248, 239, 230, 0.08);
      border: 1px solid rgba(214, 196, 177, 0.16);
    }}
    .preview-meter-fill {{
      height: 100%;
      border-radius: 999px;
      background: linear-gradient(90deg, rgba(145, 161, 125, 0.72), rgba(207, 129, 94, 0.84));
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
      border: 1px solid rgba(214, 196, 177, 0.22);
      background: rgba(24, 18, 15, 0.94);
      color: var(--ink);
      box-shadow: var(--shadow);
      animation: rise .22s ease-out both;
    }}
    .toast.success {{
      border-color: rgba(145, 161, 125, 0.32);
      box-shadow:
        var(--shadow),
        0 0 0 1px rgba(145, 161, 125, 0.08);
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
      background: rgba(248, 239, 230, 0.04);
    }}
    .palette-backdrop {{
      position: fixed;
      inset: 0;
      background: rgba(15, 11, 9, 0.72);
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
      border: 1px solid rgba(214, 196, 177, 0.22);
      background: rgba(22, 17, 14, 0.96);
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
      border: 1px solid rgba(214, 196, 177, 0.18);
      background: rgba(31, 24, 19, 0.92);
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
      border-bottom: 1px solid rgba(214, 196, 177, 0.1);
      cursor: pointer;
      transition: background .14s ease;
    }}
    .palette-item.active {{
      background: rgba(207, 129, 94, 0.12);
    }}
    .palette-item:hover {{
      background: rgba(248, 239, 230, 0.06);
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
      background: rgba(214, 196, 177, 0.12);
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
      background: linear-gradient(135deg, rgba(207, 129, 94, 0.14), rgba(24, 18, 15, 0.74));
      border: 1px solid rgba(214, 196, 177, 0.16);
    }}
    .state-banner.error {{
      background: linear-gradient(135deg, rgba(255, 106, 130, 0.18), rgba(24, 18, 15, 0.76));
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
      border: 1px dashed rgba(214, 196, 177, 0.24);
      color: var(--muted);
      text-align: center;
    }}
    .story-grid {{
      display: grid;
      grid-template-columns: minmax(300px, 34%) 1fr;
      gap: 16px;
      align-items: start;
    }}
    .story-grid > .story-list {{
      position: sticky;
      top: 92px;
      max-height: calc(100vh - 120px);
      overflow-y: auto;
      overflow-x: hidden;
      padding-right: 6px;
      scrollbar-width: thin;
    }}
    .story-grid > .story-list::-webkit-scrollbar {{ width: 6px; }}
    .story-grid > .story-list::-webkit-scrollbar-thumb {{
      background: rgba(214, 196, 177, 0.18);
      border-radius: 3px;
    }}
    .story-grid > .story-detail {{
      min-width: 0;
    }}
    .story-workspace-mode-switch {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      align-items: center;
      margin: 12px 0 6px;
    }}
    .story-workspace-mode-switch.ui-segment {{
      justify-content: flex-start;
      padding: 6px;
    }}
    .story-workspace-mode-switch .mono {{
      padding-inline: 6px;
    }}
    .story-list {{
      display: grid;
      gap: 12px;
      max-height: 760px;
      overflow: auto;
      padding-right: 4px;
    }}
    .card.selected {{
      border-color: rgba(207, 129, 94, 0.56);
      box-shadow:
        inset 0 0 0 1px rgba(207, 129, 94, 0.28),
        0 0 0 2px rgba(207, 129, 94, 0.32);
      background: rgba(45, 34, 27, 0.9);
    }}
    .card.selectable {{
      cursor: pointer;
      transition: transform .18s ease, border-color .18s ease, box-shadow .18s ease;
    }}
    .card.selectable:hover {{
      transform: translateY(-1px);
      border-color: rgba(207, 129, 94, 0.22);
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
    .story-detail-shell {{
      display: grid;
      gap: 12px;
    }}
    .story-detail-toolbar {{
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      align-items: center;
      justify-content: space-between;
      margin-top: 14px;
    }}
    .story-detail-actions {{
      margin-top: 0;
    }}
    .story-detail-actions > button,
    .story-detail-actions > a {{
      min-height: 44px;
    }}
    .story-detail-pane {{
      display: grid;
      gap: 12px;
    }}
    .story-pane-head {{
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      align-items: start;
      justify-content: space-between;
    }}
    .story-pane-copy {{
      max-width: 720px;
    }}
    .story-fact-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
      gap: 12px;
    }}
    .story-fact-card {{
      display: grid;
      gap: 10px;
      min-height: 124px;
      min-width: 0;
      overflow: hidden;
      overflow-wrap: anywhere;
      border-radius: 18px;
      border: 1px solid rgba(214, 196, 177, 0.16);
      padding: 16px;
      background: linear-gradient(180deg, rgba(248, 239, 230, 0.05), rgba(248, 239, 230, 0.02));
    }}
    .story-fact-value {{
      font-family: var(--headline);
      font-size: 1.34rem;
      letter-spacing: 0.04em;
      text-transform: uppercase;
      color: var(--ink);
    }}
    .story-fact-copy {{
      color: var(--muted);
      font-size: 0.9rem;
      line-height: 1.5;
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
      background: rgba(248, 239, 230, 0.04);
      display: grid;
      gap: 8px;
    }}
    .timeline-event.ok {{
      border-color: rgba(145, 161, 125, 0.3);
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
        radial-gradient(circle at 50% 45%, rgba(207, 129, 94, 0.16), transparent 42%),
        linear-gradient(180deg, rgba(38, 29, 22, 0.94), rgba(18, 13, 10, 0.96));
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
      background: rgba(248, 239, 230, 0.04);
      font: 700 12px/1.4 var(--mono);
      color: var(--muted);
    }}
    .text-block {{
      margin: 0;
      padding: 14px;
      border-radius: 14px;
      border: 1px solid var(--line);
      background: rgba(248, 239, 230, 0.04);
      white-space: pre-wrap;
      overflow: auto;
      font: 500 12px/1.55 var(--mono);
      color: var(--ink);
    }}
    .story-inspector-backdrop {{
      position: fixed;
      inset: 0;
      z-index: 66;
      display: none;
      align-items: stretch;
      justify-content: flex-end;
      padding: 16px;
      background: rgba(15, 11, 9, 0.62);
      backdrop-filter: blur(12px);
    }}
    .story-inspector-backdrop.open {{
      display: flex;
    }}
    .story-inspector-shell {{
      width: min(720px, 100%);
      height: 100%;
      border: 1px solid rgba(214, 196, 177, 0.16);
      border-radius: 30px;
      background: linear-gradient(180deg, rgba(38, 29, 22, 0.98), rgba(22, 17, 14, 0.97));
      box-shadow: 0 30px 80px rgba(8, 5, 3, 0.42);
      overflow: hidden;
    }}
    .story-inspector-shell:focus {{
      outline: 2px solid rgba(207, 129, 94, 0.38);
      outline-offset: 0;
    }}
    .story-inspector {{
      height: 100%;
      padding: 24px 22px;
      display: grid;
      grid-template-rows: auto minmax(0, 1fr) auto;
      gap: 16px;
    }}
    .story-inspector-head {{
      display: flex;
      gap: 14px;
      align-items: start;
      justify-content: space-between;
    }}
    .story-inspector-head-copy {{
      min-width: 0;
      display: grid;
      gap: 6px;
    }}
    .story-inspector-title {{
      font-family: var(--headline);
      font-size: 0.94rem;
      letter-spacing: 0.08em;
      text-transform: uppercase;
    }}
    .story-inspector-copy {{
      color: var(--muted);
      font-size: 0.88rem;
      line-height: 1.6;
    }}
    .story-inspector-body {{
      min-height: 0;
      overflow-y: auto;
      display: grid;
      gap: 12px;
      align-content: start;
    }}
    .story-inspector-toolbar {{
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      align-items: center;
      justify-content: space-between;
    }}
    .story-inspector-toolbar .meta {{
      margin-top: 0;
    }}
    .story-inspector-panel {{
      display: grid;
      gap: 12px;
    }}
    .story-inspector-pre {{
      min-height: min(54vh, 520px);
    }}
    .story-inspector-footer {{
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      justify-content: flex-end;
    }}
    .story-inspector-footer > button,
    .story-inspector-footer > a {{
      min-height: 44px;
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
    body[data-pane-contract="stacked"] .story-fact-grid,
    body[data-pane-contract="stacked"] .preview-grid,
    body[data-pane-contract="stacked"] .guide-grid,
    body[data-pane-contract="stacked"] .operator-guidance-grid,
    body[data-pane-contract="stacked"] .section-summary-grid,
    body[data-pane-contract="stacked"] .continuity-lane,
    body[data-pane-contract="stacked"] .workspace-mode-insight-grid,
    body[data-pane-contract="stacked"] .trace-stage-grid,
    body[data-pane-contract="stacked"] .workbench-columns,
    body[data-pane-contract="single"] .dual-grid,
    body[data-pane-contract="single"] .grid,
    body[data-pane-contract="single"] .story-grid,
    body[data-pane-contract="single"] .story-columns,
    body[data-pane-contract="single"] .story-fact-grid,
    body[data-pane-contract="single"] .preview-grid,
    body[data-pane-contract="single"] .guide-grid,
    body[data-pane-contract="single"] .operator-guidance-grid,
    body[data-pane-contract="single"] .section-summary-grid,
    body[data-pane-contract="single"] .continuity-lane,
    body[data-pane-contract="single"] .workspace-mode-insight-grid,
    body[data-pane-contract="single"] .trace-stage-grid,
    body[data-pane-contract="single"] .workbench-columns {{
      grid-template-columns: 1fr;
    }}
    body[data-responsive-viewport="compact"] .topbar,
    body[data-responsive-viewport="touch"] .topbar {{
      grid-template-columns: 1fr;
    }}
    body[data-responsive-viewport="compact"] .topbar-nav,
    body[data-responsive-viewport="touch"] .topbar-nav {{
      justify-content: start;
      flex-wrap: nowrap;
      overflow-x: auto;
      padding-bottom: 2px;
      scrollbar-width: none;
    }}
    body[data-responsive-viewport="compact"] .topbar-nav::-webkit-scrollbar,
    body[data-responsive-viewport="touch"] .topbar-nav::-webkit-scrollbar {{
      display: none;
    }}
    body[data-responsive-viewport="compact"] .workspace-mode-grid,
    body[data-responsive-viewport="compact"] .workspace-mode-insight-grid,
    body[data-responsive-viewport="compact"] .advanced-surface-grid,
    body[data-responsive-viewport="compact"] .workspace-mode-group[data-workspace-group="review"],
    body[data-responsive-viewport="compact"] .hero,
    body[data-responsive-viewport="compact"] .grid,
    body[data-responsive-viewport="compact"] .dual-grid,
    body[data-responsive-viewport="touch"] .workspace-mode-grid,
    body[data-responsive-viewport="touch"] .workspace-mode-insight-grid,
    body[data-responsive-viewport="touch"] .advanced-surface-grid,
    body[data-responsive-viewport="touch"] .workspace-mode-group[data-workspace-group="review"],
    body[data-responsive-viewport="touch"] .hero,
    body[data-responsive-viewport="touch"] .grid,
    body[data-responsive-viewport="touch"] .dual-grid {{
      grid-template-columns: 1fr;
    }}
    body[data-responsive-viewport="compact"] .batch-toolbar-card {{
      top: 152px;
    }}
    body[data-responsive-viewport="touch"] .shell {{
      padding: 16px;
    }}
    body[data-responsive-viewport="touch"] .topbar {{
      top: 10px;
      padding: 12px 14px;
    }}
    body[data-responsive-viewport="touch"] .topbar-copy span {{
      white-space: normal;
    }}
    body[data-responsive-viewport="touch"] .topbar-tools {{
      flex-wrap: wrap;
      justify-content: start;
      width: 100%;
    }}
    body[data-responsive-viewport="touch"] .topbar-context {{
      width: 100%;
    }}
    body[data-responsive-viewport="touch"] .topbar-object-anchor {{
      width: 100%;
      min-width: 0;
    }}
    body[data-responsive-viewport="touch"] .continuity-lane,
    body[data-responsive-viewport="touch"] .operator-guidance-grid,
    body[data-responsive-viewport="touch"] .section-summary-grid,
    body[data-responsive-viewport="touch"] .trace-stage-grid,
    body[data-responsive-viewport="touch"] .workbench-columns {{
      grid-template-columns: 1fr;
    }}
    body[data-responsive-viewport="touch"] .context-chip {{
      max-width: 100%;
    }}
    body[data-responsive-viewport="touch"] .hero-main,
    body[data-responsive-viewport="touch"] .hero-side,
    body[data-responsive-viewport="touch"] .panel {{
      border-radius: 22px;
      padding: 18px;
    }}
    body[data-responsive-viewport="touch"] h1 {{
      max-width: none;
      font-size: clamp(2.2rem, 11vw, 3.3rem);
      line-height: 1.02;
    }}
    body[data-responsive-viewport="touch"][data-lang="zh"] h1 {{
      font-size: clamp(2rem, 10vw, 3.1rem);
      line-height: 1.14;
    }}
    body[data-responsive-viewport="touch"] .hero-copy {{
      font-size: 0.98rem;
    }}
    body[data-responsive-viewport="touch"] .hero-stage {{
      height: 150px;
    }}
    body[data-responsive-viewport="touch"] .stage-ring {{
      top: 24px;
      bottom: 20px;
      width: 124px;
    }}
    body[data-responsive-viewport="touch"] .stage-globe {{
      width: 112px;
      height: 112px;
      top: 22px;
    }}
    body[data-responsive-viewport="touch"] .stage-console {{
      width: 88px;
      height: 42px;
      bottom: 18px;
    }}
    body[data-responsive-viewport="touch"] .guide-grid {{
      gap: 10px;
    }}
    body[data-responsive-viewport="touch"] .workspace-mode-shell {{
      padding: 14px;
    }}
    body[data-responsive-viewport="touch"] .workspace-mode-card {{
      padding: 14px;
    }}
    body[data-responsive-viewport="touch"] .workspace-mode-object-anchor,
    body[data-responsive-viewport="touch"] .live-object-anchor,
    body[data-responsive-viewport="touch"] .guide-compact-card {{
      padding: 14px;
    }}
    body[data-responsive-viewport="touch"] .workspace-mode-object-title {{
      font-size: 1.28rem;
    }}
    body[data-responsive-viewport="touch"] .live-object-title {{
      font-size: 1.54rem;
    }}
    body[data-responsive-viewport="touch"] .guide-card,
    body[data-responsive-viewport="touch"] .deck-section,
    body[data-responsive-viewport="touch"] .control-cluster {{
      padding: 12px;
    }}
    body[data-responsive-viewport="touch"] .deck-mode-strip {{
      padding: 12px;
    }}
    body[data-responsive-viewport="touch"] .batch-toolbar-card {{
      top: 132px;
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
    body[data-modal-presentation="sheet"] .story-inspector-backdrop {{
      align-items: flex-end;
      justify-content: center;
      padding: 12px;
    }}
    body[data-modal-presentation="sheet"] .story-inspector-shell {{
      width: min(720px, 100%);
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
    body[data-modal-presentation="fullscreen"] .story-inspector-backdrop {{
      padding: 0;
      align-items: stretch;
      justify-content: stretch;
    }}
    body[data-modal-presentation="fullscreen"] .story-inspector-shell {{
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
      .workspace-mode-insight-grid {{ grid-template-columns: 1fr; }}
      .workspace-mode-shell[data-workspace-chrome="compact"] .workspace-mode-head {{
        grid-template-columns: 1fr;
      }}
      .workspace-mode-shell[data-workspace-chrome="compact"] .trace-stage-grid {{
        grid-template-columns: repeat(2, minmax(0, 1fr));
      }}
      .advanced-surface-grid {{ grid-template-columns: 1fr; }}
      .workspace-mode-group[data-workspace-group="review"] {{
        grid-template-columns: 1fr;
      }}
      .hero, .grid, .dual-grid {{ grid-template-columns: 1fr; }}
      .dual-grid[data-layout="master-detail"] > #section-board {{
        position: static;
        max-height: none;
        overflow: visible;
        grid-template-rows: none;
      }}
      .dual-grid[data-layout="master-detail"] > #section-board > #watch-list {{
        overflow: visible;
        padding-right: 0;
      }}
      .hero-main {{ order: 0; }}
      .hero-side {{ order: 1; }}
      .story-grid, .story-columns, .story-fact-grid {{ grid-template-columns: 1fr; }}
      .story-grid > .story-list {{
        position: static;
        max-height: none;
        padding-right: 0;
      }}
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
      .topbar-object-anchor {{ width: 100%; min-width: 0; }}
      .context-lens-backdrop {{
        padding: 12px;
      }}
      .context-lens-shell {{
        width: min(100%, 520px);
        border-radius: 24px;
      }}
      .story-inspector-backdrop {{
        padding: 0;
        align-items: flex-end;
        justify-content: stretch;
      }}
      .story-inspector-shell {{
        width: 100%;
        height: min(88vh, 100%);
        border-bottom-left-radius: 0;
        border-bottom-right-radius: 0;
      }}
      .continuity-lane,
      .operator-guidance-grid,
      .section-summary-grid,
      .trace-stage-grid,
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
      .workspace-mode-object-anchor,
      .live-object-anchor,
      .guide-compact-card {{
        padding: 14px;
      }}
      .workspace-mode-object-title {{
        font-size: 1.28rem;
      }}
      .live-object-title {{
        font-size: 1.54rem;
      }}
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
      .context-save-form {{
        grid-template-columns: 1fr;
      }}
      .hero-stage {{ display: none; }}
      .workspace-mode-shell[data-workspace-chrome="compact"] .trace-stage-grid {{
        grid-template-columns: 1fr;
      }}
      .nav-pill {{ white-space: nowrap; }}
      .batch-toolbar-card {{ top: 122px; }}
    }}
    @media (orientation: portrait) and (max-width: 900px) {{
      .shell {{ grid-template-columns: 1fr; }}
      .guide-grid,
      .workspace-mode-grid,
      .workspace-mode-insight-grid,
      .advanced-surface-grid,
      .continuity-lane,
      .operator-guidance-grid,
      .section-summary-grid,
      .trace-stage-grid,
      .workbench-columns,
      .preview-grid,
      .dual-grid,
      .story-grid,
      .story-columns {{
        grid-template-columns: 1fr;
      }}
      .story-fact-grid {{
        grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));
      }}
      .topbar-nav {{
        overflow-x: auto;
        scroll-snap-type: x mandatory;
        scrollbar-width: none;
      }}
      .topbar-nav::-webkit-scrollbar {{ display: none; }}
      .topbar-nav > * {{ scroll-snap-align: start; }}
      .context-lens-shell,
      .story-inspector-shell {{
        inset: auto 0 0 0;
        width: 100%;
        max-height: 85vh;
        border-radius: 22px 22px 0 0;
      }}
    }}
    @media (min-aspect-ratio: 21/9) {{
      .shell {{ max-width: 1760px; margin: 0 auto; }}
      .workspace-mode-grid {{
        grid-template-columns: repeat(auto-fit, minmax(360px, 440px));
      }}
    }}
    @media (orientation: landscape) and (max-height: 600px) {{
      .topbar {{ padding-block: 8px; top: 8px; }}
      .hero-stage {{ display: none; }}
      .workspace-mode-shell {{ padding: 14px; }}
    }}
    .card,
    .panel,
    .continuity-stage,
    .control-cluster,
    .deck-section,
    .batch-toolbar-card,
    .hero-main,
    .hero-side {{
      min-width: 0;
      overflow: hidden;
      overflow-wrap: anywhere;
      word-break: break-word;
    }}
    .md-shell {{
      container-type: inline-size;
      container-name: md-shell;
      display: grid;
      grid-template-columns: minmax(300px, 34%) 1fr;
      gap: 16px;
      align-items: start;
      min-height: calc(100vh - 220px);
    }}
    .md-list {{
      min-width: 0;
      display: grid;
      grid-template-rows: auto auto 1fr;
      gap: 10px;
      padding-right: 14px;
      border-right: 1px solid var(--line);
      position: sticky;
      top: 92px;
      max-height: calc(100vh - 120px);
      overflow: hidden;
    }}
    .md-list-head {{
      display: grid;
      gap: 10px;
    }}
    .md-list-scroll {{
      min-width: 0;
      overflow-y: auto;
      overflow-x: hidden;
      display: grid;
      gap: 8px;
      padding-right: 4px;
      scrollbar-width: thin;
    }}
    .md-list-scroll::-webkit-scrollbar {{ width: 6px; }}
    .md-list-scroll::-webkit-scrollbar-thumb {{
      background: rgba(214, 196, 177, 0.18);
      border-radius: 3px;
    }}
    .md-detail {{
      min-width: 0;
      display: grid;
      gap: 14px;
      align-content: start;
    }}
    .md-detail-empty {{
      padding: 36px 28px;
      text-align: center;
      border-radius: 18px;
      border: 1px dashed rgba(214, 196, 177, 0.22);
      color: var(--muted);
      background: rgba(248, 239, 230, 0.02);
    }}
    .md-list .md-list-filter {{
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
    }}
    .md-list .md-list-search {{
      display: grid;
      grid-template-columns: 1fr auto;
      gap: 8px;
      align-items: center;
    }}
    .md-list .md-list-search input {{
      width: 100%;
      min-width: 0;
    }}
    .md-list .card.selectable {{
      padding: 12px 14px;
    }}
    .md-list .card.selectable .card-title {{
      font-size: 0.95rem;
      line-height: 1.35;
    }}
    .md-back-btn {{ display: none; }}
    .guide-disclosure {{
      border: 1px solid rgba(214, 196, 177, 0.14);
      border-radius: 18px;
      background: linear-gradient(180deg, rgba(37, 28, 22, 0.66), rgba(24, 18, 15, 0.62));
      box-shadow: inset 0 0 0 1px rgba(248, 239, 230, 0.03);
      overflow: hidden;
      min-width: 0;
      overflow-wrap: anywhere;
    }}
    .guide-disclosure > summary {{
      list-style: none;
      cursor: pointer;
      padding: 14px 16px;
      display: grid;
      grid-template-columns: 1fr auto auto;
      gap: 10px 14px;
      align-items: center;
      user-select: none;
    }}
    .guide-disclosure > summary::-webkit-details-marker {{
      display: none;
    }}
    .guide-disclosure > summary:hover {{
      background: rgba(248, 239, 230, 0.03);
    }}
    .guide-disclosure-kicker {{
      font: 700 10px/1 var(--mono);
      letter-spacing: 0.08em;
      text-transform: uppercase;
      color: var(--muted);
    }}
    .guide-disclosure-title {{
      font-family: var(--headline);
      font-size: 1rem;
      letter-spacing: 0.04em;
      color: var(--ink);
      margin-top: 4px;
      line-height: 1.35;
    }}
    .guide-disclosure-toggle {{
      font: 600 11px/1 var(--mono);
      letter-spacing: 0.08em;
      text-transform: uppercase;
      color: var(--muted);
      padding: 4px 10px;
      border-radius: 999px;
      border: 1px solid rgba(214, 196, 177, 0.18);
      background: rgba(248, 239, 230, 0.03);
    }}
    .guide-disclosure-chevron {{
      width: 18px;
      height: 18px;
      transition: transform .18s ease;
      color: var(--muted);
    }}
    .guide-disclosure[open] > summary > .guide-disclosure-chevron {{
      transform: rotate(180deg);
    }}
    .guide-disclosure[open] > summary {{
      border-bottom: 1px solid rgba(214, 196, 177, 0.12);
    }}
    .guide-disclosure-body {{
      padding: 14px 16px 18px;
      display: grid;
      gap: 12px;
    }}
    @container md-shell (max-width: 820px) {{
      .md-shell {{
        grid-template-columns: 1fr;
        min-height: 0;
      }}
      .md-shell[data-md-mode="detail"] .md-list {{ display: none; }}
      .md-shell[data-md-mode="list"] .md-detail {{ display: none; }}
      .md-list {{
        position: static;
        padding-right: 0;
        border-right: none;
        max-height: none;
      }}
      .md-back-btn {{ display: inline-flex; }}
    }}
    a:focus-visible,
    input:focus-visible,
    select:focus-visible,
    textarea:focus-visible,
    [tabindex]:not([tabindex="-1"]):focus-visible,
    .workspace-mode-card:focus-visible,
    .nav-pill:focus-visible,
    .card:focus-visible {{
      outline: 2px solid var(--accent);
      outline-offset: 2px;
      border-radius: inherit;
    }}
    @media (prefers-reduced-motion: reduce) {{
      *, *::before, *::after {{
        animation-duration: 0.001ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.001ms !important;
        scroll-behavior: auto !important;
      }}
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
          <span id="topbar-subtitle">Workflow stages | Start -&gt; Monitor -&gt; Review -&gt; Deliver</span>
        </div>
      </div>
      <nav class="topbar-nav ui-segment" aria-label="Primary Workflow Stages">
        <button class="nav-pill ui-segment-button" id="nav-intake" type="button" data-jump-target="section-intake" data-workspace-mode="intake">Start</button>
        <button class="nav-pill ui-segment-button" id="nav-missions" type="button" data-jump-target="section-board" data-workspace-mode="missions">Monitor</button>
        <button class="nav-pill ui-segment-button" id="nav-review" type="button" data-jump-target="section-triage" data-workspace-mode="review">Review</button>
        <button class="nav-pill ui-segment-button" id="nav-delivery" type="button" data-jump-target="section-ops" data-workspace-mode="delivery">Deliver</button>
      </nav>
      <div class="topbar-tools">
        <div class="topbar-context" id="context-shell">
          <button class="topbar-object-anchor ui-action-button" id="context-summary" type="button" aria-expanded="false" aria-haspopup="dialog" aria-controls="context-lens-shell">
            <span class="topbar-object-kicker" id="context-summary-kicker">Mission Intake</span>
            <span class="topbar-object-title" id="context-summary-detail" data-fit-text="context-summary-detail" data-fit-fallback="30">No active object</span>
          </button>
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
                <h2 class="panel-title" id="guide-panel-title">Workflow Stages</h2>
              </div>
              <span class="chip ok" id="guide-chip">Start -> Monitor -> Review -> Deliver</span>
            </div>
            <div class="panel-sub" id="guide-panel-copy">Create or clone a mission here. Monitoring owns runs and results, Review owns triage and stories, and advanced claim or report workspaces stay nested until they are needed.</div>
            <div class="shortcut-strip">
              <span class="chip" id="shortcut-focus">/ focus draft</span>
              <span class="chip" id="shortcut-preset">1-4 load preset</span>
              <span class="chip" id="shortcut-submit">Cmd/Ctrl+Enter deploy</span>
            </div>
            <div class="actions section-jumps">
              <button class="btn-secondary" id="jump-cockpit" type="button" data-jump-target="section-cockpit">Cockpit</button>
              <button class="btn-secondary" id="jump-triage" type="button" data-jump-target="section-triage">Triage</button>
              <button class="btn-secondary" id="jump-story" type="button" data-jump-target="section-story">Stories</button>
              <button class="btn-secondary" id="jump-ops" type="button" data-jump-target="section-ops">Ops</button>
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
          <div class="actions" id="create-watch-clones"></div>
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
    <section class="dual-grid" data-layout="master-detail">
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
      <div class="story-workspace-mode-switch ui-segment" id="story-workspace-mode-switch">
        <span class="mono" id="story-mode-switch-label"></span>
        <button class="ui-segment-button" id="story-mode-board-button" type="button" data-story-workspace-mode="board"></button>
        <button class="ui-segment-button" id="story-mode-editor-button" type="button" data-story-workspace-mode="editor"></button>
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

    <details class="advanced-surface-shell" id="review-advanced-shell">
      <summary>
        <div class="advanced-surface-summary-copy">
          <div class="advanced-surface-kicker" id="review-advanced-kicker">Secondary Review Tools</div>
          <div class="advanced-surface-title" id="review-advanced-title">Claim &amp; Report Tools</div>
          <div class="panel-sub" id="review-advanced-copy">Open claim composition and report assembly only when review needs structured output beyond triage and story editing.</div>
        </div>
        <div class="advanced-surface-meta">
          <span id="review-advanced-chip">On demand · Claim Composer · Report Studio</span>
        </div>
      </summary>
      <div class="advanced-surface-grid">
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
              <div class="panel-sub" id="report-studio-copy">Inspect report sections, quality guardrails, and export sheets over persisted report objects.</div>
            </div>
          </div>
          <div class="stack" id="report-studio-shell"></div>
        </section>
      </div>
    </details>
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

      <details class="advanced-surface-shell" id="delivery-advanced-shell">
        <summary>
          <div class="advanced-surface-summary-copy">
            <div class="advanced-surface-kicker" id="delivery-advanced-kicker">Secondary Delivery Tools</div>
            <div class="advanced-surface-title" id="delivery-advanced-title">AI &amp; Route Health</div>
            <div class="panel-sub" id="delivery-advanced-copy">Open AI projection inspection and route-health drill-down only when delivery needs diagnosis beyond dispatch posture and history.</div>
          </div>
          <div class="advanced-surface-meta">
            <span id="delivery-advanced-chip">On demand · AI Assistance · Distribution Health</span>
          </div>
        </summary>
        <div class="advanced-surface-grid">
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
                <h2 class="panel-title" id="distribution-title">Distribution Health</h2>
                <div class="panel-sub" id="distribution-copy">See whether named delivery routes are healthy and which upstream work is feeding them.</div>
              </div>
              <span class="chip" id="distribution-mode">Read-only</span>
            </div>
            <div class="stack" id="route-health"></div>
          </article>
        </div>
      </details>
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
        <div class="context-object-rail" id="context-object-rail" data-context-object-rail></div>
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
          <div class="context-lens-utility-shell">
            <div class="context-lens-utility-title" id="context-utilities-title">Utilities</div>
            <div class="context-lens-utility-row">
              <button class="btn-secondary palette-trigger" id="palette-open" type="button">Command Palette</button>
              <button class="btn-secondary" id="context-reset" type="button">Reset Context</button>
            </div>
            <div class="context-lens-utility-row">
              <button class="btn-secondary" id="context-open-section" type="button">Open Section</button>
              <button class="btn-secondary" id="context-copy-link" type="button">Copy Link</button>
            </div>
            <div class="lang-switch" id="language-switch" aria-label="Language Switch">
              <button class="lang-btn active" id="lang-en" type="button" data-lang="en">EN</button>
              <button class="lang-btn" id="lang-zh" type="button" data-lang="zh">简中</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
  <div class="story-inspector-backdrop" id="story-inspector-backdrop" hidden>
    <div class="story-inspector-shell" id="story-inspector-shell" role="dialog" aria-modal="true" aria-labelledby="story-inspector-title" aria-describedby="story-inspector-copy" tabindex="-1">
      <div class="story-inspector" id="story-inspector">
        <div class="story-inspector-head">
          <div class="story-inspector-head-copy">
            <div class="mono" id="story-inspector-kicker">Story Inspector</div>
            <div class="story-inspector-title" id="story-inspector-title">Story Export Sheet</div>
            <div class="story-inspector-copy" id="story-inspector-copy">Review exported markdown or the persisted story JSON without pushing raw output into the main workspace column.</div>
          </div>
          <button class="btn-secondary" id="story-inspector-close" type="button">Close</button>
        </div>
        <div class="story-inspector-body" id="story-inspector-body"></div>
        <div class="story-inspector-footer" id="story-inspector-footer"></div>
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
