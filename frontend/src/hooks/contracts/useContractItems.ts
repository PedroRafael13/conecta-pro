/**
 * Hooks React Query - Contract Items
 * Gestão de Itens do Contrato
 */

import { useMutation, useQueryClient } from '@tanstack/react-query';
import { contractItemService } from '@/services/contracts';
import { contractKeys } from './useContracts';
import type {
  ContractItemCreate,
  ContractItemUpdate,
  ContractItemResponse,
} from '@/types/generated/contracts/cRMContractsAPI.schemas';

/**
 * Hook para adicionar item ao contrato
 */
export function useAddContractItem() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      contractId,
      data,
    }: {
      contractId: string;
      data: ContractItemCreate;
    }) => contractItemService.add(contractId, data),
    onSuccess: (_, { contractId }) => {
      queryClient.invalidateQueries({ queryKey: contractKeys.detail(contractId) });
      queryClient.invalidateQueries({ queryKey: contractKeys.lists() });
    },
  });
}

/**
 * Hook para atualizar item do contrato
 */
export function useUpdateContractItem() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      contractId,
      itemId,
      data,
    }: {
      contractId: string;
      itemId: string;
      data: ContractItemUpdate;
    }) => contractItemService.update(contractId, itemId, data),
    onSuccess: (_, { contractId }) => {
      queryClient.invalidateQueries({ queryKey: contractKeys.detail(contractId) });
      queryClient.invalidateQueries({ queryKey: contractKeys.lists() });
    },
  });
}

/**
 * Hook para remover item do contrato
 */
export function useRemoveContractItem() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ contractId, itemId }: { contractId: string; itemId: string }) =>
      contractItemService.remove(contractId, itemId),
    onSuccess: (_, { contractId }) => {
      queryClient.invalidateQueries({ queryKey: contractKeys.detail(contractId) });
      queryClient.invalidateQueries({ queryKey: contractKeys.lists() });
    },
  });
}
