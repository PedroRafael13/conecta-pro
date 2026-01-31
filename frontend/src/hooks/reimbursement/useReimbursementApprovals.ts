/**
 * React Query Hooks - Reimbursement Approvals
 *
 * Hooks para fluxo de aprovação de reembolsos
 */

import { useMutation, useQuery, useQueryClient, type UseQueryOptions } from '@tanstack/react-query';
import { reimbursementApprovalService } from '@/services/reimbursement';
import { reimbursementKeys } from './useReimbursementRequests';
import type {
  PaginatedReimbursementResponse,
  ReimbursementApproveRequest,
  ReimbursementRejectRequest,
  ReimbursementReturnRequest,
} from '@/types/generated/reimbursement/models';

// Query Keys para approvals
export const approvalKeys = {
  all: ['reimbursement-approvals'] as const,
  pending: (params?: object) => [...approvalKeys.all, 'pending', params] as const,
};

/**
 * Lista solicitações pendentes de aprovação
 */
export function usePendingReimbursementApprovals(
  params?: Parameters<typeof reimbursementApprovalService.listPending>[0],
  options?: Omit<UseQueryOptions<PaginatedReimbursementResponse>, 'queryKey' | 'queryFn'>
) {
  return useQuery({
    queryKey: approvalKeys.pending(params),
    queryFn: () => reimbursementApprovalService.listPending(params),
    ...options,
  });
}

/**
 * Inicia análise de solicitação
 */
export function useStartReimbursementAnalysis() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (requestId: string) => reimbursementApprovalService.startAnalysis(requestId),
    onSuccess: (_, requestId) => {
      queryClient.invalidateQueries({ queryKey: reimbursementKeys.detail(requestId) });
      queryClient.invalidateQueries({ queryKey: approvalKeys.pending() });
      queryClient.invalidateQueries({ queryKey: reimbursementKeys.lists() });
    },
  });
}

/**
 * Aprova solicitação de reembolso
 */
export function useApproveReimbursement() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ requestId, data }: { requestId: string; data?: ReimbursementApproveRequest }) =>
      reimbursementApprovalService.approve(requestId, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: reimbursementKeys.detail(variables.requestId) });
      queryClient.invalidateQueries({ queryKey: approvalKeys.pending() });
      queryClient.invalidateQueries({ queryKey: reimbursementKeys.lists() });
      queryClient.invalidateQueries({ queryKey: reimbursementKeys.stats() });
    },
  });
}

/**
 * Rejeita solicitação de reembolso
 */
export function useRejectReimbursement() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ requestId, data }: { requestId: string; data: ReimbursementRejectRequest }) =>
      reimbursementApprovalService.reject(requestId, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: reimbursementKeys.detail(variables.requestId) });
      queryClient.invalidateQueries({ queryKey: approvalKeys.pending() });
      queryClient.invalidateQueries({ queryKey: reimbursementKeys.lists() });
      queryClient.invalidateQueries({ queryKey: reimbursementKeys.stats() });
    },
  });
}

/**
 * Devolve solicitação para rascunho
 */
export function useReturnReimbursementToDraft() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ requestId, data }: { requestId: string; data: ReimbursementReturnRequest }) =>
      reimbursementApprovalService.returnToDraft(requestId, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: reimbursementKeys.detail(variables.requestId) });
      queryClient.invalidateQueries({ queryKey: approvalKeys.pending() });
      queryClient.invalidateQueries({ queryKey: reimbursementKeys.lists() });
      queryClient.invalidateQueries({ queryKey: reimbursementKeys.myLists() });
    },
  });
}
