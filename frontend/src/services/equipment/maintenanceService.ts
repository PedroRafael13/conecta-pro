/**
 * Maintenance Service
 * Service layer para gestão de manutenções
 */

import { getEquipmentManutencao } from '@/types/generated/equipment/equipment-manutencao/equipment-manutencao';
import type {
  MaintenanceCreate,
  MaintenanceUpdate,
  MaintenanceResponse,
  MaintenanceListResponse,
  MaintenanceStats,
  ListMaintenancesApiV1MaintenancesGetParams,
  GetStatsApiV1MaintenancesStatsGetParams,
  GetByTechnicianApiV1MaintenancesByTechnicianTechnicianIdGetParams,
  CompleteMaintenanceApiV1MaintenancesMaintenanceIdCompletePostParams,
  BodyMarkWaitingPartsApiV1MaintenancesMaintenanceIdWaitingPartsPost,
  AddPartReplacedApiV1MaintenancesMaintenanceIdAddPartPostParams,
  SignMaintenanceApiV1MaintenancesMaintenanceIdSignPostParams,
  AssignTechnicianApiV1MaintenancesMaintenanceIdAssignTechnicianPostParams,
  SchedulePreventiveApiV1MaintenancesSchedulePreventiveEquipmentIdPostParams,
  AnalyzeHealthApiV1MaintenancesAiHealthEquipmentIdGet200,
  PredictFailureApiV1MaintenancesAiPredictFailureEquipmentIdGet200,
  RecommendScheduleApiV1MaintenancesAiRecommendScheduleGet200Item,
  RecommendScheduleApiV1MaintenancesAiRecommendScheduleGetParams,
  OptimizeRouteApiV1MaintenancesAiOptimizeRouteTechnicianIdGet200Item,
  OptimizeRouteApiV1MaintenancesAiOptimizeRouteTechnicianIdGetParams,
  AnalyzePatternsApiV1MaintenancesAiPatternsGet200,
  AnalyzePatternsApiV1MaintenancesAiPatternsGetParams,
  EstimateCostApiV1MaintenancesAiEstimateCostEquipmentIdGet200,
  EstimateCostApiV1MaintenancesAiEstimateCostEquipmentIdGetParams
} from '@/types/generated/equipment/conectaPROEquipmentManagementAPI.schemas';

const maintenanceApi = getEquipmentManutencao();

export const maintenanceService = {
  /**
   * Lista manutenções com filtros
   */
  list: async (params?: ListMaintenancesApiV1MaintenancesGetParams): Promise<MaintenanceListResponse> => {
    return await maintenanceApi.listMaintenancesApiV1MaintenancesGet(params);
  },

  /**
   * Obtém estatísticas de manutenções
   */
  getStats: async (params?: GetStatsApiV1MaintenancesStatsGetParams): Promise<MaintenanceStats> => {
    return await maintenanceApi.getStatsApiV1MaintenancesStatsGet(params);
  },

  /**
   * Lista manutenções atrasadas
   */
  getOverdue: async (): Promise<MaintenanceResponse[]> => {
    return await maintenanceApi.getOverdueApiV1MaintenancesOverdueGet();
  },

  /**
   * Lista manutenções aguardando peças
   */
  getWaitingParts: async (): Promise<MaintenanceResponse[]> => {
    return await maintenanceApi.getWaitingPartsApiV1MaintenancesWaitingPartsGet();
  },

  /**
   * Lista manutenções que precisam de follow-up
   */
  getNeedingFollowup: async (): Promise<MaintenanceResponse[]> => {
    return await maintenanceApi.getNeedingFollowupApiV1MaintenancesNeedingFollowupGet();
  },

  /**
   * Lista manutenções agendadas para uma data
   */
  getByDate: async (date: string): Promise<MaintenanceResponse[]> => {
    return await maintenanceApi.getByDateApiV1MaintenancesByDateDateGet(date);
  },

  /**
   * Lista manutenções de um equipamento
   */
  getByEquipment: async (equipmentId: string): Promise<MaintenanceResponse[]> => {
    return await maintenanceApi.getByEquipmentApiV1MaintenancesByEquipmentEquipmentIdGet(equipmentId);
  },

  /**
   * Lista manutenções de um cliente
   */
  getByClient: async (clientId: string): Promise<MaintenanceResponse[]> => {
    return await maintenanceApi.getByClientApiV1MaintenancesByClientClientIdGet(clientId);
  },

  /**
   * Lista manutenções de um técnico
   */
  getByTechnician: async (
    technicianId: string,
    params?: GetByTechnicianApiV1MaintenancesByTechnicianTechnicianIdGetParams
  ): Promise<MaintenanceResponse[]> => {
    return await maintenanceApi.getByTechnicianApiV1MaintenancesByTechnicianTechnicianIdGet(technicianId, params);
  },

  /**
   * Busca manutenção por código
   */
  getByCode: async (code: string): Promise<MaintenanceResponse> => {
    return await maintenanceApi.getByCodeApiV1MaintenancesCodeCodeGet(code);
  },

  /**
   * Busca manutenção por ID
   */
  getById: async (maintenanceId: string): Promise<MaintenanceResponse> => {
    return await maintenanceApi.getMaintenanceApiV1MaintenancesMaintenanceIdGet(maintenanceId);
  },

  /**
   * Cria nova manutenção
   */
  create: async (data: MaintenanceCreate): Promise<MaintenanceResponse> => {
    return await maintenanceApi.createMaintenanceApiV1MaintenancesPost(data);
  },

  /**
   * Atualiza manutenção
   */
  update: async (maintenanceId: string, data: MaintenanceUpdate): Promise<MaintenanceResponse> => {
    return await maintenanceApi.updateMaintenanceApiV1MaintenancesMaintenanceIdPut(maintenanceId, data);
  },

  /**
   * Remove manutenção (soft delete)
   */
  delete: async (maintenanceId: string): Promise<void> => {
    await maintenanceApi.deleteMaintenanceApiV1MaintenancesMaintenanceIdDelete(maintenanceId);
  },

  /**
   * Inicia manutenção
   */
  start: async (maintenanceId: string): Promise<MaintenanceResponse> => {
    return await maintenanceApi.startMaintenanceApiV1MaintenancesMaintenanceIdStartPost(maintenanceId);
  },

  /**
   * Conclui manutenção
   */
  complete: async (
    maintenanceId: string,
    params?: CompleteMaintenanceApiV1MaintenancesMaintenanceIdCompletePostParams
  ): Promise<MaintenanceResponse> => {
    return await maintenanceApi.completeMaintenanceApiV1MaintenancesMaintenanceIdCompletePost(maintenanceId, params);
  },

  /**
   * Cancela manutenção
   */
  cancel: async (maintenanceId: string): Promise<MaintenanceResponse> => {
    return await maintenanceApi.cancelMaintenanceApiV1MaintenancesMaintenanceIdCancelPost(maintenanceId);
  },

  /**
   * Marca como aguardando peças
   */
  markWaitingParts: async (
    maintenanceId: string,
    body: BodyMarkWaitingPartsApiV1MaintenancesMaintenanceIdWaitingPartsPost
  ): Promise<MaintenanceResponse> => {
    return await maintenanceApi.markWaitingPartsApiV1MaintenancesMaintenanceIdWaitingPartsPost(maintenanceId, body);
  },

  /**
   * Adiciona peça substituída
   */
  addPartReplaced: async (
    maintenanceId: string,
    params: AddPartReplacedApiV1MaintenancesMaintenanceIdAddPartPostParams
  ): Promise<MaintenanceResponse> => {
    return await maintenanceApi.addPartReplacedApiV1MaintenancesMaintenanceIdAddPartPost(maintenanceId, params);
  },

  /**
   * Registra assinatura do cliente
   */
  sign: async (
    maintenanceId: string,
    params: SignMaintenanceApiV1MaintenancesMaintenanceIdSignPostParams
  ): Promise<MaintenanceResponse> => {
    return await maintenanceApi.signMaintenanceApiV1MaintenancesMaintenanceIdSignPost(maintenanceId, params);
  },

  /**
   * Atribui técnico à manutenção
   */
  assignTechnician: async (
    maintenanceId: string,
    params: AssignTechnicianApiV1MaintenancesMaintenanceIdAssignTechnicianPostParams
  ): Promise<MaintenanceResponse> => {
    return await maintenanceApi.assignTechnicianApiV1MaintenancesMaintenanceIdAssignTechnicianPost(maintenanceId, params);
  },

  /**
   * Agenda manutenção preventiva
   */
  schedulePreventive: async (
    equipmentId: string,
    params?: SchedulePreventiveApiV1MaintenancesSchedulePreventiveEquipmentIdPostParams
  ): Promise<MaintenanceResponse> => {
    return await maintenanceApi.schedulePreventiveApiV1MaintenancesSchedulePreventiveEquipmentIdPost(equipmentId, params);
  },

  // AI Endpoints
  /**
   * Analisa saúde do equipamento usando IA
   */
  analyzeHealth: async (equipmentId: string): Promise<AnalyzeHealthApiV1MaintenancesAiHealthEquipmentIdGet200> => {
    return await maintenanceApi.analyzeHealthApiV1MaintenancesAiHealthEquipmentIdGet(equipmentId);
  },

  /**
   * Prevê probabilidade de falha
   */
  predictFailure: async (equipmentId: string): Promise<PredictFailureApiV1MaintenancesAiPredictFailureEquipmentIdGet200> => {
    return await maintenanceApi.predictFailureApiV1MaintenancesAiPredictFailureEquipmentIdGet(equipmentId);
  },

  /**
   * Recomenda agenda de manutenções preventivas
   */
  recommendSchedule: async (
    params?: RecommendScheduleApiV1MaintenancesAiRecommendScheduleGetParams
  ): Promise<RecommendScheduleApiV1MaintenancesAiRecommendScheduleGet200Item[]> => {
    return await maintenanceApi.recommendScheduleApiV1MaintenancesAiRecommendScheduleGet(params);
  },

  /**
   * Otimiza rota de manutenções
   */
  optimizeRoute: async (
    technicianId: string,
    params: OptimizeRouteApiV1MaintenancesAiOptimizeRouteTechnicianIdGetParams
  ): Promise<OptimizeRouteApiV1MaintenancesAiOptimizeRouteTechnicianIdGet200Item[]> => {
    return await maintenanceApi.optimizeRouteApiV1MaintenancesAiOptimizeRouteTechnicianIdGet(technicianId, params);
  },

  /**
   * Analisa padrões de manutenção
   */
  analyzePatterns: async (
    params?: AnalyzePatternsApiV1MaintenancesAiPatternsGetParams
  ): Promise<AnalyzePatternsApiV1MaintenancesAiPatternsGet200> => {
    return await maintenanceApi.analyzePatternsApiV1MaintenancesAiPatternsGet(params);
  },

  /**
   * Estima custo de manutenção
   */
  estimateCost: async (
    equipmentId: string,
    params?: EstimateCostApiV1MaintenancesAiEstimateCostEquipmentIdGetParams
  ): Promise<EstimateCostApiV1MaintenancesAiEstimateCostEquipmentIdGet200> => {
    return await maintenanceApi.estimateCostApiV1MaintenancesAiEstimateCostEquipmentIdGet(equipmentId, params);
  },
};
