"""Tests for Jina API client (read + search)."""

from __future__ import annotations

import os
from unittest.mock import MagicMock, patch

import pytest
import requests

from datapulse.core.jina_client import (
    JinaAPIClient,
    JinaReadOptions,
    JinaReadResult,
    JinaSearchOptions,
    JinaSearchResult,
)
from datapulse.core.retry import CircuitBreakerOpen


class TestJinaReadOptions:
    def test_defaults(self):
        opts = JinaReadOptions()
        assert opts.response_format == "markdown"
        assert opts.target_selector == ""
        assert opts.wait_for_selector == ""
        assert opts.no_cache is False
        assert opts.with_generated_alt is False
        assert opts.cookie == ""
        assert opts.use_post is False

    def test_custom_values(self):
        opts = JinaReadOptions(
            target_selector=".article",
            wait_for_selector="#content",
            no_cache=True,
            with_generated_alt=True,
            cookie="session=abc",
        )
        assert opts.target_selector == ".article"
        assert opts.wait_for_selector == "#content"
        assert opts.no_cache is True
        assert opts.with_generated_alt is True
        assert opts.cookie == "session=abc"


class TestJinaSearchOptions:
    def test_defaults(self):
        opts = JinaSearchOptions()
        assert opts.sites == []
        assert opts.limit == 5

    def test_custom(self):
        opts = JinaSearchOptions(sites=["python.org", "peps.python.org"], limit=10)
        assert opts.sites == ["python.org", "peps.python.org"]
        assert opts.limit == 10


class TestJinaAPIClientHeaders:
    """Test that headers are constructed correctly for read requests."""

    def _make_mock_response(self, text: str = "# Title\nContent here"):
        resp = MagicMock()
        resp.text = text
        resp.status_code = 200
        resp.raise_for_status = MagicMock()
        return resp

    def test_read_basic_headers(self):
        client = JinaAPIClient(api_key="test-key-123")
        with patch("datapulse.core.jina_client.requests.get") as mock_get:
            mock_get.return_value = self._make_mock_response()
            client.read("https://example.com")
            mock_get.assert_called_once()
            headers = mock_get.call_args[1]["headers"]
            assert headers["Authorization"] == "Bearer test-key-123"
            assert headers["X-Respond-With"] == "markdown"
            assert headers["Accept"] == "application/json"

    def test_read_with_target_selector(self):
        client = JinaAPIClient(api_key="k")
        opts = JinaReadOptions(target_selector=".main-article")
        with patch("datapulse.core.jina_client.requests.get") as mock_get:
            mock_get.return_value = self._make_mock_response()
            client.read("https://example.com", options=opts)
            headers = mock_get.call_args[1]["headers"]
            assert headers["X-Target-Selector"] == ".main-article"

    def test_read_with_wait_for_selector(self):
        client = JinaAPIClient(api_key="k")
        opts = JinaReadOptions(wait_for_selector="#loaded")
        with patch("datapulse.core.jina_client.requests.get") as mock_get:
            mock_get.return_value = self._make_mock_response()
            client.read("https://example.com", options=opts)
            headers = mock_get.call_args[1]["headers"]
            assert headers["X-Wait-For-Selector"] == "#loaded"

    def test_read_with_no_cache(self):
        client = JinaAPIClient(api_key="k")
        opts = JinaReadOptions(no_cache=True)
        with patch("datapulse.core.jina_client.requests.get") as mock_get:
            mock_get.return_value = self._make_mock_response()
            client.read("https://example.com", options=opts)
            headers = mock_get.call_args[1]["headers"]
            assert headers["X-No-Cache"] == "true"

    def test_read_with_generated_alt(self):
        client = JinaAPIClient(api_key="k")
        opts = JinaReadOptions(with_generated_alt=True)
        with patch("datapulse.core.jina_client.requests.get") as mock_get:
            mock_get.return_value = self._make_mock_response()
            client.read("https://example.com", options=opts)
            headers = mock_get.call_args[1]["headers"]
            assert headers["X-With-Generated-Alt"] == "true"

    def test_read_with_cookie(self):
        client = JinaAPIClient(api_key="k")
        opts = JinaReadOptions(cookie="session=xyz; token=abc")
        with patch("datapulse.core.jina_client.requests.get") as mock_get:
            mock_get.return_value = self._make_mock_response()
            client.read("https://example.com", options=opts)
            headers = mock_get.call_args[1]["headers"]
            assert headers["X-Set-Cookie"] == "session=xyz; token=abc"

    def test_read_with_proxy(self):
        client = JinaAPIClient(api_key="k", proxy_url="http://proxy:8080")
        with patch("datapulse.core.jina_client.requests.get") as mock_get:
            mock_get.return_value = self._make_mock_response()
            client.read("https://example.com")
            headers = mock_get.call_args[1]["headers"]
            assert headers["X-Proxy-URL"] == "http://proxy:8080"

    def test_read_no_optional_headers_when_empty(self):
        client = JinaAPIClient(api_key="k")
        with patch("datapulse.core.jina_client.requests.get") as mock_get:
            mock_get.return_value = self._make_mock_response()
            client.read("https://example.com")
            headers = mock_get.call_args[1]["headers"]
            assert "X-Target-Selector" not in headers
            assert "X-Wait-For-Selector" not in headers
            assert "X-No-Cache" not in headers
            assert "X-With-Generated-Alt" not in headers
            assert "X-Set-Cookie" not in headers
            assert "X-Proxy-URL" not in headers

    def test_read_post_method_for_spa(self):
        client = JinaAPIClient(api_key="k")
        opts = JinaReadOptions(use_post=True)
        with patch("datapulse.core.jina_client.requests.post") as mock_post:
            mock_post.return_value = self._make_mock_response()
            client.read("https://example.com/#/route", options=opts)
            mock_post.assert_called_once()
            assert mock_post.call_args[1]["json"]["url"] == "https://example.com/#/route"

    def test_read_url_construction(self):
        client = JinaAPIClient(api_key="k")
        with patch("datapulse.core.jina_client.requests.get") as mock_get:
            mock_get.return_value = self._make_mock_response()
            client.read("https://example.com/page")
            url = mock_get.call_args[0][0]
            assert url == "https://r.jina.ai/https://example.com/page"


class TestJinaAPIClientReadResult:
    def test_read_returns_result(self):
        client = JinaAPIClient(api_key="k")
        with patch("datapulse.core.jina_client.requests.get") as mock_get:
            resp = MagicMock()
            resp.text = "# Page Title\n\nThis is the content of the page."
            resp.status_code = 200
            resp.raise_for_status = MagicMock()
            mock_get.return_value = resp
            result = client.read("https://example.com")
            assert isinstance(result, JinaReadResult)
            assert result.url == "https://example.com"
            assert result.content == "# Page Title\n\nThis is the content of the page."
            assert result.status_code == 200

    def test_read_failure_raises(self):
        client = JinaAPIClient(api_key="k")
        with patch("datapulse.core.jina_client.requests.get") as mock_get:
            mock_get.side_effect = requests.RequestException("timeout")
            with pytest.raises(requests.RequestException):
                client.read("https://example.com")


class TestJinaAPIClientSearch:
    def _search_response(self, text: str):
        resp = MagicMock()
        resp.text = text
        resp.status_code = 200
        resp.raise_for_status = MagicMock()
        return resp

    def test_search_basic(self):
        client = JinaAPIClient(api_key="k")
        md = (
            "Title: Result One\n"
            "URL Source: https://example.com/one\n"
            "Description: First result description.\n\n"
            "Markdown Content:\nSome content here.\n\n"
            "---\n\n"
            "Title: Result Two\n"
            "URL Source: https://example.com/two\n"
            "Description: Second result description.\n\n"
            "Markdown Content:\nMore content here.\n"
        )
        with patch("datapulse.core.jina_client.requests.get") as mock_get:
            mock_get.return_value = self._search_response(md)
            results = client.search("test query")
            assert len(results) == 2
            assert isinstance(results[0], JinaSearchResult)
            assert results[0].title == "Result One"
            assert results[0].url == "https://example.com/one"
            assert results[0].description == "First result description."
            assert "Some content here." in results[0].content
            assert results[1].title == "Result Two"

    def test_search_url_construction(self):
        client = JinaAPIClient(api_key="k")
        with patch("datapulse.core.jina_client.requests.get") as mock_get:
            mock_get.return_value = self._search_response("")
            client.search("LLM inference")
            url = mock_get.call_args[0][0]
            assert url == "https://s.jina.ai/LLM inference"

    def test_search_with_site_restriction(self):
        client = JinaAPIClient(api_key="k")
        opts = JinaSearchOptions(sites=["python.org"])
        with patch("datapulse.core.jina_client.requests.get") as mock_get:
            mock_get.return_value = self._search_response("")
            client.search("async", options=opts)
            url = mock_get.call_args[0][0]
            assert "site:python.org" in url

    def test_search_with_multiple_sites(self):
        client = JinaAPIClient(api_key="k")
        opts = JinaSearchOptions(sites=["python.org", "peps.python.org"])
        with patch("datapulse.core.jina_client.requests.get") as mock_get:
            mock_get.return_value = self._search_response("")
            client.search("async", options=opts)
            url = mock_get.call_args[0][0]
            assert "site:python.org" in url
            assert "site:peps.python.org" in url

    def test_search_no_api_key_raises(self):
        client = JinaAPIClient(api_key="")
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="API key"):
                client.search("test")

    def test_search_empty_response(self):
        client = JinaAPIClient(api_key="k")
        with patch("datapulse.core.jina_client.requests.get") as mock_get:
            mock_get.return_value = self._search_response("")
            results = client.search("nothing")
            assert results == []


class TestJinaAPIClientCircuitBreaker:
    def test_read_and_search_independent_breakers(self):
        """Read circuit opening should not affect search circuit."""
        client = JinaAPIClient(api_key="k")
        assert client._read_cb.state == "closed"
        assert client._search_cb.state == "closed"
        assert client._read_cb is not client._search_cb

    def test_read_circuit_opens_on_failures(self):
        client = JinaAPIClient(api_key="k")
        # Lower threshold for testing
        client._read_cb.failure_threshold = 2
        with patch("datapulse.core.jina_client.requests.get") as mock_get:
            mock_get.side_effect = requests.RequestException("down")
            for _ in range(2):
                with pytest.raises(requests.RequestException):
                    client.read("https://example.com")
        assert client._read_cb.state == "open"
        # Search should still be closed
        assert client._search_cb.state == "closed"

    def test_read_when_circuit_open_raises(self):
        client = JinaAPIClient(api_key="k")
        client._read_cb.failure_threshold = 1
        with patch("datapulse.core.jina_client.requests.get") as mock_get:
            mock_get.side_effect = requests.RequestException("down")
            with pytest.raises(requests.RequestException):
                client.read("https://example.com")
        # Now circuit is open — next call should raise CircuitBreakerOpen
        with pytest.raises(CircuitBreakerOpen):
            client.read("https://example.com")


class TestJinaAPIClientAPIKeyPriority:
    def test_constructor_key_takes_precedence(self):
        with patch.dict(os.environ, {"JINA_API_KEY": "env-key"}):
            client = JinaAPIClient(api_key="explicit-key")
            assert client.api_key == "explicit-key"

    def test_env_var_fallback(self):
        with patch.dict(os.environ, {"JINA_API_KEY": "env-key"}):
            client = JinaAPIClient()
            assert client.api_key == "env-key"

    def test_no_key_is_empty(self):
        with patch.dict(os.environ, {}, clear=True):
            # Remove JINA_API_KEY if present
            os.environ.pop("JINA_API_KEY", None)
            client = JinaAPIClient()
            assert client.api_key == ""

    def test_no_auth_header_without_key(self):
        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop("JINA_API_KEY", None)
            client = JinaAPIClient()
            with patch("datapulse.core.jina_client.requests.get") as mock_get:
                resp = MagicMock()
                resp.text = "# Title\nContent"
                resp.status_code = 200
                resp.raise_for_status = MagicMock()
                mock_get.return_value = resp
                client.read("https://example.com")
                headers = mock_get.call_args[1]["headers"]
                assert "Authorization" not in headers
