# DataPulse Research OS Report Production Blueprint

## Purpose

This document distills the external Obsidian note `DataPulse_GUI_Research_OS_报告生产系统路线图_2026-03-12.md` into repository-relevant blueprint truth.

The goal is not to import a broad product essay into the repo. The goal is to decide which facts justify the next structured blueprint slices for DataPulse.

## Current Repo Read

The current repository now has a lifecycle-complete intelligence console that reaches:

- `WatchMission`
- `MissionRun`
- `DataPulseItem` triage
- `Story` assembly
- `AlertEvent` plus story export and route health

Current repo anchors:

- `docs/intelligence_lifecycle_contract.md`
- `docs/gui_intelligence_console_plan.md`
- `datapulse/core/story.py`
- `datapulse/reader.py`
- `datapulse/cli.py`
- `datapulse/mcp_server.py`
- `datapulse/console_server.py`
- `datapulse/console_markup.py`

That means the highest-leverage delta is no longer more shell polish or another browser-only surface. The highest-leverage delta is a structured report layer above `Story`.

## Canonical Report-Layer Stage Mapping

The follow-up lifecycle extension for this wave is explicit and additive:

- `Story` remains the canonical evidence package.
- `ReportBrief` captures report intent and scope above a stable story snapshot.
- `ClaimCard` introduces bounded claims with citation-backed evidence.
- `ReportSection` is deterministic section composition over claim cards.
- `Report` is the assembled artifact with quality state.
- `ExportProfile` selects shape (`brief`, `full`, `sources`, `watch_pack`) and metadata.

Invariants to enforce before `L14.3` code work:

1. Report-layer objects must never redefine mission/triage/story truth.
2. `Story` evidence is immutable source-of-truth for report-derived claims.
3. Claim/export decisions are repository-visible, deterministic, and reversible by contract changes.
4. Report outputs must remain reusable and provenance-preserving for watch refinement.
5. No GUI-only report state is allowed before Reader-backed report stores exist.

Stage map for implementation:

- `L14.2`: contract and roadmapping alignment (`ReportBrief`, `ClaimCard`, `ReportSection`, `CitationBundle`, `Report`, `ExportProfile`).
- `L14.3`: add core persistence for report nouns.
- `L14.4`: add deterministic claim/citation/quality logic.
- `L14.5`: expose report CRUD/compose/quality/export on reader, CLI, MCP, and API.
- `L14.6`: project report objects into the browser workspace.
- `L14.7`: finalize output profiles and watch-feedback hooks.
- `L14.8`: lock in cross-surface verification coverage.

## High-Value Facts To Promote

### 1. `Story` is an evidence package, not the final research asset

Current repo reality:

- `Story` already preserves evidence, timeline, contradiction, and provenance semantics.
- `story export` exists, but it remains a handoff format rather than a durable report object.

Repo implication:

- do not keep bloating `Story` until it behaves like a report
- add an additive report layer above `Story`

### 2. `Claim` is the minimum judgment unit for high-quality report production

The strongest upgrade from the external note is not "better Markdown generation". It is a first-class object for one bounded judgment with evidence and limits.

Repo implication:

- the report layer should persist `ClaimCard`-class objects instead of hiding judgments in one free-text body
- citation binding and claim limits should live in core data, not only in GUI rendering

### 3. Report production must stay Reader-backed across CLI, MCP, and browser surfaces

The current repository already treats the browser console as a projection over shared Reader-backed objects.

Repo implication:

- do not open a GUI-only report state machine
- land report objects in core plus Reader first, then project them into CLI, MCP, API, and browser

### 4. Quality gates belong in domain logic before they appear in the GUI

The external note is right that uncited claims, single-source sections, and unresolved contradictions should block formal export. Those are not styling concerns.

Repo implication:

- implement report quality evaluation in core and expose it through Reader-backed surfaces
- keep guardrail outputs operator-visible instead of silently mutating narrative text

### 5. Export is multi-shape and should feed back into watch refinement

The strongest report outputs are not limited to one Markdown file. They include:

- brief
- full report
- source pack
- watch-pack follow-up

Repo implication:

- `ExportProfile` should become a first-class report-layer concept
- report outputs should be reusable for downstream watch refinement instead of ending as a dead-end file

### 6. The report layer should extend the lifecycle contract additively, not replace current nouns

Current repo truth is stable around `Watch -> Triage -> Story -> delivery`.

Repo implication:

- the report layer should extend that chain rather than reopening mission, triage, or story semantics
- `Story` remains the evidence-preserving middle layer even after report work lands

## What Should Not Be Promoted As First-Class Slices Now

The external note does not justify immediate blueprint slices for:

- a browser rewrite or second frontend stack
- a generic freeform rich-text editor before report objects exist
- LLM-only report generation without source-bound claim objects
- multi-user collaboration or auth work
- replacing `Story` with `Report`

Those are either premature or would weaken the existing Reader-backed contract.

## Integration Rules For This Phase

All follow-up slices in this phase should obey the same constraints:

1. Preserve `Story` as the evidence package layer.
2. Add `ReportBrief`, `ClaimCard`, `ReportSection`, `CitationBundle`, `Report`, and `ExportProfile` as additive report-layer objects.
3. Keep report quality evaluation deterministic and operator-visible by default.
4. Project report nouns through Reader, CLI, MCP, API, and browser instead of inventing GUI-only state.
5. Treat `Claim Composer` and `Report Studio` as projections over persisted report objects, not as isolated editors.
6. Keep report exports provenance-preserving and reusable for later watch refinement.
7. Keep slices narrow enough that the loop can stop on machine-decidable progress.

## Stage Preview

Recommended stage language for this follow-up wave:

- `R0`: existing repo baseline `Watch -> Triage -> Story -> story export`
- `R1`: report-layer contract and lifecycle extension
- `R2`: report-layer core objects and persistence
- `R3`: claim composition, citation bundles, and quality guardrails
- `R4`: Reader, CLI, MCP, and API projection
- `R5`: browser `Claim Composer` and `Report Studio`
- `R6`: export profiles, watch-pack feedback, and regression hardening

## L14 Slice Map

| Slice | Outcome | Why it exists |
| --- | --- | --- |
| `L14.1` | Land this repo-scoped Research OS report-production blueprint and ignition map | Converts the external route-map note into repo truth without jumping straight from concept to one oversized implementation slice |
| `L14.2` | Extend the lifecycle contract and roadmap with report-layer nouns, stage mapping, and invariants | Fixes how `Story`, `ClaimCard`, `ReportSection`, `Report`, and `ExportProfile` relate before code starts drifting |
| `L14.3` | Add report-layer core objects and persistence | Makes reports first-class repo objects instead of large strings or GUI-only state |
| `L14.4` | Add claim composition, citation bundles, and report quality guardrails | Lands the core composition and trust logic before surface-level UI work |
| `L14.5` | Expose report CRUD, compose, quality, and export through Reader, CLI, MCP, and HTTP API | Preserves cross-surface parity and keeps the browser as a projection rather than a fork |
| `L14.6` | Add browser `Claim Composer` and `Report Studio` inside the current console shell | Delivers the GUI value without abandoning the existing console workbench |
| `L14.7` | Add `brief / full / sources / watch-pack` export profiles and report-to-watch feedback hooks | Turns report work into reusable research assets instead of one dead-end Markdown output |
| `L14.8` | Harden verification for report persistence, claim traceability, quality gates, and end-to-end export flows | Protects the new report layer from silent regressions before another expansion wave lands |

## Recommended Ignition Order After This Refresh

Recommended order after this refresh:

1. `L14.2`
2. `L14.3`
3. `L14.4`
4. `L14.5`
5. `L14.6`
6. `L14.7`
7. `L14.8`

This order keeps DataPulse from jumping directly into a GUI writing surface before the report layer has nouns, persistence, trust logic, and cross-surface contracts.
