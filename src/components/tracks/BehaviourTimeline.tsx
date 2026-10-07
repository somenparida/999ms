import React from 'react';
import { Behaviour } from '@/types';
import { Activity, Clock, ArrowRight } from 'lucide-react';

interface BehaviourTimelineProps {
  behaviours: Behaviour[];
  loading?: boolean;
}

const formatTime = (seconds: number): string => {
  const mins = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
};

export const BehaviourTimeline: React.FC<BehaviourTimelineProps> = ({
  behaviours,
  loading = false,
}) => {
  if (loading) {
    return (
      <div className="space-y-3 py-4 animate-pulse">
        {[1, 2, 3].map((i) => (
          <div key={i} className="h-10 bg-slate-800 rounded"></div>
        ))}
      </div>
    );
  }

  if (behaviours.length === 0) {
    return (
      <div className="p-6 text-center border border-dashed border-slate-800 rounded-lg text-xs text-slate-500">
        No state transitions or behavior records cataloged for this entity.
      </div>
    );
  }

  return (
    <div className="relative pl-6 space-y-4 before:absolute before:left-2.5 before:top-2 before:bottom-2 before:w-0.5 before:bg-slate-800">
      {behaviours.map((b, idx) => {
        const isAlertState =
          b.behaviour.toLowerCase().includes('restricted') ||
          b.behaviour.toLowerCase().includes('fall') ||
          b.behaviour.toLowerCase().includes('loitering');

        return (
          <div key={idx} className="relative group">
            {/* Timeline node */}
            <div
              className={`absolute -left-6 top-1.5 h-3 w-3 rounded-full border-2 border-slate-950 ${
                isAlertState
                  ? 'bg-rose-500 ring-2 ring-rose-500/30'
                  : 'bg-cyan-400 ring-2 ring-cyan-400/20'
              }`}
            />

            <div className="bg-slate-950/80 border border-slate-800/90 hover:border-slate-700 rounded-lg p-3 transition-colors">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-1">
                <div className="flex items-center gap-2">
                  <span className="font-mono text-xs font-bold text-white flex items-center gap-1.5">
                    <Activity className="h-3.5 w-3.5 text-cyan-400" />
                    {b.behaviour}
                  </span>
                  {isAlertState && (
                    <span className="px-1.5 py-0.2 rounded text-[9px] font-mono font-bold bg-rose-500/20 text-rose-300 border border-rose-500/30 uppercase">
                      Anomaly Phase
                    </span>
                  )}
                </div>

                <div className="flex items-center gap-2 text-[11px] font-mono text-slate-400">
                  <span className="flex items-center gap-1">
                    <Clock className="h-3 w-3 text-slate-500" />
                    {formatTime(b.start_time)}
                    <ArrowRight className="h-2.5 w-2.5 text-slate-600 inline" />
                    {formatTime(b.end_time)}
                  </span>
                  <span>({Math.max(1, b.end_time - b.start_time)}s)</span>
                  <span className="text-emerald-400">{(b.confidence * 100).toFixed(0)}%</span>
                </div>
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
};
