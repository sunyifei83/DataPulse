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
- Visual direction: "signal room / newsroom ops board", not default SaaS admin.
- Use a strong typography system, layered backgrounds, signal colors, and a few purposeful transitions.
- Optimize for desktop first, but keep mobile review capability for alerts and status.

## Scope By Stage

### G0: Console Shell

Goal:

- bring current P6 watch/alert/status capabilities into one web surface

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
- browser shell shipped as a local-first single-file UI with `/api/overview`
- current endpoints implemented: `GET /api/overview`, `GET /api/watches`, `POST /api/watches`, `POST /api/watches/{id}/run`, `POST /api/watches/{id}/disable`, `POST /api/watches/run-due`, `GET /api/alerts`, `GET /api/alert-routes`, `GET /api/watch-status`, `GET /api/triage`, `GET /api/triage/{id}/explain`, `POST /api/triage/{id}/state`, `GET /api/triage/stats`
- launch entry point: `datapulse-console --port 8765`
- a lightweight triage queue panel is now available inside the G0 shell, including duplicate explain cards; full keyboard-first analyst workflow still belongs to G2

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

### G2: Triage Workspace

Goal:

- carry the future P7 queue model into a keyboard-efficient analyst workflow

Scope:

- queue table + card split view
- state transitions
- reviewer notes
- duplicate explanations
- quick actions and shortcuts

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

Current backend status:

- `P8` backend has started with `Story / StoryEvidence / StoryTimelineEvent / StoryConflict / StoryStore`
- story clustering and persistence are available through Reader, CLI, and MCP
- browser console now exposes a first-cut read-only story board with story cards, evidence stacks, contradiction markers, timeline panels, entity graph, and Markdown export preview
- current G3 API surface: `GET /api/stories`, `GET /api/stories/{id}`, `GET /api/stories/{id}/graph`, `GET /api/stories/{id}/export`
- story editing remains future work

### G4: Ops and Distribution Center

Goal:

- give operators one place to inspect health, alerts, routes, and delivery quality

Scope:

- collector health
- watch success/error rates
- recent failures
- alert delivery history
- route health view

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

1. Add `FastAPI` adapter for current P6 objects.
2. Deliver G0 shell with watch, alerts, routes, and status.
3. Stabilize P7/P8 domain models.
4. Expand into G2/G3 workspaces.
5. Fold P9 ops into the same console.

## Definition of Done

- console can cover current watch mission lifecycle end-to-end
- API contracts are documented and tested
- visual system is distinct from generic admin boilerplate
- desktop and mobile both load correctly
- GUI remains aligned with Reader/MCP domain contracts
