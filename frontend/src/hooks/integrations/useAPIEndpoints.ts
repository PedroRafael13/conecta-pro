/**
 * Hook: useAPIEndpoints
 * Gerenciamento de API Endpoints
 */

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { apiEndpointService } from '@/lib/api/services/integrations';
import type {
  APIEndpointCreate,
  APIEndpointUpdate,
  ListEndpointsApiV1IntegrationsEndpointsGetParams,
} from '@/types/generated/integrations/conectaPROIntegrationsAPI.schemas';

const QUERY_KEY = 'integrations-api-endpoints';

/**
 * Hook para listar endpoints
 */
export function useAPIEndpoints(params?: ListEndpointsApiV1IntegrationsEndpointsGetParams) {
  return useQuery({
    queryKey: [QUERY_KEY, 'list', params],
    queryFn: () => apiEndpointService.listEndpoints(params),
  });
}

/**
 * Hook para obter endpoint por ID
 */
export function useAPIEndpoint(endpointId: string) {
  return useQuery({
    queryKey: [QUERY_KEY, 'detail', endpointId],
    queryFn: () => apiEndpointService.getEndpoint(endpointId),
    enabled: !!endpointId,
  });
}

/**
 * Hook para criar endpoint
 */
export function useCreateAPIEndpoint() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: APIEndpointCreate) => apiEndpointService.createEndpoint(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [QUERY_KEY] });
    },
  });
}

/**
 * Hook para atualizar endpoint
 */
export function useUpdateAPIEndpoint() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ endpointId, data }: { endpointId: string; data: APIEndpointUpdate }) =>
      apiEndpointService.updateEndpoint(endpointId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [QUERY_KEY] });
    },
  });
}

/**
 * Hook para deletar endpoint
 */
export function useDeleteAPIEndpoint() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (endpointId: string) => apiEndpointService.deleteEndpoint(endpointId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [QUERY_KEY] });
    },
  });
}

/**
 * Hook para depreciar endpoint
 */
export function useDeprecateAPIEndpoint() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ endpointId, params }: { endpointId: string; params: any }) =>
      apiEndpointService.deprecateEndpoint(endpointId, params),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [QUERY_KEY] });
    },
  });
}
