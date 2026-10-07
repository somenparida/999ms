import React from 'react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Cell,
} from 'recharts';
import { PieChart, AlertCircle } from 'lucide-react';

interface EventDistributionChartProps {
  data: { name: string; count: number }[];
  loading: boolean;
  error?: string | null;
}

const BAR_COLORS = ['#38bdf8', '#fbbf24', '#f43f5e', '#34d399', '#a78bfa', '#f97316'];

export const EventDistributionChart: React.FC<EventDistributionChartProps> = ({
  data,
  loading,
  error,
}) => {
  return (
    <div className="bg-slate-900/60 border border-slate-800 rounded-lg p-5 flex flex-col h-full">
      <div className="flex items-center justify-between border-b border-slate-800/80 pb-3 mb-4">
        <div className="flex items-center gap-2">
          <div className="p-1 rounded bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
            <PieChart className="h-4 w-4" />
          </div>
          <div>
            <h2 className="text-sm font-semibold text-white">Event Distribution</h2>
            <p className="text-[11px] text-slate-400">Frequency breakdown by detected event class</p>
          </div>
        </div>
        <span className="text-[11px] font-mono text-slate-500">
          Total Classes: <strong className="text-slate-300">{data.length}</strong>
        </span>
      </div>

      {loading && (
        <div className="flex-1 flex items-center justify-center min-h-[220px]">
          <div className="space-y-3 w-full px-4 animate-pulse">
            <div className="h-4 bg-slate-800 rounded w-1/3"></div>
            <div className="h-32 bg-slate-800/50 rounded"></div>
          </div>
        </div>
      )}

      {!loading && error && (
        <div className="flex-1 flex flex-col items-center justify-center p-6 text-center min-h-[220px]">
          <AlertCircle className="h-7 w-7 text-rose-400 mb-2" />
          <p className="text-xs font-semibold text-slate-200">Failed to render distribution chart</p>
          <p className="text-[11px] text-slate-500 mt-1">{error}</p>
        </div>
      )}

      {!loading && !error && data.length === 0 && (
        <div className="flex-1 flex flex-col items-center justify-center p-6 text-center min-h-[220px] border border-dashed border-slate-800 rounded-lg">
          <p className="text-xs text-slate-400">No event distribution data available.</p>
        </div>
      )}

      {!loading && !error && data.length > 0 && (
        <div className="flex-1 min-h-[220px] w-full pt-2">
          <ResponsiveContainer width="100%" height={230}>
            <BarChart
              data={data}
              layout="vertical"
              margin={{ top: 5, right: 25, left: 10, bottom: 5 }}
            >
              <XAxis
                type="number"
                allowDecimals={false}
                stroke="#64748b"
                tick={{ fill: '#94a3b8', fontSize: 11, fontFamily: 'monospace' }}
                axisLine={{ stroke: '#334155' }}
                tickLine={false}
              />
              <YAxis
                type="category"
                dataKey="name"
                width={140}
                stroke="#64748b"
                tick={{ fill: '#cbd5e1', fontSize: 11 }}
                axisLine={{ stroke: '#334155' }}
                tickLine={false}
              />
              <Tooltip
                content={({ active, payload }) => {
                  if (active && payload && payload.length) {
                    const item = payload[0].payload;
                    return (
                      <div className="rounded-lg bg-slate-900 border border-slate-700 p-2.5 shadow-xl text-xs space-y-1">
                        <p className="font-semibold text-white">{item.name}</p>
                        <p className="font-mono text-cyan-400 font-bold">
                          Count: {item.count} detections
                        </p>
                      </div>
                    );
                  }
                  return null;
                }}
              />
              <Bar dataKey="count" radius={[0, 4, 4, 0]} barSize={16}>
                {data.map((_, index) => (
                  <Cell key={`cell-${index}`} fill={BAR_COLORS[index % BAR_COLORS.length]} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  );
};
