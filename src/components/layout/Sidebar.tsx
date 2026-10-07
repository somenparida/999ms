import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  Video,
  AlertCircle,
  Compass,
  BarChart3,
  Settings,
  Shield,
  Radio,
  X,
  Cpu,
} from 'lucide-react';
import { api } from '@/services/api';

interface SidebarProps {
  isOpen: boolean;
  onClose: () => void;
}

interface NavItem {
  name: string;
  path: string;
  icon: React.ComponentType<{ className?: string }>;
  badge?: string;
}

const navItems: NavItem[] = [
  { name: 'Dashboard', path: '/dashboard', icon: LayoutDashboard },
  { name: 'Video Analysis', path: '/analysis', icon: Video },
  { name: 'Events', path: '/events', icon: AlertCircle, badge: '4' },
  { name: 'Track Explorer', path: '/tracks', icon: Compass },
  { name: 'Analytics', path: '/analytics', icon: BarChart3 },
  { name: 'Settings', path: '/settings', icon: Settings },
];

export const Sidebar: React.FC<SidebarProps> = ({ isOpen, onClose }) => {
  const isMock = api.isMockMode();

  return (
    <>
      {/* Mobile backdrop */}
      {isOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/70 backdrop-blur-xs md:hidden"
          onClick={onClose}
          aria-hidden="true"
        />
      )}

      {/* Sidebar container */}
      <aside
        className={`fixed inset-y-0 left-0 z-50 w-64 bg-slate-950 border-r border-slate-800/80 flex flex-col transition-transform duration-200 ease-in-out md:translate-x-0 md:static ${
          isOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        {/* Brand Header */}
        <div className="h-16 px-5 border-b border-slate-800/80 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="h-9 w-9 rounded-lg bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center text-cyan-400 shadow-sm shadow-cyan-500/10">
              <Shield className="h-5 w-5" />
            </div>
            <div>
              <div className="flex items-center gap-1.5">
                <span className="font-bold text-sm tracking-wider text-white">AUTOVISION</span>
                <span className="text-[10px] font-mono px-1.5 py-0.2 rounded bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
                  v1.0
                </span>
              </div>
              <p className="text-[10px] text-slate-400 leading-tight truncate">
                Autonomous Vision &amp; AI
              </p>
            </div>
          </div>

          {/* Close button for mobile */}
          <button
            onClick={onClose}
            className="md:hidden text-slate-400 hover:text-white p-1 rounded-md hover:bg-slate-800/60"
            aria-label="Close sidebar"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Primary Navigation */}
        <div className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
          <div className="px-3 pb-2 text-[10px] font-mono font-semibold uppercase tracking-wider text-slate-400">
            Navigation
          </div>

          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.path}
                to={item.path}
                onClick={onClose}
                className={({ isActive }) =>
                  `group flex items-center justify-between px-3 py-2 rounded-md text-xs font-medium transition-all duration-150 ${
                    isActive
                      ? 'bg-cyan-500/15 text-cyan-300 border-l-3 border-cyan-400 pl-2.5 font-semibold shadow-xs'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900/80'
                  }`
                }
              >
                <div className="flex items-center gap-3">
                  <Icon className="h-4 w-4 shrink-0 transition-colors group-hover:text-cyan-400" />
                  <span>{item.name}</span>
                </div>
                {item.badge && (
                  <span className="text-[10px] font-mono font-bold px-1.5 py-0.2 rounded bg-rose-500/20 text-rose-400 border border-rose-500/30">
                    {item.badge}
                  </span>
                )}
              </NavLink>
            );
          })}
        </div>

        {/* Telemetry / Status Footer */}
        <div className="p-3 border-t border-slate-800/80 bg-slate-950/60">
          <div className="rounded-lg bg-slate-900/60 border border-slate-800 p-3 space-y-2">
            <div className="flex items-center justify-between text-[11px]">
              <span className="text-slate-400 flex items-center gap-1.5 font-mono">
                <Radio className="h-3 w-3 text-emerald-400 animate-pulse" />
                Pipeline Engine
              </span>
              <span className="text-emerald-400 font-mono text-[10px] font-semibold">ONLINE</span>
            </div>
            <div className="text-[10px] text-slate-400 space-y-1 font-mono pt-1 border-t border-slate-800/60">
              <div className="flex items-center justify-between">
                <span className="flex items-center gap-1">
                  <Cpu className="h-3 w-3 text-cyan-400" /> Model
                </span>
                <span className="text-slate-300">YOLOv8 + DeepSORT</span>
              </div>
              <div className="flex items-center justify-between">
                <span>Mode</span>
                <span className={isMock ? 'text-amber-400 font-semibold' : 'text-cyan-400'}>
                  {isMock ? 'Mock API Engine' : 'Live FastAPI'}
                </span>
              </div>
            </div>
          </div>
        </div>
      </aside>
    </>
  );
};
