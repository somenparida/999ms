import React, { useEffect, useState, useCallback } from 'react';
import { api } from '@/services/api';
import {
  Video,
  Event,
  TimelineEntry,
  SystemAnalytics,
  AnalysisStatus,
} from '@/types';
import {
  Users,
  Crosshair,
  CheckCircle2,
  AlertTriangle,
  ShieldAlert,
  Activity,
  RefreshCw,
  AlertCircle,
  UploadCloud,
} from 'lucide-react';
import { StatCard } from '@/components/dashboard/StatCard';
import { RecentEvents } from '@/components/dashboard/RecentEvents';
import { EventDistributionChart } from '@/components/dashboard/EventDistributionChart';
import { ActivityTimeline } from '@/components/dashboard/ActivityTimeline';
import { ActiveVideoBanner } from '@/components/dashboard/ActiveVideoBanner';
import { UploadVideoModal } from '@/components/video/UploadVideoModal';

export const DashboardPage: React.FC = () => {
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const [activeVideo, setActiveVideo] = useState<Video | null>(null);
  const [analysisStatus, setAnalysisStatus] = useState<AnalysisStatus | null>(null);
  const [analytics, setAnalytics] = useState<SystemAnalytics | null>(null);
  const [recentEvents, setRecentEvents] = useState<Event[]>([]);
  const [timeline, setTimeline] = useState<TimelineEntry[]>([]);
  const [isUploadModalOpen, setIsUploadModalOpen] = useState<boolean>(false);

  const fetchDashboardData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      // 1. Fetch available videos
      const videos = await api.getVideos();
      const currentVideo = videos[0] || null;
      setActiveVideo(currentVideo);

      const videoId = currentVideo?.video_id || 'vid-autovision-001';

      // 2. Concurrently fetch all telemetry datasets through the API service layer
      const [statusData, analyticsData, eventsData, timelineData] = await Promise.all([
        api.getAnalysisStatus(videoId),
        api.getAnalytics(videoId),
        api.getEvents(videoId),
        api.getTimeline(videoId),
      ]);

      setAnalysisStatus(statusData);
      setAnalytics(analyticsData);
      setRecentEvents(eventsData);
      setTimeline(timelineData);
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to connect to backend telemetry service';
      setError(message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchDashboardData();
  }, [fetchDashboardData]);

  return (
    <div className="space-y-6">
      {/* Page Title & Control Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-800/80 pb-4">
        <div>
          <h1 className="text-xl font-bold tracking-tight text-white flex items-center gap-2">
            <Activity className="h-5 w-5 text-cyan-400" />
            Security &amp; Behavioral Telemetry Dashboard
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Real-time multi-agent vision intelligence, anomaly classification, and event monitoring.
          </p>
        </div>

        <div className="flex items-center gap-2 self-start sm:self-auto flex-wrap">
          <button
            onClick={() => setIsUploadModalOpen(true)}
            className="px-3 py-1.5 rounded-lg bg-cyan-500/20 hover:bg-cyan-500/30 text-cyan-300 border border-cyan-500/40 text-xs font-semibold flex items-center gap-1.5 transition-colors shadow-sm"
          >
            <UploadCloud className="h-3.5 w-3.5" />
            <span>Upload &amp; Analyze</span>
          </button>

          <button
            onClick={fetchDashboardData}
            disabled={loading}
            className="px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-800 hover:border-slate-700 text-xs text-slate-300 hover:text-white flex items-center gap-2 transition-colors disabled:opacity-50"
            title="Refresh telemetry"
          >
            <RefreshCw className={`h-3.5 w-3.5 ${loading ? 'animate-spin text-cyan-400' : ''}`} />
            <span>Sync</span>
          </button>
        </div>
      </div>

      {/* Global Error Banner */}
      {error && !loading && (
        <div className="p-4 rounded-lg bg-rose-500/10 border border-rose-500/30 flex items-start justify-between gap-3 text-xs text-rose-300">
          <div className="flex items-start gap-2">
            <AlertCircle className="h-4 w-4 text-rose-400 shrink-0 mt-0.5" />
            <div>
              <p className="font-semibold text-rose-200">Telemetry Ingestion Error</p>
              <p className="text-[11px] text-rose-400/80 mt-0.5">{error}</p>
            </div>
          </div>
          <button
            onClick={fetchDashboardData}
            className="px-2.5 py-1 rounded bg-rose-500/20 hover:bg-rose-500/30 font-medium text-rose-200 transition-colors"
          >
            Retry
          </button>
        </div>
      )}

      {/* Active Stream Banner */}
      <ActiveVideoBanner
        video={activeVideo}
        status={analysisStatus}
        loading={loading}
      />

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3.5">
        <StatCard
          title="People Detected"
          value={analytics?.people_detected ?? 0}
          icon={Users}
          sublabel="Camera stream entities"
          statusText="+2 new"
          variant="cyan"
          loading={loading}
        />
        <StatCard
          title="Active Tracks"
          value={analytics?.active_tracks ?? 0}
          icon={Crosshair}
          sublabel="Track IDs allocated"
          statusText="DeepSORT Active"
          variant="sky"
          loading={loading}
        />
        <StatCard
          title="Normal Events"
          value={analytics?.normal_events ?? 0}
          icon={CheckCircle2}
          sublabel="Baseline movements"
          statusText="92.8% Nominal"
          variant="emerald"
          loading={loading}
        />
        <StatCard
          title="Abnormal Events"
          value={analytics?.abnormal_events ?? 0}
          icon={AlertTriangle}
          sublabel="Requires supervisor verification"
          statusText="Action Required"
          variant="amber"
          loading={loading}
        />
        <StatCard
          title="High-Risk Events"
          value={analytics?.high_risk_events ?? 0}
          icon={ShieldAlert}
          sublabel="Critical safety breach"
          statusText="2 Critical"
          variant="rose"
          loading={loading}
        />
      </div>

      {/* Middle Row: Recent Events & Event Distribution Chart */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        <div className="lg:col-span-7">
          <RecentEvents
            events={recentEvents}
            loading={loading}
            error={error}
            onRetry={fetchDashboardData}
          />
        </div>
        <div className="lg:col-span-5">
          <EventDistributionChart
            data={analytics?.events_by_type || []}
            loading={loading}
            error={error}
          />
        </div>
      </div>

      {/* Bottom Row: Activity Timeline */}
      <div className="grid grid-cols-1 gap-6">
        <ActivityTimeline
          timeline={timeline}
          loading={loading}
          error={error}
        />
      </div>

      {/* Video Upload & Analysis Modal */}
      <UploadVideoModal
        isOpen={isUploadModalOpen}
        onClose={() => setIsUploadModalOpen(false)}
        onAnalysisComplete={fetchDashboardData}
      />
    </div>
  );
};
