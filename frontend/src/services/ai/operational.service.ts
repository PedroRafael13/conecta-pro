/**
 * Operational AI Service
 * Análise operacional inteligente: diaristas, equipamentos, manutenções
 */

import { customInstance } from '@/lib/axios-instance';

const DIARISTAS_BASE = '/api/v1/operacional/diaristas/ai';
const MAINTENANCE_BASE = '/api/v1/maintenances/ai';

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
  ): Promise<unknown> {
    return customInstance.get(`${DIARISTAS_BASE}/availability`, {
      params: { data_inicio: dataInicio, data_fim: dataFim, tipo },
    });
  }

  /**
   * Otimiza alocação de diaristas
   */
  static async optimizeDiaristAllocation(
    dataInicio: string,
    dataFim: string,
    budget?: number | string
  ): Promise<unknown> {
    return customInstance.get(`${DIARISTAS_BASE}/optimize`, {
      params: { data_inicio: dataInicio, data_fim: dataFim, budget },
    });
  }

  /**
   * Analisa desempenho de diarista
   */
  static async analyzeDiaristPerformance(diaristId: string): Promise<unknown> {
    return customInstance.get(
      `${DIARISTAS_BASE}/performance/${diaristId}`
    );
  }

  /**
   * Sugere diaristas para demanda
   */
  static async suggestDiarists(
    data: string,
    tipo?: string,
    hours?: number
  ): Promise<unknown> {
    return customInstance.get(`${DIARISTAS_BASE}/suggest`, {
      params: { data, tipo, hours },
    });
  }

  // ========== MANUTENÇÕES E EQUIPAMENTOS ==========

  /**
   * Estima custo de manutenção
   */
  static async estimateMaintenanceCost(equipmentId: string): Promise<unknown> {
    return customInstance.get(
      `${MAINTENANCE_BASE}/estimate-cost/${equipmentId}`
    );
  }

  /**
   * Prevê falhas de equipamento
   */
  static async predictFailure(equipmentId: string): Promise<unknown> {
    return customInstance.get(
      `${MAINTENANCE_BASE}/predict-failure/${equipmentId}`
    );
  }

  /**
   * Analisa saúde do equipamento
   */
  static async analyzeEquipmentHealth(equipmentId: string): Promise<unknown> {
    return customInstance.get(
      `${MAINTENANCE_BASE}/health/${equipmentId}`
    );
  }

  /**
   * Identifica padrões de manutenção
   */
  static async analyzeMaintenancePatterns(
    clientId?: string
  ): Promise<unknown> {
    return customInstance.get(`${MAINTENANCE_BASE}/patterns`, {
      params: { client_id: clientId },
    });
  }

  /**
   * Recomenda agendamento de manutenção
   */
  static async recommendSchedule(clientId?: string): Promise<unknown> {
    return customInstance.get(`${MAINTENANCE_BASE}/recommend-schedule`, {
      params: { client_id: clientId },
    });
  }

  /**
   * Otimiza rota de técnico
   */
  static async optimizeRoute(
    technicianId: string,
    date: string
  ): Promise<unknown> {
    return customInstance.get(
      `${MAINTENANCE_BASE}/optimize-route/${technicianId}`,
      { params: { date } }
    );
  }
}

export default OperationalAIService;
