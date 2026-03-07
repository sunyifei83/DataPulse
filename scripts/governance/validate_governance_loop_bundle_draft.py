#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from loop_core_draft import build_project_loop_state_core, build_reuse_summary, build_trust_summary, evaluate_loop_status


REQUIRED_MANIFEST_FIELDS = [
    "schema_version",
    "project",
    "generated_at_utc",
    "bundle_kind",
    "wired",
    "files",
]

REQUIRED_FILE_KEYS = [
    "plan",
    "landing_status",
]


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


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


def validate_manifest_shape(manifest: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for key in REQUIRED_MANIFEST_FIELDS:
        if key not in manifest:
            errors.append(f"missing_manifest_field:{key}")
    files = manifest.get("files", {})
    if not isinstance(files, dict):
        errors.append("invalid_manifest_files_object")
        return errors
    for key in REQUIRED_FILE_KEYS:
        if not files.get(key):
            errors.append(f"missing_manifest_files_entry:{key}")
    return errors


def main() -> int:
    args = parse_args()
    bundle_dir = args.bundle_dir
    manifest_path = bundle_dir / "adapter_bundle_manifest.draft.json"
    manifest = read_json(manifest_path)

    checks: list[dict[str, Any]] = []
    errors = validate_manifest_shape(manifest)
    checks.append(
        {
            "name": "manifest_shape",
            "ok": not errors,
            "details": errors or ["required manifest fields present"],
        }
    )

    files = dict(manifest.get("files", {}))
    resolved_files: dict[str, str] = {}
    missing_files: list[str] = []
    for key in REQUIRED_FILE_KEYS + (["slice_catalog"] if files.get("slice_catalog") else []):
        rel = str(files.get(key, ""))
        path = bundle_dir / rel
        resolved_files[key] = str(path)
        if not rel or not path.exists():
            missing_files.append(key)
    checks.append(
        {
            "name": "bundle_files_present",
            "ok": not missing_files,
            "details": missing_files or ["required bundle files present"],
        }
    )

    replay_payload: dict[str, Any] = {}
    replay_errors: list[str] = []
    if not errors and not missing_files:
        plan = read_json(bundle_dir / str(files["plan"]))
        landing_status = read_json(bundle_dir / str(files["landing_status"]))
        loop_state = build_project_loop_state_core(
            plan,
            landing_status,
            source_plan=str(bundle_dir / str(files["plan"])),
            generated_at_utc=str(manifest.get("generated_at_utc", "")),
        )
        status, reason, effective_blockers = evaluate_loop_status(loop_state, [])
        replay_payload = {
            "status": status,
            "reason": reason,
            "next_slice": loop_state.get("next_slice", {}),
            "blocking_facts": loop_state.get("blocking_facts", []),
            "effective_blocking_facts": effective_blockers,
            "remaining_promotion_gates": loop_state.get("remaining_promotion_gates", []),
            "trust_summary": build_trust_summary(loop_state),
            "reuse_summary": build_reuse_summary(loop_state),
        }
        if not loop_state.get("next_slice", {}).get("id"):
            replay_errors.append("replay_missing_next_slice")
        if "flow_control" not in loop_state:
            replay_errors.append("replay_missing_flow_control")
        if "control_contract" not in loop_state:
            replay_errors.append("replay_missing_control_contract")
    else:
        replay_errors.append("replay_skipped_due_to_bundle_errors")

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
