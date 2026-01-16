'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { clsx } from 'clsx';
import {
  CheckCircle,
  XCircle,
  AlertTriangle,
  Info,
  ChevronDown,
  ChevronUp,
  Download,
  Search,
  RefreshCw,
} from 'lucide-react';

type LogLevel = 'info' | 'success' | 'warning' | 'error';
type LogSource = 'api' | 'system' | 'user' | 'scheduler';

interface LogEntry {
  id: string;
  timestamp: Date;
  level: LogLevel;
  source: LogSource;
  message: string;
  details?: string;
  metadata?: Record<string, unknown>;
  requestId?: string;
  duration?: number; // ms
}

interface IntegrationLogProps {
  logs: LogEntry[];
  title?: string;
  maxHeight?: string;
  showFilters?: boolean;
  showExport?: boolean;
  onRefresh?: () => void;
  onExport?: () => void;
  loading?: boolean;
  className?: string;
}

const levelConfig: Record<
  LogLevel,
  { icon: typeof Info; color: string; bgColor: string; label: string }
> = {
  info: {
    icon: Info,
    color: 'text-blue-600',
    bgColor: 'bg-blue-100',
    label: 'Info',
  },
  success: {
    icon: CheckCircle,
    color: 'text-green-600',
    bgColor: 'bg-green-100',
    label: 'Sucesso',
  },
  warning: {
    icon: AlertTriangle,
    color: 'text-yellow-600',
    bgColor: 'bg-yellow-100',
    label: 'Alerta',
  },
  error: {
    icon: XCircle,
    color: 'text-red-600',
    bgColor: 'bg-red-100',
    label: 'Erro',
  },
};

const sourceLabels: Record<LogSource, string> = {
  api: 'API',
  system: 'Sistema',
  user: 'Usuario',
  scheduler: 'Agendador',
};

function formatDateTime(date: Date): string {
  return date.toLocaleDateString('pt-BR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  });
}

function formatTime(date: Date): string {
  return date.toLocaleTimeString('pt-BR', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  });
}

export function IntegrationLog({
  logs,
  title = 'Logs de Integracao',
  maxHeight = '400px',
  showFilters = true,
  showExport = true,
  onRefresh,
  onExport,
  loading = false,
  className,
}: IntegrationLogProps) {
  const [expandedLogs, setExpandedLogs] = useState<Set<string>>(new Set());
  const [filterLevel, setFilterLevel] = useState<LogLevel | 'all'>('all');
  const [filterSource, setFilterSource] = useState<LogSource | 'all'>('all');
  const [searchQuery, setSearchQuery] = useState('');

  const toggleExpanded = (id: string) => {
    setExpandedLogs((prev) => {
      const next = new Set(prev);
      if (next.has(id)) {
        next.delete(id);
      } else {
        next.add(id);
      }
      return next;
    });
  };

  const filteredLogs = logs.filter((log) => {
    if (filterLevel !== 'all' && log.level !== filterLevel) return false;
    if (filterSource !== 'all' && log.source !== filterSource) return false;
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      return (
        log.message.toLowerCase().includes(query) ||
        log.details?.toLowerCase().includes(query) ||
        log.requestId?.toLowerCase().includes(query)
      );
    }
    return true;
  });

  const logCounts = {
    info: logs.filter((l) => l.level === 'info').length,
    success: logs.filter((l) => l.level === 'success').length,
    warning: logs.filter((l) => l.level === 'warning').length,
    error: logs.filter((l) => l.level === 'error').length,
  };

  return (
    <div
      className={clsx(
        'bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden',
        className
      )}
    >
      {/* Header */}
      <div className="p-4 border-b border-gray-100">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-[#0A2540]">{title}</h3>
          <div className="flex items-center gap-2">
            {onRefresh && (
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={onRefresh}
                disabled={loading}
                className={clsx(
                  'p-2 rounded-lg transition-colors',
                  'text-gray-500 hover:text-[#FF6B35] hover:bg-orange-50',
                  loading && 'opacity-50 cursor-not-allowed'
                )}
              >
                <RefreshCw className={clsx('w-5 h-5', loading && 'animate-spin')} />
              </motion.button>
            )}
            {showExport && onExport && (
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={onExport}
                className="p-2 rounded-lg text-gray-500 hover:text-[#0A2540] hover:bg-gray-100 transition-colors"
              >
                <Download className="w-5 h-5" />
              </motion.button>
            )}
          </div>
        </div>

        {/* Stats */}
        <div className="flex items-center gap-4 mb-4">
          {Object.entries(logCounts).map(([level, count]) => {
            const config = levelConfig[level as LogLevel];
            return (
              <div
                key={level}
                className={clsx(
                  'flex items-center gap-1.5 px-2 py-1 rounded-full cursor-pointer transition-colors',
                  filterLevel === level ? config.bgColor : 'hover:bg-gray-100'
                )}
                onClick={() => setFilterLevel(filterLevel === level ? 'all' : (level as LogLevel))}
              >
                <config.icon className={clsx('w-4 h-4', config.color)} />
                <span className={clsx('text-sm font-medium', config.color)}>
                  {count}
                </span>
              </div>
            );
          })}
        </div>

        {/* Filters */}
        {showFilters && (
          <div className="flex items-center gap-3">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input
                type="text"
                placeholder="Buscar nos logs..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#FF6B35] focus:border-transparent"
              />
            </div>

            <select
              value={filterSource}
              onChange={(e) => setFilterSource(e.target.value as LogSource | 'all')}
              className="px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#FF6B35] focus:border-transparent"
            >
              <option value="all">Todas as fontes</option>
              {Object.entries(sourceLabels).map(([value, label]) => (
                <option key={value} value={value}>
                  {label}
                </option>
              ))}
            </select>
          </div>
        )}
      </div>

      {/* Log List */}
      <div
        className="overflow-y-auto"
        style={{ maxHeight }}
      >
        {loading && logs.length === 0 ? (
          <div className="flex items-center justify-center py-12">
            <RefreshCw className="w-6 h-6 text-gray-400 animate-spin" />
          </div>
        ) : filteredLogs.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-12 text-gray-500">
            <Info className="w-8 h-8 mb-2" />
            <p>Nenhum log encontrado</p>
          </div>
        ) : (
          <div className="divide-y divide-gray-100">
            {filteredLogs.map((log) => {
              const config = levelConfig[log.level];
              const Icon = config.icon;
              const isExpanded = expandedLogs.has(log.id);
              const hasDetails = log.details || log.metadata;

              return (
                <div key={log.id} className="hover:bg-gray-50 transition-colors">
                  <div
                    className={clsx(
                      'flex items-start gap-3 p-4 cursor-pointer',
                      hasDetails && 'cursor-pointer'
                    )}
                    onClick={() => hasDetails && toggleExpanded(log.id)}
                  >
                    {/* Icon */}
                    <div
                      className={clsx(
                        'flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center',
                        config.bgColor
                      )}
                    >
                      <Icon className={clsx('w-4 h-4', config.color)} />
                    </div>

                    {/* Content */}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-start justify-between gap-2">
                        <div className="flex-1 min-w-0">
                          <p className="text-sm text-gray-900">{log.message}</p>
                          <div className="flex items-center gap-2 mt-1">
                            <span className="text-xs text-gray-500">
                              {formatTime(log.timestamp)}
                            </span>
                            <span className="text-xs px-1.5 py-0.5 bg-gray-100 rounded text-gray-600">
                              {sourceLabels[log.source]}
                            </span>
                            {log.requestId && (
                              <span className="text-xs font-mono text-gray-400">
                                {log.requestId.slice(0, 8)}
                              </span>
                            )}
                            {log.duration && (
                              <span className="text-xs text-gray-500">
                                {log.duration}ms
                              </span>
                            )}
                          </div>
                        </div>

                        {hasDetails && (
                          <button className="flex-shrink-0 p-1 text-gray-400 hover:text-gray-600">
                            {isExpanded ? (
                              <ChevronUp className="w-4 h-4" />
                            ) : (
                              <ChevronDown className="w-4 h-4" />
                            )}
                          </button>
                        )}
                      </div>
                    </div>
                  </div>

                  {/* Expanded Details */}
                  <AnimatePresence>
                    {isExpanded && hasDetails && (
                      <motion.div
                        initial={{ height: 0, opacity: 0 }}
                        animate={{ height: 'auto', opacity: 1 }}
                        exit={{ height: 0, opacity: 0 }}
                        transition={{ duration: 0.2 }}
                        className="overflow-hidden"
                      >
                        <div className="px-4 pb-4 ml-11">
                          <div className="p-3 bg-gray-50 rounded-lg text-sm">
                            {log.details && (
                              <p className="text-gray-700 whitespace-pre-wrap mb-2">
                                {log.details}
                              </p>
                            )}
                            {log.metadata && (
                              <pre className="text-xs text-gray-600 overflow-x-auto">
                                {JSON.stringify(log.metadata, null, 2)}
                              </pre>
                            )}
                          </div>
                        </div>
                      </motion.div>
                    )}
                  </AnimatePresence>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="px-4 py-3 bg-gray-50 border-t border-gray-100">
        <div className="flex items-center justify-between text-xs text-gray-500">
          <span>
            {filteredLogs.length} de {logs.length} registros
          </span>
          {logs.length > 0 && (
            <span>
              Ultimo: {formatDateTime(logs[0].timestamp)}
            </span>
          )}
        </div>
      </div>
    </div>
  );
}
