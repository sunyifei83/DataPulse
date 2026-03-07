# Governance Loop Project Scaffold Draft

Status: draft only, not wired into runtime

Created: 2026-03-07

## Goal

Provide a starter scaffold that a new repository can generate before it has a real adapter implementation.

## Generated Files

The scaffold generator should produce:

- `adapter_bundle_manifest.draft.json`
- `blueprint_plan.snapshot.json`
- `code_landing_status.snapshot.json`
- `slice_adapter_catalog.snapshot.json`
- `ADOPTION_NEXT_STEPS.md`

## Properties

The scaffold should already be:

1. bundle-shaped
2. validator-compatible
3. replayable by the generic core
4. explicit about what must be replaced by project-specific truth

## DataPulse Draft Landing

The generator lives here:

- `scripts/governance/init_governance_loop_project_scaffold.py`

Example:

```bash
python3 scripts/governance/init_governance_loop_project_scaffold.py \
  --project ExampleProject \
  --out-dir out/governance/scaffold
```

Then validate and replay:

```bash
python3 scripts/governance/validate_governance_loop_bundle_draft.py \
  --bundle-dir out/governance/scaffold/exampleproject

python3 scripts/governance/run_governance_loop_bundle_draft.py \
  --bundle-dir out/governance/scaffold/exampleproject
```

## Why This Matters

This makes the first adoption step operational:

- generate
- validate
- replay

before any repository-specific runtime wiring begins.
