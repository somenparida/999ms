import React, { useRef, useState, useEffect } from 'react';
import { Video, Track, Behaviour, Event, Zone } from '@/types';
import { TrackOverlay } from './TrackOverlay';
import {
  Play,
  Pause,
  Volume2,
  VolumeX,
  Maximize,
  RotateCcw,
  Eye,
  EyeOff,
  Layers,
  Crosshair,
  Shield,
} from 'lucide-react';

interface VideoPlayerProps {
  video: Video | null;
  tracks: Track[];
  behaviours: Behaviour[];
  events: Event[];
  zones?: Zone[];
  currentTime: number;
  selectedTrackId: number | null;
  onTimeUpdate: (time: number) => void;
  onSelectTrack: (trackId: number) => void;
  onDurationChange?: (duration: number) => void;
  externalSeekTime?: number | null;
}

export const VideoPlayer: React.FC<VideoPlayerProps> = ({
  video,
  tracks,
  behaviours,
  events,
  zones = [],
  currentTime,
  selectedTrackId,
  onTimeUpdate,
  onSelectTrack,
  onDurationChange,
  externalSeekTime,
}) => {
  const videoRef = useRef<HTMLVideoElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  const [isPlaying, setIsPlaying] = useState<boolean>(false);
  const [isMuted, setIsMuted] = useState<boolean>(true);
  const [showOverlay, setShowOverlay] = useState<boolean>(true);
  const [showZones, setShowZones] = useState<boolean>(true);
  const [duration, setDuration] = useState<number>(video?.duration_seconds || 151);

  // Synchronize external seeks (from timeline or event markers)
  useEffect(() => {
    if (externalSeekTime !== null && externalSeekTime !== undefined && videoRef.current) {
      videoRef.current.currentTime = externalSeekTime;
      onTimeUpdate(externalSeekTime);
    }
  }, [externalSeekTime, onTimeUpdate]);

  const togglePlay = () => {
    if (!videoRef.current) return;
    if (isPlaying) {
      videoRef.current.pause();
    } else {
      videoRef.current.play().catch(() => {});
    }
    setIsPlaying(!isPlaying);
  };

  const handleTimeUpdate = () => {
    if (videoRef.current) {
      const time = videoRef.current.currentTime;
      onTimeUpdate(time);
    }
  };

  const handleLoadedMetadata = () => {
    if (videoRef.current) {
      const vidDuration = videoRef.current.duration || video?.duration_seconds || 151;
      setDuration(vidDuration);
      if (onDurationChange) onDurationChange(vidDuration);
    }
  };

  const toggleMute = () => {
    if (videoRef.current) {
      videoRef.current.muted = !isMuted;
      setIsMuted(!isMuted);
    }
  };

  const handleRestart = () => {
    if (videoRef.current) {
      videoRef.current.currentTime = 0;
      onTimeUpdate(0);
      if (!isPlaying) {
        videoRef.current.play();
        setIsPlaying(true);
      }
    }
  };

  const handleFullscreen = () => {
    if (!containerRef.current) return;
    if (document.fullscreenElement) {
      document.exitFullscreen();
    } else {
      containerRef.current.requestFullscreen();
    }
  };

  return (
    <div
      ref={containerRef}
      className="relative bg-slate-950 border border-slate-800 rounded-lg overflow-hidden group select-none shadow-2xl flex flex-col"
    >
      {/* HUD Header Bar Overlay */}
      <div className="absolute top-0 inset-x-0 z-30 p-3 bg-gradient-to-b from-black/80 via-black/40 to-transparent flex items-center justify-between pointer-events-none">
        <div className="flex items-center gap-2">
          <span className="h-2 w-2 rounded-full bg-rose-500 animate-pulse" />
          <span className="font-mono text-[11px] font-bold text-white tracking-wider uppercase">
            REC // SEC-04 CAM FEED
          </span>
          <span className="text-slate-500 font-mono text-[10px]">|</span>
          <span className="text-cyan-400 font-mono text-[10px] font-semibold">
            {video?.resolution || '1080p HD'} • {video?.fps || 30} FPS
          </span>
        </div>

        <div className="flex items-center gap-2 pointer-events-auto">
          {/* Zones Overlay toggle */}
          <button
            onClick={() => setShowZones(!showZones)}
            className={`px-2 py-1 rounded text-[10px] font-mono flex items-center gap-1.5 transition-colors border ${
              showZones
                ? 'bg-rose-500/20 text-rose-300 border-rose-500/50 shadow-xs'
                : 'bg-slate-900/80 text-slate-400 border-slate-700'
            }`}
            title="Toggle safety / restricted zone boundaries"
          >
            <Shield className="h-3 w-3 text-rose-400" />
            <span>ZONES: {showZones ? 'ON' : 'OFF'}</span>
          </button>

          {/* AI Overlay toggle */}
          <button
            onClick={() => setShowOverlay(!showOverlay)}
            className={`px-2.5 py-1 rounded text-[10px] font-mono flex items-center gap-1.5 transition-colors border ${
              showOverlay
                ? 'bg-cyan-500/20 text-cyan-300 border-cyan-500/50 shadow-xs'
                : 'bg-slate-900/80 text-slate-400 border-slate-700'
            }`}
            title="Toggle AI inference overlays"
          >
            {showOverlay ? <Eye className="h-3 w-3 text-cyan-400" /> : <EyeOff className="h-3 w-3" />}
            <span>OVERLAY: {showOverlay ? 'ON' : 'OFF'}</span>
          </button>
        </div>
      </div>

      {/* Video Viewport Container */}
      <div className="relative aspect-video w-full bg-black flex items-center justify-center overflow-hidden">
        <video
          ref={videoRef}
          src={video?.url}
          muted={isMuted}
          playsInline
          onTimeUpdate={handleTimeUpdate}
          onLoadedMetadata={handleLoadedMetadata}
          onEnded={() => setIsPlaying(false)}
          onClick={togglePlay}
          className="w-full h-full object-contain cursor-pointer"
        />

        {/* AI Track Bounding Box Overlay & Safety Zones */}
        <TrackOverlay
          tracks={tracks}
          behaviours={behaviours}
          events={events}
          zones={zones}
          currentTime={currentTime}
          selectedTrackId={selectedTrackId}
          onSelectTrack={onSelectTrack}
          videoWidth={1920}
          videoHeight={1080}
          visible={showOverlay}
          showZones={showZones}
        />

        {/* Big Center Play Icon when paused */}
        {!isPlaying && (
          <button
            onClick={togglePlay}
            className="absolute z-30 p-4 rounded-full bg-cyan-500/20 text-cyan-400 border border-cyan-500/40 hover:bg-cyan-500/30 hover:scale-110 transition-all shadow-xl"
            aria-label="Play video"
          >
            <Play className="h-8 w-8 fill-cyan-400 ml-0.5" />
          </button>
        )}

        {/* Reticle / Crosshair watermark in corners */}
        <div className="absolute inset-4 pointer-events-none border border-slate-700/20 z-10 flex flex-col justify-between">
          <div className="flex justify-between">
            <Crosshair className="h-4 w-4 text-slate-600/40" />
            <Crosshair className="h-4 w-4 text-slate-600/40" />
          </div>
          <div className="flex justify-between">
            <Crosshair className="h-4 w-4 text-slate-600/40" />
            <Crosshair className="h-4 w-4 text-slate-600/40" />
          </div>
        </div>
      </div>

      {/* Bottom Video Controls Toolbar */}
      <div className="h-12 bg-slate-950 border-t border-slate-800 px-4 flex items-center justify-between gap-4 text-slate-300 z-30">
        <div className="flex items-center gap-2">
          {/* Play/Pause */}
          <button
            onClick={togglePlay}
            className="p-1.5 rounded hover:bg-slate-800 text-white transition-colors"
            aria-label={isPlaying ? 'Pause' : 'Play'}
          >
            {isPlaying ? <Pause className="h-4 w-4" /> : <Play className="h-4 w-4 fill-white" />}
          </button>

          {/* Restart */}
          <button
            onClick={handleRestart}
            className="p-1.5 rounded hover:bg-slate-800 text-slate-400 hover:text-white transition-colors"
            title="Restart video"
            aria-label="Restart video"
          >
            <RotateCcw className="h-4 w-4" />
          </button>

          {/* Mute/Unmute */}
          <button
            onClick={toggleMute}
            className="p-1.5 rounded hover:bg-slate-800 text-slate-400 hover:text-white transition-colors"
            aria-label={isMuted ? 'Unmute' : 'Mute'}
          >
            {isMuted ? <VolumeX className="h-4 w-4" /> : <Volume2 className="h-4 w-4" />}
          </button>

          {/* Timestamp readout */}
          <div className="ml-2 font-mono text-xs text-slate-400 flex items-center gap-1">
            <span className="text-white font-semibold">
              {Math.floor(currentTime / 60).toString().padStart(2, '0')}:
              {Math.floor(currentTime % 60).toString().padStart(2, '0')}
            </span>
            <span>/</span>
            <span>
              {Math.floor(duration / 60).toString().padStart(2, '0')}:
              {Math.floor(duration % 60).toString().padStart(2, '0')}
            </span>
          </div>
        </div>

        {/* Right Controls */}
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1.5 text-[11px] font-mono text-cyan-400 px-2 py-0.5 rounded bg-cyan-950/60 border border-cyan-800/60">
            <Layers className="h-3 w-3" />
            <span>{tracks.length} Tracks Ingested</span>
          </div>

          <button
            onClick={handleFullscreen}
            className="p-1.5 rounded hover:bg-slate-800 text-slate-400 hover:text-white transition-colors"
            title="Toggle fullscreen"
            aria-label="Toggle fullscreen"
          >
            <Maximize className="h-4 w-4" />
          </button>
        </div>
      </div>
    </div>
  );
};
