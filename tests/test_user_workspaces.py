import types
import sys
import pytest

# stub modules like in other tests
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
auth_stub.fastapi_users = types.SimpleNamespace(
    get_auth_router=lambda *a, **k: router,
    get_register_router=lambda *a, **k: router,
    get_users_router=lambda *a, **k: router,
    current_user=lambda active=True: lambda: None,
    on_after_register=lambda cb: None,
    on_after_login=lambda cb: None,
)
auth_stub.auth_backend = None
auth_stub.UserCreate = object
auth_stub.UserRead = object
auth_stub.UserUpdate = object
auth_stub.current_active_user = lambda: None
sys.modules.setdefault('app.auth', auth_stub)

from fastapi.testclient import TestClient
from app.main import app, create_user_workspace, user_workspaces, current_active_user
from app import main

class DummyUser:
    def __init__(self, id=1, team_id=None):
        self.id = id
        self.team_id = team_id

class DummyTeam:
    id = None
    _id = 0
    def __init__(self, name):
        DummyTeam._id += 1
        self.id = DummyTeam._id
        self.name = name

class DummySession:
    def __init__(self, user):
        self.user = user
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

    async def get(self, model, id):
        if model is main.User and id == self.user.id:
            return self.user
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
async def test_create_and_list_user_workspace(monkeypatch):
    user = DummyUser()
    session = DummySession(user)
    monkeypatch.setattr(main, 'async_session_maker', lambda: session)
    monkeypatch.setattr(main, 'Team', DummyTeam)
    monkeypatch.setattr(main, 'User', DummyUser)
    monkeypatch.setattr(main, 'select', lambda *a, **k: types.SimpleNamespace(where=lambda *a, **k: None))

    res = await create_user_workspace(name='WS', user=user)
    assert res == {'id': 1, 'name': 'WS'}
    assert user.team_id == 1

    listing = await user_workspaces(user=user)
    assert listing == {'workspaces': [{'id': 1, 'name': 'WS'}]}


def test_upload_permissions(monkeypatch, tmp_path):
    user = DummyUser(team_id=1)
    called = {}
    monkeypatch.setattr(main, 'parse_file', lambda p: [{'page':1,'text':'x'}])
    def fake_add_doc(filename, owner_id=None, team_id=None, shared=False):
        called['owner'] = owner_id
        called['team'] = team_id
        return 5
    monkeypatch.setattr(main, 'add_document', fake_add_doc)
    monkeypatch.setattr(main, 'add_chunks', lambda *a, **k: None)
    monkeypatch.setattr(main, 'add_audit_log', lambda *a, **k: None)
    monkeypatch.setattr(main.vector_db, 'add_embeddings', lambda *a, **k: None)

    client = TestClient(app)
    app.dependency_overrides[current_active_user] = lambda: user
    f = tmp_path / 'f.txt'
    f.write_text('data')
    with open(f, 'rb') as fh:
        resp = client.post('/upload', files={'file': ('f.txt', fh, 'text/plain')}, data={'shared': 'false'})
    assert resp.status_code == 200
    assert resp.json()['document_id'] == 5
    assert called['team'] == 1
