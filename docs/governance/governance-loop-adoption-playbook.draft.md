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

### Layer 3.5: Typed Local-First Resource Plane

Project adapters may also project a typed local-first resource plane for agents and operators.

This plane is still adapter-owned. It exists to make current truth, blocking reasons, and slice handoffs consumable without forcing downstream consumers to scrape arbitrary files or prompt prose.

Minimum reusable resource kinds:

| Resource kind | Backing source | Required payload focus | Must not claim |
| --- | --- | --- | --- |
| `governance.plan_snapshot.v1` | blueprint plan plus resolved overlay when present | current phase tree, slice statuses, recommended next slice, activation shell | loop readiness by itself |
| `governance.current_truth.v1` | resolved plan plus project loop state plus landing status | `current_level`, `next_slice`, `status_if_run_now`, `reason_if_run_now`, workspace and promotion headline facts | final release truth or lifecycle admission |
| `governance.blocking_reasons.v1` | project loop state plus landing-status promotion reasons | `blocking_facts`, remaining promotion gates, unsatisfied reasons, freshness or source refs | that metadata is trusted without schema-plus-policy validation |
| `governance.execution_handoff.v1` | current slice brief plus local execution sidecar refs plus adapter bundle refs | slice id, execution profile, verification commands, artifact targets, lane refs, replay pointers | a new public API surface or a second control plane |
| `governance.resource_index.v1` | local manifest over the resource files above | stable ids, local paths, resource kinds, generated timestamps | that discovery metadata replaces the underlying source files |

Recommended envelope for each resource:

```json
{
  "schema_version": "governance.resource_envelope.v1",
  "resource_id": "datapulse.current_truth",
  "resource_kind": "governance.current_truth.v1",
  "generated_at_utc": "2026-04-15T12:24:25Z",
  "truth_mode": "typed_projection",
  "backing_paths": [
    "docs/governance/datapulse-blueprint-plan.json",
    "artifacts/governance/snapshots/project_specific_loop_state.draft.json"
  ],
  "trust_boundary": {
    "projection_is_not_final_truth": true,
    "tool_and_mcp_outputs_untrusted_until_validated": true
  },
  "payload": {}
}
```

Contract rules:

- local-first means the authoritative lookup path is a repo path or generated local snapshot first; remote MCP mirrors are optional follow-on projections, not the baseline contract
- typed resources may summarize or join existing machine-readable files, but they must keep source references so an operator can trace back to the governing file
- the resource plane may improve agent consumption and handoff continuity, but it does not upgrade metadata into trusted fact truth by itself
- execution handoff resources must keep repo/worktree/session ownership explicit so worktree parallelism is not mistaken for publish-lane parallelism
- current truth and blocking resources are valid only for the recorded generation window and should be regenerated after slice execution or promotion-relevant changes

### Layer 4: Reuse Kit

Export the repo-agnostic assets as a portable kit:

- generic scripts
- generic contracts
- scaffold generator
- verifier chain

## Minimum Adoption Sequence

1. define a machine-readable blueprint plan using only `phases[].slices[].status` for confirmed loop targets
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

The blueprint plan must not treat prose such as "Future Track" or any `future_*` field as a non-open planning bucket. If the repository wants the loop to recognize a target, that target must be declared as a structured slice with an explicit status.

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
8. typed local-first resources can expose current truth, blocking reasons, and execution handoffs without inventing a new public API
9. activation surfaces are explicit before any active wiring begins
10. activation cutover is described as a machine-readable plan instead of only prose guidance
11. repo-governance cutover intent stays aligned with the activation plan
12. the projected post-cutover state is explicit before live wiring begins

## Why This Matters

This is the difference between:

- "we ported a script"

and

- "we adopted a reusable governance control plane"
