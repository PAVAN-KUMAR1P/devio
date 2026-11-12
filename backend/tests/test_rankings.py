"""
test_rankings.py — Unit and integration tests for /rankings router.
"""
import pytest
from fastapi import HTTPException
from routers.rankings import get_overall_rankings, get_dimension_rankings
from models import RankingEntry, DimensionRankingEntry


def test_get_overall_rankings():
    """Verify overall composite rankings across all 31 districts."""
    rankings = get_overall_rankings()
    assert isinstance(rankings, list)
    assert len(rankings) == 31

    previous_score = 100.0
    for idx, r in enumerate(rankings):
        entry = RankingEntry.model_validate(r)
        assert entry.district_rank == idx + 1
        assert entry.overall_score <= previous_score + 1e-4
        assert entry.weight_coverage == 1.0
        assert entry.is_valid == 1
        previous_score = entry.overall_score

    # Check top and bottom known districts from SQLite baseline
    assert rankings[0]["district_name"] == "Bengaluru Urban"
    assert rankings[-1]["district_name"] == "Udupi"


def test_get_dimension_rankings_all_valid(valid_dimensions):
    """Verify dimension-specific rankings for all 6 dimensions."""
    for dim in valid_dimensions:
        dim_rankings = get_dimension_rankings(dim)
        assert len(dim_rankings) == 31
        for idx, dr in enumerate(dim_rankings):
            entry = DimensionRankingEntry.model_validate(dr)
            assert entry.dimension == dim
            assert entry.dim_rank == idx + 1
            assert 0 <= entry.dimension_score <= 100


def test_get_dimension_rankings_case_insensitive():
    """Verify case-insensitivity in dimension query parameter."""
    lower_res = get_dimension_rankings("infrastructure")
    upper_res = get_dimension_rankings("INFRASTRUCTURE")
    mixed_res = get_dimension_rankings("Infrastructure")
    assert lower_res == upper_res == mixed_res


def test_get_dimension_rankings_invalid_dimension():
    """Verify 400 status code when an invalid dimension is passed."""
    with pytest.raises(HTTPException) as exc_info:
        get_dimension_rankings("NonExistentDimension")
    assert exc_info.value.status_code == 400
    assert "Invalid dimension 'NonExistentDimension'" in exc_info.value.detail
