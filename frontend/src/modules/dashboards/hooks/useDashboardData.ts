import { useQuery } from '@tanstack/react-query';
import { api } from '@core/api';
import type {
  KPI,
  RevenueChartData,
  ComplianceScore,
  OperationStatus,
  Activity,
  DashboardFilters,
  PredictiveData,
  AnomalyData,
  TrendData,
} from '../types/dashboard.types';

interface ExecutiveDashboardData {
  kpis: KPI[];
  revenueChart: RevenueChartData[];
  complianceScores: ComplianceScore[];
  operationsStatus: OperationStatus[];
  recentActivity: Activity[];
}

interface AnalyticsDashboardData {
  predictions: PredictiveData[];
  anomalies: AnomalyData[];
  trends: TrendData[];
}

// Mock data for development
const mockExecutiveData: ExecutiveDashboardData = {
  kpis: [
    {
      id: '1',
      label: 'Receita Mensal',
      value: 284500,
      format: 'currency',
      change: 12.5,
      trend: 'up',
      sparkline: [45, 52, 48, 55, 62, 58, 65, 72, 68, 75, 82, 78],
      color: 'green',
    },
    {
      id: '2',
      label: 'ROI Medio',
      value: 24.8,
      format: 'percent',
      change: 4.2,
      trend: 'up',
      sparkline: [18, 20, 19, 22, 21, 23, 24, 23, 25, 24, 26, 25],
      color: 'blue',
    },
    {
      id: '3',
      label: 'Compliance Score',
      value: 94,
      format: 'percent',
      change: 2.1,
      trend: 'up',
      sparkline: [85, 86, 88, 87, 90, 91, 92, 91, 93, 92, 94, 94],
      color: 'purple',
    },
    {
      id: '4',
      label: 'Eficiencia Operacional',
      value: 87.3,
      format: 'percent',
      change: -1.5,
      trend: 'down',
      sparkline: [82, 84, 83, 86, 85, 88, 87, 89, 88, 90, 88, 87],
      color: 'orange',
    },
  ],
  revenueChart: [
    { date: '2025-01', revenue: 185000, forecast: 180000, label: 'Jan' },
    { date: '2025-02', revenue: 195000, forecast: 190000, label: 'Fev' },
    { date: '2025-03', revenue: 210000, forecast: 205000, label: 'Mar' },
    { date: '2025-04', revenue: 225000, forecast: 220000, label: 'Abr' },
    { date: '2025-05', revenue: 240000, forecast: 235000, label: 'Mai' },
    { date: '2025-06', revenue: 255000, forecast: 250000, label: 'Jun' },
    { date: '2025-07', revenue: 268000, forecast: 265000, label: 'Jul' },
    { date: '2025-08', revenue: 275000, forecast: 280000, label: 'Ago' },
    { date: '2025-09', revenue: 282000, forecast: 290000, label: 'Set' },
    { date: '2025-10', revenue: 290000, forecast: 300000, label: 'Out' },
    { date: '2025-11', revenue: 285000, forecast: 310000, label: 'Nov' },
    { date: '2025-12', revenue: 284500, forecast: 320000, label: 'Dez' },
  ],
  complianceScores: [
    { category: 'lgpd', score: 96, color: '#22c55e', label: 'LGPD' },
    { category: 'audit', score: 92, color: '#3b82f6', label: 'Auditoria' },
    { category: 'gov', score: 88, color: '#f97316', label: 'Governamental' },
  ],
  operationsStatus: [
    { module: 'GED', status: 'ok', percentage: 95, label: 'GED - Documentos' },
    { module: 'CRM', status: 'ok', percentage: 88, label: 'CRM - Vendas' },
    { module: 'Field', status: 'warning', percentage: 72, label: 'Servico de Campo' },
    { module: 'Finance', status: 'ok', percentage: 91, label: 'Financeiro' },
    { module: 'HR', status: 'critical', percentage: 45, label: 'RH' },
  ],
  recentActivity: [
    {
      id: '1',
      user: { name: 'Maria Silva' },
      action: 'aprovou documento',
      target: 'Contrato #2847',
      timestamp: new Date(Date.now() - 5 * 60 * 1000).toISOString(),
      type: 'success',
    },
    {
      id: '2',
      user: { name: 'Joao Santos' },
      action: 'detectou anomalia',
      target: 'Modulo Financeiro',
      timestamp: new Date(Date.now() - 15 * 60 * 1000).toISOString(),
      type: 'warning',
    },
    {
      id: '3',
      user: { name: 'Ana Costa' },
      action: 'criou proposta',
      target: 'Cliente XYZ',
      timestamp: new Date(Date.now() - 30 * 60 * 1000).toISOString(),
      type: 'info',
    },
    {
      id: '4',
      user: { name: 'Pedro Lima' },
      action: 'finalizou auditoria',
      target: 'Q4 2025',
      timestamp: new Date(Date.now() - 45 * 60 * 1000).toISOString(),
      type: 'success',
    },
    {
      id: '5',
      user: { name: 'Sistema' },
      action: 'backup concluido',
      timestamp: new Date(Date.now() - 60 * 60 * 1000).toISOString(),
      type: 'info',
    },
  ],
};

const mockAnalyticsData: AnalyticsDashboardData = {
  predictions: [
    { date: '2026-01', actual: 290000, predicted: 295000, lowerBound: 280000, upperBound: 310000 },
    { date: '2026-02', predicted: 305000, lowerBound: 290000, upperBound: 320000 },
    { date: '2026-03', predicted: 318000, lowerBound: 300000, upperBound: 336000 },
  ],
  anomalies: [
    {
      id: '1',
      metric: 'Taxa de Conversao',
      value: 12.3,
      expected: 24.5,
      deviation: -49.8,
      severity: 'high',
      timestamp: new Date().toISOString(),
      description: 'Queda significativa na taxa de conversao do CRM',
    },
    {
      id: '2',
      metric: 'Tempo Resposta API',
      value: 850,
      expected: 200,
      deviation: 325,
      severity: 'medium',
      timestamp: new Date().toISOString(),
      description: 'Latencia elevada no endpoint de documentos',
    },
  ],
  trends: [
    {
      id: '1',
      metric: 'Receita',
      direction: 'up',
      change: 15.2,
      period: 'ultimos 3 meses',
      significance: 'high',
      insight: 'Crescimento consistente impulsionado por novos contratos',
    },
    {
      id: '2',
      metric: 'Compliance',
      direction: 'stable',
      change: 1.2,
      period: 'ultimo mes',
      significance: 'medium',
      insight: 'Score de compliance estavel com pequenas melhorias em LGPD',
    },
  ],
};

export function useDashboardData(type: 'executive' | 'analytics', filters?: DashboardFilters) {
  return useQuery({
    queryKey: ['dashboard', type, filters],
    queryFn: async () => {
      try {
        const endpoint = type === 'executive'
          ? '/dashboard/executive'
          : '/analytics/dashboard';

        const response = await api.get<ExecutiveDashboardData | AnalyticsDashboardData>(
          endpoint,
          { params: filters }
        );
        return response;
      } catch {
        // Return mock data in development
        return type === 'executive' ? mockExecutiveData : mockAnalyticsData;
      }
    },
    staleTime: 1000 * 60 * 5, // 5 minutes
    refetchInterval: 1000 * 60, // Refresh every minute
  });
}

export function useKPIs() {
  const { data, isLoading, error } = useDashboardData('executive');
  return {
    kpis: (data as ExecutiveDashboardData)?.kpis || [],
    isLoading,
    error,
  };
}

export function useRevenueChart() {
  const { data, isLoading, error } = useDashboardData('executive');
  return {
    chartData: (data as ExecutiveDashboardData)?.revenueChart || [],
    isLoading,
    error,
  };
}

export function useComplianceScores() {
  const { data, isLoading, error } = useDashboardData('executive');
  return {
    scores: (data as ExecutiveDashboardData)?.complianceScores || [],
    isLoading,
    error,
  };
}

export function useOperationsStatus() {
  const { data, isLoading, error } = useDashboardData('executive');
  return {
    operations: (data as ExecutiveDashboardData)?.operationsStatus || [],
    isLoading,
    error,
  };
}

export function useRecentActivity() {
  const { data, isLoading, error } = useDashboardData('executive');
  return {
    activities: (data as ExecutiveDashboardData)?.recentActivity || [],
    isLoading,
    error,
  };
}

export function useAnalytics(filters?: DashboardFilters) {
  const { data, isLoading, error } = useDashboardData('analytics', filters);
  const analyticsData = data as AnalyticsDashboardData;

  return {
    predictions: analyticsData?.predictions || [],
    anomalies: analyticsData?.anomalies || [],
    trends: analyticsData?.trends || [],
    isLoading,
    error,
  };
}

export default useDashboardData;
