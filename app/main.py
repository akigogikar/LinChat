from fastapi import FastAPI, Depends, HTTPException, Form, UploadFile, File
from fastapi.responses import HTMLResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from typing import List
import shutil
import uuid
import openai
import json
import os

from .db import init_db, add_document, add_chunks
from .ingest import parse_file
from . import vector_db
from .scraper import scrape_url, scrape_search

app = FastAPI()


@app.on_event("startup")
def _startup():
    """Initialize the database on startup."""
    init_db()
    vector_db._get_client()
security = HTTPBasic()

CONFIG_FILE = os.path.join(os.path.dirname(__file__), "config.json")


def _read_config():
    """Load configuration from file and environment variables."""
    conf = {}
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            conf.update(json.load(f))
    env_user = os.getenv("ADMIN_USERNAME")
    if env_user:
        conf.setdefault("admin_username", env_user)
    env_password = os.getenv("ADMIN_PASSWORD")
    if env_password:
        conf.setdefault("admin_password", env_password)
    env_key = os.getenv("OPENROUTER_API_KEY")
    if env_key:
        conf.setdefault("openrouter_api_key", env_key)
    return conf


def _write_config(conf: dict) -> None:
    """Persist configuration to disk."""
    with open(CONFIG_FILE, "w") as f:
        json.dump(conf, f)


def _get_api_key() -> str:
    conf = _read_config()
    key = conf.get("openrouter_api_key")
    if not key:
        raise HTTPException(status_code=500, detail="OpenRouter API key not configured")
    return key


def _require_admin(credentials: HTTPBasicCredentials = Depends(security)):
    conf = _read_config()
    username = conf.get("admin_username", "admin")
    password = conf.get("admin_password")
    if not password:
        raise HTTPException(status_code=500, detail="Admin password not configured")
    if credentials.username != username or credentials.password != password:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return True


@app.post("/query")
async def query_llm(prompt: str):
    """Query OpenRouter LLM with the given prompt."""
    openai.api_key = _get_api_key()
    openai.base_url = "https://openrouter.ai/api/v1"
    try:
        completion = openai.ChatCompletion.create(
            model="openai/gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
        )
        return {"response": completion.choices[0].message["content"]}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/search")
async def search_docs(query: str, top_k: int = 5):
    """Retrieve relevant document chunks from the vector DB."""
    results = vector_db.query(query, top_k=top_k)
    return {"results": results}


@app.post("/internal/scrape")
async def scrape_endpoint(url: str = None, query: str = None):
    """Scrape a URL directly or via search."""
    if not url and not query:
        raise HTTPException(status_code=400, detail="url or query required")
    if query and not url:
        scraped = await scrape_search(query, max_results=1)
        if not scraped:
            raise HTTPException(status_code=404, detail="No results")
        url = scraped[0]
    content = await scrape_url(url)
    if content is None:
        raise HTTPException(status_code=500, detail="Failed to scrape")
    return {"url": url, "length": len(content)}


@app.get("/admin", response_class=HTMLResponse)
def admin_page(auth: bool = Depends(_require_admin)):
    conf = _read_config()
    key = conf.get("openrouter_api_key", "")
    return HTMLResponse(
        f"""<html><body>
        <h1>Admin Config</h1>
        <form action='/admin/set_key' method='post'>
            <label>OpenRouter API Key:</label><br/>
            <input type='text' name='key' value='{key}'/><br/>
            <input type='submit' value='Save'/>
        </form>
        </body></html>"""
    )


@app.post("/admin/set_key")
def set_key(key: str = Form(...), auth: bool = Depends(_require_admin)):
    conf = _read_config()
    conf["openrouter_api_key"] = key
    _write_config(conf)
    return {"status": "saved"}


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """Accept a file upload, store it, parse and persist chunks."""
    os.makedirs("uploads", exist_ok=True)
    ext = os.path.splitext(file.filename)[1]
    doc_uuid = str(uuid.uuid4())
    stored_name = f"{doc_uuid}{ext}"
    save_path = os.path.join("uploads", stored_name)
    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Parse file into chunks
    parsed_chunks: List[dict] = parse_file(save_path)

    # Persist to database
    document_id = add_document(stored_name)
    add_chunks(document_id, [(c.get("page"), c.get("text")) for c in parsed_chunks])
    vector_db.add_embeddings(document_id, parsed_chunks)

    return {"document_id": document_id, "chunks": len(parsed_chunks)}
