/**
 * Hooks React Query - EPI (NR-6)
 * Equipamentos de Proteção Individual
 *
 * @module hooks/health-occupational/useEPI
 * @author Conecta PRO Team
 * @date 2026-01-28
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  epiService,
  type EPICreate,
  type EPIUpdate,
  type EPIDeliveryCreate,
  type EPICategory,
  type EPIInventoryUpdate,
} from '@/lib/services/health-occupational/epi';

// =============================================================================
// QUERY KEYS
// =============================================================================

export const epiKeys = {
  all: ['epi'] as const,
  epis: () => [...epiKeys.all, 'catalog'] as const,
  epi: (id: string) => [...epiKeys.epis(), id] as const,
  epiList: (filters?: any) => [...epiKeys.epis(), 'list', filters] as const,
  deliveries: () => [...epiKeys.all, 'deliveries'] as const,
  delivery: (id: string) => [...epiKeys.deliveries(), id] as const,
  employeeRecord: (funcionarioId: string) => [...epiKeys.deliveries(), 'employee', funcionarioId] as const,
  inventory: () => [...epiKeys.all, 'inventory'] as const,
  inventoryItem: (epiId: string) => [...epiKeys.inventory(), epiId] as const,
  categories: () => [...epiKeys.all, 'categories'] as const,
  statistics: () => [...epiKeys.all, 'statistics'] as const,
};

// =============================================================================
// CATÁLOGO - QUERIES
// =============================================================================

/**
 * Hook para buscar EPI por ID
 */
export function useEPI(epiId: string | null) {
  return useQuery({
    queryKey: epiKeys.epi(epiId!),
    queryFn: () => epiService.getEPI(epiId!),
    enabled: !!epiId,
    staleTime: 10 * 60 * 1000, // 10 minutos
  });
}

/**
 * Hook para listar EPIs
 */
export function useEPIList(filters?: {
  categoria?: EPICategory;
  ativo?: boolean;
  page?: number;
  size?: number;
}) {
  return useQuery({
    queryKey: epiKeys.epiList(filters),
    queryFn: () => epiService.listEPIs(filters),
    staleTime: 5 * 60 * 1000, // 5 minutos
  });
}

/**
 * Hook para listar categorias de EPI
 */
export function useEPICategories() {
  return useQuery({
    queryKey: epiKeys.categories(),
    queryFn: () => epiService.getCategories(),
    staleTime: 60 * 60 * 1000, // 1 hora (dados estáticos)
  });
}

// =============================================================================
// CATÁLOGO - MUTATIONS
// =============================================================================

/**
 * Hook para cadastrar EPI
 */
export function useCreateEPI() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: EPICreate) => epiService.createEPI(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: epiKeys.epis() });
      queryClient.invalidateQueries({ queryKey: epiKeys.statistics() });
    },
  });
}

/**
 * Hook para atualizar EPI
 */
export function useUpdateEPI() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ epiId, data }: { epiId: string; data: EPIUpdate }) =>
      epiService.updateEPI(epiId, data),
    onSuccess: (_, { epiId }) => {
      queryClient.invalidateQueries({ queryKey: epiKeys.epi(epiId) });
      queryClient.invalidateQueries({ queryKey: epiKeys.epis() });
    },
  });
}

/**
 * Hook para desativar EPI
 */
export function useDeactivateEPI() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (epiId: string) => epiService.deactivateEPI(epiId),
    onSuccess: (_, epiId) => {
      queryClient.invalidateQueries({ queryKey: epiKeys.epi(epiId) });
      queryClient.invalidateQueries({ queryKey: epiKeys.epis() });
    },
  });
}

// =============================================================================
// ENTREGAS - QUERIES
// =============================================================================

/**
 * Hook para buscar entrega por ID
 */
export function useDelivery(deliveryId: string | null) {
  return useQuery({
    queryKey: epiKeys.delivery(deliveryId!),
    queryFn: () => epiService.getDelivery(deliveryId!),
    enabled: !!deliveryId,
    staleTime: 5 * 60 * 1000,
  });
}

/**
 * Hook para consultar ficha de EPI do funcionário
 */
export function useEmployeeEPIRecord(funcionarioId: string | null) {
  return useQuery({
    queryKey: epiKeys.employeeRecord(funcionarioId!),
    queryFn: () => epiService.getEmployeeRecord(funcionarioId!),
    enabled: !!funcionarioId,
    staleTime: 2 * 60 * 1000, // 2 minutos
  });
}

// =============================================================================
// ENTREGAS - MUTATIONS
// =============================================================================

/**
 * Hook para registrar entrega de EPI
 */
export function useDeliverEPI() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: EPIDeliveryCreate) => epiService.deliverEPI(data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({
        queryKey: epiKeys.employeeRecord(variables.funcionario_id),
      });
      queryClient.invalidateQueries({ queryKey: epiKeys.deliveries() });
      queryClient.invalidateQueries({ queryKey: epiKeys.inventory() });
      queryClient.invalidateQueries({ queryKey: epiKeys.statistics() });
    },
  });
}

/**
 * Hook para registrar devolução de EPI
 */
export function useReturnEPI() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ deliveryId, motivo, condicao }: { deliveryId: string; motivo: string; condicao: string }) =>
      epiService.returnEPI(deliveryId, motivo, condicao),
    onSuccess: (_, { deliveryId }) => {
      queryClient.invalidateQueries({ queryKey: epiKeys.delivery(deliveryId) });
      queryClient.invalidateQueries({ queryKey: epiKeys.deliveries() });
      queryClient.invalidateQueries({ queryKey: epiKeys.inventory() });
    },
  });
}

/**
 * Hook para assinar entrega
 */
export function useSignDelivery() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (deliveryId: string) => epiService.signDelivery(deliveryId),
    onSuccess: (_, deliveryId) => {
      queryClient.invalidateQueries({ queryKey: epiKeys.delivery(deliveryId) });
      queryClient.invalidateQueries({ queryKey: epiKeys.statistics() });
    },
  });
}

// =============================================================================
// ESTOQUE - QUERIES
// =============================================================================

/**
 * Hook para consultar estoque
 */
export function useEPIInventory(filters?: { categoria?: EPICategory; baixo_estoque?: boolean }) {
  return useQuery({
    queryKey: [...epiKeys.inventory(), filters],
    queryFn: () => epiService.getInventory(filters),
    staleTime: 2 * 60 * 1000, // 2 minutos
  });
}

// =============================================================================
// ESTOQUE - MUTATIONS
// =============================================================================

/**
 * Hook para atualizar estoque
 */
export function useUpdateInventory() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ epiId, data }: { epiId: string; data: EPIInventoryUpdate }) =>
      epiService.updateInventory(epiId, data),
    onSuccess: (_, { epiId }) => {
      queryClient.invalidateQueries({ queryKey: epiKeys.inventoryItem(epiId) });
      queryClient.invalidateQueries({ queryKey: epiKeys.inventory() });
    },
  });
}

/**
 * Hook para registrar entrada de estoque
 */
export function useAddToInventory() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ epiId, quantidade, lote }: { epiId: string; quantidade: number; lote?: string }) =>
      epiService.addToInventory(epiId, quantidade, lote),
    onSuccess: (_, { epiId }) => {
      queryClient.invalidateQueries({ queryKey: epiKeys.inventoryItem(epiId) });
      queryClient.invalidateQueries({ queryKey: epiKeys.inventory() });
    },
  });
}

// =============================================================================
// ESTATÍSTICAS
// =============================================================================

/**
 * Hook para estatísticas de EPI
 */
export function useEPIStatistics() {
  return useQuery({
    queryKey: epiKeys.statistics(),
    queryFn: () => epiService.getStatistics(),
    staleTime: 10 * 60 * 1000, // 10 minutos
  });
}

// =============================================================================
// HELPER HOOKS
// =============================================================================

/**
 * Hook auxiliar com todas as funcionalidades de EPI
 */
export function useEPIManagement(funcionarioId?: string | null) {
  const createEPI = useCreateEPI();
  const updateEPI = useUpdateEPI();
  const deactivateEPI = useDeactivateEPI();
  const deliverEPI = useDeliverEPI();
  const returnEPI = useReturnEPI();
  const signDelivery = useSignDelivery();
  const addToInventory = useAddToInventory();

  const epiList = useEPIList();
  const categories = useEPICategories();
  const inventory = useEPIInventory();
  const employeeRecord = useEmployeeEPIRecord(funcionarioId || null);
  const statistics = useEPIStatistics();

  return {
    // Mutations
    createEPI,
    updateEPI,
    deactivateEPI,
    deliverEPI,
    returnEPI,
    signDelivery,
    addToInventory,
    // Queries
    epiList,
    categories,
    inventory,
    employeeRecord,
    statistics,
  };
}
