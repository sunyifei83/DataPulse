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
        "--release-window-attestation",
        type=Path,
        help="Optional release-window attestation JSON used when exporting the landing-status snapshot.",
    )
    parser.add_argument(
        "--stdout",
        action="store_true",
        help="Print the bundle manifest JSON to stdout instead of writing files.",
    )
    return parser.parse_args()


def build_manifest(project: str, *, wired: bool, auto_policy_included: bool) -> dict[str, object]:
    files: dict[str, str] = {
        "plan": "blueprint_plan.snapshot.json",
        "landing_status": "code_landing_status.snapshot.json",
        "slice_catalog": "slice_adapter_catalog.snapshot.json",
    }
    if auto_policy_included:
        files["auto_continuation_policy"] = "auto_continuation_policy.snapshot.json"

    return {
        "schema_version": "adapter_bundle_manifest.v1",
        "project": project,
        "generated_at_utc": utc_now(),
        "bundle_kind": "draft_export",
        "wired": wired,
        "files": files,
        "adapter_metadata": {
            "adapter_module": "scripts/governance/datapulse_loop_adapter.py",
            "core_runner": "scripts/governance/run_governance_loop_bundle_draft.py",
            "active_runner": "scripts/governance/run_datapulse_blueprint_loop.py",
            "auto_runner": "scripts/governance/run_datapulse_auto_continuation.py",
        },
        "notes": [
            "This bundle remains read-only, even when the repository-level auto-continuation entrypoint is enabled.",
            "The bundle is intended for read-only core evaluation and replay.",
        ],
    }


def main() -> int:
    args = parse_args()
    plan = load_plan(args.plan)
    landing_status = build_code_landing_status(
        release_window_attestation_path=args.release_window_attestation.resolve()
        if isinstance(args.release_window_attestation, Path)
        else None
    )
    project = str(plan.get("project", landing_status.get("project", "DataPulse")))
    activation = dict(plan.get("activation", {}))
    auto_policy = activation.get("auto_continuation", {})
    auto_policy_included = isinstance(auto_policy, dict) and bool(auto_policy.get("path"))
    manifest = build_manifest(
        project,
        wired=bool(activation.get("wired", False)),
        auto_policy_included=auto_policy_included,
    )

    if args.stdout:
        print(json.dumps(manifest, indent=2, ensure_ascii=True))
        return 0

    out_dir = args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    write_json(out_dir / "blueprint_plan.snapshot.json", plan)
    write_json(out_dir / "code_landing_status.snapshot.json", landing_status)
    write_json(out_dir / "slice_adapter_catalog.snapshot.json", json.loads(args.catalog.read_text(encoding="utf-8")))
    if auto_policy_included:
        write_json(out_dir / "auto_continuation_policy.snapshot.json", dict(auto_policy))
    write_json(out_dir / "adapter_bundle_manifest.draft.json", manifest)
    print(out_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
