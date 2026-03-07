#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def slugify(value: str) -> str:
    lowered = value.strip().lower()
    slug = re.sub(r"[^a-z0-9]+", "-", lowered).strip("-")
    return slug or "project"


def write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_plan(project: str, slug: str) -> dict[str, object]:
    return {
        "schema_version": "blueprint_plan.v1",
        "plan_id": f"{slug}-loop-bootstrap",
        "project": project,
        "generated_at_utc": utc_now(),
        "status": "draft_not_wired",
        "activation": {
            "wired": False,
            "future_active_path": f"docs/governance/{slug}-blueprint-plan.json",
            "promotion_mode": "manual_only",
        },
        "automation_objective": {
            "target_class": "trusted_delivery_pipeline",
            "continuous_when_healthy": True,
            "halts_on_machine_decidable_blockers": True,
            "blocked_state_is_expected": True,
        },
        "slice_profiles": {
            "draft_only": {
                "description": "Plan or contract drafting slices with no default service-governance coupling.",
                "blocking_gate_groups": [],
            },
            "workflow_change": {
                "description": "Workflow or automation slices that only depend on execution safety by default.",
                "blocking_gate_groups": ["execution_safety"],
            },
            "runtime_validation": {
                "description": "Slices that intentionally depend on runtime or service evidence.",
                "blocking_gate_groups": [
                    "execution_safety",
                    "local_verification",
                    "runtime_governance",
                ],
            },
        },
        "phases": [
            {
                "id": "P0",
                "title": "Loop Contract Bootstrap",
                "goal": "Create the first machine-readable loop contracts without changing active workflows.",
                "status": "pending",
                "slices": [
                    {
                        "id": "P0.1",
                        "title": "Define project loop adapter contracts",
                        "category": "manual",
                        "execution_profile": "draft_only",
                        "promotion_scope": "none",
                        "status": "pending",
                        "artifacts": [
                            f"docs/governance/{slug}-loop-adapter-design.md",
                            f"docs/governance/{slug}-blueprint-plan.json",
                        ],
                    }
                ],
            }
        ],
        "recommended_next_slice": {
            "id": "P0.1",
            "title": "Define project loop adapter contracts",
            "reason": "Starter scaffold defaults to the first bootstrap slice.",
        },
    }


def build_landing_status(project: str) -> dict[str, object]:
    return {
        "schema_version": "code_landing_status.v1",
        "project": project,
        "generated_at_utc": utc_now(),
        "status_kind": "starter_template",
        "wired": False,
        "workspace": {
            "clean": False,
            "reason": "Replace with project-specific workspace truth.",
        },
        "gate_groups": {
            "execution_safety": [],
            "local_verification": [],
            "runtime_governance": [],
            "ci_policy": [],
            "release_governance": [],
        },
        "promotion_levels": {
            "repo_landed": {
                "satisfied": False,
                "reasons": ["repo_truth_not_exported"],
            },
            "ci_proven": {
                "satisfied": False,
                "reasons": ["repo_landed_false", "ci_truth_not_exported"],
            },
        },
        "notes": [
            "Replace this starter snapshot with a project-specific landing-status exporter.",
        ],
    }


def build_slice_catalog(project: str, slug: str) -> dict[str, object]:
    return {
        "schema_version": "slice_adapter_catalog.v1",
        "project": project,
        "generated_at_utc": utc_now(),
        "wired": False,
        "slices": {
            "P0.1": {
                "adapter_type": "bootstrap_contract",
                "execute_mode": "manual_edit",
                "summary": "Define the project-specific plan, landing-status exporter, and slice map.",
                "candidate_commands": [
                    f"edit docs/governance/{slug}-blueprint-plan.json",
                    f"implement scripts/governance/{slug}_loop_adapter.py",
                    "run the bundle validator after exporting a real landing-status snapshot",
                ],
                "target_artifacts": [
                    f"docs/governance/{slug}-blueprint-plan.json",
                    f"scripts/governance/{slug}_loop_adapter.py",
                ],
                "notes": [
                    "Keep project-specific workflow names and commands in the adapter.",
                    "Keep next-slice and blocker semantics in the reusable core.",
                ],
            }
        },
    }


def build_manifest(project: str) -> dict[str, object]:
    return {
        "schema_version": "adapter_bundle_manifest.v1",
        "project": project,
        "generated_at_utc": utc_now(),
        "bundle_kind": "starter_scaffold",
        "wired": False,
        "files": {
            "plan": "blueprint_plan.snapshot.json",
            "landing_status": "code_landing_status.snapshot.json",
            "slice_catalog": "slice_adapter_catalog.snapshot.json",
        },
        "adapter_metadata": {
            "adapter_module": "scripts/governance/<project>_loop_adapter.py",
            "core_runner": "scripts/governance/run_governance_loop_bundle_draft.py",
            "validator": "scripts/governance/validate_governance_loop_bundle_draft.py",
        },
        "notes": [
            "This scaffold is intentionally non-wired.",
            "The generated bundle should validate and replay before any active workflow wiring begins.",
        ],
    }


def build_next_steps(project: str, slug: str) -> str:
    return f"""# Governance Loop Scaffold For {project}

Status: starter scaffold

Generated: {utc_now()}

## Files

- `adapter_bundle_manifest.draft.json`
- `blueprint_plan.snapshot.json`
- `code_landing_status.snapshot.json`
- `slice_adapter_catalog.snapshot.json`

## Recommended Next Steps

1. Replace `code_landing_status.snapshot.json` with a real exporter output for {project}.
2. Expand `blueprint_plan.snapshot.json` from the single bootstrap slice into your real roadmap slices.
3. Replace placeholder adapter metadata with your actual adapter module path.
4. Run:

```bash
python3 scripts/governance/validate_governance_loop_bundle_draft.py --bundle-dir <this-dir>
python3 scripts/governance/run_governance_loop_bundle_draft.py --bundle-dir <this-dir>
```

5. Only after the bundle validates and replays should you consider active workflow wiring.

## Naming Suggestions

- plan path: `docs/governance/{slug}-blueprint-plan.json`
- adapter module: `scripts/governance/{slug}_loop_adapter.py`
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a starter governance loop scaffold for a new repository or project."
    )
    parser.add_argument("--project", required=True, help="Project name for the scaffold.")
    parser.add_argument(
        "--slug",
        default="",
        help="Optional project slug. Defaults to a slug derived from --project.",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path("out/governance/scaffold"),
        help="Output directory for the starter scaffold.",
    )
    parser.add_argument(
        "--stdout",
        action="store_true",
        help="Print the scaffold manifest JSON to stdout instead of writing files.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    slug = args.slug or slugify(args.project)
    out_dir = args.out_dir / slug

    plan = build_plan(args.project, slug)
    landing_status = build_landing_status(args.project)
    slice_catalog = build_slice_catalog(args.project, slug)
    manifest = build_manifest(args.project)
    next_steps = build_next_steps(args.project, slug)

    if args.stdout:
        payload = {
            "project": args.project,
            "slug": slug,
            "out_dir": str(out_dir),
            "files": list(manifest["files"].values()) + ["adapter_bundle_manifest.draft.json", "ADOPTION_NEXT_STEPS.md"],
        }
        print(json.dumps(payload, indent=2, ensure_ascii=True))
        return 0

    write_json(out_dir / "blueprint_plan.snapshot.json", plan)
    write_json(out_dir / "code_landing_status.snapshot.json", landing_status)
    write_json(out_dir / "slice_adapter_catalog.snapshot.json", slice_catalog)
    write_json(out_dir / "adapter_bundle_manifest.draft.json", manifest)
    write_text(out_dir / "ADOPTION_NEXT_STEPS.md", next_steps)
    print(out_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
