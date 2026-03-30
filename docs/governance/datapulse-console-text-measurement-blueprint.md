# DataPulse Console Text Measurement And Multilingual Layout Hardening Blueprint

Status: repo-scoped follow-up blueprint, manual ignition ready

Created: 2026-03-30

## Goal

Promote the `pretext` extraction into DataPulse repo truth as a narrow console and text-infrastructure follow-up.

The target is not to import a full browser text engine. The target is to:

- harden mixed-script truncation and excerpt behavior
- improve pixel-fit behavior for dense console labels, chips, and summaries
- keep the browser shell Reader-backed and free of GUI-only business state

## Repo Read Correction

Current DataPulse already has the important operating surfaces:

- a browser console shell in `datapulse/console_markup.py`
- shared excerpt helpers in `datapulse/core/utils.py`
- responsive interaction contracts and browser smoke coverage

The remaining gap is narrower than "missing text layout":

- `generate_excerpt(...)` is character-count oriented rather than grapheme-safe
- dense console labels currently rely mostly on CSS ellipsis rather than measured pixel-fit behavior
- mixed CJK, emoji, and mixed-script strings can still degrade readability in populated states

## Distilled Value From Pretext

The extracted value that maps cleanly onto this repo is:

- two-phase measurement is the right performance pattern: precompute once, relayout cheaply
- segmentation matters more than raw string length for multilingual text
- grapheme-safe truncation is the first high-value adoption point
- emoji and browser measurement quirks should stay isolated behind caches and correction layers
- full multiline layout is optional and should only open after a real hotspot is proven

## What DataPulse Should Not Copy

- do not port the whole Pretext engine into Python or inline it wholesale into the console bundle
- do not introduce a second text-domain model or browser-only lifecycle object
- do not optimize speculative virtualization or multiline prelayout before a proven hotspot exists

## Ignition Map

### L22.1 Blueprint Promotion

Land this repo-scoped blueprint, wire it into the active `blueprint plan`, and expose a new narrow manual ignition target.

### L22.2 Grapheme-Safe Truncation

First implementation target:

- add a shared grapheme-aware truncation helper in `datapulse/core/utils.py`
- keep behavior deterministic for CLI, Reader, Markdown export, and console surfaces
- add regression coverage for emoji, ZWJ sequences, CJK, and mixed-script strings

This is the next manual ignition target because it improves every text surface without requiring browser-only measurement logic.

### L22.3 Dense-Panel Pixel-Fit Measurement

Second implementation target:

- add cached canvas width helpers in `datapulse/console_markup.py`
- apply them only to selected dense labels, chips, or rail summaries where CSS ellipsis is not enough
- keep fallback behavior clean when measurement is unavailable

### L22.4 Optional Hotspot-Driven Prelayout

Third and conditional target:

- evaluate whether any dense multiline console hotspot actually needs a `prepare/layout`-style cache
- only open this path after real console evidence justifies it

This keeps DataPulse from importing a large text-layout surface before the repo proves it needs one.

## Manual Ignition Boundary

The next manual ignition target should be `L22.2`, not `L22.3` or `L22.4`.

Reason:

- shared truncation semantics are the smallest high-value adoption point
- deterministic grapheme-safe behavior benefits backend and browser surfaces together
- canvas measurement should build on top of corrected truncation semantics, not replace them

After the blueprint landing is committed and the repo is back to a clean baseline, the normal local ignition entrypoint stays:

```bash
bash scripts/governance/ignite_datapulse_codex_loop.sh
```

Expected next slice after this blueprint landing: `L22.2`

## Fact Sources

- `/Users/sunyifei/Library/Mobile Documents/iCloud~md~obsidian/Documents/SunYifei/01-项目开发/DataPulse/00_索引与计划内/pretext_text_measurement_extraction_for_datapulse.md`
- `/Users/sunyifei/DataPulse/docs/pretext_text_measurement_extraction_for_datapulse.md`

## Success Condition

DataPulse improves multilingual text behavior in the current shell through narrow, repo-owned infrastructure steps:

- deterministic grapheme-safe truncation first
- cached browser measurement second
- optional deeper prelayout only after hotspot evidence

That sequence strengthens operator ergonomics without reopening the console architecture or inventing a parallel frontend product.
