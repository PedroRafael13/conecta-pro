/**
 * usePreferences Hook
 *
 * Hook para gerenciamento de preferências de notificação
 */

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { preferenceService } from '@/services/notifications';
import type {
  PreferenceUpdate,
  PreferenceResponse,
} from '@/types/generated/notifications/conectaPRONotificationsModule.schemas';

// Query Keys
export const preferenceKeys = {
  all: ['notification-preferences'] as const,
  my: () => [...preferenceKeys.all, 'me'] as const,
};

/**
 * Hook para obter preferências do usuário
 */
export function useMyPreferences() {
  return useQuery({
    queryKey: preferenceKeys.my(),
    queryFn: () => preferenceService.getMyPreferences(),
    staleTime: 60000, // 1 minuto
  });
}

/**
 * Hook para atualizar preferências
 */
export function useUpdatePreferences() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: PreferenceUpdate) =>
      preferenceService.updateMyPreferences(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: preferenceKeys.my() });
    },
  });
}

/**
 * Hook para unsubscribe
 */
export function useUnsubscribe() {
  return useMutation({
    mutationFn: (token: string) => preferenceService.unsubscribe(token),
  });
}

/**
 * Hook para habilitar/desabilitar canal
 */
export function useToggleChannel() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ channel, enable }: { channel: string; enable: boolean }) =>
      enable
        ? preferenceService.enableChannel(channel)
        : preferenceService.disableChannel(channel),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: preferenceKeys.my() });
    },
  });
}

/**
 * Hook para habilitar/desabilitar categoria
 */
export function useToggleCategory() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ category, enable }: { category: string; enable: boolean }) =>
      enable
        ? preferenceService.enableCategory(category)
        : preferenceService.disableCategory(category),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: preferenceKeys.my() });
    },
  });
}

/**
 * Hook para definir horário de não perturbe
 */
export function useSetQuietHours() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ start, end }: { start: string; end: string }) =>
      preferenceService.setQuietHours(start, end),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: preferenceKeys.my() });
    },
  });
}

/**
 * Hook para remover horário de não perturbe
 */
export function useClearQuietHours() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: () => preferenceService.clearQuietHours(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: preferenceKeys.my() });
    },
  });
}

/**
 * Hook para verificar se canal está habilitado
 */
export function useIsChannelEnabled(channel: string) {
  const { data: preferences } = useMyPreferences();

  if (!preferences) return true;

  const channelMap: Record<string, boolean | undefined> = {
    email: preferences.email_enabled,
    whatsapp: preferences.whatsapp_enabled,
    sms: preferences.sms_enabled,
    push: preferences.push_enabled,
    in_app: preferences.in_app_enabled,
  };

  return channelMap[channel] ?? true;
}

/**
 * Hook para verificar se categoria está habilitada
 * Verifica se notificações estão habilitadas e se marketing consent está ativo para categorias de marketing
 */
export function useIsCategoryEnabled(category: string) {
  const { data: preferences } = useMyPreferences();

  if (!preferences) return true;

  // Se notificações globais estão desabilitadas, todas categorias estão desabilitadas
  if (preferences.notifications_enabled === false) return false;

  // Se é unsubscribe global, tudo desabilitado
  if (preferences.global_unsubscribe === true) return false;

  // Categorias de marketing dependem do marketing_consent
  if (category === 'marketing') {
    return preferences.marketing_consent ?? true;
  }

  // Outras categorias seguem o consentimento transacional
  return preferences.transactional_consent ?? true;
}
