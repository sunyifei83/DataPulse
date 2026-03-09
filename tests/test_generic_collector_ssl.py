from __future__ import annotations

from datapulse.collectors.generic import GenericCollector


class _FakeResponse:
    url = "https://example.com"
    headers = {"Content-Type": "text/html; charset=utf-8"}
    encoding = "utf-8"
    apparent_encoding = "utf-8"

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def raise_for_status(self) -> None:
        return None

    def iter_content(self, chunk_size: int = 8192):
        yield b"<html><body>Hello</body></html>"


class _FakeSession:
    def __init__(self, response: _FakeResponse):
        self.response = response
        self.calls: list[dict[str, object]] = []
        self.closed = False

    def get(self, *args, **kwargs):
        self.calls.append(kwargs)
        return self.response

    def close(self) -> None:
        self.closed = True


class _FakeSSLContext:
    def __init__(self):
        self.default_loaded = False
        self.loaded_cafiles: list[str] = []

    def load_default_certs(self) -> None:
        self.default_loaded = True

    def load_verify_locations(self, *, cafile: str) -> None:
        self.loaded_cafiles.append(cafile)


def test_build_ssl_context_loads_default_and_requests_bundle(monkeypatch):
    fake_context = _FakeSSLContext()

    monkeypatch.setattr("datapulse.collectors.generic.ssl.create_default_context", lambda: fake_context)
    monkeypatch.setattr("datapulse.collectors.generic.certifi.where", lambda: "/tmp/requests-ca.pem")
    monkeypatch.setattr("datapulse.collectors.generic.os.path.exists", lambda path: path == "/tmp/requests-ca.pem")

    context = GenericCollector()._build_ssl_context()

    assert context is fake_context
    assert fake_context.default_loaded is True
    assert fake_context.loaded_cafiles == ["/tmp/requests-ca.pem"]


def test_build_ssl_context_honors_datapulse_ca_bundle_override(monkeypatch):
    fake_context = _FakeSSLContext()

    monkeypatch.setenv("DATAPULSE_CA_BUNDLE", "/tmp/custom-ca.pem")
    monkeypatch.setattr("datapulse.collectors.generic.ssl.create_default_context", lambda: fake_context)
    monkeypatch.setattr("datapulse.collectors.generic.certifi.where", lambda: "/tmp/requests-ca.pem")
    monkeypatch.setattr(
        "datapulse.collectors.generic.os.path.exists",
        lambda path: path in {"/tmp/requests-ca.pem", "/tmp/custom-ca.pem"},
    )

    GenericCollector()._build_ssl_context()

    assert fake_context.loaded_cafiles == ["/tmp/requests-ca.pem", "/tmp/custom-ca.pem"]


def test_fetch_html_uses_built_session(monkeypatch):
    fake_session = _FakeSession(_FakeResponse())

    monkeypatch.setattr("datapulse.collectors.generic.GenericCollector._build_http_session", lambda self: fake_session)

    html = GenericCollector()._fetch_html("https://example.com")

    assert "Hello" in html
    assert fake_session.calls
    assert fake_session.closed is True
