import React, { useState } from 'react';
import { api } from '@/services/api';
import {
  Sliders,
  Server,
  Activity,
  Users2,
  CheckCircle2,
  AlertCircle,
  Cpu,
  Database,
  Eye,
  GitBranch,
  RefreshCw,
  ExternalLink,
} from 'lucide-react';

export const SettingsPage: React.FC = () => {
  const [detectionThreshold, setDetectionThreshold] = useState(0.65);
  const [behaviourSensitivity, setBehaviourSensitivity] = useState(0.75);
  const [alertThreshold, setAlertThreshold] = useState(0.8);

  const [mockMode, setMockMode] = useState<boolean>(api.isMockMode());
  const [backendInputUrl, setBackendInputUrl] = useState<string>(api.getBackendUrl());
  const [pinging, setPinging] = useState<boolean>(false);
  const [healthInfo, setHealthInfo] = useState<{
    status: string;
    online: boolean;
    latencyMs?: number;
  } | null>(null);

  const handleSaveBackend = () => {
    api.setBackendUrl(backendInputUrl.trim());
    handlePing();
  };

  const handleApplyPreset = (url: string) => {
    setBackendInputUrl(url);
    api.setBackendUrl(url);
  };

  const handlePing = async () => {
    setPinging(true);
    try {
      const res = await api.checkHealth();
      setHealthInfo(res);
    } catch {
      setHealthInfo({ status: 'offline', online: false });
    } finally {
      setPinging(false);
    }
  };


  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="border-b border-slate-800/80 pb-4">
        <h1 className="text-xl font-bold tracking-tight text-white flex items-center gap-2">
          <Sliders className="h-5 w-5 text-cyan-400" />
          System Settings &amp; Architecture Control
        </h1>
        <p className="text-xs text-slate-400 mt-1">
          Computer vision thresholds, sensitivity parameters, backend endpoint mapping, and team integration pipeline.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* CV Algorithm Parameters */}
        <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-5 space-y-5">
          <h2 className="text-sm font-semibold text-slate-200 flex items-center gap-2 border-b border-slate-800 pb-3">
            <Activity className="h-4 w-4 text-cyan-400" />
            Detection &amp; Anomaly Thresholds
          </h2>

          <div className="space-y-2">
            <div className="flex justify-between text-xs">
              <span className="text-slate-300">Detection Confidence Threshold</span>
              <span className="font-mono text-cyan-400 font-bold">{detectionThreshold}</span>
            </div>
            <input
              type="range"
              min="0.3"
              max="0.95"
              step="0.05"
              value={detectionThreshold}
              onChange={(e) => setDetectionThreshold(parseFloat(e.target.value))}
              className="w-full accent-cyan-500 bg-slate-800 h-1.5 rounded-lg appearance-none cursor-pointer"
            />
            <p className="text-[10px] text-slate-500">
              Minimum YOLOv8 object confidence required to instantiate a target track.
            </p>
          </div>

          <div className="space-y-2">
            <div className="flex justify-between text-xs">
              <span className="text-slate-300">Behaviour Sensitivity</span>
              <span className="font-mono text-cyan-400 font-bold">{behaviourSensitivity}</span>
            </div>
            <input
              type="range"
              min="0.3"
              max="0.95"
              step="0.05"
              value={behaviourSensitivity}
              onChange={(e) => setBehaviourSensitivity(parseFloat(e.target.value))}
              className="w-full accent-cyan-500 bg-slate-800 h-1.5 rounded-lg appearance-none cursor-pointer"
            />
            <p className="text-[10px] text-slate-500">
              Temporal window sensitivity for identifying rapid transitions, slips, or falls.
            </p>
          </div>

          <div className="space-y-2">
            <div className="flex justify-between text-xs">
              <span className="text-slate-300">Alert Escalation Threshold</span>
              <span className="font-mono text-cyan-400 font-bold">{alertThreshold}</span>
            </div>
            <input
              type="range"
              min="0.5"
              max="0.99"
              step="0.01"
              value={alertThreshold}
              onChange={(e) => setAlertThreshold(parseFloat(e.target.value))}
              className="w-full accent-cyan-500 bg-slate-800 h-1.5 rounded-lg appearance-none cursor-pointer"
            />
            <p className="text-[10px] text-slate-500">
              Confidence score threshold before triggering a HIGH RISK security advisory.
            </p>
          </div>
        </div>

        {/* Multi-Laptop Network Configuration & Backend Connection Manager (readme_backend.md) */}
        <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-5 space-y-4">
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <h2 className="text-sm font-semibold text-slate-200 flex items-center gap-2">
              <Server className="h-4 w-4 text-cyan-400" />
              Multi-Laptop Network &amp; Backend Gateway
            </h2>
            <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-cyan-950 text-cyan-300 border border-cyan-800">
              README_MULTI_LAPTOP_CONNECT.md
            </span>
          </div>

          <div className="space-y-3 text-xs">
            {/* Mode Selector */}
            <div className="flex items-center justify-between p-2.5 rounded-lg bg-slate-950/80 border border-slate-800">
              <div>
                <span className="font-semibold text-white block">Environment Mode</span>
                <span className="text-[11px] text-slate-400">
                  {mockMode ? 'Standalone Mock Engine (Local Demo Safe)' : 'Live FastAPI Backend Stream'}
                </span>
              </div>
              <button
                type="button"
                onClick={() => {
                  const newMode = !mockMode;
                  setMockMode(newMode);
                  api.setMockMode(newMode);
                }}
                className={`px-3 py-1.5 rounded-lg font-mono font-bold text-xs transition-colors border ${
                  mockMode
                    ? 'bg-cyan-500/15 text-cyan-300 border-cyan-500/40 hover:bg-cyan-500/25'
                    : 'bg-emerald-500/15 text-emerald-300 border-emerald-500/40 hover:bg-emerald-500/25'
                }`}
              >
                {mockMode ? 'SWITCH TO LIVE API' : 'SWITCH TO MOCK'}
              </button>
            </div>

            {/* Target Backend URL Input */}
            <div className="space-y-1.5">
              <label className="text-slate-300 font-medium block">
                Target Backend IP / Base URL (Member 3)
              </label>
              <div className="flex gap-2">
                <input
                  type="text"
                  value={backendInputUrl}
                  onChange={(e) => setBackendInputUrl(e.target.value)}
                  placeholder="http://192.168.1.50:8000"
                  className="flex-1 bg-slate-950 border border-slate-800 rounded-lg px-3 py-1.5 text-xs font-mono text-white focus:border-cyan-500 focus:outline-hidden"
                />
                <button
                  type="button"
                  onClick={handleSaveBackend}
                  className="px-3 py-1.5 rounded-lg bg-cyan-500 text-slate-950 font-bold hover:bg-cyan-400 transition-colors shadow-xs"
                >
                  Save URL
                </button>
              </div>
              <p className="text-[10px] text-slate-500">
                Configure Member 3 Wi-Fi LAN IP (e.g. <code>http://192.168.x.x:8000</code>) or ngrok tunnel URL.
              </p>
            </div>

            {/* Quick URL Presets */}
            <div className="flex items-center gap-2 pt-1 flex-wrap">
              <span className="text-[10px] text-slate-500 font-mono">Presets:</span>
              <button
                type="button"
                onClick={() => handleApplyPreset('http://localhost:8000')}
                className="px-2 py-0.5 rounded bg-slate-950 text-slate-400 hover:text-white border border-slate-800 text-[10px] font-mono transition-colors"
              >
                localhost:8000
              </button>
              <button
                type="button"
                onClick={() => handleApplyPreset('http://192.168.1.100:8000')}
                className="px-2 py-0.5 rounded bg-slate-950 text-slate-400 hover:text-white border border-slate-800 text-[10px] font-mono transition-colors"
              >
                Wi-Fi LAN IP
              </button>
              <button
                type="button"
                onClick={() => handleApplyPreset('https://autovision.ngrok-free.app')}
                className="px-2 py-0.5 rounded bg-slate-950 text-slate-400 hover:text-white border border-slate-800 text-[10px] font-mono transition-colors"
              >
                ngrok Tunnel
              </button>
            </div>

            {/* Ping & Telemetry Status */}
            <div className="pt-2 border-t border-slate-800/80 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <button
                  type="button"
                  onClick={handlePing}
                  disabled={pinging}
                  className="px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-200 font-medium text-[11px] flex items-center gap-1.5 transition-colors disabled:opacity-50"
                >
                  <RefreshCw className={`h-3 w-3 ${pinging ? 'animate-spin text-cyan-400' : ''}`} />
                  <span>{pinging ? 'Testing...' : 'Test Connection / Ping'}</span>
                </button>
                {healthInfo && (
                  <span
                    className={`text-[11px] font-mono flex items-center gap-1 ${
                      healthInfo.online ? 'text-emerald-400' : 'text-rose-400'
                    }`}
                  >
                    {healthInfo.online ? (
                      <CheckCircle2 className="h-3.5 w-3.5" />
                    ) : (
                      <AlertCircle className="h-3.5 w-3.5" />
                    )}
                    {healthInfo.online
                      ? `ONLINE (${healthInfo.latencyMs ?? 1}ms)`
                      : 'OFFLINE / UNREACHABLE'}
                  </span>
                )}
              </div>

              <a
                href={`${backendInputUrl}/docs`}
                target="_blank"
                rel="noreferrer"
                className="text-[11px] text-cyan-400 hover:underline flex items-center gap-1 font-mono"
              >
                <span>Swagger Docs</span>
                <ExternalLink className="h-3 w-3" />
              </a>
            </div>
          </div>
        </div>
      </div>


      {/* Team Integration & System Architecture Map */}
      <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-5 space-y-4">
        <div className="flex items-center justify-between border-b border-slate-800 pb-3">
          <div className="flex items-center gap-2">
            <Users2 className="h-4 w-4 text-cyan-400" />
            <h3 className="text-sm font-bold text-white tracking-tight">
              4-Person Team Integration Architecture
            </h3>
          </div>
          <span className="text-[10px] font-mono text-slate-400 flex items-center gap-1">
            <GitBranch className="h-3 w-3 text-cyan-400" /> Problem Statement: HNX26PSI07
          </span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
          <div className="p-3.5 rounded-lg bg-slate-950/70 border border-slate-800 space-y-2">
            <div className="flex items-center justify-between text-xs">
              <span className="font-mono font-bold text-cyan-300">Member 1</span>
              <span className="p-1 rounded bg-cyan-500/10 text-cyan-400">
                <Cpu className="h-3.5 w-3.5" />
              </span>
            </div>
            <h4 className="text-xs font-semibold text-white">Detection &amp; Tracking</h4>
            <p className="text-[11px] text-slate-400 leading-relaxed">
              YOLOv8 object detector and DeepSORT tracker producing Track entities &amp; bounding boxes.
            </p>
            <div className="text-[10px] font-mono text-emerald-400 flex items-center gap-1 pt-1">
              <CheckCircle2 className="h-3 w-3" /> Contract Ready: Track[]
            </div>
          </div>

          <div className="p-3.5 rounded-lg bg-slate-950/70 border border-slate-800 space-y-2">
            <div className="flex items-center justify-between text-xs">
              <span className="font-mono font-bold text-sky-300">Member 2</span>
              <span className="p-1 rounded bg-sky-500/10 text-sky-400">
                <Activity className="h-3.5 w-3.5" />
              </span>
            </div>
            <h4 className="text-xs font-semibold text-white">Behaviour Recognition</h4>
            <p className="text-[11px] text-slate-400 leading-relaxed">
              Spatio-temporal action analysis models classifying stationary, entry, and fall behaviors.
            </p>
            <div className="text-[10px] font-mono text-emerald-400 flex items-center gap-1 pt-1">
              <CheckCircle2 className="h-3 w-3" /> Contract Ready: Behaviour[]
            </div>
          </div>

          <div className="p-3.5 rounded-lg bg-slate-950/70 border border-slate-800 space-y-2">
            <div className="flex items-center justify-between text-xs">
              <span className="font-mono font-bold text-amber-300">Member 3</span>
              <span className="p-1 rounded bg-amber-500/10 text-amber-400">
                <Database className="h-3.5 w-3.5" />
              </span>
            </div>
            <h4 className="text-xs font-semibold text-white">FastAPI &amp; Event Engine</h4>
            <p className="text-[11px] text-slate-400 leading-relaxed">
              PostgreSQL schema, rule violation engine, incident evidence storage, and REST APIs.
            </p>
            <div className="text-[10px] font-mono text-emerald-400 flex items-center gap-1 pt-1">
              <CheckCircle2 className="h-3 w-3" /> Contract Ready: Event[]
            </div>
          </div>

          <div className="p-3.5 rounded-lg bg-slate-950/70 border border-cyan-500/40 bg-cyan-500/5 space-y-2">
            <div className="flex items-center justify-between text-xs">
              <span className="font-mono font-bold text-cyan-300">Frontend (You)</span>
              <span className="p-1 rounded bg-cyan-500/20 text-cyan-300">
                <Eye className="h-3.5 w-3.5" />
              </span>
            </div>
            <h4 className="text-xs font-semibold text-white">UI &amp; System Integration</h4>
            <p className="text-[11px] text-slate-400 leading-relaxed">
              Dashboard telemetry, Video Intelligence overlay, forensic event dossiers, and analytics.
            </p>
            <div className="text-[10px] font-mono text-cyan-400 flex items-center gap-1 pt-1">
              <CheckCircle2 className="h-3 w-3" /> Complete &amp; Verified
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
