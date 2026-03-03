#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

echo "[guardrails] token leak scan start"

TOKEN_RE='(github_pat_[A-Za-z0-9_]{35,}|jina_[A-Za-z0-9]{20,}|tvly-[A-Za-z0-9]{20,}|x-access-token:[^[:space:]]+)'
found=0

while IFS= read -r -d '' file; do
  if [[ ! -r "$file" ]]; then
    continue
  fi
  if ! grep -Iq . "$file"; then
    continue
  fi
  if [[ "$file" == "scripts/security_guardrails.sh" || "$file" == "$ROOT_DIR/scripts/security_guardrails.sh" ]]; then
    if grep -E -n "$TOKEN_RE" "$file" | grep -v 'TOKEN_RE='; then
      found=1
    fi
    continue
  fi
  if grep -E -n "$TOKEN_RE" "$file"; then
    found=1
  fi
done < <(git ls-files -z)

if [[ "$found" -eq 1 ]]; then
  echo "[guardrails][ERROR] 在已跟踪文件中检测到疑似明文 token 模式，请先清理后再入库。"
  exit 1
fi

echo "[guardrails] no suspicious token pattern found"
exit 0
