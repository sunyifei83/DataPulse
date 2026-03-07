# Governance Loop Activation Intent Draft

Status: draft only, not wired into runtime

Created: 2026-03-07

## Goal

Capture the repository-owned cutover intent that sits between an activation plan and any real active wiring.

## Position In The Stack

The activation intent should remain narrower than a workflow implementation.

It should answer:

- which repo-governance surfaces are intended for cutover
- which adapter prerequisites must remain outside repo-governance
- which runtime blockers belong to the cutover window rather than the architecture layer

## Generic Exporter

The draft exporter lives here:

- `scripts/governance/export_governance_loop_activation_intent.py`

The draft verifier lives here:

- `scripts/governance/verify_governance_loop_activation_intent.py`

Example:

```bash
python3 scripts/governance/export_governance_loop_activation_intent.py \
  --bundle-dir out/governance/scaffold/exampleproject \
  --stdout
```

The next layer above this is the activation preview:

- `docs/governance/governance-loop-activation-preview.draft.md`
- `scripts/governance/export_governance_loop_activation_preview.py`

## Why This Matters

This keeps activation planning honest:

- repo-governance cutover remains explicit
- adapter-owned truth stays out of live wiring
- runtime blockers stay visible without turning into permanent architecture obligations
