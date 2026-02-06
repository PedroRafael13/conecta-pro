/**
 * Hook: usePayments
 *
 * Gerenciamento de pagamentos de diaristas.
 */

import { useQuery } from '@tanstack/react-query';
import { diaristCoreService } from '@/services/diarists';
import type { PaymentStatus } from '@/api/diarists/generated/models';

/**
 * Hook para listar pagamentos
 */
export function useListPayments(params?: {
  diaristId?: string;
  status?: PaymentStatus;
  dataInicio?: string;
  dataFim?: string;
  skip?: number;
  limit?: number;
}) {
  return useQuery({
    queryKey: ['diarists', 'payments', 'list', params],
    queryFn: () => diaristCoreService.listPayments(params),
  });
}

/**
 * Hook para buscar pagamento por ID
 */
export function usePayment(paymentId: string) {
  return useQuery({
    queryKey: ['diarists', 'payments', 'detail', paymentId],
    queryFn: () => diaristCoreService.getPayment(paymentId),
    enabled: !!paymentId,
  });
}

/**
 * Hook para pagamentos pendentes
 */
export function usePendingPayments() {
  return useQuery({
    queryKey: ['diarists', 'payments', 'pending'],
    queryFn: () => diaristCoreService.getPendingPayments(),
  });
}

/**
 * Hook para relatório de folha de pagamento
 */
export function usePayrollReport(competencia: string, condominioId?: string) {
  return useQuery({
    queryKey: ['diarists', 'payments', 'payroll', competencia, condominioId],
    queryFn: () => diaristCoreService.getPayrollReport(competencia, condominioId),
    enabled: !!competencia && /^\d{4}-\d{2}$/.test(competencia),
  });
}
