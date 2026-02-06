/**
 * Hook: useNotifications
 *
 * Gerenciamento de notificações de diaristas.
 */

import { useQuery } from '@tanstack/react-query';
import { diaristNotificationService } from '@/services/diarists';
import type {
  TipoNotificacao,
  CanalNotificacao,
  StatusNotificacao,
} from '@/api/diarists/generated/models';

/**
 * Hook para listar notificações
 */
export function useListNotifications(params?: {
  diaristId?: string;
  tipo?: TipoNotificacao;
  status?: StatusNotificacao;
  limit?: number;
}) {
  return useQuery({
    queryKey: ['diarists', 'notifications', 'list', params],
    queryFn: () => diaristNotificationService.listNotifications(params),
  });
}

/**
 * Hook para notificações de um diarista
 */
export function useDiaristNotifications(diaristId: string, limit?: number) {
  return useQuery({
    queryKey: ['diarists', 'notifications', 'diarist', diaristId, limit],
    queryFn: () => diaristNotificationService.getDiaristNotifications(diaristId, limit),
    enabled: !!diaristId,
  });
}

/**
 * Hook para estatísticas de notificações
 */
export function useNotificationStatistics(params?: {
  dataInicio?: string;
  dataFim?: string;
}) {
  return useQuery({
    queryKey: ['diarists', 'notifications', 'statistics', params],
    queryFn: () => diaristNotificationService.getStatistics(params),
  });
}

/**
 * Hook para listar templates
 */
export function useNotificationTemplates() {
  return useQuery({
    queryKey: ['diarists', 'notifications', 'templates'],
    queryFn: () => diaristNotificationService.listTemplates(),
    staleTime: 1000 * 60 * 60, // 1 hora
  });
}

/**
 * Hook para buscar template específico
 */
export function useNotificationTemplate(tipo: TipoNotificacao) {
  return useQuery({
    queryKey: ['diarists', 'notifications', 'template', tipo],
    queryFn: () => diaristNotificationService.getTemplate(tipo),
    enabled: !!tipo,
    staleTime: 1000 * 60 * 60, // 1 hora
  });
}

/**
 * Hook para listar canais disponíveis
 */
export function useNotificationChannels() {
  return useQuery({
    queryKey: ['diarists', 'notifications', 'channels'],
    queryFn: () => diaristNotificationService.listChannels(),
    staleTime: 1000 * 60 * 60, // 1 hora
  });
}
