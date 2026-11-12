export interface DistrictSummary {
  district_id: string;
  district_name: string;
  area_km2: number | null;
  population: number | null;
}

export interface DimensionScore {
  dimension: string;
  score: number;
}

export interface NormalizedScore {
  indicator_code: string;
  normalized_score: number;
}

export interface DistrictProfile {
  district_id: string;
  district_name: string;
  area_km2: number | null;
  population: number | null;
  overall_score: number | null;
  overall_rank: number | null;
  cluster_label: number | null;
  cluster_name: string | null;
  dimension_scores: DimensionScore[];
  normalized_scores: NormalizedScore[];
}

export interface IndicatorInfo {
  indicator_code: string;
  indicator_name: string;
  dimension: string;
  direction: string;
  unit: string | null;
}

export interface IndicatorStats {
  indicator_name: string;
  dimension: string;
  direction: string;
  n: number;
  mean_value: number | null;
  min_value: number | null;
  max_value: number | null;
  range_value: number | null;
  cv_pct: number | null;
}

export interface RankingEntry {
  district_id?: string;
  district_name: string;
  overall_score: number;
  district_rank: number;
  weight_coverage?: number;
  is_valid?: number;
}

export interface DimensionRankingEntry {
  district_name: string;
  dimension: string;
  dimension_score: number;
  dim_rank: number;
}

export interface ClusterSummaryEntry {
  run_name: string;
  algorithm: string;
  cluster_label: number;
  cluster_name: string;
  district_count: number;
  avg_centroid_dist: number | null;
  districts: string | null;
}

export interface ClusterDetail {
  district_id: string;
  district_name: string;
  overall_score: number | null;
  distance_to_centroid: number | null;
}

export interface CompareEntry {
  district_id: string;
  district_name: string;
  overall_score: number | null;
  indicator_scores: Record<string, number>;
}

export interface RecommendationEntry {
  indicator_code: string;
  priority: string;
  sdg_reference: string;
  action_area: string;
  recommendation_text: string;
  normalized_score: number | null;
}

export interface EDADisparityEntry {
  indicator_name: string;
  dimension: string;
  disparity_range: number;
  max_score: number;
  min_score: number;
}

export interface EDAOutlierEntry {
  district_name: string;
  indicator_name: string;
  dimension: string;
  observed_value: number;
  indicator_mean: number;
  indicator_std: number;
  z_score: number;
  flag: string | null;
}

export interface EDAUnevennessEntry {
  district_name: string;
  score_range: number;
  avg_dim_score: number;
  dimensions_covered: number;
}
