/**
 * React Query Hooks - Data Erasure
 * Hooks para direito ao esquecimento LGPD
 */

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { ErasureService } from '@/services/security-lgpd';
import type { ErasureRequestSchema } from '@/services/security-lgpd';

/**
 * Hook para solicitar exclusão de dados
 */
export function useRequestErasure() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (request: ErasureRequestSchema) =>
      ErasureService.requestErasure(request),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ['lgpd', 'erasure'],
      });
    },
  });
}

/**
 * Hook para consultar status de exclusão
 */
export function useErasureStatus(requestId: string, enabled: boolean = true) {
  return useQuery({
    queryKey: ['lgpd', 'erasure', 'status', requestId],
    queryFn: () => ErasureService.getErasureStatus(requestId),
    enabled: enabled && !!requestId,
    refetchInterval: 5000, // Poll a cada 5 segundos para acompanhar progresso
    staleTime: 0, // Sempre buscar dados atualizados
  });
}

/**
 * Hook para solicitar exclusão total
 */
export function useRequestFullErasure() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      titularId,
      titularEmail,
      reason,
    }: {
      titularId: string;
      titularEmail: string;
      reason: string;
    }) => ErasureService.requestFullErasure(titularId, titularEmail, reason),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ['lgpd', 'erasure'],
      });
    },
  });
}

/**
 * Hook para solicitar exclusão de dados pessoais
 */
export function useRequestPersonalDataErasure() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      titularId,
      titularEmail,
      reason,
    }: {
      titularId: string;
      titularEmail: string;
      reason: string;
    }) => ErasureService.requestPersonalDataErasure(titularId, titularEmail, reason),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ['lgpd', 'erasure'],
      });
    },
  });
}

/**
 * Hook para solicitar exclusão de dados transacionais
 */
export function useRequestTransactionalErasure() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      titularId,
      titularEmail,
      reason,
    }: {
      titularId: string;
      titularEmail: string;
      reason: string;
    }) =>
      ErasureService.requestTransactionalErasure(titularId, titularEmail, reason),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ['lgpd', 'erasure'],
      });
    },
  });
}
