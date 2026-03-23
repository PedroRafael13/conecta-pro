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
  homologacao: number;
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
    const { data } = await api.get('/api/v1/people-management/operations/postos/posts/stats');
    return data.total ?? data.count ?? 0;
  } catch {
    try {
      const { data } = await api.get('/api/v1/people-management/operations/postos/posts/', {
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
    const { data } = await api.get('/api/v1/people-management/operations/escalas/scales/stats');
    return data.total ?? data.count ?? 0;
  } catch {
    try {
      const { data } = await api.get('/api/v1/people-management/operations/escalas/scales/', {
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
const HOMOLOGACAO_NAMES = [
  'SEFAZ NF-e', 'SEFAZ CT-e', 'SEFAZ MDF-e', 'NFS-e Manaus',
  'eSocial', 'FGTS Digital', 'Simples Nacional', 'Receita Federal',
];

export async function fetchIntegrationSummary(): Promise<IntegrationSummary> {
  try {
    const { data } = await api.get('/api/v1/government/dashboard/status');
    const integrations = data.integrations ?? [];
    let homologacao = 0;
    let realDegraded = 0;
    for (const item of integrations) {
      if (item.status === 'degraded' && HOMOLOGACAO_NAMES.includes(item.name)) {
        homologacao++;
      } else if (item.status === 'degraded') {
        realDegraded++;
      }
    }
    return {
      total: data.total ?? 0,
      online: data.online ?? 0,
      offline: data.offline ?? 0,
      degraded: realDegraded,
      homologacao,
    };
  } catch {
    return { total: 0, online: 0, offline: 0, degraded: 0, homologacao: 0 };
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

export interface CertificateAlert {
  id: string;
  tipo: string;
  nome: string;
  dias_para_vencer: number;
  situacao: string;
  esta_valida: boolean;
  data_validade: string;
}

export interface KitStats {
  total_kits: number;
  kits_ativos: number;
  assignments_pendentes: number;
  taxa_conclusao: number;
}

export interface GedStats {
  total_documents: number;
  pending_approval: number;
  pending_signature: number;
}

export async function fetchCertificateAlerts(): Promise<CertificateAlert[]> {
  try {
    const { data } = await api.get('/api/v1/bidding/certificates');
    const items = Array.isArray(data) ? data : data.items ?? [];
    return items
      .filter((c: CertificateAlert) => c.dias_para_vencer <= 30 || !c.esta_valida)
      .sort((a: CertificateAlert, b: CertificateAlert) => a.dias_para_vencer - b.dias_para_vencer);
  } catch {
    return [];
  }
}

export async function fetchKitStats(): Promise<KitStats> {
  try {
    const { data } = await api.get('/api/v1/document-kits/stats');
    return {
      total_kits: data.total_kits ?? 0,
      kits_ativos: data.kits_ativos ?? 0,
      assignments_pendentes: data.assignments_pendentes ?? 0,
      taxa_conclusao: data.taxa_conclusao ?? 0,
    };
  } catch {
    return { total_kits: 0, kits_ativos: 0, assignments_pendentes: 0, taxa_conclusao: 0 };
  }
}

export async function fetchGedStats(): Promise<GedStats> {
  try {
    const { data } = await api.get('/api/v1/ged/documents/stats/summary');
    return {
      total_documents: data.total_documents ?? 0,
      pending_approval: data.pending_approval ?? 0,
      pending_signature: data.pending_signature ?? 0,
    };
  } catch {
    return { total_documents: 0, pending_approval: 0, pending_signature: 0 };
  }
}

const dashboardStatsService = {
  fetchAllDashboardStats,
  fetchIntegrationSummary,
  fetchRecentActivity,
  fetchCertificateAlerts,
  fetchKitStats,
  fetchGedStats,
};

export default dashboardStatsService;
