# DataPulse HA Recovery Replay Draft

Status: draft only, manual-only

Created: 2026-03-07

## Goal

Replay the currently selected HA recovery preset through the existing remote smoke entrypoint, then immediately close the evidence loop by regenerating emergency state and HA facts.

## Draft Wrapper

The wrapper lives here:

- `scripts/governance/run_datapulse_ha_recovery_replay.py`

Example:

```bash
python3 scripts/governance/run_datapulse_ha_recovery_replay.py --json
python3 scripts/governance/run_datapulse_ha_recovery_replay.py --execute --json
```

## Execution Rules

- Default mode is dry-run.
- Actual replay only happens with explicit `--execute`.
- The wrapper uses the currently selected recovery preset and refuses unsupported routes.
- The wrapper also carries forward the current catalog match so replay remains tied to a named preset contract when available.
- After replay it regenerates `emergency_state.json` for the new run and recomputes HA facts in memory.

## Non-Impact Rules

- No existing workflow, CLI, or smoke script is changed.
- This wrapper is manual-only and opt-in.
- Governance snapshot writes remain opt-in via `--write-governance-snapshots`.

## Why This Matters

This is the first draft wrapper that turns HA diagnosis, recovery preset, replay, and post-replay fact refresh into one explicit loop step.
