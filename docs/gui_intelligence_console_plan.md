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
- current endpoints implemented: `GET /api/overview`, `GET /api/watches`, `GET /api/watches/{id}`, `GET /api/watches/{id}/results`, `POST /api/watches`, `PUT /api/watches/{id}/alert-rules`, `POST /api/watches/{id}/run`, `POST /api/watches/{id}/disable`, `POST /api/watches/run-due`, `GET /api/alerts`, `GET /api/alert-routes`, `GET /api/alert-routes/health`, `GET /api/watch-status`, `GET /api/triage`, `GET /api/triage/stats`, `GET /api/triage/{id}/explain`, `POST /api/triage/{id}/state`, `POST /api/triage/{id}/note`, `GET /api/stories`, `GET /api/stories/{id}`, `PUT /api/stories/{id}`, `GET /api/stories/{id}/graph`, `GET /api/stories/{id}/export`
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

## Definition of Done

- console can cover current watch mission lifecycle end-to-end
- API contracts are documented and tested
- visual system is distinct from generic admin boilerplate
- desktop and mobile both load correctly
- GUI remains aligned with Reader/MCP domain contracts
