import React from 'react';
import {
  LayoutDashboard,
  Map,
  ListOrdered,
  Building2,
  BarChart3,
  GitCompare,
  Boxes,
  Compass,
  Gauge,
  Lightbulb,
  LineChart,
  BookOpen,
} from 'lucide-react';

export type PageId =
  | 'overview'
  | 'map'
  | 'rankings'
  | 'district'
  | 'indicators'
  | 'compare'
  | 'clusters'
  | 'pca'
  | 'explainability'
  | 'recommendations'
  | 'eda'
  | 'methodology';

interface SidebarProps {
  currentPage: PageId;
  onNavigate: (page: PageId) => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ currentPage, onNavigate }) => {
  const navItems: { id: PageId; label: string; icon: React.ReactNode; group?: string }[] = [
    { id: 'overview', label: 'Executive Overview', icon: <LayoutDashboard className="w-4 h-4" /> },
    { id: 'map', label: 'Karnataka Map', icon: <Map className="w-4 h-4" /> },
    { id: 'rankings', label: 'District Rankings', icon: <ListOrdered className="w-4 h-4" /> },
    { id: 'district', label: 'District Profile', icon: <Building2 className="w-4 h-4" /> },
    { id: 'indicators', label: 'Indicator Explorer', icon: <BarChart3 className="w-4 h-4" /> },
    { id: 'compare', label: 'District Comparison', icon: <GitCompare className="w-4 h-4" /> },
    { id: 'clusters', label: 'ML Clustering', icon: <Boxes className="w-4 h-4" />, group: 'Advanced Analytics' },
    { id: 'pca', label: 'PCA Decomposition', icon: <Compass className="w-4 h-4" /> },
    { id: 'explainability', label: 'State Gap Diagnostics', icon: <Gauge className="w-4 h-4" /> },
    { id: 'recommendations', label: 'SDG Recommendations', icon: <Lightbulb className="w-4 h-4" /> },
    { id: 'eda', label: 'Exploratory EDA', icon: <LineChart className="w-4 h-4" /> },
    { id: 'methodology', label: 'Data & Methodology', icon: <BookOpen className="w-4 h-4" />, group: 'Audit & Governance' },
  ];

  return (
    <aside className="w-64 bg-slate-900 border-r border-slate-800 flex flex-col shrink-0 h-screen sticky top-0 overflow-y-auto">
      {/* Brand Header */}
      <div className="p-5 border-b border-slate-800/80 flex items-center gap-3">
        <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-blue-600 to-indigo-500 flex items-center justify-center shadow-lg shadow-blue-500/20 text-white font-black text-lg">
          IS
        </div>
        <div>
          <h1 className="font-bold text-sm tracking-wide text-white">InfraSense</h1>
          <p className="text-[11px] font-medium text-slate-400">Karnataka Analytics</p>
        </div>
      </div>

      {/* Nav List */}
      <div className="p-3 space-y-1 flex-1">
        {navItems.map((item, idx) => {
          const isActive = currentPage === item.id;
          return (
            <React.Fragment key={item.id}>
              {item.group && (
                <div className="pt-4 pb-1.5 px-3 text-[10px] font-bold uppercase tracking-wider text-slate-400">
                  {item.group}
                </div>
              )}
              <button
                onClick={() => onNavigate(item.id)}
                className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg text-xs font-medium transition-all ${
                  isActive
                    ? 'bg-blue-600 text-white shadow-md shadow-blue-600/20 font-semibold'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
                }`}
              >
                <span className={isActive ? 'text-white' : 'text-slate-400'}>{item.icon}</span>
                {item.label}
              </button>
            </React.Fragment>
          );
        })}
      </div>

      {/* Audit Disclaimer Badge */}
      <div className="p-4 m-3 rounded-xl bg-amber-500/10 border border-amber-500/20 text-[11px] text-amber-300/90 leading-tight">
        <div className="font-semibold text-amber-400 mb-1 flex items-center gap-1.5">
          <span className="w-2 h-2 rounded-full bg-amber-400 animate-pulse"></span>
          Prototype Sandbox
        </div>
        Running on synthetic baseline data. Results demonstrate pipeline architecture.
      </div>
    </aside>
  );
};
