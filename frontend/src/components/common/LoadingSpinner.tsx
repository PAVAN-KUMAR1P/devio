import React from 'react';

export const LoadingSpinner: React.FC<{ message?: string }> = ({
  message = 'Loading analytics data...',
}) => {
  return (
    <div className="flex flex-col items-center justify-center p-12 space-y-4">
      <div className="w-10 h-10 border-4 border-blue-500/20 border-t-blue-500 rounded-full animate-spin"></div>
      <p className="text-sm font-medium text-slate-400 animate-pulse">{message}</p>
    </div>
  );
};
