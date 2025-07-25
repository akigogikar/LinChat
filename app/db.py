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


def list_documents(
    user_id: int, team_id: Optional[int]
) -> List[Tuple[int, str, Optional[str], int]]:
    """Return document metadata including owner email."""
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute(
        "SELECT d.id, d.filename, u.email, d.is_shared"
        " FROM documents d LEFT JOIN users u ON d.owner_id = u.id"
        " WHERE d.owner_id=? OR (d.team_id=? AND d.is_shared=1)",
        (user_id, team_id),
    )
    rows = cur.fetchall()
    conn.close()
    return rows


def get_document_filename(doc_id: int) -> Optional[str]:
    """Return stored filename for a document id."""
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("SELECT filename FROM documents WHERE id=?", (doc_id,))
    row = cur.fetchone()
    conn.close()
    if row:
        return row[0]
    return None


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


def delete_document(doc_id: int) -> None:
    """Remove a document and its chunks."""
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("DELETE FROM chunks WHERE document_id=?", (doc_id,))
    cur.execute("DELETE FROM documents WHERE id=?", (doc_id,))
    conn.commit()
    conn.close()


def set_document_shared(doc_id: int, shared: bool) -> None:
    """Update the shared flag for a document."""
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("UPDATE documents SET is_shared=? WHERE id=?", (int(shared), doc_id))
    conn.commit()
    conn.close()
