#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

from datapulse_loop_contracts import DEFAULT_PLAN_PATH, REPO_ROOT, build_code_landing_status, resolve_repo_path
from promote_datapulse_working_slice_to_blueprint import resolve_target_blueprint_path
from run_codex_blueprint_loop import build_subprocess_env, dispatch_workflow, git_output, wait_for_head_workflow_run

DEFAULT_IGNITION_COMMAND = """SYSTEM_VERSION_COMPAT=1 uv run python scripts/governance/run_codex_blueprint_loop.py \\
    --model gpt-5.4 \\
    --model-reasoning-effort high \\
    --ask-for-approval never \\
    --sandbox danger-full-access \\
    --continue-through-promotions \\
    --promotion-mode auto \\
    --push-remote origin \\
    --release-tag-label loop \\
    --max-rounds 24"""


def _to_text(value: Any) -> str:
    return str(value).strip() if value is not None else ""


def current_python_command() -> list[str]:
    return [sys.executable]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Land one blueprint intake into repo truth as an independent ci_proven change, then print the clean-baseline ignition command."
    )
    parser.add_argument("--slice-id", required=True, help="Slice id to land.")
    parser.add_argument(
        "--working-plan",
        type=Path,
        default=None,
        help="Existing working-copy plan containing the slice. If omitted, a temporary working plan is created from the intake arguments below.",
    )
    parser.add_argument(
        "--target-plan",
        type=Path,
        default=DEFAULT_PLAN_PATH,
        help="Blueprint target plan path. If an overlay is passed, its base plan is updated.",
    )
    parser.add_argument("--phase-id", default="", help="Required when --working-plan is not supplied.")
    parser.add_argument("--phase-title", default="", help="Optional phase title used when creating a new phase.")
    parser.add_argument("--title", default="", help="Required when --working-plan is not supplied.")
    parser.add_argument("--status", default="pending", help="Slice status for direct intake mode.")
    parser.add_argument("--category", default="manual", help="Slice category for direct intake mode.")
    parser.add_argument("--execution-profile", default="draft_only", help="Execution profile for direct intake mode.")
    parser.add_argument("--promotion-scope", default="none", help="Promotion scope for direct intake mode.")
    parser.add_argument("--before-slice-id", default="", help="Insert before this slice in direct intake mode.")
    parser.add_argument("--after-slice-id", default="", help="Insert after this slice in direct intake mode.")
    parser.add_argument("--verification-command", action="append", default=[], help="Verification command for direct intake mode.")
    parser.add_argument("--artifact", action="append", default=[], help="Artifact path for direct intake mode.")
    parser.add_argument("--draft-artifact", action="append", default=[], help="Draft artifact path for direct intake mode.")
    parser.add_argument("--exit-condition", default="", help="Exit condition for direct intake mode.")
    parser.add_argument("--fact-md", type=Path, default=None, help="Optional markdown fact source for direct intake mode.")
    parser.add_argument("--fact-md-heading", default="", help="Optional heading inside --fact-md.")
    parser.add_argument("--fact-source", action="append", default=[], help="External fact source for direct intake mode.")
    parser.add_argument("--note", action="append", default=[], help="Additional intake note for direct intake mode.")
    parser.add_argument(
        "--extra-landing-path",
        action="append",
        default=[],
        help="Additional repo paths allowed to be dirty before landing and included in the blueprint-landing commit, such as long-form governance prose.",
    )
    parser.add_argument(
        "--allow-non-current-next-slice",
        action="store_true",
        help="Allow landing even when the promoted slice is not the current next_slice after read-only preview.",
    )
    parser.add_argument("--commit-message", default="", help="Optional commit message override.")
    parser.add_argument("--push-remote", default="origin", help="Remote used for the ci_proven push.")
    parser.add_argument("--poll-interval-seconds", type=int, default=15, help="Polling interval while waiting for proof runs.")
    parser.add_argument("--ci-timeout-seconds", type=int, default=900, help="Timeout while waiting for proof runs.")
    parser.add_argument("--ignition-command", default=DEFAULT_IGNITION_COMMAND, help="Command printed when the repo returns to a clean baseline.")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--stdout", action="store_true", help="Accepted for compatibility. JSON is always printed.")
    return parser.parse_args()


def run_json_command(command: list[str], *, required: bool = True, dry_run: bool = False) -> dict[str, Any]:
    if dry_run:
        return {"dry_run": True, "command": command}
    completed = subprocess.run(
        command,
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
        env=build_subprocess_env(),
    )
    stdout = completed.stdout.strip()
    stderr = completed.stderr.strip()
    if required and completed.returncode != 0:
        raise RuntimeError(stderr or stdout or f"command failed: {' '.join(command)}")
    content = stdout or stderr
    if not content:
        return {}
    try:
        return json.loads(content)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"command did not return JSON: {' '.join(command)}") from exc


def workspace_status_lines() -> list[str]:
    output = git_output("status", "--short")
    if not output:
        return []
    return [line for line in output.splitlines() if _to_text(line)]


def changed_paths_from_status_lines(status_lines: list[str]) -> list[str]:
    paths: list[str] = []
    for line in status_lines:
        if len(line) < 3:
            continue
        raw_path = line[2:].strip()
        if " -> " in raw_path:
            paths.extend([part.strip() for part in raw_path.split(" -> ") if _to_text(part)])
        elif _to_text(raw_path):
            paths.append(raw_path)
    deduped: list[str] = []
    seen: set[str] = set()
    for item in paths:
        if item in seen:
            continue
        seen.add(item)
        deduped.append(item)
    return deduped


def repo_relative_path(path: Path) -> str:
    resolved = path.expanduser().resolve()
    try:
        return resolved.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return ""


def is_allowed_repo_path(path_text: str, allowed_roots: set[str]) -> bool:
    candidate = _to_text(path_text)
    if not candidate:
        return False
    for root in allowed_roots:
        if candidate == root or candidate.startswith(f"{root}/"):
            return True
    return False


def assert_baseline_clean_for_landing(baseline_dirty_paths: list[str], allowed_roots: set[str]) -> None:
    disallowed = [path for path in baseline_dirty_paths if not is_allowed_repo_path(path, allowed_roots)]
    if disallowed:
        raise RuntimeError(
            "blueprint landing requires a clean baseline except for declared landing paths; disallowed dirty paths: "
            + ", ".join(disallowed)
        )


def build_direct_intake_command(args: argparse.Namespace, working_plan: Path) -> list[str]:
    if not _to_text(args.phase_id):
        raise RuntimeError("Direct intake mode requires --phase-id")
    if not _to_text(args.title):
        raise RuntimeError("Direct intake mode requires --title")
    command = [
        *current_python_command(),
        "scripts/governance/intake_external_fact_to_working_slice.py",
        "--plan",
        str(working_plan),
        "--init-from",
        str(args.target_plan),
        "--phase-id",
        str(args.phase_id),
        "--slice-id",
        str(args.slice_id),
        "--title",
        str(args.title),
        "--status",
        str(args.status),
        "--category",
        str(args.category),
        "--execution-profile",
        str(args.execution_profile),
        "--promotion-scope",
        str(args.promotion_scope),
    ]
    if _to_text(args.phase_title):
        command.extend(["--phase-title", str(args.phase_title)])
    if _to_text(args.before_slice_id):
        command.extend(["--before-slice-id", str(args.before_slice_id)])
    if _to_text(args.after_slice_id):
        command.extend(["--after-slice-id", str(args.after_slice_id)])
    if _to_text(args.exit_condition):
        command.extend(["--exit-condition", str(args.exit_condition)])
    if args.fact_md is not None:
        command.extend(["--fact-md", str(args.fact_md)])
    if _to_text(args.fact_md_heading):
        command.extend(["--fact-md-heading", str(args.fact_md_heading)])
    for item in args.verification_command:
        command.extend(["--verification-command", str(item)])
    for item in args.artifact:
        command.extend(["--artifact", str(item)])
    for item in args.draft_artifact:
        command.extend(["--draft-artifact", str(item)])
    for item in args.fact_source:
        command.extend(["--fact-source", str(item)])
    for item in args.note:
        command.extend(["--note", str(item)])
    return command


def ensure_working_plan(args: argparse.Namespace) -> tuple[Path, Path | None]:
    if args.working_plan is not None:
        return args.working_plan.expanduser().resolve(), None
    temp_dir = Path(tempfile.mkdtemp(prefix="datapulse_blueprint_intake_"))
    working_plan = temp_dir / "datapulse-blueprint-plan.working.json"
    run_json_command(build_direct_intake_command(args, working_plan), dry_run=False)
    return working_plan, temp_dir


def preview_promotion(working_plan: Path, target_plan: Path, slice_id: str, *, dry_run: bool) -> dict[str, Any]:
    if dry_run:
        return {
            "status": "preview_skipped_in_dry_run",
            "preview": {
                "selected_as_next_slice_now": True,
                "would_auto_advance_if_ignited": True,
            },
        }
    return run_json_command(
        [
            *current_python_command(),
            "scripts/governance/promote_datapulse_working_slice_to_blueprint.py",
            "--working-plan",
            str(working_plan),
            "--target-plan",
            str(target_plan),
            "--slice-id",
            slice_id,
            "--stdout",
        ]
    )


def write_promotion(working_plan: Path, target_plan: Path, slice_id: str, *, dry_run: bool) -> dict[str, Any]:
    if dry_run:
        return {"status": "promotion_skipped_in_dry_run"}
    return run_json_command(
        [
            *current_python_command(),
            "scripts/governance/promote_datapulse_working_slice_to_blueprint.py",
            "--working-plan",
            str(working_plan),
            "--target-plan",
            str(target_plan),
            "--slice-id",
            slice_id,
        ]
    )


def read_only_runtime_export(target_plan: Path, *, dry_run: bool) -> dict[str, Any]:
    if dry_run:
        return {"status": "runtime_export_skipped_in_dry_run"}
    return run_json_command(
        [
            *current_python_command(),
            "scripts/governance/run_datapulse_blueprint_loop.py",
            "--plan",
            str(target_plan),
        ]
    )


def stage_and_commit_paths(paths: list[str], commit_message: str, *, dry_run: bool) -> dict[str, Any]:
    payload = {
        "commit_message": commit_message,
        "paths": paths,
    }
    if dry_run:
        payload["dry_run"] = True
        return payload
    subprocess.run(["git", "add", "-A", "--", *paths], cwd=REPO_ROOT, check=True)
    subprocess.run(["git", "commit", "-m", commit_message], cwd=REPO_ROOT, check=True)
    payload["head"] = git_output("rev-parse", "HEAD")
    return payload


def push_branch(remote: str, branch: str, *, dry_run: bool) -> dict[str, Any]:
    payload = {
        "remote": remote,
        "branch": branch,
        "head": git_output("rev-parse", "HEAD"),
    }
    if dry_run:
        payload["dry_run"] = True
        return payload
    subprocess.run(["git", "push", remote, branch], cwd=REPO_ROOT, check=True)
    payload["upstream_head"] = git_output("rev-parse", "@{u}")
    return payload


def wait_for_ci_proof(*, remote: str, dry_run: bool, poll_interval_seconds: int, ci_timeout_seconds: int) -> dict[str, Any]:
    landing_status = build_code_landing_status()
    git_truth = dict(landing_status.get("git", {}))
    ci_truth = dict(landing_status.get("ci", {}))
    branch = _to_text(git_truth.get("branch"))
    head_sha = _to_text(git_truth.get("head"))
    required_workflow = _to_text(ci_truth.get("required_workflow"))
    proof_mode = _to_text(ci_truth.get("proof_mode")) or "push_ci_workflow"
    if not branch or not head_sha:
        raise RuntimeError("Missing branch/head truth for ci_proven wait")
    payload = {
        "proof_mode": proof_mode,
        "required_workflow": required_workflow,
        "branch": branch,
        "head": head_sha,
    }
    payload["push"] = push_branch(remote, branch, dry_run=dry_run)
    if dry_run:
        payload["dry_run"] = True
        return payload
    if proof_mode == "governance_evidence_dispatch":
        if not required_workflow:
            raise RuntimeError("governance_evidence_dispatch requires required_workflow truth")
        payload["dispatch"] = dispatch_workflow(required_workflow, branch, dry_run=False)
    if required_workflow:
        payload["workflow_run"] = wait_for_head_workflow_run(
            required_workflow,
            branch=branch,
            head_sha=head_sha,
            timeout_seconds=ci_timeout_seconds,
            poll_interval_seconds=poll_interval_seconds,
        )
    return payload


def main() -> int:
    args = parse_args()
    target_plan_arg = args.target_plan.expanduser().resolve()
    target_plan_path = resolve_target_blueprint_path(target_plan_arg)
    extra_landing_paths = [resolve_repo_path(item) for item in args.extra_landing_path]
    raw_commit_paths = [repo_relative_path(target_plan_path), *[repo_relative_path(path) for path in extra_landing_paths]]
    commit_paths: list[str] = []
    seen_commit_paths: set[str] = set()
    for path in raw_commit_paths:
        normalized = _to_text(path)
        if not normalized or normalized in seen_commit_paths:
            continue
        seen_commit_paths.add(normalized)
        commit_paths.append(normalized)
    if not commit_paths:
        raise RuntimeError("No repo-local commit paths resolved for blueprint landing")

    baseline_status_lines = workspace_status_lines()
    baseline_dirty_paths = changed_paths_from_status_lines(baseline_status_lines)
    assert_baseline_clean_for_landing(baseline_dirty_paths, set(commit_paths))

    working_plan_path, temp_dir = ensure_working_plan(args)
    try:
        preview_payload = preview_promotion(
            working_plan_path,
            target_plan_arg,
            str(args.slice_id),
            dry_run=bool(args.dry_run),
        )
        preview = dict(preview_payload.get("preview", {}))
        selected_as_next = bool(preview.get("selected_as_next_slice_now", False))
        if not args.allow_non_current_next_slice and not selected_as_next:
            raise RuntimeError(
                "Promoted slice is not the current next_slice in read-only preview; rerun with --allow-non-current-next-slice only if that is intentional."
            )

        promotion_payload = write_promotion(
            working_plan_path,
            target_plan_arg,
            str(args.slice_id),
            dry_run=bool(args.dry_run),
        )
        runtime_export = read_only_runtime_export(target_plan_arg, dry_run=bool(args.dry_run))
        runtime_next_slice = _to_text(dict(runtime_export.get("next_slice", {})).get("id"))
        if (
            not args.allow_non_current_next_slice
            and not args.dry_run
            and runtime_next_slice != _to_text(args.slice_id)
        ):
            raise RuntimeError(
                f"Read-only loop export does not resolve to the landed slice: expected {_to_text(args.slice_id)}, got {runtime_next_slice or 'none'}"
            )

        commit_message = _to_text(args.commit_message) or f"chore(blueprint): land {args.slice_id}"
        commit_payload = stage_and_commit_paths(commit_paths, commit_message, dry_run=bool(args.dry_run))
        proof_payload = wait_for_ci_proof(
            remote=str(args.push_remote),
            dry_run=bool(args.dry_run),
            poll_interval_seconds=int(args.poll_interval_seconds),
            ci_timeout_seconds=int(args.ci_timeout_seconds),
        )
        final_dirty_paths = changed_paths_from_status_lines(workspace_status_lines())
        if final_dirty_paths and not args.dry_run:
            raise RuntimeError(
                "Blueprint landing completed but repo is not back to a clean baseline: "
                + ", ".join(final_dirty_paths)
            )
        payload = {
            "status": "blueprint_landing_completed" if not args.dry_run else "blueprint_landing_dry_run",
            "promoted_slice": _to_text(args.slice_id),
            "target_plan_path": str(target_plan_path),
            "preview": preview,
            "promotion": promotion_payload,
            "runtime_export": runtime_export,
            "commit": commit_payload,
            "ci_proof": proof_payload,
            "workspace_clean_after": not final_dirty_paths,
            "workspace_dirty_after": final_dirty_paths,
            "ignition_command": str(args.ignition_command),
        }
        print(json.dumps(payload, indent=2, ensure_ascii=True))
        return 0
    finally:
        if temp_dir is not None and temp_dir.exists():
            for child in temp_dir.iterdir():
                child.unlink(missing_ok=True)
            temp_dir.rmdir()


if __name__ == "__main__":
    raise SystemExit(main())
