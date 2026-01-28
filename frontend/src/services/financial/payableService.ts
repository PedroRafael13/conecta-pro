/**
 * Service: Payables Management
 *
 * Gestão de Contas a Pagar.
 * Cobertura: 22 endpoints
 */

import { getFinancialPayables } from '@/types/generated/financial/financial-payables/financial-payables';
import type {
  PayableAccountCreate,
  PayableAccountUpdate,
  PayableAccountResponse,
  PayableInstallmentCreate,
  PayablePaymentRequest,
  ListPayablesApiV1FinancialPayablesPayablesGetParams,
} from '@/types/generated/financial/models';

const payables = getFinancialPayables();

export const payableService = {
  // Payable Accounts
  async create(data: PayableAccountCreate): Promise<PayableAccountResponse> {
    const response = await payables.createPayableApiV1FinancialPayablesPayablesPost(
      data
    );
    return response.data;
  },

  async list(params: ListPayablesApiV1FinancialPayablesPayablesGetParams = {}) {
    const response = await payables.listPayablesApiV1FinancialPayablesPayablesGet(
      params
    );
    return response.data;
  },

  async getById(payableId: string): Promise<PayableAccountResponse> {
    const response = await payables.getPayableApiV1FinancialPayablesPayablesPayableIdGet(
      payableId
    );
    return response.data;
  },

  async update(
    payableId: string,
    data: PayableAccountUpdate
  ): Promise<PayableAccountResponse> {
    const response = await payables.updatePayableApiV1FinancialPayablesPayablesPayableIdPut(
      payableId,
      data
    );
    return response.data;
  },

  async delete(payableId: string): Promise<void> {
    await payables.deletePayableApiV1FinancialPayablesPayablesPayableIdDelete(
      payableId
    );
  },

  async getDashboard(condominioId: string) {
    const response = await payables.getPayablesDashboardApiV1FinancialPayablesPayablesDashboardGet(
      { condominio_id: condominioId }
    );
    return response.data;
  },

  // Installments
  async createInstallment(data: PayableInstallmentCreate) {
    const response = await payables.createInstallmentApiV1FinancialPayablesInstallmentsPost(
      data
    );
    return response.data;
  },

  async getInstallment(installmentId: string) {
    const response = await payables.getInstallmentApiV1FinancialPayablesInstallmentsInstallmentIdGet(
      installmentId
    );
    return response.data;
  },

  // Payments
  async processPayment(data: PayablePaymentRequest) {
    const response = await payables.processPaymentApiV1FinancialPayablesPaymentsPost(
      data
    );
    return response.data;
  },

  async cancelPayment(paymentId: string) {
    const response = await payables.cancelPaymentApiV1FinancialPayablesPaymentsPaymentIdCancelPost(
      paymentId
    );
    return response.data;
  },

  // Approvals
  async approve(payableId: string, observations?: string) {
    const response = await payables.approvePayableApiV1FinancialPayablesPayablesPayableIdApprovePost(
      payableId,
      { observations }
    );
    return response.data;
  },

  async reject(payableId: string, reason: string) {
    const response = await payables.rejectPayableApiV1FinancialPayablesPayablesPayableIdRejectPost(
      payableId,
      { reason }
    );
    return response.data;
  },

  // Reports
  async getAgingReport(condominioId: string) {
    const response = await payables.getAgingReportApiV1FinancialPayablesReportsAgingGet(
      { condominio_id: condominioId }
    );
    return response.data;
  },

  async exportToExcel(params: any) {
    const response = await payables.exportPayablesToExcelApiV1FinancialPayablesExportExcelGet(
      params
    );
    return response.data;
  },
};

export default payableService;
