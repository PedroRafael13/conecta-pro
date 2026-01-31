/**
 * Notification Service
 *
 * Service layer para gerenciamento de notificações multi-canal
 * Cobre: envio, cancelamento, tracking, webhooks
 */

import { api } from '@/lib/api';
import type {
  SendNotificationRequest,
  ChannelConfigResponse,
  LogEntryResponse,
  QueueItemResponse,
  QueueStatsResponse,
  SendNotificationResponse,
} from '@/types/generated/notifications';

export class NotificationService {
  private readonly basePath = '/api/v1/notifications';

  /**
   * Envia notificação para destinatários
   */
  async send(request: SendNotificationRequest): Promise<SendNotificationResponse> {
    return await api.post(`${this.basePath}/send`, request);
  }

  /**
   * Cancela notificação pendente ou agendada
   */
  async cancel(notificationId: string, reason?: string): Promise<void> {
    await api.post(`${this.basePath}/send/${notificationId}/cancel`, null, {
      params: { reason },
    });
  }

  /**
   * Lista canais de notificação configurados
   */
  async listChannels(params?: {
    channel_type?: string;
    active?: boolean;
    skip?: number;
    limit?: number;
  }): Promise<ChannelConfigResponse[]> {
    return await api.get(`${this.basePath}/channels`, { params });
  }

  /**
   * Obtém detalhes de um canal
   */
  async getChannel(channelId: string): Promise<ChannelConfigResponse> {
    return await api.get(`${this.basePath}/channels/${channelId}`);
  }

  /**
   * Lista itens da fila de notificações
   */
  async listQueue(params?: {
    queue_status?: string;
    channel_type?: string;
    user_id?: string;
    skip?: number;
    limit?: number;
  }): Promise<QueueItemResponse[]> {
    return await api.get(`${this.basePath}/queue`, { params });
  }

  /**
   * Obtém estatísticas da fila
   */
  async getQueueStats(): Promise<QueueStatsResponse> {
    return await api.get(`${this.basePath}/queue/stats`);
  }

  /**
   * Processa itens pendentes da fila
   */
  async processQueue(params?: {
    batch_size?: number;
    channel_type?: string;
  }): Promise<{
    success: boolean;
    processed: number;
    success_count: number;
    failed_count: number;
    retry_count: number;
  }> {
    return await api.post(`${this.basePath}/queue/process`, null, {
      params,
    });
  }

  /**
   * Obtém histórico de notificações enviadas
   */
  async getHistory(params?: {
    user_id?: string;
    channel_type?: string;
    history_status?: string;
    start_date?: string;
    end_date?: string;
    skip?: number;
    limit?: number;
  }): Promise<QueueItemResponse[]> {
    return await api.get(`${this.basePath}/history`, { params });
  }

  /**
   * Obtém logs de uma notificação específica
   */
  async getLogs(notificationId: string): Promise<LogEntryResponse[]> {
    return await api.get(`${this.basePath}/logs/${notificationId}`);
  }

  /**
   * Tracking de abertura (pixel)
   */
  async trackOpen(notificationId: string): Promise<void> {
    await api.get(`${this.basePath}/track/open/${notificationId}`);
  }

  /**
   * Tracking de clique
   */
  async trackClick(notificationId: string, url: string): Promise<void> {
    await api.get(`${this.basePath}/track/click/${notificationId}`, {
      params: { url },
    });
  }
}

export const notificationService = new NotificationService();
