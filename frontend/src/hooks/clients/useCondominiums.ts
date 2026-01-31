/**
 * Hooks React Query - Condominium Management
 * Gestão de Condomínios
 *
 * MIGRADO PARA ORVAL - 31/01/2026
 * Agora usa hooks gerados automaticamente pelo Orval
 */

import { useMutation, useQueryClient } from '@tanstack/react-query';

// Tipos do Orval
import type {
  CondominiumCreate,
  CondominiumUpdate,
} from '@/types/generated/clients/conectaPROMóduloCLIENTS.schemas';

// Hooks e funções Orval
import {
  // Query hooks
  useListCondominiumsApiV1ClientsClientsClientIdCondominiumsGet,
  useGetCondominiumApiV1ClientsClientsCondominiumsCondominiumIdGet,
  useGetCondominiumStatsApiV1ClientsClientsCondominiumsStatsGet,
  // Query keys
  getListCondominiumsApiV1ClientsClientsClientIdCondominiumsGetQueryKey,
  getGetCondominiumApiV1ClientsClientsCondominiumsCondominiumIdGetQueryKey,
  getGetCondominiumStatsApiV1ClientsClientsCondominiumsStatsGetQueryKey,
  // Mutation functions
  createCondominiumApiV1ClientsClientsClientIdCondominiumsPost,
  updateCondominiumApiV1ClientsClientsCondominiumsCondominiumIdPut,
  deleteCondominiumApiV1ClientsClientsCondominiumsCondominiumIdDelete,
  activateCondominiumApiV1ClientsClientsCondominiumsCondominiumIdActivatePost,
  startImplantationApiV1ClientsClientsCondominiumsCondominiumIdStartImplantationPost,
  finishImplantationApiV1ClientsClientsCondominiumsCondominiumIdFinishImplantationPost,
} from '@/types/generated/clients/clients-cadastro';

/**
 * Re-exports de hooks Orval para queries
 */
export {
  useListCondominiumsApiV1ClientsClientsClientIdCondominiumsGet,
  useGetCondominiumApiV1ClientsClientsCondominiumsCondominiumIdGet,
  useGetCondominiumStatsApiV1ClientsClientsCondominiumsStatsGet,
};

/**
 * Aliases para manter compatibilidade com código existente
 */
export { useListCondominiumsApiV1ClientsClientsClientIdCondominiumsGet as useCondominiums };
export { useGetCondominiumApiV1ClientsClientsCondominiumsCondominiumIdGet as useCondominium };
export { useGetCondominiumStatsApiV1ClientsClientsCondominiumsStatsGet as useCondominiumStats };

/**
 * Hook para criar condomínio
 * Usa Orval mutation function com React Query manual
 */
export function useCreateCondominium() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      clientId,
      data,
    }: {
      clientId: string;
      data: CondominiumCreate;
    }) => createCondominiumApiV1ClientsClientsClientIdCondominiumsPost(clientId, data),
    onSuccess: (_, variables) => {
      // Invalida lista do cliente
      queryClient.invalidateQueries({
        queryKey: getListCondominiumsApiV1ClientsClientsClientIdCondominiumsGetQueryKey(variables.clientId),
      });
      // Invalida stats
      queryClient.invalidateQueries({
        queryKey: getGetCondominiumStatsApiV1ClientsClientsCondominiumsStatsGetQueryKey(),
      });
    },
  });
}

/**
 * Hook para atualizar condomínio
 */
export function useUpdateCondominium() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      condominiumId,
      data,
    }: {
      condominiumId: string;
      data: CondominiumUpdate;
    }) => updateCondominiumApiV1ClientsClientsCondominiumsCondominiumIdPut(condominiumId, data),
    onSuccess: (_, variables) => {
      // Invalida detalhe do condomínio
      queryClient.invalidateQueries({
        queryKey: getGetCondominiumApiV1ClientsClientsCondominiumsCondominiumIdGetQueryKey(variables.condominiumId),
      });
      // Invalida todas as listas (não sabemos o clientId aqui)
      queryClient.invalidateQueries({
        queryKey: ['/api/v1/clients/clients'],
      });
    },
  });
}

/**
 * Hook para deletar condomínio
 */
export function useDeleteCondominium() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (condominiumId: string) =>
      deleteCondominiumApiV1ClientsClientsCondominiumsCondominiumIdDelete(condominiumId),
    onSuccess: () => {
      // Invalida todas as listas e stats
      queryClient.invalidateQueries({
        queryKey: ['/api/v1/clients/clients'],
      });
      queryClient.invalidateQueries({
        queryKey: getGetCondominiumStatsApiV1ClientsClientsCondominiumsStatsGetQueryKey(),
      });
    },
  });
}

/**
 * Hook para ativar condomínio
 */
export function useActivateCondominium() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (condominiumId: string) =>
      activateCondominiumApiV1ClientsClientsCondominiumsCondominiumIdActivatePost(condominiumId),
    onSuccess: (_, condominiumId) => {
      queryClient.invalidateQueries({
        queryKey: getGetCondominiumApiV1ClientsClientsCondominiumsCondominiumIdGetQueryKey(condominiumId),
      });
      queryClient.invalidateQueries({
        queryKey: ['/api/v1/clients/clients'],
      });
      queryClient.invalidateQueries({
        queryKey: getGetCondominiumStatsApiV1ClientsClientsCondominiumsStatsGetQueryKey(),
      });
    },
  });
}

/**
 * Hook para iniciar implantação
 */
export function useStartImplantation() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (condominiumId: string) =>
      startImplantationApiV1ClientsClientsCondominiumsCondominiumIdStartImplantationPost(condominiumId),
    onSuccess: (_, condominiumId) => {
      queryClient.invalidateQueries({
        queryKey: getGetCondominiumApiV1ClientsClientsCondominiumsCondominiumIdGetQueryKey(condominiumId),
      });
      queryClient.invalidateQueries({
        queryKey: getGetCondominiumStatsApiV1ClientsClientsCondominiumsStatsGetQueryKey(),
      });
    },
  });
}

/**
 * Hook para finalizar implantação
 */
export function useFinishImplantation() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (condominiumId: string) =>
      finishImplantationApiV1ClientsClientsCondominiumsCondominiumIdFinishImplantationPost(condominiumId),
    onSuccess: (_, condominiumId) => {
      queryClient.invalidateQueries({
        queryKey: getGetCondominiumApiV1ClientsClientsCondominiumsCondominiumIdGetQueryKey(condominiumId),
      });
      queryClient.invalidateQueries({
        queryKey: getGetCondominiumStatsApiV1ClientsClientsCondominiumsStatsGetQueryKey(),
      });
    },
  });
}
