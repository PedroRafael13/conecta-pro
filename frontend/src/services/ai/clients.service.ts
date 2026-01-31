/**
 * Clients AI Service
 * Análise inteligente de clientes: perfil, segmentação, churn
 */

import { getClientsCadastro } from '@/types/generated/ai/clients-cadastro/clients-cadastro';

const clientsApi = getClientsCadastro();

/**
 * Service para análise de clientes com IA
 */
export class ClientsAIService {
  /**
   * Analisa risco de churn do cliente
   */
  static async analyzeChurnRisk(clientId: string): Promise<any> {
    return clientsApi.predictChurnRiskApiV1ClientsClientIdAiChurnRiskGet(clientId);
  }

  /**
   * Obtém perfil completo do cliente com insights
   */
  static async getClientProfile(clientId: string): Promise<any> {
    return clientsApi.analyzeClientProfileApiV1ClientsClientIdAiProfileGet(clientId);
  }

  /**
   * Obtém recomendações personalizadas para o cliente
   */
  static async getRecommendations(clientId: string): Promise<any> {
    return clientsApi.recommendServicesApiV1ClientsClientIdAiRecommendationsGet(clientId);
  }

  /**
   * Segmenta cliente em grupos estratégicos
   */
  static async getSegmentation(clientId: string): Promise<any> {
    return clientsApi.suggestSegmentationApiV1ClientsClientIdAiSegmentationGet(clientId);
  }

  /**
   * Dashboard agregado de análise de clientes
   */
  static async getDashboard(): Promise<any> {
    return clientsApi.getDashboardInsightsApiV1ClientsAiDashboardGet();
  }

  /**
   * Analisa saúde operacional do condomínio
   */
  static async analyzeCondominiumHealth(condominiumId: string): Promise<any> {
    return clientsApi.analyzeCondominiumHealthApiV1ClientsCondominiumsCondominiumIdAiHealthGet(condominiumId);
  }
}

export default ClientsAIService;
