import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  AlertTriangle,
  AlertCircle,
  Info,
  Clock,
  User,
  Calendar,
  ChevronDown,
  CheckCircle,
  X,
  Lightbulb,
  ArrowRight,
} from 'lucide-react';
import type { Conflict, ConflictType } from '../types/schedules.types';

interface ConflictAlertProps {
  conflict: Conflict;
  onResolve?: (conflictId: string) => void;
  onDismiss?: (conflictId: string) => void;
  onViewSchedules?: (scheduleIds: string[]) => void;
  variant?: 'default' | 'compact' | 'banner';
}

export const ConflictAlert: React.FC<ConflictAlertProps> = ({
  conflict,
  onResolve,
  onDismiss,
  onViewSchedules,
  variant = 'default',
}) => {
  const [isExpanded, setIsExpanded] = useState(false);

  const getConflictConfig = (tipo: ConflictType) => {
    const configs = {
      sobreposicao: {
        icon: AlertTriangle,
        title: 'Sobreposicao de Horarios',
        description: 'Profissional escalado em dois lugares ao mesmo tempo',
        color: {
          bg: 'bg-red-50',
          border: 'border-red-200',
          text: 'text-red-800',
          icon: 'text-red-600',
          badge: 'bg-red-100 text-red-700',
        },
      },
      descanso_minimo: {
        icon: Clock,
        title: 'Descanso Minimo',
        description: 'Intervalo entre turnos menor que o obrigatorio (11h)',
        color: {
          bg: 'bg-orange-50',
          border: 'border-orange-200',
          text: 'text-orange-800',
          icon: 'text-orange-600',
          badge: 'bg-orange-100 text-orange-700',
        },
      },
      limite_horas_diarias: {
        icon: AlertCircle,
        title: 'Limite de Horas Diarias',
        description: 'Excede o maximo de horas permitidas por dia',
        color: {
          bg: 'bg-yellow-50',
          border: 'border-yellow-200',
          text: 'text-yellow-800',
          icon: 'text-yellow-600',
          badge: 'bg-yellow-100 text-yellow-700',
        },
      },
      limite_horas_semanais: {
        icon: Calendar,
        title: 'Limite de Horas Semanais',
        description: 'Excede o maximo de horas permitidas por semana',
        color: {
          bg: 'bg-amber-50',
          border: 'border-amber-200',
          text: 'text-amber-800',
          icon: 'text-amber-600',
          badge: 'bg-amber-100 text-amber-700',
        },
      },
      feriado: {
        icon: Info,
        title: 'Escala em Feriado',
        description: 'Profissional escalado em dia de feriado',
        color: {
          bg: 'bg-blue-50',
          border: 'border-blue-200',
          text: 'text-blue-800',
          icon: 'text-blue-600',
          badge: 'bg-blue-100 text-blue-700',
        },
      },
      ferias: {
        icon: User,
        title: 'Profissional em Ferias',
        description: 'Profissional esta em periodo de ferias',
        color: {
          bg: 'bg-purple-50',
          border: 'border-purple-200',
          text: 'text-purple-800',
          icon: 'text-purple-600',
          badge: 'bg-purple-100 text-purple-700',
        },
      },
      atestado: {
        icon: AlertCircle,
        title: 'Profissional com Atestado',
        description: 'Profissional possui atestado medico vigente',
        color: {
          bg: 'bg-pink-50',
          border: 'border-pink-200',
          text: 'text-pink-800',
          icon: 'text-pink-600',
          badge: 'bg-pink-100 text-pink-700',
        },
      },
    };
    return configs[tipo] || configs.sobreposicao;
  };

  const getSeverityConfig = (severidade: string) => {
    const configs = {
      alta: { label: 'Alta', color: 'bg-red-500' },
      media: { label: 'Media', color: 'bg-yellow-500' },
      baixa: { label: 'Baixa', color: 'bg-blue-500' },
    };
    return configs[severidade as keyof typeof configs] || configs.baixa;
  };

  const configTipo = getConflictConfig(conflict.tipo);
  const configSeveridade = getSeverityConfig(conflict.severidade);
  const Icon = configTipo.icon;

  // Versao Banner
  if (variant === 'banner') {
    return (
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -20 }}
        className={`${configTipo.color.bg} ${configTipo.color.border} border rounded-lg p-4`}
      >
        <div className="flex items-center gap-4">
          <div className={`p-2 rounded-lg ${configTipo.color.badge}`}>
            <Icon className="w-5 h-5" />
          </div>

          <div className="flex-1">
            <div className="flex items-center gap-2 mb-0.5">
              <h4 className={`font-semibold text-sm ${configTipo.color.text}`}>
                {configTipo.title}
              </h4>
              <span
                className={`px-2 py-0.5 rounded-full text-xs font-medium text-white ${configSeveridade.color}`}
              >
                {configSeveridade.label}
              </span>
            </div>
            <p className={`text-sm ${configTipo.color.text} opacity-80`}>
              {conflict.descricao}
            </p>
          </div>

          <div className="flex items-center gap-2">
            {onViewSchedules && (
              <button
                onClick={() => onViewSchedules(conflict.schedules)}
                className={`px-3 py-1.5 text-sm font-medium rounded-lg border ${configTipo.color.border} ${configTipo.color.text} hover:bg-white/50 transition-colors`}
              >
                Ver Escalas
              </button>
            )}
            {onResolve && (
              <button
                onClick={() => onResolve(conflict.id)}
                className="px-3 py-1.5 text-sm font-medium bg-white text-gray-700 rounded-lg border border-gray-200 hover:bg-gray-50 transition-colors"
              >
                Resolver
              </button>
            )}
            {onDismiss && (
              <button
                onClick={() => onDismiss(conflict.id)}
                className="p-1.5 text-gray-400 hover:text-gray-600 rounded-lg transition-colors"
              >
                <X className="w-4 h-4" />
              </button>
            )}
          </div>
        </div>
      </motion.div>
    );
  }

  // Versao Compacta
  if (variant === 'compact') {
    return (
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className={`flex items-center gap-3 p-3 rounded-lg ${configTipo.color.bg} ${configTipo.color.border} border`}
      >
        <Icon className={`w-5 h-5 ${configTipo.color.icon}`} />
        <div className="flex-1 min-w-0">
          <p className={`text-sm font-medium ${configTipo.color.text} truncate`}>
            {conflict.profissional_nome}
          </p>
          <p className={`text-xs ${configTipo.color.text} opacity-70 truncate`}>
            {configTipo.title}
          </p>
        </div>
        <span
          className={`w-2 h-2 rounded-full ${configSeveridade.color} flex-shrink-0`}
        />
      </motion.div>
    );
  }

  // Versao Default (Expandivel)
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className={`rounded-xl border ${configTipo.color.border} overflow-hidden`}
    >
      {/* Header */}
      <div
        className={`${configTipo.color.bg} px-4 py-3 cursor-pointer`}
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className={`p-2 rounded-lg ${configTipo.color.badge}`}>
              <Icon className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h4 className={`font-semibold text-sm ${configTipo.color.text}`}>
                  {configTipo.title}
                </h4>
                <span
                  className={`px-2 py-0.5 rounded-full text-xs font-medium text-white ${configSeveridade.color}`}
                >
                  Severidade {configSeveridade.label}
                </span>
              </div>
              <p className={`text-sm ${configTipo.color.text} opacity-70 mt-0.5`}>
                {conflict.profissional_nome} - {conflict.data}
              </p>
            </div>
          </div>

          <motion.div
            animate={{ rotate: isExpanded ? 180 : 0 }}
            transition={{ duration: 0.2 }}
          >
            <ChevronDown className={`w-5 h-5 ${configTipo.color.icon}`} />
          </motion.div>
        </div>
      </div>

      {/* Conteudo Expandido */}
      <AnimatePresence>
        {isExpanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="overflow-hidden"
          >
            <div className="p-4 bg-white border-t border-gray-100">
              {/* Descricao */}
              <div className="mb-4">
                <h5 className="text-sm font-medium text-gray-700 mb-1">
                  Descricao do Conflito
                </h5>
                <p className="text-sm text-gray-600">{conflict.descricao}</p>
              </div>

              {/* Sugestao */}
              {conflict.sugestao_resolucao && (
                <div className="mb-4 p-3 bg-blue-50 rounded-lg">
                  <div className="flex items-start gap-2">
                    <Lightbulb className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
                    <div>
                      <h5 className="text-sm font-medium text-blue-800 mb-1">
                        Sugestao de Resolucao
                      </h5>
                      <p className="text-sm text-blue-700">
                        {conflict.sugestao_resolucao}
                      </p>
                    </div>
                  </div>
                </div>
              )}

              {/* Info das escalas */}
              <div className="mb-4">
                <h5 className="text-sm font-medium text-gray-700 mb-2">
                  Escalas Envolvidas
                </h5>
                <div className="space-y-2">
                  {conflict.schedules.map((scheduleId) => (
                    <div
                      key={scheduleId}
                      className="flex items-center gap-2 text-sm text-gray-600 p-2 bg-gray-50 rounded-lg"
                    >
                      <Calendar className="w-4 h-4 text-gray-400" />
                      <span>Escala #{scheduleId}</span>
                      {onViewSchedules && (
                        <button
                          onClick={() => onViewSchedules([scheduleId])}
                          className="ml-auto text-blue-600 hover:text-blue-700 text-xs font-medium flex items-center gap-1"
                        >
                          Ver <ArrowRight className="w-3 h-3" />
                        </button>
                      )}
                    </div>
                  ))}
                </div>
              </div>

              {/* Acoes */}
              <div className="flex gap-2 pt-3 border-t border-gray-100">
                {onViewSchedules && (
                  <button
                    onClick={() => onViewSchedules(conflict.schedules)}
                    className="flex-1 px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
                  >
                    Ver Todas as Escalas
                  </button>
                )}
                {onResolve && (
                  <button
                    onClick={() => onResolve(conflict.id)}
                    className="flex-1 px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 transition-colors flex items-center justify-center gap-2"
                  >
                    <CheckCircle className="w-4 h-4" />
                    Marcar como Resolvido
                  </button>
                )}
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Status de resolucao */}
      {conflict.resolvido && (
        <div className="px-4 py-2 bg-green-50 border-t border-green-200">
          <div className="flex items-center gap-2 text-sm text-green-700">
            <CheckCircle className="w-4 h-4" />
            <span>
              Resolvido por {conflict.resolvido_por} em{' '}
              {new Date(conflict.resolvido_em!).toLocaleString('pt-BR')}
            </span>
          </div>
        </div>
      )}
    </motion.div>
  );
};

// Componente para lista de conflitos
interface ConflictListProps {
  conflicts: Conflict[];
  onResolve?: (conflictId: string) => void;
  onDismiss?: (conflictId: string) => void;
  onViewSchedules?: (scheduleIds: string[]) => void;
  emptyMessage?: string;
}

export const ConflictList: React.FC<ConflictListProps> = ({
  conflicts,
  onResolve,
  onDismiss,
  onViewSchedules,
  emptyMessage = 'Nenhum conflito encontrado',
}) => {
  const activeConflicts = conflicts.filter((c) => !c.resolvido);
  const resolvedConflicts = conflicts.filter((c) => c.resolvido);

  if (conflicts.length === 0) {
    return (
      <div className="text-center py-12 bg-gray-50 rounded-xl border border-dashed border-gray-300">
        <CheckCircle className="w-12 h-12 text-green-400 mx-auto mb-3" />
        <h4 className="text-gray-600 font-medium mb-1">{emptyMessage}</h4>
        <p className="text-sm text-gray-400">
          Todas as escalas estao em conformidade
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Conflitos ativos */}
      {activeConflicts.length > 0 && (
        <div>
          <div className="flex items-center gap-2 mb-3">
            <AlertTriangle className="w-5 h-5 text-orange-600" />
            <h3 className="font-semibold text-gray-900">
              Conflitos Ativos ({activeConflicts.length})
            </h3>
          </div>
          <div className="space-y-3">
            {activeConflicts.map((conflict) => (
              <ConflictAlert
                key={conflict.id}
                conflict={conflict}
                onResolve={onResolve}
                onDismiss={onDismiss}
                onViewSchedules={onViewSchedules}
              />
            ))}
          </div>
        </div>
      )}

      {/* Conflitos resolvidos */}
      {resolvedConflicts.length > 0 && (
        <div>
          <div className="flex items-center gap-2 mb-3">
            <CheckCircle className="w-5 h-5 text-green-600" />
            <h3 className="font-semibold text-gray-900">
              Resolvidos Recentemente ({resolvedConflicts.length})
            </h3>
          </div>
          <div className="space-y-3 opacity-75">
            {resolvedConflicts.map((conflict) => (
              <ConflictAlert
                key={conflict.id}
                conflict={conflict}
                variant="compact"
              />
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default ConflictAlert;
