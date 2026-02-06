/**
 * Hook: useSuppliers
 *
 * Re-export dos hooks Orval para gerenciamento de fornecedores.
 * Cobertura: 11 endpoints - 100% Migrado para Orval
 *
 * Uso:
 *   import { useListSuppliers, useCreateSupplier } from '@/hooks/financial/useSuppliers';
 */

// Re-export de todos os hooks gerados pelo Orval
export * from '@/types/generated/financial/financial-suppliers/financial-suppliers';

// Aliases para compatibilidade com código legado
export {
  useListSuppliersApiV1FinancialSuppliersSuppliersGet as useSuppliers,
  useGetSupplierApiV1FinancialSuppliersSuppliersSupplierIdGet as useSupplier,
  useGetStatsApiV1FinancialSuppliersSuppliersStatsGet as useSupplierStats,
  useSearchSuppliersApiV1FinancialSuppliersSuppliersSearchGet as useSearchSuppliers,
  useCreateSupplierApiV1FinancialSuppliersSuppliersPost as useCreateSupplier,
  useUpdateSupplierApiV1FinancialSuppliersSuppliersSupplierIdPut as useUpdateSupplier,
  useDeleteSupplierApiV1FinancialSuppliersSuppliersSupplierIdDelete as useDeleteSupplier,
  useQualifySupplierApiV1FinancialSuppliersSuppliersSupplierIdQualifyPost as useQualifySupplier,
  useBlockSupplierApiV1FinancialSuppliersSuppliersSupplierIdBlockPost as useBlockSupplier,
  useUnblockSupplierApiV1FinancialSuppliersSuppliersSupplierIdUnblockPost as useUnblockSupplier,
  // Query Keys
  getListSuppliersApiV1FinancialSuppliersSuppliersGetQueryKey as supplierKeys,
} from '@/types/generated/financial/financial-suppliers/financial-suppliers';
