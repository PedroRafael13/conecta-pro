/**
 * React Query Hooks - Document Kit Operational
 *
 * Hooks customizados para integração operacional e geração automática.
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { toast } from 'sonner';
import {
  documentKitOperationalService,
  type GetEmployeesParams,
  type GetEmployeesByMonthParams,
  type ValidateCondominiumParams,
  type GenerateMonthlyKitsParams,
  type GenerateBatchKitsParams,
} from '@/services/document-kits/documentKitOperationalService';
import { documentKitAssignmentKeys } from './useDocumentKitAssignments';

// Query Keys
export const documentKitOperationalKeys = {
  all: ['document-kit-operational'] as const,
  employees: (params: GetEmployeesParams) =>
    [...documentKitOperationalKeys.all, 'employees', params] as const,
  employeesByMonth: (params: GetEmployeesByMonthParams) =>
    [...documentKitOperationalKeys.all, 'employees-month', params] as const,
  condominiums: () =>
    [...documentKitOperationalKeys.all, 'condominiums'] as const,
  validation: (params: ValidateCondominiumParams) =>
    [...documentKitOperationalKeys.all, 'validation', params] as const,
  schedulerStatus: () =>
    [...documentKitOperationalKeys.all, 'scheduler-status'] as const,
};

/**
 * Hook para buscar funcionários por condomínio
 */
export function useGetEmployeesByCondominium(params: GetEmployeesParams) {
  return useQuery({
    queryKey: documentKitOperationalKeys.employees(params),
    queryFn: () =>
      documentKitOperationalService.getEmployeesByCondominium(params),
    enabled: !!params.condominium_id,
    staleTime: 5 * 60 * 1000, // 5 minutos
  });
}

/**
 * Hook para buscar funcionários por mês
 */
export function useGetEmployeesByMonth(params: GetEmployeesByMonthParams) {
  return useQuery({
    queryKey: documentKitOperationalKeys.employeesByMonth(params),
    queryFn: () => documentKitOperationalService.getEmployeesByMonth(params),
    enabled: !!params.condominium_id && !!params.month && !!params.year,
    staleTime: 10 * 60 * 1000, // 10 minutos
  });
}

/**
 * Hook para listar condomínios com funcionários
 */
export function useGetCondominiumsWithEmployees() {
  return useQuery({
    queryKey: documentKitOperationalKeys.condominiums(),
    queryFn: () =>
      documentKitOperationalService.getCondominiumsWithEmployees(),
    staleTime: 15 * 60 * 1000, // 15 minutos
  });
}

/**
 * Hook para validar condomínio
 */
export function useValidateCondominium(params: ValidateCondominiumParams) {
  return useQuery({
    queryKey: documentKitOperationalKeys.validation(params),
    queryFn: () =>
      documentKitOperationalService.validateCondominiumHasEmployees(params),
    enabled: !!params.condominium_id,
    staleTime: 5 * 60 * 1000, // 5 minutos
  });
}

/**
 * Hook para buscar status do scheduler
 */
export function useSchedulerStatus() {
  return useQuery({
    queryKey: documentKitOperationalKeys.schedulerStatus(),
    queryFn: () => documentKitOperationalService.getSchedulerStatus(),
    staleTime: 1 * 60 * 1000, // 1 minuto
    refetchInterval: 2 * 60 * 1000, // Refetch a cada 2 minutos
  });
}

/**
 * Hook para gerar kits mensais para um condomínio
 */
export function useGenerateMonthlyKits() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (params: GenerateMonthlyKitsParams) =>
      documentKitOperationalService.generateMonthlyKits(params),
    onSuccess: (result) => {
      queryClient.invalidateQueries({
        queryKey: documentKitAssignmentKeys.lists(),
      });
      toast.success(
        `Kits gerados com sucesso! ${result.assignments_created} atribuições criadas.`
      );
    },
    onError: (error: Error) => {
      toast.error(`Erro ao gerar kits mensais: ${error.message}`);
    },
  });
}

/**
 * Hook para gerar kits em lote para todos os condomínios
 */
export function useGenerateBatchKits() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (params: GenerateBatchKitsParams) =>
      documentKitOperationalService.generateBatchKits(params),
    onSuccess: (result) => {
      queryClient.invalidateQueries({
        queryKey: documentKitAssignmentKeys.lists(),
      });
      toast.success(
        `Geração em lote concluída! ${result.total_assignments_created} atribuições criadas em ${result.condominiums_processed} condomínios.`
      );
    },
    onError: (error: Error) => {
      toast.error(`Erro ao gerar kits em lote: ${error.message}`);
    },
  });
}

/**
 * Hook para iniciar scheduler
 */
export function useStartScheduler() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: () => documentKitOperationalService.startScheduler(),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: documentKitOperationalKeys.schedulerStatus(),
      });
      toast.success('Scheduler iniciado com sucesso!');
    },
    onError: (error: Error) => {
      toast.error(`Erro ao iniciar scheduler: ${error.message}`);
    },
  });
}

/**
 * Hook para parar scheduler
 */
export function useStopScheduler() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: () => documentKitOperationalService.stopScheduler(),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: documentKitOperationalKeys.schedulerStatus(),
      });
      toast.success('Scheduler parado com sucesso!');
    },
    onError: (error: Error) => {
      toast.error(`Erro ao parar scheduler: ${error.message}`);
    },
  });
}
