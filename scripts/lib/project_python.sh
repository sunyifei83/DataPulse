#!/usr/bin/env bash

datapulse_python_supports_cmd() {
  "$@" - <<'PY' >/dev/null 2>&1
import sys

raise SystemExit(0 if sys.version_info[:2] >= (3, 10) else 1)
PY
}

datapulse_python_version_text() {
  "$@" - <<'PY'
import sys

print(sys.version.split()[0])
PY
}

datapulse_report_python_requirement_error() {
  local actual="${1:-unknown}"
  local label="${2:-python3}"
  if [[ "$actual" == "unknown" ]]; then
    echo "DataPulse requires Python >= 3.10. Use 'uv run ...' or set PYTHON_BIN to a python3.10+ interpreter." >&2
    return
  fi
  echo "DataPulse requires Python >= 3.10. ${label} resolves to ${actual}. Use 'uv run ...' or set PYTHON_BIN to a python3.10+ interpreter." >&2
}

datapulse_resolve_python_cmd() {
  DATAPULSE_PYTHON_CMD=()
  DATAPULSE_PYTHON_DESC=""

  if [[ -n "${PYTHON_BIN:-}" ]]; then
    read -r -a DATAPULSE_PYTHON_CMD <<< "${PYTHON_BIN}"
    if ! command -v "${DATAPULSE_PYTHON_CMD[0]}" >/dev/null 2>&1; then
      echo "Configured PYTHON_BIN not found: ${PYTHON_BIN}" >&2
      return 1
    fi
    if ! datapulse_python_supports_cmd "${DATAPULSE_PYTHON_CMD[@]}"; then
      datapulse_report_python_requirement_error \
        "$(datapulse_python_version_text "${DATAPULSE_PYTHON_CMD[@]}" 2>/dev/null || echo unknown)" \
        "PYTHON_BIN"
      return 1
    fi
    DATAPULSE_PYTHON_DESC="${PYTHON_BIN}"
    return 0
  fi

  if command -v uv >/dev/null 2>&1; then
    DATAPULSE_PYTHON_CMD=(uv run python)
    DATAPULSE_PYTHON_DESC="uv run python"
    return 0
  fi

  local candidate
  for candidate in python3.12 python3.11 python3.10 python3 python; do
    if command -v "$candidate" >/dev/null 2>&1 && datapulse_python_supports_cmd "$candidate"; then
      DATAPULSE_PYTHON_CMD=("$candidate")
      DATAPULSE_PYTHON_DESC="$candidate"
      return 0
    fi
  done

  if command -v python3 >/dev/null 2>&1; then
    datapulse_report_python_requirement_error \
      "$(datapulse_python_version_text python3 2>/dev/null || echo unknown)" \
      "python3"
    return 1
  fi

  if command -v python >/dev/null 2>&1; then
    datapulse_report_python_requirement_error \
      "$(datapulse_python_version_text python 2>/dev/null || echo unknown)" \
      "python"
    return 1
  fi

  echo "DataPulse requires Python >= 3.10, but no Python interpreter was found. Install uv or set PYTHON_BIN." >&2
  return 1
}
