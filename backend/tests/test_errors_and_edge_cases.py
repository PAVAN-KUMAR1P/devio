"""
test_errors_and_edge_cases.py — Edge case and error handling tests across routers.
"""
import pytest
from fastapi import HTTPException
from routers.districts import get_district_profile
from routers.recommendations import get_recommendations_for_district
from routers.clusters import get_cluster_districts
from routers.rankings import get_dimension_rankings
from routers.compare import compare_districts


@pytest.mark.parametrize("bad_id", ["", "   ", "KA-999", "INVALID", "KA-000", "BENGALURU"])
def test_invalid_district_ids(bad_id):
    """Verify consistent 404 response across district-lookup endpoints."""
    with pytest.raises(HTTPException) as exc_info:
        get_district_profile(bad_id)
    assert exc_info.value.status_code == 404

    with pytest.raises(HTTPException) as exc_info_reco:
        get_recommendations_for_district(bad_id)
    assert exc_info_reco.value.status_code == 404


@pytest.mark.parametrize("bad_dim", ["", "123", "Economy", "Health", "Education", "unknown"])
def test_invalid_dimensions(bad_dim):
    """Verify 400 error for non-standard dimension queries."""
    with pytest.raises(HTTPException) as exc_info:
        get_dimension_rankings(bad_dim)
    assert exc_info.value.status_code == 400
    assert "Invalid dimension" in exc_info.value.detail


@pytest.mark.parametrize("bad_cluster", [-1, 3, 4, 10, 999])
def test_invalid_cluster_ids(bad_cluster):
    """Verify 404 error for non-existent cluster labels."""
    with pytest.raises(HTTPException) as exc_info:
        get_cluster_districts(bad_cluster)
    assert exc_info.value.status_code == 404


@pytest.mark.parametrize("bad_compare_query", [
    "",
    "   ",
    "KA-001",
    "KA-001,",
    ",KA-001",
    "KA-001,   ",
    ",,,"
])
def test_malformed_compare_queries(bad_compare_query):
    """Verify 400 error for invalid comparison parameters."""
    with pytest.raises(HTTPException) as exc_info:
        compare_districts(bad_compare_query)
    assert exc_info.value.status_code in [400, 404]
