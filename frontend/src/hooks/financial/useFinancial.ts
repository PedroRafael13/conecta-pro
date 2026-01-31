/**
 * Hook Consolidado: useFinancial
 *
 * Re-export dos hooks Orval para todo o módulo FINANCIAL.
 * Cobertura: 483 endpoints em 15 submódulos - 100% Migrado para Orval.
 *
 * Este arquivo consolida os hooks de todos os submódulos financeiros.
 * Para hooks específicos, importe diretamente dos arquivos gerados ou use os aliases abaixo.
 */

// =============================================================================
// PAYABLES - Contas a Pagar
// =============================================================================
export * from '@/types/generated/financial/financial-payables/financial-payables';
export {
  useListAccountsApiV1FinancialPayablesPayablesGet as usePayables,
  useGetAccountApiV1FinancialPayablesPayablesAccountIdGet as usePayable,
  useGetStatsApiV1FinancialPayablesPayablesStatsGet as usePayableDashboard,
  useCreateAccountApiV1FinancialPayablesPayablesPost as useCreatePayable,
  useUpdateAccountApiV1FinancialPayablesPayablesAccountIdPut as useUpdatePayable,
  useRegisterPaymentApiV1FinancialPayablesPayablesInstallmentsInstallmentIdPayPost as useProcessPayment,
  getListAccountsApiV1FinancialPayablesPayablesGetQueryKey as payableKeys,
} from '@/types/generated/financial/financial-payables/financial-payables';

// =============================================================================
// CUSTOMERS - Clientes
// =============================================================================
export * from '@/types/generated/financial/financial-customers/financial-customers';
export {
  useListCustomersApiV1FinancialCustomersCustomersGet as useCustomers,
  useGetCustomerApiV1FinancialCustomersCustomersCustomerIdGet as useCustomer,
  useGetDebtSummaryApiV1FinancialCustomersCustomersCustomerIdDebtSummaryGet as useCustomerStats,
  useCreateCustomerApiV1FinancialCustomersCustomersPost as useCreateCustomer,
  getListCustomersApiV1FinancialCustomersCustomersGetQueryKey as customerKeys,
} from '@/types/generated/financial/financial-customers/financial-customers';

// =============================================================================
// RECEIVABLES - Contas a Receber
// =============================================================================
export * from '@/types/generated/financial/financial-receivables/financial-receivables';
export {
  useListAccountsApiV1FinancialReceivablesReceivablesGet as useReceivables,
  useGetAccountApiV1FinancialReceivablesReceivablesAccountIdGet as useReceivable,
  useGetStatsApiV1FinancialReceivablesReceivablesStatsGet as useReceivableDashboard,
  useCreateAccountApiV1FinancialReceivablesReceivablesPost as useCreateReceivable,
  useCreateAccountApiV1FinancialReceivablesReceivablesPost as useGenerateBilling, // Alias
  getListAccountsApiV1FinancialReceivablesReceivablesGetQueryKey as receivableKeys,
} from '@/types/generated/financial/financial-receivables/financial-receivables';

// =============================================================================
// BANK ACCOUNTS - Contas Bancárias
// =============================================================================
export * from '@/types/generated/financial/financial-bank-accounts/financial-bank-accounts';
export {
  useListBankAccountsApiV1FinancialBankAccountsBankAccountsGet as useBankAccounts,
  useGetBankAccountApiV1FinancialBankAccountsBankAccountsAccountIdGet as useBankAccount,
  useGetBalanceApiV1FinancialBankAccountsBankAccountsAccountIdBalanceGet as useBankAccountBalance,
  useCreateBankAccountApiV1FinancialBankAccountsBankAccountsPost as useCreateBankAccount,
  getListBankAccountsApiV1FinancialBankAccountsBankAccountsGetQueryKey as bankAccountKeys,
} from '@/types/generated/financial/financial-bank-accounts/financial-bank-accounts';

// =============================================================================
// BANK TRANSACTIONS - Transações Bancárias
// =============================================================================
export * from '@/types/generated/financial/financial-bank-transactions/financial-bank-transactions';
export {
  useListTransactionsApiV1FinancialBankTransactionsTransactionsGet as useBankTransactions,
  useCreateTransactionApiV1FinancialBankTransactionsTransactionsPost as useCreateBankTransaction,
  useImportOfxApiV1FinancialBankTransactionsTransactionsImportOfxPost as useImportOFX,
  getListTransactionsApiV1FinancialBankTransactionsTransactionsGetQueryKey as bankTransactionKeys,
} from '@/types/generated/financial/financial-bank-transactions/financial-bank-transactions';

// =============================================================================
// CASHFLOW - Fluxo de Caixa
// =============================================================================
export * from '@/types/generated/financial/financial-cashflow/financial-cashflow';
export {
  useListEntriesApiV1FinancialCashflowEntriesGet as useCashflowEntries,
  useGetForecastApiV1FinancialCashflowForecastGet as useCashflowForecast,
  useGetProjectionApiV1FinancialCashflowProjectionGet as useCashflowProjection,
  useGetDashboardApiV1FinancialCashflowDashboardGet as useCashflowDashboard,
  useCreateEntryApiV1FinancialCashflowEntriesPost as useCreateCashflowEntry,
  getListEntriesApiV1FinancialCashflowEntriesGetQueryKey as cashflowKeys,
} from '@/types/generated/financial/financial-cashflow/financial-cashflow';

// =============================================================================
// PURCHASE - Compras
// =============================================================================
export * from '@/types/generated/financial/financial-purchase/financial-purchase';
export {
  useListRequisitionsApiV1FinancialPurchaseRequisitionsGet as usePurchaseRequisitions,
  useListOrdersApiV1FinancialPurchaseOrdersGet as usePurchaseOrders,
  useGetDashboardApiV1FinancialPurchaseDashboardGet as usePurchaseDashboard,
  useCreateRequisitionApiV1FinancialPurchaseRequisitionsPost as useCreatePurchaseRequisition,
  useCreateOrderApiV1FinancialPurchaseOrdersPost as useCreatePurchaseOrder,
  getListRequisitionsApiV1FinancialPurchaseRequisitionsGetQueryKey as purchaseKeys,
} from '@/types/generated/financial/financial-purchase/financial-purchase';

// =============================================================================
// INVENTORY - Estoque
// =============================================================================
export * from '@/types/generated/financial/financial-inventory/financial-inventory';
export {
  useListWarehousesApiV1FinancialInventoryWarehousesGet as useWarehouses,
  useListItemsApiV1FinancialInventoryItemsGet as useInventoryItems,
  useGetItemApiV1FinancialInventoryItemsItemIdGet as useInventoryItem,
  useGetStockBalanceApiV1FinancialInventoryStockBalanceGet as useStockBalance,
  useGetDashboardApiV1FinancialInventoryDashboardGet as useInventoryDashboard,
  useCreateStockMovementApiV1FinancialInventoryStockMovementsPost as useCreateStockMovement,
  getListItemsApiV1FinancialInventoryItemsGetQueryKey as inventoryKeys,
} from '@/types/generated/financial/financial-inventory/financial-inventory';

// =============================================================================
// ACCOUNTING - Contabilidade
// =============================================================================
export * from '@/types/generated/financial/financial-accounting/financial-accounting';
export {
  useListAccountsApiV1FinancialAccountingAccountsGet as useAccountingAccounts,
  useListCostCentersApiV1FinancialAccountingCostCentersGet as useCostCenters,
  useListJournalEntriesApiV1FinancialAccountingJournalEntriesGet as useJournalEntries,
  useGetTrialBalanceApiV1FinancialAccountingTrialBalanceGet as useTrialBalance,
  useCreateJournalEntryApiV1FinancialAccountingJournalEntriesPost as useCreateJournalEntry,
  getListAccountsApiV1FinancialAccountingAccountsGetQueryKey as accountingKeys,
} from '@/types/generated/financial/financial-accounting/financial-accounting';

// =============================================================================
// FISCAL - Gestão Fiscal
// =============================================================================
export * from '@/types/generated/financial/financial-fiscal/financial-fiscal';
export {
  useListNfesApiV1FinancialFiscalNfesGet as useNFes,
  useGetNfeApiV1FinancialFiscalNfesNfeIdGet as useNFe,
  useListNfsesApiV1FinancialFiscalNfsesGet as useNFSes,
  useGetDashboardApiV1FinancialFiscalDashboardGet as useFiscalDashboard,
  useCreateNfeApiV1FinancialFiscalNfesPost as useCreateNFe,
  useAuthorizeNfeApiV1FinancialFiscalNfesNfeIdAuthorizePost as useAuthorizeNFe,
  getListNfesApiV1FinancialFiscalNfesGetQueryKey as fiscalKeys,
} from '@/types/generated/financial/financial-fiscal/financial-fiscal';

// =============================================================================
// BI DASHBOARD - Business Intelligence
// =============================================================================
export * from '@/types/generated/financial/financial-bi-dashboard/financial-bi-dashboard';
export {
  useListDashboardsApiV1FinancialBiDashboardDashboardsGet as useBIDashboards,
  useGetDashboardApiV1FinancialBiDashboardDashboardsDashboardIdGet as useBIDashboard,
  useGetFinancialOverviewApiV1FinancialBiDashboardFinancialOverviewGet as useFinancialOverview,
  useGetRevenueAnalysisApiV1FinancialBiDashboardRevenueAnalysisGet as useRevenueAnalysis,
  useGetExpenseAnalysisApiV1FinancialBiDashboardExpenseAnalysisGet as useExpenseAnalysis,
  getListDashboardsApiV1FinancialBiDashboardDashboardsGetQueryKey as biDashboardKeys,
} from '@/types/generated/financial/financial-bi-dashboard/financial-bi-dashboard';

// =============================================================================
// COSTING - Custeio ABC
// =============================================================================
export * from '@/types/generated/financial/financial-abc-costing/financial-abc-costing';
export {
  useListCostDriversApiV1FinancialAbcCostingCostDriversGet as useCostDrivers,
  useListCostActivitiesApiV1FinancialAbcCostingCostActivitiesGet as useCostActivities,
  useListCostPoolsApiV1FinancialAbcCostingCostPoolsGet as useCostPools,
  useListCostObjectsApiV1FinancialAbcCostingCostObjectsGet as useCostObjects,
  useGetDashboardApiV1FinancialAbcCostingDashboardGet as useCostingDashboard,
  useGetCostAnalysisApiV1FinancialAbcCostingCostAnalysisGet as useCostAnalysis,
  useCreateCostDriverApiV1FinancialAbcCostingCostDriversPost as useCreateCostDriver,
  getListCostDriversApiV1FinancialAbcCostingCostDriversGetQueryKey as costingKeys,
} from '@/types/generated/financial/financial-abc-costing/financial-abc-costing';
