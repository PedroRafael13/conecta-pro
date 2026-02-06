/**
 * Push Notification Service
 *
 * Service layer para push notifications mobile
 * Cobre: dispositivos, envio, campanhas, topics, analytics
 */

import { api } from '@/lib/api';
import type {
  DeviceRegisterRequest,
  SendPushRequest,
  TopicSubscribeRequest,
  TopicUnsubscribeRequest,
  CampaignAnalyticsResponse,
  CampaignListResponse,
  CampaignResponse,
  DeviceListResponse,
  DeviceResponse,
  MetricsSummaryResponse,
  NotificationResponse,
  SendPushResponse,
  TopicResponse,
} from '@/types/generated/notifications';

export class PushService {
  private readonly basePath = '/api/v1/notifications/push';

  // ========== Devices ==========

  /**
   * Registra dispositivo para push notifications
   */
  async registerDevice(data: DeviceRegisterRequest): Promise<DeviceResponse> {
    return await api.post(`${this.basePath}/devices/register`, data);
  }

  /**
   * Lista dispositivos do usuário
   */
  async listDevices(params?: {
    platform?: string;
    active_only?: boolean;
    page?: number;
    page_size?: number;
  }): Promise<DeviceListResponse> {
    return await api.get(`${this.basePath}/devices`, { params });
  }

  /**
   * Obtém detalhes de um dispositivo
   */
  async getDevice(deviceId: string): Promise<DeviceResponse> {
    return await api.get(`${this.basePath}/devices/${deviceId}`);
  }

  /**
   * Atualiza dispositivo
   */
  async updateDevice(
    deviceId: string,
    data: Partial<DeviceRegisterRequest>
  ): Promise<DeviceResponse> {
    return await api.patch(
      `${this.basePath}/devices/${deviceId}`,
      data
    );
  }

  /**
   * Remove registro do dispositivo
   */
  async unregisterDevice(deviceId: string): Promise<void> {
    await api.delete(`${this.basePath}/devices/${deviceId}`);
  }

  // ========== Topics ==========

  /**
   * Inscreve dispositivos em tópico
   */
  async subscribeToTopic(data: TopicSubscribeRequest): Promise<TopicResponse> {
    return await api.post(`${this.basePath}/topics/subscribe`, data);
  }

  /**
   * Remove inscrição de tópico
   */
  async unsubscribeFromTopic(
    data: TopicUnsubscribeRequest
  ): Promise<TopicResponse> {
    return await api.post(
      `${this.basePath}/topics/unsubscribe`,
      data
    );
  }

  /**
   * Lista tópicos disponíveis
   */
  async listTopics(): Promise<TopicResponse[]> {
    return await api.get(`${this.basePath}/topics`);
  }

  // ========== Notifications ==========

  /**
   * Envia push notification
   */
  async send(data: SendPushRequest): Promise<SendPushResponse> {
    return await api.post(`${this.basePath}/send`, data);
  }

  /**
   * Lista notificações
   */
  async listNotifications(params?: {
    user_id?: string;
    device_id?: string;
    status_filter?: string;
    page?: number;
    page_size?: number;
  }): Promise<NotificationResponse[]> {
    return await api.get(`${this.basePath}/notifications`, {
      params,
    });
  }

  /**
   * Marca notificação como aberta
   */
  async markAsOpened(notificationId: string): Promise<void> {
    await api.post(
      `${this.basePath}/notifications/${notificationId}/opened`
    );
  }

  /**
   * Marca notificação como clicada
   */
  async markAsClicked(
    notificationId: string,
    actionId?: string
  ): Promise<void> {
    await api.post(
      `${this.basePath}/notifications/${notificationId}/clicked`,
      null,
      { params: { action_id: actionId } }
    );
  }

  // ========== Campaigns ==========

  /**
   * Lista campanhas
   */
  async listCampaigns(params?: {
    status_filter?: string;
    campaign_type?: string;
    page?: number;
    page_size?: number;
  }): Promise<CampaignListResponse> {
    return await api.get(`${this.basePath}/campaigns`, { params });
  }

  /**
   * Obtém detalhes de uma campanha
   */
  async getCampaign(campaignId: string): Promise<CampaignResponse> {
    return await api.get(`${this.basePath}/campaigns/${campaignId}`);
  }

  /**
   * Envia campanha
   */
  async sendCampaign(campaignId: string): Promise<SendPushResponse> {
    return await api.post(
      `${this.basePath}/campaigns/${campaignId}/send`
    );
  }

  /**
   * Obtém analytics de uma campanha
   */
  async getCampaignAnalytics(
    campaignId: string
  ): Promise<CampaignAnalyticsResponse> {
    return await api.get(
      `${this.basePath}/campaigns/${campaignId}/analytics`
    );
  }

  /**
   * Exclui campanha
   */
  async deleteCampaign(campaignId: string): Promise<void> {
    await api.delete(`${this.basePath}/campaigns/${campaignId}`);
  }

  // ========== Analytics ==========

  /**
   * Obtém resumo de métricas
   */
  async getMetricsSummary(params?: {
    period?: string;
    start_date?: string;
    end_date?: string;
    platform?: string;
  }): Promise<MetricsSummaryResponse> {
    return await api.get(`${this.basePath}/analytics/summary`, {
      params,
    });
  }

  /**
   * Obtém estatísticas de dispositivos
   */
  async getDeviceStats(): Promise<{
    total: number;
    active: number;
    inactive: number;
    notifications_enabled: number;
    by_platform: Record<string, number>;
    by_status: Record<string, number>;
  }> {
    return await api.get(`${this.basePath}/analytics/devices`);
  }

  // ========== Helpers ==========

  /**
   * Verifica se dispositivo está registrado
   */
  async isDeviceRegistered(deviceId: string): Promise<boolean> {
    try {
      await this.getDevice(deviceId);
      return true;
    } catch {
      return false;
    }
  }

  /**
   * Envia notificação para usuário específico
   */
  async sendToUser(
    userId: string,
    title: string,
    body: string,
    data?: Record<string, unknown>
  ): Promise<SendPushResponse> {
    return this.send({
      title,
      body,
      user_ids: [userId],
      data_payload: data,
      priority: 'normal',
    });
  }

  /**
   * Envia notificação para tópico
   */
  async sendToTopic(
    topic: string,
    title: string,
    body: string,
    data?: Record<string, unknown>
  ): Promise<SendPushResponse> {
    return this.send({
      title,
      body,
      topics: [topic],
      data_payload: data,
      priority: 'normal',
    });
  }
}

export const pushService = new PushService();
