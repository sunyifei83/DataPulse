# DataPulse AI Surface Admission Contract

## Purpose

This document defines the contract of record for `L16.5`.

It separates candidate AI subscriptions from admitted surface capability facts so DataPulse can decide what is eligible to consider versus what is actually approved to use for each governed AI assistance surface.

## Scope

This contract covers:

- the machine-readable candidate subscription catalog for governed AI surfaces
- the machine-readable admission fact export for each surface and switch mode
- the minimum admission checks needed before a candidate alias-backed route may be treated as usable
- the rejectable gaps that must stay visible when a surface cannot be admitted

This contract does not cover:

- direct provider SDK bindings inside DataPulse
- provider account topology, fallback chains, or model routing internals owned by ModelBus
- Reader-backed runtime execution from `L16.6`
- GUI-only AI state or browser-local admission logic

## Current Repo Anchors

| Repo anchor | Current fact | Contract consequence |
| --- | --- | --- |
| `docs/intelligence_lifecycle_contract.md` | governed AI surfaces are `mission_suggest`, `triage_assist`, `claim_draft`, `report_draft`, and `delivery_summary` with `off / assist / review` semantics | admission must be expressed per surface and per mode rather than per tool or provider |
| `docs/governance/datapulse-modelbus-bridge-contract.md` | DataPulse addresses AI work by surface id and alias key, not by provider SDK | candidate subscriptions and admission facts must stay alias-based and provider-agnostic |
| `docs/contracts/datapulse_ai_*_contract.json` | `mission_suggest`, `triage_assist`, `claim_draft`, and `delivery_summary` already have fail-closed structured payload contracts from `L16.4` | admission must require a declared structured contract before a surface may be approved |
| `docs/governance/datapulse-modelbus-ai-governance-blueprint.md` | candidate model bundles and admitted surface capability must be separated | `L16.5` must leave machine-readable facts for both the candidate side and the admitted side |

## Candidate Subscription Object

`docs/governance/datapulse-ai-surface-subscriptions.example.json` is the contract example for the candidate side.

It records what DataPulse is allowed to consider for each surface before any runtime approval happens.

Top-level shape:

```json
{
  "schema_version": "datapulse_ai_surface_subscriptions.v1",
  "generated_at_utc": "2026-03-14T15:21:32Z",
  "governance_phase": "L16.5",
  "surfaces": []
}
```

Per-surface rules:

- `surface` must use one governed AI surface id from `L16.2`.
- `mode_candidates` lists only the AI modes that are eligible for admission review. `off` is excluded because it never calls AI.
- `required_schema_contract` names the structured payload contract that must already exist before admission can succeed.
- `required_capabilities` lists the minimum capability facts a candidate subscription must satisfy.
- `candidate_subscriptions` lists alias-backed options in preferred order. These remain candidates only.
- `known_gaps` records machine-readable blockers or concerns already known before admission evaluation.

Per-candidate rules:

- `subscription_id` is the stable identifier for the candidate package or alias-backed subscription.
- `alias` is the ModelBus-facing alias key DataPulse will call if admitted.
- `capabilities` contains provider-agnostic facts such as structured output support, schema binding, operator-visible fallback, and review safety.
- `output_contracts` lists the structured contracts the candidate claims to satisfy.
- `provider_assumptions` must stay empty for this phase. If local provider assumptions are needed, the candidate is not portable enough for admission.

## Admission Fact Object

`out/governance/datapulse-ai-surface-admission.example.json` is the export of evaluated admission truth.

It records what each surface may actually use now, including rejection gaps when no candidate can be admitted.

Top-level shape:

```json
{
  "schema_version": "datapulse_ai_surface_admission.v1",
  "generated_at_utc": "2026-03-14T15:21:32Z",
  "governance_phase": "L16.5",
  "source_subscription_contract": "docs/governance/datapulse-ai-surface-subscriptions.example.json",
  "surface_admissions": []
}
```

Per-surface rules:

- `admission_status` is `admitted` when at least one candidate satisfies all mandatory checks; otherwise it is `rejected`.
- `mode_admission.off` must always be `manual_only`.
- `mode_admission.assist` and `mode_admission.review` may only be `admitted` when the surface has a structured contract and a qualifying candidate subscription.
- `candidate_results` must show the evaluated outcome for each candidate rather than hiding standby or rejected options.
- `rejectable_gaps` must stay non-empty when a surface is rejected.
- `manual_fallback` must describe the governed non-AI behavior when admission is not available.

Per-candidate evaluation rules:

1. the surface must declare a non-empty `required_schema_contract`
2. the candidate must list that contract in `output_contracts`
3. the candidate must satisfy every entry in `required_capabilities`
4. the candidate must keep `provider_assumptions` empty
5. the admitted surface must preserve operator-visible runtime facts such as alias identity, degradation, fallback, schema validation, and manual override requirement

If any rule fails, the candidate is rejected and the missing facts must be recorded.

## Admission Invariants

The following invariants must hold for `L16.5` and follow-up work:

1. candidate subscriptions are not runtime authorization
2. admission is explicit per surface instead of being inferred from provider family or brand
3. surface admission facts must be machine-readable and operator-visible
4. missing structured contracts fail closed to manual or deterministic behavior
5. admitted capabilities must stay decoupled from local provider assumptions
6. the browser may project admission facts later, but it may not invent them

## Current Phase Consequence

Given the current repo truth from `L16.4`:

- `mission_suggest`, `triage_assist`, `claim_draft`, and `delivery_summary` can be admitted if a candidate subscription satisfies the declared schema and capability requirements
- `report_draft` must remain rejected in the admission example because no admitted structured payload contract exists yet

That rejected `report_draft` state is a required truthful outcome for this slice, not a failure to land it.
