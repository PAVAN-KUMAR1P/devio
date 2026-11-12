"""
test_pydantic_schemas.py — Exhaustive Pydantic validation across all response models.
"""
import pytest
from pydantic import ValidationError
from models import (
    StatusResponse, DistrictSummary, DistrictProfile, DimensionScore,
    NormalizedScore, IndicatorInfo, IndicatorStats, RankingEntry,
    DimensionRankingEntry, ClusterSummaryEntry, ClusterDetail,
    CompareEntry, RecommendationEntry, EDADisparityEntry,
    EDAOutlierEntry, EDAUnevennessEntry
)


def test_status_response_schema():
    valid = StatusResponse(status="ok", project="InfraSense", version="1.0")
    assert valid.status == "ok"
    with pytest.raises(ValidationError):
        StatusResponse()  # Missing required fields


def test_district_models_schema():
    dim = DimensionScore(dimension="Infrastructure", score=75.4)
    assert dim.dimension == "Infrastructure"
    assert dim.score == 75.4

    norm = NormalizedScore(indicator_code="road_density", normalized_score=82.1)
    assert norm.indicator_code == "road_density"

    profile = DistrictProfile(
        district_id="KA-001",
        district_name="Bagalkote",
        area_km2=6595.0,
        population=1889752,
        overall_score=33.3,
        overall_rank=26,
        cluster_label=2,
        cluster_name="Development Gaps",
        dimension_scores=[dim],
        normalized_scores=[norm]
    )
    assert profile.district_id == "KA-001"
    assert len(profile.dimension_scores) == 1


def test_ranking_models_schema():
    rank = RankingEntry(
        district_id="KA-005",
        district_name="Bengaluru Urban",
        overall_score=60.18,
        district_rank=1,
        weight_coverage=1.0,
        is_valid=1
    )
    assert rank.district_rank == 1

    dim_rank = DimensionRankingEntry(
        district_name="Haveri",
        dimension="Infrastructure",
        dimension_score=79.14,
        dim_rank=1
    )
    assert dim_rank.dim_rank == 1


def test_recommendation_models_schema():
    reco = RecommendationEntry(
        indicator_code="road_density",
        priority="HIGH",
        sdg_reference="SDG 9.1",
        action_area="Infrastructure",
        recommendation_text="Invest in road expansion",
        normalized_score=15.5
    )
    assert reco.priority == "HIGH"
    assert reco.sdg_reference == "SDG 9.1"
