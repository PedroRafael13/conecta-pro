import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Users, Zap, Activity, Target, Wifi, WifiOff } from 'lucide-react';
import { useSimulatedWebSocket } from '../hooks/useWebSocket';
import { formatNumber } from '@core/utils/formatters';
import type { RealtimeMetric } from '../types/dashboard.types';

interface MetricCardProps {
  metric: RealtimeMetric;
  animated?: boolean;
}

const iconMap: Record<string, React.ElementType> = {
  users: Users,
  requests: Zap,
  processes: Activity,
  success: Target,
};

const colorClasses: Record<string, string> = {
  green: 'text-green-500 bg-green-100',
  blue: 'text-blue-500 bg-blue-100',
  orange: 'text-orange-500 bg-orange-100',
  purple: 'text-purple-500 bg-purple-100',
};

function MetricCard({ metric, animated }: MetricCardProps) {
  const [displayValue, setDisplayValue] = useState(metric.value);
  const [isAnimating, setIsAnimating] = useState(false);
  const Icon = iconMap[metric.icon] || Activity;

  useEffect(() => {
    if (animated && metric.value !== displayValue) {
      setIsAnimating(true);

      // Animate counter
      const diff = metric.value - displayValue;
      const steps = 20;
      const stepValue = diff / steps;
      let current = displayValue;
      let step = 0;

      const interval = setInterval(() => {
        step++;
        current += stepValue;
        setDisplayValue(Math.round(current));

        if (step >= steps) {
          setDisplayValue(metric.value);
          setIsAnimating(false);
          clearInterval(interval);
        }
      }, 30);

      return () => clearInterval(interval);
    }
  }, [metric.value, displayValue, animated]);

  const formatValue = (value: number): string => {
    switch (metric.format) {
      case 'percent':
        return `${value}%`;
      case 'currency':
        return `R$ ${formatNumber(value)}`;
      default:
        return formatNumber(value);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      className="bg-white rounded-xl shadow-card p-5 relative overflow-hidden"
    >
      {/* Pulse indicator */}
      <div className="absolute top-3 right-3 flex items-center gap-1.5">
        <motion.div
          animate={isAnimating ? { scale: [1, 1.2, 1] } : {}}
          transition={{ repeat: Infinity, duration: 0.5 }}
          className="w-2 h-2 rounded-full bg-green-500"
        />
        <span className="text-xs text-gray-400">LIVE</span>
      </div>

      <div className="flex items-start gap-4">
        <div className={`p-3 rounded-xl ${colorClasses[metric.color]}`}>
          <Icon className="w-6 h-6" />
        </div>
        <div>
          <p className="text-sm text-gray-500">{metric.label}</p>
          <AnimatePresence mode="popLayout">
            <motion.p
              key={displayValue}
              initial={{ y: 10, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              exit={{ y: -10, opacity: 0 }}
              className="text-3xl font-bold text-gray-900 mt-1"
            >
              {formatValue(displayValue)}
            </motion.p>
          </AnimatePresence>
        </div>
      </div>
    </motion.div>
  );
}

export function RealtimeMetrics() {
  const { connected, lastMessage } = useSimulatedWebSocket('metrics');
  const [metrics, setMetrics] = useState<RealtimeMetric[]>([
    { key: 'active_users', label: 'Usuarios Online', value: 47, format: 'number', icon: 'users', color: 'green' },
    { key: 'api_requests', label: 'Requisicoes/min', value: 156, format: 'number', icon: 'requests', color: 'blue' },
    { key: 'active_processes', label: 'Processos Ativos', value: 23, format: 'number', icon: 'processes', color: 'orange' },
    { key: 'success_rate', label: 'Taxa de Sucesso', value: 98, format: 'percent', icon: 'success', color: 'purple' },
  ]);

  // Update metrics when receiving WebSocket messages
  useEffect(() => {
    if (lastMessage?.type === 'metric.update' && lastMessage.data) {
      const { key, value } = lastMessage.data as { key: string; value: number };
      // eslint-disable-next-line react-hooks/set-state-in-effect
      setMetrics((prev) =>
        prev.map((m) => (m.key === key ? { ...m, value } : m))
      );
    }
  }, [lastMessage]);

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">Metricas em Tempo Real</h3>
          <p className="text-sm text-gray-500">Atualizacoes automaticas via WebSocket</p>
        </div>
        <div
          className={`flex items-center gap-2 px-3 py-1.5 rounded-full text-sm ${
            connected
              ? 'bg-green-100 text-green-700'
              : 'bg-red-100 text-red-700'
          }`}
        >
          {connected ? (
            <Wifi className="w-4 h-4" />
          ) : (
            <WifiOff className="w-4 h-4" />
          )}
          {connected ? 'Conectado' : 'Desconectado'}
        </div>
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {metrics.map((metric) => (
          <MetricCard key={metric.key} metric={metric} animated />
        ))}
      </div>
    </div>
  );
}

export default RealtimeMetrics;
