/**
 * React Query Hooks - Visitas (CAMPO)
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { visitaService } from '@/services/campo';
import type {
  VisitaCreate,
  VisitaUpdate,
  VisitaCheckinRequest,
  VisitaCheckoutRequest,
  VisitaReagendarRequest,
  VisitaCancelarRequest,
  VisitaPropostaRequest,
  VisitaFotoRequest,
  ListarVisitasApiV1CampoVisitasGetParams,
  ListarVisitasResponsavelApiV1CampoVisitasResponsavelResponsavelIdGetParams,
  ObterDashboardApiV1CampoVisitasDashboardGetParams,
} from '@/api/campo/generated/models';

const QUERY_KEYS = {
  all: ['campo', 'visitas'] as const,
  lists: () => [...QUERY_KEYS.all, 'list'] as const,
  list: (filters?: object) => [...QUERY_KEYS.lists(), filters] as const,
  details: () => [...QUERY_KEYS.all, 'detail'] as const,
  detail: (id: string) => [...QUERY_KEYS.details(), id] as const,
  porCliente: (clienteId: string) => [...QUERY_KEYS.all, 'cliente', clienteId] as const,
  porTecnico: (tecnicoId: string) => [...QUERY_KEYS.all, 'tecnico', tecnicoId] as const,
  pendentes: () => [...QUERY_KEYS.all, 'pendentes'] as const,
  concluidas: () => [...QUERY_KEYS.all, 'concluidas'] as const,
  dashboard: (periodo?: string) => [...QUERY_KEYS.all, 'dashboard', periodo] as const,
  metricsConversao: (periodo?: string) =>
    [...QUERY_KEYS.all, 'metrics-conversao', periodo] as const,
};

/**
 * Lista visitas
 */
export const useVisitas = (params?: Parameters<typeof visitaService.listarVisitas>[0]) => {
  return useQuery({
    queryKey: QUERY_KEYS.list(params),
    queryFn: () => visitaService.listarVisitas(params),
  });
};

/**
 * Busca visita por ID
 */
export const useVisita = (visitaId: string) => {
  return useQuery({
    queryKey: QUERY_KEYS.detail(visitaId),
    queryFn: () => visitaService.buscarVisita(visitaId),
    enabled: !!visitaId,
  });
};

/**
 * Cria nova visita
 */
export const useCriarVisita = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: VisitaCreate) => visitaService.criarVisita(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.lists() });
    },
  });
};

/**
 * Atualiza visita
 */
export const useAtualizarVisita = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ visitaId, data }: { visitaId: string; data: VisitaUpdate }) =>
      visitaService.atualizarVisita(visitaId, data),
    onSuccess: (_, { visitaId }) => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.detail(visitaId) });
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.lists() });
    },
  });
};

/**
 * Deleta visita
 */
export const useDeletarVisita = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (visitaId: string) => visitaService.deletarVisita(visitaId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.lists() });
    },
  });
};

/**
 * Check-in na visita
 */
export const useCheckinVisita = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ visitaId, data }: { visitaId: string; data: VisitaCheckinRequest }) =>
      visitaService.checkin(visitaId, data),
    onSuccess: (_, { visitaId }) => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.detail(visitaId) });
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.lists() });
    },
  });
};

/**
 * Check-out da visita
 */
export const useCheckoutVisita = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ visitaId, data }: { visitaId: string; data: VisitaCheckoutRequest }) =>
      visitaService.checkout(visitaId, data),
    onSuccess: (_, { visitaId }) => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.detail(visitaId) });
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.lists() });
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.concluidas() });
    },
  });
};

/**
 * Cancela visita
 */
export const useCancelarVisita = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ visitaId, motivo }: { visitaId: string; motivo: string }) =>
      visitaService.cancelarVisita(visitaId, { motivo } as VisitaCancelarRequest),
    onSuccess: (_, { visitaId }) => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.detail(visitaId) });
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.lists() });
    },
  });
};

/**
 * Reagenda visita
 */
export const useReagendarVisita = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      visitaId,
      data,
    }: {
      visitaId: string;
      data: VisitaReagendarRequest;
    }) =>
      visitaService.reagendar(visitaId, data),
    onSuccess: (_, { visitaId }) => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.detail(visitaId) });
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.lists() });
    },
  });
};

/**
 * Vincula proposta (conversao de visita)
 */
export const useConverterVisita = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ visitaId, data }: { visitaId: string; data: VisitaPropostaRequest }) =>
      visitaService.vincularProposta(visitaId, data),
    onSuccess: (_, { visitaId }) => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.detail(visitaId) });
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.metricsConversao() });
    },
  });
};

/**
 * Lista visitas por cliente
 */
export const useVisitasPorCliente = (clienteId: string) => {
  return useQuery({
    queryKey: QUERY_KEYS.porCliente(clienteId),
    queryFn: () => visitaService.listarPorCliente(clienteId),
    enabled: !!clienteId,
  });
};

/**
 * Lista visitas por técnico (responsavel)
 */
export const useVisitasPorTecnico = (tecnicoId: string, params?: ListarVisitasResponsavelApiV1CampoVisitasResponsavelResponsavelIdGetParams) => {
  return useQuery({
    queryKey: QUERY_KEYS.porTecnico(tecnicoId),
    queryFn: () => visitaService.listarPorResponsavel(tecnicoId, params),
    enabled: !!tecnicoId,
  });
};

/**
 * Lista visitas pendentes de confirmacao
 */
export const useVisitasPendentes = () => {
  return useQuery({
    queryKey: QUERY_KEYS.pendentes(),
    queryFn: () => visitaService.listarPendentesConfirmacao(),
  });
};

/**
 * Lista visitas concluídas (filtradas por status realizada)
 */
export const useVisitasConcluidas = (params?: { page?: number; page_size?: number }) => {
  return useQuery({
    queryKey: QUERY_KEYS.concluidas(),
    queryFn: () => visitaService.listarVisitas({ ...params, status: 'realizada' }),
  });
};

/**
 * Adiciona foto a visita
 */
export const useUploadFotosVisita = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ visitaId, data }: { visitaId: string; data: VisitaFotoRequest }) =>
      visitaService.adicionarFoto(visitaId, data),
    onSuccess: (_, { visitaId }) => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.detail(visitaId) });
    },
  });
};

/**
 * Dashboard visitas
 */
export const useDashboardVisitas = (params?: ObterDashboardApiV1CampoVisitasDashboardGetParams) => {
  return useQuery({
    queryKey: QUERY_KEYS.dashboard(params?.periodo_dias?.toString()),
    queryFn: () => visitaService.dashboard(params),
  });
};

/**
 * Métricas de conversão (via dashboard)
 */
export const useMetricsConversao = (params?: ObterDashboardApiV1CampoVisitasDashboardGetParams) => {
  return useQuery({
    queryKey: QUERY_KEYS.metricsConversao(params?.periodo_dias?.toString()),
    queryFn: () => visitaService.dashboard(params),
  });
};
