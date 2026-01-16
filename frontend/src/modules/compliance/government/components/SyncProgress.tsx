'use client';

import { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { clsx } from 'clsx';
import {
  RefreshCw,
  CheckCircle,
  XCircle,
  AlertTriangle,
  Pause,
  Play,
  X,
} from 'lucide-react';

type SyncStatus = 'idle' | 'syncing' | 'paused' | 'completed' | 'error';

interface SyncStep {
  id: string;
  name: string;
  status: 'pending' | 'in_progress' | 'completed' | 'error' | 'skipped';
  progress?: number;
  message?: string;
}

interface SyncProgressProps {
  status: SyncStatus;
  progress: number; // 0-100
  currentStep?: string;
  steps?: SyncStep[];
  startTime?: Date;
  estimatedEndTime?: Date;
  processedItems?: number;
  totalItems?: number;
  errorMessage?: string;
  onPause?: () => void;
  onResume?: () => void;
  onCancel?: () => void;
  onRetry?: () => void;
  showDetails?: boolean;
  className?: string;
}

const statusConfig: Record<
  SyncStatus,
  { label: string; color: string; icon: typeof RefreshCw }
> = {
  idle: { label: 'Aguardando', color: 'text-gray-500', icon: RefreshCw },
  syncing: { label: 'Sincronizando', color: 'text-blue-500', icon: RefreshCw },
  paused: { label: 'Pausado', color: 'text-yellow-500', icon: Pause },
  completed: { label: 'Concluido', color: 'text-green-500', icon: CheckCircle },
  error: { label: 'Erro', color: 'text-red-500', icon: XCircle },
};

function formatDuration(ms: number): string {
  const seconds = Math.floor(ms / 1000);
  const minutes = Math.floor(seconds / 60);
  const hours = Math.floor(minutes / 60);

  if (hours > 0) {
    return `${hours}h ${minutes % 60}m`;
  }
  if (minutes > 0) {
    return `${minutes}m ${seconds % 60}s`;
  }
  return `${seconds}s`;
}

function formatTime(date: Date): string {
  return date.toLocaleTimeString('pt-BR', {
    hour: '2-digit',
    minute: '2-digit',
  });
}

export function SyncProgress({
  status,
  progress,
  currentStep,
  steps,
  startTime,
  estimatedEndTime,
  processedItems,
  totalItems,
  errorMessage,
  onPause,
  onResume,
  onCancel,
  onRetry,
  showDetails = true,
  className,
}: SyncProgressProps) {
  const [elapsedTime, setElapsedTime] = useState(0);
  const config = statusConfig[status];
  const StatusIcon = config.icon;

  useEffect(() => {
    if (status !== 'syncing' || !startTime) return;

    const interval = setInterval(() => {
      setElapsedTime(Date.now() - startTime.getTime());
    }, 1000);

    return () => clearInterval(interval);
  }, [status, startTime]);

  const remainingTime = estimatedEndTime
    ? Math.max(0, estimatedEndTime.getTime() - new Date().getTime())
    : null;

  return (
    <div
      className={clsx(
        'bg-white rounded-xl border shadow-sm overflow-hidden',
        status === 'error' && 'border-red-200',
        status === 'completed' && 'border-green-200',
        status === 'syncing' && 'border-blue-200',
        status !== 'error' && status !== 'completed' && status !== 'syncing' && 'border-gray-200',
        className
      )}
    >
      {/* Header */}
      <div className="p-4 border-b border-gray-100">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div
              className={clsx(
                'w-10 h-10 rounded-full flex items-center justify-center',
                status === 'syncing' && 'bg-blue-100',
                status === 'paused' && 'bg-yellow-100',
                status === 'completed' && 'bg-green-100',
                status === 'error' && 'bg-red-100',
                status === 'idle' && 'bg-gray-100'
              )}
            >
              {status === 'syncing' ? (
                <motion.div
                  animate={{ rotate: 360 }}
                  transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
                >
                  <StatusIcon className={clsx('w-5 h-5', config.color)} />
                </motion.div>
              ) : (
                <StatusIcon className={clsx('w-5 h-5', config.color)} />
              )}
            </div>

            <div>
              <h3 className="font-semibold text-[#0A2540]">{config.label}</h3>
              {currentStep && status === 'syncing' && (
                <p className="text-sm text-gray-500">{currentStep}</p>
              )}
            </div>
          </div>

          {/* Actions */}
          <div className="flex items-center gap-2">
            {status === 'syncing' && onPause && (
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={onPause}
                className="p-2 text-gray-500 hover:text-yellow-600 hover:bg-yellow-50 rounded-lg transition-colors"
                title="Pausar"
              >
                <Pause className="w-5 h-5" />
              </motion.button>
            )}
            {status === 'paused' && onResume && (
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={onResume}
                className="p-2 text-gray-500 hover:text-green-600 hover:bg-green-50 rounded-lg transition-colors"
                title="Retomar"
              >
                <Play className="w-5 h-5" />
              </motion.button>
            )}
            {(status === 'syncing' || status === 'paused') && onCancel && (
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={onCancel}
                className="p-2 text-gray-500 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                title="Cancelar"
              >
                <X className="w-5 h-5" />
              </motion.button>
            )}
            {status === 'error' && onRetry && (
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={onRetry}
                className="px-3 py-1.5 text-sm font-medium bg-red-600 text-white hover:bg-red-700 rounded-lg transition-colors"
              >
                Tentar novamente
              </motion.button>
            )}
          </div>
        </div>
      </div>

      {/* Progress Bar */}
      <div className="px-4 py-3">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm text-gray-600">Progresso</span>
          <span className="text-sm font-semibold text-[#0A2540]">{Math.round(progress)}%</span>
        </div>
        <div className="h-3 bg-gray-100 rounded-full overflow-hidden">
          <motion.div
            initial={{ width: 0 }}
            animate={{ width: `${progress}%` }}
            transition={{ duration: 0.5, ease: 'easeOut' }}
            className={clsx(
              'h-full rounded-full',
              status === 'error' && 'bg-red-500',
              status === 'completed' && 'bg-green-500',
              status === 'paused' && 'bg-yellow-500',
              status !== 'error' && status !== 'completed' && status !== 'paused' && 'bg-[#FF6B35]'
            )}
          />
        </div>

        {/* Items counter */}
        {processedItems !== undefined && totalItems !== undefined && (
          <div className="flex items-center justify-between mt-2 text-xs text-gray-500">
            <span>{processedItems.toLocaleString('pt-BR')} de {totalItems.toLocaleString('pt-BR')} itens</span>
            {remainingTime !== null && status === 'syncing' && (
              <span>~{formatDuration(remainingTime)} restantes</span>
            )}
          </div>
        )}
      </div>

      {/* Error Message */}
      <AnimatePresence>
        {status === 'error' && errorMessage && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            className="px-4 pb-4"
          >
            <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
              <div className="flex items-start gap-2">
                <AlertTriangle className="w-4 h-4 text-red-500 mt-0.5 flex-shrink-0" />
                <p className="text-sm text-red-700">{errorMessage}</p>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Steps Detail */}
      {showDetails && steps && steps.length > 0 && (
        <div className="px-4 pb-4">
          <div className="border-t border-gray-100 pt-4">
            <h4 className="text-sm font-medium text-gray-700 mb-3">Etapas</h4>
            <div className="space-y-2">
              {steps.map((step) => (
                <div
                  key={step.id}
                  className={clsx(
                    'flex items-center gap-3 p-2 rounded-lg',
                    step.status === 'in_progress' && 'bg-blue-50',
                    step.status === 'error' && 'bg-red-50'
                  )}
                >
                  {/* Step Icon */}
                  <div className="flex-shrink-0">
                    {step.status === 'completed' && (
                      <CheckCircle className="w-5 h-5 text-green-500" />
                    )}
                    {step.status === 'in_progress' && (
                      <motion.div
                        animate={{ rotate: 360 }}
                        transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
                      >
                        <RefreshCw className="w-5 h-5 text-blue-500" />
                      </motion.div>
                    )}
                    {step.status === 'error' && (
                      <XCircle className="w-5 h-5 text-red-500" />
                    )}
                    {step.status === 'pending' && (
                      <div className="w-5 h-5 rounded-full border-2 border-gray-300" />
                    )}
                    {step.status === 'skipped' && (
                      <div className="w-5 h-5 rounded-full bg-gray-200 flex items-center justify-center">
                        <span className="text-xs text-gray-500">-</span>
                      </div>
                    )}
                  </div>

                  {/* Step Content */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between">
                      <span
                        className={clsx(
                          'text-sm font-medium',
                          step.status === 'completed' && 'text-green-700',
                          step.status === 'in_progress' && 'text-blue-700',
                          step.status === 'error' && 'text-red-700',
                          step.status === 'pending' && 'text-gray-500',
                          step.status === 'skipped' && 'text-gray-400'
                        )}
                      >
                        {step.name}
                      </span>
                      {step.progress !== undefined && step.status === 'in_progress' && (
                        <span className="text-xs text-blue-600">{step.progress}%</span>
                      )}
                    </div>
                    {step.message && (
                      <p className="text-xs text-gray-500 mt-0.5 truncate">{step.message}</p>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Footer - Timing Info */}
      {(startTime || estimatedEndTime) && (
        <div className="px-4 py-3 bg-gray-50 border-t border-gray-100">
          <div className="flex items-center justify-between text-xs text-gray-500">
            {startTime && (
              <span>Iniciado: {formatTime(startTime)}</span>
            )}
            {status === 'syncing' && elapsedTime > 0 && (
              <span>Tempo decorrido: {formatDuration(elapsedTime)}</span>
            )}
            {estimatedEndTime && status === 'syncing' && (
              <span>Previsao: {formatTime(estimatedEndTime)}</span>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
