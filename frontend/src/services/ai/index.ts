/**
 * AI Services - Módulo de Inteligência Artificial
 * Exports centralizados para todos os services e hooks
 */

// ========== SERVICES ==========
export { DocumentsAIService } from './documents.service';
export { FinancialAIService } from './financial.service';
export { ClientsAIService } from './clients.service';
export { OperationalAIService } from './operational.service';
export { DocumentKitsAIService } from './document-kits.service';

// ========== HOOKS - DOCUMENTS AI ==========
export {
  useAnalyzeWithOCR,
  useClassifyDocument,
  useCheckDuplicates,
  useExtractKeywords,
  useDocumentInsights,
  useDocumentTrends,
  useDocumentsDashboard,
} from './hooks/useDocumentsAI';

// ========== HOOKS - FINANCIAL AI ==========
export {
  // Cashflow
  useDetectCashflowAnomalies,
  useForecastCashflow,
  useCashflowOpportunities,
  useCashflowRisks,
  useCashflowSuggestions,
  // Receivables
  useForecastReceivablesCashflow,
  useCollectionPriorities,
  useCustomerRiskAnalysis,
  useDelinquencyAnalysis,
  // Purchases
  usePredictDemand,
  useReorderPoint,
  useSuggestSuppliers,
  useSupplierAnalysis,
} from './hooks/useFinancialAI';

// ========== HOOKS - CLIENTS AI ==========
export {
  useChurnRisk,
  useClientProfile,
  useClientRecommendations,
  useClientSegmentation,
  useClientsDashboard,
  useCondominiumHealth,
} from './hooks/useClientsAI';

// ========== HOOKS - OPERATIONAL AI ==========
export {
  // Diaristas
  useCheckDiaristAvailability,
  useOptimizeDiaristAllocation,
  useDiaristPerformance,
  useSuggestDiarists,
  // Maintenance
  useEstimateMaintenanceCost,
  usePredictFailure,
  useEquipmentHealth,
  useMaintenancePatterns,
  useRecommendSchedule,
  useOptimizeRoute,
} from './hooks/useOperationalAI';

// ========== HOOKS - DOCUMENT KITS AI ==========
export {
  useCheckCompliance,
  useExpiringDocuments,
  usePredictStatus,
  useDocumentationPriorities,
  useSuggestDocuments,
  useDocumentUsageAnalysis,
} from './hooks/useDocumentKitsAI';
