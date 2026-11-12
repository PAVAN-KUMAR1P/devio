import React, { useState, useEffect } from 'react';
import { DistrictSummary, RecommendationEntry } from '../types/api';
import { api } from '../services/api';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { ErrorAlert } from '../components/common/ErrorAlert';
import { Badge } from '../components/common/Badge';
import { Lightbulb, Filter, Award } from 'lucide-react';

interface RecommendationsPageProps {
  districts: DistrictSummary[];
  selectedDistrictId: string;
  onSelectDistrict: (id: string) => void;
  onNavigatePage: (page: any) => void;
}

export const RecommendationsPage: React.FC<RecommendationsPageProps> = ({
  districts,
  selectedDistrictId,
  onSelectDistrict,
  onNavigatePage,
}) => {
  const [recommendations, setRecommendations] = useState<RecommendationEntry[]>([]);
  const [priorityFilter, setPriorityFilter] = useState<string>('ALL');
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let isMounted = true;
    async function loadRecos() {
      setLoading(true);
      setError(null);
      try {
        const data = await api.getRecommendations(selectedDistrictId);
        if (isMounted) setRecommendations(data);
      } catch (err: any) {
        if (isMounted) setError(err.message || 'Failed to load recommendations');
      } finally {
        if (isMounted) setLoading(false);
      }
    }
    loadRecos();
    return () => {
      isMounted = false;
    };
  }, [selectedDistrictId]);

  const filteredRecos = recommendations.filter((r) => {
    if (priorityFilter === 'ALL') return true;
    return r.priority === priorityFilter;
  });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-slate-800/80 border border-slate-700/80 rounded-xl p-6 shadow-lg flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <Lightbulb className="w-5 h-5 text-amber-400" />
            <h2 className="text-xl font-bold text-white tracking-tight">
              Actionable Recommendations & SDG Alignment
            </h2>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Prioritised policy interventions mapped to UN Sustainable Development Goals
          </p>
        </div>

        {/* District Switcher */}
        <div className="flex items-center gap-3">
          <label className="text-xs text-slate-400">Target District:</label>
          <select
            value={selectedDistrictId}
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

      {/* Priority Filters */}
      <div className="flex items-center gap-2">
        <span className="text-xs text-slate-400 flex items-center gap-1 mr-2">
          <Filter className="w-3.5 h-3.5" /> Priority Filter:
        </span>
        {['ALL', 'HIGH', 'MEDIUM', 'OK'].map((p) => (
          <button
            key={p}
            onClick={() => setPriorityFilter(p)}
            className={`px-3 py-1 rounded-lg text-xs font-semibold transition-all ${
              priorityFilter === p
                ? p === 'HIGH'
                  ? 'bg-rose-600 text-white shadow-md shadow-rose-600/20'
                  : p === 'MEDIUM'
                  ? 'bg-amber-600 text-white shadow-md shadow-amber-600/20'
                  : p === 'OK'
                  ? 'bg-emerald-600 text-white shadow-md shadow-emerald-600/20'
                  : 'bg-blue-600 text-white'
                : 'bg-slate-800 text-slate-400 hover:text-white border border-slate-700'
            }`}
          >
            {p === 'ALL' ? 'All Tiers' : `${p} Priority`}
          </button>
        ))}
      </div>

      {/* Recommendations Cards List */}
      {loading ? (
        <LoadingSpinner message="Querying recommendations table..." />
      ) : error ? (
        <ErrorAlert message={error} />
      ) : (
        <div className="space-y-3">
          {filteredRecos.map((reco, idx) => (
            <div
              key={idx}
              className="p-4 bg-slate-800/80 border border-slate-700/80 rounded-xl shadow-lg flex flex-col md:flex-row md:items-center justify-between gap-4"
            >
              <div className="flex-1 space-y-1.5">
                <div className="flex items-center gap-2.5">
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
                  <span className="text-[11px] text-slate-500 font-mono">
                    [{reco.indicator_code}]
                  </span>
                </div>
                <p className="text-xs text-slate-200 font-medium leading-relaxed">
                  {reco.recommendation_text}
                </p>
              </div>
              <div className="text-right shrink-0">
                <span className="text-[11px] text-slate-400 block">Performance:</span>
                <span className="text-sm font-mono font-bold text-white">
                  {reco.normalized_score?.toFixed(1) || 'N/A'} / 100
                </span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
