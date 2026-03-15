#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"
source "$ROOT_DIR/scripts/lib/project_python.sh"

if command -v datapulse-console >/dev/null 2>&1; then
  exec datapulse-console "$@"
fi

if ! datapulse_resolve_python_cmd; then
  exit 1
fi

PYTHON_CMD=("${DATAPULSE_PYTHON_CMD[@]}")

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
