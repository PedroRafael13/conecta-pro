import { motion } from 'framer-motion';
import { TrendingUp, TrendingDown, Minus, Lightbulb, ArrowRight } from 'lucide-react';
import { Skeleton } from '@core/components/feedback';
import type { TrendData } from '../types/dashboard.types';

interface TrendAnalysisProps {
  trends: TrendData[];
  isLoading?: boolean;
}

const directionConfig = {
  up: {
    icon: TrendingUp,
    color: 'text-green-600',
    bg: 'bg-green-100',
    badge: 'bg-green-100 text-green-700',
  },
  down: {
    icon: TrendingDown,
    color: 'text-red-600',
    bg: 'bg-red-100',
    badge: 'bg-red-100 text-red-700',
  },
  stable: {
    icon: Minus,
    color: 'text-gray-600',
    bg: 'bg-gray-100',
    badge: 'bg-gray-100 text-gray-700',
  },
};

const significanceLabels = {
  low: 'Baixa',
  medium: 'Media',
  high: 'Alta',
};

function TrendCard({ trend, index }: { trend: TrendData; index: number }) {
  const config = directionConfig[trend.direction];
  const Icon = config.icon;

  return (
    <motion.div
      initial={{ opacity: 0, x: -10 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: index * 0.1 }}
      className="border border-gray-200 rounded-lg p-4 hover:border-conecta-escuro/30 transition-colors"
    >
      <div className="flex items-start justify-between">
        <div className="flex items-center gap-3">
          <div className={`p-2 rounded-lg ${config.bg}`}>
            <Icon className={`w-5 h-5 ${config.color}`} />
          </div>
          <div>
            <h4 className="font-medium text-gray-900">{trend.metric}</h4>
            <p className="text-xs text-gray-500">{trend.period}</p>
          </div>
        </div>
        <div className="text-right">
          <p className={`text-xl font-bold ${config.color}`}>
            {trend.change > 0 ? '+' : ''}{trend.change}%
          </p>
          <span className={`text-xs px-2 py-0.5 rounded-full ${config.badge}`}>
            Significancia: {significanceLabels[trend.significance]}
          </span>
        </div>
      </div>

      {/* Insight */}
      <div className="mt-4 flex items-start gap-2 p-3 bg-blue-50 rounded-lg">
        <Lightbulb className="w-4 h-4 text-blue-500 flex-shrink-0 mt-0.5" />
        <p className="text-sm text-blue-700">{trend.insight}</p>
      </div>

      <button className="mt-3 text-sm text-conecta-escuro hover:text-conecta-medio flex items-center gap-1 w-full justify-end">
        Ver analise detalhada
        <ArrowRight className="w-4 h-4" />
      </button>
    </motion.div>
  );
}

export function TrendAnalysis({ trends, isLoading }: TrendAnalysisProps) {
  if (isLoading) {
    return (
      <div className="bg-white rounded-xl shadow-card p-6">
        <Skeleton height={24} className="w-48 mb-4" />
        <div className="space-y-4">
          {[1, 2].map((i) => (
            <Skeleton key={i} height={150} />
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl shadow-card p-6 h-full">
      <div className="flex items-center gap-2 mb-4">
        <TrendingUp className="w-5 h-5 text-conecta-escuro" />
        <h3 className="text-lg font-semibold text-gray-900">Analise de Tendencias</h3>
      </div>

      {trends.length > 0 ? (
        <div className="space-y-4">
          {trends.map((trend, index) => (
            <TrendCard key={trend.id} trend={trend} index={index} />
          ))}
        </div>
      ) : (
        <div className="text-center py-12">
          <Minus className="w-12 h-12 text-gray-400 mx-auto mb-3" />
          <p className="text-gray-600">Nenhuma tendencia significativa</p>
          <p className="text-sm text-gray-500 mt-1">
            Aguarde mais dados para analise de tendencias
          </p>
        </div>
      )}
    </div>
  );
}

export default TrendAnalysis;
