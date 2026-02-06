/**
 * Equipment Hooks
 * React Query hooks para gestão de equipamentos
 */

import { useMutation, useQuery, useQueryClient, type UseQueryOptions } from '@tanstack/react-query';
import { equipmentService } from '@/services/equipment/equipmentService';
import type {
  EquipmentCreate,
  EquipmentUpdate,
  EquipmentResponse,
  EquipmentListResponse,
  EquipmentStats,
  ListEquipmentApiV1EquipmentGetParams,
  GetStatsApiV1EquipmentStatsGetParams,
  GetExpiringWarrantyApiV1EquipmentExpiringWarrantyGetParams,
  InstallEquipmentApiV1EquipmentEquipmentIdInstallPostParams,
  UpdateOnlineStatusApiV1EquipmentEquipmentIdOnlineStatusPostParams,
  BulkUpdateOnlineStatusApiV1EquipmentBulkOnlineStatusPostParams
} from '@/types/generated/equipment/conectaPROEquipmentManagementAPI.schemas';

const EQUIPMENT_KEYS = {
  all: ['equipment'] as const,
  lists: () => [...EQUIPMENT_KEYS.all, 'list'] as const,
  list: (params?: ListEquipmentApiV1EquipmentGetParams) => [...EQUIPMENT_KEYS.lists(), params] as const,
  stats: (params?: GetStatsApiV1EquipmentStatsGetParams) => [...EQUIPMENT_KEYS.all, 'stats', params] as const,
  inStock: () => [...EQUIPMENT_KEYS.all, 'in-stock'] as const,
  needingMaintenance: () => [...EQUIPMENT_KEYS.all, 'needing-maintenance'] as const,
  offline: () => [...EQUIPMENT_KEYS.all, 'offline'] as const,
  expiringWarranty: (params?: GetExpiringWarrantyApiV1EquipmentExpiringWarrantyGetParams) => [...EQUIPMENT_KEYS.all, 'expiring-warranty', params] as const,
  byClient: (clientId: string) => [...EQUIPMENT_KEYS.all, 'by-client', clientId] as const,
  byContract: (contractId: string) => [...EQUIPMENT_KEYS.all, 'by-contract', contractId] as const,
  byCode: (code: string) => [...EQUIPMENT_KEYS.all, 'by-code', code] as const,
  detail: (id: string) => [...EQUIPMENT_KEYS.all, 'detail', id] as const,
  depreciation: (id: string) => [...EQUIPMENT_KEYS.all, 'depreciation', id] as const,
};

/**
 * Hook para listar equipamentos
 */
export const useEquipmentList = (
  params?: ListEquipmentApiV1EquipmentGetParams,
  options?: UseQueryOptions<EquipmentListResponse>
) => {
  return useQuery({
    queryKey: EQUIPMENT_KEYS.list(params),
    queryFn: () => equipmentService.list(params),
    ...options,
  });
};

/**
 * Hook para obter estatísticas de equipamentos
 */
export const useEquipmentStats = (
  params?: GetStatsApiV1EquipmentStatsGetParams,
  options?: UseQueryOptions<EquipmentStats>
) => {
  return useQuery({
    queryKey: EQUIPMENT_KEYS.stats(params),
    queryFn: () => equipmentService.getStats(params),
    ...options,
  });
};

/**
 * Hook para listar equipamentos em estoque
 */
export const useEquipmentInStock = (options?: UseQueryOptions<EquipmentResponse[]>) => {
  return useQuery({
    queryKey: EQUIPMENT_KEYS.inStock(),
    queryFn: () => equipmentService.getInStock(),
    ...options,
  });
};

/**
 * Hook para listar equipamentos que precisam de manutenção
 */
export const useEquipmentNeedingMaintenance = (options?: UseQueryOptions<EquipmentResponse[]>) => {
  return useQuery({
    queryKey: EQUIPMENT_KEYS.needingMaintenance(),
    queryFn: () => equipmentService.getNeedingMaintenance(),
    ...options,
  });
};

/**
 * Hook para listar equipamentos offline
 */
export const useEquipmentOffline = (options?: UseQueryOptions<EquipmentResponse[]>) => {
  return useQuery({
    queryKey: EQUIPMENT_KEYS.offline(),
    queryFn: () => equipmentService.getOffline(),
    ...options,
  });
};

/**
 * Hook para listar equipamentos com garantia expirando
 */
export const useEquipmentExpiringWarranty = (
  params?: GetExpiringWarrantyApiV1EquipmentExpiringWarrantyGetParams,
  options?: UseQueryOptions<EquipmentResponse[]>
) => {
  return useQuery({
    queryKey: EQUIPMENT_KEYS.expiringWarranty(params),
    queryFn: () => equipmentService.getExpiringWarranty(params),
    ...options,
  });
};

/**
 * Hook para listar equipamentos de um cliente
 */
export const useEquipmentByClient = (
  clientId: string,
  options?: UseQueryOptions<EquipmentResponse[]>
) => {
  return useQuery({
    queryKey: EQUIPMENT_KEYS.byClient(clientId),
    queryFn: () => equipmentService.getByClient(clientId),
    enabled: !!clientId,
    ...options,
  });
};

/**
 * Hook para listar equipamentos de um contrato
 */
export const useEquipmentByContract = (
  contractId: string,
  options?: UseQueryOptions<EquipmentResponse[]>
) => {
  return useQuery({
    queryKey: EQUIPMENT_KEYS.byContract(contractId),
    queryFn: () => equipmentService.getByContract(contractId),
    enabled: !!contractId,
    ...options,
  });
};

/**
 * Hook para buscar equipamento por código
 */
export const useEquipmentByCode = (
  code: string,
  options?: UseQueryOptions<EquipmentResponse>
) => {
  return useQuery({
    queryKey: EQUIPMENT_KEYS.byCode(code),
    queryFn: () => equipmentService.getByCode(code),
    enabled: !!code,
    ...options,
  });
};

/**
 * Hook para buscar equipamento por ID
 */
export const useEquipment = (
  equipmentId: string,
  options?: UseQueryOptions<EquipmentResponse>
) => {
  return useQuery({
    queryKey: EQUIPMENT_KEYS.detail(equipmentId),
    queryFn: () => equipmentService.getById(equipmentId),
    enabled: !!equipmentId,
    ...options,
  });
};

/**
 * Hook para obter depreciação do equipamento
 */
export const useEquipmentDepreciation = (
  equipmentId: string,
  options?: UseQueryOptions<any>
) => {
  return useQuery({
    queryKey: EQUIPMENT_KEYS.depreciation(equipmentId),
    queryFn: () => equipmentService.getDepreciation(equipmentId),
    enabled: !!equipmentId,
    ...options,
  });
};

/**
 * Hook para criar equipamento
 */
export const useCreateEquipment = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: EquipmentCreate) => equipmentService.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: EQUIPMENT_KEYS.lists() });
      queryClient.invalidateQueries({ queryKey: EQUIPMENT_KEYS.stats() });
      queryClient.invalidateQueries({ queryKey: EQUIPMENT_KEYS.inStock() });
    },
  });
};

/**
 * Hook para atualizar equipamento
 */
export const useUpdateEquipment = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ equipmentId, data }: { equipmentId: string; data: EquipmentUpdate }) =>
      equipmentService.update(equipmentId, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: EQUIPMENT_KEYS.detail(variables.equipmentId) });
      queryClient.invalidateQueries({ queryKey: EQUIPMENT_KEYS.lists() });
      queryClient.invalidateQueries({ queryKey: EQUIPMENT_KEYS.stats() });
    },
  });
};

/**
 * Hook para deletar equipamento
 */
export const useDeleteEquipment = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (equipmentId: string) => equipmentService.delete(equipmentId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: EQUIPMENT_KEYS.lists() });
      queryClient.invalidateQueries({ queryKey: EQUIPMENT_KEYS.stats() });
      queryClient.invalidateQueries({ queryKey: EQUIPMENT_KEYS.inStock() });
    },
  });
};

/**
 * Hook para instalar equipamento
 */
export const useInstallEquipment = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      equipmentId,
      params,
    }: {
      equipmentId: string;
      params: InstallEquipmentApiV1EquipmentEquipmentIdInstallPostParams;
    }) => equipmentService.install(equipmentId, params),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: EQUIPMENT_KEYS.detail(variables.equipmentId) });
      queryClient.invalidateQueries({ queryKey: EQUIPMENT_KEYS.lists() });
      queryClient.invalidateQueries({ queryKey: EQUIPMENT_KEYS.stats() });
      queryClient.invalidateQueries({ queryKey: EQUIPMENT_KEYS.inStock() });
    },
  });
};

/**
 * Hook para desinstalar equipamento
 */
export const useUninstallEquipment = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (equipmentId: string) => equipmentService.uninstall(equipmentId),
    onSuccess: (_, equipmentId) => {
      queryClient.invalidateQueries({ queryKey: EQUIPMENT_KEYS.detail(equipmentId) });
      queryClient.invalidateQueries({ queryKey: EQUIPMENT_KEYS.lists() });
      queryClient.invalidateQueries({ queryKey: EQUIPMENT_KEYS.stats() });
      queryClient.invalidateQueries({ queryKey: EQUIPMENT_KEYS.inStock() });
    },
  });
};

/**
 * Hook para atualizar status online
 */
export const useUpdateEquipmentOnlineStatus = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      equipmentId,
      params,
    }: {
      equipmentId: string;
      params: UpdateOnlineStatusApiV1EquipmentEquipmentIdOnlineStatusPostParams;
    }) => equipmentService.updateOnlineStatus(equipmentId, params),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: EQUIPMENT_KEYS.detail(variables.equipmentId) });
      queryClient.invalidateQueries({ queryKey: EQUIPMENT_KEYS.lists() });
      queryClient.invalidateQueries({ queryKey: EQUIPMENT_KEYS.offline() });
    },
  });
};

/**
 * Hook para atualizar status online em massa
 */
export const useBulkUpdateEquipmentOnlineStatus = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      equipmentIds,
      params,
    }: {
      equipmentIds: string[];
      params: BulkUpdateOnlineStatusApiV1EquipmentBulkOnlineStatusPostParams;
    }) => equipmentService.bulkUpdateOnlineStatus(equipmentIds, params),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: EQUIPMENT_KEYS.lists() });
      queryClient.invalidateQueries({ queryKey: EQUIPMENT_KEYS.offline() });
    },
  });
};

/**
 * Hook para gerar QR Code
 */
export const useGenerateEquipmentQrCode = () => {
  return useMutation({
    mutationFn: (equipmentId: string) => equipmentService.generateQrCode(equipmentId),
  });
};
