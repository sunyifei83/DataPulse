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
: "${REMOTE_USE_UV:=0}"
: "${REMOTE_UV_PYTHON:=3.10}"
: "${REMOTE_BOOTSTRAP_INSTALL:=0}"
: "${REMOTE_INSTALL_CMD:=$REMOTE_PYTHON -m pip install -e .}"
: "${REMOTE_PIP_EXTRAS:=}"
: "${REMOTE_HEALTH_URL:=http://127.0.0.1:18801}"
: "${REMOTE_DIRECT_SSH:=0}"
: "${REMOTE_PYTHON_MIN_VERSION:=3.10}"
: "${REMOTE_UV_BOOTSTRAP:=0}"
: "${REMOTE_UV_LOCAL_BINARY:=$(command -v uv 2>/dev/null || true)}"
: "${REMOTE_UV_INSTALL_ROOT:=$HOME/.local/bin}"
: "${REMOTE_UV_REMOTE_BINARY:=}"
: "${REMOTE_AUTOPICK_PYTHON:=1}"
: "${REMOTE_SSH_IDENTITY:=}"
: "${REMOTE_PIP_NO_PROXY:=*}"

if [[ "$REMOTE_DIRECT_SSH" != "1" && ( -z "$VPS_USER" || -z "$VPS_HOST" ) ]]; then
  if [[ -n "$MACMINI_USER" && -n "$MACMINI_HOST" ]]; then
    REMOTE_DIRECT_SSH=1
  else
    echo "ERROR: 请先设置 VPS_USER 与 VPS_HOST（VPS 两跳隧道要求）。"
    echo "示例: export VPS_USER=<vps-user> && export VPS_HOST=<vps-host> && export VPS_PORT=6069"
    exit 2
  fi
fi

REMOTE_PIP_SAFE_ENV="env NO_PROXY=\"${REMOTE_PIP_NO_PROXY}\" HTTPS_PROXY= HTTP_PROXY= ALL_PROXY= https_proxy= http_proxy= all_proxy= PIP_NO_PROXY=\"${REMOTE_PIP_NO_PROXY}\""

infer_remote_pip_extras() {
  if [[ -n "$REMOTE_PIP_EXTRAS" ]]; then
    return
  fi
  if [[ -z "$PLATFORMS" ]]; then
    return
  fi

  local extras=()
  for platform in $PLATFORMS; do
    case "$platform" in
      telegram)
        extras+=("telegram")
        ;;
      youtube)
        extras+=("youtube")
        ;;
      wechat|xhs)
        extras+=("browser")
        ;;
    esac
  done

  if (( ${#extras[@]} > 0 )); then
    local deduped=()
    for e in "${extras[@]}"; do
      local found=0
      for existing in "${deduped[@]}"; do
        if [[ "$e" == "$existing" ]]; then
          found=1
          break
        fi
      done
      if (( found == 0 )); then
        deduped+=("$e")
      fi
    done

    REMOTE_PIP_EXTRAS="$(IFS=,; echo "${deduped[*]}")"
    echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] REMOTE_PIP_EXTRAS_AUTO=$REMOTE_PIP_EXTRAS"
  fi
}

infer_remote_pip_extras

if [[ -n "$REMOTE_PIP_EXTRAS" ]]; then
  REMOTE_INSTALL_CMD="$REMOTE_PYTHON -m pip install -e .[${REMOTE_PIP_EXTRAS}]"
fi

if [[ "$REMOTE_USE_UV" == "1" ]]; then
  if [[ -n "$REMOTE_PIP_EXTRAS" ]]; then
    REMOTE_INSTALL_CMD="uv run --project ${MACMINI_DATAPULSE_DIR} --python ${REMOTE_UV_PYTHON} -- python -m pip install -e .[${REMOTE_PIP_EXTRAS}]"
  else
    REMOTE_INSTALL_CMD="uv run --project ${MACMINI_DATAPULSE_DIR} --python ${REMOTE_UV_PYTHON} -- python -m pip install -e ."
  fi
fi

if ! command -v sshpass >/dev/null 2>&1; then
  echo "WARN: 未检测到 sshpass，默认走纯 SSH 方式；若已配置密钥可直接运行。"
fi

run_remote_capture() {
  local cmd="$1"
  cmd="$(printf '%b' "$cmd")"
  cmd="export PATH=\"\\$HOME/.local/bin:\\$PATH\"; export NO_PROXY='${REMOTE_PIP_NO_PROXY}' HTTPS_PROXY= HTTP_PROXY= ALL_PROXY= https_proxy= http_proxy= all_proxy= PIP_NO_PROXY='${REMOTE_PIP_NO_PROXY}'; $cmd"
  if [[ "$REMOTE_DIRECT_SSH" == "1" ]]; then
    if [[ -n "$MACMINI_PASSWORD" ]]; then
      sshpass -p "$MACMINI_PASSWORD" ssh -o StrictHostKeyChecking=no -o PreferredAuthentications=password -o PasswordAuthentication=yes -o PubkeyAuthentication=no -p "$MACMINI_PORT" "$MACMINI_USER@$MACMINI_HOST" "$cmd"
      return
    fi
    if [[ -n "$REMOTE_SSH_IDENTITY" ]]; then
      ssh -o StrictHostKeyChecking=no -o IdentitiesOnly=yes -i "$REMOTE_SSH_IDENTITY" -p "$MACMINI_PORT" "$MACMINI_USER@$MACMINI_HOST" "$cmd"
    else
      ssh -o StrictHostKeyChecking=no -p "$MACMINI_PORT" "$MACMINI_USER@$MACMINI_HOST" "$cmd"
    fi
    return
  fi
  if [[ -n "$VPS_PASSWORD" && -n "$MACMINI_PASSWORD" ]]; then
    printf '%s\n' "$cmd" | sshpass -p "$VPS_PASSWORD" ssh -o StrictHostKeyChecking=no -p "$VPS_PORT" "$VPS_USER@$VPS_HOST" \
      "sshpass -p '$MACMINI_PASSWORD' ssh -o StrictHostKeyChecking=no -o PreferredAuthentications=password -o PasswordAuthentication=yes -o PubkeyAuthentication=no -p '$MACMINI_PORT' '$MACMINI_USER@$MACMINI_HOST' 'bash -s'"
    return
  elif [[ -n "$VPS_PASSWORD" ]]; then
    sshpass -p "$VPS_PASSWORD" ssh -o StrictHostKeyChecking=no -o PreferredAuthentications=password -o PasswordAuthentication=yes -o PubkeyAuthentication=no -J "$VPS_USER@$VPS_HOST:$VPS_PORT" -p "$MACMINI_PORT" "$MACMINI_USER@$MACMINI_HOST" "$cmd"
    return
  fi
  if [[ -n "$REMOTE_SSH_IDENTITY" ]]; then
    ssh -J "$VPS_USER@$VPS_HOST:$VPS_PORT" -i "$REMOTE_SSH_IDENTITY" -o IdentitiesOnly=yes -p "$MACMINI_PORT" "$MACMINI_USER@$MACMINI_HOST" "$cmd"
  else
    ssh -J "$VPS_USER@$VPS_HOST:$VPS_PORT" -p "$MACMINI_PORT" "$MACMINI_USER@$MACMINI_HOST" "$cmd"
  fi
}

resolve_remote_python() {
  if [[ "$REMOTE_AUTOPICK_PYTHON" != "1" ]]; then
    return
  fi
  local selected_py=""
  local candidates="${REMOTE_PYTHON} python3.12 python3.11 python3.10 python3.9 python3"
  local python_probe_b64
  python_probe_b64="$(cat <<'PY' | base64 | tr -d '\n'
import os
import shutil
import subprocess

req = os.environ.get('REQ', '3.10')
try:
    min_major, min_minor = (int(x) for x in req.split('.')[:2])
except Exception:
    min_major, min_minor = 3, 10

seen = set()
for raw in os.environ.get('CANDIDATES', '').split():
    if raw in seen:
        continue
    seen.add(raw)
    path = shutil.which(raw)
    if not path:
        continue
    try:
        ver = subprocess.check_output(
            [path, '-c', 'import sys; print(f\"{sys.version_info[0]}.{sys.version_info[1]}\")'],
            text=True,
            stderr=subprocess.STDOUT,
        ).strip()
        major, minor = (int(x) for x in ver.split('.')[:2])
        if (major, minor) >= (min_major, min_minor):
            print(raw)
            raise SystemExit(0)
    except Exception:
        continue
PY
)"
  selected_py="$(run_remote_capture "REQ='${REMOTE_PYTHON_MIN_VERSION}' CANDIDATES='${candidates}' python3 -c \"import os, base64; exec(base64.b64decode('${python_probe_b64}').decode())\" || true" )"

  if [[ -n "$selected_py" ]]; then
    REMOTE_PYTHON="$selected_py"
    echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] REMOTE_PYTHON_SELECTED=$REMOTE_PYTHON"
  else
    echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] WARN REMOTE_PYTHON_SELECTED_EMPTY: keep env REMOTE_PYTHON=$REMOTE_PYTHON"
  fi
}

resolve_remote_datapulse_dir() {
  local selected_dir=""
  local seed_candidates="${MACMINI_DATAPULSE_DIR}|${MACMINI_DATAPULSE_DIR%/}/DataPulse|${MACMINI_DATAPULSE_DIR%/}/datapulse|${MACMINI_DATAPULSE_DIR%/}/../DataPulse"
  local path_probe_b64
  path_probe_b64="$(cat <<'PY' | base64 | tr -d '\n'
import os
from pathlib import Path

seed_values = os.environ.get("SEED_CANDIDATES", "").split("|")
cands = []
for item in seed_values:
    item = item.strip()
    if item and item not in cands:
        cands.append(item)

cands.extend([
    str(Path.home() / ".openclaw" / "workspace" / "DataPulse"),
    str(Path.home() / ".openclaw" / "workspace"),
    str(Path.home() / ".openclaw"),
])

for raw in cands:
    path = Path(raw).expanduser()
    if (path / "pyproject.toml").is_file() and (path / "datapulse").is_dir():
        print(str(path))
        break
PY
)"
  selected_dir="$(run_remote_capture "SEED_CANDIDATES='${seed_candidates}' python3 -c \"import os, base64; exec(base64.b64decode('${path_probe_b64}').decode())\" || true")"
  if [[ -n "$selected_dir" ]]; then
    if [[ "$selected_dir" != "$MACMINI_DATAPULSE_DIR" ]]; then
      echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] MACMINI_DATAPULSE_DIR_RESCUE=$selected_dir"
      MACMINI_DATAPULSE_DIR="$selected_dir"
    fi
  else
    echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] WARN MACMINI_DATAPULSE_DIR_NOT_FOUND=$MACMINI_DATAPULSE_DIR"
  fi
}

exec 1> >(tee -a "$LOG_FILE")
exec 2> >(tee -a "$LOG_FILE" >&2)

echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] remote test start"
echo "RUN_ID=$RUN_ID"
echo "VPS_HOST=$VPS_HOST"
echo "MACMINI_HOST=$MACMINI_HOST"
echo "MACMINI_USER=$MACMINI_USER"
echo "REMOTE_DIRECT_SSH=$REMOTE_DIRECT_SSH"
echo "REMOTE_USE_UV=$REMOTE_USE_UV"
echo "REMOTE_UV_PYTHON=$REMOTE_UV_PYTHON"
echo "REMOTE_UV_BOOTSTRAP=$REMOTE_UV_BOOTSTRAP"
echo "REMOTE_UV_INSTALL_ROOT=$REMOTE_UV_INSTALL_ROOT"
echo "MACMINI_DATAPULSE_DIR=$MACMINI_DATAPULSE_DIR"
echo "REMOTE_PYTHON=$REMOTE_PYTHON"
echo "REMOTE_AUTOPICK_PYTHON=$REMOTE_AUTOPICK_PYTHON"
echo "REMOTE_BOOTSTRAP_INSTALL=$REMOTE_BOOTSTRAP_INSTALL"
echo "REMOTE_HEALTH_URL=$REMOTE_HEALTH_URL"
echo "PLATFORMS=$PLATFORMS"

resolve_remote_python
resolve_remote_datapulse_dir

run_remote() {
  local cmd="$1"
  cmd="$(printf '%b' "$cmd")"
  cmd="export PATH=\"\\$HOME/.local/bin:\\$PATH\"; export NO_PROXY='${REMOTE_PIP_NO_PROXY}' HTTPS_PROXY= HTTP_PROXY= ALL_PROXY= https_proxy= http_proxy= all_proxy= PIP_NO_PROXY='${REMOTE_PIP_NO_PROXY}'; $cmd"
  if [[ "$REMOTE_DIRECT_SSH" == "1" ]]; then
    if [[ -n "$MACMINI_PASSWORD" ]]; then
      sshpass -p "$MACMINI_PASSWORD" ssh -o StrictHostKeyChecking=no -o PreferredAuthentications=password -o PasswordAuthentication=yes -o PubkeyAuthentication=no -p "$MACMINI_PORT" "$MACMINI_USER@$MACMINI_HOST" "$cmd"
    else
      ssh -o StrictHostKeyChecking=no -p "$MACMINI_PORT" "$MACMINI_USER@$MACMINI_HOST" "$cmd"
    fi
    return
  fi
  if [[ -n "$VPS_PASSWORD" && -n "$MACMINI_PASSWORD" ]]; then
    printf '%s\n' "$cmd" | sshpass -p "$VPS_PASSWORD" ssh -o StrictHostKeyChecking=no -p "$VPS_PORT" "$VPS_USER@$VPS_HOST" \
      "sshpass -p '$MACMINI_PASSWORD' ssh -o StrictHostKeyChecking=no -o PreferredAuthentications=password -o PasswordAuthentication=yes -o PubkeyAuthentication=no -p '$MACMINI_PORT' '$MACMINI_USER@$MACMINI_HOST' 'bash -s'"
  elif [[ -n "$VPS_PASSWORD" ]]; then
    sshpass -p "$VPS_PASSWORD" ssh -o StrictHostKeyChecking=no -o PreferredAuthentications=password -o PasswordAuthentication=yes -o PubkeyAuthentication=no -J "$VPS_USER@$VPS_HOST:$VPS_PORT" -p "$MACMINI_PORT" "$MACMINI_USER@$MACMINI_HOST" "$cmd"
  else
    ssh -J "$VPS_USER@$VPS_HOST:$VPS_PORT" -p "$MACMINI_PORT" "$MACMINI_USER@$MACMINI_HOST" "$cmd"
  fi
}

bootstrap_uv_direct() {
  if [[ "$REMOTE_UV_BOOTSTRAP" != "1" ]]; then
    return
  fi
  if [[ "$REMOTE_DIRECT_SSH" != "1" ]]; then
    return
  fi

  local local_uv="$REMOTE_UV_LOCAL_BINARY"
  local remote_uv_platform=""
  if [[ -z "$local_uv" || ! -x "$local_uv" ]]; then
    return
  fi

  local remote_home="$HOME"
  if [[ -n "${MACMINI_PASSWORD}" ]]; then
    remote_home="$(sshpass -p "${MACMINI_PASSWORD}" ssh -o StrictHostKeyChecking=no -o PreferredAuthentications=password -o PasswordAuthentication=yes -o PubkeyAuthentication=no -p "$MACMINI_PORT" "$MACMINI_USER@$MACMINI_HOST" 'printf %s "$HOME"')"
    remote_uv_platform="$(sshpass -p "${MACMINI_PASSWORD}" ssh -o StrictHostKeyChecking=no -o PreferredAuthentications=password -o PasswordAuthentication=yes -o PubkeyAuthentication=no -p "$MACMINI_PORT" "$MACMINI_USER@$MACMINI_HOST" 'printf %s "$(uname -s)-$(uname -m)"')"
  else
    remote_home="$(ssh -o StrictHostKeyChecking=no -p "$MACMINI_PORT" "$MACMINI_USER@$MACMINI_HOST" 'printf %s "$HOME"')"
    remote_uv_platform="$(ssh -o StrictHostKeyChecking=no -p "$MACMINI_PORT" "$MACMINI_USER@$MACMINI_HOST" 'printf %s "$(uname -s)-$(uname -m)"')"
  fi
  local local_uv_platform
  local_uv_platform="$(uname -s)-$(uname -m)"
  if [[ -n "$remote_uv_platform" && "$remote_uv_platform" != "$local_uv_platform" ]]; then
    echo "[WARN] UV_LOCAL_BINARY_COPY_FAIL: platform_mismatch local=$local_uv_platform remote=$remote_uv_platform"
    return
  fi

  local remote_uv_root="$REMOTE_UV_INSTALL_ROOT"
  if [[ "$remote_uv_root" == "$HOME/"* ]]; then
    remote_uv_root="$remote_home${remote_uv_root#$HOME}"
  elif [[ "$remote_uv_root" == "~/"* ]]; then
    remote_uv_root="$remote_home/.local/bin"
  fi
  REMOTE_UV_REMOTE_BINARY="$remote_uv_root/uv"

  echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] UV_LOCAL_BINARY_COPY_START local=$local_uv remote_root=$remote_uv_root"
  if [[ -n "${MACMINI_PASSWORD}" ]]; then
    sshpass -p "${MACMINI_PASSWORD}" ssh -o StrictHostKeyChecking=no -o PreferredAuthentications=password -o PasswordAuthentication=yes -o PubkeyAuthentication=no -p "$MACMINI_PORT" "$MACMINI_USER@$MACMINI_HOST" "mkdir -p \"$remote_uv_root\""
  else
    ssh -o StrictHostKeyChecking=no -p "$MACMINI_PORT" "$MACMINI_USER@$MACMINI_HOST" "mkdir -p \"$remote_uv_root\""
  fi
  if [[ -n "${MACMINI_PASSWORD}" ]]; then
    if ! sshpass -p "${MACMINI_PASSWORD}" scp -o StrictHostKeyChecking=no -o PreferredAuthentications=password -o PasswordAuthentication=yes -o PubkeyAuthentication=no -P "$MACMINI_PORT" "$local_uv" "$MACMINI_USER@$MACMINI_HOST:$remote_uv_root/"; then
      echo "[WARN] UV_LOCAL_BINARY_COPY_FAIL: scp_failed"
      REMOTE_UV_REMOTE_BINARY=""
      return
    fi
  else
    if ! scp -o StrictHostKeyChecking=no -P "$MACMINI_PORT" "$local_uv" "$MACMINI_USER@$MACMINI_HOST:$remote_uv_root/"; then
      echo "[WARN] UV_LOCAL_BINARY_COPY_FAIL: scp_failed"
      REMOTE_UV_REMOTE_BINARY=""
      return
    fi
  fi
  run_remote "bash -lc '$REMOTE_ENV chmod +x \"$REMOTE_UV_REMOTE_BINARY\"; [ -x \"$REMOTE_UV_REMOTE_BINARY\" ] || echo \"[WARN] UV_LOCAL_BINARY_COPY_FAIL: chmod_or_exec_missing\"'"
}

REMOTE_ENV=""
for v in \
  URL_1 URL_BATCH MIN_CONFIDENCE PLATFORMS DATAPULSE_SMOKE_TWITTER_URL DATAPULSE_SMOKE_REDDIT_URL \
  DATAPULSE_SMOKE_YOUTUBE_URL DATAPULSE_SMOKE_BILIBILI_URL DATAPULSE_SMOKE_TELEGRAM_URL \
  DATAPULSE_SMOKE_RSS_URL DATAPULSE_SMOKE_WECHAT_URL DATAPULSE_SMOKE_XHS_URL \
  REMOTE_PYTHON REMOTE_PYTHON_MIN_VERSION REMOTE_BOOTSTRAP_INSTALL REMOTE_INSTALL_CMD \
  REMOTE_HEALTH_URL DATAPULSE_MIN_CONFIDENCE REMOTE_UV_BOOTSTRAP
do
  val="${!v-}"
  if [[ -n "$val" ]]; then
    REMOTE_ENV+="export $v=$(printf '%q' "$val"); "
  fi
done

if [[ -n "$REMOTE_PIP_EXTRAS" ]]; then
  REMOTE_ENV+="export REMOTE_PIP_EXTRAS=$(printf '%q' "$REMOTE_PIP_EXTRAS"); "
fi

bootstrap_uv_direct
echo "REMOTE_UV_REMOTE_BINARY=$REMOTE_UV_REMOTE_BINARY"
run_remote "bash -lc '$REMOTE_ENV if [ ! -d \"$MACMINI_DATAPULSE_DIR\" ]; then echo \"[ERR] DATAPULSE_DIR_NOT_FOUND: $MACMINI_DATAPULSE_DIR\"; exit 2; fi'"
run_remote "bash -lc '$REMOTE_ENV if [ ! -f \"$MACMINI_DATAPULSE_DIR/pyproject.toml\" ]; then echo \"[ERR] PYPROJECT_MISSING: $MACMINI_DATAPULSE_DIR/pyproject.toml\"; exit 2; fi'"
run_remote "bash -lc '$REMOTE_ENV if [ ! -d \"$MACMINI_DATAPULSE_DIR/datapulse\" ]; then echo \"[ERR] PACKAGE_MISSING: $MACMINI_DATAPULSE_DIR/datapulse\"; exit 2; fi'"
if [[ "$REMOTE_USE_UV" == "1" ]]; then
  if [[ "$REMOTE_UV_BOOTSTRAP" == "1" ]]; then
    run_remote "bash -lc '$REMOTE_ENV if [ -n \"$REMOTE_UV_REMOTE_BINARY\" ] && [ -x \"$REMOTE_UV_REMOTE_BINARY\" ]; then $REMOTE_UV_REMOTE_BINARY --version; else echo \"[INFO] UV_BOOTSTRAP_START\"; $REMOTE_PIP_SAFE_ENV $REMOTE_PYTHON -m pip install --user uv; if [ -n \"$REMOTE_UV_REMOTE_BINARY\" ] && [ -x \"$REMOTE_UV_REMOTE_BINARY\" ]; then $REMOTE_UV_REMOTE_BINARY --version; elif command -v uv >/dev/null 2>&1; then uv --version; elif $REMOTE_PYTHON -m uv --version >/dev/null 2>&1; then $REMOTE_PYTHON -m uv --version; else echo \"[ERR] UV_NOT_FOUND\"; exit 2; fi; fi'"
  else
    run_remote "bash -lc '$REMOTE_ENV if ! command -v uv >/dev/null 2>&1; then echo \"[ERR] UV_NOT_FOUND\"; exit 2; fi; uv --version'"
  fi
fi
run_remote "bash -lc '$REMOTE_ENV $REMOTE_PYTHON - <<PY\nimport os\nimport sys\nmin_version = tuple(int(x) for x in os.getenv(\"REMOTE_PYTHON_MIN_VERSION\", \"3.10\").split(\".\")[:2])\nif sys.version_info[:2] < min_version:\n    print(f\"[ERR] PYTHON_VERSION_TOO_LOW={sys.version.split()[0]}\")\n    raise SystemExit(2)\nprint(f\"[OK] PYTHON_VERSION={sys.version.split()[0]}\")\nPY'"
run_remote "bash -lc '$REMOTE_ENV $REMOTE_PYTHON --version && $REMOTE_PYTHON -m pip --version'"
if [[ "$REMOTE_BOOTSTRAP_INSTALL" == "1" ]]; then
run_remote "bash -lc '$REMOTE_ENV if [ ! -d \"$MACMINI_DATAPULSE_DIR\" ]; then echo \"[ERR] DATAPULSE_DIR_NOT_FOUND: $MACMINI_DATAPULSE_DIR\"; exit 2; fi; cd \"$MACMINI_DATAPULSE_DIR\" && echo \"[INFO] REMOTE_BOOTSTRAP_INSTALL=$REMOTE_BOOTSTRAP_INSTALL\" && $REMOTE_PIP_SAFE_ENV $REMOTE_INSTALL_CMD'"
fi
run_remote "bash -lc '$REMOTE_ENV cd $MACMINI_DATAPULSE_DIR && $REMOTE_PYTHON - <<PY\nimport datapulse\nprint(\"[OK] IMPORT datapulse\")\nPY'"
run_remote "bash -lc '$REMOTE_ENV cd $MACMINI_DATAPULSE_DIR && $REMOTE_PYTHON -m datapulse.tools.smoke --list'"
run_remote "bash -lc '$REMOTE_ENV cd $MACMINI_DATAPULSE_DIR && $REMOTE_PYTHON -m datapulse.tools.smoke --platforms $PLATFORMS --require-all --min-confidence ${MIN_CONFIDENCE}'"
run_remote "bash -lc '$REMOTE_ENV cd $MACMINI_DATAPULSE_DIR && $REMOTE_PYTHON - <<PY
from datapulse.reader import DataPulseReader

reader = DataPulseReader()
print(f\"sources={len(reader.list_sources(public_only=True))}\")
print(f\"packs={len(reader.list_packs(public_only=True))}\")
payload = reader.build_json_feed(limit=5, min_confidence=0.0)
PY'"
run_remote "bash -lc '$REMOTE_ENV cd $MACMINI_DATAPULSE_DIR && $REMOTE_PYTHON -m datapulse.cli --list --limit 5 --min-confidence 0.0 || true'"
run_remote "bash -lc '$REMOTE_ENV cd $MACMINI_DATAPULSE_DIR && $REMOTE_PYTHON - <<PY\nimport asyncio\nimport os\nfrom datapulse.agent import DataPulseAgent\nurls = []\nfor part in [os.getenv(\"URL_1\", \"\"), os.getenv(\"URL_BATCH\", \"\")]:\n    if part.strip():\n        urls.extend(part.split())\nmsg = \" \".join(urls)\nprint(\"agent_input_count=\" + str(len(urls)))\nif msg:\n    result = asyncio.run(DataPulseAgent().handle(msg))\n    print(result)\nelse:\n    print(\"no-url\")\nPY'"
run_remote "bash -lc '$REMOTE_ENV curl -fsS ${REMOTE_HEALTH_URL}/healthz && echo && curl -fsS ${REMOTE_HEALTH_URL}/readyz | python3 -m json.tool'"

run_remote "bash -lc '$REMOTE_ENV cd $MACMINI_DATAPULSE_DIR && $REMOTE_PYTHON - <<PY
from datapulse.reader import DataPulseReader

reader = DataPulseReader()
print(\"source_profiles_default=\", reader.list_subscriptions())
print(\"query_feed=\", len(reader.query_feed(limit=3)))
PY'"

# MCP 与 Skill 快速连通（文本层，不直接启动常驻 server）
run_remote "bash -lc '$REMOTE_ENV cd $MACMINI_DATAPULSE_DIR && $REMOTE_PYTHON - <<PY\nimport asyncio, os\nfrom datapulse.agent import DataPulseAgent\nfrom datapulse.mcp_server import _run_read_url\n\nurl = os.getenv(\"URL_1\", \"\")\nif not url:\n    print(\"SKIP: URL_1 not set\")\nelse:\n    print(\"mcp_read_url_json\")\n    print(asyncio.run(_run_read_url(url, min_confidence=0.0)))\n    print(\"agent_ok\")\n    print(asyncio.run(DataPulseAgent(min_confidence=0.0).handle(url)))\n\nprint(\"skill_check\")\nfrom datapulse_skill import run\nprint(run(f\"请处理 {url}\"))\nPY'"

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
