#!/usr/bin/env python
"""Generate OpenAPI schema for LinChat."""
import json
import importlib
import types
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

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

main = importlib.import_module('app.main')
app = main.app
with open('docs/openapi.json', 'w') as f:
    json.dump(app.openapi(), f, indent=2)
print('OpenAPI spec written to docs/openapi.json')
