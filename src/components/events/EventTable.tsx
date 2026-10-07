import React from 'react';
import { Event } from '@/types';
import { SeverityBadge } from './SeverityBadge';
import { Clock, Eye, Image as ImageIcon, Crosshair } from 'lucide-react';

interface EventTableProps {
  events: Event[];
  selectedEventId: string | null;
  onSelectEvent: (event: Event) => void;
}

const formatTime = (seconds: number): string => {
  const mins = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
};

export const EventTable: React.FC<EventTableProps> = ({
  events,
  selectedEventId,
  onSelectEvent,
}) => {
  if (events.length === 0) {
    return (
      <div className="py-16 text-center border border-dashed border-slate-800 rounded-lg bg-slate-900/30">
        <p className="text-sm font-medium text-slate-300">No events found matching current criteria</p>
        <p className="text-xs text-slate-500 mt-1">Try relaxing search terms or severity filters.</p>
      </div>
    );
  }

  return (
    <div className="border border-slate-800 rounded-lg overflow-hidden bg-slate-900/50 shadow-md">
      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs text-slate-300">
          <thead className="bg-slate-900/90 text-slate-400 border-b border-slate-800 uppercase font-mono text-[11px] tracking-wider">
            <tr>
              <th className="py-3 px-4">Event ID</th>
              <th className="py-3 px-4">Entity</th>
              <th className="py-3 px-4">Event Classification</th>
              <th className="py-3 px-4">Time Window</th>
              <th className="py-3 px-4">Confidence</th>
              <th className="py-3 px-4">Severity</th>
              <th className="py-3 px-4">Evidence</th>
              <th className="py-3 px-4 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/80">
            {events.map((evt) => {
              const isSelected = evt.event_id === selectedEventId;
              return (
                <tr
                  key={evt.event_id}
                  onClick={() => onSelectEvent(evt)}
                  className={`cursor-pointer transition-colors ${
                    isSelected
                      ? 'bg-cyan-500/15 text-white'
                      : 'hover:bg-slate-850/60 hover:text-white'
                  }`}
                >
                  <td className="py-3 px-4 font-mono font-bold text-cyan-400">
                    {evt.event_id}
                  </td>
                  <td className="py-3 px-4 font-mono text-slate-200">
                    <span className="flex items-center gap-1.5">
                      <Crosshair className="h-3 w-3 text-cyan-400" />
                      Person #{evt.track_id}
                    </span>
                  </td>
                  <td className="py-3 px-4 font-semibold text-white">
                    {evt.event_type}
                  </td>
                  <td className="py-3 px-4 font-mono text-slate-400 whitespace-nowrap">
                    <span className="flex items-center gap-1.5">
                      <Clock className="h-3 w-3 text-slate-500" />
                      {formatTime(evt.start_time)} – {formatTime(evt.end_time)}
                    </span>
                  </td>
                  <td className="py-3 px-4 font-mono text-slate-300">
                    {(evt.confidence * 100).toFixed(0)}%
                  </td>
                  <td className="py-3 px-4">
                    <SeverityBadge severity={evt.severity} />
                  </td>
                  <td className="py-3 px-4">
                    {evt.evidence_url ? (
                      <span className="inline-flex items-center gap-1 text-[11px] font-mono text-emerald-400 px-2 py-0.5 rounded bg-emerald-500/10 border border-emerald-500/20">
                        <ImageIcon className="h-3 w-3" />
                        Available
                      </span>
                    ) : (
                      <span className="text-[11px] font-mono text-slate-500">None</span>
                    )}
                  </td>
                  <td className="py-3 px-4 text-right">
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        onSelectEvent(evt);
                      }}
                      className="px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 text-cyan-300 hover:text-white text-[11px] font-medium border border-slate-700 inline-flex items-center gap-1 transition-colors"
                    >
                      <Eye className="h-3 w-3" />
                      <span>Details</span>
                    </button>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
};
