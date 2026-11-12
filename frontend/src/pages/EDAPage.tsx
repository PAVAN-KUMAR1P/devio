import React, { useState, useEffect } from 'react';
import { EDADisparityEntry, EDAOutlierEntry, EDAUnevennessEntry } from '../types/api';
import { api } from '../services/api';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { ErrorAlert } from '../components/common/ErrorAlert';
import { LineChart, BarChart2, Activity, ArrowUpDown } from 'lucide-react';

export const EDAPage: React.FC = () => {
  const [disparities, setDisparities] = useState<EDADisparityEntry[]>([]);
  const [outliers, setOutliers] = useState<EDAOutlierEntry[]>([]);
  const [unevenness, setUnevenness] = useState<EDAUnevennessEntry[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let isMounted = true;
    async function loadEDA() {
      setLoading(true);
      setError(null);
      try {
        const [dData, oData, uData] = await Promise.all([
          api.getDisparity(),
          api.getOutliers(),
          api.getUnevenness(),
        ]);
        if (isMounted) {
          setDisparities(dData);
          setOutliers(oData);
          setUnevenness(uData);
        }
      } catch (err: any) {
        if (isMounted) setError(err.message || 'Failed to load EDA views');
      } finally {
        if (isMounted) setLoading(false);
      }
    }
    loadEDA();
    return () => {
      isMounted = false;
    };
  }, []);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-slate-800/80 border border-slate-700/80 rounded-xl p-6 shadow-lg">
        <div className="flex items-center gap-2">
          <LineChart className="w-5 h-5 text-blue-400" />
          <h2 className="text-xl font-bold text-white tracking-tight">
            Exploratory Data Analysis (EDA) Views
          </h2>
        </div>
        <p className="text-xs text-slate-400 mt-1">
          Automated database views monitoring regional disparity, development unevenness, and statistical anomalies
        </p>
      </div>

      {loading ? (
        <LoadingSpinner message="Querying EDA views..." />
      ) : error ? (
        <ErrorAlert message={error} />
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Development Unevenness Table */}
          <div className="bg-slate-800/80 border border-slate-700/80 rounded-xl shadow-lg overflow-hidden flex flex-col">
            <div className="p-4 bg-slate-900/60 border-b border-slate-700/80">
              <h3 className="text-sm font-semibold text-white">
                Intra-District Development Unevenness (Dimension Score Range)
              </h3>
              <p className="text-xs text-slate-400 mt-0.5">
                Districts with high imbalance across sectors (e.g. high infra but low literacy)
              </p>
            </div>
            <div className="overflow-y-auto max-h-96">
              <table className="w-full text-left border-collapse text-xs">
                <thead className="bg-slate-900 sticky top-0">
                  <tr className="border-b border-slate-700/80 text-[11px] uppercase tracking-wider text-slate-400">
                    <th className="py-2.5 px-3">District</th>
                    <th className="py-2.5 px-3 text-right">Score Range</th>
                    <th className="py-2.5 px-3 text-right">Avg Dim Score</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-700/40">
                  {unevenness.map((u) => (
                    <tr key={u.district_name} className="hover:bg-slate-750/50">
                      <td className="py-2.5 px-3 font-semibold text-white">{u.district_name}</td>
                      <td className="py-2.5 px-3 text-right font-mono font-bold text-amber-400">
                        {u.score_range.toFixed(2)}
                      </td>
                      <td className="py-2.5 px-3 text-right font-mono text-slate-300">
                        {u.avg_dim_score.toFixed(2)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Regional Disparity Spread */}
          <div className="bg-slate-800/80 border border-slate-700/80 rounded-xl shadow-lg overflow-hidden flex flex-col">
            <div className="p-4 bg-slate-900/60 border-b border-slate-700/80">
              <h3 className="text-sm font-semibold text-white">
                Indicator Regional Disparity Range (0–100 Normalized)
              </h3>
              <p className="text-xs text-slate-400 mt-0.5">
                Full spread between highest and lowest district across Karnataka
              </p>
            </div>
            <div className="overflow-y-auto max-h-96">
              <table className="w-full text-left border-collapse text-xs">
                <thead className="bg-slate-900 sticky top-0">
                  <tr className="border-b border-slate-700/80 text-[11px] uppercase tracking-wider text-slate-400">
                    <th className="py-2.5 px-3">Indicator</th>
                    <th className="py-2.5 px-3">Dimension</th>
                    <th className="py-2.5 px-3 text-right">Disparity</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-700/40">
                  {disparities.map((d) => (
                    <tr key={d.indicator_name} className="hover:bg-slate-750/50">
                      <td className="py-2.5 px-3 font-semibold text-white">{d.indicator_name}</td>
                      <td className="py-2.5 px-3 text-slate-400">{d.dimension}</td>
                      <td className="py-2.5 px-3 text-right font-mono font-bold text-emerald-400">
                        {d.disparity_range.toFixed(2)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
