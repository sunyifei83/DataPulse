#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import subprocess
import tempfile
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def slugify(value: str) -> str:
    lowered = value.strip().lower()
    slug = re.sub(r"[^a-z0-9]+", "-", lowered).strip("-")
    return slug or "project"


def run_json(cmd: list[str]) -> dict[str, object]:
    completed = subprocess.run(cmd, check=True, capture_output=True, text=True)
    return json.loads(completed.stdout)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Verify that the exported governance loop reuse kit can bootstrap a new project in isolation."
    )
    parser.add_argument(
        "--project",
        default="ExampleProject",
        help="Project name used for the isolated scaffold verification.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_root = Path(tmp_dir)
        kit_dir = tmp_root / "kit"
        scaffold_root = tmp_root / "scaffold"

        subprocess.run(
            ["python3", "scripts/governance/export_governance_loop_reuse_kit.py", "--out-dir", str(kit_dir)],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )

        subprocess.run(
            [
                "python3",
                str(kit_dir / "scripts/governance/init_governance_loop_project_scaffold.py"),
                "--project",
                args.project,
                "--out-dir",
                str(scaffold_root),
            ],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )

        slug = slugify(args.project)
        bundle_dir = scaffold_root / slug
        template_adapter = bundle_dir / f"templates/scripts/governance/{slug}_loop_adapter.py"
        template_exporter = bundle_dir / f"templates/scripts/governance/export_{slug}_loop_adapter_bundle.py"

        subprocess.run(
            ["python3", "-m", "py_compile", str(template_adapter), str(template_exporter)],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )

        validate_payload = run_json(
            [
                "python3",
                str(kit_dir / "scripts/governance/validate_governance_loop_bundle_draft.py"),
                "--bundle-dir",
                str(bundle_dir),
            ]
        )
        verify_payload = run_json(
            [
                "python3",
                str(kit_dir / "scripts/governance/verify_governance_loop_adoption_draft.py"),
                "--bundle-dir",
                str(bundle_dir),
            ]
        )
        activation_payload = run_json(
            [
                "python3",
                str(kit_dir / "scripts/governance/assess_governance_loop_activation_draft.py"),
                "--bundle-dir",
                str(bundle_dir),
            ]
        )
        activation_plan_payload = run_json(
            [
                "python3",
                str(kit_dir / "scripts/governance/export_governance_loop_activation_plan.py"),
                "--bundle-dir",
                str(bundle_dir),
                "--stdout",
            ]
        )
        activation_intent_path = bundle_dir / "activation_intent.draft.json"
        subprocess.run(
            [
                "python3",
                str(kit_dir / "scripts/governance/export_governance_loop_activation_intent.py"),
                "--bundle-dir",
                str(bundle_dir),
                "--out-path",
                str(activation_intent_path),
            ],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        activation_intent_verify_payload = run_json(
            [
                "python3",
                str(kit_dir / "scripts/governance/verify_governance_loop_activation_intent.py"),
                "--bundle-dir",
                str(bundle_dir),
                "--activation-intent-json",
                str(activation_intent_path),
            ]
        )
        activation_preview_path = bundle_dir / "activation_preview.draft.json"
        subprocess.run(
            [
                "python3",
                str(kit_dir / "scripts/governance/export_governance_loop_activation_preview.py"),
                "--bundle-dir",
                str(bundle_dir),
                "--activation-intent-json",
                str(activation_intent_path),
                "--out-path",
                str(activation_preview_path),
            ],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        activation_preview_verify_payload = run_json(
            [
                "python3",
                str(kit_dir / "scripts/governance/verify_governance_loop_activation_preview.py"),
                "--bundle-dir",
                str(bundle_dir),
                "--activation-intent-json",
                str(activation_intent_path),
                "--activation-preview-json",
                str(activation_preview_path),
            ]
        )
        replay_payload = run_json(
            [
                "python3",
                str(kit_dir / "scripts/governance/run_governance_loop_bundle_draft.py"),
                "--bundle-dir",
                str(bundle_dir),
            ]
        )

        checks = [
            {
                "name": "kit_exported",
                "ok": (kit_dir / "governance_loop_reuse_kit_manifest.draft.json").exists(),
                "details": ["kit manifest exported"],
            },
            {
                "name": "starter_templates_compile",
                "ok": True,
                "details": ["starter adapter and exporter templates compile"],
            },
            {
                "name": "bundle_validates",
                "ok": bool(validate_payload.get("valid", False)),
                "details": ["bundle validator returned valid=true"],
            },
            {
                "name": "bundle_verifies",
                "ok": bool(verify_payload.get("valid", False)),
                "details": ["adoption verifier returned valid=true"],
            },
            {
                "name": "activation_boundary_assessed",
                "ok": bool(activation_payload.get("valid", False)),
                "details": [
                    f"activation surfaces={len(activation_payload.get('activation_boundary', {}).get('activation_requirements', []))}"
                ],
            },
            {
                "name": "activation_plan_exported",
                "ok": bool(activation_plan_payload.get("activation_status", {}).get("planning_ready", False)),
                "details": [
                    f"ready_for_active_wiring={activation_plan_payload.get('activation_status', {}).get('ready_for_active_wiring', False)}"
                ],
            },
            {
                "name": "activation_intent_verified",
                "ok": bool(activation_intent_verify_payload.get("valid", False)),
                "details": ["activation intent remains aligned with activation plan"],
            },
            {
                "name": "activation_preview_verified",
                "ok": bool(activation_preview_verify_payload.get("valid", False)),
                "details": ["activation preview remains aligned with activation plan and intent"],
            },
            {
                "name": "bundle_replays",
                "ok": bool(replay_payload.get("status")),
                "details": [f"bundle replay status={replay_payload.get('status', '')}"],
            },
        ]

        payload = {
            "valid": all(item["ok"] for item in checks),
            "project": args.project,
            "kit_dir": str(kit_dir),
            "bundle_dir": str(bundle_dir),
            "checks": checks,
            "validate": validate_payload,
            "verify": verify_payload,
            "activation": activation_payload,
            "activation_plan": activation_plan_payload,
            "activation_intent_verify": activation_intent_verify_payload,
            "activation_preview_verify": activation_preview_verify_payload,
            "replay": replay_payload,
        }
        print(json.dumps(payload, indent=2, ensure_ascii=True))
        return 0 if payload["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
