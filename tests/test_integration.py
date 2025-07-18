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
analysis_stub = types.ModuleType('analysis_agent')
analysis_stub.run_custom_analysis = lambda *a, **k: {}
sys.modules.setdefault('app.analysis_agent', analysis_stub)
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

from fastapi.testclient import TestClient
from app.main import app, current_active_user, CITATION_STORE
from app import main
import app.config as config

class User:
    id = 1
    team_id = 1

client = TestClient(app)
app.dependency_overrides[current_active_user] = lambda: User()


def test_upload_and_query(monkeypatch, tmp_path):
    def fake_parse(path):
        return [{"page": 1, "text": "hello"}]
    def fake_add_doc(filename, owner_id=None, team_id=None, shared=False):
        return 1
    def fake_add_chunks(doc_id, chunks):
        pass
    monkeypatch.setattr(main, "parse_file", fake_parse)
    monkeypatch.setattr(main, "add_document", fake_add_doc)
    monkeypatch.setattr(main, "add_chunks", fake_add_chunks)
    monkeypatch.setattr(main, "add_audit_log", lambda *a, **k: None)
    monkeypatch.setattr(config, "_get_api_key", lambda: "key")
    monkeypatch.setattr(config, "_get_model", lambda: "model")
    main.logger = types.SimpleNamespace(info=lambda *a, **k: None)
    monkeypatch.setattr(main.vector_db, "add_embeddings", lambda *args, **kw: None)
    # create simple file
    file_path = tmp_path / "test.txt"
    file_path.write_text("hello")
    with open(file_path, "rb") as f:
        resp = client.post("/upload", files={"file": ("test.txt", f, "text/plain")}, data={"shared": "false"})
    assert resp.status_code == 200
    assert resp.json()["document_id"] == 1

    monkeypatch.setattr(main.vector_db, "get_context", lambda prompt, top_k=5: ("ctx", []))
    class Resp:
        choices = [type("C", (), {"message": {"content": "answer"}})]
    def fake_create(**kwargs):
        return Resp()
    monkeypatch.setattr(main.openai.ChatCompletion, "create", fake_create)
    CITATION_STORE.clear()
    resp = client.post("/query", params={"prompt": "hi"})
    assert resp.status_code == 200
    assert resp.json()["response"] == "answer"
