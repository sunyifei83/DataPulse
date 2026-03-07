#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

from datapulse_loop_contracts import (
    DEFAULT_OUT_DIR,
    DEFAULT_PLAN_PATH,
    build_code_landing_status,
    build_project_loop_state,
    load_plan,
    utc_now,
    write_json,
)
from export_datapulse_release_sidecar import detect_tag, extract_notes_section, project_version


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Export a local draft evidence bundle for DataPulse. This script is manual-only and not wired into existing workflows."
    )
    parser.add_argument(
        "--plan",
        type=Path,
        default=DEFAULT_PLAN_PATH,
        help="Blueprint plan path. Defaults to the draft plan.",
    )
    parser.add_argument(
        "--tag",
        default="",
        help="Optional release tag such as v0.7.0. Defaults to the project version tag.",
    )
    parser.add_argument(
        "--notes-file",
        type=Path,
        default=Path("RELEASE_NOTES.md"),
        help="Release notes source file.",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=DEFAULT_OUT_DIR,
        help="Output directory for the draft evidence bundle.",
    )
    parser.add_argument(
        "--stdout",
        action="store_true",
        help="Print the bundle manifest JSON to stdout instead of writing files.",
    )
    return parser.parse_args()


def build_manifest(plan_path: Path, notes_file: Path, tag: str) -> dict[str, object]:
    notes_found, _ = extract_notes_section(notes_file, tag)
    return {
        "schema_version": "evidence_bundle_manifest.v1",
        "project": "DataPulse",
        "generated_at_utc": utc_now(),
        "bundle_kind": "draft_export",
        "wired": False,
        "plan_path": str(plan_path),
        "release_tag": tag,
        "release_version": tag.lstrip("v") if tag else project_version(),
        "notes_file": str(notes_file),
        "notes_section_found": notes_found,
        "files": [
            "code_landing_status.draft.json",
            "project_specific_loop_state.draft.json",
            "release_sidecar.draft.json",
            "evidence_bundle_manifest.draft.json",
        ],
    }


def main() -> int:
    args = parse_args()
    plan = load_plan(args.plan)
    plan["_source_path"] = str(args.plan.resolve())

    code_landing_status = build_code_landing_status()
    project_loop_state = build_project_loop_state(plan, code_landing_status)

    tag = detect_tag(args.tag)
    notes_file = (Path.cwd() / args.notes_file).resolve() if not args.notes_file.is_absolute() else args.notes_file
    manifest = build_manifest(args.plan, notes_file, tag)

    if args.stdout:
        print(json.dumps(manifest, indent=2, ensure_ascii=True))
        return 0

    out_dir = args.out_dir
    write_json(out_dir / "code_landing_status.draft.json", code_landing_status)
    write_json(out_dir / "project_specific_loop_state.draft.json", project_loop_state)
    subprocess.run(
        [
            "python3",
            "scripts/governance/export_datapulse_release_sidecar.py",
            "--tag",
            tag,
            "--notes-file",
            str(notes_file),
            "--output",
            str(out_dir / "release_sidecar.draft.json"),
        ],
        check=True,
    )
    write_json(out_dir / "evidence_bundle_manifest.draft.json", manifest)
    print(out_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
