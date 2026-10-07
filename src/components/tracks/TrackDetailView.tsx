import React from 'react';
import { Track, Behaviour, Event } from '@/types';
import { BehaviourTimeline } from './BehaviourTimeline';
import {
  Crosshair,
  Clock,
  Play,
  ExternalLink,
  ShieldAlert,
  Calendar,
  MapPin,
} from 'lucide-react';

import { useNavigate } from 'react-router-dom';

interface TrackDetailViewProps {
  trackId: number;
  detections: Track[];
  behaviours: Behaviour[];
  events: Event[];
}

const formatTime = (seconds: number): string => {
  const mins = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
};

export const TrackDetailView: React.FC<TrackDetailViewProps> = ({
  trackId,
  detections,
  behaviours,
  events,
}) => {
  const navigate = useNavigate();

  const firstDetect = detections[0];
  const lastDetect = detections[detections.length - 1];

  const firstTime = firstDetect?.timestamp || 0;
  const lastTime = lastDetect?.timestamp || 0;
  const trackedDuration = Math.max(1, Math.round(lastTime - firstTime));

  const avgConfidence =
    detections.reduce((acc, d) => acc + d.confidence, 0) / (detections.length || 1);

  return (
    <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-5 space-y-6">
      {/* Detail Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-4">
        <div className="flex items-center gap-3">
          <div className="h-11 w-11 rounded-lg bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center text-cyan-400">
            <Crosshair className="h-6 w-6" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-lg font-bold text-white tracking-tight">Person #{trackId}</h2>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-cyan-950 text-cyan-300 border border-cyan-800 uppercase font-semibold">
                Class: {firstDetect?.class || 'person'}
              </span>
            </div>
            <p className="text-xs text-slate-400 mt-0.5">
              Trajectory and behavioural state history in active sector
            </p>
          </div>
        </div>

        <button
          onClick={() => navigate('/analysis')}
          className="px-3.5 py-2 rounded-lg bg-cyan-500/15 hover:bg-cyan-500/25 text-cyan-300 border border-cyan-500/40 text-xs font-semibold flex items-center gap-2 transition-all shadow-sm"
        >
          <Play className="h-3.5 w-3.5 fill-cyan-400" />
          <span>Inspect in Video Analysis</span>
          <ExternalLink className="h-3 w-3" />
        </button>
      </div>

      {/* KPI Stats Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <div className="bg-slate-950/70 border border-slate-800 rounded-lg p-3">
          <span className="text-[10px] font-mono text-slate-400 block flex items-center gap-1">
            <Calendar className="h-3 w-3 text-cyan-400" /> FIRST DETECTED
          </span>
          <span className="font-mono font-bold text-sm text-white mt-1 block">
            {formatTime(firstTime)}
          </span>
        </div>

        <div className="bg-slate-950/70 border border-slate-800 rounded-lg p-3">
          <span className="text-[10px] font-mono text-slate-400 block flex items-center gap-1">
            <Clock className="h-3 w-3 text-cyan-400" /> LAST DETECTED
          </span>
          <span className="font-mono font-bold text-sm text-white mt-1 block">
            {formatTime(lastTime)}
          </span>
        </div>

        <div className="bg-slate-950/70 border border-slate-800 rounded-lg p-3">
          <span className="text-[10px] font-mono text-slate-400 block">TOTAL TRACK DURATION</span>
          <span className="font-mono font-bold text-sm text-cyan-300 mt-1 block">
            {trackedDuration}s
          </span>
        </div>

        <div className="bg-slate-950/70 border border-slate-800 rounded-lg p-3">
          <span className="text-[10px] font-mono text-slate-400 block">AVG CONFIDENCE</span>
          <span className="font-mono font-bold text-sm text-emerald-400 mt-1 block">
            {(avgConfidence * 100).toFixed(0)}%
          </span>
        </div>
      </div>

      {/* Associated Abnormal Events */}
      <div className="space-y-3">
        <h3 className="text-xs font-bold text-white uppercase tracking-wider font-mono flex items-center gap-2">
          <ShieldAlert className="h-4 w-4 text-rose-400" />
          Associated Abnormal Events ({events.length})
        </h3>

        {events.length === 0 ? (
          <div className="p-4 rounded-lg bg-slate-950/50 border border-dashed border-slate-800 text-xs text-slate-500 text-center">
            Zero abnormal behavior breaches recorded for Person #{trackId}.
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {events.map((evt) => (
              <div
                key={evt.event_id}
                onClick={() => navigate('/events')}
                className="p-3 rounded-lg bg-slate-950/80 border border-slate-800 hover:border-slate-700 cursor-pointer transition-colors space-y-1.5"
              >
                <div className="flex items-center justify-between">
                  <span className="font-mono text-xs font-bold text-cyan-300">
                    {evt.event_id}
                  </span>
                  <span
                    className={`text-[9px] font-mono px-2 py-0.5 rounded font-bold uppercase border ${
                      evt.severity === 'high'
                        ? 'bg-rose-500/10 text-rose-400 border-rose-500/30'
                        : evt.severity === 'medium'
                        ? 'bg-amber-500/10 text-amber-400 border-amber-500/30'
                        : 'bg-sky-500/10 text-sky-400 border-sky-500/30'
                    }`}
                  >
                    {evt.severity} RISK
                  </span>
                </div>
                <p className="text-xs font-semibold text-white">{evt.event_type}</p>
                <p className="text-[11px] text-slate-400 line-clamp-2">{evt.reason}</p>
                <div className="text-[10px] font-mono text-slate-500 flex items-center gap-1 pt-1">
                  <Clock className="h-2.5 w-2.5" />
                  {formatTime(evt.start_time)} – {formatTime(evt.end_time)}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Behaviour Timeline */}
      <div className="space-y-3">
        <h3 className="text-xs font-bold text-white uppercase tracking-wider font-mono flex items-center gap-2">
          <Clock className="h-4 w-4 text-cyan-400" />
          Sequential Behaviour Timeline
        </h3>
        <BehaviourTimeline behaviours={behaviours} />
      </div>

      {/* Spatial Trajectory & Track Positions (models/TrackPosition in readme_backend.md) */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <h3 className="text-xs font-bold text-white uppercase tracking-wider font-mono flex items-center gap-2">
            <MapPin className="h-4 w-4 text-cyan-400" />
            Track Trajectory Coordinates &amp; Positions ({detections.length})
          </h3>
          <span className="text-[10px] font-mono text-slate-500">
            models/TrackPosition (PostgreSQL)
          </span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-2.5 max-h-48 overflow-y-auto p-1">
          {detections.map((det, idx) => (
            <div
              key={`${det.track_id}-${det.timestamp}-${idx}`}
              className="p-2.5 rounded-lg bg-slate-950/70 border border-slate-800 text-[11px] font-mono space-y-1"
            >
              <div className="flex items-center justify-between text-slate-400">
                <span className="text-cyan-400 font-bold">T = {det.timestamp.toFixed(1)}s</span>
                <span className="text-[10px] text-emerald-400">{(det.confidence * 100).toFixed(0)}% conf</span>
              </div>
              <div className="text-slate-300 text-[10px] bg-slate-900/80 px-2 py-1 rounded border border-slate-800/80 flex justify-between">
                <span>[x1, y1]: {det.bbox[0]}, {det.bbox[1]}</span>
                <span>[x2, y2]: {det.bbox[2]}, {det.bbox[3]}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

