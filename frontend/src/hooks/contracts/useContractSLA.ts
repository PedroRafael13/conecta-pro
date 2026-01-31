/**
 * Hooks React Query - Contract SLA Reports
 * Gestão de Relatórios de SLA
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { contractSLAService } from '@/services/contracts';
import { contractKeys } from './useContracts';
import type {
  ContractSLAReportCreate,
  ContractSLAReportResponse,
  ContractSLAReportApprove,
  SLACalculation,
} from '@/types/generated/contracts/cRMContractsAPI.schemas';

/**
 * Query keys para SLA reports
 */
export const slaKeys = {
  all: ['sla-reports'] as const,
  lists: () => [...slaKeys.all, 'list'] as const,
  list: (contractId: string, params?: any) =>
    [...slaKeys.lists(), contractId, params] as const,
};

/**
 * Hook para listar relatórios de SLA
 */
export function useContractSLAReports(
  contractId: string,
  params?: { year?: number },
  enabled = true
) {
  return useQuery({
    queryKey: slaKeys.list(contractId, params),
    queryFn: () => contractSLAService.list(contractId, params),
    enabled: enabled && !!contractId,
  });
}

/**
 * Hook para criar relatório de SLA
 */
export function useCreateSLAReport() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      contractId,
      data,
    }: {
      contractId: string;
      data: ContractSLAReportCreate;
    }) => contractSLAService.create(contractId, data),
    onSuccess: (_, { contractId }) => {
      queryClient.invalidateQueries({ queryKey: slaKeys.list(contractId) });
      queryClient.invalidateQueries({ queryKey: contractKeys.detail(contractId) });
    },
  });
}

/**
 * Hook para aprovar relatório de SLA
 */
export function useApproveSLAReport() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      reportId,
      contractId,
      data,
    }: {
      reportId: string;
      contractId: string;
      data: ContractSLAReportApprove;
    }) => contractSLAService.approve(reportId, data),
    onSuccess: (_, { contractId }) => {
      queryClient.invalidateQueries({ queryKey: slaKeys.list(contractId) });
      queryClient.invalidateQueries({ queryKey: contractKeys.detail(contractId) });
    },
  });
}

/**
 * Hook para calcular SLA
 */
export function useCalculateSLA() {
  return useMutation({
    mutationFn: ({
      contractId,
      indicatorResults,
    }: {
      contractId: string;
      indicatorResults: Array<{
        name: string;
        target: number;
        actual: number;
        achieved: boolean;
        weight?: number;
      }>;
    }) => contractSLAService.calculate(contractId, indicatorResults),
  });
}
