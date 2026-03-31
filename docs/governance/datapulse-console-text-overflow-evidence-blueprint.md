# DataPulse Console Text Overflow Runtime Evidence Blueprint

Status: repo-scoped follow-up blueprint, manual ignition ready

Created: 2026-03-31

## Goal

Promote the post-`L22` follow-up into DataPulse repo truth as a narrow runtime-evidence wave.

The target is not to add more measurement machinery immediately. The target is to:

- collect repo-owned evidence for any console text surfaces that still overflow after the landed grapheme-safe truncation and cached canvas-fit work
- make those residual hotspots operator-visible or smoke-exportable
- keep later adapter-normalization or multiline-measurement work closed unless the repo proves it is needed

## Repo Read Correction

`L22` already landed the highest-value fixes:

- shared grapheme-safe truncation in `datapulse/core/utils.py`
- cached canvas-fit handling in `datapulse/console_markup.py` for selected dense labels, chips, and summaries
- regression coverage and browser smoke for the known single-line hotspots

The remaining gap is now narrower than "better text layout":

- the repo does not yet emit a stable inventory of residual overflow hotspots after the landed fit and truncation layers run
- browser smoke still proves rendered states, but it does not yet export named overflow-hit facts for follow-up admission decisions
- future adapter normalization or multiline escalation would be speculative unless those residual hotspots are first measured and named

## What This Wave Should Produce

- lightweight runtime evidence for selected dense console text containers
- smoke-visible or draft-artifact-visible counts of overflow survivors after current fit or truncation behavior applies
- an admission boundary for whether later console text work should reopen at all

## What DataPulse Should Not Do Yet

- do not reopen grapheme-safe truncation work that `L22.2` already landed
- do not normalize every `data-fit-*` surface contract before the repo proves reuse pressure exists
- do not open `prepare/layout`-style multiline measurement before real residual hotspots justify it

## Ignition Map

### L23.1 Blueprint Promotion

Land this repo-scoped follow-up blueprint, wire it into the active `blueprint plan`, and reopen a manual ignition target beyond the completed `L22` wave.

### L23.2 Runtime Overflow Hit Evidence

Next implementation target:

- instrument selected dense console text surfaces so the runtime can name when current fit or truncation still leaves overflow pressure behind
- expose the resulting facts through browser smoke and/or a draft evidence artifact rather than relying on screenshot-only inspection
- keep the evidence narrow to console text ergonomics and avoid coupling it to AI-surface admission or unrelated governance exporters

Landing shape for this slice:

- maintain a repo-owned runtime evidence summary keyed by `data-fit-text` surface ids
- surface survivor counts and named hotspots in `Ops Snapshot`
- export the same structured evidence through `scripts/datapulse_console_browser_smoke.py`

This is the next manual ignition target because it produces the missing admission evidence for whether any later text-fit adapter normalization or multiline escalation is justified.

## Manual Ignition Boundary

The next manual ignition target should be `L23.2`.

Reason:

- `L22` already closed the highest-value implementation fixes
- the next unknown is not "how to measure text better" but "which surfaces still need help after the current fix set"
- evidence should open future work, not architecture preference

After the blueprint landing is committed and the repo is back to a clean baseline, the normal local ignition entrypoint stays:

```bash
bash scripts/governance/ignite_datapulse_codex_loop.sh
```

Expected next slice after this blueprint landing: `L23.2`

## Fact Sources

- `/Users/sunyifei/Library/Mobile Documents/iCloud~md~obsidian/Documents/SunYifei/01-项目开发/DataPulse/00_索引与计划内/DataPulse_下一波blueprint候选切片_2026-03-31.md`
- `/Users/sunyifei/DataPulse/docs/governance/datapulse-console-text-measurement-blueprint.md`

## Success Condition

DataPulse can now decide whether more console text work is justified using repo-owned evidence instead of guesswork:

- residual overflow hotspots are named and reproducible
- later adapter-normalization work stays closed until reuse pressure is proven
- deeper multiline or `prepare/layout`-style work stays closed until the narrower evidence says the current single-line strategy is insufficient
