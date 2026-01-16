import { useQueryClient } from '@tanstack/react-query';
import { RefreshCw, Calendar, Download } from 'lucide-react';
import { motion } from 'framer-motion';
import { KPICards } from './KPICards';
import { RevenueChart } from './RevenueChart';
import { ComplianceChart } from './ComplianceChart';
import { OperationsChart } from './OperationsChart';
import { ActivityFeed } from './ActivityFeed';
import {
  useKPIs,
  useRevenueChart,
  useComplianceScores,
  useOperationsStatus,
  useRecentActivity,
} from '../hooks/useDashboardData';

export function ExecutiveDashboard() {
  const queryClient = useQueryClient();
  const { kpis, isLoading: kpisLoading } = useKPIs();
  const { chartData, isLoading: chartLoading } = useRevenueChart();
  const { scores, isLoading: scoresLoading } = useComplianceScores();
  const { operations, isLoading: opsLoading } = useOperationsStatus();
  const { activities, isLoading: activityLoading } = useRecentActivity();

  const handleRefresh = () => {
    queryClient.invalidateQueries({ queryKey: ['dashboard'] });
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <h1 className="text-2xl font-bold text-gray-900">Dashboard Executivo</h1>
          <p className="text-gray-600 mt-1">
            Visao geral do desempenho do sistema
          </p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="flex items-center gap-2"
        >
          <button className="btn-ghost flex items-center gap-2">
            <Calendar className="w-4 h-4" />
            <span className="hidden sm:inline">Ultimos 30 dias</span>
          </button>
          <button
            onClick={handleRefresh}
            className="btn-ghost flex items-center gap-2"
          >
            <RefreshCw className="w-4 h-4" />
            <span className="hidden sm:inline">Atualizar</span>
          </button>
          <button className="btn-secondary flex items-center gap-2">
            <Download className="w-4 h-4" />
            <span className="hidden sm:inline">Exportar</span>
          </button>
        </motion.div>
      </div>

      {/* KPI Cards */}
      <KPICards kpis={kpis} isLoading={kpisLoading} />

      {/* Revenue Chart - Full Width */}
      <RevenueChart
        data={chartData}
        isLoading={chartLoading}
        onRefresh={handleRefresh}
      />

      {/* Two Column Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <ComplianceChart scores={scores} isLoading={scoresLoading} />
        <OperationsChart operations={operations} isLoading={opsLoading} />
      </div>

      {/* Activity Feed - Full Width */}
      <ActivityFeed activities={activities} isLoading={activityLoading} />
    </div>
  );
}

export default ExecutiveDashboard;
