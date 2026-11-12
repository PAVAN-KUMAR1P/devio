"""
conftest.py — Test configuration and fixtures for InfraSense backend test suite.
"""
import sys
import os
import pytest
import sqlite3

# Add backend directory to sys.path
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from database import DB_PATH, get_db


@pytest.fixture(scope="session")
def db_connection():
    """Provides a database connection for test verification."""
    assert os.path.exists(DB_PATH), f"Database not found at {DB_PATH}"
    conn = get_db()
    yield conn
    conn.close()


@pytest.fixture(scope="session")
def valid_district_ids():
    """Returns a list of all valid district IDs from the database."""
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT district_id FROM district_master ORDER BY district_id")
    ids = [r["district_id"] for r in cur.fetchall()]
    conn.close()
    return ids


@pytest.fixture(scope="session")
def valid_dimensions():
    """Returns the official 6 development dimensions."""
    return [
        "Infrastructure",
        "Digital Access",
        "Industry",
        "Innovation",
        "Energy & Environment",
        "Human Capital"
    ]
