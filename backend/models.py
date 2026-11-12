"""
models.py — Pydantic response models for InfraSense API.
"""
from pydantic import BaseModel
from typing import Optional, List, Any


class StatusResponse(BaseModel):
    status: str
    project: str
    version: str


class DistrictSummary(BaseModel):
    district_id: str
    district_name: str
    area_km2: Optional[float]
    population: Optional[int]


class NormalizedScore(BaseModel):
    indicator_code: str
    normalized_score: float


class DimensionScore(BaseModel):
    dimension: str
    score: float


class DistrictProfile(BaseModel):
    district_id: str
    district_name: str
    area_km2: Optional[float]
    population: Optional[int]
    overall_score: Optional[float]
    overall_rank: Optional[int]
    cluster_label: Optional[int]
    cluster_name: Optional[str]
    dimension_scores: List[DimensionScore]
    normalized_scores: List[NormalizedScore]


class IndicatorInfo(BaseModel):
    indicator_code: str
    indicator_name: str
    dimension: str
    direction: str
    unit: Optional[str]


class IndicatorStats(BaseModel):
    indicator_name: str
    dimension: str
    direction: str
    n: int
    mean_value: Optional[float]
    min_value: Optional[float]
    max_value: Optional[float]
    range_value: Optional[float]
    cv_pct: Optional[float]


class RankingEntry(BaseModel):
    district_id: Optional[str]
    district_name: str
    overall_score: float
    district_rank: int
    weight_coverage: Optional[float]
    is_valid: Optional[int]


class DimensionRankingEntry(BaseModel):
    district_name: str
    dimension: str
    dimension_score: float
    dim_rank: int


class ClusterSummaryEntry(BaseModel):
    run_name: str
    algorithm: str
    cluster_label: int
    cluster_name: str
    district_count: int
    avg_centroid_dist: Optional[float]
    districts: Optional[str]


class ClusterDetail(BaseModel):
    district_id: str
    district_name: str
    overall_score: Optional[float]
    distance_to_centroid: Optional[float]


class CompareEntry(BaseModel):
    district_id: str
    district_name: str
    overall_score: Optional[float]
    indicator_scores: dict


class RecommendationEntry(BaseModel):
    indicator_code: str
    priority: Optional[str]
    sdg_reference: Optional[str]
    action_area: Optional[str]
    recommendation_text: str
    normalized_score: Optional[float]


class EDADisparityEntry(BaseModel):
    indicator_name: str
    dimension: str
    disparity_range: Optional[float]
    max_score: Optional[float]
    min_score: Optional[float]


class EDAOutlierEntry(BaseModel):
    district_name: str
    indicator_name: str
    dimension: str
    observed_value: Optional[float]
    indicator_mean: Optional[float]
    indicator_std: Optional[float]
    z_score: Optional[float]
    flag: Optional[str]


class EDAUnevennessEntry(BaseModel):
    district_name: str
    score_range: Optional[float]
    avg_dim_score: Optional[float]
    dimensions_covered: Optional[int]
