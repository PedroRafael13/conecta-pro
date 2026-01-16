'use client';

import { motion } from 'framer-motion';
import { clsx } from 'clsx';
import {
  CheckCircle,
  XCircle,
  User,
  FileText,
  Send,
  Eye,
  Shield,
  AlertTriangle,
  Play,
} from 'lucide-react';
import { LucideIcon } from 'lucide-react';

type TimelineEventType =
  | 'created'
  | 'assigned'
  | 'in_review'
  | 'data_collected'
  | 'verification'
  | 'approved'
  | 'rejected'
  | 'completed'
  | 'sent'
  | 'expired';

interface TimelineEvent {
  id: string;
  type: TimelineEventType;
  title: string;
  description?: string;
  date: Date;
  user?: string;
  metadata?: Record<string, string>;
}

interface RequestTimelineProps {
  events: TimelineEvent[];
  currentStep?: TimelineEventType;
  className?: string;
}

const eventConfig: Record<
  TimelineEventType,
  { icon: LucideIcon; color: string; bgColor: string }
> = {
  created: { icon: FileText, color: 'text-blue-600', bgColor: 'bg-blue-100' },
  assigned: { icon: User, color: 'text-purple-600', bgColor: 'bg-purple-100' },
  in_review: { icon: Eye, color: 'text-yellow-600', bgColor: 'bg-yellow-100' },
  data_collected: { icon: FileText, color: 'text-indigo-600', bgColor: 'bg-indigo-100' },
  verification: { icon: Shield, color: 'text-cyan-600', bgColor: 'bg-cyan-100' },
  approved: { icon: CheckCircle, color: 'text-green-600', bgColor: 'bg-green-100' },
  rejected: { icon: XCircle, color: 'text-red-600', bgColor: 'bg-red-100' },
  completed: { icon: CheckCircle, color: 'text-green-600', bgColor: 'bg-green-100' },
  sent: { icon: Send, color: 'text-[#FF6B35]', bgColor: 'bg-orange-100' },
  expired: { icon: AlertTriangle, color: 'text-red-600', bgColor: 'bg-red-100' },
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
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

  if (diffMins < 1) return 'Agora';
  if (diffMins < 60) return `${diffMins} min atras`;
  if (diffHours < 24) return `${diffHours}h atras`;
  if (diffDays < 7) return `${diffDays}d atras`;
  return formatDateTime(date);
}

export function RequestTimeline({
  events,
  currentStep,
  className,
}: RequestTimelineProps) {
  const sortedEvents = [...events].sort((a, b) => b.date.getTime() - a.date.getTime());

  return (
    <div className={clsx('relative', className)}>
      {/* Timeline line */}
      <div className="absolute left-5 top-0 bottom-0 w-0.5 bg-gray-200" />

      <div className="space-y-6">
        {sortedEvents.map((event, index) => {
          const config = eventConfig[event.type];
          const Icon = config.icon;
          const isFirst = index === 0;
          const isCurrent = event.type === currentStep;

          return (
            <motion.div
              key={event.id}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.3, delay: index * 0.1 }}
              className="relative flex gap-4"
            >
              {/* Icon */}
              <div className="relative z-10 flex-shrink-0">
                <div
                  className={clsx(
                    'w-10 h-10 rounded-full flex items-center justify-center',
                    config.bgColor,
                    isCurrent && 'ring-2 ring-offset-2 ring-[#FF6B35]'
                  )}
                >
                  {isCurrent ? (
                    <motion.div
                      animate={{ rotate: 360 }}
                      transition={{ duration: 2, repeat: Infinity, ease: 'linear' }}
                    >
                      <Play className={clsx('w-5 h-5', config.color)} />
                    </motion.div>
                  ) : (
                    <Icon className={clsx('w-5 h-5', config.color)} />
                  )}
                </div>
              </div>

              {/* Content */}
              <div
                className={clsx(
                  'flex-1 pb-6',
                  isFirst && 'pb-0'
                )}
              >
                <div
                  className={clsx(
                    'bg-white rounded-lg border p-4',
                    isCurrent ? 'border-[#FF6B35] shadow-sm' : 'border-gray-200'
                  )}
                >
                  <div className="flex items-start justify-between gap-2">
                    <div>
                      <h4 className="font-medium text-[#0A2540]">{event.title}</h4>
                      {event.description && (
                        <p className="text-sm text-gray-600 mt-1">{event.description}</p>
                      )}
                    </div>
                    <div className="flex flex-col items-end gap-1">
                      <span className="text-xs text-gray-500" title={formatDateTime(event.date)}>
                        {formatRelativeTime(event.date)}
                      </span>
                      {isCurrent && (
                        <span className="px-2 py-0.5 text-xs font-medium bg-[#FF6B35] text-white rounded-full">
                          Atual
                        </span>
                      )}
                    </div>
                  </div>

                  {/* User */}
                  {event.user && (
                    <div className="flex items-center gap-2 mt-3 pt-3 border-t border-gray-100">
                      <div className="w-6 h-6 rounded-full bg-gray-100 flex items-center justify-center">
                        <User className="w-3 h-3 text-gray-500" />
                      </div>
                      <span className="text-sm text-gray-600">{event.user}</span>
                    </div>
                  )}

                  {/* Metadata */}
                  {event.metadata && Object.keys(event.metadata).length > 0 && (
                    <div className="mt-3 pt-3 border-t border-gray-100">
                      <div className="flex flex-wrap gap-2">
                        {Object.entries(event.metadata).map(([key, value]) => (
                          <div
                            key={key}
                            className="px-2 py-1 bg-gray-50 rounded text-xs"
                          >
                            <span className="text-gray-500">{key}:</span>{' '}
                            <span className="text-gray-700 font-medium">{value}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </motion.div>
          );
        })}
      </div>
    </div>
  );
}
