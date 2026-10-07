import React, { useState, useEffect } from 'react';
import { api } from '@/services/api';
import { AnalysisStatus, Video } from '@/types';
import {
  UploadCloud,
  X,
  CheckCircle2,
  Play,
  FileVideo,
  RefreshCw,
  Cpu,
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';

interface UploadVideoModalProps {
  isOpen: boolean;
  onClose: () => void;
  onAnalysisComplete?: (videoId: string) => void;
}

export const UploadVideoModal: React.FC<UploadVideoModalProps> = ({
  isOpen,
  onClose,
  onAnalysisComplete,
}) => {
  const navigate = useNavigate();
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState<boolean>(false);
  const [uploadedVideo, setUploadedVideo] = useState<Video | null>(null);
  const [status, setStatus] = useState<AnalysisStatus | null>(null);

  // Poll analysis status once triggered
  useEffect(() => {
    let interval: ReturnType<typeof setInterval> | null = null;
    if (uploadedVideo && status && status.status === 'processing') {
      interval = setInterval(async () => {
        const updated = await api.getAnalysisStatus(uploadedVideo.video_id);
        setStatus(updated);
        if (updated.status === 'completed') {
          if (interval) clearInterval(interval);
          if (onAnalysisComplete) onAnalysisComplete(uploadedVideo.video_id);
        }
      }, 1000);
    }
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [uploadedVideo, status, onAnalysisComplete]);

  if (!isOpen) return null;

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0]);
    }
  };

  const handleUseDemoVideo = () => {
    // Create a mock File object
    const blob = new Blob(['sample-video-stream'], { type: 'video/mp4' });
    const file = new File([blob], 'surveillance_sector4_cam.mp4', { type: 'video/mp4' });
    setSelectedFile(file);
  };

  const handleStartUploadAndAnalysis = async () => {
    if (!selectedFile) return;
    setIsUploading(true);
    try {
      const vid = await api.uploadVideo(selectedFile);
      setUploadedVideo(vid);
      const initialStatus = await api.startAnalysis(vid.video_id);
      setStatus(initialStatus);
    } catch {
      // Error handling
    } finally {
      setIsUploading(false);
    }
  };

  const handleGoToAnalysis = () => {
    onClose();
    navigate('/analysis');
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-xs select-none">
      <div
        className="relative w-full max-w-lg bg-slate-950 border border-slate-800 rounded-xl shadow-2xl overflow-hidden p-6 space-y-5"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center justify-between border-b border-slate-800 pb-3">
          <div className="flex items-center gap-2.5">
            <div className="p-2 rounded-lg bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
              <UploadCloud className="h-5 w-5" />
            </div>
            <div>
              <h3 className="text-sm font-bold text-white tracking-tight">Ingest Video &amp; Start Analysis</h3>
              <p className="text-[11px] text-slate-400">Stream upload and multi-model AI pipeline execution</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-md text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Upload State or Progress State */}
        {!uploadedVideo ? (
          <div className="space-y-4">
            <label className="border-2 border-dashed border-slate-800 hover:border-cyan-500/50 bg-slate-900/40 rounded-xl p-8 flex flex-col items-center justify-center cursor-pointer transition-colors text-center group">
              <FileVideo className="h-10 w-10 text-slate-600 group-hover:text-cyan-400 transition-colors mb-2" />
              <span className="text-xs font-semibold text-white">
                {selectedFile ? selectedFile.name : 'Select or drop video file'}
              </span>
              <span className="text-[10px] text-slate-500 mt-1">
                Supports MP4, AVI, MKV (1080p, 30fps recommended)
              </span>
              <input
                type="file"
                accept="video/*"
                onChange={handleFileChange}
                className="hidden"
              />
            </label>

            <div className="flex items-center justify-between text-xs">
              <span className="text-slate-400">Want to test with sample data?</span>
              <button
                type="button"
                onClick={handleUseDemoVideo}
                className="text-cyan-400 hover:text-cyan-300 font-medium"
              >
                Use Sector-04 Demo Video
              </button>
            </div>

            <button
              onClick={handleStartUploadAndAnalysis}
              disabled={!selectedFile || isUploading}
              className="w-full py-2.5 rounded-lg bg-cyan-500/20 hover:bg-cyan-500/30 text-cyan-300 border border-cyan-500/40 text-xs font-bold transition-all disabled:opacity-40 flex items-center justify-center gap-2 shadow-sm"
            >
              {isUploading ? (
                <>
                  <RefreshCw className="h-4 w-4 animate-spin text-cyan-400" />
                  <span>Uploading stream to ingestion pipeline...</span>
                </>
              ) : (
                <>
                  <UploadCloud className="h-4 w-4" />
                  <span>Start AI Vision Pipeline</span>
                </>
              )}
            </button>
          </div>
        ) : (
          /* Analysis In-Progress / Completed State */
          <div className="space-y-5 py-2">
            <div className="p-3 rounded-lg bg-slate-900/60 border border-slate-800 flex items-center justify-between text-xs">
              <span className="text-slate-300 font-medium truncate">{uploadedVideo.title}</span>
              <span className="font-mono text-cyan-400 font-bold">{status?.progress || 0}%</span>
            </div>

            {/* Progress Bar */}
            <div className="space-y-2">
              <div className="h-2 w-full bg-slate-900 rounded-full overflow-hidden border border-slate-800">
                <div
                  className="h-full bg-cyan-400 transition-all duration-300 shadow-sm shadow-cyan-400"
                  style={{ width: `${status?.progress || 0}%` }}
                />
              </div>

              <div className="flex items-center gap-2 text-xs font-mono text-slate-400">
                {status?.status === 'completed' ? (
                  <CheckCircle2 className="h-4 w-4 text-emerald-400 shrink-0" />
                ) : (
                  <RefreshCw className="h-4 w-4 text-cyan-400 animate-spin shrink-0" />
                )}
                <span className="truncate">{status?.current_step || 'Processing stream...'}</span>
              </div>
            </div>

            {/* Models engaged */}
            <div className="p-3 rounded-lg bg-slate-900/40 border border-slate-800 space-y-1.5 text-[11px] font-mono text-slate-400">
              <div className="flex items-center justify-between">
                <span className="flex items-center gap-1 text-slate-300">
                  <Cpu className="h-3 w-3 text-cyan-400" /> YOLOv8x Detection:
                </span>
                <span className="text-emerald-400 font-semibold">Active</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="flex items-center gap-1 text-slate-300">
                  <Cpu className="h-3 w-3 text-sky-400" /> DeepSORT Multi-Object Tracking:
                </span>
                <span className="text-emerald-400 font-semibold">Active</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="flex items-center gap-1 text-slate-300">
                  <Cpu className="h-3 w-3 text-amber-400" /> Behaviour &amp; Anomaly Engine:
                </span>
                <span className={status?.status === 'completed' ? 'text-emerald-400' : 'text-amber-400'}>
                  {status?.status === 'completed' ? '4 Events Generated' : 'Running'}
                </span>
              </div>
            </div>

            {/* Completed Action button */}
            {status?.status === 'completed' && (
              <button
                onClick={handleGoToAnalysis}
                className="w-full py-2.5 rounded-lg bg-cyan-500/25 hover:bg-cyan-500/35 text-cyan-300 border border-cyan-500/50 text-xs font-bold transition-all flex items-center justify-center gap-2 shadow-md animate-pulse"
              >
                <Play className="h-4 w-4 fill-cyan-400" />
                <span>Open Video Analysis Workspace</span>
              </button>
            )}
          </div>
        )}
      </div>
    </div>
  );
};
