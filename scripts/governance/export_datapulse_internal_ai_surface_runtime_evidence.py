#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from datapulse.core.alerts import AlertEvent
from datapulse.core.models import DataPulseItem, SourceType
from datapulse.reader import DataPulseReader
from export_datapulse_internal_ai_surface_admission import (
    DEFAULT_BRIDGE_CONFIG_PATH,
    DEFAULT_REGISTRY_PATH,
    DEFAULT_SURFACE_ADMISSION_PATH,
    build_payload as build_internal_admission_payload,
)

DEFAULT_OUTPUT_PATH = REPO_ROOT / "out/governance/datapulse_internal_ai_surface_runtime_evidence.draft.json"
_SANDBOX_ENV_KEYS = (
    "DATAPULSE_MEMORY_DIR",
    "DATAPULSE_SOURCE_CATALOG",
    "DATAPULSE_STORIES_PATH",
    "DATAPULSE_REPORTS_PATH",
    "DATAPULSE_ALERT_ROUTING_PATH",
    "DATAPULSE_WATCHLIST_PATH",
    "DATAPULSE_MODELBUS_BUNDLE_DIR",
)
_ADMITTED_INTERNAL_TARGETS = {"claim_draft", "delivery_summary"}
def utc_now() -> str:
    from datetime import datetime, timezone

    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def display_path(path: Path) -> str:
    resolved = path.resolve()
    if resolved.is_relative_to(REPO_ROOT):
        return str(resolved.relative_to(REPO_ROOT))
    return str(resolved)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Export one internal DataPulse AI runtime evidence bundle for claim_draft or delivery_summary while keeping report_draft fail-closed."
    )
    parser.add_argument(
        "--bundle-dir",
        type=Path,
        default=REPO_ROOT / "config/modelbus/datapulse",
        help="Repo-native ModelBus bundle directory used for the runtime window.",
    )
    parser.add_argument(
        "--registry",
        type=Path,
        default=DEFAULT_REGISTRY_PATH,
        help="Path to datapulse-internal-ai-surface-registry.draft.json.",
    )
    parser.add_argument(
        "--bridge-config",
        type=Path,
        default=DEFAULT_BRIDGE_CONFIG_PATH,
        help="Path to the ModelBus bridge config.",
    )
    parser.add_argument(
        "--surface-admission",
        type=Path,
        default=DEFAULT_SURFACE_ADMISSION_PATH,
        help="Path to the ModelBus surface admission facts.",
    )
    parser.add_argument(
        "--surface",
        choices=sorted(_ADMITTED_INTERNAL_TARGETS),
        default="claim_draft",
        help="The admitted internal surface to close in this first runtime evidence wave.",
    )
    parser.add_argument(
        "--mode",
        default="review",
        choices=["off", "assist", "review"],
        help="Governed mode used for the runtime window.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT_PATH,
        help="Output path for the internal AI surface runtime evidence JSON.",
    )
    parser.add_argument(
        "--stdout",
        action="store_true",
        help="Print JSON to stdout instead of writing the default draft file.",
    )
    return parser.parse_args()


def _synthetic_items() -> list[DataPulseItem]:
    return [
        DataPulseItem(
            source_type=SourceType.GENERIC,
            source_name="internal-runtime",
            title="Internal runtime closure signal",
            content="Internal authoring runtime closure signal for claim or delivery proof.",
            url="https://example.com/internal-runtime/item-1",
            id="item-1",
            confidence=0.94,
        ),
        DataPulseItem(
            source_type=SourceType.GENERIC,
            source_name="internal-runtime",
            title="Internal runtime closure follow-up",
            content="Second evidence row keeps attribution and citation binding available inside the same runtime window.",
            url="https://example.com/internal-runtime/item-2",
            id="item-2",
            confidence=0.83,
        ),
    ]


def _admission_index(payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        str(row.get("surface_id", "")).strip(): dict(row)
        for row in payload.get("surface_admission_rows", [])
        if isinstance(row, dict) and str(row.get("surface_id", "")).strip()
    }


def _blocking_failure_reason(precheck: dict[str, Any], admission_row: dict[str, Any]) -> str:
    failure_reason = str(admission_row.get("failure_reason", "") or "").strip()
    if failure_reason:
        return failure_reason
    for gap in precheck.get("rejectable_gaps", []):
        if not isinstance(gap, dict):
            continue
        if not bool(gap.get("blocking", False)):
            continue
        reason = str(gap.get("reason", "") or "").strip()
        if reason:
            return reason
    return ""


def _surface_summary(projection: dict[str, Any], admission_row: dict[str, Any]) -> dict[str, Any]:
    precheck = dict(projection.get("precheck") or {}) if isinstance(projection.get("precheck"), dict) else {}
    runtime_facts = (
        dict(projection.get("runtime_facts") or {})
        if isinstance(projection.get("runtime_facts"), dict)
        else {}
    )
    output = dict(projection.get("output") or {}) if isinstance(projection.get("output"), dict) else {}
    surface = str(projection.get("surface", "") or "").strip()
    bound_aliases = [
        str(item).strip()
        for item in admission_row.get("bound_aliases", [])
        if str(item).strip()
    ]
    served_by_alias = str(
        runtime_facts.get("served_by_alias", "") or precheck.get("alias", "") or admission_row.get("requested_alias", "")
    ).strip()
    request_id = str(runtime_facts.get("request_id", "") or "").strip()
    rejectable_gap_ids = [
        str(gap.get("gap_id", "")).strip()
        for gap in precheck.get("rejectable_gaps", [])
        if isinstance(gap, dict) and str(gap.get("gap_id", "")).strip()
    ]
    must_expose_runtime_facts = [
        str(item).strip()
        for item in precheck.get("must_expose_runtime_facts", [])
        if str(item).strip()
    ]
    missing_runtime_facts = [
        fact_name for fact_name in must_expose_runtime_facts if fact_name not in runtime_facts
    ]
    schema_valid = bool(runtime_facts.get("schema_valid", False))
    output_present = bool(output)
    runtime_status = str(runtime_facts.get("status", "") or "").strip()
    contract_id = str(
        runtime_facts.get("contract_id", "")
        or output.get("contract_id", "")
        or admission_row.get("schema_contract_id", "")
        or ""
    ).strip()
    fail_closed = bool(admission_row.get("fail_closed", False)) or (
        not output_present and not schema_valid and runtime_status in {"rejected", "invalid", "manual_only"}
    )
    bridge_request_present = isinstance(projection.get("bridge_request"), dict)
    failure_reason = _blocking_failure_reason(precheck, admission_row)
    alias_bound = bool(served_by_alias and served_by_alias in bound_aliases)
    failure_reason_present = bool(failure_reason)

    evidence_status = "blocked"
    if (
        surface in _ADMITTED_INTERNAL_TARGETS
        and bool(precheck.get("ok", False))
        and str(precheck.get("admission_status", "")).strip().lower() == "admitted"
        and output_present
        and schema_valid
        and bool(contract_id)
        and bool(request_id)
        and alias_bound
        and bridge_request_present
        and not missing_runtime_facts
    ):
        evidence_status = "verified"
    if (
        surface == "report_draft"
        and fail_closed
        and str(precheck.get("admission_status", "")).strip().lower() == "rejected"
        and bool(request_id)
        and alias_bound
        and bridge_request_present
        and not missing_runtime_facts
        and failure_reason_present
    ):
        evidence_status = "verified_fail_closed"

    return {
        "surface": surface,
        "mode": str(projection.get("mode", "") or "").strip(),
        "subject": dict(projection.get("subject") or {}) if isinstance(projection.get("subject"), dict) else {},
        "bound_aliases": bound_aliases,
        "bound_tools": [
            str(item).strip()
            for item in admission_row.get("bound_tools", [])
            if str(item).strip()
        ],
        "requested_alias": str(admission_row.get("requested_alias", "") or "").strip(),
        "served_by_alias": served_by_alias,
        "request_id": request_id,
        "runtime_status": runtime_status,
        "bridge_request_present": bridge_request_present,
        "output_present": output_present,
        "schema_valid": schema_valid,
        "contract_id": contract_id,
        "tool_schema_verdict": str(admission_row.get("tool_schema_verdict", "") or "").strip(),
        "tool_policy_verdict": str(admission_row.get("tool_policy_verdict", "") or "").strip(),
        "admission_status": str(admission_row.get("admission_status", "") or "").strip(),
        "fail_closed": fail_closed,
        "failure_reason": failure_reason,
        "failure_reason_present": failure_reason_present,
        "rejectable_gap_ids": rejectable_gap_ids,
        "must_expose_runtime_facts": must_expose_runtime_facts,
        "missing_runtime_facts": missing_runtime_facts,
        "errors": [str(item).strip() for item in runtime_facts.get("errors", []) if str(item).strip()],
        "binding": {
            "request_id_present": bool(request_id),
            "served_alias_bound": alias_bound,
            "failure_reason_bound": failure_reason_present,
        },
        "evidence_status": evidence_status,
    }


def _synthetic_context(reader: DataPulseReader) -> dict[str, Any]:
    mission = reader.create_watch(
        name="Internal Runtime Closure Watch",
        query="datapulse internal runtime closure",
        mission_intent={
            "scope_entities": ["DataPulse", "ModelBus"],
            "scope_topics": ["runtime", "governance"],
            "scope_regions": ["global"],
        },
        sites=["example.com"],
        schedule="@hourly",
    )
    story = reader.create_story(
        title="Internal Runtime Closure Story",
        summary="Synthetic story used to prove claim_draft runtime observability.",
        status="active",
        item_count=2,
        confidence=0.91,
        entities=["DataPulse", "ModelBus"],
        primary_evidence=[
            {
                "item_id": "item-1",
                "title": "Internal runtime closure signal",
                "url": "https://example.com/internal-runtime/item-1",
                "source_name": "internal-runtime",
                "source_type": "generic",
                "review_state": "verified",
            }
        ],
        secondary_evidence=[
            {
                "item_id": "item-2",
                "title": "Internal runtime closure follow-up",
                "url": "https://example.com/internal-runtime/item-2",
                "source_name": "internal-runtime",
                "source_type": "generic",
                "review_state": "triaged",
            }
        ],
        semantic_review={
            "claim_candidates": [
                "Internal authoring surfaces should bind runtime request IDs and aliases inside one proof window.",
                "report_draft stays fail-closed until an admitted contract lands.",
            ]
        },
        contradictions=[],
    )
    brief = reader.create_report_brief(
        title="Internal Runtime Closure Brief",
        audience="operators",
        objective="Validate internal AI authoring runtime evidence.",
        intent="Keep internal authoring evidence repo-native and fail-closed where required.",
        tags=["modelbus", "internal-surface", "runtime-evidence"],
    )
    report = reader.create_report(
        title="Internal Runtime Closure Report",
        summary="Synthetic report used to prove report_draft fail-closed runtime observability.",
        brief_id=brief["id"],
    )
    claim = reader.create_claim_card(
        statement="The internal runtime closure sample preserves alias and request attribution.",
        brief_id=brief["id"],
    )
    citation_bundle = reader.create_citation_bundle(
        label="Internal Runtime Evidence Bundle",
        claim_card_id=claim["id"],
        source_item_ids=["item-1", "item-2"],
        source_urls=[
            "https://example.com/internal-runtime/item-1",
            "https://example.com/internal-runtime/item-2",
        ],
        note="Repo-local evidence bundle for internal runtime closure proof.",
    )
    reader.update_claim_card(claim["id"], citation_bundle_ids=[citation_bundle["id"]])
    section = reader.create_report_section(
        report_id=report["id"],
        title="Internal Runtime Closure",
        claim_card_ids=[claim["id"]],
        position=1,
    )
    reader.update_report(
        report["id"],
        brief_id=brief["id"],
        section_ids=[section["id"]],
        claim_card_ids=[claim["id"]],
        citation_bundle_ids=[citation_bundle["id"]],
    )

    reader.create_alert_route(
        name="ops-webhook",
        channel="webhook",
        webhook_url="https://example.com/internal-runtime",
    )
    event = AlertEvent(
        mission_id="internal-runtime-closure",
        mission_name="Internal Runtime Closure",
        rule_name="ops-threshold",
        channels=["json"],
        item_ids=["item-1"],
        summary="Internal runtime closure triggered ops-threshold",
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
    return {
        "mission": mission,
        "story": story,
        "brief": brief,
        "report": report,
        "event": event,
    }


def build_payload(
    *,
    bundle_dir: Path,
    registry_path: Path,
    bridge_config_path: Path,
    surface_admission_path: Path,
    selected_surface: str,
    mode: str,
) -> dict[str, Any]:
    if selected_surface not in _ADMITTED_INTERNAL_TARGETS:
        raise ValueError(f"unsupported selected surface: {selected_surface}")

    admission_payload = build_internal_admission_payload(
        registry_path.resolve(),
        bridge_config_path.resolve(),
        surface_admission_path.resolve(),
    )
    admission_rows = _admission_index(admission_payload)
    missing_surfaces = [surface for surface in {selected_surface, "report_draft"} if surface not in admission_rows]
    if missing_surfaces:
        raise ValueError(f"missing internal admission rows for: {', '.join(sorted(missing_surfaces))}")

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

            inbox_path.write_text(
                json.dumps([item.to_dict() for item in _synthetic_items()], ensure_ascii=True, indent=2) + "\n",
                encoding="utf-8",
            )
            catalog_path.write_text('{"version":2,"sources":[],"subscriptions":{},"packs":[]}' + "\n", encoding="utf-8")

            os.environ["DATAPULSE_MEMORY_DIR"] = str(tmp_root)
            os.environ["DATAPULSE_SOURCE_CATALOG"] = str(catalog_path)
            os.environ["DATAPULSE_STORIES_PATH"] = str(stories_path)
            os.environ["DATAPULSE_REPORTS_PATH"] = str(reports_path)
            os.environ["DATAPULSE_ALERT_ROUTING_PATH"] = str(routes_path)
            os.environ["DATAPULSE_WATCHLIST_PATH"] = str(watchlist_path)
            os.environ["DATAPULSE_MODELBUS_BUNDLE_DIR"] = str(bundle_dir.resolve())

            reader = DataPulseReader(inbox_path=str(inbox_path))
            context = _synthetic_context(reader)

            projections = {
                "claim_draft": reader.ai_claim_draft(
                    context["story"]["id"],
                    mode=mode,
                    brief_id=context["brief"]["id"],
                ),
                "report_draft": reader.ai_report_draft(context["report"]["id"], mode=mode),
                "delivery_summary": reader.ai_delivery_summary(context["event"].id, mode=mode),
            }
            selected_projection = projections.get(selected_surface)
            report_projection = projections.get("report_draft")
            if selected_projection is None or report_projection is None:
                raise RuntimeError("internal runtime evidence exporter failed to build required surface projections")

            surfaces = [
                _surface_summary(selected_projection, admission_rows[selected_surface]),
                _surface_summary(report_projection, admission_rows["report_draft"]),
            ]
            surface_map = {row["surface"]: row for row in surfaces}
            selected_row = surface_map[selected_surface]
            report_row = surface_map["report_draft"]
            same_window_closed = (
                selected_row["evidence_status"] == "verified"
                and report_row["evidence_status"] == "verified_fail_closed"
                and selected_row["binding"]["request_id_present"]
                and selected_row["binding"]["served_alias_bound"]
                and report_row["binding"]["request_id_present"]
                and report_row["binding"]["served_alias_bound"]
                and report_row["binding"]["failure_reason_bound"]
            )
            blocking_reasons: list[str] = []
            if selected_row["evidence_status"] != "verified":
                blocking_reasons.append(f"{selected_surface}_not_verified")
            if not selected_row["binding"]["request_id_present"]:
                blocking_reasons.append(f"{selected_surface}_request_id_missing")
            if not selected_row["binding"]["served_alias_bound"]:
                blocking_reasons.append(f"{selected_surface}_bound_alias_missing")
            if report_row["evidence_status"] != "verified_fail_closed":
                blocking_reasons.append("report_draft_not_verified_fail_closed")
            if not report_row["binding"]["request_id_present"]:
                blocking_reasons.append("report_draft_request_id_missing")
            if not report_row["binding"]["served_alias_bound"]:
                blocking_reasons.append("report_draft_bound_alias_missing")
            if not report_row["binding"]["failure_reason_bound"]:
                blocking_reasons.append("report_draft_failure_reason_missing")

            return {
                "schema_version": "datapulse_internal_ai_surface_runtime_evidence.v1",
                "project": "DataPulse",
                "generated_at_utc": utc_now(),
                "state_kind": "draft_export",
                "selected_surface": selected_surface,
                "sources": {
                    "internal_ai_surface_registry": display_path(registry_path.resolve()),
                    "bridge_config": display_path(bridge_config_path.resolve()),
                    "surface_admission": display_path(surface_admission_path.resolve()),
                },
                "repo_native_bundle": {
                    "runtime_bundle_dir": display_path(bundle_dir.resolve()),
                    "selection": "explicit_env",
                    "same_window_strategy": "single_export_run",
                },
                "surfaces": surfaces,
                "closure": {
                    "same_window_closed": same_window_closed,
                    "required_surfaces": [
                        {
                            "surface": selected_surface,
                            "expected_evidence_status": "verified",
                        },
                        {
                            "surface": "report_draft",
                            "expected_evidence_status": "verified_fail_closed",
                        },
                    ],
                    "verified_surfaces": [
                        row["surface"]
                        for row in surfaces
                        if row["evidence_status"] in {"verified", "verified_fail_closed"}
                    ],
                    "blocking_reasons": blocking_reasons,
                    "replay_entrypoint": (
                        "python3 scripts/governance/export_datapulse_internal_ai_surface_runtime_evidence.py "
                        f"--bundle-dir {display_path(bundle_dir.resolve())} --surface {selected_surface}"
                    ),
                },
                "summary": {
                    "selected_surface": selected_surface,
                    "request_ids": {
                        row["surface"]: row["request_id"]
                        for row in surfaces
                    },
                    "bound_aliases": {
                        row["surface"]: row["served_by_alias"]
                        for row in surfaces
                    },
                    "fail_closed_surface_ids": [
                        row["surface"]
                        for row in surfaces
                        if row["fail_closed"]
                    ],
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
    payload = build_payload(
        bundle_dir=args.bundle_dir.resolve(),
        registry_path=args.registry.resolve(),
        bridge_config_path=args.bridge_config.resolve(),
        surface_admission_path=args.surface_admission.resolve(),
        selected_surface=args.surface,
        mode=args.mode,
    )
    if args.stdout:
        print(json.dumps(payload, indent=2, ensure_ascii=True))
        return 0
    write_json(args.output.resolve(), payload)
    print(args.output.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
