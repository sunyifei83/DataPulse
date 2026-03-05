#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

echo "[guardrails] token leak scan start"

TOKEN_RE='(github_pat_[A-Za-z0-9_]{35,}|gh[pousr]_[A-Za-z0-9_]{35,}|jina_[A-Za-z0-9]{20,}|tvly-[A-Za-z0-9]{20,}|x-access-token:[^[:space:]]+|sk_(live|test)_[A-Za-z0-9]{20,}|AIza[0-9A-Za-z_-]{35}|AKIA[0-9A-Z]{16}|eyJ[a-zA-Z0-9_-]{20,}|(?:[?&](?:api[_-]?)?key|token|secret|access[_-]?key)=[^[:space:]\"<>]{16,})'
ENV_ASSIGN_RE='(^|[[:space:]])[A-Za-z_][A-Za-z0-9_]*(API_KEY|APP_KEY|ACCESS_KEY|AUTH_TOKEN|CLIENT_SECRET|CLIENT_ID|SECRET|TOKEN|PASSWORD|BEARER_TOKEN)=[A-Za-z0-9._~+/-]{24,}'
found=0

is_template_file() {
  case "$1" in
    *\.env.openclaw.example)
      return 0
      ;;
    *)
      return 1
      ;;
  esac
}

is_forbidden_local_secret_file() {
  case "$1" in
    .env.openclaw.local|*/.env.openclaw.local|.env.openclaw|*/.env.openclaw|.env.local|*/.env.local|.env.secret|*/.env.secret|.env|*/.env|.env.datapulse|*/.env.datapulse|local-secrets.json|*/local-secrets.json|session_state.json|*/session_state.json|datapulse-openclaw.env|*/datapulse-openclaw.env|openclaw-*.env|*/openclaw-*.env|openclaw-*.env.local|*/openclaw-*.env.local|openclaw-*.secret|*/openclaw-*.secret|model-endpoints.local.*|*/model-endpoints.local.*)
      if [[ "$1" == *.env.openclaw.example || "$1" == */.env.openclaw.example ]]; then
        return 1
      fi
      return 0
      ;;
    *)
      return 1
      ;;
  esac
}

while IFS= read -r -d '' file; do
  if is_forbidden_local_secret_file "$file"; then
    echo "[guardrails][ERROR] 已追踪到疑似本地敏感文件：$file（请改用 .gitignore 外的安全模板并在本地单独维护）"
    found=1
    continue
  fi

  if is_template_file "$file"; then
    continue
  fi

  if [[ ! -r "$file" ]]; then
    continue
  fi
  if ! grep -Iq . "$file"; then
    continue
  fi

  if [[ "$file" == "scripts/security_guardrails.sh" || "$file" == "$ROOT_DIR/scripts/security_guardrails.sh" ]]; then
    grep -E -n "$TOKEN_RE" "$file" | grep -v 'TOKEN_RE=' && found=1 || true
    continue
  fi

  if grep -E -n "$TOKEN_RE" "$file"; then
    found=1
  fi
  if grep -E -n "$ENV_ASSIGN_RE" "$file"; then
    found=1
  fi
done < <(git ls-files -z)

if [[ "$found" -eq 1 ]]; then
  echo "[guardrails][ERROR] 在已跟踪文件中检测到疑似明文 token/敏感值或本地明文凭据文件，请先清理后再入库。"
  exit 1
fi

echo "[guardrails] no suspicious token pattern found"
exit 0
