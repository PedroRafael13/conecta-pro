/**
 * Hooks React Query - PPRA/PGR (NR-9)
 * Mapeamento de Riscos Ocupacionais
 *
 * @module hooks/health-occupational/usePPRA
 * @author Conecta PRO Team
 * @date 2026-01-28
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  ppraService,
  type RiskMappingCreate,
  type RiskMappingUpdate,
  type ControlMeasureCreate,
  type ControlMeasureUpdate,
  type ControlMeasureStatus,
} from '@/lib/services/health-occupational/ppra';

// =============================================================================
// QUERY KEYS
// =============================================================================

export const ppraKeys = {
  all: ['ppra'] as const,
  mappings: () => [...ppraKeys.all, 'mappings'] as const,
  mapping: (id: string) => [...ppraKeys.mappings(), id] as const,
  mappingList: (filters?: any) => [...ppraKeys.mappings(), 'list', filters] as const,
  sectorRisks: (setor: string) => [...ppraKeys.all, 'risks', 'sector', setor] as const,
  functionRisks: (funcao: string) => [...ppraKeys.all, 'risks', 'function', funcao] as const,
  measures: () => [...ppraKeys.all, 'measures'] as const,
  measure: (id: string) => [...ppraKeys.measures(), id] as const,
  mappingMeasures: (mappingId: string, status?: ControlMeasureStatus) =>
    [...ppraKeys.measures(), 'mapping', mappingId, status] as const,
  categories: () => [...ppraKeys.all, 'categories'] as const,
  statistics: () => [...ppraKeys.all, 'statistics'] as const,
};

// =============================================================================
// MAPEAMENTO - QUERIES
// =============================================================================

/**
 * Hook para buscar mapeamento por ID
 */
export function useRiskMapping(mappingId: string | null) {
  return useQuery({
    queryKey: ppraKeys.mapping(mappingId!),
    queryFn: () => ppraService.getMapping(mappingId!),
    enabled: !!mappingId,
    staleTime: 10 * 60 * 1000, // 10 minutos
  });
}

/**
 * Hook para listar mapeamentos
 */
export function useRiskMappings(filters?: {
  setor?: string;
  ativo?: boolean;
  page?: number;
  size?: number;
}) {
  return useQuery({
    queryKey: ppraKeys.mappingList(filters),
    queryFn: () => ppraService.listMappings(filters),
    staleTime: 5 * 60 * 1000, // 5 minutos
  });
}

/**
 * Hook para consultar riscos de um setor
 */
export function useSectorRisks(setor: string | null) {
  return useQuery({
    queryKey: ppraKeys.sectorRisks(setor!),
    queryFn: () => ppraService.getSectorRisks(setor!),
    enabled: !!setor,
    staleTime: 10 * 60 * 1000, // 10 minutos
  });
}

/**
 * Hook para consultar riscos de uma função
 */
export function useFunctionRisks(funcao: string | null) {
  return useQuery({
    queryKey: ppraKeys.functionRisks(funcao!),
    queryFn: () => ppraService.getFunctionRisks(funcao!),
    enabled: !!funcao,
    staleTime: 10 * 60 * 1000, // 10 minutos
  });
}

/**
 * Hook para listar categorias de risco
 */
export function useRiskCategories() {
  return useQuery({
    queryKey: ppraKeys.categories(),
    queryFn: () => ppraService.getRiskCategories(),
    staleTime: 60 * 60 * 1000, // 1 hora (dados estáticos)
  });
}

// =============================================================================
// MAPEAMENTO - MUTATIONS
// =============================================================================

/**
 * Hook para criar mapeamento de riscos
 */
export function useCreateRiskMapping() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: RiskMappingCreate) => ppraService.createMapping(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ppraKeys.mappings() });
      queryClient.invalidateQueries({ queryKey: ppraKeys.statistics() });
    },
  });
}

/**
 * Hook para atualizar mapeamento
 */
export function useUpdateRiskMapping() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ mappingId, data }: { mappingId: string; data: RiskMappingUpdate }) =>
      ppraService.updateMapping(mappingId, data),
    onSuccess: (_, { mappingId }) => {
      queryClient.invalidateQueries({ queryKey: ppraKeys.mapping(mappingId) });
      queryClient.invalidateQueries({ queryKey: ppraKeys.mappings() });
    },
  });
}

// =============================================================================
// MEDIDAS DE CONTROLE - QUERIES
// =============================================================================

/**
 * Hook para listar medidas de controle de um mapeamento
 */
export function useControlMeasures(mappingId: string | null, status?: ControlMeasureStatus) {
  return useQuery({
    queryKey: ppraKeys.mappingMeasures(mappingId!, status),
    queryFn: () => ppraService.listControlMeasures(mappingId!, status),
    enabled: !!mappingId,
    staleTime: 5 * 60 * 1000, // 5 minutos
  });
}

// =============================================================================
// MEDIDAS DE CONTROLE - MUTATIONS
// =============================================================================

/**
 * Hook para adicionar medida de controle
 */
export function useAddControlMeasure() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: ControlMeasureCreate) => ppraService.addControlMeasure(data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({
        queryKey: ppraKeys.mappingMeasures(variables.mapeamento_id),
      });
      queryClient.invalidateQueries({
        queryKey: ppraKeys.mapping(variables.mapeamento_id),
      });
    },
  });
}

/**
 * Hook para atualizar medida de controle
 */
export function useUpdateControlMeasure() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ measureId, data }: { measureId: string; data: ControlMeasureUpdate }) =>
      ppraService.updateControlMeasure(measureId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ppraKeys.measures() });
    },
  });
}

// =============================================================================
// ESTATÍSTICAS
// =============================================================================

/**
 * Hook para estatísticas do PPRA
 */
export function usePPRAStatistics() {
  return useQuery({
    queryKey: ppraKeys.statistics(),
    queryFn: () => ppraService.getStatistics(),
    staleTime: 10 * 60 * 1000, // 10 minutos
  });
}

// =============================================================================
// HELPER HOOKS
// =============================================================================

/**
 * Hook auxiliar com todas as funcionalidades do PPRA
 */
export function usePPRA(setor?: string | null, funcao?: string | null) {
  const createMapping = useCreateRiskMapping();
  const updateMapping = useUpdateRiskMapping();
  const addControlMeasure = useAddControlMeasure();
  const updateControlMeasure = useUpdateControlMeasure();

  const mappings = useRiskMappings();
  const sectorRisks = useSectorRisks(setor || null);
  const functionRisks = useFunctionRisks(funcao || null);
  const categories = useRiskCategories();
  const statistics = usePPRAStatistics();

  return {
    // Mutations
    createMapping,
    updateMapping,
    addControlMeasure,
    updateControlMeasure,
    // Queries
    mappings,
    sectorRisks,
    functionRisks,
    categories,
    statistics,
  };
}
