/**
 * React Query Hooks - Push Notifications
 *
 * Hooks para gerenciar notificações push do usuário,
 * preferências e ações de leitura.
 *
 * @module hooks/mobile/usePushNotifications
 */

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  listNotifications,
  markAsRead,
  markAsDelivered,
  getNotificationPreferences,
  updateNotificationPreferences,
  sendBroadcastNotification,
  getNotificationStats,
  markMultipleAsRead,
} from '@/services/mobile/pushNotificationService';
import type {
  NotificationPreferencesUpdate,
  BroadcastNotificationRequest,
} from '@/types/generated/mobile/conectaPROMobileAPI.schemas';

/**
 * Hook para listar notificações.
 *
 * @param params - Parâmetros de paginação e filtro
 *
 * @example
 * ```tsx
 * const { data, isLoading } = useNotifications({
 *   page: 1,
 *   unread_only: true,
 * });
 *
 * console.log('Unread:', data?.unread_count);
 * ```
 */
export function useNotifications(params?: {
  page?: number;
  page_size?: number;
  unread_only?: boolean;
}) {
  return useQuery({
    queryKey: ['notifications', 'list', params],
    queryFn: () => listNotifications(params),
  });
}

/**
 * Hook para marcar notificação como lida.
 *
 * @example
 * ```tsx
 * const { mutate: markRead } = useMarkAsRead();
 *
 * markRead(notificationId);
 * ```
 */
export function useMarkAsRead() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: markAsRead,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['notifications'] });
    },
  });
}

/**
 * Hook para marcar notificação como entregue.
 *
 * @example
 * ```tsx
 * const { mutate: markDelivered } = useMarkAsDelivered();
 *
 * // Chamar ao receber push notification
 * markDelivered(notificationId);
 * ```
 */
export function useMarkAsDelivered() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: markAsDelivered,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['notifications'] });
    },
  });
}

/**
 * Hook para obter preferências de notificação.
 *
 * @example
 * ```tsx
 * const { data: preferences } = useNotificationPreferences();
 *
 * if (preferences?.push_enabled) {
 *   // Push habilitado
 * }
 * ```
 */
export function useNotificationPreferences() {
  return useQuery({
    queryKey: ['notifications', 'preferences'],
    queryFn: getNotificationPreferences,
  });
}

/**
 * Hook para atualizar preferências.
 *
 * @example
 * ```tsx
 * const { mutate: updatePrefs } = useUpdateNotificationPreferences();
 *
 * updatePrefs({
 *   push_enabled: true,
 *   sound_enabled: false,
 * });
 * ```
 */
export function useUpdateNotificationPreferences() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: updateNotificationPreferences,
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ['notifications', 'preferences'],
      });
    },
  });
}

/**
 * Hook para enviar broadcast (ADMIN).
 *
 * @example
 * ```tsx
 * const { mutate: broadcast } = useSendBroadcast();
 *
 * broadcast({
 *   title: 'Alerta Importante',
 *   body: 'Manutenção programada',
 *   target_all: true,
 * });
 * ```
 */
export function useSendBroadcast() {
  return useMutation({
    mutationFn: sendBroadcastNotification,
  });
}

/**
 * Hook para estatísticas de notificações (ADMIN).
 *
 * @param days - Número de dias
 *
 * @example
 * ```tsx
 * const { data: stats } = useNotificationStats(30);
 *
 * console.log('Delivery rate:', stats?.delivery_rate);
 * ```
 */
export function useNotificationStats(days: number = 30) {
  return useQuery({
    queryKey: ['notifications', 'stats', days],
    queryFn: () => getNotificationStats(days),
  });
}

/**
 * Hook para marcar múltiplas notificações como lidas.
 *
 * @example
 * ```tsx
 * const { mutate: markAllRead } = useMarkMultipleAsRead();
 *
 * markAllRead([id1, id2, id3]);
 * ```
 */
export function useMarkMultipleAsRead() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: markMultipleAsRead,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['notifications'] });
    },
  });
}

/**
 * Hook helper para contador de não lidas.
 *
 * @example
 * ```tsx
 * const unreadCount = useUnreadCount();
 *
 * return <Badge>{unreadCount}</Badge>;
 * ```
 */
export function useUnreadCount() {
  const { data } = useNotifications({ unread_only: true, page_size: 1 });
  return data?.unread_count || 0;
}
