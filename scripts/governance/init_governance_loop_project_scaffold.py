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
            "active_path": f"docs/governance/{slug}-blueprint-plan.json",
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


def build_manifest(project: str, slug: str) -> dict[str, object]:
    module_name = slug.replace("-", "_")
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
            "adapter_module": f"scripts/governance/{module_name}_loop_adapter.py",
            "core_runner": "scripts/governance/run_governance_loop_bundle_draft.py",
            "validator": "scripts/governance/validate_governance_loop_bundle_draft.py",
        },
        "notes": [
            "This scaffold is intentionally non-wired.",
            "The generated bundle should validate and replay before any active workflow wiring begins.",
        ],
    }


def build_adapter_module(project: str, slug: str) -> str:
    module_name = slug.replace("-", "_")
    return f"""#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from loop_core_draft import build_project_loop_state_core, build_reuse_summary, build_trust_summary, dedupe, evaluate_loop_status
from loop_bundle_draft import resolve_adapter_entry


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PLAN_PATH = REPO_ROOT / "docs/governance/{slug}-blueprint-plan.json"
DEFAULT_CATALOG_PATH = REPO_ROOT / "docs/governance/{slug}-slice-adapter-catalog.json"
DEFAULT_LANDING_STATUS_PATH = REPO_ROOT / "out/governance/code_landing_status.json"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_{module_name}_catalog(path: Path = DEFAULT_CATALOG_PATH) -> dict[str, Any]:
    return read_json(path)


def build_{module_name}_code_landing_status(path: Path = DEFAULT_LANDING_STATUS_PATH) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(
            "Replace this starter loader with a real landing-status exporter, or provide a snapshot at out/governance/code_landing_status.json."
        )
    return read_json(path)


def build_{module_name}_loop_runtime(
    plan_path: Path = DEFAULT_PLAN_PATH,
    catalog_path: Path = DEFAULT_CATALOG_PATH,
    landing_status_path: Path = DEFAULT_LANDING_STATUS_PATH,
    ignore_blocking_facts: list[str] | None = None,
) -> dict[str, Any]:
    ignored = ignore_blocking_facts or []
    plan = read_json(plan_path)
    landing_status = build_{module_name}_code_landing_status(landing_status_path)
    loop_state = build_project_loop_state_core(
        plan,
        landing_status,
        source_plan=str(plan_path),
        generated_at_utc=str(landing_status.get("generated_at_utc", utc_now())),
    )
    next_slice = dict(loop_state.get("next_slice", {{}}))
    catalog = load_{module_name}_catalog(catalog_path)
    status, reason, effective_blockers = evaluate_loop_status(loop_state, ignored)

    return {{
        "status": status,
        "reason": reason,
        "project": "{project}",
        "current_level": loop_state.get("current_level", ""),
        "next_slice": next_slice,
        "blocking_facts": loop_state.get("blocking_facts", []),
        "effective_blocking_facts": effective_blockers,
        "ignored_blocking_facts": dedupe(ignored),
        "remaining_promotion_gates": loop_state.get("remaining_promotion_gates", []),
        "pipeline_contract": loop_state.get("pipeline_contract", {{}}),
        "control_contract": loop_state.get("control_contract", {{}}),
        "flow_control": loop_state.get("flow_control", {{}}),
        "trust_summary": build_trust_summary(loop_state),
        "reuse_summary": build_reuse_summary(loop_state),
        "adapter_entry": resolve_adapter_entry(catalog, next_slice.get("id", "")),
    }}
"""


def build_bundle_exporter_module(project: str, slug: str) -> str:
    module_name = slug.replace("-", "_")
    return f"""#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from {module_name}_loop_adapter import (
    DEFAULT_CATALOG_PATH,
    DEFAULT_PLAN_PATH,
    build_{module_name}_code_landing_status,
    read_json,
    utc_now,
)


def write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\\n", encoding="utf-8")


def build_manifest() -> dict[str, object]:
    return {{
        "schema_version": "adapter_bundle_manifest.v1",
        "project": "{project}",
        "generated_at_utc": utc_now(),
        "bundle_kind": "draft_export",
        "wired": False,
        "files": {{
            "plan": "blueprint_plan.snapshot.json",
            "landing_status": "code_landing_status.snapshot.json",
            "slice_catalog": "slice_adapter_catalog.snapshot.json",
        }},
        "adapter_metadata": {{
            "adapter_module": "scripts/governance/{module_name}_loop_adapter.py",
            "core_runner": "scripts/governance/run_governance_loop_bundle_draft.py",
            "validator": "scripts/governance/validate_governance_loop_bundle_draft.py",
        }},
    }}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export an adapter bundle for {project}.")
    parser.add_argument("--plan", type=Path, default=DEFAULT_PLAN_PATH)
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG_PATH)
    parser.add_argument("--landing-status", type=Path, default=Path("out/governance/code_landing_status.json"))
    parser.add_argument("--out-dir", type=Path, default=Path("out/governance/adapter_bundle"))
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    plan = read_json(args.plan)
    landing_status = build_{module_name}_code_landing_status(args.landing_status)
    catalog = read_json(args.catalog)
    manifest = build_manifest()
    write_json(args.out_dir / "blueprint_plan.snapshot.json", plan)
    write_json(args.out_dir / "code_landing_status.snapshot.json", landing_status)
    write_json(args.out_dir / "slice_adapter_catalog.snapshot.json", catalog)
    write_json(args.out_dir / "adapter_bundle_manifest.draft.json", manifest)
    print(args.out_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
"""


def build_next_steps(project: str, slug: str) -> str:
    return f"""# Governance Loop Scaffold For {project}

Status: starter scaffold

Generated: {utc_now()}

## Files

- `adapter_bundle_manifest.draft.json`
- `blueprint_plan.snapshot.json`
- `code_landing_status.snapshot.json`
- `slice_adapter_catalog.snapshot.json`
- `templates/scripts/governance/{slug.replace("-", "_")}_loop_adapter.py`
- `templates/scripts/governance/export_{slug.replace("-", "_")}_loop_adapter_bundle.py`

## Recommended Next Steps

1. Replace `code_landing_status.snapshot.json` with a real exporter output for {project}.
2. Expand `blueprint_plan.snapshot.json` from the single bootstrap slice into your real roadmap slices.
3. Copy the generated starter templates under `templates/` into your target repository and replace the placeholder landing-status loader.
4. Replace placeholder adapter metadata with your actual adapter module path.
5. Run:

```bash
python3 scripts/governance/validate_governance_loop_bundle_draft.py --bundle-dir <this-dir>
python3 scripts/governance/verify_governance_loop_adoption_draft.py --bundle-dir <this-dir>
python3 scripts/governance/run_governance_loop_bundle_draft.py --bundle-dir <this-dir>
python3 scripts/governance/assess_governance_loop_activation_draft.py --bundle-dir <this-dir>
python3 scripts/governance/export_governance_loop_activation_plan.py --bundle-dir <this-dir> --stdout
python3 scripts/governance/export_governance_loop_activation_intent.py --bundle-dir <this-dir> --stdout
python3 scripts/governance/export_governance_loop_activation_preview.py --bundle-dir <this-dir> --stdout
```

6. Only after the bundle validates, compares, replays, and exposes a minimal activation boundary should you consider active workflow wiring.

## Naming Suggestions

- plan path: `docs/governance/{slug}-blueprint-plan.json`
- adapter module: `scripts/governance/{slug}_loop_adapter.py`
- bundle exporter: `scripts/governance/export_{slug}_loop_adapter_bundle.py`
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
    manifest = build_manifest(args.project, slug)
    next_steps = build_next_steps(args.project, slug)

    if args.stdout:
        payload = {
            "project": args.project,
            "slug": slug,
            "out_dir": str(out_dir),
            "files": list(manifest["files"].values())
            + [
                "adapter_bundle_manifest.draft.json",
                "ADOPTION_NEXT_STEPS.md",
                f"templates/scripts/governance/{slug.replace('-', '_')}_loop_adapter.py",
                f"templates/scripts/governance/export_{slug.replace('-', '_')}_loop_adapter_bundle.py",
            ],
        }
        print(json.dumps(payload, indent=2, ensure_ascii=True))
        return 0

    write_json(out_dir / "blueprint_plan.snapshot.json", plan)
    write_json(out_dir / "code_landing_status.snapshot.json", landing_status)
    write_json(out_dir / "slice_adapter_catalog.snapshot.json", slice_catalog)
    write_json(out_dir / "adapter_bundle_manifest.draft.json", manifest)
    write_text(out_dir / "ADOPTION_NEXT_STEPS.md", next_steps)
    write_text(
        out_dir / f"templates/scripts/governance/{slug.replace('-', '_')}_loop_adapter.py",
        build_adapter_module(args.project, slug),
    )
    write_text(
        out_dir / f"templates/scripts/governance/export_{slug.replace('-', '_')}_loop_adapter_bundle.py",
        build_bundle_exporter_module(args.project, slug),
    )
    print(out_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
