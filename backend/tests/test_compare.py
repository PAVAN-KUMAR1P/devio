"""
test_compare.py — Unit and integration tests for /compare router.
"""
import pytest
from fastapi import HTTPException
from routers.compare import compare_districts
from models import CompareEntry


def test_compare_two_valid_districts():
    """Verify comparing 2 valid districts."""
    results = compare_districts("KA-001,KA-005")
    assert isinstance(results, list)
    assert len(results) == 2

    for item in results:
        entry = CompareEntry.model_validate(item)
        assert entry.district_id in ["KA-001", "KA-005"]
        assert entry.overall_score is not None
        assert len(entry.indicator_scores) == 14
        for code, val in entry.indicator_scores.items():
            assert 0 <= val <= 100


def test_compare_three_valid_districts():
    """Verify comparing 3 valid districts."""
    results = compare_districts("KA-001,KA-002,KA-003")
    assert len(results) == 3


def test_compare_fewer_than_two_districts():
    """Verify 400 error when fewer than 2 districts are supplied."""
    with pytest.raises(HTTPException) as exc_info:
        compare_districts("KA-001")
    assert exc_info.value.status_code == 400
    assert "Provide at least 2 district IDs" in exc_info.value.detail


def test_compare_more_than_ten_districts():
    """Verify 400 error when exceeding the 10-district limit."""
    ids = [f"KA-{str(i).zfill(3)}" for i in range(1, 13)]  # 12 districts
    query_str = ",".join(ids)
    with pytest.raises(HTTPException) as exc_info:
        compare_districts(query_str)
    assert exc_info.value.status_code == 400
    assert "Cannot compare more than 10 districts" in exc_info.value.detail


def test_compare_all_nonexistent_districts():
    """Verify 404 error when none of the requested districts exist."""
    with pytest.raises(HTTPException) as exc_info:
        compare_districts("KA-998,KA-999")
    assert exc_info.value.status_code == 404
    assert "None of the specified districts were found" in exc_info.value.detail


def test_compare_partial_valid_districts():
    """Verify that valid districts are returned even if one ID is nonexistent."""
    results = compare_districts("KA-001,KA-999")
    assert len(results) == 1
    assert results[0].district_id == "KA-001"
