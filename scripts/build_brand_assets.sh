#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SOURCE_IMAGE="${1:-$ROOT_DIR/docs/形象.jpg}"
ASSET_DIR="${2:-$ROOT_DIR/docs/assets}"

HERO_OUTPUT="$ASSET_DIR/datapulse-command-chamber-hero.jpg"
SQUARE_OUTPUT="$ASSET_DIR/datapulse-command-chamber-square.jpg"
ICON_OUTPUT="$ASSET_DIR/datapulse-command-chamber-icon.png"
SVG_OUTPUT="$ASSET_DIR/datapulse-command-chamber.svg"

if ! command -v sips >/dev/null 2>&1; then
  echo "sips not found; this script currently requires macOS sips." >&2
  exit 1
fi

if [[ ! -f "$SOURCE_IMAGE" ]]; then
  echo "brand source image not found: $SOURCE_IMAGE" >&2
  exit 1
fi

mkdir -p "$ASSET_DIR"

echo "[brand] source: $SOURCE_IMAGE"
echo "[brand] asset dir: $ASSET_DIR"

echo "[brand] build hero crop -> $HERO_OUTPUT"
sips -c 640 1280 "$SOURCE_IMAGE" --out "$HERO_OUTPUT" >/dev/null

echo "[brand] build square crop -> $SQUARE_OUTPUT"
sips -c 768 768 "$SOURCE_IMAGE" --out "$SQUARE_OUTPUT" >/dev/null

echo "[brand] build icon -> $ICON_OUTPUT"
sips -z 256 256 "$SQUARE_OUTPUT" -s format png --out "$ICON_OUTPUT" >/dev/null

if [[ ! -f "$SVG_OUTPUT" ]]; then
  echo "[brand] note: vector derivative not found at $SVG_OUTPUT"
fi

echo "[brand] built assets:"
ls -lh "$HERO_OUTPUT" "$SQUARE_OUTPUT" "$ICON_OUTPUT"
