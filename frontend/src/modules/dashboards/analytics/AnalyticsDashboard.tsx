import { useState, useMemo } from 'react';
import { motion } from 'framer-motion';
import { Calendar, Filter, Download, RefreshCw, Brain } from 'lucide-react';
import { PredictiveChart } from './PredictiveChart';
import { AnomalyDetection } from './AnomalyDetection';
import { TrendAnalysis } from './TrendAnalysis';
import { useAnalytics } from '../hooks/useDashboardData';
import type { DashboardFilters } from '../types/dashboard.types';

const dateRangeOptions = [
  { value: '7d', label: 'Ultimos 7 dias' },
  { value: '30d', label: 'Ultimos 30 dias' },
  { value: '90d', label: 'Ultimos 90 dias' },
  { value: '1y', label: 'Ultimo ano' },
];

const moduleOptions = [
  { value: 'all', label: 'Todos os modulos' },
  { value: 'crm', label: 'CRM' },
  { value: 'finance', label: 'Financeiro' },
  { value: 'operations', label: 'Operacoes' },
  { value: 'compliance', label: 'Compliance' },
];

export function AnalyticsDashboard() {
  const [dateRange, setDateRange] = useState('30d');
  const [selectedModule, setSelectedModule] = useState('all');

  const filters: DashboardFilters = useMemo(() => ({
    dateRange: {
      start: new Date(new Date().getTime() - 30 * 24 * 60 * 60 * 1000).toISOString(),
      end: new Date().toISOString(),
    },
    modules: selectedModule === 'all' ? undefined : [selectedModule],
  }), [selectedModule]);

  const { predictions, anomalies, trends, isLoading } = useAnalytics(filters);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <div className="flex items-center gap-2">
            <Brain className="w-7 h-7 text-conecta-laranja" />
            <h1 className="text-2xl font-bold text-gray-900">Analytics Avancado</h1>
          </div>
          <p className="text-gray-600 mt-1">
            Analises preditivas e deteccao de anomalias com IA
          </p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="flex items-center gap-2 flex-wrap"
        >
          {/* Date Range Select */}
          <div className="relative">
            <select
              value={dateRange}
              onChange={(e) => setDateRange(e.target.value)}
              className="appearance-none bg-white border border-gray-300 rounded-lg px-4 py-2 pr-8 text-sm focus:outline-none focus:ring-2 focus:ring-conecta-escuro"
            >
              {dateRangeOptions.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
            <Calendar className="w-4 h-4 text-gray-400 absolute right-2 top-1/2 -translate-y-1/2 pointer-events-none" />
          </div>

          {/* Module Select */}
          <div className="relative">
            <select
              value={selectedModule}
              onChange={(e) => setSelectedModule(e.target.value)}
              className="appearance-none bg-white border border-gray-300 rounded-lg px-4 py-2 pr-8 text-sm focus:outline-none focus:ring-2 focus:ring-conecta-escuro"
            >
              {moduleOptions.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
            <Filter className="w-4 h-4 text-gray-400 absolute right-2 top-1/2 -translate-y-1/2 pointer-events-none" />
          </div>

          <button className="btn-ghost flex items-center gap-2">
            <RefreshCw className="w-4 h-4" />
          </button>

          <button className="btn-secondary flex items-center gap-2">
            <Download className="w-4 h-4" />
            <span className="hidden sm:inline">Exportar</span>
          </button>
        </motion.div>
      </div>

      {/* AI Model Info */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="bg-gradient-to-r from-conecta-escuro to-conecta-medio rounded-xl p-4 text-white"
      >
        <div className="flex items-center justify-between flex-wrap gap-4">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-white/10 rounded-lg">
              <Brain className="w-6 h-6" />
            </div>
            <div>
              <p className="font-medium">Modelo de IA: Conecta PRO ML v2.0</p>
              <p className="text-sm text-white/70">
                Ultima atualizacao: hoje as 14:30
              </p>
            </div>
          </div>
          <div className="flex items-center gap-6 text-sm">
            <div>
              <p className="text-white/70">Precisao</p>
              <p className="font-semibold text-lg">95.2%</p>
            </div>
            <div>
              <p className="text-white/70">Dados Processados</p>
              <p className="font-semibold text-lg">2.4M</p>
            </div>
            <div>
              <p className="text-white/70">Anomalias Detectadas</p>
              <p className="font-semibold text-lg">{anomalies.length}</p>
            </div>
          </div>
        </div>
      </motion.div>

      {/* Predictive Chart - Full Width */}
      <PredictiveChart data={predictions} isLoading={isLoading} />

      {/* Two Column Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <AnomalyDetection anomalies={anomalies} isLoading={isLoading} />
        <TrendAnalysis trends={trends} isLoading={isLoading} />
      </div>
    </div>
  );
}

export default AnalyticsDashboard;
