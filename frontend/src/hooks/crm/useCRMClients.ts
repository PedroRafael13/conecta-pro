/**
 * Hook para clientes CRM — usa /api/v1/crm/clients/ (com MRR e lead_source)
 */
import { useQuery } from '@tanstack/react-query';
import { customInstance } from '@/lib/api-client';

interface CRMClient {
  id: string;
  code: string;
  name: string;
  trading_name: string | null;
  cnpj: string;
  email: string;
  phone: string | null;
  mobile: string | null;
  endereco: {
    rua: string | null;
    numero: string | null;
    bairro: string | null;
    cidade: string | null;
    estado: string | null;
    cep: string | null;
  };
  status: string;
  segment: string | null;
  contract_start_date: string | null;
  health_score: number | null;
  satisfaction_score: number | null;
  total_revenue: number;
  total_debt: number;
  is_defaulter: boolean;
  is_vip: boolean;
  crm_origin: string | null;
  lead_id: string | null;
  lead_name: string | null;
  lead_source: string | null;
  mrr: number;
  contratos_ativos: number;
  created_at: string | null;
}

interface CRMClientsResponse {
  items: CRMClient[];
  total: number;
  gerado_em: string;
}

interface CRMClientResumo {
  clientes_ativos: number;
  clientes_inativos: number;
  inadimplentes: number;
  vip: number;
  originados_crm: number;
  mrr_total: number;
  segmentos: number;
  gerado_em: string;
}

export function useCRMClients(filters?: { status?: string; segment?: string }) {
  return useQuery<CRMClientsResponse>({
    queryKey: ['crm-clients', filters],
    queryFn: async () => {
      const params = new URLSearchParams();
      if (filters?.status) params.set('status', filters.status);
      if (filters?.segment) params.set('segment', filters.segment);
      const qs = params.toString() ? `?${params.toString()}` : '';
      return customInstance<CRMClientsResponse>({
        url: `/api/v1/crm/clients/${qs}`,
        method: 'GET',
      });
    },
    staleTime: 30_000,
  });
}

export function useCRMClientResumo() {
  return useQuery<CRMClientResumo>({
    queryKey: ['crm-clients-resumo'],
    queryFn: () =>
      customInstance<CRMClientResumo>({
        url: '/api/v1/crm/clients/resumo',
        method: 'GET',
      }),
    staleTime: 60_000,
  });
}

export function useCRMClientDetalhe(clientId: string) {
  return useQuery({
    queryKey: ['crm-client', clientId],
    queryFn: () =>
      customInstance({
        url: `/api/v1/crm/clients/${clientId}`,
        method: 'GET',
      }),
    enabled: !!clientId,
    staleTime: 30_000,
  });
}

export type { CRMClient, CRMClientsResponse, CRMClientResumo };
