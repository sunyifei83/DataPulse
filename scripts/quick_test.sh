#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

# Use a robust Python launcher compatible with different local setups.
if [[ -n "${PYTHON_BIN:-}" ]]; then
  read -r -a PYTHON_CMD <<< "${PYTHON_BIN}"
else
  if command -v uv >/dev/null 2>&1; then
    PYTHON_CMD=(uv run python3)
  else
    PYTHON_CMD=(python3)
  fi
fi

if ! command -v "${PYTHON_CMD[0]}" >/dev/null 2>&1; then
  if command -v python >/dev/null 2>&1; then
    PYTHON_CMD=(python)
  else
    echo "  ⚠️ Python executable not found. Set PYTHON_BIN to a valid interpreter."
    exit 1
  fi
fi

run_python() {
  "${PYTHON_CMD[@]}" "$@"
}

DATAPULSE_CLI=(datapulse)
if ! command -v datapulse >/dev/null 2>&1; then
  DATAPULSE_CLI=("${PYTHON_CMD[@]}" -m datapulse.cli)
fi

DATAPULSE_SMOKE=(datapulse-smoke)
if ! command -v datapulse-smoke >/dev/null 2>&1; then
  DATAPULSE_SMOKE=("${PYTHON_CMD[@]}" -m datapulse.tools.smoke)
fi

DATAPULSE_CONSOLE_SMOKE=(bash scripts/datapulse_console_smoke.sh)

echo "[1/7] Env check"
printf '%s\n' "  Python: $(${PYTHON_CMD[@]} --version 2>&1 || true)"
printf '%s\n' "  Pip package: datapulse -> $(run_python -c 'import datapulse,sys; print(datapulse.__name__)' 2>/dev/null || echo unavailable)"

echo "[2/7] CLI smoke list (safe)"
if [[ ${#DATAPULSE_SMOKE[@]} -gt 0 ]]; then
  "${DATAPULSE_SMOKE[@]}" --list || true
else
  echo "  ⚠️ datapulse-smoke not installed in PATH."
fi

echo "[3/7] Console smoke"
"${DATAPULSE_CONSOLE_SMOKE[@]}"

echo "[4/7] CLI single URL (if URL_1 is set)"
if [[ -n "${URL_1:-}" ]]; then
  "${DATAPULSE_CLI[@]}" "$URL_1" --min-confidence "${MIN_CONFIDENCE:-0.0}"
else
  echo "  ⚪ Skip: set URL_1 for a real URL test."
fi

echo "[5/7] CLI batch URL (if URL_BATCH is set)"
if [[ -n "${URL_BATCH:-}" ]]; then
  IFS=' ' read -r -a batch_urls <<< "${URL_BATCH}"
  "${DATAPULSE_CLI[@]}" --batch "${batch_urls[@]}" --min-confidence "${MIN_CONFIDENCE:-0.0}"
else
  echo "  ⚪ Skip: set URL_BATCH for one-line batch test."
fi

echo "[6/7] Memory lifecycle"
${DATAPULSE_CLI[@]} --list --limit 5 --min-confidence 0.0 || true
${DATAPULSE_CLI[@]} --clear

echo "[7/7] Agent quick call (if URL_BATCH or URL_1 set)"
if [[ -n "${URL_1:-}${URL_BATCH:-}" ]]; then
  run_python - <<'PY'
import asyncio
import os

from datapulse.agent import DataPulseAgent

urls = []
for part in [os.getenv("URL_1", ""), os.getenv("URL_BATCH", "")]:
    urls.extend(part.split())

message = " ".join(urls)

agent = DataPulseAgent()
resp = asyncio.run(agent.handle(message))
print(resp)
PY
else
  echo "  ⚪ Skip: set URL_1 or URL_BATCH before running agent section."
fi

echo "Quick test finished."
