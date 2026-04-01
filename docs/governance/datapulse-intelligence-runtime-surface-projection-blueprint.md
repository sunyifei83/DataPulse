# DataPulse Intelligence Runtime And Surface Projection Blueprint

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

## L27 Slice Map

| Slice | Outcome | Why it exists |
| --- | --- | --- |
| `L27.1` | Land this repo-scoped runtime-kernel and surface-projection blueprint plus fact promotion | Converts the cross-repo runtime judgment into repo truth before code slices reopen |
| `L27.2` | Freeze the canonical runtime layer map, ownership rules, and service-seam targets | Fixes what belongs to acquisition adapters, Reader/lifecycle kernel, surface projections, AI overlay, and governance before refactor work drifts |
| `L27.3` | Extract domain service seams behind a stable `DataPulseReader` facade | Reduces monolithic Reader growth without reopening public lifecycle nouns or pushing orchestration into surface wrappers |
| `L27.4` | Introduce a machine-readable surface capability catalog and shared projection helpers | Turns CLI/MCP/console/agent/skill parity into explicit repo truth instead of repeated ad hoc glue |
| `L27.5` | Harden parity verification, runtime introspection, and reopen rules | Prevents silent surface drift and records what evidence would justify a later reopen above this wave |

## Recommended Ignition Order After This Refresh

Recommended order after this refresh:

1. `L27.1`
2. `L27.2`
3. `L27.3`
4. `L27.4`
5. `L27.5`

This order keeps DataPulse from jumping straight into another implementation-heavy expansion before the runtime boundary, service seams, and surface-parity rules are explicit repo truth.
