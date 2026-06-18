"""
Database helpers — SQLAlchemy Core (Phase 6 upgrade).

Why SQLAlchemy Core instead of raw sqlite3?
  - Works with SQLite (local dev / tests) AND PostgreSQL (production)
    by just changing the DATABASE_URL environment variable.
  - Handles connection pooling, dialect differences, and parameter escaping.
  - No ORM magic — we still write plain SQL via text(), keeping things
    transparent and easy to read.

Environment variables (read at call time, not import time):
  DATABASE_URL  PostgreSQL connection string, e.g.:
                  postgresql://user:pass@host:5432/dbname
                If not set, falls back to SQLite via DB_PATH.
  DB_PATH       SQLite file path (default: ticketdesk.db in cwd).
                Ignored when DATABASE_URL is set.

To swap databases: just change DATABASE_URL. No code changes needed.
"""

from __future__ import annotations

import os
from contextlib import contextmanager

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Connection


# ---------------------------------------------------------------------------
# URL resolution
# ---------------------------------------------------------------------------

def get_database_url() -> str:
    """
    Build the SQLAlchemy connection URL at call time.

    Priority:
      1. DATABASE_URL env var  → PostgreSQL (production / Render)
      2. DB_PATH env var       → SQLite file at that path
      3. Default               → SQLite 'ticketdesk.db' in cwd
    """
    db_url = os.environ.get("DATABASE_URL")
    if db_url:
        # Render supplies postgres:// URLs; SQLAlchemy needs postgresql://
        return db_url.replace("postgres://", "postgresql://", 1)
    db_path = os.environ.get("DB_PATH", "ticketdesk.db")
    return f"sqlite:///{db_path}"


# ---------------------------------------------------------------------------
# DDL
# ---------------------------------------------------------------------------

def _create_table_sql(url: str) -> str:
    """
    Return the CREATE TABLE statement for the active database dialect.
    The only difference between SQLite and PostgreSQL is the primary-key type.
    """
    if url.startswith("postgresql"):
        # SERIAL auto-increments in PostgreSQL
        id_col = "BIGSERIAL PRIMARY KEY"
        # PostgreSQL stores timestamps as TIMESTAMPTZ (timezone-aware)
        ts_type = "TEXT"
    else:
        # INTEGER PRIMARY KEY is SQLite's auto-increment rowid alias
        id_col = "INTEGER PRIMARY KEY AUTOINCREMENT"
        ts_type = "TEXT"

    return f"""
    CREATE TABLE IF NOT EXISTS tickets (
        id          {id_col},
        title       TEXT  NOT NULL,
        description TEXT  NOT NULL DEFAULT '',
        requester   TEXT  NOT NULL,
        assignee    TEXT,
        priority    TEXT  NOT NULL DEFAULT 'medium',
        status      TEXT  NOT NULL DEFAULT 'open',
        created_at  {ts_type} NOT NULL,
        updated_at  {ts_type} NOT NULL
    )
    """


# ---------------------------------------------------------------------------
# Connection context manager
# ---------------------------------------------------------------------------

@contextmanager
def db_conn():
    """
    Context manager: open a connection → yield → commit (or rollback) → close.

    Usage:
        with db_conn() as conn:
            conn.execute(text("INSERT ..."), {"key": value})
        # auto-committed above; rolled back on any exception

    The engine is created fresh per call so that changing DATABASE_URL /
    DB_PATH between requests (e.g. in tests) always takes effect.
    For high-throughput production use, move the engine to module level
    and use a proper connection pool.
    """
    url = get_database_url()
    # echo=False keeps SQL out of logs; set True temporarily to debug queries
    engine = create_engine(url, echo=False)
    with engine.connect() as conn:
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
    engine.dispose()  # release pool resources


# ---------------------------------------------------------------------------
# Initialisation
# ---------------------------------------------------------------------------

def init_db() -> None:
    """Create the tickets table if it doesn't exist. Called once on startup."""
    url = get_database_url()
    engine = create_engine(url, echo=False)
    with engine.connect() as conn:
        conn.execute(text(_create_table_sql(url)))
        conn.commit()
    engine.dispose()
