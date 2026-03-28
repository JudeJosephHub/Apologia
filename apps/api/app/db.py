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
                church_name TEXT,
                youtube_url TEXT,
                youtube_video_id TEXT,
                youtube_channel_id TEXT,
                video_status TEXT NOT NULL DEFAULT 'pending_match',
                transcript_status TEXT NOT NULL DEFAULT 'none',
                status TEXT NOT NULL,
                file_path TEXT NOT NULL,
                original_filename TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS daily_inspiration (
                date_key TEXT PRIMARY KEY,
                kind TEXT NOT NULL,
                text TEXT NOT NULL,
                citation TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        existing_cols = {
            row[1] for row in conn.execute("PRAGMA table_info(sermons)").fetchall()
        }
        migrations = [
            ("church_name", "ALTER TABLE sermons ADD COLUMN church_name TEXT"),
            ("youtube_url", "ALTER TABLE sermons ADD COLUMN youtube_url TEXT"),
            ("youtube_video_id", "ALTER TABLE sermons ADD COLUMN youtube_video_id TEXT"),
            ("youtube_channel_id", "ALTER TABLE sermons ADD COLUMN youtube_channel_id TEXT"),
            (
                "video_status",
                "ALTER TABLE sermons ADD COLUMN video_status TEXT NOT NULL DEFAULT 'pending_match'",
            ),
            (
                "transcript_status",
                "ALTER TABLE sermons ADD COLUMN transcript_status TEXT NOT NULL DEFAULT 'none'",
            ),
        ]
        for col, ddl in migrations:
            if col not in existing_cols:
                conn.execute(ddl)
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_sermons_created_at ON sermons(created_at DESC)"
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_sermons_video_status ON sermons(video_status)"
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_daily_inspiration_created_at ON daily_inspiration(created_at DESC)"
        )
        conn.commit()
    finally:
        conn.close()


def get_db() -> Generator[sqlite3.Connection, None, None]:
    """FastAPI dependency that yields a SQLite connection per request."""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    try:
        yield conn
    finally:
        conn.close()
