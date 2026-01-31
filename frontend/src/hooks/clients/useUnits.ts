/**
 * Hooks React Query - Unit Management
 * Gestão de Unidades
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { unitService } from '@/services/clients';
import type {
  UnitCreate,
  UnitUpdate,
} from '@/types/generated/clients/conectaPROMóduloCLIENTS.schemas';

/**
 * Query keys para cache
 */
export const unitKeys = {
  all: ['units'] as const,
  lists: () => [...unitKeys.all, 'list'] as const,
  list: (condominiumId: string, filters?: any) =>
    [...unitKeys.lists(), condominiumId, filters] as const,
  details: () => [...unitKeys.all, 'detail'] as const,
  detail: (id: string) => [...unitKeys.details(), id] as const,
  stats: (condominiumId: string) =>
    [...unitKeys.all, 'stats', condominiumId] as const,
};

/**
 * Hook para listar unidades do condomínio
 */
export function useUnits(
  condominiumId: string,
  params?: {
    skip?: number;
    limit?: number;
  },
  enabled = true
) {
  return useQuery({
    queryKey: unitKeys.list(condominiumId, params),
    queryFn: () => unitService.list(condominiumId, params),
    enabled: enabled && !!condominiumId,
  });
}

/**
 * Hook para obter unidade por ID
 */
export function useUnit(unitId: string, enabled = true) {
  return useQuery({
    queryKey: unitKeys.detail(unitId),
    queryFn: () => unitService.getById(unitId),
    enabled: enabled && !!unitId,
  });
}

/**
 * Hook para obter estatísticas de unidades
 */
export function useUnitStats(condominiumId: string, enabled = true) {
  return useQuery({
    queryKey: unitKeys.stats(condominiumId),
    queryFn: () => unitService.getStats(condominiumId),
    enabled: enabled && !!condominiumId,
  });
}

/**
 * Hook para criar unidade
 */
export function useCreateUnit() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      condominiumId,
      data,
    }: {
      condominiumId: string;
      data: UnitCreate;
    }) => unitService.create(condominiumId, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({
        queryKey: unitKeys.list(variables.condominiumId),
      });
      queryClient.invalidateQueries({
        queryKey: unitKeys.stats(variables.condominiumId),
      });
    },
  });
}

/**
 * Hook para atualizar unidade
 */
export function useUpdateUnit() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ unitId, data }: { unitId: string; data: UnitUpdate }) =>
      unitService.update(unitId, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: unitKeys.detail(variables.unitId) });
      queryClient.invalidateQueries({ queryKey: unitKeys.lists() });
    },
  });
}

/**
 * Hook para deletar unidade
 */
export function useDeleteUnit() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (unitId: string) => unitService.delete(unitId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: unitKeys.lists() });
    },
  });
}

/**
 * Hook para definir proprietário
 */
export function useSetUnitOwner() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      unitId,
      params,
    }: {
      unitId: string;
      params: {
        name: string;
        document?: string;
        phone?: string;
        email?: string;
      };
    }) => unitService.setOwner(unitId, params),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: unitKeys.detail(variables.unitId) });
    },
  });
}

/**
 * Hook para definir morador/inquilino
 */
export function useSetUnitResident() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      unitId,
      params,
    }: {
      unitId: string;
      params: {
        name: string;
        document?: string;
        phone?: string;
        email?: string;
        is_tenant?: boolean;
      };
    }) => unitService.setResident(unitId, params),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: unitKeys.detail(variables.unitId) });
    },
  });
}

/**
 * Hook para remover morador
 */
export function useClearUnitResident() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (unitId: string) => unitService.clearResident(unitId),
    onSuccess: (_, unitId) => {
      queryClient.invalidateQueries({ queryKey: unitKeys.detail(unitId) });
    },
  });
}
