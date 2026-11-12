"""
routers/districts.py — District endpoints for InfraSense API.
"""
from fastapi import APIRouter, HTTPException
from typing import List
from database import get_db, rows_to_dicts
from models import DistrictSummary, DistrictProfile, DimensionScore, NormalizedScore

router = APIRouter(prefix="/districts", tags=["districts"])


@router.get("", response_model=List[DistrictSummary])
def get_all_districts():
    """List all 31 districts with basic master data."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT district_id, district_name, area_km2, population
        FROM district_master
        ORDER BY district_name ASC
    """)
    rows = cursor.fetchall()
    conn.close()
    return rows_to_dicts(rows)


@router.get("/{district_id}", response_model=DistrictProfile)
def get_district_profile(district_id: str):
    """Return full development profile for a single district."""
    conn = get_db()
    cursor = conn.cursor()

    # 1. District Master
    cursor.execute("""
        SELECT district_id, district_name, area_km2, population
        FROM district_master
        WHERE district_id = ?
    """, (district_id,))
    dist_row = cursor.fetchone()
    if not dist_row:
        conn.close()
        raise HTTPException(status_code=404, detail=f"District {district_id} not found")

    dist = dict(dist_row)

    # 2. Overall score & rank
    cursor.execute("""
        SELECT overall_score, district_rank
        FROM district_rankings
        WHERE district_name = ?
    """, (dist["district_name"],))
    rank_row = cursor.fetchone()
    overall_score = rank_row["overall_score"] if rank_row else None
    overall_rank = rank_row["district_rank"] if rank_row else None

    # 3. Cluster assignment (latest K-Means run)
    cursor.execute("""
        SELECT dc.cluster_label, dc.cluster_name
        FROM district_clusters dc
        JOIN analysis_runs ar ON ar.run_id = dc.run_id
        WHERE dc.district_id = ? AND ar.algorithm = 'K-Means'
        ORDER BY dc.run_id DESC LIMIT 1
    """, (district_id,))
    clust_row = cursor.fetchone()
    cluster_label = clust_row["cluster_label"] if clust_row else None
    cluster_name = clust_row["cluster_name"] if clust_row else None

    # 4. Dimension scores
    cursor.execute("""
        SELECT dimension, score
        FROM district_scores
        WHERE district_id = ? AND score_type = 'dimension'
        ORDER BY dimension ASC
    """, (district_id,))
    dim_rows = cursor.fetchall()
    dimension_scores = [DimensionScore(dimension=r["dimension"], score=round(r["score"], 2)) for r in dim_rows]

    # 5. Normalized scores
    cursor.execute("""
        SELECT indicator_code, normalized_score
        FROM normalized_indicators
        WHERE district_id = ?
        ORDER BY indicator_code ASC
    """, (district_id,))
    norm_rows = cursor.fetchall()
    normalized_scores = [NormalizedScore(indicator_code=r["indicator_code"], normalized_score=round(r["normalized_score"], 2)) for r in norm_rows]

    conn.close()

    return DistrictProfile(
        district_id=dist["district_id"],
        district_name=dist["district_name"],
        area_km2=dist["area_km2"],
        population=dist["population"],
        overall_score=round(overall_score, 2) if overall_score is not None else None,
        overall_rank=overall_rank,
        cluster_label=cluster_label,
        cluster_name=cluster_name,
        dimension_scores=dimension_scores,
        normalized_scores=normalized_scores,
    )
