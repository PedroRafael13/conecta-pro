'use client';

import { motion } from 'framer-motion';
import { clsx } from 'clsx';
import {
  Calendar,
  Clock,
  CheckCircle,
  XCircle,
  AlertTriangle,
  ChevronRight,
  Bell,
} from 'lucide-react';

type ObligationStatus = 'pending' | 'in_progress' | 'completed' | 'overdue' | 'not_applicable';
type ObligationPriority = 'low' | 'medium' | 'high' | 'critical';
type ObligationType = 'monthly' | 'quarterly' | 'annual' | 'eventual';

interface ObligationItemProps {
  id: string;
  title: string;
  description?: string;
  code?: string; // e.g., "GFIP", "DCTF", "EFD"
  status: ObligationStatus;
  priority: ObligationPriority;
  type: ObligationType;
  deadline: Date;
  completedAt?: Date;
  responsible?: string;
  relatedAPI?: string;
  onClick?: (id: string) => void;
  onMarkComplete?: (id: string) => void;
  onSetReminder?: (id: string) => void;
  className?: string;
}

const statusConfig: Record<
  ObligationStatus,
  { label: string; color: string; bgColor: string; icon: typeof Clock }
> = {
  pending: {
    label: 'Pendente',
    color: 'text-yellow-600',
    bgColor: 'bg-yellow-100',
    icon: Clock,
  },
  in_progress: {
    label: 'Em Andamento',
    color: 'text-blue-600',
    bgColor: 'bg-blue-100',
    icon: Clock,
  },
  completed: {
    label: 'Concluido',
    color: 'text-green-600',
    bgColor: 'bg-green-100',
    icon: CheckCircle,
  },
  overdue: {
    label: 'Atrasado',
    color: 'text-red-600',
    bgColor: 'bg-red-100',
    icon: XCircle,
  },
  not_applicable: {
    label: 'N/A',
    color: 'text-gray-600',
    bgColor: 'bg-gray-100',
    icon: AlertTriangle,
  },
};

const priorityConfig: Record<ObligationPriority, { color: string; label: string }> = {
  low: { color: 'bg-gray-400', label: 'Baixa' },
  medium: { color: 'bg-yellow-400', label: 'Media' },
  high: { color: 'bg-orange-500', label: 'Alta' },
  critical: { color: 'bg-red-500', label: 'Critica' },
};

const typeLabels: Record<ObligationType, string> = {
  monthly: 'Mensal',
  quarterly: 'Trimestral',
  annual: 'Anual',
  eventual: 'Eventual',
};

function formatDate(date: Date): string {
  return date.toLocaleDateString('pt-BR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
  });
}

function getDaysUntilDeadline(deadline: Date): number {
  const now = new Date();
  const diffTime = deadline.getTime() - now.getTime();
  return Math.ceil(diffTime / (1000 * 60 * 60 * 24));
}

export function ObligationItem({
  id,
  title,
  description,
  code,
  status,
  priority,
  type,
  deadline,
  completedAt,
  responsible,
  relatedAPI,
  onClick,
  onMarkComplete,
  onSetReminder,
  className,
}: ObligationItemProps) {
  const config = statusConfig[status];
  const priorityStyle = priorityConfig[priority];
  const StatusIcon = config.icon;
  const daysUntil = getDaysUntilDeadline(deadline);
  const isUrgent = status !== 'completed' && status !== 'not_applicable' && daysUntil <= 5;
  const isOverdue = daysUntil < 0;

  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.2 }}
      className={clsx(
        'group bg-white rounded-lg border transition-all duration-200',
        'hover:shadow-md cursor-pointer',
        isUrgent && status !== 'overdue' && 'border-yellow-300 bg-yellow-50/30',
        status === 'overdue' && 'border-red-300 bg-red-50/30',
        status !== 'overdue' && !isUrgent && 'border-gray-200',
        className
      )}
      onClick={() => onClick?.(id)}
    >
      <div className="p-4">
        <div className="flex items-start gap-4">
          {/* Priority Indicator */}
          <div className="flex flex-col items-center gap-2 flex-shrink-0">
            <div
              className={clsx(
                'w-2 h-2 rounded-full',
                priorityStyle.color
              )}
              title={`Prioridade: ${priorityStyle.label}`}
            />
            <div
              className={clsx(
                'w-10 h-10 rounded-lg flex items-center justify-center',
                config.bgColor
              )}
            >
              <StatusIcon className={clsx('w-5 h-5', config.color)} />
            </div>
          </div>

          {/* Content */}
          <div className="flex-1 min-w-0">
            <div className="flex items-start justify-between gap-2">
              <div>
                <div className="flex items-center gap-2">
                  {code && (
                    <span className="px-2 py-0.5 text-xs font-mono font-bold bg-[#0A2540] text-white rounded">
                      {code}
                    </span>
                  )}
                  <h4 className="font-semibold text-[#0A2540] group-hover:text-[#FF6B35] transition-colors">
                    {title}
                  </h4>
                </div>
                {description && (
                  <p className="text-sm text-gray-600 mt-1 line-clamp-2">
                    {description}
                  </p>
                )}
              </div>

              <ChevronRight className="w-5 h-5 text-gray-400 group-hover:text-[#FF6B35] transition-colors flex-shrink-0" />
            </div>

            {/* Meta info */}
            <div className="flex flex-wrap items-center gap-3 mt-3">
              {/* Type */}
              <span className="text-xs text-gray-500 bg-gray-100 px-2 py-0.5 rounded">
                {typeLabels[type]}
              </span>

              {/* Status */}
              <span
                className={clsx(
                  'text-xs font-medium px-2 py-0.5 rounded-full',
                  config.bgColor,
                  config.color
                )}
              >
                {config.label}
              </span>

              {/* Related API */}
              {relatedAPI && (
                <span className="text-xs text-gray-500">
                  via {relatedAPI}
                </span>
              )}

              {/* Responsible */}
              {responsible && (
                <span className="text-xs text-gray-500">
                  Resp: {responsible}
                </span>
              )}
            </div>

            {/* Deadline */}
            <div className="flex items-center justify-between mt-3 pt-3 border-t border-gray-100">
              <div className="flex items-center gap-4">
                {/* Deadline */}
                <div className="flex items-center gap-1.5">
                  <Calendar className="w-4 h-4 text-gray-400" />
                  <span
                    className={clsx(
                      'text-sm font-medium',
                      isOverdue ? 'text-red-600' : isUrgent ? 'text-yellow-600' : 'text-gray-700'
                    )}
                  >
                    {formatDate(deadline)}
                  </span>
                </div>

                {/* Days remaining */}
                {status !== 'completed' && status !== 'not_applicable' && (
                  <div
                    className={clsx(
                      'flex items-center gap-1 text-sm',
                      isOverdue ? 'text-red-600' : isUrgent ? 'text-yellow-600' : 'text-gray-500'
                    )}
                  >
                    <Clock className="w-4 h-4" />
                    {isOverdue ? (
                      <span>{Math.abs(daysUntil)}d atrasado</span>
                    ) : (
                      <span>{daysUntil}d restantes</span>
                    )}
                  </div>
                )}

                {/* Completed date */}
                {completedAt && (
                  <div className="flex items-center gap-1 text-sm text-green-600">
                    <CheckCircle className="w-4 h-4" />
                    <span>Concluido em {formatDate(completedAt)}</span>
                  </div>
                )}
              </div>

              {/* Quick Actions */}
              <div className="flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                {onSetReminder && status !== 'completed' && (
                  <motion.button
                    whileHover={{ scale: 1.1 }}
                    whileTap={{ scale: 0.9 }}
                    onClick={(e) => {
                      e.stopPropagation();
                      onSetReminder(id);
                    }}
                    className="p-1.5 text-gray-500 hover:text-[#FF6B35] hover:bg-orange-50 rounded-lg transition-colors"
                    title="Definir lembrete"
                  >
                    <Bell className="w-4 h-4" />
                  </motion.button>
                )}
                {onMarkComplete && status !== 'completed' && status !== 'not_applicable' && (
                  <motion.button
                    whileHover={{ scale: 1.1 }}
                    whileTap={{ scale: 0.9 }}
                    onClick={(e) => {
                      e.stopPropagation();
                      onMarkComplete(id);
                    }}
                    className="p-1.5 text-gray-500 hover:text-green-600 hover:bg-green-50 rounded-lg transition-colors"
                    title="Marcar como concluido"
                  >
                    <CheckCircle className="w-4 h-4" />
                  </motion.button>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </motion.div>
  );
}
