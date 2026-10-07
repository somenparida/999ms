import React, { useEffect, useState, useCallback } from 'react';
import { api } from '@/services/api';
import { SystemAnalytics } from '@/types';
import {
  ActivityOverTimeChart,
  SeverityDonutChart,
  BehaviourDistributionChart,
  EventTypeDistributionChart,
} from '@/components/analytics/AnalyticsCharts';
import { StatCard } from '@/components/dashboard/StatCard';
import {
  BarChart3,
  RefreshCw,
  AlertCircle,
  Users,
  Crosshair,
  CheckCircle2,
  AlertTriangle,
  ShieldAlert,
  Cpu,
} from 'lucide-react';

export const AnalyticsPage: React.FC = () => {
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [analytics, setAnalytics] = useState<SystemAnalytics | null>(null);

  const loadAnalytics = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.getAnalytics('vid-autovision-001');
      setAnalytics(data);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to load telemetry analytics';
      setError(msg);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadAnalytics();
  }, [loadAnalytics]);

  return (
    <div className="space-y-6">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800/80 pb-4">
        <div>
          <h1 className="text-xl font-bold tracking-tight text-white flex items-center gap-2">
            <BarChart3 className="h-5 w-5 text-cyan-400" />
            System Analytics &amp; Behavior Forensics
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Statistical aggregate metrics, temporal anomaly rates, risk distributions, and behavioral frequency profiling.
          </p>
        </div>

        <button
          onClick={loadAnalytics}
          disabled={loading}
          className="self-start sm:self-auto px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-800 hover:border-slate-700 text-xs text-slate-300 hover:text-white flex items-center gap-2 transition-colors disabled:opacity-50"
          title="Refresh analytics data"
        >
          <RefreshCw className={`h-3.5 w-3.5 ${loading ? 'animate-spin text-cyan-400' : ''}`} />
          <span>Refresh Analytics</span>
        </button>
      </div>

      {/* Error State */}
      {error && !loading && (
        <div className="p-4 rounded-lg bg-rose-500/10 border border-rose-500/30 flex items-start justify-between text-xs text-rose-300">
          <div className="flex items-start gap-2">
            <AlertCircle className="h-4 w-4 text-rose-400 shrink-0 mt-0.5" />
            <div>
              <p className="font-semibold text-rose-200">Analytics Aggregation Error</p>
              <p className="text-[11px] text-rose-400/80 mt-0.5">{error}</p>
            </div>
          </div>
          <button
            onClick={loadAnalytics}
            className="px-2.5 py-1 rounded bg-rose-500/20 hover:bg-rose-500/30 font-medium text-rose-200"
          >
            Retry
          </button>
        </div>
      )}

      {/* KPI Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3.5">
        <StatCard
          title="Total People"
          value={analytics?.people_detected ?? 0}
          icon={Users}
          sublabel="Identified in active stream"
          statusText="Nominal"
          variant="cyan"
          loading={loading}
        />
        <StatCard
          title="Total Tracks"
          value={analytics?.active_tracks ?? 0}
          icon={Crosshair}
          sublabel="Unique trajectories"
          statusText="DeepSORT Active"
          variant="sky"
          loading={loading}
        />
        <StatCard
          title="Normal Events"
          value={analytics?.normal_events ?? 0}
          icon={CheckCircle2}
          sublabel="Baseline compliance"
          statusText="92.8% Nominal"
          variant="emerald"
          loading={loading}
        />
        <StatCard
          title="Abnormal Events"
          value={analytics?.abnormal_events ?? 0}
          icon={AlertTriangle}
          sublabel="Flagged anomalies"
          statusText="4 Breaches"
          variant="amber"
          loading={loading}
        />
        <StatCard
          title="High-Risk Events"
          value={analytics?.high_risk_events ?? 0}
          icon={ShieldAlert}
          sublabel="Critical safety hazards"
          statusText="Immediate Action"
          variant="rose"
          loading={loading}
        />
      </div>

      {/* Visual Analytics 2x2 Grid */}
      {loading ? (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 animate-pulse">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="h-72 bg-slate-900/60 border border-slate-800 rounded-xl" />
          ))}
        </div>
      ) : analytics ? (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <ActivityOverTimeChart data={analytics.activity_over_time} />
          <SeverityDonutChart data={analytics.events_by_severity} />
          <EventTypeDistributionChart data={analytics.events_by_type} />
          <BehaviourDistributionChart data={analytics.behaviour_distribution} />
        </div>
      ) : null}

      {/* Architecture Notice Footer */}
      <div className="p-4 rounded-xl bg-slate-900/40 border border-slate-800 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs text-slate-400 font-mono">
        <div className="flex items-center gap-2 text-slate-300">
          <Cpu className="h-4 w-4 text-cyan-400" />
          <span>Analytics Engine: Aggregate Time-Series Ingestion</span>
        </div>
        <span className="text-[11px] text-slate-500">
          Data contract: SystemAnalytics (decoupled from FastAPI backend)
        </span>
      </div>
    </div>
  );
};
