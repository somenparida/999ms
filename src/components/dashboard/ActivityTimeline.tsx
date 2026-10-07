import React from 'react';
import { TimelineEntry } from '@/types';
import { Clock, Activity, AlertCircle, ArrowUpRight } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

interface ActivityTimelineProps {
  timeline: TimelineEntry[];
  loading: boolean;
  error?: string | null;
}

export const ActivityTimeline: React.FC<ActivityTimelineProps> = ({
  timeline,
  loading,
  error,
}) => {
  const navigate = useNavigate();

  return (
    <div className="bg-slate-900/60 border border-slate-800 rounded-lg p-5 flex flex-col h-full">
      <div className="flex items-center justify-between border-b border-slate-800/80 pb-3 mb-4">
        <div className="flex items-center gap-2">
          <div className="p-1 rounded bg-sky-500/10 text-sky-400 border border-sky-500/20">
            <Activity className="h-4 w-4" />
          </div>
          <div>
            <h2 className="text-sm font-semibold text-white">Live Activity Timeline</h2>
            <p className="text-[11px] text-slate-400">Sequential detection telemetry and state changes</p>
          </div>
        </div>
        <button
          onClick={() => navigate('/analysis')}
          className="text-xs text-cyan-400 hover:text-cyan-300 font-medium flex items-center gap-1 transition-colors"
        >
          <span>Open Analysis Workspace</span>
          <ArrowUpRight className="h-3 w-3" />
        </button>
      </div>

      {loading && (
        <div className="space-y-4 py-2 flex-1">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="flex gap-3 animate-pulse">
              <div className="h-8 w-14 bg-slate-800 rounded shrink-0"></div>
              <div className="flex-1 space-y-1.5">
                <div className="h-3 bg-slate-800 rounded w-1/3"></div>
                <div className="h-3 bg-slate-850 rounded w-3/4"></div>
              </div>
            </div>
          ))}
        </div>
      )}

      {!loading && error && (
        <div className="flex-1 flex flex-col items-center justify-center p-6 text-center">
          <AlertCircle className="h-7 w-7 text-rose-400 mb-2" />
          <p className="text-xs font-semibold text-slate-200">Failed to load activity stream</p>
          <p className="text-[11px] text-slate-500 mt-1">{error}</p>
        </div>
      )}

      {!loading && !error && timeline.length === 0 && (
        <div className="flex-1 flex flex-col items-center justify-center p-6 text-center border border-dashed border-slate-800 rounded-lg">
          <p className="text-xs text-slate-400">No activity recorded for this period.</p>
        </div>
      )}

      {!loading && !error && timeline.length > 0 && (
        <div className="relative pl-4 space-y-4 before:absolute before:left-2 before:top-2 before:bottom-2 before:w-px before:bg-slate-800">
          {timeline.map((item, idx) => {
            const isAbnormal = item.type === 'event';
            return (
              <div key={idx} className="relative flex items-start gap-3 group">
                {/* Node dot on timeline */}
                <div
                  className={`absolute -left-4 top-1.5 h-2 w-2 rounded-full border-2 border-slate-950 ${
                    isAbnormal ? 'bg-rose-500 ring-2 ring-rose-500/20' : 'bg-cyan-400 ring-2 ring-cyan-400/20'
                  }`}
                />

                <div className="flex flex-col sm:flex-row sm:items-center gap-1 sm:gap-3 flex-1 min-w-0">
                  <span className="font-mono text-[11px] font-semibold text-slate-400 shrink-0 flex items-center gap-1">
                    <Clock className="h-3 w-3 text-slate-500" />
                    {item.formatted_time}
                  </span>

                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <span className="font-mono text-xs font-bold text-cyan-300">
                        Person #{item.track_id}
                      </span>
                      <span className="text-xs text-slate-200 font-medium truncate">
                        {item.label}
                      </span>
                      {item.severity && (
                        <span
                          className={`text-[9px] font-mono px-1.5 py-0.2 rounded font-bold uppercase ${
                            item.severity === 'high'
                              ? 'bg-rose-500/20 text-rose-300'
                              : item.severity === 'medium'
                              ? 'bg-amber-500/20 text-amber-300'
                              : 'bg-sky-500/20 text-sky-300'
                          }`}
                        >
                          {item.severity}
                        </span>
                      )}
                    </div>
                    {item.description && (
                      <p className="text-[11px] text-slate-400 truncate mt-0.5">
                        {item.description}
                      </p>
                    )}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
