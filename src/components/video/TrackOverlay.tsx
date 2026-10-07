import React from 'react';
import { Track, Behaviour, Event, Zone } from '@/types';
import { ShieldAlert, AlertTriangle } from 'lucide-react';

interface TrackOverlayProps {
  tracks: Track[];
  behaviours: Behaviour[];
  events: Event[];
  zones?: Zone[];
  currentTime: number;
  selectedTrackId: number | null;
  onSelectTrack: (trackId: number) => void;
  videoWidth?: number;
  videoHeight?: number;
  visible?: boolean;
  showZones?: boolean;
}

export const TrackOverlay: React.FC<TrackOverlayProps> = ({
  tracks,
  behaviours,
  events,
  zones = [],
  currentTime,
  selectedTrackId,
  onSelectTrack,
  videoWidth = 1920,
  videoHeight = 1080,
  visible = true,
  showZones = true,
}) => {
  if (!visible) return null;

  // Filter tracks relevant to current timestamp or selected track
  const activeTracks = tracks.filter((t) => {
    if (t.track_id === selectedTrackId) return true;
    return Math.abs(t.timestamp - currentTime) <= 8;
  });

  // Deduplicate by track_id, keeping the closest timestamp to currentTime
  const tracksToRenderMap = new Map<number, Track>();
  activeTracks.forEach((track) => {
    const existing = tracksToRenderMap.get(track.track_id);
    if (!existing || Math.abs(track.timestamp - currentTime) < Math.abs(existing.timestamp - currentTime)) {
      tracksToRenderMap.set(track.track_id, track);
    }
  });

  const tracksToRender = Array.from(tracksToRenderMap.values());

  // Check if any active track is inside a restricted zone at currentTime
  const isRestrictedZoneBreached = events.some(
    (e) => e.severity === 'high' && currentTime >= e.start_time && currentTime <= e.end_time
  );

  return (
    <div className="absolute inset-0 pointer-events-none overflow-hidden select-none z-20">
      {/* 1. Member 3 Backend Zones Overlay */}
      {showZones &&
        zones.map((zone) => {
          if (!zone.enabled || zone.coordinates.length < 2) return null;

          const isRestricted = zone.zone_type === 'restricted';
          const [p1, p2, p3] = zone.coordinates;
          const left = p1[0];
          const top = p1[1];
          const width = p2 ? Math.abs(p2[0] - p1[0]) : 40;
          const height = p3 ? Math.abs(p3[1] - p1[1]) : 50;

          return (
            <div
              key={zone.zone_id}
              className={`absolute border-2 border-dashed transition-all duration-300 pointer-events-none ${
                isRestricted
                  ? isRestrictedZoneBreached
                    ? 'border-rose-500 bg-rose-500/20 shadow-lg shadow-rose-500/20 animate-pulse'
                    : 'border-rose-500/70 bg-rose-500/10'
                  : 'border-amber-400/60 bg-amber-500/5'
              }`}
              style={{
                left: `${left}%`,
                top: `${top}%`,
                width: `${width}%`,
                height: `${height}%`,
              }}
            >
              {/* Zone Tag */}
              <div
                className={`absolute top-1 left-1 px-1.5 py-0.5 rounded text-[9px] font-mono font-bold uppercase tracking-wider flex items-center gap-1 border ${
                  isRestricted
                    ? isRestrictedZoneBreached
                      ? 'bg-rose-950 text-rose-300 border-rose-500'
                      : 'bg-rose-950/80 text-rose-400 border-rose-600/60'
                    : 'bg-amber-950/80 text-amber-300 border-amber-600/60'
                }`}
              >
                {isRestricted ? (
                  <ShieldAlert className="h-2.5 w-2.5 text-rose-400" />
                ) : (
                  <AlertTriangle className="h-2.5 w-2.5 text-amber-400" />
                )}
                <span>
                  {zone.name} {isRestrictedZoneBreached && isRestricted ? '// BREACH' : ''}
                </span>
              </div>
            </div>
          );
        })}

      {/* 2. Detected Entity Bounding Boxes */}
      {tracksToRender.map((track) => {
        const [x1, y1, x2, y2] = track.bbox;
        const isNormalized = x1 <= 1 && y1 <= 1 && x2 <= 1 && y2 <= 1;
        const leftPct = isNormalized ? x1 * 100 : (x1 / videoWidth) * 100;
        const topPct = isNormalized ? y1 * 100 : (y1 / videoHeight) * 100;
        const widthPct = isNormalized ? (x2 - x1) * 100 : ((x2 - x1) / videoWidth) * 100;
        const heightPct = isNormalized ? (y2 - y1) * 100 : ((y2 - y1) / videoHeight) * 100;

        const isSelected = track.track_id === selectedTrackId;

        // Current behaviour for this track at current time
        const currentBehaviour =
          behaviours.find(
            (b) => b.track_id === track.track_id && currentTime >= b.start_time && currentTime <= b.end_time
          ) || behaviours.filter((b) => b.track_id === track.track_id)[0];

        // Check if there is an active abnormal event for this track
        const activeEvent = events.find(
          (e) => e.track_id === track.track_id && currentTime >= e.start_time && currentTime <= e.end_time
        );

        const isHighRisk = activeEvent?.severity === 'high';
        const isMediumRisk = activeEvent?.severity === 'medium';

        let borderColor = 'border-cyan-400';
        let bgColor = 'bg-cyan-500/10';
        let tagBg = 'bg-cyan-950/90 text-cyan-300 border-cyan-500/60';

        if (isHighRisk) {
          borderColor = 'border-rose-500 animate-pulse';
          bgColor = 'bg-rose-500/15';
          tagBg = 'bg-rose-950/90 text-rose-200 border-rose-500/80';
        } else if (isMediumRisk) {
          borderColor = 'border-amber-400';
          bgColor = 'bg-amber-500/15';
          tagBg = 'bg-amber-950/90 text-amber-200 border-amber-500/80';
        } else if (isSelected) {
          borderColor = 'border-sky-300 ring-2 ring-sky-400/50';
          bgColor = 'bg-sky-500/20';
          tagBg = 'bg-sky-950/90 text-sky-200 border-sky-400';
        }

        return (
          <div
            key={track.track_id}
            onClick={(e) => {
              e.stopPropagation();
              onSelectTrack(track.track_id);
            }}
            className={`absolute border-2 transition-all duration-150 cursor-pointer pointer-events-auto ${borderColor} ${bgColor}`}
            style={{
              left: `${Math.max(2, Math.min(88, leftPct))}%`,
              top: `${Math.max(2, Math.min(85, topPct))}%`,
              width: `${Math.max(8, Math.min(50, widthPct))}%`,
              height: `${Math.max(12, Math.min(65, heightPct))}%`,
            }}
          >
            {/* Corner targets for CV Intelligence aesthetic */}
            <div className="absolute -top-1 -left-1 w-2 h-2 border-t-2 border-l-2 border-white" />
            <div className="absolute -top-1 -right-1 w-2 h-2 border-t-2 border-r-2 border-white" />
            <div className="absolute -bottom-1 -left-1 w-2 h-2 border-b-2 border-l-2 border-white" />
            <div className="absolute -bottom-1 -right-1 w-2 h-2 border-b-2 border-r-2 border-white" />

            {/* Top ID & Class Tag */}
            <div
              className={`absolute -top-7 left-0 px-2 py-0.5 rounded text-[10px] font-mono font-bold tracking-tight border flex items-center gap-1.5 shadow-md whitespace-nowrap ${tagBg}`}
            >
              <span>#{track.track_id}</span>
              <span className="capitalize">{track.class}</span>
              <span className="opacity-80">{(track.confidence * 100).toFixed(0)}%</span>
            </div>

            {/* Bottom Behaviour Tag */}
            {currentBehaviour && (
              <div
                className={`absolute -bottom-6 left-0 px-1.5 py-0.5 rounded text-[9px] font-mono font-medium tracking-tight border flex items-center gap-1 shadow-md whitespace-nowrap ${
                  isHighRisk
                    ? 'bg-rose-950/90 text-rose-300 border-rose-500/70'
                    : 'bg-slate-950/90 text-cyan-300 border-slate-700'
                }`}
              >
                <span className="truncate max-w-[130px]">{currentBehaviour.behaviour}</span>
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
};
