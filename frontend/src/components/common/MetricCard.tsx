import React from 'react';

interface MetricCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon?: React.ReactNode;
  trend?: {
    label: string;
    positive?: boolean;
  };
  onClick?: () => void;
}

export const MetricCard: React.FC<MetricCardProps> = ({
  title,
  value,
  subtitle,
  icon,
  trend,
  onClick,
}) => {
  return (
    <div
      onClick={onClick}
      className={`bg-slate-800/80 border border-slate-700/80 rounded-xl p-5 shadow-lg backdrop-blur-sm transition-all duration-200 ${
        onClick ? 'cursor-pointer hover:border-blue-500 hover:shadow-blue-500/10' : ''
      }`}
    >
      <div className="flex items-start justify-between">
        <div>
          <p className="text-xs font-medium uppercase tracking-wider text-slate-400">{title}</p>
          <h3 className="mt-2 text-2xl font-bold tracking-tight text-white">{value}</h3>
          {subtitle && <p className="mt-1 text-xs text-slate-400">{subtitle}</p>}
        </div>
        {icon && (
          <div className="p-2.5 rounded-lg bg-blue-500/10 text-blue-400 border border-blue-500/20">
            {icon}
          </div>
        )}
      </div>
      {trend && (
        <div className="mt-3 pt-3 border-t border-slate-700/50 flex items-center gap-1.5 text-xs">
          <span
            className={`font-semibold ${
              trend.positive === undefined
                ? 'text-slate-300'
                : trend.positive
                ? 'text-emerald-400'
                : 'text-rose-400'
            }`}
          >
            {trend.label}
          </span>
        </div>
      )}
    </div>
  );
};
