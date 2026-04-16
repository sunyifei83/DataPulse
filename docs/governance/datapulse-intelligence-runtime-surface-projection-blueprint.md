# DataPulse Intelligence Runtime And Surface Projection Blueprint

Status: repo-scoped follow-up blueprint, `L27.2` boundary-freeze landing completed

Created: 2026-04-01

Updated: 2026-04-01

## Purpose

This document promotes the external Obsidian runtime-extraction note into repository-scoped blueprint truth.

The goal is not to copy Claude Code's agent runtime into DataPulse. The goal is to identify the repo-specific high-value capability that DataPulse has already formed in code: a local-first intelligence runtime with Reader-backed lifecycle truth, multi-surface projections, a governed AI overlay, and a blueprint-driven control plane.

## Current Repo Read

The current repository now has five distinct layers that already behave like one runtime stack:

1. acquisition adapters:
   - `datapulse/core/router.py`
   - `datapulse/core/search_gateway.py`
   - `datapulse/collectors/*`
2. lifecycle kernel:
   - `datapulse/reader.py`
   - `datapulse/core/watchlist.py`
   - `datapulse/core/triage.py`
   - `datapulse/core/story.py`
   - `datapulse/core/report.py`
   - `datapulse/core/alerts.py`
3. surface projections:
   - `datapulse/cli.py`
   - `datapulse/mcp_server.py`
   - `datapulse/console_server.py`
   - `datapulse/agent.py`
   - `SKILL.md`
   - `datapulse_skill/manifest.json`
4. governed AI overlay:
   - `docs/intelligence_lifecycle_contract.md`
   - `docs/governance/datapulse-modelbus-ai-governance-blueprint.md`
   - `config/modelbus/datapulse/surface_admission.json`
   - `config/modelbus/datapulse/bridge_config.json`
5. repo governance control plane:
   - `docs/governance/datapulse-blueprint-plan.json`
   - `scripts/governance/run_codex_blueprint_loop.py`
   - `scripts/governance/ignite_datapulse_codex_loop.sh`

That changes the highest-leverage delta.

The repo no longer needs a collector-count wave or another browser-first expansion wave as the primary target. The next delta is to freeze the runtime boundaries, reduce repeated projection glue, and make cross-surface capability ownership explicit before the next growth cycle.

## Canonical Runtime Layer Mapping

### 1. Acquisition Adapters

This layer owns:

- source-specific parsing
- public-web search acquisition
- route-to-collector selection
- retry or source fallback at the intake boundary

This layer does not own lifecycle truth, operator workflow, or cross-surface parity.

### 2. Lifecycle Kernel

This layer owns:

- `WatchMission`
- `MissionRun`
- `DataPulseItem` triage state
- `Story`
- report-layer nouns
- delivery and ops snapshots
- Reader-backed orchestration over those objects

Current repo fact:

- `datapulse/reader.py` is already the de facto runtime kernel, not a thin helper.

### 3. Surface Projections

This layer owns projection, not business truth:

- CLI flag and output projection
- MCP tool projection
- browser API projection
- lightweight agent/skill wrappers

Invariants:

1. surface code must project shared lifecycle nouns instead of inventing new ones
2. surface-specific affordances may differ, but semantic capability ownership must stay aligned
3. no surface should quietly become the canonical orchestration owner for a lifecycle capability

### 4. Governed AI Overlay

This layer remains additive:

- AI attaches to existing lifecycle objects
- AI payloads stay contract-bound and fail closed
- admitted capability facts remain separate from candidate subscriptions
- final review, export, and dispatch authority stay with deterministic or operator-owned flows

### 5. Repo Governance Control Plane

This layer owns:

- blueprint progress truth
- next-slice selection
- evidence round-trip
- runtime-hit and release attestation truth
- ignition and reopen semantics

This matters because the runtime/surface wave should now be landed as machine-readable repo progression rather than as informal refactor intent.

## High-Value Facts To Promote

### 1. DataPulse is now closer to an intelligence runtime than to a collector bundle

Current repo reality:

- `datapulse/reader.py` is `6769` lines
- `datapulse/cli.py` is `2593` lines
- `datapulse/mcp_server.py` is `2016` lines
- `datapulse/console_server.py` is `1007` lines

Repo implication:

- the highest-leverage abstraction is no longer "which collector lands next"
- the highest-leverage abstraction is the kernel-plus-projection runtime shape already present in code

### 2. Cross-surface parity is now a first-class product capability

Current repo reality:

- watch, triage, story, report, delivery, and AI surfaces already span Reader, CLI, MCP, and browser API
- agent and skill packaging already project the same repo into assistant-facing entrypoints

Repo implication:

- surface parity should be treated as a primary acceptance target
- future capability work should declare which surfaces it lands on and which remain intentionally absent

### 3. The next scaling risk is repeated surface glue, not missing workflow nouns

Current repo reality:

- lifecycle nouns are already explicit through mission, triage, story, report, delivery, and AI governance docs
- repeated glue is now concentrated around Reader-to-surface wiring and the continued growth of `DataPulseReader`

Repo implication:

- the next blueprint wave should target service seams, projection metadata, and parity verification
- the repo should stop paying for every new capability by touching each surface ad hoc

### 4. AI and governance are overlays on the runtime, not alternate runtimes

Current repo reality:

- AI surfaces are governed through contracts, admissions, and fail-closed semantics
- blueprint and evidence exporters already provide repo-level control-plane truth

Repo implication:

- runtime refactors must preserve AI/governance as overlays over shared lifecycle objects
- no future slice should move business truth into provider-specific or browser-only side channels

### 5. This repo can now legitimately blueprint maintainability work as leverage work

Current repo reality:

- the codex blueprint loop already exists
- the active blueprint can reopen on new narrow slices

Repo implication:

- runtime-boundary and surface-parity work is now a justified ignition target, not a side note

## What Should Not Be Promoted As First-Class Slices Now

This wave does not justify immediate blueprint slices for:

- another collector-only expansion wave as the primary target
- a second frontend stack or GUI-only workflow state
- direct provider-specific AI glue inside CLI, MCP, or browser handlers
- turning surface wrappers into business-logic owners
- replacing `DataPulseReader` public semantics before the next domain seams are frozen

Those moves would either duplicate the runtime or weaken already-landed cross-surface truth.

## Integration Rules For This Phase

All follow-up slices in this phase should obey the same constraints:

1. new lifecycle capability must land in shared core plus Reader-backed semantics before surface-specific polish
2. acquisition adapters remain upstream capability providers, not lifecycle owners
3. CLI, MCP, console, agent, and skill surfaces must project shared capability nouns rather than freeform wrapper names
4. AI surfaces remain governed overlays with fail-closed structured contracts
5. runtime-control and evidence outputs remain machine-readable and separate from browser-only status views
6. internal Reader decomposition may change file structure, but not the canonical lifecycle nouns exposed across surfaces
7. future slices should leave machine-readable parity or availability facts where practical
8. slices must stay narrow enough that the blueprint loop can stop on machine-decidable progress

## Stage Preview

Recommended stage language for this follow-up wave:

- `K0`: current repo baseline `acquisition adapters -> Reader kernel -> CLI/MCP/console/agent/skill projections -> governed AI overlay -> blueprint control plane`
- `K1`: runtime-boundary and ownership freeze
- `K2`: Reader domain-service seams behind a stable facade
- `K3`: machine-readable surface capability catalog
- `K4`: shared projection helpers and surface introspection
- `K5`: parity verification and reopen hardening

## L27.1 Landing Note

`L27.1` is now landed in repo docs and active blueprint truth.

What landed:

- this repo-scoped blueprint now records DataPulse as a Reader-backed intelligence runtime with acquisition adapters, a Reader/lifecycle kernel, multi-surface projections, a governed AI overlay, and a repo governance control plane
- the active blueprint now treats `L27` as the open runtime-boundary wave instead of a future idea
- structured repo truth now exposes `L27.2` as the next manual ignition target before service-seam extraction or surface-catalog work begins

Acceptance evidence:

- `test -f docs/governance/datapulse-intelligence-runtime-surface-projection-blueprint.md`
- `python3 -m json.tool docs/governance/datapulse-blueprint-plan.draft.json`
- `python3 -m json.tool docs/governance/datapulse-blueprint-plan.json`

`L27.2` should freeze six things before Reader decomposition or surface-catalog work begins:

1. the canonical runtime layer map and which repo anchors currently realize each layer
2. what each layer owns versus what it must not absorb
3. the stable `DataPulseReader` facade boundary that later seams must stay behind
4. the target domain service seams that `L27.3` may extract
5. the projection and AI-overlay rules that keep cross-surface semantics aligned
6. the acceptance and reopen checks that prevent this wave from drifting back into collector-count or frontend-only debates

## L27.2 Frozen Runtime Boundary Contract

`L27.2` freezes the repo truth that `L27.3` and `L27.4` must preserve.

### Canonical Runtime Layer Map

| Layer | Current repo anchors | Owns | Must not own |
| --- | --- | --- | --- |
| Acquisition adapters | `datapulse/core/router.py`, `datapulse/core/search_gateway.py`, `datapulse/collectors/*` | source-specific parsing, source selection, intake retries, upstream fetch fallback, normalization at the intake boundary | lifecycle state transitions, story/report truth, route dispatch truth, surface-specific UX contracts |
| Reader/lifecycle kernel | `datapulse/reader.py`, `datapulse/core/watchlist.py`, `datapulse/core/triage.py`, `datapulse/core/story.py`, `datapulse/core/report.py`, `datapulse/core/alerts.py` | canonical lifecycle nouns, persistence-backed orchestration, cross-surface capability semantics, route and delivery facts, the stable `DataPulseReader` facade | provider-specific SDK glue, browser-only workflow truth, blueprint progress truth, collector-specific parsing rules |
| Surface projections | `datapulse/cli.py`, `datapulse/mcp_server.py`, `datapulse/console_server.py`, `datapulse/agent.py`, `SKILL.md`, `datapulse_skill/manifest.json` | transport projection, command/tool/http shapes, surface-local affordances, output formatting, operator or assistant entrypoints | canonical lifecycle state, hidden orchestration forks, alternate domain nouns, provider-owned AI policy |
| Governed AI overlay | `docs/intelligence_lifecycle_contract.md`, `docs/governance/datapulse-modelbus-ai-governance-blueprint.md`, `config/modelbus/datapulse/surface_admission.json`, `config/modelbus/datapulse/bridge_config.json` | admitted AI surface ids, `off` / `assist` / `review` semantics, bridge policy, fail-closed structured payloads over existing lifecycle objects | final lifecycle writes, alternate runtime chains, ungated surface publication, browser-only or provider-only source truth |
| Governance control plane | `docs/governance/datapulse-blueprint-plan.json`, `docs/governance/datapulse-blueprint-plan.draft.json`, `scripts/governance/run_codex_blueprint_loop.py`, `scripts/governance/ignite_datapulse_codex_loop.sh` | blueprint progress truth, next-slice selection, evidence/export loop semantics, reopen and promotion decisions | mission execution, delivery dispatch, AI provider behavior, business-runtime orchestration |

### Stable Reader Facade And Service-Seam Targets

- `DataPulseReader` remains the canonical repo runtime facade for shared lifecycle capability semantics during this wave.
- `L27.3` may decompose Reader internals, but it must preserve the same public lifecycle nouns and keep CLI, MCP, console, agent, and skill wrappers as projections over that shared facade.
- service-seam extraction is therefore constrained to Reader-internal orchestration owners, not public runtime renaming.

The target service seams for future work are frozen to these bounded owners:

| Target seam | Current repo anchors | Scope frozen in `L27.2` |
| --- | --- | --- |
| Mission seam | `datapulse/reader.py`, `datapulse/core/watchlist.py`, `datapulse/core/scheduler.py` | watch creation, mission mutation, run triggers, due-run orchestration, mission and ops snapshots |
| Triage seam | `datapulse/reader.py`, `datapulse/core/triage.py`, `datapulse/core/models.py` | inbox review state, notes/actions, duplicate handling, triage explanations, queue stats |
| Story seam | `datapulse/reader.py`, `datapulse/core/story.py` | story build, update, graph/export, evidence aggregation, contradiction and semantic-review projection |
| Report seam | `datapulse/reader.py`, `datapulse/core/report.py` | report brief, claim, section, report, export-profile, and report-quality orchestration |
| Delivery seam | `datapulse/reader.py`, `datapulse/core/alerts.py`, report-delivery runtime flows | route health, delivery subscriptions, dispatch packages, dispatch records, delivery summaries |
| Governed AI seam | `datapulse/reader.py`, AI governance docs and ModelBus config | surface precheck, admitted assist/review flows, governed draft or summary payload generation |

Seam rules:

- acquisition adapters stay upstream of those seams and remain capability providers to the kernel rather than lifecycle owners
- `L27.3` must not treat CLI, MCP, console, agent, or skill wrappers as the home for mission, triage, story, report, delivery, or AI orchestration
- `L27.4` may add projection metadata or helper layers, but it must not move lifecycle truth out of the Reader/kernel boundary

### Projection, Overlay, And Control-Plane Ownership Rules

- new capability work must land in a shared kernel seam before surface-specific polish, unless the capability is explicitly projection-only
- surface wrappers may rename flags, routes, or presentation details for ergonomics, but they must not invent new lifecycle nouns or alternate state machines
- AI runtime work remains additive to the frozen lifecycle nouns and may only emit contract-bound candidate payloads or summaries
- governance automation remains read-only with respect to business runtime behavior; it may describe, select, or attest slices, but not become a mission runner or delivery executor

### Acceptance And Reopen Checks

- future slices in this wave should declare which frozen seam owns the capability before code extraction begins
- a reopen above this contract requires repo evidence of one of three things: a layer-map contradiction, a seam that cannot stay behind `DataPulseReader`, or a parity requirement that cannot be expressed without inventing wrapper-owned business truth
- collector-count growth, standalone-frontend preference, or provider-specific AI convenience are not by themselves valid reasons to reopen this boundary contract

## L32 Typed Local-First Handoff Resource Plane

`L32` adds one execution-control follow-up over the frozen runtime map: a typed local-first resource plane for current truth, blocking reasons, and execution handoffs.

This does not reopen `L27` and it does not create a new product surface.

It is a control-plane projection layer for agents and operators that sits on top of existing local files and generated snapshots.

### Resource Kinds And Backing Truth

| Resource kind | Backing repo truth | Purpose | Must not become |
| --- | --- | --- | --- |
| `datapulse.execution.current_truth.v1` | resolved blueprint plan plus `artifacts/governance/snapshots/project_specific_loop_state.draft.json` | one typed read of `current_level`, `next_slice`, `status_if_run_now`, `reason_if_run_now`, and promotion posture | a replacement for the phase tree or lifecycle truth |
| `datapulse.execution.blocking_reasons.v1` | `project_specific_loop_state.draft.json` plus `code_landing_status.draft.json` | one typed read of `blocking_facts`, remaining promotion gates, and unsatisfied promotion reasons | a metadata-only trust upgrade for tool or MCP output |
| `datapulse.execution.handoff.v1` | current slice brief, target artifacts, verification commands, and local execution-confidence sidecar refs when present | make the next manual slice or blocked handoff replayable without prompt archaeology | a new public API, chat surface, or alternate runtime chain |
| `datapulse.execution.resource_index.v1` | local manifest over the resources above | stable discovery entrypoint for agents, operators, and future local wrappers | canonical business truth by itself |

### Local-First Addressing Rules

- the first lookup path is always a repo file or generated local snapshot, not a remote MCP server
- future MCP or console projections may mirror these resources, but they must preserve the original repo path and generation window
- resource ids should stay stable across projection surfaces so the same handoff can be reopened without restating file paths in prose
- every resource should keep a `trust_boundary` section that says the projection is typed consumption aid only, not final truth by itself

### Current Truth And Blocking Payload Boundary

`datapulse.execution.current_truth.v1` should expose only the execution headline needed to decide whether the loop can continue:

- current level and current next slice
- `status_if_run_now` and `reason_if_run_now`
- workspace cleanliness and promotion mode
- generated-at time plus source refs back to the plan and loop snapshot

`datapulse.execution.blocking_reasons.v1` should expose only the machine-decidable blockers and their provenance:

- `blocking_facts`
- remaining promotion gates
- unsatisfied reasons for `repo_landed` or `ci_proven`
- freshness pointers back to the landing-status snapshot or attestation source when relevant

Neither resource may upgrade sidecar facts, MCP payloads, or tool metadata into admitted lifecycle truth.

### Execution Handoff Boundary

`datapulse.execution.handoff.v1` is the typed handoff object for local slice execution.

It should bind:

- the slice id, title, execution profile, and exit condition
- target artifacts and verification commands
- repo/worktree/session/output-root lane refs when the slice depends on them
- local execution-confidence sidecar refs when a run captured them
- the current-truth and blocking-reasons resource ids that justified the handoff

This keeps handoffs local-first and typed without narrating the governance plane as a new operator product or a second runtime kernel.

### Runtime And Surface Constraints

- Reader-backed lifecycle objects remain canonical for missions, triage, story, report, delivery, and governed AI flows
- surface projections may consume the execution resource plane, but they must present it as governance or operator context rather than as business-runtime state
- the governance control plane may emit or mirror these typed resources, but it still does not own mission execution, delivery dispatch, or AI provider semantics
- resource metadata may summarize current truth and blockers, but source-governed files remain the authority that later validation and replay must trace back to

## L27 Slice Map

| Slice | Outcome | Why it exists |
| --- | --- | --- |
| `L27.1` | Land this repo-scoped runtime-kernel and surface-projection blueprint plus fact promotion | Converts the cross-repo runtime judgment into repo truth before code slices reopen |
| `L27.2` | Freeze the canonical runtime layer map, ownership rules, and service-seam targets | Fixes what belongs to acquisition adapters, Reader/lifecycle kernel, surface projections, AI overlay, and governance before refactor work drifts |
| `L27.3` | Extract domain service seams behind a stable `DataPulseReader` facade | Reduces monolithic Reader growth without reopening public lifecycle nouns or pushing orchestration into surface wrappers |
| `L27.4` | Introduce a machine-readable surface capability catalog and shared projection helpers | Turns CLI/MCP/console/agent/skill parity into explicit repo truth instead of repeated ad hoc glue |
| `L27.5` | Harden parity verification, runtime introspection, and reopen rules | Prevents silent surface drift and records what evidence would justify a later reopen above this wave |

## Recommended Ignition Order

Recommended remaining order after `L27.2`:

1. `L27.3`
2. `L27.4`
3. `L27.5`

This order keeps DataPulse from jumping straight into implementation-heavy refactor work before the runtime boundary, service seams, and surface-parity rules are explicit repo truth.

## L27.5 Landing Note

`L27.5` is now landed in repo code, tests, and active blueprint truth.

What landed:

- shared runtime introspection now projects cross-surface capability coverage, parity status, and reopen rules from `datapulse/surface_capabilities.py`
- operators can inspect the landed runtime surface map through `datapulse --runtime-introspection`, MCP `runtime_introspection`, and `GET /api/runtime/introspection` without reading wrapper implementations by hand
- targeted verification now proves both the green path and a broken-catalog regression path, so missing surface entries or entrypoint drift become machine-detectable instead of purely narrative review
- repo truth now records the admissible reopen evidence for this wave: a layer-map contradiction, a seam that cannot stay behind `DataPulseReader`, or a parity requirement that would force wrapper-owned business truth
- repo truth also records inadmissible reopen reasons for this wave: collector-count growth, standalone-frontend preference, or provider-specific AI convenience by themselves

## Manual Ignition Boundary

`L27.5` is now landed, so the `L27` runtime-boundary and surface-parity wave is complete and there is no open slice remaining in this wave.

Reason:

- `L26` remains the completed console follow-up wave and does not need to reopen
- `L27.1` promoted the runtime-kernel and surface-projection read into repo truth
- `L27.2` froze the runtime layer map, ownership rules, and service-seam targets that future work must preserve
- `L27.3` extracted Reader-internal service seams without changing public lifecycle nouns
- `L27.4` landed a shared machine-readable surface capability catalog and projection helpers
- `L27.5` landed machine-detectable parity verification, cross-surface runtime introspection, and explicit reopen evidence rules

After the blueprint landing is committed and the repo is back to a clean baseline, the normal local ignition entrypoint stays:

```bash
bash scripts/governance/ignite_datapulse_codex_loop.sh
```

Expected next slice after this wave: `no-open-slice` until a new blueprint wave or admissible reopen evidence appears
