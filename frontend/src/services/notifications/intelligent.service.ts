/**
 * Intelligent Notification Service
 *
 * Service layer para notificações inteligentes com IA
 * Cobre: personalização, timing, canal, A/B testing, analytics, LGPD
 */

import { api } from '@/lib/api';
import type {
  AnalyticsDashboardResponse,
  BehaviorAnalysisResponse,
  ChannelResponse,
  ConsentResponse,
  DataRequestResponse,
  ExperimentResponse,
  ExperimentResultResponse,
  PersonalizeResponse,
  TimingResponse,
} from '@/types/generated/notifications';

export class IntelligentNotificationService {
  private readonly basePath = '/api/v1/notifications/intelligent';

  // ========== Personalização ==========

  /**
   * Personaliza notificação com IA
   */
  async personalize(data: {
    user_id: number;
    notification_type: string;
    template_title: string;
    template_body: string;
    context?: Record<string, unknown>;
    tone?: string;
  }): Promise<PersonalizeResponse> {
    return await api.post(`${this.basePath}/personalize`, data);
  }

  /**
   * Otimiza horário de envio
   */
  async optimizeTiming(data: {
    user_id: number;
    notification_type: string;
    earliest_time?: string;
    deadline?: string;
  }): Promise<TimingResponse> {
    return await api.post(`${this.basePath}/timing/optimize`, data);
  }

  /**
   * Seleciona melhor canal
   */
  async selectChannel(data: {
    user_id: number;
    notification_type: string;
    content?: Record<string, unknown>;
  }): Promise<ChannelResponse> {
    return await api.post(`${this.basePath}/channel/select`, data);
  }

  // ========== Análise Comportamental ==========

  /**
   * Obtém análise comportamental do usuário
   */
  async getUserBehavior(userId: number): Promise<BehaviorAnalysisResponse> {
    return await api.get(`${this.basePath}/behavior/${userId}`);
  }

  /**
   * Obtém insights comportamentais
   */
  async getBehaviorInsights(userId: number): Promise<
    Array<{
      type: string;
      description: string;
      confidence: number;
      recommendation: string;
    }>
  > {
    return await api.get(
      `${this.basePath}/behavior/${userId}/insights`
    );
  }

  /**
   * Prediz engajamento do usuário
   */
  async predictEngagement(
    userId: number,
    notificationType: string
  ): Promise<{
    will_open: boolean;
    open_probability: number;
    will_click: boolean;
    click_probability: number;
    best_time_to_send: string;
    reasoning: string;
  }> {
    return await api.get(
      `${this.basePath}/behavior/${userId}/engagement-prediction`,
      {
        params: { notification_type: notificationType },
      }
    );
  }

  // ========== A/B Testing ==========

  /**
   * Cria novo experimento A/B
   */
  async createExperiment(data: {
    name: string;
    description: string;
    variants: Array<Record<string, unknown>>;
    primary_metric?: string;
    target_sample_size?: number;
    min_confidence?: number;
  }): Promise<ExperimentResponse> {
    return await api.post(`${this.basePath}/experiments`, data);
  }

  /**
   * Inicia experimento
   */
  async startExperiment(experimentId: string): Promise<ExperimentResponse> {
    return await api.post(
      `${this.basePath}/experiments/${experimentId}/start`
    );
  }

  /**
   * Obtém resultados do experimento
   */
  async getExperimentResults(
    experimentId: string
  ): Promise<ExperimentResultResponse> {
    return await api.get(
      `${this.basePath}/experiments/${experimentId}/results`
    );
  }

  /**
   * Aloca usuário a uma variante
   */
  async allocateUserToVariant(
    experimentId: string,
    userId: number
  ): Promise<{
    experiment_id: string;
    user_id: number;
    variant_id: string;
    variant_name: string;
    config: Record<string, unknown>;
  }> {
    return await api.get(
      `${this.basePath}/experiments/${experimentId}/allocate/${userId}`
    );
  }

  /**
   * Registra evento do experimento
   */
  async recordExperimentEvent(
    experimentId: string,
    variantId: string,
    eventType: string,
    userId: number
  ): Promise<void> {
    await api.post(`${this.basePath}/experiments/${experimentId}/event`, null, {
      params: {
        variant_id: variantId,
        event_type: eventType,
        user_id: userId,
      },
    });
  }

  // ========== Analytics ==========

  /**
   * Obtém dashboard de analytics
   */
  async getAnalyticsDashboard(): Promise<AnalyticsDashboardResponse> {
    return await api.get(`${this.basePath}/analytics/dashboard`);
  }

  /**
   * Obtém analytics por canal
   */
  async getChannelAnalytics(days: number = 30): Promise<
    Array<{
      channel: string;
      total_sent: number;
      delivery_rate: number;
      open_rate: number;
      click_rate: number;
      trend: string;
    }>
  > {
    return await api.get(`${this.basePath}/analytics/channels`, {
      params: { days },
    });
  }

  /**
   * Obtém analytics de um usuário
   */
  async getUserAnalytics(
    userId: number
  ): Promise<Record<string, unknown>> {
    return await api.get(
      `${this.basePath}/analytics/user/${userId}`
    );
  }

  /**
   * Gera relatório de métricas
   */
  async generateReport(
    startDate: string,
    endDate: string
  ): Promise<{
    period: string;
    total_notifications: number;
    total_users: number;
    insights: string[];
    recommendations: string[];
  }> {
    return await api.get(`${this.basePath}/analytics/report`, {
      params: { start_date: startDate, end_date: endDate },
    });
  }

  // ========== LGPD Compliance ==========

  /**
   * Registra consentimento
   */
  async recordConsent(data: {
    consent_type: string;
    granted: boolean;
    consent_text: string;
    version: string;
  }): Promise<ConsentResponse> {
    return await api.post(`${this.basePath}/consent`, data);
  }

  /**
   * Retira consentimento
   */
  async withdrawConsent(consentType: string): Promise<void> {
    await api.delete(`${this.basePath}/consent/${consentType}`);
  }

  /**
   * Obtém consentimentos do usuário
   */
  async getUserConsents(): Promise<
    Array<{
      id: string;
      type: string;
      status: string;
      granted_at: string | null;
      expires_at: string | null;
    }>
  > {
    return await api.get(`${this.basePath}/consent`);
  }

  /**
   * Cria solicitação de dados LGPD
   */
  async createDataRequest(data: {
    request_type: string;
    requester_email: string;
  }): Promise<DataRequestResponse> {
    return await api.post(`${this.basePath}/data-request`, data);
  }

  /**
   * Verifica solicitação de dados
   */
  async verifyDataRequest(
    requestId: string,
    token: string
  ): Promise<{ verified: boolean }> {
    return await api.post(
      `${this.basePath}/data-request/${requestId}/verify`,
      null,
      { params: { token } }
    );
  }

  /**
   * Obtém logs de auditoria
   */
  async getAuditLogs(
    userId?: number,
    limit: number = 100
  ): Promise<
    Array<{
      id: string;
      timestamp: string;
      action: string;
      user_id: number | null;
      resource_type: string;
      reason: string;
    }>
  > {
    return await api.get(`${this.basePath}/compliance/audit-logs`, {
      params: { user_id: userId, limit },
    });
  }

  // ========== Utility ==========

  /**
   * Health check do módulo
   */
  async healthCheck(): Promise<{
    status: string;
    module: string;
    version: string;
  }> {
    return await api.get(`${this.basePath}/health`);
  }

  /**
   * Verifica se pode enviar notificação para usuário
   */
  async canSendNotification(
    userId: number,
    notificationType: string
  ): Promise<{
    can_send: boolean;
    reason: string;
    compliance_check?: string;
  }> {
    return await api.get(`${this.basePath}/can-send/${userId}`, {
      params: { notification_type: notificationType },
    });
  }
}

export const intelligentNotificationService =
  new IntelligentNotificationService();
