import React from 'react';
import { Event } from '@/types';
import { ShieldAlert, AlertTriangle, Clock, CheckCircle2, Image as ImageIcon, ExternalLink } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

interface CurrentAlertPanelProps {
  activeEvent: Event | null;
  currentTime: number;
}

const formatTime = (seconds: number): string => {
  const mins = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
};

export const CurrentAlertPanel: React.FC<CurrentAlertPanelProps> = ({
  activeEvent,
  currentTime,
}) => {
  const navigate = useNavigate();

  return (
    <div className="bg-slate-900/60 border border-slate-800 rounded-lg p-4 flex flex-col h-full">
      <div className="flex items-center justify-between border-b border-slate-800/80 pb-3 mb-3">
        <div className="flex items-center gap-2">
          <div
            className={`p-1 rounded ${
              activeEvent
                ? activeEvent.severity === 'high'
                  ? 'bg-rose-500/10 text-rose-400 border border-rose-500/30'
                  : 'bg-amber-500/10 text-amber-400 border border-amber-500/30'
                : 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30'
            }`}
          >
            {activeEvent ? (
              activeEvent.severity === 'high' ? (
                <ShieldAlert className="h-4 w-4" />
              ) : (
                <AlertTriangle className="h-4 w-4" />
              )
            ) : (
              <CheckCircle2 className="h-4 w-4" />
            )}
          </div>
          <div>
            <h3 className="text-xs font-semibold text-white">Current Anomaly Status</h3>
            <p className="text-[10px] text-slate-400">Timestamp: {formatTime(currentTime)}</p>
          </div>
        </div>

        {activeEvent && (
          <span
            className={`text-[10px] font-mono font-bold px-2 py-0.5 rounded uppercase tracking-wider border ${
              activeEvent.severity === 'high'
                ? 'bg-rose-500/20 text-rose-300 border-rose-500/40 animate-pulse'
                : activeEvent.severity === 'medium'
                ? 'bg-amber-500/20 text-amber-300 border-amber-500/40'
                : 'bg-sky-500/20 text-sky-300 border-sky-500/40'
            }`}
          >
            {activeEvent.severity} RISK
          </span>
        )}
      </div>

      {/* No Active Alert View */}
      {!activeEvent && (
        <div className="flex-1 flex flex-col items-center justify-center p-4 text-center border border-dashed border-slate-800/80 rounded-lg">
          <div className="p-2 rounded-full bg-emerald-500/10 text-emerald-400 mb-2">
            <CheckCircle2 className="h-5 w-5" />
          </div>
          <p className="text-xs font-medium text-slate-300">No active alerts</p>
          <p className="text-[10px] text-slate-500 mt-0.5 max-w-[200px]">
            Target stream conforms to standard safety behaviors.
          </p>
        </div>
      )}

      {/* Active Alert Detailed View */}
      {activeEvent && (
        <div className="space-y-3 flex-1 flex flex-col justify-between">
          <div className="space-y-2.5">
            <div className="p-3 rounded-lg bg-slate-950/80 border border-slate-800 space-y-1.5">
              <div className="flex items-center justify-between">
                <span className="font-mono text-xs font-bold text-cyan-300">
                  Person #{activeEvent.track_id}
                </span>
                <span className="font-mono text-[10px] text-slate-400">
                  {activeEvent.event_id}
                </span>
              </div>
              <h4 className="text-sm font-bold text-white tracking-tight">
                {activeEvent.event_type}
              </h4>
              <p className="text-[11px] text-slate-400 leading-relaxed">
                {activeEvent.reason}
              </p>
            </div>

            {/* Metrics */}
            <div className="grid grid-cols-2 gap-2 text-[11px] font-mono">
              <div className="p-2 rounded bg-slate-950 border border-slate-800">
                <span className="text-slate-500 block text-[10px]">CONFIDENCE</span>
                <span className="font-bold text-white text-xs">
                  {(activeEvent.confidence * 100).toFixed(0)}%
                </span>
              </div>

              <div className="p-2 rounded bg-slate-950 border border-slate-800">
                <span className="text-slate-500 block text-[10px]">TIME WINDOW</span>
                <span className="font-bold text-cyan-400 text-xs flex items-center gap-1">
                  <Clock className="h-3 w-3 inline text-slate-500" />
                  {formatTime(activeEvent.start_time)} – {formatTime(activeEvent.end_time)}
                </span>
              </div>
            </div>

            {/* Evidence Image Card */}
            {activeEvent.evidence_url && (
              <div className="p-2 rounded bg-slate-950 border border-slate-800 space-y-1.5">
                <div className="flex items-center justify-between text-[10px]">
                  <span className="text-slate-400 flex items-center gap-1">
                    <ImageIcon className="h-3 w-3 text-cyan-400" />
                    Keyframe Evidence Captured
                  </span>
                  <span className="font-mono text-emerald-400 font-semibold uppercase">
                    Available
                  </span>
                </div>
                <div className="aspect-video w-full rounded overflow-hidden relative border border-slate-800 bg-black">
                  <img
                    src={activeEvent.evidence_url}
                    alt="Anomaly evidence frame"
                    className="w-full h-full object-cover"
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-black/70 via-transparent to-transparent flex items-end p-1.5">
                    <span className="text-[9px] font-mono text-slate-300">
                      FRAME @ {formatTime(activeEvent.start_time)}
                    </span>
                  </div>
                </div>
              </div>
            )}
          </div>

          <button
            onClick={() => navigate('/events')}
            className="w-full mt-2 py-1.5 px-3 rounded-lg bg-slate-800 hover:bg-slate-750 text-xs font-medium text-cyan-300 border border-slate-700 flex items-center justify-center gap-1.5 transition-colors"
          >
            <span>Inspect Complete Event Log</span>
            <ExternalLink className="h-3 w-3" />
          </button>
        </div>
      )}
    </div>
  );
};
