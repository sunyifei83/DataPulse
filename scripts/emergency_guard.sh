#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
REPORT_PATH=""
LOG_PATH=""
RULES_PATH=""
PREV_REPORT_PATH=""
OUT_PATH=""

usage() {
  cat <<'EOF'
Usage:
  bash scripts/emergency_guard.sh \
    --report <artifacts/.../remote_report.md> \
    [--log <artifacts/.../remote_test.log>] \
    [--rules <docs/emergency_rules.json>] \
    [--prev-report <artifacts/.../remote_report.md>] \
    [--out <artifacts/.../emergency_state.json>]
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --report)
      REPORT_PATH="$2"
      shift 2
      ;;
    --log)
      LOG_PATH="$2"
      shift 2
      ;;
    --rules)
      RULES_PATH="$2"
      shift 2
      ;;
    --prev-report)
      PREV_REPORT_PATH="$2"
      shift 2
      ;;
    --out)
      OUT_PATH="$2"
      shift 2
      ;;
    *)
      usage
      exit 2
      ;;
  esac
done

if [[ -z "$REPORT_PATH" ]]; then
  usage
  exit 2
fi

if [[ -z "$RULES_PATH" ]]; then
  RULES_PATH="docs/emergency_rules.json"
fi

resolve_path() {
  local p="$1"
  if [[ "$p" = /* ]]; then
    echo "$p"
  else
    echo "$ROOT_DIR/$p"
  fi
}

REPORT_PATH="$(resolve_path "$REPORT_PATH")"
RULES_PATH="$(resolve_path "$RULES_PATH")"
if [[ -n "${LOG_PATH}" ]]; then
  LOG_PATH="$(resolve_path "$LOG_PATH")"
fi
if [[ -n "${PREV_REPORT_PATH}" ]]; then
  PREV_REPORT_PATH="$(resolve_path "$PREV_REPORT_PATH")"
fi
if [[ -n "${OUT_PATH}" ]]; then
  OUT_PATH="$(resolve_path "$OUT_PATH")"
fi

if [[ ! -f "$REPORT_PATH" ]]; then
  echo "[error] remote report not found: $REPORT_PATH"
  exit 2
fi
if [[ ! -f "$RULES_PATH" ]]; then
  echo "[error] rules not found: $RULES_PATH"
  exit 2
fi
if [[ -n "$LOG_PATH" && ! -f "$LOG_PATH" ]]; then
  echo "[warn] log file not found, continue with report only: $LOG_PATH"
  LOG_PATH=""
fi
if [[ -n "$PREV_REPORT_PATH" && ! -f "$PREV_REPORT_PATH" ]]; then
  echo "[warn] previous report not found, skip diff check: $PREV_REPORT_PATH"
  PREV_REPORT_PATH=""
fi

if [[ -z "$OUT_PATH" ]]; then
  OUT_PATH="$(dirname "$REPORT_PATH")/emergency_state.json"
fi

python3 - <<'PY'
import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List


parser = argparse.ArgumentParser()
parser.add_argument("--report", required=True)
parser.add_argument("--log", default="")
parser.add_argument("--rules", required=True)
parser.add_argument("--prev_report", default="")
parser.add_argument("--out", required=True)
parser.add_argument("--root", required=True)
args = parser.parse_args()

report_path = Path(args.report)
log_path = Path(args.log) if args.log else None
rules_path = Path(args.rules)
prev_report = Path(args.prev_report) if args.prev_report else None
out_path = Path(args.out)
root_dir = Path(args.root)


def read_text(path: Path) -> str:
    if not path or not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="ignore")


def parse_report(path: Path) -> Dict:
    text = read_text(path)
    result = {
        "run_id": "",
        "fail_steps": None,
        "env": {},
        "block_codes": [],
        "raw": text,
    }
    if not text:
        return result

    for line in text.splitlines():
        if result["run_id"] == "" and "RUN_ID=" in line:
            result["run_id"] = line.split("RUN_ID=", 1)[1].strip()
        m = re.match(r"^- 运行ID:\s*(\S+)", line)
        if m:
            result["run_id"] = m.group(1).strip()
        m = re.match(r"^- 失败步骤:\s*(\d+)", line)
        if m:
            result["fail_steps"] = int(m.group(1))
        m = re.match(r"^- ([A-Z][A-Z0-9_]+):\s*(.*)$", line)
        if m:
            result["env"][m.group(1)] = m.group(2).strip()

    in_block = False
    for line in text.splitlines():
        if line.strip().startswith("## 阻断码"):
            in_block = True
            continue
        if in_block:
            if line.strip().startswith("## "):
                break
            m = re.match(r"^\s*-\s*(.+?)\s*$", line)
            if not m:
                continue
            token = m.group(1)
            if token == "无新增阻断码":
                continue
            if re.fullmatch(r"[A-Z][A-Z0-9_]+", token) or token.startswith("context window exceeded"):
                result["block_codes"].append(token)
    return result


def lower_set(values: List[str]) -> List[str]:
    return [v.lower() for v in values]


rules = json.loads(rules_path.read_text(encoding="utf-8"))
signals = rules.get("signals", [])
state_map = {state["id"]: state.get("name", state["id"]) for state in rules.get("state_machine", [])}
rerun_rules = rules.get("rerun", {})
stop_rules = rules.get("stop_rules", {})

current = parse_report(report_path)
prev = parse_report(prev_report) if prev_report else {}
log_text = read_text(log_path) if log_path else ""
full_text = f"{current['raw']}\n{log_text}".lower()

block_codes = []
for code in current["block_codes"]:
    if code not in block_codes:
        block_codes.append(code)

for signal in signals:
    sig_id = signal.get("id", "")
    aliases = [sig_id] + signal.get("aliases", [])
    for alias in aliases:
        if not alias:
            continue
        if alias.lower() in full_text and sig_id not in block_codes:
            block_codes.append(sig_id)
            break

first_trigger = ""
for signal in signals:
    sig_id = signal.get("id", "")
    if sig_id in block_codes:
        first_trigger = sig_id
        break

signal_map = {signal.get("id"): signal for signal in signals}
first_signal = signal_map.get(first_trigger, {})
primary_action = first_signal.get("primary_action", "")

state = "S0"
state_name = state_map.get(state, "监控")
stop = False
fail_steps = current["fail_steps"] if current["fail_steps"] is not None else 0

blocker_codes = set(stop_rules.get("blocker_codes", []))
if fail_steps == 0 and not block_codes:
    state = "S5"
    state_name = state_map.get(state, state)
    conclusion = "GREEN"
elif blocker_codes.intersection(block_codes):
    state = "S5"
    state_name = state_map.get(state, state)
    stop = True
    conclusion = "RED"
else:
    state = "S1"
    state_name = state_map.get(state, state)
    conclusion = "YELLOW" if block_codes else "RED"

if fail_steps and fail_steps > 0 and conclusion == "GREEN":
    conclusion = "RED"

should_new_run = bool(rerun_rules.get("always_new_run_on_failure", True) and fail_steps and fail_steps > 0)
restart_codes = {code.lower() for code in rerun_rules.get("codes_require_new_run_id", [])}
if first_trigger and first_trigger.lower() in restart_codes:
    should_new_run = True
if block_codes:
    should_new_run = True

tracked_keys = rerun_rules.get("tracked_env_keys", [])
changed_params = []
if prev:
    prev_env = prev.get("env", {})
    curr_env = current.get("env", {})
    for key in tracked_keys:
        if key in curr_env and key in prev_env and curr_env[key] != prev_env[key]:
            changed_params.append({
                "key": key,
                "previous": prev_env[key],
                "current": curr_env[key],
            })
            should_new_run = True

if first_trigger == "context window exceeded" and first_signal.get("id") and not should_new_run:
    should_new_run = True

state_payload = {
    "run_id": current.get("run_id", ""),
    "first_trigger": first_trigger,
    "state": {
        "id": state,
        "name": state_name,
    },
    "stop": stop,
    "should_new_run_id": should_new_run,
    "block_codes": block_codes,
    "blocker_codes": sorted(blocker_codes.intersection(block_codes)),
    "fail_steps": fail_steps,
    "changed_params": changed_params,
    "conclusion": conclusion,
    "recommendation": {
        "primary_action": primary_action,
        "secondary_action": first_signal.get("secondary_action", ""),
        "remediation_class": first_signal.get("class", ""),
    },
    "evidence": {
        "report": str(report_path),
        "log": str(log_path) if log_path else "",
        "prev_report": str(prev_report) if prev_report else "",
        "report_root": str(root_dir),
    },
    "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
}

out_path.parent.mkdir(parents=True, exist_ok=True)
out_path.write_text(json.dumps(state_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

print(json.dumps(state_payload, ensure_ascii=False))
print(f"state_file={out_path}")
print(f"RUN_ID={state_payload['run_id']}")
print(f"STATE={state_payload['state']['id']} {state_payload['state']['name']}")
print(f"FIRST_TRIGGER={state_payload['first_trigger'] or 'NONE'}")
print(f"NEW_RUN_ID_REQUIRED={state_payload['should_new_run_id']}")
print(f"STOP={state_payload['stop']}")
print(f"CONCLUSION={state_payload['conclusion']}")
PY \
  --report "$REPORT_PATH" \
  --log "${LOG_PATH:-}" \
  --rules "$RULES_PATH" \
  --prev_report "${PREV_REPORT_PATH:-}" \
  --out "$OUT_PATH" \
  --root "$ROOT_DIR"
