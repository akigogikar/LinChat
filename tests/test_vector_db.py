import sys
import types

sys.modules.setdefault('chromadb', types.SimpleNamespace(PersistentClient=object))
sys.modules.setdefault('chromadb.config', types.SimpleNamespace(Settings=object))
sys.modules.setdefault('sentence_transformers', types.SimpleNamespace(SentenceTransformer=lambda x: None))

from app import vector_db

class DummyModel:
    class Emb(list):
        def tolist(self):
            return list(self)

    def encode(self, texts):
        return self.Emb([[len(t)] for t in texts])

class DummyCollection:
    def __init__(self):
        self.data = []

    def add(self, documents, embeddings, ids, metadatas):
        for d, e, i, m in zip(documents, embeddings, ids, metadatas):
            self.data.append({"doc": d, "embedding": e, "id": i, "meta": m})

    def query(self, query_embeddings, n_results):
        docs = [d["doc"] for d in self.data[:n_results]]
        ids = [d["id"] for d in self.data[:n_results]]
        metas = [d["meta"] for d in self.data[:n_results]]
        return {"documents": [docs], "ids": [ids], "metadatas": [metas]}


def test_add_and_query(monkeypatch):
    collection = DummyCollection()
    monkeypatch.setattr(vector_db, "_get_collection", lambda: collection)
    monkeypatch.setattr(vector_db, "_get_model", lambda: DummyModel())

    vector_db.add_embeddings(1, [{"page": 1, "text": "hello"}])
    res = vector_db.query("hello", top_k=1)
    assert res and res[0]["text"] == "hello"


def test_add_web_embeddings(monkeypatch):
    collection = DummyCollection()
    monkeypatch.setattr(vector_db, "_get_collection", lambda: collection)
    monkeypatch.setattr(vector_db, "_get_model", lambda: DummyModel())

    vector_db.add_web_embeddings("http://example.com", "web text")
    res = vector_db.query("web", top_k=1)
    assert res and res[0]["url"] == "http://example.com"
