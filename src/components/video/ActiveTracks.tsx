import React from 'react';
import { Track, Behaviour, Event } from '@/types';
import { Users, Crosshair, ChevronRight, Activity, ShieldAlert } from 'lucide-react';

interface ActiveTracksProps {
  tracks: Track[];
  behaviours: Behaviour[];
  events: Event[];
  selectedTrackId: number | null;
  currentTime: number;
  onSelectTrack: (trackId: number, seekTimestamp?: number) => void;
}

export const ActiveTracks: React.FC<ActiveTracksProps> = ({
  tracks,
  behaviours,
  events,
  selectedTrackId,
  currentTime,
  onSelectTrack,
}) => {
  // Aggregate unique track IDs
  const uniqueTrackIds = Array.from(new Set(tracks.map((t) => t.track_id))).sort((a, b) => a - b);

  return (
    <div className="bg-slate-900/60 border border-slate-800 rounded-lg p-4 flex flex-col h-full">
      <div className="flex items-center justify-between border-b border-slate-800/80 pb-3 mb-3">
        <div className="flex items-center gap-2">
          <div className="p-1 rounded bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
            <Users className="h-4 w-4" />
          </div>
          <div>
            <h3 className="text-xs font-semibold text-white">Active Tracks</h3>
            <p className="text-[10px] text-slate-400">DeepSORT Track ID allocations</p>
          </div>
        </div>
        <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-800 text-cyan-400 font-bold border border-slate-700">
          {uniqueTrackIds.length} Entities
        </span>
      </div>

      <div className="space-y-2 overflow-y-auto max-h-[280px] pr-1 flex-1">
        {uniqueTrackIds.map((id) => {
          const trackDetections = tracks.filter((t) => t.track_id === id);
          const firstDetection = trackDetections[0];
          const isSelected = id === selectedTrackId;

          // Find current behaviour at currentTime or fallback
          const currentBehaviour = behaviours.find(
            (b) => b.track_id === id && currentTime >= b.start_time && currentTime <= b.end_time
          ) || behaviours.filter((b) => b.track_id === id)[0];

          // Check if entity has any abnormal event
          const entityEvents = events.filter((e) => e.track_id === id);
          const hasHighRisk = entityEvents.some((e) => e.severity === 'high');

          // Average confidence
          const avgConfidence =
            trackDetections.reduce((acc, t) => acc + t.confidence, 0) / (trackDetections.length || 1);

          return (
            <div
              key={id}
              onClick={() => onSelectTrack(id, firstDetection?.timestamp)}
              className={`p-2.5 rounded-lg border transition-all duration-150 cursor-pointer flex items-center justify-between gap-2 ${
                isSelected
                  ? 'bg-cyan-500/15 border-cyan-400 text-white shadow-sm'
                  : 'bg-slate-950/70 border-slate-800 hover:border-slate-700 hover:bg-slate-900/60 text-slate-300'
              }`}
            >
              <div className="space-y-1 min-w-0">
                <div className="flex items-center gap-2">
                  <span className="font-mono text-xs font-bold text-cyan-300 flex items-center gap-1">
                    <Crosshair className="h-3 w-3 text-cyan-400" />
                    Person #{id}
                  </span>
                  <span className="text-[10px] text-slate-400 capitalize">
                    {firstDetection?.class || 'person'}
                  </span>
                  {hasHighRisk && (
                    <span className="p-0.5 rounded bg-rose-500/20 text-rose-400 border border-rose-500/30">
                      <ShieldAlert className="h-3 w-3" />
                    </span>
                  )}
                </div>

                <div className="flex items-center gap-2 text-[10px] text-slate-400">
                  <span className="truncate flex items-center gap-1 text-slate-300">
                    <Activity className="h-2.5 w-2.5 text-cyan-400" />
                    {currentBehaviour?.behaviour || 'Stationary'}
                  </span>
                  <span>•</span>
                  <span className="font-mono">{(avgConfidence * 100).toFixed(0)}% conf</span>
                </div>
              </div>

              <div className="shrink-0 flex items-center gap-1">
                <span className="text-[10px] font-mono text-cyan-400 group-hover:text-cyan-300">
                  Select
                </span>
                <ChevronRight className="h-3.5 w-3.5 text-slate-500" />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
