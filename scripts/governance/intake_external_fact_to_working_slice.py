#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from datapulse_loop_contracts import (
    DEFAULT_OUT_DIR,
    DEFAULT_PLAN_PATH,
    assert_plan_path_mutable,
    build_code_landing_status,
    build_project_loop_state,
    load_plan,
    prepare_working_copy,
    utc_now,
    update_phase_statuses,
    write_plan,
)


ALLOWED_SLICE_STATUSES = {"pending", "in_progress", "completed", "skipped", "blocked", "failed"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Intake an external fact into a mutable DataPulse blueprint working copy as a structured slice proposal."
    )
    parser.add_argument(
        "--plan",
        type=Path,
        default=DEFAULT_OUT_DIR / "datapulse-blueprint-plan.working.json",
        help="Mutable working copy path. This script refuses to modify docs/governance plans.",
    )
    parser.add_argument(
        "--init-from",
        type=Path,
        default=DEFAULT_PLAN_PATH,
        help="Source plan used when --plan does not yet exist.",
    )
    parser.add_argument("--phase-id", required=True, help="Target phase id. Creates the phase when missing.")
    parser.add_argument("--phase-title", default="", help="Required when creating a new phase.")
    parser.add_argument("--slice-id", required=True, help="New structured slice id.")
    parser.add_argument("--title", required=True, help="New structured slice title.")
    parser.add_argument(
        "--status",
        default="pending",
        choices=sorted(ALLOWED_SLICE_STATUSES),
        help="Structured slice status. Use pending or in_progress if the loop should see the slice as open.",
    )
    parser.add_argument("--category", default="manual", help="Slice category. Defaults to manual.")
    parser.add_argument(
        "--execution-profile",
        default="draft_only",
        help="Execution profile declared in slice_profiles.",
    )
    parser.add_argument("--promotion-scope", default="none", help="Promotion scope. Defaults to none.")
    parser.add_argument(
        "--before-slice-id",
        default="",
        help="Insert the new slice before this slice inside the target phase.",
    )
    parser.add_argument(
        "--after-slice-id",
        default="",
        help="Insert the new slice after this slice inside the target phase.",
    )
    parser.add_argument(
        "--verification-command",
        action="append",
        default=[],
        help="Verification command to run after landing the slice. May be passed multiple times.",
    )
    parser.add_argument(
        "--artifact",
        action="append",
        default=[],
        help="Artifact path produced or updated by the slice. May be passed multiple times.",
    )
    parser.add_argument(
        "--draft-artifact",
        action="append",
        default=[],
        help="Draft artifact path produced before active wiring. May be passed multiple times.",
    )
    parser.add_argument("--exit-condition", default="", help="Exit condition for the slice.")
    parser.add_argument(
        "--fact-md",
        type=Path,
        default=None,
        help="Optional external Obsidian/Markdown fact source. The path is recorded in fact_sources and fact_intake.",
    )
    parser.add_argument(
        "--fact-md-heading",
        default="",
        help="Optional heading within --fact-md that the slice comes from.",
    )
    parser.add_argument(
        "--fact-source",
        action="append",
        default=[],
        help="External fact source path, note, or URI. May be passed multiple times.",
    )
    parser.add_argument(
        "--note",
        action="append",
        default=[],
        help="Additional intake note. May be passed multiple times.",
    )
    parser.add_argument(
        "--stdout",
        action="store_true",
        help="Print the mutated working copy instead of writing it to --plan.",
    )
    return parser.parse_args()


def strip_wrapping_quotes(value: str) -> str:
    text = value.strip()
    if len(text) >= 2 and ((text[0] == '"' and text[-1] == '"') or (text[0] == "'" and text[-1] == "'")):
        return text[1:-1].strip()
    return text


def resolve_fact_md(raw_path: Path | None) -> Path | None:
    if raw_path is None:
        return None
    resolved = raw_path.expanduser().resolve()
    if not resolved.exists():
        raise ValueError(f"Fact markdown source not found: {resolved}")
    if not resolved.is_file():
        raise ValueError(f"Fact markdown source is not a file: {resolved}")
    if resolved.suffix.lower() != ".md":
        raise ValueError(f"Fact markdown source must be a .md file: {resolved}")
    return resolved


def parse_fact_md_metadata(fact_md: Path | None, heading_hint: str) -> dict[str, Any]:
    if fact_md is None:
        return {}

    text = fact_md.read_text(encoding="utf-8")
    lines = text.splitlines()
    frontmatter_title = ""
    heading_values: list[str] = []
    heading_lines: list[str] = []
    selected_heading = ""
    in_frontmatter = bool(lines and lines[0].strip() == "---")
    frontmatter_done = not in_frontmatter

    for index, raw_line in enumerate(lines):
        line = raw_line.rstrip()
        if in_frontmatter and index == 0:
            continue
        if in_frontmatter and not frontmatter_done:
            if line.strip() == "---":
                frontmatter_done = True
                continue
            if line.strip().startswith("title:"):
                _, value = line.split(":", 1)
                frontmatter_title = strip_wrapping_quotes(value)
            continue
        if line.lstrip().startswith("#"):
            heading_text = line.lstrip("#").strip()
            if heading_text:
                heading_values.append(heading_text)
                heading_lines.append(heading_text)

    if heading_hint.strip():
        target = heading_hint.strip()
        if target not in heading_lines:
            raise ValueError(f"Heading not found in {fact_md}: {target}")
        selected_heading = target

    return {
        "path": str(fact_md),
        "frontmatter_title": frontmatter_title,
        "first_heading": heading_values[0] if heading_values else "",
        "selected_heading": selected_heading,
        "wikilink_name": fact_md.stem,
    }


def ensure_working_copy(plan_path: Path, init_from: Path) -> dict[str, Any]:
    assert_plan_path_mutable(plan_path)
    if plan_path.exists():
        plan = load_plan(plan_path)
        plan["_source_path"] = str(plan_path.resolve())
        return plan
    plan = prepare_working_copy(init_from, plan_path)
    plan["_source_path"] = str(plan_path.resolve())
    return plan


def find_phase(plan: dict[str, Any], phase_id: str) -> dict[str, Any] | None:
    for phase in plan.get("phases", []):
        if str(phase.get("id", "")).strip() == phase_id:
            return phase
    return None


def phase_slice_ids(phase: dict[str, Any]) -> list[str]:
    return [str(item.get("id", "")).strip() for item in phase.get("slices", [])]


def ensure_unique_slice_id(plan: dict[str, Any], slice_id: str) -> None:
    for phase in plan.get("phases", []):
        for item in phase.get("slices", []):
            if str(item.get("id", "")).strip() == slice_id:
                raise ValueError(f"Slice already exists: {slice_id}")


def ensure_phase(plan: dict[str, Any], phase_id: str, phase_title: str) -> dict[str, Any]:
    phase = find_phase(plan, phase_id)
    if phase is not None:
        return phase
    if not phase_title.strip():
        raise ValueError(f"Missing --phase-title for new phase: {phase_id}")
    phase = {
        "id": phase_id,
        "title": phase_title.strip(),
        "status": "pending",
        "slices": [],
    }
    phases = list(plan.get("phases", []))
    phases.append(phase)
    plan["phases"] = phases
    return phase


def validate_position_args(before_slice_id: str, after_slice_id: str) -> None:
    if before_slice_id and after_slice_id:
        raise ValueError("Use only one of --before-slice-id or --after-slice-id.")


def build_slice_payload(args: argparse.Namespace, fact_md_meta: dict[str, Any]) -> dict[str, Any]:
    fact_sources = list(args.fact_source)
    fact_md_path = str(fact_md_meta.get("path", "")).strip()
    selected_heading = str(fact_md_meta.get("selected_heading", "")).strip()
    if fact_md_path:
        fact_sources.append(f"{fact_md_path}#{selected_heading}" if selected_heading else fact_md_path)

    payload: dict[str, Any] = {
        "id": args.slice_id,
        "title": args.title,
        "category": args.category,
        "execution_profile": args.execution_profile,
        "promotion_scope": args.promotion_scope,
        "status": args.status,
    }
    if args.verification_command:
        payload["verification_commands"] = list(args.verification_command)
    if args.artifact:
        payload["artifacts"] = list(args.artifact)
    if args.draft_artifact:
        payload["draft_artifacts"] = list(args.draft_artifact)
    if args.exit_condition.strip():
        payload["exit_condition"] = args.exit_condition.strip()
    if fact_sources:
        payload["fact_sources"] = fact_sources
    if args.note:
        payload["notes"] = list(args.note)
    fact_intake: dict[str, Any] = {
        "imported_at_utc": utc_now(),
        "source_count": len(fact_sources),
    }
    if fact_md_meta:
        fact_intake["source_note"] = {
            "path": fact_md_path,
            "frontmatter_title": str(fact_md_meta.get("frontmatter_title", "")).strip(),
            "first_heading": str(fact_md_meta.get("first_heading", "")).strip(),
            "selected_heading": selected_heading,
            "wikilink_name": str(fact_md_meta.get("wikilink_name", "")).strip(),
        }
    payload["fact_intake"] = fact_intake
    return payload


def insert_slice(phase: dict[str, Any], slice_payload: dict[str, Any], *, before_slice_id: str, after_slice_id: str) -> None:
    slices = list(phase.get("slices", []))
    target_id = before_slice_id or after_slice_id
    if not target_id:
        slices.append(slice_payload)
        phase["slices"] = slices
        return

    ids = phase_slice_ids(phase)
    if target_id not in ids:
        raise ValueError(f"Target slice for insertion not found in phase {phase.get('id')}: {target_id}")
    position = ids.index(target_id)
    insert_at = position if before_slice_id else position + 1
    slices.insert(insert_at, slice_payload)
    phase["slices"] = slices


def validate_execution_profile(plan: dict[str, Any], execution_profile: str) -> None:
    profiles = dict(plan.get("slice_profiles", {}))
    if execution_profile not in profiles:
        raise ValueError(f"Unknown execution profile: {execution_profile}")


def summarize_preview(plan: dict[str, Any], inserted_slice_id: str) -> dict[str, Any]:
    landing_status = build_code_landing_status()
    loop_state = build_project_loop_state(plan, landing_status)
    next_slice = dict(loop_state.get("next_slice", {}))
    flow_control = dict(loop_state.get("flow_control", {}))
    selected_now = str(next_slice.get("id", "")) == inserted_slice_id
    ready_for_auto = selected_now and str(flow_control.get("status_if_run_now", "")) == "ready_for_auto_advance"
    return {
        "current_level": loop_state.get("current_level", ""),
        "selected_as_next_slice_now": selected_now,
        "next_slice": next_slice,
        "status_if_run_now": flow_control.get("status_if_run_now", ""),
        "reason_if_run_now": flow_control.get("reason_if_run_now", ""),
        "blocking_facts": list(loop_state.get("blocking_facts", [])),
        "remaining_promotion_gates": list(loop_state.get("remaining_promotion_gates", [])),
        "would_auto_advance_if_ignited": ready_for_auto,
    }


def main() -> int:
    args = parse_args()
    validate_position_args(args.before_slice_id, args.after_slice_id)
    fact_md = resolve_fact_md(args.fact_md)
    fact_md_meta = parse_fact_md_metadata(fact_md, args.fact_md_heading)
    plan = ensure_working_copy(args.plan, args.init_from)
    validate_execution_profile(plan, args.execution_profile)
    ensure_unique_slice_id(plan, args.slice_id)
    phase = ensure_phase(plan, args.phase_id, args.phase_title)
    slice_payload = build_slice_payload(args, fact_md_meta)
    insert_slice(
        phase,
        slice_payload,
        before_slice_id=args.before_slice_id.strip(),
        after_slice_id=args.after_slice_id.strip(),
    )
    plan["last_updated_utc"] = utc_now()
    update_phase_statuses(plan)
    preview = summarize_preview(plan, args.slice_id)

    if args.stdout:
        print(
            json.dumps(
                {
                    "status": "proposed",
                    "plan_path": str(args.plan),
                    "inserted_slice": slice_payload,
                    "preview": preview,
                    "fact_source_note": fact_md_meta,
                    "plan": plan,
                },
                indent=2,
                ensure_ascii=True,
            )
        )
        return 0

    write_plan(args.plan, plan)
    print(
        json.dumps(
            {
                "status": "proposed",
                "plan_path": str(args.plan),
                "inserted_slice": {
                    "id": slice_payload.get("id", ""),
                    "title": slice_payload.get("title", ""),
                    "status": slice_payload.get("status", ""),
                    "phase_id": args.phase_id,
                },
                "preview": preview,
                "fact_source_note": fact_md_meta,
            },
            indent=2,
            ensure_ascii=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
