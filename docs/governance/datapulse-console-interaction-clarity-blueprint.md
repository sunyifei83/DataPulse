# DataPulse Console Interaction Clarity Blueprint

Status: repo-scoped follow-up blueprint, `L24.5` landed; handoff moved to `L25`

Created: 2026-03-31

Updated: 2026-03-31

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

## L24.2 Contract Freeze

`L24.2` is now the repo-owned contract freeze for three things:

1. which console context is shareable and restorable through the URL
2. which section-level summary cards are required before the next shell implementation slice lands
3. which source owns operator guidance and explanation copy

### URL-Restorable Workspace State

Only shareable operating context belongs in the canonical URL.

| Scope | Canonical URL contract | Why it belongs in URL state | Explicitly not URL state |
| --- | --- | --- | --- |
| Active shell section | hash-based section focus: `#section-intake`, `#section-board`, `#section-cockpit`, `#section-triage`, `#section-story`, `#section-claims`, `#section-report-studio`, `#section-ops` | lets operators refresh or share the current lane without introducing a second routing tree | a separate workspace-mode query param; workspace mode continues to derive from section focus |
| Mission workspace | `watch_search`, `watch_id` | preserves the mission search and selected mission context that operators actually review | unsaved `Deploy Mission` draft fields, mission deck collapse state, transient success toasts |
| Triage workspace | `triage_filter`, `triage_search`, `triage_id` | preserves queue scope and the currently inspected inbox item | temporary keyboard focus, modal open state, note composer cursor state |
| Story workspace | `story_view`, `story_filter`, `story_sort`, `story_search`, `story_id`, `story_mode` | preserves the story board or editor context that operators may need to reopen or share | unsaved editor text, one-off inspector expansions, temporary export preview toggles |
| Saved views and deep links | saved views and context-lens share links store the full canonical URL as their payload | keeps one canonical state contract instead of inventing separate share payload schemas | extra first-class params for pinned views, saved-view names, or link-history bookkeeping |

Local-only convenience state stays outside the URL contract:

- `create-watch-draft`, command-palette recent items or query text, context-link history, and the saved-view catalog remain local storage concerns
- language preference remains local preference, not shareable workspace truth
- reversible mutation history, toast visibility, modal open or close state, and dismissible helper banners remain transient UI state
- `L24.3` should only add a new URL parameter if the state is operator-meaningful, stable across refresh, and safe to share as repo truth

### Required Section Summary Cards

`L24.3` must add one summary frame per required section with:

1. the current objective
2. one success card showing what is already working
3. one blocker card showing the dominant blocker or next unsatisfied prerequisite

These are the required sections for admission in this wave:

| Section | Objective frame must answer | Success card must answer | Blocker card must answer | Current fact inputs |
| --- | --- | --- | --- | --- |
| `section-intake` | what mission or route-aware watch the operator is preparing to launch | whether the current draft can already map to a valid mission or reusable preset/clone source | which required field or route prerequisite is still missing before create or clone should proceed | current deploy form state, preset/clone source, available named routes |
| `section-board` | which mission set is currently under review | whether there are missions or search hits worth continuing into cockpit | whether the board is empty, filtered to zero, or missing the next mission context needed for inspection | watch list, search term, selected mission |
| `section-cockpit` | what the selected mission is doing now | whether recent runs, results, or current alert settings show the mission is inspectable and alive | whether there is no selected mission, the latest run failed, or retry guidance indicates the next operator action | selected watch detail, recent runs, latest failure, retry guidance |
| `section-triage` | which inbox slice requires review | whether the current queue or selected item is moving toward verification, duplicate resolution, or story promotion | whether backlog pressure, duplicate uncertainty, or missing selection is blocking the next review action | triage stats, selected item, duplicate explain, review state |
| `section-story` | which story or evidence package is being advanced | whether the selected story has enough evidence, timeline, or export-ready context to move forward | whether missing story selection, unresolved contradiction, or evidence gaps are blocking promotion or export | story detail, conflicts, evidence stack, export preview |
| `section-ops` | which route or delivery posture the operator is supervising | whether daemon, route health, and recent delivery observations show the lane is healthy enough to trust | whether degraded or missing routes, collector trouble, or delivery failures require remediation | daemon status, route health, alerts, ops summary |

Additional rules:

- these cards must be backed by current Reader-derived or persisted facts, not browser-only heuristics
- when a hard blocker does not exist, the blocker slot should show the next unsatisfied prerequisite or dominant operational risk rather than decorative reassurance
- `section-claims` and `section-report-studio` may adopt the same card schema later, but they are not required admission blockers for `L24.3`

### Operator Guidance Ownership

Operator guidance must stay attributable to one canonical owner per copy class.

| Copy class | Canonical owner | Examples | Must not happen |
| --- | --- | --- | --- |
| Runtime explanation facts | Reader/API-backed guidance already exposed by the shell | mission retry guidance, duplicate explain, route-health remediation, server-derived mission suggestions | the browser invents a conflicting explanation from local-only heuristics |
| Static field semantics and parameter help | `docs/datapulse_console_parameter_guide.md` | alert-rule field meaning, route vs domain semantics, shared `digest_profile` defaults, prompt-pack provenance rules | ad hoc inline labels become the only place where parameter meaning is defined |
| Cross-section summary framing and shared operator wording | this blueprint now; later implemented as one shared shell contract in `L24.4` | success-card headings, blocker-card tone, explanation ownership across mission, triage, story, and route lanes | each lane drifts into separate wording or toast-only explanation rules |
| Saved-view and deep-link summaries | the shell's canonical context descriptor built from current URL plus current facts | context-lens summaries, saved-view chip summaries, share-link labels | separate summary builders per storage feature with incompatible wording |

Guardrails:

- toasts, local dismissals, and command-palette hints may echo canonical guidance, but they cannot be the only owner of explanation copy
- bilingual operator guidance must stay paired inside the same repo-owned source for each copy class
- `L24.4` may centralize implementation, but it must not change the ownership boundaries frozen here

## L24 Slice Map

| Slice | Outcome | Why it exists |
| --- | --- | --- |
| `L24.1` | Land this repo-scoped console interaction-clarity blueprint and manual ignition map | Converts the external extraction into repo truth and reopens the console lane after the completed `L23` wave |
| `L24.2` | Freeze the URL-restorable workspace-state, section-summary, and operator-guidance contract | Prevents implementation drift before state, copy ownership, and explanation boundaries are explicit |
| `L24.3` | Add URL-restorable workspace context and section-level success/blocker cards in the current console shell | Lands the highest-value operator clarity improvement without changing lifecycle nouns |
| `L24.4` | Centralize guidance and action-explanation surfaces across mission, triage, story, and route lanes | Makes copy and next-step reasoning consistent instead of leaving it scattered across the shell |
| `L24.5` | Extract console client/state helpers and harden restored-context browser smoke | Improves maintainability and verification after the new context and guidance semantics land |

## Completion Handoff

`L24` is now complete in repo truth through `L24.5`.

What landed in this wave:

- URL-restorable workspace context
- section-level objective, success, and blocker framing
- centralized operator guidance and action-explanation ownership
- helper extraction plus restored-context browser smoke hardening

What this wave does not solve on its own:

- top-level same-rank surface overload
- duplicated onboarding and workflow copy in the intake shell
- early promotion of advanced surfaces such as `Claim Composer`, `Report Studio`, `AI Assistance Surfaces`, and `Distribution Health`
- stage-owned output visibility and no-result or blocked-state ownership across the simplified shell

That follow-on work is now reopened as:

- `docs/governance/datapulse-console-workflow-simplification-blueprint.md`

## Manual Ignition Boundary

The next manual ignition target no longer lives in `L24`.

The next manual ignition target is `L25.2`, which freezes the workflow-first shell contract after the new `L25.1` blueprint promotion.

Normal local ignition entrypoint remains:

```bash
bash scripts/governance/ignite_datapulse_codex_loop.sh
```

Expected next slice after this completed wave: `L25.2`

## Fact Sources

- `/Users/sunyifei/Library/Mobile Documents/iCloud~md~obsidian/Documents/SunYifei/01-项目开发/DataPulse/00_索引与计划/DataPulse_agent-skills-hub前端交互清晰化补强清单_2026-03-31.md`
- `/Users/sunyifei/DataPulse/docs/gui_intelligence_console_plan.md`
- `/Users/sunyifei/DataPulse/docs/governance/datapulse-console-workflow-simplification-blueprint.md`

## Success Condition

DataPulse finished the console-clarity wave without reopening frontend architecture:

- important workspace context is shareable and restorable
- each major lane can show operators what success or blockage currently looks like
- guidance and explanation surfaces are centralized enough to stay consistent
- the browser remains a Reader-backed command chamber rather than drifting into a second product

The next repo-owned question is now narrower:

- how to simplify the shell around workflow order and owned outputs without losing the command chamber identity or Reader-backed lifecycle truth
