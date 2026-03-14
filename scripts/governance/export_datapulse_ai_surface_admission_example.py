#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SUBSCRIPTIONS_PATH = REPO_ROOT / "docs/governance/datapulse-ai-surface-subscriptions.example.json"
DEFAULT_OUTPUT_PATH = REPO_ROOT / "out/governance/datapulse-ai-surface-admission.example.json"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def display_path(path: Path) -> str:
    resolved = path.resolve()
    if resolved.is_relative_to(REPO_ROOT):
        return str(resolved.relative_to(REPO_ROOT))
    return str(resolved)


def evaluate_candidate(
    candidate: dict[str, Any],
    required_capabilities: set[str],
    required_schema_contract: str,
) -> tuple[bool, dict[str, Any]]:
    capabilities = {
        str(item).strip()
        for item in candidate.get("capabilities", [])
        if str(item).strip()
    }
    output_contracts = {
        str(item).strip()
        for item in candidate.get("output_contracts", [])
        if str(item).strip()
    }
    provider_assumptions = [
        str(item).strip()
        for item in candidate.get("provider_assumptions", [])
        if str(item).strip()
    ]
    missing_capabilities = sorted(required_capabilities - capabilities)
    missing_contracts: list[str] = []
    if not required_schema_contract:
        missing_contracts.append("surface_required_schema_contract")
    elif required_schema_contract not in output_contracts:
        missing_contracts.append(required_schema_contract)

    eligible = not missing_capabilities and not missing_contracts and not provider_assumptions
    return eligible, {
        "subscription_id": str(candidate.get("subscription_id", "")).strip(),
        "alias": str(candidate.get("alias", "")).strip(),
        "selection_rank": int(candidate.get("selection_rank", 0) or 0),
        "status": "eligible" if eligible else "rejected",
        "missing_capabilities": missing_capabilities,
        "missing_contracts": missing_contracts,
        "provider_assumptions": provider_assumptions,
        "degraded_result_allowed": bool(candidate.get("degraded_result_allowed", False)),
    }


def build_surface_admission(surface_payload: dict[str, Any]) -> dict[str, Any]:
    required_capabilities = {
        str(item).strip()
        for item in surface_payload.get("required_capabilities", [])
        if str(item).strip()
    }
    required_schema_contract = str(surface_payload.get("required_schema_contract", "")).strip()
    candidates = list(surface_payload.get("candidate_subscriptions", []))
    results: list[dict[str, Any]] = []
    eligible_results: list[dict[str, Any]] = []

    for candidate in candidates:
        eligible, result = evaluate_candidate(candidate, required_capabilities, required_schema_contract)
        results.append(result)
        if eligible:
            eligible_results.append(result)

    eligible_results.sort(key=lambda item: (item.get("selection_rank", 0), item.get("subscription_id", "")))
    admitted = eligible_results[0] if eligible_results else None

    candidate_results: list[dict[str, Any]] = []
    for result in sorted(results, key=lambda item: (item.get("selection_rank", 0), item.get("subscription_id", ""))):
        candidate_result = dict(result)
        if admitted and candidate_result["subscription_id"] == admitted["subscription_id"]:
            candidate_result["status"] = "admitted"
        elif candidate_result["status"] == "eligible":
            candidate_result["status"] = "eligible_standby"
        candidate_results.append(candidate_result)

    known_gaps = [
        {
            "gap_id": str(item.get("gap_id", "")).strip(),
            "blocking": bool(item.get("blocking", False)),
            "reason": str(item.get("reason", "")).strip(),
        }
        for item in surface_payload.get("known_gaps", [])
        if str(item.get("gap_id", "")).strip()
    ]

    if not required_schema_contract:
        known_gaps.append(
            {
                "gap_id": "missing_required_schema_contract",
                "blocking": True,
                "reason": "The surface does not yet declare an admitted structured payload contract.",
            }
        )

    if not admitted:
        for result in candidate_results:
            if result["missing_capabilities"]:
                known_gaps.append(
                    {
                        "gap_id": f"{result['subscription_id']}:missing_capabilities",
                        "blocking": True,
                        "reason": "Candidate subscription is missing one or more required capabilities.",
                    }
                )
            if result["missing_contracts"]:
                known_gaps.append(
                    {
                        "gap_id": f"{result['subscription_id']}:missing_contract_binding",
                        "blocking": True,
                        "reason": "Candidate subscription does not satisfy the required structured contract binding.",
                    }
                )
            if result["provider_assumptions"]:
                known_gaps.append(
                    {
                        "gap_id": f"{result['subscription_id']}:provider_assumptions_present",
                        "blocking": True,
                        "reason": "Candidate subscription depends on provider-local assumptions.",
                    }
                )

    deduped_gaps: list[dict[str, Any]] = []
    seen_gap_ids: set[str] = set()
    for gap in known_gaps:
        gap_id = gap["gap_id"]
        if gap_id in seen_gap_ids:
            continue
        seen_gap_ids.add(gap_id)
        deduped_gaps.append(gap)

    admission_status = "admitted" if admitted else "rejected"
    return {
        "surface": str(surface_payload.get("surface", "")).strip(),
        "lifecycle_anchor": str(surface_payload.get("lifecycle_anchor", "")).strip(),
        "required_output_kind": str(surface_payload.get("required_output_kind", "")).strip(),
        "required_schema_contract": required_schema_contract,
        "admission_status": admission_status,
        "mode_admission": {
            "off": "manual_only",
            "assist": "admitted" if admitted else "rejected",
            "review": "admitted" if admitted else "rejected",
        },
        "admitted_subscription_id": admitted["subscription_id"] if admitted else "",
        "admitted_alias": admitted["alias"] if admitted else "",
        "admitted_capabilities": sorted(required_capabilities) if admitted else [],
        "must_expose_runtime_facts": list(surface_payload.get("must_expose_runtime_facts", [])),
        "candidate_results": candidate_results,
        "rejectable_gaps": deduped_gaps,
        "manual_fallback": (
            "manual_or_deterministic_behavior"
            if not admitted
            else "manual_review_of_ai_payload_before_final_state_change"
        ),
    }


def build_payload(subscriptions: dict[str, Any], source_path: Path) -> dict[str, Any]:
    surfaces = list(subscriptions.get("surfaces", []))
    return {
        "schema_version": "datapulse_ai_surface_admission.v1",
        "generated_at_utc": utc_now(),
        "governance_phase": str(subscriptions.get("governance_phase", "")).strip() or "L16.5",
        "source_subscription_contract": display_path(source_path),
        "surface_admissions": [build_surface_admission(surface) for surface in surfaces],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Export DataPulse AI surface admission facts from the candidate subscription contract."
    )
    parser.add_argument(
        "--subscriptions",
        type=Path,
        default=DEFAULT_SUBSCRIPTIONS_PATH,
        help="Candidate subscription contract path.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT_PATH,
        help="Output path for the admission fact example.",
    )
    parser.add_argument(
        "--stdout",
        action="store_true",
        help="Print JSON to stdout instead of writing the output file.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    subscriptions = read_json(args.subscriptions)
    payload = build_payload(subscriptions, args.subscriptions)
    if args.stdout:
        print(json.dumps(payload, indent=2, ensure_ascii=True))
        return 0
    write_json(args.output, payload)
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
