import React from 'react';
import { Track, Behaviour, Event } from '@/types';
import { Crosshair, Clock, ShieldAlert, ChevronRight } from 'lucide-react';

interface TrackCardProps {
  trackId: number;
  detections: Track[];
  behaviours: Behaviour[];
  events: Event[];
  isSelected: boolean;
  onSelect: (trackId: number) => void;
}

const formatTime = (seconds: number): string => {
  const mins = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
};

export const TrackCard: React.FC<TrackCardProps> = ({
  trackId,
  detections,
  behaviours,
  events,
  isSelected,
  onSelect,
}) => {
  const firstDetect = detections[0];
  const lastDetect = detections[detections.length - 1];

  const firstTimestamp = firstDetect?.timestamp || 0;
  const lastTimestamp = lastDetect?.timestamp || 0;

  const avgConfidence =
    detections.reduce((acc, d) => acc + d.confidence, 0) / (detections.length || 1);

  const latestBehaviour = behaviours[behaviours.length - 1]?.behaviour || 'Stationary';

  const abnormalCount = events.length;
  const hasHighRisk = events.some((e) => e.severity === 'high');

  return (
    <div
      onClick={() => onSelect(trackId)}
      className={`p-4 rounded-lg border transition-all duration-150 cursor-pointer space-y-3 ${
        isSelected
          ? 'bg-cyan-500/15 border-cyan-400 text-white shadow-md'
          : 'bg-slate-900/60 border-slate-800 hover:border-slate-700 hover:bg-slate-900/90 text-slate-300'
      }`}
    >
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="p-1.5 rounded-md bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
            <Crosshair className="h-4 w-4" />
          </div>
          <div>
            <span className="font-mono text-sm font-bold text-white">Person #{trackId}</span>
            <span className="text-[10px] text-slate-400 block capitalize">
              {firstDetect?.class || 'person'} • DeepSORT ID
            </span>
          </div>
        </div>

        {hasHighRisk ? (
          <span className="inline-flex items-center gap-1 text-[10px] font-mono font-bold px-2 py-0.5 rounded bg-rose-500/20 text-rose-300 border border-rose-500/30">
            <ShieldAlert className="h-3 w-3" />
            CRITICAL
          </span>
        ) : (
          <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-400">
            NOMINAL
          </span>
        )}
      </div>

      <div className="grid grid-cols-2 gap-2 text-[11px] font-mono bg-slate-950/60 p-2.5 rounded border border-slate-850">
        <div>
          <span className="text-slate-500 text-[10px] block">LIFESPAN</span>
          <span className="text-white flex items-center gap-1 mt-0.5">
            <Clock className="h-3 w-3 text-slate-400" />
            {formatTime(firstTimestamp)} – {formatTime(lastTimestamp)}
          </span>
        </div>
        <div>
          <span className="text-slate-500 text-[10px] block">AVG CONFIDENCE</span>
          <span className="text-emerald-400 font-bold mt-0.5 block">
            {(avgConfidence * 100).toFixed(0)}%
          </span>
        </div>
      </div>

      <div className="flex items-center justify-between text-xs pt-1 border-t border-slate-800/80">
        <span className="text-slate-400 text-[11px] truncate max-w-[140px]">
          Latest: <strong className="text-slate-200">{latestBehaviour}</strong>
        </span>
        <div className="flex items-center gap-1.5 text-cyan-400 text-xs font-semibold">
          <span>{abnormalCount > 0 ? `${abnormalCount} Alerts` : 'Inspected'}</span>
          <ChevronRight className="h-3 w-3" />
        </div>
      </div>
    </div>
  );
};
