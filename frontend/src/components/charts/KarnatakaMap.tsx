import React, { useState } from 'react';
import { RankingEntry } from '../../types/api';

interface KarnatakaMapProps {
  rankings: RankingEntry[];
  selectedDistrictId?: string;
  onSelectDistrict?: (districtId: string) => void;
  title?: string;
}

// Geographic grid coordinates and polygon layout for all 31 districts of Karnataka
interface DistrictGeo {
  id: string;
  name: string;
  x: number;
  y: number;
  w: number;
  h: number;
  region: 'North' | 'Central' | 'South' | 'Coastal';
}

const DISTRICT_COORDS: DistrictGeo[] = [
  // Far North
  { id: 'KA-006', name: 'Bidar', x: 300, y: 30, w: 70, h: 45, region: 'North' },
  { id: 'KA-017', name: 'Kalaburagi', x: 260, y: 80, w: 90, h: 50, region: 'North' },
  { id: 'KA-029', name: 'Vijayapura', x: 170, y: 70, w: 85, h: 55, region: 'North' },
  { id: 'KA-030', name: 'Yadgir', x: 310, y: 135, w: 75, h: 50, region: 'North' },
  { id: 'KA-001', name: 'Bagalkote', x: 160, y: 130, w: 80, h: 48, region: 'North' },
  { id: 'KA-003', name: 'Belagavi', x: 75, y: 110, w: 80, h: 70, region: 'North' },
  { id: 'KA-023', name: 'Raichur', x: 250, y: 180, w: 85, h: 48, region: 'North' },
  { id: 'KA-020', name: 'Koppal', x: 190, y: 185, w: 55, h: 48, region: 'North' },
  { id: 'KA-014', name: 'Gadag', x: 135, y: 185, w: 50, h: 48, region: 'North' },
  { id: 'KA-013', name: 'Dharwad', x: 80, y: 185, w: 50, h: 48, region: 'North' },
  { id: 'KA-028', name: 'Uttara Kannada', x: 30, y: 220, w: 65, h: 90, region: 'Coastal' },

  // Central
  { id: 'KA-031', name: 'Vijayanagara', x: 200, y: 240, w: 65, h: 50, region: 'Central' },
  { id: 'KA-002', name: 'Ballari', x: 270, y: 235, w: 70, h: 55, region: 'Central' },
  { id: 'KA-016', name: 'Haveri', x: 105, y: 240, w: 60, h: 50, region: 'Central' },
  { id: 'KA-012', name: 'Davanagere', x: 140, y: 295, w: 65, h: 50, region: 'Central' },
  { id: 'KA-010', name: 'Chitradurga', x: 210, y: 295, w: 70, h: 60, region: 'Central' },
  { id: 'KA-025', name: 'Shivamogga', x: 80, y: 310, w: 55, h: 65, region: 'Central' },

  // Coastal & Malnad
  { id: 'KA-027', name: 'Udupi', x: 30, y: 340, w: 45, h: 65, region: 'Coastal' },
  { id: 'KA-009', name: 'Chikkamagaluru', x: 80, y: 380, w: 65, h: 55, region: 'South' },
  { id: 'KA-011', name: 'Dakshina Kannada', x: 35, y: 410, w: 50, h: 65, region: 'Coastal' },
  { id: 'KA-018', name: 'Kodagu', x: 55, y: 480, w: 55, h: 50, region: 'South' },

  // South & East
  { id: 'KA-026', name: 'Tumakuru', x: 220, y: 360, w: 75, h: 70, region: 'South' },
  { id: 'KA-008', name: 'Chikkaballapura', x: 300, y: 365, w: 65, h: 50, region: 'South' },
  { id: 'KA-019', name: 'Kolar', x: 350, y: 415, w: 60, h: 55, region: 'South' },
  { id: 'KA-015', name: 'Hassan', x: 120, y: 430, w: 65, h: 60, region: 'South' },
  { id: 'KA-004', name: 'Bengaluru Rural', x: 285, y: 420, w: 60, h: 45, region: 'South' },
  { id: 'KA-005', name: 'Bengaluru Urban', x: 275, y: 470, w: 60, h: 45, region: 'South' },
  { id: 'KA-024', name: 'Ramanagara', x: 220, y: 480, w: 50, h: 50, region: 'South' },
  { id: 'KA-021', name: 'Mandya', x: 165, y: 490, w: 50, h: 50, region: 'South' },
  { id: 'KA-022', name: 'Mysuru', x: 135, y: 535, w: 65, h: 55, region: 'South' },
  { id: 'KA-007', name: 'Chamarajanagar', x: 185, y: 550, w: 70, h: 55, region: 'South' },
];

export const KarnatakaMap: React.FC<KarnatakaMapProps> = ({
  rankings,
  selectedDistrictId,
  onSelectDistrict,
  title = 'Karnataka District Development Map',
}) => {
  const [hoveredDistrict, setHoveredDistrict] = useState<RankingEntry | null>(null);
  const [mousePos, setMousePos] = useState<{ x: number; y: number }>({ x: 0, y: 0 });

  // Fast score lookup map by district name
  const scoreMap = new Map<string, RankingEntry>();
  rankings.forEach((r) => scoreMap.set(r.district_name.toLowerCase(), r));

  const getDistrictFill = (name: string, isSelected: boolean) => {
    const entry = scoreMap.get(name.toLowerCase());
    if (!entry) return '#334155';
    const score = entry.overall_score;

    if (isSelected) return '#3b82f6'; // Bright blue for selected
    if (score >= 55) return '#10b981'; // Green (Top Tier)
    if (score >= 45) return '#0ea5e9'; // Cyan/Blue (Moderate-High)
    if (score >= 35) return '#f59e0b'; // Amber (Moderate)
    return '#f43f5e'; // Rose (Lagging)
  };

  return (
    <div className="relative bg-slate-800/80 border border-slate-700/80 rounded-xl p-5 shadow-lg flex flex-col items-center">
      <div className="w-full flex items-center justify-between mb-3 pb-3 border-b border-slate-700/60">
        <div>
          <h3 className="text-sm font-semibold text-white tracking-wide">{title}</h3>
          <p className="text-xs text-slate-400 mt-0.5">Click any district to inspect full profile</p>
        </div>
        <div className="flex items-center gap-2 text-xs">
          <span className="flex items-center gap-1 text-slate-300">
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-500"></span> ≥ 55
          </span>
          <span className="flex items-center gap-1 text-slate-300">
            <span className="w-2.5 h-2.5 rounded-full bg-sky-500"></span> 45–54
          </span>
          <span className="flex items-center gap-1 text-slate-300">
            <span className="w-2.5 h-2.5 rounded-full bg-amber-500"></span> 35–44
          </span>
          <span className="flex items-center gap-1 text-slate-300">
            <span className="w-2.5 h-2.5 rounded-full bg-rose-500"></span> &lt; 35
          </span>
        </div>
      </div>

      <div
        className="relative w-full max-w-[480px] h-[580px] flex items-center justify-center"
        onMouseMove={(e) => {
          const rect = e.currentTarget.getBoundingClientRect();
          setMousePos({ x: e.clientX - rect.left, y: e.clientY - rect.top });
        }}
      >
        <svg
          viewBox="0 0 440 640"
          className="w-full h-full drop-shadow-md select-none"
        >
          {/* Subtle outline map background */}
          <rect x="0" y="0" width="440" height="640" fill="transparent" />

          {DISTRICT_COORDS.map((dist) => {
            const entry = scoreMap.get(dist.name.toLowerCase());
            const isSelected = selectedDistrictId === dist.id;
            const isHovered = hoveredDistrict?.district_name.toLowerCase() === dist.name.toLowerCase();

            return (
              <g
                key={dist.id}
                className="cursor-pointer transition-transform duration-150"
                onClick={() => onSelectDistrict && onSelectDistrict(dist.id)}
                onMouseEnter={() => setHoveredDistrict(entry || null)}
                onMouseLeave={() => setHoveredDistrict(null)}
              >
                <rect
                  x={dist.x}
                  y={dist.y}
                  width={dist.w}
                  height={dist.h}
                  rx="6"
                  ry="6"
                  fill={getDistrictFill(dist.name, isSelected)}
                  stroke={isSelected ? '#ffffff' : isHovered ? '#60a5fa' : '#1e293b'}
                  strokeWidth={isSelected ? '2.5' : isHovered ? '2' : '1'}
                  className="transition-all duration-200 hover:opacity-90"
                />
                <text
                  x={dist.x + dist.w / 2}
                  y={dist.y + dist.h / 2 - 3}
                  textAnchor="middle"
                  dominantBaseline="middle"
                  className="fill-white font-semibold text-[9.5px] pointer-events-none drop-shadow"
                >
                  {dist.name}
                </text>
                {entry && (
                  <text
                    x={dist.x + dist.w / 2}
                    y={dist.y + dist.h / 2 + 10}
                    textAnchor="middle"
                    dominantBaseline="middle"
                    className="fill-slate-100 text-[8px] font-mono pointer-events-none opacity-90"
                  >
                    #{entry.district_rank} ({entry.overall_score.toFixed(1)})
                  </text>
                )}
              </g>
            );
          })}
        </svg>

        {/* Floating Tooltip */}
        {hoveredDistrict && (
          <div
            className="absolute pointer-events-none z-50 bg-slate-900/95 border border-blue-500/40 rounded-lg p-2.5 shadow-xl backdrop-blur-md text-xs space-y-1 transform -translate-x-1/2 -translate-y-full"
            style={{
              left: `${mousePos.x}px`,
              top: `${Math.max(mousePos.y - 12, 10)}px`,
            }}
          >
            <div className="font-bold text-white border-b border-slate-700/80 pb-1 flex items-center justify-between gap-3">
              <span>{hoveredDistrict.district_name}</span>
              <span className="text-blue-400 font-mono">Rank #{hoveredDistrict.district_rank}</span>
            </div>
            <div className="flex items-center justify-between gap-4 text-slate-300">
              <span>Overall Score:</span>
              <span className="font-bold text-emerald-400 font-mono">
                {hoveredDistrict.overall_score.toFixed(2)} / 100
              </span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
