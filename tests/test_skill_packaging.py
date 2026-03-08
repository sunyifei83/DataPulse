from __future__ import annotations

from pathlib import Path


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
