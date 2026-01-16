'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { clsx } from 'clsx';
import {
  Wifi,
  WifiOff,
  RefreshCw,
  Clock,
  AlertTriangle,
  CheckCircle,
  Activity,
  ExternalLink,
} from 'lucide-react';

type APIStatus = 'online' | 'offline' | 'degraded' | 'maintenance' | 'unknown';

interface APIStatusCardProps {
  id: string;
  name: string;
  description?: string;
  provider: string;
  status: APIStatus;
  lastCheck?: Date;
  lastSync?: Date;
  uptime?: number; // percentage
  responseTime?: number; // ms
  endpoint?: string;
  onRefresh?: (id: string) => void;
  onConfigure?: (id: string) => void;
  onViewLogs?: (id: string) => void;
  refreshing?: boolean;
  className?: string;
}

const statusConfig: Record<
  APIStatus,
  { label: string; color: string; bgColor: string; icon: typeof Wifi }
> = {
  online: {
    label: 'Online',
    color: 'text-green-600',
    bgColor: 'bg-green-100',
    icon: Wifi,
  },
  offline: {
    label: 'Offline',
    color: 'text-red-600',
    bgColor: 'bg-red-100',
    icon: WifiOff,
  },
  degraded: {
    label: 'Degradado',
    color: 'text-yellow-600',
    bgColor: 'bg-yellow-100',
    icon: AlertTriangle,
  },
  maintenance: {
    label: 'Manutencao',
    color: 'text-blue-600',
    bgColor: 'bg-blue-100',
    icon: Clock,
  },
  unknown: {
    label: 'Desconhecido',
    color: 'text-gray-600',
    bgColor: 'bg-gray-100',
    icon: AlertTriangle,
  },
};


function formatDateTime(date: Date): string {
  return date.toLocaleDateString('pt-BR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}

function formatRelativeTime(date: Date): string {
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / (1000 * 60));
  const diffHours = Math.floor(diffMs / (1000 * 60 * 60));

  if (diffMins < 1) return 'Agora';
  if (diffMins < 60) return `${diffMins}min atras`;
  if (diffHours < 24) return `${diffHours}h atras`;
  return formatDateTime(date);
}

export function APIStatusCard({
  id,
  name,
  description,
  provider,
  status,
  lastCheck,
  lastSync,
  uptime,
  responseTime,
  endpoint,
  onRefresh,
  onConfigure,
  onViewLogs,
  refreshing = false,
  className,
}: APIStatusCardProps) {
  const [pulseActive, setPulseActive] = useState(status === 'online');
  const config = statusConfig[status];
  const StatusIcon = config.icon;

  useEffect(() => {
    setPulseActive(status === 'online');
  }, [status]);

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className={clsx(
        'bg-white rounded-xl border shadow-sm overflow-hidden',
        'hover:shadow-md transition-shadow duration-200',
        status === 'offline' && 'border-red-200',
        status === 'degraded' && 'border-yellow-200',
        status === 'online' && 'border-green-200',
        status !== 'offline' && status !== 'degraded' && status !== 'online' && 'border-gray-200',
        className
      )}
    >
      {/* Header */}
      <div className="p-4 border-b border-gray-100">
        <div className="flex items-start justify-between gap-4">
          <div className="flex items-center gap-3">
            {/* Provider Logo/Icon */}
            <div className="w-12 h-12 rounded-lg bg-[#0A2540] flex items-center justify-center flex-shrink-0">
              <span className="text-white font-bold text-lg">
                {provider.slice(0, 2).toUpperCase()}
              </span>
            </div>

            <div>
              <h3 className="text-lg font-semibold text-[#0A2540]">{name}</h3>
              <p className="text-sm text-gray-500">{provider}</p>
            </div>
          </div>

          {/* Status Badge */}
          <div className="flex items-center gap-2">
            <div
              className={clsx(
                'relative flex items-center gap-1.5 px-3 py-1.5 rounded-full',
                config.bgColor
              )}
            >
              {pulseActive && (
                <motion.div
                  animate={{ scale: [1, 1.5, 1], opacity: [0.5, 0, 0.5] }}
                  transition={{ duration: 2, repeat: Infinity }}
                  className="absolute inset-0 rounded-full bg-green-400"
                />
              )}
              <StatusIcon className={clsx('w-4 h-4 relative z-10', config.color)} />
              <span className={clsx('text-sm font-medium relative z-10', config.color)}>
                {config.label}
              </span>
            </div>
          </div>
        </div>

        {description && (
          <p className="text-sm text-gray-600 mt-3">{description}</p>
        )}
      </div>

      {/* Metrics */}
      <div className="grid grid-cols-3 divide-x divide-gray-100 bg-gray-50">
        {/* Response Time */}
        <div className="p-3 text-center">
          <div className="flex items-center justify-center gap-1 mb-1">
            <Activity className="w-4 h-4 text-gray-400" />
          </div>
          <p
            className={clsx(
              'text-lg font-bold',
              responseTime && responseTime < 200
                ? 'text-green-600'
                : responseTime && responseTime < 500
                ? 'text-yellow-600'
                : responseTime
                ? 'text-red-600'
                : 'text-gray-400'
            )}
          >
            {responseTime ? `${responseTime}ms` : '-'}
          </p>
          <p className="text-xs text-gray-500">Latencia</p>
        </div>

        {/* Uptime */}
        <div className="p-3 text-center">
          <div className="flex items-center justify-center gap-1 mb-1">
            <CheckCircle className="w-4 h-4 text-gray-400" />
          </div>
          <p
            className={clsx(
              'text-lg font-bold',
              uptime && uptime >= 99
                ? 'text-green-600'
                : uptime && uptime >= 95
                ? 'text-yellow-600'
                : uptime
                ? 'text-red-600'
                : 'text-gray-400'
            )}
          >
            {uptime !== undefined ? `${uptime.toFixed(1)}%` : '-'}
          </p>
          <p className="text-xs text-gray-500">Uptime</p>
        </div>

        {/* Last Sync */}
        <div className="p-3 text-center">
          <div className="flex items-center justify-center gap-1 mb-1">
            <RefreshCw className="w-4 h-4 text-gray-400" />
          </div>
          <p className="text-lg font-bold text-[#0A2540]">
            {lastSync ? formatRelativeTime(lastSync).split(' ')[0] : '-'}
          </p>
          <p className="text-xs text-gray-500">Ult. Sync</p>
        </div>
      </div>

      {/* Details */}
      <div className="p-4 space-y-3">
        {/* Last Check */}
        {lastCheck && (
          <div className="flex items-center justify-between text-sm">
            <span className="text-gray-500">Ultima verificacao</span>
            <span className="text-gray-700" title={formatDateTime(lastCheck)}>
              {formatRelativeTime(lastCheck)}
            </span>
          </div>
        )}

        {/* Endpoint */}
        {endpoint && (
          <div className="flex items-center justify-between text-sm">
            <span className="text-gray-500">Endpoint</span>
            <a
              href={endpoint}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-1 text-[#FF6B35] hover:underline truncate max-w-[200px]"
            >
              <span className="truncate">{endpoint}</span>
              <ExternalLink className="w-3 h-3 flex-shrink-0" />
            </a>
          </div>
        )}
      </div>

      {/* Actions */}
      <div className="px-4 py-3 bg-gray-50 border-t border-gray-100">
        <div className="flex items-center justify-between gap-2">
          <div className="flex items-center gap-2">
            {onRefresh && (
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => onRefresh(id)}
                disabled={refreshing}
                className={clsx(
                  'px-3 py-1.5 text-sm font-medium rounded-lg transition-colors',
                  'flex items-center gap-1.5',
                  'bg-[#FF6B35] text-white hover:bg-[#e55a2b]',
                  refreshing && 'opacity-50 cursor-not-allowed'
                )}
              >
                <RefreshCw
                  className={clsx('w-4 h-4', refreshing && 'animate-spin')}
                />
                {refreshing ? 'Verificando...' : 'Verificar'}
              </motion.button>
            )}
          </div>

          <div className="flex items-center gap-2">
            {onViewLogs && (
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => onViewLogs(id)}
                className="px-3 py-1.5 text-sm font-medium text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
              >
                Ver Logs
              </motion.button>
            )}
            {onConfigure && (
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => onConfigure(id)}
                className="px-3 py-1.5 text-sm font-medium text-[#0A2540] hover:bg-gray-100 rounded-lg transition-colors"
              >
                Configurar
              </motion.button>
            )}
          </div>
        </div>
      </div>
    </motion.div>
  );
}
