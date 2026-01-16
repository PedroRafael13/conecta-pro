/**
 * Endpoints da API para o módulo Financial
 * Baseado no backend /api/v1/financial
 */

export const FINANCIAL_ENDPOINTS = {
  // ==================== RECEIVABLES (CONTAS A RECEBER) ====================
  RECEIVABLES: {
    LIST: '/financial/receivables',
    CREATE: '/financial/receivables',
    STATS: '/financial/receivables/stats',
    OVERDUE: '/financial/receivables/overdue',
    DUE_SOON: '/financial/receivables/due-soon',
    DETAIL: (id: string) => `/financial/receivables/${id}`,
    UPDATE: (id: string) => `/financial/receivables/${id}`,
    DELETE: (id: string) => `/financial/receivables/${id}`,
    CANCEL: (id: string) => `/financial/receivables/${id}/cancel`,
    SUSPEND: (id: string) => `/financial/receivables/${id}/suspend`,
    PROTEST: (id: string) => `/financial/receivables/${id}/protest`,
    WRITE_OFF: (id: string) => `/financial/receivables/${id}/write-off`,
    AGREEMENT: (id: string) => `/financial/receivables/${id}/agreement`,
    // Installments
    INSTALLMENTS: (id: string) => `/financial/receivables/${id}/installments`,
    INSTALLMENTS_PENDING: '/financial/receivables/installments/pending',
    INSTALLMENT_DETAIL: (id: string) => `/financial/receivables/installments/${id}`,
    INSTALLMENT_UPDATE: (id: string) => `/financial/receivables/installments/${id}`,
    GENERATE_BOLETO: (id: string) => `/financial/receivables/installments/${id}/generate-boleto`,
    GENERATE_PIX: (id: string) => `/financial/receivables/installments/${id}/generate-pix`,
    PAY_INSTALLMENT: (id: string) => `/financial/receivables/installments/${id}/pay`,
    RENEGOTIATE: (id: string) => `/financial/receivables/installments/${id}/renegotiate`,
    // Payments
    RECONCILE_PAYMENT: (id: string) => `/financial/receivables/payments/${id}/reconcile`,
    REVERSE_PAYMENT: (id: string) => `/financial/receivables/payments/${id}/reverse`,
    PENDING_RECONCILIATION: '/financial/receivables/payments/pending-reconciliation',
    // Bulk
    BULK_BOLETOS: '/financial/receivables/bulk-generate-boletos',
    BULK_PAYMENT: '/financial/receivables/bulk-payment',
    BULK_NOTIFY: '/financial/receivables/bulk-notify',
    // AI
    CUSTOMER_RISK: (id: string) => `/financial/receivables/ai/customer-risk/${id}`,
    COLLECTION_PRIORITIES: '/financial/receivables/ai/collection-priorities',
    DELINQUENCY_ANALYSIS: '/financial/receivables/ai/delinquency-analysis',
  },

  // ==================== PAYABLES (CONTAS A PAGAR) ====================
  PAYABLES: {
    LIST: '/financial/payables',
    CREATE: '/financial/payables',
    STATS: '/financial/payables/stats',
    OVERDUE: '/financial/payables/overdue',
    DUE_SOON: '/financial/payables/due-soon',
    DETAIL: (id: string) => `/financial/payables/${id}`,
    UPDATE: (id: string) => `/financial/payables/${id}`,
    DELETE: (id: string) => `/financial/payables/${id}`,
    APPROVE: (id: string) => `/financial/payables/${id}/approve`,
    REJECT: (id: string) => `/financial/payables/${id}/reject`,
    SCHEDULE: (id: string) => `/financial/payables/${id}/schedule`,
    BULK_APPROVE: '/financial/payables/bulk-approve',
    BULK_PAYMENT: '/financial/payables/bulk-payment',
    PROCESS_RECURRING: '/financial/payables/process-recurring',
    // Installments
    INSTALLMENTS: (id: string) => `/financial/payables/${id}/installments`,
    INSTALLMENTS_PENDING: '/financial/payables/installments/pending',
    PAY_INSTALLMENT: (id: string) => `/financial/payables/installments/${id}/pay`,
    RENEGOTIATE: (id: string) => `/financial/payables/installments/${id}/renegotiate`,
    // Payments
    RECONCILE_PAYMENT: (id: string) => `/financial/payables/payments/${id}/reconcile`,
    REVERSE_PAYMENT: (id: string) => `/financial/payables/payments/${id}/reverse`,
    PENDING_RECONCILIATION: '/financial/payables/payments/pending-reconciliation',
  },

  // ==================== SUPPLIERS (FORNECEDORES) ====================
  SUPPLIERS: {
    LIST: '/financial/suppliers',
    CREATE: '/financial/suppliers',
    STATS: '/financial/suppliers/stats',
    SEARCH: '/financial/suppliers/search',
    DETAIL: (id: string) => `/financial/suppliers/${id}`,
    UPDATE: (id: string) => `/financial/suppliers/${id}`,
    DELETE: (id: string) => `/financial/suppliers/${id}`,
    BLOCK: (id: string) => `/financial/suppliers/${id}/block`,
    UNBLOCK: (id: string) => `/financial/suppliers/${id}/unblock`,
    QUALIFY: (id: string) => `/financial/suppliers/${id}/qualify`,
    VALIDATE_PAYMENT: (id: string) => `/financial/suppliers/${id}/validate-payment`,
  },

  // ==================== CUSTOMERS (CLIENTES) ====================
  CUSTOMERS: {
    LIST: '/financial/customers',
    CREATE: '/financial/customers',
    DETAIL: (id: string) => `/financial/customers/${id}`,
    UPDATE: (id: string) => `/financial/customers/${id}`,
    DELETE: (id: string) => `/financial/customers/${id}`,
    BLOCK: (id: string) => `/financial/customers/${id}/block`,
    UNBLOCK: (id: string) => `/financial/customers/${id}/unblock`,
    BY_DOCUMENT: (doc: string) => `/financial/customers/document/${doc}`,
    BY_MORADOR: (id: string) => `/financial/customers/morador/${id}`,
    BY_UNIDADE: (id: string) => `/financial/customers/unidade/${id}`,
    DEBTORS: '/financial/customers/debtors',
    DEBT_SUMMARY: (id: string) => `/financial/customers/${id}/debt-summary`,
  },

  // ==================== BILLING RULES (REGRAS DE COBRANCA) ====================
  BILLING_RULES: {
    LIST: '/financial/billing-rules',
    CREATE: '/financial/billing-rules',
    ACTIVE: '/financial/billing-rules/active',
    DUE_FOR_GENERATION: '/financial/billing-rules/due-for-generation',
    DETAIL: (id: string) => `/financial/billing-rules/${id}`,
    UPDATE: (id: string) => `/financial/billing-rules/${id}`,
    DELETE: (id: string) => `/financial/billing-rules/${id}`,
    ACTIVATE: (id: string) => `/financial/billing-rules/${id}/activate`,
    CANCEL: (id: string) => `/financial/billing-rules/${id}/cancel`,
    PAUSE: (id: string) => `/financial/billing-rules/${id}/pause`,
    GENERATE: (id: string) => `/financial/billing-rules/${id}/generate`,
    PROCESS_ALL: '/financial/billing-rules/process-all',
  },

  // ==================== RECEIVABLE CATEGORIES ====================
  RECEIVABLE_CATEGORIES: {
    LIST: '/financial/receivable-categories',
    CREATE: '/financial/receivable-categories',
    TREE: '/financial/receivable-categories/tree',
    DETAIL: (id: string) => `/financial/receivable-categories/${id}`,
    UPDATE: (id: string) => `/financial/receivable-categories/${id}`,
    DELETE: (id: string) => `/financial/receivable-categories/${id}`,
    CHILDREN: (id: string) => `/financial/receivable-categories/${id}/children`,
    ACTIVATE: (id: string) => `/financial/receivable-categories/${id}/activate`,
    DEACTIVATE: (id: string) => `/financial/receivable-categories/${id}/deactivate`,
  },

  // ==================== BANK ACCOUNTS ====================
  BANK_ACCOUNTS: {
    LIST: '/financial/bank-accounts',
    CREATE: '/financial/bank-accounts',
    STATS: '/financial/bank-accounts/stats',
    MAIN: '/financial/bank-accounts/main',
    TRANSFER: '/financial/bank-accounts/transfer',
    DETAIL: (id: string) => `/financial/bank-accounts/${id}`,
    UPDATE: (id: string) => `/financial/bank-accounts/${id}`,
    DELETE: (id: string) => `/financial/bank-accounts/${id}`,
    SET_MAIN: (id: string) => `/financial/bank-accounts/${id}/set-main`,
    ACTIVATE: (id: string) => `/financial/bank-accounts/${id}/activate`,
    SUSPEND: (id: string) => `/financial/bank-accounts/${id}/suspend`,
    ADJUST_BALANCE: (id: string) => `/financial/bank-accounts/${id}/adjust-balance`,
  },

  // ==================== BANK TRANSACTIONS ====================
  BANK_TRANSACTIONS: {
    LIST: '/financial/bank-transactions',
    CREATE: '/financial/bank-transactions',
    IMPORT: '/financial/bank-transactions/import',
    IMPORT_OFX: '/financial/bank-transactions/import/ofx',
    SUMMARY: '/financial/bank-transactions/summary',
    BY_PERIOD: '/financial/bank-transactions/by-period',
    PENDING_RECONCILIATION: '/financial/bank-transactions/pending-reconciliation',
    DETAIL: (id: string) => `/financial/bank-transactions/${id}`,
    UPDATE: (id: string) => `/financial/bank-transactions/${id}`,
    DELETE: (id: string) => `/financial/bank-transactions/${id}`,
    CONFIRM: (id: string) => `/financial/bank-transactions/${id}/confirm`,
    CANCEL: (id: string) => `/financial/bank-transactions/${id}/cancel`,
    RECONCILE: (id: string) => `/financial/bank-transactions/${id}/reconcile`,
  },

  // ==================== BANK RECONCILIATION ====================
  BANK_RECONCILIATION: {
    LIST: '/financial/bank-reconciliation',
    CREATE: '/financial/bank-reconciliation',
    IN_PROGRESS: '/financial/bank-reconciliation/in-progress',
    DETAIL: (id: string) => `/financial/bank-reconciliation/${id}`,
    UPDATE: (id: string) => `/financial/bank-reconciliation/${id}`,
    DELETE: (id: string) => `/financial/bank-reconciliation/${id}`,
    IMPORT_STATEMENT: (id: string) => `/financial/bank-reconciliation/${id}/import-statement`,
    MATCH: (id: string) => `/financial/bank-reconciliation/${id}/match`,
    ADJUSTMENT: (id: string) => `/financial/bank-reconciliation/${id}/adjustment`,
    COMPLETE: (id: string) => `/financial/bank-reconciliation/${id}/complete`,
    REOPEN: (id: string) => `/financial/bank-reconciliation/${id}/reopen`,
    DETAILS: (id: string) => `/financial/bank-reconciliation/${id}/details`,
    EXPORT: (id: string) => `/financial/bank-reconciliation/${id}/export`,
  },

  // ==================== CASHFLOW ====================
  CASHFLOW: {
    SUMMARY: '/financial/cashflow/summary',
    DASHBOARD: '/financial/cashflow/dashboard',
    PROJECTION: '/financial/cashflow/projection',
    CATEGORY_BREAKDOWN: '/financial/cashflow/category-breakdown',
    SUPPLIER_BREAKDOWN: '/financial/cashflow/supplier-breakdown',
    TRENDS: '/financial/cashflow/trends',
    // Entries
    ENTRIES: '/financial/cashflow/entries',
    ENTRIES_CREATE: '/financial/cashflow/entries',
    ENTRIES_PENDING: '/financial/cashflow/entries/pending',
    ENTRIES_TOTALS: '/financial/cashflow/entries/totals',
    ENTRY_DETAIL: (id: string) => `/financial/cashflow/entries/${id}`,
    ENTRY_UPDATE: (id: string) => `/financial/cashflow/entries/${id}`,
    ENTRY_DELETE: (id: string) => `/financial/cashflow/entries/${id}`,
    ENTRY_REALIZE: (id: string) => `/financial/cashflow/entries/${id}/realize`,
    // Forecasts
    FORECASTS: '/financial/cashflow/forecasts',
    FORECASTS_CREATE: '/financial/cashflow/forecasts',
    FORECASTS_ACTIVE: '/financial/cashflow/forecasts/active',
    FORECAST_DETAIL: (id: string) => `/financial/cashflow/forecasts/${id}`,
    FORECAST_UPDATE: (id: string) => `/financial/cashflow/forecasts/${id}`,
    FORECAST_DELETE: (id: string) => `/financial/cashflow/forecasts/${id}`,
    FORECAST_UPDATE_ACTUALS: (id: string) => `/financial/cashflow/forecasts/${id}/update-actuals`,
    // AI
    AI_FORECAST: '/financial/cashflow/ai/forecast',
    AI_ANOMALIES: '/financial/cashflow/ai/anomalies',
    AI_SUGGESTIONS: '/financial/cashflow/ai/suggestions',
    AI_RISKS: '/financial/cashflow/ai/risks',
    AI_OPPORTUNITIES: '/financial/cashflow/ai/opportunities',
  },

  // ==================== DASHBOARD ====================
  DASHBOARD: {
    MAIN: '/financial/dashboard',
    SUMMARY: '/financial/dashboard/summary',
    KPIs: '/financial/dashboard/kpis',
    ALERTS: '/financial/dashboard/alerts',
    CHARTS: '/financial/dashboard/charts',
  },
} as const;

export default FINANCIAL_ENDPOINTS;
