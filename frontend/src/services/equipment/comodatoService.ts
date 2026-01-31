/**
 * Comodato Service
 * Service layer para gestão de comodatos
 */

import {
  listComodatosApiV1ComodatosGet,
  createComodatoApiV1ComodatosPost,
  getStatsApiV1ComodatosStatsGet,
  getActiveApiV1ComodatosActiveGet,
  getPendingDeliveryApiV1ComodatosPendingDeliveryGet,
  getPendingSignatureApiV1ComodatosPendingSignatureGet,
  getPendingReturnApiV1ComodatosPendingReturnGet,
  getExpiringApiV1ComodatosExpiringGet,
  getExpiredApiV1ComodatosExpiredGet,
  getByClientApiV1ComodatosByClientClientIdGet,
  getComodatoApiV1ComodatosComodatoIdGet,
  updateComodatoApiV1ComodatosComodatoIdPut,
  deleteComodatoApiV1ComodatosComodatoIdDelete,
  getByCodeApiV1ComodatosCodeCodeGet,
  signComodatoApiV1ComodatosComodatoIdSignPost,
  deliverComodatoApiV1ComodatosComodatoIdDeliverPost,
  requestReturnApiV1ComodatosComodatoIdRequestReturnPost,
  scheduleReturnApiV1ComodatosComodatoIdScheduleReturnPost,
  registerReturnApiV1ComodatosComodatoIdReturnPost,
  registerDamageApiV1ComodatosComodatoIdDamagePost,
  terminateComodatoApiV1ComodatosComodatoIdTerminatePost,
  transferComodatoApiV1ComodatosComodatoIdTransferPost,
  markAsLostApiV1ComodatosComodatoIdMarkLostPost,
  generateContractPdfApiV1ComodatosComodatoIdContractPdfPost,
  generateDeliveryTermApiV1ComodatosComodatoIdDeliveryTermPost,
  generateReturnTermApiV1ComodatosComodatoIdReturnTermPost,
} from '@/types/generated/equipment/equipment-comodato/equipment-comodato';
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

export const comodatoService = {
  /**
   * Lista comodatos com filtros
   */
  list: async (params?: ListComodatosApiV1ComodatosGetParams): Promise<ComodatoListResponse> => {
    return await listComodatosApiV1ComodatosGet(params);
  },

  /**
   * Obtém estatísticas de comodatos
   */
  getStats: async (params?: GetStatsApiV1ComodatosStatsGetParams): Promise<GetStatsApiV1ComodatosStatsGet200> => {
    return await getStatsApiV1ComodatosStatsGet(params);
  },

  /**
   * Lista comodatos ativos
   */
  getActive: async (params?: GetActiveApiV1ComodatosActiveGetParams): Promise<ComodatoResponse[]> => {
    return await getActiveApiV1ComodatosActiveGet(params);
  },

  /**
   * Lista comodatos aguardando assinatura
   */
  getPendingSignature: async (): Promise<ComodatoResponse[]> => {
    return await getPendingSignatureApiV1ComodatosPendingSignatureGet();
  },

  /**
   * Lista comodatos aguardando entrega
   */
  getPendingDelivery: async (): Promise<ComodatoResponse[]> => {
    return await getPendingDeliveryApiV1ComodatosPendingDeliveryGet();
  },

  /**
   * Lista comodatos com devolução pendente
   */
  getPendingReturn: async (): Promise<ComodatoResponse[]> => {
    return await getPendingReturnApiV1ComodatosPendingReturnGet();
  },

  /**
   * Lista comodatos expirando
   */
  getExpiring: async (params?: GetExpiringApiV1ComodatosExpiringGetParams): Promise<ComodatoResponse[]> => {
    return await getExpiringApiV1ComodatosExpiringGet(params);
  },

  /**
   * Lista comodatos expirados não devolvidos
   */
  getExpired: async (): Promise<ComodatoResponse[]> => {
    return await getExpiredApiV1ComodatosExpiredGet();
  },

  /**
   * Lista comodatos de um cliente
   */
  getByClient: async (clientId: string): Promise<ComodatoResponse[]> => {
    return await getByClientApiV1ComodatosByClientClientIdGet(clientId);
  },

  /**
   * Busca comodato por código
   */
  getByCode: async (code: string): Promise<ComodatoResponse> => {
    return await getByCodeApiV1ComodatosCodeCodeGet(code);
  },

  /**
   * Busca comodato por ID
   */
  getById: async (comodatoId: string): Promise<ComodatoResponse> => {
    return await getComodatoApiV1ComodatosComodatoIdGet(comodatoId);
  },

  /**
   * Cria novo comodato
   */
  create: async (data: ComodatoCreate): Promise<ComodatoResponse> => {
    return await createComodatoApiV1ComodatosPost(data);
  },

  /**
   * Atualiza comodato
   */
  update: async (comodatoId: string, data: ComodatoUpdate): Promise<ComodatoResponse> => {
    return await updateComodatoApiV1ComodatosComodatoIdPut(comodatoId, data);
  },

  /**
   * Remove comodato (soft delete)
   */
  delete: async (comodatoId: string): Promise<void> => {
    await deleteComodatoApiV1ComodatosComodatoIdDelete(comodatoId);
  },

  /**
   * Registra assinatura do contrato
   */
  sign: async (
    comodatoId: string,
    params: SignComodatoApiV1ComodatosComodatoIdSignPostParams
  ): Promise<ComodatoResponse> => {
    return await signComodatoApiV1ComodatosComodatoIdSignPost(comodatoId, params);
  },

  /**
   * Registra entrega do equipamento
   */
  deliver: async (
    comodatoId: string,
    params: DeliverComodatoApiV1ComodatosComodatoIdDeliverPostParams,
    body?: BodyDeliverComodatoApiV1ComodatosComodatoIdDeliverPost
  ): Promise<ComodatoResponse> => {
    return await deliverComodatoApiV1ComodatosComodatoIdDeliverPost(
      comodatoId,
      body ?? { photos: null },
      params
    );
  },

  /**
   * Solicita devolução
   */
  requestReturn: async (comodatoId: string): Promise<ComodatoResponse> => {
    return await requestReturnApiV1ComodatosComodatoIdRequestReturnPost(comodatoId);
  },

  /**
   * Agenda devolução
   */
  scheduleReturn: async (
    comodatoId: string,
    params: ScheduleReturnApiV1ComodatosComodatoIdScheduleReturnPostParams
  ): Promise<ComodatoResponse> => {
    return await scheduleReturnApiV1ComodatosComodatoIdScheduleReturnPost(comodatoId, params);
  },

  /**
   * Registra devolução
   */
  registerReturn: async (
    comodatoId: string,
    params: RegisterReturnApiV1ComodatosComodatoIdReturnPostParams,
    body?: BodyRegisterReturnApiV1ComodatosComodatoIdReturnPost
  ): Promise<ComodatoResponse> => {
    return await registerReturnApiV1ComodatosComodatoIdReturnPost(
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
    return await registerDamageApiV1ComodatosComodatoIdDamagePost(comodatoId, params);
  },

  /**
   * Marca equipamento como perdido
   */
  markAsLost: async (comodatoId: string): Promise<ComodatoResponse> => {
    return await markAsLostApiV1ComodatosComodatoIdMarkLostPost(comodatoId);
  },

  /**
   * Encerra contrato de comodato
   */
  terminate: async (
    comodatoId: string,
    params: TerminateComodatoApiV1ComodatosComodatoIdTerminatePostParams
  ): Promise<ComodatoResponse> => {
    return await terminateComodatoApiV1ComodatosComodatoIdTerminatePost(comodatoId, params);
  },

  /**
   * Transfere comodato para outro cliente
   */
  transfer: async (
    comodatoId: string,
    params: TransferComodatoApiV1ComodatosComodatoIdTransferPostParams
  ): Promise<ComodatoResponse> => {
    return await transferComodatoApiV1ComodatosComodatoIdTransferPost(comodatoId, params);
  },

  /**
   * Gera PDF do contrato
   */
  generateContractPdf: async (comodatoId: string): Promise<GenerateContractPdfApiV1ComodatosComodatoIdContractPdfPost200> => {
    return await generateContractPdfApiV1ComodatosComodatoIdContractPdfPost(comodatoId);
  },

  /**
   * Gera termo de entrega
   */
  generateDeliveryTerm: async (comodatoId: string): Promise<GenerateDeliveryTermApiV1ComodatosComodatoIdDeliveryTermPost200> => {
    return await generateDeliveryTermApiV1ComodatosComodatoIdDeliveryTermPost(comodatoId);
  },

  /**
   * Gera termo de devolução
   */
  generateReturnTerm: async (comodatoId: string): Promise<GenerateReturnTermApiV1ComodatosComodatoIdReturnTermPost200> => {
    return await generateReturnTermApiV1ComodatosComodatoIdReturnTermPost(comodatoId);
  },
};
