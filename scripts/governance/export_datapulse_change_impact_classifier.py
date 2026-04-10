#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = REPO_ROOT / "artifacts" / "governance" / "snapshots" / "change_impact_classifier.draft.json"
DEFAULT_LOOP_STATE = REPO_ROOT / "out" / "ha_latest_release_bundle" / "project_specific_loop_state.draft.json"
DEFAULT_RELEASE_WINDOW_ATTESTATION = REPO_ROOT / "out" / "ha_latest_release_bundle" / "datapulse_release_window_attestation.draft.json"
DEFAULT_SURFACE_RUNTIME_HIT_EVIDENCE = REPO_ROOT / "out" / "ha_latest_release_bundle" / "datapulse_surface_runtime_hit_evidence.draft.json"


HIGH_RISK_RULES = (
    (
        (
            "config/modelbus/",
            "export_datapulse_modelbus_consumer_bundle.py",
            "export_datapulse_internal_ai_surface_admission.py",
            "export_datapulse_internal_ai_surface_registry.py",
            "export_datapulse_internal_ai_surface_runtime_evidence.py",
        ),
        (
            "bridge_contract",
            "admission_semantics",
            "governed_surface_contract",
            "shared_handoff_object",
        ),
        "Changed paths hit DataPulse northbound surface or ModelBus handoff contract files.",
    ),
    (
        (
            "export_datapulse_release_",
            "export_datapulse_ha_",
            "export_datapulse_surface_runtime_hit_evidence.py",
            "out/ha_latest_release_bundle/",
        ),
        (
            "release_window_truth",
            "same_window_attestation",
            "tri_repo_control_tower_status",
        ),
        "Changed paths hit release-window or same-window attestation evidence surfaces.",
    ),
)

SEED_RULES = (
    (
        (
            "scripts/governance/",
            "docs/governance/",
            "artifacts/governance/",
        ),
        (
            "shared_handoff_object",
            "tri_repo_control_tower_status",
        ),
        "Changed paths touch governance handoff surfaces that should be mirrored by the control tower.",
    ),
)


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def snapshot_date() -> str:
    return utc_now()[:10]


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return payload if isinstance(payload, dict) else {}


def _git_changed_paths(repo_root: Path) -> list[str]:
    run = subprocess.run(
        ["git", "status", "--short"],
        cwd=str(repo_root),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    if run.returncode != 0:
        return []
    changed_paths: list[str] = []
    for raw_line in run.stdout.splitlines():
        line = raw_line.rstrip()
        if not line:
            continue
        path = line[3:] if len(line) > 3 else line
        path = path.split(" -> ", 1)[-1].strip()
        if path:
            changed_paths.append(path)
    return changed_paths


def _git_head_sha(repo_root: Path) -> str:
    run = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=str(repo_root),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    return run.stdout.strip() if run.returncode == 0 else ""


def _match_rules(
    changed_paths: list[str],
    rules: tuple[tuple[tuple[str, ...], tuple[str, ...], str], ...],
) -> tuple[set[str], list[str]]:
    axes: set[str] = set()
    reasons: list[str] = []
    for path in changed_paths:
        normalized = path.replace("\\", "/")
        for patterns, rule_axes, reason in rules:
            if any(pattern in normalized for pattern in patterns):
                axes.update(rule_axes)
                if reason not in reasons:
                    reasons.append(reason)
    return axes, reasons


def build_payload(
    *,
    changed_paths: list[str],
    loop_state_path: Path,
    release_window_attestation_path: Path,
    surface_runtime_hit_evidence_path: Path,
) -> dict[str, Any]:
    loop_state = _read_json(loop_state_path)
    release_window_attestation = _read_json(release_window_attestation_path)
    surface_runtime_hit_evidence = _read_json(surface_runtime_hit_evidence_path)
    high_axes, high_reasons = _match_rules(changed_paths, HIGH_RISK_RULES)
    seed_axes, seed_reasons = _match_rules(changed_paths, SEED_RULES)

    if high_axes:
        classification = "shared_contract_risk_high"
        touched_axes = sorted(high_axes.union(seed_axes))
        reasons = high_reasons + [reason for reason in seed_reasons if reason not in high_reasons]
        confidence = "high"
    elif seed_axes:
        classification = "shared_handoff_seed"
        touched_axes = sorted(seed_axes)
        reasons = seed_reasons
        confidence = "medium"
    else:
        classification = "repo_local_only"
        touched_axes = []
        if changed_paths:
            reasons = [
                "Changed paths do not hit frozen tri-repo shared contract axes; keep the change repo-local."
            ]
        else:
            reasons = [
                "No changed paths detected from git status; defaulting the classifier to repo_local_only."
            ]
        confidence = "high"

    dispatch_recommended = classification != "repo_local_only"
    change_scope = "working_tree" if changed_paths else "head"
    target_repos = ["modelbus"] if dispatch_recommended else []
    summary = (
        "DataPulse changes hit shared tri-repo contract axes and should be mirrored by ModelBus."
        if dispatch_recommended
        else "DataPulse changes currently remain repo-local and do not require tri-repo signal dispatch."
    )

    evidence_refs = [
        {
            "kind": "repo_native_command",
            "path": "git status --short",
            "generated_at_utc": utc_now(),
            "digest_sha256": None,
            "note": "Changed paths were derived from the live working tree status.",
        },
        {
            "kind": "repo_native_file",
            "path": str(loop_state_path),
            "generated_at_utc": str(loop_state.get("generated_at_utc") or None),
            "digest_sha256": None,
            "note": "Current DataPulse loop snapshot used as repo-native context.",
        },
        {
            "kind": "release_artifact",
            "path": str(release_window_attestation_path),
            "generated_at_utc": str(release_window_attestation.get("generated_at_utc") or None),
            "digest_sha256": None,
            "note": "Release-window attestation provides same-window context for tri-repo classification.",
        },
        {
            "kind": "release_artifact",
            "path": str(surface_runtime_hit_evidence_path),
            "generated_at_utc": str(surface_runtime_hit_evidence.get("generated_at_utc") or None),
            "digest_sha256": None,
            "note": "Surface runtime evidence anchors current release-window truth.",
        },
    ]

    unresolved_questions = []
    if classification == "shared_handoff_seed" and not touched_axes:
        unresolved_questions.append("Shared handoff seed was selected without a concrete touched axis.")

    return {
        "schema": "tri_repo.change_impact_classifier.v1",
        "generated_at_utc": utc_now(),
        "snapshot_date": snapshot_date(),
        "repo": "datapulse",
        "head_sha": _git_head_sha(REPO_ROOT),
        "classification": classification,
        "change_scope": change_scope,
        "confidence": confidence,
        "summary": summary,
        "touched_axes": touched_axes,
        "reasons": reasons,
        "changed_paths": changed_paths,
        "source_paths": [
            str(loop_state_path),
            str(release_window_attestation_path),
            str(surface_runtime_hit_evidence_path),
        ],
        "target_repos": target_repos,
        "dispatch_recommended": dispatch_recommended,
        "evidence_refs": evidence_refs,
        "unresolved_questions": unresolved_questions,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Export a DataPulse tri-repo change impact classifier payload."
    )
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--loop-state", type=Path, default=DEFAULT_LOOP_STATE)
    parser.add_argument("--release-window-attestation", type=Path, default=DEFAULT_RELEASE_WINDOW_ATTESTATION)
    parser.add_argument("--surface-runtime-hit-evidence", type=Path, default=DEFAULT_SURFACE_RUNTIME_HIT_EVIDENCE)
    parser.add_argument("--changed-path", action="append", default=[])
    parser.add_argument("--stdout", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    changed_paths = [str(item).strip() for item in args.changed_path if str(item).strip()]
    if not changed_paths:
        changed_paths = _git_changed_paths(REPO_ROOT)
    payload = build_payload(
        changed_paths=changed_paths,
        loop_state_path=args.loop_state.resolve(),
        release_window_attestation_path=args.release_window_attestation.resolve(),
        surface_runtime_hit_evidence_path=args.surface_runtime_hit_evidence.resolve(),
    )
    if args.stdout:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0
    args.output.resolve().parent.mkdir(parents=True, exist_ok=True)
    args.output.resolve().write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(args.output.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
