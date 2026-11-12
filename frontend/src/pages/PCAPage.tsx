import React from 'react';
import {
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  ZAxis,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
  Cell,
} from 'recharts';
import { Compass, BarChart2, Layers } from 'lucide-react';

interface PCAPageProps {
  onSelectDistrict: (id: string) => void;
  onNavigatePage: (page: any) => void;
}

export const PCAPage: React.FC<PCAPageProps> = ({ onSelectDistrict, onNavigatePage }) => {
  // Scree plot explained variance data (from PCA pipeline run)
  const screeData = [
    { component: 'PC1', variance: 19.77, cumulative: 19.77 },
    { component: 'PC2', variance: 16.38, cumulative: 36.15 },
    { component: 'PC3', variance: 12.45, cumulative: 48.60 },
    { component: 'PC4', variance: 10.12, cumulative: 58.72 },
    { component: 'PC5', variance: 8.85, cumulative: 67.57 },
    { component: 'PC6', variance: 7.34, cumulative: 74.91 },
    { component: 'PC7', variance: 6.22, cumulative: 81.13 },
    { component: 'PC8', variance: 5.10, cumulative: 86.23 },
    { component: 'PC9', variance: 4.31, cumulative: 90.54 },
    { component: 'PC10', variance: 3.25, cumulative: 93.79 },
    { component: 'PC11', variance: 2.55, cumulative: 96.34 },
    { component: 'PC12', variance: 1.82, cumulative: 98.16 },
    { component: 'PC13', variance: 1.14, cumulative: 99.30 },
    { component: 'PC14', variance: 0.70, cumulative: 100.0 },
  ];

  // Representative PC1 vs PC2 projections for districts
  const biplotData = [
    { name: 'Bengaluru Urban', pc1: 4.82, pc2: 3.12, cluster: 'Cluster 0' },
    { name: 'Raichur', pc1: 2.15, pc2: -1.84, cluster: 'Cluster 1' },
    { name: 'Chitradurga', pc1: 1.65, pc2: 0.42, cluster: 'Cluster 1' },
    { name: 'Bengaluru Rural', pc1: 2.45, pc2: -0.92, cluster: 'Cluster 1' },
    { name: 'Kalaburagi', pc1: 1.35, pc2: -0.85, cluster: 'Cluster 1' },
    { name: 'Hassan', pc1: 1.12, pc2: -1.45, cluster: 'Cluster 1' },
    { name: 'Bidar', pc1: 0.95, pc2: -1.20, cluster: 'Cluster 1' },
    { name: 'Mandya', pc1: 0.85, pc2: 1.55, cluster: 'Cluster 1' },
    { name: 'Tumakuru', pc1: 0.42, pc2: 1.85, cluster: 'Cluster 2' },
    { name: 'Shivamogga', pc1: 0.15, pc2: 1.45, cluster: 'Cluster 2' },
    { name: 'Belagavi', pc1: 0.65, pc2: -0.85, cluster: 'Cluster 2' },
    { name: 'Davanagere', pc1: 0.25, pc2: 0.95, cluster: 'Cluster 2' },
    { name: 'Dharwad', pc1: -0.45, pc2: 0.12, cluster: 'Cluster 2' },
    { name: 'Ballari', pc1: -0.85, pc2: -1.35, cluster: 'Cluster 1' },
    { name: 'Dakshina Kannada', pc1: -1.25, pc2: -0.45, cluster: 'Cluster 2' },
    { name: 'Uttara Kannada', pc1: -1.65, pc2: -1.15, cluster: 'Cluster 2' },
    { name: 'Bagalkote', pc1: -1.45, pc2: 0.65, cluster: 'Cluster 2' },
    { name: 'Kodagu', pc1: -1.85, pc2: 0.25, cluster: 'Cluster 2' },
    { name: 'Koppal', pc1: -1.95, pc2: 0.45, cluster: 'Cluster 2' },
    { name: 'Mysuru', pc1: -2.35, pc2: 0.15, cluster: 'Cluster 2' },
    { name: 'Udupi', pc1: -2.85, pc2: -0.65, cluster: 'Cluster 2' },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-slate-800/80 border border-slate-700/80 rounded-xl p-6 shadow-lg">
        <div className="flex items-center gap-2">
          <Compass className="w-5 h-5 text-blue-400" />
          <h2 className="text-xl font-bold text-white tracking-tight">
            Principal Component Analysis (PCA) Decomposition
          </h2>
        </div>
        <p className="text-xs text-slate-400 mt-1">
          Dimensionality reduction across 14 indicators: PC1 & PC2 explain 36.15% cumulative statewide variance
        </p>
      </div>

      {/* PCA Metrics Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="bg-slate-800/80 border border-slate-700/80 rounded-xl p-5">
          <p className="text-xs font-medium uppercase text-slate-400">PC1 Explained Variance</p>
          <h3 className="mt-2 text-2xl font-bold text-emerald-400">19.77%</h3>
          <p className="text-xs text-slate-400 mt-1">Primary axis: Economic & Enterprise Density</p>
        </div>
        <div className="bg-slate-800/80 border border-slate-700/80 rounded-xl p-5">
          <p className="text-xs font-medium uppercase text-slate-400">PC2 Explained Variance</p>
          <h3 className="mt-2 text-2xl font-bold text-blue-400">16.38%</h3>
          <p className="text-xs text-slate-400 mt-1">Secondary axis: Environmental & Human Capital</p>
        </div>
        <div className="bg-slate-800/80 border border-slate-700/80 rounded-xl p-5">
          <p className="text-xs font-medium uppercase text-slate-400">Components for &gt; 80% Variance</p>
          <h3 className="mt-2 text-2xl font-bold text-amber-400">7 of 14</h3>
          <p className="text-xs text-slate-400 mt-1">81.13% cumulative variance explained</p>
        </div>
      </div>

      {/* 2D PCA Biplot Scatter & Scree Plot */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* 2D Projection Biplot */}
        <div className="lg:col-span-7 bg-slate-800/80 border border-slate-700/80 rounded-xl p-5 shadow-lg">
          <div className="flex items-center justify-between pb-3 border-b border-slate-700/60 mb-4">
            <div>
              <h3 className="text-sm font-semibold text-white">PC1 vs PC2 District Projections</h3>
              <p className="text-xs text-slate-400">Coordinates represent relative district orientation</p>
            </div>
            <div className="flex items-center gap-3 text-xs">
              <span className="flex items-center gap-1 text-emerald-400">
                <span className="w-2.5 h-2.5 rounded-full bg-emerald-500"></span> Urban Core
              </span>
              <span className="flex items-center gap-1 text-blue-400">
                <span className="w-2.5 h-2.5 rounded-full bg-blue-500"></span> Moderate
              </span>
              <span className="flex items-center gap-1 text-rose-400">
                <span className="w-2.5 h-2.5 rounded-full bg-rose-500"></span> Lagging
              </span>
            </div>
          </div>

          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 0 }}>
                <XAxis
                  type="number"
                  dataKey="pc1"
                  name="PC1"
                  stroke="#64748b"
                  fontSize={10}
                  domain={[-3.5, 5.5]}
                />
                <YAxis
                  type="number"
                  dataKey="pc2"
                  name="PC2"
                  stroke="#64748b"
                  fontSize={10}
                  domain={[-2.5, 3.5]}
                />
                <Tooltip
                  cursor={{ strokeDasharray: '3 3' }}
                  content={({ payload }) => {
                    if (payload && payload.length) {
                      const data = payload[0].payload;
                      return (
                        <div className="bg-slate-900 border border-slate-700 rounded-lg p-2 text-xs shadow-xl">
                          <p className="font-bold text-white">{data.name}</p>
                          <p className="text-slate-400">
                            PC1: {data.pc1} · PC2: {data.pc2}
                          </p>
                          <p className="text-blue-400 font-semibold">{data.cluster}</p>
                        </div>
                      );
                    }
                    return null;
                  }}
                />
                <Scatter name="Districts" data={biplotData} fill="#3b82f6" />
              </ScatterChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Scree Plot */}
        <div className="lg:col-span-5 bg-slate-800/80 border border-slate-700/80 rounded-xl p-5 shadow-lg">
          <h3 className="text-sm font-semibold text-white pb-3 border-b border-slate-700/60 mb-4">
            PCA Scree Plot (Individual % Variance)
          </h3>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={screeData.slice(0, 10)} margin={{ top: 10, right: 10, left: -20, bottom: 20 }}>
                <XAxis dataKey="component" stroke="#64748b" fontSize={10} />
                <YAxis stroke="#64748b" fontSize={10} domain={[0, 25]} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#0f172a',
                    borderColor: '#334155',
                    borderRadius: '8px',
                    fontSize: '11px',
                  }}
                />
                <Bar dataKey="variance" fill="#3b82f6" radius={[4, 4, 0, 0]}>
                  {screeData.slice(0, 10).map((entry, index) => (
                    <Cell
                      key={`cell-${index}`}
                      fill={index < 2 ? '#10b981' : index < 7 ? '#3b82f6' : '#64748b'}
                    />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
};
