/**
 * Comodato Service
 * Service layer para gestão de comodatos
 */

import { getEquipmentComodato } from '@/types/generated/equipment/equipment-comodato/equipment-comodato';
import type {
  ComodatoCreate,
  ComodatoUpdate,
  ComodatoResponse,
  ComodatoListResponse,
  ListComodatosApiV1ComodatosGetParams,
  GetStatsApiV1ComodatosStatsGetParams,
  GetStatsApiV1ComodatosStatsGet200,
  GetActiveApiV1ComodatosActiveGetParams,
  GetExpiringApiV1ComodatosExpiringGetParams,
  SignComodatoApiV1ComodatosComodatoIdSignPostParams,
  DeliverComodatoApiV1ComodatosComodatoIdDeliverPostParams,
  BodyDeliverComodatoApiV1ComodatosComodatoIdDeliverPost,
  ScheduleReturnApiV1ComodatosComodatoIdScheduleReturnPostParams,
  RegisterReturnApiV1ComodatosComodatoIdReturnPostParams,
  BodyRegisterReturnApiV1ComodatosComodatoIdReturnPost,
  RegisterDamageApiV1ComodatosComodatoIdDamagePostParams,
  TerminateComodatoApiV1ComodatosComodatoIdTerminatePostParams,
  TransferComodatoApiV1ComodatosComodatoIdTransferPostParams,
  GenerateContractPdfApiV1ComodatosComodatoIdContractPdfPost200,
  GenerateDeliveryTermApiV1ComodatosComodatoIdDeliveryTermPost200,
  GenerateReturnTermApiV1ComodatosComodatoIdReturnTermPost200
} from '@/types/generated/equipment/conectaPROEquipmentManagementAPI.schemas';

const comodatoApi = getEquipmentComodato();

export const comodatoService = {
  /**
   * Lista comodatos com filtros
   */
  list: async (params?: ListComodatosApiV1ComodatosGetParams): Promise<ComodatoListResponse> => {
    return await comodatoApi.listComodatosApiV1ComodatosGet(params);
  },

  /**
   * Obtém estatísticas de comodatos
   */
  getStats: async (params?: GetStatsApiV1ComodatosStatsGetParams): Promise<GetStatsApiV1ComodatosStatsGet200> => {
    return await comodatoApi.getStatsApiV1ComodatosStatsGet(params);
  },

  /**
   * Lista comodatos ativos
   */
  getActive: async (params?: GetActiveApiV1ComodatosActiveGetParams): Promise<ComodatoResponse[]> => {
    return await comodatoApi.getActiveApiV1ComodatosActiveGet(params);
  },

  /**
   * Lista comodatos aguardando assinatura
   */
  getPendingSignature: async (): Promise<ComodatoResponse[]> => {
    return await comodatoApi.getPendingSignatureApiV1ComodatosPendingSignatureGet();
  },

  /**
   * Lista comodatos aguardando entrega
   */
  getPendingDelivery: async (): Promise<ComodatoResponse[]> => {
    return await comodatoApi.getPendingDeliveryApiV1ComodatosPendingDeliveryGet();
  },

  /**
   * Lista comodatos com devolução pendente
   */
  getPendingReturn: async (): Promise<ComodatoResponse[]> => {
    return await comodatoApi.getPendingReturnApiV1ComodatosPendingReturnGet();
  },

  /**
   * Lista comodatos expirando
   */
  getExpiring: async (params?: GetExpiringApiV1ComodatosExpiringGetParams): Promise<ComodatoResponse[]> => {
    return await comodatoApi.getExpiringApiV1ComodatosExpiringGet(params);
  },

  /**
   * Lista comodatos expirados não devolvidos
   */
  getExpired: async (): Promise<ComodatoResponse[]> => {
    return await comodatoApi.getExpiredApiV1ComodatosExpiredGet();
  },

  /**
   * Lista comodatos de um cliente
   */
  getByClient: async (clientId: string): Promise<ComodatoResponse[]> => {
    return await comodatoApi.getByClientApiV1ComodatosByClientClientIdGet(clientId);
  },

  /**
   * Busca comodato por código
   */
  getByCode: async (code: string): Promise<ComodatoResponse> => {
    return await comodatoApi.getByCodeApiV1ComodatosCodeCodeGet(code);
  },

  /**
   * Busca comodato por ID
   */
  getById: async (comodatoId: string): Promise<ComodatoResponse> => {
    return await comodatoApi.getComodatoApiV1ComodatosComodatoIdGet(comodatoId);
  },

  /**
   * Cria novo comodato
   */
  create: async (data: ComodatoCreate): Promise<ComodatoResponse> => {
    return await comodatoApi.createComodatoApiV1ComodatosPost(data);
  },

  /**
   * Atualiza comodato
   */
  update: async (comodatoId: string, data: ComodatoUpdate): Promise<ComodatoResponse> => {
    return await comodatoApi.updateComodatoApiV1ComodatosComodatoIdPut(comodatoId, data);
  },

  /**
   * Remove comodato (soft delete)
   */
  delete: async (comodatoId: string): Promise<void> => {
    await comodatoApi.deleteComodatoApiV1ComodatosComodatoIdDelete(comodatoId);
  },

  /**
   * Registra assinatura do contrato
   */
  sign: async (
    comodatoId: string,
    params: SignComodatoApiV1ComodatosComodatoIdSignPostParams
  ): Promise<ComodatoResponse> => {
    return await comodatoApi.signComodatoApiV1ComodatosComodatoIdSignPost(comodatoId, params);
  },

  /**
   * Registra entrega do equipamento
   */
  deliver: async (
    comodatoId: string,
    params: DeliverComodatoApiV1ComodatosComodatoIdDeliverPostParams,
    body?: BodyDeliverComodatoApiV1ComodatosComodatoIdDeliverPost
  ): Promise<ComodatoResponse> => {
    return await comodatoApi.deliverComodatoApiV1ComodatosComodatoIdDeliverPost(
      comodatoId,
      body ?? { photos: null },
      params
    );
  },

  /**
   * Solicita devolução
   */
  requestReturn: async (comodatoId: string): Promise<ComodatoResponse> => {
    return await comodatoApi.requestReturnApiV1ComodatosComodatoIdRequestReturnPost(comodatoId);
  },

  /**
   * Agenda devolução
   */
  scheduleReturn: async (
    comodatoId: string,
    params: ScheduleReturnApiV1ComodatosComodatoIdScheduleReturnPostParams
  ): Promise<ComodatoResponse> => {
    return await comodatoApi.scheduleReturnApiV1ComodatosComodatoIdScheduleReturnPost(comodatoId, params);
  },

  /**
   * Registra devolução
   */
  registerReturn: async (
    comodatoId: string,
    params: RegisterReturnApiV1ComodatosComodatoIdReturnPostParams,
    body?: BodyRegisterReturnApiV1ComodatosComodatoIdReturnPost
  ): Promise<ComodatoResponse> => {
    return await comodatoApi.registerReturnApiV1ComodatosComodatoIdReturnPost(
      comodatoId,
      body ?? { photos: null },
      params
    );
  },

  /**
   * Registra dano no equipamento
   */
  registerDamage: async (
    comodatoId: string,
    params: RegisterDamageApiV1ComodatosComodatoIdDamagePostParams
  ): Promise<ComodatoResponse> => {
    return await comodatoApi.registerDamageApiV1ComodatosComodatoIdDamagePost(comodatoId, params);
  },

  /**
   * Marca equipamento como perdido
   */
  markAsLost: async (comodatoId: string): Promise<ComodatoResponse> => {
    return await comodatoApi.markAsLostApiV1ComodatosComodatoIdMarkLostPost(comodatoId);
  },

  /**
   * Encerra contrato de comodato
   */
  terminate: async (
    comodatoId: string,
    params: TerminateComodatoApiV1ComodatosComodatoIdTerminatePostParams
  ): Promise<ComodatoResponse> => {
    return await comodatoApi.terminateComodatoApiV1ComodatosComodatoIdTerminatePost(comodatoId, params);
  },

  /**
   * Transfere comodato para outro cliente
   */
  transfer: async (
    comodatoId: string,
    params: TransferComodatoApiV1ComodatosComodatoIdTransferPostParams
  ): Promise<ComodatoResponse> => {
    return await comodatoApi.transferComodatoApiV1ComodatosComodatoIdTransferPost(comodatoId, params);
  },

  /**
   * Gera PDF do contrato
   */
  generateContractPdf: async (comodatoId: string): Promise<GenerateContractPdfApiV1ComodatosComodatoIdContractPdfPost200> => {
    return await comodatoApi.generateContractPdfApiV1ComodatosComodatoIdContractPdfPost(comodatoId);
  },

  /**
   * Gera termo de entrega
   */
  generateDeliveryTerm: async (comodatoId: string): Promise<GenerateDeliveryTermApiV1ComodatosComodatoIdDeliveryTermPost200> => {
    return await comodatoApi.generateDeliveryTermApiV1ComodatosComodatoIdDeliveryTermPost(comodatoId);
  },

  /**
   * Gera termo de devolução
   */
  generateReturnTerm: async (comodatoId: string): Promise<GenerateReturnTermApiV1ComodatosComodatoIdReturnTermPost200> => {
    return await comodatoApi.generateReturnTermApiV1ComodatosComodatoIdReturnTermPost(comodatoId);
  },
};
