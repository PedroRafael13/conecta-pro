/**
 * Model Management Hooks
 *
 * Hooks React Query para gerenciamento de modelos ML.
 */

import { useQuery, useMutation, UseQueryOptions, UseMutationOptions, useQueryClient } from '@tanstack/react-query';
import { modelManagementService } from '@/services/analytics';

/**
 * Hook para listar modelos
 */
export function useModels(
  options?: Omit<UseQueryOptions<any>, 'queryKey' | 'queryFn'>
) {
  return useQuery({
    queryKey: ['ml-models'],
    queryFn: () => modelManagementService.listModels(),
    staleTime: 600000, // 10 minutos
    ...options,
  });
}

/**
 * Hook para listar versões de modelo
 */
export function useModelVersions(
  modelName: string,
  stage?: string,
  options?: Omit<UseQueryOptions<any>, 'queryKey' | 'queryFn'>
) {
  return useQuery({
    queryKey: ['ml-model-versions', modelName, stage],
    queryFn: () => modelManagementService.listModelVersions(modelName, stage),
    enabled: !!modelName,
    staleTime: 600000,
    ...options,
  });
}

/**
 * Hook para comparar versões
 */
export function useCompareVersions(
  modelName: string,
  version1: string,
  version2: string,
  options?: Omit<UseQueryOptions<any>, 'queryKey' | 'queryFn'>
) {
  return useQuery({
    queryKey: ['ml-model-compare', modelName, version1, version2],
    queryFn: () => modelManagementService.compareVersions(modelName, version1, version2),
    enabled: !!modelName && !!version1 && !!version2,
    staleTime: 600000,
    ...options,
  });
}

/**
 * Hook para promover modelo
 */
export function usePromoteModel(
  options?: UseMutationOptions<any, Error, { modelName: string; version: string; targetStage?: string }>
) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ modelName, version, targetStage }) =>
      modelManagementService.promoteModel(modelName, version, targetStage),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['ml-models'] });
      queryClient.invalidateQueries({ queryKey: ['ml-model-versions', variables.modelName] });
    },
    ...options,
  });
}
