# DataPulse Auto Continuation Policy

Status: active repo-governance policy

Created: 2026-03-07

## Purpose

Define the narrow repository-governance surface that closes `repo_auto_continuation_policy` without coupling the loop core to product workflows.

## Contract

- Policy truth lives in `docs/governance/datapulse-auto-continuation-policy.json`.
- Repository entrypoint lives in `.github/workflows/governance-loop-auto.yml`.
- Runtime evaluation lives in `scripts/governance/run_datapulse_auto_continuation.py`.

## Operating Rule

- When the environment is healthy, the scheduled governance entrypoint re-evaluates the active loop state without requiring manual handoff.
- When machine-decidable blockers are present, the entrypoint stops and emits governance facts instead of trying to push through them.
- The workflow remains read-only. It refreshes governance snapshots and evidence bundles, but does not invoke business service entrypoints, publish releases, or rewrite tags.

## Why This Is The Minimal Active Cutover

- It closes the repo-governance auto-continuation gap.
- It keeps execution semantics in the adapter and control semantics in the reusable core.
- It does not fold DataPulse product behavior into the reusable loop.
