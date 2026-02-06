/**
 * Service Layer - Client AI Services (DEPRECATED)
 * Serviços de IA para Análise de Clientes
 *
 * @deprecated Use hooks Orval de @/types/generated/clients/clients-cadastro/clients-cadastro
 *
 * Mapeamento de hooks:
 * - clientAIService.analyzeProfile -> useAnalyzeClientProfileApiV1ClientsClientsClientIdAiProfileGet
 * - clientAIService.suggestSegmentation -> useSuggestSegmentationApiV1ClientsClientsClientIdAiSegmentationGet
 * - clientAIService.predictChurnRisk -> usePredictChurnRiskApiV1ClientsClientsClientIdAiChurnRiskGet
 * - clientAIService.recommendServices -> useRecommendServicesApiV1ClientsClientsClientIdAiRecommendationsGet
 * - clientAIService.analyzeCondominiumHealth -> useAnalyzeCondominiumHealthApiV1ClientsClientsCondominiumsCondominiumIdAiHealthGet
 * - clientAIService.getDashboardInsights -> useGetDashboardInsightsApiV1ClientsClientsAiDashboardGet
 */

// Re-export dos hooks Orval para compatibilidade
export {
  useAnalyzeClientProfileApiV1ClientsClientsClientIdAiProfileGet as useAnalyzeClientProfile,
  useSuggestSegmentationApiV1ClientsClientsClientIdAiSegmentationGet as useSuggestSegmentation,
  usePredictChurnRiskApiV1ClientsClientsClientIdAiChurnRiskGet as usePredictChurnRisk,
  useRecommendServicesApiV1ClientsClientsClientIdAiRecommendationsGet as useRecommendServices,
  useAnalyzeCondominiumHealthApiV1ClientsClientsCondominiumsCondominiumIdAiHealthGet as useAnalyzeCondominiumHealth,
  useGetDashboardInsightsApiV1ClientsClientsAiDashboardGet as useGetDashboardInsights,
} from '@/types/generated/clients/clients-cadastro';
