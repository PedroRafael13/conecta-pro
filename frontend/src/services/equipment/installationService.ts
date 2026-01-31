/**
 * Installation Service
 * Service layer para gestão de instalações
 */

import { getEquipmentInstalacoes } from '@/types/generated/equipment/equipment-instalacoes/equipment-instalacoes';
import type {
  InstallationCreate,
  InstallationUpdate,
  InstallationResponse,
  InstallationListResponse,
  ListInstallationsApiV1InstallationsGetParams,
  GetStatsApiV1InstallationsStatsGetParams,
  GetStatsApiV1InstallationsStatsGet200,
  GetByTechnicianApiV1InstallationsByTechnicianTechnicianIdGetParams,
  GetTechnicianScheduleApiV1InstallationsTechnicianScheduleTechnicianIdGetParams,
  CompleteInstallationApiV1InstallationsInstallationIdCompletePostParams,
  CancelInstallationApiV1InstallationsInstallationIdCancelPostParams,
  RescheduleInstallationApiV1InstallationsInstallationIdReschedulePostParams,
  AcceptInstallationApiV1InstallationsInstallationIdAcceptPostParams,
  AddPhotoApiV1InstallationsInstallationIdPhotoPostParams,
  AssignTechnicianApiV1InstallationsInstallationIdAssignTechnicianPostParams
} from '@/types/generated/equipment/conectaPROEquipmentManagementAPI.schemas';

const installationApi = getEquipmentInstalacoes();

export const installationService = {
  /**
   * Lista instalações com filtros
   */
  list: async (params?: ListInstallationsApiV1InstallationsGetParams): Promise<InstallationListResponse> => {
    return await installationApi.listInstallationsApiV1InstallationsGet(params);
  },

  /**
   * Lista instalações atrasadas
   */
  getOverdue: async (): Promise<InstallationResponse[]> => {
    return await installationApi.getOverdueApiV1InstallationsOverdueGet();
  },

  /**
   * Lista instalações aguardando aceite
   */
  getPendingAcceptance: async (): Promise<InstallationResponse[]> => {
    return await installationApi.getPendingAcceptanceApiV1InstallationsPendingAcceptanceGet();
  },

  /**
   * Lista instalações agendadas para uma data
   */
  getByDate: async (date: string): Promise<InstallationResponse[]> => {
    return await installationApi.getByDateApiV1InstallationsByDateDateGet(date);
  },

  /**
   * Lista instalações de um cliente
   */
  getByClient: async (clientId: string): Promise<InstallationResponse[]> => {
    return await installationApi.getByClientApiV1InstallationsByClientClientIdGet(clientId);
  },

  /**
   * Lista instalações de um técnico
   */
  getByTechnician: async (
    technicianId: string,
    params?: GetByTechnicianApiV1InstallationsByTechnicianTechnicianIdGetParams
  ): Promise<InstallationResponse[]> => {
    return await installationApi.getByTechnicianApiV1InstallationsByTechnicianTechnicianIdGet(technicianId, params);
  },

  /**
   * Obtém agenda do técnico para uma data
   */
  getTechnicianSchedule: async (
    technicianId: string,
    params: GetTechnicianScheduleApiV1InstallationsTechnicianScheduleTechnicianIdGetParams
  ): Promise<InstallationResponse[]> => {
    return await installationApi.getTechnicianScheduleApiV1InstallationsTechnicianScheduleTechnicianIdGet(technicianId, params);
  },

  /**
   * Obtém estatísticas de instalações
   */
  getStats: async (params: GetStatsApiV1InstallationsStatsGetParams): Promise<GetStatsApiV1InstallationsStatsGet200> => {
    return await installationApi.getStatsApiV1InstallationsStatsGet(params);
  },

  /**
   * Busca instalação por código
   */
  getByCode: async (code: string): Promise<InstallationResponse> => {
    return await installationApi.getByCodeApiV1InstallationsCodeCodeGet(code);
  },

  /**
   * Busca instalação por ID
   */
  getById: async (installationId: string): Promise<InstallationResponse> => {
    return await installationApi.getInstallationApiV1InstallationsInstallationIdGet(installationId);
  },

  /**
   * Cria nova instalação
   */
  create: async (data: InstallationCreate): Promise<InstallationResponse> => {
    return await installationApi.createInstallationApiV1InstallationsPost(data);
  },

  /**
   * Atualiza instalação
   */
  update: async (installationId: string, data: InstallationUpdate): Promise<InstallationResponse> => {
    return await installationApi.updateInstallationApiV1InstallationsInstallationIdPut(installationId, data);
  },

  /**
   * Remove instalação (soft delete)
   */
  delete: async (installationId: string): Promise<void> => {
    await installationApi.deleteInstallationApiV1InstallationsInstallationIdDelete(installationId);
  },

  /**
   * Inicia instalação
   */
  start: async (installationId: string): Promise<InstallationResponse> => {
    return await installationApi.startInstallationApiV1InstallationsInstallationIdStartPost(installationId);
  },

  /**
   * Conclui instalação
   */
  complete: async (
    installationId: string,
    params?: CompleteInstallationApiV1InstallationsInstallationIdCompletePostParams
  ): Promise<InstallationResponse> => {
    return await installationApi.completeInstallationApiV1InstallationsInstallationIdCompletePost(installationId, params);
  },

  /**
   * Cancela instalação
   */
  cancel: async (
    installationId: string,
    params: CancelInstallationApiV1InstallationsInstallationIdCancelPostParams
  ): Promise<InstallationResponse> => {
    return await installationApi.cancelInstallationApiV1InstallationsInstallationIdCancelPost(installationId, params);
  },

  /**
   * Reagenda instalação
   */
  reschedule: async (
    installationId: string,
    params: RescheduleInstallationApiV1InstallationsInstallationIdReschedulePostParams
  ): Promise<InstallationResponse> => {
    return await installationApi.rescheduleInstallationApiV1InstallationsInstallationIdReschedulePost(installationId, params);
  },

  /**
   * Registra aceite do cliente
   */
  accept: async (
    installationId: string,
    params: AcceptInstallationApiV1InstallationsInstallationIdAcceptPostParams
  ): Promise<InstallationResponse> => {
    return await installationApi.acceptInstallationApiV1InstallationsInstallationIdAcceptPost(installationId, params);
  },

  /**
   * Adiciona foto à instalação
   */
  addPhoto: async (
    installationId: string,
    params: AddPhotoApiV1InstallationsInstallationIdPhotoPostParams
  ): Promise<InstallationResponse> => {
    return await installationApi.addPhotoApiV1InstallationsInstallationIdPhotoPost(installationId, params);
  },

  /**
   * Atribui técnico à instalação
   */
  assignTechnician: async (
    installationId: string,
    params: AssignTechnicianApiV1InstallationsInstallationIdAssignTechnicianPostParams
  ): Promise<InstallationResponse> => {
    return await installationApi.assignTechnicianApiV1InstallationsInstallationIdAssignTechnicianPost(installationId, params);
  },
};
