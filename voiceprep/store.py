"""Local SQLite storage for practice sessions.

Sessions live in a single SQLite file (default ``~/.voiceprep/sessions.db``)
so progress can be tracked over time without any account or network.
"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path

DEFAULT_DB_PATH = Path.home() / ".voiceprep" / "sessions.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question_id TEXT NOT NULL,
    category TEXT NOT NULL,
    transcript TEXT NOT NULL,
    seconds REAL,
    word_count INTEGER NOT NULL,
    filler_count INTEGER NOT NULL,
    filler_rate REAL NOT NULL,
    wpm REAL,
    star_score REAL NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
"""


@dataclass(frozen=True)
class Session:
    id: int
    question_id: str
    category: str
    transcript: str
    seconds: float | None
    word_count: int
    filler_count: int
    filler_rate: float
    wpm: float | None
    star_score: float
    created_at: str


def connect(db_path: str | Path = DEFAULT_DB_PATH) -> sqlite3.Connection:
    """Open the database, creating the file and schema if needed."""
    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.execute(SCHEMA)
    conn.commit()
    return conn


def save_session(
    conn: sqlite3.Connection,
    *,
    question_id: str,
    category: str,
    transcript: str,
    seconds: float | None,
    word_count: int,
    filler_count: int,
    filler_rate: float,
    wpm: float | None,
    star_score: float,
) -> int:
    """Insert one analyzed session and return its row id."""
    cursor = conn.execute(
        """
        INSERT INTO sessions
            (question_id, category, transcript, seconds, word_count,
             filler_count, filler_rate, wpm, star_score)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            question_id,
            category,
            transcript,
            seconds,
            word_count,
            filler_count,
            filler_rate,
            wpm,
            star_score,
        ),
    )
    conn.commit()
    return cursor.lastrowid


def list_sessions(conn: sqlite3.Connection, limit: int = 20) -> list[Session]:
    """Return the most recent sessions, newest first."""
    rows = conn.execute(
        """
        SELECT id, question_id, category, transcript, seconds, word_count,
               filler_count, filler_rate, wpm, star_score, created_at
        FROM sessions ORDER BY id DESC LIMIT ?
        """,
        (limit,),
    ).fetchall()
    return [Session(*row) for row in rows]


def summary(conn: sqlite3.Connection) -> dict[str, float | int]:
    """Aggregate stats across all sessions (zeros when empty)."""
    row = conn.execute(
        """
        SELECT COUNT(*),
               COALESCE(AVG(filler_rate), 0),
               COALESCE(AVG(wpm), 0),
               COALESCE(AVG(star_score), 0),
               COALESCE(AVG(word_count), 0)
        FROM sessions
        """
    ).fetchone()
    count, avg_filler_rate, avg_wpm, avg_star, avg_words = row
    return {
        "sessions": count,
        "avg_filler_rate": round(avg_filler_rate, 1),
        "avg_wpm": round(avg_wpm, 1),
        "avg_star_score": round(avg_star, 2),
        "avg_word_count": round(avg_words, 1),
    }
