# DataPulse Loop Decoupling Principles Draft

Status: draft only, not wired into runtime

Created: 2026-03-07

## Goal

Keep the loop focused on automatic blueprint-plan progression while minimizing coupling to DataPulse feature behavior and service governance.

## Continuity Principle

The loop does not need to run forever to be considered "non-stop" in the useful sense.

What matters is this:

1. when the environment is healthy, the loop can continue slice progression without human relay
2. when the environment is abnormal, the loop stops on machine-decidable blockers instead of waiting for human interpretation

If either side is missing, the loop is still an operator aid. Only when both sides exist does it become a trustworthy delivery path.

## Core Principle

The loop should treat repository functionality, runtime HA, CI, and release governance as evidence providers, not as the loop's primary domain model.

The primary domain model should stay:

1. blueprint slices
2. slice status
3. next-slice selection
4. slice-specific verification profile
5. promotion scope only when required

## Coupling Rules

### Rule 1: No Global Service Gate For Every Slice

- A slice should only depend on the evidence required by its own execution profile.
- Remote HA and release evidence must not block plan-only or local-wrapper slices.

### Rule 2: Separate Execution Blockers From Open Promotion Gaps

- `open_gates` can remain global facts.
- `blocking_facts` should only describe what prevents the current next slice from being executed safely.

### Rule 3: Keep Slice Profiles Small

Recommended slice profiles:

- `draft_only`
- `local_wrapper`
- `workflow_change`
- `release_policy_change`
- `runtime_validation`

The profile should decide which evidence scopes are relevant.

### Rule 4: Service Governance Is A Plugin Layer

- local smoke
- remote HA smoke
- emergency gate
- CI policy
- release sidecar

These should be consumed through adapter lookups, not hardcoded as universal loop truth.

### Rule 5: Promotion Scope Must Be Explicit

- `none`
- `repo`
- `ci`
- `release`

Do not assume every slice eventually needs `release`.

### Rule 6: Stop And Reopen Semantics Must Be First-Class

- expected terminal stop must be machine-readable
- reopen triggers must be machine-decidable
- evidence round-trip must happen before a promotion step is considered complete

Do not treat completion as "nothing more happened." Treat it as a stable control state that can be re-opened by specific facts.

## Trusted Pipeline Bar

The loop should be treated as a trusted delivery pipeline only when all of the following are true:

1. next-slice continuation is machine-triggerable under healthy conditions
2. blocker detection is machine-decidable under abnormal conditions
3. the loop can explain why it stopped in contract form, not only in human narrative
4. resume is possible by clearing blockers or changing the next slice, without reinterpreting the whole repo manually

This is why L1-L4 matter structurally:

- L1 converts report-style commands into gateable stop signals
- L2 externalizes landing facts into machine-readable evidence
- L3 externalizes next-slice and blocker truth
- L4 removes human relay gaps between repo truth and CI or release evidence

Without these layers, the loop may still be useful, but it remains closer to an auxiliary script than to a trusted pipeline.

## Immediate Application To DataPulse

- `L0-L3` are blueprint/governance bootstrap slices and should not be globally blocked by remote HA or release evidence.
- `L4.1` is a workflow-change slice; it may care about repo execution safety, but it should not be blocked by the very release evidence it is meant to introduce.
- Future product slices should declare their own verification profile instead of inheriting the full repository governance stack by default.
- A `blocked` state is not a failure of the loop. It is expected healthy behavior when the blocker surface is machine-decidable.
