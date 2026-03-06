#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

if command -v datapulse-console >/dev/null 2>&1; then
  exec datapulse-console "$@"
fi

if command -v uv >/dev/null 2>&1; then
  exec uv run datapulse-console "$@"
elif command -v python3 >/dev/null 2>&1; then
  PYTHON_CMD=(python3)
elif command -v python >/dev/null 2>&1; then
  PYTHON_CMD=(python)
else
  echo "Python executable not found." >&2
  exit 1
fi

if ! "${PYTHON_CMD[@]}" - <<'PY' >/dev/null 2>&1
import importlib
import sys

missing = [name for name in ("fastapi", "uvicorn") if importlib.util.find_spec(name) is None]
if missing:
    sys.exit(1)
PY
then
  echo "Console dependencies are missing. Install with: uv pip install -e \".[console]\"" >&2
  exit 1
fi

exec "${PYTHON_CMD[@]}" -m datapulse.console_server "$@"
