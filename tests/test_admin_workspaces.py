import pytest
import sys
import types
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

from fastapi import HTTPException
from fastapi.security import HTTPBasicCredentials

from app import main
import app.config as config

class DummyTeam:
    _id = 0
    def __init__(self, name):
        DummyTeam._id += 1
        self.id = DummyTeam._id
        self.name = name


class DummySession:
    def __init__(self):
        self.teams = []

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        pass

    def add(self, obj):
        self.teams.append(obj)

    async def commit(self):
        pass

    async def refresh(self, obj):
        pass

    async def get(self, *a, **kw):
        return None

    async def execute(self, *a, **kw):
        class Result:
            def scalars(self_inner):
                class Sc:
                    def all(self_inner2):
                        return self.teams
                return Sc()
        return Result()


@pytest.mark.asyncio
async def test_create_and_list_workspaces(monkeypatch):
    session = DummySession()
    monkeypatch.setattr(main, 'async_session_maker', lambda: session)
    monkeypatch.setattr(main, 'Team', DummyTeam)
    monkeypatch.setattr(main, '_require_admin', lambda credentials=None: True)

    res = await main.create_workspace(name='Test')
    assert res['name'] == 'Test'
    assert res['id'] == 1

    listing = await main.list_workspaces()
    assert listing['workspaces'] == [{'id': 1, 'name': 'Test'}]


def test_require_admin(monkeypatch):
    monkeypatch.setattr(config, '_read_config', lambda: {'admin_username': 'admin', 'admin_password': 'secret'})
    creds = HTTPBasicCredentials(username='admin', password='secret')
    assert main._require_admin(creds) is True


def test_require_admin_bad(monkeypatch):
    monkeypatch.setattr(config, '_read_config', lambda: {'admin_username': 'admin', 'admin_password': 'secret'})
    creds = HTTPBasicCredentials(username='user', password='wrong')
    with pytest.raises(HTTPException):
        main._require_admin(creds)
