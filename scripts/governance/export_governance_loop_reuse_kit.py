#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
KIT_SCRIPT_FILES = [
    "scripts/governance/assess_governance_loop_activation_draft.py",
    "scripts/governance/export_governance_loop_activation_plan.py",
    "scripts/governance/export_governance_loop_activation_intent.py",
    "scripts/governance/export_governance_loop_activation_preview.py",
    "scripts/governance/loop_core_draft.py",
    "scripts/governance/loop_bundle_draft.py",
    "scripts/governance/run_governance_loop_core_draft.py",
    "scripts/governance/run_governance_loop_bundle_draft.py",
    "scripts/governance/validate_governance_loop_bundle_draft.py",
    "scripts/governance/verify_governance_loop_adoption_draft.py",
    "scripts/governance/verify_governance_loop_activation_intent.py",
    "scripts/governance/verify_governance_loop_activation_preview.py",
    "scripts/governance/init_governance_loop_project_scaffold.py",
]
KIT_DOC_FILES = [
    "docs/governance/governance-loop-activation-boundary.draft.md",
    "docs/governance/governance-loop-activation-intent.draft.md",
    "docs/governance/governance-loop-activation-plan.draft.md",
    "docs/governance/governance-loop-activation-preview.draft.md",
    "docs/governance/governance-loop-core-contract.draft.md",
    "docs/governance/loop-project-adapter-contract.draft.md",
    "docs/governance/loop-adapter-bundle-contract.draft.md",
    "docs/governance/governance-loop-adoption-playbook.draft.md",
    "docs/governance/governance-loop-project-scaffold.draft.md",
    "docs/governance/governance-loop-adoption-verification.draft.md",
]


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def build_manifest() -> dict[str, object]:
    return {
        "schema_version": "governance_loop_reuse_kit_manifest.v1",
        "generated_at_utc": utc_now(),
        "kit_kind": "draft_export",
        "scripts": KIT_SCRIPT_FILES,
        "docs": KIT_DOC_FILES,
        "entrypoints": {
            "scaffold_generator": "scripts/governance/init_governance_loop_project_scaffold.py",
            "bundle_runner": "scripts/governance/run_governance_loop_bundle_draft.py",
            "bundle_validator": "scripts/governance/validate_governance_loop_bundle_draft.py",
            "adoption_verifier": "scripts/governance/verify_governance_loop_adoption_draft.py",
            "activation_assessor": "scripts/governance/assess_governance_loop_activation_draft.py",
            "activation_plan_exporter": "scripts/governance/export_governance_loop_activation_plan.py",
            "activation_intent_exporter": "scripts/governance/export_governance_loop_activation_intent.py",
            "activation_intent_verifier": "scripts/governance/verify_governance_loop_activation_intent.py",
            "activation_preview_exporter": "scripts/governance/export_governance_loop_activation_preview.py",
            "activation_preview_verifier": "scripts/governance/verify_governance_loop_activation_preview.py",
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Export a reusable governance loop kit containing repo-agnostic scripts and contracts."
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=REPO_ROOT / "out/governance/reuse_kit",
        help="Output directory for the reusable kit.",
    )
    parser.add_argument(
        "--stdout",
        action="store_true",
        help="Print the kit manifest JSON instead of writing files.",
    )
    return parser.parse_args()


def copy_files(out_dir: Path, rel_paths: list[str]) -> None:
    for rel in rel_paths:
        src = REPO_ROOT / rel
        dst = out_dir / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)


def main() -> int:
    args = parse_args()
    manifest = build_manifest()
    if args.stdout:
        print(json.dumps(manifest, indent=2, ensure_ascii=True))
        return 0

    out_dir = args.out_dir
    copy_files(out_dir, KIT_SCRIPT_FILES + KIT_DOC_FILES)
    write_json(out_dir / "governance_loop_reuse_kit_manifest.draft.json", manifest)
    print(out_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
