/**
 * React Query Hooks - Reimbursement Items
 *
 * Hooks para gerenciamento de itens de reembolso
 */

import { useMutation, useQueryClient } from '@tanstack/react-query';
import { reimbursementItemService } from '@/services/reimbursement';
import { reimbursementKeys } from './useReimbursementRequests';
import type {
  ReimbursementItemCreate,
  ReimbursementItemUpdate,
} from '@/types/generated/reimbursement/models';

/**
 * Adiciona item a uma solicitação
 */
export function useCreateReimbursementItem() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ requestId, data }: { requestId: string; data: ReimbursementItemCreate }) =>
      reimbursementItemService.create(requestId, data),
    onSuccess: (_, variables) => {
      // Invalida detail da request (que inclui os itens)
      queryClient.invalidateQueries({ queryKey: reimbursementKeys.detail(variables.requestId) });
      queryClient.invalidateQueries({ queryKey: reimbursementKeys.lists() });
      queryClient.invalidateQueries({ queryKey: reimbursementKeys.myLists() });
    },
  });
}

/**
 * Atualiza um item
 */
export function useUpdateReimbursementItem() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      requestId,
      itemId,
      data,
    }: {
      requestId: string;
      itemId: string;
      data: ReimbursementItemUpdate;
    }) => reimbursementItemService.update(requestId, itemId, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: reimbursementKeys.detail(variables.requestId) });
      queryClient.invalidateQueries({ queryKey: reimbursementKeys.lists() });
      queryClient.invalidateQueries({ queryKey: reimbursementKeys.myLists() });
    },
  });
}

/**
 * Remove um item
 */
export function useDeleteReimbursementItem() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ requestId, itemId }: { requestId: string; itemId: string }) =>
      reimbursementItemService.delete(requestId, itemId),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: reimbursementKeys.detail(variables.requestId) });
      queryClient.invalidateQueries({ queryKey: reimbursementKeys.lists() });
      queryClient.invalidateQueries({ queryKey: reimbursementKeys.myLists() });
    },
  });
}
