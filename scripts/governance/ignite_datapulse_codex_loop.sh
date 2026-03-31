#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

export SYSTEM_VERSION_COMPAT="${SYSTEM_VERSION_COMPAT:-1}"

cd "$ROOT_DIR"

EXTRA_ARGS=()
if [[ "${DATAPULSE_CODEX_ALLOW_EXISTING_DIRTY_WORKTREE:-1}" == "0" ]]; then
  EXTRA_ARGS+=(--no-allow-existing-dirty-worktree)
else
  EXTRA_ARGS+=(--allow-existing-dirty-worktree)
fi
if [[ -n "${DATAPULSE_CODEX_DIRTY_WORKTREE_SETTLE_MAX_ATTEMPTS:-}" ]]; then
  EXTRA_ARGS+=(--dirty-worktree-settle-max-attempts "${DATAPULSE_CODEX_DIRTY_WORKTREE_SETTLE_MAX_ATTEMPTS}")
fi

exec uv run python scripts/governance/run_codex_blueprint_loop.py \
  --model "${DATAPULSE_CODEX_MODEL:-gpt-5.4}" \
  --model-reasoning-effort "${DATAPULSE_CODEX_REASONING_EFFORT:-high}" \
  --ask-for-approval "${DATAPULSE_CODEX_APPROVAL_POLICY:-never}" \
  --dangerously-bypass-approvals-and-sandbox \
  --promotion-mode "${DATAPULSE_CODEX_PROMOTION_MODE:-auto}" \
  "${EXTRA_ARGS[@]}" \
  "$@"
