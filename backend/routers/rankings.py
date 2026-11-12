"""
routers/rankings.py — Ranking endpoints for InfraSense API.
"""
from fastapi import APIRouter, HTTPException
from typing import List
from database import get_db, rows_to_dicts
from models import RankingEntry, DimensionRankingEntry

router = APIRouter(prefix="/rankings", tags=["rankings"])


@router.get("/overall", response_model=List[RankingEntry])
def get_overall_rankings():
    """Return all 31 districts ranked by their composite overall development score."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT dm.district_id, dr.district_name, dr.overall_score,
               dr.district_rank, dr.weight_coverage, dr.is_valid
        FROM district_rankings dr
        JOIN district_master dm ON dm.district_name = dr.district_name
        ORDER BY dr.district_rank ASC
    """)
    rows = cursor.fetchall()
    conn.close()
    return rows_to_dicts(rows)


@router.get("/dimension/{dimension}", response_model=List[DimensionRankingEntry])
def get_dimension_rankings(dimension: str):
    """Return district rankings for a specific development dimension."""
    valid_dims = [
        "Infrastructure", "Digital Access", "Industry",
        "Innovation", "Energy & Environment", "Human Capital"
    ]
    # Case-insensitive match
    matched = None
    for d in valid_dims:
        if d.lower() == dimension.lower():
            matched = d
            break
    if not matched:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid dimension '{dimension}'. Valid options: {valid_dims}"
        )

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT district_name, dimension, dimension_score, dim_rank
        FROM dimension_rankings
        WHERE dimension = ?
        ORDER BY dim_rank ASC
    """, (matched,))
    rows = cursor.fetchall()
    conn.close()
    return rows_to_dicts(rows)
