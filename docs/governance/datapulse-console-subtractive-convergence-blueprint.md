# DataPulse Console Subtractive Convergence Blueprint

Status: repo-scoped follow-up blueprint, `L33.1` and `L33.2` landed; `L33.3` is the next manual ignition target

Created: 2026-04-16

Updated: 2026-04-16

## Goal

Promote the next console product-fit judgment into repo truth as a narrow follow-up wave after the completed `L26` modularity-and-traceability work.

The target is not to reopen shell-order simplification, restart a frontend-stack debate, or invent browser-only lifecycle state.

The target is to:

- remove first-load scope that no longer belongs in the default operator lane
- demote accelerators back into accelerators instead of letting them compete with the primary rail
- compact populated-workspace chrome so real objects outrank onboarding copy
- treat saved-view and context restore stability as a product-fit contract rather than as incidental browser-smoke detail

## Repo Read Correction

Current DataPulse already has the important console baseline:

- `L25` landed the workflow-first shell order, first-rank versus demoted surface rules, stage-owned outputs, and stage-owned feedback
- `L26` landed the shared console API client boundary, stage-linked traceability, shared signal taxonomy, and bounded frontend-escalation rules
- browser acceptance can already follow `Start -> Monitor -> Review -> Deliver`, inspect owned outputs, and route signal explanations back to the expected stage-owned surface

The remaining gap is no longer "can the console explain the workflow?"

The remaining gap is the second-round subtraction problem:

- the default shell still preloads too many advanced or hidden surfaces before the active stage actually needs them
- accelerators such as saved views, context dock, context lens, deep links, and palette semantics still consume too much top-level visual rank
- populated workspaces still carry too much onboarding chrome relative to the live work object
- restore-path instability has now shown up in browser smoke, which means the cost of complexity is no longer abstract

## Remaining Follow-Up Targets

### Stage-Aware Hydration Boundary

This wave should define which facts belong in the default first load and which facts must wait until the active stage or selected object actually requires them.

Repo implication:

- do not keep preloading report, delivery, digest, and AI surfaces simply because they exist
- treat first-load scope as an operator-lane contract rather than as a convenience cache
- keep Reader-backed truth canonical; only the browser fetch timing should change

### Accelerator Demotion Boundary

This wave should reassert that accelerators are optional speed paths, not co-primary navigation.

Repo implication:

- lifecycle rail remains the primary navigation model
- one context bar may remain visible for current object and scope facts
- context dock, saved views, deep links, and palette affordances should appear only when they materially help the current lane

### Populated-Workspace Chrome Compaction

This wave should define when onboarding and guide surfaces must yield to live work objects.

Repo implication:

- first-run, empty, and blocked states may still present guidance prominently
- once live missions, triage items, stories, alerts, or routes exist, the current object must outrank explanatory chrome
- the command-chamber identity should survive compaction instead of collapsing into flat admin minimalism

### Restore-Path Stability Boundary

This wave should treat restored-context behavior as a repo-owned acceptance contract.

Minimum continuity path:

1. save a view
2. pin or default it
3. restore on boot or from dock
4. reopen workspace context
5. continue moving through the expected stage without state drift

Repo implication:

- the browser shell must not leave restored context in a half-open or visually stale state after rerender
- acceptance should verify state alignment across `body dataset`, `aria-expanded`, dock visibility, and the active section

## What This Wave Must Preserve

Invariants:

1. `WatchMission`, `DataPulseItem`, `Story`, `Report`, and named routes remain canonical lifecycle nouns
2. the browser remains a projection over Reader, CLI, MCP, and HTTP truth
3. the workflow-first shell order from `L25` remains intact unless a later contract explicitly reopens it
4. the client boundary, stage-linked trace surface, and shared signal taxonomy from `L26` remain canonical
5. the command-chamber identity remains intentional and repo-specific even when top-level chrome is reduced

## What This Wave Must Not Do

This wave must not:

- reopen the shell-order simplification question solved in `L25`
- reopen standalone frontend engineering on preference, polish, or generic maintainability claims
- turn first-load reduction into browser-only lifecycle truth
- keep accelerators visible simply because they were previously shipped
- hide blocked or empty states so aggressively that operators lose next-step clarity

## L33 Contract Targets

`L33.2` freezes five things before implementation begins:

1. the default first-load hydration boundary by stage and selected object
2. the visible navigation hierarchy and accelerator demotion rules
3. the populated-workspace compaction rules for hero, guidance, and auxiliary chrome
4. the restore-path stability contract for saved views, dock visibility, and workspace context reopening
5. the acceptance checks for request scope, visible chrome, and restored-context stability

## L33.2 Frozen Subtractive-Convergence Contract

### Default First-Load Hydration Boundary

- first load should fetch only the active stage list, the active object detail when one is selected, and the minimum cross-stage continuity counts needed to answer "what do I do next?"
- the browser must not preload report-family, delivery-audit, digest, or AI projection payloads when the active stage does not need them
- these surfaces are deferred by default until the stage or selected object explicitly requires them:
  - `report briefs`
  - `claim cards`
  - `citation bundles`
  - `report sections`
  - `reports`
  - `export profiles`
  - `delivery package audit`
  - `report markdown preview`
  - AI assist projections that are not active-stage or selected-object critical
- Reader, API, and persisted lifecycle truth stay unchanged; only browser fetch scope and timing may change

### Visible Navigation Hierarchy And Accelerator Demotion

- one primary lifecycle rail remains visible at first rank: `Start -> Monitor -> Review -> Deliver`
- one context bar may remain visible for current object, current filter scope, and current stage facts
- accelerators must not remain continuously visible unless they are actively usable in the current state:
  - `context dock`
  - `saved views`
  - `default landing view`
  - `deep links`
  - `command palette`
  - `context lens`
- the dock must stay hidden when there is no pinned saved view to expose
- accelerators may still exist and remain shareable or restorable, but they must not read as a second navigation system

### Populated-Workspace Chrome Compaction

- onboarding and guide surfaces may stay prominent only when the active workspace is first-run, empty, or explicitly blocked
- once live work objects exist, the default view must compact hero and guide chrome so the current object becomes the first visual anchor
- compacted populated state should still preserve:
  - one sentence of current-stage framing
  - one primary CTA
  - the current object and continuity facts
- explanatory copy, jump strips, and auxiliary hints should yield before object cards, selected detail panes, or stage-owned summaries yield

### Restore-Path Stability Contract

- saved-view restoration must keep section, filter, and selected-object continuity aligned after rerender
- after default or dock-driven restore, reopening workspace context must still move all visible state into the open position together:
  - `document.body.dataset.contextLensOpen`
  - `#context-summary[aria-expanded]`
  - backdrop open class
  - lens hidden/open state
- focus recovery may not silently cancel the intended open state
- acceptance should treat this as a product-fit regression if it breaks, not as a minor browser-only convenience miss

### Acceptance And Request-Scope Checks

- later implementation slices must preserve `L25` shell order and `L26` trace or signal ownership
- browser acceptance must verify not only route reachability, but also:
  - hidden dock behavior when no pinned saved views exist
  - compact populated-workspace chrome after live objects load
  - restored-context stability through saved-view and dock flows
  - first-load request scope staying inside the active stage boundary
- request-scope checks may use browser-side fetch observation, but they must not invent browser-only lifecycle semantics

## L33 Slice Map

| Slice | Outcome | Why it exists |
| --- | --- | --- |
| `L33.1` | Land this repo-scoped subtractive-convergence blueprint and fact promotion | Reopens the console lane with the right problem after the completed `L26` wave |
| `L33.2` | Freeze the first-load, accelerator, compaction, and restore-stability contract | Prevents implementation drift before subtraction work begins |
| `L33.3` | Harden saved-view, dock, and workspace-context restore stability while demoting dock visibility to pinned-only contexts | Fixes the first concrete instability and removes always-on accelerator chrome |
| `L33.4` | Introduce stage-aware hydration and defer advanced preloads until the active stage or selected object needs them | Reduces first-load scope without changing lifecycle truth |
| `L33.5` | Compact populated-workspace chrome and demote onboarding or accelerator copy behind live objects | Makes current work objects outrank guide chrome once the shell is in use |
| `L33.6` | Harden browser smoke and acceptance around request scope, hidden dock rules, populated chrome, and restore stability | Turns subtractive-convergence regressions into machine-detectable failures |

## Recommended Ignition Order

Recommended order:

1. `L33.2`; landed
2. `L33.3`
3. `L33.4`
4. `L33.5`
5. `L33.6`

## Manual Ignition Boundary

`L33.1` and `L33.2` are now landed, so the next manual ignition target is `L33.3`.

Reason:

- `L25` already solved shell order and first-rank stage ownership
- `L26` already solved client boundary, stage-linked traceability, signal ownership, and bounded frontend escalation
- `L33.2` now freezes the subtractive-convergence contract, so the next repo-owned gap is the first concrete implementation boundary: restore stability plus pinned-only dock visibility

After the blueprint landing is committed and the repo returns to a clean baseline, the normal local ignition entrypoint remains:

```bash
bash scripts/governance/ignite_datapulse_codex_loop.sh
```

Expected next slice after this contract freeze landing: `L33.3`

## Fact Sources

- `/Users/sunyifei/Library/Mobile Documents/iCloud~md~obsidian/Documents/SunYifei/01-项目开发/DataPulse/00_索引与计划/DataPulse_console_UIUX减法收敛与最优解路线图_2026-04-16.md`
- `/Users/sunyifei/Library/Mobile Documents/iCloud~md~obsidian/Documents/SunYifei/01-项目开发/DataPulse/00_索引与计划/DataPulse_console_P0减法收敛实施清单_2026-04-16.md`
- `/Users/sunyifei/DataPulse/docs/gui_intelligence_console_plan.md`
- `/Users/sunyifei/DataPulse/datapulse/console_client.py`
- `/Users/sunyifei/DataPulse/scripts/datapulse_console_browser_smoke.py`

## Success Condition

DataPulse reopens console follow-up work without reopening the wrong questions:

- the contract-freeze slice for subtraction is now landed, and the next ignition target is the restore-stability plus pinned-dock implementation boundary
- first-load scope, accelerator rank, and populated-workspace chrome all become explicit repo truth before implementation starts
- restore-path stability is promoted into a first-class acceptance boundary
- the current shell remains the implementation surface, while lifecycle truth, shell order, and frontend-escalation boundaries stay intact
