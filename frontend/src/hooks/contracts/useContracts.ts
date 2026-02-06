/**
 * Hooks React Query - Contract Management
 * Gestão de Contratos CRM
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { contractService } from '@/services/contracts';
import type {
  ContractCreate,
  ContractUpdate,
  ContractResponse,
  ContractDetailResponse,
  ContractListResponse,
  ContractStats,
  ContractAlert,
  ContractRenewal,
  RenewalResult,
  AdjustmentResult,
} from '@/types/generated/contracts/cRMContractsAPI.schemas';

/**
 * Query keys para cache
 */
export const contractKeys = {
  all: ['contracts'] as const,
  lists: () => [...contractKeys.all, 'list'] as const,
  list: (filters?: any) => [...contractKeys.lists(), filters] as const,
  details: () => [...contractKeys.all, 'detail'] as const,
  detail: (id: string) => [...contractKeys.details(), id] as const,
  stats: (params?: any) => [...contractKeys.all, 'stats', params] as const,
  alerts: (params?: any) => [...contractKeys.all, 'alerts', params] as const,
};

/**
 * Hook para listar contratos
 */
export function useContracts(params?: {
  page?: number;
  page_size?: number;
  status?: string;
  contract_type?: string;
  client_id?: string;
  commercial_manager_id?: string;
  account_manager_id?: string;
  has_sla?: boolean;
  min_value?: number;
  max_value?: number;
  search?: string;
}) {
  return useQuery({
    queryKey: contractKeys.list(params),
    queryFn: () => contractService.list(params),
  });
}

/**
 * Hook para obter estatísticas de contratos
 */
export function useContractStats(params?: {
  client_id?: string;
  commercial_manager_id?: string;
}) {
  return useQuery({
    queryKey: contractKeys.stats(params),
    queryFn: () => contractService.getStats(params),
  });
}

/**
 * Hook para obter alertas de contratos
 */
export function useContractAlerts(params?: { days_ahead?: number }) {
  return useQuery({
    queryKey: contractKeys.alerts(params),
    queryFn: () => contractService.getAlerts(params),
    refetchInterval: 5 * 60 * 1000, // Refetch a cada 5 minutos
  });
}

/**
 * Hook para obter contrato por ID
 */
export function useContract(contractId: string, enabled = true) {
  return useQuery({
    queryKey: contractKeys.detail(contractId),
    queryFn: () => contractService.getById(contractId),
    enabled: enabled && !!contractId,
  });
}

/**
 * Hook para criar contrato
 */
export function useCreateContract() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: ContractCreate) => contractService.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: contractKeys.lists() });
      queryClient.invalidateQueries({ queryKey: contractKeys.stats() });
    },
  });
}

/**
 * Hook para atualizar contrato
 */
export function useUpdateContract() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      contractId,
      data,
    }: {
      contractId: string;
      data: ContractUpdate;
    }) => contractService.update(contractId, data),
    onSuccess: (_, { contractId }) => {
      queryClient.invalidateQueries({ queryKey: contractKeys.detail(contractId) });
      queryClient.invalidateQueries({ queryKey: contractKeys.lists() });
      queryClient.invalidateQueries({ queryKey: contractKeys.stats() });
    },
  });
}

/**
 * Hook para enviar contrato para assinatura
 */
export function useSubmitContract() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (contractId: string) => contractService.submit(contractId),
    onSuccess: (_, contractId) => {
      queryClient.invalidateQueries({ queryKey: contractKeys.detail(contractId) });
      queryClient.invalidateQueries({ queryKey: contractKeys.lists() });
      queryClient.invalidateQueries({ queryKey: contractKeys.stats() });
    },
  });
}

/**
 * Hook para ativar contrato
 */
export function useActivateContract() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (contractId: string) => contractService.activate(contractId),
    onSuccess: (_, contractId) => {
      queryClient.invalidateQueries({ queryKey: contractKeys.detail(contractId) });
      queryClient.invalidateQueries({ queryKey: contractKeys.lists() });
      queryClient.invalidateQueries({ queryKey: contractKeys.stats() });
      queryClient.invalidateQueries({ queryKey: contractKeys.alerts() });
    },
  });
}

/**
 * Hook para suspender contrato
 */
export function useSuspendContract() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ contractId, reason }: { contractId: string; reason?: string }) =>
      contractService.suspend(contractId, reason),
    onSuccess: (_, { contractId }) => {
      queryClient.invalidateQueries({ queryKey: contractKeys.detail(contractId) });
      queryClient.invalidateQueries({ queryKey: contractKeys.lists() });
      queryClient.invalidateQueries({ queryKey: contractKeys.stats() });
    },
  });
}

/**
 * Hook para encerrar contrato
 */
export function useTerminateContract() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ contractId, reason }: { contractId: string; reason?: string }) =>
      contractService.terminate(contractId, reason),
    onSuccess: (_, { contractId }) => {
      queryClient.invalidateQueries({ queryKey: contractKeys.detail(contractId) });
      queryClient.invalidateQueries({ queryKey: contractKeys.lists() });
      queryClient.invalidateQueries({ queryKey: contractKeys.stats() });
    },
  });
}

/**
 * Hook para calcular renovação
 */
export function useCalculateRenewal() {
  return useMutation({
    mutationFn: ({
      contractId,
      data,
    }: {
      contractId: string;
      data: ContractRenewal;
    }) => contractService.calculateRenewal(contractId, data),
  });
}

/**
 * Hook para calcular reajuste
 */
export function useCalculateAdjustment() {
  return useMutation({
    mutationFn: ({
      contractId,
      params,
    }: {
      contractId: string;
      params?: { custom_percent?: number; effective_date?: string };
    }) => contractService.calculateAdjustment(contractId, params),
  });
}

/**
 * Hook para deletar contrato
 */
export function useDeleteContract() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (contractId: string) => contractService.delete(contractId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: contractKeys.lists() });
      queryClient.invalidateQueries({ queryKey: contractKeys.stats() });
    },
  });
}
