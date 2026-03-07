#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from loop_bundle_draft import build_bundle_runtime_payload, load_bundle_manifest, resolve_bundle_files, validate_manifest_shape
from loop_core_draft import validate_blueprint_plan_structure


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate a governance loop adapter bundle and replay it through the generic core."
    )
    parser.add_argument(
        "--bundle-dir",
        type=Path,
        required=True,
        help="Directory containing adapter_bundle_manifest.draft.json and referenced snapshot files.",
    )
    return parser.parse_args()

def main() -> int:
    args = parse_args()
    bundle_dir = args.bundle_dir
    manifest_path, manifest = load_bundle_manifest(bundle_dir)

    checks: list[dict[str, Any]] = []
    errors = validate_manifest_shape(manifest)
    checks.append(
        {
            "name": "manifest_shape",
            "ok": not errors,
            "details": errors or ["required manifest fields present"],
        }
    )

    resolved, missing_files = resolve_bundle_files(bundle_dir, manifest)
    resolved_files = {key: str(value) for key, value in resolved.items()}
    checks.append(
        {
            "name": "bundle_files_present",
            "ok": not missing_files,
            "details": missing_files or ["required bundle files present"],
        }
    )

    plan_errors: list[str] = []
    if not missing_files:
        plan = json.loads(resolved["plan"].read_text(encoding="utf-8"))
        plan_errors = [f"invalid_blueprint_plan:{item}" for item in validate_blueprint_plan_structure(plan)]
    checks.append(
        {
            "name": "blueprint_plan_structure",
            "ok": not plan_errors,
            "details": plan_errors or ["blueprint plan is phase/slice/status structured"],
        }
    )

    replay_payload, replay_errors, _, _ = build_bundle_runtime_payload(bundle_dir, [])
    if errors or missing_files or plan_errors:
        replay_errors = replay_errors or ["replay_skipped_due_to_bundle_errors"]

    checks.append(
        {
            "name": "core_replay",
            "ok": not replay_errors,
            "details": replay_errors or ["core replay succeeded"],
        }
    )

    payload = {
        "valid": all(item["ok"] for item in checks),
        "bundle_dir": str(bundle_dir),
        "manifest_path": str(manifest_path),
        "resolved_files": resolved_files,
        "checks": checks,
        "replay": replay_payload,
    }
    print(json.dumps(payload, indent=2, ensure_ascii=True))
    return 0 if payload["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
