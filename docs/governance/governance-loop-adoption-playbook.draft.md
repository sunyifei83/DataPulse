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

### Layer 4: Reuse Kit

Export the repo-agnostic assets as a portable kit:

- generic scripts
- generic contracts
- scaffold generator
- verifier chain

## Minimum Adoption Sequence

1. define a machine-readable blueprint plan
2. export a landing-status snapshot
3. map slice profiles to blocking gate groups
4. export an adapter bundle
5. validate the bundle with the generic validator
6. compare adapter runtime output with bundle replay
7. replay the bundle through the generic core
8. assess the activation boundary and separate missing wiring from runtime blockers
9. export a machine-readable activation plan
10. export and verify a machine-readable activation intent
11. export and verify an activation preview
12. only then consider active workflow wiring

## DataPulse Draft Reference

Current draft reference points:

- core contract: `docs/governance/governance-loop-core-contract.draft.md`
- adapter contract: `docs/governance/loop-project-adapter-contract.draft.md`
- bundle contract: `docs/governance/loop-adapter-bundle-contract.draft.md`
- bundle validator: `scripts/governance/validate_governance_loop_bundle_draft.py`
- adoption verifier: `scripts/governance/verify_governance_loop_adoption_draft.py`
- DataPulse verifier: `scripts/governance/verify_datapulse_loop_adoption_draft.py`
- scaffold generator: `scripts/governance/init_governance_loop_project_scaffold.py`
- scaffold guide: `docs/governance/governance-loop-project-scaffold.draft.md`
- verification guide: `docs/governance/governance-loop-adoption-verification.draft.md`
- activation-boundary guide: `docs/governance/governance-loop-activation-boundary.draft.md`
- activation-plan guide: `docs/governance/governance-loop-activation-plan.draft.md`
- activation-intent guide: `docs/governance/governance-loop-activation-intent.draft.md`
- activation-preview guide: `docs/governance/governance-loop-activation-preview.draft.md`
- reuse kit exporter: `scripts/governance/export_governance_loop_reuse_kit.py`
- reuse kit verifier: `scripts/governance/verify_governance_loop_reuse_kit.py`
- activation-boundary assessor: `scripts/governance/assess_governance_loop_activation_draft.py`
- activation-plan exporter: `scripts/governance/export_governance_loop_activation_plan.py`
- activation-intent exporter: `scripts/governance/export_governance_loop_activation_intent.py`
- activation-intent verifier: `scripts/governance/verify_governance_loop_activation_intent.py`
- activation-preview exporter: `scripts/governance/export_governance_loop_activation_preview.py`
- activation-preview verifier: `scripts/governance/verify_governance_loop_activation_preview.py`
- reuse kit guide: `docs/governance/governance-loop-reuse-kit.draft.md`

## Acceptance Bar For A New Repository

A new repository should not claim loop reuse just because it copied a driver.

It should meet all of these:

1. the bundle validates
2. the generic core can replay the bundle
3. the replay exposes machine-decidable blockers
4. terminal stop and reopen semantics are present in state output
5. repository-specific commands remain in the adapter, not in the core
6. a fresh scaffold can be generated and then replaced incrementally by project truth
7. adapter runtime output and bundle replay remain consistent
8. activation surfaces are explicit before any active wiring begins
9. activation cutover is described as a machine-readable plan instead of only prose guidance
10. repo-governance cutover intent stays aligned with the activation plan
11. the projected post-cutover state is explicit before live wiring begins

## Why This Matters

This is the difference between:

- "we ported a script"

and

- "we adopted a reusable governance control plane"
