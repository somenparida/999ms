import React, { useEffect, useState, useMemo, useCallback } from 'react';
import { api } from '@/services/api';
import { Event } from '@/types';
import { EventTable } from '@/components/events/EventTable';
import { EventDetailsModal } from '@/components/events/EventDetailsModal';
import {
  AlertCircle,
  Search,
  Filter,
  ArrowUpDown,
  RefreshCw,
  ShieldAlert,
  AlertTriangle,
  Info,
  Layers,
} from 'lucide-react';

export const EventsPage: React.FC = () => {
  const [events, setEvents] = useState<Event[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Search & Filter State
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [severityFilter, setSeverityFilter] = useState<'all' | 'high' | 'medium' | 'low'>('all');
  const [selectedEventType, setSelectedEventType] = useState<string>('all');
  const [sortBy, setSortBy] = useState<'time-desc' | 'time-asc' | 'conf-desc' | 'severity'>('time-desc');

  // Selected event modal
  const [selectedEvent, setSelectedEvent] = useState<Event | null>(null);

  const loadEvents = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.getEvents('vid-autovision-001');
      setEvents(data);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to fetch event catalog';
      setError(msg);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadEvents();
  }, [loadEvents]);

  // Unique event types for dropdown
  const uniqueEventTypes = useMemo(() => {
    return Array.from(new Set(events.map((e) => e.event_type)));
  }, [events]);

  // Filtered and sorted events
  const processedEvents = useMemo(() => {
    return events
      .filter((evt) => {
        // 1. Search Query
        if (searchQuery.trim()) {
          const q = searchQuery.toLowerCase();
          const matchId = evt.event_id.toLowerCase().includes(q);
          const matchTrack = `person #${evt.track_id}`.toLowerCase().includes(q) || evt.track_id.toString().includes(q);
          const matchType = evt.event_type.toLowerCase().includes(q);
          const matchReason = evt.reason?.toLowerCase().includes(q);
          if (!matchId && !matchTrack && !matchType && !matchReason) return false;
        }

        // 2. Severity filter
        if (severityFilter !== 'all' && evt.severity !== severityFilter) {
          return false;
        }

        // 3. Event Type filter
        if (selectedEventType !== 'all' && evt.event_type !== selectedEventType) {
          return false;
        }

        return true;
      })
      .sort((a, b) => {
        if (sortBy === 'time-desc') return b.start_time - a.start_time;
        if (sortBy === 'time-asc') return a.start_time - b.start_time;
        if (sortBy === 'conf-desc') return b.confidence - a.confidence;
        if (sortBy === 'severity') {
          const rank = { high: 3, medium: 2, low: 1 };
          return rank[b.severity] - rank[a.severity];
        }
        return 0;
      });
  }, [events, searchQuery, severityFilter, selectedEventType, sortBy]);

  // Counts
  const highRiskCount = events.filter((e) => e.severity === 'high').length;
  const medRiskCount = events.filter((e) => e.severity === 'medium').length;
  const lowRiskCount = events.filter((e) => e.severity === 'low').length;

  return (
    <div className="space-y-6">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800/80 pb-4">
        <div>
          <h1 className="text-xl font-bold tracking-tight text-white flex items-center gap-2">
            <AlertCircle className="h-5 w-5 text-cyan-400" />
            Detected Behavioral Events &amp; Anomalies
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Complete incident catalog, safety breach classifications, and timestamped forensic evidence.
          </p>
        </div>

        <button
          onClick={loadEvents}
          disabled={loading}
          className="self-start sm:self-auto px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-800 hover:border-slate-700 text-xs text-slate-300 hover:text-white flex items-center gap-2 transition-colors disabled:opacity-50"
          title="Reload events from service layer"
        >
          <RefreshCw className={`h-3.5 w-3.5 ${loading ? 'animate-spin text-cyan-400' : ''}`} />
          <span>Reload Catalog</span>
        </button>
      </div>

      {/* Metric Summary Strip */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <div className="bg-slate-900/60 border border-slate-800 rounded-lg p-3 flex items-center justify-between">
          <div>
            <span className="text-[10px] font-mono text-slate-400 block">TOTAL RECORDED</span>
            <span className="text-lg font-bold font-mono text-white mt-0.5 block">{events.length}</span>
          </div>
          <div className="p-2 rounded bg-slate-800 text-slate-300">
            <Layers className="h-4 w-4" />
          </div>
        </div>

        <div className="bg-slate-900/60 border border-slate-800 rounded-lg p-3 flex items-center justify-between">
          <div>
            <span className="text-[10px] font-mono text-rose-400 block">HIGH RISK ALERTS</span>
            <span className="text-lg font-bold font-mono text-rose-400 mt-0.5 block">{highRiskCount}</span>
          </div>
          <div className="p-2 rounded bg-rose-500/10 text-rose-400 border border-rose-500/20">
            <ShieldAlert className="h-4 w-4" />
          </div>
        </div>

        <div className="bg-slate-900/60 border border-slate-800 rounded-lg p-3 flex items-center justify-between">
          <div>
            <span className="text-[10px] font-mono text-amber-400 block">MEDIUM PRIORITY</span>
            <span className="text-lg font-bold font-mono text-amber-400 mt-0.5 block">{medRiskCount}</span>
          </div>
          <div className="p-2 rounded bg-amber-500/10 text-amber-400 border border-amber-500/20">
            <AlertTriangle className="h-4 w-4" />
          </div>
        </div>

        <div className="bg-slate-900/60 border border-slate-800 rounded-lg p-3 flex items-center justify-between">
          <div>
            <span className="text-[10px] font-mono text-sky-400 block">LOW RISK ADVISORIES</span>
            <span className="text-lg font-bold font-mono text-sky-400 mt-0.5 block">{lowRiskCount}</span>
          </div>
          <div className="p-2 rounded bg-sky-500/10 text-sky-400 border border-sky-500/20">
            <Info className="h-4 w-4" />
          </div>
        </div>
      </div>

      {/* Filtering Toolbar */}
      <div className="bg-slate-900/70 border border-slate-800 rounded-lg p-3.5 flex flex-col md:flex-row gap-3 items-stretch md:items-center justify-between">
        {/* Search */}
        <div className="relative flex-1 max-w-md">
          <Search className="h-4 w-4 text-slate-500 absolute left-3 top-1/2 -translate-y-1/2 pointer-events-none" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search by Event ID, Person #, Type, Reason..."
            className="w-full bg-slate-950 border border-slate-800 rounded-lg pl-9 pr-3 py-1.5 text-xs text-white placeholder-slate-500 focus:outline-hidden focus:border-cyan-500 transition-colors"
          />
        </div>

        {/* Filter dropdowns */}
        <div className="flex items-center gap-2.5 flex-wrap">
          {/* Severity filter */}
          <div className="flex items-center gap-1.5 text-xs text-slate-400">
            <Filter className="h-3.5 w-3.5 text-cyan-400" />
            <span>Severity:</span>
            <select
              value={severityFilter}
              onChange={(e) => setSeverityFilter(e.target.value as any)}
              className="bg-slate-950 border border-slate-800 text-xs text-slate-200 px-2 py-1.5 rounded-lg focus:outline-hidden focus:border-cyan-500"
            >
              <option value="all">All Severities</option>
              <option value="high">High Risk</option>
              <option value="medium">Medium Risk</option>
              <option value="low">Low Risk</option>
            </select>
          </div>

          {/* Event Type filter */}
          <div className="flex items-center gap-1.5 text-xs text-slate-400">
            <span>Type:</span>
            <select
              value={selectedEventType}
              onChange={(e) => setSelectedEventType(e.target.value)}
              className="bg-slate-950 border border-slate-800 text-xs text-slate-200 px-2 py-1.5 rounded-lg focus:outline-hidden focus:border-cyan-500"
            >
              <option value="all">All Event Types</option>
              {uniqueEventTypes.map((type) => (
                <option key={type} value={type}>
                  {type}
                </option>
              ))}
            </select>
          </div>

          {/* Sort order */}
          <div className="flex items-center gap-1.5 text-xs text-slate-400">
            <ArrowUpDown className="h-3.5 w-3.5 text-cyan-400" />
            <span>Sort:</span>
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value as any)}
              className="bg-slate-950 border border-slate-800 text-xs text-slate-200 px-2 py-1.5 rounded-lg focus:outline-hidden focus:border-cyan-500"
            >
              <option value="time-desc">Newest First</option>
              <option value="time-asc">Oldest First</option>
              <option value="conf-desc">Highest Confidence</option>
              <option value="severity">Severity Rank</option>
            </select>
          </div>
        </div>
      </div>

      {/* Error State */}
      {error && !loading && (
        <div className="p-4 rounded-lg bg-rose-500/10 border border-rose-500/30 flex items-start justify-between text-xs text-rose-300">
          <div className="flex items-start gap-2">
            <AlertCircle className="h-4 w-4 text-rose-400 shrink-0 mt-0.5" />
            <div>
              <p className="font-semibold text-rose-200">Catalog Loading Failed</p>
              <p className="text-[11px] text-rose-400/80 mt-0.5">{error}</p>
            </div>
          </div>
          <button
            onClick={loadEvents}
            className="px-2.5 py-1 rounded bg-rose-500/20 hover:bg-rose-500/30 font-medium text-rose-200"
          >
            Retry
          </button>
        </div>
      )}

      {/* Loading Skeleton */}
      {loading && (
        <div className="space-y-3 py-6 animate-pulse">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="h-12 bg-slate-900/60 rounded-lg border border-slate-800" />
          ))}
        </div>
      )}

      {/* Main Table View */}
      {!loading && !error && (
        <EventTable
          events={processedEvents}
          selectedEventId={selectedEvent?.event_id || null}
          onSelectEvent={(evt) => setSelectedEvent(evt)}
        />
      )}

      {/* Event Details Modal */}
      <EventDetailsModal
        event={selectedEvent}
        onClose={() => setSelectedEvent(null)}
      />
    </div>
  );
};
