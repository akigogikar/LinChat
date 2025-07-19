import sys
import types
play_mod = types.ModuleType('playwright')
fake_async = types.ModuleType('playwright.async_api')
fake_async.async_playwright = lambda: None
play_mod.async_api = fake_async
sys.modules.setdefault('playwright', play_mod)
sys.modules.setdefault('playwright.async_api', fake_async)
sys.modules.setdefault('chromadb', types.SimpleNamespace(PersistentClient=object))
sys.modules.setdefault('chromadb.config', types.SimpleNamespace(Settings=object))
sys.modules.setdefault('sentence_transformers', types.SimpleNamespace(SentenceTransformer=lambda x: None))
import pytest
from app.scraper import service
from app import vector_db


def test_extract_text():
    html = "<html><body><script>bad</script><table><tr><td>A</td></tr></table><p>Hi</p></body></html>"
    text = service._extract_text(html)
    assert "A" in text and "Hi" in text


@pytest.mark.asyncio
async def test_scrape_url(monkeypatch):
    async def fake_fetch(url):
        return "<html><body><p>Hello</p></body></html>"
    called = {}
    def fake_add(url, text, workspace_id=None):
        called["url"] = url
        called["text"] = text
        called["workspace_id"] = workspace_id
    monkeypatch.setattr(service, "_fetch_html", fake_fetch)
    monkeypatch.setattr(vector_db, "add_web_embeddings", fake_add)
    text = await service.scrape_url("http://example.com", workspace_id=1)
    assert text == "Hello"
    assert called["url"] == "http://example.com"
    assert called["workspace_id"] == 1


@pytest.mark.asyncio
async def test_scrape_search(monkeypatch):
    def fake_get(url, params=None):
        class Resp:
            text = '<a class="result__a" href="http://example.com">x</a>'
            def raise_for_status(self):
                pass
        return Resp()
    async def fake_scrape_url(url, workspace_id=None):
        assert workspace_id == 2
        return "content"
    import types as _types
    monkeypatch.setitem(sys.modules, 'httpx', _types.SimpleNamespace(get=fake_get))
    monkeypatch.setattr(service, "scrape_url", fake_scrape_url)
    urls = await service.scrape_search("query", max_results=1, workspace_id=2)
    assert urls == ["http://example.com"]
