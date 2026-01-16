import { useQuery } from '@tanstack/react-query';
import { api } from '@core/api';
import type { GovernmentAPI, Obligation, GovernmentStats } from '../types/government.types';

const mockAPIs: GovernmentAPI[] = [
  { id: '1', name: 'Receita Federal', code: 'RFB', description: 'Consulta CNPJ/CPF', status: 'online', lastSync: '2026-01-12T10:00:00Z', successRate: 99.5, icon: 'building' },
  { id: '2', name: 'Portal PNCP', code: 'PNCP', description: 'Licitacoes publicas', status: 'online', lastSync: '2026-01-12T09:00:00Z', successRate: 98.2, icon: 'file-text' },
  { id: '3', name: 'e-Social', code: 'ESOCIAL', description: 'Eventos trabalhistas', status: 'online', lastSync: '2026-01-12T08:00:00Z', successRate: 97.8, icon: 'users' },
  { id: '4', name: 'SEFAZ', code: 'SEFAZ', description: 'Notas fiscais', status: 'online', lastSync: '2026-01-12T07:00:00Z', successRate: 99.1, icon: 'receipt' },
  { id: '5', name: 'CAGED', code: 'CAGED', description: 'Admissoes/demissoes', status: 'online', lastSync: '2026-01-11T18:00:00Z', successRate: 99.8, icon: 'user-plus' },
  { id: '6', name: 'RAIS', code: 'RAIS', description: 'Relacao anual', status: 'manutencao', lastSync: '2026-01-10T12:00:00Z', successRate: 95.0, icon: 'calendar' },
  { id: '7', name: 'FGTS Digital', code: 'FGTS', description: 'Depositos FGTS', status: 'online', lastSync: '2026-01-12T06:00:00Z', successRate: 98.5, icon: 'wallet' },
  { id: '8', name: 'INSS', code: 'INSS', description: 'Contribuicoes previdenciarias', status: 'online', lastSync: '2026-01-12T05:00:00Z', successRate: 99.0, icon: 'shield' },
];

const mockObligations: Obligation[] = [
  { id: '1', name: 'Declaracao RAIS 2025', apiId: '6', apiName: 'RAIS', type: 'anual', deadline: '2026-03-31T23:59:59Z', status: 'pendente', documents: [] },
  { id: '2', name: 'e-Social S-1200 Janeiro', apiId: '3', apiName: 'e-Social', type: 'mensal', deadline: '2026-01-15T23:59:59Z', status: 'enviado', documents: [], submittedAt: '2026-01-10T14:00:00Z' },
  { id: '3', name: 'CAGED Janeiro', apiId: '5', apiName: 'CAGED', type: 'mensal', deadline: '2026-02-07T23:59:59Z', status: 'pendente', documents: [] },
];

const mockStats: GovernmentStats = {
  apisConnected: 7,
  obligationsPending: 5,
  syncSuccess: 98.5,
  nearDeadlines: 2,
};

export function useGovernmentAPIs() {
  return useQuery({
    queryKey: ['government', 'apis'],
    queryFn: async () => {
      try {
        return await api.get<GovernmentAPI[]>('/government-integrations/apis');
      } catch {
        return mockAPIs;
      }
    },
    refetchInterval: 30000,
  });
}

export function useObligations() {
  return useQuery({
    queryKey: ['government', 'obligations'],
    queryFn: async () => {
      try {
        return await api.get<Obligation[]>('/government-integrations/obligations');
      } catch {
        return mockObligations;
      }
    },
  });
}

export function useGovernmentStats() {
  return useQuery({
    queryKey: ['government', 'stats'],
    queryFn: async () => {
      try {
        return await api.get<GovernmentStats>('/government-integrations/stats');
      } catch {
        return mockStats;
      }
    },
  });
}
