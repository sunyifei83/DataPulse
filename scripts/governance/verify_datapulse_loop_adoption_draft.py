#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

from datapulse_loop_adapter_draft import DEFAULT_CATALOG_PATH, build_datapulse_loop_runtime
from datapulse_loop_contracts import DEFAULT_PLAN_PATH, build_code_landing_status, load_plan, write_json
from export_datapulse_loop_adapter_bundle import build_manifest
from loop_bundle_draft import build_bundle_runtime_payload, compare_loop_payloads


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Verify that the DataPulse adapter runtime matches the generic bundle replay."
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
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    adapter_payload = build_datapulse_loop_runtime(args.plan, args.catalog, [])

    with tempfile.TemporaryDirectory() as tmp_dir:
        bundle_dir = Path(tmp_dir) / "datapulse-bundle"
        bundle_dir.mkdir(parents=True, exist_ok=True)

        plan = load_plan(args.plan)
        landing_status = build_code_landing_status()
        manifest = build_manifest(str(plan.get("project", "DataPulse")))

        write_json(bundle_dir / "blueprint_plan.snapshot.json", plan)
        write_json(bundle_dir / "code_landing_status.snapshot.json", landing_status)
        write_json(bundle_dir / "slice_adapter_catalog.snapshot.json", json.loads(args.catalog.read_text(encoding="utf-8")))
        write_json(bundle_dir / "adapter_bundle_manifest.draft.json", manifest)

        replay_payload, replay_errors, resolved_files, manifest_path = build_bundle_runtime_payload(bundle_dir, [])
        mismatches = compare_loop_payloads(adapter_payload, replay_payload) if not replay_errors else ["comparison_skipped_due_to_bundle_errors"]

        checks = [
            {
                "name": "bundle_replay",
                "ok": not replay_errors,
                "details": replay_errors or ["bundle replay succeeded"],
            },
            {
                "name": "adapter_runtime_matches_bundle_replay",
                "ok": not mismatches,
                "details": mismatches or ["adapter runtime matches bundle replay on comparable fields"],
            },
        ]

        payload = {
            "valid": all(item["ok"] for item in checks),
            "bundle_dir": str(bundle_dir),
            "manifest_path": manifest_path,
            "resolved_files": resolved_files,
            "checks": checks,
            "adapter_runtime": adapter_payload,
            "replay": replay_payload,
        }
        print(json.dumps(payload, indent=2, ensure_ascii=True))
        return 0 if payload["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
