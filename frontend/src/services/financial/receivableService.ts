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
  ReceivableInstallmentUpdate,
  ReceivableBulkPaymentRequest,
  ReceivablePaymentCreate,
  ReceivablePaymentReconcileRequest,
  ReceivableInstallmentResponse,
  ReceivablePaymentResponse,
  ListAccountsApiV1FinancialReceivablesReceivablesGetParams,
  GetStatsApiV1FinancialReceivablesReceivablesStatsGetParams,
  GetOverdueApiV1FinancialReceivablesReceivablesOverdueGetParams,
  GetDueSoonApiV1FinancialReceivablesReceivablesDueSoonGetParams,
  GetPendingInstallmentsApiV1FinancialReceivablesReceivablesInstallmentsPendingGetParams,
  GetCollectionPrioritiesApiV1FinancialReceivablesReceivablesAiCollectionPrioritiesGetParams,
  GetDelinquencyAnalysisApiV1FinancialReceivablesReceivablesAiDelinquencyAnalysisGetParams,
  GetCashFlowForecastApiV1FinancialReceivablesReceivablesAiCashFlowForecastGetParams,
} from '@/types/generated/financial/models';

const receivables = getFinancialReceivables();

export const receivableService = {
  // Receivable Accounts
  async create(data: ReceivableAccountCreate): Promise<ReceivableAccountResponse> {
    const response = await receivables.createAccountApiV1FinancialReceivablesReceivablesPost(data);
    return response.data;
  },

  async list(params: ListAccountsApiV1FinancialReceivablesReceivablesGetParams) {
    const response = await receivables.listAccountsApiV1FinancialReceivablesReceivablesGet(params);
    return response.data;
  },

  async getById(receivableId: string): Promise<ReceivableAccountResponse> {
    const response = await receivables.getAccountApiV1FinancialReceivablesReceivablesAccountIdGet(receivableId);
    return response.data;
  },

  async update(
    receivableId: string,
    data: ReceivableAccountUpdate
  ): Promise<ReceivableAccountResponse> {
    const response = await receivables.updateAccountApiV1FinancialReceivablesReceivablesAccountIdPut(
      receivableId,
      data
    );
    return response.data;
  },

  async delete(receivableId: string): Promise<void> {
    await receivables.deleteAccountApiV1FinancialReceivablesReceivablesAccountIdDelete(receivableId);
  },

  async getStats(params?: GetStatsApiV1FinancialReceivablesReceivablesStatsGetParams) {
    const response = await receivables.getStatsApiV1FinancialReceivablesReceivablesStatsGet(params);
    return response.data;
  },

  async getOverdue(params?: GetOverdueApiV1FinancialReceivablesReceivablesOverdueGetParams) {
    const response = await receivables.getOverdueApiV1FinancialReceivablesReceivablesOverdueGet(params);
    return response.data;
  },

  async getDueSoon(params?: GetDueSoonApiV1FinancialReceivablesReceivablesDueSoonGetParams) {
    const response = await receivables.getDueSoonApiV1FinancialReceivablesReceivablesDueSoonGet(params);
    return response.data;
  },

  // Installments
  async listInstallments(accountId: string): Promise<ReceivableInstallmentResponse[]> {
    const response = await receivables.listInstallmentsApiV1FinancialReceivablesReceivablesAccountIdInstallmentsGet(accountId);
    return response.data;
  },

  async getInstallment(installmentId: string): Promise<ReceivableInstallmentResponse> {
    const response = await receivables.getInstallmentApiV1FinancialReceivablesReceivablesInstallmentsInstallmentIdGet(installmentId);
    return response.data;
  },

  async updateInstallment(
    installmentId: string,
    data: ReceivableInstallmentUpdate
  ): Promise<ReceivableInstallmentResponse> {
    const response = await receivables.updateInstallmentApiV1FinancialReceivablesReceivablesInstallmentsInstallmentIdPut(
      installmentId,
      data
    );
    return response.data;
  },

  async getPendingInstallments(
    params: GetPendingInstallmentsApiV1FinancialReceivablesReceivablesInstallmentsPendingGetParams
  ): Promise<ReceivableInstallmentResponse[]> {
    const response = await receivables.getPendingInstallmentsApiV1FinancialReceivablesReceivablesInstallmentsPendingGet(params);
    return response.data;
  },

  // Payments
  async registerPayment(
    installmentId: string,
    data: ReceivablePaymentCreate
  ): Promise<ReceivablePaymentResponse> {
    const response = await receivables.registerPaymentApiV1FinancialReceivablesReceivablesInstallmentsInstallmentIdPayPost(
      installmentId,
      data
    );
    return response.data;
  },

  async bulkPayment(data: ReceivableBulkPaymentRequest) {
    const response = await receivables.bulkPaymentApiV1FinancialReceivablesReceivablesBulkPaymentPost(data);
    return response.data;
  },

  async reconcilePayment(
    paymentId: string,
    data: ReceivablePaymentReconcileRequest
  ): Promise<ReceivablePaymentResponse> {
    const response = await receivables.reconcilePaymentApiV1FinancialReceivablesReceivablesPaymentsPaymentIdReconcilePost(
      paymentId,
      data
    );
    return response.data;
  },

  // AI Features
  async getCollectionPriorities(
    params: GetCollectionPrioritiesApiV1FinancialReceivablesReceivablesAiCollectionPrioritiesGetParams
  ) {
    const response = await receivables.getCollectionPrioritiesApiV1FinancialReceivablesReceivablesAiCollectionPrioritiesGet(params);
    return response.data;
  },

  async getCashFlowForecast(
    params: GetCashFlowForecastApiV1FinancialReceivablesReceivablesAiCashFlowForecastGetParams
  ) {
    const response = await receivables.getCashFlowForecastApiV1FinancialReceivablesReceivablesAiCashFlowForecastGet(params);
    return response.data;
  },

  async getDelinquencyAnalysis(
    params: GetDelinquencyAnalysisApiV1FinancialReceivablesReceivablesAiDelinquencyAnalysisGetParams
  ) {
    const response = await receivables.getDelinquencyAnalysisApiV1FinancialReceivablesReceivablesAiDelinquencyAnalysisGet(params);
    return response.data;
  },

  async getCustomerRisk(customerId: string) {
    const response = await receivables.getCustomerRiskApiV1FinancialReceivablesReceivablesAiCustomerRiskCustomerIdGet(customerId);
    return response.data;
  },

  // Debt
  async getCustomerDebt(customerId: string) {
    const response = await receivables.getCustomerDebtApiV1FinancialReceivablesReceivablesDebtCustomerCustomerIdGet(customerId);
    return response.data;
  },

  async getUnitDebt(unidadeId: string) {
    const response = await receivables.getUnitDebtApiV1FinancialReceivablesReceivablesDebtUnitUnidadeIdGet(unidadeId);
    return response.data;
  },
};

export default receivableService;
