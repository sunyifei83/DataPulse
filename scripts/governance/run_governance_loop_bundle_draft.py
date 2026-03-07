#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path


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


def load_manifest(bundle_dir: Path) -> tuple[Path, dict[str, object]]:
    manifest_path = bundle_dir / "adapter_bundle_manifest.draft.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    return manifest_path, manifest


def main() -> int:
    args = parse_args()
    manifest_path, manifest = load_manifest(args.bundle_dir)
    files = dict(manifest.get("files", {}))
    cmd = [
        "python3",
        "scripts/governance/run_governance_loop_core_draft.py",
        "--plan",
        str(args.bundle_dir / str(files.get("plan", ""))),
        "--landing-status",
        str(args.bundle_dir / str(files.get("landing_status", ""))),
    ]
    slice_catalog = files.get("slice_catalog", "")
    if slice_catalog:
        cmd.extend(["--catalog", str(args.bundle_dir / str(slice_catalog))])
    for item in args.ignore_blocking_fact:
        cmd.extend(["--ignore-blocking-fact", item])
    completed = subprocess.run(cmd, check=True, capture_output=True, text=True)
    payload = json.loads(completed.stdout)
    payload["bundle_manifest"] = str(manifest_path)
    print(json.dumps(payload, indent=2, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
