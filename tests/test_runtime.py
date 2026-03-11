from __future__ import annotations

import pytest

from datapulse._runtime import build_python_version_error, ensure_supported_python


def test_build_python_version_error_mentions_minimum_and_uv() -> None:
    message = build_python_version_error((3, 9, 6), executable="/usr/bin/python3")

    assert "Python 3.10+" in message
    assert "3.9.6" in message
    assert "/usr/bin/python3" in message
    assert "`uv run ...`" in message


def test_ensure_supported_python_rejects_older_runtime() -> None:
    with pytest.raises(RuntimeError, match=r"requires Python 3\.10\+"):
        ensure_supported_python((3, 9, 6), executable="/usr/bin/python3")


def test_ensure_supported_python_accepts_supported_runtime() -> None:
    ensure_supported_python((3, 10, 0), executable="/usr/bin/python3.10")
