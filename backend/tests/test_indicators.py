"""
test_indicators.py — Unit and integration tests for /indicators router.
"""
import pytest
from routers.indicators import list_indicators, get_indicator_stats
from models import IndicatorInfo, IndicatorStats


def test_list_indicators():
    """Verify listing all 14 indicators and their metadata."""
    indicators = list_indicators()
    assert isinstance(indicators, list)
    assert len(indicators) == 14

    codes = set()
    negative_indicators = []
    for item in indicators:
        model = IndicatorInfo.model_validate(item)
        codes.add(model.indicator_code)
        if model.direction == "negative":
            negative_indicators.append(model.indicator_code)

    assert len(codes) == 14
    # Verify PM2.5 is the only negative polarity indicator
    assert negative_indicators == ["pm25"]


def test_get_indicator_stats():
    """Verify descriptive statistics for all 14 indicators."""
    stats = get_indicator_stats()
    assert isinstance(stats, list)
    assert len(stats) == 14

    for s in stats:
        model = IndicatorStats.model_validate(s)
        assert model.n == 31  # All 31 districts observed
        assert model.min_value is not None
        assert model.max_value is not None
        assert model.mean_value is not None
        assert model.min_value <= model.mean_value <= model.max_value
        assert round(model.max_value - model.min_value, 2) == round(model.range_value, 2)
        assert model.cv_pct is not None and model.cv_pct > 0
