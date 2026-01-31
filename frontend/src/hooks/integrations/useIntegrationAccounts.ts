/**
 * Hook: useIntegrationAccounts
 * Gerenciamento de contas de integração
 */

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { integrationAccountService } from '@/lib/api/services/integrations';
import type {
  IntegrationAccountCreate,
  IntegrationAccountUpdate,
  ListAccountsApiV1IntegrationsIntegrationsConnectorsAccountsGetParams,
} from '@/types/generated/integrations/conectaPROIntegrationsAPI.schemas';

const QUERY_KEY = 'integrations-accounts';

/**
 * Hook para listar contas de integração
 */
export function useIntegrationAccounts(
  params?: ListAccountsApiV1IntegrationsIntegrationsConnectorsAccountsGetParams
) {
  return useQuery({
    queryKey: [QUERY_KEY, 'list', params],
    queryFn: () => integrationAccountService.listAccounts(params),
  });
}

/**
 * Hook para obter conta por ID
 */
export function useIntegrationAccount(accountId: string) {
  return useQuery({
    queryKey: [QUERY_KEY, 'detail', accountId],
    queryFn: () => integrationAccountService.getAccount(accountId),
    enabled: !!accountId,
  });
}

/**
 * Hook para criar conta de integração
 */
export function useCreateIntegrationAccount() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: IntegrationAccountCreate) =>
      integrationAccountService.createAccount(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [QUERY_KEY] });
    },
  });
}

/**
 * Hook para atualizar conta
 */
export function useUpdateIntegrationAccount() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ accountId, data }: { accountId: string; data: IntegrationAccountUpdate }) =>
      integrationAccountService.updateAccount(accountId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [QUERY_KEY] });
    },
  });
}

/**
 * Hook para deletar conta
 */
export function useDeleteIntegrationAccount() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (accountId: string) => integrationAccountService.deleteAccount(accountId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [QUERY_KEY] });
    },
  });
}

/**
 * Hook para testar conexão (health check)
 */
export function useTestIntegrationConnection() {
  return useMutation({
    mutationFn: (accountId: string) => integrationAccountService.healthCheck(accountId),
  });
}
