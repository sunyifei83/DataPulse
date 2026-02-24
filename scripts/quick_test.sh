#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

echo "[1/6] Env check"
printf '%s\n' "  Python: $(python --version 2>&1 || true)"
printf '%s\n' "  Pip package: datapulse -> $(python -c 'import datapulse,sys; print(datapulse.__name__)' 2>/dev/null || echo unavailable)"

echo "[2/6] CLI smoke list (safe)"
if command -v datapulse-smoke >/dev/null 2>&1; then
  datapulse-smoke --list || true
else
  echo "  ⚠️ datapulse-smoke not installed in PATH."
fi

echo "[3/6] CLI single URL (if URL_1 is set)"
if [[ -n "${URL_1:-}" ]]; then
  datapulse "$URL_1" --min-confidence "${MIN_CONFIDENCE:-0.0}"
else
  echo "  ⚪ Skip: set URL_1 for a real URL test."
fi

echo "[4/6] CLI batch URL (if URL_BATCH is set)"
if [[ -n "${URL_BATCH:-}" ]]; then
  IFS=' ' read -r -a batch_urls <<< "${URL_BATCH}"
  datapulse --batch "${batch_urls[@]}" --min-confidence "${MIN_CONFIDENCE:-0.0}"
else
  echo "  ⚪ Skip: set URL_BATCH for one-line batch test."
fi

echo "[5/6] Memory lifecycle"
datapulse --list --limit 5 --min-confidence 0.0 || true
datapulse --clear

echo "[6/6] Agent quick call (if URL_BATCH or URL_1 set)"
if [[ -n "${URL_1:-}${URL_BATCH:-}" ]]; then
  python - <<'PY'
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
