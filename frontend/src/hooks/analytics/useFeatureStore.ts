/**
 * Feature Store Hooks
 *
 * Hooks React Query para Feature Store de ML.
 */

import { useQuery, UseQueryOptions } from '@tanstack/react-query';
import { featureStoreService } from '@/services/analytics';

/**
 * Hook para features de usuário
 */
export function useUserFeatures(
  userId: string | number,
  features?: string[],
  options?: Omit<UseQueryOptions<any>, 'queryKey' | 'queryFn'>
) {
  return useQuery({
    queryKey: ['ml-user-features', userId, features],
    queryFn: () => featureStoreService.getUserFeatures(String(userId), features),
    enabled: !!userId,
    staleTime: 300000, // 5 minutos
    ...options,
  });
}

/**
 * Hook para listar features disponíveis
 */
export function useAvailableFeatures(
  options?: Omit<UseQueryOptions<any>, 'queryKey' | 'queryFn'>
) {
  return useQuery({
    queryKey: ['ml-available-features'],
    queryFn: () => featureStoreService.listAvailableFeatures(),
    staleTime: 600000, // 10 minutos
    ...options,
  });
}

/**
 * Hook para metadados de feature
 */
export function useFeatureMetadata(
  featureName: string,
  options?: Omit<UseQueryOptions<any>, 'queryKey' | 'queryFn'>
) {
  return useQuery({
    queryKey: ['ml-feature-metadata', featureName],
    queryFn: () => featureStoreService.getFeatureMetadata(featureName),
    enabled: !!featureName,
    staleTime: 600000,
    ...options,
  });
}
