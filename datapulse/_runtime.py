"""Runtime guards for supported Python versions."""

from __future__ import annotations

import sys
from typing import Sequence

MIN_PYTHON = (3, 10)


def _coerce_version_info(version_info: Sequence[int] | None = None) -> tuple[int, ...]:
    raw = version_info if version_info is not None else sys.version_info
    return tuple(int(part) for part in raw[:3])


def build_python_version_error(
    version_info: Sequence[int] | None = None,
    *,
    executable: str | None = None,
) -> str:
    actual = _coerce_version_info(version_info)
    actual_text = ".".join(str(part) for part in actual if part is not None)
    executable_text = executable or sys.executable or "python3"
    return (
        f"DataPulse requires Python {MIN_PYTHON[0]}.{MIN_PYTHON[1]}+; "
        f"found Python {actual_text} via {executable_text}. "
        "Use `uv run ...` or a python3.10+ interpreter."
    )


def ensure_supported_python(
    version_info: Sequence[int] | None = None,
    *,
    executable: str | None = None,
) -> None:
    actual = _coerce_version_info(version_info)
    if actual[:2] < MIN_PYTHON:
        raise RuntimeError(build_python_version_error(actual, executable=executable))
