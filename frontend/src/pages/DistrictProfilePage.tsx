import React, { useState, useEffect } from 'react';
import {
  DistrictProfile,
  DistrictSummary,
  RecommendationEntry,
} from '../types/api';
import { api } from '../services/api';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { ErrorAlert } from '../components/common/ErrorAlert';
import { Badge } from '../components/common/Badge';
import {
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  ResponsiveContainer,
  Tooltip,
} from 'recharts';
import {
  Award,
  Layers,
  CheckCircle,
  AlertCircle,
  Lightbulb,
  Building,
  Users,
  Compass,
} from 'lucide-react';

interface DistrictProfilePageProps {
  districtId: string;
  districts: DistrictSummary[];
  onSelectDistrict: (id: string) => void;
}

export const DistrictProfilePage: React.FC<DistrictProfilePageProps> = ({
  districtId,
  districts,
  onSelectDistrict,
}) => {
  const [profile, setProfile] = useState<DistrictProfile | null>(null);
  const [recommendations, setRecommendations] = useState<RecommendationEntry[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let isMounted = true;
    async function loadData() {
      setLoading(true);
      setError(null);
      try {
        const [profData, recoData] = await Promise.all([
          api.getDistrictProfile(districtId),
          api.getRecommendations(districtId),
        ]);
        if (isMounted) {
          setProfile(profData);
          setRecommendations(recoData);
        }
      } catch (err: any) {
        if (isMounted) setError(err.message || 'Failed to load district data');
      } finally {
        if (isMounted) setLoading(false);
      }
    }
    loadData();
    return () => {
      isMounted = false;
    };
  }, [districtId]);

  if (loading) return <LoadingSpinner message={`Loading profile for ${districtId}...`} />;
  if (error || !profile) {
    return (
      <ErrorAlert
        title="District Profile Error"
        message={error || 'Could not find district'}
        onRetry={() => onSelectDistrict(districtId)}
      />
    );
  }

  // Prepare Radar Data (6 dimensions)
  const radarData = profile.dimension_scores.map((d) => ({
    dimension: d.dimension,
    score: d.score,
    fullMark: 100,
  }));

  // Find Top 3 Strengths & Top 3 Deficits from normalized indicators
  const sortedIndicators = [...profile.normalized_scores].sort(
    (a, b) => b.normalized_score - a.normalized_score
  );
  const topStrengths = sortedIndicators.slice(0, 3);
  const topDeficits = sortedIndicators.slice(-3).reverse();

  return (
    <div className="space-y-6">
      {/* District Header & Selector Bar */}
      <div className="bg-slate-800/80 border border-slate-700/80 rounded-xl p-6 shadow-lg flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-3">
            <h2 className="text-2xl font-bold text-white tracking-tight">{profile.district_name}</h2>
            <Badge variant="primary" size="md">
              {profile.district_id}
            </Badge>
            {profile.cluster_name && (
              <Badge variant="info" size="md">
                Cluster {profile.cluster_label}: {profile.cluster_name}
              </Badge>
            )}
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Comprehensive development scorecard across 6 dimensions and 14 indicators
          </p>
        </div>

        {/* District Switcher Dropdown */}
        <div className="flex items-center gap-3">
          <label className="text-xs text-slate-400">Switch District:</label>
          <select
            value={districtId}
            onChange={(e) => onSelectDistrict(e.target.value)}
            className="bg-slate-900 border border-slate-700 rounded-lg px-3 py-1.5 text-xs text-white focus:outline-none focus:border-blue-500"
          >
            {districts.map((d) => (
              <option key={d.district_id} value={d.district_id}>
                {d.district_name} ({d.district_id})
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Metric Cards Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-slate-800/80 border border-slate-700/80 rounded-xl p-5">
          <p className="text-xs font-medium uppercase text-slate-400">Overall Development Score</p>
          <div className="mt-2 flex items-baseline gap-2">
            <span className="text-3xl font-extrabold text-white">
              {profile.overall_score?.toFixed(1) || 'N/A'}
            </span>
            <span className="text-xs text-slate-400">/ 100</span>
          </div>
          <div className="mt-3 w-full bg-slate-700 rounded-full h-1.5 overflow-hidden">
            <div
              className="bg-blue-500 h-1.5 rounded-full"
              style={{ width: `${profile.overall_score || 0}%` }}
            ></div>
          </div>
        </div>

        <div className="bg-slate-800/80 border border-slate-700/80 rounded-xl p-5">
          <p className="text-xs font-medium uppercase text-slate-400">Karnataka State Rank</p>
          <div className="mt-2 flex items-baseline gap-2">
            <span className="text-3xl font-extrabold text-emerald-400">
              #{profile.overall_rank || 'N/A'}
            </span>
            <span className="text-xs text-slate-400">of 31 Districts</span>
          </div>
          <div className="mt-3 flex items-center gap-1.5 text-xs text-slate-400">
            <Award className="w-3.5 h-3.5 text-amber-400" />
            <span>Ranked by composite score</span>
          </div>
        </div>

        <div className="bg-slate-800/80 border border-slate-700/80 rounded-xl p-5">
          <p className="text-xs font-medium uppercase text-slate-400">Geographical Area</p>
          <div className="mt-2 flex items-baseline gap-2">
            <span className="text-3xl font-extrabold text-white">
              {profile.area_km2?.toLocaleString() || 'N/A'}
            </span>
            <span className="text-xs text-slate-400">km²</span>
          </div>
          <div className="mt-3 flex items-center gap-1.5 text-xs text-slate-400">
            <Building className="w-3.5 h-3.5 text-blue-400" />
            <span>Land Area</span>
          </div>
        </div>

        <div className="bg-slate-800/80 border border-slate-700/80 rounded-xl p-5">
          <p className="text-xs font-medium uppercase text-slate-400">Total Population</p>
          <div className="mt-2 flex items-baseline gap-2">
            <span className="text-3xl font-extrabold text-white">
              {profile.population ? (profile.population / 1000000).toFixed(2) + 'M' : 'N/A'}
            </span>
            <span className="text-xs text-slate-400">({profile.population?.toLocaleString()})</span>
          </div>
          <div className="mt-3 flex items-center gap-1.5 text-xs text-slate-400">
            <Users className="w-3.5 h-3.5 text-indigo-400" />
            <span>District Inhabitants</span>
          </div>
        </div>
      </div>

      {/* Radar Chart & Strengths/Deficits Section */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Radar Chart */}
        <div className="lg:col-span-6 bg-slate-800/80 border border-slate-700/80 rounded-xl p-5 shadow-lg">
          <div className="flex items-center gap-2 pb-3 border-b border-slate-700/60 mb-2">
            <Layers className="w-4 h-4 text-blue-400" />
            <h3 className="text-sm font-semibold text-white">6-Dimension Development Radar</h3>
          </div>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <RadarChart data={radarData}>
                <PolarGrid stroke="#334155" />
                <PolarAngleAxis dataKey="dimension" tick={{ fill: '#94a3b8', fontSize: 11 }} />
                <PolarRadiusAxis domain={[0, 100]} stroke="#475569" tick={{ fontSize: 9 }} />
                <Radar
                  name={profile.district_name}
                  dataKey="score"
                  stroke="#3b82f6"
                  fill="#3b82f6"
                  fillOpacity={0.4}
                />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#0f172a',
                    borderColor: '#334155',
                    borderRadius: '8px',
                    fontSize: '12px',
                  }}
                />
              </RadarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Strengths & Deficits Summary */}
        <div className="lg:col-span-6 space-y-4">
          <div className="bg-slate-800/80 border border-slate-700/80 rounded-xl p-5 shadow-lg">
            <div className="flex items-center gap-2 pb-2 border-b border-slate-700/60 text-emerald-400">
              <CheckCircle className="w-4 h-4" />
              <h4 className="text-sm font-semibold">Key Relative Strengths</h4>
            </div>
            <div className="mt-3 space-y-2.5">
              {topStrengths.map((s) => (
                <div
                  key={s.indicator_code}
                  className="p-2.5 bg-slate-900/60 border border-slate-700/50 rounded-lg flex items-center justify-between"
                >
                  <span className="text-xs text-slate-200 capitalize font-medium">
                    {s.indicator_code.replace(/_/g, ' ')}
                  </span>
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-mono font-bold text-emerald-400">
                      {s.normalized_score.toFixed(1)} / 100
                    </span>
                    <Badge variant="success">High</Badge>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="bg-slate-800/80 border border-slate-700/80 rounded-xl p-5 shadow-lg">
            <div className="flex items-center gap-2 pb-2 border-b border-slate-700/60 text-rose-400">
              <AlertCircle className="w-4 h-4" />
              <h4 className="text-sm font-semibold">Critical Priority Deficits</h4>
            </div>
            <div className="mt-3 space-y-2.5">
              {topDeficits.map((d) => (
                <div
                  key={d.indicator_code}
                  className="p-2.5 bg-slate-900/60 border border-slate-700/50 rounded-lg flex items-center justify-between"
                >
                  <span className="text-xs text-slate-200 capitalize font-medium">
                    {d.indicator_code.replace(/_/g, ' ')}
                  </span>
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-mono font-bold text-rose-400">
                      {d.normalized_score.toFixed(1)} / 100
                    </span>
                    <Badge variant="danger">Lagging</Badge>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* 14 Indicators Scorecard Table */}
      <div className="bg-slate-800/80 border border-slate-700/80 rounded-xl p-5 shadow-lg">
        <h3 className="text-sm font-semibold text-white pb-3 border-b border-slate-700/60">
          All 14 Normalised Indicator Scores
        </h3>
        <div className="mt-4 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
          {profile.normalized_scores.map((item) => (
            <div
              key={item.indicator_code}
              className="p-3 bg-slate-900/60 border border-slate-700/50 rounded-lg space-y-2"
            >
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold text-slate-200 capitalize">
                  {item.indicator_code.replace(/_/g, ' ')}
                </span>
                <span className="text-xs font-mono font-bold text-blue-400">
                  {item.normalized_score.toFixed(1)}
                </span>
              </div>
              <div className="w-full bg-slate-800 rounded-full h-1.5 overflow-hidden">
                <div
                  className={`h-1.5 rounded-full ${
                    item.normalized_score >= 60
                      ? 'bg-emerald-500'
                      : item.normalized_score >= 40
                      ? 'bg-amber-500'
                      : 'bg-rose-500'
                  }`}
                  style={{ width: `${item.normalized_score}%` }}
                ></div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Tailored Recommendations & SDG Alignment Section */}
      <div className="bg-slate-800/80 border border-slate-700/80 rounded-xl p-5 shadow-lg">
        <div className="flex items-center gap-2 pb-3 border-b border-slate-700/60 mb-4">
          <Lightbulb className="w-4 h-4 text-amber-400" />
          <h3 className="text-sm font-semibold text-white">
            Targeted Policy Recommendations & SDG Interventions
          </h3>
        </div>
        <div className="space-y-3">
          {recommendations.map((reco, idx) => (
            <div
              key={idx}
              className="p-3.5 bg-slate-900/60 border border-slate-700/50 rounded-lg flex flex-col md:flex-row md:items-center justify-between gap-3"
            >
              <div className="flex-1 space-y-1">
                <div className="flex items-center gap-2">
                  <Badge
                    variant={
                      reco.priority === 'HIGH'
                        ? 'danger'
                        : reco.priority === 'MEDIUM'
                        ? 'warning'
                        : 'success'
                    }
                  >
                    {reco.priority} Priority
                  </Badge>
                  <span className="text-xs font-bold text-blue-400 font-mono">
                    {reco.sdg_reference}
                  </span>
                  <span className="text-[11px] text-slate-400">· Area: {reco.action_area}</span>
                </div>
                <p className="text-xs text-slate-200">{reco.recommendation_text}</p>
              </div>
              <div className="text-right shrink-0">
                <span className="text-[11px] text-slate-400 block">Current Score:</span>
                <span className="text-xs font-mono font-bold text-white">
                  {reco.normalized_score?.toFixed(1) || 'N/A'} / 100
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
