import { motion } from 'framer-motion';
import {
  AlertTriangle,
  AlertCircle,
  Info,
  Clock,
  User,
  MessageSquare,
  CheckCircle,
  MoreVertical,
} from 'lucide-react';
import { formatRelativeTime } from '@core/utils/formatters';
import { Avatar } from '@core/components/ui';
import type { Anomaly } from '../types/audit.types';

interface AnomalyCardProps {
  anomaly: Anomaly;
  onAssign?: (id: string) => void;
  onResolve?: (id: string) => void;
  onViewDetails?: (anomaly: Anomaly) => void;
}

const priorityConfig = {
  urgente: {
    icon: AlertTriangle,
    color: 'text-red-500',
    bg: 'bg-red-50',
    border: 'border-red-200',
    badge: 'bg-red-100 text-red-700',
  },
  alta: {
    icon: AlertCircle,
    color: 'text-orange-500',
    bg: 'bg-orange-50',
    border: 'border-orange-200',
    badge: 'bg-orange-100 text-orange-700',
  },
  media: {
    icon: Info,
    color: 'text-yellow-500',
    bg: 'bg-yellow-50',
    border: 'border-yellow-200',
    badge: 'bg-yellow-100 text-yellow-700',
  },
  baixa: {
    icon: Info,
    color: 'text-blue-500',
    bg: 'bg-blue-50',
    border: 'border-blue-200',
    badge: 'bg-blue-100 text-blue-700',
  },
};

const statusConfig = {
  pendente: { label: 'Pendente', color: 'bg-gray-100 text-gray-700' },
  em_analise: { label: 'Em Analise', color: 'bg-blue-100 text-blue-700' },
  resolvida: { label: 'Resolvida', color: 'bg-green-100 text-green-700' },
};

export function AnomalyCard({ anomaly, onAssign, onResolve, onViewDetails }: AnomalyCardProps) {
  const config = priorityConfig[anomaly.priority];
  const status = statusConfig[anomaly.status];
  const Icon = config.icon;

  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      className={`${config.bg} ${config.border} border rounded-xl p-4 hover:shadow-md transition-shadow`}
    >
      <div className="flex items-start gap-3">
        <div className={`p-2 rounded-lg ${config.bg}`}>
          <Icon className={`w-5 h-5 ${config.color}`} />
        </div>

        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between gap-2">
            <div>
              <h4 className="font-medium text-gray-900">{anomaly.title}</h4>
              <p className="text-sm text-gray-600 mt-0.5">{anomaly.description}</p>
            </div>
            <button className="p-1 hover:bg-white/50 rounded">
              <MoreVertical className="w-4 h-4 text-gray-400" />
            </button>
          </div>

          <div className="flex items-center gap-3 mt-3 flex-wrap">
            <span className={`text-xs px-2 py-0.5 rounded-full ${config.badge}`}>
              {anomaly.priority}
            </span>
            <span className={`text-xs px-2 py-0.5 rounded-full ${status.color}`}>
              {status.label}
            </span>
            <span className="text-xs text-gray-500 flex items-center gap-1">
              <Clock className="w-3 h-3" />
              {formatRelativeTime(anomaly.detectedAt)}
            </span>
            {anomaly.comments.length > 0 && (
              <span className="text-xs text-gray-500 flex items-center gap-1">
                <MessageSquare className="w-3 h-3" />
                {anomaly.comments.length}
              </span>
            )}
          </div>

          <div className="flex items-center justify-between mt-4 pt-3 border-t border-gray-200/50">
            <div className="flex items-center gap-2">
              {anomaly.assignedTo ? (
                <div className="flex items-center gap-2">
                  <Avatar name={anomaly.assignedTo.name} size="xs" />
                  <span className="text-xs text-gray-600">{anomaly.assignedTo.name}</span>
                </div>
              ) : (
                <button
                  onClick={() => onAssign?.(anomaly.id)}
                  className="text-xs text-conecta-escuro hover:underline flex items-center gap-1"
                >
                  <User className="w-3 h-3" />
                  Atribuir
                </button>
              )}
            </div>

            <div className="flex items-center gap-2">
              {anomaly.status !== 'resolvida' && (
                <button
                  onClick={() => onResolve?.(anomaly.id)}
                  className="text-xs px-3 py-1 bg-green-100 text-green-700 rounded-full hover:bg-green-200 flex items-center gap-1"
                >
                  <CheckCircle className="w-3 h-3" />
                  Resolver
                </button>
              )}
              <button
                onClick={() => onViewDetails?.(anomaly)}
                className="text-xs px-3 py-1 bg-white text-gray-700 rounded-full hover:bg-gray-100"
              >
                Detalhes
              </button>
            </div>
          </div>
        </div>
      </div>
    </motion.div>
  );
}

export default AnomalyCard;
