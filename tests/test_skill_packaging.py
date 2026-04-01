from __future__ import annotations

from pathlib import Path

from datapulse.surface_capabilities import build_runtime_surface_introspection


def test_root_skill_markdown_has_openclaw_frontmatter():
    skill_path = Path(__file__).resolve().parents[1] / "SKILL.md"

    assert skill_path.exists()

    text = skill_path.read_text(encoding="utf-8")
    assert text.startswith("---\n")

    frontmatter, body = text.split("\n---\n", 1)

    assert "name: datapulse" in frontmatter
    assert "description:" in frontmatter
    assert "metadata:" in frontmatter
    assert body.lstrip().startswith("# DataPulse Skill")


def test_runtime_introspection_covers_skill_surface() -> None:
    payload = build_runtime_surface_introspection()
    skill_surface = next(row for row in payload["surfaces"] if row["id"] == "skill")

    assert skill_surface["projection_kind"] == "documentation_and_manifest"
    assert skill_surface["availability_counts"]["documented"] >= 1
    assert payload["reopen_rules"]["inadmissible_reasons"][0]["id"] == "collector_count_growth"
