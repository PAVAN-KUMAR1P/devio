"""
test_clusters.py — Unit and integration tests for /clusters router.
"""
import pytest
from fastapi import HTTPException
from routers.clusters import get_cluster_summary, get_cluster_districts
from models import ClusterSummaryEntry, ClusterDetail


def test_get_cluster_summary():
    """Verify cluster summary overview from latest K-Means run."""
    summary = get_cluster_summary()
    assert isinstance(summary, list)
    assert len(summary) == 3  # k=3 clusters

    total_districts = 0
    for cs in summary:
        entry = ClusterSummaryEntry.model_validate(cs)
        assert entry.algorithm == "K-Means"
        assert entry.district_count > 0
        assert entry.avg_centroid_dist is not None and entry.avg_centroid_dist >= 0
        assert len(entry.districts) > 0
        total_districts += entry.district_count

    assert total_districts == 31


@pytest.mark.parametrize("cluster_id", [0, 1, 2])
def test_get_cluster_districts_valid(cluster_id):
    """Verify listing districts within a valid cluster."""
    districts = get_cluster_districts(cluster_id)
    assert isinstance(districts, list)
    assert len(districts) > 0

    previous_score = 100.0
    for d in districts:
        entry = ClusterDetail.model_validate(d)
        assert entry.district_id.startswith("KA-")
        assert entry.distance_to_centroid is not None and entry.distance_to_centroid >= 0
        if entry.overall_score is not None:
            assert entry.overall_score <= previous_score + 1e-4
            previous_score = entry.overall_score


def test_get_cluster_districts_invalid_id():
    """Verify 404 status code when cluster ID does not exist."""
    with pytest.raises(HTTPException) as exc_info:
        get_cluster_districts(999)
    assert exc_info.value.status_code == 404
    assert "No districts found for cluster 999" in exc_info.value.detail
