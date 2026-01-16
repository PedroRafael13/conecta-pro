import { motion } from 'framer-motion';
import { AlertTriangle, TrendingDown, TrendingUp, Eye, CheckCircle } from 'lucide-react';
import { formatRelativeTime } from '@core/utils/formatters';
import { Skeleton } from '@core/components/feedback';
import type { AnomalyData } from '../types/dashboard.types';

interface AnomalyDetectionProps {
  anomalies: AnomalyData[];
  isLoading?: boolean;
}

const severityConfig = {
  low: {
    bg: 'bg-yellow-50',
    border: 'border-yellow-200',
    text: 'text-yellow-700',
    icon: 'text-yellow-500',
    badge: 'bg-yellow-100 text-yellow-700',
  },
  medium: {
    bg: 'bg-orange-50',
    border: 'border-orange-200',
    text: 'text-orange-700',
    icon: 'text-orange-500',
    badge: 'bg-orange-100 text-orange-700',
  },
  high: {
    bg: 'bg-red-50',
    border: 'border-red-200',
    text: 'text-red-700',
    icon: 'text-red-500',
    badge: 'bg-red-100 text-red-700',
  },
};

function AnomalyCard({ anomaly, index }: { anomaly: AnomalyData; index: number }) {
  const config = severityConfig[anomaly.severity];
  const isNegative = anomaly.deviation < 0;

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.1 }}
      className={`${config.bg} ${config.border} border rounded-lg p-4`}
    >
      <div className="flex items-start justify-between">
        <div className="flex items-start gap-3">
          <div className={`p-2 rounded-lg ${config.badge}`}>
            <AlertTriangle className="w-4 h-4" />
          </div>
          <div>
            <h4 className="font-medium text-gray-900">{anomaly.metric}</h4>
            <p className="text-sm text-gray-600 mt-1">{anomaly.description}</p>
          </div>
        </div>
        <span className={`text-xs px-2 py-1 rounded-full ${config.badge}`}>
          {anomaly.severity === 'high' ? 'Alta' : anomaly.severity === 'medium' ? 'Media' : 'Baixa'}
        </span>
      </div>

      <div className="mt-4 grid grid-cols-3 gap-4">
        <div>
          <p className="text-xs text-gray-500">Valor Atual</p>
          <p className={`text-lg font-semibold ${config.text}`}>{anomaly.value}</p>
        </div>
        <div>
          <p className="text-xs text-gray-500">Esperado</p>
          <p className="text-lg font-semibold text-gray-900">{anomaly.expected}</p>
        </div>
        <div>
          <p className="text-xs text-gray-500">Desvio</p>
          <div className="flex items-center gap-1">
            {isNegative ? (
              <TrendingDown className="w-4 h-4 text-red-500" />
            ) : (
              <TrendingUp className="w-4 h-4 text-red-500" />
            )}
            <p className={`text-lg font-semibold ${config.text}`}>
              {anomaly.deviation > 0 ? '+' : ''}{anomaly.deviation.toFixed(1)}%
            </p>
          </div>
        </div>
      </div>

      <div className="mt-4 flex items-center justify-between">
        <span className="text-xs text-gray-500">
          Detectado {formatRelativeTime(anomaly.timestamp)}
        </span>
        <div className="flex items-center gap-2">
          <button className="text-xs text-conecta-escuro hover:text-conecta-medio flex items-center gap-1">
            <Eye className="w-3 h-3" />
            Investigar
          </button>
          <button className="text-xs text-green-600 hover:text-green-700 flex items-center gap-1">
            <CheckCircle className="w-3 h-3" />
            Resolver
          </button>
        </div>
      </div>
    </motion.div>
  );
}

export function AnomalyDetection({ anomalies, isLoading }: AnomalyDetectionProps) {
  if (isLoading) {
    return (
      <div className="bg-white rounded-xl shadow-card p-6">
        <Skeleton height={24} className="w-48 mb-4" />
        <div className="space-y-4">
          {[1, 2].map((i) => (
            <Skeleton key={i} height={140} />
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl shadow-card p-6 h-full">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <AlertTriangle className="w-5 h-5 text-conecta-laranja" />
          <h3 className="text-lg font-semibold text-gray-900">Deteccao de Anomalias</h3>
        </div>
        <span className="text-xs px-2 py-1 bg-red-100 text-red-700 rounded-full">
          {anomalies.length} detectadas
        </span>
      </div>

      {anomalies.length > 0 ? (
        <div className="space-y-4">
          {anomalies.map((anomaly, index) => (
            <AnomalyCard key={anomaly.id} anomaly={anomaly} index={index} />
          ))}
        </div>
      ) : (
        <div className="text-center py-12">
          <CheckCircle className="w-12 h-12 text-green-500 mx-auto mb-3" />
          <p className="text-gray-600">Nenhuma anomalia detectada</p>
          <p className="text-sm text-gray-500 mt-1">
            Todos os indicadores estao dentro dos parametros esperados
          </p>
        </div>
      )}
    </div>
  );
}

export default AnomalyDetection;
