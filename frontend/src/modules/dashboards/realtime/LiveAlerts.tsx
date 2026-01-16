import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  AlertTriangle,
  Shield,
  Lock,
  FileText,
  X,
  Check,
  Bell,
  Volume2,
  VolumeX,
} from 'lucide-react';
import { formatRelativeTime } from '@core/utils/formatters';
import type { LiveAlert } from '../types/dashboard.types';

interface LiveAlertsProps {
  maxAlerts?: number;
}

const alertConfig = {
  anomaly: {
    icon: AlertTriangle,
    color: 'text-yellow-500',
    bg: 'bg-yellow-50',
    border: 'border-yellow-200',
  },
  compliance: {
    icon: Shield,
    color: 'text-red-500',
    bg: 'bg-red-50',
    border: 'border-red-200',
  },
  security: {
    icon: Lock,
    color: 'text-purple-500',
    bg: 'bg-purple-50',
    border: 'border-purple-200',
  },
  document: {
    icon: FileText,
    color: 'text-blue-500',
    bg: 'bg-blue-50',
    border: 'border-blue-200',
  },
};

const severityColors = {
  low: 'bg-yellow-100 text-yellow-700',
  medium: 'bg-orange-100 text-orange-700',
  high: 'bg-red-100 text-red-700',
  critical: 'bg-red-600 text-white',
};

// Mock alerts for demo
const mockAlerts: LiveAlert[] = [
  {
    id: '1',
    type: 'anomaly',
    severity: 'medium',
    message: 'Anomalia detectada: Queda de 30% na taxa de conversao',
    timestamp: new Date(Date.now() - 2 * 60 * 1000).toISOString(),
    acknowledged: false,
  },
  {
    id: '2',
    type: 'compliance',
    severity: 'high',
    message: 'Falha de compliance: Documento sem assinatura digital',
    timestamp: new Date(Date.now() - 5 * 60 * 1000).toISOString(),
    acknowledged: false,
  },
  {
    id: '3',
    type: 'document',
    severity: 'low',
    message: 'Documento aguardando aprovacao: Contrato #2847',
    timestamp: new Date(Date.now() - 15 * 60 * 1000).toISOString(),
    acknowledged: true,
  },
];

function AlertItem({
  alert,
  onAcknowledge,
  onDismiss,
}: {
  alert: LiveAlert;
  onAcknowledge: (id: string) => void;
  onDismiss: (id: string) => void;
}) {
  const config = alertConfig[alert.type];
  const Icon = config.icon;

  return (
    <motion.div
      initial={{ opacity: 0, x: -20, height: 0 }}
      animate={{ opacity: 1, x: 0, height: 'auto' }}
      exit={{ opacity: 0, x: 20, height: 0 }}
      className={`${config.bg} ${config.border} border rounded-lg p-4 ${
        alert.acknowledged ? 'opacity-60' : ''
      }`}
    >
      <div className="flex items-start gap-3">
        <div className={`p-2 rounded-lg ${config.bg}`}>
          <Icon className={`w-5 h-5 ${config.color}`} />
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between gap-2">
            <p className="text-sm text-gray-900">{alert.message}</p>
            <span className={`text-xs px-2 py-0.5 rounded-full flex-shrink-0 ${severityColors[alert.severity]}`}>
              {alert.severity}
            </span>
          </div>
          <p className="text-xs text-gray-500 mt-1">
            {formatRelativeTime(alert.timestamp)}
          </p>
        </div>
      </div>

      <div className="flex items-center justify-end gap-2 mt-3">
        {!alert.acknowledged && (
          <button
            onClick={() => onAcknowledge(alert.id)}
            className="text-xs text-green-600 hover:text-green-700 flex items-center gap-1"
          >
            <Check className="w-3 h-3" />
            Reconhecer
          </button>
        )}
        <button
          onClick={() => onDismiss(alert.id)}
          className="text-xs text-gray-500 hover:text-gray-700 flex items-center gap-1"
        >
          <X className="w-3 h-3" />
          Dispensar
        </button>
      </div>
    </motion.div>
  );
}

export function LiveAlerts({ maxAlerts = 5 }: LiveAlertsProps) {
  const [alerts, setAlerts] = useState<LiveAlert[]>(mockAlerts);
  const [soundEnabled, setSoundEnabled] = useState(false);

  // Simulate new alerts
  useEffect(() => {
    const interval = setInterval(() => {
      // 20% chance of new alert
      if (Math.random() < 0.2) {
        const newAlert: LiveAlert = {
          id: Date.now().toString(),
          type: (['anomaly', 'compliance', 'security', 'document'] as const)[
            Math.floor(Math.random() * 4)
          ],
          severity: (['low', 'medium', 'high'] as const)[Math.floor(Math.random() * 3)],
          message: [
            'Nova anomalia detectada no sistema',
            'Verificacao de compliance pendente',
            'Tentativa de acesso nao autorizado',
            'Documento requer atencao',
          ][Math.floor(Math.random() * 4)],
          timestamp: new Date().toISOString(),
          acknowledged: false,
        };

        setAlerts((prev) => [newAlert, ...prev].slice(0, maxAlerts));
      }
    }, 10000);

    return () => clearInterval(interval);
  }, [maxAlerts]);

  const handleAcknowledge = (id: string) => {
    setAlerts((prev) =>
      prev.map((a) => (a.id === id ? { ...a, acknowledged: true } : a))
    );
  };

  const handleDismiss = (id: string) => {
    setAlerts((prev) => prev.filter((a) => a.id !== id));
  };

  const unacknowledgedCount = alerts.filter((a) => !a.acknowledged).length;

  return (
    <div className="bg-white rounded-xl shadow-card p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Bell className="w-5 h-5 text-conecta-laranja" />
          <h3 className="text-lg font-semibold text-gray-900">Alertas em Tempo Real</h3>
          {unacknowledgedCount > 0 && (
            <span className="px-2 py-0.5 text-xs bg-red-100 text-red-700 rounded-full">
              {unacknowledgedCount} novos
            </span>
          )}
        </div>
        <button
          onClick={() => setSoundEnabled(!soundEnabled)}
          className={`p-2 rounded-lg transition-colors ${
            soundEnabled
              ? 'bg-conecta-escuro text-white'
              : 'bg-gray-100 text-gray-500'
          }`}
        >
          {soundEnabled ? (
            <Volume2 className="w-4 h-4" />
          ) : (
            <VolumeX className="w-4 h-4" />
          )}
        </button>
      </div>

      {/* Alerts List */}
      <div className="space-y-3 max-h-96 overflow-y-auto">
        <AnimatePresence mode="popLayout">
          {alerts.length > 0 ? (
            alerts.map((alert) => (
              <AlertItem
                key={alert.id}
                alert={alert}
                onAcknowledge={handleAcknowledge}
                onDismiss={handleDismiss}
              />
            ))
          ) : (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="text-center py-8"
            >
              <Check className="w-12 h-12 text-green-500 mx-auto mb-2" />
              <p className="text-gray-600">Nenhum alerta ativo</p>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}

export default LiveAlerts;
