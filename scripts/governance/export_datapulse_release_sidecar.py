#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from datapulse_loop_contracts import (
    DEFAULT_OUT_DIR,
    REPO_ROOT,
    git_output,
    latest_artifact_file,
    parse_emergency_state,
    parse_local_report,
    parse_remote_report,
    read_text,
    repo_workspace_clean,
    utc_now,
    workflow_dispatch_available,
    write_json,
)


def project_version() -> str:
    pyproject = REPO_ROOT / "pyproject.toml"
    text = read_text(pyproject)
    match = re.search(r'(?m)^version\s*=\s*"([^"]+)"', text)
    return match.group(1) if match else "0.0.0"


def detect_tag(tag_arg: str) -> str:
    if tag_arg.strip():
        return tag_arg.strip()
    return f"v{project_version()}"


def extract_notes_section(notes_file: Path, tag: str) -> tuple[bool, str]:
    if not notes_file.exists():
        return False, ""
    target = re.escape(tag.lstrip("v"))
    lines = read_text(notes_file).splitlines()
    header_patterns = [
        rf"^##\s+Release:\s*DataPulse\s+v{target}\b",
        rf"^##\s+Release:\s+v{target}\b",
        rf"^##\s*DataPulse\s+v{target}\b",
    ]
    start = None
    for idx, line in enumerate(lines):
        if any(re.match(pattern, line) for pattern in header_patterns):
            start = idx + 1
            break
    if start is None:
        return False, ""
    end = len(lines)
    for idx in range(start, len(lines)):
        if re.match(r"^##\s+Release:|^##\s*DataPulse", lines[idx]):
            end = idx
            break
    section = "\n".join(lines[start:end]).strip()
    return bool(section), section


def dist_files() -> list[str]:
    dist_dir = REPO_ROOT / "dist"
    if not dist_dir.exists():
        return []
    return sorted(str(path.relative_to(REPO_ROOT)) for path in dist_dir.iterdir() if path.is_file())


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Export a draft DataPulse release sidecar bundle. This script is manual-only and not wired into existing workflows."
    )
    parser.add_argument("--tag", default="", help="Release tag such as v0.7.0. Defaults to the project version tag.")
    parser.add_argument(
        "--notes-file",
        type=Path,
        default=Path("RELEASE_NOTES.md"),
        help="Release notes source file.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUT_DIR / "release_sidecar.draft.json",
        help="Output path for the draft release sidecar JSON.",
    )
    parser.add_argument("--stdout", action="store_true", help="Print JSON to stdout instead of writing the default draft file.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    tag = detect_tag(args.tag)
    version = tag.lstrip("v")
    notes_file = (REPO_ROOT / args.notes_file).resolve() if not args.notes_file.is_absolute() else args.notes_file
    notes_found, notes_excerpt = extract_notes_section(notes_file, tag)
    workspace_clean, _dirty_entries = repo_workspace_clean()
    remote_report = parse_remote_report(latest_artifact_file("remote_report.md"))
    emergency_state = parse_emergency_state(latest_artifact_file("emergency_state.json"))
    local_report = parse_local_report(latest_artifact_file("local_report.md"))
    release_workflow = REPO_ROOT / ".github/workflows/release.yml"

    payload = {
        "schema_version": "release_sidecar.v1",
        "project": "DataPulse",
        "generated_at_utc": utc_now(),
        "sidecar_kind": "draft_export",
        "wired": False,
        "release": {
            "tag": tag,
            "version": version,
            "notes_file": str(notes_file.relative_to(REPO_ROOT)),
            "notes_section_found": notes_found,
            "notes_excerpt_preview": notes_excerpt.splitlines()[:8],
        },
        "git": {
            "head": git_output("rev-parse", "HEAD"),
            "branch": git_output("branch", "--show-current"),
            "workspace_clean": workspace_clean,
        },
        "build_artifacts": {
            "dist_exists": bool(dist_files()),
            "files": dist_files(),
        },
        "evidence": {
            "latest_remote_report": remote_report,
            "latest_emergency_state": emergency_state,
            "latest_local_report": local_report,
        },
        "workflow": {
            "draft_workflow_path": "docs/governance/datapulse-evidence-workflow.draft.yml",
            "workflow_dispatch_available_in_active_release_workflow": workflow_dispatch_available(release_workflow),
            "active_release_workflow": ".github/workflows/release.yml",
        },
        "promotion_readiness": {
            "structured_release_bundle_available": False,
            "reasons": [
                reason
                for reason in [
                    "" if workflow_dispatch_available(release_workflow) else "workflow_dispatch_missing",
                    "structured_release_bundle_missing",
                    "" if notes_found else "release_notes_section_missing",
                    "" if workspace_clean else "workspace_dirty",
                ]
                if reason
            ],
        },
    }

    if args.stdout:
        print(json.dumps(payload, indent=2, ensure_ascii=True))
        return 0

    write_json(args.output, payload)
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
