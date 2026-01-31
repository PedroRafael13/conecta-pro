/**
 * Service: Bank Transaction Management
 * Cobertura: 13 endpoints
 */

import { getFinancialBankTransactions } from '@/types/generated/financial/financial-bank-transactions/financial-bank-transactions';
import type {
  BankTransactionCreate,
  BankTransactionUpdate,
  BankTransactionImport,
  ListTransactionsApiV1FinancialBankTransactionsBankTransactionsGetParams,
  GetPendingReconciliationApiV1FinancialBankTransactionsBankTransactionsPendingReconciliationGetParams,
  GetByPeriodApiV1FinancialBankTransactionsBankTransactionsByPeriodGetParams,
  GetSummaryApiV1FinancialBankTransactionsBankTransactionsSummaryGetParams,
  CancelTransactionApiV1FinancialBankTransactionsBankTransactionsTransactionIdCancelPostParams,
  ReconcileTransactionApiV1FinancialBankTransactionsBankTransactionsTransactionIdReconcilePostParams,
  BodyImportOfxFileApiV1FinancialBankTransactionsBankTransactionsImportOfxPost,
  ImportOfxFileApiV1FinancialBankTransactionsBankTransactionsImportOfxPostParams,
} from '@/types/generated/financial/models';

const transactions = getFinancialBankTransactions();

export const bankTransactionService = {
  async create(data: BankTransactionCreate) {
    return await transactions.createTransactionApiV1FinancialBankTransactionsBankTransactionsPost(
      data
    );
  },

  async list(
    params: ListTransactionsApiV1FinancialBankTransactionsBankTransactionsGetParams
  ) {
    return await transactions.listTransactionsApiV1FinancialBankTransactionsBankTransactionsGet(
      params
    );
  },

  async getById(transactionId: string) {
    return await transactions.getTransactionApiV1FinancialBankTransactionsBankTransactionsTransactionIdGet(
      transactionId
    );
  },

  async update(transactionId: string, data: BankTransactionUpdate) {
    return await transactions.updateTransactionApiV1FinancialBankTransactionsBankTransactionsTransactionIdPut(
      transactionId,
      data
    );
  },

  async delete(transactionId: string) {
    return await transactions.deleteTransactionApiV1FinancialBankTransactionsBankTransactionsTransactionIdDelete(
      transactionId
    );
  },

  async confirm(transactionId: string) {
    return await transactions.confirmTransactionApiV1FinancialBankTransactionsBankTransactionsTransactionIdConfirmPost(
      transactionId
    );
  },

  async cancel(
    transactionId: string,
    params: CancelTransactionApiV1FinancialBankTransactionsBankTransactionsTransactionIdCancelPostParams
  ) {
    return await transactions.cancelTransactionApiV1FinancialBankTransactionsBankTransactionsTransactionIdCancelPost(
      transactionId,
      params
    );
  },

  async reconcile(
    transactionId: string,
    params?: ReconcileTransactionApiV1FinancialBankTransactionsBankTransactionsTransactionIdReconcilePostParams
  ) {
    return await transactions.reconcileTransactionApiV1FinancialBankTransactionsBankTransactionsTransactionIdReconcilePost(
      transactionId,
      params
    );
  },

  async getPendingReconciliation(
    params: GetPendingReconciliationApiV1FinancialBankTransactionsBankTransactionsPendingReconciliationGetParams
  ) {
    return await transactions.getPendingReconciliationApiV1FinancialBankTransactionsBankTransactionsPendingReconciliationGet(
      params
    );
  },

  async getByPeriod(
    params: GetByPeriodApiV1FinancialBankTransactionsBankTransactionsByPeriodGetParams
  ) {
    return await transactions.getByPeriodApiV1FinancialBankTransactionsBankTransactionsByPeriodGet(
      params
    );
  },

  async getSummary(
    params: GetSummaryApiV1FinancialBankTransactionsBankTransactionsSummaryGetParams
  ) {
    return await transactions.getSummaryApiV1FinancialBankTransactionsBankTransactionsSummaryGet(
      params
    );
  },

  async importTransactions(data: BankTransactionImport) {
    return await transactions.importTransactionsApiV1FinancialBankTransactionsBankTransactionsImportPost(
      data
    );
  },

  async importOfxFile(
    body: BodyImportOfxFileApiV1FinancialBankTransactionsBankTransactionsImportOfxPost,
    params: ImportOfxFileApiV1FinancialBankTransactionsBankTransactionsImportOfxPostParams
  ) {
    return await transactions.importOfxFileApiV1FinancialBankTransactionsBankTransactionsImportOfxPost(
      body,
      params
    );
  },
};

export default bankTransactionService;
