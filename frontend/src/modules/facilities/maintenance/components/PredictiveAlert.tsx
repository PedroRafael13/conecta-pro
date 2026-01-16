'use client';

import React from 'react';
import { motion } from 'framer-motion';
import {
  Brain,
  AlertTriangle,
  Calendar,
  Wrench,
  CheckCircle,
  ChevronRight,
  Sparkles,
  Cpu,
  BarChart3
} from 'lucide-react';
import type { PredictiveAlert as PredictiveAlertType } from '../types/maintenance.types';

interface PredictiveAlertProps {
  alert: PredictiveAlertType;
  onAcknowledge?: (alertId: string) => void;
  onCreateOrder?: (alertId: string) => void;
  onViewDetails?: (alert: PredictiveAlertType) => void;
  compact?: boolean;
}

const severityConfig = {
  critica: {
    bg: 'bg-red-50',
    border: 'border-red-200',
    text: 'text-red-700',
    icon: 'text-red-500',
    label: 'Critico'
  },
  alta: {
    bg: 'bg-orange-50',
    border: 'border-orange-200',
    text: 'text-orange-700',
    icon: 'text-orange-500',
    label: 'Alto'
  },
  media: {
    bg: 'bg-yellow-50',
    border: 'border-yellow-200',
    text: 'text-yellow-700',
    icon: 'text-yellow-500',
    label: 'Medio'
  },
  baixa: {
    bg: 'bg-blue-50',
    border: 'border-blue-200',
    text: 'text-blue-700',
    icon: 'text-blue-500',
    label: 'Baixo'
  }
};

export function PredictiveAlert({
  alert,
  onAcknowledge,
  onCreateOrder,
  onViewDetails,
  compact = false
}: PredictiveAlertProps) {
  const severity = severityConfig[alert.severidade];

  const getProbabilityColor = (prob: number) => {
    if (prob >= 80) return 'text-red-600';
    if (prob >= 60) return 'text-orange-600';
    if (prob >= 40) return 'text-yellow-600';
    return 'text-green-600';
  };

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString('pt-BR', {
      day: '2-digit',
      month: 'short',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  // Versao compacta
  if (compact) {
    return (
      <motion.div
        initial={{ opacity: 0, x: -10 }}
        animate={{ opacity: 1, x: 0 }}
        className={`${severity.bg} ${severity.border} border rounded-lg p-3 cursor-pointer hover:shadow-sm transition-all`}
        onClick={() => onViewDetails?.(alert)}
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className={`p-1.5 rounded-lg bg-white/50`}>
              <Brain className={`w-4 h-4 ${severity.icon}`} />
            </div>
            <div>
              <p className="text-sm font-medium text-gray-900">{alert.equipment_nome}</p>
              <p className="text-xs text-gray-500">
                {alert.probabilidade_falha}% de chance de falha em {alert.dias_estimados} dias
              </p>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            {alert.ordem_criada ? (
              <span className="flex items-center space-x-1 px-2 py-1 bg-green-100 text-green-700 rounded-full text-xs">
                <CheckCircle className="w-3 h-3" />
                <span>OS criada</span>
              </span>
            ) : (
              <span className={`px-2 py-1 rounded-full text-xs font-medium ${severity.bg} ${severity.text}`}>
                {severity.label}
              </span>
            )}
            <ChevronRight className="w-4 h-4 text-gray-400" />
          </div>
        </div>
      </motion.div>
    );
  }

  // Versao completa
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className={`bg-white border rounded-xl shadow-sm overflow-hidden ${
        alert.severidade === 'critica' ? 'ring-2 ring-red-200' : ''
      }`}
    >
      {/* Header com gradiente */}
      <div className={`${severity.bg} ${severity.border} border-b p-4`}>
        <div className="flex items-start justify-between">
          <div className="flex items-center space-x-3">
            <div className="p-2.5 bg-white rounded-lg shadow-sm">
              <Brain className={`w-6 h-6 ${severity.icon}`} />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <h3 className="font-semibold text-gray-900">Alerta Preditivo</h3>
                <span className="flex items-center space-x-1 text-xs text-purple-600">
                  <Sparkles className="w-3 h-3" />
                  <span>IA</span>
                </span>
              </div>
              <p className="text-sm text-gray-600 mt-0.5">{alert.equipment_nome}</p>
            </div>
          </div>

          <span className={`px-3 py-1 rounded-full text-xs font-medium ${severity.bg} ${severity.text} border ${severity.border}`}>
            {severity.label}
          </span>
        </div>
      </div>

      {/* Body */}
      <div className="p-4 space-y-4">
        {/* Probability Gauge */}
        <div className="flex items-center space-x-4">
          <div className="flex-shrink-0">
            <div className="relative w-20 h-20">
              <svg className="w-20 h-20 transform -rotate-90">
                <circle
                  cx="40"
                  cy="40"
                  r="35"
                  fill="none"
                  stroke="#e5e7eb"
                  strokeWidth="6"
                />
                <circle
                  cx="40"
                  cy="40"
                  r="35"
                  fill="none"
                  stroke={
                    alert.probabilidade_falha >= 80 ? '#ef4444' :
                    alert.probabilidade_falha >= 60 ? '#f97316' :
                    alert.probabilidade_falha >= 40 ? '#eab308' :
                    '#22c55e'
                  }
                  strokeWidth="6"
                  strokeLinecap="round"
                  strokeDasharray={`${alert.probabilidade_falha * 2.2} 220`}
                />
              </svg>
              <div className="absolute inset-0 flex flex-col items-center justify-center">
                <span className={`text-xl font-bold ${getProbabilityColor(alert.probabilidade_falha)}`}>
                  {alert.probabilidade_falha}%
                </span>
              </div>
            </div>
          </div>

          <div className="flex-1">
            <p className="text-sm text-gray-600">Probabilidade de Falha</p>
            <div className="flex items-center space-x-2 mt-1">
              <Calendar className="w-4 h-4 text-gray-400" />
              <span className="text-sm font-medium text-gray-900">
                Estimado em {alert.dias_estimados} dias
              </span>
            </div>
            {alert.confianca && (
              <div className="flex items-center space-x-2 mt-1">
                <BarChart3 className="w-4 h-4 text-gray-400" />
                <span className="text-xs text-gray-500">
                  Confianca do modelo: {alert.confianca}%
                </span>
              </div>
            )}
          </div>
        </div>

        {/* Recommendation */}
        <div className="bg-gray-50 rounded-lg p-3">
          <p className="text-xs text-gray-500 mb-1">Recomendacao</p>
          <p className="text-sm text-gray-700">{alert.recomendacao}</p>
        </div>

        {/* Based on factors */}
        {alert.baseado_em.length > 0 && (
          <div>
            <p className="text-xs text-gray-500 mb-2">Baseado em:</p>
            <div className="flex flex-wrap gap-2">
              {alert.baseado_em.map((fator, index) => (
                <span
                  key={index}
                  className="inline-flex items-center px-2 py-1 bg-gray-100 text-gray-700 rounded text-xs"
                >
                  {fator}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Model info */}
        {alert.modelo_ia && (
          <div className="flex items-center space-x-2 text-xs text-gray-500 pt-2 border-t border-gray-100">
            <Cpu className="w-3 h-3" />
            <span>Modelo: {alert.modelo_ia}</span>
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="px-4 py-3 bg-gray-50 border-t border-gray-100">
        <div className="flex items-center justify-between">
          <span className="text-xs text-gray-500">
            Detectado em {formatDate(alert.created_at)}
          </span>

          <div className="flex items-center space-x-2">
            {!alert.acknowledged && onAcknowledge && (
              <button
                onClick={() => onAcknowledge(alert.id)}
                className="px-3 py-1.5 text-xs text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
              >
                Reconhecer
              </button>
            )}

            {!alert.ordem_criada && onCreateOrder && (
              <button
                onClick={() => onCreateOrder(alert.id)}
                className="flex items-center space-x-1.5 px-4 py-1.5 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors"
              >
                <Wrench className="w-4 h-4" />
                <span>Criar OS</span>
              </button>
            )}

            {alert.ordem_criada && (
              <span className="flex items-center space-x-1.5 px-3 py-1.5 text-sm text-green-700 bg-green-100 rounded-lg">
                <CheckCircle className="w-4 h-4" />
                <span>OS {alert.ordem_id}</span>
              </span>
            )}
          </div>
        </div>
      </div>
    </motion.div>
  );
}

// Lista de alertas preditivos
interface PredictiveAlertListProps {
  alerts: PredictiveAlertType[];
  onAcknowledge?: (alertId: string) => void;
  onCreateOrder?: (alertId: string) => void;
  onViewDetails?: (alert: PredictiveAlertType) => void;
}

export function PredictiveAlertList({
  alerts,
  onAcknowledge,
  onCreateOrder,
  onViewDetails
}: PredictiveAlertListProps) {
  if (alerts.length === 0) {
    return (
      <div className="text-center py-12">
        <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <CheckCircle className="w-8 h-8 text-green-500" />
        </div>
        <h3 className="text-lg font-medium text-gray-900 mb-1">Tudo em ordem!</h3>
        <p className="text-gray-500">Nenhum alerta preditivo no momento</p>
      </div>
    );
  }

  // Ordenar por severidade e probabilidade
  const sortedAlerts = [...alerts].sort((a, b) => {
    const severityOrder = { critica: 0, alta: 1, media: 2, baixa: 3 };
    if (severityOrder[a.severidade] !== severityOrder[b.severidade]) {
      return severityOrder[a.severidade] - severityOrder[b.severidade];
    }
    return b.probabilidade_falha - a.probabilidade_falha;
  });

  return (
    <div className="space-y-4">
      {/* Summary */}
      <div className="grid grid-cols-4 gap-4 mb-6">
        <div className="bg-red-50 border border-red-200 rounded-lg p-3">
          <p className="text-2xl font-bold text-red-700">
            {alerts.filter(a => a.severidade === 'critica').length}
          </p>
          <p className="text-xs text-red-600">Criticos</p>
        </div>
        <div className="bg-orange-50 border border-orange-200 rounded-lg p-3">
          <p className="text-2xl font-bold text-orange-700">
            {alerts.filter(a => a.severidade === 'alta').length}
          </p>
          <p className="text-xs text-orange-600">Alta prioridade</p>
        </div>
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3">
          <p className="text-2xl font-bold text-yellow-700">
            {alerts.filter(a => a.severidade === 'media').length}
          </p>
          <p className="text-xs text-yellow-600">Media prioridade</p>
        </div>
        <div className="bg-green-50 border border-green-200 rounded-lg p-3">
          <p className="text-2xl font-bold text-green-700">
            {alerts.filter(a => a.ordem_criada).length}
          </p>
          <p className="text-xs text-green-600">Com OS criada</p>
        </div>
      </div>

      {/* Alert cards */}
      {sortedAlerts.map((alert, index) => (
        <motion.div
          key={alert.id}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: index * 0.1 }}
        >
          <PredictiveAlert
            alert={alert}
            onAcknowledge={onAcknowledge}
            onCreateOrder={onCreateOrder}
            onViewDetails={onViewDetails}
          />
        </motion.div>
      ))}
    </div>
  );
}

// Widget de resumo para dashboard
interface PredictiveSummaryWidgetProps {
  alerts: PredictiveAlertType[];
  onViewAll?: () => void;
}

export function PredictiveSummaryWidget({ alerts, onViewAll }: PredictiveSummaryWidgetProps) {
  const criticalCount = alerts.filter(a => a.severidade === 'critica' || a.severidade === 'alta').length;
  const pendingCount = alerts.filter(a => !a.ordem_criada).length;

  return (
    <div className="bg-gradient-to-br from-purple-500 to-indigo-600 rounded-xl p-5 text-white">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-2">
          <Brain className="w-6 h-6" />
          <h3 className="font-semibold">Manutencao Preditiva</h3>
        </div>
        <Sparkles className="w-5 h-5 opacity-70" />
      </div>

      <div className="grid grid-cols-2 gap-4 mb-4">
        <div className="bg-white/10 rounded-lg p-3">
          <p className="text-3xl font-bold">{alerts.length}</p>
          <p className="text-sm opacity-80">Alertas Ativos</p>
        </div>
        <div className="bg-white/10 rounded-lg p-3">
          <p className="text-3xl font-bold">{pendingCount}</p>
          <p className="text-sm opacity-80">Aguardando Acao</p>
        </div>
      </div>

      {criticalCount > 0 && (
        <div className="flex items-center space-x-2 bg-red-500/20 rounded-lg p-2 mb-4">
          <AlertTriangle className="w-4 h-4" />
          <span className="text-sm">{criticalCount} alertas de alta prioridade</span>
        </div>
      )}

      {onViewAll && (
        <button
          onClick={onViewAll}
          className="w-full flex items-center justify-center space-x-2 py-2 bg-white/20 hover:bg-white/30 rounded-lg transition-colors"
        >
          <span className="text-sm font-medium">Ver Todos os Alertas</span>
          <ChevronRight className="w-4 h-4" />
        </button>
      )}
    </div>
  );
}

export default PredictiveAlert;
