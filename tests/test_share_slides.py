import types
import pytest
import sys
sys.modules.setdefault('pandas', types.ModuleType('pandas'))
play_mod = types.ModuleType('playwright')
fake_async = types.ModuleType('playwright.async_api')
fake_async.async_playwright = lambda: None
play_mod.async_api = fake_async
sys.modules.setdefault('playwright', play_mod)
sys.modules.setdefault('playwright.async_api', fake_async)
sys.modules.setdefault('chromadb', types.SimpleNamespace(PersistentClient=object))
sys.modules.setdefault('chromadb.config', types.SimpleNamespace(Settings=object))
sys.modules.setdefault('sentence_transformers', types.SimpleNamespace(SentenceTransformer=lambda x: None))
weasy = types.ModuleType('weasyprint')
weasy.HTML = object
sys.modules.setdefault('weasyprint', weasy)
sys.modules.setdefault('markdown', types.ModuleType('markdown'))
auth_stub = types.ModuleType('app.auth')
class RouterStub:
    def __init__(self):
        self.routes = []
        self.on_startup = []
        self.on_shutdown = []
        self.lifespan_context = None

router = RouterStub()
auth_stub.fastapi_users = types.SimpleNamespace(get_auth_router=lambda *a, **k: router,
                                                get_register_router=lambda *a, **k: router,
                                                get_users_router=lambda *a, **k: router,
                                                current_user=lambda active=True: lambda: None,
                                                on_after_register=lambda cb: None,
                                                on_after_login=lambda cb: None)
auth_stub.auth_backend = None
auth_stub.UserCreate = object
auth_stub.UserRead = object
auth_stub.UserUpdate = object
auth_stub.current_active_user = lambda: None
sys.modules.setdefault('app.auth', auth_stub)
sys.modules.setdefault('chromadb', types.SimpleNamespace(PersistentClient=object))
sys.modules.setdefault('chromadb.config', types.SimpleNamespace(Settings=object))
sys.modules.setdefault('sentence_transformers', types.SimpleNamespace(SentenceTransformer=lambda x: None))

from app import main

class User:
    id = 1
    team_id = 1


@pytest.mark.asyncio
async def test_share_document(monkeypatch):
    monkeypatch.setattr(main, 'allowed_document_ids', lambda uid, tid: [1])
    called = {}
    def fake_share(doc_id, shared):
        called['args'] = (doc_id, shared)
    monkeypatch.setattr(main, 'set_document_shared', fake_share)
    monkeypatch.setattr(main, 'add_audit_log', lambda *a, **k: None)

    res = await main.share_document(1, True, user=User())
    assert res == {'id': 1, 'is_shared': True}
    assert called['args'] == (1, True)


@pytest.mark.asyncio
async def test_generate_slides(monkeypatch):
    deck = types.SimpleNamespace(dict=lambda: {'slides': [{'title': 'T', 'bullets': ['b'], 'table': None}]})
    monkeypatch.setattr(main, 'generate_slide_deck', lambda prompt: deck)
    main.logger = types.SimpleNamespace(info=lambda *a, **k: None)
    monkeypatch.setattr(main, 'add_audit_log', lambda *a, **k: None)

    res = await main.slides('hi', user=User())
    assert res == {'slides': [{'title': 'T', 'bullets': ['b'], 'table': None}]}


