# DataPulse Codex Blueprint Loop Draft

Status: local companion entrypoint

Created: 2026-03-07

## Goal

Add the missing execution half of the DataPulse loop:

1. refresh governance truth
2. detect when `next_slice` is ready
3. run a local Codex round to land only that slice
4. refresh governance truth again
5. stop or continue based on machine-readable state

## Extracted Trigger Pattern From EquityGuardian

The reusable execution pattern is not "always keep running".

It is:

1. export loop state before action
2. stop immediately if the runtime is already `blocked` or `stopped`
3. when the runtime is `ready`, invoke a local Codex round from the repository root
4. re-export loop state after the round
5. continue only while the runtime stays `ready`
6. stop on machine-decidable blockers or terminal completion

## DataPulse Adaptation

DataPulse keeps two separate entrypoints on purpose:

### 1. Scheduled Governance Refresh

- `.github/workflows/governance-loop-auto.yml`
- `scripts/governance/run_datapulse_auto_continuation.py`

This path stays read-only. It refreshes governance truth and emits whether the repo is ready, blocked, or stopped.

### 2. Local Codex Slice Execution

- `scripts/governance/run_codex_blueprint_loop.py`

This path is the mutable companion entrypoint. It is intended for a controlled local environment, not for the scheduled GitHub workflow.

The runner consumes the same machine-readable slice execution brief that the runtime exposes. If a slice has no explicit catalog entry yet, the adapter synthesizes a fallback brief from the structured blueprint slice itself, including:

- `execution_profile`
- `verification_commands`
- `artifacts` / `draft_artifacts`
- `exit_condition`

After each Codex round, the runner now enforces four control-plane checks before continuing:

1. run the current slice's `verification_commands` when declared
2. stop on `no_progress_detected` if the round leaves the slice, plan state, promotion gates, and workspace state unchanged
3. before any automatic `repo_landed` promotion, run the strict local quick gate so `lint/typecheck/console smoke` regressions are caught before commit/push instead of by remote CI
4. when `--promotion-mode auto` is enabled, first auto-resolve local `repo_landed`, then attempt the lowest-coupling `ci_proven` path that matches the current change scope:
   - non-docs changes: `git push` and wait for the real `CI` workflow run for the current `HEAD`
   - docs-only changes: `git push`, dispatch `.github/workflows/governance-evidence.yml`, and wait for that run to succeed for the current `HEAD`
5. once the loop reaches a terminal `stopped` state, refresh the tracked repository governance snapshots so `out/governance` and `out/ha_latest_release_bundle` match the live terminal truth instead of leaving only ephemeral temp outputs behind

That pre-promotion quick gate also covers the ignition-wrapper "take over an already dirty worktree" path, so operators do not need to remember a separate manual verification command before starting the local companion loop.

Recommended trigger:

```bash
bash scripts/governance/ignite_datapulse_codex_loop.sh
```

The ignition wrapper now enables `--allow-existing-dirty-worktree` by default so the local companion loop can take over `repo_landed` promotion for already-landed slice changes in the current worktree. To keep manual promotion review, run:

```bash
DATAPULSE_CODEX_ALLOW_EXISTING_DIRTY_WORKTREE=0 bash scripts/governance/ignite_datapulse_codex_loop.sh
```

Equivalent expanded command:

```bash
SYSTEM_VERSION_COMPAT=1 uv run python scripts/governance/run_codex_blueprint_loop.py \
  --model gpt-5.4 \
  --model-reasoning-effort xhigh \
  --ask-for-approval never \
  --dangerously-bypass-approvals-and-sandbox \
  --promotion-mode auto
```

## Guardrails

- The local Codex loop may mutate the repository to land the current `next_slice`.
- The scheduled governance workflow must remain read-only.
- Confirmed blueprint targets still must be declared only as structured `phase + slices + status`.
- The Codex loop should land only the current `next_slice`, unless a tightly-scoped prerequisite is unavoidable.
- After each round, governance truth must be refreshed before deciding whether to continue.
- If the slice catalog is missing an entry for the current slice, use the synthesized execution brief instead of inventing prose-only instructions.
- `--promotion-mode auto` now means "allow local repo_landed auto-promotion, then auto-resolve the current `ci_proven` path by pushing and waiting for real GitHub workflow evidence". It still does not mean release/tag autopilot.
- The local Codex loop now keeps in-round evaluation ephemeral, but on a terminal `stopped` result it refreshes the tracked governance snapshots back into the repository so local `out/` truth does not lag behind the last successful run.
- The ignition wrapper allows existing dirty worktree promotion takeover by default; set `DATAPULSE_CODEX_ALLOW_EXISTING_DIRTY_WORKTREE=0` when you want to keep a manual repo_landed review step.
- Hard-stop gates such as `workflow_dispatch_missing`, `structured_release_bundle_missing`, `ci_run_failed`, or `governance_evidence_failed` must stop the loop instead of being auto-overridden.

## Why This Matters

This closes the gap between:

- "the loop can sense that a slice is ready"

and

- "the loop can use a controlled executor to land that slice and then re-evaluate itself"
