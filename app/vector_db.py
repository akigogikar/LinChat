import os
from typing import Iterable, List, Dict

from chromadb import PersistentClient
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

DB_DIR = os.path.join(os.path.dirname(__file__), "chroma")
COLLECTION_NAME = "documents"

_client = None
_collection = None
_model = None

def _get_client() -> PersistentClient:
    """Return a persistent chroma client."""
    global _client
    if _client is None:
        os.makedirs(DB_DIR, exist_ok=True)
        _client = PersistentClient(path=DB_DIR, settings=Settings(anonymized_telemetry=False))
    return _client

def _get_collection():
    """Return the collection used for document embeddings."""
    global _collection
    if _collection is None:
        client = _get_client()
        _collection = client.get_or_create_collection(COLLECTION_NAME)
    return _collection

def _get_model() -> SentenceTransformer:
    """Load the sentence transformer model lazily."""
    global _model
    if _model is None:
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model

def add_embeddings(document_id: int, chunks: Iterable[Dict]) -> None:
    """Embed and store document chunks in the vector database."""
    collection = _get_collection()
    model = _get_model()
    texts: List[str] = []
    ids: List[str] = []
    metadata: List[Dict] = []
    for chunk in chunks:
        text = chunk.get("text")
        page = chunk.get("page")
        if not text:
            continue
        texts.append(text)
        ids.append(f"{document_id}_{page}")
        metadata.append({"document_id": document_id, "page": page})
    if not texts:
        return
    embeddings = model.encode(texts).tolist()
    collection.add(documents=texts, embeddings=embeddings, ids=ids, metadatas=metadata)

def query(text: str, top_k: int = 5) -> List[Dict]:
    """Return the most relevant chunks for the given text query."""
    collection = _get_collection()
    model = _get_model()
    query_emb = model.encode([text]).tolist()
    results = collection.query(query_embeddings=query_emb, n_results=top_k)
    out: List[Dict] = []
    for chunk_id, doc, meta in zip(results["ids"][0], results["documents"][0], results["metadatas"][0]):
        out.append({
            "id": chunk_id,
            "text": doc,
            "document_id": meta.get("document_id"),
            "page": meta.get("page"),
        })
    return out

def get_context(prompt: str, top_k: int = 5) -> str:
    """Return a concatenated text block for LLM context retrieval."""
    chunks = query(prompt, top_k=top_k)
    lines = [f"(Doc {c['document_id']} page {c['page']}) {c['text']}" for c in chunks]
    return "\n\n".join(lines)
