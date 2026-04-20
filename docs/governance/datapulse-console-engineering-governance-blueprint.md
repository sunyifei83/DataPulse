# DataPulse Console Engineering Governance Blueprint

Status: repo-scoped admitted follow-up blueprint; current reopening target is `L34.3` (`Pure-function JS unit coverage`)

Created: 2026-04-20

Updated: 2026-04-20

## Goal

Promote the console JS code-engineering governance into repo truth as a narrow follow-up wave that bounds how the browser-side codebase evolves, without reopening the completed shell-shape and subtractive-convergence tracks.

The target is not to migrate to React, Vue, Preact, or any bundler, not to adopt a TypeScript runtime, and not to restart the generic "rewrite the UI" debate.

The target is to:

- absorb the already-proven local extracted-console baseline into repo truth before further frontend-governance claims are promoted
- bound the console JS codebase so future change cost scales sub-linearly with file size
- make the triage list surface server-auditable without moving the console to a framework
- make browser-side pure functions testable without adopting a bundler
- keep the console as a deployable `git pull && restart` operational tool, with zero new build-step dependencies on the critical runtime path

## Repo Read Correction

The pre-`L34.1` repo read and the current repo truth are no longer the same thing.

Current repo truth:

- `docs/governance/datapulse-blueprint-plan.json` closes `L33` in repo truth through `L33.6`, closes `L34.1` through extracted-console baseline absorption, and leaves `L34` open on later engineering-governance work
- operators should currently treat `L34.3` (`Pure-function JS unit coverage`) as the live manual ignition target for this wave
- `datapulse/static/console/` is tracked repo content, `datapulse/console_client.py` and `datapulse/console_server.py` concatenate sorted console fragments into one classic `<script>` bundle, and `uv run python scripts/governance/run_datapulse_quick_test_gate.py` passes against that landed baseline

Historical pre-landing local working-copy truth:

- before `L34.1`, the working tree already contained an extracted console JS tree under `datapulse/static/console/`
- before `L34.1`, `datapulse/console_client.py` and `datapulse/console_server.py` already knew how to concatenate sorted console fragments into one classic `<script>` bundle
- before `L34.1`, `uv run python scripts/governance/run_datapulse_quick_test_gate.py` already passed against that local working-copy baseline

What is not yet true:

- list-rendering surfaces still rely on client-side `innerHTML =` rebuilds, so exact operator-visible replay is not yet a server-owned fact
- pure JS helpers such as list parsing, filter normalization, and preview readiness still have no JS-side unit coverage in CI

Therefore:

- Step 1 and Step 2 are now landed repo-truth facts rather than working-copy-only baseline claims
- later engineering-governance slices may now build on that admitted baseline, with `L34.3` as the current live follow-up target

## Remaining Follow-Up Targets

### Extracted-Console Baseline Absorption

This wave first absorbed the already-working local console extraction baseline into repo truth through `L34.1`.

Repo implication:

- landed `datapulse/static/console/` as tracked repo content
- landed the sorted-fragment loader contract in `datapulse/console_client.py` and `datapulse/console_server.py`
- kept classic `<script>` global-scope semantics intact
- proved the absorbed baseline with the existing quick gate before later slices advanced

### Domain-Level Split Of The Main Bundle

After baseline absorption, this wave should split `datapulse/static/console/99-main.js` into domain-owned fragments under the same directory.

Repo implication:

- prefer one domain per fragment file: watch, triage, story, route, delivery, report+claim, context+shell
- isolate the current top-level boot and document-level listener wiring into one `90-bootstrap.js` style file
- preserve semantic execution order and hoist-sensitive behavior in the concatenated bundle
- do not claim byte-for-byte equality once domain regrouping begins; the invariant is runtime equivalence, not textual zero diff

### Pure-Function JS Unit Coverage

This wave should add a minimal Node-side test runner for the pure JS helpers that currently drift silently.

Repo implication:

- add a top-level `package.json` and `vitest.config.js`
- the test harness must use an isolated VM or explicit named-return wrapper; simply evaluating the bundle with `new Function(...); fn(globalThis)` is not sufficient to expose top-level helpers as globals
- the harness must exclude or neutralize top-level boot side effects; a bundle that immediately hydrates the page cannot be executed unchanged inside the test runtime
- do not introduce a bundler, a TypeScript runtime, or browser E2E as part of this slice

### Server-Rendered Triage Fragments

This wave should migrate the triage queue rendering path from client-side `innerHTML =` list rebuilds to htmx-driven server-rendered HTML fragments.

Repo implication:

- fragment routes must live under `/api/fragments/triage/...`
- existing JSON routes under `/api/triage/...` remain unchanged for CLI, MCP, and existing tests
- if the repo chooses Jinja templates, `jinja2` must be declared explicitly and template files must be included in wheel packaging; this cannot be assumed implicit
- fragment audit output must go to an ignored runtime path such as `artifacts/runtime/triage_fragments/`, not a tracked `logs/` tree
- an exact DOM replay claim is valid only if the fragment request and fragment log carry the operator-visible state that affects rendering

## Replay Boundary For The Triage Pilot

This wave freezes one narrow replayability rule for the htmx pilot:

- exact replay applies to the fragment-managed triage list, banner, and card surfaces
- exact replay does not include ephemeral textarea cursor position, IME composition state, or unsent draft note contents

To claim exact replay of the fragment-managed surfaces, the fragment request and the fragment log must carry at minimum:

- active triage filter
- search text
- selected item id
- selected item ids
- pinned evidence ids
- story-focus id or equivalent evidence-focus context

If a browser-owned state affects rendered HTML but is not serialized into the fragment request and log, the implementation must downgrade its claim from "exact replay" to "structural replay only".

## What This Wave Must Preserve

Invariants:

1. `WatchMission`, `DataPulseItem`, `Story`, `Report`, and named routes remain canonical lifecycle nouns
2. the browser remains a projection over Reader, CLI, MCP, and HTTP truth
3. the workflow-first shell order from `L25`, the trace and signal ownership from `L26`, and the subtractive-convergence baseline from `L33` remain canonical
4. the command-chamber identity remains repo-specific rather than collapsing into a generic admin shell
5. the current quick gate remains the minimal local baseline proof for repo-landed console work

## What This Wave Must Not Do

This wave must not:

- pretend the current local extracted-console baseline is already landed repo truth when it is not
- reopen standalone frontend engineering on preference, polish, or abstract maintainability claims
- introduce ES modules, a bundler, or a TypeScript runtime
- claim exact DOM replay while leaving rendering-critical state browser-local and unlogged
- add a JS test harness that depends on accidental `globalThis` leakage from top-level function declarations

## Slice Map

### Slice 1 - Extracted-Console Baseline Absorption

Scope:

- land the Step 1 and Step 2 working-copy console extraction as clean repo truth

Acceptance:

- `datapulse/static/console/` is tracked
- `datapulse/console_client.py` and `datapulse/console_server.py` both load the sorted fragment bundle
- `uv run python scripts/governance/run_datapulse_quick_test_gate.py` passes
- the repo returns to a clean baseline after the slice lands

Risk: low. This slice promotes an already-proven local baseline instead of inventing a new architecture.

Effort: 1-2 engineer-days.

### Slice 2 - Domain-Level Split

Scope:

- split `99-main.js` into domain fragments and isolate current top-level boot wiring into `90-bootstrap.js`

Acceptance:

- concatenated bundle remains semantically equivalent
- node parses the concatenated bundle
- `uv run python scripts/governance/run_datapulse_quick_test_gate.py` passes
- manual browser smoke through the main operator path shows no console error

Risk: low.

Effort: 2-3 engineer-days.

### Slice 3 - Pure-Function JS Unit Tests

Scope:

- `package.json`
- `vitest.config.js`
- `tests/js/setup.*`
- `tests/js/*.test.js`

Acceptance:

- `npm run test:js` or equivalent passes locally and in CI
- CI gains an independent `frontend-test` job
- the harness uses a VM or named-return wrapper instead of `fn(globalThis)`
- the harness excludes or neutralizes boot side effects before evaluating pure helpers
- the minimum helper set is covered: `parseListField`, `formatListField`, `toggleListValue`, `normalizeTriageFilter`, `normalizeStorySort`, `normalizeStoryFilter`, `normalizeStoryWorkspaceMode`, `normalizeStoryDetailView`, `draftHasAdvancedSignal`, `buildCreateWatchPreview`, `summarizeCreateWatchAdvanced`

Risk: low.

Effort: 1 engineer-day.

### Slice 4 - Htmx Triage Fragment Pilot

Scope:

- triage queue list, banner, and card-level fragment rendering under `/api/fragments/triage/...`

Acceptance:

- explicit `jinja2` dependency and template packaging are landed if Jinja is used
- fragment audit output lands under an ignored runtime root
- fragment request plus fragment log carry the rendering-critical view state frozen above
- operator walk-through of open, filter, select, verify, escalate, clear remains functionally equivalent
- keyboard shortcuts `J`, `K`, `V`, `T`, `E`, `I`, `N`, `S`, `D` still fire
- exact replay claims are limited to surfaces whose rendering-critical state is logged

Risk: medium.

Effort: 5-8 engineer-days.

## Slice Sequencing

- Slice 1 is now landed, so later slices no longer depend on working-copy-only extraction facts
- Slice 2 follows Slice 1
- Slice 3 may start after Slice 1, but its green closeout is easiest after Slice 2 isolates boot into a dedicated fragment
- Slice 4 depends on Slice 2 and Slice 3; the triage pilot should not be the first place where boot isolation or helper-testability gets discovered

## Non-Goals

- introducing any JS framework (React, Vue, Preact, Alpine, Svelte, Solid)
- introducing any bundler (esbuild, vite, rollup, webpack, parcel)
- introducing TypeScript runtime or `.ts` source files
- extending htmx fragment rendering beyond the triage pilot within this wave
- changing canonical JSON API semantics under `/api/...`
- reopening the completed shell-order or subtractive-convergence waves

## Activation Boundary

Landing this blueprint file by itself does not claim that the active blueprint already reopened.

Repo truth now treats this document as an admitted reopen path because:

- the governance loop has accepted this blueprint into the structured plan
- the admitted wave now has `L34.1` landed as its baseline-absorption closeout
- the current operator-facing ignition target is `L34.3` (`Pure-function JS unit coverage`)

Operator-facing ignition timing and gate order are summarized in:

- `docs/governance/datapulse-console-engineering-ignition-readiness.draft.md`

With `L34.2` landed, the current operator-facing reopening target is `L34.3`; `L34.4` still waits on the JS test harness slice before the htmx pilot can claim its replay boundary.
