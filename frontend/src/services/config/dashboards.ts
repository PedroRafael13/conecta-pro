/**
 * Service Layer - Dashboards
 * Dashboards de configurações e tenant
 */

import { axiosInstance } from '@/lib/axios-instance';
import type {
  ConfigDashboard,
  TenantDashboard,
} from '@/types/generated/config/conectaPROCONFIGModuleAPI.schemas';

const BASE_PATH = '/api/v1/config';

/**
 * Obtém dashboard geral de configurações
 */
export const getConfigDashboard = async (): Promise<ConfigDashboard> => {
  const { data } = await axiosInstance.get<ConfigDashboard>(
    `${BASE_PATH}/dashboard`
  );
  return data;
};

/**
 * Obtém dashboard de tenant específico
 */
export const getTenantDashboard = async (
  tenantId: string
): Promise<TenantDashboard> => {
  const { data } = await axiosInstance.get<TenantDashboard>(
    `${BASE_PATH}/tenants/${tenantId}/dashboard`
  );
  return data;
};

// ==================== Helpers - Config Dashboard ====================

/**
 * Calcula percentual de uso (exemplo)
 */
export const calculateUsagePercentage = (
  used: number,
  total: number
): number => {
  if (total === 0) return 0;
  return Math.round((used / total) * 100);
};

/**
 * Formata números grandes
 */
export const formatLargeNumber = (num: number): string => {
  if (num >= 1000000) {
    return `${(num / 1000000).toFixed(1)}M`;
  }
  if (num >= 1000) {
    return `${(num / 1000).toFixed(1)}K`;
  }
  return num.toString();
};

/**
 * Obtém cor do indicador baseado em percentual
 */
export const getIndicatorColor = (percentage: number): string => {
  if (percentage >= 90) return 'red';
  if (percentage >= 70) return 'yellow';
  return 'green';
};

// ==================== Helpers - Tenant Dashboard ====================

/**
 * Calcula taxa de crescimento
 */
export const calculateGrowthRate = (
  current: number,
  previous: number
): number => {
  if (previous === 0) return 0;
  return Math.round(((current - previous) / previous) * 100);
};

/**
 * Formata taxa de crescimento
 */
export const formatGrowthRate = (rate: number): string => {
  const sign = rate >= 0 ? '+' : '';
  return `${sign}${rate}%`;
};

/**
 * Obtém status de saúde do tenant
 */
export const getTenantHealthStatus = (
  dashboard: TenantDashboard
): 'healthy' | 'warning' | 'critical' => {
  // Lógica customizável baseada em métricas
  const issues: number[] = [];

  // Exemplo: verificar métricas críticas
  // if (dashboard.some_metric > threshold) issues.push(1);

  if (issues.length === 0) return 'healthy';
  if (issues.length <= 2) return 'warning';
  return 'critical';
};

/**
 * Obtém label do status de saúde
 */
export const getHealthStatusLabel = (
  status: 'healthy' | 'warning' | 'critical'
): string => {
  const labels = {
    healthy: 'Saudável',
    warning: 'Atenção',
    critical: 'Crítico',
  };
  return labels[status];
};

/**
 * Obtém cor do status de saúde
 */
export const getHealthStatusColor = (
  status: 'healthy' | 'warning' | 'critical'
): string => {
  const colors = {
    healthy: 'green',
    warning: 'yellow',
    critical: 'red',
  };
  return colors[status];
};

// ==================== Agregações e Estatísticas ====================

export interface DashboardSummary {
  total_items: number;
  active_items: number;
  inactive_items: number;
  usage_percentage: number;
  health_status: 'healthy' | 'warning' | 'critical';
}

/**
 * Gera resumo do dashboard
 */
export const generateDashboardSummary = (
  dashboard: ConfigDashboard | TenantDashboard
): DashboardSummary => {
  // Implementação genérica - ajustar baseado na estrutura real
  return {
    total_items: 0,
    active_items: 0,
    inactive_items: 0,
    usage_percentage: 0,
    health_status: 'healthy',
  };
};

/**
 * Compara dashboards (atual vs anterior)
 */
export interface DashboardComparison {
  metric: string;
  current: number;
  previous: number;
  change: number;
  change_percentage: number;
  trend: 'up' | 'down' | 'stable';
}

export const compareDashboards = (
  current: any,
  previous: any,
  metrics: string[]
): DashboardComparison[] => {
  return metrics.map((metric) => {
    const currentValue = current[metric] || 0;
    const previousValue = previous[metric] || 0;
    const change = currentValue - previousValue;
    const changePercentage = calculateGrowthRate(currentValue, previousValue);

    let trend: 'up' | 'down' | 'stable' = 'stable';
    if (change > 0) trend = 'up';
    else if (change < 0) trend = 'down';

    return {
      metric,
      current: currentValue,
      previous: previousValue,
      change,
      change_percentage: changePercentage,
      trend,
    };
  });
};

/**
 * Obtém ícone da tendência
 */
export const getTrendIcon = (trend: 'up' | 'down' | 'stable'): string => {
  const icons = {
    up: '📈',
    down: '📉',
    stable: '➡️',
  };
  return icons[trend];
};

/**
 * Obtém cor da tendência (contexto positivo)
 */
export const getTrendColor = (
  trend: 'up' | 'down' | 'stable',
  isPositive: boolean = true
): string => {
  if (trend === 'stable') return 'gray';
  if (isPositive) {
    return trend === 'up' ? 'green' : 'red';
  } else {
    return trend === 'up' ? 'red' : 'green';
  }
};

// ==================== Export de Dados ====================

/**
 * Exporta dashboard como JSON
 */
export const exportDashboardAsJSON = (
  dashboard: ConfigDashboard | TenantDashboard
): string => {
  return JSON.stringify(dashboard, null, 2);
};

/**
 * Exporta dashboard como CSV (simples)
 */
export const exportDashboardAsCSV = (data: Record<string, any>): string => {
  const headers = Object.keys(data);
  const values = Object.values(data);

  return `${headers.join(',')}\n${values.join(',')}`;
};
