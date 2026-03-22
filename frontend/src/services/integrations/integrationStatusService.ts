/**
 * Integration Status Service
 *
 * Consulta status real de TODAS as integrações externas do sistema.
 */

import api from '@/lib/api';

export interface IntegrationStatusItem {
  id: string;
  name: string;
  category: 'banking' | 'government' | 'hr';
  status: 'online' | 'offline' | 'degraded' | 'homologacao';
  description: string;
  last_check: string | null;
  last_sync: string | null;
  response_time_ms: number | null;
  error_message: string | null;
}

export interface IntegrationStatusResponse {
  total: number;
  online: number;
  offline: number;
  degraded: number;
  homologacao: number;
  integrations: IntegrationStatusItem[];
  checked_at: string;
}

/**
 * Integrações governamentais em homologação (tpAmb=2).
 * São "degraded" no backend mas na verdade estão em ambiente de teste.
 */
const HOMOLOGACAO_NAMES = [
  'SEFAZ NF-e', 'SEFAZ CT-e', 'SEFAZ MDF-e', 'NFS-e Manaus',
  'eSocial', 'FGTS Digital', 'Simples Nacional', 'Receita Federal',
];

/**
 * Busca status de todas as integrações
 */
export async function fetchIntegrationStatus(): Promise<IntegrationStatusResponse> {
  const { data } = await api.get<IntegrationStatusResponse>(
    '/api/v1/government/dashboard/status'
  );

  // Reclassificar integrações gov em homologação de "degraded" para "homologacao"
  let homologacaoCount = 0;
  let realDegraded = 0;

  const integrations = data.integrations.map((item) => {
    if (item.status === 'degraded' && HOMOLOGACAO_NAMES.includes(item.name)) {
      homologacaoCount++;
      return { ...item, status: 'homologacao' as const, error_message: 'Ambiente de homologação (tpAmb=2)' };
    }
    if (item.status === 'degraded') {
      realDegraded++;
    }
    return item;
  });

  return {
    ...data,
    integrations,
    degraded: realDegraded,
    homologacao: homologacaoCount,
  };
}

/**
 * Busca dashboard completo de monitoramento governamental
 */
export async function fetchGovernmentDashboard(dias: number = 7) {
  const { data } = await api.get('/api/v1/government/dashboard/', { params: { dias } });
  return data;
}

/**
 * Busca métricas detalhadas
 */
export async function fetchGovernmentMetrics(dias: number = 30) {
  const { data } = await api.get('/api/v1/government/dashboard/metricas', { params: { dias } });
  return data;
}

/**
 * Busca alertas de certificados
 */
export async function fetchCertificateAlerts() {
  const { data } = await api.get('/api/v1/government/dashboard/certificados/alertas');
  return data;
}

/**
 * Busca eventos recentes
 */
export async function fetchRecentEvents(limite: number = 20) {
  const { data } = await api.get('/api/v1/government/dashboard/eventos', { params: { limite } });
  return data;
}

const integrationStatusService = {
  fetchIntegrationStatus,
  fetchGovernmentDashboard,
  fetchGovernmentMetrics,
  fetchCertificateAlerts,
  fetchRecentEvents,
};

export default integrationStatusService;
