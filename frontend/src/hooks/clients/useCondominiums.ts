/**
 * Hooks React Query - Condominium Management
 * Gestão de Condomínios
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { condominiumService } from '@/services/clients';
import type {
  CondominiumCreate,
  CondominiumUpdate,
} from '@/types/generated/clients/conectaPROMóduloCLIENTS.schemas';

/**
 * Query keys para cache
 */
export const condominiumKeys = {
  all: ['condominiums'] as const,
  lists: () => [...condominiumKeys.all, 'list'] as const,
  list: (clientId: string, filters?: any) =>
    [...condominiumKeys.lists(), clientId, filters] as const,
  details: () => [...condominiumKeys.all, 'detail'] as const,
  detail: (id: string) => [...condominiumKeys.details(), id] as const,
  stats: (clientId?: string) =>
    [...condominiumKeys.all, 'stats', clientId] as const,
};

/**
 * Hook para listar condomínios do cliente
 */
export function useCondominiums(
  clientId: string,
  params?: {
    skip?: number;
    limit?: number;
  },
  enabled = true
) {
  return useQuery({
    queryKey: condominiumKeys.list(clientId, params),
    queryFn: () => condominiumService.list(clientId, params),
    enabled: enabled && !!clientId,
  });
}

/**
 * Hook para obter condomínio por ID
 */
export function useCondominium(condominiumId: string, enabled = true) {
  return useQuery({
    queryKey: condominiumKeys.detail(condominiumId),
    queryFn: () => condominiumService.getById(condominiumId),
    enabled: enabled && !!condominiumId,
  });
}

/**
 * Hook para obter estatísticas de condomínios
 */
export function useCondominiumStats(clientId?: string) {
  return useQuery({
    queryKey: condominiumKeys.stats(clientId),
    queryFn: () => condominiumService.getStats(clientId),
  });
}

/**
 * Hook para criar condomínio
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
    }) => condominiumService.create(clientId, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({
        queryKey: condominiumKeys.list(variables.clientId),
      });
      queryClient.invalidateQueries({ queryKey: condominiumKeys.stats() });
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
    }) => condominiumService.update(condominiumId, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({
        queryKey: condominiumKeys.detail(variables.condominiumId),
      });
      queryClient.invalidateQueries({ queryKey: condominiumKeys.lists() });
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
      condominiumService.delete(condominiumId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: condominiumKeys.lists() });
      queryClient.invalidateQueries({ queryKey: condominiumKeys.stats() });
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
      condominiumService.activate(condominiumId),
    onSuccess: (_, condominiumId) => {
      queryClient.invalidateQueries({
        queryKey: condominiumKeys.detail(condominiumId),
      });
      queryClient.invalidateQueries({ queryKey: condominiumKeys.lists() });
      queryClient.invalidateQueries({ queryKey: condominiumKeys.stats() });
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
      condominiumService.startImplantation(condominiumId),
    onSuccess: (_, condominiumId) => {
      queryClient.invalidateQueries({
        queryKey: condominiumKeys.detail(condominiumId),
      });
      queryClient.invalidateQueries({ queryKey: condominiumKeys.stats() });
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
      condominiumService.finishImplantation(condominiumId),
    onSuccess: (_, condominiumId) => {
      queryClient.invalidateQueries({
        queryKey: condominiumKeys.detail(condominiumId),
      });
      queryClient.invalidateQueries({ queryKey: condominiumKeys.stats() });
    },
  });
}
