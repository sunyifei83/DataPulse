# DataPulse External Fact Intake Draft

Status: draft only, manual intake path

Created: 2026-03-07

## Goal

Turn an external fact note into repository blueprint truth without letting prose bypass the loop contract.

The repository rule stays the same:

- external notes may be evidence
- the loop only reads structured `phase + slices + status`
- the first repository-visible step is a structured slice, not a copied markdown paragraph

## Recommended Landing Pattern

Use a two-step intake:

1. read the external fact note and create a mutable working-copy slice proposal
2. review the preview and then promote that one slice into the repository blueprint truth

This keeps `docs/governance/*.json` as the source of loop truth while still letting Codex read an external Obsidian note.

## Scripts

Create a working-copy slice proposal from an external Markdown note:

```bash
python3 scripts/governance/intake_external_fact_to_working_slice.py \
  --plan out/governance/datapulse-blueprint-plan.working.json \
  --init-from docs/governance/datapulse-blueprint-plan.json \
  --phase-id L6 \
  --phase-title "External fact intake" \
  --slice-id L6.1 \
  --title "Decompose intelligence platformization note into structured blueprint follow-up slices" \
  --status pending \
  --execution-profile draft_only \
  --promotion-scope none \
  --artifact docs/governance/datapulse-blueprint-plan.draft.json \
  --fact-md "/Users/sunyifei/Library/Mobile Documents/iCloud~md~obsidian/Documents/SunYifei/01-项目开发/DataPulse/00_索引与计划/仓内功能升维与情报中台化计划.md"
```

The intake output tells you whether the new slice is already the current `next_slice` and whether it would auto-advance if ignited:

- `selected_as_next_slice_now`
- `status_if_run_now`
- `blocking_facts`
- `would_auto_advance_if_ignited`

Promote one reviewed working-copy slice into repository blueprint truth:

```bash
python3 scripts/governance/promote_datapulse_working_slice_to_blueprint.py \
  --working-plan out/governance/datapulse-blueprint-plan.working.json \
  --slice-id L6.1
```

For the clean-baseline path, land that blueprint change as its own docs/governance commit, wait for `ci_proven`, and only then ignite the local Codex loop:

```bash
python3 scripts/governance/land_datapulse_blueprint_intake.py \
  --working-plan /tmp/datapulse-blueprint-plan.working.json \
  --slice-id L6.1
```

That wrapper:

- previews whether the promoted slice becomes the current `next_slice`
- commits only the declared blueprint landing paths
- pushes and waits for the required `ci_proven` workflow
- returns only when the repository is back to a clean baseline

After that independent landing completes, ignite the local Codex loop and keep the external note mounted for reference:

```bash
bash scripts/governance/ignite_datapulse_codex_loop.sh \
  --obsidian-source "/Users/sunyifei/Library/Mobile Documents/iCloud~md~obsidian/Documents/SunYifei/01-项目开发/DataPulse/00_索引与计划/仓内功能升维与情报中台化计划.md"
```

## Why The First Imported Slice Should Usually Be A Decomposition Slice

A broad external note usually contains multiple future actions. The loop should not receive that entire note as one giant open slice.

The safer pattern is:

1. import a slice whose job is "decompose this note into repo-relevant structured follow-up slices"
2. let Codex land the plan update in `docs/governance/datapulse-blueprint-plan.draft.json`
3. let the loop reopen on the first newly declared executable slice

This keeps the blueprint machine-readable and prevents external roadmap prose from becoming ambiguous loop truth.

## Practical Decision Rule

Use the proposed slice immediately only when all of the following are true:

- it is now the first non-completed slice in the blueprint order
- `blocking_facts` is empty for that slice
- the slice is narrow enough to be landed in one Codex round

Otherwise, keep it as a reviewed blueprint change and let the loop stop on the machine-decidable blocker.
