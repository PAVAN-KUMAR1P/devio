"""
routers/recommendations.py — District recommendations endpoint for InfraSense API.
"""
from fastapi import APIRouter, HTTPException
from typing import List
from database import get_db
from models import RecommendationEntry

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


@router.get("/{district_id}", response_model=List[RecommendationEntry])
def get_recommendations_for_district(district_id: str):
    """
    Return prioritised policy and infrastructure recommendations for a given district.
    Queries district_recommendations table, falling back to computed weakest indicators
    if the table is empty or missing.
    """
    conn = get_db()
    cursor = conn.cursor()

    # Check if district exists
    cursor.execute("SELECT district_id, district_name FROM district_master WHERE district_id = ?", (district_id,))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail=f"District {district_id} not found")

    # Check if district_recommendations table exists and has rows for this district
    cursor.execute("""
        SELECT name FROM sqlite_master WHERE type='table' AND name='district_recommendations'
    """)
    table_exists = cursor.fetchone()

    rows = []
    if table_exists:
        cursor.execute("""
            SELECT indicator_code, priority_level, sdg_link, area,
                   recommendation, normalized_score
            FROM district_recommendations
            WHERE district_id = ?
            ORDER BY
                CASE priority_level
                    WHEN 'HIGH' THEN 1
                    WHEN 'MEDIUM' THEN 2
                    ELSE 3
                END ASC,
                normalized_score ASC
        """, (district_id,))
        db_rows = cursor.fetchall()
        for r in db_rows:
            rows.append(RecommendationEntry(
                indicator_code=r["indicator_code"],
                priority=r["priority_level"],
                sdg_reference=r["sdg_link"],
                action_area=r["area"],
                recommendation_text=r["recommendation"],
                normalized_score=round(r["normalized_score"], 2) if r["normalized_score"] is not None else None
            ))

    # Fallback if no recommendations stored
    if not rows:
        cursor.execute("""
            SELECT ni.indicator_code, ni.normalized_score, im.indicator_name, im.dimension
            FROM normalized_indicators ni
            JOIN indicator_master im ON im.indicator_code = ni.indicator_code
            WHERE ni.district_id = ?
            ORDER BY ni.normalized_score ASC
            LIMIT 5
        """, (district_id,))
        for r in cursor.fetchall():
            score = round(r["normalized_score"], 2)
            priority = "HIGH" if score < 40 else ("MEDIUM" if score < 60 else "OK")
            rows.append(RecommendationEntry(
                indicator_code=r["indicator_code"],
                priority=priority,
                sdg_reference="SDG 9 / Local Targets",
                action_area=r["dimension"],
                recommendation_text=f"Target improvement in {r['indicator_name']} (current score: {score}/100)",
                normalized_score=score
            ))

    conn.close()
    return rows
