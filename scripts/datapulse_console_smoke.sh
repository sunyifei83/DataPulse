#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"
source "$ROOT_DIR/scripts/lib/project_python.sh"

if ! datapulse_resolve_python_cmd; then
  exit 1
fi

PYTHON_CMD=("${DATAPULSE_PYTHON_CMD[@]}")

echo "[console-smoke] start"

echo "[console-smoke] check: module import"
"${PYTHON_CMD[@]}" - <<'PY'
import datapulse.console_server
print("module_ok")
PY

echo "[console-smoke] check: digest projection routes"
"${PYTHON_CMD[@]}" - <<'PY'
from fastapi.testclient import TestClient

from datapulse.console_server import create_app

client = TestClient(create_app())
assert client.get("/api/digest-profile").status_code == 200
assert client.get("/api/digest/console?profile=default&limit=3").status_code == 200
print("digest_routes_ok")
PY

echo "[console-smoke] check: module help"
"${PYTHON_CMD[@]}" -m datapulse.console_server --help >/dev/null

echo "[console-smoke] check: wrapper help"
bash scripts/datapulse_console.sh --help >/dev/null

if command -v datapulse-console >/dev/null 2>&1; then
  echo "[console-smoke] check: installed entrypoint help"
  datapulse-console --help >/dev/null
else
  echo "[console-smoke] skip: datapulse-console not installed in PATH"
fi

if [[ "${DATAPULSE_CONSOLE_BROWSER_SMOKE:-0}" == "1" ]]; then
  echo "[console-smoke] check: browser smoke"
  uv run --extra console --with playwright python scripts/datapulse_console_browser_smoke.py
else
  echo "[console-smoke] skip: browser smoke (set DATAPULSE_CONSOLE_BROWSER_SMOKE=1 to enable)"
fi

echo "[console-smoke] pass"
