'use client';

/**
 * Hooks React Query - Tenders (Editais)
 *
 * Hooks para gestão de editais de licitação, integração PNCP
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { toast } from 'sonner';
import tendersService, {
  type ListTendersParams,
  type PNCPBuscarParams,
  type MarcarParticipacaoParams,
  type AlterarStatusParams,
} from '@/services/bidding/tenders.service';
import type {
  TenderCreate,
  TenderUpdate,
} from '@/types/generated/bidding';

const QUERY_KEYS = {
  all: ['bidding', 'tenders'] as const,
  lists: () => [...QUERY_KEYS.all, 'list'] as const,
  list: (params?: ListTendersParams) => [...QUERY_KEYS.lists(), params] as const,
  details: () => [...QUERY_KEYS.all, 'detail'] as const,
  detail: (id: string) => [...QUERY_KEYS.details(), id] as const,
  abertos: (params?: any) => [...QUERY_KEYS.all, 'abertos', params] as const,
  segmento: (segmento: string, params?: any) =>
    [...QUERY_KEYS.all, 'segmento', segmento, params] as const,
  pncp: (params?: PNCPBuscarParams) => [...QUERY_KEYS.all, 'pncp', params] as const,
  dashboard: (params?: any) => [...QUERY_KEYS.all, 'dashboard', params] as const,
};

/**
 * Hook para listar editais com filtros
 */
export function useListarEditais(params?: ListTendersParams) {
  return useQuery({
    queryKey: QUERY_KEYS.list(params),
    queryFn: () => tendersService.listarEditais(params),
    staleTime: 1000 * 60 * 5, // 5 minutos
  });
}

/**
 * Hook para buscar edital por ID
 */
export function useBuscarEdital(tenderId: string, enabled = true) {
  return useQuery({
    queryKey: QUERY_KEYS.detail(tenderId),
    queryFn: () => tendersService.buscarEditalPorId(tenderId),
    enabled: enabled && !!tenderId,
    staleTime: 1000 * 60 * 5,
  });
}

/**
 * Hook para criar novo edital
 */
export function useCriarEdital() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (payload: TenderCreate) => tendersService.criarEdital(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.lists() });
      toast.success('Edital criado com sucesso');
    },
    onError: (error: any) => {
      toast.error(error?.response?.data?.detail || 'Erro ao criar edital');
    },
  });
}

/**
 * Hook para atualizar edital
 */
export function useAtualizarEdital() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: TenderUpdate }) =>
      tendersService.atualizarEdital(id, data),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.lists() });
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.detail(data.id) });
      toast.success('Edital atualizado com sucesso');
    },
    onError: (error: any) => {
      toast.error(error?.response?.data?.detail || 'Erro ao atualizar edital');
    },
  });
}

/**
 * Hook para remover edital
 */
export function useRemoverEdital() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (tenderId: string) => tendersService.removerEdital(tenderId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.lists() });
      toast.success('Edital removido com sucesso');
    },
    onError: (error: any) => {
      toast.error(error?.response?.data?.detail || 'Erro ao remover edital');
    },
  });
}

/**
 * Hook para listar editais abertos
 */
export function useListarEditaisAbertos(params?: {
  uf?: string;
  segmento?: string;
  page?: number;
  size?: number;
}) {
  return useQuery({
    queryKey: QUERY_KEYS.abertos(params),
    queryFn: () => tendersService.listarEditaisAbertos(params),
    staleTime: 1000 * 60 * 5,
  });
}

/**
 * Hook para listar editais por segmento
 */
export function useListarEditaisPorSegmento(
  segmento: string,
  params?: { page?: number; size?: number }
) {
  return useQuery({
    queryKey: QUERY_KEYS.segmento(segmento, params),
    queryFn: () => tendersService.listarEditaisPorSegmento(segmento, params),
    enabled: !!segmento,
    staleTime: 1000 * 60 * 5,
  });
}

/**
 * Hook para marcar participação em edital
 */
export function useMarcarParticipacao() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (params: MarcarParticipacaoParams) =>
      tendersService.marcarParticipacao(params),
    onSuccess: (data, variables) => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.lists() });
      queryClient.invalidateQueries({
        queryKey: QUERY_KEYS.detail(variables.tender_id),
      });
      toast.success('Participação registrada com sucesso');
    },
    onError: (error: any) => {
      toast.error(
        error?.response?.data?.detail || 'Erro ao registrar participação'
      );
    },
  });
}

/**
 * Hook para alterar status do edital
 */
export function useAlterarStatusEdital() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (params: AlterarStatusParams) =>
      tendersService.alterarStatus(params),
    onSuccess: (data, variables) => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.lists() });
      queryClient.invalidateQueries({
        queryKey: QUERY_KEYS.detail(variables.tender_id),
      });
      toast.success('Status alterado com sucesso');
    },
    onError: (error: any) => {
      toast.error(error?.response?.data?.detail || 'Erro ao alterar status');
    },
  });
}

/**
 * Hook para buscar editais no PNCP
 */
export function useBuscarPNCP(params?: PNCPBuscarParams, enabled = false) {
  return useQuery({
    queryKey: QUERY_KEYS.pncp(params),
    queryFn: () => tendersService.buscarPNCP(params || {}),
    enabled,
    staleTime: 1000 * 60 * 10, // 10 minutos
  });
}

/**
 * Hook mutation para buscar editais no PNCP sob demanda
 */
export function useBuscarPNCPMutation() {
  return useMutation({
    mutationFn: (params: PNCPBuscarParams) => tendersService.buscarPNCP(params),
    onSuccess: () => {
      toast.success('Busca no PNCP realizada com sucesso');
    },
    onError: (error: any) => {
      toast.error(error?.response?.data?.detail || 'Erro ao buscar no PNCP');
    },
  });
}

/**
 * Hook para sincronizar editais com PNCP
 */
export function useSincronizarPNCP() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (params?: { uf?: string; dias_retroativos?: number }) =>
      tendersService.sincronizarPNCP(params),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.lists() });
      toast.success(
        `${data.total_sincronizado} editais sincronizados com sucesso`
      );
    },
    onError: (error: any) => {
      toast.error(
        error?.response?.data?.detail || 'Erro ao sincronizar com PNCP'
      );
    },
  });
}

/**
 * Hook para dashboard de editais
 */
export function useTendersDashboard(params?: {
  uf?: string;
  periodo_dias?: number;
}) {
  return useQuery({
    queryKey: QUERY_KEYS.dashboard(params),
    queryFn: () => tendersService.getDashboard(params),
    staleTime: 1000 * 60 * 10, // 10 minutos
  });
}
