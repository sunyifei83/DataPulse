"""Tests for GitHubCollector (mocked API)."""

from __future__ import annotations

from unittest.mock import patch

from datapulse.collectors.github import GitHubCollector


class _Resp:
    def __init__(self, status_code: int, payload: dict | None = None):
        self.status_code = status_code
        self._payload = payload or {}

    def json(self):
        return self._payload


def test_parse_repo_success_with_release():
    collector = GitHubCollector()
    repo_payload = {
        "full_name": "OpenLineage/OpenLineage",
        "description": "An open standard for lineage metadata.",
        "stargazers_count": 5400,
        "forks_count": 920,
        "open_issues_count": 120,
        "subscribers_count": 88,
        "language": "Java",
        "license": {"spdx_id": "Apache-2.0"},
        "topics": ["lineage", "data"],
        "default_branch": "main",
        "pushed_at": "2026-03-01T00:00:00Z",
        "created_at": "2020-01-01T00:00:00Z",
        "updated_at": "2026-03-02T00:00:00Z",
        "archived": False,
        "disabled": False,
        "html_url": "https://github.com/OpenLineage/OpenLineage",
        "homepage": "https://openlineage.io",
    }
    release_payload = {
        "tag_name": "v1.2.3",
        "name": "1.2.3",
        "published_at": "2026-02-20T00:00:00Z",
        "html_url": "https://github.com/OpenLineage/OpenLineage/releases/tag/v1.2.3",
    }

    def _fake_get(url: str, **kwargs):  # noqa: ARG001
        if url.endswith("/repos/OpenLineage/OpenLineage"):
            return _Resp(200, repo_payload)
        if url.endswith("/repos/OpenLineage/OpenLineage/releases/latest"):
            return _Resp(200, release_payload)
        raise AssertionError(url)

    with patch("requests.get", side_effect=_fake_get):
        result = collector.parse("https://github.com/OpenLineage/OpenLineage")

    assert result.success is True
    assert result.title == "OpenLineage/OpenLineage"
    assert result.extra["stars"] == 5400
    assert result.extra["forks"] == 920
    assert result.extra["release"]["tag_name"] == "v1.2.3"
    assert "github_api" in result.confidence_flags
    assert "rich_data" in result.confidence_flags


def test_parse_repo_503_returns_degraded_success():
    collector = GitHubCollector()

    def _fake_get(url: str, **kwargs):  # noqa: ARG001
        if url.endswith("/releases/latest"):
            return _Resp(404, {})
        return _Resp(503, {})

    with patch("requests.get", side_effect=_fake_get):
        result = collector.parse("https://github.com/acme/project")

    assert result.success is True
    assert result.extra["api_degraded"] is True
    assert "fetch_degraded" in result.confidence_flags
    assert result.extra["repo"] == "acme/project"


def test_parse_repo_404_returns_failure():
    collector = GitHubCollector()

    def _fake_get(url: str, **kwargs):  # noqa: ARG001
        if url.endswith("/repos/acme/missing"):
            return _Resp(404, {})
        return _Resp(404, {})

    with patch("requests.get", side_effect=_fake_get):
        result = collector.parse("https://github.com/acme/missing")

    assert result.success is False
