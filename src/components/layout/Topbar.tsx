import React, { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import {
  Menu,
  Server,
  Bell,
  Clock,
  ChevronRight,
} from 'lucide-react';
import { api } from '@/services/api';

interface TopbarProps {
  onMenuClick: () => void;
}

const routeTitles: Record<string, { title: string; subtitle: string }> = {
  '/dashboard': {
    title: 'Dashboard',
    subtitle: 'High-level telemetry, KPI metrics, and recent anomaly overview',
  },
  '/analysis': {
    title: 'Video Analysis',
    subtitle: 'Real-time multi-track video intelligence and trajectory overlay workspace',
  },
  '/events': {
    title: 'Events',
    subtitle: 'Catalog of abnormal behaviors, safety threshold breaches, and evidence logs',
  },
  '/tracks': {
    title: 'Track Explorer',
    subtitle: 'Entity trajectory inspection, lifecycle metrics, and state history',
  },
  '/analytics': {
    title: 'Analytics',
    subtitle: 'Aggregated statistical metrics, risk heatmaps, and category distributions',
  },
  '/settings': {
    title: 'Settings',
    subtitle: 'Computer vision thresholds, sensitivity parameters, and network connectivity',
  },
};

export const Topbar: React.FC<TopbarProps> = ({ onMenuClick }) => {
  const location = useLocation();
  const [timeString, setTimeString] = useState<string>('');
  const [backendHealth, setBackendHealth] = useState<{ status: string; online: boolean }>({
    status: 'online (mock)',
    online: true,
  });

  const isMock = api.isMockMode();
  const backendUrl = api.getBackendUrl();
  const currentRouteInfo = routeTitles[location.pathname] || {
    title: 'AUTOVISION Workspace',
    subtitle: 'Autonomous Vision & Behaviour Intelligence',
  };

  useEffect(() => {
    // Update live clock
    const updateTime = () => {
      const now = new Date();
      setTimeString(
        now.toLocaleTimeString('en-US', {
          hour12: false,
          hour: '2-digit',
          minute: '2-digit',
          second: '2-digit',
        })
      );
    };
    updateTime();
    const timer = setInterval(updateTime, 1000);

    // Initial health check
    api.checkHealth().then(setBackendHealth).catch(() => {
      setBackendHealth({ status: 'offline', online: false });
    });

    return () => clearInterval(timer);
  }, []);

  return (
    <header className="h-16 border-b border-slate-800/80 bg-slate-950/80 backdrop-blur-md px-4 sm:px-6 flex items-center justify-between sticky top-0 z-30">
      {/* Left: Mobile hamburger + Page Breadcrumbs */}
      <div className="flex items-center gap-3">
        <button
          onClick={onMenuClick}
          className="md:hidden text-slate-400 hover:text-white p-2 rounded-lg hover:bg-slate-850"
          aria-label="Open sidebar"
        >
          <Menu className="h-5 w-5" />
        </button>

        <div className="flex flex-col">
          <div className="flex items-center gap-1.5 text-xs text-slate-400">
            <span className="font-semibold text-slate-300">AUTOVISION</span>
            <ChevronRight className="h-3 w-3 text-slate-400" />
            <span className="text-cyan-400 font-medium">{currentRouteInfo.title}</span>
          </div>
          <h1 className="text-sm font-bold text-white tracking-tight hidden sm:block">
            {currentRouteInfo.title}
          </h1>
        </div>
      </div>

      {/* Right: Telemetry, Backend Status, Clock, Alerts */}
      <div className="flex items-center gap-3">
        {/* Live Timestamp (Monitoring Center standard) */}
        <div className="hidden lg:flex items-center gap-1.5 px-2.5 py-1 rounded bg-slate-900 border border-slate-800 text-[11px] font-mono text-slate-300">
          <Clock className="h-3.5 w-3.5 text-cyan-400" />
          <span>{timeString || '00:00:00'}</span>
        </div>

        {/* Backend Connectivity Status */}
        <div className="hidden sm:flex items-center gap-1.5 px-2.5 py-1 rounded bg-slate-900 border border-slate-800 text-[11px] font-mono">
          <Server className="h-3.5 w-3.5 text-slate-400" />
          <span className="text-slate-400">API:</span>
          <span className={isMock ? 'text-amber-400' : 'text-cyan-400'}>
            {isMock ? 'MOCK ENGINE' : backendUrl.replace('http://', '')}
          </span>
        </div>

        {/* System Online Status Indicator */}
        <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-slate-900/90 border border-slate-800 text-xs font-mono">
          <span
            className={`h-2 w-2 rounded-full ${
              backendHealth.online
                ? 'bg-emerald-400 shadow-xs shadow-emerald-400/50 animate-pulse'
                : 'bg-rose-500'
            }`}
          />
          <span className="font-semibold tracking-wider text-slate-200 text-[11px]">
            {backendHealth.online ? 'SYSTEM ONLINE' : 'OFFLINE'}
          </span>
        </div>

        {/* Quick Alert Bell */}
        <div className="relative">
          <button
            className="p-2 rounded-lg bg-slate-900 border border-slate-800 text-slate-400 hover:text-white hover:bg-slate-850 transition-colors"
            title="Active Security Alerts"
            aria-label="Active Security Alerts"
          >
            <Bell className="h-4 w-4" />
            <span className="absolute -top-1 -right-1 flex h-4 w-4 items-center justify-center rounded-full bg-rose-600 text-[9px] font-bold text-white font-mono">
              2
            </span>
          </button>
        </div>
      </div>
    </header>
  );
};
