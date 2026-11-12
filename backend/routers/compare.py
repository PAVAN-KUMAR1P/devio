"""
routers/compare.py — District comparison endpoint for InfraSense API.
"""
from fastapi import APIRouter, HTTPException, Query
from typing import List
from database import get_db
from models import CompareEntry

router = APIRouter(prefix="/compare", tags=["compare"])


@router.get("", response_model=List[CompareEntry])
def compare_districts(
    districts: str = Query(..., description="Comma-separated district IDs, e.g. KA-001,KA-005")
):
    """
    Side-by-side comparison of 2 to 5 districts across all 14 indicators
    and composite overall score.
    """
    id_list = [d.strip() for d in districts.split(",") if d.strip()]
    if len(id_list) < 2:
        raise HTTPException(
            status_code=400,
            detail="Provide at least 2 district IDs separated by commas (e.g. ?districts=KA-001,KA-005)"
        )
    if len(id_list) > 10:
        raise HTTPException(
            status_code=400,
            detail="Cannot compare more than 10 districts at once."
        )

    conn = get_db()
    cursor = conn.cursor()

    results = []
    for dist_id in id_list:
        # Master info
        cursor.execute("""
            SELECT district_id, district_name
            FROM district_master
            WHERE district_id = ?
        """, (dist_id,))
        m = cursor.fetchone()
        if not m:
            continue

        # Overall score
        cursor.execute("""
            SELECT score FROM district_scores
            WHERE district_id = ? AND score_type = 'overall'
        """, (dist_id,))
        sc = cursor.fetchone()
        overall = round(sc["score"], 2) if sc else None

        # 14 indicator scores
        cursor.execute("""
            SELECT indicator_code, normalized_score
            FROM normalized_indicators
            WHERE district_id = ?
            ORDER BY indicator_code
        """, (dist_id,))
        ind_rows = cursor.fetchall()
        ind_dict = {r["indicator_code"]: round(r["normalized_score"], 2) for r in ind_rows}

        results.append(CompareEntry(
            district_id=m["district_id"],
            district_name=m["district_name"],
            overall_score=overall,
            indicator_scores=ind_dict
        ))

    conn.close()

    if not results:
        raise HTTPException(status_code=404, detail="None of the specified districts were found.")

    return results
