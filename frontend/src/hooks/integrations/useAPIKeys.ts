/**
 * Hook: useAPIKeys
 * Gerenciamento de API Keys
 */

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { apiKeyService } from '@/lib/api/services/integrations';
import type {
  APIKeyCreate,
  APIKeyUpdate,
  ListApiKeysApiV1IntegrationsApiKeysGetParams,
  RevokeApiKeyApiV1IntegrationsApiKeysKeyIdRevokePostBody,
  VerifyApiKeyApiV1IntegrationsApiKeysVerifyPostParams,
} from '@/types/generated/integrations/conectaPROIntegrationsAPI.schemas';

const QUERY_KEY = 'integrations-api-keys';

/**
 * Hook para listar API keys
 */
export function useAPIKeys(params?: ListApiKeysApiV1IntegrationsApiKeysGetParams) {
  return useQuery({
    queryKey: [QUERY_KEY, 'list', params],
    queryFn: () => apiKeyService.listApiKeys(params),
  });
}

/**
 * Hook para obter API key por ID
 */
export function useAPIKey(keyId: string) {
  return useQuery({
    queryKey: [QUERY_KEY, 'detail', keyId],
    queryFn: () => apiKeyService.getApiKey(keyId),
    enabled: !!keyId,
  });
}

/**
 * Hook para criar API key
 */
export function useCreateAPIKey() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: APIKeyCreate) => apiKeyService.createApiKey(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [QUERY_KEY] });
    },
  });
}

/**
 * Hook para atualizar API key
 */
export function useUpdateAPIKey() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ keyId, data }: { keyId: string; data: APIKeyUpdate }) =>
      apiKeyService.updateApiKey(keyId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [QUERY_KEY] });
    },
  });
}

/**
 * Hook para revogar API key
 */
export function useRevokeAPIKey() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      keyId,
      data,
    }: {
      keyId: string;
      data: RevokeApiKeyApiV1IntegrationsApiKeysKeyIdRevokePostBody;
    }) => apiKeyService.revokeApiKey(keyId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [QUERY_KEY] });
    },
  });
}

/**
 * Hook para verificar API key
 */
export function useVerifyAPIKey() {
  return useMutation({
    mutationFn: (params: VerifyApiKeyApiV1IntegrationsApiKeysVerifyPostParams) =>
      apiKeyService.verifyApiKey(params),
  });
}
