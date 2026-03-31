# DataPulse Console Interaction Clarity Blueprint

Status: repo-scoped follow-up blueprint, manual ignition ready

Created: 2026-03-31

## Goal

Promote the `agent-skills-hub` frontend extraction into DataPulse repo truth as a narrow console-clarity wave.

The target is not to replace the current command chamber, introduce a second frontend product, or fork lifecycle state into the browser.

The target is to:

- make the current console stages easier to understand at a glance
- make important workspace context shareable and restorable through URL state
- centralize operator guidance and action-explanation surfaces
- reduce future console iteration risk by introducing clearer client and state boundaries

## Repo Read Correction

Current DataPulse already has the important operating surface:

- a Reader-backed browser console in `datapulse/console_server.py` and `datapulse/console_markup.py`
- lifecycle rail coverage across intake, mission board, cockpit, triage, story, report, and delivery
- mission presets, route suggestions, duplicate explain, retry guidance, action history, and keyboard or palette affordances
- text-fit and overflow-evidence hardening from the completed `L22` and `L23` waves

The remaining gap is narrower than "needs a better frontend":

- important workspace context still mixes hash, local storage, and in-memory state in ways that are hard to share or restore cleanly
- major sections do not yet expose a consistent success-signal versus blocker-signal framing
- operator guidance and explanation copy exist, but they are still scattered across deck hints, retry cards, and inline labels instead of one owned contract
- client-side API and state logic still live mainly inside one markup bundle, which slows safe iteration and verification

## What `agent-skills-hub` Gets Right For This Repo

The useful extracted capability is not its product category. It is interaction shape.

High-value patterns to import:

1. URL-restorable state for filters, selected views, and operating context
2. clearer separation between entry actions, operating results, and deeper detail panes
3. consistent information hierarchy for list, detail, loading, and error states
4. a centralized client layer instead of repeated request construction inside every render surface
5. action feedback that leaves persistent context behind instead of relying only on transient toast success
6. badge-like summary signals that can expand into explanation without overwhelming the default surface

Repo implication:

- DataPulse should import clarity and restoration patterns, not copy `agent-skills-hub` as a frontend stack or product shell

## What This Wave Must Preserve

Invariants for this wave:

1. `WatchMission`, `DataPulseItem`, `Story`, `Report`, and named routes remain the canonical lifecycle nouns
2. the browser must stay a projection over Reader, CLI, MCP, and HTTP semantics rather than inventing GUI-only business state
3. existing mission presets, route guidance, duplicate explain, and retry advice are preserved and extended, not rewritten from scratch
4. URL state should refine the current section and story context model rather than replacing it with a parallel routing system
5. operator guidance must stay attributable to real persisted state and backend-derived facts
6. maintainability extraction should reduce console bundle coupling without forcing an immediate React or Vite migration

## What Should Not Be Reopened In This Wave

This wave should not reopen:

- a default React or Vite migration as the next mandatory step
- a second browser-only state model for mission, triage, story, or report flow
- a generic admin-dashboard visual language that discards the current command chamber identity
- lifecycle reshaping that breaks Reader parity in exchange for page-level neatness
- duplicated explanation logic that reimplements existing retry, duplicate, or route-health semantics without reusing them

## L24 Slice Map

| Slice | Outcome | Why it exists |
| --- | --- | --- |
| `L24.1` | Land this repo-scoped console interaction-clarity blueprint and manual ignition map | Converts the external extraction into repo truth and reopens the console lane after the completed `L23` wave |
| `L24.2` | Freeze the URL-restorable workspace-state, section-summary, and operator-guidance contract | Prevents implementation drift before state, copy ownership, and explanation boundaries are explicit |
| `L24.3` | Add URL-restorable workspace context and section-level success/blocker cards in the current console shell | Lands the highest-value operator clarity improvement without changing lifecycle nouns |
| `L24.4` | Centralize guidance and action-explanation surfaces across mission, triage, story, and route lanes | Makes copy and next-step reasoning consistent instead of leaving it scattered across the shell |
| `L24.5` | Extract console client/state helpers and harden restored-context browser smoke | Improves maintainability and verification after the new context and guidance semantics land |

## Recommended Ignition Order After This Refresh

Recommended order after this refresh:

1. `L24.2`
2. `L24.3`
3. `L24.4`
4. `L24.5`

This order keeps the next work narrow:

- first freeze the workspace-state and guidance contract
- then land restorable context plus section-level success or blocker framing
- then consolidate explanation and help surfaces
- then extract helpers and harden smoke for the new restored-context paths

## Manual Ignition Boundary

The next manual ignition target should be `L24.2`, not `L24.3` or `L24.5`.

Reason:

- current DataPulse already has mission presets, route snaps, retry guidance, and duplicate explain fragments
- the immediate gap is contract clarity, not more heuristics
- URL state, section summary cards, and guidance ownership should be explicit before implementation spreads across markup, docs, tests, and smoke flows

After the blueprint landing is committed and the repo is back to a clean baseline, the normal local ignition entrypoint stays:

```bash
bash scripts/governance/ignite_datapulse_codex_loop.sh
```

Expected next slice after this blueprint landing: `L24.2`

## Fact Sources

- `/Users/sunyifei/Library/Mobile Documents/iCloud~md~obsidian/Documents/SunYifei/01-项目开发/DataPulse/00_索引与计划/DataPulse_agent-skills-hub前端交互清晰化补强清单_2026-03-31.md`
- `/Users/sunyifei/DataPulse/docs/gui_intelligence_console_plan.md`

## Success Condition

DataPulse improves console clarity without reopening frontend architecture:

- important workspace context is shareable and restorable
- each major lane can show operators what success or blockage currently looks like
- guidance and explanation surfaces are centralized enough to stay consistent
- the browser remains a Reader-backed command chamber rather than drifting into a second product
