import React, { useState, useEffect } from 'react';
import { DistrictSummary, CompareEntry } from '../types/api';
import { api } from '../services/api';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { ErrorAlert } from '../components/common/ErrorAlert';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { GitCompare, Plus, X, Layers } from 'lucide-react';

interface ComparePageProps {
  districts: DistrictSummary[];
}

export const ComparePage: React.FC<ComparePageProps> = ({ districts }) => {
  const [selectedIds, setSelectedIds] = useState<string[]>(['KA-005', 'KA-023', 'KA-022']);
  const [compareData, setCompareData] = useState<CompareEntry[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let isMounted = true;
    async function loadComparison() {
      if (selectedIds.length < 2) return;
      setLoading(true);
      setError(null);
      try {
        const data = await api.compareDistricts(selectedIds);
        if (isMounted) setCompareData(data);
      } catch (err: any) {
        if (isMounted) setError(err.message || 'Comparison request failed');
      } finally {
        if (isMounted) setLoading(false);
      }
    }
    loadComparison();
    return () => {
      isMounted = false;
    };
  }, [selectedIds]);

  const addDistrict = (id: string) => {
    if (selectedIds.includes(id) || selectedIds.length >= 5) return;
    setSelectedIds([...selectedIds, id]);
  };

  const removeDistrict = (id: string) => {
    if (selectedIds.length <= 2) return; // Keep at least 2
    setSelectedIds(selectedIds.filter((d) => d !== id));
  };

  // Prepare Grouped Bar Chart Data
  // We extract indicator names from compareData[0]
  const indicatorCodes = compareData.length
    ? Object.keys(compareData[0].indicator_scores)
    : [];

  const chartData = indicatorCodes.map((code) => {
    const row: any = { indicator: code.replace(/_/g, ' ') };
    compareData.forEach((d) => {
      row[d.district_name] = d.indicator_scores[code];
    });
    return row;
  });

  const colors = ['#3b82f6', '#10b981', '#f59e0b', '#8b5cf6', '#ec4899'];

  return (
    <div className="space-y-6">
      {/* Header & Controls */}
      <div className="bg-slate-800/80 border border-slate-700/80 rounded-xl p-6 shadow-lg">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <GitCompare className="w-5 h-5 text-blue-400" />
              <h2 className="text-xl font-bold text-white tracking-tight">District Comparison Matrix</h2>
            </div>
            <p className="text-xs text-slate-400 mt-1">
              Select 2 to 5 districts for side-by-side indicator and composite score benchmarking
            </p>
          </div>

          {/* District Selector Add Dropdown */}
          <div className="flex items-center gap-2">
            <select
              onChange={(e) => {
                if (e.target.value) {
                  addDistrict(e.target.value);
                  e.target.value = '';
                }
              }}
              className="bg-slate-900 border border-slate-700 rounded-lg px-3 py-1.5 text-xs text-white focus:outline-none focus:border-blue-500"
              disabled={selectedIds.length >= 5}
            >
              <option value="">+ Add District ({selectedIds.length}/5)...</option>
              {districts
                .filter((d) => !selectedIds.includes(d.district_id))
                .map((d) => (
                  <option key={d.district_id} value={d.district_id}>
                    {d.district_name} ({d.district_id})
                  </option>
                ))}
            </select>
          </div>
        </div>

        {/* Selected District Chips */}
        <div className="mt-4 flex flex-wrap items-center gap-2 pt-3 border-t border-slate-700/60">
          {selectedIds.map((id, idx) => {
            const dObj = districts.find((d) => d.district_id === id);
            return (
              <span
                key={id}
                className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-slate-900 border border-slate-700 text-white"
                style={{ borderLeftColor: colors[idx % colors.length], borderLeftWidth: '4px' }}
              >
                <span>{dObj?.district_name || id}</span>
                {selectedIds.length > 2 && (
                  <button
                    onClick={() => removeDistrict(id)}
                    className="text-slate-400 hover:text-rose-400 transition-colors ml-1"
                  >
                    <X className="w-3 h-3" />
                  </button>
                )}
              </span>
            );
          })}
        </div>
      </div>

      {loading ? (
        <LoadingSpinner message="Querying comparison endpoint..." />
      ) : error ? (
        <ErrorAlert message={error} />
      ) : (
        <>
          {/* Grouped Bar Chart Comparison across 14 Indicators */}
          <div className="bg-slate-800/80 border border-slate-700/80 rounded-xl p-5 shadow-lg">
            <h3 className="text-sm font-semibold text-white pb-3 border-b border-slate-700/60 mb-4">
              Side-by-Side Indicator Comparison (0–100 Scores)
            </h3>
            <div className="h-96">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart
                  data={chartData}
                  margin={{ top: 10, right: 20, left: -10, bottom: 60 }}
                >
                  <XAxis
                    dataKey="indicator"
                    stroke="#64748b"
                    fontSize={10}
                    angle={-35}
                    textAnchor="end"
                    interval={0}
                  />
                  <YAxis stroke="#64748b" fontSize={10} domain={[0, 100]} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: '#0f172a',
                      borderColor: '#334155',
                      borderRadius: '8px',
                      fontSize: '11px',
                    }}
                  />
                  <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '10px' }} />
                  {compareData.map((d, idx) => (
                    <Bar
                      key={d.district_id}
                      dataKey={d.district_name}
                      fill={colors[idx % colors.length]}
                      radius={[3, 3, 0, 0]}
                    />
                  ))}
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Tabular Comparison Matrix */}
          <div className="bg-slate-800/80 border border-slate-700/80 rounded-xl shadow-lg overflow-hidden">
            <div className="p-4 bg-slate-900/60 border-b border-slate-700/80">
              <h3 className="text-sm font-semibold text-white">Full Comparative Matrix</h3>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse text-xs">
                <thead>
                  <tr className="bg-slate-900 border-b border-slate-700/80 text-[11px] uppercase tracking-wider text-slate-400 font-semibold">
                    <th className="py-3 px-4">Metric / Indicator</th>
                    {compareData.map((d) => (
                      <th key={d.district_id} className="py-3 px-4 text-center font-bold text-white">
                        {d.district_name}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-700/40">
                  <tr className="bg-blue-950/20 font-semibold">
                    <td className="py-3 px-4 text-blue-300">Overall Composite Score</td>
                    {compareData.map((d) => (
                      <td
                        key={d.district_id}
                        className="py-3 px-4 text-center font-mono font-bold text-emerald-400"
                      >
                        {d.overall_score?.toFixed(2) || 'N/A'}
                      </td>
                    ))}
                  </tr>
                  {indicatorCodes.map((code) => (
                    <tr key={code} className="hover:bg-slate-750/50 transition-colors">
                      <td className="py-2.5 px-4 text-slate-300 capitalize">
                        {code.replace(/_/g, ' ')}
                      </td>
                      {compareData.map((d) => (
                        <td
                          key={d.district_id}
                          className="py-2.5 px-4 text-center font-mono text-slate-200"
                        >
                          {d.indicator_scores[code]?.toFixed(1) || '0.0'}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </>
      )}
    </div>
  );
};
