import React from 'react';
import { LucideIcon } from 'lucide-react';

interface StatCardProps {
  title: string;
  value: string | number;
  icon: LucideIcon;
  sublabel?: string;
  statusText?: string;
  variant?: 'cyan' | 'emerald' | 'amber' | 'rose' | 'sky' | 'slate';
  loading?: boolean;
}

const colorMap = {
  cyan: {
    iconBg: 'bg-cyan-500/10 text-cyan-400 border-cyan-500/20',
    text: 'text-cyan-400',
    border: 'border-slate-800 hover:border-cyan-500/30',
  },
  emerald: {
    iconBg: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
    text: 'text-emerald-400',
    border: 'border-slate-800 hover:border-emerald-500/30',
  },
  amber: {
    iconBg: 'bg-amber-500/10 text-amber-400 border-amber-500/20',
    text: 'text-amber-400',
    border: 'border-slate-800 hover:border-amber-500/30',
  },
  rose: {
    iconBg: 'bg-rose-500/10 text-rose-400 border-rose-500/20',
    text: 'text-rose-400',
    border: 'border-slate-800 hover:border-rose-500/30',
  },
  sky: {
    iconBg: 'bg-sky-500/10 text-sky-400 border-sky-500/20',
    text: 'text-sky-400',
    border: 'border-slate-800 hover:border-sky-500/30',
  },
  slate: {
    iconBg: 'bg-slate-800 text-slate-300 border-slate-700',
    text: 'text-white',
    border: 'border-slate-800 hover:border-slate-700',
  },
};

export const StatCard: React.FC<StatCardProps> = ({
  title,
  value,
  icon: Icon,
  sublabel,
  statusText,
  variant = 'cyan',
  loading = false,
}) => {
  const styles = colorMap[variant] || colorMap.cyan;

  if (loading) {
    return (
      <div className="bg-slate-900/60 border border-slate-800 rounded-lg p-4 animate-pulse">
        <div className="flex justify-between items-center mb-3">
          <div className="h-3 w-20 bg-slate-800 rounded"></div>
          <div className="h-7 w-7 bg-slate-800 rounded-lg"></div>
        </div>
        <div className="h-7 w-14 bg-slate-800 rounded mb-2"></div>
        <div className="h-2.5 w-24 bg-slate-850 rounded"></div>
      </div>
    );
  }

  return (
    <div
      className={`bg-slate-900/60 border ${styles.border} rounded-lg p-4 transition-all duration-150 flex flex-col justify-between`}
    >
      <div className="flex items-center justify-between text-xs text-slate-400">
        <span className="font-medium tracking-tight truncate">{title}</span>
        <div className={`p-1.5 rounded-lg border ${styles.iconBg}`}>
          <Icon className="h-4 w-4" />
        </div>
      </div>

      <div className="mt-3">
        <div className={`text-2xl font-bold font-mono tracking-tight ${styles.text}`}>
          {value}
        </div>
        {(sublabel || statusText) && (
          <div className="mt-1 flex items-center justify-between text-[11px] text-slate-500">
            {sublabel && <span className="truncate">{sublabel}</span>}
            {statusText && (
              <span className={`font-medium ml-auto ${styles.text}`}>{statusText}</span>
            )}
          </div>
        )}
      </div>
    </div>
  );
};
