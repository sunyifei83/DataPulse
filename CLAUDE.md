# DataPulse Claude Entrypoint

This file is a Claude-compatible shim, not an independent repo constitution.

## Instruction Chain

1. Treat `AGENTS.md` as the canonical DataPulse instruction plane.
2. Use `docs/governance/datapulse-codex-blueprint-loop.draft.md` for governance-loop startup behavior, guardrails, and stop conditions.
3. Future Claude-specific entrypoints, memory files, or rule fragments must extend this chain instead of forking repo governance text.

## Boundary Reminders

- Land only the current `next_slice`; do not advance unrelated blueprint work.
- Keep `.github/workflows/governance-loop-auto.yml` read-only.
- Do not hand-edit governance snapshots or evidence bundles.
- Shared instructions improve execution consistency only; they do not replace runtime evidence or lifecycle admission.
