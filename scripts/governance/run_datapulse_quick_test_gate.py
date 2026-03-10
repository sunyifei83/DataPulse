#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
from pathlib import Path

from datapulse_loop_contracts import DEFAULT_QUICK_TEST_GATE_PATH, REPO_ROOT, display_path, utc_now, write_json

DEFAULT_OUTPUT_PATH = DEFAULT_QUICK_TEST_GATE_PATH


def shell_words(value: str) -> list[str]:
    return [part for part in value.split() if part]


def detect_python_cmd() -> list[str]:
    env_python = os.environ.get("PYTHON_BIN", "").strip()
    if env_python:
        return shell_words(env_python)
    if shutil.which("uv"):
        return ["uv", "run", "python3"]
    if shutil.which("python3"):
        return ["python3"]
    if shutil.which("python"):
        return ["python"]
    raise RuntimeError("Python executable not found.")


def detect_command(preferred: str, fallback: list[str]) -> list[str]:
    if shutil.which(preferred):
        return [preferred]
    return fallback


def detect_python_tool(tool: str, python_cmd: list[str], *, module: str | None = None) -> list[str]:
    if shutil.which("uv"):
        return ["uv", "run", tool]
    if shutil.which(tool):
        return [tool]
    return python_cmd + ["-m", module or tool]


def git_output(*args: str) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        return ""
    return completed.stdout.strip()


def run_step(name: str, command: list[str]) -> dict[str, object]:
    completed = subprocess.run(command, cwd=REPO_ROOT, check=False, capture_output=True, text=True)
    return {
        "name": name,
        "command": command,
        "rc": completed.returncode,
        "ok": completed.returncode == 0,
        "stdout_tail": completed.stdout.strip().splitlines()[-5:],
        "stderr_tail": completed.stderr.strip().splitlines()[-5:],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Manual-only strict, read-only quick gate for DataPulse. Not wired into existing workflows."
    )
    parser.add_argument(
        "--out-path",
        type=Path,
        default=DEFAULT_OUTPUT_PATH,
        help="Output path for the persisted quick gate fact.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print machine-readable summary JSON.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    python_cmd = detect_python_cmd()
    ruff_cmd = detect_python_tool("ruff", python_cmd)
    mypy_cmd = detect_python_tool("mypy", python_cmd)
    datapulse_cli = detect_command("datapulse", python_cmd + ["-m", "datapulse.cli"])
    datapulse_smoke = detect_command("datapulse-smoke", python_cmd + ["-m", "datapulse.tools.smoke"])

    steps: list[dict[str, object]] = []
    steps.append(
        run_step(
            "python_import",
            python_cmd + ["-c", "import datapulse; print(datapulse.__name__)"],
        )
    )
    steps.append(run_step("lint_datapulse", ruff_cmd + ["check", "datapulse/"]))
    steps.append(run_step("typecheck_datapulse", mypy_cmd + ["datapulse/"]))
    steps.append(run_step("console_smoke", ["bash", "scripts/datapulse_console_smoke.sh"]))
    steps.append(run_step("smoke_list", datapulse_smoke + ["--list"]))
    steps.append(run_step("cli_list", datapulse_cli + ["--list", "--limit", "5", "--min-confidence", "0.0"]))

    url_1 = os.environ.get("URL_1", "").strip()
    if url_1:
        steps.append(run_step("single_url", datapulse_cli + [url_1, "--min-confidence", os.environ.get("MIN_CONFIDENCE", "0.0")]))

    url_batch = os.environ.get("URL_BATCH", "").strip()
    if url_batch:
        steps.append(
            run_step(
                "batch_url",
                datapulse_cli + ["--batch", *shell_words(url_batch), "--min-confidence", os.environ.get("MIN_CONFIDENCE", "0.0")],
            )
        )

    ok = all(bool(step["ok"]) for step in steps)
    payload = {
        "schema_version": "quick_test_gate.v1",
        "generated_at_utc": utc_now(),
        "git": {
            "head": git_output("rev-parse", "HEAD"),
            "branch": git_output("branch", "--show-current"),
        },
        "ok": ok,
        "read_only": True,
        "steps": steps,
    }
    if args.out_path:
        payload["path"] = display_path(args.out_path.resolve())
        write_json(args.out_path, payload)
    print(json.dumps(payload, indent=2, ensure_ascii=True))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
