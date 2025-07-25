import os
from typing import Iterable, List, Dict

from chromadb import PersistentClient
from chromadb.config import Settings
import openai
from . import config

DB_DIR = os.getenv(
    "LINCHAT_VECTOR_DIR",
    os.path.join(os.path.dirname(__file__), "chroma"),
)
COLLECTION_NAME = "documents"

_client = None
_collection = None



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


EMBEDDING_MODEL = os.getenv("OPENROUTER_EMBED_MODEL", "openai/text-embedding-ada-002")


def _embed(texts: List[str]) -> List[List[float]]:
    """Return vector embeddings from the external API."""
    openai.api_key = config._get_api_key()
    openai.base_url = "https://openrouter.ai/api/v1"
    response = openai.Embedding.create(model=EMBEDDING_MODEL, input=texts)
    return [d["embedding"] for d in response["data"]]


def add_embeddings(
    document_id: int, chunks: Iterable[Dict], workspace_id: int | None = None
) -> None:
    """Embed and store document chunks in the vector database."""
    collection = _get_collection()
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
        metadata.append(
            {"document_id": document_id, "page": page, "workspace_id": workspace_id}
        )
    if not texts:
        return
    embeddings = _embed(texts)
    collection.add(documents=texts, embeddings=embeddings, ids=ids, metadatas=metadata)


def add_web_embeddings(url: str, text: str, workspace_id: int | None = None) -> None:
    """Embed and store web page text with URL metadata."""
    collection = _get_collection()
    embedding = _embed([text])
    collection.add(
        documents=[text],
        embeddings=embedding,
        ids=[url],
        metadatas=[{"url": url, "workspace_id": workspace_id}],
    )


def query(
    text: str,
    top_k: int = 5,
    allowed_ids: Iterable[int] | None = None,
    workspace_id: int | None = None,
) -> List[Dict]:
    """Return the most relevant chunks for the given text query."""
    collection = _get_collection()
    query_emb = _embed([text])

    fetch_k = max(top_k * 5, top_k)
    results = collection.query(query_embeddings=query_emb, n_results=fetch_k)
    out: List[Dict] = []
    for chunk_id, doc, meta in zip(
        results["ids"][0], results["documents"][0], results["metadatas"][0]
    ):
        doc_id = meta.get("document_id")
        if doc_id is not None and allowed_ids is not None and doc_id not in allowed_ids:
            continue
        if workspace_id is not None and meta.get("workspace_id") not in (None, workspace_id):
            continue
        out.append({
            "id": chunk_id,
            "text": doc,
            "document_id": doc_id,
            "page": meta.get("page"),
            "url": meta.get("url"),
        })
        if len(out) >= top_k:
            break
    return out


def get_context(
    prompt: str,
    top_k: int = 5,
    allowed_ids: Iterable[int] | None = None,
    workspace_id: int | None = None,
) -> tuple[str, List[Dict]]:
    """Return concatenated context and source metadata for LLM retrieval."""
    chunks = query(prompt, top_k=top_k, allowed_ids=allowed_ids, workspace_id=workspace_id)
    lines: List[str] = []
    sources: List[Dict] = []
    offset = 0
    for idx, c in enumerate(chunks, start=1):
        if c.get("url"):
            prefix = f"(URL {c['url']})"
        else:
            prefix = f"(Doc {c['document_id']} page {c['page']})"
        line = f"[{idx}] {prefix} {c['text']}"
        lines.append(line)
        sources.append(
            {
                "id": str(idx),
                "chunk_id": c["id"],
                "document_id": c.get("document_id"),
                "page": c.get("page"),
                "url": c.get("url"),
                "text": c["text"],
                "offset_start": offset,
                "offset_end": offset + len(line),
            }
        )
        offset += len(line) + 2  # account for join newline spacing

    context = "\n\n".join(lines)
    return context, sources


def delete_document(document_id: int) -> None:
    """Remove all embeddings for a document."""
    collection = _get_collection()
    collection.delete(where={"document_id": document_id})
