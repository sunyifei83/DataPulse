# DataPulse Working Copy Mode Draft

Status: draft only, not wired into runtime

Created: 2026-03-07

## Goal

Allow the blueprint loop to progress on a mutable plan copy without mutating the draft source plan under `docs/governance`.

## Rules

- The mutable plan copy should live under `out/` or a temp path.
- The working copy mode must refuse to edit `docs/governance/*.json`.
- The working copy is for loop progression experiments, not for repository truth.

## Scripts

Create a working copy:

```bash
python3 scripts/governance/init_datapulse_blueprint_working_copy.py
```

Advance the current next slice in a working copy:

```bash
python3 scripts/governance/advance_datapulse_blueprint_working_copy.py \
  --plan out/governance/datapulse-blueprint-plan.working.json \
  --ignore-blocking-fact workspace_dirty \
  --ignore-blocking-fact draft_not_wired \
  --allow-blocked
```

## Why This Matters

- It lets the loop mechanics mature without binding to active repository truth too early.
- It keeps blueprint progression separate from service governance rollout.
