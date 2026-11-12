"""
routers/indicators.py — Indicator endpoints for InfraSense API.
"""
from fastapi import APIRouter
from typing import List
from database import get_db, rows_to_dicts
from models import IndicatorInfo, IndicatorStats

router = APIRouter(prefix="/indicators", tags=["indicators"])


@router.get("", response_model=List[IndicatorInfo])
def list_indicators():
    """List all 14 indicators with metadata (code, name, dimension, direction, unit)."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT indicator_code, indicator_name, dimension, direction, unit
        FROM indicator_master
        ORDER BY dimension, indicator_code
    """)
    rows = cursor.fetchall()
    conn.close()
    return rows_to_dicts(rows)


@router.get("/stats", response_model=List[IndicatorStats])
def get_indicator_stats():
    """Return descriptive statistics for all 14 indicators."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT indicator_name, dimension, direction, n,
               mean_value, min_value, max_value, range_value, cv_pct
        FROM indicator_descriptive_stats
        ORDER BY dimension, indicator_name
    """)
    rows = cursor.fetchall()
    conn.close()
    return rows_to_dicts(rows)
