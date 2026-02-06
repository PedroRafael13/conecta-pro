/**
 * Preference Service
 *
 * Service layer para gerenciamento de preferências de notificação
 * Cobre: preferências do usuário, unsubscribe, categorias
 */

import { api } from '@/lib/api';
import type {
  PreferenceUpdate,
  PreferenceResponse,
} from '@/types/generated/notifications/conectaPRONotificationsModule.schemas';

/**
 * Canais de notificação suportados
 */
export type NotificationChannel = 'email' | 'whatsapp' | 'sms' | 'push' | 'in_app';

/**
 * Mapeamento de canal para campo de preferência
 */
const channelFieldMap: Record<NotificationChannel, keyof PreferenceUpdate> = {
  email: 'email_enabled',
  whatsapp: 'whatsapp_enabled',
  sms: 'sms_enabled',
  push: 'push_enabled',
  in_app: 'in_app_enabled',
};

/**
 * Verifica se uma string é um canal válido
 */
function isValidChannel(channel: string): channel is NotificationChannel {
  return channel in channelFieldMap;
}

export class PreferenceService {
  private readonly basePath = '/api/v1/notifications/preferences';

  /**
   * Obtém preferências do usuário atual
   */
  async getMyPreferences(): Promise<PreferenceResponse> {
    const response = await api.get<PreferenceResponse>(`${this.basePath}/me`);
    return response.data;
  }

  /**
   * Atualiza preferências do usuário atual
   */
  async updateMyPreferences(
    data: PreferenceUpdate
  ): Promise<PreferenceResponse> {
    const response = await api.patch<PreferenceResponse>(`${this.basePath}/me`, data);
    return response.data;
  }

  /**
   * Processa unsubscribe via link
   */
  async unsubscribe(token: string): Promise<void> {
    await api.post(`${this.basePath}/unsubscribe`, null, {
      params: { token },
    });
  }

  /**
   * Habilita canal específico
   */
  async enableChannel(channel: string): Promise<PreferenceResponse> {
    if (!isValidChannel(channel)) {
      throw new Error(`Canal desconhecido: ${channel}`);
    }

    const fieldName = channelFieldMap[channel];
    return this.updateMyPreferences({
      [fieldName]: true,
    } as PreferenceUpdate);
  }

  /**
   * Desabilita canal específico
   */
  async disableChannel(channel: string): Promise<PreferenceResponse> {
    if (!isValidChannel(channel)) {
      throw new Error(`Canal desconhecido: ${channel}`);
    }

    const fieldName = channelFieldMap[channel];
    return this.updateMyPreferences({
      [fieldName]: false,
    } as PreferenceUpdate);
  }

  /**
   * Habilita/desabilita preferências de categoria
   */
  async setCategoryPreference(
    category: string,
    enabled: boolean,
    channels?: string[]
  ): Promise<PreferenceResponse> {
    return this.updateMyPreferences({
      category_preferences: {
        [category]: {
          enabled,
          channels,
        },
      },
    });
  }

  /**
   * Habilita categoria específica
   */
  async enableCategory(category: string): Promise<PreferenceResponse> {
    return this.setCategoryPreference(category, true);
  }

  /**
   * Desabilita categoria específica
   */
  async disableCategory(category: string): Promise<PreferenceResponse> {
    return this.setCategoryPreference(category, false);
  }

  /**
   * Define horário de não perturbe
   */
  async setQuietHours(
    start: string,
    end: string
  ): Promise<PreferenceResponse> {
    return this.updateMyPreferences({
      quiet_hours_enabled: true,
      quiet_hours_start: start,
      quiet_hours_end: end,
    });
  }

  /**
   * Remove horário de não perturbe
   */
  async clearQuietHours(): Promise<PreferenceResponse> {
    return this.updateMyPreferences({
      quiet_hours_enabled: false,
      quiet_hours_start: null,
      quiet_hours_end: null,
    });
  }
}

export const preferenceService = new PreferenceService();
