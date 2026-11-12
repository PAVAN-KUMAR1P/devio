"""
test_districts.py — Unit and integration tests for /districts router.
"""
import pytest
from fastapi import HTTPException
from routers.districts import get_all_districts, get_district_profile
from models import DistrictSummary, DistrictProfile


def test_get_all_districts(valid_district_ids):
    """Verify listing all 31 districts with proper attributes."""
    districts = get_all_districts()
    assert isinstance(districts, list)
    assert len(districts) == 31
    assert len(districts) == len(valid_district_ids)

    # Validate against Pydantic schema
    for d in districts:
        model = DistrictSummary.model_validate(d)
        assert model.district_id.startswith("KA-")
        assert len(model.district_name) > 0
        assert model.area_km2 is not None and model.area_km2 > 0
        assert model.population is not None and model.population > 0

    # Verify alphabetical ordering
    names = [d["district_name"] for d in districts]
    assert names == sorted(names)


@pytest.mark.parametrize("district_id", ["KA-001", "KA-005", "KA-031"])
def test_get_district_profile_valid(district_id):
    """Verify detailed profile retrieval for sample districts."""
    profile = get_district_profile(district_id)
    assert isinstance(profile, DistrictProfile)
    assert profile.district_id == district_id
    assert profile.overall_score is not None
    assert 0 <= profile.overall_score <= 100
    assert profile.overall_rank is not None and 1 <= profile.overall_rank <= 31

    # Check 6 dimension scores
    assert len(profile.dimension_scores) == 6
    for ds in profile.dimension_scores:
        assert 0 <= ds.score <= 100

    # Check 14 normalized indicator scores
    assert len(profile.normalized_scores) == 14
    for ns in profile.normalized_scores:
        assert 0 <= ns.normalized_score <= 100


def test_get_district_profile_invalid_id():
    """Verify 404 raised for nonexistent district ID."""
    with pytest.raises(HTTPException) as exc_info:
        get_district_profile("KA-999")
    assert exc_info.value.status_code == 404
    assert "District KA-999 not found" in exc_info.value.detail
