# Governance Loop Adoption Verification Draft

Status: draft only, not wired into runtime

Created: 2026-03-07

## Goal

Make loop adoption verification executable rather than purely narrative.

## Verification Layers

### Layer 1: Bundle Validity

Check that:

- the manifest shape is valid
- required files exist
- the generic core can replay the bundle

Primary tool:

- `scripts/governance/validate_governance_loop_bundle_draft.py`

### Layer 2: Adapter Consistency

Check that:

- the adapter runtime output matches the bundle replay on core-comparable fields

Primary tools:

- `scripts/governance/verify_governance_loop_adoption_draft.py`
- `scripts/governance/verify_datapulse_loop_adoption_draft.py`

## Why This Matters

A repository has not really adopted the reusable loop core if:

- its bundle can replay
- but its adapter runtime says something materially different

The adoption bar should therefore be:

1. validate
2. replay
3. compare

## DataPulse Draft Reference

DataPulse now has:

- generic bundle validator
- generic adoption verifier
- DataPulse-specific adoption verifier

This is the first point where the reusable loop stack can check its own portability claim.
