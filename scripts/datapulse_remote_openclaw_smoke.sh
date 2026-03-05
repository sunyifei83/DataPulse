#!/usr/bin/env bash
set -euo pipefail

for env_file in ".env.openclaw.local" ".env.openclaw" ".env.local" ".env.secret" ".env"; do
  if [[ -f "$env_file" ]]; then
    set -a
    source "$env_file"
    set +a
    break
  fi
done

RUN_ID="${RUN_ID:-$(date +%Y%m%d_%H%M%S)}"
OUT_DIR="${OUT_DIR:-$(pwd)/artifacts}"
RUN_LOG_DIR="$OUT_DIR/openclaw_datapulse_${RUN_ID}"
mkdir -p "$RUN_LOG_DIR"
LOG_FILE="$RUN_LOG_DIR/remote_test.log"
REMOTE_REPORT="$RUN_LOG_DIR/remote_report.md"
TRACE_FILE="$LOG_FILE"

: "${VPS_USER:=}"
: "${VPS_HOST:=}"
: "${VPS_PASSWORD:=}"
: "${MACMINI_USER:=$USER}"
: "${MACMINI_HOST:=127.0.0.1}"
: "${MACMINI_HOST_CANDIDATES:=$MACMINI_HOST}"
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
: "${SSH_CONNECT_TIMEOUT:=8}"
: "${REMOTE_ABORT_ON_CONNECT_FAIL:=1}"

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
    local -a deduped=()
    for e in "${extras[@]}"; do
      local found=0
      for existing in "${deduped[@]-}"; do
        if [[ "$e" == "$existing" ]]; then
          found=1
          break
        fi
      done
      if (( found == 0 )); then
        deduped+=("$e")
      fi
    done

    REMOTE_PIP_EXTRAS="$(IFS=,; echo "${deduped[*]-}")"
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
      sshpass -p "$MACMINI_PASSWORD" ssh -o StrictHostKeyChecking=no -o ConnectTimeout="$SSH_CONNECT_TIMEOUT" -o PreferredAuthentications=password -o PasswordAuthentication=yes -o PubkeyAuthentication=no -p "$MACMINI_PORT" "$MACMINI_USER@$MACMINI_HOST" "$cmd"
      return
    fi
    if [[ -n "$REMOTE_SSH_IDENTITY" ]]; then
      ssh -o StrictHostKeyChecking=no -o ConnectTimeout="$SSH_CONNECT_TIMEOUT" -o IdentitiesOnly=yes -i "$REMOTE_SSH_IDENTITY" -p "$MACMINI_PORT" "$MACMINI_USER@$MACMINI_HOST" "$cmd"
    else
      ssh -o StrictHostKeyChecking=no -o ConnectTimeout="$SSH_CONNECT_TIMEOUT" -p "$MACMINI_PORT" "$MACMINI_USER@$MACMINI_HOST" "$cmd"
    fi
    return
  fi
  if [[ -n "$VPS_PASSWORD" && -n "$MACMINI_PASSWORD" ]]; then
    printf '%s\n' "$cmd" | sshpass -p "$VPS_PASSWORD" ssh -o StrictHostKeyChecking=no -o ConnectTimeout="$SSH_CONNECT_TIMEOUT" -p "$VPS_PORT" "$VPS_USER@$VPS_HOST" \
      "sshpass -p '$MACMINI_PASSWORD' ssh -o StrictHostKeyChecking=no -o ConnectTimeout=$SSH_CONNECT_TIMEOUT -o PreferredAuthentications=password -o PasswordAuthentication=yes -o PubkeyAuthentication=no -p '$MACMINI_PORT' '$MACMINI_USER@$MACMINI_HOST' 'bash -s'"
    return
  elif [[ -n "$VPS_PASSWORD" ]]; then
    sshpass -p "$VPS_PASSWORD" ssh -o StrictHostKeyChecking=no -o ConnectTimeout="$SSH_CONNECT_TIMEOUT" -o PreferredAuthentications=password -o PasswordAuthentication=yes -o PubkeyAuthentication=no -J "$VPS_USER@$VPS_HOST:$VPS_PORT" -p "$MACMINI_PORT" "$MACMINI_USER@$MACMINI_HOST" "$cmd"
    return
  fi
  if [[ -n "$REMOTE_SSH_IDENTITY" ]]; then
    ssh -J "$VPS_USER@$VPS_HOST:$VPS_PORT" -o StrictHostKeyChecking=no -o ConnectTimeout="$SSH_CONNECT_TIMEOUT" -i "$REMOTE_SSH_IDENTITY" -o IdentitiesOnly=yes -p "$MACMINI_PORT" "$MACMINI_USER@$MACMINI_HOST" "$cmd"
  else
    ssh -J "$VPS_USER@$VPS_HOST:$VPS_PORT" -o StrictHostKeyChecking=no -o ConnectTimeout="$SSH_CONNECT_TIMEOUT" -p "$MACMINI_PORT" "$MACMINI_USER@$MACMINI_HOST" "$cmd"
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
  if ! selected_py="$(run_remote_capture "REQ='${REMOTE_PYTHON_MIN_VERSION}' CANDIDATES='${candidates}' python3 -c \"import os, base64; exec(base64.b64decode('${python_probe_b64}').decode())\" || true" )"; then
    echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] WARN REMOTE_PYTHON_PROBE_FAILED"
    selected_py=""
  fi

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
  if ! selected_dir="$(run_remote_capture "SEED_CANDIDATES='${seed_candidates}' python3 -c \"import os, base64; exec(base64.b64decode('${path_probe_b64}').decode())\" || true")"; then
    echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] WARN REMOTE_DATAPULSE_DIR_PROBE_FAILED"
    selected_dir=""
  fi
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
echo "MACMINI_HOST_CANDIDATES=$MACMINI_HOST_CANDIDATES"
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
      sshpass -p "$MACMINI_PASSWORD" ssh -o StrictHostKeyChecking=no -o ConnectTimeout="$SSH_CONNECT_TIMEOUT" -o PreferredAuthentications=password -o PasswordAuthentication=yes -o PubkeyAuthentication=no -p "$MACMINI_PORT" "$MACMINI_USER@$MACMINI_HOST" "$cmd"
    else
      ssh -o StrictHostKeyChecking=no -o ConnectTimeout="$SSH_CONNECT_TIMEOUT" -p "$MACMINI_PORT" "$MACMINI_USER@$MACMINI_HOST" "$cmd"
    fi
    return
  fi
  if [[ -n "$VPS_PASSWORD" && -n "$MACMINI_PASSWORD" ]]; then
    printf '%s\n' "$cmd" | sshpass -p "$VPS_PASSWORD" ssh -o StrictHostKeyChecking=no -o ConnectTimeout="$SSH_CONNECT_TIMEOUT" -p "$VPS_PORT" "$VPS_USER@$VPS_HOST" \
      "sshpass -p '$MACMINI_PASSWORD' ssh -o StrictHostKeyChecking=no -o ConnectTimeout=$SSH_CONNECT_TIMEOUT -o PreferredAuthentications=password -o PasswordAuthentication=yes -o PubkeyAuthentication=no -p '$MACMINI_PORT' '$MACMINI_USER@$MACMINI_HOST' 'bash -s'"
  elif [[ -n "$VPS_PASSWORD" ]]; then
    sshpass -p "$VPS_PASSWORD" ssh -o StrictHostKeyChecking=no -o ConnectTimeout="$SSH_CONNECT_TIMEOUT" -o PreferredAuthentications=password -o PasswordAuthentication=yes -o PubkeyAuthentication=no -J "$VPS_USER@$VPS_HOST:$VPS_PORT" -p "$MACMINI_PORT" "$MACMINI_USER@$MACMINI_HOST" "$cmd"
  else
    ssh -J "$VPS_USER@$VPS_HOST:$VPS_PORT" -o StrictHostKeyChecking=no -o ConnectTimeout="$SSH_CONNECT_TIMEOUT" -p "$MACMINI_PORT" "$MACMINI_USER@$MACMINI_HOST" "$cmd"
  fi
}

REMOTE_STEP_TOTAL=0
REMOTE_STEP_FAILED=0
declare -a REMOTE_STEP_RESULTS=()
declare -a REMOTE_BLOCK_CODES=()

_add_block_code() {
  local code="$1"
  for code_item in "${REMOTE_BLOCK_CODES[@]-}"; do
    if [[ "$code_item" == "$code" ]]; then
      return
    fi
  done
  REMOTE_BLOCK_CODES+=("$code")
}

_collect_block_codes() {
  local output="$1"
  local candidate
  local candidates=(
    DATAPULSE_DIR_NOT_FOUND
    PYPROJECT_MISSING
    PACKAGE_MISSING
    PYTHON_VERSION_TOO_LOW
    UV_NOT_FOUND
    UV_LOCAL_BINARY_COPY_FAIL
    IMPORT_FAILED
    BUILD_DEPENDENCY_PROXY_FAIL
    REMOTE_PLATFORM_DEPENDENCY_MISSING
    SSH_CONNECTION_REFUSED
    SSH_HOST_KEY_UNKNOWN
    SSH_AUTH_FAILED
  )
  for candidate in "${candidates[@]}"; do
    if [[ "$output" == *"$candidate"* ]]; then
      _add_block_code "$candidate"
    fi
  done
  if [[ "$output" == *"ProxyError"* || "$output" == *"Could not connect to proxy"* || "$output" == *"proxyconnect"* ]]; then
    _add_block_code "BUILD_DEPENDENCY_PROXY_FAIL"
  fi
  if [[ "$output" == *"Connection refused"* || "$output" == *"No route to host"* ]]; then
    _add_block_code "SSH_CONNECTION_REFUSED"
  fi
  if [[ "$output" == *"Could not resolve host"* ]]; then
    _add_block_code "SSH_HOST_KEY_UNKNOWN"
  fi
  if [[ "$output" == *"Permission denied"* || "$output" == *"Authentication failed"* ]]; then
    _add_block_code "SSH_AUTH_FAILED"
  fi
}

_remediation_for_code() {
  case "$1" in
    DATAPULSE_DIR_NOT_FOUND)
      cat <<'MSG'
修复动作（优先级高）：
- 检查 `MACMINI_DATAPULSE_DIR` 是否指向源码根（需包含 `pyproject.toml` 与 `datapulse/`）。
- 建议优先执行 `ls "$MACMINI_DATAPULSE_DIR"` 与 `ls "$MACMINI_DATAPULSE_DIR/datapulse"`，确认无误后重试。
- 若路径偏移，保留 `MACMINI_DATAPULSE_DIR` 为空让脚本自动探测 `.../DataPulse`。
MSG
      ;;
    PYPROJECT_MISSING)
      cat <<'MSG'
修复动作（优先级高）：
- 目标路径未检测到 `pyproject.toml`，请改为仓库源码根目录。
- 推荐：`export MACMINI_DATAPULSE_DIR=<repo_root>`。
MSG
      ;;
    PACKAGE_MISSING)
      cat <<'MSG'
修复动作（优先级高）：
- 当前路径下缺少 `datapulse/`，说明未切到源码根（常见是跳到上级目录/安装目录）。
- 建议设置：`MACMINI_DATAPULSE_DIR` 指向源码根，或确认 `ls "$MACMINI_DATAPULSE_DIR/datapulse"` 可见后重试。
MSG
      ;;
    PYTHON_VERSION_TOO_LOW)
      cat <<'MSG'
修复动作（优先级高）：
- 远端 Python < 3.10，需切到 3.10+ 解释器。
- 建议：`export REMOTE_PYTHON=python3.11` 或保持 `REMOTE_AUTOPICK_PYTHON=1` 自动兜底。
- 如无本地版本，先 `python3 -m venv ~/.venv/datapulse && source ~/.venv/datapulse/bin/activate` 后重试。
MSG
      ;;
    UV_NOT_FOUND)
      cat <<'MSG'
修复动作：
- 远端未检测到 `uv`，建议 `export REMOTE_USE_UV=0` 使用传统 pip，或在远端 `python3 -m pip install --user uv`。
MSG
      ;;
    UV_LOCAL_BINARY_COPY_FAIL|BUILD_DEPENDENCY_PROXY_FAIL)
      cat <<'MSG'
修复动作：
- 检查代理设置与依赖下载链路：
  - 建议运行前确保 `REMOTE_PIP_NO_PROXY=*`。
  - 若出现代理错误，可执行 `export REMOTE_PIP_NO_PROXY="*"`，必要时 `unset HTTPS_PROXY HTTP_PROXY ALL_PROXY`.
- `REMOTE_UV_BOOTSTRAP=1` 或 `REMOTE_PIP_SAFE_ENV` 已内置隔离，可再次运行尝试。
MSG
      ;;
    SSH_CONNECTION_REFUSED)
      cat <<'MSG'
修复动作：
- 先确认 macmini SSH 服务是否启动（默认 22），并测试本机：
  - `ssh -p ${MACMINI_PORT} ${MACMINI_USER}@${MACMINI_HOST}`
- 若本机无服务，检查 SSH 启动状态或切换内网直连端口设置。
MSG
      ;;
    SSH_HOST_KEY_UNKNOWN)
      cat <<'MSG'
修复动作：
- 修复主机名解析与跳链路：
  - 确认 VPS_HOST / MACMINI_HOST 可解析。
  - 使用 `ping` / `ssh -J ...` 验证连通性后再重试。
MSG
      ;;
    SSH_AUTH_FAILED)
      cat <<'MSG'
修复动作：
- 认证失败常见于口令/密钥不匹配或禁用口令。
- 建议优先确认 `MACMINI_PASSWORD`/`REMOTE_SSH_IDENTITY`，并验证 `ssh -v` 输出定位失败位点。
MSG
      ;;
    IMPORT_FAILED)
      cat <<'MSG'
修复动作：
- 依赖未就绪导致 `import datapulse` 失败。
- 建议设置 `REMOTE_BOOTSTRAP_INSTALL=1`，并按平台补齐 `REMOTE_PIP_EXTRAS`（如 `telegram,youtube,browser`）。
- 重跑后关注 `pip install -e .` 的报错行。
MSG
      ;;
    REMOTE_PLATFORM_DEPENDENCY_MISSING)
      cat <<'MSG'
修复动作：
- 平台级 collector 依赖缺失，建议根据失败平台补齐 `REMOTE_PIP_EXTRAS` 后重试（如 `telegram` / `youtube` / `browser`）。
MSG
      ;;
    *)
      echo "修复动作：请对照阻断阶段日志定位根因后重试本脚本。"
      ;;
  esac
}

run_remote_step() {
  local name="$1"
  local required="${2:-1}"
  local cmd="$3"
  local output
  local rc
  local stamp

  REMOTE_STEP_TOTAL=$((REMOTE_STEP_TOTAL + 1))
  stamp="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "[$stamp] [STEP $REMOTE_STEP_TOTAL] $name" | tee -a "$TRACE_FILE"

  set +e
  output="$(run_remote "$cmd" 2>&1)"
  rc=$?
  set -e

  if [[ -n "$output" ]]; then
    printf '%s\n' "$output" | tee -a "$TRACE_FILE"
  fi
  if (( rc == 0 )); then
    REMOTE_STEP_RESULTS+=("PASS|$name")
    echo "[$stamp] [STEP $REMOTE_STEP_TOTAL] PASS" | tee -a "$TRACE_FILE"
    return 0
  fi

  if (( required == 0 )); then
    REMOTE_STEP_RESULTS+=("OPTIONAL_FAIL|$name|$rc")
    echo "[$stamp] [STEP $REMOTE_STEP_TOTAL] FAIL(optional) rc=$rc" | tee -a "$TRACE_FILE"
    return 0
  fi

  REMOTE_STEP_FAILED=$((REMOTE_STEP_FAILED + 1))
  REMOTE_STEP_RESULTS+=("FAIL|$name|$rc")
  echo "[$stamp] [STEP $REMOTE_STEP_TOTAL] FAIL rc=$rc" | tee -a "$TRACE_FILE"
  _collect_block_codes "$output"
  return 0
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
    remote_home="$(sshpass -p "${MACMINI_PASSWORD}" ssh -o StrictHostKeyChecking=no -o ConnectTimeout="$SSH_CONNECT_TIMEOUT" -o PreferredAuthentications=password -o PasswordAuthentication=yes -o PubkeyAuthentication=no -p "$MACMINI_PORT" "$MACMINI_USER@$MACMINI_HOST" 'printf %s "$HOME"')"
    remote_uv_platform="$(sshpass -p "${MACMINI_PASSWORD}" ssh -o StrictHostKeyChecking=no -o ConnectTimeout="$SSH_CONNECT_TIMEOUT" -o PreferredAuthentications=password -o PasswordAuthentication=yes -o PubkeyAuthentication=no -p "$MACMINI_PORT" "$MACMINI_USER@$MACMINI_HOST" 'printf %s "$(uname -s)-$(uname -m)"')"
  else
    remote_home="$(ssh -o StrictHostKeyChecking=no -o ConnectTimeout="$SSH_CONNECT_TIMEOUT" -p "$MACMINI_PORT" "$MACMINI_USER@$MACMINI_HOST" 'printf %s "$HOME"')"
    remote_uv_platform="$(ssh -o StrictHostKeyChecking=no -o ConnectTimeout="$SSH_CONNECT_TIMEOUT" -p "$MACMINI_PORT" "$MACMINI_USER@$MACMINI_HOST" 'printf %s "$(uname -s)-$(uname -m)"')"
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
    sshpass -p "${MACMINI_PASSWORD}" ssh -o StrictHostKeyChecking=no -o ConnectTimeout="$SSH_CONNECT_TIMEOUT" -o PreferredAuthentications=password -o PasswordAuthentication=yes -o PubkeyAuthentication=no -p "$MACMINI_PORT" "$MACMINI_USER@$MACMINI_HOST" "mkdir -p \"$remote_uv_root\""
  else
    ssh -o StrictHostKeyChecking=no -o ConnectTimeout="$SSH_CONNECT_TIMEOUT" -p "$MACMINI_PORT" "$MACMINI_USER@$MACMINI_HOST" "mkdir -p \"$remote_uv_root\""
  fi
  if [[ -n "${MACMINI_PASSWORD}" ]]; then
    if ! sshpass -p "${MACMINI_PASSWORD}" scp -o StrictHostKeyChecking=no -o ConnectTimeout="$SSH_CONNECT_TIMEOUT" -o PreferredAuthentications=password -o PasswordAuthentication=yes -o PubkeyAuthentication=no -P "$MACMINI_PORT" "$local_uv" "$MACMINI_USER@$MACMINI_HOST:$remote_uv_root/"; then
      echo "[WARN] UV_LOCAL_BINARY_COPY_FAIL: scp_failed"
      REMOTE_UV_REMOTE_BINARY=""
      return
    fi
  else
    if ! scp -o StrictHostKeyChecking=no -o ConnectTimeout="$SSH_CONNECT_TIMEOUT" -P "$MACMINI_PORT" "$local_uv" "$MACMINI_USER@$MACMINI_HOST:$remote_uv_root/"; then
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

emit_remote_report() {
  {
    echo "# DataPulse OpenClaw 远端联测报告"
    echo "- 运行ID: $RUN_ID"
    echo "- VPS_HOST: $VPS_HOST"
    echo "- MACMINI_HOST: $MACMINI_HOST"
    echo "- MACMINI_USER: $MACMINI_USER"
    echo "- 总步骤: $REMOTE_STEP_TOTAL"
    echo "- 失败步骤: $REMOTE_STEP_FAILED"
    echo "- 开始时间: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
    echo "- 结束时间: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
    echo "- 日志: $LOG_FILE"
    echo "- Trace: $TRACE_FILE"
    echo "- 平台: $PLATFORMS"
    echo "## 步骤结果"
    for item in "${REMOTE_STEP_RESULTS[@]}"; do
      status="${item%%|*}"
      rest="${item#*|}"
      if [[ "$status" == "PASS" ]]; then
        echo "- PASS | $rest"
        continue
      fi
      name="${rest%|*}"
      rc="${item##*|}"
      if [[ "$status" == "OPTIONAL_FAIL" ]]; then
        echo "- WARN | ${name} (optional, rc=${rc})"
      else
        echo "- FAIL | ${name} (rc=${rc})"
      fi
    done
    if (( ${#REMOTE_BLOCK_CODES[@]-0} > 0 )); then
      echo
      echo "## 阻断码"
      for code in "${REMOTE_BLOCK_CODES[@]-}"; do
        echo "- $code"
      done
      echo
      echo "## 建议动作"
      for code in "${REMOTE_BLOCK_CODES[@]-}"; do
        echo "### $code"
        _remediation_for_code "$code"
        echo
      done
    else
      echo
      echo "## 阻断码"
      echo "- 无新增阻断码"
    fi
  } > "$REMOTE_REPORT"
}

check_remote_tunnel() {
  if [[ "$REMOTE_ABORT_ON_CONNECT_FAIL" != "1" ]]; then
    return 0
  fi

  local host
  local output
  local rc
  local selected=""
  local test_cmd='echo SSH_TUNNEL_OK'

  for host in $(printf '%s' "$MACMINI_HOST_CANDIDATES" | tr ',;' ' '); do
    [[ -z "$host" ]] && continue
    MACMINI_HOST="$host"
    set +e
    output="$(run_remote "$test_cmd" 2>&1)"
    rc=$?
    set -e

    if [[ $rc == 0 ]]; then
      selected="$host"
      echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] tunnel check ok on host=$host"
      break
    fi

    echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] tunnel check failed on host=$host" | tee -a "$TRACE_FILE"
    if [[ -n "$output" ]]; then
      printf '%s\n' "$output" | tee -a "$TRACE_FILE"
    fi
  done

  if [[ -z "$selected" ]]; then
    _collect_block_codes "$output"
    _add_block_code "SSH_CONNECTION_REFUSED"
    REMOTE_STEP_TOTAL=1
    REMOTE_STEP_FAILED=1
    REMOTE_STEP_RESULTS=("FAIL|tunnel check|2")
    echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] tunnel check failed; aborting before step execution."
    emit_remote_report
    echo "remote report: $REMOTE_REPORT"
    exit 2
  fi

  MACMINI_HOST="$selected"
}

check_remote_tunnel

bootstrap_uv_direct
echo "REMOTE_UV_REMOTE_BINARY=$REMOTE_UV_REMOTE_BINARY"
run_remote_step "check datapulse directory exists" 1 "bash -lc '$REMOTE_ENV if [ ! -d \"$MACMINI_DATAPULSE_DIR\" ]; then echo \"[ERR] DATAPULSE_DIR_NOT_FOUND: $MACMINI_DATAPULSE_DIR\"; exit 2; fi'"
run_remote_step "check pyproject" 1 "bash -lc '$REMOTE_ENV if [ ! -f \"$MACMINI_DATAPULSE_DIR/pyproject.toml\" ]; then echo \"[ERR] PYPROJECT_MISSING: $MACMINI_DATAPULSE_DIR/pyproject.toml\"; exit 2; fi'"
run_remote_step "check datapulse package" 1 "bash -lc '$REMOTE_ENV if [ ! -d \"$MACMINI_DATAPULSE_DIR/datapulse\" ]; then echo \"[ERR] PACKAGE_MISSING: $MACMINI_DATAPULSE_DIR/datapulse\"; exit 2; fi'"
if [[ "$REMOTE_USE_UV" == "1" ]]; then
  if [[ "$REMOTE_UV_BOOTSTRAP" == "1" ]]; then
    run_remote_step "check uv/bootstrap" 1 "bash -lc '$REMOTE_ENV if [ -n \"$REMOTE_UV_REMOTE_BINARY\" ] && [ -x \"$REMOTE_UV_REMOTE_BINARY\" ]; then $REMOTE_UV_REMOTE_BINARY --version; else echo \"[INFO] UV_BOOTSTRAP_START\"; $REMOTE_PIP_SAFE_ENV $REMOTE_PYTHON -m pip install --user uv; if [ -n \"$REMOTE_UV_REMOTE_BINARY\" ] && [ -x \"$REMOTE_UV_REMOTE_BINARY\" ]; then $REMOTE_UV_REMOTE_BINARY --version; elif command -v uv >/dev/null 2>&1; then uv --version; elif $REMOTE_PYTHON -m uv --version >/dev/null 2>&1; then $REMOTE_PYTHON -m uv --version; else echo \"[ERR] UV_NOT_FOUND\"; exit 2; fi; fi'"
  else
    run_remote_step "check uv present" 1 "bash -lc '$REMOTE_ENV if ! command -v uv >/dev/null 2>&1; then echo \"[ERR] UV_NOT_FOUND\"; exit 2; fi; uv --version'"
  fi
fi
run_remote_step "check python version" 1 "bash -lc '$REMOTE_ENV $REMOTE_PYTHON - <<PY\nimport os\nimport sys\nmin_version = tuple(int(x) for x in os.getenv(\"REMOTE_PYTHON_MIN_VERSION\", \"3.10\").split(\".\")[:2])\nif sys.version_info[:2] < min_version:\n    print(f\"[ERR] PYTHON_VERSION_TOO_LOW={sys.version.split()[0]}\")\n    raise SystemExit(2)\nprint(f\"[OK] PYTHON_VERSION={sys.version.split()[0]}\")\nPY'"
run_remote_step "check pip toolchain" 1 "bash -lc '$REMOTE_ENV $REMOTE_PYTHON --version && $REMOTE_PYTHON -m pip --version'"
if [[ "$REMOTE_BOOTSTRAP_INSTALL" == "1" ]]; then
  run_remote_step "bootstrap install" 1 "bash -lc '$REMOTE_ENV if [ ! -d \"$MACMINI_DATAPULSE_DIR\" ]; then echo \"[ERR] DATAPULSE_DIR_NOT_FOUND: $MACMINI_DATAPULSE_DIR\"; exit 2; fi; cd \"$MACMINI_DATAPULSE_DIR\" && echo \"[INFO] REMOTE_BOOTSTRAP_INSTALL=$REMOTE_BOOTSTRAP_INSTALL\" && $REMOTE_PIP_SAFE_ENV $REMOTE_INSTALL_CMD || (echo \"[ERR] BUILD_DEPENDENCY_PROXY_FAIL: install_failed\"; exit 1)'"
fi
run_remote_step "import datapulse" 1 "bash -lc '$REMOTE_ENV cd $MACMINI_DATAPULSE_DIR && $REMOTE_PYTHON - <<PY\nimport sys\n\ntry:\n    import datapulse\n    print(\"[OK] IMPORT datapulse\")\nexcept Exception as exc:\n    print(f\"[ERR] IMPORT_FAILED={type(exc).__name__}:{exc}\")\n    raise SystemExit(2)\nPY'"
run_remote_step "smoke list" 1 "bash -lc '$REMOTE_ENV cd $MACMINI_DATAPULSE_DIR && $REMOTE_PYTHON -m datapulse.tools.smoke --list'"
run_remote_step "smoke platforms" 1 "bash -lc '$REMOTE_ENV cd $MACMINI_DATAPULSE_DIR && $REMOTE_PYTHON -m datapulse.tools.smoke --platforms $PLATFORMS --require-all --min-confidence ${MIN_CONFIDENCE}'"
run_remote_step "reader metrics" 1 "bash -lc '$REMOTE_ENV cd $MACMINI_DATAPULSE_DIR && $REMOTE_PYTHON - <<PY
from datapulse.reader import DataPulseReader

reader = DataPulseReader()
print(f\"sources={len(reader.list_sources(public_only=True))}\")
print(f\"packs={len(reader.list_packs(public_only=True))}\")
payload = reader.build_json_feed(limit=5, min_confidence=0.0)
PY'"
run_remote_step "cli list" 0 "bash -lc '$REMOTE_ENV cd $MACMINI_DATAPULSE_DIR && $REMOTE_PYTHON -m datapulse.cli --list --limit 5 --min-confidence 0.0 || true'"
run_remote_step "agent smoke" 1 "bash -lc '$REMOTE_ENV cd $MACMINI_DATAPULSE_DIR && $REMOTE_PYTHON - <<PY\nimport asyncio\nimport os\nfrom datapulse.agent import DataPulseAgent\nurls = []\nfor part in [os.getenv(\"URL_1\", \"\"), os.getenv(\"URL_BATCH\", \"\")]:\n    if part.strip():\n        urls.extend(part.split())\nmsg = \" \".join(urls)\nprint(\"agent_input_count=\" + str(len(urls)))\nif msg:\n    result = asyncio.run(DataPulseAgent().handle(msg))\n    print(result)\nelse:\n    print(\"no-url\")\nPY'"
run_remote_step "healthz/readyz" 1 "bash -lc '$REMOTE_ENV curl -fsS ${REMOTE_HEALTH_URL}/healthz && echo && curl -fsS ${REMOTE_HEALTH_URL}/readyz | python3 -m json.tool'"

run_remote_step "feed query probes" 1 "bash -lc '$REMOTE_ENV cd $MACMINI_DATAPULSE_DIR && $REMOTE_PYTHON - <<PY
from datapulse.reader import DataPulseReader

reader = DataPulseReader()
print(\"source_profiles_default=\", reader.list_subscriptions())
print(\"query_feed=\", len(reader.query_feed(limit=3)))
PY'"

# MCP 与 Skill 快速连通（文本层，不直接启动常驻 server）
run_remote_step "mcp/agent quick probe" 1 "bash -lc '$REMOTE_ENV cd $MACMINI_DATAPULSE_DIR && $REMOTE_PYTHON - <<PY\nimport asyncio, os\nfrom datapulse.agent import DataPulseAgent\nfrom datapulse.mcp_server import _run_read_url\n\nurl = os.getenv(\"URL_1\", \"\")\nif not url:\n    print(\"SKIP: URL_1 not set\")\nelse:\n    print(\"mcp_read_url_json\")\n    print(asyncio.run(_run_read_url(url, min_confidence=0.0)))\n    print(\"agent_ok\")\n    print(asyncio.run(DataPulseAgent(min_confidence=0.0).handle(url)))\n\nprint(\"skill_check\")\nfrom datapulse_skill import run\nprint(run(f\"请处理 {url}\"))\nPY'"

emit_remote_report

echo "remote report: $REMOTE_REPORT"
echo "远端日志: $LOG_FILE"
echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] remote test done"
