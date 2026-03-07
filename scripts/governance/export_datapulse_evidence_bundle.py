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
        "--probe-ha-readiness",
        action="store_true",
        help="Opt in to probing release_readiness when exporting HA delivery facts.",
    )
    parser.add_argument(
        "--stdout",
        action="store_true",
        help="Print the bundle manifest JSON to stdout instead of writing files.",
    )
    return parser.parse_args()


def build_manifest(plan_path: Path, notes_file: Path, tag: str, probe_ha_readiness: bool) -> dict[str, object]:
    files = [
        "code_landing_status.draft.json",
        "ha_delivery_facts.draft.json",
        "ha_delivery_landing.draft.json",
        "ha_recovery_preset.draft.json",
        "project_specific_loop_state.draft.json",
        "release_sidecar.draft.json",
        "evidence_bundle_manifest.draft.json",
    ]
    if probe_ha_readiness:
        files.insert(1, "release_readiness_fact.draft.json")
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
        "ha_readiness_probed": probe_ha_readiness,
        "files": files,
    }


def main() -> int:
    args = parse_args()
    plan = load_plan(args.plan)
    plan["_source_path"] = str(args.plan.resolve())

    code_landing_status = build_code_landing_status()
    project_loop_state = build_project_loop_state(plan, code_landing_status)

    tag = detect_tag(args.tag)
    notes_file = (Path.cwd() / args.notes_file).resolve() if not args.notes_file.is_absolute() else args.notes_file
    manifest = build_manifest(args.plan, notes_file, tag, args.probe_ha_readiness)

    if args.stdout:
        print(json.dumps(manifest, indent=2, ensure_ascii=True))
        return 0

    out_dir = args.out_dir
    write_json(out_dir / "code_landing_status.draft.json", code_landing_status)
    release_readiness_fact_args: list[str] = []
    if args.probe_ha_readiness:
        subprocess.run(
            [
                "python3",
                "scripts/governance/export_datapulse_release_readiness_fact.py",
                "--output",
                str(out_dir / "release_readiness_fact.draft.json"),
            ],
            check=True,
        )
        release_readiness_fact_args = [
            "--release-readiness-fact-json",
            str(out_dir / "release_readiness_fact.draft.json"),
        ]
    subprocess.run(
        [
            "python3",
            "scripts/governance/export_datapulse_ha_delivery_facts.py",
            "--output",
            str(out_dir / "ha_delivery_facts.draft.json"),
            *release_readiness_fact_args,
        ],
        check=True,
    )
    subprocess.run(
        [
            "python3",
            "scripts/governance/export_datapulse_ha_delivery_landing.py",
            "--ha-facts-json",
            str(out_dir / "ha_delivery_facts.draft.json"),
            "--output",
            str(out_dir / "ha_delivery_landing.draft.json"),
        ],
        check=True,
    )
    subprocess.run(
        [
            "python3",
            "scripts/governance/export_datapulse_ha_recovery_preset.py",
            "--ha-facts-json",
            str(out_dir / "ha_delivery_facts.draft.json"),
            "--output",
            str(out_dir / "ha_recovery_preset.draft.json"),
        ],
        check=True,
    )
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
