import os
import sqlite3
from typing import Iterable, Tuple

DB_FILE = os.path.join(os.path.dirname(__file__), "data.db")


def init_db() -> None:
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute(
        """CREATE TABLE IF NOT EXISTS documents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        filename TEXT
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
    conn.commit()
    conn.close()


def add_document(filename: str) -> int:
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("INSERT INTO documents (filename) VALUES (?)", (filename,))
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
