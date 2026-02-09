/**
 * Clients AI Service
 * Análise inteligente de clientes: perfil, segmentação, churn
 */

import { customInstance } from '@/lib/axios-instance';

/**
 * Service para análise de clientes com IA
 */
export class ClientsAIService {
  /**
   * Analisa risco de churn do cliente
   */
  static async analyzeChurnRisk(clientId: string): Promise<unknown> {
    return customInstance.get(`/api/v1/clients/${clientId}/ai/churn-risk`);
  }

  /**
   * Obtém perfil completo do cliente com insights
   */
  static async getClientProfile(clientId: string): Promise<unknown> {
    return customInstance.get(`/api/v1/clients/${clientId}/ai/profile`);
  }

  /**
   * Obtém recomendações personalizadas para o cliente
   */
  static async getRecommendations(clientId: string): Promise<unknown> {
    return customInstance.get(`/api/v1/clients/${clientId}/ai/recommendations`);
  }

  /**
   * Segmenta cliente em grupos estratégicos
   */
  static async getSegmentation(clientId: string): Promise<unknown> {
    return customInstance.get(`/api/v1/clients/${clientId}/ai/segmentation`);
  }

  /**
   * Dashboard agregado de análise de clientes
   */
  static async getDashboard(): Promise<unknown> {
    return customInstance.get('/api/v1/clients/ai/dashboard');
  }

  /**
   * Analisa saúde operacional do condomínio
   */
  static async analyzeCondominiumHealth(condominiumId: string): Promise<unknown> {
    return customInstance.get(`/api/v1/clients/condominiums/${condominiumId}/ai/health`);
  }
}

export default ClientsAIService;
