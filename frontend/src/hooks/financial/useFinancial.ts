/**
 * Hook Consolidado: useFinancial
 *
 * Hooks React Query para todo o módulo FINANCIAL.
 * Cobertura: 483 endpoints em 15 submódulos.
 *
 * Este arquivo consolida os hooks mais usados de cada submódulo.
 * Para hooks específicos, importe diretamente do arquivo correspondente.
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  supplierService,
  payableService,
  customerService,
  receivableService,
  bankAccountService,
  bankTransactionService,
  cashflowService,
  purchaseService,
  inventoryService,
  accountingService,
  fiscalService,
  biDashboardService,
  costingService,
} from '@/services/financial';

// =============================================================================
// PAYABLES - Contas a Pagar
// =============================================================================

export const payableKeys = {
  all: ['payables'] as const,
  lists: () => [...payableKeys.all, 'list'] as const,
  list: (filters: any) => [...payableKeys.lists(), filters] as const,
  details: () => [...payableKeys.all, 'detail'] as const,
  detail: (id: string) => [...payableKeys.details(), id] as const,
  dashboard: (condominioId: string) =>
    [...payableKeys.all, 'dashboard', condominioId] as const,
};

export function usePayables(params: any = {}) {
  return useQuery({
    queryKey: payableKeys.list(params),
    queryFn: () => payableService.list(params),
  });
}

export function usePayable(payableId: string, enabled = true) {
  return useQuery({
    queryKey: payableKeys.detail(payableId),
    queryFn: () => payableService.getById(payableId),
    enabled: enabled && !!payableId,
  });
}

export function usePayableDashboard(condominioId: string) {
  return useQuery({
    queryKey: payableKeys.dashboard(condominioId),
    queryFn: () => payableService.getDashboard(condominioId),
    enabled: !!condominioId,
  });
}

export function useCreatePayable() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: any) => payableService.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: payableKeys.lists() });
    },
  });
}

export function useUpdatePayable() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: any }) =>
      payableService.update(id, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: payableKeys.lists() });
      queryClient.invalidateQueries({
        queryKey: payableKeys.detail(variables.id),
      });
    },
  });
}

export function useProcessPayment() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: any) => payableService.processPayment(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: payableKeys.lists() });
    },
  });
}

// =============================================================================
// CUSTOMERS - Clientes
// =============================================================================

export const customerKeys = {
  all: ['customers'] as const,
  lists: () => [...customerKeys.all, 'list'] as const,
  list: (filters: any) => [...customerKeys.lists(), filters] as const,
  details: () => [...customerKeys.all, 'detail'] as const,
  detail: (id: string) => [...customerKeys.details(), id] as const,
  stats: (condominioId: string) =>
    [...customerKeys.all, 'stats', condominioId] as const,
};

export function useCustomers(params: any = {}) {
  return useQuery({
    queryKey: customerKeys.list(params),
    queryFn: () => customerService.list(params),
  });
}

export function useCustomer(customerId: string, enabled = true) {
  return useQuery({
    queryKey: customerKeys.detail(customerId),
    queryFn: () => customerService.getById(customerId),
    enabled: enabled && !!customerId,
  });
}

export function useCustomerStats(condominioId: string) {
  return useQuery({
    queryKey: customerKeys.stats(condominioId),
    queryFn: () => customerService.getStats(condominioId),
    enabled: !!condominioId,
  });
}

export function useCreateCustomer() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: any) => customerService.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: customerKeys.lists() });
    },
  });
}

// =============================================================================
// RECEIVABLES - Contas a Receber
// =============================================================================

export const receivableKeys = {
  all: ['receivables'] as const,
  lists: () => [...receivableKeys.all, 'list'] as const,
  list: (filters: any) => [...receivableKeys.lists(), filters] as const,
  details: () => [...receivableKeys.all, 'detail'] as const,
  detail: (id: string) => [...receivableKeys.details(), id] as const,
  dashboard: (condominioId: string) =>
    [...receivableKeys.all, 'dashboard', condominioId] as const,
};

export function useReceivables(params: any = {}) {
  return useQuery({
    queryKey: receivableKeys.list(params),
    queryFn: () => receivableService.list(params),
  });
}

export function useReceivable(receivableId: string, enabled = true) {
  return useQuery({
    queryKey: receivableKeys.detail(receivableId),
    queryFn: () => receivableService.getById(receivableId),
    enabled: enabled && !!receivableId,
  });
}

export function useReceivableDashboard(condominioId: string) {
  return useQuery({
    queryKey: receivableKeys.dashboard(condominioId),
    queryFn: () => receivableService.getDashboard(condominioId),
    enabled: !!condominioId,
  });
}

export function useCreateReceivable() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: any) => receivableService.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: receivableKeys.lists() });
    },
  });
}

export function useGenerateBilling() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      condominioId,
      referenceMonth,
    }: {
      condominioId: string;
      referenceMonth: string;
    }) => receivableService.generateBilling(condominioId, referenceMonth),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: receivableKeys.lists() });
    },
  });
}

// =============================================================================
// BANK ACCOUNTS - Contas Bancárias
// =============================================================================

export const bankAccountKeys = {
  all: ['bank-accounts'] as const,
  lists: () => [...bankAccountKeys.all, 'list'] as const,
  list: (filters: any) => [...bankAccountKeys.lists(), filters] as const,
  details: () => [...bankAccountKeys.all, 'detail'] as const,
  detail: (id: string) => [...bankAccountKeys.details(), id] as const,
  balance: (id: string) => [...bankAccountKeys.all, 'balance', id] as const,
};

export function useBankAccounts(params: any = {}) {
  return useQuery({
    queryKey: bankAccountKeys.list(params),
    queryFn: () => bankAccountService.list(params),
  });
}

export function useBankAccount(accountId: string, enabled = true) {
  return useQuery({
    queryKey: bankAccountKeys.detail(accountId),
    queryFn: () => bankAccountService.getById(accountId),
    enabled: enabled && !!accountId,
  });
}

export function useBankAccountBalance(accountId: string, enabled = true) {
  return useQuery({
    queryKey: bankAccountKeys.balance(accountId),
    queryFn: () => bankAccountService.getBalance(accountId),
    enabled: enabled && !!accountId,
    refetchInterval: 30000, // Atualiza a cada 30s
  });
}

export function useCreateBankAccount() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: any) => bankAccountService.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: bankAccountKeys.lists() });
    },
  });
}

// =============================================================================
// BANK TRANSACTIONS - Transações Bancárias
// =============================================================================

export const bankTransactionKeys = {
  all: ['bank-transactions'] as const,
  lists: () => [...bankTransactionKeys.all, 'list'] as const,
  list: (filters: any) => [...bankTransactionKeys.lists(), filters] as const,
  details: () => [...bankTransactionKeys.all, 'detail'] as const,
  detail: (id: string) => [...bankTransactionKeys.details(), id] as const,
};

export function useBankTransactions(params: any = {}) {
  return useQuery({
    queryKey: bankTransactionKeys.list(params),
    queryFn: () => bankTransactionService.list(params),
  });
}

export function useCreateBankTransaction() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: any) => bankTransactionService.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: bankTransactionKeys.lists() });
      queryClient.invalidateQueries({ queryKey: bankAccountKeys.all });
    },
  });
}

export function useImportOFX() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      accountId,
      file,
    }: {
      accountId: string;
      file: File;
    }) => bankTransactionService.importOFX(accountId, file),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: bankTransactionKeys.lists() });
    },
  });
}

// =============================================================================
// CASHFLOW - Fluxo de Caixa
// =============================================================================

export const cashflowKeys = {
  all: ['cashflow'] as const,
  entries: () => [...cashflowKeys.all, 'entries'] as const,
  forecast: (params: any) => [...cashflowKeys.all, 'forecast', params] as const,
  dailyFlow: (params: any) => [...cashflowKeys.all, 'daily', params] as const,
  projection: (condominioId: string, months: number) =>
    [...cashflowKeys.all, 'projection', condominioId, months] as const,
  dashboard: (condominioId: string) =>
    [...cashflowKeys.all, 'dashboard', condominioId] as const,
};

export function useCashflowEntries(params: any = {}) {
  return useQuery({
    queryKey: cashflowKeys.entries(),
    queryFn: () => cashflowService.listEntries(params),
  });
}

export function useCashflowForecast(params: any) {
  return useQuery({
    queryKey: cashflowKeys.forecast(params),
    queryFn: () => cashflowService.getForecast(params),
    enabled: !!params.condominio_id,
  });
}

export function useCashflowProjection(condominioId: string, months = 12) {
  return useQuery({
    queryKey: cashflowKeys.projection(condominioId, months),
    queryFn: () => cashflowService.getProjection(condominioId, months),
    enabled: !!condominioId,
  });
}

export function useCashflowDashboard(condominioId: string) {
  return useQuery({
    queryKey: cashflowKeys.dashboard(condominioId),
    queryFn: () => cashflowService.getDashboard(condominioId),
    enabled: !!condominioId,
  });
}

export function useCreateCashflowEntry() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: any) => cashflowService.createEntry(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: cashflowKeys.entries() });
    },
  });
}

// =============================================================================
// PURCHASE - Compras
// =============================================================================

export const purchaseKeys = {
  all: ['purchase'] as const,
  requisitions: () => [...purchaseKeys.all, 'requisitions'] as const,
  requisition: (id: string) =>
    [...purchaseKeys.all, 'requisition', id] as const,
  orders: () => [...purchaseKeys.all, 'orders'] as const,
  order: (id: string) => [...purchaseKeys.all, 'order', id] as const,
  dashboard: (condominioId: string) =>
    [...purchaseKeys.all, 'dashboard', condominioId] as const,
};

export function usePurchaseRequisitions(params: any = {}) {
  return useQuery({
    queryKey: purchaseKeys.requisitions(),
    queryFn: () => purchaseService.listRequisitions(params),
  });
}

export function usePurchaseOrders(params: any = {}) {
  return useQuery({
    queryKey: purchaseKeys.orders(),
    queryFn: () => purchaseService.listOrders(params),
  });
}

export function usePurchaseDashboard(condominioId: string) {
  return useQuery({
    queryKey: purchaseKeys.dashboard(condominioId),
    queryFn: () => purchaseService.getDashboard(condominioId),
    enabled: !!condominioId,
  });
}

export function useCreatePurchaseRequisition() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: any) => purchaseService.createRequisition(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: purchaseKeys.requisitions() });
    },
  });
}

export function useCreatePurchaseOrder() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: any) => purchaseService.createOrder(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: purchaseKeys.orders() });
    },
  });
}

// =============================================================================
// INVENTORY - Estoque
// =============================================================================

export const inventoryKeys = {
  all: ['inventory'] as const,
  warehouses: () => [...inventoryKeys.all, 'warehouses'] as const,
  items: () => [...inventoryKeys.all, 'items'] as const,
  item: (id: string) => [...inventoryKeys.all, 'item', id] as const,
  balance: (itemId: string, warehouseId?: string) =>
    [...inventoryKeys.all, 'balance', itemId, warehouseId] as const,
  dashboard: (condominioId: string) =>
    [...inventoryKeys.all, 'dashboard', condominioId] as const,
};

export function useWarehouses(params: any = {}) {
  return useQuery({
    queryKey: inventoryKeys.warehouses(),
    queryFn: () => inventoryService.listWarehouses(params),
  });
}

export function useInventoryItems(params: any = {}) {
  return useQuery({
    queryKey: inventoryKeys.items(),
    queryFn: () => inventoryService.listItems(params),
  });
}

export function useInventoryItem(itemId: string, enabled = true) {
  return useQuery({
    queryKey: inventoryKeys.item(itemId),
    queryFn: () => inventoryService.getItem(itemId),
    enabled: enabled && !!itemId,
  });
}

export function useStockBalance(
  itemId: string,
  warehouseId?: string,
  enabled = true
) {
  return useQuery({
    queryKey: inventoryKeys.balance(itemId, warehouseId),
    queryFn: () => inventoryService.getItemBalance(itemId, warehouseId),
    enabled: enabled && !!itemId,
  });
}

export function useInventoryDashboard(condominioId: string) {
  return useQuery({
    queryKey: inventoryKeys.dashboard(condominioId),
    queryFn: () => inventoryService.getDashboard(condominioId),
    enabled: !!condominioId,
  });
}

export function useCreateStockMovement() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: any) => inventoryService.createMovement(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: inventoryKeys.items() });
    },
  });
}

// =============================================================================
// ACCOUNTING - Contabilidade
// =============================================================================

export const accountingKeys = {
  all: ['accounting'] as const,
  accounts: () => [...accountingKeys.all, 'accounts'] as const,
  account: (id: string) => [...accountingKeys.all, 'account', id] as const,
  costCenters: () => [...accountingKeys.all, 'cost-centers'] as const,
  journalEntries: () => [...accountingKeys.all, 'journal-entries'] as const,
  trialBalance: (condominioId: string, periodId: string) =>
    [...accountingKeys.all, 'trial-balance', condominioId, periodId] as const,
};

export function useAccountingAccounts(params: any = {}) {
  return useQuery({
    queryKey: accountingKeys.accounts(),
    queryFn: () => accountingService.listAccounts(params),
  });
}

export function useCostCenters(params: any = {}) {
  return useQuery({
    queryKey: accountingKeys.costCenters(),
    queryFn: () => accountingService.listCostCenters(params),
  });
}

export function useJournalEntries(params: any = {}) {
  return useQuery({
    queryKey: accountingKeys.journalEntries(),
    queryFn: () => accountingService.listJournalEntries(params),
  });
}

export function useTrialBalance(condominioId: string, periodId: string) {
  return useQuery({
    queryKey: accountingKeys.trialBalance(condominioId, periodId),
    queryFn: () => accountingService.getTrialBalance(condominioId, periodId),
    enabled: !!condominioId && !!periodId,
  });
}

export function useCreateJournalEntry() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: any) => accountingService.createJournalEntry(data),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: accountingKeys.journalEntries(),
      });
    },
  });
}

// =============================================================================
// FISCAL - Gestão Fiscal
// =============================================================================

export const fiscalKeys = {
  all: ['fiscal'] as const,
  nfes: () => [...fiscalKeys.all, 'nfes'] as const,
  nfe: (id: string) => [...fiscalKeys.all, 'nfe', id] as const,
  nfses: () => [...fiscalKeys.all, 'nfses'] as const,
  speds: () => [...fiscalKeys.all, 'speds'] as const,
  dashboard: (condominioId: string) =>
    [...fiscalKeys.all, 'dashboard', condominioId] as const,
};

export function useNFes(params: any = {}) {
  return useQuery({
    queryKey: fiscalKeys.nfes(),
    queryFn: () => fiscalService.listNFes(params),
  });
}

export function useNFe(nfeId: string, enabled = true) {
  return useQuery({
    queryKey: fiscalKeys.nfe(nfeId),
    queryFn: () => fiscalService.getNFe(nfeId),
    enabled: enabled && !!nfeId,
  });
}

export function useNFSes(params: any = {}) {
  return useQuery({
    queryKey: fiscalKeys.nfses(),
    queryFn: () => fiscalService.listNFSes(params),
  });
}

export function useFiscalDashboard(condominioId: string) {
  return useQuery({
    queryKey: fiscalKeys.dashboard(condominioId),
    queryFn: () => fiscalService.getDashboard(condominioId),
    enabled: !!condominioId,
  });
}

export function useCreateNFe() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: any) => fiscalService.createNFe(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: fiscalKeys.nfes() });
    },
  });
}

export function useAuthorizeNFe() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (nfeId: string) => fiscalService.authorizeNFe(nfeId),
    onSuccess: (_, nfeId) => {
      queryClient.invalidateQueries({ queryKey: fiscalKeys.nfe(nfeId) });
      queryClient.invalidateQueries({ queryKey: fiscalKeys.nfes() });
    },
  });
}

// =============================================================================
// BI DASHBOARD - Business Intelligence
// =============================================================================

export const biDashboardKeys = {
  all: ['bi-dashboard'] as const,
  dashboards: () => [...biDashboardKeys.all, 'dashboards'] as const,
  dashboard: (id: string) => [...biDashboardKeys.all, 'dashboard', id] as const,
  kpis: () => [...biDashboardKeys.all, 'kpis'] as const,
  overview: (condominioId: string) =>
    [...biDashboardKeys.all, 'overview', condominioId] as const,
};

export function useBIDashboards(params: any = {}) {
  return useQuery({
    queryKey: biDashboardKeys.dashboards(),
    queryFn: () => biDashboardService.listDashboards(params),
  });
}

export function useBIDashboard(dashboardId: string, enabled = true) {
  return useQuery({
    queryKey: biDashboardKeys.dashboard(dashboardId),
    queryFn: () => biDashboardService.getDashboard(dashboardId),
    enabled: enabled && !!dashboardId,
  });
}

export function useFinancialOverview(condominioId: string) {
  return useQuery({
    queryKey: biDashboardKeys.overview(condominioId),
    queryFn: () => biDashboardService.getFinancialOverview(condominioId),
    enabled: !!condominioId,
  });
}

export function useRevenueAnalysis(
  condominioId: string,
  startDate: string,
  endDate: string
) {
  return useQuery({
    queryKey: [
      ...biDashboardKeys.all,
      'revenue',
      condominioId,
      startDate,
      endDate,
    ],
    queryFn: () =>
      biDashboardService.getRevenueAnalysis(condominioId, startDate, endDate),
    enabled: !!condominioId && !!startDate && !!endDate,
  });
}

export function useExpenseAnalysis(
  condominioId: string,
  startDate: string,
  endDate: string
) {
  return useQuery({
    queryKey: [
      ...biDashboardKeys.all,
      'expense',
      condominioId,
      startDate,
      endDate,
    ],
    queryFn: () =>
      biDashboardService.getExpenseAnalysis(condominioId, startDate, endDate),
    enabled: !!condominioId && !!startDate && !!endDate,
  });
}

// =============================================================================
// COSTING - Custeio ABC
// =============================================================================

export const costingKeys = {
  all: ['costing'] as const,
  drivers: () => [...costingKeys.all, 'drivers'] as const,
  activities: () => [...costingKeys.all, 'activities'] as const,
  pools: () => [...costingKeys.all, 'pools'] as const,
  objects: () => [...costingKeys.all, 'objects'] as const,
  dashboard: (condominioId: string) =>
    [...costingKeys.all, 'dashboard', condominioId] as const,
};

export function useCostDrivers(params: any = {}) {
  return useQuery({
    queryKey: costingKeys.drivers(),
    queryFn: () => costingService.listDrivers(params),
  });
}

export function useCostActivities(params: any = {}) {
  return useQuery({
    queryKey: costingKeys.activities(),
    queryFn: () => costingService.listActivities(params),
  });
}

export function useCostPools(params: any = {}) {
  return useQuery({
    queryKey: costingKeys.pools(),
    queryFn: () => costingService.listPools(params),
  });
}

export function useCostObjects(params: any = {}) {
  return useQuery({
    queryKey: costingKeys.objects(),
    queryFn: () => costingService.listObjects(params),
  });
}

export function useCostingDashboard(condominioId: string) {
  return useQuery({
    queryKey: costingKeys.dashboard(condominioId),
    queryFn: () => costingService.getDashboard(condominioId),
    enabled: !!condominioId,
  });
}

export function useCostAnalysis(condominioId: string, periodId: string) {
  return useQuery({
    queryKey: [...costingKeys.all, 'analysis', condominioId, periodId],
    queryFn: () => costingService.getCostAnalysis(condominioId, periodId),
    enabled: !!condominioId && !!periodId,
  });
}

export function useCreateCostDriver() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: any) => costingService.createDriver(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: costingKeys.drivers() });
    },
  });
}
