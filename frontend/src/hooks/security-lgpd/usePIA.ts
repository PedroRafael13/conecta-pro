/**
 * React Query Hooks - Privacy Impact Assessment
 * Hooks para avaliações de impacto PIA/DPIA
 */

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { PIAService } from '@/services/security-lgpd';
import type { PIARequest } from '@/services/security-lgpd';

/**
 * Hook para criar avaliação PIA/DPIA
 */
export function useCreatePIA() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (request: PIARequest) => PIAService.createPIA(request),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ['lgpd', 'pia'],
      });
    },
  });
}

/**
 * Hook para consultar avaliação específica
 */
export function usePIA(assessmentId: string, enabled: boolean = true) {
  return useQuery({
    queryKey: ['lgpd', 'pia', assessmentId],
    queryFn: () => PIAService.getPIA(assessmentId),
    enabled: enabled && !!assessmentId,
    staleTime: 5 * 60 * 1000, // 5 minutos
  });
}

/**
 * Hook para listar categorias de risco
 */
export function useRiskCategories() {
  return useQuery({
    queryKey: ['lgpd', 'pia', 'risk-categories'],
    queryFn: () => PIAService.listRiskCategories(),
    staleTime: 30 * 60 * 1000, // 30 minutos (dados estáticos)
  });
}

/**
 * Hook para criar PIA simplificada
 */
export function useCreateSimplePIA() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      projectName,
      description,
      dataCategories,
    }: {
      projectName: string;
      description: string;
      dataCategories: string[];
    }) => PIAService.createSimplePIA(projectName, description, dataCategories),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ['lgpd', 'pia'],
      });
    },
  });
}

/**
 * Hook para criar PIA completa
 */
export function useCreateCompletePIA() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      projectName,
      description,
      dataCategories,
      processingPurposes,
      dataSubjects,
      riskFactors,
    }: {
      projectName: string;
      description: string;
      dataCategories: string[];
      processingPurposes: string[];
      dataSubjects: string[];
      riskFactors: string[];
    }) =>
      PIAService.createCompletePIA(
        projectName,
        description,
        dataCategories,
        processingPurposes,
        dataSubjects,
        riskFactors
      ),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ['lgpd', 'pia'],
      });
    },
  });
}
