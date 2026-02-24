#!/usr/bin/env bash

set -euo pipefail

show_help() {
  cat <<'EOF'
Usage:
  ./scripts/release_publish.sh --tag vX.Y.Z [--notes-file path] [--repo owner/repo]

Options:
  --tag           Git tag to create if missing (default: from project version, e.g. v0.1.0)
  --notes-file    Notes file path (default: RELEASE_NOTES.md)
  --repo          GitHub repo in form owner/repo (default: auto from git remote)
  --dry-run       Print commands only without executing destructive steps
EOF
}

TAG=""
NOTES_FILE="RELEASE_NOTES.md"
REPO=""
DRY_RUN=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --tag)
      TAG="$2"
      shift 2
      ;;
    --notes-file)
      NOTES_FILE="$2"
      shift 2
      ;;
    --repo)
      REPO="$2"
      shift 2
      ;;
    --dry-run)
      DRY_RUN=1
      shift
      ;;
    -h|--help)
      show_help
      exit 0
      ;;
    *)
      echo "unknown arg: $1" >&2
      show_help
      exit 1
      ;;
  esac
done

PROJECT_VERSION=$(python - <<'PY'
import re, pathlib
text = pathlib.Path("pyproject.toml").read_text(encoding="utf-8")
m = re.search(r'(?m)^version\\s*=\\s*"([^"]+)"', text)
print(m.group(1) if m else "0.0.0")
PY
)

if [[ -z "$TAG" ]]; then
  TAG="v${PROJECT_VERSION}"
fi

if [[ -z "$REPO" ]]; then
  REPO=$(git remote get-url origin | sed -E 's#(git@github.com:|https://github.com/)##; s#\\.git$##')
fi

run() {
  if [[ "$DRY_RUN" -eq 1 ]]; then
    printf '[dry-run] %s\n' "$*"
  else
    eval "$*"
  fi
}

run "python -m pip install --upgrade build >/dev/null"
run rm -rf dist
run python -m build --sdist --wheel .

if ! git rev-parse "$TAG" >/dev/null 2>&1; then
  run git tag "$TAG"
fi
run git push origin "$TAG"

if [[ ! -f "$NOTES_FILE" ]]; then
  echo "Notes file not found: $NOTES_FILE" >&2
  exit 1
fi

run gh release create "$TAG" dist/* --repo "$REPO" --title "DataPulse ${TAG}" --notes-file "$NOTES_FILE"

echo "Release publish finished: ${TAG}"
