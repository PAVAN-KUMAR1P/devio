"""
test_eda.py — Unit and integration tests for /eda router.
"""
import pytest
from routers.eda import get_regional_disparity, get_indicator_outliers, get_development_unevenness
from models import EDADisparityEntry, EDAOutlierEntry, EDAUnevennessEntry


def test_get_regional_disparity():
    """Verify regional disparity rankings for all 14 indicators."""
    disparity = get_regional_disparity()
    assert isinstance(disparity, list)
    assert len(disparity) == 14

    prev_range = 1000.0
    for item in disparity:
        entry = EDADisparityEntry.model_validate(item)
        assert entry.disparity_range <= prev_range + 1e-4
        assert entry.min_score <= entry.max_score
        prev_range = entry.disparity_range


def test_get_indicator_outliers():
    """Verify statistical outlier detection (|z| > 2.0)."""
    outliers = get_indicator_outliers()
    assert isinstance(outliers, list)
    assert len(outliers) > 0  # 4 known outliers in synthetic dataset

    prev_abs_z = 100.0
    for item in outliers:
        entry = EDAOutlierEntry.model_validate(item)
        assert abs(entry.z_score) >= 2.0
        assert abs(entry.z_score) <= prev_abs_z + 1e-4
        assert entry.flag == "OUTLIER"
        prev_abs_z = abs(entry.z_score)


def test_get_development_unevenness():
    """Verify development unevenness across all 31 districts."""
    unevenness = get_development_unevenness()
    assert isinstance(unevenness, list)
    assert len(unevenness) == 31

    prev_score_range = 100.0
    for item in unevenness:
        entry = EDAUnevennessEntry.model_validate(item)
        assert entry.dimensions_covered == 6
        assert entry.score_range <= prev_score_range + 1e-4
        assert 0 <= entry.avg_dim_score <= 100
        prev_score_range = entry.score_range
