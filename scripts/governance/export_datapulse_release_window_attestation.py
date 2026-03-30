#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from datapulse_loop_contracts import (
    DEFAULT_OUT_DIR,
    REPO_ROOT,
    display_path,
    git_output,
    read_json,
    utc_now,
    write_json,
)

from datapulse.governance_paths import EVIDENCE_BUNDLE_ROOT
from datapulse.governance_paths import read_root as resolve_governance_read_root

DEFAULT_BUNDLE_DIR = resolve_governance_read_root(EVIDENCE_BUNDLE_ROOT, repo_root=REPO_ROOT)
DEFAULT_OUTPUT_PATH = DEFAULT_OUT_DIR / "datapulse_release_window_attestation.draft.json"
DEFAULT_RUNTIME_HIT_PATH = DEFAULT_OUT_DIR / "datapulse_surface_runtime_hit_evidence.draft.json"
DEFAULT_RELEASE_SIDECAR_PATH = DEFAULT_OUT_DIR / "release_sidecar.draft.json"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Export a fail-closed DataPulse release-window attestation by binding existing bundle, runtime-hit, sidecar, and replay facts."
    )
    parser.add_argument(
        "--bundle-dir",
        type=Path,
        default=DEFAULT_BUNDLE_DIR,
        help="Canonical structured bundle directory to attest.",
    )
    parser.add_argument(
        "--runtime-hit-json",
        type=Path,
        default=DEFAULT_RUNTIME_HIT_PATH,
        help="Existing runtime-hit evidence JSON to bind.",
    )
    parser.add_argument(
        "--release-sidecar-json",
        type=Path,
        default=DEFAULT_RELEASE_SIDECAR_PATH,
        help="Existing release sidecar JSON to bind.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT_PATH,
        help="Primary output path for the attestation JSON.",
    )
    parser.add_argument(
        "--max-source-age-seconds",
        type=int,
        default=900,
        help="Fail-closed freshness limit for each bound source.",
    )
    parser.add_argument(
        "--max-inter-source-skew-seconds",
        type=int,
        default=300,
        help="Fail-closed skew limit across bound source timestamps.",
    )
    parser.add_argument(
        "--stdout",
        action="store_true",
        help="Print JSON to stdout instead of writing files.",
    )
    return parser.parse_args()


def parse_utc(raw_value: str) -> datetime | None:
    value = str(raw_value or "").strip()
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)
    except ValueError:
        return None


def compact_utc(value: datetime) -> str:
    return value.astimezone(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def dedupe(items: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for item in items:
        text = str(item or "").strip()
        if not text or text in seen:
            continue
        seen.add(text)
        result.append(text)
    return result


def load_optional_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    payload = read_json(path)
    return payload if isinstance(payload, dict) else {}


def _string(value: Any) -> str:
    return str(value).strip() if value is not None else ""


def normalize_repo_path(raw_value: Any) -> str:
    value = _string(raw_value)
    if not value:
        return ""
    path = Path(value).expanduser()
    if not path.is_absolute():
        path = (REPO_ROOT / path).resolve()
    else:
        path = path.resolve()
    return display_path(path)


def build_runtime_section(runtime_hit_payload: dict[str, Any], runtime_hit_path: Path) -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    bundle_default = dict(runtime_hit_payload.get("bundle_default", {})) if isinstance(runtime_hit_payload.get("bundle_default"), dict) else {}
    closure = dict(runtime_hit_payload.get("closure", {})) if isinstance(runtime_hit_payload.get("closure"), dict) else {}
    target_rows = {
        _string(item.get("surface")): dict(item)
        for item in runtime_hit_payload.get("closure", {}).get("required_runtime_hit_targets", [])
        if isinstance(item, dict) and _string(item.get("surface"))
    } if isinstance(runtime_hit_payload.get("closure"), dict) else {}

    surface_rows = {
        _string(item.get("surface")): dict(item)
        for item in runtime_hit_payload.get("surfaces", [])
        if isinstance(item, dict) and _string(item.get("surface"))
    }

    ordered_surfaces: list[dict[str, Any]] = []
    for surface_name in ["delivery_summary", "report_draft"]:
        row = surface_rows.get(surface_name, {})
        target = target_rows.get(surface_name, {})
        observed = _string(row.get("evidence_status"))
        expected = _string(target.get("expected_evidence_status"))
        ordered_surfaces.append(
            {
                "surface": surface_name,
                "expected_evidence_status": expected,
                "observed_evidence_status": observed,
                "release_scope": _string(target.get("release_scope")),
                "request_id": _string(row.get("request_id")),
                "served_by_alias": _string(row.get("served_by_alias")),
                "contract_id": _string(row.get("contract_id")),
                "fail_closed": bool(row.get("fail_closed", False)),
                "satisfied": bool(expected and observed == expected),
            }
        )

    return (
        {
            "path": display_path(runtime_hit_path.resolve()),
            "schema_version": _string(runtime_hit_payload.get("schema_version")),
            "generated_at_utc": _string(runtime_hit_payload.get("generated_at_utc")),
            "bundle_default_strategy": _string(bundle_default.get("strategy")),
            "runtime_bundle_dir": normalize_repo_path(bundle_default.get("runtime_bundle_dir")),
            "closure_replay_entrypoint": _string(closure.get("replay_entrypoint")),
            "release_level_prerequisites": dict(runtime_hit_payload.get("release_level_prerequisites", {}))
            if isinstance(runtime_hit_payload.get("release_level_prerequisites"), dict)
            else {},
            "required_surfaces": ordered_surfaces,
        },
        surface_rows,
    )


def build_release_sidecar_truth(sidecar_payload: dict[str, Any], sidecar_path: Path) -> dict[str, Any]:
    release = dict(sidecar_payload.get("release", {})) if isinstance(sidecar_payload.get("release"), dict) else {}
    git_payload = dict(sidecar_payload.get("git", {})) if isinstance(sidecar_payload.get("git"), dict) else {}
    readiness = (
        dict(sidecar_payload.get("governed_ai_release_readiness", {}))
        if isinstance(sidecar_payload.get("governed_ai_release_readiness"), dict)
        else {}
    )
    promotion = (
        dict(sidecar_payload.get("promotion_readiness", {}))
        if isinstance(sidecar_payload.get("promotion_readiness"), dict)
        else {}
    )
    return {
        "path": display_path(sidecar_path.resolve()),
        "schema_version": _string(sidecar_payload.get("schema_version")),
        "generated_at_utc": _string(sidecar_payload.get("generated_at_utc")),
        "release_tag": _string(release.get("tag")),
        "git_head": _string(git_payload.get("head")),
        "workspace_clean": bool(git_payload.get("workspace_clean", False)),
        "structured_release_bundle_available": bool(promotion.get("structured_release_bundle_available", False)),
        "runtime_hit_evidence_available": bool(readiness.get("runtime_hit_evidence_available", False)),
        "required_change_prerequisites_met": bool(readiness.get("required_change_prerequisites_met", False)),
        "promotion_discussion_allowed": bool(readiness.get("promotion_discussion_allowed", False)),
        "promotion_readiness_reasons": [
            _string(item)
            for item in promotion.get("reasons", [])
            if _string(item)
        ],
    }


def bundle_runtime_source(structured_manifest: dict[str, Any], *, bundle_dir: Path) -> tuple[str, list[str]]:
    runtime_bundle = (
        dict(structured_manifest.get("runtime_bundle", {}))
        if isinstance(structured_manifest.get("runtime_bundle"), dict)
        else {}
    )
    source_dir = _string(runtime_bundle.get("source_dir")) or display_path(bundle_dir.resolve())
    copied_files = (
        [_string(item) for item in runtime_bundle.get("files_copied", []) if _string(item)]
        if isinstance(runtime_bundle.get("files_copied"), list)
        else []
    )
    return source_dir, copied_files


def build_freshness(
    attestation_time: datetime,
    source_entries: list[tuple[str, Path, str]],
    *,
    max_source_age_seconds: int,
    max_inter_source_skew_seconds: int,
) -> tuple[dict[str, Any], list[str], list[datetime]]:
    rows: list[dict[str, Any]] = []
    blockers: list[str] = []
    parsed_times: list[datetime] = []

    for source_name, path, generated_at_utc in source_entries:
        source_time = parse_utc(generated_at_utc)
        if source_time is None:
            rows.append(
                {
                    "source": source_name,
                    "path": display_path(path.resolve()),
                    "generated_at_utc": _string(generated_at_utc),
                    "age_seconds": -1,
                    "fresh": False,
                }
            )
            blockers.append("source_timestamp_missing")
            continue

        parsed_times.append(source_time)
        age_seconds = int((attestation_time - source_time).total_seconds())
        fresh = True
        if source_time > attestation_time:
            blockers.append("source_timestamp_in_future")
            fresh = False
        elif age_seconds > max_source_age_seconds:
            blockers.append("source_stale")
            fresh = False

        rows.append(
            {
                "source": source_name,
                "path": display_path(path.resolve()),
                "generated_at_utc": _string(generated_at_utc),
                "age_seconds": age_seconds,
                "fresh": fresh,
            }
        )

    max_skew = 0
    if len(parsed_times) >= 2:
        max_skew = int((max(parsed_times) - min(parsed_times)).total_seconds())
        if max_skew > max_inter_source_skew_seconds:
            blockers.append("source_time_skew_exceeded")

    all_sources_fresh = all(bool(row.get("fresh", False)) for row in rows) and "source_time_skew_exceeded" not in blockers
    return (
        {
            "max_source_age_seconds": max_source_age_seconds,
            "max_inter_source_skew_seconds": max_inter_source_skew_seconds,
            "all_sources_fresh": all_sources_fresh,
            "max_observed_skew_seconds": max_skew,
            "sources": rows,
        },
        dedupe(blockers),
        parsed_times,
    )


def main() -> int:
    args = parse_args()
    bundle_dir = args.bundle_dir.resolve()
    output_path = args.output.resolve()
    bundle_output_path = (bundle_dir / output_path.name).resolve()
    runtime_hit_path = args.runtime_hit_json.resolve()
    release_sidecar_path = args.release_sidecar_json.resolve()

    structured_manifest_path = bundle_dir / "structured_release_bundle_manifest.draft.json"
    bundle_manifest_path = bundle_dir / "bundle_manifest.json"
    adapter_manifest_path = bundle_dir / "adapter_bundle_manifest.draft.json"

    structured_manifest = load_optional_json(structured_manifest_path)
    bundle_manifest = load_optional_json(bundle_manifest_path)
    runtime_hit_payload = load_optional_json(runtime_hit_path)
    release_sidecar_payload = load_optional_json(release_sidecar_path)

    runtime_hit_evidence, runtime_surface_rows = build_runtime_section(runtime_hit_payload, runtime_hit_path)
    release_sidecar_truth = build_release_sidecar_truth(release_sidecar_payload, release_sidecar_path)
    runtime_bundle_source_dir, runtime_bundle_files = bundle_runtime_source(structured_manifest, bundle_dir=bundle_dir)
    normalized_runtime_bundle_source_dir = normalize_repo_path(runtime_bundle_source_dir)
    bundle_identity = {
        "bundle_dir": display_path(bundle_dir),
        "evidence_bundle_dir": display_path(bundle_dir),
        "structured_manifest_path": display_path(structured_manifest_path.resolve()),
        "structured_manifest_generated_at_utc": _string(structured_manifest.get("generated_at_utc")),
        "adapter_bundle_manifest_path": display_path(adapter_manifest_path.resolve()),
        "bundle_manifest_path": display_path(bundle_manifest_path.resolve()),
        "bundle_id": _string(bundle_manifest.get("bundle_id")),
        "consumer_id": _string(bundle_manifest.get("consumer_id")),
        "runtime_bundle_source_dir": normalized_runtime_bundle_source_dir,
        "runtime_bundle_files": runtime_bundle_files,
        "bundle_files": list(structured_manifest.get("files", [])) if isinstance(structured_manifest.get("files"), list) else [],
    }

    primary_bundle_replay_entrypoint = (
        "python3 scripts/governance/validate_governance_loop_bundle_draft.py "
        f"--bundle-dir {display_path(bundle_dir)}"
    )
    runtime_hit_replay_entrypoint = _string(runtime_hit_evidence.get("closure_replay_entrypoint"))
    replay_binding = {
        "primary_bundle_replay": {
            "kind": "generic_core_bundle_replay",
            "entrypoint": primary_bundle_replay_entrypoint,
            "bundle_dir": display_path(bundle_dir),
            "expected_result": "valid=true",
        },
        "runtime_hit_replay": {
            "kind": "runtime_hit_export",
            "entrypoint": runtime_hit_replay_entrypoint,
            "bundle_dir": _string(runtime_hit_evidence.get("runtime_bundle_dir")) or display_path(bundle_dir),
            "expected_result": "delivery_summary=verified and report_draft=verified_fail_closed",
        },
        "ha_recovery_replay": {
            "kind": "manual_remote_smoke_replay",
            "entrypoint": "python3 scripts/governance/run_datapulse_ha_recovery_replay.py --json",
            "manual_execute_entrypoint": "python3 scripts/governance/run_datapulse_ha_recovery_replay.py --execute --json",
            "expected_result": "manual replay stays attributable to the same declared window unless recovery requires a new RUN_ID",
        },
    }

    attestation_generated_at = utc_now()
    attestation_time = parse_utc(attestation_generated_at)
    if attestation_time is None:
        raise RuntimeError("attestation timestamp generation failed")

    freshness, freshness_blockers, parsed_source_times = build_freshness(
        attestation_time,
        [
            ("structured_release_bundle_manifest", structured_manifest_path, bundle_identity["structured_manifest_generated_at_utc"]),
            ("runtime_hit_evidence", runtime_hit_path, _string(runtime_hit_payload.get("generated_at_utc"))),
            ("release_sidecar", release_sidecar_path, _string(release_sidecar_payload.get("generated_at_utc"))),
        ],
        max_source_age_seconds=args.max_source_age_seconds,
        max_inter_source_skew_seconds=args.max_inter_source_skew_seconds,
    )

    git_head = _string(release_sidecar_truth.get("git_head")) or git_output("rev-parse", "HEAD")
    window_anchor = max(parsed_source_times) if parsed_source_times else attestation_time
    window_id = f"dp-release-window-{compact_utc(window_anchor)}-{git_head or 'unknown-head'}"

    blocking_reasons: list[str] = []
    if not structured_manifest or not bundle_manifest:
        blocking_reasons.append("missing_bundle_manifest")
    if not runtime_hit_payload:
        blocking_reasons.append("missing_runtime_hit_evidence")
    if not release_sidecar_payload:
        blocking_reasons.append("missing_release_sidecar")
    if not (REPO_ROOT / "scripts/governance/validate_governance_loop_bundle_draft.py").exists():
        blocking_reasons.append("missing_primary_bundle_replay")
    if not runtime_hit_replay_entrypoint or not (REPO_ROOT / "scripts/governance/export_datapulse_surface_runtime_hit_evidence.py").exists():
        blocking_reasons.append("missing_runtime_hit_replay")

    runtime_bundle_dir = normalize_repo_path(runtime_hit_evidence.get("runtime_bundle_dir"))
    expected_runtime_bundle_dir = _string(bundle_identity.get("runtime_bundle_source_dir")) or bundle_identity["bundle_dir"]
    if runtime_bundle_dir and expected_runtime_bundle_dir and runtime_bundle_dir != expected_runtime_bundle_dir:
        blocking_reasons.append("bundle_runtime_dir_mismatch")
    if _string(release_sidecar_truth.get("git_head")) and git_head and _string(release_sidecar_truth.get("git_head")) != git_head:
        blocking_reasons.append("git_head_mismatch")

    delivery_row = runtime_surface_rows.get("delivery_summary", {})
    report_row = runtime_surface_rows.get("report_draft", {})
    if _string(delivery_row.get("evidence_status")) != "verified":
        blocking_reasons.append("delivery_summary_not_verified")
    if _string(report_row.get("evidence_status")) != "verified_fail_closed":
        blocking_reasons.append("report_draft_not_verified_fail_closed")

    bundle_files = [str(item).strip() for item in bundle_identity.get("bundle_files", []) if str(item).strip()]
    if Path(runtime_hit_evidence["path"]).name not in bundle_files:
        blocking_reasons.append("runtime_hit_evidence_not_in_bundle_files")
    if Path(release_sidecar_truth["path"]).name not in bundle_files:
        blocking_reasons.append("release_sidecar_not_in_bundle_files")

    if not bool(release_sidecar_truth.get("structured_release_bundle_available", False)):
        blocking_reasons.append("structured_release_bundle_not_available")
    if not bool(release_sidecar_truth.get("runtime_hit_evidence_available", False)):
        blocking_reasons.append("missing_runtime_hit_evidence")
    if not bool(release_sidecar_truth.get("required_change_prerequisites_met", False)):
        blocking_reasons.append("required_runtime_prerequisites_not_met")
    if release_sidecar_truth.get("promotion_readiness_reasons"):
        blocking_reasons.extend(str(item) for item in release_sidecar_truth["promotion_readiness_reasons"])

    blocking_reasons.extend(freshness_blockers)
    blocking_reasons = dedupe(blocking_reasons)
    attestation_status = "attested" if not blocking_reasons else "blocked"

    payload = {
        "schema_version": "datapulse_release_window_attestation.v1",
        "project": "DataPulse",
        "generated_at_utc": attestation_generated_at,
        "window_id": window_id,
        "git_head": git_head,
        "attestation_status": attestation_status,
        "blocking_reasons": blocking_reasons,
        "same_window": {
            "required": True,
            "same_head_required": True,
            "same_bundle_dir_required": False,
            "same_runtime_bundle_required": True,
            "proven": attestation_status == "attested" and bool(freshness.get("all_sources_fresh", False)),
            "reasons": [] if attestation_status == "attested" else blocking_reasons,
        },
        "freshness": freshness,
        "bundle_identity": bundle_identity,
        "runtime_hit_evidence": runtime_hit_evidence,
        "release_sidecar_truth": release_sidecar_truth,
        "replay_binding": replay_binding,
    }

    if args.stdout:
        print(json.dumps(payload, indent=2, ensure_ascii=True))
        return 0

    write_json(output_path, payload)
    if bundle_dir.exists() and bundle_dir.is_dir() and bundle_output_path != output_path:
        write_json(bundle_output_path, payload)
    print(output_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
