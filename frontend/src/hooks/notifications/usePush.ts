/**
 * usePush Hook
 *
 * Hook para gerenciamento de push notifications
 */

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { pushService } from '@/services/notifications';
import type {
  DeviceRegisterRequest,
  SendPushRequest,
  TopicSubscribeRequest,
  TopicUnsubscribeRequest,
} from '@/types/generated/notifications';

// Query Keys
export const pushKeys = {
  all: ['push-notifications'] as const,
  devices: () => [...pushKeys.all, 'devices'] as const,
  device: (id: string) => [...pushKeys.devices(), id] as const,
  topics: () => [...pushKeys.all, 'topics'] as const,
  notifications: (filters: string) => [...pushKeys.all, 'notifications', { filters }] as const,
  campaigns: (filters: string) => [...pushKeys.all, 'campaigns', { filters }] as const,
  campaign: (id: string) => [...pushKeys.all, 'campaign', id] as const,
  campaignAnalytics: (id: string) => [...pushKeys.all, 'campaign-analytics', id] as const,
  metricsSummary: (filters: string) => [...pushKeys.all, 'metrics', { filters }] as const,
  deviceStats: () => [...pushKeys.all, 'device-stats'] as const,
};

// ========== Devices ==========

/**
 * Hook para listar dispositivos
 */
export function useDevices(params?: {
  platform?: string;
  active_only?: boolean;
  page?: number;
  page_size?: number;
}) {
  return useQuery({
    queryKey: pushKeys.devices(),
    queryFn: () => pushService.listDevices(params),
    staleTime: 60000, // 1 minuto
  });
}

/**
 * Hook para obter dispositivo específico
 */
export function useDevice(deviceId: string) {
  return useQuery({
    queryKey: pushKeys.device(deviceId),
    queryFn: () => pushService.getDevice(deviceId),
    enabled: !!deviceId,
  });
}

/**
 * Hook para registrar dispositivo
 */
export function useRegisterDevice() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: DeviceRegisterRequest) => pushService.registerDevice(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: pushKeys.devices() });
    },
  });
}

/**
 * Hook para atualizar dispositivo
 */
export function useUpdateDevice() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ deviceId, data }: { deviceId: string; data: Partial<DeviceRegisterRequest> }) =>
      pushService.updateDevice(deviceId, data),
    onSuccess: (_, { deviceId }) => {
      queryClient.invalidateQueries({ queryKey: pushKeys.device(deviceId) });
      queryClient.invalidateQueries({ queryKey: pushKeys.devices() });
    },
  });
}

/**
 * Hook para remover dispositivo
 */
export function useUnregisterDevice() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (deviceId: string) => pushService.unregisterDevice(deviceId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: pushKeys.devices() });
    },
  });
}

// ========== Topics ==========

/**
 * Hook para listar tópicos
 */
export function useTopics() {
  return useQuery({
    queryKey: pushKeys.topics(),
    queryFn: () => pushService.listTopics(),
    staleTime: 300000, // 5 minutos
  });
}

/**
 * Hook para inscrever em tópico
 */
export function useSubscribeToTopic() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: TopicSubscribeRequest) => pushService.subscribeToTopic(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: pushKeys.topics() });
      queryClient.invalidateQueries({ queryKey: pushKeys.devices() });
    },
  });
}

/**
 * Hook para desinscrever de tópico
 */
export function useUnsubscribeFromTopic() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: TopicUnsubscribeRequest) => pushService.unsubscribeFromTopic(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: pushKeys.topics() });
      queryClient.invalidateQueries({ queryKey: pushKeys.devices() });
    },
  });
}

// ========== Notifications ==========

/**
 * Hook para listar notificações
 */
export function usePushNotifications(params?: {
  user_id?: string;
  device_id?: string;
  status_filter?: string;
  page?: number;
  page_size?: number;
}) {
  const filters = JSON.stringify(params);

  return useQuery({
    queryKey: pushKeys.notifications(filters),
    queryFn: () => pushService.listNotifications(params),
    staleTime: 30000, // 30 segundos
  });
}

/**
 * Hook para enviar push notification
 */
export function useSendPush() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: SendPushRequest) => pushService.send(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: pushKeys.all });
    },
  });
}

/**
 * Hook para marcar como aberta
 */
export function useMarkAsOpened() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (notificationId: string) => pushService.markAsOpened(notificationId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: pushKeys.all });
    },
  });
}

/**
 * Hook para marcar como clicada
 */
export function useMarkAsClicked() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ notificationId, actionId }: { notificationId: string; actionId?: string }) =>
      pushService.markAsClicked(notificationId, actionId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: pushKeys.all });
    },
  });
}

// ========== Campaigns ==========

/**
 * Hook para listar campanhas
 */
export function useCampaigns(params?: {
  status_filter?: string;
  campaign_type?: string;
  page?: number;
  page_size?: number;
}) {
  const filters = JSON.stringify(params);

  return useQuery({
    queryKey: pushKeys.campaigns(filters),
    queryFn: () => pushService.listCampaigns(params),
    staleTime: 60000, // 1 minuto
  });
}

/**
 * Hook para obter campanha
 */
export function useCampaign(campaignId: string) {
  return useQuery({
    queryKey: pushKeys.campaign(campaignId),
    queryFn: () => pushService.getCampaign(campaignId),
    enabled: !!campaignId,
  });
}

/**
 * Hook para enviar campanha
 */
export function useSendCampaign() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (campaignId: string) => pushService.sendCampaign(campaignId),
    onSuccess: (_, campaignId) => {
      queryClient.invalidateQueries({ queryKey: pushKeys.campaign(campaignId) });
      queryClient.invalidateQueries({ queryKey: pushKeys.campaigns('') });
    },
  });
}

/**
 * Hook para analytics de campanha
 */
export function useCampaignAnalytics(campaignId: string) {
  return useQuery({
    queryKey: pushKeys.campaignAnalytics(campaignId),
    queryFn: () => pushService.getCampaignAnalytics(campaignId),
    enabled: !!campaignId,
    staleTime: 60000,
  });
}

/**
 * Hook para deletar campanha
 */
export function useDeleteCampaign() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (campaignId: string) => pushService.deleteCampaign(campaignId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: pushKeys.campaigns('') });
    },
  });
}

// ========== Analytics ==========

/**
 * Hook para resumo de métricas
 */
export function useMetricsSummary(params?: {
  period?: string;
  start_date?: string;
  end_date?: string;
  platform?: string;
}) {
  const filters = JSON.stringify(params);

  return useQuery({
    queryKey: pushKeys.metricsSummary(filters),
    queryFn: () => pushService.getMetricsSummary(params),
    staleTime: 60000,
  });
}

/**
 * Hook para estatísticas de dispositivos
 */
export function useDeviceStats() {
  return useQuery({
    queryKey: pushKeys.deviceStats(),
    queryFn: () => pushService.getDeviceStats(),
    staleTime: 300000, // 5 minutos
  });
}

// ========== Helpers ==========

/**
 * Hook para verificar se dispositivo está registrado
 */
export function useIsDeviceRegistered(deviceId: string) {
  return useQuery({
    queryKey: [...pushKeys.device(deviceId), 'registered'],
    queryFn: () => pushService.isDeviceRegistered(deviceId),
    enabled: !!deviceId,
  });
}

/**
 * Hook para enviar notificação para usuário
 */
export function useSendToUser() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      userId,
      title,
      body,
      data,
    }: {
      userId: string;
      title: string;
      body: string;
      data?: Record<string, unknown>;
    }) => pushService.sendToUser(userId, title, body, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: pushKeys.all });
    },
  });
}

/**
 * Hook para enviar notificação para tópico
 */
export function useSendToTopic() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      topic,
      title,
      body,
      data,
    }: {
      topic: string;
      title: string;
      body: string;
      data?: Record<string, unknown>;
    }) => pushService.sendToTopic(topic, title, body, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: pushKeys.all });
    },
  });
}
