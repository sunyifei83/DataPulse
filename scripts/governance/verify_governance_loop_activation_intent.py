#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from export_governance_loop_activation_plan import load_activation_plan_from_bundle


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Verify that a governance loop activation intent remains aligned with the activation plan derived from a bundle."
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
        required=True,
        help="Path to a governance_loop_activation_intent.v1 JSON payload.",
    )
    return parser.parse_args()


def intent_surface_ids(payload: dict[str, Any]) -> set[str]:
    return {
        str(item.get("surface_id", ""))
        for item in payload.get("repo_governance_targets", [])
        if item.get("surface_id")
    }


def intent_prereq_ids(payload: dict[str, Any]) -> set[str]:
    return {
        str(item.get("surface_id", ""))
        for item in payload.get("project_adapter_prerequisites", [])
        if item.get("surface_id")
    }


def intent_runtime_facts(payload: dict[str, Any]) -> set[str]:
    return {
        str(item.get("fact", ""))
        for item in payload.get("runtime_cutover_window", {}).get("facts", [])
        if item.get("fact")
    }


def main() -> int:
    args = parse_args()
    activation_plan, exit_code = load_activation_plan_from_bundle(args.bundle_dir)
    if exit_code:
        print(json.dumps(activation_plan, indent=2, ensure_ascii=True))
        return exit_code

    intent = read_json(args.activation_intent_json)

    expected_repo = {
        str(item.get("surface_id", ""))
        for item in next(
            (track for track in activation_plan.get("activation_tracks", []) if track.get("track_id") == "repo_governance_cutover"),
            {"items": []},
        ).get("items", [])
        if item.get("surface_id")
    }
    expected_adapter = {
        str(item.get("surface_id", ""))
        for item in next(
            (track for track in activation_plan.get("activation_tracks", []) if track.get("track_id") == "project_adapter_completion"),
            {"items": []},
        ).get("items", [])
        if item.get("surface_id")
    }
    expected_runtime = {
        str(item.get("fact", ""))
        for item in next(
            (track for track in activation_plan.get("activation_tracks", []) if track.get("track_id") == "runtime_cutover_window"),
            {"items": []},
        ).get("items", [])
        if item.get("fact")
    }

    actual_repo = intent_surface_ids(intent)
    actual_adapter = intent_prereq_ids(intent)
    actual_runtime = intent_runtime_facts(intent)

    checks = [
        {
            "name": "intent_schema_version",
            "ok": str(intent.get("schema_version", "")) == "governance_loop_activation_intent.v1",
            "details": ["activation intent schema is correct"]
            if str(intent.get("schema_version", "")) == "governance_loop_activation_intent.v1"
            else [f"unexpected_schema_version:{intent.get('schema_version', '')}"],
        },
        {
            "name": "repo_governance_targets_cover_plan",
            "ok": actual_repo == expected_repo,
            "details": ["repo-governance targets match activation plan"]
            if actual_repo == expected_repo
            else [f"missing_or_extra_repo_targets:{sorted(actual_repo.symmetric_difference(expected_repo))}"],
        },
        {
            "name": "adapter_prerequisites_cover_plan",
            "ok": actual_adapter == expected_adapter,
            "details": ["adapter prerequisites match activation plan"]
            if actual_adapter == expected_adapter
            else [f"missing_or_extra_adapter_prereqs:{sorted(actual_adapter.symmetric_difference(expected_adapter))}"],
        },
        {
            "name": "runtime_cutover_window_matches_plan",
            "ok": actual_runtime == expected_runtime,
            "details": ["runtime cutover facts match activation plan"]
            if actual_runtime == expected_runtime
            else [f"missing_or_extra_runtime_facts:{sorted(actual_runtime.symmetric_difference(expected_runtime))}"],
        },
        {
            "name": "cutover_ready_flag_respects_plan",
            "ok": bool(intent.get("intent_status", {}).get("ready_for_repo_cutover", False))
            == bool(activation_plan.get("activation_status", {}).get("ready_for_active_wiring", False)),
            "details": ["cutover readiness flag matches activation plan"]
            if bool(intent.get("intent_status", {}).get("ready_for_repo_cutover", False))
            == bool(activation_plan.get("activation_status", {}).get("ready_for_active_wiring", False))
            else ["cutover readiness flag diverges from activation plan"],
        },
        {
            "name": "cutover_now_flag_respects_runtime_window",
            "ok": bool(intent.get("intent_status", {}).get("cutover_now_recommended", False))
            == bool(activation_plan.get("activation_status", {}).get("cutover_now_recommended", False)),
            "details": ["cutover-now recommendation matches activation plan"]
            if bool(intent.get("intent_status", {}).get("cutover_now_recommended", False))
            == bool(activation_plan.get("activation_status", {}).get("cutover_now_recommended", False))
            else ["cutover-now recommendation diverges from activation plan"],
        },
    ]

    payload = {
        "valid": all(item["ok"] for item in checks),
        "bundle_dir": str(args.bundle_dir),
        "activation_intent_json": str(args.activation_intent_json),
        "checks": checks,
        "expected": {
            "repo_governance_targets": sorted(expected_repo),
            "adapter_prerequisites": sorted(expected_adapter),
            "runtime_cutover_facts": sorted(expected_runtime),
            "ready_for_repo_cutover": bool(activation_plan.get("activation_status", {}).get("ready_for_active_wiring", False)),
            "cutover_now_recommended": bool(activation_plan.get("activation_status", {}).get("cutover_now_recommended", False)),
        },
    }
    print(json.dumps(payload, indent=2, ensure_ascii=True))
    return 0 if payload["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
