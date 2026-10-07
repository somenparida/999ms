import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Video, AnalysisStatus } from '@/types';
import { Video as VideoIcon, CheckCircle2, Play, ExternalLink } from 'lucide-react';

interface ActiveVideoBannerProps {
  video: Video | null;
  status: AnalysisStatus | null;
  loading: boolean;
}

export const ActiveVideoBanner: React.FC<ActiveVideoBannerProps> = ({
  video,
  status,
  loading,
}) => {
  const navigate = useNavigate();

  if (loading) {
    return (
      <div className="bg-slate-900/40 border border-slate-800 rounded-lg p-4 animate-pulse flex justify-between items-center">
        <div className="space-y-2 w-1/2">
          <div className="h-4 bg-slate-800 rounded w-1/3"></div>
          <div className="h-3 bg-slate-850 rounded w-2/3"></div>
        </div>
        <div className="h-8 w-32 bg-slate-800 rounded"></div>
      </div>
    );
  }

  if (!video) return null;

  return (
    <div className="bg-gradient-to-r from-slate-900/90 via-slate-900/60 to-slate-950 border border-slate-800 rounded-lg p-4 flex flex-col md:flex-row md:items-center justify-between gap-4">
      <div className="flex items-start gap-3">
        <div className="h-10 w-10 rounded-lg bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center text-cyan-400 shrink-0">
          <VideoIcon className="h-5 w-5" />
        </div>
        <div>
          <div className="flex items-center gap-2 flex-wrap">
            <span className="text-xs font-mono px-2 py-0.5 rounded bg-cyan-950 text-cyan-300 border border-cyan-800/80 font-semibold">
              ACTIVE FEED
            </span>
            <h2 className="text-sm font-bold text-white tracking-tight">{video.title}</h2>
          </div>
          <p className="text-xs text-slate-400 mt-1 flex items-center gap-3 flex-wrap">
            <span>File: <strong className="font-mono text-slate-300">{video.filename}</strong></span>
            <span>•</span>
            <span>Resolution: <strong className="font-mono text-slate-300">{video.resolution}</strong></span>
            <span>•</span>
            <span>Duration: <strong className="font-mono text-slate-300">{Math.floor(video.duration_seconds / 60)}m {video.duration_seconds % 60}s</strong></span>
          </p>
        </div>
      </div>

      <div className="flex items-center gap-3 shrink-0">
        <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-950/80 border border-slate-800 text-xs">
          <CheckCircle2 className="h-4 w-4 text-emerald-400" />
          <span className="text-slate-300">Status:</span>
          <span className="font-mono text-emerald-400 font-semibold uppercase">
            {status?.status || 'COMPLETED'}
          </span>
          <span className="text-slate-600">|</span>
          <span className="font-mono text-cyan-400">{status?.progress || 100}%</span>
        </div>

        <button
          onClick={() => navigate('/analysis')}
          className="px-3.5 py-1.5 rounded-lg bg-cyan-500/15 hover:bg-cyan-500/25 text-cyan-300 border border-cyan-500/40 text-xs font-semibold flex items-center gap-2 transition-all shadow-sm"
        >
          <Play className="h-3.5 w-3.5 fill-cyan-400" />
          <span>Inspect Feed</span>
          <ExternalLink className="h-3 w-3" />
        </button>
      </div>
    </div>
  );
};
