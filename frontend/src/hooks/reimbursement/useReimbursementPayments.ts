/**
 * React Query Hooks - Reimbursement Payments
 *
 * Hooks para processamento financeiro de reembolsos
 */

import { useMutation, useQuery, useQueryClient, type UseQueryOptions } from '@tanstack/react-query';
import { reimbursementPaymentService } from '@/services/reimbursement';
import { reimbursementKeys } from './useReimbursementRequests';
import type {
  PaginatedReimbursementResponse,
  ReimbursementProcessRequest,
} from '@/types/generated/reimbursement/models';

// Query Keys para payments
export const paymentKeys = {
  all: ['reimbursement-payments'] as const,
  readyForPayment: (params?: object) => [...paymentKeys.all, 'ready', params] as const,
};

/**
 * Lista solicitações prontas para pagamento
 */
export function useReadyForPaymentReimbursements(
  params?: Parameters<typeof reimbursementPaymentService.listReadyForPayment>[0],
  options?: Omit<UseQueryOptions<PaginatedReimbursementResponse>, 'queryKey' | 'queryFn'>
) {
  return useQuery({
    queryKey: paymentKeys.readyForPayment(params),
    queryFn: () => reimbursementPaymentService.listReadyForPayment(params),
    ...options,
  });
}

/**
 * Processa pagamento de reembolso
 * Gera conta a pagar no financeiro
 */
export function useProcessReimbursementPayment() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ requestId, data }: { requestId: string; data?: ReimbursementProcessRequest }) =>
      reimbursementPaymentService.process(requestId, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: reimbursementKeys.detail(variables.requestId) });
      queryClient.invalidateQueries({ queryKey: paymentKeys.readyForPayment() });
      queryClient.invalidateQueries({ queryKey: reimbursementKeys.lists() });
      queryClient.invalidateQueries({ queryKey: reimbursementKeys.stats() });
    },
  });
}
