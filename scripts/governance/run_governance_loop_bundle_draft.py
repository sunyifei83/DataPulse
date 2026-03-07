#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from loop_bundle_draft import build_bundle_runtime_payload


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the generic governance loop core against an adapter bundle manifest."
    )
    parser.add_argument(
        "--bundle-dir",
        type=Path,
        required=True,
        help="Directory containing adapter_bundle_manifest.draft.json and referenced snapshot files.",
    )
    parser.add_argument(
        "--ignore-blocking-fact",
        action="append",
        default=[],
        help="Blocking fact to ignore for preview purposes. Can be supplied multiple times.",
    )
    return parser.parse_args()

def main() -> int:
    args = parse_args()
    payload, errors, _, _ = build_bundle_runtime_payload(args.bundle_dir, args.ignore_blocking_fact)
    if errors:
        print(json.dumps({"status": "invalid_bundle", "errors": errors}, indent=2, ensure_ascii=True))
        return 1
    print(json.dumps(payload, indent=2, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
