"""
routers/clusters.py — Cluster endpoints for InfraSense API.
"""
from fastapi import APIRouter, HTTPException
from typing import List
from database import get_db, rows_to_dicts
from models import ClusterSummaryEntry, ClusterDetail

router = APIRouter(prefix="/clusters", tags=["clusters"])


@router.get("", response_model=List[ClusterSummaryEntry])
def get_cluster_summary():
    """Return summary of all clusters from the latest K-Means analysis run."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT ar.run_name, ar.algorithm, dc.cluster_label, dc.cluster_name,
               COUNT(dc.district_id) AS district_count,
               ROUND(AVG(dc.distance_to_centroid), 3) AS avg_centroid_dist,
               GROUP_CONCAT(dm.district_name, ', ') AS districts
        FROM district_clusters dc
        JOIN analysis_runs ar ON ar.run_id = dc.run_id
        JOIN district_master dm ON dm.district_id = dc.district_id
        WHERE ar.run_id = (SELECT MAX(run_id) FROM analysis_runs WHERE algorithm = 'K-Means')
        GROUP BY ar.run_id, dc.cluster_label
        ORDER BY dc.cluster_label ASC
    """)
    rows = cursor.fetchall()
    conn.close()
    return rows_to_dicts(rows)


@router.get("/{cluster_id}", response_model=List[ClusterDetail])
def get_cluster_districts(cluster_id: int):
    """Return all districts assigned to a given cluster label."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT dc.district_id, dm.district_name,
               ROUND(ds.score, 2) AS overall_score,
               ROUND(dc.distance_to_centroid, 3) AS distance_to_centroid
        FROM district_clusters dc
        JOIN district_master dm ON dm.district_id = dc.district_id
        JOIN analysis_runs ar ON ar.run_id = dc.run_id
        LEFT JOIN district_scores ds ON ds.district_id = dc.district_id AND ds.score_type = 'overall'
        WHERE dc.cluster_label = ?
          AND ar.run_id = (SELECT MAX(run_id) FROM analysis_runs WHERE algorithm = 'K-Means')
        ORDER BY ds.score DESC
    """, (cluster_id,))
    rows = cursor.fetchall()
    conn.close()
    if not rows:
        raise HTTPException(status_code=404, detail=f"No districts found for cluster {cluster_id}")
    return rows_to_dicts(rows)
