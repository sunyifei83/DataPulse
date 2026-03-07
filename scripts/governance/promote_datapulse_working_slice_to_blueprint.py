#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from copy import deepcopy
from pathlib import Path
from typing import Any

from datapulse_loop_contracts import (
    ACTIVE_PLAN_PATH,
    DEFAULT_OUT_DIR,
    DRAFT_PLAN_PATH,
    apply_activation_policy,
    build_code_landing_status,
    build_project_loop_state,
    deep_merge_dicts,
    display_path,
    read_json,
    refresh_recommended_next_slice,
    resolve_repo_path,
    update_phase_statuses,
    utc_now,
    write_plan,
)
from loop_core_draft import ensure_valid_blueprint_plan


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Promote one structured slice from a mutable working copy into the repository blueprint truth."
    )
    parser.add_argument(
        "--working-plan",
        type=Path,
        default=DEFAULT_OUT_DIR / "datapulse-blueprint-plan.working.json",
        help="Mutable working copy containing the proposed slice.",
    )
    parser.add_argument(
        "--target-plan",
        type=Path,
        default=ACTIVE_PLAN_PATH if ACTIVE_PLAN_PATH.exists() else DRAFT_PLAN_PATH,
        help="Repository blueprint path. If an overlay is passed, its base plan is updated instead.",
    )
    parser.add_argument("--slice-id", required=True, help="Slice id to promote from the working copy.")
    parser.add_argument("--stdout", action="store_true", help="Print the promoted target plan JSON instead of writing it.")
    return parser.parse_args()


def phase_ids(plan: dict[str, Any]) -> list[str]:
    return [str(phase.get("id", "")).strip() for phase in plan.get("phases", [])]


def slice_ids(phase: dict[str, Any]) -> list[str]:
    return [str(item.get("id", "")).strip() for item in phase.get("slices", [])]


def find_phase(plan: dict[str, Any], phase_id: str) -> tuple[int, dict[str, Any] | None]:
    for index, phase in enumerate(plan.get("phases", [])):
        if str(phase.get("id", "")).strip() == phase_id:
            return index, phase
    return -1, None


def find_slice_in_working_plan(working_plan: dict[str, Any], slice_id: str) -> tuple[dict[str, Any], int, dict[str, Any]]:
    target = slice_id.strip()
    for phase in working_plan.get("phases", []):
        for index, item in enumerate(phase.get("slices", [])):
            if str(item.get("id", "")).strip() == target:
                return phase, index, deepcopy(item)
    raise ValueError(f"Slice not found in working plan: {slice_id}")


def resolve_target_blueprint_path(raw_path: Path) -> Path:
    candidate = raw_path.expanduser().resolve()
    payload = read_json(candidate)
    if str(payload.get("schema_version", "")) != "blueprint_plan_overlay.v1":
        return candidate
    base_plan_raw = str(payload.get("base_plan", "")).strip()
    if not base_plan_raw:
        raise ValueError(f"Overlay target missing base_plan: {candidate}")
    return resolve_repo_path(base_plan_raw, relative_to=candidate)


def insert_phase_from_working(target_plan: dict[str, Any], working_plan: dict[str, Any], source_phase: dict[str, Any]) -> dict[str, Any]:
    phase_id = str(source_phase.get("id", "")).strip()
    _, existing_phase = find_phase(target_plan, phase_id)
    if existing_phase is not None:
        return existing_phase

    new_phase = {
        "id": phase_id,
        "title": str(source_phase.get("title", "")).strip(),
        "status": "pending",
        "slices": [],
    }
    target_phases = list(target_plan.get("phases", []))
    working_order = phase_ids(working_plan)
    target_order = phase_ids(target_plan)
    source_position = working_order.index(phase_id)
    insert_at = len(target_phases)

    for lookback in range(source_position - 1, -1, -1):
        anchor_id = working_order[lookback]
        if anchor_id in target_order:
            insert_at = target_order.index(anchor_id) + 1
            break
    else:
        for lookahead in range(source_position + 1, len(working_order)):
            anchor_id = working_order[lookahead]
            if anchor_id in target_order:
                insert_at = target_order.index(anchor_id)
                break

    target_phases.insert(insert_at, new_phase)
    target_plan["phases"] = target_phases
    return new_phase


def insert_slice_from_working(target_phase: dict[str, Any], source_phase: dict[str, Any], source_index: int, slice_payload: dict[str, Any]) -> None:
    target_slices = list(target_phase.get("slices", []))
    target_ids = slice_ids(target_phase)
    slice_id = str(slice_payload.get("id", "")).strip()
    if slice_id in target_ids:
        raise ValueError(f"Slice already exists in target blueprint: {slice_id}")

    source_ids = slice_ids(source_phase)
    insert_at = len(target_slices)
    for lookback in range(source_index - 1, -1, -1):
        anchor_id = source_ids[lookback]
        if anchor_id in target_ids:
            insert_at = target_ids.index(anchor_id) + 1
            break
    else:
        for lookahead in range(source_index + 1, len(source_ids)):
            anchor_id = source_ids[lookahead]
            if anchor_id in target_ids:
                insert_at = target_ids.index(anchor_id)
                break

    target_slices.insert(insert_at, slice_payload)
    target_phase["slices"] = target_slices


def build_preview_plan(raw_preview_path: Path, mutated_base_plan: dict[str, Any]) -> dict[str, Any]:
    preview_payload = read_json(raw_preview_path)
    if str(preview_payload.get("schema_version", "")) != "blueprint_plan_overlay.v1":
        return mutated_base_plan
    overlay = {key: value for key, value in preview_payload.items() if key not in {"schema_version", "base_plan"}}
    merged = deep_merge_dicts(mutated_base_plan, overlay)
    return apply_activation_policy(merged, source_path=raw_preview_path)


def summarize_target_preview(plan: dict[str, Any], slice_id: str) -> dict[str, Any]:
    landing_status = build_code_landing_status()
    loop_state = build_project_loop_state(plan, landing_status)
    next_slice = dict(loop_state.get("next_slice", {}))
    flow_control = dict(loop_state.get("flow_control", {}))
    return {
        "current_level": loop_state.get("current_level", ""),
        "selected_as_next_slice_now": str(next_slice.get("id", "")) == slice_id,
        "next_slice": next_slice,
        "status_if_run_now": flow_control.get("status_if_run_now", ""),
        "reason_if_run_now": flow_control.get("reason_if_run_now", ""),
        "blocking_facts": list(loop_state.get("blocking_facts", [])),
        "remaining_promotion_gates": list(loop_state.get("remaining_promotion_gates", [])),
        "would_auto_advance_if_ignited": str(next_slice.get("id", "")) == slice_id
        and str(flow_control.get("status_if_run_now", "")) == "ready_for_auto_advance",
    }


def main() -> int:
    args = parse_args()
    working_plan_path = args.working_plan.expanduser().resolve()
    preview_plan_path = args.target_plan.expanduser().resolve()
    target_plan_path = resolve_target_blueprint_path(args.target_plan)

    working_plan = read_json(working_plan_path)
    source_phase, source_index, slice_payload = find_slice_in_working_plan(working_plan, args.slice_id)
    target_plan = read_json(target_plan_path)
    ensure_valid_blueprint_plan(target_plan, source=display_path(target_plan_path.resolve()))

    target_phase = insert_phase_from_working(target_plan, working_plan, source_phase)
    insert_slice_from_working(target_phase, source_phase, source_index, slice_payload)

    target_plan["last_updated_utc"] = utc_now()
    update_phase_statuses(target_plan)
    refresh_recommended_next_slice(target_plan)
    ensure_valid_blueprint_plan(target_plan, source=display_path(target_plan_path.resolve()))
    preview_plan = build_preview_plan(preview_plan_path, target_plan)
    preview = summarize_target_preview(preview_plan, args.slice_id)

    if args.stdout:
        print(
            json.dumps(
                {
                    "status": "promoted",
                    "target_plan_path": str(target_plan_path),
                    "loop_read_plan_path": str(preview_plan_path),
                    "promoted_slice": slice_payload,
                    "preview": preview,
                    "plan": target_plan,
                },
                indent=2,
                ensure_ascii=True,
            )
        )
        return 0

    write_plan(target_plan_path, target_plan)
    print(
        json.dumps(
            {
                "status": "promoted",
                "target_plan_path": str(target_plan_path),
                "loop_read_plan_path": str(preview_plan_path),
                "promoted_slice": {
                    "id": str(slice_payload.get("id", "")).strip(),
                    "title": str(slice_payload.get("title", "")).strip(),
                    "phase_id": str(source_phase.get("id", "")).strip(),
                    "status": str(slice_payload.get("status", "")).strip(),
                },
                "preview": preview,
            },
            indent=2,
            ensure_ascii=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
