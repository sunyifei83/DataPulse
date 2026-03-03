#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

OUT_DIR="${OUT_DIR:-$ROOT_DIR/artifacts}"
RUN_ID="${RUN_ID:-$(date +%Y%m%d_%H%M%S)}"
REPORT_DIR="$OUT_DIR/xhs_quality_${RUN_ID}"
mkdir -p "$REPORT_DIR"

JSON_REPORT="$REPORT_DIR/xhs_quality_report.json"
MD_REPORT="$REPORT_DIR/xhs_quality_report.md"
RUN_LOG="$REPORT_DIR/run.log"

export DATAPULSE_XHS_QUERY="${DATAPULSE_XHS_QUERY:-openclaw}"
export DATAPULSE_XHS_LIMIT="${DATAPULSE_XHS_LIMIT:-8}"
export DATAPULSE_XHS_MIN_CONFIDENCE="${DATAPULSE_XHS_MIN_CONFIDENCE:-0.0}"
export DATAPULSE_XHS_SELECT="${DATAPULSE_XHS_SELECT:-1}"
export DATAPULSE_XHS_PREFER_ENGAGEMENT="${DATAPULSE_XHS_PREFER_ENGAGEMENT:-1}"
export DATAPULSE_XHS_NO_CONTENT_PRINT="${DATAPULSE_XHS_NO_CONTENT_PRINT:-1}"
export DATAPULSE_XHS_TIMEOUT_SECONDS="${DATAPULSE_XHS_TIMEOUT_SECONDS:-120}"

{
  echo "Started at: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "Query: $DATAPULSE_XHS_QUERY"
  echo "Limit: $DATAPULSE_XHS_LIMIT"
  echo "Min-confidence: $DATAPULSE_XHS_MIN_CONFIDENCE"
  echo "Prefer engagement: $DATAPULSE_XHS_PREFER_ENGAGEMENT"
  echo "Select index: $DATAPULSE_XHS_SELECT"
} | tee "$RUN_LOG"

CMD=(uv run python3 scripts/xhs_quality_report.py
  --query "$DATAPULSE_XHS_QUERY"
  --limit "$DATAPULSE_XHS_LIMIT"
  --min-confidence "$DATAPULSE_XHS_MIN_CONFIDENCE"
  --select "$DATAPULSE_XHS_SELECT"
  --json
  --json-indent 2
)

if [[ "$DATAPULSE_XHS_PREFER_ENGAGEMENT" == "1" ]]; then
  CMD+=(--prefer-engagement)
fi
if [[ "$DATAPULSE_XHS_NO_CONTENT_PRINT" == "1" ]]; then
  CMD+=(--no-content-print)
fi

set +e
if command -v timeout >/dev/null 2>&1; then
  timeout "$DATAPULSE_XHS_TIMEOUT_SECONDS" "${CMD[@]}" > "$JSON_REPORT" 2>> "$RUN_LOG"
  CMD_EXIT=$?
else
  "${CMD[@]}" > "$JSON_REPORT" 2>> "$RUN_LOG"
  CMD_EXIT=$?
fi
set -e

if (( CMD_EXIT == 124 )); then
  echo "ERROR: xhs quality report timed out: ${DATAPULSE_XHS_TIMEOUT_SECONDS}s" | tee -a "$RUN_LOG"
  exit 1
fi

if (( CMD_EXIT != 0 )); then
  echo "WARN: xhs quality report exit code $CMD_EXIT (retained for report generation)" | tee -a "$RUN_LOG"
fi

python3 - "$JSON_REPORT" "$MD_REPORT" <<'PY'
from __future__ import annotations

import json
import sys
from datetime import datetime

json_path, md_path = sys.argv[1], sys.argv[2]

with open(json_path, "r", encoding="utf-8") as fp:
    payload = json.load(fp)

items = payload.get("items", [])
query = payload.get("query", "")
searched_at = payload.get("searched_at", "")
provider = payload.get("provider", "")
mode = payload.get("mode", "")
platform = payload.get("platform", "")
select_idx = payload.get("selected_index")
selected = payload.get("selected", {})
ok = bool(payload.get("ok", False))

lines = [
    "# DataPulse XHS 复核报告",
    f"- 时间: {datetime.utcnow().isoformat() + 'Z'}",
    f"- 查询词: {query}",
    f"- 查询时间: {searched_at}",
    f"- 平台/方案: {platform} | {provider}/{mode}",
    f"- 运行结果: {'成功' if ok else '未检出'}",
    f"- 条目数量: {len(items)}",
    f"- 建议复核条目: {select_idx or 1}",
    "",
]

if not ok:
    lines.append(f"- 失败原因: {payload.get('reason', 'unknown')}")
else:
    for idx, item in enumerate(items[:5], 1):
        lines.append(f"## {idx}. {item.get('title', 'untitled')}")
        lines.append(f"- 来源: {item.get('source_name', '')}")
        lines.append(f"- URL: {item.get('url', '')}")
        lines.append(f"- 置信度: {item.get('confidence')}")
        lines.append(f"- score: {item.get('score')}")
        lines.append(f"- tier: {item.get('metadata', {}).get('tier', '')}")
        lines.append(f"- rationale: {item.get('metadata', {}).get('tier_rationale', '')}")
        lines.append(f"- confidence_factors: {', '.join(item.get('confidence_factors', [])) or 'none'}")
        lines.append(f"- search_sources: {','.join(item.get('search', {}).get('sources', []))}")
        lines.append(f"- sample: {(item.get('sample', '') or '')[:260]}")
        lines.append("")

if selected:
    lines.extend([
        "## 推荐复核项（Top)",
        f"- URL: {selected.get('url', '')}",
        f"- 置信度: {selected.get('confidence')}",
        f"- score: {selected.get('score')}",
        f"- sample: {(selected.get('sample', '') or '')[:260]}",
    ])

with open(md_path, "w", encoding="utf-8") as fp:
    fp.write("\n".join(lines))
PY

{
  echo "JSON: $JSON_REPORT"
  echo "Markdown: $MD_REPORT"
} | tee -a "$RUN_LOG"
echo "Done."

if (( CMD_EXIT != 0 )); then
  exit "$CMD_EXIT"
fi
