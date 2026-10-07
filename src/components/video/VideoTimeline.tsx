import React, { useRef } from 'react';
import { Event, Behaviour } from '@/types';
import { Clock, ShieldAlert, AlertTriangle, Info } from 'lucide-react';

interface VideoTimelineProps {
  currentTime: number;
  duration: number;
  events: Event[];
  behaviours: Behaviour[];
  selectedEventId: string | null;
  onSeek: (time: number) => void;
  onSelectEvent: (event: Event) => void;
}

const formatTime = (seconds: number): string => {
  if (isNaN(seconds) || seconds < 0) return '00:00';
  const mins = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
};

export const VideoTimeline: React.FC<VideoTimelineProps> = ({
  currentTime,
  duration,
  events,
  selectedEventId,
  onSeek,
  onSelectEvent,
}) => {
  const timelineRef = useRef<HTMLDivElement>(null);

  const safeDuration = duration > 0 ? duration : 151; // default to 02:31 if not loaded
  const progressPercent = Math.min(100, Math.max(0, (currentTime / safeDuration) * 100));

  const handleTimelineClick = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!timelineRef.current) return;
    const rect = timelineRef.current.getBoundingClientRect();
    const clickX = e.clientX - rect.left;
    const clickRatio = Math.max(0, Math.min(1, clickX / rect.width));
    const newTime = clickRatio * safeDuration;
    onSeek(newTime);
  };

  return (
    <div className="bg-slate-900/90 border border-slate-800 rounded-lg p-3 space-y-2 select-none">
      {/* Top Header: Time display + Event Markers legend */}
      <div className="flex items-center justify-between text-xs">
        <div className="flex items-center gap-2 font-mono">
          <Clock className="h-3.5 w-3.5 text-cyan-400" />
          <span className="font-bold text-white text-sm">{formatTime(currentTime)}</span>
          <span className="text-slate-500">/</span>
          <span className="text-slate-400">{formatTime(safeDuration)}</span>
        </div>

        <div className="flex items-center gap-3 text-[11px] font-mono text-slate-400">
          <span className="flex items-center gap-1">
            <span className="h-2 w-2 rounded-full bg-rose-500" /> High Anomaly
          </span>
          <span className="flex items-center gap-1">
            <span className="h-2 w-2 rounded-full bg-amber-400" /> Medium Anomaly
          </span>
          <span className="flex items-center gap-1">
            <span className="h-2 w-2 rounded-full bg-sky-400" /> Low Risk
          </span>
        </div>
      </div>

      {/* Main Interactive Timeline Bar */}
      <div
        ref={timelineRef}
        onClick={handleTimelineClick}
        className="relative h-8 bg-slate-950 rounded-md border border-slate-800 cursor-pointer overflow-visible flex items-center group"
      >
        {/* Background Track grid ticks */}
        <div className="absolute inset-0 flex justify-between px-2 items-center pointer-events-none opacity-20">
          {[...Array(11)].map((_, i) => (
            <div key={i} className="h-2 w-px bg-slate-500" />
          ))}
        </div>

        {/* Progress Fill */}
        <div
          className="absolute left-0 top-0 bottom-0 bg-cyan-500/20 border-r-2 border-cyan-400 pointer-events-none transition-all duration-75"
          style={{ width: `${progressPercent}%` }}
        />

        {/* Current Time Scrubber Needle */}
        <div
          className="absolute top-0 bottom-0 w-0.5 bg-cyan-400 z-30 pointer-events-none shadow-sm shadow-cyan-400"
          style={{ left: `${progressPercent}%` }}
        >
          <div className="absolute -top-1 -left-1.5 w-3.5 h-3.5 bg-cyan-400 rounded-full shadow-md flex items-center justify-center">
            <div className="w-1.5 h-1.5 bg-slate-950 rounded-full" />
          </div>
        </div>

        {/* Event Markers Overlay */}
        {events.map((evt) => {
          const markerPos = (evt.start_time / safeDuration) * 100;
          const isSelected = evt.event_id === selectedEventId;
          const isHigh = evt.severity === 'high';
          const isMed = evt.severity === 'medium';

          const markerBg = isHigh ? 'bg-rose-500' : isMed ? 'bg-amber-400' : 'bg-sky-400';
          const ringColor = isHigh ? 'ring-rose-500/40' : isMed ? 'ring-amber-400/40' : 'ring-sky-400/40';

          return (
            <div
              key={evt.event_id}
              onClick={(e) => {
                e.stopPropagation();
                onSeek(evt.start_time);
                onSelectEvent(evt);
              }}
              style={{ left: `${Math.min(97, Math.max(3, markerPos))}%` }}
              className="absolute z-20 -translate-x-1/2 group/marker cursor-pointer py-1"
            >
              {/* Event Marker Pin */}
              <div
                className={`w-3 h-5 rounded-sm flex items-center justify-center transition-transform hover:scale-125 ${markerBg} ${
                  isSelected ? 'ring-4 ' + ringColor + ' scale-125' : ''
                }`}
              >
                {isHigh ? (
                  <ShieldAlert className="h-2.5 w-2.5 text-white" />
                ) : isMed ? (
                  <AlertTriangle className="h-2.5 w-2.5 text-slate-950" />
                ) : (
                  <Info className="h-2.5 w-2.5 text-slate-950" />
                )}
              </div>

              {/* Marker Tooltip on Hover */}
              <div className="absolute bottom-7 left-1/2 -translate-x-1/2 hidden group-hover/marker:flex flex-col items-center z-40 pointer-events-none">
                <div className="bg-slate-950 border border-slate-700 px-2 py-1 rounded text-[10px] font-mono shadow-xl whitespace-nowrap space-y-0.5">
                  <div className="font-bold text-white flex items-center gap-1">
                    <span>{evt.event_id}:</span>
                    <span className="text-cyan-300 font-semibold">{evt.event_type}</span>
                  </div>
                  <div className="text-slate-400 flex items-center justify-between gap-2">
                    <span>Person #{evt.track_id}</span>
                    <span>{formatTime(evt.start_time)}</span>
                  </div>
                </div>
                <div className="w-1.5 h-1.5 bg-slate-950 border-r border-b border-slate-700 rotate-45 -mt-1" />
              </div>
            </div>
          );
        })}
      </div>

      {/* Event Range Markers Footer */}
      <div className="flex items-center justify-between text-[10px] font-mono text-slate-500 pt-0.5">
        <span>00:00</span>
        <div className="flex gap-2">
          {events.map((evt) => (
            <button
              key={evt.event_id}
              onClick={() => {
                onSeek(evt.start_time);
                onSelectEvent(evt);
              }}
              className={`px-1.5 py-0.5 rounded transition-colors ${
                evt.event_id === selectedEventId
                  ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40'
                  : 'hover:text-slate-300 hover:bg-slate-800'
              }`}
            >
              {evt.event_id} ({formatTime(evt.start_time)})
            </button>
          ))}
        </div>
        <span>{formatTime(safeDuration)}</span>
      </div>
    </div>
  );
};
