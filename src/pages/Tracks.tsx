import React, { useEffect, useState, useMemo, useCallback } from 'react';
import { api } from '@/services/api';
import { Track, Behaviour, Event } from '@/types';
import { TrackCard } from '@/components/tracks/TrackCard';
import { TrackDetailView } from '@/components/tracks/TrackDetailView';
import {
  Compass,
  RefreshCw,
  AlertCircle,
  Search,
  Users,
} from 'lucide-react';

export const TracksPage: React.FC = () => {
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const [tracks, setTracks] = useState<Track[]>([]);
  const [behaviours, setBehaviours] = useState<Behaviour[]>([]);
  const [events, setEvents] = useState<Event[]>([]);

  const [selectedTrackId, setSelectedTrackId] = useState<number | null>(7);
  const [searchQuery, setSearchQuery] = useState<string>('');

  const loadTrackData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [tList, bList, eList] = await Promise.all([
        api.getTracks('vid-autovision-001'),
        api.getBehaviours('vid-autovision-001'),
        api.getEvents('vid-autovision-001'),
      ]);

      setTracks(tList);
      setBehaviours(bList);
      setEvents(eList);

      // Default selection to track 7 if available, or first track
      if (tList.length > 0) {
        const hasTrack7 = tList.some((t) => t.track_id === 7);
        setSelectedTrackId(hasTrack7 ? 7 : tList[0].track_id);
      }
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to load tracked entities data';
      setError(msg);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadTrackData();
  }, [loadTrackData]);

  // Unique track IDs
  const uniqueTrackIds = useMemo(() => {
    const ids = Array.from(new Set(tracks.map((t) => t.track_id))).sort((a, b) => a - b);
    if (!searchQuery.trim()) return ids;
    return ids.filter((id) => `person #${id}`.toLowerCase().includes(searchQuery.toLowerCase()) || id.toString().includes(searchQuery));
  }, [tracks, searchQuery]);

  // Selected track records
  const selectedTrackDetections = useMemo(() => {
    if (selectedTrackId === null) return [];
    return tracks.filter((t) => t.track_id === selectedTrackId);
  }, [tracks, selectedTrackId]);

  const selectedTrackBehaviours = useMemo(() => {
    if (selectedTrackId === null) return [];
    return behaviours.filter((b) => b.track_id === selectedTrackId);
  }, [behaviours, selectedTrackId]);

  const selectedTrackEvents = useMemo(() => {
    if (selectedTrackId === null) return [];
    return events.filter((e) => e.track_id === selectedTrackId);
  }, [events, selectedTrackId]);

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800/80 pb-4">
        <div>
          <h1 className="text-xl font-bold tracking-tight text-white flex items-center gap-2">
            <Compass className="h-5 w-5 text-cyan-400" />
            Track Explorer &amp; Entity Dossiers
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            DeepSORT entity lifecycle analysis, temporal behavior histories, and per-entity security anomalies.
          </p>
        </div>

        <button
          onClick={loadTrackData}
          disabled={loading}
          className="self-start sm:self-auto px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-800 hover:border-slate-700 text-xs text-slate-300 hover:text-white flex items-center gap-2 transition-colors disabled:opacity-50"
          title="Reload tracks from service layer"
        >
          <RefreshCw className={`h-3.5 w-3.5 ${loading ? 'animate-spin text-cyan-400' : ''}`} />
          <span>Sync Tracks</span>
        </button>
      </div>

      {/* Error View */}
      {error && !loading && (
        <div className="p-4 rounded-lg bg-rose-500/10 border border-rose-500/30 flex items-start justify-between text-xs text-rose-300">
          <div className="flex items-start gap-2">
            <AlertCircle className="h-4 w-4 text-rose-400 shrink-0 mt-0.5" />
            <div>
              <p className="font-semibold text-rose-200">Track Ingestion Failed</p>
              <p className="text-[11px] text-rose-400/80 mt-0.5">{error}</p>
            </div>
          </div>
          <button
            onClick={loadTrackData}
            className="px-2.5 py-1 rounded bg-rose-500/20 hover:bg-rose-500/30 font-medium text-rose-200"
          >
            Retry
          </button>
        </div>
      )}

      {/* Main Content Layout */}
      {loading ? (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 animate-pulse">
          <div className="lg:col-span-4 space-y-3">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="h-28 bg-slate-900/60 border border-slate-800 rounded-lg"></div>
            ))}
          </div>
          <div className="lg:col-span-8">
            <div className="h-96 bg-slate-900/60 border border-slate-800 rounded-lg"></div>
          </div>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Left Column: Entity Selector List (4 cols) */}
          <div className="lg:col-span-4 space-y-3">
            {/* Search filter */}
            <div className="relative">
              <Search className="h-4 w-4 text-slate-500 absolute left-3 top-1/2 -translate-y-1/2 pointer-events-none" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search by Track ID..."
                className="w-full bg-slate-900/80 border border-slate-800 rounded-lg pl-9 pr-3 py-2 text-xs text-white placeholder-slate-500 focus:outline-hidden focus:border-cyan-500 transition-colors"
              />
            </div>

            <div className="flex items-center justify-between text-xs text-slate-400 px-1 pt-1">
              <span className="flex items-center gap-1.5 font-mono text-[11px]">
                <Users className="h-3.5 w-3.5 text-cyan-400" />
                <span>{uniqueTrackIds.length} Entities Indexed</span>
              </span>
              <span className="text-[10px] text-slate-500 font-mono">DeepSORT</span>
            </div>

            <div className="space-y-2.5 overflow-y-auto max-h-[620px] pr-1">
              {uniqueTrackIds.map((id) => (
                <TrackCard
                  key={id}
                  trackId={id}
                  detections={tracks.filter((t) => t.track_id === id)}
                  behaviours={behaviours.filter((b) => b.track_id === id)}
                  events={events.filter((e) => e.track_id === id)}
                  isSelected={id === selectedTrackId}
                  onSelect={(selectedId) => setSelectedTrackId(selectedId)}
                />
              ))}

              {uniqueTrackIds.length === 0 && (
                <div className="p-8 text-center border border-dashed border-slate-800 rounded-lg text-xs text-slate-500">
                  No tracked entities matched "{searchQuery}"
                </div>
              )}
            </div>
          </div>

          {/* Right Column: Detailed Entity Dossier (8 cols) */}
          <div className="lg:col-span-8">
            {selectedTrackId !== null && selectedTrackDetections.length > 0 ? (
              <TrackDetailView
                trackId={selectedTrackId}
                detections={selectedTrackDetections}
                behaviours={selectedTrackBehaviours}
                events={selectedTrackEvents}
              />
            ) : (
              <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-12 text-center text-slate-500">
                <Compass className="h-10 w-10 text-slate-700 mx-auto mb-3" />
                <p className="text-sm font-medium text-slate-300">No entity selected</p>
                <p className="text-xs text-slate-500 mt-1">
                  Choose a tracked entity from the left list to inspect its trajectory and timeline.
                </p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
