"""
routers/eda.py — Exploratory Data Analysis endpoints for InfraSense API.
"""
from fastapi import APIRouter
from typing import List
from database import get_db, rows_to_dicts
from models import EDADisparityEntry, EDAOutlierEntry, EDAUnevennessEntry

router = APIRouter(prefix="/eda", tags=["eda"])


@router.get("/disparity", response_model=List[EDADisparityEntry])
def get_regional_disparity():
    """Return indicators ranked by highest regional disparity (inter-district spread)."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT indicator_name, dimension, disparity_range, max_score, min_score
        FROM indicator_regional_disparity
        ORDER BY disparity_range DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    return rows_to_dicts(rows)


@router.get("/outliers", response_model=List[EDAOutlierEntry])
def get_indicator_outliers():
    """Return districts with indicator values differing by > 2 standard deviations from state mean."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT district_name, indicator_name, dimension,
               observed_value, indicator_mean, indicator_std, z_score, flag
        FROM indicator_outliers
        ORDER BY ABS(z_score) DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    return rows_to_dicts(rows)


@router.get("/unevenness", response_model=List[EDAUnevennessEntry])
def get_development_unevenness():
    """Return districts ranked by internal development imbalance (highest score range across dimensions)."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT district_name, score_range, avg_dim_score, dimensions_covered
        FROM development_unevenness
        ORDER BY score_range DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    return rows_to_dicts(rows)
