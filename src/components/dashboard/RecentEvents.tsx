import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Event } from '@/types';
import { ShieldAlert, AlertTriangle, Info, Clock, ChevronRight, AlertCircle, RefreshCw } from 'lucide-react';

interface RecentEventsProps {
  events: Event[];
  loading: boolean;
  error?: string | null;
  onRetry?: () => void;
}

const severityConfig = {
  high: {
    bg: 'bg-rose-500/10 text-rose-400 border-rose-500/30',
    dot: 'bg-rose-500',
    icon: ShieldAlert,
    label: 'HIGH',
  },
  medium: {
    bg: 'bg-amber-500/10 text-amber-400 border-amber-500/30',
    dot: 'bg-amber-400',
    icon: AlertTriangle,
    label: 'MED',
  },
  low: {
    bg: 'bg-sky-500/10 text-sky-400 border-sky-500/30',
    dot: 'bg-sky-400',
    icon: Info,
    label: 'LOW',
  },
};

const formatTime = (seconds: number): string => {
  const mins = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
};

export const RecentEvents: React.FC<RecentEventsProps> = ({
  events,
  loading,
  error,
  onRetry,
}) => {
  const navigate = useNavigate();

  return (
    <div className="bg-slate-900/60 border border-slate-800 rounded-lg p-5 flex flex-col h-full">
      <div className="flex items-center justify-between border-b border-slate-800/80 pb-3 mb-4">
        <div className="flex items-center gap-2">
          <div className="p-1 rounded bg-rose-500/10 text-rose-400 border border-rose-500/20">
            <ShieldAlert className="h-4 w-4" />
          </div>
          <div>
            <h2 className="text-sm font-semibold text-white">Recent Abnormal Events</h2>
            <p className="text-[11px] text-slate-400">High-priority alerts detected in camera streams</p>
          </div>
        </div>
        <button
          onClick={() => navigate('/events')}
          className="text-xs text-cyan-400 hover:text-cyan-300 font-medium flex items-center gap-1 transition-colors"
        >
          <span>View All</span>
          <ChevronRight className="h-3 w-3" />
        </button>
      </div>

      {/* Loading State */}
      {loading && (
        <div className="space-y-3 py-2 flex-1">
          {[1, 2, 3].map((i) => (
            <div
              key={i}
              className="p-3 rounded-lg border border-slate-800 bg-slate-950/40 animate-pulse flex items-center justify-between"
            >
              <div className="space-y-1.5 w-2/3">
                <div className="h-3.5 bg-slate-800 rounded w-1/3"></div>
                <div className="h-3 bg-slate-850 rounded w-1/2"></div>
              </div>
              <div className="h-6 w-16 bg-slate-800 rounded"></div>
            </div>
          ))}
        </div>
      )}

      {/* Error State */}
      {!loading && error && (
        <div className="flex-1 flex flex-col items-center justify-center p-6 text-center">
          <AlertCircle className="h-8 w-8 text-rose-400 mb-2" />
          <p className="text-xs font-semibold text-slate-200">Unable to load recent events</p>
          <p className="text-[11px] text-slate-500 mt-1 max-w-xs">{error}</p>
          {onRetry && (
            <button
              onClick={onRetry}
              className="mt-3 px-3 py-1.5 rounded-md bg-slate-800 hover:bg-slate-700 text-xs text-cyan-400 border border-slate-700 flex items-center gap-1.5 transition-colors"
            >
              <RefreshCw className="h-3 w-3" />
              <span>Retry</span>
            </button>
          )}
        </div>
      )}

      {/* Empty State */}
      {!loading && !error && events.length === 0 && (
        <div className="flex-1 flex flex-col items-center justify-center p-6 text-center border border-dashed border-slate-800/80 rounded-lg">
          <div className="p-2.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 mb-2">
            <ShieldAlert className="h-5 w-5" />
          </div>
          <p className="text-xs font-medium text-slate-300">No abnormal events detected</p>
          <p className="text-[11px] text-slate-500 mt-1">
            System running within baseline safety tolerances.
          </p>
        </div>
      )}

      {/* Events List */}
      {!loading && !error && events.length > 0 && (
        <div className="space-y-2.5 overflow-y-auto max-h-[360px] pr-1">
          {events.map((evt) => {
            const config = severityConfig[evt.severity] || severityConfig.medium;
            return (
              <div
                key={evt.event_id}
                onClick={() => navigate('/events')}
                className="group p-3 rounded-lg bg-slate-950/70 border border-slate-800/90 hover:border-cyan-500/40 hover:bg-slate-900/50 cursor-pointer transition-all duration-150 flex items-center justify-between gap-3"
              >
                <div className="space-y-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <span className="font-mono text-xs font-bold text-cyan-300">
                      Person #{evt.track_id}
                    </span>
                    <span className="text-slate-600">•</span>
                    <span className="text-xs font-medium text-white truncate">
                      {evt.event_type}
                    </span>
                  </div>
                  <div className="flex items-center gap-3 text-[11px] text-slate-400">
                    <span className="font-mono flex items-center gap-1 text-slate-400">
                      <Clock className="h-3 w-3 text-slate-500" />
                      {formatTime(evt.start_time)}
                    </span>
                    <span>Confidence: <strong className="font-mono text-slate-300">{(evt.confidence * 100).toFixed(0)}%</strong></span>
                  </div>
                  {evt.reason && (
                    <p className="text-[11px] text-slate-500 line-clamp-1 italic">
                      "{evt.reason}"
                    </p>
                  )}
                </div>

                <div className="shrink-0 flex flex-col items-end gap-1.5">
                  <span
                    className={`inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-mono font-bold tracking-wider uppercase border ${config.bg}`}
                  >
                    <span className={`h-1.5 w-1.5 rounded-full ${config.dot}`} />
                    {config.label}
                  </span>
                  <span className="text-[10px] font-mono text-slate-500 group-hover:text-cyan-400 flex items-center gap-0.5 transition-colors">
                    <span>Inspect</span>
                    <ChevronRight className="h-2.5 w-2.5" />
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
