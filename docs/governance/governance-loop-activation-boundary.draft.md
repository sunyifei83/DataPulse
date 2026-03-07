# Governance Loop Activation Boundary Draft

Status: draft only, not wired into runtime

Created: 2026-03-07

## Goal

Define the minimum activation surface between a reusable governance loop core and a repository's live workflow or service-governance paths.

## Core Distinction

The activation boundary must separate three classes of truth:

- reusable control-plane semantics
- repo-specific activation surfaces
- runtime or policy blockers

A dirty workspace or failing smoke is an operating fact. It should stop the loop, but it should not be treated as reusable-core coupling.

## Inputs

The draft activation assessor consumes:

- a validated adapter bundle
- generic bundle replay output
- adapter metadata from the bundle manifest

## Outputs

The assessor should expose:

- open activation surfaces
- operating blockers that should stay runtime facts
- a minimal activation sequence
- whether the bundle is ready to discuss active wiring at all

That assessment can then be promoted into a machine-readable activation plan.

See:

- `docs/governance/governance-loop-activation-plan.draft.md`
- `scripts/governance/export_governance_loop_activation_plan.py`

## Generic Assessor

The draft assessor lives here:

- `scripts/governance/assess_governance_loop_activation_draft.py`

Example:

```bash
python3 scripts/governance/assess_governance_loop_activation_draft.py \
  --bundle-dir out/governance/scaffold/exampleproject
```

## Surface Classes

### Project Adapter Surfaces

- repo truth exporter
- CI truth exporter
- strict verification contracts
- project-specific release evidence contracts

### Repository Governance Surfaces

- active loop entrypoint wiring
- auto-continuation policy
- workflow-dispatch or scheduler entrypoint

### Runtime Or Policy Blockers

- dirty workspace
- failing local or remote evidence
- emergency stop
- CI policy facts such as docs-only skip

## Why This Matters

This is the missing layer between:

- a portable replay kit

and

- a low-coupling activation plan that can turn the loop into a trusted delivery pipeline
