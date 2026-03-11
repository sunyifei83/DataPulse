# GUI Intelligence Console Plan

## Goal

Add a browser-based intelligence console for DataPulse that turns the current CLI/MCP workflow into a persistent analyst workspace.

This is not a decorative dashboard. The UI should become the operating surface for:

- recurring watch missions
- triage and review queues
- story and evidence workspaces
- alert routing and ops status

## Product Judgment

- A GUI is now justified because DataPulse has crossed the point where command-only workflows create friction for repeat usage.
- The GUI should be a thin operating layer over stable domain models, not a second product with its own state.
- The first release should be local-first and single-user. Multi-user auth is a later concern.
- The UI should not ship as a generic admin template. It needs an intentional "intelligence console" visual language.

## Lifecycle Contract Alignment

This roadmap now projects the repo-level contract in [intelligence_lifecycle_contract.md](/Users/sunyifei/DataPulse/docs/intelligence_lifecycle_contract.md) instead of describing a parallel GUI feature tree.

Canonical lifecycle:

- `WatchMission -> MissionRun -> DataPulseItem review/triage -> Story/evidence package -> AlertEvent / route delivery / story export`

Stage mapping:

- `G0` provides the cross-lifecycle shell and overview, but does not define new lifecycle nouns.
- `G1` is the mission/run operating surface for `WatchMission` and `MissionRun`.
- `G2` is the triage surface for shared `DataPulseItem` review state, notes, and duplicate explanations.
- `G3` is the evidence surface for persisted `Story` objects, timelines, contradictions, graphs, and story export previews.
- `G4` is the delivery/ops surface for `AlertEvent`, named routes, route health, and distribution quality observations.

Roadmap rules:

- the browser must stay a Reader-backed projection of the same lifecycle contract used by CLI and MCP
- later delivery/subscription expansion belongs to the delivery contract follow-up, not to ad hoc GUI-only state

## Recommended Delivery Shape

### Frontend

- `frontend/console`
- `Vite + React + TypeScript`
- `TanStack Router` or `React Router`
- `TanStack Query` for server state
- custom CSS variables for visual system
- `Motion` or CSS animation for controlled transitions
- graph/timeline rendering only where needed

### Backend

- reuse Python runtime
- add a small HTTP API layer on top of `DataPulseReader`
- recommended path: `FastAPI`
- keep API contracts aligned with existing Reader objects

### Why This Stack

- React is justified because the console needs stateful panes, cards, filters, graphs, and cross-panel interactions.
- FastAPI fits the current Python codebase and keeps business logic in one place.
- A browser UI is lower-friction than Electron and more expressive than a TUI for story/timeline/graph work.

## UX Direction

- Avoid CRUD dashboard aesthetics.
- Visual direction: "signal room / command chamber / newsroom ops board", not default SaaS admin.
- Brand baseline: use the command chamber key visual and palette defined in `docs/brand_identity.md`.
- Use a strong typography system, layered backgrounds, signal colors, and a few purposeful transitions.
- Optimize for desktop first, but keep mobile review capability for alerts and status.

## Scope By Stage

### G0: Console Shell

Goal:

- bring current mission entry, alert/status, and cross-lifecycle overview capabilities into one web surface

Scope:

- app shell
- global nav
- home overview
- watch list
- alert list
- daemon status panel
- route audit panel

API surface:

- `GET /api/watches`
- `POST /api/watches`
- `POST /api/watches/{id}/run`
- `POST /api/watches/run-due`
- `GET /api/alerts`
- `GET /api/alert-routes`
- `GET /api/watch-status`

Exit criteria:

- users can complete the current P6 workflow without leaving the browser

Current implementation status:

- `FastAPI` adapter shipped in `datapulse/console_server.py`
- the shell markup bundle is now split into `datapulse/console_markup.py`, keeping `console_server.py` focused on FastAPI routing and Reader-backed API projections
- browser shell shipped as a local-first single-file UI with `/api/overview`
- current endpoints implemented: `GET /api/overview`, `GET /api/watches`, `GET /api/watches/{id}`, `GET /api/watches/{id}/results`, `POST /api/watches`, `PUT /api/watches/{id}/alert-rules`, `POST /api/watches/{id}/run`, `POST /api/watches/{id}/disable`, `POST /api/watches/run-due`, `GET /api/alerts`, `GET /api/alert-routes`, `GET /api/alert-routes/health`, `GET /api/watch-status`, `GET /api/ops`, `GET /api/ops/scorecard`, `GET /api/triage`, `GET /api/triage/stats`, `GET /api/triage/{id}/explain`, `POST /api/triage/{id}/state`, `POST /api/triage/{id}/note`, `GET /api/stories`, `GET /api/stories/{id}`, `PUT /api/stories/{id}`, `GET /api/stories/{id}/graph`, `GET /api/stories/{id}/export`
- launch entry points: `datapulse-console --port 8765`, `python -m datapulse.console_server --port 8765`, `bash scripts/datapulse_console.sh --port 8765`
- console smoke script shipped: `bash scripts/datapulse_console_smoke.sh`
- extended browser smoke now exists as `uv run --with playwright python scripts/datapulse_console_browser_smoke.py`, with `DATAPULSE_CONSOLE_BROWSER_SMOKE=1 bash scripts/datapulse_console_smoke.sh` as the convenience path
- the deploy surface is now a mission deck rather than a plain form: presets, clone-from-mission, route/platform quick picks, local draft persistence, server-derived suggestions, and live mission projection are all available inside the existing shell
- the shell now includes a command palette, recent action log, reversible mission/triage/story mutations, and optimistic board refresh patterns
- a lightweight triage queue panel is now available inside the G0 shell, including duplicate explain cards; full keyboard-first analyst workflow still belongs to G2
- mission detail is now available as a first-cut cockpit slice inside the shell, including next run, recent runs, recent alert outcomes, a persisted result stream, and retry guidance for the latest failed run
- route health is now available as a read-only ops slice for named delivery targets, surfacing healthy/degraded/missing delivery states

### G1: Mission Cockpit

Goal:

- make watch missions feel like live radar boards instead of list items

Scope:

- mission detail page
- result stream
- filter chips
- timeline strip
- mission run history
- alert rule editor

Exit criteria:

- one mission can be reviewed, run, tuned, and audited from a single screen

Current implementation status:

- first-cut mission cockpit shipped inside the existing shell via `GET /api/watches/{id}` and `GET /api/watches/{id}/results`
- current cockpit scope: schedule context, recent run history, recent alert outcomes, persisted result stream, result filter chips, a merged timeline strip, latest-failure retry guidance, and a multi-rule alert editor backed by `PUT /api/watches/{id}/alert-rules`
- current cockpit interaction uplift also includes mission enable/disable/delete controls, reversible mutations through the action log, and server-derived deck recommendations that help operators avoid duplicate mission drift before they create or fork a watch
- current parity outside the browser: `datapulse --watch-show`, `datapulse --watch-results`, `datapulse --watch-alert-set`, `datapulse --watch-alert-clear`, `watch_show(identifier)`, `watch_results(identifier)`, and `watch_set_alert_rules(identifier, alert_rules)`
- current G1 first-cut scope is functionally closed inside the shell; future work is richer mission drill-down rather than missing cockpit basics

### G2: Triage Workspace

Goal:

- carry the future P7 queue model into a keyboard-efficient analyst workflow

Scope:

- queue table + card split view
- state transitions
- reviewer notes
- duplicate explanations
- quick actions and shortcuts

Current implementation status:

- first-cut triage workspace shipped inside the existing shell via `GET /api/triage`, `GET /api/triage/stats`, `GET /api/triage/{id}/explain`, `POST /api/triage/{id}/state`, and `POST /api/triage/{id}/note`
- current browser scope: queue cards, state filter chips, keyboard selection, duplicate explain, state transitions, review-note history, and an inline note composer that writes back without leaving the queue
- queue mutations now also flow through the shared action log, so fast state changes can be reversed without leaving the browser shell
- current parity outside the browser: `datapulse --triage-list`, `datapulse --triage-explain`, `datapulse --triage-update`, `datapulse --triage-note`, `datapulse --triage-stats`, and `triage_list(...)`, `triage_explain(...)`, `triage_update(...)`, `triage_note(...)`, `triage_stats()`
- current keyboard shortcuts: `J/K` move selection, `V/T/E/I` apply state changes, `D` loads duplicate explain, `N` focuses the note composer
- reviewer SLA views and deeper split-pane workflow remain future work

Dependency:

- requires P7 state/action model to stabilize first

### G3: Story Workspace

Goal:

- visualize the future P8 story/evidence model

Scope:

- story board
- timeline view
- evidence stack
- entity graph
- contradiction markers

Dependency:

- requires P8 story model to exist first

Current implementation status:

- `P8` backend has started with `Story / StoryEvidence / StoryTimelineEvent / StoryConflict / StoryStore`
- story clustering and persistence are available through Reader, CLI, and MCP
- browser console now exposes a first-cut story workspace with story cards, evidence stacks, contradiction markers, timeline panels, entity graph, Markdown export preview, and a persisted story editor
- story edits now participate in the reversible action log, which keeps the browser shell aligned with the same persisted story objects while still giving operators a short undo window
- current G3 API surface: `GET /api/stories`, `GET /api/stories/{id}`, `PUT /api/stories/{id}`, `GET /api/stories/{id}/graph`, `GET /api/stories/{id}/export`
- current write scope: update `title / summary / status` for one persisted story via `datapulse --story-update`, `story_update(...)`, or the browser `story editor`
- story merge, evidence reordering, and richer editorial workflow remain future work

### G4: Ops and Distribution Center

Goal:

- give operators one place to inspect health, alerts, routes, and delivery quality

Scope:

- collector health
- watch success/error rates
- recent failures
- alert delivery history
- route health view

Current implementation status:

- the read-only ops board now surfaces collector tier breakdown, aggregate watch success metrics, and a watch health board alongside route delivery health
- the ops board now also includes collector drill-down and route drill-down slices so operators can see remediation hints, mission counts, rule counts, and latest route failure detail without leaving the shell
- the Reader-backed ops surface now also exports an intelligence governance scorecard for coverage, freshness, alert yield, triage throughput, and story conversion through both `GET /api/ops` and `GET /api/ops/scorecard`
- current parity outside the browser: `datapulse --ops-overview` and `ops_overview(...)`
- current ops scope now also includes route delivery timeline, so recent route attempts can be inspected without leaving the shell

Dependency:

- builds on P9 ops/distribution data

## Technical Guardrails

- Do not couple the UI to CLI text output.
- All write actions should go through Reader-backed API contracts.
- Build read-only views first, then add mutations after API schemas settle.
- Prefer server-derived state over duplicating business rules in the frontend.
- Keep the console optional; CLI and MCP remain first-class interfaces.
- Treat repository commit plus GitHub Actions as the admission gate for GUI increments, not local-only validation.

## Risks

- Biggest risk: starting UI work before triage/story schemas are stable.
- Second risk: introducing a Node frontend without a clean Python API boundary.
- Third risk: defaulting to a bland admin template and losing product identity.

## Suggested Sequence

1. Keep `WatchMission` and `MissionRun` contracts stable across Reader, CLI, MCP, and API.
2. Treat `G2` as the shared triage state surface rather than a second queue model.
3. Treat `G3` as the evidence-preserving story surface, not a presentation-only board.
4. Fold delivery observations (`AlertEvent`, routes, story export, ops facts) into one route-backed output model before richer subscriptions.
5. Expand drill-down only after the lifecycle nouns stay stable across all surfaces.

## Follow-up Baseline

The console has now crossed the "missing CRUD" phase.

Current browser baseline:

- mission, triage, story, and route flows all have first-cut create/read/update/delete coverage inside the shell
- triage-to-story promotion, story-to-triage evidence focus, route CRUD, command palette persistence, URL deep links, saved views, pinned views, default landing views, and context-lens sharing are all available
- onboarding and empty states now teach the in-browser lifecycle `Mission Intake -> Mission Board/Cockpit -> Triage -> Story Workspace -> Route Manager / Distribution Health` instead of sending first-time operators back to CLI-first assumptions
- story and route onboarding now point to browser actions such as `Create Story`, `Story Intake`, `Alert Route`, and `Route Manager`, keeping first-pass operation inside the shell
- the remaining problem is no longer "can the browser do the lifecycle work" but "can operators move through it with lower cognitive load, clearer priorities, and stronger product fit"

That changes the follow-up shape.

- the next slices should optimize operating feel, information architecture, and verification safety
- they should not reopen parallel browser-only state models or fork the Reader-backed lifecycle contract

## Repo-Relevant Follow-up Slice Map

This follow-up map is promoted into the repository blueprint as phase `L11` on March 10, 2026.

### L11.1 Visual System Consolidation

Goal:

- turn the current shell from a capable dark dashboard into a more legible operating surface with clearer hierarchy, calmer scan paths, and stronger brand consistency

Repo anchors:

- `datapulse/console_markup.py`
- `docs/brand_identity.md`
- `docs/gui_intelligence_console_plan.md`

Focus:

- unify header, dock, card, toolbar, chip, empty-state, and danger-action styling
- reduce large undifferentiated dark panels and make primary actions visually obvious
- keep the command-chamber visual language without drifting into a generic admin template

Exit condition:

- the shell has one explicit visual system for hierarchy, emphasis, alerts, danger states, and empty states across mission, triage, story, route, and topbar surfaces

Landing note on March 10, 2026:

- landed a sticky topbar with explicit section navigation, context lens controls, and pinned-view dock support
- consolidated mission intake into stepped deck sections, calmer guide cards, and clearer primary-vs-secondary toolbar emphasis
- reused the same card, toolbox, batch-toolbar, empty-state, chip, and danger-action treatment across mission, triage, story, route, and ops surfaces
- added bilingual typography handling so Chinese labels do not inherit the condensed Latin treatment that was tuned for the English shell

### L11.2 Workspace Mode And Information-Architecture Compression

Goal:

- reduce first-load cognitive load by grouping the long single-page console into clearer operating modes instead of asking users to parse every module at once

Repo anchors:

- `datapulse/console_markup.py`
- `docs/gui_intelligence_console_plan.md`

Focus:

- introduce a mode layer such as `Operations / Review / Config`
- make default landing views and top-level section visibility feel intentional rather than exhaustive
- preserve deep-link, saved-view, and context-lens semantics while reducing visible noise

Exit condition:

- a first-time operator can identify the current working mode and relevant modules without scanning the full page length

Landing note on March 10, 2026:

- grouped the browser shell into explicit `Operations`, `Review`, and `Config` workspace modes instead of leaving every major module visible in one long default surface
- moved mission intake, mission board, and cockpit into the operations lane; triage and stories into the review lane; ops, alert stream, route manager, and delivery health into the config lane
- kept section hash, saved-view, pinned-view, and context-lens behavior intact by deriving the active workspace mode from the currently focused section rather than inventing a parallel routing model
- updated focus jumps such as mission draft, story intake, and route deck to switch to the correct workspace mode before scrolling, so hidden-mode modules still open predictably

### L11.3 High-Frequency Action And Convenience Uplift

Goal:

- make the shell feel faster for repeat operators by pushing likely next actions closer to the data instead of relying on memory and scrolling

Repo anchors:

- `datapulse/console_markup.py`
- `datapulse/console_server.py`
- `tests/test_console_server.py`

Focus:

- add stronger card-level quick actions and next-best-action affordances across mission, triage, story, and route flows
- expand keyboard shortcuts and bulk-action safety where they materially reduce handling time
- keep reversible mutations and clear danger semantics as the guardrail for faster interaction

Exit condition:

- the highest-frequency mission-to-triage-to-story-to-route workflows can be driven with fewer context switches, fewer scroll jumps, and less recall burden

### L11.4 Guided Onboarding And Empty-State Productization

Goal:

- lower the barrier for first-time and intermittent users by making the shell teach the lifecycle instead of assuming they already understand it

Repo anchors:

- `datapulse/console_markup.py`
- `docs/datapulse_console_parameter_guide.md`
- `docs/gui_intelligence_console_plan.md`

Focus:

- add guided empty states, first-step prompts, and short lifecycle copy for mission creation, triage review, story promotion, and route setup
- make the shell explain why each area exists and what action is expected next
- keep the UI concise; guidance should reduce confusion, not become a tutorial wall

Exit condition:

- a new operator can understand the lifecycle path `Mission -> Triage -> Story -> Route` from inside the browser without falling back to the CLI docs first

### L11.5 Browser Interaction Verification Hardening

Goal:

- stop the growing stateful UI surface from regressing silently while the productization slices land

Repo anchors:

- `scripts/datapulse_console_browser_smoke.py`
- `scripts/datapulse_console_smoke.sh`
- `tests/test_console_server.py`
- `datapulse/console_markup.py`

Focus:

- add browser-level regression coverage for deep-link restore, saved-view and pinned-dock flows, default landing behavior, triage-to-story promotion, route CRUD, and context reset
- keep the verification surface repo-local and compatible with the existing smoke path
- prefer a small set of high-signal operating-flow checks over brittle snapshot coverage

Exit condition:

- the most stateful browser workflows have repeatable regression coverage strong enough to protect further console productization work

## Manual Ignition Order

Recommended ignition order:

1. `L11.1` because visual hierarchy is now the highest-leverage improvement to perceived quality and scan speed.
2. `L11.2` because layout compression should follow the new hierarchy rather than be designed against the old one.
3. `L11.3` because convenience work is easier to judge after hierarchy and mode boundaries are clearer.
4. `L11.4` because onboarding copy should describe the refined flow rather than the current transitional one.
5. `L11.5` before closing the phase, or earlier if UI churn accelerates and manual verification starts lagging.

## Definition of Done

- console can cover current watch mission lifecycle end-to-end
- API contracts are documented and tested
- visual system is distinct from generic admin boilerplate
- desktop and mobile both load correctly
- GUI remains aligned with Reader/MCP domain contracts

## Follow-up Promotion: L12 Console Operating-Surface Refactor Blueprint

This follow-up map is promoted into the repository blueprint as phase `L12` on March 10, 2026.

The current browser shell is no longer missing core lifecycle capability. The remaining problem is operating-surface convergence:

- there are too many competing navigation and context systems for repeat operators
- cross-stage continuity is weaker than the lifecycle copy implies
- card action density is high enough to flatten priority and increase hesitation
- desktop and mobile behavior exist, but they are not yet governed by one explicit interaction contract

The next phase should therefore treat the console as a workbench-refactor problem rather than as another CRUD-expansion phase.

### North-Star Restatement

The console should become:

- the primary in-browser operating surface for `Mission -> Triage -> Story -> Delivery`
- a thinner, lower-noise projection of the existing Reader-backed lifecycle contract
- a state-driven workbench where the likely next action is obvious without relying on copy walls, memory, or palette recall

The console should not become:

- a second product with GUI-only nouns
- a shell where navigation, context management, and acceleration features compete as equal first-class entry points
- a desktop-only visual showcase that degrades into stacked confusion on mobile

### Information-Architecture Blueprint

The next IA should stabilize around four layers only:

1. Primary lifecycle rail
   - `Intake`
   - `Missions`
   - `Review`
   - `Delivery`
2. Context bar
   - current object
   - active filters or queue mode
   - saved-view or deep-link state
   - compact status facts that explain "where am I and what is scoped right now?"
3. Working surface
   - list
   - detail
   - editor or drill-down pane
4. Accelerators
   - command palette
   - deep links
   - saved views
   - keyboard shortcuts

Concretely:

- `Intake` should center mission drafting, presets, clone, and live mission projection.
- `Missions` should treat mission board plus cockpit as one workspace, with list-selection continuity instead of two mentally separate zones.
- `Review` should treat triage and story as one evidence lane, with explicit triage-to-story and story-to-evidence continuity.
- `Delivery` should group alert stream, route manager, distribution health, and ops facts into one route-backed output plane.

IA rules:

- onboarding copy must be subordinate to the working surface once real data exists
- the current object should remain visible while moving within a workspace
- cross-stage counts should be surfaced where they reduce hopping, for example mission-to-triage and mission-to-story continuity facts

### Navigation Convergence Contract

Only one persistent primary navigation model should remain visible at a time.

Navigation rules:

- merge current workspace-mode and section-nav semantics into one explicit primary rail
- keep the context lens and workspace rail as secondary utilities, not competing top-level nav
- keep the command palette as an accelerator, not as a required discovery path for common work
- preserve deep-link, saved-view, and pinned-view restoration, but do not let them define the primary information hierarchy
- ensure mutations return operators to the same working context unless the mutation explicitly promotes them to the next lifecycle stage

Practical outcome:

- operators should understand where they are from one rail plus one context bar
- they should not need to parse topbar nav, workspace mode, context dock, context lens, and command palette as separate nav systems

### Card Action Priority Contract

Every high-frequency card should expose one state-driven primary CTA.

Global rules:

- one primary action per card
- at most two visible secondary quick actions
- destructive and low-frequency actions move to a danger row or overflow treatment
- bulk action bars appear only when selection is nonzero
- empty states teach the next action, but real cards should not require reading instructional prose before acting

Mission card priority:

- due or never-run mission: primary `Run Mission`
- failed mission: primary `Inspect Failure` or `Retry`
- active mission with output: primary `Open Cockpit`
- disabled mission: primary `Enable`

Triage card priority:

- `new` or `triaged`: primary `Verify`
- high-risk or contradictory evidence: primary `Escalate`
- note capture, duplicate explain, and story promotion remain visible but secondary
- delete stays destructive and tertiary

Story card priority:

- conflicted story: primary `Open Story` with explicit conflict emphasis
- active story: primary `Open Story`
- archive or restore remains secondary
- markdown preview remains tertiary

Route and delivery card priority:

- unhealthy route: primary `Inspect Route`
- unused route: primary `Edit Route` or `Attach To Mission`
- health facts should lead, not configuration chrome

### Desktop Interaction Contract

Desktop rules should optimize for continuous handling and low scroll churn:

- `>= 1280px`: list-detail or list-detail-editor split panes are the default where the workflow is selection-heavy
- `1024px - 1279px`: keep sticky context and batch bars, but collapse nonessential supporting panels before collapsing primary data
- keyboard shortcuts should be available contextually and discoverably, not as permanent visual noise
- list selection should preserve scroll position and detail focus after state mutations where possible
- the hero surface and long guidance blocks should collapse when the operator is already inside a populated workspace

### Mobile Interaction Contract

Mobile rules should prioritize one dominant task at a time:

- use one primary pane at a time rather than stacking full desktop density
- detail views should open as full-screen panels or clear mode switches, not half-visible desktop leftovers
- command palette and context lens should behave as full-screen modal utilities
- only the primary action should remain persistently visible; secondary actions should move into an action sheet or expandable menu
- long chip rows should compress into summaries or horizontal rails rather than wrapping into tall noise walls
- decorative hero treatment should yield to mission, triage, story, and delivery facts on small screens

### Repo-Relevant Follow-up Slice Map

### L12.1 GUI Refactor Blueprint Promotion

Goal:

- convert the current UX judgment into repo-truth documentation plus machine-readable ignition slices

Repo anchors:

- `docs/gui_intelligence_console_plan.md`
- `docs/governance/datapulse-blueprint-plan.draft.json`

Exit condition:

- the repository contains an explicit GUI refactor blueprint and a next-slice map for manual ignition

Landing note on March 10, 2026:

- captured the next-phase IA, navigation, action-priority, and responsive-interaction contract in this document
- split the refactor into repo-relevant follow-up slices instead of leaving it as prose-only design intent
- promoted those slices into the machine-readable blueprint so the next manual ignition target is explicit

### L12.2 Navigation Convergence And Chrome Reduction

Goal:

- collapse overlapping meta-navigation into one primary rail and one secondary context layer

Repo anchors:

- `datapulse/console_markup.py`
- `tests/test_console_server.py`
- `docs/gui_intelligence_console_plan.md`

Focus:

- converge topbar nav, workspace-mode semantics, dock visibility, and context-summary behavior into one hierarchy
- keep saved views, deep links, and palette acceleration intact without treating them as co-primary navigation
- reduce nonessential chrome above populated workspaces

Exit condition:

- operators can reliably move across intake, missions, review, and delivery without learning multiple competing navigation systems

Landing note on March 10, 2026:

- replaced the `Operations / Review / Config` workspace cards as the primary entry system with one lifecycle rail: `Intake / Missions / Review / Delivery`
- moved board-vs-cockpit and triage-vs-story switching into the secondary workspace-context layer so section detail stays close without creating a second top-level nav
- kept command palette, saved views, and deep links intact as accelerators, but no longer treat them as co-primary wayfinding surfaces

### L12.3 Information-Architecture Recomposition And Cross-Stage Continuity

Goal:

- make lifecycle continuity visible in the workspace structure instead of leaving it implicit in copy

Repo anchors:

- `datapulse/console_markup.py`
- `datapulse/console_server.py`
- `tests/test_console_server.py`
- `docs/gui_intelligence_console_plan.md`

Focus:

- recompose mission, review, and delivery workspaces around shared object continuity
- surface cross-stage counters and next-hop facts where they reduce context switching
- tighten list-detail-editor relationships across mission board, cockpit, triage, and story workspaces

Exit condition:

- the browser shell shows how work moves from mission to evidence to story to delivery without relying on explanatory text alone

Landing note on March 10, 2026:

- added mission continuity cards so cockpit detail keeps mission output, review load, and downstream delivery facts visible together
- turned triage into a list-plus-workbench relationship, moving note capture, duplicate explain, and story handoff into one selected-evidence surface instead of repeating full editors inside every card
- added story and delivery readiness cards so evidence, narrative state, alerting missions, and route health stay connected as one lifecycle flow inside the browser shell

### L12.4 State-Driven Card Action Hierarchy

Goal:

- make the likely next action obvious on mission, triage, story, and route cards

Repo anchors:

- `datapulse/console_markup.py`
- `datapulse/console_server.py`
- `tests/test_console_server.py`
- `docs/gui_intelligence_console_plan.md`

Focus:

- implement one-primary-CTA rules across high-frequency cards
- demote destructive or low-frequency actions into clearer secondary treatments
- align batch-tool visibility, quick actions, and danger semantics to the same hierarchy rules

Exit condition:

- action priority is legible enough that operators can act from card state without reading dense button rows

Landing note on March 10, 2026:

- replaced static mission, triage, story, and route button rows with shared CTA hierarchy helpers so each card now exposes one state-driven primary action plus calmer secondary and danger rows
- pushed triage next-hop controls and route health cards onto the same hierarchy, so story handoff and route inspection no longer compete with delete or low-frequency controls at the same visual weight
- reduced idle batch-toolbar noise by showing selection-driven bulk controls only after evidence or story selection is live

### L12.5 Desktop And Mobile Interaction Normalization

Goal:

- codify responsive behavior so the shell stays coherent across desktop and mobile review use

Repo anchors:

- `datapulse/console_markup.py`
- `docs/brand_identity.md`
- `docs/gui_intelligence_console_plan.md`

Focus:

- define pane behavior, density rules, sticky bars, modal behavior, and action-sheet fallbacks by breakpoint
- preserve command-chamber brand language without letting it dominate small-screen utility
- make mobile review safe for alerts, status, and focused triage or story work

Responsive contract:

- `> 1100px`: comfortable density, split-pane work surfaces, side-panel utilities, inline secondary actions
- `761px - 1100px`: compact density, stacked panes, sheet-style utilities, inline secondary actions
- `<= 760px`: touch density, one dominant pane at a time, full-screen context or palette utilities, action-sheet fallback for secondary and danger actions

Exit condition:

- desktop and mobile share one interaction contract instead of a collection of ad hoc breakpoint exceptions

Landing note on March 10, 2026:

- codified one shared responsive contract in the console shell, covering density, pane layout, modal presentation, and secondary-action fallback instead of relying on ad hoc breakpoint tweaks
- aligned context lens and command palette behavior with the same modal contract so desktop uses a side-panel posture while touch viewports promote full-screen utility surfaces
- added action-sheet fallback for secondary and danger controls on touch widths so cards keep one dominant inline action while preserving the existing desktop CTA hierarchy
- updated brand guidance so command-chamber chrome stays recognizable across breakpoints without outranking operational facts on smaller screens

### L12.6 Interaction Verification For Navigation, CTA Priority, And Responsive Behavior

Goal:

- protect the refactor slices from silent regressions while the shell structure changes

Repo anchors:

- `scripts/datapulse_console_smoke.sh`
- `scripts/datapulse_console_browser_smoke.py`
- `tests/test_console_server.py`
- `datapulse/console_markup.py`

Focus:

- extend high-signal browser checks for navigation convergence, context restore, CTA prominence, and responsive behavior
- prefer workflow-level assertions over brittle visual snapshots
- keep the verification path repo-local and compatible with the current manual ignition model

Exit condition:

- the next console refactor wave can ship with regression protection strong enough to support further productization work

## L12 Manual Ignition Order

Recommended ignition order:

1. `L12.2` because navigation convergence removes the highest-cost source of cognitive overhead.
2. `L12.3` because IA recomposition should follow the new navigation hierarchy, not the old shell shape.
3. `L12.4` because card action hierarchy is easier to judge once workspace boundaries are stable.
4. `L12.5` because responsive behavior should be normalized against the converged IA and CTA model.
5. `L12.6` before closing the phase, or earlier if UI churn accelerates and manual verification starts lagging.

## L12 Definition of Done

- one primary navigation model governs the shell
- lifecycle continuity is visible in workspace structure, not only in copy
- high-frequency cards expose state-driven primary actions and calmer secondary action density
- desktop and mobile behavior follow one explicit interaction contract
- verification coverage is strong enough to protect further console refactor work

## Follow-up Promotion: L13 Console Workbench Convergence And Live Desk Refactor

This follow-up map is promoted into the repository blueprint as phase `L13` on March 11, 2026.

`L12` closed the first operating-surface refactor wave, but the browser shell still behaves more like a set of stage-specific pages than one continuous analyst desk:

- populated workspaces still let hero treatment, guidance copy, and supporting chrome outrank current-object facts in key states
- desktop selection-heavy flows still depend on long-page stacking more than stable list-detail-support panes
- the selected mission, evidence item, story, and route are not carried strongly enough across lifecycle jumps
- chips, helper copy, and secondary controls still create more visual competition than repeat operators should need to parse

The next phase should therefore treat the console as an object-first workbench convergence problem:

- the first populated screen should show the current object, the current pressure, and the likely next action
- moving between `Intake`, `Missions`, `Review`, and `Delivery` should preserve one visible handoff chain
- desktop should optimize for stable panes and low scroll churn
- mobile should keep one dominant pane and one dominant action at a time

This phase intentionally does not promote a frontend-stack rewrite slice yet. The repo-relevant next wave remains the Reader-backed browser shell itself, not a parallel React migration track.

### North-Star Restatement

The console should become:

- a live analyst desk where populated states lead with current mission, evidence, story, or route facts instead of decorative onboarding
- a workbench where the active object remains visible while moving across lifecycle stages
- a pane-stable desktop surface that reduces scroll churn in mission, triage, story, and delivery work
- a lower-noise UI where chips mostly summarize state and one dominant action remains obvious

The console should not become:

- a hero-first landing page once the repository already has live missions, triage items, stories, and routes
- a set of disconnected stage pages that force users to rebuild context after every jump
- a control wall where instructional prose, chips, and secondary actions flatten the actual operating priority
- a premature framework-migration project that delays repo-local working-surface convergence

### Repo-Relevant Follow-up Slice Map

### L13.1 Workbench-Convergence Blueprint Promotion

Goal:

- convert the latest GUI/workbench refactor judgment into repo-truth documentation plus machine-readable ignition slices

Repo anchors:

- `docs/gui_intelligence_console_plan.md`
- `docs/governance/datapulse-blueprint-plan.draft.json`
- `docs/governance/datapulse-blueprint-plan.json`

Exit condition:

- the repository contains an explicit `L13` workbench-convergence blueprint and the active blueprint path points operators at the next manual ignition target

Landing note on March 11, 2026:

- translated the latest UI/UXD review into repo-relevant follow-up slices instead of leaving it as prose-only critique
- promoted those slices into the machine-readable blueprint so the next manual ignition target is explicit again
- refreshed the active overlay metadata so the repository-owned blueprint truth now advertises the new workbench-convergence phase

### L13.2 Live Desk And Current-Object-First Intake Refactor

Goal:

- demote hero-first onboarding when real workspace facts exist and replace it with a live-desk posture

Repo anchors:

- `datapulse/console_markup.py`
- `tests/test_console_server.py`
- `docs/gui_intelligence_console_plan.md`

Focus:

- make the first populated intake screen lead with current mission, review pressure, delivery risk, and the likely next action
- keep mission drafting, presets, and clone support accessible without letting them dominate the first live operating view
- collapse long guidance blocks when the shell already has real missions, triage items, stories, or routes

Exit condition:

- a populated browser shell opens on current-object facts and next-step actions before decorative hero treatment or copy-heavy guidance

Landing note on March 11, 2026:

- implemented the live intake desk posture with current-object fact cards, pressure signal chips, and prioritized next actions when workspace data exists
- kept mission drafting and mission/route deep-linking available while reducing hero-first dominance on populated states

### L13.3 Persistent Object Rail And Cross-Stage Handoff Memory

Goal:

- keep the current mission, evidence item, story, and route visible while moving across lifecycle surfaces

Repo anchors:

- `datapulse/console_markup.py`
- `datapulse/console_server.py`
- `tests/test_console_server.py`
- `docs/gui_intelligence_console_plan.md`

Focus:

- promote the current context bar into a persistent object rail rather than treating it only as a saved-view utility
- preserve selected-object continuity across `Missions`, `Review`, `Story`, and `Delivery` jumps
- ensure reversible mutations return operators to the same object context unless the mutation explicitly promotes the work to a new stage

Exit condition:

- moving from mission to evidence to story to route no longer feels like opening disconnected desks; one visible handoff chain remains in view

### L13.4 Desktop Workbench Pane Normalization

Goal:

- replace long-page stacking in selection-heavy flows with stable desktop workbench panes

Repo anchors:

- `datapulse/console_markup.py`
- `tests/test_console_server.py`
- `docs/gui_intelligence_console_plan.md`

Focus:

- normalize mission handling into list-detail-support pane relationships
- normalize review handling into queue-workbench-support pane relationships
- normalize delivery handling into alert-route-health pane relationships
- preserve list scroll position and detail focus after state mutations where possible

Exit condition:

- desktop work no longer depends on repeated full-page scroll traversal for mission, triage, story, and delivery handling

### L13.5 Review-Story Evidence Lane And Story Editor Mode

Goal:

- tighten triage-to-story continuity into one evidence lane with clearer board-versus-editor boundaries

Repo anchors:

- `datapulse/console_markup.py`
- `datapulse/console_server.py`
- `tests/test_console_server.py`
- `docs/gui_intelligence_console_plan.md`

Focus:

- keep selected evidence and linked story context synchronized instead of treating triage and story as loosely adjacent pages
- split story workspace into a board mode and an editor mode with clearer transitions
- reduce story-detail report sprawl by making editorial and analytical surfaces explicitly mode-driven

Exit condition:

- operators can promote evidence into narrative work without reselecting context or parsing one long story report surface

### L13.6 Populated-Workspace Control Compression

Goal:

- reduce cognitive noise in populated workspaces by compressing chips, helper copy, and secondary controls

Repo anchors:

- `datapulse/console_markup.py`
- `docs/brand_identity.md`
- `docs/gui_intelligence_console_plan.md`

Focus:

- make chips summarize state more often than they expose peer-level button walls
- keep one dominant action obvious while demoting secondary and danger actions into calmer treatments
- collapse instructional prose once the relevant workspace already contains real operational data

Exit condition:

- populated cards and workspaces scan faster, with less instructional reading and less control-priority flattening

### L13.7 Interaction Verification For Live Desk, Object Rail, And Pane Stability

Goal:

- protect the next workbench-convergence wave from silent regressions

Repo anchors:

- `scripts/datapulse_console_smoke.sh`
- `scripts/datapulse_console_browser_smoke.py`
- `tests/test_console_server.py`
- `datapulse/console_markup.py`

Focus:

- extend browser checks for populated-intake behavior, current-object rail persistence, pane-mode stability, and story editor transitions
- add assertions for mobile one-dominant-pane behavior and reduced chrome noise in populated states
- keep verification repo-local and compatible with the current manual ignition model

Exit condition:

- the next workbench refactor wave has regression coverage for the new object-first operating model before another round of shell expansion lands

## L13 Manual Ignition Order

Recommended ignition order:

1. `L13.2` because intake posture sets the first object-first mental model and removes the highest-leverage source of hero-first noise.
2. `L13.3` because the current-object rail should be established before deeper pane and editor refactors depend on it.
3. `L13.4` because pane normalization should follow the new current-object model rather than the old long-page shell.
4. `L13.5` because evidence-lane and story-editor convergence is easier to judge once the pane model is stable.
5. `L13.6` because control compression should be tuned against the converged workbench rather than the current transitional chrome.
6. `L13.7` before closing the phase, or earlier if workbench churn accelerates and manual verification starts lagging.

## L13 Definition of Done

- populated intake behaves like a live desk instead of a hero-first landing page
- one persistent object rail keeps mission, evidence, story, and route handoff visible across lifecycle movement
- desktop selection-heavy flows use stable pane relationships instead of long-page stacking
- story work separates board and editor intent clearly enough to reduce report-style sprawl
- populated workspaces compress control and copy noise without hiding the dominant action
- verification coverage is strong enough to protect the new object-first operating model
