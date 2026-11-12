import React, { useState } from 'react';
import { Search, CheckCircle2, AlertCircle, FileCode, ExternalLink } from 'lucide-react';
import { DistrictSummary } from '../../types/api';

interface NavbarProps {
  districts: DistrictSummary[];
  selectedDistrictId: string;
  onSelectDistrict: (id: string) => void;
  apiConnected: boolean;
  pageTitle: string;
}

export const Navbar: React.FC<NavbarProps> = ({
  districts,
  selectedDistrictId,
  onSelectDistrict,
  apiConnected,
  pageTitle,
}) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [dropdownOpen, setDropdownOpen] = useState(false);

  const filteredDistricts = districts.filter(
    (d) =>
      d.district_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      d.district_id.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <header className="h-16 bg-slate-900/80 backdrop-blur-md border-b border-slate-800 sticky top-0 z-30 px-6 flex items-center justify-between">
      <div className="flex items-center gap-3">
        <h2 className="text-sm font-semibold text-white tracking-wide">{pageTitle}</h2>
      </div>

      <div className="flex items-center gap-4">
        {/* District Quick Search Dropdown */}
        <div className="relative">
          <div className="relative flex items-center">
            <Search className="w-3.5 h-3.5 text-slate-400 absolute left-3 pointer-events-none" />
            <input
              type="text"
              placeholder="Search 31 districts..."
              value={searchQuery}
              onChange={(e) => {
                setSearchQuery(e.target.value);
                setDropdownOpen(true);
              }}
              onFocus={() => setDropdownOpen(true)}
              className="w-56 pl-8 pr-3 py-1.5 bg-slate-800/80 border border-slate-700 rounded-lg text-xs text-white placeholder-slate-400 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-all"
            />
          </div>

          {dropdownOpen && searchQuery && (
            <div className="absolute right-0 mt-1.5 w-64 max-h-60 overflow-y-auto bg-slate-800 border border-slate-700 rounded-xl shadow-2xl py-1 z-50">
              {filteredDistricts.length === 0 ? (
                <div className="px-4 py-2 text-xs text-slate-400">No districts match "{searchQuery}"</div>
              ) : (
                filteredDistricts.map((d) => (
                  <button
                    key={d.district_id}
                    onClick={() => {
                      onSelectDistrict(d.district_id);
                      setDropdownOpen(false);
                      setSearchQuery('');
                    }}
                    className={`w-full text-left px-3 py-2 text-xs flex items-center justify-between hover:bg-slate-700/60 transition-colors ${
                      d.district_id === selectedDistrictId ? 'bg-blue-600/20 text-blue-400 font-semibold' : 'text-slate-200'
                    }`}
                  >
                    <span>{d.district_name}</span>
                    <span className="text-[10px] text-slate-400 font-mono">{d.district_id}</span>
                  </button>
                ))
              )}
            </div>
          )}
        </div>

        {/* Backend API Connection Indicator */}
        <div
          className={`flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[11px] font-medium border ${
            apiConnected
              ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30'
              : 'bg-rose-500/10 text-rose-400 border-rose-500/30'
          }`}
        >
          {apiConnected ? (
            <>
              <CheckCircle2 className="w-3 h-3 text-emerald-400" />
              <span>FastAPI 8000</span>
            </>
          ) : (
            <>
              <AlertCircle className="w-3 h-3 text-rose-400" />
              <span>Backend Offline</span>
            </>
          )}
        </div>

        {/* OpenAPI Link */}
        <a
          href="http://localhost:8000/docs"
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-center gap-1 text-xs text-slate-400 hover:text-blue-400 transition-colors"
        >
          <FileCode className="w-3.5 h-3.5" />
          <span>API Docs</span>
          <ExternalLink className="w-2.5 h-2.5 opacity-60" />
        </a>
      </div>
    </header>
  );
};
