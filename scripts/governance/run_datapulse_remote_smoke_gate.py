#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import subprocess
from pathlib import Path

from datapulse_loop_contracts import REPO_ROOT, latest_artifact_file, parse_remote_report


REMOTE_SMOKE_SCRIPT = REPO_ROOT / "scripts/datapulse_remote_openclaw_smoke.sh"


def default_run_id() -> str:
    completed = subprocess.run(
        ["date", "+%Y%m%d_%H%M%S"],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Manual-only strict gate wrapper for datapulse_remote_openclaw_smoke.sh. Not wired into existing workflows."
    )
    parser.add_argument("--run-id", default=os.environ.get("RUN_ID", ""), help="RUN_ID to use when executing the remote smoke script.")
    parser.add_argument("--report", type=Path, help="Evaluate an explicit remote_report.md instead of running the smoke script.")
    parser.add_argument(
        "--latest-only",
        action="store_true",
        help="Evaluate the latest remote_report.md under artifacts without running the smoke script.",
    )
    parser.add_argument(
        "--allow-failed-steps",
        type=int,
        default=0,
        help="Allowed failed step count before this wrapper returns nonzero.",
    )
    parser.add_argument(
        "--require-no-block-codes",
        action="store_true",
        help="Also fail if the parsed remote report contains any block codes.",
    )
    parser.add_argument("--json", action="store_true", help="Print machine-readable summary JSON.")
    return parser.parse_args()


def resolve_report_path(args: argparse.Namespace) -> tuple[Path | None, int]:
    if args.report:
        return args.report.resolve(), 0
    if args.latest_only:
        return latest_artifact_file("remote_report.md"), 0

    run_id = args.run_id or default_run_id()
    env = os.environ.copy()
    env["RUN_ID"] = run_id
    completed = subprocess.run(["bash", str(REMOTE_SMOKE_SCRIPT)], cwd=REPO_ROOT, env=env, check=False)
    report_path = REPO_ROOT / f"artifacts/openclaw_datapulse_{run_id}/remote_report.md"
    return report_path, completed.returncode


def main() -> int:
    args = parse_args()
    report_path, command_rc = resolve_report_path(args)
    if report_path is None or not report_path.exists():
        payload = {
            "ok": False,
            "reason": "remote_report_missing",
            "report_path": str(report_path) if report_path else "",
            "command_rc": command_rc,
        }
        if args.json:
            print(json.dumps(payload, indent=2, ensure_ascii=True))
        else:
            print(f"[gate] missing remote report: {payload['report_path']}")
        return 2

    summary = parse_remote_report(report_path)
    if summary is None:
        payload = {
            "ok": False,
            "reason": "remote_report_unparseable",
            "report_path": str(report_path),
            "command_rc": command_rc,
        }
        if args.json:
            print(json.dumps(payload, indent=2, ensure_ascii=True))
        else:
            print(f"[gate] unparseable remote report: {report_path}")
        return 2

    failed_steps = int(summary.get("failed_steps", 0))
    block_codes = list(summary.get("block_codes", []))
    ok = command_rc == 0 and failed_steps <= args.allow_failed_steps
    if args.require_no_block_codes and block_codes:
        ok = False

    payload = {
        "ok": ok,
        "command_rc": command_rc,
        "report_path": str(report_path.relative_to(REPO_ROOT)),
        "run_id": summary.get("run_id", ""),
        "failed_steps": failed_steps,
        "allow_failed_steps": args.allow_failed_steps,
        "block_codes": block_codes,
        "require_no_block_codes": args.require_no_block_codes,
    }
    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=True))
    else:
        state = "PASS" if ok else "FAIL"
        print(
            f"[gate] {state} remote smoke run_id={payload['run_id']} "
            f"failed_steps={failed_steps} block_codes={len(block_codes)}"
        )
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
