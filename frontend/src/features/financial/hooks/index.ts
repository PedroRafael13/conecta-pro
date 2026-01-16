/**
 * React Query Hooks para o módulo Financial
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  receivableService,
  payableService,
  supplierService,
  customerService,
  billingRuleService,
  receivableCategoryService,
  bankAccountService,
  bankTransactionService,
  cashflowService,
  financialDashboardService,
} from '../api/services';
import type {
  ReceivableFilter,
  ReceivableAccountCreate,
  ReceivableAccountUpdate,
  ReceivablePaymentCreate,
  PayableFilter,
  PayableAccountCreate,
  PayableAccountUpdate,
  PayablePaymentCreate,
  PayableScheduleRequest,
  SupplierFilter,
  SupplierCreate,
  SupplierUpdate,
  CustomerFilter,
  CustomerCreate,
  CustomerUpdate,
  BillingRuleCreate,
  BillingRuleUpdate,
  ReceivableCategoryCreate,
  ReceivableCategoryUpdate,
  BankAccountFilter,
  BankAccountCreate,
  BankAccountUpdate,
  TransferRequest,
  BankTransactionFilter,
  BankTransactionCreate,
  BankTransactionUpdate,
  CashFlowFilter,
  CashFlowEntryCreate,
  CashFlowEntryUpdate,
} from '../types';

// ==================== QUERY KEYS ====================

export const FINANCIAL_QUERY_KEYS = {
  receivables: {
    all: ['financial', 'receivables'] as const,
    lists: () => [...FINANCIAL_QUERY_KEYS.receivables.all, 'list'] as const,
    list: (filters: any) => [...FINANCIAL_QUERY_KEYS.receivables.lists(), filters] as const,
    details: () => [...FINANCIAL_QUERY_KEYS.receivables.all, 'detail'] as const,
    detail: (id: string) => [...FINANCIAL_QUERY_KEYS.receivables.details(), id] as const,
    stats: () => [...FINANCIAL_QUERY_KEYS.receivables.all, 'stats'] as const,
    overdue: () => [...FINANCIAL_QUERY_KEYS.receivables.all, 'overdue'] as const,
    dueSoon: () => [...FINANCIAL_QUERY_KEYS.receivables.all, 'due-soon'] as const,
  },
  payables: {
    all: ['financial', 'payables'] as const,
    lists: () => [...FINANCIAL_QUERY_KEYS.payables.all, 'list'] as const,
    list: (filters: any) => [...FINANCIAL_QUERY_KEYS.payables.lists(), filters] as const,
    details: () => [...FINANCIAL_QUERY_KEYS.payables.all, 'detail'] as const,
    detail: (id: string) => [...FINANCIAL_QUERY_KEYS.payables.details(), id] as const,
    stats: () => [...FINANCIAL_QUERY_KEYS.payables.all, 'stats'] as const,
    overdue: () => [...FINANCIAL_QUERY_KEYS.payables.all, 'overdue'] as const,
    dueSoon: () => [...FINANCIAL_QUERY_KEYS.payables.all, 'due-soon'] as const,
  },
  suppliers: {
    all: ['financial', 'suppliers'] as const,
    lists: () => [...FINANCIAL_QUERY_KEYS.suppliers.all, 'list'] as const,
    list: (filters: any) => [...FINANCIAL_QUERY_KEYS.suppliers.lists(), filters] as const,
    details: () => [...FINANCIAL_QUERY_KEYS.suppliers.all, 'detail'] as const,
    detail: (id: string) => [...FINANCIAL_QUERY_KEYS.suppliers.details(), id] as const,
    stats: () => [...FINANCIAL_QUERY_KEYS.suppliers.all, 'stats'] as const,
  },
  customers: {
    all: ['financial', 'customers'] as const,
    lists: () => [...FINANCIAL_QUERY_KEYS.customers.all, 'list'] as const,
    list: (filters: any) => [...FINANCIAL_QUERY_KEYS.customers.lists(), filters] as const,
    details: () => [...FINANCIAL_QUERY_KEYS.customers.all, 'detail'] as const,
    detail: (id: string) => [...FINANCIAL_QUERY_KEYS.customers.details(), id] as const,
  },
  billingRules: {
    all: ['financial', 'billing-rules'] as const,
    lists: () => [...FINANCIAL_QUERY_KEYS.billingRules.all, 'list'] as const,
    list: (filters: any) => [...FINANCIAL_QUERY_KEYS.billingRules.lists(), filters] as const,
    details: () => [...FINANCIAL_QUERY_KEYS.billingRules.all, 'detail'] as const,
    detail: (id: string) => [...FINANCIAL_QUERY_KEYS.billingRules.details(), id] as const,
  },
  receivableCategories: {
    all: ['financial', 'receivable-categories'] as const,
    lists: () => [...FINANCIAL_QUERY_KEYS.receivableCategories.all, 'list'] as const,
    tree: () => [...FINANCIAL_QUERY_KEYS.receivableCategories.all, 'tree'] as const,
    details: () => [...FINANCIAL_QUERY_KEYS.receivableCategories.all, 'detail'] as const,
    detail: (id: string) => [...FINANCIAL_QUERY_KEYS.receivableCategories.details(), id] as const,
  },
  bankAccounts: {
    all: ['financial', 'bank-accounts'] as const,
    lists: () => [...FINANCIAL_QUERY_KEYS.bankAccounts.all, 'list'] as const,
    list: (filters: any) => [...FINANCIAL_QUERY_KEYS.bankAccounts.lists(), filters] as const,
    details: () => [...FINANCIAL_QUERY_KEYS.bankAccounts.all, 'detail'] as const,
    detail: (id: string) => [...FINANCIAL_QUERY_KEYS.bankAccounts.details(), id] as const,
    stats: () => [...FINANCIAL_QUERY_KEYS.bankAccounts.all, 'stats'] as const,
    main: () => [...FINANCIAL_QUERY_KEYS.bankAccounts.all, 'main'] as const,
  },
  bankTransactions: {
    all: ['financial', 'bank-transactions'] as const,
    lists: () => [...FINANCIAL_QUERY_KEYS.bankTransactions.all, 'list'] as const,
    list: (filters: any) => [...FINANCIAL_QUERY_KEYS.bankTransactions.lists(), filters] as const,
    details: () => [...FINANCIAL_QUERY_KEYS.bankTransactions.all, 'detail'] as const,
    detail: (id: string) => [...FINANCIAL_QUERY_KEYS.bankTransactions.details(), id] as const,
    summary: () => [...FINANCIAL_QUERY_KEYS.bankTransactions.all, 'summary'] as const,
    pending: () => [...FINANCIAL_QUERY_KEYS.bankTransactions.all, 'pending'] as const,
  },
  cashflow: {
    all: ['financial', 'cashflow'] as const,
    summary: (params?: any) => [...FINANCIAL_QUERY_KEYS.cashflow.all, 'summary', params] as const,
    dashboard: (params?: any) => [...FINANCIAL_QUERY_KEYS.cashflow.all, 'dashboard', params] as const,
    projection: (params?: any) => [...FINANCIAL_QUERY_KEYS.cashflow.all, 'projection', params] as const,
    entries: () => [...FINANCIAL_QUERY_KEYS.cashflow.all, 'entries'] as const,
    forecasts: () => [...FINANCIAL_QUERY_KEYS.cashflow.all, 'forecasts'] as const,
  },
  dashboard: {
    all: ['financial', 'dashboard'] as const,
    main: (params?: any) => [...FINANCIAL_QUERY_KEYS.dashboard.all, 'main', params] as const,
    kpis: () => [...FINANCIAL_QUERY_KEYS.dashboard.all, 'kpis'] as const,
    alerts: () => [...FINANCIAL_QUERY_KEYS.dashboard.all, 'alerts'] as const,
  },
};

// ==================== RECEIVABLES HOOKS ====================

export function useReceivables(params?: ReceivableFilter & { page?: number; page_size?: number; condominio_id?: string }) {
  return useQuery({
    queryKey: FINANCIAL_QUERY_KEYS.receivables.list(params),
    queryFn: () => receivableService.list(params),
  });
}

export function useReceivable(id: string) {
  return useQuery({
    queryKey: FINANCIAL_QUERY_KEYS.receivables.detail(id),
    queryFn: () => receivableService.getById(id),
    enabled: !!id,
  });
}

export function useReceivableStats(params?: { condominio_id?: string }) {
  return useQuery({
    queryKey: FINANCIAL_QUERY_KEYS.receivables.stats(),
    queryFn: () => receivableService.getStats(params),
  });
}

export function useReceivablesOverdue(params?: { condominio_id?: string; limit?: number }) {
  return useQuery({
    queryKey: FINANCIAL_QUERY_KEYS.receivables.overdue(),
    queryFn: () => receivableService.getOverdue(params),
  });
}

export function useReceivablesDueSoon(params?: { condominio_id?: string; days?: number; limit?: number }) {
  return useQuery({
    queryKey: FINANCIAL_QUERY_KEYS.receivables.dueSoon(),
    queryFn: () => receivableService.getDueSoon(params),
  });
}

export function useCreateReceivable() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: ReceivableAccountCreate) => receivableService.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: FINANCIAL_QUERY_KEYS.receivables.all });
    },
  });
}

export function useUpdateReceivable() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: ReceivableAccountUpdate }) =>
      receivableService.update(id, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: FINANCIAL_QUERY_KEYS.receivables.detail(variables.id) });
      queryClient.invalidateQueries({ queryKey: FINANCIAL_QUERY_KEYS.receivables.lists() });
    },
  });
}

export function useDeleteReceivable() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => receivableService.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: FINANCIAL_QUERY_KEYS.receivables.all });
    },
  });
}

export function useCancelReceivable() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, reason }: { id: string; reason?: string }) =>
      receivableService.cancel(id, reason),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: FINANCIAL_QUERY_KEYS.receivables.all });
    },
  });
}

export function usePayReceivableInstallment() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: ReceivablePaymentCreate }) =>
      receivableService.payInstallment(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: FINANCIAL_QUERY_KEYS.receivables.all });
      queryClient.invalidateQueries({ queryKey: FINANCIAL_QUERY_KEYS.bankTransactions.all });
    },
  });
}

export function useGenerateBoleto() {
  return useMutation({
    mutationFn: (id: string) => receivableService.generateBoleto(id),
  });
}

export function useGeneratePix() {
  return useMutation({
    mutationFn: (id: string) => receivableService.generatePix(id),
  });
}

// ==================== PAYABLES HOOKS ====================

export function usePayables(params?: PayableFilter & { page?: number; page_size?: number; condominio_id?: string }) {
  return useQuery({
    queryKey: FINANCIAL_QUERY_KEYS.payables.list(params),
    queryFn: () => payableService.list(params),
  });
}

export function usePayable(id: string) {
  return useQuery({
    queryKey: FINANCIAL_QUERY_KEYS.payables.detail(id),
    queryFn: () => payableService.getById(id),
    enabled: !!id,
  });
}

export function usePayableStats(params?: { condominio_id?: string }) {
  return useQuery({
    queryKey: FINANCIAL_QUERY_KEYS.payables.stats(),
    queryFn: () => payableService.getStats(params),
  });
}

export function usePayablesOverdue(params?: { condominio_id?: string; limit?: number }) {
  return useQuery({
    queryKey: FINANCIAL_QUERY_KEYS.payables.overdue(),
    queryFn: () => payableService.getOverdue(params),
  });
}

export function usePayablesDueSoon(params?: { condominio_id?: string; days?: number; limit?: number }) {
  return useQuery({
    queryKey: FINANCIAL_QUERY_KEYS.payables.dueSoon(),
    queryFn: () => payableService.getDueSoon(params),
  });
}

export function useCreatePayable() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: PayableAccountCreate) => payableService.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: FINANCIAL_QUERY_KEYS.payables.all });
    },
  });
}

export function useUpdatePayable() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: PayableAccountUpdate }) =>
      payableService.update(id, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: FINANCIAL_QUERY_KEYS.payables.detail(variables.id) });
      queryClient.invalidateQueries({ queryKey: FINANCIAL_QUERY_KEYS.payables.lists() });
    },
  });
}

export function useDeletePayable() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => payableService.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: FINANCIAL_QUERY_KEYS.payables.all });
    },
  });
}

export function useApprovePayable() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, notes }: { id: string; notes?: string }) =>
      payableService.approve(id, notes),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: FINANCIAL_QUERY_KEYS.payables.all });
    },
  });
}

export function useRejectPayable() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, reason }: { id: string; reason: string }) =>
      payableService.reject(id, reason),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: FINANCIAL_QUERY_KEYS.payables.all });
    },
  });
}

export function useSchedulePayable() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: PayableScheduleRequest }) =>
      payableService.schedule(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: FINANCIAL_QUERY_KEYS.payables.all });
    },
  });
}

export function usePayPayableInstallment() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: PayablePaymentCreate }) =>
      payableService.payInstallment(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: FINANCIAL_QUERY_KEYS.payables.all });
      queryClient.invalidateQueries({ queryKey: FINANCIAL_QUERY_KEYS.bankTransactions.all });
    },
  });
}

// ==================== SUPPLIERS HOOKS ====================

export function useSuppliers(params?: SupplierFilter & { page?: number; page_size?: number; condominio_id?: string }) {
  return useQuery({
    queryKey: FINANCIAL_QUERY_KEYS.suppliers.list(params),
    queryFn: () => supplierService.list(params),
  });
}

export function useSupplier(id: string) {
  return useQuery({
    queryKey: FINANCIAL_QUERY_KEYS.suppliers.detail(id),
    queryFn: () => supplierService.getById(id),
    enabled: !!id,
  });
}

export function useSupplierStats(params?: { condominio_id?: string }) {
  return useQuery({
    queryKey: FINANCIAL_QUERY_KEYS.suppliers.stats(),
    queryFn: () => supplierService.getStats(params),
  });
}

export function useCreateSupplier() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: SupplierCreate) => supplierService.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: FINANCIAL_QUERY_KEYS.suppliers.all });
    },
  });
}

export function useUpdateSupplier() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: SupplierUpdate }) =>
      supplierService.update(id, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: FINANCIAL_QUERY_KEYS.suppliers.detail(variables.id) });
      queryClient.invalidateQueries({ queryKey: FINANCIAL_QUERY_KEYS.suppliers.lists() });
    },
  });
}

export function useDeleteSupplier() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => supplierService.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: FINANCIAL_QUERY_KEYS.suppliers.all });
    },
  });
}

export function useBlockSupplier() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => supplierService.block(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: FINANCIAL_QUERY_KEYS.suppliers.all });
    },
  });
}

export function useUnblockSupplier() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => supplierService.unblock(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: FINANCIAL_QUERY_KEYS.suppliers.all });
    },
  });
}

// ==================== CUSTOMERS HOOKS ====================

export function useCustomers(params?: CustomerFilter & { page?: number; page_size?: number; condominio_id?: string }) {
  return useQuery({
    queryKey: FINANCIAL_QUERY_KEYS.customers.list(params),
    queryFn: () => customerService.list(params),
  });
}

export function useCustomer(id: string) {
  return useQuery({
    queryKey: FINANCIAL_QUERY_KEYS.customers.detail(id),
    queryFn: () => customerService.getById(id),
    enabled: !!id,
  });
}

export function useCreateCustomer() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: CustomerCreate) => customerService.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: FINANCIAL_QUERY_KEYS.customers.all });
    },
  });
}

export function useUpdateCustomer() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: CustomerUpdate }) =>
      customerService.update(id, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: FINANCIAL_QUERY_KEYS.customers.detail(variables.id) });
      queryClient.invalidateQueries({ queryKey: FINANCIAL_QUERY_KEYS.customers.lists() });
    },
  });
}

export function useDeleteCustomer() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => customerService.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: FINANCIAL_QUERY_KEYS.customers.all });
    },
  });
}

// ==================== BILLING RULES HOOKS ====================

export function useBillingRules(params?: { page?: number; page_size?: number; condominio_id?: string }) {
  return useQuery({
    queryKey: FINANCIAL_QUERY_KEYS.billingRules.list(params),
    queryFn: () => billingRuleService.list(params),
  });
}

export function useBillingRule(id: string) {
  return useQuery({
    queryKey: FINANCIAL_QUERY_KEYS.billingRules.detail(id),
    queryFn: () => billingRuleService.getById(id),
    enabled: !!id,
  });
}

export function useCreateBillingRule() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: BillingRuleCreate) => billingRuleService.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: FINANCIAL_QUERY_KEYS.billingRules.all });
    },
  });
}

export function useUpdateBillingRule() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: BillingRuleUpdate }) =>
      billingRuleService.update(id, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: FINANCIAL_QUERY_KEYS.billingRules.detail(variables.id) });
      queryClient.invalidateQueries({ queryKey: FINANCIAL_QUERY_KEYS.billingRules.lists() });
    },
  });
}

export function useDeleteBillingRule() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => billingRuleService.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: FINANCIAL_QUERY_KEYS.billingRules.all });
    },
  });
}

export function useActivateBillingRule() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => billingRuleService.activate(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: FINANCIAL_QUERY_KEYS.billingRules.all });
    },
  });
}

export function usePauseBillingRule() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => billingRuleService.pause(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: FINANCIAL_QUERY_KEYS.billingRules.all });
    },
  });
}

export function useGenerateBillingRule() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => billingRuleService.generate(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: FINANCIAL_QUERY_KEYS.receivables.all });
    },
  });
}

// ==================== RECEIVABLE CATEGORIES HOOKS ====================

export function useReceivableCategories(params?: { page?: number; page_size?: number; condominio_id?: string }) {
  return useQuery({
    queryKey: FINANCIAL_QUERY_KEYS.receivableCategories.lists(),
    queryFn: () => receivableCategoryService.list(params),
  });
}

export function useReceivableCategoryTree(params?: { condominio_id?: string }) {
  return useQuery({
    queryKey: FINANCIAL_QUERY_KEYS.receivableCategories.tree(),
    queryFn: () => receivableCategoryService.getTree(params),
  });
}

export function useCreateReceivableCategory() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: ReceivableCategoryCreate) => receivableCategoryService.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: FINANCIAL_QUERY_KEYS.receivableCategories.all });
    },
  });
}

export function useUpdateReceivableCategory() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: ReceivableCategoryUpdate }) =>
      receivableCategoryService.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: FINANCIAL_QUERY_KEYS.receivableCategories.all });
    },
  });
}

export function useDeleteReceivableCategory() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => receivableCategoryService.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: FINANCIAL_QUERY_KEYS.receivableCategories.all });
    },
  });
}

// ==================== BANK ACCOUNTS HOOKS ====================

export function useBankAccounts(params?: BankAccountFilter & { page?: number; page_size?: number; condominio_id?: string }) {
  return useQuery({
    queryKey: FINANCIAL_QUERY_KEYS.bankAccounts.list(params),
    queryFn: () => bankAccountService.list(params),
  });
}

export function useBankAccount(id: string) {
  return useQuery({
    queryKey: FINANCIAL_QUERY_KEYS.bankAccounts.detail(id),
    queryFn: () => bankAccountService.getById(id),
    enabled: !!id,
  });
}

export function useBankAccountStats(params?: { condominio_id?: string }) {
  return useQuery({
    queryKey: FINANCIAL_QUERY_KEYS.bankAccounts.stats(),
    queryFn: () => bankAccountService.getStats(params),
  });
}

export function useMainBankAccount(params?: { condominio_id?: string }) {
  return useQuery({
    queryKey: FINANCIAL_QUERY_KEYS.bankAccounts.main(),
    queryFn: () => bankAccountService.getMain(params),
  });
}

export function useCreateBankAccount() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: BankAccountCreate) => bankAccountService.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: FINANCIAL_QUERY_KEYS.bankAccounts.all });
    },
  });
}

export function useUpdateBankAccount() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: BankAccountUpdate }) =>
      bankAccountService.update(id, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: FINANCIAL_QUERY_KEYS.bankAccounts.detail(variables.id) });
      queryClient.invalidateQueries({ queryKey: FINANCIAL_QUERY_KEYS.bankAccounts.lists() });
    },
  });
}

export function useDeleteBankAccount() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => bankAccountService.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: FINANCIAL_QUERY_KEYS.bankAccounts.all });
    },
  });
}

export function useSetMainBankAccount() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => bankAccountService.setMain(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: FINANCIAL_QUERY_KEYS.bankAccounts.all });
    },
  });
}

export function useBankTransfer() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: TransferRequest) => bankAccountService.transfer(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: FINANCIAL_QUERY_KEYS.bankAccounts.all });
      queryClient.invalidateQueries({ queryKey: FINANCIAL_QUERY_KEYS.bankTransactions.all });
    },
  });
}

// ==================== BANK TRANSACTIONS HOOKS ====================

export function useBankTransactions(params?: BankTransactionFilter & { page?: number; page_size?: number; condominio_id?: string }) {
  return useQuery({
    queryKey: FINANCIAL_QUERY_KEYS.bankTransactions.list(params),
    queryFn: () => bankTransactionService.list(params),
  });
}

export function useBankTransaction(id: string) {
  return useQuery({
    queryKey: FINANCIAL_QUERY_KEYS.bankTransactions.detail(id),
    queryFn: () => bankTransactionService.getById(id),
    enabled: !!id,
  });
}

export function useBankTransactionSummary(params?: { condominio_id?: string; date_start?: string; date_end?: string }) {
  return useQuery({
    queryKey: FINANCIAL_QUERY_KEYS.bankTransactions.summary(),
    queryFn: () => bankTransactionService.getSummary(params),
  });
}

export function usePendingReconciliation(params?: { condominio_id?: string; account_id?: string }) {
  return useQuery({
    queryKey: FINANCIAL_QUERY_KEYS.bankTransactions.pending(),
    queryFn: () => bankTransactionService.getPendingReconciliation(params),
  });
}

export function useCreateBankTransaction() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: BankTransactionCreate) => bankTransactionService.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: FINANCIAL_QUERY_KEYS.bankTransactions.all });
      queryClient.invalidateQueries({ queryKey: FINANCIAL_QUERY_KEYS.bankAccounts.all });
    },
  });
}

export function useUpdateBankTransaction() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: BankTransactionUpdate }) =>
      bankTransactionService.update(id, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: FINANCIAL_QUERY_KEYS.bankTransactions.detail(variables.id) });
      queryClient.invalidateQueries({ queryKey: FINANCIAL_QUERY_KEYS.bankTransactions.lists() });
    },
  });
}

export function useConfirmBankTransaction() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => bankTransactionService.confirm(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: FINANCIAL_QUERY_KEYS.bankTransactions.all });
      queryClient.invalidateQueries({ queryKey: FINANCIAL_QUERY_KEYS.bankAccounts.all });
    },
  });
}

export function useCancelBankTransaction() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => bankTransactionService.cancel(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: FINANCIAL_QUERY_KEYS.bankTransactions.all });
      queryClient.invalidateQueries({ queryKey: FINANCIAL_QUERY_KEYS.bankAccounts.all });
    },
  });
}

export function useReconcileBankTransaction() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data?: { reconcile_with_id?: string; reconcile_with_type?: string } }) =>
      bankTransactionService.reconcile(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: FINANCIAL_QUERY_KEYS.bankTransactions.all });
    },
  });
}

// ==================== CASHFLOW HOOKS ====================

export function useCashflowSummary(params?: { condominio_id?: string; date_start?: string; date_end?: string }) {
  return useQuery({
    queryKey: FINANCIAL_QUERY_KEYS.cashflow.summary(params),
    queryFn: () => cashflowService.getSummary(params),
  });
}

export function useCashflowDashboard(params?: { condominio_id?: string; period?: string }) {
  return useQuery({
    queryKey: FINANCIAL_QUERY_KEYS.cashflow.dashboard(params),
    queryFn: () => cashflowService.getDashboard(params),
  });
}

export function useCashflowProjection(params?: { condominio_id?: string; days?: number }) {
  return useQuery({
    queryKey: FINANCIAL_QUERY_KEYS.cashflow.projection(params),
    queryFn: () => cashflowService.getProjection(params),
  });
}

export function useCashflowEntries(params?: CashFlowFilter & { page?: number; page_size?: number; condominio_id?: string }) {
  return useQuery({
    queryKey: [...FINANCIAL_QUERY_KEYS.cashflow.entries(), params],
    queryFn: () => cashflowService.listEntries(params),
  });
}

export function useCreateCashflowEntry() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: CashFlowEntryCreate) => cashflowService.createEntry(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: FINANCIAL_QUERY_KEYS.cashflow.all });
    },
  });
}

export function useUpdateCashflowEntry() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: CashFlowEntryUpdate }) =>
      cashflowService.updateEntry(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: FINANCIAL_QUERY_KEYS.cashflow.all });
    },
  });
}

export function useDeleteCashflowEntry() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => cashflowService.deleteEntry(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: FINANCIAL_QUERY_KEYS.cashflow.all });
    },
  });
}

export function useRealizeCashflowEntry() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data?: { realized_amount?: number; realized_date?: string } }) =>
      cashflowService.realizeEntry(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: FINANCIAL_QUERY_KEYS.cashflow.all });
    },
  });
}

// ==================== DASHBOARD HOOKS ====================

export function useFinancialDashboard(params?: { condominio_id?: string; period?: string }) {
  return useQuery({
    queryKey: FINANCIAL_QUERY_KEYS.dashboard.main(params),
    queryFn: () => financialDashboardService.getDashboard(params),
  });
}

export function useFinancialKPIs(params?: { condominio_id?: string }) {
  return useQuery({
    queryKey: FINANCIAL_QUERY_KEYS.dashboard.kpis(),
    queryFn: () => financialDashboardService.getKPIs(params),
  });
}

export function useFinancialAlerts(params?: { condominio_id?: string }) {
  return useQuery({
    queryKey: FINANCIAL_QUERY_KEYS.dashboard.alerts(),
    queryFn: () => financialDashboardService.getAlerts(params),
  });
}
