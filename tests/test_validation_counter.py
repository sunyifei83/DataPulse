"""Tests for the warn→fail admission counter (issue #52, design §11.2)."""
from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from datapulse.core import validation_counter as vc


@pytest.fixture
def counter_path(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    path = tmp_path / "counter.json"
    monkeypatch.setenv(vc.PATH_OVERRIDE_ENV, str(path))
    return path


def test_load_state_returns_zeroed_initial_when_file_missing(counter_path: Path) -> None:
    state = vc.load_state()
    assert state["schema_version"] == vc.SCHEMA_VERSION
    assert state["total_validations"] == 0
    assert state["warn_count"] == 0
    assert state["validations_since_last_warn"] == 0
    assert state["first_validation_utc"] is None
    assert state["last_warn_utc"] is None


def test_record_event_clean_increments_total_and_streak(counter_path: Path) -> None:
    vc.record_event(warned=False)
    vc.record_event(warned=False)
    state = vc.load_state()
    assert state["total_validations"] == 2
    assert state["warn_count"] == 0
    assert state["validations_since_last_warn"] == 2
    assert state["first_validation_utc"] is not None
    assert state["last_validation_utc"] is not None
    assert state["last_warn_utc"] is None


def test_record_event_warn_resets_streak_and_increments_warn_count(counter_path: Path) -> None:
    vc.record_event(warned=False)
    vc.record_event(warned=False)
    vc.record_event(warned=True)
    state = vc.load_state()
    assert state["total_validations"] == 3
    assert state["warn_count"] == 1
    assert state["validations_since_last_warn"] == 0
    assert state["last_warn_utc"] is not None
    # subsequent clean events build a new streak
    vc.record_event(warned=False)
    assert vc.load_state()["validations_since_last_warn"] == 1


def test_load_state_resets_on_schema_version_mismatch(counter_path: Path) -> None:
    counter_path.write_text(json.dumps({"schema_version": 999, "total_validations": 42}))
    state = vc.load_state()
    assert state["total_validations"] == 0
    assert state["schema_version"] == vc.SCHEMA_VERSION


def test_load_state_resets_on_corrupt_json(counter_path: Path) -> None:
    counter_path.write_text("{not json")
    state = vc.load_state()
    assert state["total_validations"] == 0


def test_check_admission_denies_when_no_events_yet(counter_path: Path) -> None:
    granted, reason = vc.check_admission(min_validations=10)
    assert granted is False
    assert "no validations" in reason


def test_check_admission_denies_when_below_threshold_with_zero_warns(counter_path: Path) -> None:
    for _ in range(5):
        vc.record_event(warned=False)
    granted, reason = vc.check_admission(min_validations=10)
    assert granted is False
    assert "have 5" in reason


def test_check_admission_grants_when_min_clean_events_reached_zero_warns(counter_path: Path) -> None:
    for _ in range(10):
        vc.record_event(warned=False)
    granted, reason = vc.check_admission(min_validations=10)
    assert granted is True
    assert "zero warns" in reason


def test_check_admission_grants_when_streak_since_last_warn_reaches_min(counter_path: Path) -> None:
    vc.record_event(warned=True)
    for _ in range(10):
        vc.record_event(warned=False)
    granted, reason = vc.check_admission(min_validations=10)
    assert granted is True
    assert "since last warn" in reason


def test_check_admission_denies_again_when_new_warn_resets_streak(counter_path: Path) -> None:
    for _ in range(10):
        vc.record_event(warned=False)
    vc.record_event(warned=True)
    granted, reason = vc.check_admission(min_validations=10)
    assert granted is False
    assert "have 0" in reason


def test_main_check_returns_exit_zero_when_granted(counter_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    for _ in range(10):
        vc.record_event(warned=False)
    rc = vc.main(["check", "--min-validations", "10"])
    assert rc == 0
    err = capsys.readouterr().err
    assert err.startswith("GRANTED:")


def test_main_check_returns_exit_one_when_pending(counter_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    vc.record_event(warned=False)
    rc = vc.main(["check", "--min-validations", "10"])
    assert rc == 1
    err = capsys.readouterr().err
    assert err.startswith("PENDING:")


def test_main_state_dumps_json_to_stdout(counter_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    vc.record_event(warned=False)
    rc = vc.main(["state"])
    assert rc == 0
    out = capsys.readouterr().out
    parsed = json.loads(out)
    assert parsed["total_validations"] == 1


def test_main_reset_deletes_counter_file(counter_path: Path) -> None:
    vc.record_event(warned=False)
    assert counter_path.exists()
    rc = vc.main(["reset"])
    assert rc == 0
    assert not counter_path.exists()
    # reset on missing file is also a no-op success
    rc = vc.main(["reset"])
    assert rc == 0


def test_default_path_falls_back_to_home_when_env_unset(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv(vc.PATH_OVERRIDE_ENV, raising=False)
    path = vc.default_path()
    assert path.name == "modelbus_validation_counter.json"
    assert path.parent.name == ".datapulse"


def test_record_event_persists_atomically_with_no_temp_leftovers(counter_path: Path) -> None:
    vc.record_event(warned=False)
    vc.record_event(warned=True)
    parent = counter_path.parent
    siblings = [p.name for p in parent.iterdir() if p.name != counter_path.name]
    # No leftover tempfiles from atomic write
    assert all(not s.startswith(counter_path.name + ".") for s in siblings), siblings


def test_reader_record_modelbus_validation_increments_counter(counter_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Integration: the reader's _record_modelbus_validation hook updates the counter."""
    from datapulse.reader import DataPulseReader

    monkeypatch.setenv("INBOX_FILE", str(counter_path.parent / "inbox.json"))
    reader = DataPulseReader()
    bundle_errors: list[str] = []
    reader._record_modelbus_validation(bundle_errors=bundle_errors, validation_errors=[])
    reader._record_modelbus_validation(
        bundle_errors=bundle_errors,
        validation_errors=["[upstream] foo at /bar: missing"],
    )
    state = vc.load_state()
    assert state["total_validations"] == 2
    assert state["warn_count"] == 1
    assert state["validations_since_last_warn"] == 0
