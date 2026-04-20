# DataPulse Console Engineering Ignition Readiness Draft

Status: draft readiness read, manual and opt-in

Created: 2026-04-20

## Goal

Provide one repo-local readiness read for the admitted console-engineering follow-up:

- whether the wave is manually ignitable now
- which blocker clears first
- when the A / C / B implementation targets become admissible manual ignition work

## Non-Impact Rules

- This draft does not modify `docs/governance/datapulse-blueprint-plan.json`.
- It does not mark any slice open, landed, or promoted.
- It does not authorize local loop execution by itself.

## Current Verdict

As of `2026-04-20`, the active repo truth now says:

- `recommended_next_slice = L34.1`
- `current next_slice title = Extracted-Console Baseline Absorption`
- `L33` is completed in repo truth through `L33.6`

The admitted follow-up blueprint now exists at:

- `docs/governance/datapulse-console-engineering-governance-blueprint.md`

The current local working-copy baseline also exists:

- `datapulse/static/console/` already exists locally as an extracted console tree
- `datapulse/console_client.py` and `datapulse/console_server.py` already know how to concatenate the sorted fragments into one classic script bundle

But that baseline is still local working-copy truth, not active repo truth.

Therefore the current readiness verdict is:

- baseline absorption is now the live manual ignition target for this admitted wave
- A domain split is not manually ignitable yet
- C pure-function JS tests are not manually ignitable yet
- B htmx triage fragments are not manually ignitable yet

## First Blocking Gate

The first blocker for A / B / C is not technical complexity inside those later targets.

It is the missing repo-truth absorption of the already-working extracted-console baseline.

Until that absorption is landed:

- the active plan remains on `L34.1`
- later engineering-governance slices still depend on working-copy-only facts
- no operator should treat A / B / C as valid manual ignition targets

## Admissible Ignition Order

### Gate 0 - Candidate Wave Admission

This gate is now completed in repo truth.

The repo has admitted the blueprint into structured plan truth and exposed a first real `next_slice`.

This gate still does not mean A / B / C may start ahead of baseline absorption.

### Gate 1 - Extracted-Console Baseline Absorption

This is the first implementation slice for the wave.

Scope:

- land `datapulse/static/console/` as tracked repo content
- land the sorted-fragment loader contract in `datapulse/console_client.py` and `datapulse/console_server.py`
- keep classic script global-scope semantics intact
- prove the absorbed baseline with the current quick gate

Estimated effort:

- `1-2 engineer-days`

Ignition rule:

- if Gate 1 is not landed, A / C / B all stay blocked

### Gate 2 - A Domain-Level Split

This is the first of the three requested implementation targets.

Scope:

- split `99-main.js` into domain fragments
- isolate top-level boot wiring into `90-bootstrap.js`

Estimated effort:

- `2-3 engineer-days`

Ignition rule:

- admissible only after Gate 1 lands

### Gate 3 - C Pure-Function JS Unit Tests

This is the second admissible implementation target.

Scope:

- add `package.json`
- add `vitest.config.js`
- add `tests/js/setup.*`
- add `tests/js/*.test.js`

Estimated effort:

- `1 engineer-day`

Ignition rule:

- admissible after Gate 1 lands
- green closeout is easiest after Gate 2 isolates boot into `90-bootstrap.js`

### Gate 4 - B Htmx Triage Fragment Pilot

This is the last admissible implementation target in the wave.

Scope:

- triage queue list, banner, and card surfaces only
- fragment routes under `/api/fragments/triage/...`
- explicit `jinja2` dependency plus template packaging if Jinja is used
- fragment audit output under `artifacts/runtime/triage_fragments/`

Estimated effort:

- `5-8 engineer-days`

Ignition rule:

- admissible only after Gate 2 and Gate 3 both land

## Relative Earliest Windows

Let `D0` mean:

- the calendar day when the admitted wave entered structured plan truth and Gate 1 was allowed to start

Then the earliest admissible manual ignition windows are:

- Gate 1 baseline absorption: `D0`
- A domain split: `D0 + 1` to `D0 + 2` days, depending on when Gate 1 closes
- C pure-function JS tests: technically after Gate 1; operationally best at `D0 + 2` to `D0 + 4` days so it can reuse `90-bootstrap.js`
- B htmx triage fragments: after A and C, so not before roughly `D0 + 4` days and more realistically after that

## Calendar Example

Because this wave was admitted on `2026-04-20`, the earliest illustrative windows are now:

- Gate 1 could become the live manual ignition target on `2026-04-20`
- A could become manually ignitable around `2026-04-21` to `2026-04-22`
- C could become manually ignitable around `2026-04-22` to `2026-04-24`
- B could become manually ignitable only after both A and C, so not before roughly `2026-04-24`

This remains a sequencing illustration rather than a guarantee of closeout date.

The active repo truth now authorizes Gate 1 as the live manual ignition target, but it still does not authorize A / C / B ahead of baseline absorption landing.

## Operator Answer

For the three requested implementation targets:

1. A cannot enter manual ignition now. It becomes admissible only after baseline absorption lands.
2. C cannot enter manual ignition now. It becomes admissible after baseline absorption, with the cleanest closeout after A.
3. B cannot enter manual ignition now. It becomes admissible only after both A and C land.

The first thing that legitimately became the manual ignition target for this wave is not A / B / C.

It is the baseline-absorption slice that turns the current working-copy console extraction into repo truth.

## Source Alignment

- `docs/governance/datapulse-blueprint-plan.json`
- `docs/governance/datapulse-blueprint-plan.draft.json`
- `docs/governance/datapulse-console-engineering-governance-blueprint.md`
- `docs/gui_intelligence_console_plan.md`
