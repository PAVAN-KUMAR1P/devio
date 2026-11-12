import React, { useState, useEffect } from 'react';
import { IndicatorInfo, IndicatorStats } from '../types/api';
import { api } from '../services/api';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { ErrorAlert } from '../components/common/ErrorAlert';
import { Badge } from '../components/common/Badge';
import { BarChart3, Layers, Info } from 'lucide-react';

export const IndicatorsPage: React.FC = () => {
  const [indicators, setIndicators] = useState<IndicatorInfo[]>([]);
  const [stats, setStats] = useState<IndicatorStats[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let isMounted = true;
    async function loadData() {
      setLoading(true);
      setError(null);
      try {
        const [indData, statsData] = await Promise.all([
          api.getIndicators(),
          api.getIndicatorStats(),
        ]);
        if (isMounted) {
          setIndicators(indData);
          setStats(statsData);
        }
      } catch (err: any) {
        if (isMounted) setError(err.message || 'Failed to load indicator catalog');
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
          <BarChart3 className="w-5 h-5 text-blue-400" />
          <h2 className="text-xl font-bold text-white tracking-tight">
            14 Indicator Definitions & Descriptive Statistics
          </h2>
        </div>
        <p className="text-xs text-slate-400 mt-1">
          Catalog of development indicators across 6 dimensions with mathematical polarity and observed sample moments
        </p>
      </div>

      {loading ? (
        <LoadingSpinner message="Querying indicator definitions..." />
      ) : error ? (
        <ErrorAlert message={error} />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {indicators.map((ind) => {
            const stat = stats.find((s) => s.indicator_name === ind.indicator_name);
            return (
              <div
                key={ind.indicator_code}
                className="bg-slate-800/80 border border-slate-700/80 rounded-xl p-5 shadow-lg space-y-3"
              >
                <div className="flex items-start justify-between">
                  <div>
                    <h3 className="text-sm font-bold text-white">{ind.indicator_name}</h3>
                    <p className="text-[11px] text-blue-400 font-mono mt-0.5">
                      {ind.indicator_code} · {ind.dimension}
                    </p>
                  </div>
                  <Badge variant={ind.direction === 'positive' ? 'success' : 'danger'}>
                    {ind.direction === 'positive' ? 'Higher is better' : 'Lower is better'}
                  </Badge>
                </div>

                <div className="grid grid-cols-3 gap-2 p-2.5 bg-slate-900/60 rounded-lg text-center text-xs">
                  <div>
                    <span className="text-[10px] text-slate-400 block uppercase">Mean</span>
                    <span className="font-mono font-bold text-slate-200">
                      {stat?.mean_value !== undefined && stat?.mean_value !== null ? stat.mean_value.toFixed(2) : 'N/A'}
                    </span>
                  </div>
                  <div>
                    <span className="text-[10px] text-slate-400 block uppercase">Min / Max</span>
                    <span className="font-mono font-bold text-slate-200">
                      {stat?.min_value !== undefined && stat?.min_value !== null ? stat.min_value.toFixed(1) : 'N/A'} / {stat?.max_value !== undefined && stat?.max_value !== null ? stat.max_value.toFixed(1) : 'N/A'}
                    </span>
                  </div>
                  <div>
                    <span className="text-[10px] text-slate-400 block uppercase">CV %</span>
                    <span className="font-mono font-bold text-emerald-400">
                      {stat?.cv_pct !== undefined && stat?.cv_pct !== null ? stat.cv_pct.toFixed(1) + '%' : 'N/A'}
                    </span>
                  </div>
                </div>

                <div className="flex items-center justify-between text-[11px] text-slate-400 pt-2 border-t border-slate-700/50">
                  <span>Unit: {ind.unit || 'Score'}</span>
                  <span>Sample Size: 31 Districts</span>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
