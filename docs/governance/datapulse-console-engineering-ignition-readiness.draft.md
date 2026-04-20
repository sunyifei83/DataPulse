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

- `recommended_next_slice = L34.2`
- `current next_slice title = Domain-level split of the main bundle`
- `L33` is completed in repo truth through `L33.6`
- `L34.1` is completed in repo truth through extracted-console baseline absorption

The admitted follow-up blueprint now exists at:

- `docs/governance/datapulse-console-engineering-governance-blueprint.md`

The landed baseline now means:

- `datapulse/static/console/` is tracked repo content as an extracted console tree
- `datapulse/console_client.py` and `datapulse/console_server.py` concatenate the sorted fragments into one classic script bundle
- `uv run python scripts/governance/run_datapulse_quick_test_gate.py` passes against that landed baseline

Therefore the current readiness verdict is:

- A domain split is now the live manual ignition target for this admitted wave
- C pure-function JS tests are now manually ignitable, though the cleanest closeout remains after A isolates boot wiring
- B htmx triage fragments are not manually ignitable yet

## First Blocking Gate

The first blocker for later console-engineering work is no longer baseline absorption.

`L34.1` is landed, so the remaining gating truth is sequencing:

- the active plan now moves to `L34.2`
- `L34.3` is admissible after the landed baseline, but its cleanest closeout still follows `L34.2`
- `L34.4` remains blocked until both `L34.2` and `L34.3` land

## Admissible Ignition Order

### Gate 0 - Candidate Wave Admission

This gate is now completed in repo truth.

The repo has admitted the blueprint into structured plan truth and exposed a first real `next_slice`.

This gate no longer limits the current target set, because baseline absorption is already landed.

### Gate 1 - Extracted-Console Baseline Absorption

This gate is now completed in repo truth.

Scope:

- landed `datapulse/static/console/` as tracked repo content
- landed the sorted-fragment loader contract in `datapulse/console_client.py` and `datapulse/console_server.py`
- kept classic script global-scope semantics intact
- proved the absorbed baseline with the current quick gate

Estimated effort:

- `1-2 engineer-days`

Ignition rule:

- cleared; A is now live, C is admissible, and B still waits on later gates

### Gate 2 - A Domain-Level Split

This is now the live implementation target for the wave.

Scope:

- split `99-main.js` into domain fragments
- isolate top-level boot wiring into `90-bootstrap.js`

Estimated effort:

- `2-3 engineer-days`

Ignition rule:

- admissible now

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

- admissible now
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

- Gate 1 baseline absorption: `D0`; now landed
- A domain split: immediately after Gate 1 closes; now the live target
- C pure-function JS tests: technically after Gate 1; operationally still best after A so it can reuse `90-bootstrap.js`
- B htmx triage fragments: after A and C, so not before both later gates close

## Calendar Example

Because this wave was admitted and `L34.1` landed on `2026-04-20`, the earliest illustrative windows are now:

- Gate 1 landed on `2026-04-20`
- A is manually ignitable now on `2026-04-20`
- C is technically manually ignitable now, with the cleanest closeout after A
- B becomes manually ignitable only after both A and C land

This remains a sequencing illustration rather than a guarantee of closeout date.

The active repo truth now authorizes A as the live manual ignition target, keeps C admissible after the landed baseline, and still does not authorize B ahead of both later gates landing.

## Operator Answer

For the three requested implementation targets:

1. A can enter manual ignition now. It is the current `next_slice`.
2. C can enter manual ignition now. Its cleanest closeout still follows A.
3. B cannot enter manual ignition now. It becomes admissible only after both A and C land.

The first thing that legitimately became the manual ignition target for this wave was the baseline-absorption slice that turned the extracted console baseline into repo truth.

With that slice landed, the live target is now A.

## Source Alignment

- `docs/governance/datapulse-blueprint-plan.json`
- `docs/governance/datapulse-blueprint-plan.draft.json`
- `docs/governance/datapulse-console-engineering-governance-blueprint.md`
- `docs/gui_intelligence_console_plan.md`
