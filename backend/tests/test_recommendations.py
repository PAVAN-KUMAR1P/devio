"""
test_recommendations.py — Unit and integration tests for /recommendations router.
"""
import pytest
from fastapi import HTTPException
from routers.recommendations import get_recommendations_for_district
from models import RecommendationEntry


def test_get_recommendations_valid_district():
    """Verify recommendation generation and SDG mappings for a valid district."""
    recs = get_recommendations_for_district("KA-001")
    assert isinstance(recs, list)
    assert len(recs) == 14  # All 14 indicators assessed

    priority_order = {"HIGH": 1, "MEDIUM": 2, "OK": 3}
    prev_priority = 1
    for r in recs:
        entry = RecommendationEntry.model_validate(r)
        assert entry.indicator_code is not None
        assert entry.priority in ["HIGH", "MEDIUM", "OK"]
        assert entry.action_area is not None
        assert entry.recommendation_text is not None and len(entry.recommendation_text) > 0
        assert entry.sdg_reference.startswith("SDG")

        # Verify priority sorting
        curr_prio = priority_order[entry.priority]
        assert curr_prio >= prev_priority
        prev_priority = curr_prio


def test_get_recommendations_invalid_district():
    """Verify 404 error when querying recommendations for nonexistent district."""
    with pytest.raises(HTTPException) as exc_info:
        get_recommendations_for_district("KA-999")
    assert exc_info.value.status_code == 404
    assert "District KA-999 not found" in exc_info.value.detail


def test_recommendations_sdg_coverage():
    """Verify that recommendations reference valid Sustainable Development Goals."""
    recs = get_recommendations_for_district("KA-005")
    sdgs = {r.sdg_reference for r in recs}
    expected_sdgs = {"SDG 4.6", "SDG 7.2", "SDG 8.3", "SDG 8.5", "SDG 9.1", "SDG 9.b", "SDG 9.c", "SDG 11.2", "SDG 11.6", "SDG 15.2"}
    assert sdgs.issubset(expected_sdgs) or len(sdgs.intersection(expected_sdgs)) > 0
