/**
 * Hooks React Query - PCMSO (NR-7)
 * Exames Médicos Ocupacionais e ASO
 *
 * @module hooks/health-occupational/usePCMSO
 * @author Conecta PRO Team
 * @date 2026-01-28
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { pcmsoService, type MedicalExamCreate, type ASOCreate, type ExamStatus, type ExamType } from '@/lib/services/health-occupational/pcmso';
import { getErrorMessage } from '@/lib/api';

// =============================================================================
// QUERY KEYS
// =============================================================================

export const pcmsoKeys = {
  all: ['pcmso'] as const,
  exams: () => [...pcmsoKeys.all, 'exams'] as const,
  exam: (id: string) => [...pcmsoKeys.exams(), id] as const,
  employeeExams: (funcionarioId: string) => [...pcmsoKeys.exams(), 'employee', funcionarioId] as const,
  asos: () => [...pcmsoKeys.all, 'asos'] as const,
  aso: (id: string) => [...pcmsoKeys.asos(), id] as const,
  expiringASOs: (days: number) => [...pcmsoKeys.asos(), 'expiring', days] as const,
  statistics: () => [...pcmsoKeys.all, 'statistics'] as const,
};

// =============================================================================
// EXAMES MÉDICOS - QUERIES
// =============================================================================

/**
 * Hook para buscar exame por ID
 */
export function useExam(exameId: string | null) {
  return useQuery({
    queryKey: pcmsoKeys.exam(exameId!),
    queryFn: () => pcmsoService.getExam(exameId!),
    enabled: !!exameId,
    staleTime: 5 * 60 * 1000, // 5 minutos
  });
}

/**
 * Hook para listar exames de um funcionário
 */
export function useEmployeeExams(
  funcionarioId: string | null,
  filters?: {
    status?: ExamStatus;
    tipo?: ExamType;
    page?: number;
    size?: number;
  }
) {
  return useQuery({
    queryKey: [...pcmsoKeys.employeeExams(funcionarioId!), filters],
    queryFn: () => pcmsoService.listEmployeeExams(funcionarioId!, filters),
    enabled: !!funcionarioId,
    staleTime: 2 * 60 * 1000, // 2 minutos
  });
}

// =============================================================================
// EXAMES MÉDICOS - MUTATIONS
// =============================================================================

/**
 * Hook para agendar exame médico
 */
export function useScheduleExam() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: MedicalExamCreate) => pcmsoService.scheduleExam(data),
    onSuccess: (_, variables) => {
      // Invalida lista de exames do funcionário
      queryClient.invalidateQueries({
        queryKey: pcmsoKeys.employeeExams(variables.funcionario_id),
      });
      // Invalida estatísticas
      queryClient.invalidateQueries({
        queryKey: pcmsoKeys.statistics(),
      });
    },
  });
}

/**
 * Hook para atualizar exame
 */
export function useUpdateExam() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ exameId, data }: { exameId: string; data: any }) =>
      pcmsoService.updateExam(exameId, data),
    onSuccess: (_, { exameId }) => {
      // Invalida exame específico
      queryClient.invalidateQueries({
        queryKey: pcmsoKeys.exam(exameId),
      });
      // Invalida todas as listas de exames
      queryClient.invalidateQueries({
        queryKey: pcmsoKeys.exams(),
      });
    },
  });
}

/**
 * Hook para confirmar exame
 */
export function useConfirmExam() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (exameId: string) => pcmsoService.confirmExam(exameId),
    onSuccess: (_, exameId) => {
      queryClient.invalidateQueries({ queryKey: pcmsoKeys.exam(exameId) });
      queryClient.invalidateQueries({ queryKey: pcmsoKeys.exams() });
    },
  });
}

/**
 * Hook para marcar exame como realizado
 */
export function useCompleteExam() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (exameId: string) => pcmsoService.completeExam(exameId),
    onSuccess: (_, exameId) => {
      queryClient.invalidateQueries({ queryKey: pcmsoKeys.exam(exameId) });
      queryClient.invalidateQueries({ queryKey: pcmsoKeys.exams() });
      queryClient.invalidateQueries({ queryKey: pcmsoKeys.statistics() });
    },
  });
}

// =============================================================================
// ASO - QUERIES
// =============================================================================

/**
 * Hook para buscar ASO por ID
 */
export function useASO(asoId: string | null) {
  return useQuery({
    queryKey: pcmsoKeys.aso(asoId!),
    queryFn: () => pcmsoService.getASO(asoId!),
    enabled: !!asoId,
    staleTime: 10 * 60 * 1000, // 10 minutos
  });
}

/**
 * Hook para listar ASOs com vencimento próximo
 */
export function useExpiringASOs(days: number = 30) {
  return useQuery({
    queryKey: pcmsoKeys.expiringASOs(days),
    queryFn: () => pcmsoService.listExpiringASOs(days),
    staleTime: 5 * 60 * 1000, // 5 minutos
  });
}

// =============================================================================
// ASO - MUTATIONS
// =============================================================================

/**
 * Hook para emitir ASO
 */
export function useEmitASO() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: ASOCreate) => pcmsoService.emitASO(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: pcmsoKeys.asos() });
      queryClient.invalidateQueries({ queryKey: pcmsoKeys.statistics() });
    },
  });
}

/**
 * Hook para assinar ASO
 */
export function useSignASO() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (asoId: string) => pcmsoService.signASO(asoId),
    onSuccess: (_, asoId) => {
      queryClient.invalidateQueries({ queryKey: pcmsoKeys.aso(asoId) });
    },
  });
}

// =============================================================================
// ESTATÍSTICAS
// =============================================================================

/**
 * Hook para estatísticas do PCMSO
 */
export function usePCMSOStatistics() {
  return useQuery({
    queryKey: pcmsoKeys.statistics(),
    queryFn: () => pcmsoService.getStatistics(),
    staleTime: 10 * 60 * 1000, // 10 minutos
  });
}

// =============================================================================
// HELPER HOOKS
// =============================================================================

/**
 * Hook auxiliar com todas as funcionalidades do PCMSO
 */
export function usePCMSO(funcionarioId?: string | null) {
  const scheduleExam = useScheduleExam();
  const updateExam = useUpdateExam();
  const confirmExam = useConfirmExam();
  const completeExam = useCompleteExam();
  const emitASO = useEmitASO();
  const signASO = useSignASO();

  const employeeExams = useEmployeeExams(funcionarioId || null);
  const expiringASOs = useExpiringASOs(30);
  const statistics = usePCMSOStatistics();

  return {
    // Mutations
    scheduleExam,
    updateExam,
    confirmExam,
    completeExam,
    emitASO,
    signASO,
    // Queries
    employeeExams,
    expiringASOs,
    statistics,
  };
}
