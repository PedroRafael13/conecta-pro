/**
 * Hooks React Query - Contract Addendums
 * Gestão de Aditivos Contratuais
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { contractAddendumService } from '@/services/contracts';
import { contractKeys } from './useContracts';
import type {
  ContractAddendumCreate,
  ContractAddendumResponse,
  ContractAddendumSign,
} from '@/types/generated/contracts/cRMContractsAPI.schemas';

/**
 * Query keys para aditivos
 */
export const addendumKeys = {
  all: ['addendums'] as const,
  lists: () => [...addendumKeys.all, 'list'] as const,
  list: (contractId: string) => [...addendumKeys.lists(), contractId] as const,
};

/**
 * Hook para listar aditivos do contrato
 */
export function useContractAddendums(contractId: string, enabled = true) {
  return useQuery({
    queryKey: addendumKeys.list(contractId),
    queryFn: () => contractAddendumService.list(contractId),
    enabled: enabled && !!contractId,
  });
}

/**
 * Hook para criar aditivo
 */
export function useCreateAddendum() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      contractId,
      data,
    }: {
      contractId: string;
      data: ContractAddendumCreate;
    }) => contractAddendumService.create(contractId, data),
    onSuccess: (_, { contractId }) => {
      queryClient.invalidateQueries({ queryKey: addendumKeys.list(contractId) });
      queryClient.invalidateQueries({ queryKey: contractKeys.detail(contractId) });
    },
  });
}

/**
 * Hook para assinar aditivo
 */
export function useSignAddendum() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      addendumId,
      contractId,
      data,
    }: {
      addendumId: string;
      contractId: string;
      data: ContractAddendumSign;
    }) => contractAddendumService.sign(addendumId, data),
    onSuccess: (_, { contractId }) => {
      queryClient.invalidateQueries({ queryKey: addendumKeys.list(contractId) });
      queryClient.invalidateQueries({ queryKey: contractKeys.detail(contractId) });
      queryClient.invalidateQueries({ queryKey: contractKeys.lists() });
    },
  });
}
