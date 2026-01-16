import { useQuery } from '@tanstack/react-query';
import { api } from '@core/api';
import type { BiddingOpportunity, BiddingProposal, BiddingStats } from '../types/bidding.types';

const mockOpportunities: BiddingOpportunity[] = [
  {
    id: '1',
    title: 'Servicos de Limpeza e Conservacao Predial',
    number: 'PE-001/2026',
    organ: 'Prefeitura Municipal de Sao Paulo',
    modalidade: 'pregao',
    status: 'nova',
    value: 1850000,
    publishedAt: '2026-01-10T10:00:00Z',
    deadline: '2026-01-25T14:00:00Z',
    aiScore: 92,
    categories: ['limpeza', 'conservacao'],
    requirements: ['Atestado capacidade tecnica', 'Certidoes negativas', 'Balanco patrimonial'],
    documents: [],
    matchReasons: ['Experiencia em limpeza predial', 'Certificacao ISO 9001', 'Capacidade tecnica comprovada'],
  },
  {
    id: '2',
    title: 'Manutencao Predial Preventiva e Corretiva',
    number: 'CC-012/2026',
    organ: 'Tribunal de Justica do Estado',
    modalidade: 'concorrencia',
    status: 'em_analise',
    value: 3200000,
    publishedAt: '2026-01-08T10:00:00Z',
    deadline: '2026-02-10T10:00:00Z',
    aiScore: 78,
    categories: ['manutencao', 'predial'],
    requirements: ['Atestado tecnico', 'Qualificacao economica', 'Habilitacao juridica'],
    documents: [],
    matchReasons: ['Portfolio similar', 'Equipe tecnica qualificada'],
  },
  {
    id: '3',
    title: 'Vigilancia Patrimonial Armada',
    number: 'PE-045/2026',
    organ: 'Banco do Brasil S.A.',
    modalidade: 'pregao',
    status: 'proposta_enviada',
    value: 4500000,
    publishedAt: '2026-01-05T10:00:00Z',
    deadline: '2026-01-20T09:00:00Z',
    aiScore: 85,
    categories: ['vigilancia', 'seguranca'],
    requirements: ['Autorizacao PF', 'Certificacao vigilancia', 'Seguro responsabilidade'],
    documents: [],
    matchReasons: ['Autorizacao ativa', 'Historico positivo', 'Equipe treinada'],
  },
];

const mockStats: BiddingStats = {
  totalOpportunities: 45,
  proposalsSent: 12,
  winRate: 42,
  avgROI: 18.5,
  totalValue: 12500000,
};

export function useBiddingOpportunities(status?: string) {
  return useQuery({
    queryKey: ['bidding', 'opportunities', status],
    queryFn: async () => {
      try {
        return await api.get<BiddingOpportunity[]>('/bidding/opportunities', { params: { status } });
      } catch {
        if (status) {
          return mockOpportunities.filter(o => o.status === status);
        }
        return mockOpportunities;
      }
    },
  });
}

export function useBiddingStats() {
  return useQuery({
    queryKey: ['bidding', 'stats'],
    queryFn: async () => {
      try {
        return await api.get<BiddingStats>('/bidding/stats');
      } catch {
        return mockStats;
      }
    },
  });
}

export function useBiddingProposals() {
  return useQuery({
    queryKey: ['bidding', 'proposals'],
    queryFn: async () => {
      try {
        return await api.get<BiddingProposal[]>('/bidding/proposals');
      } catch {
        return [];
      }
    },
  });
}
