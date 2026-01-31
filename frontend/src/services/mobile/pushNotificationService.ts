/**
 * Service Layer - Push Notifications
 *
 * Gerencia notificações push do usuário e preferências.
 * Suporta Android (FCM) e iOS (APNs).
 *
 * Features:
 * - Listagem de notificações com paginação
 * - Marcar como lida/entregue
 * - Preferências de notificação
 * - Filtros e ordenação
 * - Broadcast notifications (admin)
 *
 * @module services/mobile/pushNotificationService
 */

import { api } from '@/lib/api';
import type {
  NotificationListResponse,
  NotificationPreferences,
  NotificationPreferencesUpdate,
  BroadcastNotificationRequest,
  BroadcastNotificationResponse,
} from '@/types/generated/mobile/conectaPROMobileAPI.schemas';

const BASE_URL = '/api/v1/mobile';

/**
 * Lista notificações do usuário.
 *
 * Suporta paginação e filtro de não lidas.
 *
 * @param params - Parâmetros de paginação e filtro
 * @returns Lista de notificações com metadados
 */
export async function listNotifications(params?: {
  page?: number;
  page_size?: number;
  unread_only?: boolean;
}): Promise<NotificationListResponse> {
  const response = await api.get<NotificationListResponse>(
    `${BASE_URL}/notifications`,
    { params }
  );
  return response.data;
}

/**
 * Marca notificação como lida.
 *
 * @param notificationId - ID da notificação
 * @returns Confirmação
 */
export async function markAsRead(notificationId: string): Promise<{
  message: string;
}> {
  const response = await api.post(
    `${BASE_URL}/notifications/${notificationId}/read`
  );
  return response.data;
}

/**
 * Marca notificação como entregue (callback do dispositivo).
 *
 * @param notificationId - ID da notificação
 * @returns Confirmação
 */
export async function markAsDelivered(notificationId: string): Promise<{
  message: string;
}> {
  const response = await api.post(
    `${BASE_URL}/notifications/${notificationId}/delivered`
  );
  return response.data;
}

/**
 * Obtém preferências de notificação do usuário.
 *
 * @returns Preferências atuais
 */
export async function getNotificationPreferences(): Promise<NotificationPreferences> {
  const response = await api.get<NotificationPreferences>(
    `${BASE_URL}/notifications/preferences`
  );
  return response.data;
}

/**
 * Atualiza preferências de notificação.
 *
 * @param preferences - Novas preferências (parcial)
 * @returns Preferências atualizadas
 */
export async function updateNotificationPreferences(
  preferences: NotificationPreferencesUpdate
): Promise<NotificationPreferences> {
  const response = await api.put<NotificationPreferences>(
    `${BASE_URL}/notifications/preferences`,
    preferences
  );
  return response.data;
}

/**
 * Envia notificação em broadcast (ADMIN).
 *
 * Requer permissão de administrador.
 *
 * @param request - Dados da notificação broadcast
 * @returns Resultado do envio
 */
export async function sendBroadcastNotification(
  request: BroadcastNotificationRequest
): Promise<BroadcastNotificationResponse> {
  const response = await api.post<BroadcastNotificationResponse>(
    `${BASE_URL}/admin/notifications/broadcast`,
    request
  );
  return response.data;
}

/**
 * Obtém estatísticas de notificações (ADMIN).
 *
 * @param days - Número de dias (padrão: 30)
 * @returns Estatísticas
 */
export async function getNotificationStats(days: number = 30): Promise<{
  total_sent: number;
  total_delivered: number;
  total_read: number;
  delivery_rate: number;
  read_rate: number;
  by_type: Record<string, number>;
  by_platform: Record<string, number>;
}> {
  const response = await api.get(
    `${BASE_URL}/admin/notifications/stats`,
    { params: { days } }
  );
  return response.data;
}

/**
 * Helper: Marca múltiplas notificações como lidas.
 *
 * @param notificationIds - Array de IDs
 * @returns Resultados individuais
 */
export async function markMultipleAsRead(
  notificationIds: string[]
): Promise<Array<{ id: string; success: boolean; error?: string }>> {
  const results = await Promise.allSettled(
    notificationIds.map((id) => markAsRead(id))
  );

  return results.map((result, index) => ({
    id: notificationIds[index],
    success: result.status === 'fulfilled',
    error: result.status === 'rejected' ? result.reason.message : undefined,
  }));
}

/**
 * Helper: Verifica se notificações push estão habilitadas.
 *
 * @returns true se push está habilitado
 */
export async function isPushEnabled(): Promise<boolean> {
  try {
    const prefs = await getNotificationPreferences();
    return prefs.push_enabled || false;
  } catch {
    return false;
  }
}
