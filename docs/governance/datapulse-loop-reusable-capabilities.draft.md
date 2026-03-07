# DataPulse Loop Reusable Capabilities Draft

Status: draft only, not wired into runtime

Created: 2026-03-07

## Goal

Extract the parts of the EquityGuardian loop that are truly reusable in DataPulse without copying project-specific semantics or coupling the loop to DataPulse service governance.

## What EquityGuardian Actually Proved

The most reusable result is not that a script ran to completion.

The reusable result is that the loop already proved four control-plane abilities in one closed circuit:

1. progress truth is machine-readable
2. stop truth is machine-readable
3. promotion evidence is re-ingested after action
4. complete state is an expected terminal stop, not an ambiguous idle state

That is why the meaningful reusable unit is not a single file. It is a closed-loop control model.

## Reusable Capability Stack

### 1. Progress Truth

The loop must always be able to answer:

- what is the current level
- what is the next slice
- whether the next slice is a real work slice, a promotion slice, or complete

Reusable form in DataPulse:

- `blueprint_plan.v1`
- `project_specific_loop_state.v1`
- next-open-slice selection

### 2. Stop Truth

The loop must always be able to answer:

- why it is blocked
- whether the stop is expected or abnormal
- whether the blocker is machine-decidable

Reusable form in DataPulse:

- `blocking_facts`
- `remaining_promotion_gates`
- `flow_control`
- gateable verification wrappers

### 3. Reopen Truth

The loop must always be able to answer what facts re-open progression after an expected stop.

Reusable trigger classes:

- a new open slice is added to the blueprint plan
- workspace or repo changes re-open repo-level promotion
- CI or release evidence regression re-opens promotion gates

Without reopen truth, completion is only a snapshot. With reopen truth, completion becomes a stable operating state.

### 4. Evidence Round-Trip

A promotion step is not complete when an action is fired.

It is complete only when evidence is pulled back into repo-local truth and state is re-exported.

Reusable form in DataPulse:

- export state before action
- execute promotion or slice
- collect workflow or release evidence
- re-export landing status and loop state
- continue or stop

### 5. Expected Terminal Stop

The loop must distinguish:

- blocked because something is wrong
- waiting because manual handoff is still configured
- stopped because the blueprint is complete and promotion gates are closed

This is the semantic upgrade from "runner" to "pipeline."

## Core Versus Adapter

What should be reusable as core:

- plan schema
- landing status schema
- loop state schema
- multi-round driver skeleton
- promotion executor skeleton
- projection sync skeleton
- terminal stop and reopen semantics
- control-plane evaluator implementation

What must stay in the project adapter:

- slice definitions
- verification commands
- workflow names and evidence paths
- release policy
- projection targets
- product or governance verdict wording

## DataPulse Landing Boundary

DataPulse already has draft coverage for most of the control-plane skeleton:

- progress truth: drafted
- stop truth: drafted
- reopen truth: drafted as contract
- evidence round-trip: drafted, not yet wired
- expected terminal stop: drafted, not yet active

What is still missing for real reuse:

1. an active evidence workflow path that the driver can trigger and watch
2. a structured sidecar or bundle that the driver can re-ingest
3. one authoritative release policy instead of split release paths
4. activation from manual draft mode into real repo truth

## First Concrete Extraction In This Repo

The first repo-local extraction of that reusable layer now lives in:

- `scripts/governance/loop_core_draft.py`
- `docs/governance/governance-loop-core-contract.draft.md`
- `scripts/governance/run_governance_loop_core_draft.py`
- `scripts/governance/datapulse_loop_adapter_draft.py`
- `docs/governance/loop-project-adapter-contract.draft.md`
- `scripts/governance/export_datapulse_loop_adapter_bundle.py`
- `scripts/governance/run_governance_loop_bundle_draft.py`
- `docs/governance/loop-adapter-bundle-contract.draft.md`
- `scripts/governance/validate_governance_loop_bundle_draft.py`
- `docs/governance/governance-loop-adoption-playbook.draft.md`

That matters because the DataPulse adapter can now shrink toward:

- landing-status collection
- slice catalog and slice profiles
- workflow and evidence mapping

while the reusable control-plane semantics move into one repo-agnostic draft module.

## Higher-Level Conclusion

The reusable capability is not "copy EquityGuardian loop."

The reusable capability is:

1. a blueprint-first control plane
2. machine-decidable stop semantics
3. evidence round-trip after promotion
4. expected terminal stop with machine-decidable reopen triggers

That is the correct abstraction level for DataPulse.
