/**
 * Hooks React Query - Integration Settings
 * Gestão de Integrações
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { integrationService } from '@/services/clients';
import type {
  IntegrationSettingsCreate,
  IntegrationSettingsUpdate,
} from '@/types/generated/clients/conectaPROMóduloCLIENTS.schemas';

/**
 * Query keys para cache
 */
export const integrationKeys = {
  all: ['integrations'] as const,
  lists: () => [...integrationKeys.all, 'list'] as const,
  list: (clientId: string) => [...integrationKeys.lists(), clientId] as const,
  details: () => [...integrationKeys.all, 'detail'] as const,
  detail: (id: string) => [...integrationKeys.details(), id] as const,
};

/**
 * Hook para listar integrações do cliente
 */
export function useIntegrations(clientId: string, enabled = true) {
  return useQuery({
    queryKey: integrationKeys.list(clientId),
    queryFn: () => integrationService.list(clientId),
    enabled: enabled && !!clientId,
  });
}

/**
 * Hook para obter integração por ID
 */
export function useIntegration(settingsId: string, enabled = true) {
  return useQuery({
    queryKey: integrationKeys.detail(settingsId),
    queryFn: () => integrationService.getById(settingsId),
    enabled: enabled && !!settingsId,
  });
}

/**
 * Hook para criar integração
 */
export function useCreateIntegration() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      clientId,
      data,
    }: {
      clientId: string;
      data: IntegrationSettingsCreate;
    }) => integrationService.create(clientId, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({
        queryKey: integrationKeys.list(variables.clientId),
      });
    },
  });
}

/**
 * Hook para atualizar integração
 */
export function useUpdateIntegration() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      settingsId,
      data,
    }: {
      settingsId: string;
      data: IntegrationSettingsUpdate;
    }) => integrationService.update(settingsId, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({
        queryKey: integrationKeys.detail(variables.settingsId),
      });
      queryClient.invalidateQueries({ queryKey: integrationKeys.lists() });
    },
  });
}

/**
 * Hook para habilitar integração
 */
export function useEnableIntegration() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (settingsId: string) => integrationService.enable(settingsId),
    onSuccess: (_, settingsId) => {
      queryClient.invalidateQueries({
        queryKey: integrationKeys.detail(settingsId),
      });
      queryClient.invalidateQueries({ queryKey: integrationKeys.lists() });
    },
  });
}

/**
 * Hook para desabilitar integração
 */
export function useDisableIntegration() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (settingsId: string) => integrationService.disable(settingsId),
    onSuccess: (_, settingsId) => {
      queryClient.invalidateQueries({
        queryKey: integrationKeys.detail(settingsId),
      });
      queryClient.invalidateQueries({ queryKey: integrationKeys.lists() });
    },
  });
}
