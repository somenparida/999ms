import React from 'react';
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
} from 'recharts';
import { SystemAnalytics } from '@/types';
import { Activity, ShieldAlert, PieChart as PieChartIcon, BarChart2 } from 'lucide-react';

const SEVERITY_COLORS: Record<string, string> = {
  high: '#f43f5e',
  medium: '#fbbf24',
  low: '#38bdf8',
};

const BEHAVIOUR_COLORS = ['#38bdf8', '#818cf8', '#34d399', '#fbbf24', '#f43f5e', '#a78bfa'];

export const ActivityOverTimeChart: React.FC<{ data: SystemAnalytics['activity_over_time'] }> = ({
  data,
}) => {
  return (
    <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-5 flex flex-col h-full">
      <div className="flex items-center justify-between border-b border-slate-800 pb-3 mb-4">
        <div className="flex items-center gap-2">
          <div className="p-1 rounded bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
            <Activity className="h-4 w-4" />
          </div>
          <div>
            <h3 className="text-xs font-bold text-white tracking-tight">Temporal Activity &amp; Breach Frequency</h3>
            <p className="text-[10px] text-slate-400">Total detected entities vs. flagged anomalies over time</p>
          </div>
        </div>
        <span className="text-[10px] font-mono text-cyan-400 px-2 py-0.5 rounded bg-slate-800 border border-slate-700">
          30s Intervals
        </span>
      </div>

      <div className="w-full h-[240px]">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={data} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
            <defs>
              <linearGradient id="colorTotal" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#38bdf8" stopOpacity={0.4} />
                <stop offset="95%" stopColor="#38bdf8" stopOpacity={0.0} />
              </linearGradient>
              <linearGradient id="colorAbnormal" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#f43f5e" stopOpacity={0.5} />
                <stop offset="95%" stopColor="#f43f5e" stopOpacity={0.0} />
              </linearGradient>
            </defs>
            <XAxis
              dataKey="time"
              stroke="#64748b"
              tick={{ fill: '#94a3b8', fontSize: 11, fontFamily: 'monospace' }}
              axisLine={{ stroke: '#334155' }}
              tickLine={false}
            />
            <YAxis
              stroke="#64748b"
              tick={{ fill: '#94a3b8', fontSize: 11, fontFamily: 'monospace' }}
              axisLine={{ stroke: '#334155' }}
              tickLine={false}
            />
            <Tooltip
              content={({ active, payload, label }) => {
                if (active && payload && payload.length) {
                  return (
                    <div className="rounded-lg bg-slate-900 border border-slate-700 p-2.5 shadow-xl text-xs space-y-1">
                      <p className="font-mono text-slate-300 font-semibold">{label}</p>
                      <p className="text-cyan-400">Total Entities: {payload[0]?.value}</p>
                      <p className="text-rose-400">Flagged Anomalies: {payload[1]?.value}</p>
                    </div>
                  );
                }
                return null;
              }}
            />
            <Legend
              wrapperStyle={{ fontSize: 11, fontFamily: 'monospace', paddingTop: 8 }}
              formatter={(value) => (value === 'count' ? 'Total Ingested Entities' : 'Abnormal Breaches')}
            />
            <Area
              type="monotone"
              dataKey="count"
              stroke="#38bdf8"
              strokeWidth={2}
              fillOpacity={1}
              fill="url(#colorTotal)"
            />
            <Area
              type="monotone"
              dataKey="abnormal"
              stroke="#f43f5e"
              strokeWidth={2}
              fillOpacity={1}
              fill="url(#colorAbnormal)"
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export const SeverityDonutChart: React.FC<{ data: SystemAnalytics['events_by_severity'] }> = ({
  data,
}) => {
  return (
    <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-5 flex flex-col h-full">
      <div className="flex items-center justify-between border-b border-slate-800 pb-3 mb-4">
        <div className="flex items-center gap-2">
          <div className="p-1 rounded bg-rose-500/10 text-rose-400 border border-rose-500/20">
            <ShieldAlert className="h-4 w-4" />
          </div>
          <div>
            <h3 className="text-xs font-bold text-white tracking-tight">Risk Tier Breakdown</h3>
            <p className="text-[10px] text-slate-400">Anomaly severity level classification</p>
          </div>
        </div>
      </div>

      <div className="w-full h-[240px] flex items-center justify-center">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={data}
              dataKey="count"
              nameKey="severity"
              cx="50%"
              cy="50%"
              innerRadius={55}
              outerRadius={80}
              paddingAngle={5}
            >
              {data.map((entry, index) => (
                <Cell
                  key={`cell-${index}`}
                  fill={SEVERITY_COLORS[entry.severity] || '#94a3b8'}
                  stroke="#020617"
                  strokeWidth={2}
                />
              ))}
            </Pie>
            <Tooltip
              content={({ active, payload }) => {
                if (active && payload && payload.length) {
                  const item = payload[0].payload;
                  return (
                    <div className="rounded-lg bg-slate-900 border border-slate-700 p-2 shadow-xl text-xs space-y-0.5">
                      <p className="font-mono font-bold text-white uppercase">{item.severity} RISK</p>
                      <p className="font-mono text-cyan-400">{item.count} Incidents</p>
                    </div>
                  );
                }
                return null;
              }}
            />
            <Legend
              formatter={(value) => `${value.toUpperCase()} RISK`}
              wrapperStyle={{ fontSize: 11, fontFamily: 'monospace', paddingTop: 8 }}
            />
          </PieChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export const BehaviourDistributionChart: React.FC<{
  data: SystemAnalytics['behaviour_distribution'];
}> = ({ data }) => {
  return (
    <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-5 flex flex-col h-full">
      <div className="flex items-center justify-between border-b border-slate-800 pb-3 mb-4">
        <div className="flex items-center gap-2">
          <div className="p-1 rounded bg-sky-500/10 text-sky-400 border border-sky-500/20">
            <BarChart2 className="h-4 w-4" />
          </div>
          <div>
            <h3 className="text-xs font-bold text-white tracking-tight">Behaviour Distribution</h3>
            <p className="text-[10px] text-slate-400">Classified action frequencies across all tracks</p>
          </div>
        </div>
      </div>

      <div className="w-full h-[240px]">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data} layout="vertical" margin={{ top: 5, right: 20, left: 20, bottom: 5 }}>
            <XAxis
              type="number"
              stroke="#64748b"
              tick={{ fill: '#94a3b8', fontSize: 11, fontFamily: 'monospace' }}
              axisLine={{ stroke: '#334155' }}
              tickLine={false}
            />
            <YAxis
              type="category"
              dataKey="behaviour"
              width={130}
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
                    <div className="rounded-lg bg-slate-900 border border-slate-700 p-2 shadow-xl text-xs space-y-0.5">
                      <p className="font-semibold text-white">{item.behaviour}</p>
                      <p className="font-mono text-cyan-400">{item.count} Instances</p>
                    </div>
                  );
                }
                return null;
              }}
            />
            <Bar dataKey="count" radius={[0, 4, 4, 0]} barSize={16}>
              {data.map((_, index) => (
                <Cell
                  key={`cell-b-${index}`}
                  fill={BEHAVIOUR_COLORS[index % BEHAVIOUR_COLORS.length]}
                />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export const EventTypeDistributionChart: React.FC<{ data: SystemAnalytics['events_by_type'] }> = ({
  data,
}) => {
  return (
    <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-5 flex flex-col h-full">
      <div className="flex items-center justify-between border-b border-slate-800 pb-3 mb-4">
        <div className="flex items-center gap-2">
          <div className="p-1 rounded bg-amber-500/10 text-amber-400 border border-amber-500/20">
            <PieChartIcon className="h-4 w-4" />
          </div>
          <div>
            <h3 className="text-xs font-bold text-white tracking-tight">Events by Incident Type</h3>
            <p className="text-[10px] text-slate-400">Categorical distribution of anomaly triggers</p>
          </div>
        </div>
      </div>

      <div className="w-full h-[240px]">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data} layout="vertical" margin={{ top: 5, right: 20, left: 30, bottom: 5 }}>
            <XAxis
              type="number"
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
                    <div className="rounded-lg bg-slate-900 border border-slate-700 p-2 shadow-xl text-xs space-y-0.5">
                      <p className="font-semibold text-white">{item.name}</p>
                      <p className="font-mono text-cyan-400">{item.count} Detections</p>
                    </div>
                  );
                }
                return null;
              }}
            />
            <Bar dataKey="count" radius={[0, 4, 4, 0]} barSize={16} fill="#38bdf8">
              {data.map((_, index) => (
                <Cell
                  key={`cell-e-${index}`}
                  fill={BEHAVIOUR_COLORS[(index + 2) % BEHAVIOUR_COLORS.length]}
                />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};
