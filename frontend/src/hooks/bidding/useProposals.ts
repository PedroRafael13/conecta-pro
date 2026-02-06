'use client';

/**
 * Hooks React Query - Proposals (Propostas)
 *
 * Hooks para gestão de propostas comerciais de licitação
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { toast } from 'sonner';
import proposalsService, {
  type ListProposalsParams,
  type SubmeterPropostaParams,
  type AlterarStatusPropostaParams,
  type BiddingProposalCreate,
  type BiddingProposalUpdate,
  type ProposalItemCreate,
} from '@/services/bidding/proposals.service';

const QUERY_KEYS = {
  all: ['bidding', 'proposals'] as const,
  lists: () => [...QUERY_KEYS.all, 'list'] as const,
  list: (params?: ListProposalsParams) => [...QUERY_KEYS.lists(), params] as const,
  details: () => [...QUERY_KEYS.all, 'detail'] as const,
  detail: (id: string) => [...QUERY_KEYS.details(), id] as const,
  items: (proposalId: string) => [...QUERY_KEYS.detail(proposalId), 'items'] as const,
  tender: (tenderId: string, params?: any) =>
    [...QUERY_KEYS.all, 'tender', tenderId, params] as const,
  emAndamento: (params?: any) =>
    [...QUERY_KEYS.all, 'em-andamento', params] as const,
  aprovadas: (params?: any) => [...QUERY_KEYS.all, 'aprovadas', params] as const,
  dashboard: (params?: any) => [...QUERY_KEYS.all, 'dashboard', params] as const,
};

/**
 * Hook para listar propostas com filtros
 */
export function useListarPropostas(params?: ListProposalsParams) {
  return useQuery({
    queryKey: QUERY_KEYS.list(params),
    queryFn: () => proposalsService.listarPropostas(params),
    staleTime: 1000 * 60 * 5,
  });
}

/**
 * Hook para buscar proposta por ID
 */
export function useBuscarProposta(proposalId: string, enabled = true) {
  return useQuery({
    queryKey: QUERY_KEYS.detail(proposalId),
    queryFn: () => proposalsService.buscarPropostaPorId(proposalId),
    enabled: enabled && !!proposalId,
    staleTime: 1000 * 60 * 5,
  });
}

/**
 * Hook para criar nova proposta
 */
export function useCriarProposta() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (payload: BiddingProposalCreate) =>
      proposalsService.criarProposta(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.lists() });
      toast.success('Proposta criada com sucesso');
    },
    onError: (error: any) => {
      toast.error(error?.response?.data?.detail || 'Erro ao criar proposta');
    },
  });
}

/**
 * Hook para atualizar proposta
 */
export function useAtualizarProposta() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: BiddingProposalUpdate }) =>
      proposalsService.atualizarProposta(id, data),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.lists() });
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.detail(data.id) });
      toast.success('Proposta atualizada com sucesso');
    },
    onError: (error: any) => {
      toast.error(
        error?.response?.data?.detail || 'Erro ao atualizar proposta'
      );
    },
  });
}

/**
 * Hook para remover proposta
 */
export function useRemoverProposta() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (proposalId: string) =>
      proposalsService.removerProposta(proposalId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.lists() });
      toast.success('Proposta removida com sucesso');
    },
    onError: (error: any) => {
      toast.error(error?.response?.data?.detail || 'Erro ao remover proposta');
    },
  });
}

/**
 * Hook para listar propostas de um edital
 */
export function useListarPropostasPorEdital(
  tenderId: string,
  params?: { page?: number; size?: number }
) {
  return useQuery({
    queryKey: QUERY_KEYS.tender(tenderId, params),
    queryFn: () => proposalsService.listarPropostasPorEdital(tenderId, params),
    enabled: !!tenderId,
    staleTime: 1000 * 60 * 5,
  });
}

/**
 * Hook para submeter proposta
 */
export function useSubmeterProposta() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (params: SubmeterPropostaParams) =>
      proposalsService.submeterProposta(params),
    onSuccess: (data, variables) => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.lists() });
      queryClient.invalidateQueries({
        queryKey: QUERY_KEYS.detail(variables.proposal_id),
      });
      toast.success('Proposta submetida com sucesso');
    },
    onError: (error: any) => {
      toast.error(
        error?.response?.data?.detail || 'Erro ao submeter proposta'
      );
    },
  });
}

/**
 * Hook para alterar status da proposta
 */
export function useAlterarStatusProposta() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (params: AlterarStatusPropostaParams) =>
      proposalsService.alterarStatusProposta(params),
    onSuccess: (data, variables) => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.lists() });
      queryClient.invalidateQueries({
        queryKey: QUERY_KEYS.detail(variables.proposal_id),
      });
      toast.success('Status alterado com sucesso');
    },
    onError: (error: any) => {
      toast.error(error?.response?.data?.detail || 'Erro ao alterar status');
    },
  });
}

/**
 * Hook para listar propostas em andamento
 */
export function useListarPropostasEmAndamento(params?: {
  page?: number;
  size?: number;
}) {
  return useQuery({
    queryKey: QUERY_KEYS.emAndamento(params),
    queryFn: () => proposalsService.listarPropostasEmAndamento(params),
    staleTime: 1000 * 60 * 5,
  });
}

/**
 * Hook para listar propostas aprovadas
 */
export function useListarPropostasAprovadas(params?: {
  page?: number;
  size?: number;
}) {
  return useQuery({
    queryKey: QUERY_KEYS.aprovadas(params),
    queryFn: () => proposalsService.listarPropostasAprovadas(params),
    staleTime: 1000 * 60 * 5,
  });
}

/**
 * Hook para dashboard de propostas
 */
export function useProposalsDashboard(params?: { periodo_dias?: number }) {
  return useQuery({
    queryKey: QUERY_KEYS.dashboard(params),
    queryFn: () => proposalsService.getDashboard(params),
    staleTime: 1000 * 60 * 10,
  });
}

// ========== ITENS DE PROPOSTA ==========

/**
 * Hook para listar itens de uma proposta
 */
export function useListarItens(proposalId: string) {
  return useQuery({
    queryKey: QUERY_KEYS.items(proposalId),
    queryFn: () => proposalsService.listarItens(proposalId),
    enabled: !!proposalId,
    staleTime: 1000 * 60 * 5,
  });
}

/**
 * Hook para adicionar item à proposta
 */
export function useAdicionarItem() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      proposalId,
      data,
    }: {
      proposalId: string;
      data: ProposalItemCreate;
    }) => proposalsService.adicionarItem(proposalId, data),
    onSuccess: (data, variables) => {
      queryClient.invalidateQueries({
        queryKey: QUERY_KEYS.items(variables.proposalId),
      });
      queryClient.invalidateQueries({
        queryKey: QUERY_KEYS.detail(variables.proposalId),
      });
      toast.success('Item adicionado com sucesso');
    },
    onError: (error: any) => {
      toast.error(error?.response?.data?.detail || 'Erro ao adicionar item');
    },
  });
}

/**
 * Hook para atualizar item da proposta
 */
export function useAtualizarItem() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      proposalId,
      itemId,
      data,
    }: {
      proposalId: string;
      itemId: string;
      data: any;
    }) => proposalsService.atualizarItem(proposalId, itemId, data),
    onSuccess: (data, variables) => {
      queryClient.invalidateQueries({
        queryKey: QUERY_KEYS.items(variables.proposalId),
      });
      queryClient.invalidateQueries({
        queryKey: QUERY_KEYS.detail(variables.proposalId),
      });
      toast.success('Item atualizado com sucesso');
    },
    onError: (error: any) => {
      toast.error(error?.response?.data?.detail || 'Erro ao atualizar item');
    },
  });
}

/**
 * Hook para remover item da proposta
 */
export function useRemoverItem() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ proposalId, itemId }: { proposalId: string; itemId: string }) =>
      proposalsService.removerItem(proposalId, itemId),
    onSuccess: (data, variables) => {
      queryClient.invalidateQueries({
        queryKey: QUERY_KEYS.items(variables.proposalId),
      });
      queryClient.invalidateQueries({
        queryKey: QUERY_KEYS.detail(variables.proposalId),
      });
      toast.success('Item removido com sucesso');
    },
    onError: (error: any) => {
      toast.error(error?.response?.data?.detail || 'Erro ao remover item');
    },
  });
}
