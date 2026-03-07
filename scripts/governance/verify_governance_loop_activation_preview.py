#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from export_governance_loop_activation_intent import build_activation_intent
from export_governance_loop_activation_plan import load_activation_plan_from_bundle
from export_governance_loop_activation_preview import build_activation_preview


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Verify that a governance loop activation preview remains aligned with the activation intent and activation plan."
    )
    parser.add_argument(
        "--bundle-dir",
        type=Path,
        required=True,
        help="Directory containing adapter_bundle_manifest.draft.json and referenced snapshot files.",
    )
    parser.add_argument(
        "--activation-intent-json",
        type=Path,
        help="Optional activation intent JSON. If omitted, the verifier derives intent from the bundle.",
    )
    parser.add_argument(
        "--activation-preview-json",
        type=Path,
        required=True,
        help="Path to a governance_loop_activation_preview.v1 JSON payload.",
    )
    return parser.parse_args()


def comparable_preview(payload: dict[str, Any]) -> dict[str, Any]:
    keys = [
        "schema_version",
        "project",
        "preview_status",
        "projected_post_cutover_state",
        "repo_governance_bindings",
        "project_adapter_prerequisites",
        "runtime_cutover_window",
        "non_goals",
    ]
    return {key: payload.get(key) for key in keys}


def main() -> int:
    args = parse_args()
    activation_plan, exit_code = load_activation_plan_from_bundle(args.bundle_dir)
    if exit_code:
        print(json.dumps(activation_plan, indent=2, ensure_ascii=True))
        return exit_code

    if args.activation_intent_json:
        intent = read_json(args.activation_intent_json)
    else:
        intent = build_activation_intent(activation_plan)

    expected = build_activation_preview(activation_plan, intent)
    actual = read_json(args.activation_preview_json)

    expected_comp = comparable_preview(expected)
    actual_comp = comparable_preview(actual)
    mismatches = [key for key, value in expected_comp.items() if actual_comp.get(key) != value]

    checks = [
        {
            "name": "preview_schema_version",
            "ok": str(actual.get("schema_version", "")) == "governance_loop_activation_preview.v1",
            "details": ["activation preview schema is correct"]
            if str(actual.get("schema_version", "")) == "governance_loop_activation_preview.v1"
            else [f"unexpected_schema_version:{actual.get('schema_version', '')}"],
        },
        {
            "name": "preview_matches_plan_and_intent",
            "ok": not mismatches,
            "details": ["activation preview matches activation plan and intent"]
            if not mismatches
            else [f"preview_mismatches:{mismatches}"],
        },
    ]

    payload = {
        "valid": all(item["ok"] for item in checks),
        "bundle_dir": str(args.bundle_dir),
        "activation_preview_json": str(args.activation_preview_json),
        "checks": checks,
    }
    print(json.dumps(payload, indent=2, ensure_ascii=True))
    return 0 if payload["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
