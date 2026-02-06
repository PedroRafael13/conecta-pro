/**
 * Operational AI Service
 * Análise operacional inteligente: diaristas, equipamentos, manutenções
 */

import { getOperacionalDiaristas } from '@/types/generated/ai/operacional-diaristas/operacional-diaristas';
import { getEquipmentManutencao } from '@/types/generated/ai/equipment-manutencao/equipment-manutencao';

const diaristasApi = getOperacionalDiaristas();
const maintenanceApi = getEquipmentManutencao();

/**
 * Service para análise operacional com IA
 */
export class OperationalAIService {
  // ========== DIARISTAS ==========

  /**
   * Verifica disponibilidade de diaristas
   */
  static async checkDiaristAvailability(
    dataInicio: string,
    dataFim: string,
    tipo?: string
  ): Promise<any> {
    return diaristasApi.analyzeAvailabilityApiV1OperacionalDiaristasAiAvailabilityGet({
      data_inicio: dataInicio,
      data_fim: dataFim,
      tipo: tipo as any,
    });
  }

  /**
   * Otimiza alocação de diaristas
   */
  static async optimizeDiaristAllocation(
    dataInicio: string,
    dataFim: string,
    budget?: number | string
  ): Promise<any> {
    return diaristasApi.optimizeScheduleApiV1OperacionalDiaristasAiOptimizeGet({
      data_inicio: dataInicio,
      data_fim: dataFim,
      budget: budget as any,
    });
  }

  /**
   * Analisa desempenho de diarista
   */
  static async analyzeDiaristPerformance(diaristId: string): Promise<any> {
    return diaristasApi.analyzePerformanceApiV1OperacionalDiaristasAiPerformanceDiaristIdGet(
      diaristId
    );
  }

  /**
   * Sugere diaristas para demanda
   */
  static async suggestDiarists(
    data: string,
    tipo?: string,
    hours?: number
  ): Promise<any> {
    return diaristasApi.suggestDiaristsApiV1OperacionalDiaristasAiSuggestGet({
      data,
      tipo: tipo as any,
      // hours removido - parâmetro não existe no schema gerado
    });
  }

  // ========== MANUTENÇÕES E EQUIPAMENTOS ==========

  /**
   * Estima custo de manutenção
   */
  static async estimateMaintenanceCost(equipmentId: string): Promise<any> {
    return maintenanceApi.estimateCostApiV1MaintenancesAiEstimateCostEquipmentIdGet(
      equipmentId
    );
  }

  /**
   * Prevê falhas de equipamento
   */
  static async predictFailure(equipmentId: string): Promise<any> {
    return maintenanceApi.predictFailureApiV1MaintenancesAiPredictFailureEquipmentIdGet(
      equipmentId
    );
  }

  /**
   * Analisa saúde do equipamento
   */
  static async analyzeEquipmentHealth(equipmentId: string): Promise<any> {
    return maintenanceApi.analyzeHealthApiV1MaintenancesAiHealthEquipmentIdGet(
      equipmentId
    );
  }

  /**
   * Identifica padrões de manutenção
   */
  static async analyzeMaintenancePatterns(
    clientId?: string
  ): Promise<any> {
    return maintenanceApi.analyzePatternsApiV1MaintenancesAiPatternsGet({
      client_id: clientId,
    });
  }

  /**
   * Recomenda agendamento de manutenção
   */
  static async recommendSchedule(clientId?: string): Promise<any> {
    return maintenanceApi.recommendScheduleApiV1MaintenancesAiRecommendScheduleGet({
      client_id: clientId,
    });
  }

  /**
   * Otimiza rota de técnico
   */
  static async optimizeRoute(
    technicianId: string,
    date: string
  ): Promise<any> {
    return maintenanceApi.optimizeRouteApiV1MaintenancesAiOptimizeRouteTechnicianIdGet(
      technicianId,
      { date }
    );
  }
}

export default OperationalAIService;
