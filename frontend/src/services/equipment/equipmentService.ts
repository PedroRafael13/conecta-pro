/**
 * Equipment Service
 * Service layer para gestão de equipamentos
 */

import {
  listEquipmentApiV1EquipmentGet,
  createEquipmentApiV1EquipmentPost,
  getStatsApiV1EquipmentStatsGet,
  getInStockApiV1EquipmentInStockGet,
  getNeedingMaintenanceApiV1EquipmentNeedingMaintenanceGet,
  getOfflineApiV1EquipmentOfflineGet,
  getExpiringWarrantyApiV1EquipmentExpiringWarrantyGet,
  getByClientApiV1EquipmentByClientClientIdGet,
  getByContractApiV1EquipmentByContractContractIdGet,
  getEquipmentApiV1EquipmentEquipmentIdGet,
  updateEquipmentApiV1EquipmentEquipmentIdPut,
  deleteEquipmentApiV1EquipmentEquipmentIdDelete,
  getByCodeApiV1EquipmentCodeCodeGet,
  installEquipmentApiV1EquipmentEquipmentIdInstallPost,
  uninstallEquipmentApiV1EquipmentEquipmentIdUninstallPost,
  updateOnlineStatusApiV1EquipmentEquipmentIdOnlineStatusPost,
  bulkUpdateOnlineStatusApiV1EquipmentBulkOnlineStatusPost,
  generateQrCodeApiV1EquipmentEquipmentIdQrCodePost,
  getDepreciationApiV1EquipmentEquipmentIdDepreciationGet,
} from '@/types/generated/equipment/equipment/equipment';
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
  BulkUpdateOnlineStatusApiV1EquipmentBulkOnlineStatusPostParams,
  BulkUpdateOnlineStatusApiV1EquipmentBulkOnlineStatusPost200,
  GenerateQrCodeApiV1EquipmentEquipmentIdQrCodePost200,
  GetDepreciationApiV1EquipmentEquipmentIdDepreciationGet200
} from '@/types/generated/equipment/conectaPROEquipmentManagementAPI.schemas';

export const equipmentService = {
  /**
   * Lista equipamentos com filtros
   */
  list: async (params?: ListEquipmentApiV1EquipmentGetParams): Promise<EquipmentListResponse> => {
    return await listEquipmentApiV1EquipmentGet(params);
  },

  /**
   * Obtém estatísticas de equipamentos
   */
  getStats: async (params?: GetStatsApiV1EquipmentStatsGetParams): Promise<EquipmentStats> => {
    return await getStatsApiV1EquipmentStatsGet(params);
  },

  /**
   * Lista equipamentos em estoque
   */
  getInStock: async (): Promise<EquipmentResponse[]> => {
    return await getInStockApiV1EquipmentInStockGet();
  },

  /**
   * Lista equipamentos que precisam de manutenção
   */
  getNeedingMaintenance: async (): Promise<EquipmentResponse[]> => {
    return await getNeedingMaintenanceApiV1EquipmentNeedingMaintenanceGet();
  },

  /**
   * Lista equipamentos offline
   */
  getOffline: async (): Promise<EquipmentResponse[]> => {
    return await getOfflineApiV1EquipmentOfflineGet();
  },

  /**
   * Lista equipamentos com garantia expirando
   */
  getExpiringWarranty: async (params?: GetExpiringWarrantyApiV1EquipmentExpiringWarrantyGetParams): Promise<EquipmentResponse[]> => {
    return await getExpiringWarrantyApiV1EquipmentExpiringWarrantyGet(params);
  },

  /**
   * Lista equipamentos de um cliente
   */
  getByClient: async (clientId: string): Promise<EquipmentResponse[]> => {
    return await getByClientApiV1EquipmentByClientClientIdGet(clientId);
  },

  /**
   * Lista equipamentos de um contrato
   */
  getByContract: async (contractId: string): Promise<EquipmentResponse[]> => {
    return await getByContractApiV1EquipmentByContractContractIdGet(contractId);
  },

  /**
   * Busca equipamento por código
   */
  getByCode: async (code: string): Promise<EquipmentResponse> => {
    return await getByCodeApiV1EquipmentCodeCodeGet(code);
  },

  /**
   * Busca equipamento por ID
   */
  getById: async (equipmentId: string): Promise<EquipmentResponse> => {
    return await getEquipmentApiV1EquipmentEquipmentIdGet(equipmentId);
  },

  /**
   * Cria novo equipamento
   */
  create: async (data: EquipmentCreate): Promise<EquipmentResponse> => {
    return await createEquipmentApiV1EquipmentPost(data);
  },

  /**
   * Atualiza equipamento
   */
  update: async (equipmentId: string, data: EquipmentUpdate): Promise<EquipmentResponse> => {
    return await updateEquipmentApiV1EquipmentEquipmentIdPut(equipmentId, data);
  },

  /**
   * Remove equipamento (soft delete)
   */
  delete: async (equipmentId: string): Promise<void> => {
    await deleteEquipmentApiV1EquipmentEquipmentIdDelete(equipmentId);
  },

  /**
   * Registra instalação de equipamento
   */
  install: async (
    equipmentId: string,
    params: InstallEquipmentApiV1EquipmentEquipmentIdInstallPostParams
  ): Promise<EquipmentResponse> => {
    return await installEquipmentApiV1EquipmentEquipmentIdInstallPost(equipmentId, params);
  },

  /**
   * Desinstala equipamento
   */
  uninstall: async (equipmentId: string): Promise<EquipmentResponse> => {
    return await uninstallEquipmentApiV1EquipmentEquipmentIdUninstallPost(equipmentId);
  },

  /**
   * Atualiza status online/offline
   */
  updateOnlineStatus: async (
    equipmentId: string,
    params: UpdateOnlineStatusApiV1EquipmentEquipmentIdOnlineStatusPostParams
  ): Promise<EquipmentResponse> => {
    return await updateOnlineStatusApiV1EquipmentEquipmentIdOnlineStatusPost(equipmentId, params);
  },

  /**
   * Atualiza status online/offline em massa
   */
  bulkUpdateOnlineStatus: async (
    equipmentIds: string[],
    params: BulkUpdateOnlineStatusApiV1EquipmentBulkOnlineStatusPostParams
  ): Promise<BulkUpdateOnlineStatusApiV1EquipmentBulkOnlineStatusPost200> => {
    return await bulkUpdateOnlineStatusApiV1EquipmentBulkOnlineStatusPost(equipmentIds, params);
  },

  /**
   * Gera QR Code para equipamento
   */
  generateQrCode: async (equipmentId: string): Promise<GenerateQrCodeApiV1EquipmentEquipmentIdQrCodePost200> => {
    return await generateQrCodeApiV1EquipmentEquipmentIdQrCodePost(equipmentId);
  },

  /**
   * Calcula depreciação do equipamento
   */
  getDepreciation: async (equipmentId: string): Promise<GetDepreciationApiV1EquipmentEquipmentIdDepreciationGet200> => {
    return await getDepreciationApiV1EquipmentEquipmentIdDepreciationGet(equipmentId);
  },
};
