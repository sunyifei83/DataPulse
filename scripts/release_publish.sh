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
  --keep-full-changelog
                 Keep lines containing `Full Changelog` in notes file (disabled by default)
  --dry-run       Print commands only without executing destructive steps
EOF
}

TAG=""
NOTES_FILE="RELEASE_NOTES.md"
REPO=""
DRY_RUN=0
SCRUB_FULL_CHANGELOG=1

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
    --keep-full-changelog)
      SCRUB_FULL_CHANGELOG=0
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

PROJECT_VERSION=$(python3 - <<'PY'
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

extract_notes() {
  local notes_file="$1"
  local tag="$2"
  local raw_notes

  raw_notes=$(
    python3 - "$notes_file" "$tag" <<'PY'
import pathlib
import re
import sys

notes_path = pathlib.Path(sys.argv[1])
tag = sys.argv[2]
target = tag.lstrip("v")
text = notes_path.read_text(encoding="utf-8")
lines = text.splitlines()
header_patterns = [
    rf"^##\s+Release:\s*DataPulse\s+v{re.escape(target)}\b",
    rf"^##\s+Release:\s+v{re.escape(target)}\b",
    rf"^##\s*DataPulse\s+v{re.escape(target)}\b",
]
start = None
for idx, line in enumerate(lines):
    if start is None and any(re.match(p, line) for p in header_patterns):
        start = idx + 1
        break

if start is None:
    sys.stderr.write(f"Release notes section not found for tag {tag}.\\n")
    sys.exit(1)

end = len(lines)
for idx in range(start, len(lines)):
    if re.match(r"^##\s+Release:|^##\s*DataPulse", lines[idx]):
        end = idx
        break

section = "\n".join(lines[start:end]).strip()
if not section:
    sys.stderr.write(f"Release notes section for {tag} is empty.\\n")
    sys.exit(1)
else:
    print(section)
PY
  )

  if [[ -z "$raw_notes" ]]; then
    echo "No notes found for ${tag} in ${notes_file}." >&2
    return 1
  fi

  if [[ "$SCRUB_FULL_CHANGELOG" -eq 1 ]]; then
    printf "%s" "$raw_notes" | python3 -c 'import sys; [sys.stdout.write(line if "Full Changelog" not in line else "") for line in sys.stdin.read().splitlines(True)]'
  else
    printf "%s" "$raw_notes"
  fi
}

TMP_NOTES_FILE=$(mktemp)
trap 'rm -f "$TMP_NOTES_FILE"' EXIT

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

{
  echo "Release notes for ${TAG}:"
  echo "----------------------------------------"
  notes_body="$(extract_notes "$NOTES_FILE" "$TAG")" || exit 1
  printf '%s' "$notes_body" | tee "$TMP_NOTES_FILE"
  echo "----------------------------------------"
} >&2

if ! python3 - "$TMP_NOTES_FILE" <<'PY'
import pathlib, sys
text = pathlib.Path(sys.argv[1]).read_text(encoding="utf-8")
if "Full Changelog" in text:
    print("ERROR: Release notes still contain 'Full Changelog'.")
    sys.exit(1)
PY
then
  if [[ "$SCRUB_FULL_CHANGELOG" -eq 1 ]]; then
    echo "Release notes contain 'Full Changelog'; use --keep-full-changelog or clean RELEASE_NOTES.md first." >&2
    exit 1
  fi
fi

run gh release create "$TAG" dist/* --repo "$REPO" --title "DataPulse ${TAG}" --notes-file "$TMP_NOTES_FILE"

echo "Release publish finished: ${TAG}"
