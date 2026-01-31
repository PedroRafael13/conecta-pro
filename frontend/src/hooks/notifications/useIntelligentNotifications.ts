/**
 * useIntelligentNotifications Hook
 *
 * Hook para notificações inteligentes com IA
 */

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { intelligentNotificationService } from '@/services/notifications';

// Query Keys
export const intelligentKeys = {
  all: ['intelligent-notifications'] as const,
  behavior: (userId: number) => [...intelligentKeys.all, 'behavior', userId] as const,
  insights: (userId: number) => [...intelligentKeys.all, 'insights', userId] as const,
  engagement: (userId: number, type: string) =>
    [...intelligentKeys.all, 'engagement', userId, type] as const,
  experiments: () => [...intelligentKeys.all, 'experiments'] as const,
  experiment: (id: string) => [...intelligentKeys.experiments(), id] as const,
  experimentResults: (id: string) =>
    [...intelligentKeys.experiment(id), 'results'] as const,
  analytics: () => [...intelligentKeys.all, 'analytics'] as const,
  channelAnalytics: (days: number) =>
    [...intelligentKeys.analytics(), 'channels', days] as const,
  userAnalytics: (userId: number) =>
    [...intelligentKeys.analytics(), 'user', userId] as const,
  consents: () => [...intelligentKeys.all, 'consents'] as const,
  auditLogs: (userId?: number) => [...intelligentKeys.all, 'audit', { userId }] as const,
};

// ========== Personalização ==========

/**
 * Hook para personalizar notificação com IA
 */
export function usePersonalize() {
  return useMutation({
    mutationFn: (data: {
      user_id: number;
      notification_type: string;
      template_title: string;
      template_body: string;
      context?: Record<string, unknown>;
      tone?: string;
    }) => intelligentNotificationService.personalize(data),
  });
}

/**
 * Hook para otimizar timing de envio
 */
export function useOptimizeTiming() {
  return useMutation({
    mutationFn: (data: {
      user_id: number;
      notification_type: string;
      earliest_time?: string;
      deadline?: string;
    }) => intelligentNotificationService.optimizeTiming(data),
  });
}

/**
 * Hook para selecionar canal ideal
 */
export function useSelectChannel() {
  return useMutation({
    mutationFn: (data: {
      user_id: number;
      notification_type: string;
      content?: Record<string, unknown>;
    }) => intelligentNotificationService.selectChannel(data),
  });
}

// ========== Comportamento ==========

/**
 * Hook para obter análise comportamental
 */
export function useUserBehavior(userId: number) {
  return useQuery({
    queryKey: intelligentKeys.behavior(userId),
    queryFn: () => intelligentNotificationService.getUserBehavior(userId),
    enabled: !!userId && userId > 0,
    staleTime: 300000, // 5 minutos
  });
}

/**
 * Hook para insights comportamentais
 */
export function useBehaviorInsights(userId: number) {
  return useQuery({
    queryKey: intelligentKeys.insights(userId),
    queryFn: () => intelligentNotificationService.getBehaviorInsights(userId),
    enabled: !!userId && userId > 0,
    staleTime: 300000,
  });
}

/**
 * Hook para predição de engajamento
 */
export function usePredictEngagement(userId: number, notificationType: string) {
  return useQuery({
    queryKey: intelligentKeys.engagement(userId, notificationType),
    queryFn: () =>
      intelligentNotificationService.predictEngagement(userId, notificationType),
    enabled: !!userId && userId > 0 && !!notificationType,
    staleTime: 60000, // 1 minuto
  });
}

// ========== A/B Testing ==========

/**
 * Hook para criar experimento
 */
export function useCreateExperiment() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: {
      name: string;
      description: string;
      variants: Array<Record<string, unknown>>;
      primary_metric?: string;
      target_sample_size?: number;
      min_confidence?: number;
    }) => intelligentNotificationService.createExperiment(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: intelligentKeys.experiments() });
    },
  });
}

/**
 * Hook para iniciar experimento
 */
export function useStartExperiment() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (experimentId: string) =>
      intelligentNotificationService.startExperiment(experimentId),
    onSuccess: (_, experimentId) => {
      queryClient.invalidateQueries({
        queryKey: intelligentKeys.experiment(experimentId),
      });
    },
  });
}

/**
 * Hook para obter resultados do experimento
 */
export function useExperimentResults(experimentId: string) {
  return useQuery({
    queryKey: intelligentKeys.experimentResults(experimentId),
    queryFn: () => intelligentNotificationService.getExperimentResults(experimentId),
    enabled: !!experimentId,
    staleTime: 60000,
  });
}

/**
 * Hook para alocar usuário a variante
 */
export function useAllocateToVariant() {
  return useMutation({
    mutationFn: ({ experimentId, userId }: { experimentId: string; userId: number }) =>
      intelligentNotificationService.allocateUserToVariant(experimentId, userId),
  });
}

/**
 * Hook para registrar evento de experimento
 */
export function useRecordExperimentEvent() {
  return useMutation({
    mutationFn: ({
      experimentId,
      variantId,
      eventType,
      userId,
    }: {
      experimentId: string;
      variantId: string;
      eventType: string;
      userId: number;
    }) =>
      intelligentNotificationService.recordExperimentEvent(
        experimentId,
        variantId,
        eventType,
        userId
      ),
  });
}

// ========== Analytics ==========

/**
 * Hook para dashboard de analytics
 */
export function useAnalyticsDashboard() {
  return useQuery({
    queryKey: intelligentKeys.analytics(),
    queryFn: () => intelligentNotificationService.getAnalyticsDashboard(),
    staleTime: 60000,
    refetchInterval: 120000, // Refetch a cada 2 minutos
  });
}

/**
 * Hook para analytics por canal
 */
export function useChannelAnalytics(days: number = 30) {
  return useQuery({
    queryKey: intelligentKeys.channelAnalytics(days),
    queryFn: () => intelligentNotificationService.getChannelAnalytics(days),
    staleTime: 300000, // 5 minutos
  });
}

/**
 * Hook para analytics de usuário
 */
export function useUserAnalytics(userId: number) {
  return useQuery({
    queryKey: intelligentKeys.userAnalytics(userId),
    queryFn: () => intelligentNotificationService.getUserAnalytics(userId),
    enabled: !!userId && userId > 0,
    staleTime: 300000,
  });
}

/**
 * Hook para gerar relatório
 */
export function useGenerateReport() {
  return useMutation({
    mutationFn: ({ startDate, endDate }: { startDate: string; endDate: string }) =>
      intelligentNotificationService.generateReport(startDate, endDate),
  });
}

// ========== LGPD ==========

/**
 * Hook para registrar consentimento
 */
export function useRecordConsent() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: {
      consent_type: string;
      granted: boolean;
      consent_text: string;
      version: string;
    }) => intelligentNotificationService.recordConsent(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: intelligentKeys.consents() });
    },
  });
}

/**
 * Hook para retirar consentimento
 */
export function useWithdrawConsent() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (consentType: string) =>
      intelligentNotificationService.withdrawConsent(consentType),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: intelligentKeys.consents() });
    },
  });
}

/**
 * Hook para obter consentimentos do usuário
 */
export function useUserConsents() {
  return useQuery({
    queryKey: intelligentKeys.consents(),
    queryFn: () => intelligentNotificationService.getUserConsents(),
    staleTime: 300000, // 5 minutos
  });
}

/**
 * Hook para criar solicitação de dados
 */
export function useCreateDataRequest() {
  return useMutation({
    mutationFn: (data: { request_type: string; requester_email: string }) =>
      intelligentNotificationService.createDataRequest(data),
  });
}

/**
 * Hook para verificar solicitação de dados
 */
export function useVerifyDataRequest() {
  return useMutation({
    mutationFn: ({ requestId, token }: { requestId: string; token: string }) =>
      intelligentNotificationService.verifyDataRequest(requestId, token),
  });
}

/**
 * Hook para logs de auditoria de notificações
 */
export function useNotificationAuditLogs(userId?: number, limit: number = 100) {
  return useQuery({
    queryKey: intelligentKeys.auditLogs(userId),
    queryFn: () => intelligentNotificationService.getAuditLogs(userId, limit),
    staleTime: 60000,
  });
}

// ========== Utility ==========

/**
 * Hook para health check
 */
export function useHealthCheck() {
  return useQuery({
    queryKey: [...intelligentKeys.all, 'health'],
    queryFn: () => intelligentNotificationService.healthCheck(),
    staleTime: 60000,
  });
}

/**
 * Hook para verificar se pode enviar notificação
 */
export function useCanSendNotification(userId: number, notificationType: string) {
  return useQuery({
    queryKey: [...intelligentKeys.all, 'can-send', userId, notificationType],
    queryFn: () =>
      intelligentNotificationService.canSendNotification(userId, notificationType),
    enabled: !!userId && userId > 0 && !!notificationType,
  });
}
