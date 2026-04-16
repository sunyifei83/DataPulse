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

## Shared Instruction Plane

DataPulse now names one shared instruction chain for repo-native execution:

1. `AGENTS.md` is the canonical repo-root instruction plane for agent runtimes and repo-native handoff docs.
2. `CLAUDE.md` is a thin Claude-compatible entrypoint that extends `AGENTS.md` instead of duplicating it.
3. Governance-loop startup reads `AGENTS.md` first and then this document for loop-specific execution behavior.

Future Claude-specific entrypoints must extend `CLAUDE.md` and `AGENTS.md` rather than maintaining a parallel constitutional copy. Loop prompts and operator handoffs should cite the same chain instead of restating policy in prose.

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

The `L20.2` contract freezes three resolver-owned roots that later implementation slices must honor without changing the wrapper commands:

- `runtime_bundle_root`: `config/modelbus/datapulse/`
- `governance_snapshot_root`: `artifacts/governance/snapshots/`
- `evidence_bundle_root`: `artifacts/governance/release_bundle/`

Legacy `out/governance`, `out/release_bundle`, and `out/ha_latest_release_bundle` remain read-fallbacks during migration, but closeout refresh now targets the canonical resolver roots instead of treating those `out/*` directories as permanent tracked truth.

After each Codex round, the runner now enforces six control-plane checks before continuing:

1. run the current slice's `verification_commands` when declared
2. stop on `no_progress_detected` if the round leaves the slice, plan state, promotion gates, and workspace state unchanged
3. when a round closes on a `workspace_dirty`-only `repo_landed` boundary, first try to auto-settle that dirty worktree by running the strict local quick gate before any commit so `lint/typecheck/console smoke` regressions are caught before commit/push instead of by remote CI
4. if that dirty-worktree auto-settle keeps failing on the same round boundary, keep retrying up to `--dirty-worktree-settle-max-attempts`; once the retry budget is exhausted, the default ignition path falls back to dirty-worktree carryover so the next round can keep running without manual intervention. Use `--no-allow-existing-dirty-worktree` to keep the old strict-stop behavior after the retry budget is exhausted.
5. when `--promotion-mode auto` is enabled, first auto-resolve local `repo_landed`, then attempt the lowest-coupling `ci_proven` path that matches the current change scope:
   - non-docs changes: `git push` and wait for the real `CI` workflow run for the current `HEAD`
   - docs-only changes: `git push`, dispatch `.github/workflows/governance-evidence.yml`, and wait for that run to succeed for the current `HEAD`
6. once the loop reaches a terminal `stopped` state, refresh the resolved governance snapshot and evidence-bundle roots for the current repository contract; canonical closeout now lands in `artifacts/governance/snapshots/` and `artifacts/governance/release_bundle/`, while legacy `out/*` roots remain compatibility fallbacks only

That dirty-worktree auto-settle path only applies when the runtime is already on a `repo_landed` candidate boundary. The loop does not synthesize checkpoint commits for unfinished slices just to force a clean worktree, because that would blur slice-completion truth.

The local loop log directory `out/codex_blueprint_loop/` is also treated as ignored operational output so blueprint-only or closeout-only runs do not reopen the repository by themselves.

## Execution Lane Ownership

DataPulse now treats `repo x worktree x session x output_root` as an explicit lane contract rather than operator memory:

| Lane | Repo ownership | Worktree ownership | Session ownership | Output-root ownership | Resume contract |
| --- | --- | --- | --- | --- | --- |
| Scheduled governance refresh | Runs against the active repo truth at `docs/governance/datapulse-blueprint-plan.json`; it does not land business slices. | The workflow checkout is read-only for governance purposes and must not become a mutable loop worktree. | None. This lane must not depend on browser login state or sidecar-only session files. | May refresh `governance_snapshot_root` and `evidence_bundle_root` through exporters; it does not own `out/codex_blueprint_loop/`. | Re-run `scripts/governance/run_datapulse_auto_continuation.py` from the same repo root and stop on machine-decided `blocked` or `stopped` truth. |
| Local Codex blueprint loop | Uses the same active repo truth and may mutate the current `next_slice` only. | One dedicated, machine-exclusive loop worktree owns the mutable round state. Dirty-worktree carryover, auto-settle retries, and promotion retries are scoped to that same worktree only. | The loop has no private credential store. When a slice uses authenticated collectors or sidecars, it may only reuse the existing shared `DATAPULSE_SESSION_DIR` boundary; session files are not stored under the loop output directory. | `out/codex_blueprint_loop/` owns prompts, last-message captures, and promotion-auto-repair checkpoints; tracked closeout writes still go through `governance_snapshot_root` and `evidence_bundle_root`, while `runtime_bundle_root` remains a resolver input rather than round scratch space. | Resume from the same repo worktree plus refreshed governance snapshots and the existing `out/codex_blueprint_loop/` state. `workspace_dirty` carryover is admissible only on the same `repo_landed` boundary and must not be reinterpreted as a clean baseline or a second publish lane. |
| Local sidecar execution | The repo checkout remains the only blueprint and governance truth even when a helper sidecar uses its own checkout or runtime files. | A sidecar may use `DATAPULSE_NATIVE_COLLECTOR_BRIDGE_WORKDIR` or another tool-local working directory, but that directory is sidecar-owned runtime state, not an alternate blueprint worktree. | Shared authenticated session files live under `DATAPULSE_SESSION_DIR`; sidecar-local cookies, API keys, or secret stores remain outside the repo contract and must not be promoted into governance truth. | Sidecar scratch/state belongs in `DATAPULSE_NATIVE_COLLECTOR_STATE_DIR` or tool-local outputs. Any repo-governance export still resolves through the canonical snapshot and evidence roots instead of inventing a sidecar bundle root. | Resume by reusing the same repo checkout, sidecar workdir, and declared session boundary; clearing a missing-session or dirty-worktree blocker must not require reconstructing lane ownership from memory alone. |

Recommended trigger:

```bash
bash scripts/governance/ignite_datapulse_codex_loop.sh
```

The ignition wrapper now assumes a dedicated, machine-exclusive loop worktree. By default it enables dirty-worktree carryover fallback only after the auto-settle retry budget is exhausted:

```bash
bash scripts/governance/ignite_datapulse_codex_loop.sh
```

Tune the retry budget when you want the loop to spend longer trying to auto-clean the round boundary before it falls back:

```bash
DATAPULSE_CODEX_DIRTY_WORKTREE_SETTLE_MAX_ATTEMPTS=5 bash scripts/governance/ignite_datapulse_codex_loop.sh
```

Disable dirty-worktree carryover fallback only when you intentionally want strict clean-baseline supervision:

```bash
DATAPULSE_CODEX_ALLOW_EXISTING_DIRTY_WORKTREE=0 bash scripts/governance/ignite_datapulse_codex_loop.sh
```

Equivalent expanded command:

```bash
SYSTEM_VERSION_COMPAT=1 uv run python scripts/governance/run_codex_blueprint_loop.py \
  --model gpt-5.4 \
  --model-reasoning-effort high \
  --ask-for-approval never \
  --sandbox danger-full-access \
  --continue-through-promotions \
  --promotion-mode auto \
  --push-remote origin \
  --release-tag-label loop
```

## Guardrails

- The local Codex loop may mutate the repository to land the current `next_slice`.
- Loop startup must stay on the shared instruction chain: `AGENTS.md` -> `CLAUDE.md` when a Claude-compatible runtime is present -> `docs/governance/datapulse-codex-blueprint-loop.draft.md`.
- The scheduled governance workflow must remain read-only.
- Confirmed blueprint targets still must be declared only as structured `phase + slices + status`.
- The Codex loop should land only the current `next_slice`, unless a tightly-scoped prerequisite is unavoidable.
- After each round, governance truth must be refreshed before deciding whether to continue.
- If the slice catalog is missing an entry for the current slice, use the synthesized execution brief instead of inventing prose-only instructions.
- `--promotion-mode auto` now means "allow local repo_landed auto-promotion, then auto-resolve the current `ci_proven` path by pushing and waiting for real GitHub workflow evidence". It still does not mean release/tag autopilot.
- Worktree, session, and output-root ownership stay lane-scoped: the scheduled workflow stays read-only, sidecar state stays sidecar-local, and only repo-native plan truth may advance `next_slice`.
- Dirty-worktree auto-settle is limited to `repo_landed` candidate boundaries; it must not manufacture checkpoint commits for an unfinished slice solely to make the worktree look clean.
- The local Codex loop now keeps in-round evaluation ephemeral, but on a terminal `stopped` result it refreshes the resolver-addressed governance and evidence outputs so local truth does not lag behind the last successful run.
- Legacy `out/governance` and `out/*release_bundle*` directories are no longer required tracked stop-truth surfaces; they are ignored compatibility fallbacks.
- The ignition wrapper now defaults to auto-settle retries plus dirty-worktree carryover fallback; use `DATAPULSE_CODEX_ALLOW_EXISTING_DIRTY_WORKTREE=0` only when you intentionally want the old strict stop after the retry budget is exhausted.
- Hard-stop gates such as `workflow_dispatch_missing`, `structured_release_bundle_missing`, `ci_run_failed`, or `governance_evidence_failed` must stop the loop instead of being auto-overridden.

## Why This Matters

This closes the gap between:

- "the loop can sense that a slice is ready"

and

- "the loop can use a controlled executor to land that slice and then re-evaluate itself"
