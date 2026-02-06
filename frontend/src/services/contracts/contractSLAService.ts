/**
 * Service Layer - Contract SLA Reports
 * Gestão de Relatórios de SLA
 */

import { customInstance } from '@/lib/axios-instance';
import type {
  ContractSLAReportCreate,
  ContractSLAReportResponse,
  ContractSLAReportApprove,
  SLACalculation,
} from '@/types/generated/contracts/cRMContractsAPI.schemas';

const BASE_URL = '/api/v1/contracts';

/**
 * Service de SLA Reports
 */
export const contractSLAService = {
  /**
   * Cria relatório de SLA mensal
   */
  create: async (
    contractId: string,
    data: ContractSLAReportCreate
  ): Promise<ContractSLAReportResponse> => {
    return await customInstance.post<ContractSLAReportResponse>(
      `${BASE_URL}/${contractId}/sla-reports`,
      data
    );
  },

  /**
   * Lista relatórios de SLA do contrato
   */
  list: async (
    contractId: string,
    params?: { year?: number }
  ): Promise<ContractSLAReportResponse[]> => {
    return await customInstance.get<ContractSLAReportResponse[]>(
      `${BASE_URL}/${contractId}/sla-reports`,
      { params }
    );
  },

  /**
   * Aprova ou disputa relatório de SLA
   */
  approve: async (
    reportId: string,
    data: ContractSLAReportApprove
  ): Promise<ContractSLAReportResponse> => {
    return await customInstance.post<ContractSLAReportResponse>(
      `${BASE_URL}/sla-reports/${reportId}/approve`,
      data
    );
  },

  /**
   * Calcula SLA do contrato (simulação)
   */
  calculate: async (
    contractId: string,
    indicatorResults: Array<{
      name: string;
      target: number;
      actual: number;
      achieved: boolean;
      weight?: number;
    }>
  ): Promise<SLACalculation> => {
    return await customInstance.post<SLACalculation>(
      `${BASE_URL}/${contractId}/calculate-sla`,
      indicatorResults
    );
  },
};
