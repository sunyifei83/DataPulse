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
- `templates/scripts/governance/<project>_loop_adapter.py`
- `templates/scripts/governance/export_<project>_loop_adapter_bundle.py`

## Properties

The scaffold should already be:

1. bundle-shaped
2. validator-compatible
3. replayable by the generic core
4. explicit about what must be replaced by project-specific truth
5. equipped with starter adapter and bundle-exporter templates
6. free of prose-only future buckets such as `future_*` or "Future Track"

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

python3 scripts/governance/verify_governance_loop_adoption_draft.py \
  --bundle-dir out/governance/scaffold/exampleproject

python3 scripts/governance/run_governance_loop_bundle_draft.py \
  --bundle-dir out/governance/scaffold/exampleproject

python3 scripts/governance/assess_governance_loop_activation_draft.py \
  --bundle-dir out/governance/scaffold/exampleproject

python3 scripts/governance/export_governance_loop_activation_plan.py \
  --bundle-dir out/governance/scaffold/exampleproject \
  --stdout

python3 scripts/governance/export_governance_loop_activation_intent.py \
  --bundle-dir out/governance/scaffold/exampleproject \
  --stdout

python3 scripts/governance/export_governance_loop_activation_preview.py \
  --bundle-dir out/governance/scaffold/exampleproject \
  --stdout
```

## Why This Matters

This makes the first adoption step operational:

- generate
- validate
- replay
- assess activation boundary
- export activation plan
- export activation intent
- export activation preview

before any repository-specific runtime wiring begins.
