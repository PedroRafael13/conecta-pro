/**
 * React Query Hooks - Ordens de Serviço (CAMPO)
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { ordemServicoService } from '@/services/campo';
import type { OrdemServicoCreate, OrdemServicoUpdate } from '@/api/campo/generated/models';
import type {
  OrdemServicoAgendamento,
  OrdemServicoStatusUpdate,
  OrdemServicoMaterialBaixa,
  OrdemServicoAvaliacao,
} from '@/services/campo/types';

const QUERY_KEYS = {
  all: ['campo', 'ordens-servico'] as const,
  lists: () => [...QUERY_KEYS.all, 'list'] as const,
  list: (filters?: object) => [...QUERY_KEYS.lists(), filters] as const,
  details: () => [...QUERY_KEYS.all, 'detail'] as const,
  detail: (id: string) => [...QUERY_KEYS.details(), id] as const,
  atrasadas: () => [...QUERY_KEYS.all, 'atrasadas'] as const,
  porTecnico: (tecnicoId: string) => [...QUERY_KEYS.all, 'tecnico', tecnicoId] as const,
  porCliente: (clienteId: string) => [...QUERY_KEYS.all, 'cliente', clienteId] as const,
  dashboard: (periodo?: string) => [...QUERY_KEYS.all, 'dashboard', periodo] as const,
};

/**
 * Lista ordens de serviço
 */
export const useOrdens = (params?: Parameters<typeof ordemServicoService.listarOrdens>[0]) => {
  return useQuery({
    queryKey: QUERY_KEYS.list(params),
    queryFn: () => ordemServicoService.listarOrdens(params),
  });
};

/**
 * Busca ordem de serviço por ID
 */
export const useOrdem = (ordemId: string) => {
  return useQuery({
    queryKey: QUERY_KEYS.detail(ordemId),
    queryFn: () => ordemServicoService.buscarOrdem(ordemId),
    enabled: !!ordemId,
  });
};

/**
 * Cria nova ordem de serviço
 */
export const useCriarOrdem = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: OrdemServicoCreate) => ordemServicoService.criarOrdem(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.lists() });
    },
  });
};

/**
 * Atualiza ordem de serviço
 */
export const useAtualizarOrdem = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ ordemId, data }: { ordemId: string; data: OrdemServicoUpdate }) =>
      ordemServicoService.atualizarOrdem(ordemId, data),
    onSuccess: (_, { ordemId }) => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.detail(ordemId) });
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.lists() });
    },
  });
};

/**
 * Agenda ordem de serviço
 */
export const useAgendarOrdem = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ ordemId, data }: { ordemId: string; data: OrdemServicoAgendamento }) =>
      ordemServicoService.agendarOrdem(ordemId, data),
    onSuccess: (_, { ordemId }) => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.detail(ordemId) });
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.lists() });
    },
  });
};

/**
 * Inicia ordem de serviço (check-in)
 */
export const useIniciarOrdem = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ ordemId, data }: { ordemId: string; data: { latitude: number; longitude: number; observacoes?: string } }) =>
      ordemServicoService.fazerCheckin(ordemId, data),
    onSuccess: (_, { ordemId }) => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.detail(ordemId) });
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.lists() });
    },
  });
};

/**
 * Pausa ordem de serviço
 */
export const usePausarOrdem = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ ordemId, motivo }: { ordemId: string; motivo: string }) =>
      ordemServicoService.pausarOrdem(ordemId, { motivo }),
    onSuccess: (_, { ordemId }) => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.detail(ordemId) });
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.lists() });
    },
  });
};

/**
 * Conclui ordem de serviço
 */
export const useConcluirOrdem = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ ordemId, data }: { ordemId: string; data: { observacoes?: string; solucao_aplicada?: string } }) =>
      ordemServicoService.concluirOrdem(ordemId, data),
    onSuccess: (_, { ordemId }) => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.detail(ordemId) });
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.lists() });
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.dashboard() });
    },
  });
};

/**
 * Cancela ordem de serviço
 */
export const useCancelarOrdem = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ ordemId, data }: { ordemId: string; data: { motivo: string } }) =>
      ordemServicoService.cancelarOrdem(ordemId, data),
    onSuccess: (_, { ordemId }) => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.detail(ordemId) });
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.lists() });
    },
  });
};

/**
 * Lista ordens atrasadas
 */
export const useOrdensAtrasadas = () => {
  return useQuery({
    queryKey: QUERY_KEYS.atrasadas(),
    queryFn: () => ordemServicoService.listarAtrasadas(),
  });
};

/**
 * Lista ordens por técnico
 */
export const useOrdensPorTecnico = (tecnicoId: string) => {
  return useQuery({
    queryKey: QUERY_KEYS.porTecnico(tecnicoId),
    queryFn: () => ordemServicoService.listarPorTecnico(tecnicoId),
    enabled: !!tecnicoId,
  });
};

/**
 * Lista ordens por cliente
 */
export const useOrdensPorCliente = (clienteId: string) => {
  return useQuery({
    queryKey: QUERY_KEYS.porCliente(clienteId),
    queryFn: () => ordemServicoService.listarPorCliente(clienteId),
    enabled: !!clienteId,
  });
};

/**
 * Baixa materiais
 */
export const useBaixarMateriais = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      ordemId,
      materiais,
    }: {
      ordemId: string;
      materiais: OrdemServicoMaterialBaixa[];
    }) => ordemServicoService.baixarMateriais(ordemId, materiais),
    onSuccess: (_, { ordemId }) => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.detail(ordemId) });
    },
  });
};

/**
 * Avaliar ordem
 */
export const useAvaliarOrdem = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      ordemId,
      avaliacao,
    }: {
      ordemId: string;
      avaliacao: OrdemServicoAvaliacao;
    }) => ordemServicoService.avaliar(ordemId, avaliacao),
    onSuccess: (_, { ordemId }) => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.detail(ordemId) });
    },
  });
};

/**
 * Upload fotos
 */
export const useUploadFotosOrdem = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ ordemId, data }: { ordemId: string; data: { tipo: string; url: string; descricao?: string } }) =>
      ordemServicoService.uploadFotos(ordemId, data),
    onSuccess: (_, { ordemId }) => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.detail(ordemId) });
    },
  });
};

/**
 * Dashboard de ordens
 */
export const useDashboardOrdens = (params?: { periodo?: string; tecnico_id?: string }) => {
  return useQuery({
    queryKey: QUERY_KEYS.dashboard(params?.periodo),
    queryFn: () => ordemServicoService.dashboard(params),
  });
};
