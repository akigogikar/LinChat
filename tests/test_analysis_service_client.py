import types
import asyncio
import pytest

import app.analysis_service_client as client

class DummyResponse:
    def __init__(self):
        self.headers = {"Chart": "img"}
    def raise_for_status(self):
        pass
    def json(self):
        return [{"col": "A"}]

class DummyClient:
    def __init__(self, called):
        self.called = called
    async def __aenter__(self):
        return self
    async def __aexit__(self, exc_type, exc, tb):
        pass
    async def post(self, url, files=None):
        self.called["url"] = url
        self.called["filename"] = list(files.values())[0].name
        return DummyResponse()

def test_analyze_file(monkeypatch, tmp_path):
    called = {}
    monkeypatch.setattr(client, "httpx", types.SimpleNamespace(AsyncClient=lambda: DummyClient(called)))
    f = tmp_path / "x.txt"
    f.write_text("data")
    data, chart = asyncio.run(client.analyze_file(str(f)))
    assert data == [{"col": "A"}]
    assert chart == "img"
    assert called["url"].endswith("/analysis")
    assert called["filename"].endswith("x.txt")
