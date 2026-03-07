# Governance Loop Reuse Kit Draft

Status: draft only, not wired into runtime

Created: 2026-03-07

## Goal

Package the repo-agnostic governance loop pieces into a movable kit that another repository can copy without bringing over DataPulse-specific adapters.

## Kit Contents

The kit should include:

- generic core scripts
- generic bundle scripts
- generic validator and verifier scripts
- generic activation-boundary assessor
- generic activation-plan exporter
- generic activation-intent exporter and verifier
- generic activation-preview exporter and verifier
- scaffold generator
- core and adoption contracts

## Export Tool

The kit exporter lives here:

- `scripts/governance/export_governance_loop_reuse_kit.py`

The kit verifier lives here:

- `scripts/governance/verify_governance_loop_reuse_kit.py`

The activation-boundary assessor lives here:

- `scripts/governance/assess_governance_loop_activation_draft.py`

The activation-boundary guide lives here:

- `docs/governance/governance-loop-activation-boundary.draft.md`

The activation-plan exporter lives here:

- `scripts/governance/export_governance_loop_activation_plan.py`

The activation-plan guide lives here:

- `docs/governance/governance-loop-activation-plan.draft.md`

The activation-intent exporter lives here:

- `scripts/governance/export_governance_loop_activation_intent.py`

The activation-intent verifier lives here:

- `scripts/governance/verify_governance_loop_activation_intent.py`

The activation-intent guide lives here:

- `docs/governance/governance-loop-activation-intent.draft.md`

The activation-preview exporter lives here:

- `scripts/governance/export_governance_loop_activation_preview.py`

The activation-preview verifier lives here:

- `scripts/governance/verify_governance_loop_activation_preview.py`

The activation-preview guide lives here:

- `docs/governance/governance-loop-activation-preview.draft.md`

## Expected Flow

The reusable kit should support this order:

1. generate a starter scaffold
2. validate the bundle
3. replay the bundle through the generic core
4. compare or verify the adapter-facing view
5. assess the activation boundary
6. export the activation plan
7. export and verify the activation intent
8. export and verify the activation preview

Only after that should a repository discuss active workflow wiring.

## Why This Matters

This is the first point where the reusable governance loop can be treated as:

- a portable asset
- a portable activation-planning asset

instead of only:

- a pattern documented inside DataPulse
