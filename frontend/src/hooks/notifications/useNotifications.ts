/**
 * useNotifications Hook
 *
 * Hook para gerenciamento de notificações com React Query
 */

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { notificationService } from '@/services/notifications';
import type {
  SendNotificationRequest,
  QueueItemResponse,
  QueueStatsResponse,
  SendNotificationResponse,
} from '@/types/generated/notifications';

// Query Keys
export const notificationKeys = {
  all: ['notifications'] as const,
  lists: () => [...notificationKeys.all, 'list'] as const,
  list: (filters: string) => [...notificationKeys.lists(), { filters }] as const,
  details: () => [...notificationKeys.all, 'detail'] as const,
  detail: (id: string) => [...notificationKeys.details(), id] as const,
  queue: () => [...notificationKeys.all, 'queue'] as const,
  queueStats: () => [...notificationKeys.all, 'queue-stats'] as const,
  history: (filters: string) => [...notificationKeys.all, 'history', { filters }] as const,
  logs: (id: string) => [...notificationKeys.all, 'logs', id] as const,
  channels: () => [...notificationKeys.all, 'channels'] as const,
};

/**
 * Hook para listar fila de notificações
 */
export function useNotificationQueue(params?: {
  queue_status?: string;
  channel_type?: string;
  user_id?: string;
  skip?: number;
  limit?: number;
}) {
  return useQuery({
    queryKey: notificationKeys.queue(),
    queryFn: () => notificationService.listQueue(params),
    staleTime: 30000, // 30 segundos
    refetchInterval: 60000, // Refetch a cada minuto
  });
}

/**
 * Hook para estatísticas da fila
 */
export function useQueueStats() {
  return useQuery({
    queryKey: notificationKeys.queueStats(),
    queryFn: () => notificationService.getQueueStats(),
    staleTime: 30000,
    refetchInterval: 30000, // Refetch a cada 30s
  });
}

/**
 * Hook para histórico de notificações
 */
export function useNotificationHistory(params?: {
  user_id?: string;
  channel_type?: string;
  history_status?: string;
  start_date?: string;
  end_date?: string;
  skip?: number;
  limit?: number;
}) {
  const filters = JSON.stringify(params);

  return useQuery({
    queryKey: notificationKeys.history(filters),
    queryFn: () => notificationService.getHistory(params),
    staleTime: 60000, // 1 minuto
  });
}

/**
 * Hook para logs de notificação
 */
export function useNotificationLogs(notificationId: string) {
  return useQuery({
    queryKey: notificationKeys.logs(notificationId),
    queryFn: () => notificationService.getLogs(notificationId),
    enabled: !!notificationId,
  });
}

/**
 * Hook para listar canais
 */
export function useNotificationChannels(params?: {
  channel_type?: string;
  active?: boolean;
  skip?: number;
  limit?: number;
}) {
  return useQuery({
    queryKey: notificationKeys.channels(),
    queryFn: () => notificationService.listChannels(params),
    staleTime: 300000, // 5 minutos
  });
}

/**
 * Hook para enviar notificação
 */
export function useSendNotification() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: SendNotificationRequest) => notificationService.send(data),
    onSuccess: () => {
      // Invalidar queries relevantes
      queryClient.invalidateQueries({ queryKey: notificationKeys.queue() });
      queryClient.invalidateQueries({ queryKey: notificationKeys.queueStats() });
    },
  });
}

/**
 * Hook para cancelar notificação
 */
export function useCancelNotification() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ notificationId, reason }: { notificationId: string; reason?: string }) =>
      notificationService.cancel(notificationId, reason),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: notificationKeys.queue() });
      queryClient.invalidateQueries({ queryKey: notificationKeys.queueStats() });
    },
  });
}

/**
 * Hook para processar fila
 */
export function useProcessQueue() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (params?: { batch_size?: number; channel_type?: string }) =>
      notificationService.processQueue(params),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: notificationKeys.queue() });
      queryClient.invalidateQueries({ queryKey: notificationKeys.queueStats() });
    },
  });
}

/**
 * Hook para tracking de abertura
 */
export function useTrackOpen() {
  return useMutation({
    mutationFn: (notificationId: string) => notificationService.trackOpen(notificationId),
  });
}

/**
 * Hook para tracking de clique
 */
export function useTrackClick() {
  return useMutation({
    mutationFn: ({ notificationId, url }: { notificationId: string; url: string }) =>
      notificationService.trackClick(notificationId, url),
  });
}
