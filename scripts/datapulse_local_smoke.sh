#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

OUT_DIR="${OUT_DIR:-$ROOT_DIR/artifacts}"
RUN_ID="${RUN_ID:-$(date +%Y%m%d_%H%M%S)}"
RUN_LOG_DIR="$OUT_DIR/openclaw_datapulse_${RUN_ID}"
mkdir -p "$RUN_LOG_DIR"
LOG_FILE="$RUN_LOG_DIR/local_test.log"

if [[ -f ".env.openclaw" ]]; then
  set -a
  source ".env.openclaw"
  set +a
elif [[ -f ".env" ]]; then
  set -a
  source ".env"
  set +a
fi

: "${URL_1:=}"
: "${URL_BATCH:=}"
: "${PLATFORMS:=twitter reddit youtube bilibili telegram rss wechat xhs}"
: "${MIN_CONFIDENCE:=${DATAPULSE_MIN_CONFIDENCE:-0.0}}"

PYTHON_BIN="${PYTHON_BIN:-python3}"
DATAPULSE_CLI=(datapulse)
DATAPULSE_SMOKE=(datapulse-smoke)

if ! command -v datapulse >/dev/null 2>&1; then
  DATAPULSE_CLI=("$PYTHON_BIN" -m datapulse.cli)
fi
if ! command -v datapulse-smoke >/dev/null 2>&1; then
  DATAPULSE_SMOKE=("$PYTHON_BIN" -m datapulse.tools.smoke)
fi

exec 1> >(tee -a "$LOG_FILE")
exec 2> >(tee -a "$LOG_FILE" >&2)

{
  echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] datapulse local smoke start"
  echo "RUN_ID=$RUN_ID"
  echo "ROOT_DIR=$ROOT_DIR"
  echo "MIN_CONFIDENCE=$MIN_CONFIDENCE"
  echo "URL_1=$URL_1"
  echo "URL_BATCH=$URL_BATCH"
  echo "PLATFORMS=$PLATFORMS"
} | tee -a "$LOG_FILE"

pass_count=0
fail_count=0
step() {
  local title="$1"; shift
  printf "\n### %s\n" "$title"
  printf "%s\n" "$(printf '%*s' 80 '' | tr ' ' '=')"
}

run_cmd() {
  local name="$1"; shift
  if "$@"; then
    echo "PASS: $name"
    pass_count=$((pass_count+1))
  else
    echo "FAIL: $name"
    fail_count=$((fail_count+1))
  fi
}

step "1) 环境与入口"
run_cmd "datapulse CLI 可用（入口）" "${DATAPULSE_CLI[@]}" --help
run_cmd "datapulse-smoke 可用（入口）" "${DATAPULSE_SMOKE[@]}" --list
run_cmd "Python 加载 datapulse" "$PYTHON_BIN" - <<'PY'
import datapulse
print(datapulse.__name__)
PY

step "2) 平台变量清单"
run_cmd "smoke --list 可执行" "${DATAPULSE_SMOKE[@]}" --list

step "3) 单链路冒烟"
if [[ -n "$URL_1" ]]; then
    run_cmd "单条 URL 解析" "${DATAPULSE_CLI[@]}" "$URL_1" --min-confidence "$MIN_CONFIDENCE"
else
  echo "SKIP: URL_1 空；请设置环境变量 URL_1"
fi

step "4) 批量解析冒烟"
if [[ -n "$URL_BATCH" ]]; then
  # 使用 read -a 拆分空格分隔的 URL（支持空格分割列表）
  IFS=' ' read -r -a batch_urls <<< "$URL_BATCH"
  if [[ ${#batch_urls[@]} -gt 0 ]]; then
    run_cmd "批量 URL 解析" "${DATAPULSE_CLI[@]}" --batch "${batch_urls[@]}" --min-confidence "$MIN_CONFIDENCE"
  else
    echo "SKIP: URL_BATCH 为空"
  fi
else
  echo "SKIP: URL_BATCH 空；请设置环境变量 URL_BATCH"
fi

step "5) 记忆存储生命周期"
run_cmd "列表命令" "${DATAPULSE_CLI[@]}" --list --limit 5 --min-confidence 0.0

step "6) 平台覆盖（read only）"
if (("${#DATAPULSE_SMOKE[@]}" > 0)); then
  "${DATAPULSE_SMOKE[@]}" --platforms $PLATFORMS --list
else
  echo "SKIP: datapulse-smoke 不存在"
fi

step "7) Agent 快速路径"
run_cmd "agent 快速调用" "$PYTHON_BIN" - <<'PY'
import asyncio
import os
from datapulse.agent import DataPulseAgent
urls = []
for part in [os.getenv("URL_1", ""), os.getenv("URL_BATCH", "")]:
    if part.strip():
        urls.extend(part.split())
if not urls:
    print("SKIP")
else:
    message = " ".join(urls)
    result = asyncio.run(DataPulseAgent().handle(message))
    print(f"status={result.get('status')} count={result.get('count', 0)}")
PY

step "8) 来源与订阅"
run_cmd "source catalog 可访问" "$PYTHON_BIN" - <<'PY'
from datapulse.reader import DataPulseReader
reader = DataPulseReader()
print(f"sources={len(reader.list_sources(public_only=True))}")
print(f"packs={len(reader.list_packs(public_only=True))}")
PY

step "9) Feed 输出"
run_cmd "feed 生成" "$PYTHON_BIN" - <<'PY'
from datapulse.reader import DataPulseReader
import os

reader = DataPulseReader()
payload = reader.build_json_feed(limit=5, min_confidence=float(os.environ.get("MIN_CONFIDENCE", "0.0")))
items = payload.get("items", [])
print(f"feed_items={len(items)}")
print(payload.get("title"))
PY

step "10) Smoke 平台回归"
if (("${#DATAPULSE_SMOKE[@]}" > 0)); then
  run_cmd "smoke 平台回归" "${DATAPULSE_SMOKE[@]}" --platforms $PLATFORMS --require-all --min-confidence "$MIN_CONFIDENCE"
else
  echo "SKIP: datapulse-smoke 不存在"
fi

printf '\n[%s] PASS=%s FAIL=%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$pass_count" "$fail_count"
{
  echo "# 数据脉搏本机联测报告"
  echo "- 运行ID: $RUN_ID"
  echo "- 开始时间: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "- PASS: $pass_count"
  echo "- FAIL: $fail_count"
  echo "- Log: $LOG_FILE"
} > "$RUN_LOG_DIR/local_report.md"

echo "local report: $RUN_LOG_DIR/local_report.md"
exit 0
