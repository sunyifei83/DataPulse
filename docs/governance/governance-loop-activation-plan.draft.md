# Governance Loop Activation Plan Draft

Status: draft only, not wired into runtime

Created: 2026-03-07

## Goal

Turn activation-boundary assessment into a machine-readable cutover plan without directly modifying any live repository workflow.

## Position In The Stack

The activation plan sits one layer above:

- generic core replay
- activation-boundary assessment

It should answer:

- what must be completed in the project adapter first
- what can remain deferred to repo-governance cutover
- which blockers are runtime facts rather than architecture work

## Generic Exporter

The draft exporter lives here:

- `scripts/governance/export_governance_loop_activation_plan.py`

Example:

```bash
python3 scripts/governance/export_governance_loop_activation_plan.py \
  --bundle-dir out/governance/scaffold/exampleproject \
  --stdout
```

## Expected Tracks

The exported plan should split work into three tracks:

1. project-adapter completion
2. repo-governance cutover
3. runtime cutover window

This keeps the reusable core decoupled from:

- repository-specific truth exporters
- active workflow entrypoints
- runtime blocker handling

The next layer above this is the activation intent:

- `docs/governance/governance-loop-activation-intent.draft.md`
- `scripts/governance/export_governance_loop_activation_intent.py`

## Why This Matters

This is how the reusable loop stops being only:

- a replay kit

and becomes:

- a low-coupling activation-planning system
