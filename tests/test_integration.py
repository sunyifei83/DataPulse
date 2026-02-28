"""Integration tests for end-to-end read_url pipeline."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from datapulse.core.models import DataPulseItem, SourceType
from datapulse.reader import DataPulseReader


SAMPLE_HTML = """
<html>
<head>
    <title>Test Article</title>
    <meta property="og:title" content="Test Article - OG" />
    <meta name="author" content="Test Author" />
</head>
<body>
    <article>
        <h1>Test Article</h1>
        <p>This is a test article with enough content to pass confidence scoring.
        It contains multiple sentences and paragraphs to simulate a real web page.
        The content should be substantial enough for the pipeline to process.</p>
        <p>Additional paragraph with more meaningful content for extraction.
        DataPulse should be able to parse this and produce a valid DataPulseItem.</p>
    </article>
</body>
</html>
"""


class TestReadUrlPipeline:
    """End-to-end test: URL → parse → DataPulseItem → inbox persistence."""

    @pytest.fixture()
    def reader(self, tmp_path):
        inbox_path = str(tmp_path / "inbox.json")
        catalog_path = str(tmp_path / "catalog.json")
        Path(catalog_path).write_text(
            json.dumps({"version": 1, "sources": [], "subscriptions": {}, "packs": []}),
            encoding="utf-8",
        )
        import os
        os.environ["DATAPULSE_SOURCE_CATALOG"] = catalog_path
        # Suppress markdown output
        os.environ.pop("DATAPULSE_MARKDOWN_PATH", None)
        os.environ.pop("OBSIDIAN_VAULT", None)
        os.environ.pop("OUTPUT_DIR", None)
        r = DataPulseReader(inbox_path=inbox_path)
        yield r
        os.environ.pop("DATAPULSE_SOURCE_CATALOG", None)

    @patch("datapulse.collectors.generic.requests.get")
    def test_read_url_produces_item(self, mock_get, reader):
        """Full pipeline: mock HTTP → parse → item in inbox."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "text/html; charset=utf-8"}
        mock_response.content = SAMPLE_HTML.encode("utf-8")
        mock_response.text = SAMPLE_HTML
        mock_response.encoding = "utf-8"
        mock_response.apparent_encoding = "utf-8"
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=False)
        # iter_content for streaming
        mock_response.iter_content = MagicMock(return_value=[SAMPLE_HTML.encode("utf-8")])
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        item = reader._read_sync("https://example.com/test-article")

        assert isinstance(item, DataPulseItem)
        assert item.url == "https://example.com/test-article"
        assert item.source_type == SourceType.GENERIC
        assert item.confidence > 0
        assert item.title != ""
        assert len(item.content) > 0

        # Item should be persisted in inbox
        assert len(reader.inbox.items) == 1
        assert reader.inbox.items[0].id == item.id

    @patch("datapulse.collectors.generic.requests.get")
    def test_read_url_saves_to_disk(self, mock_get, reader):
        """Verify inbox is persisted to JSON file after read."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "text/html"}
        mock_response.content = SAMPLE_HTML.encode("utf-8")
        mock_response.text = SAMPLE_HTML
        mock_response.encoding = "utf-8"
        mock_response.apparent_encoding = "utf-8"
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=False)
        mock_response.iter_content = MagicMock(return_value=[SAMPLE_HTML.encode("utf-8")])
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        reader._read_sync("https://example.com/persist-test")

        # Reload from disk
        inbox_path = str(reader.inbox.path)
        assert Path(inbox_path).exists()
        data = json.loads(Path(inbox_path).read_text(encoding="utf-8"))
        assert len(data) == 1
        assert data[0]["url"] == "https://example.com/persist-test"

    @patch("datapulse.collectors.generic.requests.get")
    def test_duplicate_url_not_added_twice(self, mock_get, reader):
        """Inbox deduplication: same URL should not create duplicate entries."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "text/html"}
        mock_response.content = SAMPLE_HTML.encode("utf-8")
        mock_response.text = SAMPLE_HTML
        mock_response.encoding = "utf-8"
        mock_response.apparent_encoding = "utf-8"
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=False)
        mock_response.iter_content = MagicMock(return_value=[SAMPLE_HTML.encode("utf-8")])
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        reader._read_sync("https://example.com/dup-test")
        reader._read_sync("https://example.com/dup-test")

        assert len(reader.inbox.items) == 1
