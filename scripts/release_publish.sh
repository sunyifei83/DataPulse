#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

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
PYTHON_CMD=()
PYTHON_DESC=""
PYTHON_VERSION=""
PREPARE_BUILD_CMD=()
BUILD_CMD=()
BUILD_DESC=""

python_supports_project() {
  local candidate="$1"
  "$candidate" - <<'PY' >/dev/null 2>&1
import sys
raise SystemExit(0 if sys.version_info[:2] >= (3, 10) else 1)
PY
}

resolve_python_cmd() {
  if [[ -n "${DATAPULSE_RELEASE_PYTHON:-}" ]]; then
    if ! command -v "${DATAPULSE_RELEASE_PYTHON}" >/dev/null 2>&1; then
      echo "Configured DATAPULSE_RELEASE_PYTHON not found: ${DATAPULSE_RELEASE_PYTHON}" >&2
      exit 1
    fi
    if ! python_supports_project "${DATAPULSE_RELEASE_PYTHON}"; then
      echo "Configured DATAPULSE_RELEASE_PYTHON must be Python >= 3.10: ${DATAPULSE_RELEASE_PYTHON}" >&2
      exit 1
    fi
    PYTHON_CMD=("${DATAPULSE_RELEASE_PYTHON}")
    PYTHON_DESC="${DATAPULSE_RELEASE_PYTHON}"
    return
  fi

  for candidate in python3.12 python3.11 python3.10 python3; do
    if command -v "$candidate" >/dev/null 2>&1 && python_supports_project "$candidate"; then
      PYTHON_CMD=("$candidate")
      PYTHON_DESC="$candidate"
      return
    fi
  done

  if command -v uv >/dev/null 2>&1; then
    PYTHON_CMD=(uv run --python 3.10 python)
    PYTHON_DESC="uv run --python 3.10 python"
    return
  fi

  echo "No Python >= 3.10 runtime found. Set DATAPULSE_RELEASE_PYTHON or install uv." >&2
  exit 1
}

python_run() {
  "${PYTHON_CMD[@]}" "$@"
}

capture_python_version() {
  PYTHON_VERSION="$(
    python_run - <<'PY'
import sys

print(f"{sys.version_info[0]}.{sys.version_info[1]}")
PY
  )"
}

configure_build_cmd() {
  PREPARE_BUILD_CMD=()

  if python_run -m build --help >/dev/null 2>&1; then
    BUILD_CMD=("${PYTHON_CMD[@]}" -m build --sdist --wheel .)
    BUILD_DESC="${PYTHON_DESC} -m build"
    return
  fi

  if python_run -m pip --version >/dev/null 2>&1; then
    PREPARE_BUILD_CMD=("${PYTHON_CMD[@]}" -m pip install --upgrade build)
    BUILD_CMD=("${PYTHON_CMD[@]}" -m build --sdist --wheel .)
    BUILD_DESC="${PYTHON_DESC} -m pip install --upgrade build && ${PYTHON_DESC} -m build"
    return
  fi

  if command -v uv >/dev/null 2>&1; then
    BUILD_CMD=(uv run --python "${PYTHON_VERSION}" --with build python -m build --sdist --wheel .)
    BUILD_DESC="uv run --python ${PYTHON_VERSION} --with build python -m build"
    return
  fi

  echo "Selected Python runtime lacks both build and pip, and uv is unavailable." >&2
  exit 1
}

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

resolve_python_cmd
capture_python_version
configure_build_cmd

PROJECT_VERSION=$(python_run - <<'PY'
import re, pathlib
text = pathlib.Path("pyproject.toml").read_text(encoding="utf-8")
m = re.search(r'(?m)^version\s*=\s*"([^"]+)"', text)
print(m.group(1) if m else "0.0.0")
PY
)

if [[ -z "$TAG" ]]; then
  TAG="v${PROJECT_VERSION}"
fi

if [[ -z "$REPO" ]]; then
  REPO=$(
    git remote get-url origin |
      sed -E 's#^git@github.com:##; s#^ssh://git@github.com/##; s#^https://[^/]+@github.com/##; s#^https://github.com/##; s#\.git$##'
  )
fi

extract_notes() {
  local notes_file="$1"
  local tag="$2"
  local raw_notes

  raw_notes=$(
    python_run - "$notes_file" "$tag" <<'PY'
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
    sys.stderr.write(f"Release notes section not found for tag {tag}.\n")
    sys.exit(1)

end = len(lines)
for idx in range(start, len(lines)):
    if re.match(r"^##\s+Release:|^##\s*DataPulse", lines[idx]):
        end = idx
        break

section = "\n".join(lines[start:end]).strip()
if not section:
    sys.stderr.write(f"Release notes section for {tag} is empty.\n")
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
    printf "%s" "$raw_notes" | python_run -c 'import sys; [sys.stdout.write(line if "Full Changelog" not in line else "") for line in sys.stdin.read().splitlines(True)]'
  else
    printf "%s" "$raw_notes"
  fi
}

TMP_NOTES_FILE=$(mktemp)
TMP_TAG_FILE=$(mktemp)
trap 'rm -f "$TMP_NOTES_FILE" "$TMP_TAG_FILE"' EXIT

run_cmd() {
  if [[ "$DRY_RUN" -eq 1 ]]; then
    printf '[dry-run]'
    printf ' %q' "$@"
    printf '\n'
  else
    "$@"
  fi
}

if [[ ! -f "$NOTES_FILE" ]]; then
  echo "Notes file not found: $NOTES_FILE" >&2
  exit 1
fi

notes_body="$(extract_notes "$NOTES_FILE" "$TAG")" || exit 1
printf '%s' "$notes_body" > "$TMP_NOTES_FILE"

{
  echo "Release notes for ${TAG}:"
  echo "----------------------------------------"
  cat "$TMP_NOTES_FILE"
  echo "----------------------------------------"
} >&2

if ! python_run - "$TMP_NOTES_FILE" <<'PY'
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

{
  printf 'DataPulse %s\n\n' "$TAG"
  cat "$TMP_NOTES_FILE"
} > "$TMP_TAG_FILE"

run_cmd rm -rf dist
if [[ ${#PREPARE_BUILD_CMD[@]} -gt 0 ]]; then
  run_cmd "${PREPARE_BUILD_CMD[@]}"
fi
run_cmd "${BUILD_CMD[@]}"

if git rev-parse "$TAG" >/dev/null 2>&1; then
  existing_tag_type="$(git cat-file -t "$TAG" 2>/dev/null || true)"
  if [[ "$existing_tag_type" != "tag" ]]; then
    echo "Existing tag ${TAG} is lightweight; recreate it as an annotated tag before publishing." >&2
    exit 1
  fi
else
  run_cmd git tag -a "$TAG" -F "$TMP_TAG_FILE"
fi
run_cmd git push origin "$TAG"

release_assets=(
  "dist/datapulse-${PROJECT_VERSION}-py3-none-any.whl"
  "dist/datapulse-${PROJECT_VERSION}.tar.gz"
)

run_cmd gh release create "$TAG" "${release_assets[@]}" --repo "$REPO" --title "DataPulse ${TAG}" --notes-file "$TMP_NOTES_FILE"

echo "Release publish finished: ${TAG}"
