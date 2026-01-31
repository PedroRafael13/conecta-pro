/**
 * React Query Hooks - Reimbursement Attachments
 *
 * Hooks para gerenciamento de anexos/comprovantes
 */

import { useMutation, useQuery, useQueryClient, type UseQueryOptions } from '@tanstack/react-query';
import { reimbursementAttachmentService } from '@/services/reimbursement';
import { reimbursementKeys } from './useReimbursementRequests';
import type { ReimbursementAttachmentResponse } from '@/types/generated/reimbursement/models';

// Query Keys para attachments
export const attachmentKeys = {
  all: ['reimbursement-attachments'] as const,
  lists: () => [...attachmentKeys.all, 'list'] as const,
  list: (requestId: string, itemId?: string) =>
    [...attachmentKeys.lists(), requestId, itemId] as const,
};

/**
 * Lista anexos de uma solicitação
 */
export function useReimbursementAttachments(
  requestId: string,
  itemId?: string,
  options?: Omit<UseQueryOptions<ReimbursementAttachmentResponse[]>, 'queryKey' | 'queryFn'>
) {
  return useQuery({
    queryKey: attachmentKeys.list(requestId, itemId),
    queryFn: () => reimbursementAttachmentService.list(requestId, itemId),
    enabled: !!requestId,
    ...options,
  });
}

/**
 * Upload de anexo
 */
export function useUploadReimbursementAttachment() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      requestId,
      file,
      options,
    }: {
      requestId: string;
      file: File;
      options?: {
        itemId?: string;
        attachmentType?: string;
        description?: string;
      };
    }) => reimbursementAttachmentService.upload(requestId, file, options),
    onSuccess: (_, variables) => {
      // Invalida lista de attachments
      queryClient.invalidateQueries({
        queryKey: attachmentKeys.list(variables.requestId, variables.options?.itemId),
      });
      // Invalida detail da request
      queryClient.invalidateQueries({ queryKey: reimbursementKeys.detail(variables.requestId) });
    },
  });
}

/**
 * Remove anexo
 */
export function useDeleteReimbursementAttachment() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (attachmentId: string) => reimbursementAttachmentService.delete(attachmentId),
    onSuccess: () => {
      // Invalida todas as listas de attachments
      queryClient.invalidateQueries({ queryKey: attachmentKeys.lists() });
      // Invalida todos os details de requests
      queryClient.invalidateQueries({ queryKey: reimbursementKeys.details() });
    },
  });
}

/**
 * Download de anexo
 */
export function useDownloadReimbursementAttachment() {
  return useMutation({
    mutationFn: (attachmentId: string) => reimbursementAttachmentService.download(attachmentId),
    onSuccess: (blob, attachmentId) => {
      // Cria URL temporária para download
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `attachment-${attachmentId}`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    },
  });
}
