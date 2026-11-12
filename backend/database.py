"""
database.py — SQLite connection helper for InfraSense backend.
Opens a fresh connection per request with row_factory=sqlite3.Row.
"""
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "InfraSense_Production.db")


def get_db() -> sqlite3.Connection:
    """Return a SQLite connection with row_factory set to sqlite3.Row."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def rows_to_dicts(rows) -> list:
    """Convert a list of sqlite3.Row objects to plain dicts."""
    return [dict(r) for r in rows]
