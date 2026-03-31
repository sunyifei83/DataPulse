# DataPulse Console Workflow-First Simplification Blueprint

Status: repo-scoped follow-up blueprint, `L25` repo truth completed through `L25.5`; no open slice

Created: 2026-03-31

Updated: 2026-03-31

## Goal

Promote the current GUI simplification judgment into repo truth as a narrow follow-up wave after the completed `L24` console interaction-clarity work.

The target is not to rebuild the frontend stack, discard the command chamber identity, or invent a second browser-only lifecycle model.

The target is to:

- reduce top-level cognitive load in the current Reader-backed console
- reorganize the shell around workflow order instead of capability pile-up
- make steps, outputs, and next actions obvious at a glance
- demote internal or advanced surfaces that should not compete for top-level attention
- move important run, no-result, warning, and completion feedback onto the surface that owns the work instead of relying only on transient toasts

## Repo Read Correction

Current DataPulse already has the important clarity infrastructure:

- the browser shell is Reader-backed and local-first
- `L24.2` through `L24.5` already landed URL-restorable context, section-level summary framing, centralized operator guidance, and client or state helper extraction
- mission run feedback is no longer invisible-only runtime churn; the shell now exposes started, pending, completed, no-result, and failed states through action-log updates and explicit toasts

The remaining gap is no longer "the console needs more explanation."

The remaining gap is workflow shape:

- too many first-rank surfaces still compete on the default shell
- the intake area still duplicates lifecycle guidance, mission setup, and auxiliary explanation in the same visual rank
- review and delivery areas still expose `Claim Composer`, `Report Studio`, `AI Assistance Surfaces`, and `Distribution Health` too early for most operators
- outputs are persisted in the system, but the default shell still makes it too hard to answer "what came out of the step I just did?"

## Distilled External Practice

This wave is grounded in external patterns that fit this repo's problem shape.

### GOV.UK Service Manual

The service standard emphasizes understanding the user problem in the simplest effective way before optimizing a preferred solution.

Source:

- [Understand users and their needs](https://www.gov.uk/service-manual/service-standard/point-1-understand-user-needs)

Repo implication:

- do not keep adding surfaces because the underlying capabilities exist
- restructure the shell around what operators need to complete next

### GOV.UK Task Lists

The `Complete multiple tasks` pattern exists to help users understand:

- the tasks involved in completing a transaction
- the order they should complete tasks in
- when they have completed tasks

It also recommends grouping lots of tasks into steps.

Source:

- [Complete multiple tasks](https://design-system.service.gov.uk/patterns/complete-multiple-tasks/)

Repo implication:

- the shell should make lifecycle steps and completion status explicit
- top-level navigation should resemble a workflow map more than a capability dump

### GOV.UK Accordion, Tabs, And Conditional Reveal

The accordion guidance explicitly says:

- only use accordions when there is evidence they help
- do not use them for content all users need to see
- it is usually better to simplify and reduce content, split content across multiple pages, or keep content on one page separated by headings

The tabs guidance says tabs are for navigating between related sections of content, displaying one section at a time, and are useful when users need to switch quickly without seeing multiple sections at once.

The radios guidance says complicated conditionally revealed questions should move to the next page or next step instead of being expanded inline.

Sources:

- [Accordion](https://design-system.service.gov.uk/components/accordion/)
- [Tabs](https://design-system.service.gov.uk/components/tabs/)
- [Radios](https://design-system.service.gov.uk/components/radios/)

Repo implication:

- do not try to rescue the current complexity through more foldouts
- reserve tabs for detail views such as one mission's `Config / Runs / Results`
- move complex secondary decisions into the next step or nested workspace instead of showing everything at the same rank

### Fluent 2 Feedback Surfaces

Fluent 2 distinguishes `Toast` from `Message bar`:

- toast is temporary and useful for non-critical status updates
- progress toasts are appropriate for operations the user initiated
- message bars communicate important state for the page, tab, card, or container where the work is happening
- error and warning message bars should include a resolution path

Sources:

- [Toast](https://fluent2.microsoft.design/components/web/react/core/toast/usage)
- [Message bar](https://fluent2.microsoft.design/components/web/react/core/messagebar/usage)

Repo implication:

- keep toasts for started or completed acknowledgements
- move no-result, blocked, degraded, and corrective-action states into page-level or card-level surfaces

### Carbon Navigation And Empty States

Carbon distinguishes:

- global or system-level tasks
- local or product-level tasks

Carbon also treats no-data, user-action, and error-management empty states as first-class situations and warns that more content is not automatically better because it increases cognitive cost.

Sources:

- [Global header](https://carbondesignsystem.com/patterns/global-header/)
- [Empty states pattern](https://carbondesignsystem.com/patterns/empty-states-pattern/)

Repo implication:

- separate global console chrome from workflow navigation
- design no-result, completion, and configuration-missing states in place, with one clear next action

## Workflow-First Shell Judgment

### Default Top-Level Shape

The default shell should be reorganized around four workflow stages:

1. `Start`
2. `Monitor`
3. `Review`
4. `Deliver`

Meaning:

- `Start` frames the current task list and entrypoint rather than carrying a dense permanent onboarding wall
- `Monitor` owns mission creation, mission list, mission detail, and result inspection
- `Review` owns triage, story advancement, and the outputs that are still under editorial or analyst control
- `Deliver` owns routes, dispatch posture, delivery history, and downstream status

### Promotion And Demotion Rules

Top-level surfaces must be limited to what most operators need to answer:

1. what step am I in
2. what object am I acting on
3. what output already exists
4. what next action is available

These surfaces remain first-rank:

- mission list and mission detail
- triage queue
- story workspace
- route and delivery posture
- workflow progress and task completion state

These surfaces should be demoted behind nested actions, drawers, detail tabs, or advanced mode:

- `Claim Composer`
- `Report Studio`
- `AI Assistance Surfaces`
- `Distribution Health`
- repeated lifecycle onboarding copy that competes with real work objects

### Output Visibility Contract

Each workflow stage must expose its owned output explicitly:

| Stage | Operator question | Required owned output |
| --- | --- | --- |
| `Start` | what can I begin next | task list and readiness state |
| `Monitor` | what did the mission produce | latest run outcome, result count, no-result explanation, route trigger outcome |
| `Review` | what evidence survived analyst review | triage state, promoted story candidate, contradiction or readiness state |
| `Deliver` | what was sent or blocked | dispatch status, route health, and delivery history |

If a stage has no output yet, the empty state must explain:

1. why the surface is empty
2. what the primary next action is
3. where that action lives

## What This Wave Must Preserve

Invariants:

1. `WatchMission`, `DataPulseItem`, `Story`, `Report`, and named routes remain canonical lifecycle nouns in the backend and API
2. the browser remains a projection over Reader, CLI, MCP, and HTTP truth
3. the command chamber visual language remains intentional and repo-specific
4. current URL-restorable workspace context remains valid unless a later contract explicitly reopens it
5. existing retry guidance, duplicate explain, and mission guidance stay reused rather than re-derived

## What This Wave Must Not Do

This wave must not:

- trigger a default React or Vite migration decision
- open a second routing tree unrelated to the current section and URL contract
- create a bland admin-dashboard shell that discards the command chamber language
- let advanced or internal semantics remain promoted just because they already have a panel
- replace lifecycle nouns with marketing language in the backend or API

## L25 Contract Targets

`L25.2` should freeze five things before shell simplification begins:

1. the top-level workflow stages and which existing sections collapse into each stage
2. which surfaces remain first-rank versus demoted
3. the output visibility contract per stage
4. feedback ownership across toast, message bar, and empty-state surfaces
5. the minimum acceptance checklist for operator comprehension

## L25.2 Frozen Workflow-First Shell Contract

`L25.2` froze the repo truth that `L25.3` and `L25.4` later implemented.

### Stage Map

The top-level shell must expose four workflow stages in this order:

1. `Start`
2. `Monitor`
3. `Review`
4. `Deliver`

Existing sections collapse into those stages as follows:

| Stage | Existing shell scope that belongs here | What stays visible at first rank |
| --- | --- | --- |
| `Start` | mission kickoff, readiness framing, operator task list, entry actions | readiness state, primary start action, current workflow checklist |
| `Monitor` | mission creation, mission list, mission detail, run and result inspection | mission list, selected mission detail, latest run outcome |
| `Review` | triage, story advancement, analyst review, contradiction handling | triage queue, story workspace, analyst readiness state |
| `Deliver` | routes, dispatch posture, delivery history, downstream status | route posture, dispatch outcome, delivery history |

### First-Rank Versus Demoted Surfaces

These surfaces remain first-rank in the default shell:

- workflow stage navigation and completion state
- mission list plus selected mission detail
- triage queue
- story workspace
- route and delivery posture
- each stage's currently owned output card or summary

These surfaces are demoted behind nested actions, detail tabs, drawers, or explicit advanced mode:

- `Claim Composer`
- `Report Studio`
- `AI Assistance Surfaces`
- `Distribution Health`
- repeated onboarding or lifecycle explainer copy after the operator has already entered the relevant stage

Demotion rule:

- a surface does not stay first-rank just because it already exists; it must directly answer the current stage, current object, owned output, or primary next action

### Stage-Owned Output Contract

Each stage owns a visible output surface that answers the operator's main question before they leave the stage.

| Stage | Primary operator question | Owned output that must stay visible |
| --- | --- | --- |
| `Start` | what can I begin next | readiness state, current checklist, and primary start action |
| `Monitor` | what did the mission produce | latest run outcome, result count, no-result explanation, and route trigger outcome when applicable |
| `Review` | what survived analyst review | triage disposition, promoted story candidate, contradiction state, and readiness to deliver |
| `Deliver` | what was sent or blocked | dispatch status, route health, downstream delivery history, and current blocker if delivery did not proceed |

If a stage does not yet have a produced output, its empty state must explain why the stage is empty, what the primary next action is, and where that action lives.

### Feedback Ownership Rules

Feedback ownership is stage-local by default.

| Surface | Owner | Allowed use |
| --- | --- | --- |
| Toast | transient acknowledgement for the action the operator just started or finished | started, queued, completed, or copied acknowledgements that do not need to persist |
| Message bar | the stage, tab, card, or detail container that owns the affected work object | actionable warning, degraded state, no-result explanation, blocked state, or recoverable error with a next step |
| Empty state | the stage-owned output area when no object or no output exists yet | explain why nothing is shown, name the next action, and point to the control that resolves it |

Ownership rule:

- no-result, blocked, degraded, and corrective-action states must not rely on toast history alone once the operator may need to refer back to them

### Minimum Acceptance Checklist

Before `L25.3` is considered landed, the repo must preserve these comprehension checks:

1. an operator can identify the current workflow stage without reading auxiliary docs
2. an operator can identify the current object being acted on inside that stage
3. an operator can identify the owned output or the explicit reason it is still empty
4. an operator can identify one primary next action without scanning demoted surfaces
5. a no-result, warning, or blocked state appears on the stage-owned surface that can resolve it

## L25 Slice Map

| Slice | Outcome | Why it exists |
| --- | --- | --- |
| `L25.1` | Land this repo-scoped workflow-first simplification blueprint and fact promotion | Opens a new wave after `L24` completion without confusing it with the already-landed URL or guidance work |
| `L25.2` | Freeze the workflow-first shell contract and promotion or demotion rules | Prevents implementation drift before shell simplification starts |
| `L25.3` | Simplify the top-level shell into workflow-first stages and reduce same-rank surfaces | Lowers cognitive load where operators first enter and move through the console |
| `L25.4` | Move no-result, warning, completion, and blocked states onto stage-owned surfaces | Makes step outcomes legible without relying on transient toast history |
| `L25.5` | Harden browser smoke and acceptance around workflow order, stage outputs, and next-step discoverability | Prevents regressions after the shell is simplified |

## Recommended Ignition Order

Recommended order:

1. `L25.2` landed
2. `L25.3` landed
3. `L25.4` landed
4. `L25.5` landed

## Completion Handoff

`L25` is now complete in repo truth through `L25.5`.

What landed in this wave:

- workflow-first shell order around `Start / Monitor / Review / Deliver`
- first-rank versus demoted surface rules
- stage-owned output visibility and empty-state ownership
- stage-local feedback ownership for no-result, warning, blocked, and completion states
- browser smoke and acceptance hardening around workflow order and next-step discoverability

What this wave does not reopen automatically:

- a React or Vite migration
- a GUI-only control plane
- additional surface promotion just because a capability already exists

Current repo truth for this wave now has no open structured slice.

## Manual Ignition Boundary

The next manual ignition target no longer lives inside `L25`.

Reason:

- the repo already has the clarity primitives needed from `L24`
- the workflow-first shell follow-up is already closed in repo truth through `L25.5`
- any further change should reopen through a new blueprint wave or evidence-backed regression rather than pretending `L25` is still in flight

After the blueprint landing is committed and the repo is back to a clean baseline, the normal local ignition entrypoint stays:

```bash
bash scripts/governance/ignite_datapulse_codex_loop.sh
```

Expected next slice after this closeout: `no-open-slice`

## Fact Sources

- `/Users/sunyifei/Library/Mobile Documents/iCloud~md~obsidian/Documents/SunYifei/01-项目开发/DataPulse/00_索引与计划/DataPulse_agent-skills-hub前端交互清晰化补强清单_2026-03-31.md`
- `/Users/sunyifei/DataPulse/docs/gui_intelligence_console_plan.md`
- `/Users/sunyifei/DataPulse/docs/governance/datapulse-console-interaction-clarity-blueprint.md`
- [Understand users and their needs](https://www.gov.uk/service-manual/service-standard/point-1-understand-user-needs)
- [Complete multiple tasks](https://design-system.service.gov.uk/patterns/complete-multiple-tasks/)
- [Accordion](https://design-system.service.gov.uk/components/accordion/)
- [Tabs](https://design-system.service.gov.uk/components/tabs/)
- [Radios](https://design-system.service.gov.uk/components/radios/)
- [Toast](https://fluent2.microsoft.design/components/web/react/core/toast/usage)
- [Message bar](https://fluent2.microsoft.design/components/web/react/core/messagebar/usage)
- [Global header](https://carbondesignsystem.com/patterns/global-header/)
- [Empty states pattern](https://carbondesignsystem.com/patterns/empty-states-pattern/)

## Success Condition

DataPulse completed the workflow-first GUI wave without reopening frontend architecture:

- the top-level shell is simplified around workflow order
- output visibility and next-step discovery are explicit repo-owned obligations
- advanced surfaces are demoted by rule rather than by taste
- there is no current open structured slice inside this wave
