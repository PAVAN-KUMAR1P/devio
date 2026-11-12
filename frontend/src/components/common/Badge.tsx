import React from 'react';

interface BadgeProps {
  children: React.ReactNode;
  variant?: 'primary' | 'success' | 'warning' | 'danger' | 'slate' | 'info';
  size?: 'sm' | 'md';
}

export const Badge: React.FC<BadgeProps> = ({
  children,
  variant = 'slate',
  size = 'sm',
}) => {
  const variantStyles = {
    primary: 'bg-blue-500/15 text-blue-400 border-blue-500/30',
    success: 'bg-emerald-500/15 text-emerald-400 border-emerald-500/30',
    warning: 'bg-amber-500/15 text-amber-400 border-amber-500/30',
    danger: 'bg-rose-500/15 text-rose-400 border-rose-500/30',
    slate: 'bg-slate-700/40 text-slate-300 border-slate-600/40',
    info: 'bg-cyan-500/15 text-cyan-400 border-cyan-500/30',
  };

  const sizeStyles = {
    sm: 'text-xs px-2 py-0.5',
    md: 'text-sm px-2.5 py-1',
  };

  return (
    <span
      className={`inline-flex items-center gap-1 font-medium rounded-full border ${variantStyles[variant]} ${sizeStyles[size]}`}
    >
      {children}
    </span>
  );
};
