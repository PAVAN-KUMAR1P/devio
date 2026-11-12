import {
  DistrictSummary,
  DistrictProfile,
  IndicatorInfo,
  IndicatorStats,
  RankingEntry,
  DimensionRankingEntry,
  ClusterSummaryEntry,
  ClusterDetail,
  CompareEntry,
  RecommendationEntry,
  EDADisparityEntry,
  EDAOutlierEntry,
  EDAUnevennessEntry,
} from '../types/api';

const API_BASE = 'http://localhost:8000';

async function request<T>(endpoint: string): Promise<T> {
  const url = `${API_BASE}${endpoint}`;
  try {
    const res = await fetch(url);
    if (!res.ok) {
      throw new Error(`API error ${res.status}: ${res.statusText}`);
    }
    return await res.json();
  } catch (err) {
    console.error(`Failed to fetch ${url}:`, err);
    throw err;
  }
}

export const api = {
  // Health
  checkHealth: () => request<{ status: string; project: string; version: string }>('/'),

  // Districts
  getDistricts: () => request<DistrictSummary[]>('/districts'),
  getDistrictProfile: (id: string) => request<DistrictProfile>(`/districts/${id}`),

  // Indicators
  getIndicators: () => request<IndicatorInfo[]>('/indicators'),
  getIndicatorStats: () => request<IndicatorStats[]>('/indicators/stats'),

  // Rankings
  getOverallRankings: () => request<RankingEntry[]>('/rankings/overall'),
  getDimensionRankings: (dimension: string) =>
    request<DimensionRankingEntry[]>(`/rankings/dimension/${encodeURIComponent(dimension)}`),

  // Clusters
  getClusters: () => request<ClusterSummaryEntry[]>('/clusters'),
  getClusterDistricts: (clusterId: number) =>
    request<ClusterDetail[]>(`/clusters/${clusterId}`),

  // Compare
  compareDistricts: (ids: string[]) =>
    request<CompareEntry[]>(`/compare?districts=${ids.join(',')}`),

  // Recommendations
  getRecommendations: (districtId: string) =>
    request<RecommendationEntry[]>(`/recommendations/${districtId}`),

  // EDA
  getDisparity: () => request<EDADisparityEntry[]>('/eda/disparity'),
  getOutliers: () => request<EDAOutlierEntry[]>('/eda/outliers'),
  getUnevenness: () => request<EDAUnevennessEntry[]>('/eda/unevenness'),
};
