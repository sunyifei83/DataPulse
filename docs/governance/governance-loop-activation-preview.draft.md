# Governance Loop Activation Preview Draft

Status: draft only, not wired into runtime

Created: 2026-03-07

## Goal

Preview what would remain open after repo-governance cutover if the current activation intent were implemented as declared.

## Position In The Stack

The activation preview sits above:

- activation plan
- activation intent

It should answer:

- whether the remaining open items after cutover are still architectural or only runtime
- whether repo-governance cutover is blocked by adapter prerequisites
- whether the trusted-pipeline bar would still fail because of runtime facts

## Generic Exporter

The draft exporter lives here:

- `scripts/governance/export_governance_loop_activation_preview.py`

The draft verifier lives here:

- `scripts/governance/verify_governance_loop_activation_preview.py`

Example:

```bash
python3 scripts/governance/export_governance_loop_activation_preview.py \
  --bundle-dir out/governance/scaffold/exampleproject \
  --stdout
```

## Why This Matters

This is the last non-invasive planning layer before any active wiring:

- it keeps repo-governance cutover explicit
- it shows which blockers would still remain after cutover
- it prevents conflating repo wiring work with runtime stabilization work
