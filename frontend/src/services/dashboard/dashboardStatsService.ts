/**
 * Dashboard Stats Service
 *
 * Busca dados reais do backend para o dashboard principal.
 */

import api from '@/lib/api';

export interface DashboardStats {
  employees: number;
  active_posts: number;
  clients: number;
  scales: number;
}

export interface IntegrationSummary {
  total: number;
  online: number;
  offline: number;
  degraded: number;
}

export interface RecentActivityItem {
  id: string;
  type: string;
  description: string;
  timestamp: string;
  module?: string;
}

/**
 * Busca contagem real de colaboradores
 */
async function fetchEmployeeCount(): Promise<number> {
  try {
    const { data } = await api.get('/api/v1/operacional/employees/', {
      params: { page: 1, page_size: 1 },
    });
    return data.total ?? data.count ?? 0;
  } catch {
    return 0;
  }
}

/**
 * Busca contagem real de postos ativos
 */
async function fetchPostCount(): Promise<number> {
  try {
    const { data } = await api.get('/api/v1/operacional/postos/stats');
    return data.total ?? data.count ?? 0;
  } catch {
    try {
      const { data } = await api.get('/api/v1/operacional/postos/', {
        params: { page: 1, page_size: 1 },
      });
      return data.total ?? data.count ?? 0;
    } catch {
      return 0;
    }
  }
}

/**
 * Busca contagem real de clientes
 */
async function fetchClientCount(): Promise<number> {
  try {
    const { data } = await api.get('/api/v1/clients/stats');
    return data.total_clients ?? data.total ?? data.count ?? 0;
  } catch {
    try {
      const { data } = await api.get('/api/v1/clients/', {
        params: { page: 1, page_size: 1 },
      });
      return data.total ?? data.count ?? 0;
    } catch {
      return 0;
    }
  }
}

/**
 * Busca contagem real de escalas
 */
async function fetchScaleCount(): Promise<number> {
  try {
    const { data } = await api.get('/api/v1/operacional/escalas/stats');
    return data.total ?? data.count ?? 0;
  } catch {
    try {
      const { data } = await api.get('/api/v1/operacional/escalas/', {
        params: { page: 1, page_size: 1 },
      });
      return data.total ?? data.count ?? 0;
    } catch {
      return 0;
    }
  }
}

/**
 * Busca todas as stats do dashboard em paralelo
 */
export async function fetchAllDashboardStats(): Promise<DashboardStats> {
  const [employees, active_posts, clients, scales] = await Promise.all([
    fetchEmployeeCount(),
    fetchPostCount(),
    fetchClientCount(),
    fetchScaleCount(),
  ]);
  return { employees, active_posts, clients, scales };
}

/**
 * Busca resumo das integrações
 */
export async function fetchIntegrationSummary(): Promise<IntegrationSummary> {
  try {
    const { data } = await api.get('/api/v1/government/dashboard/status');
    return {
      total: data.total ?? 0,
      online: data.online ?? 0,
      offline: data.offline ?? 0,
      degraded: data.degraded ?? 0,
    };
  } catch {
    return { total: 0, online: 0, offline: 0, degraded: 0 };
  }
}

/**
 * Busca atividade recente do dashboard operacional
 */
export async function fetchRecentActivity(): Promise<RecentActivityItem[]> {
  try {
    const { data } = await api.get('/api/v1/operacional/dashboard');
    return data.recent_activity ?? data.activities ?? [];
  } catch {
    return [];
  }
}

const dashboardStatsService = {
  fetchAllDashboardStats,
  fetchIntegrationSummary,
  fetchRecentActivity,
};

export default dashboardStatsService;
