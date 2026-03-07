# Governance Loop Adoption Playbook Draft

Status: draft only, not wired into runtime

Created: 2026-03-07

## Goal

Provide a practical landing path for bringing the reusable governance loop into another repository without copying DataPulse-specific logic.

## Three-Layer Adoption Model

### Layer 1: Core

Keep the reusable control plane:

- `loop_core_draft.py`
- `run_governance_loop_core_draft.py`
- `run_governance_loop_bundle_draft.py`

This layer owns:

- next-slice evaluation
- blocking-fact evaluation
- flow-control semantics
- terminal stop semantics
- trust and reuse summaries

### Layer 2: Project Adapter

Implement repository-specific collection and mapping:

- plan loading
- landing-status collection
- slice catalog loading
- project-specific execution hints

This layer owns facts, not control semantics.

### Layer 3: Adapter Bundle

Export the adapter bundle as the stable handoff:

- plan snapshot
- landing-status snapshot
- optional slice catalog
- bundle manifest

This layer makes replay and validation possible without importing the project adapter.

## Minimum Adoption Sequence

1. define a machine-readable blueprint plan
2. export a landing-status snapshot
3. map slice profiles to blocking gate groups
4. export an adapter bundle
5. validate the bundle with the generic validator
6. replay the bundle through the generic core
7. only then consider active workflow wiring

## DataPulse Draft Reference

Current draft reference points:

- core contract: `docs/governance/governance-loop-core-contract.draft.md`
- adapter contract: `docs/governance/loop-project-adapter-contract.draft.md`
- bundle contract: `docs/governance/loop-adapter-bundle-contract.draft.md`
- bundle validator: `scripts/governance/validate_governance_loop_bundle_draft.py`

## Acceptance Bar For A New Repository

A new repository should not claim loop reuse just because it copied a driver.

It should meet all of these:

1. the bundle validates
2. the generic core can replay the bundle
3. the replay exposes machine-decidable blockers
4. terminal stop and reopen semantics are present in state output
5. repository-specific commands remain in the adapter, not in the core

## Why This Matters

This is the difference between:

- "we ported a script"

and

- "we adopted a reusable governance control plane"
