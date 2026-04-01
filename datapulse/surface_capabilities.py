"""Shared surface capability projections for DataPulse wrappers."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parent.parent
_CATALOG_PATH = _REPO_ROOT / "docs" / "governance" / "datapulse-surface-capability-catalog.draft.json"
_DEFAULT_SURFACES = ("cli", "mcp", "console", "agent", "skill")
_SUPPORTED_AVAILABILITY = {"available", "documented", "unavailable"}
_BLUEPRINT_REOPEN_RULES = {
    "schema_version": "datapulse_runtime_reopen_rules.v1",
    "wave_id": "L27",
    "slice_id": "L27.5",
    "admissible_evidence": [
        {
            "id": "layer_map_contradiction",
            "description": "Repo evidence shows the frozen runtime layer map is contradicted by the landed code or docs.",
        },
        {
            "id": "reader_seam_cannot_hold",
            "description": "Repo evidence shows a required capability cannot stay behind DataPulseReader without breaking the frozen seam contract.",
        },
        {
            "id": "parity_requires_wrapper_truth",
            "description": "Repo evidence shows surface parity cannot be expressed without inventing wrapper-owned business truth outside the Reader-backed runtime.",
        },
    ],
    "inadmissible_reasons": [
        {
            "id": "collector_count_growth",
            "description": "Collector-count growth alone does not reopen the runtime boundary wave.",
        },
        {
            "id": "standalone_frontend_preference",
            "description": "Standalone frontend preference alone does not reopen the runtime boundary wave.",
        },
        {
            "id": "provider_specific_ai_convenience",
            "description": "Provider-specific AI convenience alone does not reopen the runtime boundary wave.",
        },
    ],
}


def surface_capability_catalog_path() -> Path:
    return _CATALOG_PATH


@lru_cache(maxsize=1)
def load_surface_capability_catalog() -> dict[str, Any]:
    with _CATALOG_PATH.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def supported_surface_ids() -> tuple[str, ...]:
    payload = load_surface_capability_catalog()
    surfaces = payload.get("surfaces")
    if not isinstance(surfaces, list):
        return _DEFAULT_SURFACES
    normalized: list[str] = []
    for row in surfaces:
        if not isinstance(row, dict):
            continue
        surface_id = str(row.get("id", "") or "").strip().lower()
        if surface_id:
            normalized.append(surface_id)
    return tuple(normalized) or _DEFAULT_SURFACES


def governed_ai_surface_ids() -> tuple[str, ...]:
    payload = load_surface_capability_catalog()
    rows = payload.get("capabilities")
    if not isinstance(rows, list):
        return ()
    surface_ids: list[str] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        surface_id = str(row.get("governed_ai_surface_id", "") or "").strip()
        if surface_id:
            surface_ids.append(surface_id)
    return tuple(surface_ids)


def runtime_reopen_rules() -> dict[str, Any]:
    return json.loads(json.dumps(_BLUEPRINT_REOPEN_RULES))


def build_surface_capability_projection(
    surface: str,
    *,
    catalog: dict[str, Any] | None = None,
    include_unavailable: bool = False,
) -> dict[str, Any]:
    payload = catalog if catalog is not None else load_surface_capability_catalog()
    surface_id = _normalize_surface_id(surface)
    surface_meta = _surface_meta(surface_id, payload)
    capability_rows = payload.get("capabilities")
    projected: list[dict[str, Any]] = []

    if isinstance(capability_rows, list):
        for capability in capability_rows:
            if not isinstance(capability, dict):
                continue
            surface_entry = capability.get("surfaces", {})
            if not isinstance(surface_entry, dict):
                surface_entry = {}
            projection = surface_entry.get(surface_id, {})
            if not isinstance(projection, dict):
                projection = {}
            availability = _normalize_availability(projection.get("availability"))
            if availability == "unavailable" and not include_unavailable:
                continue
            verification = capability.get("verification", {})
            if not isinstance(verification, dict):
                verification = {}
            projected.append(
                {
                    "id": str(capability.get("id", "") or "").strip(),
                    "title": str(capability.get("title", "") or "").strip(),
                    "category": str(capability.get("category", "") or "").strip(),
                    "owner_seam": str(capability.get("owner_seam", "") or "").strip(),
                    "availability": availability,
                    "entrypoints": _normalize_string_list(projection.get("entrypoints")),
                    "notes": _normalize_string_list(projection.get("notes")),
                    "guardrails": capability.get("guardrails", []),
                    "expected_verification": {
                        "shared": verification.get("shared", []),
                        "surface": verification.get(surface_id, []),
                    },
                }
            )

    return {
        "schema_version": "datapulse_surface_projection.v1",
        "catalog_id": str(payload.get("catalog_id", "") or "").strip(),
        "catalog_path": str(_CATALOG_PATH.relative_to(_REPO_ROOT)),
        "generated_at_utc": str(payload.get("generated_at_utc", "") or "").strip(),
        "surface": surface_id,
        "surface_meta": surface_meta,
        "include_unavailable": include_unavailable,
        "capability_count": len(projected),
        "capabilities": projected,
    }


def build_surface_parity_report(*, catalog: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = catalog if catalog is not None else load_surface_capability_catalog()
    surfaces = supported_surface_ids()
    capability_rows = payload.get("capabilities")
    surface_meta_by_id = {row.get("id", ""): row for row in payload.get("surfaces", []) if isinstance(row, dict)}
    coverage_by_surface: dict[str, dict[str, Any]] = {}
    capability_checks: list[dict[str, Any]] = []
    findings: list[dict[str, Any]] = []

    for surface_id in surfaces:
        meta = surface_meta_by_id.get(surface_id, {})
        coverage_by_surface[surface_id] = {
            "title": str(meta.get("title", "") or "").strip(),
            "projection_kind": str(meta.get("projection_kind", "") or "").strip(),
            "capability_count": 0,
            "available": 0,
            "documented": 0,
            "unavailable": 0,
        }

    if isinstance(capability_rows, list):
        for capability in capability_rows:
            if not isinstance(capability, dict):
                continue
            capability_id = str(capability.get("id", "") or "").strip()
            surfaces_payload = capability.get("surfaces", {})
            if not isinstance(surfaces_payload, dict):
                surfaces_payload = {}
            missing_surfaces = [surface_id for surface_id in surfaces if surface_id not in surfaces_payload]
            unknown_surfaces = sorted(surface_id for surface_id in surfaces_payload if surface_id not in surfaces)
            invalid_availability: list[dict[str, str]] = []
            entrypoint_gaps: list[dict[str, str]] = []

            for surface_id in surfaces:
                coverage_by_surface[surface_id]["capability_count"] += 1
                projection = surfaces_payload.get(surface_id, {})
                if not isinstance(projection, dict):
                    projection = {}
                availability = _normalize_availability(projection.get("availability"))
                if availability not in _SUPPORTED_AVAILABILITY:
                    invalid_availability.append(
                        {
                            "surface": surface_id,
                            "availability": str(projection.get("availability", "") or "").strip(),
                        }
                    )
                coverage_by_surface[surface_id][availability if availability in _SUPPORTED_AVAILABILITY else "unavailable"] += 1
                entrypoints = _normalize_string_list(projection.get("entrypoints"))
                if availability in {"available", "documented"} and not entrypoints:
                    entrypoint_gaps.append({"surface": surface_id, "availability": availability})

            capability_check = {
                "id": capability_id,
                "missing_surfaces": missing_surfaces,
                "unknown_surfaces": unknown_surfaces,
                "invalid_availability": invalid_availability,
                "entrypoint_gaps": entrypoint_gaps,
            }
            capability_checks.append(capability_check)

            if missing_surfaces:
                findings.append(
                    {
                        "kind": "missing_surfaces",
                        "capability_id": capability_id,
                        "surfaces": missing_surfaces,
                    }
                )
            if unknown_surfaces:
                findings.append(
                    {
                        "kind": "unknown_surfaces",
                        "capability_id": capability_id,
                        "surfaces": unknown_surfaces,
                    }
                )
            if invalid_availability:
                findings.append(
                    {
                        "kind": "invalid_availability",
                        "capability_id": capability_id,
                        "details": invalid_availability,
                    }
                )
            if entrypoint_gaps:
                findings.append(
                    {
                        "kind": "entrypoint_gap",
                        "capability_id": capability_id,
                        "details": entrypoint_gaps,
                    }
                )

    return {
        "schema_version": "datapulse_surface_parity_report.v1",
        "catalog_id": str(payload.get("catalog_id", "") or "").strip(),
        "catalog_path": str(_CATALOG_PATH.relative_to(_REPO_ROOT)),
        "generated_at_utc": str(payload.get("generated_at_utc", "") or "").strip(),
        "surface_count": len(surfaces),
        "capability_count": len(capability_checks),
        "ok": not findings,
        "coverage_by_surface": coverage_by_surface,
        "findings": findings,
        "capabilities": capability_checks,
    }


def build_runtime_surface_introspection(
    *,
    catalog: dict[str, Any] | None = None,
    include_unavailable: bool = True,
) -> dict[str, Any]:
    payload = catalog if catalog is not None else load_surface_capability_catalog()
    surfaces = supported_surface_ids()
    surface_rows: list[dict[str, Any]] = []

    for surface_id in surfaces:
        projection = build_surface_capability_projection(
            surface_id,
            catalog=payload,
            include_unavailable=include_unavailable,
        )
        counts = {
            "available": 0,
            "documented": 0,
            "unavailable": 0,
        }
        for capability in projection.get("capabilities", []):
            if not isinstance(capability, dict):
                continue
            availability = _normalize_availability(capability.get("availability"))
            counts[availability if availability in counts else "unavailable"] += 1
        surface_rows.append(
            {
                "id": surface_id,
                "title": str(projection.get("surface_meta", {}).get("title", "") or "").strip(),
                "projection_kind": str(projection.get("surface_meta", {}).get("projection_kind", "") or "").strip(),
                "artifacts": _normalize_string_list(projection.get("surface_meta", {}).get("artifacts")),
                "capability_count": int(projection.get("capability_count", 0) or 0),
                "availability_counts": counts,
                "projection": projection,
            }
        )

    return {
        "schema_version": "datapulse_runtime_surface_introspection.v1",
        "catalog_id": str(payload.get("catalog_id", "") or "").strip(),
        "catalog_path": str(_CATALOG_PATH.relative_to(_REPO_ROOT)),
        "generated_at_utc": str(payload.get("generated_at_utc", "") or "").strip(),
        "surface_count": len(surface_rows),
        "capability_count": len(payload.get("capabilities", [])) if isinstance(payload.get("capabilities"), list) else 0,
        "include_unavailable": include_unavailable,
        "surfaces": surface_rows,
        "parity": build_surface_parity_report(catalog=payload),
        "reopen_rules": runtime_reopen_rules(),
    }


def _normalize_surface_id(surface: str) -> str:
    normalized = str(surface or "").strip().lower()
    if normalized not in supported_surface_ids():
        raise ValueError(f"Unsupported surface: {surface}")
    return normalized


def _surface_meta(surface_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    surfaces = payload.get("surfaces")
    if not isinstance(surfaces, list):
        return {"id": surface_id}
    for row in surfaces:
        if not isinstance(row, dict):
            continue
        candidate = str(row.get("id", "") or "").strip().lower()
        if candidate == surface_id:
            return row
    return {"id": surface_id}


def _normalize_availability(value: Any) -> str:
    normalized = str(value or "unavailable").strip().lower()
    if normalized in _SUPPORTED_AVAILABILITY:
        return normalized
    return normalized or "unavailable"


def _normalize_string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    normalized: list[str] = []
    for item in value:
        text = str(item or "").strip()
        if text:
            normalized.append(text)
    return normalized
