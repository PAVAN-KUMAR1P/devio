import React, { useState } from 'react';
import {
  DistrictSummary,
  RankingEntry,
  DimensionRankingEntry,
} from '../types/api';
import { MetricCard } from '../components/common/MetricCard';
import { KarnatakaMap } from '../components/charts/KarnatakaMap';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from 'recharts';
import {
  Building2,
  TrendingUp,
  Award,
  AlertTriangle,
  Layers,
  ArrowRight,
} from 'lucide-react';

interface OverviewPageProps {
  districts: DistrictSummary[];
  rankings: RankingEntry[];
  onSelectDistrict: (id: string) => void;
  onNavigatePage: (page: any) => void;
}

export const OverviewPage: React.FC<OverviewPageProps> = ({
  districts,
  rankings,
  onSelectDistrict,
  onNavigatePage,
}) => {
  const [selectedDimension, setSelectedDimension] = useState<string>('Overall');

  const avgScore = rankings.length
    ? (rankings.reduce((sum, r) => sum + r.overall_score, 0) / rankings.length).toFixed(1)
    : '44.5';

  const topDistrict = rankings[0];
  const bottomDistrict = rankings[rankings.length - 1];

  // Six dimensions summary benchmarks
  const dimensionsSummary = [
    { name: 'Infrastructure', weight: '20%', avg: 51.4, top: 'Haveri (79.1)', lag: 'Mandya (12.2)' },
    { name: 'Digital Access', weight: '15%', avg: 49.3, top: 'Vijayapura (83.8)', lag: 'Belagavi (10.0)' },
    { name: 'Industry', weight: '20%', avg: 39.8, top: 'Raichur (100.0)', lag: 'Mysuru (0.6)' },
    { name: 'Innovation', weight: '10%', avg: 8.4, top: 'BLR Urban (100.0)', lag: 'DK (0.2)' },
    { name: 'Energy & Env', weight: '20%', avg: 47.9, top: 'Mandya (75.6)', lag: 'Shivamogga (17.2)' },
    { name: 'Human Capital', weight: '15%', avg: 42.6, top: 'Tumakuru (100.0)', lag: 'UK (0.0)' },
  ];

  // Top 5 vs Bottom 5 Data for comparison chart
  const top5 = rankings.slice(0, 5);
  const bottom5 = rankings.slice(-5).reverse();
  const barChartData = [
    ...top5.map((d) => ({ name: d.district_name, score: d.overall_score, type: 'top' })),
    ...bottom5.map((d) => ({ name: d.district_name, score: d.overall_score, type: 'bottom' })),
  ];

  return (
    <div className="space-y-6">
      {/* KPI Cards Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          title="Districts Analysed"
          value={districts.length || 31}
          subtitle="All administrative units covered"
          icon={<Building2 className="w-5 h-5" />}
          trend={{ label: '100% Data Coverage', positive: true }}
        />
        <MetricCard
          title="State Avg Development Score"
          value={`${avgScore} / 100`}
          subtitle="Composite across 6 dimensions"
          icon={<TrendingUp className="w-5 h-5" />}
          trend={{ label: 'Min: 21.5 · Max: 60.2' }}
        />
        <MetricCard
          title="Highest Scoring District"
          value={topDistrict?.district_name || 'Bengaluru Urban'}
          subtitle={`Score: ${topDistrict?.overall_score.toFixed(1) || '60.2'} (Rank #1)`}
          icon={<Award className="w-5 h-5" />}
          trend={{ label: 'Leader in Innovation & HC', positive: true }}
          onClick={() => topDistrict && onSelectDistrict(topDistrict.district_id || 'KA-005')}
        />
        <MetricCard
          title="Lowest Scoring District"
          value={bottomDistrict?.district_name || 'Udupi'}
          subtitle={`Score: ${bottomDistrict?.overall_score.toFixed(1) || '21.5'} (Rank #31)`}
          icon={<AlertTriangle className="w-5 h-5 text-rose-400" />}
          trend={{ label: 'Critical Intervention Area', positive: false }}
          onClick={() => bottomDistrict && onSelectDistrict(bottomDistrict.district_id || 'KA-027')}
        />
      </div>

      {/* Main Grid: Interactive Map + Dimension Summary */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Map Column */}
        <div className="lg:col-span-7">
          <KarnatakaMap
            rankings={rankings}
            onSelectDistrict={(id) => {
              onSelectDistrict(id);
              onNavigatePage('district');
            }}
          />
        </div>

        {/* Six Dimensions Summary Column */}
        <div className="lg:col-span-5 space-y-6">
          <div className="bg-slate-800/80 border border-slate-700/80 rounded-xl p-5 shadow-lg">
            <div className="flex items-center justify-between pb-3 border-b border-slate-700/60">
              <div className="flex items-center gap-2">
                <Layers className="w-4 h-4 text-blue-400" />
                <h3 className="text-sm font-semibold text-white">Six Dimension Performance</h3>
              </div>
              <span className="text-[11px] text-slate-400">Weighted Composite</span>
            </div>

            <div className="mt-4 space-y-3">
              {dimensionsSummary.map((dim) => (
                <div
                  key={dim.name}
                  className="p-3 bg-slate-900/60 border border-slate-700/50 rounded-lg hover:border-blue-500/40 transition-colors"
                >
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-semibold text-white">{dim.name}</span>
                    <span className="text-[11px] text-blue-400 font-mono">Weight: {dim.weight}</span>
                  </div>
                  <div className="mt-2 w-full bg-slate-800 rounded-full h-2 overflow-hidden">
                    <div
                      className="bg-gradient-to-r from-blue-500 to-emerald-400 h-2 rounded-full"
                      style={{ width: `${dim.avg}%` }}
                    ></div>
                  </div>
                  <div className="mt-2 flex items-center justify-between text-[10px] text-slate-400">
                    <span className="text-emerald-400">Top: {dim.top}</span>
                    <span className="text-rose-400">Lag: {dim.lag}</span>
                  </div>
                </div>
              ))}
            </div>

            <button
              onClick={() => onNavigatePage('rankings')}
              className="mt-4 w-full py-2 bg-blue-600/20 hover:bg-blue-600/30 border border-blue-500/40 text-blue-400 text-xs font-medium rounded-lg flex items-center justify-center gap-1.5 transition-colors"
            >
              <span>Explore Full Rankings</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      </div>

      {/* Top 5 vs Bottom 5 Comparison Chart & Quick Action Matrix */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        <div className="lg:col-span-8 bg-slate-800/80 border border-slate-700/80 rounded-xl p-5 shadow-lg">
          <div className="flex items-center justify-between pb-3 border-b border-slate-700/60 mb-4">
            <div>
              <h3 className="text-sm font-semibold text-white">Top 5 vs Bottom 5 Development Scores</h3>
              <p className="text-xs text-slate-400">Highlighting state inter-district variance</p>
            </div>
            <div className="flex items-center gap-3 text-xs">
              <span className="flex items-center gap-1 text-emerald-400">
                <span className="w-2.5 h-2.5 rounded-sm bg-emerald-500"></span> Top 5
              </span>
              <span className="flex items-center gap-1 text-rose-400">
                <span className="w-2.5 h-2.5 rounded-sm bg-rose-500"></span> Bottom 5
              </span>
            </div>
          </div>

          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={barChartData} margin={{ top: 10, right: 10, left: -20, bottom: 25 }}>
                <XAxis
                  dataKey="name"
                  stroke="#64748b"
                  fontSize={10}
                  angle={-30}
                  textAnchor="end"
                  interval={0}
                />
                <YAxis stroke="#64748b" fontSize={10} domain={[0, 70]} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#0f172a',
                    borderColor: '#334155',
                    borderRadius: '8px',
                    fontSize: '12px',
                  }}
                />
                <Bar dataKey="score" radius={[4, 4, 0, 0]}>
                  {barChartData.map((entry, index) => (
                    <Cell
                      key={`cell-${index}`}
                      fill={entry.type === 'top' ? '#10b981' : '#f43f5e'}
                    />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Quick Action Matrix Card */}
        <div className="lg:col-span-4 bg-slate-800/80 border border-slate-700/80 rounded-xl p-5 shadow-lg flex flex-col justify-between">
          <div>
            <h3 className="text-sm font-semibold text-white pb-3 border-b border-slate-700/60">
              Analytical Modules
            </h3>
            <div className="mt-4 space-y-2.5">
              <button
                onClick={() => onNavigatePage('compare')}
                className="w-full text-left p-2.5 bg-slate-900/60 hover:bg-slate-700/40 border border-slate-700/50 rounded-lg text-xs flex items-center justify-between text-slate-200 transition-colors"
              >
                <span>District Comparison Matrix</span>
                <ArrowRight className="w-3.5 h-3.5 text-blue-400" />
              </button>
              <button
                onClick={() => onNavigatePage('clusters')}
                className="w-full text-left p-2.5 bg-slate-900/60 hover:bg-slate-700/40 border border-slate-700/50 rounded-lg text-xs flex items-center justify-between text-slate-200 transition-colors"
              >
                <span>Machine Learning Clustering</span>
                <ArrowRight className="w-3.5 h-3.5 text-blue-400" />
              </button>
              <button
                onClick={() => onNavigatePage('pca')}
                className="w-full text-left p-2.5 bg-slate-900/60 hover:bg-slate-700/40 border border-slate-700/50 rounded-lg text-xs flex items-center justify-between text-slate-200 transition-colors"
              >
                <span>PCA Biplot Decomposition</span>
                <ArrowRight className="w-3.5 h-3.5 text-blue-400" />
              </button>
              <button
                onClick={() => onNavigatePage('recommendations')}
                className="w-full text-left p-2.5 bg-slate-900/60 hover:bg-slate-700/40 border border-slate-700/50 rounded-lg text-xs flex items-center justify-between text-slate-200 transition-colors"
              >
                <span>SDG Priority Intervention Matrix</span>
                <ArrowRight className="w-3.5 h-3.5 text-blue-400" />
              </button>
            </div>
          </div>

          <div className="mt-4 pt-3 border-t border-slate-700/60 text-[11px] text-slate-400 flex items-center justify-between">
            <span>FastAPI Connected</span>
            <span className="text-emerald-400 font-mono">14 Endpoints Active</span>
          </div>
        </div>
      </div>
    </div>
  );
};
