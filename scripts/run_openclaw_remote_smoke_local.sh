#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

OPENCLAW_ENV_FILES=(
  ".env.openclaw.local"
  ".env.openclaw"
  ".env.local"
  ".env.secret"
  ".env"
)

OPENCLAW_LOCAL=".env.openclaw.local"
OPENCLAW_TEMPLATE=".env.openclaw.example"
AUTO_PERSIST_KEYS=(
  VPS_USER VPS_HOST VPS_PASSWORD VPS_PORT
  MACMINI_USER MACMINI_HOST MACMINI_PASSWORD MACMINI_PORT MACMINI_DATAPULSE_DIR
  REMOTE_PYTHON REMOTE_PYTHON_MIN_VERSION REMOTE_AUTOPICK_PYTHON REMOTE_BOOTSTRAP_INSTALL
  REMOTE_PIP_EXTRAS REMOTE_HEALTH_URL REMOTE_DIRECT_SSH
  REMOTE_USE_UV REMOTE_UV_PYTHON REMOTE_UV_BOOTSTRAP REMOTE_UV_LOCAL_BINARY REMOTE_UV_INSTALL_ROOT
  PLATFORMS MIN_CONFIDENCE RUN_ID OUT_DIR
  URL_1 URL_BATCH DATAPULSE_SMOKE_TWITTER_URL DATAPULSE_SMOKE_REDDIT_URL DATAPULSE_SMOKE_YOUTUBE_URL
  DATAPULSE_SMOKE_BILIBILI_URL DATAPULSE_SMOKE_TELEGRAM_URL DATAPULSE_SMOKE_RSS_URL
  DATAPULSE_SMOKE_WECHAT_URL DATAPULSE_SMOKE_XHS_URL
  TG_API_ID TG_API_HASH DATAPULSE_TG_MAX_MESSAGES DATAPULSE_TG_MAX_CHARS DATAPULSE_TG_CUTOFF_HOURS
  JINA_API_KEY TAVILY_API_KEY FIRECRAWL_API_KEY GROQ_API_KEY OPENROUTER_API_KEY DATAPULSE_LLM_API_KEY
)

is_missing_value() {
  local value="$1"
  [[ -z "$value" || "$value" == "<"*">" || "$value" == "<>" || "$value" == "<REDACTED>" ]]
}

load_env_file() {
  local source_file="$1"
  if [[ -f "$source_file" ]]; then
    set -a
    source "$source_file"
    set +a
    return 0
  fi
  return 1
}

persist_local_env() {
  local template="$1"
  local output_file="$2"
  local has_value=0

  {
    echo "# OpenClaw 远端回归自动持久化副本（本地）"
    echo "# 说明：此文件仅用于本地调试，按需更新。"
    echo "# 若需改动，请编辑 .env.openclaw.example 后重新复制更新。"
    echo
  } > "$output_file"

  for key in "${AUTO_PERSIST_KEYS[@]}"; do
    local value="${!key-}"
    if is_missing_value "${value-}"; then
      continue
    fi
    printf '%s=%q\n' "$key" "$value" >> "$output_file"
    has_value=1
  done

  if [[ "$has_value" -eq 0 ]]; then
    if [[ -f "$template" ]]; then
      cp "$template" "$output_file"
    else
      echo "# 未检测到可持久化字段，可补齐环境变量后重试。" >> "$output_file"
    fi
    return 1
  fi

  return 0
}

if [[ -f "$OPENCLAW_LOCAL" ]]; then
  load_env_file "$OPENCLAW_LOCAL"
else
  local_source=""
  for env_file in "${OPENCLAW_ENV_FILES[@]:1}"; do
    if [[ -f "$env_file" ]]; then
      local_source="$env_file"
      break
    fi
  done

  if [[ -n "$local_source" ]]; then
    load_env_file "$local_source"
  fi

  if persist_local_env "$OPENCLAW_TEMPLATE" "$OPENCLAW_LOCAL"; then
    echo "INFO: 已自动从当前会话/环境变量补齐并持久化 -> $OPENCLAW_LOCAL"
  else
    echo "WARN: 未检测到可直接持久化的凭据字段（${local_source:-无历史配置）}；将继续尝试从当前环境直接执行。"
  fi
fi

bash "scripts/datapulse_remote_openclaw_smoke.sh" "$@"
