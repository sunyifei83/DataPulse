#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

pass_count=0
fail_count=0

pass() {
  echo "[PASS] $1"
  pass_count=$((pass_count + 1))
}

fail() {
  echo "[FAIL] $1"
  fail_count=$((fail_count + 1))
}

check_required_file() {
  local path="$1"
  if [[ -e "$path" ]]; then
    pass "required file exists: $path"
  else
    fail "missing required file: $path"
  fi
}

check_cmd() {
  local name="$1"
  if command -v "$name" >/dev/null 2>&1; then
    pass "command available: $name"
  else
    fail "command unavailable: $name"
  fi
}

if [[ ! -d .git ]]; then
  fail "not a git repository root"
else
  pass "git repository detected"
fi

check_cmd python3
check_cmd jq || true
check_cmd gh || true

if grep -qxF ".claude/" .gitignore; then
  pass ".claude/ 已写入 .gitignore"
else
  fail ".claude/ 未写入 .gitignore"
fi

check_required_file "pyproject.toml"
check_required_file "README.md"
check_required_file "README_CN.md"
check_required_file "README_EN.md"
check_required_file "docs/contracts/openclaw_datapulse_tool_contract.json"
check_required_file "docs/openclaw_tavily_multi_execution_plan.json"
check_required_file "docs/release_checklist.md"
check_required_file "docs/search_gateway_config.md"
check_required_file "docs/release_rollback_guide.md"
check_required_file "scripts/release_publish.sh"
check_required_file "scripts/datapulse_local_smoke.sh"
check_required_file "scripts/datapulse_remote_openclaw_smoke.sh"

if python3 -m json.tool docs/contracts/openclaw_datapulse_tool_contract.json >/dev/null; then
  pass "openclaw contract JSON valid"
else
  fail "openclaw contract JSON invalid"
fi

if bash scripts/security_guardrails.sh; then
  pass "security guardrails passed"
else
  fail "security guardrails failed"
fi

if python3 -m compileall datapulse mcp_server.py >/dev/null 2>&1; then
  pass "python compile check passed"
else
  fail "python compile check failed"
fi

echo "release readiness: pass=$pass_count fail=$fail_count"
if [[ "$fail_count" -ne 0 ]]; then
  exit 1
fi
echo "[OK] release readiness check passed"
