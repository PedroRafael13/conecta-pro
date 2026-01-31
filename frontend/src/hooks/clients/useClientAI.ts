/**
 * Hooks React Query - Client AI Services (Migrado para Orval)
 * Serviços de IA para Clientes
 *
 * MIGRADO: Re-exports dos hooks Orval gerados
 */

// Re-export dos hooks Orval com nomes simplificados
export {
  useAnalyzeClientProfileApiV1ClientsClientsClientIdAiProfileGet as useClientProfileAnalysis,
  useSuggestSegmentationApiV1ClientsClientsClientIdAiSegmentationGet as useClientSegmentation,
  usePredictChurnRiskApiV1ClientsClientsClientIdAiChurnRiskGet as useClientChurnRisk,
  useRecommendServicesApiV1ClientsClientsClientIdAiRecommendationsGet as useServiceRecommendations,
  useAnalyzeCondominiumHealthApiV1ClientsClientsCondominiumsCondominiumIdAiHealthGet as useCondominiumHealth,
  useGetDashboardInsightsApiV1ClientsClientsAiDashboardGet as useClientDashboardInsights,
} from '@/types/generated/clients/clients-cadastro';
