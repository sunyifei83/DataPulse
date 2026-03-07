#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

from datapulse_loop_contracts import DEFAULT_PLAN_PATH, REPO_ROOT, load_plan, utc_now, write_json


DEFAULT_BUNDLE_DIR = REPO_ROOT / "out/release_bundle"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Export a manual-only structured release bundle for DataPulse without wiring active release workflows."
    )
    parser.add_argument(
        "--plan",
        type=Path,
        default=DEFAULT_PLAN_PATH,
        help="Blueprint plan path. Defaults to the active plan overlay.",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=DEFAULT_BUNDLE_DIR,
        help="Output directory for the structured release bundle.",
    )
    parser.add_argument("--tag", default="", help="Optional release tag such as v0.7.0.")
    parser.add_argument(
        "--notes-file",
        type=Path,
        default=Path("RELEASE_NOTES.md"),
        help="Release notes source file.",
    )
    parser.add_argument(
        "--probe-ha-readiness",
        action="store_true",
        help="Opt in to bundling a fresh release_readiness fact alongside the evidence bundle.",
    )
    parser.add_argument(
        "--stdout",
        action="store_true",
        help="Print the structured release bundle manifest JSON to stdout instead of writing files.",
    )
    return parser.parse_args()


def build_manifest(
    bundle_dir: Path,
    *,
    tag: str,
    notes_file: Path,
    probe_ha_readiness: bool,
    auto_policy_included: bool,
) -> dict[str, object]:
    files = [
        "adapter_bundle_manifest.draft.json",
        "blueprint_plan.snapshot.json",
        "slice_adapter_catalog.snapshot.json",
        "code_landing_status.snapshot.json",
        "evidence_bundle_manifest.draft.json",
        "code_landing_status.draft.json",
        "ha_delivery_facts.draft.json",
        "ha_delivery_landing.draft.json",
        "ha_recovery_preset.draft.json",
        "project_specific_loop_state.draft.json",
        "release_sidecar.draft.json",
    ]
    if probe_ha_readiness:
        files.insert(2, "release_readiness_fact.draft.json")
    if auto_policy_included:
        files.insert(3, "auto_continuation_policy.snapshot.json")
    return {
        "schema_version": "structured_release_bundle_manifest.v1",
        "project": "DataPulse",
        "generated_at_utc": utc_now(),
        "bundle_kind": "draft_export",
        "wired": False,
        "bundle_dir": str(bundle_dir),
        "release_tag": tag,
        "notes_file": str(notes_file),
        "ha_readiness_probed": probe_ha_readiness,
        "files": files,
    }


def main() -> int:
    args = parse_args()
    bundle_dir = args.out_dir.resolve()
    notes_file = (REPO_ROOT / args.notes_file).resolve() if not args.notes_file.is_absolute() else args.notes_file.resolve()
    plan = load_plan(args.plan.resolve())
    auto_policy = dict(plan.get("activation", {}).get("auto_continuation", {}))
    manifest = build_manifest(
        bundle_dir,
        tag=args.tag.strip(),
        notes_file=notes_file,
        probe_ha_readiness=args.probe_ha_readiness,
        auto_policy_included=bool(auto_policy.get("path")),
    )

    if args.stdout:
        print(json.dumps(manifest, indent=2, ensure_ascii=True))
        return 0

    bundle_dir.mkdir(parents=True, exist_ok=True)
    write_json(bundle_dir / "structured_release_bundle_manifest.draft.json", manifest)
    subprocess.run(
        [
            "python3",
            "scripts/governance/export_datapulse_loop_adapter_bundle.py",
            "--plan",
            str(args.plan.resolve()),
            "--out-dir",
            str(bundle_dir),
        ],
        cwd=REPO_ROOT,
        check=True,
    )
    subprocess.run(
        [
            "python3",
            "scripts/governance/export_datapulse_evidence_bundle.py",
            "--plan",
            str(args.plan.resolve()),
            "--out-dir",
            str(bundle_dir),
            *(["--tag", args.tag.strip()] if args.tag.strip() else []),
            "--notes-file",
            str(notes_file),
            *(["--probe-ha-readiness"] if args.probe_ha_readiness else []),
        ],
        cwd=REPO_ROOT,
        check=True,
    )
    print(bundle_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
