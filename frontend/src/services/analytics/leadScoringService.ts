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
    return scoreLeadApiV1AnalyticsLeadsScorePost(lead) as Promise<LeadScoreResponse>;
  },

  /**
   * Top leads por score
   */
  async getTopLeads(limit = 50, minQuality = 'warm') {
    return getTopLeadsApiV1AnalyticsLeadsTopGet({
      limit,
      min_quality: minQuality,
    }) as Promise<unknown>;
  },

  /**
   * Analytics de lead scoring
   */
  async getScoringAnalytics() {
    return getScoringAnalyticsApiV1AnalyticsLeadsAnalyticsGet() as Promise<unknown>;
  },
};
