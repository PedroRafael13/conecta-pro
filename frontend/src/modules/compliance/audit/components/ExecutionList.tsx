import { motion } from 'framer-motion';
import { Play, CheckCircle, XCircle, Loader2, Clock, AlertTriangle, FileText } from 'lucide-react';
import { formatRelativeTime } from '@core/utils/formatters';
import type { AuditExecution } from '../types/audit.types';

interface ExecutionListProps {
  executions: AuditExecution[];
  isLoading?: boolean;
  onViewDetails?: (execution: AuditExecution) => void;
  onExport?: (id: string) => void;
}

const statusConfig = {
  executando: {
    icon: Loader2,
    color: 'text-blue-500',
    bg: 'bg-blue-50',
    label: 'Executando',
    animate: true,
  },
  completo: {
    icon: CheckCircle,
    color: 'text-green-500',
    bg: 'bg-green-50',
    label: 'Completo',
    animate: false,
  },
  erro: {
    icon: XCircle,
    color: 'text-red-500',
    bg: 'bg-red-50',
    label: 'Erro',
    animate: false,
  },
};

export function ExecutionList({ executions, isLoading, onViewDetails, onExport }: ExecutionListProps) {
  if (isLoading) {
    return (
      <div className="bg-white rounded-xl shadow-card p-6 animate-pulse">
        <div className="h-6 bg-gray-200 rounded w-40 mb-4" />
        <div className="space-y-3">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-16 bg-gray-200 rounded" />
          ))}
        </div>
      </div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-white rounded-xl shadow-card p-6"
    >
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Play className="w-5 h-5 text-conecta-escuro" />
          <h3 className="text-lg font-semibold text-gray-900">Execucoes Recentes</h3>
        </div>
        <span className="text-sm text-gray-500">{executions.length} execucoes</span>
      </div>

      <div className="space-y-3">
        {executions.map((execution, index) => {
          const config = statusConfig[execution.status];
          const Icon = config.icon;

          return (
            <motion.div
              key={execution.id}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.05 }}
              className={`${config.bg} rounded-lg p-4 hover:shadow-md transition-shadow cursor-pointer`}
              onClick={() => onViewDetails?.(execution)}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <Icon
                    className={`w-5 h-5 ${config.color} ${config.animate ? 'animate-spin' : ''}`}
                  />
                  <div>
                    <p className="font-medium text-gray-900">{execution.ruleName}</p>
                    <div className="flex items-center gap-3 text-sm text-gray-500">
                      <span className="flex items-center gap-1">
                        <Clock className="w-3 h-3" />
                        {formatRelativeTime(execution.startedAt)}
                      </span>
                      {execution.anomaliesFound > 0 && (
                        <span className="flex items-center gap-1 text-orange-600">
                          <AlertTriangle className="w-3 h-3" />
                          {execution.anomaliesFound} anomalias
                        </span>
                      )}
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  <span className={`text-xs px-2 py-1 rounded-full ${config.bg} ${config.color}`}>
                    {config.label}
                  </span>
                  {execution.status === 'completo' && (
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        onExport?.(execution.id);
                      }}
                      className="p-2 hover:bg-white rounded-lg transition-colors"
                      title="Exportar PDF"
                    >
                      <FileText className="w-4 h-4 text-gray-500" />
                    </button>
                  )}
                </div>
              </div>
            </motion.div>
          );
        })}

        {executions.length === 0 && (
          <div className="text-center py-8 text-gray-500">
            Nenhuma execucao encontrada
          </div>
        )}
      </div>
    </motion.div>
  );
}

export default ExecutionList;
