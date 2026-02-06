/**
 * React Query Hooks - Document Kit Items
 *
 * Hooks customizados para gerenciamento de itens dos kits.
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { toast } from 'sonner';
import {
  documentKitItemService,
  type ReorderItemsParams,
} from '@/services/document-kits/documentKitItemService';
import type {
  DocumentKitItemCreate,
  DocumentKitItemUpdate,
} from '@/types/generated/document-kits';
import { documentKitKeys } from './useDocumentKits';

// Query Keys
export const documentKitItemKeys = {
  all: ['document-kit-items'] as const,
  lists: () => [...documentKitItemKeys.all, 'list'] as const,
  list: (kit_id: string, condominio_id: string) =>
    [...documentKitItemKeys.lists(), kit_id, condominio_id] as const,
  details: () => [...documentKitItemKeys.all, 'detail'] as const,
  detail: (item_id: string, condominio_id: string) =>
    [...documentKitItemKeys.details(), item_id, condominio_id] as const,
};

/**
 * Hook para listar itens de um kit
 */
export function useKitItems(
  kit_id: string,
  condominio_id: string,
  only_active: boolean = true
) {
  return useQuery({
    queryKey: documentKitItemKeys.list(kit_id, condominio_id),
    queryFn: () =>
      documentKitItemService.listItems(kit_id, condominio_id, only_active),
    enabled: !!kit_id && !!condominio_id,
  });
}

/**
 * Hook para buscar um item por ID
 */
export function useKitItem(item_id: string, condominio_id: string) {
  return useQuery({
    queryKey: documentKitItemKeys.detail(item_id, condominio_id),
    queryFn: () => documentKitItemService.getItem(item_id, condominio_id),
    enabled: !!item_id && !!condominio_id,
  });
}

/**
 * Hook para adicionar item ao kit
 */
export function useAddKitItem() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      kit_id,
      data,
      condominio_id,
    }: {
      kit_id: string;
      data: DocumentKitItemCreate;
      condominio_id: string;
    }) => documentKitItemService.addItem(kit_id, data, condominio_id),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({
        queryKey: documentKitItemKeys.list(
          variables.kit_id,
          variables.condominio_id
        ),
      });
      queryClient.invalidateQueries({
        queryKey: documentKitKeys.detail(
          variables.kit_id,
          variables.condominio_id
        ),
      });
      toast.success('Item adicionado com sucesso!');
    },
    onError: (error: Error) => {
      toast.error(`Erro ao adicionar item: ${error.message}`);
    },
  });
}

/**
 * Hook para atualizar item
 */
export function useUpdateKitItem() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      item_id,
      data,
      condominio_id,
    }: {
      item_id: string;
      data: DocumentKitItemUpdate;
      condominio_id: string;
    }) => documentKitItemService.updateItem(item_id, data, condominio_id),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({
        queryKey: documentKitItemKeys.lists(),
      });
      queryClient.invalidateQueries({
        queryKey: documentKitItemKeys.detail(
          variables.item_id,
          variables.condominio_id
        ),
      });
      toast.success('Item atualizado com sucesso!');
    },
    onError: (error: Error) => {
      toast.error(`Erro ao atualizar item: ${error.message}`);
    },
  });
}

/**
 * Hook para deletar item
 */
export function useDeleteKitItem() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      item_id,
      condominio_id,
    }: {
      item_id: string;
      condominio_id: string;
    }) => documentKitItemService.deleteItem(item_id, condominio_id),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: documentKitItemKeys.lists(),
      });
      toast.success('Item removido com sucesso!');
    },
    onError: (error: Error) => {
      toast.error(`Erro ao remover item: ${error.message}`);
    },
  });
}

/**
 * Hook para reordenar itens
 */
export function useReorderKitItems() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (params: ReorderItemsParams) =>
      documentKitItemService.reorderItems(params),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({
        queryKey: documentKitItemKeys.list(
          variables.kit_id,
          variables.condominio_id
        ),
      });
      toast.success('Itens reordenados com sucesso!');
    },
    onError: (error: Error) => {
      toast.error(`Erro ao reordenar itens: ${error.message}`);
    },
  });
}
