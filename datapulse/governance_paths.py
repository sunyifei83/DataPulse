from __future__ import annotations

import os
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parent.parent

RUNTIME_BUNDLE_ROOT = "runtime_bundle_root"
GOVERNANCE_SNAPSHOT_ROOT = "governance_snapshot_root"
EVIDENCE_BUNDLE_ROOT = "evidence_bundle_root"

_ROOT_SPECS: dict[str, dict[str, Any]] = {
    RUNTIME_BUNDLE_ROOT: {
        "env_var": "DATAPULSE_RUNTIME_BUNDLE_ROOT",
        "canonical_root": "config/modelbus/datapulse",
        "legacy_roots": [
            "out/ha_latest_release_bundle",
        ],
    },
    GOVERNANCE_SNAPSHOT_ROOT: {
        "env_var": "DATAPULSE_GOVERNANCE_SNAPSHOT_ROOT",
        "canonical_root": "artifacts/governance/snapshots",
        "legacy_roots": [
            "out/governance",
        ],
    },
    EVIDENCE_BUNDLE_ROOT: {
        "env_var": "DATAPULSE_EVIDENCE_BUNDLE_ROOT",
        "canonical_root": "artifacts/governance/release_bundle",
        "legacy_roots": [
            "out/release_bundle",
            "out/ha_latest_release_bundle",
        ],
    },
}


def resolve_repo_path(raw_path: str | Path, *, repo_root: Path = REPO_ROOT) -> Path:
    path = Path(str(raw_path or "").strip()).expanduser()
    if path.is_absolute():
        return path.resolve()
    return (repo_root / path).resolve()


def _dedupe_path_entries(entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    deduped: list[dict[str, Any]] = []
    seen: set[str] = set()
    for entry in entries:
        path = entry.get("path")
        if not isinstance(path, Path):
            continue
        key = str(path.resolve())
        if key in seen:
            continue
        seen.add(key)
        deduped.append(entry)
    return deduped


def configured_root_env_var(resolver_name: str) -> str:
    spec = _ROOT_SPECS.get(resolver_name)
    if spec is None:
        raise KeyError(f"unknown resolver: {resolver_name}")
    return str(spec["env_var"])


def canonical_root(resolver_name: str, *, repo_root: Path = REPO_ROOT) -> Path:
    spec = _ROOT_SPECS.get(resolver_name)
    if spec is None:
        raise KeyError(f"unknown resolver: {resolver_name}")
    canonical = Path(spec["canonical_root"])
    if canonical.is_absolute():
        return canonical.resolve()
    return resolve_repo_path(canonical, repo_root=repo_root)


def configured_root(
    resolver_name: str,
    *,
    repo_root: Path = REPO_ROOT,
    environ: dict[str, str] | None = None,
) -> Path | None:
    env = environ if environ is not None else os.environ
    env_var = configured_root_env_var(resolver_name)
    raw_path = str(env.get(env_var, "") or "").strip()
    if not raw_path:
        return None
    return resolve_repo_path(raw_path, repo_root=repo_root)


def legacy_roots(resolver_name: str, *, repo_root: Path = REPO_ROOT) -> list[Path]:
    spec = _ROOT_SPECS.get(resolver_name)
    if spec is None:
        raise KeyError(f"unknown resolver: {resolver_name}")
    return [resolve_repo_path(path, repo_root=repo_root) for path in spec["legacy_roots"]]


def root_candidate_entries(
    resolver_name: str,
    *,
    explicit_root: Path | str | None = None,
    repo_root: Path = REPO_ROOT,
    environ: dict[str, str] | None = None,
) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    if explicit_root is not None and str(explicit_root).strip():
        entries.append(
            {
                "path": resolve_repo_path(explicit_root, repo_root=repo_root),
                "source": "explicit_root",
                "resolver_name": resolver_name,
            }
        )
    configured = configured_root(resolver_name, repo_root=repo_root, environ=environ)
    if configured is not None:
        entries.append(
            {
                "path": configured,
                "source": "configured_root",
                "resolver_name": resolver_name,
                "env_var": configured_root_env_var(resolver_name),
            }
        )
    entries.append(
        {
            "path": canonical_root(resolver_name, repo_root=repo_root),
            "source": "canonical_root",
            "resolver_name": resolver_name,
        }
    )
    for legacy in legacy_roots(resolver_name, repo_root=repo_root):
        entries.append(
            {
                "path": legacy,
                "source": "legacy_fallback",
                "resolver_name": resolver_name,
            }
        )
    return _dedupe_path_entries(entries)


def root_candidates(
    resolver_name: str,
    *,
    explicit_root: Path | str | None = None,
    repo_root: Path = REPO_ROOT,
    environ: dict[str, str] | None = None,
) -> list[Path]:
    return [entry["path"] for entry in root_candidate_entries(
        resolver_name,
        explicit_root=explicit_root,
        repo_root=repo_root,
        environ=environ,
    )]


def write_root(
    resolver_name: str,
    *,
    explicit_root: Path | str | None = None,
    repo_root: Path = REPO_ROOT,
    environ: dict[str, str] | None = None,
) -> Path:
    candidates = root_candidate_entries(
        resolver_name,
        explicit_root=explicit_root,
        repo_root=repo_root,
        environ=environ,
    )
    for entry in candidates:
        if entry.get("source") != "legacy_fallback":
            return entry["path"]
    return candidates[0]["path"]


def read_root(
    resolver_name: str,
    *,
    explicit_root: Path | str | None = None,
    repo_root: Path = REPO_ROOT,
    environ: dict[str, str] | None = None,
) -> Path:
    candidates = root_candidates(
        resolver_name,
        explicit_root=explicit_root,
        repo_root=repo_root,
        environ=environ,
    )
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return write_root(
        resolver_name,
        explicit_root=explicit_root,
        repo_root=repo_root,
        environ=environ,
    )


def read_path(
    resolver_name: str,
    relative_path: str | Path,
    *,
    explicit_path: Path | str | None = None,
    explicit_root: Path | str | None = None,
    repo_root: Path = REPO_ROOT,
    environ: dict[str, str] | None = None,
) -> Path:
    if explicit_path is not None and str(explicit_path).strip():
        return resolve_repo_path(explicit_path, repo_root=repo_root)
    rel = Path(str(relative_path))
    if rel.is_absolute():
        return rel.resolve()
    candidates = [
        (root / rel).resolve()
        for root in root_candidates(
            resolver_name,
            explicit_root=explicit_root,
            repo_root=repo_root,
            environ=environ,
        )
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return (write_root(
        resolver_name,
        explicit_root=explicit_root,
        repo_root=repo_root,
        environ=environ,
    ) / rel).resolve()


def write_path(
    resolver_name: str,
    relative_path: str | Path,
    *,
    explicit_path: Path | str | None = None,
    explicit_root: Path | str | None = None,
    repo_root: Path = REPO_ROOT,
    environ: dict[str, str] | None = None,
) -> Path:
    if explicit_path is not None and str(explicit_path).strip():
        return resolve_repo_path(explicit_path, repo_root=repo_root)
    rel = Path(str(relative_path))
    if rel.is_absolute():
        return rel.resolve()
    return (write_root(
        resolver_name,
        explicit_root=explicit_root,
        repo_root=repo_root,
        environ=environ,
    ) / rel).resolve()
