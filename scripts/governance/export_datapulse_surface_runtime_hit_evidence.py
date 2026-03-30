#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import tempfile
from pathlib import Path
from typing import Any

from datapulse.governance_paths import (
    RUNTIME_BUNDLE_ROOT,
    canonical_root as resolve_governance_canonical_root,
    read_root as resolve_governance_read_root,
)
from datapulse_loop_contracts import DEFAULT_OUT_DIR, REPO_ROOT, display_path, utc_now, write_json

from datapulse.core.alerts import AlertEvent
from datapulse.reader import DataPulseReader

DEFAULT_BUNDLE_DIR = resolve_governance_read_root(RUNTIME_BUNDLE_ROOT, repo_root=REPO_ROOT)
CANONICAL_RUNTIME_BUNDLE_DIR = resolve_governance_canonical_root(RUNTIME_BUNDLE_ROOT, repo_root=REPO_ROOT)
DEFAULT_OUTPUT_PATH = DEFAULT_OUT_DIR / "datapulse_surface_runtime_hit_evidence.draft.json"
_SANDBOX_ENV_KEYS = (
    "DATAPULSE_MEMORY_DIR",
    "DATAPULSE_SOURCE_CATALOG",
    "DATAPULSE_STORIES_PATH",
    "DATAPULSE_REPORTS_PATH",
    "DATAPULSE_ALERT_ROUTING_PATH",
    "DATAPULSE_WATCHLIST_PATH",
    "DATAPULSE_MODELBUS_BUNDLE_DIR",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Export current-window runtime-hit evidence for governed DataPulse AI surfaces."
    )
    parser.add_argument(
        "--bundle-dir",
        type=Path,
        default=DEFAULT_BUNDLE_DIR,
        help="ModelBus consumer bundle directory used for the runtime window.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT_PATH,
        help="Output path for the runtime-hit evidence JSON.",
    )
    parser.add_argument(
        "--mode",
        default="review",
        choices=["off", "assist", "review"],
        help="Governed mode used for the runtime-hit window.",
    )
    parser.add_argument(
        "--stdout",
        action="store_true",
        help="Print JSON to stdout instead of writing the default draft file.",
    )
    return parser.parse_args()


def _surface_summary(projection: dict[str, Any]) -> dict[str, Any]:
    precheck = projection.get("precheck")
    precheck = precheck if isinstance(precheck, dict) else {}
    runtime_facts = projection.get("runtime_facts")
    runtime_facts = runtime_facts if isinstance(runtime_facts, dict) else {}
    output = projection.get("output")
    output = output if isinstance(output, dict) else {}

    served_by_alias = str(runtime_facts.get("served_by_alias", "") or precheck.get("alias", "") or "").strip()
    rejectable_gap_ids = [
        str(gap.get("gap_id", "")).strip()
        for gap in precheck.get("rejectable_gaps", [])
        if isinstance(gap, dict) and str(gap.get("gap_id", "")).strip()
    ]
    schema_valid = bool(runtime_facts.get("schema_valid", False))
    output_present = bool(output)
    fail_closed = not output_present and not schema_valid and str(runtime_facts.get("status", "")).strip().lower() in {
        "rejected",
        "invalid",
        "manual_only",
    }
    surface = str(projection.get("surface", "") or "").strip()

    evidence_status = "blocked"
    if surface == "delivery_summary" and output_present and schema_valid and served_by_alias:
        evidence_status = "verified"
    if surface == "report_draft" and fail_closed and served_by_alias and str(runtime_facts.get("request_id", "")).strip():
        evidence_status = "verified_fail_closed"

    return {
        "surface": surface,
        "mode": str(projection.get("mode", "") or "").strip(),
        "subject": dict(projection.get("subject") or {}) if isinstance(projection.get("subject"), dict) else {},
        "admission_source": str(precheck.get("admission_source", "") or "").strip(),
        "bundle_selection": str(precheck.get("bundle_selection", "") or "").strip(),
        "precheck_ok": bool(precheck.get("ok", False)),
        "mode_status": str(precheck.get("mode_status", "") or "").strip(),
        "admission_status": str(precheck.get("admission_status", "") or "").strip(),
        "served_by_alias": served_by_alias,
        "requested_alias": str(precheck.get("requested_alias", "") or "").strip(),
        "request_id": str(runtime_facts.get("request_id", "") or "").strip(),
        "schema_valid": schema_valid,
        "runtime_status": str(runtime_facts.get("status", "") or "").strip(),
        "output_present": output_present,
        "contract_id": str(runtime_facts.get("contract_id", "") or output.get("contract_id", "") or "").strip(),
        "fail_closed": fail_closed,
        "bridge_request_present": isinstance(projection.get("bridge_request"), dict),
        "rejectable_gap_ids": rejectable_gap_ids,
        "errors": [str(item).strip() for item in runtime_facts.get("errors", []) if str(item).strip()],
        "evidence_status": evidence_status,
    }


def build_payload(bundle_dir: Path, *, mode: str) -> dict[str, Any]:
    saved_env = {key: os.environ.get(key) for key in _SANDBOX_ENV_KEYS}
    try:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_root = Path(tmp_dir)
            inbox_path = tmp_root / "inbox.json"
            catalog_path = tmp_root / "catalog.json"
            reports_path = tmp_root / "reports.json"
            routes_path = tmp_root / "routes.json"
            stories_path = tmp_root / "stories.json"
            watchlist_path = tmp_root / "watchlist.json"

            inbox_path.write_text("[]\n", encoding="utf-8")
            catalog_path.write_text('{"version":2,"sources":[],"subscriptions":{},"packs":[]}' + "\n", encoding="utf-8")

            os.environ["DATAPULSE_MEMORY_DIR"] = str(tmp_root)
            os.environ["DATAPULSE_SOURCE_CATALOG"] = str(catalog_path)
            os.environ["DATAPULSE_STORIES_PATH"] = str(stories_path)
            os.environ["DATAPULSE_REPORTS_PATH"] = str(reports_path)
            os.environ["DATAPULSE_ALERT_ROUTING_PATH"] = str(routes_path)
            os.environ["DATAPULSE_WATCHLIST_PATH"] = str(watchlist_path)
            os.environ["DATAPULSE_MODELBUS_BUNDLE_DIR"] = str(bundle_dir.resolve())

            reader = DataPulseReader(inbox_path=str(inbox_path))

            report = reader.create_report(
                title="AI Runtime Closure Report",
                summary="Synthetic report used to prove report_draft fail-closed runtime observability.",
            )
            claim = reader.create_claim_card(
                statement="The runtime-hit closure sample preserves attribution and replay context.",
                brief_id="",
            )
            section = reader.create_report_section(
                report_id=report["id"],
                title="Runtime Closure",
                claim_card_ids=[claim["id"]],
                position=1,
            )
            reader.update_report(
                report["id"],
                section_ids=[section["id"]],
                claim_card_ids=[claim["id"]],
            )

            reader.create_alert_route(
                name="ops-webhook",
                channel="webhook",
                webhook_url="https://example.com/runtime-hit",
            )
            event = AlertEvent(
                mission_id="runtime-closure",
                mission_name="Runtime Closure",
                rule_name="ops-threshold",
                channels=["json"],
                item_ids=["item-1"],
                summary="Runtime Closure triggered ops-threshold",
                delivered_channels=["json", "webhook:ops-webhook"],
                extra={
                    "rule": {
                        "name": "ops-threshold",
                        "routes": ["ops-webhook"],
                        "channels": ["json"],
                    },
                    "delivery_errors": {},
                },
            )
            reader.alert_store.add(event, cooldown_seconds=0)

            delivery_projection = reader.ai_delivery_summary(event.id, mode=mode)
            report_projection = reader.ai_report_draft(report["id"], mode=mode)
            if delivery_projection is None or report_projection is None:
                raise RuntimeError("runtime-hit exporter failed to build synthetic surface projections")

            delivery_summary = _surface_summary(delivery_projection)
            report_summary = _surface_summary(report_projection)
            surfaces = [delivery_summary, report_summary]
            surface_map = {row["surface"]: row for row in surfaces}
            bundle_first_default_ready = all(
                row.get("admission_source") == "modelbus_bundle" for row in surfaces
            )
            shadow_ready = surface_map.get("delivery_summary", {}).get("evidence_status") == "verified" and bundle_first_default_ready
            required_ready = (
                shadow_ready
                and surface_map.get("report_draft", {}).get("evidence_status") == "verified_fail_closed"
            )
            blocking_reasons: list[str] = []
            if not bundle_first_default_ready:
                blocking_reasons.append("bundle_first_default_not_satisfied")
            if surface_map.get("delivery_summary", {}).get("evidence_status") != "verified":
                blocking_reasons.append("delivery_summary_runtime_hit_not_verified")
            if surface_map.get("report_draft", {}).get("evidence_status") != "verified_fail_closed":
                blocking_reasons.append("report_draft_required_runtime_surface_not_verified")

            return {
                "schema_version": "datapulse_surface_runtime_hit_evidence.v1",
                "project": "DataPulse",
                "generated_at_utc": utc_now(),
                "bundle_default": {
                    "strategy": "bundle_first",
                    "canonical_bundle_path": display_path(CANONICAL_RUNTIME_BUNDLE_DIR.resolve()),
                    "runtime_bundle_dir": display_path(bundle_dir.resolve()),
                    "local_snapshot_parallel_primary_disabled": True,
                },
                "surfaces": surfaces,
                "release_level_prerequisites": {
                    "bundle_first_default_ready": bundle_first_default_ready,
                    "shadow_change_prerequisites_met": shadow_ready,
                    "required_change_prerequisites_met": required_ready,
                    "promotion_discussion_allowed": required_ready,
                },
                "closure": {
                    "required_runtime_hit_targets": [
                        {"surface": "delivery_summary", "expected_evidence_status": "verified", "release_scope": "shadow"},
                        {"surface": "report_draft", "expected_evidence_status": "verified_fail_closed", "release_scope": "required"},
                    ],
                    "verified_surfaces": [
                        row["surface"]
                        for row in surfaces
                        if row["evidence_status"] in {"verified", "verified_fail_closed"}
                    ],
                    "blocking_reasons": blocking_reasons,
                    "replay_entrypoint": (
                        f"python3 scripts/governance/export_datapulse_surface_runtime_hit_evidence.py "
                        f"--bundle-dir {display_path(bundle_dir.resolve())}"
                    ),
                },
            }
    finally:
        for key, value in saved_env.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value


def main() -> int:
    args = parse_args()
    payload = build_payload(args.bundle_dir.resolve(), mode=args.mode)
    if args.stdout:
        print(json.dumps(payload, indent=2, ensure_ascii=True))
        return 0
    write_json(args.output.resolve(), payload)
    print(args.output.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
