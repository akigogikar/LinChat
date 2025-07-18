from fastapi import FastAPI, Depends, HTTPException, Form, UploadFile, File
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from typing import List, Optional
import shutil
import uuid
import openai
import pandas as pd
import json
import os
import re
import logging
import asyncio
import time

from .logging_setup import setup_logging

from .db import (
    init_db,
    add_document,
    add_chunks,
    list_documents,
    add_audit_log,
    allowed_document_ids,
)
from .ingest import parse_file
from . import vector_db
from .scraper import scrape_url, scrape_search
from .analysis_agent import run_custom_analysis
from .reporting import (
    generate_summary,
    generate_table,
    generate_slide_deck,
    markdown_to_pdf,
    html_to_pdf,
    dataframe_to_excel,
    slide_deck_to_pptx,
    Table as TableSchema,
    SlideDeck,
)
from .auth import (
    fastapi_users,
    auth_backend,
    UserCreate,
    UserRead,
    UserUpdate,
    current_active_user,
)
from .database import async_session_maker
from .models import User, AuditLog
from sqlalchemy import select

app = FastAPI()
app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth/jwt",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["users"],
)

# In-memory store of citation metadata keyed by request ID
# Each entry stores a timestamp and a mapping of citation IDs to metadata
CITATION_STORE: dict[str, dict] = {}

# Expiration for citation entries in seconds
CITATION_TTL = int(os.getenv("CITATION_TTL", "3600"))
# How often to check for expired citations
CITATION_CLEANUP_INTERVAL = int(os.getenv("CITATION_CLEANUP_INTERVAL", "60"))

setup_logging()
logger = logging.getLogger(__name__)


async def _cleanup_citations() -> None:
    """Background task to purge expired citation entries."""
    while True:
        await asyncio.sleep(CITATION_CLEANUP_INTERVAL)
        now = time.time()
        expired = [
            req_id
            for req_id, data in list(CITATION_STORE.items())
            if now - data.get("timestamp", 0) > CITATION_TTL
        ]
        for req_id in expired:
            CITATION_STORE.pop(req_id, None)


def _log_action(user_id: int, action: str) -> None:
    """Record an audit log entry and write to the logger."""
    logger.info("user %s %s", user_id, action)
    add_audit_log(user_id, action)


def _insert_links(text: str, req_id: str) -> str:
    """Replace [id] citations with clickable links."""
    def repl(match: re.Match) -> str:
        cid = match.group(1)
        return f"<a href='/source/{req_id}/{cid}'>[{cid}]</a>"

    return re.sub(r"\[(\d+)\]", repl, text)


@app.on_event("startup")
async def _startup():
    """Initialize the database on startup."""
    logger.info("Starting LinChat in %s environment", ENV)
    init_db()
    vector_db._get_client()
    from .database import engine, Base

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    asyncio.create_task(_cleanup_citations())


security = HTTPBasic()

CONFIG_DIR = os.path.dirname(__file__)
ENV = os.getenv("LINCHAT_ENV", "development")
CONFIG_FILE = os.path.join(CONFIG_DIR, f"config.{ENV}.json")
DEFAULT_CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")


def _read_config():
    """Load configuration from file and environment variables."""
    conf = {}
    config_path = CONFIG_FILE if os.path.exists(CONFIG_FILE) else DEFAULT_CONFIG_FILE
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
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
    env_model = os.getenv("OPENROUTER_MODEL")
    if env_model:
        conf.setdefault("openrouter_model", env_model)
    return conf


def _write_config(conf: dict) -> None:
    """Persist configuration to disk."""
    with open(CONFIG_FILE, "w") as f:
        json.dump(conf, f, indent=2)


def _get_api_key() -> str:
    conf = _read_config()
    key = conf.get("openrouter_api_key")
    if not key:
        raise HTTPException(status_code=500, detail="OpenRouter API key not configured")
    return key


def _get_model() -> str:
    conf = _read_config()
    return conf.get("openrouter_model", "openai/gpt-3.5-turbo")


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
async def query_llm(
    prompt: str,
    url: Optional[str] = None,
    search: Optional[str] = None,
    top_k: int = 5,
    user=Depends(current_active_user),
):
    """Query OpenRouter LLM with context retrieval and optional web scraping."""
    openai.api_key = _get_api_key()
    openai.base_url = "https://openrouter.ai/api/v1"

    request_id = str(uuid.uuid4())
    allowed_ids = allowed_document_ids(user.id, user.team_id)
    try:
        context, sources = vector_db.get_context(prompt, top_k=top_k, allowed_ids=allowed_ids)
    except TypeError:
        # fallback for older implementations during tests
        context, sources = vector_db.get_context(prompt, top_k=top_k)

    scraped_text = ""
    if search and not url:
        urls = await scrape_search(search, max_results=1)
        if not urls:
            raise HTTPException(status_code=404, detail="No search results")
        url = urls[0]
    if url:
        scraped_text = await scrape_url(url) or ""

    prefix = f"Question: {prompt}\n\nContext:\n"
    # update source offsets relative to full user message
    for src in sources:
        src["offset_start"] += len(prefix)
        src["offset_end"] += len(prefix)

    CITATION_STORE[request_id] = {
        "timestamp": time.time(),
        "entries": {src["id"]: src for src in sources},
    }

    user_content = f"{prefix}{context}\n\nScraped:\n{scraped_text}"

    messages = [
        {
            "role": "system",
            "content": "Use the provided context and scraped text to answer the user question. Cite sources using [id] notation.",
        },
        {"role": "user", "content": user_content},
    ]

    try:
        completion = openai.ChatCompletion.create(
            model=_get_model(),
            messages=messages,
        )
        raw = completion.choices[0].message["content"]
        response_text = _insert_links(raw, request_id)
        _log_action(user.id, "query_llm")
        return {"response": response_text, "request_id": request_id}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/search")
async def search_docs(query: str, top_k: int = 5, user=Depends(current_active_user)):
    """Retrieve relevant document chunks from the vector DB."""
    allowed_ids = allowed_document_ids(user.id, user.team_id)
    try:
        results = vector_db.query(query, top_k=top_k, allowed_ids=allowed_ids)
    except TypeError:
        results = vector_db.query(query, top_k=top_k)
    _log_action(user.id, "search")
    return {"results": results}


@app.get("/source/{req_id}/{cid}")
def get_source(req_id: str, cid: str, user=Depends(current_active_user)):
    """Return the stored source excerpt for a citation ID."""
    store = CITATION_STORE.get(req_id)
    if not store:
        raise HTTPException(status_code=404, detail="Citation not found")
    if time.time() - store.get("timestamp", 0) > CITATION_TTL:
        CITATION_STORE.pop(req_id, None)
        raise HTTPException(status_code=404, detail="Citation not found")
    info = store.get("entries", {}).get(cid)
    if not info:
        raise HTTPException(status_code=404, detail="Citation not found")
    _log_action(user.id, f"get_source:{cid}")
    return {
        "id": cid,
        "text": info.get("text"),
        "document_id": info.get("document_id"),
        "page": info.get("page"),
        "url": info.get("url"),
        "offset_start": info.get("offset_start"),
        "offset_end": info.get("offset_end"),
    }


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
async def admin_page(auth: bool = Depends(_require_admin)):
    conf = _read_config()
    key = conf.get("openrouter_api_key", "")
    model = conf.get("openrouter_model", _get_model())
    async with async_session_maker() as session:
        users = (await session.execute(select(User))).scalars().all()
        logs = (await session.execute(select(AuditLog).order_by(AuditLog.timestamp.desc()).limit(20))).scalars().all()
    user_rows = "".join(f"<li>{u.email}</li>" for u in users)
    log_rows = "".join(f"<li>{log.timestamp}: {log.user_id} - {log.action}</li>" for log in logs)
    return HTMLResponse(
        f"""<html><body>
        <h1>Admin Config</h1>
        <form action='/admin/set_key' method='post'>
            <label>OpenRouter API Key:</label><br/>
            <input type='text' name='key' value='{key}'/><br/>
            <label>Model:</label><br/>
            <input type='text' name='model' value='{model}'/><br/>
            <input type='submit' value='Save'/>
        </form>
        <h2>Users</h2>
        <ul>{user_rows}</ul>
        <h2>Audit Logs</h2>
        <ul>{log_rows}</ul>
        </body></html>"""
    )


@app.post("/admin/set_key")
def set_key(
    key: str = Form(...),
    model: str = Form(None),
    auth: bool = Depends(_require_admin),
):
    conf = _read_config()
    conf["openrouter_api_key"] = key
    if model:
        conf["openrouter_model"] = model
    _write_config(conf)
    return {"status": "saved"}


@app.get("/documents")
async def get_documents(user=Depends(current_active_user)):
    docs = list_documents(user.id, user.team_id)
    return {"documents": [{"id": d[0], "filename": d[1]} for d in docs]}


@app.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    shared: bool = Form(False),
    user=Depends(current_active_user),
):
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
    document_id = add_document(stored_name, owner_id=user.id, team_id=user.team_id, shared=shared)
    add_audit_log(user.id, f"upload:{stored_name}")
    add_chunks(document_id, [(c.get("page"), c.get("text")) for c in parsed_chunks])
    vector_db.add_embeddings(document_id, parsed_chunks)

    return {"document_id": document_id, "chunks": len(parsed_chunks)}


@app.post("/summarize")
async def summarize(prompt: str, user=Depends(current_active_user)):
    """Return a structured summary for the prompt."""
    summary = generate_summary(prompt)
    _log_action(user.id, "summarize")
    return summary.dict()


@app.post("/generate_table")
async def table(prompt: str, user=Depends(current_active_user)):
    """Generate a table structure from the LLM."""
    table = generate_table(prompt)
    _log_action(user.id, "generate_table")
    return table.dict()


@app.post("/generate_slides")
async def slides(prompt: str, user=Depends(current_active_user)):
    """Generate a slide deck structure from the LLM."""
    deck = generate_slide_deck(prompt)
    _log_action(user.id, "generate_slides")
    return deck.dict()


@app.post("/custom_analysis")
async def custom_analysis(
    prompt: str, file: UploadFile = File(...), user=Depends(current_active_user)
):
    """Generate Rust code via the LLM for custom analysis and return results."""
    os.makedirs("uploads", exist_ok=True)
    path = os.path.join("uploads", f"{uuid.uuid4()}_{file.filename}")
    with open(path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    result = run_custom_analysis(path, prompt)
    _log_action(user.id, "custom_analysis")
    return result


@app.post("/export/pdf")
def export_pdf(content: str, markdown: bool = True, user=Depends(current_active_user)):
    """Convert provided content to PDF and return the file."""
    os.makedirs("uploads", exist_ok=True)
    out_path = os.path.join("uploads", f"{uuid.uuid4()}.pdf")
    if markdown:
        markdown_to_pdf(content, out_path)
    else:
        html_to_pdf(content, out_path)
    _log_action(user.id, "export_pdf")
    return FileResponse(out_path, media_type="application/pdf", filename="output.pdf")


@app.post("/export/excel")
def export_excel(table: TableSchema, user=Depends(current_active_user)):
    """Export a table schema to an Excel file."""
    os.makedirs("uploads", exist_ok=True)
    out_path = os.path.join("uploads", f"{uuid.uuid4()}.xlsx")
    df = pd.DataFrame(table.rows, columns=table.columns)
    dataframe_to_excel(df, out_path)
    _log_action(user.id, "export_excel")
    return FileResponse(out_path, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", filename="output.xlsx")


@app.post("/export/pptx")
def export_pptx(deck: SlideDeck, user=Depends(current_active_user)):
    """Export slide deck JSON to a PPTX file."""
    os.makedirs("uploads", exist_ok=True)
    out_path = os.path.join("uploads", f"{uuid.uuid4()}.pptx")
    slide_deck_to_pptx(deck, out_path)
    _log_action(user.id, "export_pptx")
    return FileResponse(out_path, media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation", filename="output.pptx")
