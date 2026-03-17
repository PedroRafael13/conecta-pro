/**
 * Hooks React Query - SST (Saude e Seguranca do Trabalho)
 * Afastamentos, CAT, Estabilidade, Ajuda Medicamento
 *
 * @module hooks/sst
 * @author Conecta PRO Team
 * @date 2026-03-16
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  sstService,
  type AfastamentoCreate,
  type CATCreate,
} from '@/lib/services/sst';

// =============================================================================
// QUERY KEYS
// =============================================================================

export const sstKeys = {
  all: ['sst'] as const,
  dashboard: () => [...sstKeys.all, 'dashboard'] as const,
  afastamentos: () => [...sstKeys.all, 'afastamentos'] as const,
  afastamento: (id: string) => [...sstKeys.afastamentos(), id] as const,
  cats: () => [...sstKeys.all, 'cats'] as const,
  taxaAcidente: () => [...sstKeys.all, 'taxa-acidente'] as const,
  estabilidade: () => [...sstKeys.all, 'estabilidade'] as const,
  ajudaMedicamento: () => [...sstKeys.all, 'ajuda-medicamento'] as const,
};

// =============================================================================
// DASHBOARD
// =============================================================================

/**
 * Hook para dashboard SST
 */
export function useSSTDashboard() {
  return useQuery({
    queryKey: sstKeys.dashboard(),
    queryFn: () => sstService.getDashboard(),
    staleTime: 5 * 60 * 1000,
  });
}

// =============================================================================
// AFASTAMENTOS - QUERIES
// =============================================================================

/**
 * Hook para listar afastamentos
 */
export function useAfastamentos(status?: string) {
  return useQuery({
    queryKey: [...sstKeys.afastamentos(), status],
    queryFn: () => sstService.listAfastamentos(status),
    staleTime: 2 * 60 * 1000,
  });
}

/**
 * Hook para buscar afastamento por ID
 */
export function useAfastamento(id: string | null) {
  return useQuery({
    queryKey: sstKeys.afastamento(id!),
    queryFn: () => sstService.getAfastamento(id!),
    enabled: !!id,
    staleTime: 5 * 60 * 1000,
  });
}

// =============================================================================
// AFASTAMENTOS - MUTATIONS
// =============================================================================

/**
 * Hook para criar afastamento
 */
export function useCreateAfastamento() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: AfastamentoCreate) =>
      sstService.createAfastamento(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: sstKeys.afastamentos() });
      queryClient.invalidateQueries({ queryKey: sstKeys.dashboard() });
      queryClient.invalidateQueries({ queryKey: sstKeys.ajudaMedicamento() });
      queryClient.invalidateQueries({ queryKey: sstKeys.estabilidade() });
    },
  });
}

/**
 * Hook para registrar retorno de afastamento
 */
export function useRegistrarRetorno() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data_retorno }: { id: string; data_retorno: string }) =>
      sstService.registrarRetorno(id, data_retorno),
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: sstKeys.afastamento(id) });
      queryClient.invalidateQueries({ queryKey: sstKeys.afastamentos() });
      queryClient.invalidateQueries({ queryKey: sstKeys.dashboard() });
      queryClient.invalidateQueries({ queryKey: sstKeys.estabilidade() });
    },
  });
}

// =============================================================================
// CAT - QUERIES
// =============================================================================

/**
 * Hook para listar CATs
 */
export function useCATs(employee_id?: string) {
  return useQuery({
    queryKey: [...sstKeys.cats(), employee_id],
    queryFn: () => sstService.listCATs(employee_id),
    staleTime: 2 * 60 * 1000,
  });
}

/**
 * Hook para taxa de acidente
 */
export function useTaxaAcidente() {
  return useQuery({
    queryKey: sstKeys.taxaAcidente(),
    queryFn: () => sstService.getTaxaAcidente(),
    staleTime: 10 * 60 * 1000,
  });
}

// =============================================================================
// CAT - MUTATIONS
// =============================================================================

/**
 * Hook para criar CAT
 */
export function useCreateCAT() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: CATCreate) => sstService.createCAT(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: sstKeys.cats() });
      queryClient.invalidateQueries({ queryKey: sstKeys.taxaAcidente() });
      queryClient.invalidateQueries({ queryKey: sstKeys.dashboard() });
    },
  });
}

// =============================================================================
// ESTABILIDADE
// =============================================================================

/**
 * Hook para listar colaboradores em estabilidade
 */
export function useEstabilidade() {
  return useQuery({
    queryKey: sstKeys.estabilidade(),
    queryFn: () => sstService.listEstabilidade(),
    staleTime: 5 * 60 * 1000,
  });
}

// =============================================================================
// AJUDA MEDICAMENTO
// =============================================================================

/**
 * Hook para listar colaboradores com ajuda medicamento
 */
export function useAjudaMedicamento() {
  return useQuery({
    queryKey: sstKeys.ajudaMedicamento(),
    queryFn: () => sstService.listAjudaMedicamento(),
    staleTime: 5 * 60 * 1000,
  });
}
