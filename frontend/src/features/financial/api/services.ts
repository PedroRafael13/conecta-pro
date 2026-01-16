/**
 * Services para o módulo Financial
 * Camada de abstração para chamadas HTTP
 */

import { api } from '@/core/api/client';
import { FINANCIAL_ENDPOINTS } from './endpoints';
import type {
  PaginatedResponse,
  // Receivables
  ReceivableAccount,
  ReceivableAccountCreate,
  ReceivableAccountUpdate,
  ReceivableInstallment,
  ReceivablePaymentCreate,
  ReceivableFilter,
  ReceivableStats,
  // Payables
  PayableAccount,
  PayableAccountCreate,
  PayableAccountUpdate,
  PayableInstallment,
  PayablePaymentCreate,
  PayableScheduleRequest,
  PayableFilter,
  PayableStats,
  // Bank Accounts
  BankAccount,
  BankAccountCreate,
  BankAccountUpdate,
  TransferRequest,
  BankAccountFilter,
  BankAccountStats,
  // Bank Transactions
  BankTransaction,
  BankTransactionCreate,
  BankTransactionUpdate,
  BankTransactionFilter,
  BankTransactionStats,
  // Cashflow
  CashFlowEntry,
  CashFlowEntryCreate,
  CashFlowEntryUpdate,
  CashFlowForecast,
  CashFlowSummary,
  CashFlowProjection,
  CashFlowFilter,
  CashFlowDashboard,
  CashFlowProjectionResponse,
  // Suppliers
  Supplier,
  SupplierCreate,
  SupplierUpdate,
  SupplierFilter,
  SupplierStats,
  // Customers
  Customer,
  CustomerCreate,
  CustomerUpdate,
  CustomerFilter,
  // Billing Rules
  BillingRule,
  BillingRuleCreate,
  BillingRuleUpdate,
  // Receivable Categories
  ReceivableCategory,
  ReceivableCategoryCreate,
  ReceivableCategoryUpdate,
  // Dashboard
  FinancialDashboard,
  FinancialKPIs,
} from '../types';

// ==================== RECEIVABLES SERVICE ====================

export const receivableService = {
  list: async (params?: ReceivableFilter & { page?: number; page_size?: number; condominio_id?: string }) => {
    return api.get<PaginatedResponse<ReceivableAccount>>(FINANCIAL_ENDPOINTS.RECEIVABLES.LIST, { params });
  },

  getById: async (id: string) => {
    return api.get<ReceivableAccount>(FINANCIAL_ENDPOINTS.RECEIVABLES.DETAIL(id));
  },

  create: async (data: ReceivableAccountCreate) => {
    return api.post<ReceivableAccount>(FINANCIAL_ENDPOINTS.RECEIVABLES.CREATE, data);
  },

  update: async (id: string, data: ReceivableAccountUpdate) => {
    return api.put<ReceivableAccount>(FINANCIAL_ENDPOINTS.RECEIVABLES.UPDATE(id), data);
  },

  delete: async (id: string) => {
    return api.delete(FINANCIAL_ENDPOINTS.RECEIVABLES.DELETE(id));
  },

  getStats: async (params?: { condominio_id?: string }) => {
    return api.get<ReceivableStats>(FINANCIAL_ENDPOINTS.RECEIVABLES.STATS, { params });
  },

  getOverdue: async (params?: { condominio_id?: string; limit?: number }) => {
    return api.get<ReceivableAccount[]>(FINANCIAL_ENDPOINTS.RECEIVABLES.OVERDUE, { params });
  },

  getDueSoon: async (params?: { condominio_id?: string; days?: number; limit?: number }) => {
    return api.get<ReceivableAccount[]>(FINANCIAL_ENDPOINTS.RECEIVABLES.DUE_SOON, { params });
  },

  cancel: async (id: string, reason?: string) => {
    return api.post(FINANCIAL_ENDPOINTS.RECEIVABLES.CANCEL(id), null, { params: { reason } });
  },

  suspend: async (id: string, reason?: string) => {
    return api.post(FINANCIAL_ENDPOINTS.RECEIVABLES.SUSPEND(id), null, { params: { reason } });
  },

  // Installments
  getInstallments: async (id: string) => {
    return api.get<ReceivableInstallment[]>(FINANCIAL_ENDPOINTS.RECEIVABLES.INSTALLMENTS(id));
  },

  payInstallment: async (id: string, data: ReceivablePaymentCreate) => {
    return api.post(FINANCIAL_ENDPOINTS.RECEIVABLES.PAY_INSTALLMENT(id), data);
  },

  generateBoleto: async (id: string) => {
    return api.post(FINANCIAL_ENDPOINTS.RECEIVABLES.GENERATE_BOLETO(id));
  },

  generatePix: async (id: string) => {
    return api.post(FINANCIAL_ENDPOINTS.RECEIVABLES.GENERATE_PIX(id));
  },
};

// ==================== PAYABLES SERVICE ====================

export const payableService = {
  list: async (params?: PayableFilter & { page?: number; page_size?: number; condominio_id?: string }) => {
    return api.get<PaginatedResponse<PayableAccount>>(FINANCIAL_ENDPOINTS.PAYABLES.LIST, { params });
  },

  getById: async (id: string) => {
    return api.get<PayableAccount>(FINANCIAL_ENDPOINTS.PAYABLES.DETAIL(id));
  },

  create: async (data: PayableAccountCreate) => {
    return api.post<PayableAccount>(FINANCIAL_ENDPOINTS.PAYABLES.CREATE, data);
  },

  update: async (id: string, data: PayableAccountUpdate) => {
    return api.put<PayableAccount>(FINANCIAL_ENDPOINTS.PAYABLES.UPDATE(id), data);
  },

  delete: async (id: string) => {
    return api.delete(FINANCIAL_ENDPOINTS.PAYABLES.DELETE(id));
  },

  getStats: async (params?: { condominio_id?: string }) => {
    return api.get<PayableStats>(FINANCIAL_ENDPOINTS.PAYABLES.STATS, { params });
  },

  getOverdue: async (params?: { condominio_id?: string; limit?: number }) => {
    return api.get<PayableAccount[]>(FINANCIAL_ENDPOINTS.PAYABLES.OVERDUE, { params });
  },

  getDueSoon: async (params?: { condominio_id?: string; days?: number; limit?: number }) => {
    return api.get<PayableAccount[]>(FINANCIAL_ENDPOINTS.PAYABLES.DUE_SOON, { params });
  },

  approve: async (id: string, notes?: string) => {
    return api.post(FINANCIAL_ENDPOINTS.PAYABLES.APPROVE(id), null, { params: { notes } });
  },

  reject: async (id: string, reason: string) => {
    return api.post(FINANCIAL_ENDPOINTS.PAYABLES.REJECT(id), null, { params: { reason } });
  },

  schedule: async (id: string, data: PayableScheduleRequest) => {
    return api.post(FINANCIAL_ENDPOINTS.PAYABLES.SCHEDULE(id), data);
  },

  // Installments
  getInstallments: async (id: string) => {
    return api.get<PayableInstallment[]>(FINANCIAL_ENDPOINTS.PAYABLES.INSTALLMENTS(id));
  },

  payInstallment: async (id: string, data: PayablePaymentCreate) => {
    return api.post(FINANCIAL_ENDPOINTS.PAYABLES.PAY_INSTALLMENT(id), data);
  },

  // Bulk
  bulkApprove: async (ids: string[], notes?: string) => {
    return api.post(FINANCIAL_ENDPOINTS.PAYABLES.BULK_APPROVE, { ids, notes });
  },

  bulkPayment: async (payments: Array<{ installment_id: string; amount: number; payment_date: string }>) => {
    return api.post(FINANCIAL_ENDPOINTS.PAYABLES.BULK_PAYMENT, { payments });
  },
};

// ==================== SUPPLIERS SERVICE ====================

export const supplierService = {
  list: async (params?: SupplierFilter & { page?: number; page_size?: number; condominio_id?: string }) => {
    return api.get<PaginatedResponse<Supplier>>(FINANCIAL_ENDPOINTS.SUPPLIERS.LIST, { params });
  },

  getById: async (id: string) => {
    return api.get<Supplier>(FINANCIAL_ENDPOINTS.SUPPLIERS.DETAIL(id));
  },

  create: async (data: SupplierCreate) => {
    return api.post<Supplier>(FINANCIAL_ENDPOINTS.SUPPLIERS.CREATE, data);
  },

  update: async (id: string, data: SupplierUpdate) => {
    return api.put<Supplier>(FINANCIAL_ENDPOINTS.SUPPLIERS.UPDATE(id), data);
  },

  delete: async (id: string) => {
    return api.delete(FINANCIAL_ENDPOINTS.SUPPLIERS.DELETE(id));
  },

  getStats: async (params?: { condominio_id?: string }) => {
    return api.get<SupplierStats>(FINANCIAL_ENDPOINTS.SUPPLIERS.STATS, { params });
  },

  search: async (term: string, fields?: string[]) => {
    return api.get<Supplier[]>(FINANCIAL_ENDPOINTS.SUPPLIERS.SEARCH, { params: { term, fields } });
  },

  block: async (id: string) => {
    return api.post(FINANCIAL_ENDPOINTS.SUPPLIERS.BLOCK(id));
  },

  unblock: async (id: string) => {
    return api.post(FINANCIAL_ENDPOINTS.SUPPLIERS.UNBLOCK(id));
  },

  qualify: async (id: string, data: { score: number; notes?: string }) => {
    return api.post(FINANCIAL_ENDPOINTS.SUPPLIERS.QUALIFY(id), data);
  },
};

// ==================== CUSTOMERS SERVICE ====================

export const customerService = {
  list: async (params?: CustomerFilter & { page?: number; page_size?: number; condominio_id?: string }) => {
    return api.get<PaginatedResponse<Customer>>(FINANCIAL_ENDPOINTS.CUSTOMERS.LIST, { params });
  },

  getById: async (id: string) => {
    return api.get<Customer>(FINANCIAL_ENDPOINTS.CUSTOMERS.DETAIL(id));
  },

  create: async (data: CustomerCreate) => {
    return api.post<Customer>(FINANCIAL_ENDPOINTS.CUSTOMERS.CREATE, data);
  },

  update: async (id: string, data: CustomerUpdate) => {
    return api.put<Customer>(FINANCIAL_ENDPOINTS.CUSTOMERS.UPDATE(id), data);
  },

  delete: async (id: string) => {
    return api.delete(FINANCIAL_ENDPOINTS.CUSTOMERS.DELETE(id));
  },

  getByDocument: async (document: string) => {
    return api.get<Customer>(FINANCIAL_ENDPOINTS.CUSTOMERS.BY_DOCUMENT(document));
  },

  getDebtors: async (params?: { condominio_id?: string }) => {
    return api.get<Customer[]>(FINANCIAL_ENDPOINTS.CUSTOMERS.DEBTORS, { params });
  },

  getDebtSummary: async (id: string) => {
    return api.get(FINANCIAL_ENDPOINTS.CUSTOMERS.DEBT_SUMMARY(id));
  },

  block: async (id: string) => {
    return api.post(FINANCIAL_ENDPOINTS.CUSTOMERS.BLOCK(id));
  },

  unblock: async (id: string) => {
    return api.post(FINANCIAL_ENDPOINTS.CUSTOMERS.UNBLOCK(id));
  },
};

// ==================== BILLING RULES SERVICE ====================

export const billingRuleService = {
  list: async (params?: { page?: number; page_size?: number; condominio_id?: string }) => {
    return api.get<PaginatedResponse<BillingRule>>(FINANCIAL_ENDPOINTS.BILLING_RULES.LIST, { params });
  },

  getById: async (id: string) => {
    return api.get<BillingRule>(FINANCIAL_ENDPOINTS.BILLING_RULES.DETAIL(id));
  },

  create: async (data: BillingRuleCreate) => {
    return api.post<BillingRule>(FINANCIAL_ENDPOINTS.BILLING_RULES.CREATE, data);
  },

  update: async (id: string, data: BillingRuleUpdate) => {
    return api.put<BillingRule>(FINANCIAL_ENDPOINTS.BILLING_RULES.UPDATE(id), data);
  },

  delete: async (id: string) => {
    return api.delete(FINANCIAL_ENDPOINTS.BILLING_RULES.DELETE(id));
  },

  getActive: async (params?: { condominio_id?: string }) => {
    return api.get<BillingRule[]>(FINANCIAL_ENDPOINTS.BILLING_RULES.ACTIVE, { params });
  },

  activate: async (id: string) => {
    return api.post(FINANCIAL_ENDPOINTS.BILLING_RULES.ACTIVATE(id));
  },

  pause: async (id: string) => {
    return api.post(FINANCIAL_ENDPOINTS.BILLING_RULES.PAUSE(id));
  },

  cancel: async (id: string) => {
    return api.post(FINANCIAL_ENDPOINTS.BILLING_RULES.CANCEL(id));
  },

  generate: async (id: string) => {
    return api.post(FINANCIAL_ENDPOINTS.BILLING_RULES.GENERATE(id));
  },

  processAll: async (params?: { condominio_id?: string }) => {
    return api.post(FINANCIAL_ENDPOINTS.BILLING_RULES.PROCESS_ALL, null, { params });
  },
};

// ==================== RECEIVABLE CATEGORIES SERVICE ====================

export const receivableCategoryService = {
  list: async (params?: { page?: number; page_size?: number; condominio_id?: string }) => {
    return api.get<PaginatedResponse<ReceivableCategory>>(FINANCIAL_ENDPOINTS.RECEIVABLE_CATEGORIES.LIST, { params });
  },

  getById: async (id: string) => {
    return api.get<ReceivableCategory>(FINANCIAL_ENDPOINTS.RECEIVABLE_CATEGORIES.DETAIL(id));
  },

  create: async (data: ReceivableCategoryCreate) => {
    return api.post<ReceivableCategory>(FINANCIAL_ENDPOINTS.RECEIVABLE_CATEGORIES.CREATE, data);
  },

  update: async (id: string, data: ReceivableCategoryUpdate) => {
    return api.put<ReceivableCategory>(FINANCIAL_ENDPOINTS.RECEIVABLE_CATEGORIES.UPDATE(id), data);
  },

  delete: async (id: string) => {
    return api.delete(FINANCIAL_ENDPOINTS.RECEIVABLE_CATEGORIES.DELETE(id));
  },

  getTree: async (params?: { condominio_id?: string }) => {
    return api.get<ReceivableCategory[]>(FINANCIAL_ENDPOINTS.RECEIVABLE_CATEGORIES.TREE, { params });
  },

  activate: async (id: string) => {
    return api.post(FINANCIAL_ENDPOINTS.RECEIVABLE_CATEGORIES.ACTIVATE(id));
  },

  deactivate: async (id: string) => {
    return api.post(FINANCIAL_ENDPOINTS.RECEIVABLE_CATEGORIES.DEACTIVATE(id));
  },
};

// ==================== BANK ACCOUNTS SERVICE ====================

export const bankAccountService = {
  list: async (params?: BankAccountFilter & { page?: number; page_size?: number; condominio_id?: string }) => {
    return api.get<PaginatedResponse<BankAccount>>(FINANCIAL_ENDPOINTS.BANK_ACCOUNTS.LIST, { params });
  },

  getById: async (id: string) => {
    return api.get<BankAccount>(FINANCIAL_ENDPOINTS.BANK_ACCOUNTS.DETAIL(id));
  },

  create: async (data: BankAccountCreate) => {
    return api.post<BankAccount>(FINANCIAL_ENDPOINTS.BANK_ACCOUNTS.CREATE, data);
  },

  update: async (id: string, data: BankAccountUpdate) => {
    return api.put<BankAccount>(FINANCIAL_ENDPOINTS.BANK_ACCOUNTS.UPDATE(id), data);
  },

  delete: async (id: string) => {
    return api.delete(FINANCIAL_ENDPOINTS.BANK_ACCOUNTS.DELETE(id));
  },

  getStats: async (params?: { condominio_id?: string }) => {
    return api.get<BankAccountStats>(FINANCIAL_ENDPOINTS.BANK_ACCOUNTS.STATS, { params });
  },

  getMain: async (params?: { condominio_id?: string }) => {
    return api.get<BankAccount>(FINANCIAL_ENDPOINTS.BANK_ACCOUNTS.MAIN, { params });
  },

  setMain: async (id: string) => {
    return api.post(FINANCIAL_ENDPOINTS.BANK_ACCOUNTS.SET_MAIN(id));
  },

  activate: async (id: string) => {
    return api.post(FINANCIAL_ENDPOINTS.BANK_ACCOUNTS.ACTIVATE(id));
  },

  suspend: async (id: string) => {
    return api.post(FINANCIAL_ENDPOINTS.BANK_ACCOUNTS.SUSPEND(id));
  },

  transfer: async (data: TransferRequest) => {
    return api.post(FINANCIAL_ENDPOINTS.BANK_ACCOUNTS.TRANSFER, data);
  },

  adjustBalance: async (id: string, data: { amount: number; reason: string }) => {
    return api.post(FINANCIAL_ENDPOINTS.BANK_ACCOUNTS.ADJUST_BALANCE(id), data);
  },
};

// ==================== BANK TRANSACTIONS SERVICE ====================

export const bankTransactionService = {
  list: async (params?: BankTransactionFilter & { page?: number; page_size?: number; condominio_id?: string }) => {
    return api.get<PaginatedResponse<BankTransaction>>(FINANCIAL_ENDPOINTS.BANK_TRANSACTIONS.LIST, { params });
  },

  getById: async (id: string) => {
    return api.get<BankTransaction>(FINANCIAL_ENDPOINTS.BANK_TRANSACTIONS.DETAIL(id));
  },

  create: async (data: BankTransactionCreate) => {
    return api.post<BankTransaction>(FINANCIAL_ENDPOINTS.BANK_TRANSACTIONS.CREATE, data);
  },

  update: async (id: string, data: BankTransactionUpdate) => {
    return api.put<BankTransaction>(FINANCIAL_ENDPOINTS.BANK_TRANSACTIONS.UPDATE(id), data);
  },

  delete: async (id: string) => {
    return api.delete(FINANCIAL_ENDPOINTS.BANK_TRANSACTIONS.DELETE(id));
  },

  getSummary: async (params?: { condominio_id?: string; date_start?: string; date_end?: string }) => {
    return api.get<BankTransactionStats>(FINANCIAL_ENDPOINTS.BANK_TRANSACTIONS.SUMMARY, { params });
  },

  getPendingReconciliation: async (params?: { condominio_id?: string; account_id?: string }) => {
    return api.get<BankTransaction[]>(FINANCIAL_ENDPOINTS.BANK_TRANSACTIONS.PENDING_RECONCILIATION, { params });
  },

  confirm: async (id: string) => {
    return api.post(FINANCIAL_ENDPOINTS.BANK_TRANSACTIONS.CONFIRM(id));
  },

  cancel: async (id: string) => {
    return api.post(FINANCIAL_ENDPOINTS.BANK_TRANSACTIONS.CANCEL(id));
  },

  reconcile: async (id: string, data?: { reconcile_with_id?: string; reconcile_with_type?: string }) => {
    return api.post(FINANCIAL_ENDPOINTS.BANK_TRANSACTIONS.RECONCILE(id), data);
  },

  importOFX: async (file: File, accountId: string) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('account_id', accountId);
    return api.post(FINANCIAL_ENDPOINTS.BANK_TRANSACTIONS.IMPORT_OFX, formData);
  },
};

// ==================== CASHFLOW SERVICE ====================

export const cashflowService = {
  getSummary: async (params?: { condominio_id?: string; date_start?: string; date_end?: string }) => {
    return api.get<CashFlowSummary>(FINANCIAL_ENDPOINTS.CASHFLOW.SUMMARY, { params });
  },

  getDashboard: async (params?: { condominio_id?: string; period?: string }) => {
    return api.get<CashFlowDashboard>(FINANCIAL_ENDPOINTS.CASHFLOW.DASHBOARD, { params });
  },

  getProjection: async (params?: { condominio_id?: string; days?: number }) => {
    return api.get<CashFlowProjectionResponse>(FINANCIAL_ENDPOINTS.CASHFLOW.PROJECTION, { params });
  },

  getCategoryBreakdown: async (params?: { condominio_id?: string; date_start?: string; date_end?: string }) => {
    return api.get(FINANCIAL_ENDPOINTS.CASHFLOW.CATEGORY_BREAKDOWN, { params });
  },

  getTrends: async (params?: { condominio_id?: string; period?: string }) => {
    return api.get(FINANCIAL_ENDPOINTS.CASHFLOW.TRENDS, { params });
  },

  // Entries
  listEntries: async (params?: CashFlowFilter & { page?: number; page_size?: number; condominio_id?: string }) => {
    return api.get<PaginatedResponse<CashFlowEntry>>(FINANCIAL_ENDPOINTS.CASHFLOW.ENTRIES, { params });
  },

  createEntry: async (data: CashFlowEntryCreate) => {
    return api.post<CashFlowEntry>(FINANCIAL_ENDPOINTS.CASHFLOW.ENTRIES_CREATE, data);
  },

  updateEntry: async (id: string, data: CashFlowEntryUpdate) => {
    return api.put<CashFlowEntry>(FINANCIAL_ENDPOINTS.CASHFLOW.ENTRY_UPDATE(id), data);
  },

  deleteEntry: async (id: string) => {
    return api.delete(FINANCIAL_ENDPOINTS.CASHFLOW.ENTRY_DELETE(id));
  },

  realizeEntry: async (id: string, data?: { realized_amount?: number; realized_date?: string }) => {
    return api.post(FINANCIAL_ENDPOINTS.CASHFLOW.ENTRY_REALIZE(id), data);
  },

  // Forecasts
  listForecasts: async (params?: { page?: number; page_size?: number; condominio_id?: string }) => {
    return api.get<PaginatedResponse<CashFlowForecast>>(FINANCIAL_ENDPOINTS.CASHFLOW.FORECASTS, { params });
  },

  getActiveForecast: async (params?: { condominio_id?: string }) => {
    return api.get<CashFlowForecast>(FINANCIAL_ENDPOINTS.CASHFLOW.FORECASTS_ACTIVE, { params });
  },

  // AI
  getAIForecast: async (params?: { condominio_id?: string; days?: number }) => {
    return api.post(FINANCIAL_ENDPOINTS.CASHFLOW.AI_FORECAST, null, { params });
  },

  getAISuggestions: async (params?: { condominio_id?: string }) => {
    return api.get(FINANCIAL_ENDPOINTS.CASHFLOW.AI_SUGGESTIONS, { params });
  },

  getAIRisks: async (params?: { condominio_id?: string }) => {
    return api.get(FINANCIAL_ENDPOINTS.CASHFLOW.AI_RISKS, { params });
  },
};

// ==================== DASHBOARD SERVICE ====================

export const financialDashboardService = {
  getDashboard: async (params?: { condominio_id?: string; period?: string }) => {
    return api.get<FinancialDashboard>(FINANCIAL_ENDPOINTS.DASHBOARD.MAIN, { params });
  },

  getSummary: async (params?: { condominio_id?: string; period?: string }) => {
    return api.get(FINANCIAL_ENDPOINTS.DASHBOARD.SUMMARY, { params });
  },

  getKPIs: async (params?: { condominio_id?: string }) => {
    return api.get<FinancialKPIs>(FINANCIAL_ENDPOINTS.DASHBOARD.KPIs, { params });
  },

  getAlerts: async (params?: { condominio_id?: string }) => {
    return api.get(FINANCIAL_ENDPOINTS.DASHBOARD.ALERTS, { params });
  },

  getCharts: async (params?: { condominio_id?: string; period?: string }) => {
    return api.get(FINANCIAL_ENDPOINTS.DASHBOARD.CHARTS, { params });
  },
};

// ==================== EXPORTS ====================

export default {
  receivables: receivableService,
  payables: payableService,
  suppliers: supplierService,
  customers: customerService,
  billingRules: billingRuleService,
  receivableCategories: receivableCategoryService,
  bankAccounts: bankAccountService,
  bankTransactions: bankTransactionService,
  cashflow: cashflowService,
  dashboard: financialDashboardService,
};
