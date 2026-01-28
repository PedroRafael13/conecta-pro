/**
 * Churn Prediction Service
 *
 * Serviço para predição de churn de usuários com IA.
 */

import {
  predictChurnApiV1AnalyticsChurnPredictPost,
  getHighRiskUsersApiV1AnalyticsChurnHighRiskGet,
  getChurnAnalyticsApiV1AnalyticsChurnAnalyticsGet,
} from '@/api/generated/analytics/analytics-predictive/analytics-predictive';

import type {
  ChurnPredictionRequest,
  ChurnPredictionResponse,
} from '@/api/generated/analytics/conectaPROAnalyticsModule.schemas';

export const churnPredictionService = {
  /**
   * Predizer churn de usuário
   */
  async predictChurn(userId: number): Promise<ChurnPredictionResponse> {
    const response = await predictChurnApiV1AnalyticsChurnPredictPost({
      user_id: userId,
    });
    return response.data;
  },

  /**
   * Listar usuários com alto risco de churn
   */
  async getHighRiskUsers(limit = 50, minRisk = 'high') {
    const response = await getHighRiskUsersApiV1AnalyticsChurnHighRiskGet({
      limit,
      min_risk: minRisk,
    });
    return response.data;
  },

  /**
   * Analytics de churn
   */
  async getChurnAnalytics() {
    const response = await getChurnAnalyticsApiV1AnalyticsChurnAnalyticsGet();
    return response.data;
  },
};
