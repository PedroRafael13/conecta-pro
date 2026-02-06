/**
 * Hook: useWebhooks
 * Gerenciamento de Webhooks
 */

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { webhookService } from '@/lib/api/services/integrations';
import type {
  WebhookConfigCreate,
  WebhookConfigUpdate,
  WebhookTestRequest,
  ListWebhooksApiV1IntegrationsWebhooksGetParams,
  TriggerWebhookEventApiV1IntegrationsWebhooksTriggerPostBody,
  TriggerWebhookEventApiV1IntegrationsWebhooksTriggerPostParams,
} from '@/types/generated/integrations/conectaPROIntegrationsAPI.schemas';

const QUERY_KEY = 'integrations-webhooks';

/**
 * Hook para listar webhooks
 */
export function useWebhooks(params?: ListWebhooksApiV1IntegrationsWebhooksGetParams) {
  return useQuery({
    queryKey: [QUERY_KEY, 'list', params],
    queryFn: () => webhookService.listWebhooks(params),
  });
}

/**
 * Hook para obter webhook por ID
 */
export function useWebhook(webhookId: string) {
  return useQuery({
    queryKey: [QUERY_KEY, 'detail', webhookId],
    queryFn: () => webhookService.getWebhook(webhookId),
    enabled: !!webhookId,
  });
}

/**
 * Hook para obter estatísticas do webhook
 */
export function useWebhookStats(webhookId: string) {
  return useQuery({
    queryKey: [QUERY_KEY, 'stats', webhookId],
    queryFn: () => webhookService.getWebhookStats(webhookId),
    enabled: !!webhookId,
  });
}

/**
 * Hook para criar webhook
 */
export function useCreateWebhook() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: WebhookConfigCreate) => webhookService.createWebhook(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [QUERY_KEY] });
    },
  });
}

/**
 * Hook para atualizar webhook
 */
export function useUpdateWebhook() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ webhookId, data }: { webhookId: string; data: WebhookConfigUpdate }) =>
      webhookService.updateWebhook(webhookId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [QUERY_KEY] });
    },
  });
}

/**
 * Hook para testar webhook
 */
export function useTestWebhook() {
  return useMutation({
    mutationFn: ({ webhookId, data }: { webhookId: string; data: WebhookTestRequest }) =>
      webhookService.testWebhook(webhookId, data),
  });
}

/**
 * Hook para regenerar secret do webhook
 */
export function useRegenerateWebhookSecret() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (webhookId: string) => webhookService.regenerateSecret(webhookId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [QUERY_KEY] });
    },
  });
}

/**
 * Hook para disparar evento de webhook
 */
export function useTriggerWebhookEvent() {
  return useMutation({
    mutationFn: ({
      data,
      params,
    }: {
      data: TriggerWebhookEventApiV1IntegrationsWebhooksTriggerPostBody;
      params: TriggerWebhookEventApiV1IntegrationsWebhooksTriggerPostParams;
    }) => webhookService.triggerWebhookEvent(data, params),
  });
}
