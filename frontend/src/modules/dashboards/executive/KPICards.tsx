import { motion } from 'framer-motion';
import {
  TrendingUp,
  TrendingDown,
  Minus,
  DollarSign,
  Target,
  Shield,
  Gauge,
} from 'lucide-react';
import {
  LineChart,
  Line,
  ResponsiveContainer,
} from 'recharts';
import { formatCurrency, formatNumber } from '@core/utils/formatters';
import { Skeleton } from '@core/components/feedback';
import type { KPI } from '../types/dashboard.types';

interface KPICardProps {
  kpi: KPI;
  index?: number;
}

const colorClasses: Record<string, { bg: string; text: string; icon: string }> = {
  green: {
    bg: 'bg-green-100',
    text: 'text-green-600',
    icon: 'text-green-600',
  },
  blue: {
    bg: 'bg-blue-100',
    text: 'text-blue-600',
    icon: 'text-blue-600',
  },
  purple: {
    bg: 'bg-purple-100',
    text: 'text-purple-600',
    icon: 'text-purple-600',
  },
  orange: {
    bg: 'bg-orange-100',
    text: 'text-orange-600',
    icon: 'text-orange-600',
  },
  red: {
    bg: 'bg-red-100',
    text: 'text-red-600',
    icon: 'text-red-600',
  },
};

function formatValue(value: number, format: KPI['format']): string {
  switch (format) {
    case 'currency':
      return formatCurrency(value);
    case 'percent':
      return `${formatNumber(value)}%`;
    default:
      return formatNumber(value);
  }
}

function KPICard({ kpi, index = 0 }: KPICardProps) {
  const colors = colorClasses[kpi.color || 'blue'];
  const icons = [DollarSign, Target, Shield, Gauge];
  const Icon = icons[index % icons.length];
  const isPositive = kpi.change >= 0;
  const TrendIcon = kpi.trend === 'up' ? TrendingUp : kpi.trend === 'down' ? TrendingDown : Minus;

  const sparklineData = kpi.sparkline?.map((value, i) => ({ value, index: i })) || [];

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.1 }}
      className="bg-white rounded-xl shadow-card p-6 hover:shadow-lg transition-shadow"
    >
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <p className="text-sm font-medium text-gray-500 mb-1">{kpi.label}</p>
          <p className="text-3xl font-bold text-gray-900">
            {formatValue(kpi.value, kpi.format)}
          </p>

          {/* Change indicator */}
          <div className="flex items-center gap-1.5 mt-2">
            <div
              className={`flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium ${
                isPositive ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
              }`}
            >
              <TrendIcon className="w-3 h-3" />
              {isPositive ? '+' : ''}{kpi.change}%
            </div>
            <span className="text-xs text-gray-500">vs mes anterior</span>
          </div>
        </div>

        {/* Icon */}
        <div className={`p-3 rounded-xl ${colors.bg}`}>
          <Icon className={`w-6 h-6 ${colors.icon}`} />
        </div>
      </div>

      {/* Sparkline */}
      {sparklineData.length > 0 && (
        <div className="mt-4 h-12">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={sparklineData}>
              <Line
                type="monotone"
                dataKey="value"
                stroke={isPositive ? '#22c55e' : '#ef4444'}
                strokeWidth={2}
                dot={false}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}
    </motion.div>
  );
}

interface KPICardsProps {
  kpis: KPI[];
  isLoading?: boolean;
}

export function KPICards({ kpis, isLoading }: KPICardsProps) {
  if (isLoading) {
    return (
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {[1, 2, 3, 4].map((i) => (
          <div key={i} className="bg-white rounded-xl shadow-card p-6">
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <Skeleton height={16} className="w-24 mb-2" />
                <Skeleton height={36} className="w-32 mb-2" />
                <Skeleton height={20} className="w-20" />
              </div>
              <Skeleton width={48} height={48} rounded="lg" />
            </div>
            <Skeleton height={48} className="mt-4" />
          </div>
        ))}
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      {kpis.map((kpi, index) => (
        <KPICard key={kpi.id} kpi={kpi} index={index} />
      ))}
    </div>
  );
}

export default KPICards;
