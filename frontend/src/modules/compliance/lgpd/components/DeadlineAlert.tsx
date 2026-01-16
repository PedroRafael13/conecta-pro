'use client';

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { clsx } from 'clsx';
import { AlertTriangle, Clock, X, Bell, ChevronRight } from 'lucide-react';

type AlertSeverity = 'low' | 'medium' | 'high' | 'critical';

interface DeadlineAlertProps {
  id: string;
  title: string;
  description?: string;
  deadline: Date;
  maxDays?: number; // LGPD default is 15 days
  requestType?: string;
  onAction?: (id: string) => void;
  onDismiss?: (id: string) => void;
  dismissible?: boolean;
  showCountdown?: boolean;
  className?: string;
}

function calculateTimeRemaining(deadline: Date): {
  days: number;
  hours: number;
  minutes: number;
  seconds: number;
  total: number;
  isExpired: boolean;
} {
  const now = new Date();
  const total = deadline.getTime() - now.getTime();
  const isExpired = total <= 0;

  if (isExpired) {
    return { days: 0, hours: 0, minutes: 0, seconds: 0, total: 0, isExpired: true };
  }

  const days = Math.floor(total / (1000 * 60 * 60 * 24));
  const hours = Math.floor((total % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
  const minutes = Math.floor((total % (1000 * 60 * 60)) / (1000 * 60));
  const seconds = Math.floor((total % (1000 * 60)) / 1000);

  return { days, hours, minutes, seconds, total, isExpired };
}

function getSeverity(daysRemaining: number, maxDays: number): AlertSeverity {
  const percentage = daysRemaining / maxDays;
  if (daysRemaining <= 0) return 'critical';
  if (percentage <= 0.2) return 'critical'; // 20% or less
  if (percentage <= 0.4) return 'high'; // 40% or less
  if (percentage <= 0.6) return 'medium'; // 60% or less
  return 'low';
}

const severityConfig: Record<
  AlertSeverity,
  { bg: string; border: string; text: string; icon: string }
> = {
  low: {
    bg: 'bg-blue-50',
    border: 'border-blue-200',
    text: 'text-blue-800',
    icon: 'text-blue-500',
  },
  medium: {
    bg: 'bg-yellow-50',
    border: 'border-yellow-200',
    text: 'text-yellow-800',
    icon: 'text-yellow-500',
  },
  high: {
    bg: 'bg-orange-50',
    border: 'border-orange-200',
    text: 'text-orange-800',
    icon: 'text-orange-500',
  },
  critical: {
    bg: 'bg-red-50',
    border: 'border-red-200',
    text: 'text-red-800',
    icon: 'text-red-500',
  },
};

export function DeadlineAlert({
  id,
  title,
  description,
  deadline,
  maxDays = 15,
  requestType,
  onAction,
  onDismiss,
  dismissible = true,
  showCountdown = true,
  className,
}: DeadlineAlertProps) {
  const [timeRemaining, setTimeRemaining] = useState(calculateTimeRemaining(deadline));
  const [isDismissed, setIsDismissed] = useState(false);

  useEffect(() => {
    if (!showCountdown) return;

    const interval = setInterval(() => {
      setTimeRemaining(calculateTimeRemaining(deadline));
    }, 1000);

    return () => clearInterval(interval);
  }, [deadline, showCountdown]);

  const severity = getSeverity(timeRemaining.days, maxDays);
  const config = severityConfig[severity];

  const handleDismiss = () => {
    setIsDismissed(true);
    onDismiss?.(id);
  };

  return (
    <AnimatePresence>
      {!isDismissed && (
        <motion.div
          initial={{ opacity: 0, y: -10, scale: 0.95 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          exit={{ opacity: 0, y: -10, scale: 0.95 }}
          transition={{ duration: 0.2 }}
          className={clsx(
            'relative rounded-xl border p-4',
            config.bg,
            config.border,
            className
          )}
        >
          {/* Pulse animation for critical */}
          {severity === 'critical' && (
            <motion.div
              animate={{ opacity: [0.5, 0, 0.5] }}
              transition={{ duration: 2, repeat: Infinity }}
              className="absolute inset-0 rounded-xl bg-red-500/10"
            />
          )}

          <div className="relative flex items-start gap-4">
            {/* Icon */}
            <div
              className={clsx(
                'flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center',
                severity === 'critical' ? 'bg-red-100' : 'bg-white/50'
              )}
            >
              {severity === 'critical' ? (
                <motion.div
                  animate={{ rotate: [0, -10, 10, -10, 0] }}
                  transition={{ duration: 0.5, repeat: Infinity, repeatDelay: 2 }}
                >
                  <AlertTriangle className={clsx('w-5 h-5', config.icon)} />
                </motion.div>
              ) : (
                <Clock className={clsx('w-5 h-5', config.icon)} />
              )}
            </div>

            {/* Content */}
            <div className="flex-1 min-w-0">
              <div className="flex items-start justify-between gap-2">
                <div>
                  <div className="flex items-center gap-2">
                    <h4 className={clsx('font-semibold', config.text)}>{title}</h4>
                    {requestType && (
                      <span className="px-2 py-0.5 text-xs font-medium bg-white/60 rounded-full">
                        {requestType}
                      </span>
                    )}
                  </div>
                  {description && (
                    <p className={clsx('text-sm mt-1 opacity-80', config.text)}>
                      {description}
                    </p>
                  )}
                </div>

                {dismissible && (
                  <button
                    onClick={handleDismiss}
                    className={clsx(
                      'p-1 rounded-lg transition-colors',
                      'hover:bg-white/50',
                      config.text
                    )}
                  >
                    <X className="w-4 h-4" />
                  </button>
                )}
              </div>

              {/* Countdown */}
              {showCountdown && (
                <div className="mt-3">
                  {timeRemaining.isExpired ? (
                    <div className="flex items-center gap-2">
                      <Bell className="w-4 h-4 text-red-600" />
                      <span className="text-sm font-bold text-red-600">
                        PRAZO EXPIRADO
                      </span>
                    </div>
                  ) : (
                    <div className="flex items-center gap-3">
                      <div className="flex items-center gap-2">
                        <div className="text-center">
                          <div
                            className={clsx(
                              'text-2xl font-bold leading-none',
                              config.text
                            )}
                          >
                            {String(timeRemaining.days).padStart(2, '0')}
                          </div>
                          <div className="text-xs opacity-60 mt-0.5">dias</div>
                        </div>
                        <span className={clsx('text-xl font-bold opacity-40', config.text)}>:</span>
                        <div className="text-center">
                          <div
                            className={clsx(
                              'text-2xl font-bold leading-none',
                              config.text
                            )}
                          >
                            {String(timeRemaining.hours).padStart(2, '0')}
                          </div>
                          <div className="text-xs opacity-60 mt-0.5">horas</div>
                        </div>
                        <span className={clsx('text-xl font-bold opacity-40', config.text)}>:</span>
                        <div className="text-center">
                          <div
                            className={clsx(
                              'text-2xl font-bold leading-none',
                              config.text
                            )}
                          >
                            {String(timeRemaining.minutes).padStart(2, '0')}
                          </div>
                          <div className="text-xs opacity-60 mt-0.5">min</div>
                        </div>
                        <span className={clsx('text-xl font-bold opacity-40', config.text)}>:</span>
                        <div className="text-center">
                          <div
                            className={clsx(
                              'text-2xl font-bold leading-none tabular-nums',
                              config.text
                            )}
                          >
                            {String(timeRemaining.seconds).padStart(2, '0')}
                          </div>
                          <div className="text-xs opacity-60 mt-0.5">seg</div>
                        </div>
                      </div>

                      {/* Progress bar */}
                      <div className="flex-1 ml-4">
                        <div className="h-2 bg-white/40 rounded-full overflow-hidden">
                          <motion.div
                            initial={{ width: '100%' }}
                            animate={{
                              width: `${Math.max(0, (timeRemaining.days / maxDays) * 100)}%`,
                            }}
                            className={clsx(
                              'h-full rounded-full',
                              severity === 'critical'
                                ? 'bg-red-500'
                                : severity === 'high'
                                ? 'bg-orange-500'
                                : severity === 'medium'
                                ? 'bg-yellow-500'
                                : 'bg-blue-500'
                            )}
                          />
                        </div>
                        <p className={clsx('text-xs mt-1 opacity-60', config.text)}>
                          {timeRemaining.days} de {maxDays} dias restantes
                        </p>
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* Action button */}
              {onAction && (
                <motion.button
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={() => onAction(id)}
                  className={clsx(
                    'mt-3 inline-flex items-center gap-1 px-3 py-1.5 rounded-lg',
                    'text-sm font-medium transition-colors',
                    severity === 'critical'
                      ? 'bg-red-600 text-white hover:bg-red-700'
                      : 'bg-white/60 hover:bg-white/80',
                    severity !== 'critical' && config.text
                  )}
                >
                  Atender Solicitacao
                  <ChevronRight className="w-4 h-4" />
                </motion.button>
              )}
            </div>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
