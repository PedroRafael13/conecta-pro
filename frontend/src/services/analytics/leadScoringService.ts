/**
 * Lead Scoring Service
 *
 * Serviço para pontuação de leads com IA.
 */

import {
  scoreLeadApiV1AnalyticsLeadsScorePost,
  getTopLeadsApiV1AnalyticsLeadsTopGet,
  getScoringAnalyticsApiV1AnalyticsLeadsAnalyticsGet,
} from '@/api/generated/analytics/analytics-predictive/analytics-predictive';

import type {
  LeadScoreRequest,
  LeadScoreResponse,
} from '@/api/generated/analytics/conectaPROAnalyticsModule.schemas';

export const leadScoringService = {
  /**
   * Calcular score de lead
   */
  async scoreLead(lead: LeadScoreRequest): Promise<LeadScoreResponse> {
    const response = await scoreLeadApiV1AnalyticsLeadsScorePost(lead);
    return response.data;
  },

  /**
   * Top leads por score
   */
  async getTopLeads(limit = 50, minQuality = 'warm') {
    const response = await getTopLeadsApiV1AnalyticsLeadsTopGet({
      limit,
      min_quality: minQuality,
    });
    return response.data;
  },

  /**
   * Analytics de lead scoring
   */
  async getScoringAnalytics() {
    const response = await getScoringAnalyticsApiV1AnalyticsLeadsAnalyticsGet();
    return response.data;
  },
};
