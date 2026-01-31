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
  PayableInstallmentUpdate,
  PayableBulkPaymentRequest,
  PayableBulkApproveRequest,
  PayablePaymentCreate,
  PayablePaymentReconcileRequest,
  PayableInstallmentResponse,
  PayablePaymentResponse,
  ListAccountsApiV1FinancialPayablesPayablesGetParams,
  GetStatsApiV1FinancialPayablesPayablesStatsGetParams,
  GetOverdueApiV1FinancialPayablesPayablesOverdueGetParams,
  GetDueSoonApiV1FinancialPayablesPayablesDueSoonGetParams,
  GetPendingInstallmentsApiV1FinancialPayablesPayablesInstallmentsPendingGetParams,
  ApproveAccountApiV1FinancialPayablesPayablesAccountIdApprovePostParams,
  RejectAccountApiV1FinancialPayablesPayablesAccountIdRejectPostParams,
} from '@/types/generated/financial/models';

const payables = getFinancialPayables();

export const payableService = {
  // Payable Accounts
  async create(data: PayableAccountCreate): Promise<PayableAccountResponse> {
    const response = await payables.createAccountApiV1FinancialPayablesPayablesPost(data);
    return response.data;
  },

  async list(params: ListAccountsApiV1FinancialPayablesPayablesGetParams) {
    const response = await payables.listAccountsApiV1FinancialPayablesPayablesGet(params);
    return response.data;
  },

  async getById(payableId: string): Promise<PayableAccountResponse> {
    const response = await payables.getAccountApiV1FinancialPayablesPayablesAccountIdGet(payableId);
    return response.data;
  },

  async update(
    payableId: string,
    data: PayableAccountUpdate
  ): Promise<PayableAccountResponse> {
    const response = await payables.updateAccountApiV1FinancialPayablesPayablesAccountIdPut(
      payableId,
      data
    );
    return response.data;
  },

  async delete(payableId: string): Promise<void> {
    await payables.deleteAccountApiV1FinancialPayablesPayablesAccountIdDelete(payableId);
  },

  async getStats(params?: GetStatsApiV1FinancialPayablesPayablesStatsGetParams) {
    const response = await payables.getStatsApiV1FinancialPayablesPayablesStatsGet(params);
    return response.data;
  },

  async getOverdue(params?: GetOverdueApiV1FinancialPayablesPayablesOverdueGetParams) {
    const response = await payables.getOverdueApiV1FinancialPayablesPayablesOverdueGet(params);
    return response.data;
  },

  async getDueSoon(params: GetDueSoonApiV1FinancialPayablesPayablesDueSoonGetParams) {
    const response = await payables.getDueSoonApiV1FinancialPayablesPayablesDueSoonGet(params);
    return response.data;
  },

  // Installments
  async listInstallments(accountId: string): Promise<PayableInstallmentResponse[]> {
    const response = await payables.listInstallmentsApiV1FinancialPayablesPayablesAccountIdInstallmentsGet(accountId);
    return response.data;
  },

  async updateInstallment(
    installmentId: string,
    data: PayableInstallmentUpdate
  ): Promise<PayableInstallmentResponse> {
    const response = await payables.updateInstallmentApiV1FinancialPayablesPayablesInstallmentsInstallmentIdPut(
      installmentId,
      data
    );
    return response.data;
  },

  async getPendingInstallments(
    params: GetPendingInstallmentsApiV1FinancialPayablesPayablesInstallmentsPendingGetParams
  ): Promise<PayableInstallmentResponse[]> {
    const response = await payables.getPendingInstallmentsApiV1FinancialPayablesPayablesInstallmentsPendingGet(params);
    return response.data;
  },

  // Payments
  async registerPayment(
    installmentId: string,
    data: PayablePaymentCreate
  ): Promise<PayablePaymentResponse> {
    const response = await payables.registerPaymentApiV1FinancialPayablesPayablesInstallmentsInstallmentIdPayPost(
      installmentId,
      data
    );
    return response.data;
  },

  async bulkPayment(data: PayableBulkPaymentRequest) {
    const response = await payables.bulkPaymentApiV1FinancialPayablesPayablesBulkPaymentPost(data);
    return response.data;
  },

  async reconcilePayment(
    paymentId: string,
    data: PayablePaymentReconcileRequest
  ): Promise<PayablePaymentResponse> {
    const response = await payables.reconcilePaymentApiV1FinancialPayablesPayablesPaymentsPaymentIdReconcilePost(
      paymentId,
      data
    );
    return response.data;
  },

  // Approvals
  async approve(
    accountId: string,
    params?: ApproveAccountApiV1FinancialPayablesPayablesAccountIdApprovePostParams
  ): Promise<PayableAccountResponse> {
    const response = await payables.approveAccountApiV1FinancialPayablesPayablesAccountIdApprovePost(
      accountId,
      params
    );
    return response.data;
  },

  async bulkApprove(data: PayableBulkApproveRequest) {
    const response = await payables.bulkApproveApiV1FinancialPayablesPayablesBulkApprovePost(data);
    return response.data;
  },

  async reject(
    accountId: string,
    params: RejectAccountApiV1FinancialPayablesPayablesAccountIdRejectPostParams
  ): Promise<PayableAccountResponse> {
    const response = await payables.rejectAccountApiV1FinancialPayablesPayablesAccountIdRejectPost(
      accountId,
      params
    );
    return response.data;
  },
};

export default payableService;
