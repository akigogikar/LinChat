import os
import sqlite3
from typing import Iterable, Tuple, List, Optional
from datetime import datetime

DB_FILE = os.getenv(
    "LINCHAT_DB_FILE",
    os.path.join(os.path.dirname(__file__), "data.db"),
)


def init_db() -> None:
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute(
        """CREATE TABLE IF NOT EXISTS documents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        filename TEXT,
        owner_id INTEGER,
        team_id INTEGER,
        is_shared INTEGER DEFAULT 0
    )"""
    )
    cur.execute(
        """CREATE TABLE IF NOT EXISTS chunks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        document_id INTEGER,
        page INTEGER,
        text TEXT,
        FOREIGN KEY(document_id) REFERENCES documents(id)
    )"""
    )
    cur.execute(
        """CREATE TABLE IF NOT EXISTS audit_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        action TEXT,
        timestamp TEXT
    )"""
    )
    conn.commit()
    conn.close()


def add_document(
    filename: str,
    owner_id: Optional[int] = None,
    team_id: Optional[int] = None,
    shared: bool = False,
) -> int:
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO documents (filename, owner_id, team_id, is_shared) VALUES (?, ?, ?, ?)",
        (filename, owner_id, team_id, int(shared)),
    )
    doc_id = cur.lastrowid
    conn.commit()
    conn.close()
    return doc_id


def add_chunks(document_id: int, chunks: Iterable[Tuple[int, str]]) -> None:
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.executemany(
        "INSERT INTO chunks (document_id, page, text) VALUES (?, ?, ?)",
        [(document_id, page, text) for page, text in chunks],
    )
    conn.commit()
    conn.close()


def add_audit_log(user_id: int, action: str) -> None:
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO audit_logs (user_id, action, timestamp) VALUES (?, ?, ?)",
        (user_id, action, datetime.utcnow().isoformat()),
    )
    conn.commit()
    conn.close()


def list_documents(user_id: int, team_id: Optional[int]) -> List[Tuple[int, str]]:
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute(
        "SELECT id, filename FROM documents WHERE owner_id=?"
        " OR (team_id=? AND is_shared=1)",
        (user_id, team_id),
    )
    rows = cur.fetchall()
    conn.close()
    return rows


def allowed_document_ids(user_id: int, team_id: Optional[int]) -> List[int]:
    """Return document IDs accessible to the given user."""
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    try:
        cur.execute(
            "SELECT id FROM documents WHERE owner_id=? OR (team_id=? AND is_shared=1)",
            (user_id, team_id),
        )
        rows = [r[0] for r in cur.fetchall()]
    except sqlite3.OperationalError:
        rows = []
    finally:
        conn.close()
    return rows
