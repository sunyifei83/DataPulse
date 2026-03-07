#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from datapulse_loop_adapter_draft import DEFAULT_CATALOG_PATH
from datapulse_loop_contracts import DEFAULT_OUT_DIR, DEFAULT_PLAN_PATH, build_code_landing_status, load_plan, utc_now, write_json


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Export a draft DataPulse adapter bundle that the generic governance loop core can consume."
    )
    parser.add_argument(
        "--plan",
        type=Path,
        default=DEFAULT_PLAN_PATH,
        help="Blueprint plan path. Defaults to the draft plan.",
    )
    parser.add_argument(
        "--catalog",
        type=Path,
        default=DEFAULT_CATALOG_PATH,
        help="Slice adapter catalog path. Defaults to the draft catalog.",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=DEFAULT_OUT_DIR / "adapter_bundle",
        help="Output directory for the draft adapter bundle.",
    )
    parser.add_argument(
        "--stdout",
        action="store_true",
        help="Print the bundle manifest JSON to stdout instead of writing files.",
    )
    return parser.parse_args()


def build_manifest(project: str) -> dict[str, object]:
    return {
        "schema_version": "adapter_bundle_manifest.v1",
        "project": project,
        "generated_at_utc": utc_now(),
        "bundle_kind": "draft_export",
        "wired": False,
        "files": {
            "plan": "blueprint_plan.snapshot.json",
            "landing_status": "code_landing_status.snapshot.json",
            "slice_catalog": "slice_adapter_catalog.snapshot.json",
        },
        "adapter_metadata": {
            "adapter_module": "scripts/governance/datapulse_loop_adapter_draft.py",
            "core_runner": "scripts/governance/run_governance_loop_bundle_draft.py",
        },
        "notes": [
            "This bundle is additive only and not wired into active workflows.",
            "The bundle is intended for read-only core evaluation and replay.",
        ],
    }


def main() -> int:
    args = parse_args()
    plan = load_plan(args.plan)
    landing_status = build_code_landing_status()
    project = str(plan.get("project", landing_status.get("project", "DataPulse")))
    manifest = build_manifest(project)

    if args.stdout:
        print(json.dumps(manifest, indent=2, ensure_ascii=True))
        return 0

    out_dir = args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    write_json(out_dir / "blueprint_plan.snapshot.json", plan)
    write_json(out_dir / "code_landing_status.snapshot.json", landing_status)
    write_json(out_dir / "slice_adapter_catalog.snapshot.json", json.loads(args.catalog.read_text(encoding="utf-8")))
    write_json(out_dir / "adapter_bundle_manifest.draft.json", manifest)
    print(out_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
