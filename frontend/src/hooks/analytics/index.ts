/**
 * Analytics Hooks
 *
 * Exporta todos os hooks do módulo Analytics.
 */

// Executive Dashboard
export {
  useExecutiveDashboard,
  useKpisByCategory,
  useActiveAlerts,
  usePredictiveInsights,
  useExecutiveSummary,
  useExportDashboard,
  useDashboardHealth,
} from './useExecutiveDashboard';

// Churn Prediction
export {
  usePredictChurn,
  useHighRiskUsers,
  useChurnAnalytics,
} from './useChurnPrediction';

// Forecast
export {
  useSalesForecast,
  useForecastScenarios,
  useForecastAccuracy,
} from './useForecast';

// Fraud Detection
export {
  useAnalyzeTransaction,
  useFraudAlerts,
  useUpdateAlertStatus,
  useFraudAnalytics,
  useUserRiskProfile,
} from './useFraudDetection';

// Lead Scoring
export {
  useScoreLead,
  useTopLeads,
  useScoringAnalytics,
} from './useLeadScoring';

// Model Management
export {
  useModels,
  useModelVersions,
  useCompareVersions,
  usePromoteModel,
} from './useModelManagement';

// Monitoring
export {
  useMonitoringDashboard,
  useModelHealth,
  useMonitoringAlerts,
  useAcknowledgeAlert,
} from './useMonitoring';

// Feature Store
export {
  useUserFeatures,
  useAvailableFeatures,
  useFeatureMetadata,
} from './useFeatureStore';
