"""Tests for XHS media Referer injection utility."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from datapulse.core.media import (
    build_media_headers,
    build_referer,
    download_media,
    needs_referer,
)


class TestNeedsReferer:
    def test_xhscdn_domain(self):
        assert needs_referer("https://sns-img-qc.xhscdn.com/photo.jpg") is True

    def test_ci_xiaohongshu(self):
        assert needs_referer("https://ci.xiaohongshu.com/image/abc.png") is True

    def test_subdomain_of_xhscdn(self):
        assert needs_referer("https://deep.sub.xhscdn.com/video.mp4") is True

    def test_non_xhs_domain(self):
        assert needs_referer("https://cdn.example.com/image.jpg") is False

    def test_empty_url(self):
        assert needs_referer("") is False


class TestBuildReferer:
    def test_basic_referer(self):
        ref = build_referer("https://sns-img-qc.xhscdn.com/photo/abc.jpg?token=x")
        assert ref == "https://sns-img-qc.xhscdn.com/"

    def test_http_scheme(self):
        ref = build_referer("http://ci.xiaohongshu.com/img.png")
        assert ref == "http://ci.xiaohongshu.com/"


class TestBuildMediaHeaders:
    def test_xhs_url_includes_referer(self):
        headers = build_media_headers("https://sns-img-qc.xhscdn.com/photo.jpg")
        assert "Referer" in headers
        assert "User-Agent" in headers

    def test_non_xhs_url_no_referer(self):
        headers = build_media_headers("https://cdn.example.com/photo.jpg")
        assert "Referer" not in headers
        assert "User-Agent" in headers


class TestDownloadMedia:
    def test_successful_download(self):
        mock_resp = MagicMock()
        mock_resp.iter_content.return_value = [b"chunk1", b"chunk2"]
        mock_resp.raise_for_status.return_value = None

        with patch("datapulse.core.media.requests.get", return_value=mock_resp):
            data = download_media("https://sns-img-qc.xhscdn.com/photo.jpg")
            assert data == b"chunk1chunk2"

    def test_exceeds_max_bytes(self):
        mock_resp = MagicMock()
        mock_resp.iter_content.return_value = [b"x" * 1024] * 20
        mock_resp.raise_for_status.return_value = None

        with patch("datapulse.core.media.requests.get", return_value=mock_resp):
            data = download_media(
                "https://sns-img-qc.xhscdn.com/photo.jpg",
                max_bytes=10000,
            )
            assert data is None

    def test_request_failure_returns_none(self):
        import requests as req_lib

        with patch(
            "datapulse.core.media.requests.get",
            side_effect=req_lib.ConnectionError("fail"),
        ):
            data = download_media("https://sns-img-qc.xhscdn.com/photo.jpg")
            assert data is None
