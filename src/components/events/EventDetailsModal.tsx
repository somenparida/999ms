import React, { useState } from 'react';
import { Event } from '@/types';
import { SeverityBadge } from './SeverityBadge';
import {
  X,
  Clock,
  Crosshair,
  FileText,
  Image as ImageIcon,
  ExternalLink,
  Play,
  AlertCircle,
} from 'lucide-react';

import { useNavigate } from 'react-router-dom';

interface EventDetailsModalProps {
  event: Event | null;
  onClose: () => void;
}

const formatTime = (seconds: number): string => {
  const mins = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
};

export const EventDetailsModal: React.FC<EventDetailsModalProps> = ({ event, onClose }) => {
  const navigate = useNavigate();
  const [imageLoaded, setImageLoaded] = useState(false);
  const [imageError, setImageError] = useState(false);
  const [evidenceMode, setEvidenceMode] = useState<'image' | 'clip'>('image');

  if (!event) return null;


  const durationSecs = Math.max(1, event.end_time - event.start_time);

  const handleOpenAnalysis = () => {
    navigate('/analysis');
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-xs select-none">
      <div
        className="relative w-full max-w-2xl bg-slate-950 border border-slate-800 rounded-xl shadow-2xl overflow-hidden flex flex-col max-h-[90vh]"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="px-6 py-4 border-b border-slate-800/90 flex items-center justify-between bg-slate-900/60">
          <div className="flex items-center gap-3">
            <span className="font-mono text-sm font-bold text-cyan-400 bg-cyan-950/80 px-2.5 py-1 rounded border border-cyan-800">
              {event.event_id}
            </span>
            <div>
              <h2 className="text-base font-bold text-white tracking-tight">{event.event_type}</h2>
              <p className="text-xs text-slate-400">Automated Vision Anomaly Dossier</p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <SeverityBadge severity={event.severity} />
            <button
              onClick={onClose}
              className="p-1 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors ml-2"
              aria-label="Close details"
            >
              <X className="h-5 w-5" />
            </button>
          </div>
        </div>

        {/* Content Body */}
        <div className="p-6 space-y-5 overflow-y-auto">
          {/* Metadata Grid */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            <div className="bg-slate-900/60 border border-slate-800/80 rounded-lg p-3">
              <span className="text-[10px] font-mono text-slate-400 block flex items-center gap-1">
                <Crosshair className="h-3 w-3 text-cyan-400" /> ENTITY
              </span>
              <span className="font-mono font-bold text-sm text-cyan-300 mt-1 block">
                Person #{event.track_id}
              </span>
            </div>

            <div className="bg-slate-900/60 border border-slate-800/80 rounded-lg p-3">
              <span className="text-[10px] font-mono text-slate-400 block flex items-center gap-1">
                <Clock className="h-3 w-3 text-slate-400" /> TIME WINDOW
              </span>
              <span className="font-mono font-bold text-xs text-white mt-1 block">
                {formatTime(event.start_time)} – {formatTime(event.end_time)}
              </span>
            </div>

            <div className="bg-slate-900/60 border border-slate-800/80 rounded-lg p-3">
              <span className="text-[10px] font-mono text-slate-400 block">DURATION</span>
              <span className="font-mono font-bold text-sm text-white mt-1 block">
                {durationSecs}s
              </span>
            </div>

            <div className="bg-slate-900/60 border border-slate-800/80 rounded-lg p-3">
              <span className="text-[10px] font-mono text-slate-400 block">CONFIDENCE</span>
              <span className="font-mono font-bold text-sm text-emerald-400 mt-1 block">
                {(event.confidence * 100).toFixed(0)}%
              </span>
            </div>
          </div>

          {/* Incident Description */}
          <div className="bg-slate-900/60 border border-slate-800 rounded-lg p-4 space-y-1.5">
            <div className="flex items-center gap-2 text-xs font-semibold text-slate-300">
              <FileText className="h-4 w-4 text-cyan-400" />
              <span>Event Classification Rationale</span>
            </div>
            <p className="text-xs text-slate-300 leading-relaxed font-sans pl-6">
              {event.reason || 'Entity exceeded normal spatial behavioral tolerances.'}
            </p>
          </div>

          {/* Evidence Viewer (Image Snapshot & Video Clip) */}
          <div className="bg-slate-900/60 border border-slate-800 rounded-lg p-4 space-y-3">
            <div className="flex items-center justify-between text-xs font-semibold text-slate-300">
              <div className="flex items-center gap-2">
                <ImageIcon className="h-4 w-4 text-cyan-400" />
                <span>Forensic Incident Evidence</span>
              </div>
              
              {/* Evidence Media Mode Toggle (Photo Snapshot vs Video Clip) */}
              <div className="flex items-center gap-1 bg-slate-950 p-0.5 rounded-lg border border-slate-800 text-[10px] font-mono">
                <button
                  type="button"
                  onClick={() => setEvidenceMode('image')}
                  className={`px-2 py-0.5 rounded transition-colors ${
                    evidenceMode === 'image'
                      ? 'bg-cyan-500/20 text-cyan-300 font-bold border border-cyan-500/40'
                      : 'text-slate-400 hover:text-slate-200'
                  }`}
                >
                  Keyframe Image
                </button>
                <button
                  type="button"
                  onClick={() => setEvidenceMode('clip')}
                  className={`px-2 py-0.5 rounded transition-colors ${
                    evidenceMode === 'clip'
                      ? 'bg-cyan-500/20 text-cyan-300 font-bold border border-cyan-500/40'
                      : 'text-slate-400 hover:text-slate-200'
                  }`}
                >
                  Event Clip (.mp4)
                </button>
              </div>
            </div>

            {evidenceMode === 'clip' && event.clip_url ? (
              <div className="relative aspect-video rounded-lg overflow-hidden border border-slate-800 bg-black flex flex-col justify-center items-center">
                <video
                  src={event.clip_url}
                  controls
                  autoPlay
                  muted
                  playsInline
                  className="w-full h-full object-contain"
                />
                <div className="absolute top-2 left-2 px-2 py-0.5 rounded bg-black/80 backdrop-blur-xs text-[9px] font-mono text-cyan-400 border border-cyan-800/80 pointer-events-none">
                  STORAGE: /storage/event_clips/{event.event_id}.mp4
                </div>
              </div>
            ) : event.evidence_url ? (
              <div className="relative aspect-video rounded-lg overflow-hidden border border-slate-800 bg-black flex items-center justify-center">
                {!imageLoaded && !imageError && (
                  <div className="text-xs font-mono text-slate-400 animate-pulse">
                    Loading high-resolution evidence buffer...
                  </div>
                )}
                {imageError ? (
                  <div className="flex flex-col items-center text-xs text-slate-500">
                    <AlertCircle className="h-6 w-6 text-slate-600 mb-1" />
                    <span>Evidence image preview currently unavailable</span>
                  </div>
                ) : (
                  <img
                    src={event.evidence_url}
                    alt={`Evidence for ${event.event_id}`}
                    onLoad={() => setImageLoaded(true)}
                    onError={() => setImageError(true)}
                    className="w-full h-full object-cover"
                  />
                )}
                <div className="absolute bottom-2 left-2 px-2 py-1 rounded bg-black/80 backdrop-blur-xs text-[10px] font-mono text-cyan-300 border border-cyan-800/80">
                  TIMESTAMP: {formatTime(event.start_time)} // CAMERA 04 // STORAGE: /storage/evidence/
                </div>
              </div>
            ) : (
              <div className="aspect-video rounded-lg border border-dashed border-slate-800 flex flex-col items-center justify-center text-xs text-slate-500 p-4">
                <ImageIcon className="h-8 w-8 text-slate-700 mb-2" />
                <span>No photographic evidence file linked for this record.</span>
              </div>
            )}
          </div>

        </div>

        {/* Action Footer */}
        <div className="px-6 py-3.5 border-t border-slate-800/90 bg-slate-900/40 flex items-center justify-between">
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs font-semibold text-slate-300 transition-colors"
          >
            Close Dossier
          </button>

          <button
            onClick={handleOpenAnalysis}
            className="px-4 py-2 rounded-lg bg-cyan-500/20 hover:bg-cyan-500/30 text-xs font-semibold text-cyan-300 border border-cyan-500/40 flex items-center gap-2 transition-colors shadow-sm"
          >
            <Play className="h-3.5 w-3.5 fill-cyan-400" />
            <span>Inspect in Video Analysis Workspace</span>
            <ExternalLink className="h-3.5 w-3.5" />
          </button>
        </div>
      </div>
    </div>
  );
};
