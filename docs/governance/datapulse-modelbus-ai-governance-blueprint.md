# DataPulse ModelBus AI Governance Blueprint

## Purpose

This document promotes the external ModelBusProject AI-governance note into repository-scoped blueprint truth.

The goal is not to import a second runtime or another product essay into DataPulse. The goal is to define the next narrow blueprint slices that let DataPulse add AI assistance under the same lifecycle, delivery, and governance rails that already exist in-repo.

## Current Repo Read

The repository now has enough structured lifecycle and governance surface area that AI assistance can be added as a governed assist layer rather than as ad hoc provider calls.

Current repo anchors:

- `docs/intelligence_lifecycle_contract.md`
- `docs/intelligence_delivery_contract.md`
- `docs/gui_intelligence_console_plan.md`
- `docs/governance/datapulse-evidence-backend-contract.md`
- `docs/governance/datapulse-report-delivery-subscription-blueprint.md`
- `datapulse/reader.py`
- `datapulse/core/triage.py`
- `datapulse/core/story.py`
- `datapulse/core/report.py`
- `datapulse/core/alerts.py`

That changes the highest-leverage delta.

The repo no longer needs scattered model/provider helpers first. The next delta is to define one governed AI-assistance plane that can serve watch, triage, report, and delivery workflows without granting AI direct final-state authority.

## Canonical AI Assistance Stage Mapping

The follow-up lifecycle extension for this wave should stay additive:

- `WatchMission`, `MissionRun`, `DataPulseItem`, `Story`, `Report`, and `ExportProfile` remain the canonical business objects.
- AI assistance should be modeled as governed helper surfaces over those objects, not as a second lifecycle.
- surface-level model choice, fallback, and provider routing should resolve through a ModelBus bridge instead of repo-local SDK coupling.
- structured AI payloads should fail closed before they can influence review, report, or delivery work.
- admitted capabilities should be explicit per surface before Reader-backed runtime calls land.

Invariants to enforce before implementation work:

1. AI assistance may generate `suggestion`, `draft`, `explain`, or candidate judgment objects only; it cannot write final review or delivery state directly.
2. `off`, `assist`, and `review` must be explicit shared semantics across Reader, CLI, MCP, and console surfaces.
3. DataPulse must not hardcode provider SDK assumptions, route secrets, or model-selection policy into watch, triage, report, or delivery code.
4. structured output contracts are required for governed AI payloads; missing or invalid schema must fail closed.
5. capability admission must be machine-readable per surface before any model is treated as production-eligible.
6. runtime fallback, degradation, and audit remain visible governance facts rather than hidden prompt behavior.
7. browser projection must stay a thin surface over Reader-backed objects; no GUI-only AI state machine is allowed.

Stage map for implementation:

- `L16.1`: repo-scoped blueprint and ignition-map landing
- `L16.2`: AI assistance surface contracts plus `off/assist/review` semantics
- `L16.3`: DataPulse-to-ModelBus bridge contract
- `L16.4`: structured output contracts and fail-closed validation
- `L16.5`: candidate subscriptions and admission facts per AI surface
- `L16.6`: Reader-backed AI assistance services
- `L16.7`: CLI, MCP, console, and ops projection
- `L16.8`: verification and governance-scorecard hardening

## L16.2 Surface Contract Baseline

`L16.2` should treat the following as the formal AI assistance surfaces for this wave:

| Surface | Business anchor | Output class | Final authority remains with |
| --- | --- | --- | --- |
| `mission_suggest` | watch and mission planning | suggestion | operator or existing deterministic mission logic |
| `triage_assist` | item review and triage explanation | explain / candidate judgment | operator triage action |
| `claim_draft` | story-to-claim staging | draft | report quality and editorial review |
| `report_draft` | report assembly and export shaping | draft | report finalization and export gates |
| `delivery_summary` | delivery audit, route health, and output explanation | summary / explain | attributable alert, route, and dispatch flows |

Shared switch semantics:

- `off`: fully deterministic/manual behavior; no AI call for the surface
- `assist`: AI may return additive suggestions, drafts, or explanations only
- `review`: AI may prefill candidate initial assessments for the same surface, but operator confirmation is still required before any final-state effect

Authority rules:

- no AI surface may write final `review_state`, final report/export authority, or route dispatch outcomes directly
- `review` is still operator-confirmed mode, not autonomous mode
- the same surface ids and switch meanings must hold across Reader, CLI, MCP, API, and console projections

## L16.3 ModelBus Bridge Contract Baseline

`L16.3` should treat [datapulse-modelbus-bridge-contract.md](/Users/sunyifei/DataPulse/docs/governance/datapulse-modelbus-bridge-contract.md) as the contract of record for the repo-facing ModelBus boundary.

Bridge inputs that DataPulse may own in this phase:

- `base_url`
- `bus_key`
- `alias_by_surface`
- `timeout_seconds`
- caller metadata and governed runtime hints such as whether degraded results are acceptable

Bridge rules for this phase:

- DataPulse chooses the governed surface id, lifecycle context, and `off / assist / review` mode.
- DataPulse resolves one stable alias key per surface; alias keys are governance identifiers, not provider names.
- ModelBus owns alias expansion, provider routing, retries, fallback order, and downstream provider credentials.
- DataPulse owns only the bridge-facing `bus_key`; downstream provider secrets stay outside the repo boundary.
- missing alias mapping, missing `bus_key`, or invalid bridge output must fail closed to manual or deterministic behavior.
- runtime fallback and degradation must come back as visible runtime facts so later slices can project them into scorecards and operator views.

## Internal Research Staging Boundary For Current Repo-Prep

The current repo-prep wave also fixes what DataPulse may name internally without widening its published surface set:

- `ReportBrief` and `CitationBundle` remain landed repo-backed report objects.
- `research_packet` and repo-local research `evidence_bundle` are repo-local working-slice objects that stage inputs toward those landed objects.
- those staging nouns are not public AI surfaces, not stable CLI/MCP/API contract nouns, and not substitutes for runtime admission evidence.
- `web_research` remains a non-public candidate surface until CLI surface enumeration, lifecycle/AI-governance contract language, and same-window runtime evidence align.

## Post-Fix ModelBus Joint-Debug Entry Criteria

The next same-window joint-debug window should open only when all of the following are true:

1. ModelBus bundle truth, DataPulse CLI surface enumeration, and repo contract language describe the same published public AI surface set for the debug window.
2. If the aligned public set is still five surfaces, `web_research` remains internal-only and is not treated as admitted or operator-visible.
3. `research_packet` and repo-local research `evidence_bundle` are described as staging-only working-slice nouns, while `ReportBrief` and `CitationBundle` remain the landed repo-backed objects they feed.
4. same-window machine-readable runtime evidence exists for `mission_suggest`, `triage_assist`, `claim_draft`, `report_draft`, and `delivery_summary`.
5. `mission_suggest`, `triage_assist`, `claim_draft`, and `delivery_summary` verify as `verified`, while `report_draft` verifies as `verified_fail_closed`.
6. runtime provenance exposes `admission_source=modelbus_bundle`, `served_by_alias`, `request_id`, `degraded`, `fallback_used`, `schema_valid`, and `manual_override_required`.
7. the debug-prep slice does not bind provider-specific aliases or downstream provider credentials directly into DataPulse business modules.

Only after this gate is met should a later slice discuss whether `web_research` graduates from internal staging language into a published surface.

## High-Value Facts To Promote

### 1. DataPulse already has the right governance rails for AI assistance

Current repo reality:

- lifecycle progression is explicit from watch through report and delivery
- delivery surfaces already separate source truth, route dispatch, and ops observations
- evidence backends already have deterministic fallback and provenance rules

Repo implication:

- AI assistance should extend current governance rails instead of inventing a special-case AI feature lane
- the ModelBus bridge should look like another governed backend boundary, not a parallel product runtime inside DataPulse

### 2. The next meaningful AI upgrade is surface governance, not more raw model hookups

Current repo reality:

- DataPulse already has object boundaries for triage, story, report, and delivery work
- report and delivery slices established cross-surface parity and route-backed output semantics

Repo implication:

- the next blueprint wave should define AI surfaces such as `mission_suggest`, `triage_assist`, `claim_draft`, `report_draft`, and `delivery_summary`
- model selection should attach to surface capability and governance mode, not to whichever module imports an SDK

### 3. Structured contracts and admission facts must precede runtime usage

Current repo reality:

- the repo already treats governance facts, route health, and export shape as explicit contracts
- the evidence backend contract already rejects hidden overwrite behavior and silent fallback drift

Repo implication:

- AI outputs should become explicit schema-governed payloads instead of freeform prose that "looks parseable"
- candidate model bundles and admitted surface capability must be separated so DataPulse can reject unsafe or unqualified routes before runtime use

### 4. ModelBus should own routing and fallback policy while DataPulse owns business truth

Current repo reality:

- DataPulse owns mission, triage, story, report, and delivery objects
- named routes already separate reusable sink identity from transport configuration

Repo implication:

- DataPulse should hand ModelBus a governed surface request and receive a structured result plus runtime facts
- DataPulse should not duplicate provider compatibility, token-pool, or fallback orchestration logic that belongs in the ModelBus layer
- DataPulse should treat `base_url + bus_key + alias_by_surface + timeout` as the repo-facing bridge contract and keep fallback ownership declarative rather than provider-specific

### 5. Cross-surface projection still matters more than GUI novelty

Current repo reality:

- browser console work is intentionally a projection over Reader-backed objects
- governance docs already reject GUI-only lifecycle drift

Repo implication:

- AI assistance must appear through Reader, CLI, MCP, API, and console with the same surface nouns and switch semantics
- no browser-first AI copilot state should land before Reader-backed contracts and admission facts exist

## What Should Not Be Promoted As First-Class Slices Now

This wave does not justify immediate blueprint slices for:

- direct provider SDK integrations in DataPulse business modules
- a GUI-only copilot workflow or hidden browser-side AI draft store
- ungated model experimentation against production surfaces
- AI-authored final triage, export, or route-dispatch authority
- duplicating a full ModelBus runtime, billing, or multi-tenant control plane inside this repo

Those moves would either fork the lifecycle or weaken existing governance truth.

## Integration Rules For This Phase

All follow-up slices in this phase should obey the same constraints:

1. preserve current lifecycle truth in `WatchMission`, `DataPulseItem`, `Story`, `Report`, and `ExportProfile`
2. treat AI assistance as an additive governed layer over existing objects
3. keep `off`, `assist`, and `review` semantics explicit and shared across surfaces
4. use a stable ModelBus bridge contract for `base_url`, `bus_key`, surface alias mapping, timeout, and fallback ownership
5. require structured AI payload contracts and fail closed when validation or contract lookup fails
6. separate candidate model subscriptions from admitted surface capabilities
7. expose runtime fallback, schema-pass, admission, and manual-override facts through operator-visible governance outputs
8. project the same AI assistance nouns through Reader, CLI, MCP, API, and browser instead of inventing GUI-only state
9. keep slices narrow enough that the loop can stop on machine-decidable progress

## L32 Execution-Control Model-Tier Profile Contract

`L32` is a repo-native execution-control overlay, not a public runtime or ModelBus routing change.

The profiles below govern local planning and bounded execution lanes only. They must not be narrated as new public AI surfaces, published alias policy, or release-routing semantics.

| Profile id | Preferred local lane now | Allowed task shape | Must stay out of scope |
| --- | --- | --- | --- |
| `planning_architecture_review` | `gpt-5.4` | architecture review, slice planning, contract diffs, cross-repo governance reasoning | broad code churn, silent runtime policy rewrites, or public-surface expansion |
| `bounded_exporter_doc_edit` | `gpt-5.4-mini` | small exporter updates, doc sync, mirror or classifier touchups, bounded repo edits with explicit artifact targets | multi-phase refactors, open-ended codebase rewrites, or implicit promotion-policy changes |
| `codex_compatibility_repair` | `gpt-5.3-codex` | historical Codex-compatible repair lanes, strong coding regressions, or compatibility-preserving bounded edits where the existing Codex lane still matters | default routing for all work, new provider-policy narrative, or a claim that older Codex lanes remain the public runtime baseline |
| `local_operator_recovery` | `Claude Code` style local operator lane | resume, recap, worktree/session recovery, protocol repair, and tool-native local runtime experiments under operator supervision | direct published-runtime authority, automatic release promotion, or hidden trust elevation for hooks, MCP metadata, or tool output |

Contract rules for any future consumer of these profiles:

- treat the profile id as repo-governance truth and the model binding above as the current preferred local binding, not as a public ModelBus alias contract
- use explicit allowlists when a loop runner, handoff resource, or sidecar claims one of these profiles
- fail closed to manual operator review when a requested profile is missing, ambiguous, or wider than the slice's declared artifact and verification scope
- keep profile choice inside `L1` execution economics; `L0` published runtime contracts, surface admission, and ModelBus fallback ownership remain unchanged
- preserve the Reader-backed lifecycle kernel as canonical business truth; these profiles only steer how local operators and agent runtimes approach repo work

## Stage Preview

Recommended stage language for this follow-up wave:

- `A0`: current repo baseline `deterministic lifecycle + optional evidence backend + report-backed delivery`
- `A1`: AI assistance blueprint, surface map, and ignition order
- `A2`: shared AI surface contract and switch semantics
- `A3`: ModelBus bridge contract and runtime-boundary definition
- `A4`: structured payload schemas and fail-closed validation
- `A5`: subscription candidate sets and admitted-surface governance facts
- `A6`: Reader-backed AI assist runtime services
- `A7`: CLI, MCP, API, console, and ops projection
- `A8`: verification gates, scorecards, and runtime-regression hardening

## L16 Slice Map

| Slice | Outcome | Why it exists |
| --- | --- | --- |
| `L16.1` | Land this repo-scoped ModelBus-backed AI assistance governance blueprint and ignition map | Converts the external ModelBus note into repo truth before runtime or contract slices reopen |
| `L16.2` | Define AI assistance surfaces and `off/assist/review` switch semantics in the shared lifecycle contract | Fixes what AI is allowed to do before bridge or schema work starts drifting; formal surfaces are `mission_suggest`, `triage_assist`, `claim_draft`, `report_draft`, and `delivery_summary` |
| `L16.3` | Add the DataPulse-to-ModelBus bridge contract for route alias, bus key, and runtime config inputs | Keeps DataPulse decoupled from provider SDK details while making runtime boundaries explicit |
| `L16.4` | Add structured AI output contracts and fail-closed validation | Prevents freeform or invalid AI payloads from quietly entering governed flows |
| `L16.5` | Introduce candidate subscriptions and admitted-surface capability facts | Separates "available to consider" from "approved to use" for each AI surface |
| `L16.6` | Add Reader-backed AI assistance services for governed suggestions, drafts, and prechecks | Lands runtime value without letting AI write final operational state |
| `L16.7` | Project AI assistance through CLI, MCP, console, and ops scorecards | Preserves cross-surface parity and keeps the browser as a projection |
| `L16.8` | Harden verification gates and governance scorecards for AI runtime semantics | Protects switch modes, validation, fallback, admission, and override observability before broader promotion |

## Recommended Ignition Order After This Refresh

Recommended order after this refresh:

1. `L16.1`
2. `L16.2`
3. `L16.3`
4. `L16.4`
5. `L16.5`
6. `L16.6`
7. `L16.7`
8. `L16.8`

This order keeps DataPulse from jumping into runtime calls or browser affordances before AI surface authority, ModelBus boundaries, structured contracts, and admission governance are explicit.
