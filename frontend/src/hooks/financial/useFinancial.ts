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
  useListTransactionsApiV1FinancialBankTransactionsBankTransactionsGet as useBankTransactions,
  useCreateTransactionApiV1FinancialBankTransactionsBankTransactionsPost as useCreateBankTransaction,
  useImportOfxFileApiV1FinancialBankTransactionsBankTransactionsImportOfxPost as useImportOFX,
  getListTransactionsApiV1FinancialBankTransactionsBankTransactionsGetQueryKey as bankTransactionKeys,
} from '@/types/generated/financial/financial-bank-transactions/financial-bank-transactions';

// =============================================================================
// CASHFLOW - Fluxo de Caixa
// =============================================================================
export * from '@/types/generated/financial/financial-cashflow/financial-cashflow';
export {
  useListEntriesApiV1FinancialCashflowCashflowEntriesGet as useCashflowEntries,
  useListForecastsApiV1FinancialCashflowCashflowForecastsGet as useCashflowForecast,
  useGetProjectionApiV1FinancialCashflowCashflowProjectionGet as useCashflowProjection,
  useGetDashboardApiV1FinancialCashflowCashflowDashboardGet as useCashflowDashboard,
  useCreateEntryApiV1FinancialCashflowCashflowEntriesPost as useCreateCashflowEntry,
  getListEntriesApiV1FinancialCashflowCashflowEntriesGetQueryKey as cashflowKeys,
} from '@/types/generated/financial/financial-cashflow/financial-cashflow';

// =============================================================================
// PURCHASE - Compras
// =============================================================================
export * from '@/types/generated/financial/financial-purchase/financial-purchase';
export {
  useListRequisitionsApiV1FinancialPurchasePurchasesRequisitionsGet as usePurchaseRequisitions,
  useListOrdersApiV1FinancialPurchasePurchasesOrdersGet as usePurchaseOrders,
  useGetRequisitionStatsApiV1FinancialPurchasePurchasesRequisitionsStatsGet as usePurchaseDashboard,
  useCreateRequisitionApiV1FinancialPurchasePurchasesRequisitionsPost as useCreatePurchaseRequisition,
  useCreateOrderApiV1FinancialPurchasePurchasesOrdersPost as useCreatePurchaseOrder,
  getListRequisitionsApiV1FinancialPurchasePurchasesRequisitionsGetQueryKey as purchaseKeys,
} from '@/types/generated/financial/financial-purchase/financial-purchase';

// =============================================================================
// INVENTORY - Estoque
// =============================================================================
export * from '@/types/generated/financial/financial-inventory/financial-inventory';
export {
  useListWarehousesApiV1FinancialInventoryInventoryWarehousesGet as useWarehouses,
  useListStockItemsApiV1FinancialInventoryInventoryStockItemsGet as useInventoryItems,
  useGetStockItemApiV1FinancialInventoryInventoryStockItemsItemIdGet as useInventoryItem,
  useGetStockStatsApiV1FinancialInventoryInventoryStockItemsStatsGet as useStockBalance,
  useGetWarehouseStatsApiV1FinancialInventoryInventoryWarehousesStatsGet as useInventoryDashboard,
  useCreateMovementApiV1FinancialInventoryInventoryMovementsPost as useCreateStockMovement,
  getListStockItemsApiV1FinancialInventoryInventoryStockItemsGetQueryKey as inventoryKeys,
} from '@/types/generated/financial/financial-inventory/financial-inventory';

// =============================================================================
// ACCOUNTING - Contabilidade
// =============================================================================
export * from '@/types/generated/financial/financial-accounting/financial-accounting';
export {
  useListAccountsApiV1FinancialAccountingAccountingAccountsGet as useAccountingAccounts,
  useListCostCentersApiV1FinancialAccountingAccountingCostCentersGet as useCostCenters,
  useListJournalEntriesApiV1FinancialAccountingAccountingJournalEntriesGet as useJournalEntries,
  useGetTrialBalanceApiV1FinancialAccountingAccountingTrialBalancesBalanceIdGet as useTrialBalance,
  useCreateJournalEntryApiV1FinancialAccountingAccountingJournalEntriesPost as useCreateJournalEntry,
  getListAccountsApiV1FinancialAccountingAccountingAccountsGetQueryKey as accountingKeys,
} from '@/types/generated/financial/financial-accounting/financial-accounting';

// =============================================================================
// FISCAL - Gestão Fiscal
// =============================================================================
export * from '@/types/generated/financial/financial-fiscal/financial-fiscal';
export {
  useListarNfesApiV1FinancialFiscalFiscalNfeGet as useNFes,
  useObterNfeApiV1FinancialFiscalFiscalNfeNfeIdGet as useNFe,
  useListarNfsesApiV1FinancialFiscalFiscalNfseGet as useNFSes,
  useObterDashboardFiscalApiV1FinancialFiscalFiscalDashboardGet as useFiscalDashboard,
  useCriarNfeApiV1FinancialFiscalFiscalNfePost as useCreateNFe,
  useEmitirNfeApiV1FinancialFiscalFiscalNfeEmitirPost as useAuthorizeNFe,
  getListarNfesApiV1FinancialFiscalFiscalNfeGetQueryKey as fiscalKeys,
} from '@/types/generated/financial/financial-fiscal/financial-fiscal';

// =============================================================================
// BI DASHBOARD - Business Intelligence
// =============================================================================
export * from '@/types/generated/financial/financial-bi-dashboard/financial-bi-dashboard';
export {
  useListDashboardsApiV1FinancialBiDashboardBiDashboardsGet as useBIDashboards,
  useGetDashboardApiV1FinancialBiDashboardBiDashboardsDashboardIdGet as useBIDashboard,
  useGetDashboardStatsApiV1FinancialBiDashboardBiDashboardsStatsGet as useFinancialOverview,
  getListDashboardsApiV1FinancialBiDashboardBiDashboardsGetQueryKey as biDashboardKeys,
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
