import React from 'react';
import { BookOpen, ShieldCheck, AlertCircle, Layers, Award } from 'lucide-react';

export const MethodologyPage: React.FC = () => {
  const dimensionWeights = [
    { dimension: 'Infrastructure', weight: 0.20, rationale: 'Foundational physical enabler; underpins all other dimensions' },
    { dimension: 'Digital Access', weight: 0.15, rationale: 'Cross-cutting; enables service delivery and digital economy' },
    { dimension: 'Industry', weight: 0.20, rationale: 'Economic engine; enterprise density and employment' },
    { dimension: 'Innovation', weight: 0.10, rationale: 'Emerging; tech creation and patent productivity' },
    { dimension: 'Energy & Environment', weight: 0.20, rationale: 'Long-term sustainability, clean air, renewable generation' },
    { dimension: 'Human Capital', weight: 0.15, rationale: 'Long-run social driver; literacy as primary proxy' },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-slate-800/80 border border-slate-700/80 rounded-xl p-6 shadow-lg">
        <div className="flex items-center gap-2">
          <BookOpen className="w-5 h-5 text-blue-400" />
          <h2 className="text-xl font-bold text-white tracking-tight">
            Methodology, Normalization & Audit Disclosure
          </h2>
        </div>
        <p className="text-xs text-slate-400 mt-1">
          Technical specifications, mathematical formulas, and governance audit records
        </p>
      </div>

      {/* Audit Caution Banner */}
      <div className="p-5 bg-amber-500/10 border border-amber-500/30 rounded-xl space-y-2 text-xs leading-relaxed text-amber-200">
        <div className="flex items-center gap-2 font-bold text-amber-400 text-sm">
          <AlertCircle className="w-4 h-4 shrink-0" />
          <span>Stage 1 Audit Finding: Prototype / Synthetic Status</span>
        </div>
        <p>
          All observations currently loaded in <code>InfraSense_Production.db</code> are synthetic placeholders generated on 12 Nov 2026. Tables <code>data_sources</code> and <code>raw_observations</code> currently hold 0 records. All rankings, clusters, and recommendations represent proof-of-concept pipeline deliverables and must be replaced with official government data (Census 2011, PMGSY, Udyam, CPCB, MoSPI) before adoption.
        </p>
      </div>

      {/* Mathematical Normalization Formula */}
      <div className="bg-slate-800/80 border border-slate-700/80 rounded-xl p-5 shadow-lg space-y-3">
        <h3 className="text-sm font-semibold text-white pb-2 border-b border-slate-700/60">
          Mathematical Normalization Mechanics (0–100 Rescaling)
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
          <div className="p-3.5 bg-slate-900/60 rounded-lg space-y-1.5 border border-slate-700/50">
            <h4 className="font-semibold text-emerald-400">Positive Polarity Indicators (13 Indicators)</h4>
            <p className="text-slate-300 font-mono text-[11px] bg-slate-950 p-2 rounded border border-slate-800">
              Score = ((X - X_min) / (X_max - X_min)) * 100
            </p>
            <p className="text-slate-400 text-[11px]">
              Higher observed value yields a higher development score.
            </p>
          </div>
          <div className="p-3.5 bg-slate-900/60 rounded-lg space-y-1.5 border border-slate-700/50">
            <h4 className="font-semibold text-rose-400">Negative Polarity Indicator (Annual Avg PM2.5)</h4>
            <p className="text-slate-300 font-mono text-[11px] bg-slate-950 p-2 rounded border border-slate-800">
              Score = ((X_max - X) / (X_max - X_min)) * 100
            </p>
            <p className="text-slate-400 text-[11px]">
              Lower observed pollution yields a higher development score.
            </p>
          </div>
        </div>
      </div>

      {/* Dimension Weights Table */}
      <div className="bg-slate-800/80 border border-slate-700/80 rounded-xl shadow-lg overflow-hidden">
        <div className="p-4 bg-slate-900/60 border-b border-slate-700/80">
          <h3 className="text-sm font-semibold text-white">Dimension Macro-Weighting Scheme</h3>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-xs">
            <thead>
              <tr className="bg-slate-900 border-b border-slate-700/80 text-[11px] uppercase tracking-wider text-slate-400 font-semibold">
                <th className="py-3 px-4">Dimension</th>
                <th className="py-3 px-4 text-center">Weight</th>
                <th className="py-3 px-4">Policy Rationale</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-700/40">
              {dimensionWeights.map((w) => (
                <tr key={w.dimension} className="hover:bg-slate-750/50">
                  <td className="py-3 px-4 font-semibold text-white">{w.dimension}</td>
                  <td className="py-3 px-4 text-center font-mono font-bold text-blue-400">
                    {(w.weight * 100).toFixed(0)}%
                  </td>
                  <td className="py-3 px-4 text-slate-300">{w.rationale}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
