import React from 'react';
import { ShieldAlert, AlertTriangle, Info } from 'lucide-react';

interface SeverityBadgeProps {
  severity: 'low' | 'medium' | 'high';
  className?: string;
  showIcon?: boolean;
}

const severityConfig = {
  high: {
    label: 'HIGH RISK',
    style: 'bg-rose-500/10 text-rose-400 border-rose-500/30',
    icon: ShieldAlert,
    dot: 'bg-rose-500',
  },
  medium: {
    label: 'MED RISK',
    style: 'bg-amber-500/10 text-amber-400 border-amber-500/30',
    icon: AlertTriangle,
    dot: 'bg-amber-400',
  },
  low: {
    label: 'LOW RISK',
    style: 'bg-sky-500/10 text-sky-400 border-sky-500/30',
    icon: Info,
    dot: 'bg-sky-400',
  },
};

export const SeverityBadge: React.FC<SeverityBadgeProps> = ({
  severity,
  className = '',
  showIcon = true,
}) => {
  const config = severityConfig[severity] || severityConfig.medium;
  const Icon = config.icon;

  return (
    <span
      className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded text-[10px] font-mono font-bold tracking-wider uppercase border ${config.style} ${className}`}
    >
      {showIcon && <Icon className="h-3 w-3 shrink-0" />}
      <span>{config.label}</span>
    </span>
  );
};
