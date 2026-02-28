"""Tests for ArxivCollector — no network calls."""

from __future__ import annotations

import pytest

from datapulse.collectors.arxiv import ArxivCollector, extract_arxiv_id


SAMPLE_ATOM_XML = """\
<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <entry>
    <id>http://arxiv.org/abs/2301.00001v1</id>
    <title>  Attention Is All You Need
    </title>
    <summary>We propose a new architecture based on attention mechanisms.
    This paper describes the Transformer model.</summary>
    <author><name>Alice Smith</name></author>
    <author><name>Bob Jones</name></author>
    <author><name>Charlie Brown</name></author>
    <category term="cs.CL" />
    <category term="cs.AI" />
    <published>2023-01-01T00:00:00Z</published>
    <updated>2023-01-02T00:00:00Z</updated>
    <link title="pdf" href="https://arxiv.org/pdf/2301.00001v1" rel="related" type="application/pdf"/>
    <link href="https://arxiv.org/abs/2301.00001v1" rel="alternate" type="text/html"/>
  </entry>
</feed>
"""

SAMPLE_ATOM_MANY_AUTHORS = """\
<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <entry>
    <id>http://arxiv.org/abs/2301.00002v1</id>
    <title>Many Authors Paper</title>
    <summary>Abstract of a large collaboration paper.</summary>
    {authors}
    <category term="physics.hep-ex" />
    <published>2023-06-01T00:00:00Z</published>
  </entry>
</feed>
"""


class TestCanHandle:
    def test_abs_url(self):
        c = ArxivCollector()
        assert c.can_handle("https://arxiv.org/abs/2301.00001") is True

    def test_pdf_url(self):
        c = ArxivCollector()
        assert c.can_handle("https://arxiv.org/pdf/2301.00001") is True

    def test_arxiv_notation(self):
        c = ArxivCollector()
        assert c.can_handle("arxiv:2301.00001") is True

    def test_negative_generic_url(self):
        c = ArxivCollector()
        assert c.can_handle("https://example.com/page") is False

    def test_negative_youtube(self):
        c = ArxivCollector()
        assert c.can_handle("https://youtube.com/watch?v=abc") is False


class TestExtractId:
    def test_abs_url(self):
        assert extract_arxiv_id("https://arxiv.org/abs/2301.00001") == "2301.00001"

    def test_pdf_url(self):
        assert extract_arxiv_id("https://arxiv.org/pdf/2301.00001") == "2301.00001"

    def test_with_version(self):
        assert extract_arxiv_id("https://arxiv.org/abs/2301.00001v2") == "2301.00001"

    def test_arxiv_notation(self):
        assert extract_arxiv_id("arxiv:2301.00001") == "2301.00001"

    def test_invalid_url(self):
        assert extract_arxiv_id("https://example.com") is None

    def test_five_digit_id(self):
        assert extract_arxiv_id("https://arxiv.org/abs/2301.12345") == "2301.12345"


class TestParseAtomResponse:
    def test_basic_parse(self):
        c = ArxivCollector()
        result = c._parse_atom_response(
            "https://arxiv.org/abs/2301.00001",
            "2301.00001",
            SAMPLE_ATOM_XML,
        )
        assert result.success is True
        assert result.title == "Attention Is All You Need"
        assert "attention mechanisms" in result.content.lower()

    def test_authors_extracted(self):
        c = ArxivCollector()
        result = c._parse_atom_response(
            "https://arxiv.org/abs/2301.00001",
            "2301.00001",
            SAMPLE_ATOM_XML,
        )
        assert "Alice Smith" in result.extra["authors"]
        assert "Bob Jones" in result.extra["authors"]
        assert len(result.extra["authors"]) == 3

    def test_categories_in_tags(self):
        c = ArxivCollector()
        result = c._parse_atom_response(
            "https://arxiv.org/abs/2301.00001",
            "2301.00001",
            SAMPLE_ATOM_XML,
        )
        assert "cs.CL" in result.tags
        assert "cs.AI" in result.tags

    def test_extra_fields(self):
        c = ArxivCollector()
        result = c._parse_atom_response(
            "https://arxiv.org/abs/2301.00001",
            "2301.00001",
            SAMPLE_ATOM_XML,
        )
        assert result.extra["arxiv_id"] == "2301.00001"
        assert result.extra["pdf_url"] == "https://arxiv.org/pdf/2301.00001v1"
        assert result.extra["published"] == "2023-01-01T00:00:00Z"
        assert result.extra["categories"] == ["cs.CL", "cs.AI"]

    def test_confidence_flags(self):
        c = ArxivCollector()
        result = c._parse_atom_response(
            "https://arxiv.org/abs/2301.00001",
            "2301.00001",
            SAMPLE_ATOM_XML,
        )
        assert "arxiv_api" in result.confidence_flags
        assert "structured_metadata" in result.confidence_flags

    def test_authors_truncated(self):
        """More than 10 authors should be truncated with 'et al.' note."""
        authors_xml = "".join(
            f"<author><name>Author {i}</name></author>" for i in range(15)
        )
        xml = SAMPLE_ATOM_MANY_AUTHORS.format(authors=authors_xml)
        c = ArxivCollector()
        result = c._parse_atom_response(
            "https://arxiv.org/abs/2301.00002",
            "2301.00002",
            xml,
        )
        assert len(result.extra["authors"]) == 11  # 10 + "et al. (15 total)"
        assert "et al." in result.extra["authors"][-1]

    def test_invalid_xml(self):
        c = ArxivCollector()
        result = c._parse_atom_response(
            "https://arxiv.org/abs/2301.00001",
            "2301.00001",
            "not xml at all",
        )
        assert result.success is False

    def test_no_entry(self):
        xml = '<?xml version="1.0"?><feed xmlns="http://www.w3.org/2005/Atom"></feed>'
        c = ArxivCollector()
        result = c._parse_atom_response(
            "https://arxiv.org/abs/9999.99999",
            "9999.99999",
            xml,
        )
        assert result.success is False
