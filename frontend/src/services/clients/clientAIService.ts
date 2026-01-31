/**
 * Service Layer - Client AI Services
 * Serviços de IA para Análise de Clientes
 */

import { axiosInstance } from '@/lib/axios-instance';

const BASE_URL = '/api/v1/clients';

interface AIProfileAnalysis {
  client_id: string;
  profile_score: number;
  strengths: string[];
  weaknesses: string[];
  recommendations: string[];
}

interface AISegmentation {
  client_id: string;
  suggested_segment: string;
  confidence: number;
  factors: string[];
}

interface AIChurnRisk {
  client_id: string;
  churn_probability: number;
  risk_level: 'low' | 'medium' | 'high';
  risk_factors: string[];
  retention_actions: string[];
}

interface AIServiceRecommendation {
  service_name: string;
  relevance_score: number;
  justification: string;
  estimated_value: number;
}

interface AICondominiumHealth {
  condominium_id: string;
  health_score: number;
  status: 'healthy' | 'attention' | 'critical';
  metrics: {
    occupation_rate: number;
    payment_regularity: number;
    incident_rate: number;
  };
  recommendations: string[];
}

interface AIDashboardInsights {
  total_clients: number;
  high_value_clients: number;
  at_risk_clients: number;
  growth_opportunities: number;
  top_insights: Array<{
    type: string;
    message: string;
    priority: 'low' | 'medium' | 'high';
  }>;
}

/**
 * Service de IA para Clientes
 */
export const clientAIService = {
  /**
   * Analisa perfil do cliente com IA
   */
  analyzeProfile: async (clientId: string): Promise<AIProfileAnalysis> => {
    const response = await axiosInstance.get<AIProfileAnalysis>(
      `${BASE_URL}/${clientId}/ai/profile`
    );
    return response.data;
  },

  /**
   * Sugere segmentação para cliente
   */
  suggestSegmentation: async (clientId: string): Promise<AISegmentation> => {
    const response = await axiosInstance.get<AISegmentation>(
      `${BASE_URL}/${clientId}/ai/segmentation`
    );
    return response.data;
  },

  /**
   * Prediz risco de churn
   */
  predictChurnRisk: async (clientId: string): Promise<AIChurnRisk> => {
    const response = await axiosInstance.get<AIChurnRisk>(
      `${BASE_URL}/${clientId}/ai/churn-risk`
    );
    return response.data;
  },

  /**
   * Recomenda serviços para cliente
   */
  recommendServices: async (
    clientId: string
  ): Promise<AIServiceRecommendation[]> => {
    const response = await axiosInstance.get<AIServiceRecommendation[]>(
      `${BASE_URL}/${clientId}/ai/recommendations`
    );
    return response.data;
  },

  /**
   * Analisa saúde do condomínio
   */
  analyzeCondominiumHealth: async (
    condominiumId: string
  ): Promise<AICondominiumHealth> => {
    const response = await axiosInstance.get<AICondominiumHealth>(
      `${BASE_URL}/condominiums/${condominiumId}/ai/health`
    );
    return response.data;
  },

  /**
   * Obtém insights para dashboard
   */
  getDashboardInsights: async (): Promise<AIDashboardInsights> => {
    const response = await axiosInstance.get<AIDashboardInsights>(
      `${BASE_URL}/ai/dashboard`
    );
    return response.data;
  },
};
