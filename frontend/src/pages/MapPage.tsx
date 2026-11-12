import React from 'react';
import { RankingEntry } from '../types/api';
import { KarnatakaMap } from '../components/charts/KarnatakaMap';
import { Map, Info } from 'lucide-react';

interface MapPageProps {
  rankings: RankingEntry[];
  selectedDistrictId: string;
  onSelectDistrict: (id: string) => void;
  onNavigatePage: (page: any) => void;
}

export const MapPage: React.FC<MapPageProps> = ({
  rankings,
  selectedDistrictId,
  onSelectDistrict,
  onNavigatePage,
}) => {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-slate-800/80 border border-slate-700/80 rounded-xl p-6 shadow-lg">
        <div className="flex items-center gap-2">
          <Map className="w-5 h-5 text-blue-400" />
          <h2 className="text-xl font-bold text-white tracking-tight">
            Karnataka District Geographical Choropleth Map
          </h2>
        </div>
        <p className="text-xs text-slate-400 mt-1">
          Geographic spatial visualization of 31 Karnataka districts color-graded by development score
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        <div className="lg:col-span-8 flex justify-center">
          <div className="w-full max-w-xl">
            <KarnatakaMap
              rankings={rankings}
              selectedDistrictId={selectedDistrictId}
              onSelectDistrict={(id) => {
                onSelectDistrict(id);
                onNavigatePage('district');
              }}
            />
          </div>
        </div>

        <div className="lg:col-span-4 bg-slate-800/80 border border-slate-700/80 rounded-xl p-5 shadow-lg space-y-4">
          <div className="flex items-center gap-2 pb-3 border-b border-slate-700/60 text-blue-400">
            <Info className="w-4 h-4" />
            <h3 className="text-sm font-semibold">Choropleth Legend & Regional Key</h3>
          </div>
          <div className="space-y-3 text-xs text-slate-300 leading-relaxed">
            <p>
              • <strong>Color Grading:</strong> Districts with scores $\ge 55$ are rendered in <span className="text-emerald-400 font-semibold">Emerald Green</span>, $45–54$ in <span className="text-sky-400 font-semibold">Cyan</span>, $35–44$ in <span className="text-amber-400 font-semibold">Amber</span>, and &lt; 35 in <span className="text-rose-400 font-semibold">Rose Red</span>.
            </p>
            <p>
              • <strong>Regional Pattern:</strong> The Southern corridor around Bengaluru Urban and Rural displays high innovation and digital connectivity, whereas parts of Kalyana Karnataka (NE) and Coastal Malnad show acute sectoral divergences.
            </p>
            <p>
              • <strong>Interaction:</strong> Hover to view district rank and composite development score. Click any district to navigate directly to its diagnostic profile.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
