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
- The local companion ignition path now expects a clean baseline by default; explicit dirty-worktree takeover is a supervised recovery path, not the normal blueprint-execution mode.

## Lane Ownership

- The scheduled governance entrypoint owns read-only re-evaluation from the active repo root; it may refresh `governance_snapshot_root` and `evidence_bundle_root`, but it does not own a mutable loop worktree, `out/codex_blueprint_loop/`, or any authenticated session boundary.
- The local ignition lane owns one dedicated loop worktree plus `out/codex_blueprint_loop/` as resumable round state; dirty-worktree carryover and promotion retry apply only inside that same worktree.
- Session-backed sidecars may reuse the canonical `DATAPULSE_SESSION_DIR` boundary and their own tool-local state directories, but those session or sidecar paths do not become blueprint truth, governance stop truth, or a second publish surface.

## Why This Is The Minimal Active Cutover

- It closes the repo-governance auto-continuation gap.
- It keeps execution semantics in the adapter and control semantics in the reusable core.
- It does not fold DataPulse product behavior into the reusable loop.
