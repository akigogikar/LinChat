from fastapi import FastAPI, Depends, HTTPException, Form, UploadFile, File
from fastapi.responses import FileResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from typing import List, Optional
import shutil
import uuid
import openai
import pandas as pd
import os
import re
import json
from . import config
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
    delete_document,
    set_document_shared,
)
from .ingest import parse_file
from . import vector_db
from .scraper import scrape_url, scrape_search
from .analysis_agent import run_custom_analysis
from .analysis_service_client import analyze_file
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
from .models import User, AuditLog, Team, ChatThread, ChatMessage
from sqlalchemy import select
import secrets

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
ENV = os.getenv("LINCHAT_ENV", "development")


def _require_admin(credentials: HTTPBasicCredentials = Depends(security)):
    conf = config._read_config()
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
    session_id: int | None = None,
    user=Depends(current_active_user),
):
    """Query OpenRouter LLM with context retrieval and optional web scraping."""
    openai.api_key = config._get_api_key()
    openai.base_url = "https://openrouter.ai/api/v1"

    request_id = str(uuid.uuid4())
    allowed_ids = allowed_document_ids(user.id, user.team_id)

    # create or validate chat session
    async with async_session_maker() as session:
        if session_id is None:
            thread = ChatThread(user_id=user.id, workspace_id=user.team_id)
            session.add(thread)
            await session.commit()
            await session.refresh(thread)
            session_id = thread.id
        else:
            thread = await session.get(ChatThread, session_id)
            if not thread:
                raise HTTPException(status_code=404, detail="Chat session not found")

        session.add(ChatMessage(thread_id=session_id, user_id=user.id, role="user", content=prompt))
        await session.commit()
    try:
        context, sources = vector_db.get_context(
            prompt, top_k=top_k, allowed_ids=allowed_ids, workspace_id=user.team_id
        )
    except TypeError:
        # fallback for older implementations during tests
        context, sources = vector_db.get_context(prompt, top_k=top_k)

    scraped_text = ""
    if search and not url:
        urls = await scrape_search(search, max_results=1, workspace_id=user.team_id)
        if not urls:
            raise HTTPException(status_code=404, detail="No search results")
        url = urls[0]
    if url:
        scraped_text = await scrape_url(url, workspace_id=user.team_id) or ""

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
            model=config._get_model(),
            messages=messages,
        )
        raw = completion.choices[0].message["content"]
        response_text = _insert_links(raw, request_id)
        async with async_session_maker() as session:
            session.add(
                ChatMessage(
                    thread_id=session_id,
                    user_id=user.id,
                    role="assistant",
                    content=raw,
                )
            )
            await session.commit()
        _log_action(user.id, "query_llm")
        return {"response": response_text, "request_id": request_id, "session_id": session_id}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/search")
async def search_docs(query: str, top_k: int = 5, user=Depends(current_active_user)):
    """Retrieve relevant document chunks from the vector DB."""
    allowed_ids = allowed_document_ids(user.id, user.team_id)
    try:
        results = vector_db.query(
            query, top_k=top_k, allowed_ids=allowed_ids, workspace_id=user.team_id
        )
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


@app.get("/admin/data")
async def admin_data(auth: bool = Depends(_require_admin)):
    conf = config._read_config()
    has_key = config.has_openrouter_key()
    model = conf.get("openrouter_model", config._get_model())
    async with async_session_maker() as session:
        users = (await session.execute(select(User))).scalars().all()
        teams = (await session.execute(select(Team))).scalars().all()
        logs = (
            await session.execute(
                select(AuditLog).order_by(AuditLog.timestamp.desc()).limit(20)
            )
        ).scalars().all()
    return {
        "has_key": has_key,
        "model": model,
        "users": [
            {"id": u.id, "email": u.email, "team_id": u.team_id} for u in users
        ],
        "workspaces": [{"id": t.id, "name": t.name} for t in teams],
        "logs": [
            {
                "id": log.id,
                "user_id": log.user_id,
                "action": log.action,
                "timestamp": log.timestamp.isoformat(),
            }
            for log in logs
        ],
    }


@app.post("/admin/set_key")
def set_key(
    key: str = Form(...),
    model: str = Form(None),
    auth: bool = Depends(_require_admin),
):
    config.set_openrouter_credentials(key, model)
    return {"status": "saved"}


@app.post("/admin/invite")
async def invite_user(
    email: str = Form(...),
    team_id: int | None = Form(None),
    auth: bool = Depends(_require_admin),
):
    """Create a new user with a temporary password."""
    password = secrets.token_hex(8)
    import hashlib
    async with async_session_maker() as session:
        user = User(
            email=email,
            hashed_password=hashlib.sha256(password.encode()).hexdigest(),
            team_id=team_id,
            is_active=True,
            is_superuser=False,
            is_verified=False,
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
    return {"id": user.id, "password": password}


@app.post("/admin/reset_password")
async def admin_reset_password(
    user_id: int = Form(...), auth: bool = Depends(_require_admin)
):
    """Reset a user's password and return the new one."""
    new_pw = secrets.token_hex(8)
    import hashlib
    async with async_session_maker() as session:
        user = await session.get(User, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        user.hashed_password = hashlib.sha256(new_pw.encode()).hexdigest()
        await session.commit()
    return {"status": "reset", "password": new_pw}


@app.get("/admin/workspaces")
async def list_workspaces(auth: bool = Depends(_require_admin)):
    async with async_session_maker() as session:
        teams = (await session.execute(select(Team))).scalars().all()
    return {"workspaces": [{"id": t.id, "name": t.name} for t in teams]}


@app.post("/admin/workspaces")
async def create_workspace(
    name: str = Form(...), auth: bool = Depends(_require_admin)
):
    async with async_session_maker() as session:
        team = Team(name=name)
        session.add(team)
        await session.commit()
        await session.refresh(team)
    return {"id": team.id, "name": team.name}


@app.get("/workspaces")
async def user_workspaces(user=Depends(current_active_user)):
    """Return all workspaces."""
    async with async_session_maker() as session:
        teams = (await session.execute(select(Team))).scalars().all()
    return {"workspaces": [{"id": t.id, "name": t.name} for t in teams]}


@app.post("/workspaces")
async def create_user_workspace(name: str = Form(...), user=Depends(current_active_user)):
    """Allow any user to create a new workspace."""
    async with async_session_maker() as session:
        team = Team(name=name)
        session.add(team)
        await session.commit()
        await session.refresh(team)
    return {"id": team.id, "name": team.name}


@app.post("/users/{user_id}/workspace")
async def assign_user_workspace(
    user_id: int, team_id: int = Form(...), auth: bool = Depends(_require_admin)
):
    """Assign a user to a workspace."""
    async with async_session_maker() as session:
        user_obj = await session.get(User, user_id)
        if not user_obj:
            raise HTTPException(status_code=404, detail="User not found")
        user_obj.team_id = team_id
        await session.commit()
    return {"status": "assigned"}


@app.delete("/admin/workspaces/{workspace_id}")
async def delete_workspace(workspace_id: int, auth: bool = Depends(_require_admin)):
    async with async_session_maker() as session:
        team = await session.get(Team, workspace_id)
        if team:
            await session.delete(team)
            await session.commit()
    return {"status": "deleted"}


@app.get("/documents")
async def get_documents(user=Depends(current_active_user)):
    docs = list_documents(user.id, user.team_id)
    return {
        "documents": [
            {"id": d[0], "filename": d[1], "is_shared": bool(d[2])} for d in docs
        ]
    }


@app.delete("/documents/{doc_id}")
async def remove_document(doc_id: int, user=Depends(current_active_user)):
    allowed = allowed_document_ids(user.id, user.team_id)
    if doc_id not in allowed:
        raise HTTPException(status_code=404, detail="Document not found")
    delete_document(doc_id)
    vector_db.delete_document(doc_id)
    _log_action(user.id, f"delete:{doc_id}")
    return {"status": "deleted"}


@app.post("/documents/{doc_id}/share")
async def share_document(doc_id: int, shared: bool, user=Depends(current_active_user)):
    allowed = allowed_document_ids(user.id, user.team_id)
    if doc_id not in allowed:
        raise HTTPException(status_code=404, detail="Document not found")
    set_document_shared(doc_id, shared)
    _log_action(user.id, f"share:{doc_id}:{shared}")
    return {"id": doc_id, "is_shared": shared}


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
    vector_db.add_embeddings(document_id, parsed_chunks, workspace_id=user.team_id)

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


@app.post("/analysis_llm")
async def analysis_llm(
    prompt: str, file: UploadFile = File(...), user=Depends(current_active_user)
):
    """Run the Rust analysis service and summarize results with the LLM."""
    os.makedirs("uploads", exist_ok=True)
    path = os.path.join("uploads", f"{uuid.uuid4()}_{file.filename}")
    with open(path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    stats, chart = await analyze_file(path)
    openai.api_key = config._get_api_key()
    openai.base_url = "https://openrouter.ai/api/v1"
    messages = [
        {
            "role": "system",
            "content": "Use the analysis results to answer the user question. Do not show any code.",
        },
        {"role": "user", "content": f"{prompt}\n\nData:\n{json.dumps(stats)}"},
    ]
    completion = openai.ChatCompletion.create(
        model=config._get_model(), messages=messages
    )
    answer = completion.choices[0].message["content"]
    _log_action(user.id, "analysis_llm")
    return {"answer": answer, "data": stats, "chart": chart}


@app.post("/chat/sessions")
async def create_chat_session(user=Depends(current_active_user)):
    async with async_session_maker() as session:
        thread = ChatThread(user_id=user.id, workspace_id=user.team_id)
        session.add(thread)
        await session.commit()
        await session.refresh(thread)
    return {"id": thread.id}


@app.get("/chat/{session_id}/export/pdf")
async def export_chat_pdf(session_id: int, user=Depends(current_active_user)):
    async with async_session_maker() as session:
        thread = await session.get(ChatThread, session_id)
        if not thread:
            raise HTTPException(status_code=404, detail="Chat session not found")
        messages = (
            await session.execute(
                select(ChatMessage)
                .where(ChatMessage.thread_id == session_id)
                .order_by(ChatMessage.timestamp)
            )
        ).scalars().all()
    lines = [
        f"**{'User' if m.role == 'user' else 'Assistant'}:** {m.content}"
        for m in messages
    ]
    transcript = "\n\n".join(lines)
    return export_pdf(transcript, markdown=True, user=user)


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
