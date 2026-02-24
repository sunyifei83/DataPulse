#!/usr/bin/env bash
set -euo pipefail

RUN_ID="${RUN_ID:-$(date +%Y%m%d_%H%M%S)}"
OUT_DIR="${OUT_DIR:-$(pwd)/artifacts}"
RUN_LOG_DIR="$OUT_DIR/openclaw_datapulse_${RUN_ID}"
mkdir -p "$RUN_LOG_DIR"
LOG_FILE="$RUN_LOG_DIR/remote_test.log"
REMOTE_REPORT="$RUN_LOG_DIR/remote_report.md"

if [[ -f ".env.openclaw" ]]; then
  set -a
  source ".env.openclaw"
  set +a
elif [[ -f ".env" ]]; then
  set -a
  source ".env"
  set +a
fi

: "${VPS_USER:=}"
: "${VPS_HOST:=}"
: "${VPS_PASSWORD:=}"
: "${MACMINI_USER:=$USER}"
: "${MACMINI_HOST:=127.0.0.1}"
: "${MACMINI_PASSWORD:=}"
: "${VPS_PORT:=6069}"
: "${MACMINI_PORT:=22}"
: "${MACMINI_DATAPULSE_DIR:=$HOME/.openclaw/workspace/DataPulse}"
: "${PLATFORMS:=twitter reddit youtube bilibili telegram rss wechat xhs}"
: "${MIN_CONFIDENCE:=0.0}"
: "${URL_1:=}"
: "${URL_BATCH:=}"
: "${DATAPULSE_SMOKE_TWITTER_URL:=}"
: "${DATAPULSE_SMOKE_REDDIT_URL:=}"
: "${DATAPULSE_SMOKE_YOUTUBE_URL:=}"
: "${DATAPULSE_SMOKE_BILIBILI_URL:=}"
: "${DATAPULSE_SMOKE_TELEGRAM_URL:=}"
: "${DATAPULSE_SMOKE_RSS_URL:=}"
: "${DATAPULSE_SMOKE_WECHAT_URL:=}"
: "${DATAPULSE_SMOKE_XHS_URL:=}"
: "${REMOTE_PYTHON:=python3}"
: "${REMOTE_BOOTSTRAP_INSTALL:=0}"
: "${REMOTE_INSTALL_CMD:=$REMOTE_PYTHON -m pip install -e .}"
: "${REMOTE_HEALTH_URL:=http://127.0.0.1:18801}"
: "${REMOTE_DIRECT_SSH:=0}"

if [[ "$REMOTE_DIRECT_SSH" != "1" && ( -z "$VPS_USER" || -z "$VPS_HOST" ) ]]; then
  echo "ERROR: 请先设置 VPS_USER 与 VPS_HOST（VPS 两跳隧道要求）。"
  echo "示例: export VPS_USER=<vps-user> && export VPS_HOST=<vps-host> && export VPS_PORT=6069"
  exit 2
fi

if ! command -v sshpass >/dev/null 2>&1; then
  echo "WARN: 未检测到 sshpass，默认走纯 SSH 方式；若已配置密钥可直接运行。"
fi

exec 1> >(tee -a "$LOG_FILE")
exec 2> >(tee -a "$LOG_FILE" >&2)

echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] remote test start"
echo "RUN_ID=$RUN_ID"
echo "VPS_HOST=$VPS_HOST"
echo "MACMINI_HOST=$MACMINI_HOST"
echo "MACMINI_USER=$MACMINI_USER"
echo "REMOTE_DIRECT_SSH=$REMOTE_DIRECT_SSH"
echo "MACMINI_DATAPULSE_DIR=$MACMINI_DATAPULSE_DIR"
echo "REMOTE_PYTHON=$REMOTE_PYTHON"
echo "REMOTE_BOOTSTRAP_INSTALL=$REMOTE_BOOTSTRAP_INSTALL"
echo "REMOTE_HEALTH_URL=$REMOTE_HEALTH_URL"
echo "PLATFORMS=$PLATFORMS"

run_remote() {
  local cmd="$1"
  if [[ "$REMOTE_DIRECT_SSH" == "1" ]]; then
    if [[ -n "$MACMINI_PASSWORD" ]]; then
      sshpass -p "$MACMINI_PASSWORD" ssh -o StrictHostKeyChecking=no -p "$MACMINI_PORT" "$MACMINI_USER@$MACMINI_HOST" "$cmd"
    else
      ssh -o StrictHostKeyChecking=no -p "$MACMINI_PORT" "$MACMINI_USER@$MACMINI_HOST" "$cmd"
    fi
    return
  fi
  if [[ -n "$VPS_PASSWORD" && -n "$MACMINI_PASSWORD" ]]; then
    printf '%s\n' "$cmd" | sshpass -p "$VPS_PASSWORD" ssh -o StrictHostKeyChecking=no -p "$VPS_PORT" "$VPS_USER@$VPS_HOST" \
      "sshpass -p '$MACMINI_PASSWORD' ssh -o StrictHostKeyChecking=no -p '$MACMINI_PORT' '$MACMINI_USER@$MACMINI_HOST' 'bash -s'"
  elif [[ -n "$VPS_PASSWORD" ]]; then
    sshpass -p "$VPS_PASSWORD" ssh -o StrictHostKeyChecking=no -J "$VPS_USER@$VPS_HOST:$VPS_PORT" -p "$MACMINI_PORT" "$MACMINI_USER@$MACMINI_HOST" "$cmd"
  else
    ssh -J "$VPS_USER@$VPS_HOST:$VPS_PORT" -p "$MACMINI_PORT" "$MACMINI_USER@$MACMINI_HOST" "$cmd"
  fi
}

REMOTE_ENV=""
for v in \
  URL_1 URL_BATCH MIN_CONFIDENCE PLATFORMS DATAPULSE_SMOKE_TWITTER_URL DATAPULSE_SMOKE_REDDIT_URL \
  DATAPULSE_SMOKE_YOUTUBE_URL DATAPULSE_SMOKE_BILIBILI_URL DATAPULSE_SMOKE_TELEGRAM_URL \
  DATAPULSE_SMOKE_RSS_URL DATAPULSE_SMOKE_WECHAT_URL DATAPULSE_SMOKE_XHS_URL \
  REMOTE_PYTHON REMOTE_BOOTSTRAP_INSTALL REMOTE_INSTALL_CMD REMOTE_HEALTH_URL DATAPULSE_MIN_CONFIDENCE
do
  val="${!v-}"
  if [[ -n "$val" ]]; then
    REMOTE_ENV+="export $v=$(printf '%q' "$val"); "
  fi
done

run_remote "bash -lc '$REMOTE_ENV if [ ! -d \"$MACMINI_DATAPULSE_DIR\" ]; then echo \"[ERR] DATAPULSE_DIR_NOT_FOUND: $MACMINI_DATAPULSE_DIR\"; exit 2; fi'"
run_remote "bash -lc '$REMOTE_ENV if [ ! -f \"$MACMINI_DATAPULSE_DIR/pyproject.toml\" ]; then echo \"[ERR] PYPROJECT_MISSING: $MACMINI_DATAPULSE_DIR/pyproject.toml\"; exit 2; fi'"
run_remote "bash -lc '$REMOTE_ENV if [ ! -d \"$MACMINI_DATAPULSE_DIR/datapulse\" ]; then echo \"[ERR] PACKAGE_MISSING: $MACMINI_DATAPULSE_DIR/datapulse\"; exit 2; fi'"
run_remote "bash -lc '$REMOTE_ENV $REMOTE_PYTHON - <<\\'PY\\'\nimport sys\nif sys.version_info < (3, 10):\n    print(f\"[ERR] PYTHON_VERSION_TOO_LOW={sys.version.split()[0]}\")\n    raise SystemExit(2)\nprint(f\"[OK] PYTHON_VERSION={sys.version.split()[0]}\")\nPY'"
run_remote "bash -lc '$REMOTE_ENV $REMOTE_PYTHON --version && $REMOTE_PYTHON -m pip --version'"
if [[ "$REMOTE_BOOTSTRAP_INSTALL" == "1" ]]; then
  run_remote "bash -lc '$REMOTE_ENV if [ ! -d \"$MACMINI_DATAPULSE_DIR\" ]; then echo \"[ERR] DATAPULSE_DIR_NOT_FOUND: $MACMINI_DATAPULSE_DIR\"; exit 2; fi; cd \"$MACMINI_DATAPULSE_DIR\" && echo \"[INFO] REMOTE_BOOTSTRAP_INSTALL=$REMOTE_BOOTSTRAP_INSTALL\" && $REMOTE_INSTALL_CMD'"
fi
run_remote "bash -lc '$REMOTE_ENV cd $MACMINI_DATAPULSE_DIR && $REMOTE_PYTHON - <<\\'PY\\'\nimport datapulse\nprint(\"[OK] IMPORT datapulse\")\nPY'"
run_remote "bash -lc '$REMOTE_ENV cd $MACMINI_DATAPULSE_DIR && $REMOTE_PYTHON -m datapulse.tools.smoke --list'"
run_remote "bash -lc '$REMOTE_ENV cd $MACMINI_DATAPULSE_DIR && $REMOTE_PYTHON -m datapulse.tools.smoke --platforms $PLATFORMS --require-all --min-confidence ${MIN_CONFIDENCE}'"
run_remote "bash -lc '$REMOTE_ENV cd $MACMINI_DATAPULSE_DIR && $REMOTE_PYTHON - <<\\'PY\\'
from datapulse.reader import DataPulseReader

reader = DataPulseReader()
print(f\"sources={len(reader.list_sources(public_only=True))}\")
print(f\"packs={len(reader.list_packs(public_only=True))}\")
payload = reader.build_json_feed(limit=5, min_confidence=0.0)
print(f\"feed_items={len(payload.get('items', []))}\")
PY'"
run_remote "bash -lc '$REMOTE_ENV cd $MACMINI_DATAPULSE_DIR && $REMOTE_PYTHON -m datapulse.cli --list --limit 5 --min-confidence 0.0 || true'"
run_remote "bash -lc '$REMOTE_ENV cd $MACMINI_DATAPULSE_DIR && $REMOTE_PYTHON - <<\\'PY\\'\nimport asyncio\nimport os\nfrom datapulse.agent import DataPulseAgent\nurls = []\nfor part in [os.getenv(\"URL_1\", \"\"), os.getenv(\"URL_BATCH\", \"\")]:\n    if part.strip():\n        urls.extend(part.split())\nmsg = \" \".join(urls)\nprint(\"agent_input_count=\" + str(len(urls)))\nif msg:\n    result = asyncio.run(DataPulseAgent().handle(msg))\n    print(result)\nelse:\n    print(\"no-url\")\nPY'"
run_remote "bash -lc '$REMOTE_ENV curl -fsS ${REMOTE_HEALTH_URL}/healthz && echo && curl -fsS ${REMOTE_HEALTH_URL}/readyz | python3 -m json.tool'"

run_remote "bash -lc '$REMOTE_ENV cd $MACMINI_DATAPULSE_DIR && $REMOTE_PYTHON - <<\\'PY\\'
from datapulse.reader import DataPulseReader

reader = DataPulseReader()
print('source_profiles_default=', reader.list_subscriptions())
print('query_feed=', len(reader.query_feed(limit=3)))
PY'"

# MCP 与 Skill 快速连通（文本层，不直接启动常驻 server）
run_remote "bash -lc '$REMOTE_ENV cd $MACMINI_DATAPULSE_DIR && $REMOTE_PYTHON - <<\\'PY\\'\nimport asyncio, os\nfrom datapulse.agent import DataPulseAgent\nfrom datapulse.mcp_server import _run_read_url\n\nurl = os.getenv(\"URL_1\", \"\")\nif not url:\n    print(\"SKIP: URL_1 not set\")\nelse:\n    print(\"mcp_read_url_json\")\n    print(asyncio.run(_run_read_url(url, min_confidence=0.0)))\n    print(\"agent_ok\")\n    print(asyncio.run(DataPulseAgent(min_confidence=0.0).handle(url)))\n\nprint(\"skill_check\")\nfrom datapulse_skill import run\nprint(run(f\"请处理 {url or 'https://example.com'}\"))\nPY'"

{
  echo "# DataPulse OpenClaw 远端联测报告"
  echo "- 运行ID: $RUN_ID"
  echo "- VPS_HOST: $VPS_HOST"
  echo "- MACMINI_HOST: $MACMINI_HOST"
  echo "- MACMINI_USER: $MACMINI_USER"
  echo "- 开始时间: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "- 日志: $LOG_FILE"
} > "$REMOTE_REPORT"

echo "remote report: $REMOTE_REPORT"
echo "远端日志: $LOG_FILE"
echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] remote test done"
