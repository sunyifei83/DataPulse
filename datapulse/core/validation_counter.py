"""ModelBus validation event counter for warn→fail admission gating.

Persists per-event state to a JSON file so a small CLI gate can mechanically
decide when the warn-only default can be flipped to fail-closed (issue #52,
Task 7). See design §11.2 for why this replaces a calendar-based soak.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCHEMA_VERSION = 1
PATH_OVERRIDE_ENV = "DATAPULSE_MODELBUS_VALIDATION_COUNTER_PATH"
DEFAULT_MIN_VALIDATIONS = 10


def default_path() -> Path:
    if override := os.getenv(PATH_OVERRIDE_ENV):
        return Path(override).expanduser()
    return Path.home() / ".datapulse" / "modelbus_validation_counter.json"


def _now_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _initial_state() -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "first_validation_utc": None,
        "last_validation_utc": None,
        "total_validations": 0,
        "warn_count": 0,
        "last_warn_utc": None,
        "validations_since_last_warn": 0,
    }


def load_state(path: Path | None = None) -> dict[str, Any]:
    path = path or default_path()
    if not path.exists():
        return _initial_state()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return _initial_state()
    if not isinstance(data, dict) or data.get("schema_version") != SCHEMA_VERSION:
        return _initial_state()
    merged = _initial_state()
    merged.update({k: data[k] for k in merged if k in data})
    return merged


def _atomic_write(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=path.name + ".", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, sort_keys=True)
            f.write("\n")
        os.replace(tmp, path)
    except Exception:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def record_event(warned: bool, *, path: Path | None = None) -> dict[str, Any]:
    """Record one validation event, persist, return updated state."""
    path = path or default_path()
    state = load_state(path)
    now = _now_utc()
    state["total_validations"] = int(state.get("total_validations", 0)) + 1
    state["last_validation_utc"] = now
    if state["first_validation_utc"] is None:
        state["first_validation_utc"] = now
    if warned:
        state["warn_count"] = int(state.get("warn_count", 0)) + 1
        state["last_warn_utc"] = now
        state["validations_since_last_warn"] = 0
    else:
        state["validations_since_last_warn"] = int(state.get("validations_since_last_warn", 0)) + 1
    _atomic_write(path, state)
    return state


def check_admission(
    min_validations: int = DEFAULT_MIN_VALIDATIONS,
    *,
    path: Path | None = None,
) -> tuple[bool, str]:
    """Return (granted, reason). Granted iff ≥min_validations clean events since last warn."""
    state = load_state(path)
    total = int(state.get("total_validations", 0))
    if total == 0:
        return (False, "no validations recorded yet")
    warns = int(state.get("warn_count", 0))
    streak = int(state.get("validations_since_last_warn", 0))
    if warns == 0:
        if total < min_validations:
            return (False, f"need {min_validations} clean validations, have {total}")
        return (True, f"{total} clean validations, zero warns since instrumentation")
    if streak < min_validations:
        return (
            False,
            f"need {min_validations} clean validations since last warn at {state.get('last_warn_utc')}, have {streak}",
        )
    return (True, f"{streak} clean validations since last warn at {state.get('last_warn_utc')}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="datapulse.core.validation_counter")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_check = sub.add_parser("check", help="exit 0 if warn→fail admission granted, 1 if pending")
    p_check.add_argument("--min-validations", type=int, default=DEFAULT_MIN_VALIDATIONS)
    p_check.add_argument("--path", type=Path, default=None)

    p_state = sub.add_parser("state", help="dump counter state as JSON to stdout")
    p_state.add_argument("--path", type=Path, default=None)

    p_reset = sub.add_parser("reset", help="delete counter file (no-op if absent)")
    p_reset.add_argument("--path", type=Path, default=None)

    args = parser.parse_args(argv)

    if args.cmd == "check":
        granted, reason = check_admission(args.min_validations, path=args.path)
        sys.stderr.write(f"{'GRANTED' if granted else 'PENDING'}: {reason}\n")
        return 0 if granted else 1
    if args.cmd == "state":
        sys.stdout.write(json.dumps(load_state(args.path), indent=2, sort_keys=True))
        sys.stdout.write("\n")
        return 0
    if args.cmd == "reset":
        target = args.path or default_path()
        try:
            target.unlink()
        except FileNotFoundError:
            pass
        return 0
    return 2


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
