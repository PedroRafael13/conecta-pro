/**
 * Hooks React Query - Client Management
 * Gestão de Clientes
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { clientService } from '@/services/clients';
import type {
  ClientCreate,
  ClientUpdate,
  ClientResponse,
  ClientListResponse,
  ClientStats,
} from '@/types/generated/clients/conectaPROMóduloCLIENTS.schemas';

/**
 * Query keys para cache
 */
export const clientKeys = {
  all: ['clients'] as const,
  lists: () => [...clientKeys.all, 'list'] as const,
  list: (filters?: any) => [...clientKeys.lists(), filters] as const,
  details: () => [...clientKeys.all, 'detail'] as const,
  detail: (id: string) => [...clientKeys.details(), id] as const,
  stats: () => [...clientKeys.all, 'stats'] as const,
};

/**
 * Hook para listar clientes
 */
export function useClients(params?: {
  skip?: number;
  limit?: number;
  type?: string;
  status?: string;
  segment?: string;
  is_defaulter?: boolean;
  is_vip?: boolean;
  guardian_enabled?: boolean;
  plus_enabled?: boolean;
  city?: string;
  state?: string;
  search?: string;
  order_by?: string;
  order_desc?: boolean;
}) {
  return useQuery({
    queryKey: clientKeys.list(params),
    queryFn: () => clientService.list(params),
  });
}

/**
 * Hook para obter estatísticas de clientes
 */
export function useClientStats() {
  return useQuery({
    queryKey: clientKeys.stats(),
    queryFn: () => clientService.getStats(),
  });
}

/**
 * Hook para obter cliente por ID
 */
export function useClient(clientId: string, enabled = true) {
  return useQuery({
    queryKey: clientKeys.detail(clientId),
    queryFn: () => clientService.getById(clientId),
    enabled: enabled && !!clientId,
  });
}

/**
 * Hook para obter cliente completo (com relações)
 */
export function useClientFull(clientId: string, enabled = true) {
  return useQuery({
    queryKey: [...clientKeys.detail(clientId), 'full'],
    queryFn: () => clientService.getFullById(clientId),
    enabled: enabled && !!clientId,
  });
}

/**
 * Hook para criar cliente
 */
export function useCreateClient() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: ClientCreate) => clientService.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: clientKeys.lists() });
      queryClient.invalidateQueries({ queryKey: clientKeys.stats() });
    },
  });
}

/**
 * Hook para atualizar cliente
 */
export function useUpdateClient() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ clientId, data }: { clientId: string; data: ClientUpdate }) =>
      clientService.update(clientId, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({
        queryKey: clientKeys.detail(variables.clientId),
      });
      queryClient.invalidateQueries({ queryKey: clientKeys.lists() });
    },
  });
}

/**
 * Hook para deletar cliente
 */
export function useDeleteClient() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (clientId: string) => clientService.delete(clientId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: clientKeys.lists() });
      queryClient.invalidateQueries({ queryKey: clientKeys.stats() });
    },
  });
}

/**
 * Hook para ativar cliente
 */
export function useActivateClient() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (clientId: string) => clientService.activate(clientId),
    onSuccess: (_, clientId) => {
      queryClient.invalidateQueries({ queryKey: clientKeys.detail(clientId) });
      queryClient.invalidateQueries({ queryKey: clientKeys.lists() });
      queryClient.invalidateQueries({ queryKey: clientKeys.stats() });
    },
  });
}

/**
 * Hook para suspender cliente
 */
export function useSuspendClient() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ clientId, reason }: { clientId: string; reason?: string }) =>
      clientService.suspend(clientId, reason),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({
        queryKey: clientKeys.detail(variables.clientId),
      });
      queryClient.invalidateQueries({ queryKey: clientKeys.lists() });
      queryClient.invalidateQueries({ queryKey: clientKeys.stats() });
    },
  });
}

/**
 * Hook para bloquear cliente
 */
export function useBlockClient() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ clientId, reason }: { clientId: string; reason?: string }) =>
      clientService.block(clientId, reason),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({
        queryKey: clientKeys.detail(variables.clientId),
      });
      queryClient.invalidateQueries({ queryKey: clientKeys.lists() });
      queryClient.invalidateQueries({ queryKey: clientKeys.stats() });
    },
  });
}

/**
 * Hook para marcar cliente como inadimplente
 */
export function useSetDefaulter() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      clientId,
      debtAmount,
    }: {
      clientId: string;
      debtAmount: number;
    }) => clientService.setDefaulter(clientId, debtAmount),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({
        queryKey: clientKeys.detail(variables.clientId),
      });
      queryClient.invalidateQueries({ queryKey: clientKeys.lists() });
      queryClient.invalidateQueries({ queryKey: clientKeys.stats() });
    },
  });
}

/**
 * Hook para remover status de inadimplente
 */
export function useClearDefaulter() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (clientId: string) => clientService.clearDefaulter(clientId),
    onSuccess: (_, clientId) => {
      queryClient.invalidateQueries({ queryKey: clientKeys.detail(clientId) });
      queryClient.invalidateQueries({ queryKey: clientKeys.lists() });
      queryClient.invalidateQueries({ queryKey: clientKeys.stats() });
    },
  });
}

/**
 * Hook para habilitar Guardian
 */
export function useEnableGuardian() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      clientId,
      guardianClientId,
    }: {
      clientId: string;
      guardianClientId: string;
    }) => clientService.enableGuardian(clientId, guardianClientId),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({
        queryKey: clientKeys.detail(variables.clientId),
      });
    },
  });
}

/**
 * Hook para habilitar Conecta Plus
 */
export function useEnablePlus() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      clientId,
      plusClientId,
    }: {
      clientId: string;
      plusClientId: string;
    }) => clientService.enablePlus(clientId, plusClientId),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({
        queryKey: clientKeys.detail(variables.clientId),
      });
    },
  });
}
