# DataPulse Console Modularity And Traceability Blueprint

Status: repo-scoped follow-up blueprint, `L26.1` repo truth landed

Created: 2026-03-31

Updated: 2026-03-31

## Goal

Promote the remaining GUI follow-up gaps into repo truth as a narrow wave after the completed `L25` workflow-first shell simplification.

The target is not to reopen shell-order simplification, promote advanced surfaces back to first rank, or force a default React or Vite migration.

The target is to:

- introduce one clearer console client boundary for shared `/api/...` access
- make stage outputs traceable across the operator path instead of leaving them fragmented across cards and logs
- standardize operator-visible signal badges and explanation ownership for quality, delivery, overflow, and trust-style signals
- bound the frontend-engineering question so it only reopens if the repo still shows real maintainability pressure after the narrower follow-up lands

## Repo Read Correction

Current DataPulse already has the important GUI baseline:

- `L24` landed URL-restorable workspace context, section-level summary framing, operator-guidance ownership, and helper extraction
- `L25` landed workflow-first shell order, first-rank versus demoted surface rules, stage-owned output visibility, and stage-owned feedback
- run feedback is no longer invisible and the shell already exposes explicit started, pending, completed, no-result, and failed states

The remaining gap is no longer shell shape.

The remaining gaps are follow-up structure and traceability:

- shared `/api/...` client access is still more distributed than it should be for safe iteration
- stage outputs exist, but the shell still lacks one repo-owned trace surface that helps operators answer "what happened after I started this work?"
- signal semantics remain fragmented across cards, chips, and copy instead of one owned taxonomy
- the frontend-stack question still needs a bounded reopening rule so it does not drift back into generic "rewrite the UI" discussion

## Remaining Follow-Up Targets

### Shared Client Boundary

This wave should define one canonical browser-side owner for shared `/api/...` request construction and response normalization.

Repo implication:

- prefer one shared client module or equivalent owner for repeated fetch logic
- keep render surfaces and event handlers focused on state and presentation
- do not fork Reader or HTTP lifecycle semantics into browser-only business state

### Stage-Linked Output Trace

This wave should define one operator-visible trace surface that makes the path across stages legible.

Minimum path:

1. mission or start action
2. run outcome
3. triage disposition
4. story promotion or contradiction state
5. delivery outcome or explicit reason the flow stopped earlier

Repo implication:

- action logs may contribute evidence, but they are not enough by themselves
- the trace surface should remain stage-linked and output-oriented rather than becoming a generic audit dump

### Shared Signal Taxonomy

This wave should standardize a narrow signal vocabulary for operator-facing status indicators.

Initial candidate classes:

- `Quality`
- `Delivery`
- `Overflow`
- `Trust`

Repo implication:

- no badge may be decorative-only
- every shared signal must name its owner, meaning, and next-action or explanation surface
- signal expansions must stay attributable to real Reader or API facts when they make factual claims

### Frontend Escalation Boundary

This wave should define when the repo is actually allowed to reopen a standalone frontend engineering decision.

Repo implication:

- do not reopen React or Vite by default
- first land the narrower client-boundary and traceability work
- only reopen standalone frontend engineering if evidence shows the current shell still cannot evolve safely enough after those narrower changes

## What This Wave Must Preserve

Invariants:

1. `WatchMission`, `DataPulseItem`, `Story`, `Report`, and named routes remain canonical lifecycle nouns
2. the browser remains a projection over Reader, CLI, MCP, and HTTP truth
3. the workflow-first shell order from `L25` remains intact unless a later contract explicitly reopens it
4. current URL-restorable workspace context remains valid unless a later contract explicitly reopens it
5. existing action-log, retry guidance, duplicate explain, and stage-owned feedback remain reused rather than re-derived

## What This Wave Must Not Do

This wave must not:

- reopen the shell-order simplification question solved in `L25`
- force a standalone frontend stack decision before the narrower follow-up lands
- let a client-boundary refactor invent browser-only lifecycle truth
- add badges or signals that do not map to an owned explanation surface
- collapse the command chamber identity into a generic admin shell

## L26 Contract Targets

`L26.2` should freeze five things before implementation begins:

1. which module or owner becomes the canonical console client boundary
2. what the minimum stage-linked output trace must show
3. which shared signal classes exist and who owns their explanation
4. when the frontend-engineering question is allowed to reopen
5. which comprehension and acceptance checks must pass before the wave can close

## L26 Slice Map

| Slice | Outcome | Why it exists |
| --- | --- | --- |
| `L26.1` | Land this repo-scoped modularity-and-traceability blueprint and fact promotion | Reopens the next GUI follow-up without pretending `L25` is still unfinished |
| `L26.2` | Freeze the client-boundary, traceability, signal, and frontend-escalation contract | Prevents implementation drift before the remaining GUI gaps are addressed |
| `L26.3` | Extract a shared console API client boundary and reduce repeated fetch wiring | Lowers iteration risk in the current shell without reopening frontend architecture |
| `L26.4` | Add stage-linked output trace surfaces and shared signal taxonomy | Makes outputs and status explanations easier to follow across the workflow-first shell |
| `L26.5` | Reassess standalone frontend escalation only after the narrower follow-up lands and harden acceptance | Keeps frontend-stack discussion evidence-based instead of speculative |

## Recommended Ignition Order

Recommended order:

1. `L26.2`
2. `L26.3`
3. `L26.4`
4. `L26.5`

## Manual Ignition Boundary

With `L26.1` landed, the next manual ignition target should be `L26.2`.

Reason:

- `L25` already solved shell order and first-rank surface reduction
- the next risk is drift in client boundary, traceability shape, and signal ownership
- freezing those obligations is the narrowest way to reopen GUI work without regressing into frontend-stack debates

After the blueprint landing is committed and the repo is back to a clean baseline, the normal local ignition entrypoint stays:

```bash
bash scripts/governance/ignite_datapulse_codex_loop.sh
```

Expected next slice after this blueprint landing: `L26.2`

## Fact Sources

- `/Users/sunyifei/Library/Mobile Documents/iCloud~md~obsidian/Documents/SunYifei/01-项目开发/DataPulse/00_索引与计划/DataPulse_agent-skills-hub前端交互清晰化补强清单_2026-03-31.md`
- `/Users/sunyifei/DataPulse/docs/gui_intelligence_console_plan.md`
- `/Users/sunyifei/DataPulse/docs/governance/datapulse-console-workflow-simplification-blueprint.md`

## Success Condition

DataPulse reopens GUI follow-up work without reopening the wrong problem:

- the remaining gaps are narrowed to client boundary, traceability, signal ownership, and bounded frontend escalation
- `L25` remains closed as the completed shell-order wave
- next ignition is unambiguous: `L26.2`
