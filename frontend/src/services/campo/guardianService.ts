/**
 * Service Layer - Guardian (CAMPO)
 * Gestão de logs, ocorrências e equipamentos Guardian
 */

import * as AccessLogAPI from '@/api/campo/generated/guardian-access-logs/guardian-access-logs';
import * as OccurrenceAPI from '@/api/campo/generated/guardian-occurrences/guardian-occurrences';
import * as EquipmentAPI from '@/api/campo/generated/guardian-equipment/guardian-equipment';
import * as SyncAPI from '@/api/campo/generated/guardian-sync/guardian-sync';
import type {
  // Access Log types
  AccessLogCreate,
  ListAccessLogsApiV1CampoGuardianAccessLogsGuardianAccessLogsGetParams,
  GetAccessLogStatsApiV1CampoGuardianAccessLogsGuardianAccessLogsStatsGetParams,
  // Occurrence types
  GuardianOccurrenceCreate,
  ListOccurrencesApiV1CampoGuardianOccurrencesGuardianOccurrencesGetParams,
  GetOccurrenceStatsApiV1CampoGuardianOccurrencesGuardianOccurrencesStatsGetParams,
  GetOpenOccurrencesApiV1CampoGuardianOccurrencesGuardianOccurrencesOpenGetParams,
  GetCriticalOpenOccurrencesApiV1CampoGuardianOccurrencesGuardianOccurrencesCriticalOpenGetParams,
  ClassifyOccurrenceApiV1CampoGuardianOccurrencesGuardianOccurrencesClassifyPostParams,
  CheckEscalationApiV1CampoGuardianOccurrencesGuardianOccurrencesCheckEscalationPostParams,
  SuggestOccurrenceActionsApiV1CampoGuardianOccurrencesGuardianOccurrencesSuggestActionsPostParams,
  // Equipment types
  EquipmentStatusCreate,
  EquipmentStatusUpdate,
  ListEquipmentStatusApiV1CampoGuardianEquipmentStatusGuardianEquipmentStatusGetParams,
  GetOfflineEquipmentApiV1CampoGuardianEquipmentStatusGuardianEquipmentStatusOfflineGetParams,
  GetEquipmentNeedsMaintenanceApiV1CampoGuardianEquipmentStatusGuardianEquipmentStatusNeedsMaintenanceGetParams,
  GetEquipmentWithAlertsApiV1CampoGuardianEquipmentStatusGuardianEquipmentStatusWithAlertsGetParams,
  SetEquipmentOnlineApiV1CampoGuardianEquipmentStatusGuardianEquipmentStatusEquipmentIdSetOnlinePostParams,
  SetEquipmentOfflineApiV1CampoGuardianEquipmentStatusGuardianEquipmentStatusEquipmentIdSetOfflinePostParams,
  GetEquipmentStatsApiV1CampoGuardianEquipmentStatusGuardianEquipmentStatusStatsGetParams,
  // Sync types
  GuardianSyncCreate,
  ListSyncsApiV1CampoGuardianSyncGuardianSyncGetParams,
  GetPendingSyncsApiV1CampoGuardianSyncGuardianSyncPendingGetParams,
  GetFailedForRetryApiV1CampoGuardianSyncGuardianSyncFailedForRetryGetParams,
  GetSyncStatsApiV1CampoGuardianSyncGuardianSyncStatsGetParams,
} from '@/api/campo/generated/models';

/**
 * Service para Access Logs
 */
export class GuardianAccessLogService {
  async listar(params?: ListAccessLogsApiV1CampoGuardianAccessLogsGuardianAccessLogsGetParams) {
    return AccessLogAPI.listAccessLogsApiV1CampoGuardianAccessLogsGuardianAccessLogsGet(params);
  }

  async buscar(logId: string) {
    return AccessLogAPI.getAccessLogApiV1CampoGuardianAccessLogsGuardianAccessLogsLogIdGet(logId);
  }

  async criar(data: AccessLogCreate) {
    return AccessLogAPI.createAccessLogApiV1CampoGuardianAccessLogsGuardianAccessLogsPost(data);
  }

  async criarBatch(logs: AccessLogCreate[]) {
    return AccessLogAPI.createAccessLogsBatchApiV1CampoGuardianAccessLogsGuardianAccessLogsBatchPost(logs);
  }

  async buscarPorPessoa(personDocument: string) {
    return AccessLogAPI.getLogsByPersonApiV1CampoGuardianAccessLogsGuardianAccessLogsByPersonPersonDocumentGet(
      personDocument
    );
  }

  async buscarPorVeiculo(vehiclePlate: string) {
    return AccessLogAPI.getLogsByVehicleApiV1CampoGuardianAccessLogsGuardianAccessLogsByVehicleVehiclePlateGet(
      vehiclePlate
    );
  }

  async estatisticas(params?: GetAccessLogStatsApiV1CampoGuardianAccessLogsGuardianAccessLogsStatsGetParams) {
    return AccessLogAPI.getAccessLogStatsApiV1CampoGuardianAccessLogsGuardianAccessLogsStatsGet(params);
  }

  async deletar(logId: string) {
    return AccessLogAPI.deleteAccessLogApiV1CampoGuardianAccessLogsGuardianAccessLogsLogIdDelete(logId);
  }
}

/**
 * Service para Occurrences
 */
export class GuardianOccurrenceService {
  async listar(params?: ListOccurrencesApiV1CampoGuardianOccurrencesGuardianOccurrencesGetParams) {
    return OccurrenceAPI.listOccurrencesApiV1CampoGuardianOccurrencesGuardianOccurrencesGet(params);
  }

  async buscar(occurrenceId: string) {
    return OccurrenceAPI.getOccurrenceApiV1CampoGuardianOccurrencesGuardianOccurrencesOccurrenceIdGet(
      occurrenceId
    );
  }

  async criar(data: GuardianOccurrenceCreate) {
    return OccurrenceAPI.createOccurrenceApiV1CampoGuardianOccurrencesGuardianOccurrencesPost(data);
  }

  async deletar(occurrenceId: string) {
    return OccurrenceAPI.deleteOccurrenceApiV1CampoGuardianOccurrencesGuardianOccurrencesOccurrenceIdDelete(
      occurrenceId
    );
  }

  async classificar(params: ClassifyOccurrenceApiV1CampoGuardianOccurrencesGuardianOccurrencesClassifyPostParams) {
    return OccurrenceAPI.classifyOccurrenceApiV1CampoGuardianOccurrencesGuardianOccurrencesClassifyPost(params);
  }

  async verificarEscalacao(params: CheckEscalationApiV1CampoGuardianOccurrencesGuardianOccurrencesCheckEscalationPostParams) {
    return OccurrenceAPI.checkEscalationApiV1CampoGuardianOccurrencesGuardianOccurrencesCheckEscalationPost(params);
  }

  async listarAbertas(params?: GetOpenOccurrencesApiV1CampoGuardianOccurrencesGuardianOccurrencesOpenGetParams) {
    return OccurrenceAPI.getOpenOccurrencesApiV1CampoGuardianOccurrencesGuardianOccurrencesOpenGet(params);
  }

  async listarCriticasAbertas(params?: GetCriticalOpenOccurrencesApiV1CampoGuardianOccurrencesGuardianOccurrencesCriticalOpenGetParams) {
    return OccurrenceAPI.getCriticalOpenOccurrencesApiV1CampoGuardianOccurrencesGuardianOccurrencesCriticalOpenGet(params);
  }

  async estatisticas(params?: GetOccurrenceStatsApiV1CampoGuardianOccurrencesGuardianOccurrencesStatsGetParams) {
    return OccurrenceAPI.getOccurrenceStatsApiV1CampoGuardianOccurrencesGuardianOccurrencesStatsGet(params);
  }

  async sugerirAcoes(params: SuggestOccurrenceActionsApiV1CampoGuardianOccurrencesGuardianOccurrencesSuggestActionsPostParams) {
    return OccurrenceAPI.suggestOccurrenceActionsApiV1CampoGuardianOccurrencesGuardianOccurrencesSuggestActionsPost(params);
  }
}

/**
 * Service para Equipment Status
 */
export class GuardianEquipmentService {
  async listar(params?: ListEquipmentStatusApiV1CampoGuardianEquipmentStatusGuardianEquipmentStatusGetParams) {
    return EquipmentAPI.listEquipmentStatusApiV1CampoGuardianEquipmentStatusGuardianEquipmentStatusGet(params);
  }

  async buscar(equipmentId: string) {
    return EquipmentAPI.getEquipmentStatusApiV1CampoGuardianEquipmentStatusGuardianEquipmentStatusEquipmentIdGet(
      equipmentId
    );
  }

  async criar(data: EquipmentStatusCreate) {
    return EquipmentAPI.createEquipmentStatusApiV1CampoGuardianEquipmentStatusGuardianEquipmentStatusPost(data);
  }

  async atualizar(equipmentId: string, data: EquipmentStatusUpdate) {
    return EquipmentAPI.updateEquipmentStatusApiV1CampoGuardianEquipmentStatusGuardianEquipmentStatusEquipmentIdPatch(
      equipmentId,
      data
    );
  }

  async deletar(equipmentId: string) {
    return EquipmentAPI.deleteEquipmentStatusApiV1CampoGuardianEquipmentStatusGuardianEquipmentStatusEquipmentIdDelete(
      equipmentId
    );
  }

  async listarOffline(params?: GetOfflineEquipmentApiV1CampoGuardianEquipmentStatusGuardianEquipmentStatusOfflineGetParams) {
    return EquipmentAPI.getOfflineEquipmentApiV1CampoGuardianEquipmentStatusGuardianEquipmentStatusOfflineGet(params);
  }

  async listarManutencao(params?: GetEquipmentNeedsMaintenanceApiV1CampoGuardianEquipmentStatusGuardianEquipmentStatusNeedsMaintenanceGetParams) {
    return EquipmentAPI.getEquipmentNeedsMaintenanceApiV1CampoGuardianEquipmentStatusGuardianEquipmentStatusNeedsMaintenanceGet(params);
  }

  async listarComAlertas(params?: GetEquipmentWithAlertsApiV1CampoGuardianEquipmentStatusGuardianEquipmentStatusWithAlertsGetParams) {
    return EquipmentAPI.getEquipmentWithAlertsApiV1CampoGuardianEquipmentStatusGuardianEquipmentStatusWithAlertsGet(params);
  }

  async setarOnline(equipmentId: string, params?: SetEquipmentOnlineApiV1CampoGuardianEquipmentStatusGuardianEquipmentStatusEquipmentIdSetOnlinePostParams) {
    return EquipmentAPI.setEquipmentOnlineApiV1CampoGuardianEquipmentStatusGuardianEquipmentStatusEquipmentIdSetOnlinePost(
      equipmentId,
      params
    );
  }

  async setarOffline(equipmentId: string, params?: SetEquipmentOfflineApiV1CampoGuardianEquipmentStatusGuardianEquipmentStatusEquipmentIdSetOfflinePostParams) {
    return EquipmentAPI.setEquipmentOfflineApiV1CampoGuardianEquipmentStatusGuardianEquipmentStatusEquipmentIdSetOfflinePost(
      equipmentId,
      params
    );
  }

  async estatisticas(params?: GetEquipmentStatsApiV1CampoGuardianEquipmentStatusGuardianEquipmentStatusStatsGetParams) {
    return EquipmentAPI.getEquipmentStatsApiV1CampoGuardianEquipmentStatusGuardianEquipmentStatusStatsGet(params);
  }
}

/**
 * Service para Sync
 */
export class GuardianSyncService {
  async listar(params?: ListSyncsApiV1CampoGuardianSyncGuardianSyncGetParams) {
    return SyncAPI.listSyncsApiV1CampoGuardianSyncGuardianSyncGet(params);
  }

  async buscar(syncId: string) {
    return SyncAPI.getSyncApiV1CampoGuardianSyncGuardianSyncSyncIdGet(syncId);
  }

  async criar(data: GuardianSyncCreate) {
    return SyncAPI.createSyncApiV1CampoGuardianSyncGuardianSyncPost(data);
  }

  async deletar(syncId: string) {
    return SyncAPI.deleteSyncApiV1CampoGuardianSyncGuardianSyncSyncIdDelete(syncId);
  }

  async listarPendentes(params?: GetPendingSyncsApiV1CampoGuardianSyncGuardianSyncPendingGetParams) {
    return SyncAPI.getPendingSyncsApiV1CampoGuardianSyncGuardianSyncPendingGet(params);
  }

  async listarFalhas(params?: GetFailedForRetryApiV1CampoGuardianSyncGuardianSyncFailedForRetryGetParams) {
    return SyncAPI.getFailedForRetryApiV1CampoGuardianSyncGuardianSyncFailedForRetryGet(params);
  }

  async retentar(syncId: string, data: { notes?: string } = {}) {
    return SyncAPI.retrySyncApiV1CampoGuardianSyncGuardianSyncSyncIdRetryPost(syncId, data);
  }

  async resumo() {
    return SyncAPI.getSyncSummaryApiV1CampoGuardianSyncGuardianSyncSummaryGet();
  }

  async estatisticas(params?: GetSyncStatsApiV1CampoGuardianSyncGuardianSyncStatsGetParams) {
    return SyncAPI.getSyncStatsApiV1CampoGuardianSyncGuardianSyncStatsGet(params);
  }
}

// Exports das instâncias
export const guardianAccessLogService = new GuardianAccessLogService();
export const guardianOccurrenceService = new GuardianOccurrenceService();
export const guardianEquipmentService = new GuardianEquipmentService();
export const guardianSyncService = new GuardianSyncService();
