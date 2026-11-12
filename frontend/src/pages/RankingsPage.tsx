import React, { useState, useEffect } from 'react';
import { RankingEntry, DimensionRankingEntry } from '../types/api';
import { api } from '../services/api';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { ErrorAlert } from '../components/common/ErrorAlert';
import { Search, Award, ArrowUpDown, ExternalLink } from 'lucide-react';

interface RankingsPageProps {
  onSelectDistrict: (id: string) => void;
  onNavigatePage: (page: any) => void;
}

export const RankingsPage: React.FC<RankingsPageProps> = ({
  onSelectDistrict,
  onNavigatePage,
}) => {
  const [selectedDimension, setSelectedDimension] = useState<string>('Overall');
  const [overallRankings, setOverallRankings] = useState<RankingEntry[]>([]);
  const [dimensionRankings, setDimensionRankings] = useState<DimensionRankingEntry[]>([]);
  const [search, setSearch] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const dimensions = [
    'Overall',
    'Infrastructure',
    'Digital Access',
    'Industry',
    'Innovation',
    'Energy & Environment',
    'Human Capital',
  ];

  useEffect(() => {
    let isMounted = true;
    async function loadRankings() {
      setLoading(true);
      setError(null);
      try {
        if (selectedDimension === 'Overall') {
          const data = await api.getOverallRankings();
          if (isMounted) setOverallRankings(data);
        } else {
          const data = await api.getDimensionRankings(selectedDimension);
          if (isMounted) setDimensionRankings(data);
        }
      } catch (err: any) {
        if (isMounted) setError(err.message || 'Failed to load rankings');
      } finally {
        if (isMounted) setLoading(false);
      }
    }
    loadRankings();
    return () => {
      isMounted = false;
    };
  }, [selectedDimension]);

  const filteredOverall = overallRankings.filter((r) =>
    r.district_name.toLowerCase().includes(search.toLowerCase())
  );

  const filteredDim = dimensionRankings.filter((r) =>
    r.district_name.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="bg-slate-800/80 border border-slate-700/80 rounded-xl p-6 shadow-lg flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-white tracking-tight">Karnataka District Rankings</h2>
          <p className="text-xs text-slate-400 mt-1">
            Standardised 0–100 comparative evaluation of all 31 districts
          </p>
        </div>

        {/* Search Input */}
        <div className="relative">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5 pointer-events-none" />
          <input
            type="text"
            placeholder="Search district..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-64 pl-9 pr-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-xs text-white placeholder-slate-400 focus:outline-none focus:border-blue-500"
          />
        </div>
      </div>

      {/* Dimension Filter Tabs */}
      <div className="flex items-center gap-1.5 overflow-x-auto pb-2 scrollbar-none">
        {dimensions.map((dim) => (
          <button
            key={dim}
            onClick={() => setSelectedDimension(dim)}
            className={`px-3.5 py-1.5 rounded-lg text-xs font-semibold whitespace-nowrap transition-all ${
              selectedDimension === dim
                ? 'bg-blue-600 text-white shadow-md shadow-blue-600/20'
                : 'bg-slate-800/80 hover:bg-slate-700/60 text-slate-400 hover:text-white border border-slate-700/60'
            }`}
          >
            {dim}
          </button>
        ))}
      </div>

      {/* Table Section */}
      {loading ? (
        <LoadingSpinner message={`Loading ${selectedDimension} rankings...`} />
      ) : error ? (
        <ErrorAlert message={error} />
      ) : (
        <div className="bg-slate-800/80 border border-slate-700/80 rounded-xl shadow-lg overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="bg-slate-900/80 border-b border-slate-700/80 text-[11px] uppercase tracking-wider text-slate-400 font-semibold">
                  <th className="py-3.5 px-4 w-16 text-center">Rank</th>
                  <th className="py-3.5 px-4">District</th>
                  <th className="py-3.5 px-4 text-right">Score</th>
                  <th className="py-3.5 px-4 w-48">Score Bar</th>
                  <th className="py-3.5 px-4 text-center">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-700/40 text-xs">
                {selectedDimension === 'Overall'
                  ? filteredOverall.map((item) => (
                      <tr
                        key={item.district_name}
                        className="hover:bg-slate-750/50 transition-colors"
                      >
                        <td className="py-3 px-4 text-center">
                          <span
                            className={`inline-flex items-center justify-center w-6 h-6 rounded-full font-bold font-mono text-[11px] ${
                              item.district_rank === 1
                                ? 'bg-amber-500/20 text-amber-400 border border-amber-500/40'
                                : item.district_rank === 2
                                ? 'bg-slate-400/20 text-slate-300 border border-slate-400/40'
                                : item.district_rank === 3
                                ? 'bg-amber-700/20 text-amber-600 border border-amber-700/40'
                                : 'text-slate-400'
                            }`}
                          >
                            {item.district_rank}
                          </span>
                        </td>
                        <td className="py-3 px-4 font-semibold text-white">
                          {item.district_name}
                          {item.district_id && (
                            <span className="ml-2 text-[10px] text-slate-400 font-mono">
                              ({item.district_id})
                            </span>
                          )}
                        </td>
                        <td className="py-3 px-4 text-right font-mono font-bold text-emerald-400">
                          {item.overall_score.toFixed(2)}
                        </td>
                        <td className="py-3 px-4">
                          <div className="w-full bg-slate-900 rounded-full h-2 overflow-hidden">
                            <div
                              className="bg-gradient-to-r from-blue-500 to-emerald-400 h-2 rounded-full"
                              style={{ width: `${item.overall_score}%` }}
                            ></div>
                          </div>
                        </td>
                        <td className="py-3 px-4 text-center">
                          <button
                            onClick={() => {
                              if (item.district_id) onSelectDistrict(item.district_id);
                              onNavigatePage('district');
                            }}
                            className="inline-flex items-center gap-1 px-2.5 py-1 bg-slate-700/60 hover:bg-blue-600 hover:text-white rounded-md text-[11px] text-slate-300 transition-colors"
                          >
                            <span>Profile</span>
                            <ExternalLink className="w-2.5 h-2.5" />
                          </button>
                        </td>
                      </tr>
                    ))
                  : filteredDim.map((item) => (
                      <tr
                        key={item.district_name}
                        className="hover:bg-slate-750/50 transition-colors"
                      >
                        <td className="py-3 px-4 text-center font-mono font-bold text-slate-300">
                          #{item.dim_rank}
                        </td>
                        <td className="py-3 px-4 font-semibold text-white">
                          {item.district_name}
                        </td>
                        <td className="py-3 px-4 text-right font-mono font-bold text-blue-400">
                          {item.dimension_score.toFixed(2)}
                        </td>
                        <td className="py-3 px-4">
                          <div className="w-full bg-slate-900 rounded-full h-2 overflow-hidden">
                            <div
                              className="bg-blue-500 h-2 rounded-full"
                              style={{ width: `${item.dimension_score}%` }}
                            ></div>
                          </div>
                        </td>
                        <td className="py-3 px-4 text-center">
                          <button
                            onClick={() => onNavigatePage('district')}
                            className="inline-flex items-center gap-1 px-2.5 py-1 bg-slate-700/60 hover:bg-blue-600 hover:text-white rounded-md text-[11px] text-slate-300 transition-colors"
                          >
                            <span>Profile</span>
                            <ExternalLink className="w-2.5 h-2.5" />
                          </button>
                        </td>
                      </tr>
                    ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};
