import React from 'react';
import { AlertCircle, RefreshCw } from 'lucide-react';

interface ErrorAlertProps {
  title?: string;
  message: string;
  onRetry?: () => void;
}

export const ErrorAlert: React.FC<ErrorAlertProps> = ({
  title = 'Failed to load data',
  message,
  onRetry,
}) => {
  return (
    <div className="bg-rose-500/10 border border-rose-500/30 rounded-xl p-5 flex items-start gap-4">
      <AlertCircle className="w-6 h-6 text-rose-400 shrink-0 mt-0.5" />
      <div className="flex-1">
        <h4 className="text-sm font-semibold text-rose-300">{title}</h4>
        <p className="mt-1 text-xs text-rose-200/80 leading-relaxed">{message}</p>
        {onRetry && (
          <button
            onClick={onRetry}
            className="mt-3 inline-flex items-center gap-1.5 px-3 py-1.5 bg-rose-500/20 hover:bg-rose-500/30 border border-rose-500/40 text-rose-200 text-xs font-medium rounded-lg transition-colors"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            Retry Request
          </button>
        )}
      </div>
    </div>
  );
};
