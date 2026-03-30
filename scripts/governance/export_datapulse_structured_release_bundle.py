#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

from datapulse.governance_paths import (
    EVIDENCE_BUNDLE_ROOT,
    RUNTIME_BUNDLE_ROOT,
    read_root as resolve_governance_read_root,
    write_root as resolve_governance_write_root,
)
from datapulse_loop_contracts import DEFAULT_PLAN_PATH, REPO_ROOT, load_plan, read_json, utc_now, write_json

DEFAULT_BUNDLE_DIR = resolve_governance_write_root(EVIDENCE_BUNDLE_ROOT, repo_root=REPO_ROOT)
DEFAULT_RUNTIME_BUNDLE_DIR = resolve_governance_read_root(RUNTIME_BUNDLE_ROOT, repo_root=REPO_ROOT)
REQUIRED_RUNTIME_ARTIFACTS = ("surface_admission", "bridge_config", "release_status")


def current_python_command() -> list[str]:
    return [sys.executable]


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
    parser.add_argument(
        "--runtime-bundle-dir",
        type=Path,
        default=DEFAULT_RUNTIME_BUNDLE_DIR,
        help="Stable runtime bundle directory copied into the structured evidence bundle.",
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
    runtime_bundle_dir: Path,
    runtime_bundle_files: list[str],
    tag: str,
    notes_file: Path,
    probe_ha_readiness: bool,
    auto_policy_included: bool,
) -> dict[str, object]:
    files = [
        "adapter_bundle_manifest.draft.json",
        "bundle_manifest.json",
        "surface_admission.json",
        "bridge_config.json",
        "release_status.json",
        "blueprint_plan.snapshot.json",
        "slice_adapter_catalog.snapshot.json",
        "code_landing_status.snapshot.json",
        "datapulse-ai-surface-admission.example.json",
        "datapulse_surface_runtime_hit_evidence.draft.json",
        "datapulse_release_window_attestation.draft.json",
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
        "runtime_bundle": {
            "source_dir": str(runtime_bundle_dir),
            "files_copied": runtime_bundle_files,
        },
        "ha_readiness_probed": probe_ha_readiness,
        "files": files,
    }


def runtime_bundle_copy_map(runtime_bundle_dir: Path) -> dict[str, Path]:
    manifest_path = (runtime_bundle_dir / "bundle_manifest.json").resolve()
    if not manifest_path.exists():
        raise RuntimeError(f"runtime bundle manifest missing: {manifest_path}")
    manifest = read_json(manifest_path)
    if str(manifest.get("schema") or "").strip() != "modelbus.consumer_bundle_manifest.v1":
        raise RuntimeError(f"runtime bundle manifest invalid: {manifest_path}")
    artifacts = dict(manifest.get("artifacts", {})) if isinstance(manifest.get("artifacts"), dict) else {}
    copy_map = {"bundle_manifest.json": manifest_path}
    for artifact_key in REQUIRED_RUNTIME_ARTIFACTS:
        artifact = dict(artifacts.get(artifact_key, {})) if isinstance(artifacts.get(artifact_key), dict) else {}
        raw_path = str(artifact.get("path") or "").strip()
        if not raw_path:
            raise RuntimeError(f"runtime bundle manifest missing artifacts.{artifact_key}.path")
        source_path = Path(raw_path).expanduser()
        if not source_path.is_absolute():
            source_path = (runtime_bundle_dir / source_path).resolve()
        else:
            source_path = source_path.resolve()
        if not source_path.exists():
            raise RuntimeError(f"runtime bundle artifact missing: {source_path}")
        copy_map[str(Path(raw_path))] = source_path
    return copy_map


def copy_runtime_bundle_files(runtime_bundle_dir: Path, bundle_dir: Path) -> list[str]:
    copied_files: list[str] = []
    for relative_path, source_path in runtime_bundle_copy_map(runtime_bundle_dir).items():
        destination = (bundle_dir / relative_path).resolve()
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source_path, destination)
        copied_files.append(relative_path)
    return copied_files


def main() -> int:
    args = parse_args()
    bundle_dir = args.out_dir.resolve()
    runtime_bundle_dir = args.runtime_bundle_dir.resolve()
    notes_file = (REPO_ROOT / args.notes_file).resolve() if not args.notes_file.is_absolute() else args.notes_file.resolve()
    plan = load_plan(args.plan.resolve())
    auto_policy = dict(plan.get("activation", {}).get("auto_continuation", {}))
    bundle_dir.mkdir(parents=True, exist_ok=True)
    runtime_bundle_files = copy_runtime_bundle_files(runtime_bundle_dir, bundle_dir)
    manifest = build_manifest(
        bundle_dir,
        runtime_bundle_dir=runtime_bundle_dir,
        runtime_bundle_files=runtime_bundle_files,
        tag=args.tag.strip(),
        notes_file=notes_file,
        probe_ha_readiness=args.probe_ha_readiness,
        auto_policy_included=bool(auto_policy.get("path")),
    )

    if args.stdout:
        print(json.dumps(manifest, indent=2, ensure_ascii=True))
        return 0

    write_json(bundle_dir / "structured_release_bundle_manifest.draft.json", manifest)
    subprocess.run(
        [
            *current_python_command(),
            "scripts/governance/export_datapulse_evidence_bundle.py",
            "--plan",
            str(args.plan.resolve()),
            "--out-dir",
            str(bundle_dir),
            "--bundle-dir",
            str(bundle_dir),
            "--runtime-bundle-dir",
            str(runtime_bundle_dir),
            *(["--tag", args.tag.strip()] if args.tag.strip() else []),
            "--notes-file",
            str(notes_file),
            *(["--probe-ha-readiness"] if args.probe_ha_readiness else []),
        ],
        cwd=REPO_ROOT,
        check=True,
    )
    subprocess.run(
        [
            *current_python_command(),
            "scripts/governance/export_datapulse_loop_adapter_bundle.py",
            "--plan",
            str(args.plan.resolve()),
            "--out-dir",
            str(bundle_dir),
            "--release-window-attestation",
            str((bundle_dir / "datapulse_release_window_attestation.draft.json").resolve()),
        ],
        cwd=REPO_ROOT,
        check=True,
    )
    print(bundle_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
