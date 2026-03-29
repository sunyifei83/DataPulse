#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from datapulse_loop_contracts import (
    DEFAULT_OUT_DIR,
    REPO_ROOT,
    ci_docs_only_skip_active,
    git_output,
    latest_artifact_file,
    parse_emergency_state,
    parse_local_report,
    parse_remote_report,
    read_json,
    read_text,
    repo_workspace_clean,
    structured_release_bundle_available,
    utc_now,
    workspace_dirty_gate_active,
    workflow_dispatch_available,
    write_json,
)

RUNTIME_HIT_EVIDENCE_PATH = DEFAULT_OUT_DIR / "datapulse_surface_runtime_hit_evidence.draft.json"


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
    parser.add_argument(
        "--runtime-hit-json",
        type=Path,
        default=RUNTIME_HIT_EVIDENCE_PATH,
        help="Runtime-hit evidence JSON used when computing governed AI release readiness.",
    )
    parser.add_argument("--stdout", action="store_true", help="Print JSON to stdout instead of writing the default draft file.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    tag = detect_tag(args.tag)
    version = tag.lstrip("v")
    notes_file = (REPO_ROOT / args.notes_file).resolve() if not args.notes_file.is_absolute() else args.notes_file
    notes_found, notes_excerpt = extract_notes_section(notes_file, tag)
    workspace_clean, dirty_entries = repo_workspace_clean()
    docs_only_skip_active, _change_paths = ci_docs_only_skip_active(workspace_clean, dirty_entries)
    workspace_dirty_active = workspace_dirty_gate_active(workspace_clean, dirty_entries)
    remote_report = parse_remote_report(latest_artifact_file("remote_report.md"))
    emergency_state = parse_emergency_state(latest_artifact_file("emergency_state.json"))
    local_report = parse_local_report(latest_artifact_file("local_report.md"))
    release_workflow = REPO_ROOT / ".github/workflows/release.yml"
    governance_workflow = REPO_ROOT / ".github/workflows/governance-evidence.yml"
    dispatch_entrypoints = [
        path
        for path in [
            ".github/workflows/release.yml" if workflow_dispatch_available(release_workflow) else "",
            ".github/workflows/governance-evidence.yml" if workflow_dispatch_available(governance_workflow) else "",
        ]
        if path
    ]
    workflow_dispatch = bool(dispatch_entrypoints)
    runtime_hit_path = args.runtime_hit_json.resolve()
    runtime_hit_evidence = read_json(runtime_hit_path) if runtime_hit_path.exists() else {}
    runtime_prereqs = (
        runtime_hit_evidence.get("release_level_prerequisites", {})
        if isinstance(runtime_hit_evidence, dict)
        else {}
    )
    runtime_surfaces = runtime_hit_evidence.get("surfaces", []) if isinstance(runtime_hit_evidence, dict) else []

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
            "ai_runtime_hit_evidence_path": (
                str(runtime_hit_path.relative_to(REPO_ROOT))
                if runtime_hit_path.is_relative_to(REPO_ROOT)
                else str(runtime_hit_path)
            )
            if runtime_hit_path.exists()
            else "",
        },
        "workflow": {
            "draft_workflow_path": "docs/governance/datapulse-evidence-workflow.draft.yml",
            "workflow_dispatch_available_in_active_release_workflow": workflow_dispatch,
            "workflow_dispatch_entrypoints": dispatch_entrypoints,
            "active_release_workflow": dispatch_entrypoints[0] if dispatch_entrypoints else ".github/workflows/release.yml",
        },
        "governed_ai_release_readiness": {
            "runtime_hit_evidence_available": bool(runtime_hit_evidence),
            "bundle_first_default_ready": bool(runtime_prereqs.get("bundle_first_default_ready", False)),
            "shadow_change_prerequisites_met": bool(runtime_prereqs.get("shadow_change_prerequisites_met", False)),
            "required_change_prerequisites_met": bool(runtime_prereqs.get("required_change_prerequisites_met", False)),
            "promotion_discussion_allowed": bool(runtime_prereqs.get("promotion_discussion_allowed", False)),
            "surfaces": [
                {
                    "surface": str(row.get("surface", "") or ""),
                    "evidence_status": str(row.get("evidence_status", "") or ""),
                    "served_by_alias": str(row.get("served_by_alias", "") or ""),
                    "schema_valid": bool(row.get("schema_valid", False)),
                }
                for row in runtime_surfaces
                if isinstance(row, dict)
            ],
        },
        "promotion_readiness": {
            "structured_release_bundle_available": structured_release_bundle_available(),
            "reasons": [
                reason
                for reason in [
                    "" if workflow_dispatch else "workflow_dispatch_missing",
                    "" if structured_release_bundle_available() else "structured_release_bundle_missing",
                    "" if notes_found else "release_notes_section_missing",
                    "" if not workspace_dirty_active else "workspace_dirty",
                    "" if runtime_hit_evidence else "ai_runtime_hit_evidence_missing",
                    "" if runtime_prereqs.get("bundle_first_default_ready", False) else "bundle_first_default_not_ready",
                    "" if runtime_prereqs.get("required_change_prerequisites_met", False) else "required_runtime_surface_not_ready",
                ]
                if reason
            ],
            "docs_only_skip_active": docs_only_skip_active,
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
