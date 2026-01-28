/**
 * Hook: useSuppliers
 *
 * React Query hooks para gerenciamento de fornecedores.
 * Cobertura: 11 endpoints
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { supplierService } from '@/services/financial';
import type {
  SupplierCreate,
  SupplierUpdate,
  SupplierResponse,
  SupplierListResponse,
} from '@/types/generated/financial/models';

// Query Keys
export const supplierKeys = {
  all: ['suppliers'] as const,
  lists: () => [...supplierKeys.all, 'list'] as const,
  list: (filters: any) => [...supplierKeys.lists(), filters] as const,
  details: () => [...supplierKeys.all, 'detail'] as const,
  detail: (id: string) => [...supplierKeys.details(), id] as const,
  stats: (condominioId: string) =>
    [...supplierKeys.all, 'stats', condominioId] as const,
  history: (id: string) => [...supplierKeys.all, 'history', id] as const,
};

/**
 * Hook para listar fornecedores
 */
export function useSuppliers(params: any = {}) {
  return useQuery({
    queryKey: supplierKeys.list(params),
    queryFn: () => supplierService.list(params),
  });
}

/**
 * Hook para buscar fornecedor por ID
 */
export function useSupplier(supplierId: string, enabled = true) {
  return useQuery({
    queryKey: supplierKeys.detail(supplierId),
    queryFn: () => supplierService.getById(supplierId),
    enabled: enabled && !!supplierId,
  });
}

/**
 * Hook para estatísticas de fornecedores
 */
export function useSupplierStats(condominioId: string) {
  return useQuery({
    queryKey: supplierKeys.stats(condominioId),
    queryFn: () => supplierService.getStats({ condominio_id: condominioId }),
    enabled: !!condominioId,
  });
}

/**
 * Hook para histórico do fornecedor
 */
export function useSupplierHistory(supplierId: string, enabled = true) {
  return useQuery({
    queryKey: supplierKeys.history(supplierId),
    queryFn: () => supplierService.getHistory(supplierId),
    enabled: enabled && !!supplierId,
  });
}

/**
 * Hook para criar fornecedor
 */
export function useCreateSupplier() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: SupplierCreate) => supplierService.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: supplierKeys.lists() });
    },
  });
}

/**
 * Hook para atualizar fornecedor
 */
export function useUpdateSupplier() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      id,
      data,
    }: {
      id: string;
      data: SupplierUpdate;
    }) => supplierService.update(id, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: supplierKeys.lists() });
      queryClient.invalidateQueries({
        queryKey: supplierKeys.detail(variables.id),
      });
    },
  });
}

/**
 * Hook para deletar fornecedor
 */
export function useDeleteSupplier() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (supplierId: string) => supplierService.delete(supplierId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: supplierKeys.lists() });
    },
  });
}

/**
 * Hook para qualificar fornecedor
 */
export function useQualifySupplier() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      id,
      data,
    }: {
      id: string;
      data: any;
    }) => supplierService.qualify(id, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({
        queryKey: supplierKeys.detail(variables.id),
      });
    },
  });
}

/**
 * Hook para bloquear fornecedor
 */
export function useBlockSupplier() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      id,
      reason,
    }: {
      id: string;
      reason: string;
    }) => supplierService.block(id, { reason }),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({
        queryKey: supplierKeys.detail(variables.id),
      });
      queryClient.invalidateQueries({ queryKey: supplierKeys.lists() });
    },
  });
}

/**
 * Hook para desbloquear fornecedor
 */
export function useUnblockSupplier() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (supplierId: string) => supplierService.unblock(supplierId),
    onSuccess: (_, supplierId) => {
      queryClient.invalidateQueries({
        queryKey: supplierKeys.detail(supplierId),
      });
      queryClient.invalidateQueries({ queryKey: supplierKeys.lists() });
    },
  });
}

/**
 * Hook para busca rápida de fornecedores
 */
export function useSearchSuppliers(query: string, enabled = true) {
  return useQuery({
    queryKey: [...supplierKeys.all, 'search', query],
    queryFn: () => supplierService.search({ q: query }),
    enabled: enabled && query.length >= 2,
  });
}
