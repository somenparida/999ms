import React, { useEffect, useState, useCallback } from 'react';
import { api } from '@/services/api';
import { Video, Track, Behaviour, Event, AnalysisStatus, Zone } from '@/types';
import { VideoPlayer } from '@/components/video/VideoPlayer';
import { VideoTimeline } from '@/components/video/VideoTimeline';
import { ActiveTracks } from '@/components/video/ActiveTracks';
import { CurrentAlertPanel } from '@/components/video/CurrentAlertPanel';
import {
  Crosshair,
  RefreshCw,
  AlertCircle,
  PlayCircle,
  CheckCircle2,
  Cpu,
  Activity,
  ChevronDown,
} from 'lucide-react';



export const AnalysisPage: React.FC = () => {
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Core Data
  const [videos, setVideos] = useState<Video[]>([]);
  const [selectedVideoId, setSelectedVideoId] = useState<string>('vid-autovision-001');
  const [tracks, setTracks] = useState<Track[]>([]);
  const [behaviours, setBehaviours] = useState<Behaviour[]>([]);
  const [events, setEvents] = useState<Event[]>([]);
  const [zones, setZones] = useState<Zone[]>([]);
  const [analysisStatus, setAnalysisStatus] = useState<AnalysisStatus | null>(null);

  // Playback & Interaction State
  const [currentTime, setCurrentTime] = useState<number>(0);
  const [videoDuration, setVideoDuration] = useState<number>(151);
  const [externalSeekTime, setExternalSeekTime] = useState<number | null>(null);
  const [selectedTrackId, setSelectedTrackId] = useState<number | null>(7);
  const [selectedEvent, setSelectedEvent] = useState<Event | null>(null);

  // Simulated analysis execution state
  const [isAnalyzing, setIsAnalyzing] = useState<boolean>(false);

  // Load all telemetry data for current video
  const loadVideoData = useCallback(async (videoId: string) => {
    setLoading(true);
    setError(null);
    try {
      const [vList, tList, bList, eList, zList, status] = await Promise.all([
        api.getVideos(),
        api.getTracks(videoId),
        api.getBehaviours(videoId),
        api.getEvents(videoId),
        api.getZones(videoId),
        api.getAnalysisStatus(videoId),
      ]);

      setVideos(vList);
      setTracks(tList);
      setBehaviours(bList);
      setEvents(eList);
      setZones(zList);
      setAnalysisStatus(status);

      // Default selected event to the first high-risk event (e.g. EVT001)
      const firstHigh = eList.find((e) => e.severity === 'high') || eList[0] || null;
      setSelectedEvent(firstHigh);
      if (firstHigh) {
        setSelectedTrackId(firstHigh.track_id);
      }
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to load video intelligence workspace';
      setError(message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadVideoData(selectedVideoId);
  }, [selectedVideoId, loadVideoData]);

  // Determine currently active abnormal event based on video currentTime or selectedEvent
  const activeEventAtTime =
    events.find((e) => currentTime >= e.start_time && currentTime <= e.end_time) ||
    selectedEvent;

  // Handlers
  const handleSelectTrack = (trackId: number, seekTimestamp?: number) => {
    setSelectedTrackId(trackId);
    if (seekTimestamp !== undefined) {
      setExternalSeekTime(seekTimestamp);
      setCurrentTime(seekTimestamp);
    }
    // Select any event for this track
    const trackEvent = events.find((e) => e.track_id === trackId);
    if (trackEvent) {
      setSelectedEvent(trackEvent);
    }
  };

  const handleSelectEvent = (event: Event) => {
    setSelectedEvent(event);
    setSelectedTrackId(event.track_id);
    setExternalSeekTime(event.start_time);
    setCurrentTime(event.start_time);
  };

  const handleTimelineSeek = (time: number) => {
    setExternalSeekTime(time);
    setCurrentTime(time);
    // If seek matches an event, update selected event
    const matchedEvent = events.find((e) => time >= e.start_time && time <= e.end_time);
    if (matchedEvent) {
      setSelectedEvent(matchedEvent);
      setSelectedTrackId(matchedEvent.track_id);
    }
  };

  // AI Pipeline Import Handlers (readme_backend.md: Member 1 & Member 2 Integration)
  const [importNotice, setImportNotice] = useState<string | null>(null);
  const [isImporting, setIsImporting] = useState<boolean>(false);

  const handleImportMember1Tracks = async () => {
    setIsImporting(true);
    try {
      const res = await api.importTracks(selectedVideoId, tracks);
      setImportNotice(`[Member 1 Imported] Successfully processed ${res.imported} tracks via POST /api/videos/${selectedVideoId}/tracks/import`);
      setTimeout(() => setImportNotice(null), 4500);
    } catch {
      setImportNotice('Failed to import tracks from Member 1.');
      setTimeout(() => setImportNotice(null), 4500);
    } finally {
      setIsImporting(false);
    }
  };

  const handleImportMember2Behaviours = async () => {
    setIsImporting(true);
    try {
      const res = await api.importBehaviours(selectedVideoId, behaviours);
      setImportNotice(`[Member 2 Imported] Successfully processed ${res.imported} behaviours via POST /api/videos/${selectedVideoId}/behaviours/import`);
      setTimeout(() => setImportNotice(null), 4500);
    } catch {
      setImportNotice('Failed to import behaviours from Member 2.');
      setTimeout(() => setImportNotice(null), 4500);
    } finally {
      setIsImporting(false);
    }
  };

  const handleTriggerAnalysis = async () => {
    setIsAnalyzing(true);
    try {
      const status = await api.startAnalysis(selectedVideoId);
      setAnalysisStatus(status);
      setTimeout(() => {
        setIsAnalyzing(false);
        setAnalysisStatus({
          video_id: selectedVideoId,
          status: 'completed',
          progress: 100,
          current_step: 'Analysis completed successfully',
        });
      }, 1500);
    } catch {
      setIsAnalyzing(false);
    }
  };

  const currentVideo = videos.find((v) => v.video_id === selectedVideoId) || videos[0] || null;

  return (
    <div className="space-y-6">

      {/* Workspace Top Toolbar */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 border-b border-slate-800/80 pb-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-xl font-bold tracking-tight text-white flex items-center gap-2">
              <Crosshair className="h-5 w-5 text-cyan-400" />
              Video Intelligence Workspace
            </h1>
            <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-cyan-950 text-cyan-400 border border-cyan-800 font-bold uppercase">
              Primary Demo Mode
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Real-time entity bounding box rendering, DeepSORT tracking telemetry, and automated behavior anomaly detection.
          </p>
        </div>

        {/* Video selector and simulated analysis trigger */}
        <div className="flex items-center gap-3 flex-wrap">
          <div className="relative">
            <select
              value={selectedVideoId}
              onChange={(e) => setSelectedVideoId(e.target.value)}
              className="appearance-none bg-slate-900 border border-slate-800 text-xs text-slate-200 pl-3 pr-8 py-1.5 rounded-lg font-mono focus:border-cyan-500 focus:outline-hidden cursor-pointer"
            >
              {videos.map((v) => (
                <option key={v.video_id} value={v.video_id}>
                  {v.title} ({v.resolution})
                </option>
              ))}
            </select>
            <ChevronDown className="h-3.5 w-3.5 text-slate-400 absolute right-2.5 top-1/2 -translate-y-1/2 pointer-events-none" />
          </div>

          {/* Member 1 & Member 2 AI Pipeline Import Controls (readme_backend.md) */}
          <button
            onClick={handleImportMember1Tracks}
            disabled={isImporting || loading}
            className="px-2.5 py-1.5 rounded-lg bg-slate-900 hover:bg-slate-800 text-slate-300 hover:text-white border border-slate-700/80 text-xs font-mono flex items-center gap-1.5 transition-colors disabled:opacity-50"
            title="Import DeepSORT tracks from Member 1 (POST /api/videos/{id}/tracks/import)"
          >
            <Cpu className="h-3.5 w-3.5 text-cyan-400" />
            <span>+ Tracks (M1)</span>
          </button>

          <button
            onClick={handleImportMember2Behaviours}
            disabled={isImporting || loading}
            className="px-2.5 py-1.5 rounded-lg bg-slate-900 hover:bg-slate-800 text-slate-300 hover:text-white border border-slate-700/80 text-xs font-mono flex items-center gap-1.5 transition-colors disabled:opacity-50"
            title="Import behaviour classifications from Member 2 (POST /api/videos/{id}/behaviours/import)"
          >
            <Activity className="h-3.5 w-3.5 text-sky-400" />
            <span>+ Behaviours (M2)</span>
          </button>

          <button
            onClick={handleTriggerAnalysis}
            disabled={isAnalyzing || loading}
            className="px-3 py-1.5 rounded-lg bg-cyan-500/15 hover:bg-cyan-500/25 text-cyan-300 border border-cyan-500/40 text-xs font-semibold flex items-center gap-2 transition-all disabled:opacity-50"
            title="Simulate analysis execution via service layer"
          >
            {isAnalyzing ? (
              <RefreshCw className="h-3.5 w-3.5 animate-spin text-cyan-400" />
            ) : (
              <PlayCircle className="h-3.5 w-3.5 fill-cyan-400" />
            )}
            <span>{isAnalyzing ? 'Processing Pipeline...' : 'Re-Run Pipeline'}</span>
          </button>
        </div>
      </div>

      {/* AI Pipeline Import Toast Notice */}
      {importNotice && (
        <div className="p-3 rounded-lg bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-between gap-3 text-xs text-emerald-300 font-mono animate-fadeIn">
          <div className="flex items-center gap-2">
            <CheckCircle2 className="h-4 w-4 text-emerald-400 shrink-0" />
            <span>{importNotice}</span>
          </div>
          <button
            onClick={() => setImportNotice(null)}
            className="text-emerald-400 hover:text-white text-xs"
          >
            Dismiss
          </button>
        </div>
      )}


      {/* Error Banner */}
      {error && !loading && (
        <div className="p-4 rounded-lg bg-rose-500/10 border border-rose-500/30 flex items-start justify-between gap-3 text-xs text-rose-300">
          <div className="flex items-start gap-2">
            <AlertCircle className="h-4 w-4 text-rose-400 shrink-0 mt-0.5" />
            <div>
              <p className="font-semibold text-rose-200">Video Analysis Workspace Error</p>
              <p className="text-[11px] text-rose-400/80 mt-0.5">{error}</p>
            </div>
          </div>
          <button
            onClick={() => loadVideoData(selectedVideoId)}
            className="px-2.5 py-1 rounded bg-rose-500/20 hover:bg-rose-500/30 font-medium text-rose-200 transition-colors"
          >
            Retry
          </button>
        </div>
      )}

      {/* Main Workspace Layout */}
      {loading ? (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 animate-pulse">
          <div className="lg:col-span-8 space-y-4">
            <div className="aspect-video bg-slate-900/60 rounded-lg border border-slate-800 flex items-center justify-center">
              <span className="text-xs text-slate-500 font-mono">Initializing video stream &amp; overlay buffers...</span>
            </div>
            <div className="h-16 bg-slate-900/60 rounded-lg border border-slate-800"></div>
          </div>
          <div className="lg:col-span-4 space-y-4">
            <div className="h-64 bg-slate-900/60 rounded-lg border border-slate-800"></div>
            <div className="h-64 bg-slate-900/60 rounded-lg border border-slate-800"></div>
          </div>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Left Column: Video Intelligence Stream + Timeline (col-span-8) */}
          <div className="lg:col-span-8 space-y-4">
            {/* Video Player Component with Track Bounding Box Overlay & Safety Zones */}
            <VideoPlayer
              video={currentVideo}
              tracks={tracks}
              behaviours={behaviours}
              events={events}
              zones={zones}
              currentTime={currentTime}
              selectedTrackId={selectedTrackId}
              onTimeUpdate={(t) => setCurrentTime(t)}
              onSelectTrack={handleSelectTrack}
              onDurationChange={(d) => setVideoDuration(d)}
              externalSeekTime={externalSeekTime}
            />

            {/* Interactive Video Timeline Component */}
            <VideoTimeline
              currentTime={currentTime}
              duration={videoDuration}
              events={events}
              behaviours={behaviours}
              selectedEventId={selectedEvent?.event_id || null}
              onSeek={handleTimelineSeek}
              onSelectEvent={handleSelectEvent}
            />

            {/* Pipeline Telemetry Strip */}
            <div className="p-3 rounded-lg bg-slate-900/40 border border-slate-800/80 flex items-center justify-between text-xs text-slate-400 font-mono">
              <div className="flex items-center gap-3">
                <span className="flex items-center gap-1.5 text-cyan-400">
                  <Cpu className="h-3.5 w-3.5" />
                  YOLOv8x + DeepSORT Engine
                </span>
                <span className="hidden sm:inline text-slate-600">•</span>
                <span className="hidden sm:inline text-slate-300">
                  Inference: 14.2ms / frame
                </span>
              </div>

              <div className="flex items-center gap-2">
                <CheckCircle2 className="h-3.5 w-3.5 text-emerald-400" />
                <span className="text-emerald-400 font-semibold uppercase text-[11px]">
                  {analysisStatus?.status || 'COMPLETED'} ({analysisStatus?.progress || 100}%)
                </span>
              </div>
            </div>
          </div>

          {/* Right Column: Alert Panel & Active Tracks (col-span-4) */}
          <div className="lg:col-span-4 space-y-4">
            {/* Current Alert / Active Event Panel */}
            <CurrentAlertPanel
              activeEvent={activeEventAtTime}
              currentTime={currentTime}
            />

            {/* Active Tracks Panel */}
            <ActiveTracks
              tracks={tracks}
              behaviours={behaviours}
              events={events}
              selectedTrackId={selectedTrackId}
              currentTime={currentTime}
              onSelectTrack={handleSelectTrack}
            />
          </div>
        </div>
      )}
    </div>
  );
};
