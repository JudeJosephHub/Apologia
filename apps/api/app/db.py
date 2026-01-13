import sqlite3
from typing import Generator

from .config import DB_PATH


def init_db() -> None:
    """Initialize SQLite schema for storing sermons."""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS sermons (
                id TEXT PRIMARY KEY,
                sermon_name TEXT NOT NULL,
                series_name TEXT,
                week_or_date TEXT,
                pastor_name TEXT,
                status TEXT NOT NULL,
                file_path TEXT NOT NULL,
                original_filename TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_sermons_created_at ON sermons(created_at DESC)"
        )
        conn.commit()
    finally:
        conn.close()


def get_db() -> Generator[sqlite3.Connection, None, None]:
    """FastAPI dependency that yields a SQLite connection per request."""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()
