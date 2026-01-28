/**
 * Service: Receivables Management
 *
 * Gestão de Contas a Receber.
 * Cobertura: 33 endpoints
 */

import { getFinancialReceivables } from '@/types/generated/financial/financial-receivables/financial-receivables';
import type {
  ReceivableAccountCreate,
  ReceivableAccountUpdate,
  ReceivableAccountResponse,
  ReceivableInstallmentCreate,
  ReceivablePaymentRequest,
  ListReceivablesApiV1FinancialReceivablesReceivablesGetParams,
} from '@/types/generated/financial/models';

const receivables = getFinancialReceivables();

export const receivableService = {
  // Receivable Accounts
  async create(data: ReceivableAccountCreate): Promise<ReceivableAccountResponse> {
    const response = await receivables.createReceivableApiV1FinancialReceivablesReceivablesPost(
      data
    );
    return response.data;
  },

  async list(
    params: ListReceivablesApiV1FinancialReceivablesReceivablesGetParams = {}
  ) {
    const response = await receivables.listReceivablesApiV1FinancialReceivablesReceivablesGet(
      params
    );
    return response.data;
  },

  async getById(receivableId: string): Promise<ReceivableAccountResponse> {
    const response = await receivables.getReceivableApiV1FinancialReceivablesReceivablesReceivableIdGet(
      receivableId
    );
    return response.data;
  },

  async update(
    receivableId: string,
    data: ReceivableAccountUpdate
  ): Promise<ReceivableAccountResponse> {
    const response = await receivables.updateReceivableApiV1FinancialReceivablesReceivablesReceivableIdPut(
      receivableId,
      data
    );
    return response.data;
  },

  async delete(receivableId: string): Promise<void> {
    await receivables.deleteReceivableApiV1FinancialReceivablesReceivablesReceivableIdDelete(
      receivableId
    );
  },

  async getDashboard(condominioId: string) {
    const response = await receivables.getReceivablesDashboardApiV1FinancialReceivablesReceivablesDashboardGet(
      { condominio_id: condominioId }
    );
    return response.data;
  },

  // Installments
  async createInstallment(data: ReceivableInstallmentCreate) {
    const response = await receivables.createInstallmentApiV1FinancialReceivablesInstallmentsPost(
      data
    );
    return response.data;
  },

  async getInstallment(installmentId: string) {
    const response = await receivables.getInstallmentApiV1FinancialReceivablesInstallmentsInstallmentIdGet(
      installmentId
    );
    return response.data;
  },

  // Payments
  async processPayment(data: ReceivablePaymentRequest) {
    const response = await receivables.processPaymentApiV1FinancialReceivablesPaymentsPost(
      data
    );
    return response.data;
  },

  async cancelPayment(paymentId: string) {
    const response = await receivables.cancelPaymentApiV1FinancialReceivablesPaymentsPaymentIdCancelPost(
      paymentId
    );
    return response.data;
  },

  // Billing
  async generateBilling(condominioId: string, referenceMonth: string) {
    const response = await receivables.generateBillingApiV1FinancialReceivablesBillingGeneratePost(
      { condominio_id: condominioId, reference_month: referenceMonth }
    );
    return response.data;
  },

  async sendBoleto(receivableId: string) {
    const response = await receivables.sendBoletoApiV1FinancialReceivablesReceivablesReceivableIdBoletoSendPost(
      receivableId
    );
    return response.data;
  },

  async printBoleto(receivableId: string) {
    const response = await receivables.printBoletoApiV1FinancialReceivablesReceivablesReceivableIdBoletoPrintGet(
      receivableId
    );
    return response.data;
  },

  // Reports
  async getAgingReport(condominioId: string) {
    const response = await receivables.getAgingReportApiV1FinancialReceivablesReportsAgingGet(
      { condominio_id: condominioId }
    );
    return response.data;
  },

  async getDefaultersReport(condominioId: string) {
    const response = await receivables.getDefaultersReportApiV1FinancialReceivablesReportsDefaultersGet(
      { condominio_id: condominioId }
    );
    return response.data;
  },

  async exportToExcel(params: any) {
    const response = await receivables.exportReceivablesToExcelApiV1FinancialReceivablesExportExcelGet(
      params
    );
    return response.data;
  },
};

export default receivableService;
