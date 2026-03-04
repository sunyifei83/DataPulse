#!/usr/bin/env bash

set -euo pipefail

printf '%s\n' "[release-smoke] start"

if ! command -v gh >/dev/null 2>&1; then
  echo "gh not found" >&2
  exit 1
fi

if ! command -v jq >/dev/null 2>&1; then
  echo "jq not found" >&2
  exit 1
fi

if ! command -v rg >/dev/null 2>&1; then
  echo "rg not found" >&2
  exit 1
fi

printf '%s\n' "[release-smoke] check: gh releases no Full Changelog noise"
HAS_NOISE=0
for t in $(gh release list --json tagName | jq -r '.[].tagName' | sort -V); do
  if gh release view "$t" --json body --jq '.body' | rg -n "Full Changelog|full changelog" >/dev/null; then
    echo "[release-smoke] NOK  $t"
    HAS_NOISE=1
  else
    echo "[release-smoke] OK   $t"
  fi
done

if [[ "$HAS_NOISE" -ne 0 ]]; then
  echo "[release-smoke] Full Changelog noise detected in release notes" >&2
  exit 1
fi

printf '%s\n' "[release-smoke] pass"
