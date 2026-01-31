/**
 * Custom hooks React Query para Document Kits
 * Criado manualmente pois não há schema OpenAPI para este módulo
 */
import {
  useMutation,
  useQuery,
  useQueryClient,
  type UseMutationOptions,
  type UseQueryOptions,
} from '@tanstack/react-query';

import {
  documentKitsService,
  type DocumentKit,
  type DocumentKitCreate,
  type DocumentKitUpdate,
  type DocumentKitStats,
  type DocumentKitItem,
} from '@/lib/services/document-kits';
import type { PaginatedResponse } from '@/lib/services/types';

// Query Keys
export const documentKitsKeys = {
  all: ['document-kits'] as const,
  lists: () => [...documentKitsKeys.all, 'list'] as const,
  list: (page: number, pageSize: number, category?: string) =>
    [...documentKitsKeys.lists(), { page, pageSize, category }] as const,
  details: () => [...documentKitsKeys.all, 'detail'] as const,
  detail: (id: string) => [...documentKitsKeys.details(), id] as const,
  stats: () => [...documentKitsKeys.all, 'stats'] as const,
  items: (kitId: string) => [...documentKitsKeys.all, 'items', kitId] as const,
};

// Hooks de Query

/**
 * Hook para listar kits de documentos
 */
export const useListDocumentKits = (
  page: number = 1,
  pageSize: number = 20,
  category?: string,
  options?: Omit<UseQueryOptions<PaginatedResponse<DocumentKit>>, 'queryKey' | 'queryFn'>
) => {
  return useQuery({
    queryKey: documentKitsKeys.list(page, pageSize, category),
    queryFn: () => documentKitsService.list(page, pageSize, category),
    ...options,
  });
};

/**
 * Hook para buscar kit por ID
 */
export const useDocumentKit = (
  id: string,
  options?: Omit<UseQueryOptions<DocumentKit>, 'queryKey' | 'queryFn'>
) => {
  return useQuery({
    queryKey: documentKitsKeys.detail(id),
    queryFn: () => documentKitsService.getById(id),
    enabled: !!id,
    ...options,
  });
};

/**
 * Hook para buscar estatísticas
 */
export const useDocumentKitsStats = (
  options?: Omit<UseQueryOptions<DocumentKitStats>, 'queryKey' | 'queryFn'>
) => {
  return useQuery({
    queryKey: documentKitsKeys.stats(),
    queryFn: () => documentKitsService.getStats(),
    ...options,
  });
};

/**
 * Hook para listar itens de um kit
 */
export const useDocumentKitItems = (
  kitId: string,
  options?: Omit<UseQueryOptions<DocumentKitItem[]>, 'queryKey' | 'queryFn'>
) => {
  return useQuery({
    queryKey: documentKitsKeys.items(kitId),
    queryFn: () => documentKitsService.getItems(kitId),
    enabled: !!kitId,
    ...options,
  });
};

// Hooks de Mutation

/**
 * Hook para criar kit
 */
export const useCreateDocumentKit = (
  options?: UseMutationOptions<DocumentKit, Error, DocumentKitCreate>
) => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: DocumentKitCreate) => documentKitsService.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: documentKitsKeys.lists() });
      queryClient.invalidateQueries({ queryKey: documentKitsKeys.stats() });
    },
    ...options,
  });
};

/**
 * Hook para atualizar kit
 */
export const useUpdateDocumentKit = (
  options?: UseMutationOptions<DocumentKit, Error, { id: string; data: DocumentKitUpdate }>
) => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: DocumentKitUpdate }) =>
      documentKitsService.update(id, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: documentKitsKeys.lists() });
      queryClient.invalidateQueries({ queryKey: documentKitsKeys.detail(variables.id) });
      queryClient.invalidateQueries({ queryKey: documentKitsKeys.stats() });
    },
    ...options,
  });
};

/**
 * Hook para excluir kit
 */
export const useDeleteDocumentKit = (
  options?: UseMutationOptions<void, Error, string>
) => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => documentKitsService.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: documentKitsKeys.lists() });
      queryClient.invalidateQueries({ queryKey: documentKitsKeys.stats() });
    },
    ...options,
  });
};

/**
 * Hook para ativar kit
 */
export const useActivateDocumentKit = (
  options?: UseMutationOptions<DocumentKit, Error, string>
) => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => documentKitsService.activate(id),
    onSuccess: (_, id) => {
      queryClient.invalidateQueries({ queryKey: documentKitsKeys.lists() });
      queryClient.invalidateQueries({ queryKey: documentKitsKeys.detail(id) });
      queryClient.invalidateQueries({ queryKey: documentKitsKeys.stats() });
    },
    ...options,
  });
};

/**
 * Hook para desativar kit
 */
export const useDeactivateDocumentKit = (
  options?: UseMutationOptions<DocumentKit, Error, string>
) => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => documentKitsService.deactivate(id),
    onSuccess: (_, id) => {
      queryClient.invalidateQueries({ queryKey: documentKitsKeys.lists() });
      queryClient.invalidateQueries({ queryKey: documentKitsKeys.detail(id) });
      queryClient.invalidateQueries({ queryKey: documentKitsKeys.stats() });
    },
    ...options,
  });
};

/**
 * Hook para duplicar kit
 */
export const useDuplicateDocumentKit = (
  options?: UseMutationOptions<DocumentKit, Error, { id: string; newName?: string }>
) => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, newName }: { id: string; newName?: string }) =>
      documentKitsService.duplicate(id, newName),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: documentKitsKeys.lists() });
      queryClient.invalidateQueries({ queryKey: documentKitsKeys.stats() });
    },
    ...options,
  });
};

/**
 * Hook para adicionar item ao kit
 */
export const useAddDocumentKitItem = (
  options?: UseMutationOptions<DocumentKitItem, Error, { kitId: string; item: Omit<DocumentKitItem, 'id'> }>
) => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ kitId, item }: { kitId: string; item: Omit<DocumentKitItem, 'id'> }) =>
      documentKitsService.addItem(kitId, item),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: documentKitsKeys.items(variables.kitId) });
      queryClient.invalidateQueries({ queryKey: documentKitsKeys.detail(variables.kitId) });
    },
    ...options,
  });
};

/**
 * Hook para remover item do kit
 */
export const useRemoveDocumentKitItem = (
  options?: UseMutationOptions<void, Error, { itemId: string; kitId: string }>
) => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ itemId }: { itemId: string; kitId: string }) =>
      documentKitsService.removeItem(itemId),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: documentKitsKeys.items(variables.kitId) });
      queryClient.invalidateQueries({ queryKey: documentKitsKeys.detail(variables.kitId) });
    },
    ...options,
  });
};

/**
 * Hook para atualizar item do kit
 */
export const useUpdateDocumentKitItem = (
  options?: UseMutationOptions<DocumentKitItem, Error, { itemId: string; kitId: string; item: Partial<DocumentKitItem> }>
) => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ itemId, item }: { itemId: string; kitId: string; item: Partial<DocumentKitItem> }) =>
      documentKitsService.updateItem(itemId, item),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: documentKitsKeys.items(variables.kitId) });
      queryClient.invalidateQueries({ queryKey: documentKitsKeys.detail(variables.kitId) });
    },
    ...options,
  });
};
