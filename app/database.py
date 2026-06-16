"""
Database helpers — SQLite via the standard-library sqlite3 module.

get_db_path() reads DB_PATH from the environment at *call time*, not import
time, so tests can point at a tmp file and the Docker container can point at
a named volume without changing any code.

Swapping to PostgreSQL later:
  1. pip install psycopg2-binary
  2. Replace sqlite3.connect(path) with psycopg2.connect(DSN)
  3. AUTOINCREMENT -> SERIAL  |  TEXT -> VARCHAR / TIMESTAMPTZ
  4. Remove WAL pragma (Postgres handles concurrency internally)
"""

from __future__ import annotations

import os
import sqlite3
from contextlib import contextmanager

_CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS tickets (
    id          INTEGER  PRIMARY KEY AUTOINCREMENT,
    title       TEXT     NOT NULL,
    description TEXT     NOT NULL DEFAULT '',
    requester   TEXT     NOT NULL,
    assignee    TEXT,
    priority    TEXT     NOT NULL DEFAULT 'medium',
    status      TEXT     NOT NULL DEFAULT 'open',
    created_at  TEXT     NOT NULL,
    updated_at  TEXT     NOT NULL
);
"""


def get_db_path() -> str:
    """Return the database file path from the environment at call time."""
    return os.environ.get("DB_PATH", "ticketdesk.db")


def _open_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row        # rows behave like dicts
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA foreign_keys=ON;")
    return conn


@contextmanager
def db_conn():
    """
    Context manager: open → yield → commit (or rollback on error) → close.

    Usage:
        with db_conn() as conn:
            conn.execute("INSERT ...", values)
        # auto-committed above; rolled back on any exception
    """
    conn = _open_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db() -> None:
    """Create the tickets table if it does not exist. Called on startup."""
    with db_conn() as conn:
        conn.execute(_CREATE_TABLE)
