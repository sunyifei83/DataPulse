# Governance Loop Core Contract Draft

Status: draft only, not wired into runtime

Created: 2026-03-07

## Goal

Define the minimum repo-agnostic control-plane contract that can be reused across repositories without copying project-specific workflow semantics.

## Core Boundary

The core should know only these things:

1. blueprint plan structure
2. landing-status structure
3. next-slice selection
4. blocking fact derivation from slice profiles
5. flow-control semantics
6. terminal stop and reopen semantics

The core should not know:

- project verification commands
- project workflow names
- project release verdict wording
- project markdown projections
- project HA or product semantics

## Canonical Inputs

### Input 1: blueprint plan

Required fields:

- `activation`
- `slice_profiles`
- `phases[].slices[]`

### Input 2: landing status

Required fields:

- `workspace.clean`
- `gate_groups`
- `promotion_levels`

## Canonical Outputs

### Output 1: project loop state

The core must be able to derive:

- `current_level`
- `next_slice`
- `remaining_promotion_gates`
- `blocking_facts`
- `flow_control`
- `control_contract`

### Output 2: runtime summaries

The core may additionally derive:

- trusted-pipeline summary
- reusable-capability summary
- ready/blocked/stopped status

## Expected Semantics

### Continue

When the environment is healthy and the loop is activated, the core should classify the state as ready for auto-advance.

### Block

When slice-relevant blockers exist, the core should classify the state as blocked, with machine-decidable blocker facts.

### Terminal Stop

When `next_slice=no-open-slice`, the core should distinguish:

- `loop_complete`
- `promotion_gates_open`

### Reopen

The core should carry machine-decidable reopen triggers, at minimum:

- new open slice added
- workspace or repo change reopens repo promotion
- CI or release evidence regression reopens promotion gates

## First Draft Landing In DataPulse

The first extracted core lives here:

- `scripts/governance/loop_core_draft.py`
- `scripts/governance/run_governance_loop_core_draft.py`
- `scripts/governance/run_governance_loop_bundle_draft.py`
- `scripts/governance/validate_governance_loop_bundle_draft.py`

The current DataPulse-specific adapter remains responsible for:

- collecting landing status from git, artifacts, CI policy, and release policy
- defining slice profiles and slice content
- mapping slices to commands and artifacts

The project-side adapter contract is documented here:

- `docs/governance/loop-project-adapter-contract.draft.md`
- `docs/governance/loop-adapter-bundle-contract.draft.md`
- `docs/governance/governance-loop-adoption-playbook.draft.md`

## Why This Matters

This is the concrete line between:

- "we copied EquityGuardian scripts"
- and
- "we extracted a reusable governance loop core with a project adapter"
