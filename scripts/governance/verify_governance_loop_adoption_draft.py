#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from loop_bundle_draft import build_bundle_runtime_payload, compare_loop_payloads, read_json


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Verify governance loop adoption by replaying a bundle and optionally comparing it with an adapter runtime JSON."
    )
    parser.add_argument(
        "--bundle-dir",
        type=Path,
        required=True,
        help="Directory containing adapter_bundle_manifest.draft.json and referenced snapshot files.",
    )
    parser.add_argument(
        "--adapter-runtime-json",
        type=Path,
        help="Optional adapter runtime JSON to compare against the bundle replay output.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    replay_payload, replay_errors, resolved_files, manifest_path = build_bundle_runtime_payload(args.bundle_dir, [])

    checks = [
        {
            "name": "bundle_replay",
            "ok": not replay_errors,
            "details": replay_errors or ["bundle replay succeeded"],
        }
    ]

    comparison: dict[str, object] = {}
    if args.adapter_runtime_json:
        adapter_payload = read_json(args.adapter_runtime_json)
        mismatches = compare_loop_payloads(adapter_payload, replay_payload) if not replay_errors else ["comparison_skipped_due_to_bundle_errors"]
        comparison = {
            "adapter_runtime_json": str(args.adapter_runtime_json),
            "mismatches": mismatches,
        }
        checks.append(
            {
                "name": "adapter_runtime_matches_bundle_replay",
                "ok": not mismatches,
                "details": mismatches or ["adapter runtime matches bundle replay on comparable fields"],
            }
        )

    payload = {
        "valid": all(item["ok"] for item in checks),
        "bundle_dir": str(args.bundle_dir),
        "manifest_path": manifest_path,
        "resolved_files": resolved_files,
        "checks": checks,
        "replay": replay_payload,
        "comparison": comparison,
    }
    print(json.dumps(payload, indent=2, ensure_ascii=True))
    return 0 if payload["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
