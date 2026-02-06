'use client';

/**
 * Hooks React Query - Contracts (Contratos Públicos)
 *
 * Hooks para gestão de contratos públicos, medições, aditivos
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { toast } from 'sonner';
import contractsService, {
  type ListContractsParams,
  type AlterarStatusContratoParams,
  type AditivarParams,
} from '@/services/bidding/contracts.service';
import type {
  PublicContractCreate,
  PublicContractUpdate,
  MeasurementSummary,
} from '@/types/generated/bidding';

const QUERY_KEYS = {
  all: ['bidding', 'contracts'] as const,
  lists: () => [...QUERY_KEYS.all, 'list'] as const,
  list: (params?: ListContractsParams) => [...QUERY_KEYS.lists(), params] as const,
  details: () => [...QUERY_KEYS.all, 'detail'] as const,
  detail: (id: string) => [...QUERY_KEYS.details(), id] as const,
  measurements: (contractId: string) =>
    [...QUERY_KEYS.detail(contractId), 'measurements'] as const,
  vigentes: (params?: any) => [...QUERY_KEYS.all, 'vigentes', params] as const,
  vencendo: (params?: any) => [...QUERY_KEYS.all, 'vencendo', params] as const,
  dashboard: (params?: any) => [...QUERY_KEYS.all, 'dashboard', params] as const,
};

/**
 * Hook para listar contratos com filtros
 */
export function useListarContratos(params?: ListContractsParams) {
  return useQuery({
    queryKey: QUERY_KEYS.list(params),
    queryFn: () => contractsService.listarContratos(params),
    staleTime: 1000 * 60 * 5,
  });
}

/**
 * Hook para buscar contrato por ID
 */
export function useBuscarContrato(contractId: string, enabled = true) {
  return useQuery({
    queryKey: QUERY_KEYS.detail(contractId),
    queryFn: () => contractsService.buscarContratoPorId(contractId),
    enabled: enabled && !!contractId,
    staleTime: 1000 * 60 * 5,
  });
}

/**
 * Hook para criar novo contrato
 */
export function useCriarContrato() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (payload: PublicContractCreate) =>
      contractsService.criarContrato(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.lists() });
      toast.success('Contrato criado com sucesso');
    },
    onError: (error: any) => {
      toast.error(error?.response?.data?.detail || 'Erro ao criar contrato');
    },
  });
}

/**
 * Hook para atualizar contrato
 */
export function useAtualizarContrato() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: PublicContractUpdate }) =>
      contractsService.atualizarContrato(id, data),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.lists() });
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.detail(data.id) });
      toast.success('Contrato atualizado com sucesso');
    },
    onError: (error: any) => {
      toast.error(
        error?.response?.data?.detail || 'Erro ao atualizar contrato'
      );
    },
  });
}

/**
 * Hook para remover contrato
 */
export function useRemoverContrato() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (contractId: string) =>
      contractsService.removerContrato(contractId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.lists() });
      toast.success('Contrato removido com sucesso');
    },
    onError: (error: any) => {
      toast.error(error?.response?.data?.detail || 'Erro ao remover contrato');
    },
  });
}

/**
 * Hook para listar contratos vigentes
 */
export function useListarContratosVigentes(params?: {
  page?: number;
  size?: number;
}) {
  return useQuery({
    queryKey: QUERY_KEYS.vigentes(params),
    queryFn: () => contractsService.listarContratosVigentes(params),
    staleTime: 1000 * 60 * 5,
  });
}

/**
 * Hook para listar contratos vencendo
 */
export function useListarContratosVencendo(params?: {
  dias?: number;
  page?: number;
  size?: number;
}) {
  return useQuery({
    queryKey: QUERY_KEYS.vencendo(params),
    queryFn: () => contractsService.listarContratosVencendo(params),
    staleTime: 1000 * 60 * 5,
  });
}

/**
 * Hook para alterar status do contrato
 */
export function useAlterarStatusContrato() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (params: AlterarStatusContratoParams) =>
      contractsService.alterarStatus(params),
    onSuccess: (data, variables) => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.lists() });
      queryClient.invalidateQueries({
        queryKey: QUERY_KEYS.detail(variables.contract_id),
      });
      toast.success('Status alterado com sucesso');
    },
    onError: (error: any) => {
      toast.error(error?.response?.data?.detail || 'Erro ao alterar status');
    },
  });
}

/**
 * Hook para criar aditivo de contrato
 */
export function useAditivar() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (params: AditivarParams) => contractsService.aditivar(params),
    onSuccess: (data, variables) => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.lists() });
      queryClient.invalidateQueries({
        queryKey: QUERY_KEYS.detail(variables.contract_id),
      });
      toast.success('Aditivo criado com sucesso');
    },
    onError: (error: any) => {
      toast.error(error?.response?.data?.detail || 'Erro ao criar aditivo');
    },
  });
}

/**
 * Hook para dashboard de contratos
 */
export function useContractsDashboard(params?: { periodo_dias?: number }) {
  return useQuery({
    queryKey: QUERY_KEYS.dashboard(params),
    queryFn: () => contractsService.getDashboard(params),
    staleTime: 1000 * 60 * 10,
  });
}

// ========== MEDIÇÕES ==========
// NOTA: Funções de medições comentadas até os tipos estarem disponíveis no schema gerado

/*
export function useListarMedicoes(
  contractId: string,
  params?: { status?: string }
) {
  return useQuery({
    queryKey: QUERY_KEYS.measurements(contractId),
    queryFn: () => contractsService.listarMedicoes(contractId, params),
    enabled: !!contractId,
    staleTime: 1000 * 60 * 5,
  });
}

export function useCriarMedicao() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      contractId,
      data,
    }: {
      contractId: string;
      data: any;
    }) => contractsService.criarMedicao(contractId, data),
    onSuccess: (data, variables) => {
      queryClient.invalidateQueries({
        queryKey: QUERY_KEYS.measurements(variables.contractId),
      });
      queryClient.invalidateQueries({
        queryKey: QUERY_KEYS.detail(variables.contractId),
      });
      toast.success('Medição criada com sucesso');
    },
    onError: (error: any) => {
      toast.error(error?.response?.data?.detail || 'Erro ao criar medição');
    },
  });
}

export function useAtualizarMedicao() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      contractId,
      measurementId,
      data,
    }: {
      contractId: string;
      measurementId: string;
      data: any;
    }) => contractsService.atualizarMedicao(contractId, measurementId, data),
    onSuccess: (data, variables) => {
      queryClient.invalidateQueries({
        queryKey: QUERY_KEYS.measurements(variables.contractId),
      });
      queryClient.invalidateQueries({
        queryKey: QUERY_KEYS.detail(variables.contractId),
      });
      toast.success('Medição atualizada com sucesso');
    },
    onError: (error: any) => {
      toast.error(error?.response?.data?.detail || 'Erro ao atualizar medição');
    },
  });
}

export function useAprovarMedicao() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      contractId,
      measurementId,
      observacoes,
    }: {
      contractId: string;
      measurementId: string;
      observacoes?: string;
    }) => contractsService.aprovarMedicao(contractId, measurementId, observacoes),
    onSuccess: (data, variables) => {
      queryClient.invalidateQueries({
        queryKey: QUERY_KEYS.measurements(variables.contractId),
      });
      queryClient.invalidateQueries({
        queryKey: QUERY_KEYS.detail(variables.contractId),
      });
      toast.success('Medição aprovada com sucesso');
    },
    onError: (error: any) => {
      toast.error(error?.response?.data?.detail || 'Erro ao aprovar medição');
    },
  });
}

export function useRejeitarMedicao() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      contractId,
      measurementId,
      motivo,
    }: {
      contractId: string;
      measurementId: string;
      motivo: string;
    }) => contractsService.rejeitarMedicao(contractId, measurementId, motivo),
    onSuccess: (data, variables) => {
      queryClient.invalidateQueries({
        queryKey: QUERY_KEYS.measurements(variables.contractId),
      });
      queryClient.invalidateQueries({
        queryKey: QUERY_KEYS.detail(variables.contractId),
      });
      toast.success('Medição rejeitada');
    },
    onError: (error: any) => {
      toast.error(error?.response?.data?.detail || 'Erro ao rejeitar medição');
    },
  });
}
*/
