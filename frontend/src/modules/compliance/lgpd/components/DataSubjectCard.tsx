'use client';

import { motion } from 'framer-motion';
import { clsx } from 'clsx';
import {
  User,
  Mail,
  Phone,
  FileText,
  Download,
  Trash2,
  Edit2,
  Clock,
  CheckCircle,
  AlertTriangle,
} from 'lucide-react';

type RequestType = 'access' | 'rectification' | 'deletion' | 'portability' | 'objection';
type RequestStatus = 'pending' | 'in_progress' | 'completed' | 'rejected';

interface DataSubjectRequest {
  id: string;
  type: RequestType;
  status: RequestStatus;
  createdAt: Date;
  deadline: Date;
}

interface DataSubjectCardProps {
  id: string;
  name: string;
  email: string;
  phone?: string;
  document?: string;
  registrationDate: Date;
  lastActivity?: Date;
  activeConsents: number;
  totalRequests: number;
  pendingRequests: DataSubjectRequest[];
  onViewDetails?: (id: string) => void;
  onCreateRequest?: (id: string, type: RequestType) => void;
  onExportData?: (id: string) => void;
  onAnonymize?: (id: string) => void;
  className?: string;
}

const requestTypeLabels: Record<RequestType, string> = {
  access: 'Acesso',
  rectification: 'Retificacao',
  deletion: 'Exclusao',
  portability: 'Portabilidade',
  objection: 'Oposicao',
};

const requestStatusConfig: Record<RequestStatus, { label: string; color: string; icon: typeof Clock }> = {
  pending: { label: 'Pendente', color: 'text-yellow-600 bg-yellow-100', icon: Clock },
  in_progress: { label: 'Em andamento', color: 'text-blue-600 bg-blue-100', icon: Clock },
  completed: { label: 'Concluido', color: 'text-green-600 bg-green-100', icon: CheckCircle },
  rejected: { label: 'Rejeitado', color: 'text-red-600 bg-red-100', icon: AlertTriangle },
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

export function DataSubjectCard({
  id,
  name,
  email,
  phone,
  document,
  registrationDate,
  lastActivity,
  activeConsents,
  totalRequests,
  pendingRequests,
  onViewDetails,
  onCreateRequest,
  onExportData,
  onAnonymize,
  className,
}: DataSubjectCardProps) {
  const hasPendingRequests = pendingRequests.length > 0;
  const urgentRequests = pendingRequests.filter((r) => getDaysUntilDeadline(r.deadline) <= 5);

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className={clsx(
        'bg-white rounded-xl border shadow-sm overflow-hidden',
        'hover:shadow-md transition-shadow duration-200',
        hasPendingRequests ? 'border-[#FF6B35]' : 'border-gray-200',
        className
      )}
    >
      {/* Header */}
      <div className="p-4 border-b border-gray-100">
        <div className="flex items-start gap-4">
          {/* Avatar */}
          <div className="w-12 h-12 rounded-full bg-[#0A2540] flex items-center justify-center flex-shrink-0">
            <User className="w-6 h-6 text-white" />
          </div>

          {/* Info */}
          <div className="flex-1 min-w-0">
            <h3 className="text-lg font-semibold text-[#0A2540] truncate">{name}</h3>
            <div className="flex flex-col gap-1 mt-1">
              <div className="flex items-center gap-2 text-sm text-gray-600">
                <Mail className="w-4 h-4" />
                <span className="truncate">{email}</span>
              </div>
              {phone && (
                <div className="flex items-center gap-2 text-sm text-gray-600">
                  <Phone className="w-4 h-4" />
                  <span>{phone}</span>
                </div>
              )}
              {document && (
                <div className="flex items-center gap-2 text-sm text-gray-600">
                  <FileText className="w-4 h-4" />
                  <span>{document}</span>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-3 divide-x divide-gray-100 bg-gray-50">
        <div className="p-3 text-center">
          <p className="text-2xl font-bold text-[#0A2540]">{activeConsents}</p>
          <p className="text-xs text-gray-500">Consentimentos</p>
        </div>
        <div className="p-3 text-center">
          <p className="text-2xl font-bold text-[#0A2540]">{totalRequests}</p>
          <p className="text-xs text-gray-500">Solicitacoes</p>
        </div>
        <div className="p-3 text-center">
          <p className={clsx('text-2xl font-bold', urgentRequests.length > 0 ? 'text-red-600' : 'text-green-600')}>
            {pendingRequests.length}
          </p>
          <p className="text-xs text-gray-500">Pendentes</p>
        </div>
      </div>

      {/* Pending Requests */}
      {hasPendingRequests && (
        <div className="p-4 border-t border-gray-100">
          <h4 className="text-sm font-medium text-gray-700 mb-2">Solicitacoes Pendentes</h4>
          <div className="space-y-2">
            {pendingRequests.slice(0, 3).map((request) => {
              const config = requestStatusConfig[request.status];
              const daysLeft = getDaysUntilDeadline(request.deadline);
              const isUrgent = daysLeft <= 5;

              return (
                <div
                  key={request.id}
                  className={clsx(
                    'flex items-center justify-between p-2 rounded-lg',
                    isUrgent ? 'bg-red-50' : 'bg-gray-50'
                  )}
                >
                  <div className="flex items-center gap-2">
                    <span className={clsx('px-2 py-0.5 text-xs font-medium rounded-full', config.color)}>
                      {requestTypeLabels[request.type]}
                    </span>
                    <span className="text-xs text-gray-500">{formatDate(request.createdAt)}</span>
                  </div>
                  <div className={clsx('flex items-center gap-1 text-xs font-medium', isUrgent ? 'text-red-600' : 'text-gray-600')}>
                    <Clock className="w-3 h-3" />
                    <span>{daysLeft}d restantes</span>
                  </div>
                </div>
              );
            })}
            {pendingRequests.length > 3 && (
              <p className="text-xs text-gray-500 text-center mt-1">
                +{pendingRequests.length - 3} mais solicitacoes
              </p>
            )}
          </div>
        </div>
      )}

      {/* Dates */}
      <div className="px-4 py-2 bg-gray-50 border-t border-gray-100">
        <div className="flex justify-between text-xs text-gray-500">
          <span>Cadastro: {formatDate(registrationDate)}</span>
          {lastActivity && <span>Ultima atividade: {formatDate(lastActivity)}</span>}
        </div>
      </div>

      {/* Actions */}
      <div className="px-4 py-3 border-t border-gray-100">
        <div className="flex items-center justify-between">
          {/* Quick Actions */}
          <div className="flex items-center gap-1">
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => onCreateRequest?.(id, 'access')}
              className="px-2 py-1 text-xs font-medium text-[#0A2540] hover:bg-gray-100 rounded transition-colors"
            >
              Acesso
            </motion.button>
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => onCreateRequest?.(id, 'portability')}
              className="px-2 py-1 text-xs font-medium text-[#0A2540] hover:bg-gray-100 rounded transition-colors"
            >
              Portabilidade
            </motion.button>
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => onCreateRequest?.(id, 'deletion')}
              className="px-2 py-1 text-xs font-medium text-red-600 hover:bg-red-50 rounded transition-colors"
            >
              Exclusao
            </motion.button>
          </div>

          {/* Icon Actions */}
          <div className="flex items-center gap-2">
            {onViewDetails && (
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => onViewDetails(id)}
                className="p-2 text-gray-500 hover:text-[#0A2540] hover:bg-gray-100 rounded-lg transition-colors"
                title="Ver detalhes"
              >
                <Edit2 className="w-4 h-4" />
              </motion.button>
            )}
            {onExportData && (
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => onExportData(id)}
                className="p-2 text-gray-500 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                title="Exportar dados"
              >
                <Download className="w-4 h-4" />
              </motion.button>
            )}
            {onAnonymize && (
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => onAnonymize(id)}
                className="p-2 text-gray-500 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                title="Anonimizar"
              >
                <Trash2 className="w-4 h-4" />
              </motion.button>
            )}
          </div>
        </div>
      </div>
    </motion.div>
  );
}
