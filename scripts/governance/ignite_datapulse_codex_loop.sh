#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

export SYSTEM_VERSION_COMPAT="${SYSTEM_VERSION_COMPAT:-1}"

cd "$ROOT_DIR"

exec uv run python scripts/governance/run_codex_blueprint_loop.py \
  --model "${DATAPULSE_CODEX_MODEL:-gpt-5.4}" \
  --model-reasoning-effort "${DATAPULSE_CODEX_REASONING_EFFORT:-xhigh}" \
  --ask-for-approval "${DATAPULSE_CODEX_APPROVAL_POLICY:-never}" \
  --dangerously-bypass-approvals-and-sandbox \
  --promotion-mode "${DATAPULSE_CODEX_PROMOTION_MODE:-auto}" \
  "$@"
