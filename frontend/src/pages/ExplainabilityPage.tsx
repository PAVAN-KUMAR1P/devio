import React, { useState, useEffect } from 'react';
import { EDADisparityEntry, EDAOutlierEntry } from '../types/api';
import { api } from '../services/api';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { ErrorAlert } from '../components/common/ErrorAlert';
import { Gauge, AlertTriangle, ArrowUpDown, TrendingUp } from 'lucide-react';

interface ExplainabilityPageProps {
  onSelectDistrict: (id: string) => void;
  onNavigatePage: (page: any) => void;
}

export const ExplainabilityPage: React.FC<ExplainabilityPageProps> = ({
  onSelectDistrict,
  onNavigatePage,
}) => {
  const [disparities, setDisparities] = useState<EDADisparityEntry[]>([]);
  const [outliers, setOutliers] = useState<EDAOutlierEntry[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let isMounted = true;
    async function loadData() {
      setLoading(true);
      setError(null);
      try {
        const [dispData, outData] = await Promise.all([
          api.getDisparity(),
          api.getOutliers(),
        ]);
        if (isMounted) {
          setDisparities(dispData);
          setOutliers(outData);
        }
      } catch (err: any) {
        if (isMounted) setError(err.message || 'Failed to load explainability data');
      } finally {
        if (isMounted) setLoading(false);
      }
    }
    loadData();
    return () => {
      isMounted = false;
    };
  }, []);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-slate-800/80 border border-slate-700/80 rounded-xl p-6 shadow-lg">
        <div className="flex items-center gap-2">
          <Gauge className="w-5 h-5 text-blue-400" />
          <h2 className="text-xl font-bold text-white tracking-tight">
            Explainability & State-Average Divergence Diagnostics
          </h2>
        </div>
        <p className="text-xs text-slate-400 mt-1">
          Quantifying district gap vs Karnataka state benchmark (&Delta; = Score - State Mean) and statistical outliers
        </p>
      </div>

      {loading ? (
        <LoadingSpinner message="Loading explainability models..." />
      ) : error ? (
        <ErrorAlert message={error} />
      ) : (
        <>
          {/* Statistical Outliers Detected */}
          <div className="bg-slate-800/80 border border-slate-700/80 rounded-xl p-5 shadow-lg">
            <div className="flex items-center gap-2 pb-3 border-b border-slate-700/60 mb-4 text-amber-400">
              <AlertTriangle className="w-4 h-4" />
              <h3 className="text-sm font-semibold">
                Detected Statistical Outliers (|z-score| &gt; 2.0)
              </h3>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {outliers.map((o, idx) => (
                <div
                  key={idx}
                  className="p-4 bg-slate-900/60 border border-amber-500/30 rounded-lg flex items-start justify-between"
                >
                  <div>
                    <h4 className="text-sm font-bold text-white">{o.district_name}</h4>
                    <p className="text-xs text-slate-300 mt-1 font-medium">{o.indicator_name}</p>
                    <p className="text-[11px] text-slate-400 mt-0.5">
                      Observed: {o.observed_value.toFixed(2)} · State Mean: {o.indicator_mean.toFixed(2)}
                    </p>
                  </div>
                  <div className="text-right">
                    <span className="inline-block px-2.5 py-1 bg-amber-500/20 text-amber-400 font-mono font-bold text-xs rounded-lg border border-amber-500/30">
                      z = +{o.z_score.toFixed(2)}
                    </span>
                    <span className="block text-[10px] text-slate-400 mt-1 uppercase font-semibold">
                      Outlier
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Statewide Indicator Disparity Ranking */}
          <div className="bg-slate-800/80 border border-slate-700/80 rounded-xl shadow-lg overflow-hidden">
            <div className="p-4 bg-slate-900/60 border-b border-slate-700/80">
              <h3 className="text-sm font-semibold text-white">
                Statewide Indicator Regional Disparity (Spread = Max - Min)
              </h3>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse text-xs">
                <thead>
                  <tr className="bg-slate-900 border-b border-slate-700/80 text-[11px] uppercase tracking-wider text-slate-400 font-semibold">
                    <th className="py-3 px-4">Indicator</th>
                    <th className="py-3 px-4">Dimension</th>
                    <th className="py-3 px-4 text-right">Min Score</th>
                    <th className="py-3 px-4 text-right">Max Score</th>
                    <th className="py-3 px-4 text-right">Disparity Spread</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-700/40">
                  {disparities.map((item) => (
                    <tr key={item.indicator_name} className="hover:bg-slate-750/50 transition-colors">
                      <td className="py-3 px-4 font-semibold text-white">{item.indicator_name}</td>
                      <td className="py-3 px-4 text-slate-400">{item.dimension}</td>
                      <td className="py-3 px-4 text-right font-mono text-rose-400">
                        {item.min_score.toFixed(1)}
                      </td>
                      <td className="py-3 px-4 text-right font-mono text-emerald-400">
                        {item.max_score.toFixed(1)}
                      </td>
                      <td className="py-3 px-4 text-right font-mono font-bold text-blue-400">
                        {item.disparity_range.toFixed(1)}
                      </td>
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
