/**
 * Hooks React Query - Contract Management
 * Gestão de Contratos
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { contractService } from '@/services/clients';
import type {
  ClientContractCreate,
  ClientContractUpdate,
} from '@/types/generated/clients/conectaPROMóduloCLIENTS.schemas';

/**
 * Query keys para cache
 */
export const contractKeys = {
  all: ['contracts'] as const,
  lists: () => [...contractKeys.all, 'list'] as const,
  list: (clientId: string, filters?: any) =>
    [...contractKeys.lists(), clientId, filters] as const,
  details: () => [...contractKeys.all, 'detail'] as const,
  detail: (id: string) => [...contractKeys.details(), id] as const,
};

/**
 * Hook para listar contratos do cliente
 */
export function useContracts(
  clientId: string,
  params?: {
    skip?: number;
    limit?: number;
  },
  enabled = true
) {
  return useQuery({
    queryKey: contractKeys.list(clientId, params),
    queryFn: () => contractService.list(clientId, params),
    enabled: enabled && !!clientId,
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
    mutationFn: ({
      clientId,
      data,
    }: {
      clientId: string;
      data: ClientContractCreate;
    }) => contractService.create(clientId, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({
        queryKey: contractKeys.list(variables.clientId),
      });
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
      data: ClientContractUpdate;
    }) => contractService.update(contractId, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({
        queryKey: contractKeys.detail(variables.contractId),
      });
      queryClient.invalidateQueries({ queryKey: contractKeys.lists() });
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
    },
  });
}

/**
 * Hook para suspender contrato
 */
export function useSuspendContract() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      contractId,
      reason,
    }: {
      contractId: string;
      reason?: string;
    }) => contractService.suspend(contractId, reason),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({
        queryKey: contractKeys.detail(variables.contractId),
      });
      queryClient.invalidateQueries({ queryKey: contractKeys.lists() });
    },
  });
}

/**
 * Hook para cancelar contrato
 */
export function useCancelContract() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      contractId,
      reason,
    }: {
      contractId: string;
      reason?: string;
    }) => contractService.cancel(contractId, reason),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({
        queryKey: contractKeys.detail(variables.contractId),
      });
      queryClient.invalidateQueries({ queryKey: contractKeys.lists() });
    },
  });
}
